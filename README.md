# RAG Docs Chatbot

A retrieval-augmented generation (RAG) API that answers questions from project documentation. Documents are chunked, embedded, and stored in PostgreSQL with pgvector. At query time, the closest chunks are retrieved and passed to a local Ollama model, which returns an answer with source citations.

Built as a hands-on AI / Forward Deployed Engineering portfolio project: a small, inspectable pipeline from raw markdown to a FastAPI `/chat` endpoint.

**Stack:** FastAPI · SQLAlchemy · PostgreSQL / Neon · pgvector · Sentence Transformers · Ollama (`llama3.2:3b`)

---

## Why this project

Typical RAG demos hide the retrieval path inside a framework. This repo keeps each stage as its own script so you can run, inspect, and debug them independently:

| Stage | Script | What you can prove |
| --- | --- | --- |
| Split documents | `chunker.py` / `ingest.py` | Overlapping chunks land in Postgres |
| Vectorize | `embed.py` | Only rows with `embedding IS NULL` are encoded |
| Retrieve | `search.py` | Cosine-nearest neighbors in pgvector |
| Generate | `chat.py` | Grounded answers plus source snippets |
| Serve | `main.py` | HTTP API for search and chat |

The knowledge base in `source_docs/` is operational documentation (Git, Docker, EC2, CI/CD). The chatbot is trained on that corpus, not on this README.

---

## Architecture

```mermaid
flowchart LR
  subgraph ingest [Ingestion]
    MD[Markdown in source_docs]
    CH[chunker.py]
    IN[ingest.py]
    MD --> CH --> IN
  end

  subgraph store [PostgreSQL + pgvector]
    T[document_chunks]
  end

  subgraph embed [Embeddings]
    EM[embed.py<br/>all-MiniLM-L6-v2]
  end

  subgraph query [Query path]
    API[FastAPI]
    SE[search.py]
    RAG[chat.py]
    LLM[Ollama llama3.2:3b]
  end

  IN --> T
  T --> EM
  EM --> T
  API --> SE
  SE --> T
  SE --> RAG
  RAG --> LLM
  RAG --> API
```

**End-to-end flow**

1. Markdown files are split into 500-character windows with 50-character overlap.
2. Chunks are inserted into `document_chunks` with `embedding = NULL`.
3. `all-MiniLM-L6-v2` writes a 384-dimensional vector per chunk (same width as the `Vector(384)` column).
4. A user query is encoded with the **same** model.
5. pgvector ranks rows by cosine distance and returns `top_k` chunks.
6. Those chunks become the prompt context for Ollama.
7. The API returns the model answer and the retrieved sources.

Retrieval and generation are separate: `/search` stops at nearest neighbors; `/chat` adds the LLM.

---

## Project layout

```text
rag-docs-chatbot/
├── main.py                 # FastAPI app: /health, /search, /chat
├── chat.py                 # RAG prompt + Ollama generation
├── search.py               # Query embedding + cosine k-NN
├── ingest.py               # Load markdown into Postgres
├── embed.py                # Fill missing embeddings
├── chunker.py              # Sliding-window text splitter
├── model.py                # SQLAlchemy DocumentChunk
├── database.py             # Engine / session from DATABASE_URL
├── create_tables.py        # create_all for document_chunks
├── requirements.txt
├── source_docs/            # Corpus the chatbot retrieves from
│   ├── PROJECT_DOCUMENTATION.md
│   └── PROJECT_RUNBOOK.md
└── .gitignore
```

---

## Prerequisites

- Python 3.12+
- A PostgreSQL database with the **pgvector** extension (Neon is a typical hosted option)
- [Ollama](https://ollama.com) installed locally, with the chat model pulled
- Hugging Face access for the first `sentence-transformers` download (optional `HF_TOKEN` reduces rate limits)

---

## Setup

### 1. Clone and virtualenv

```bash
git clone <your-repo-url>
cd rag-docs-chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install ollama   # used by chat.py; add to requirements if you freeze again
```

### 2. Environment

Create `.env` in the project root (never commit this file):

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

`database.py` loads this with `python-dotenv`. If `DATABASE_URL` is missing, the engine is left as `None` so imports do not crash without credentials.

### 3. Enable pgvector

On a new Postgres / Neon database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. Create tables

```bash
python3 create_tables.py
```

This runs `Base.metadata.create_all`. It creates tables that do not exist; it does **not** alter an existing table if you later change a column.

### 5. Ingest, then embed

```bash
python3 ingest.py
python3 embed.py
```

Ingest is idempotent per `source_file`: if any row already exists for that path, the file is skipped.

### 6. Ollama

```bash
ollama pull llama3.2:3b
ollama serve          # if the daemon is not already running
```

`chat.py` calls `ollama.chat(model="llama3.2:3b", ...)`. The Ollama HTTP API must be reachable on the machine that runs FastAPI (default `localhost:11434`).

### 7. Run the API

```bash
python3 -m uvicorn main:app --reload
```

- App: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Stop the server with **Ctrl+C**. Ctrl+Z only suspends the process and leaves port 8000 in use.

---

## Database

SQLAlchemy model (`model.py`):

| Column | Type | Role |
| --- | --- | --- |
| `id` | `Integer`, PK | Chunk identity |
| `source_file` | `String` | Path of the ingested markdown file |
| `content` | `Text` | Chunk text used for both embedding and LLM context |
| `embedding` | `Vector(384)` | MiniLM embedding; `NULL` until `embed.py` runs |

Sessions are created with `autocommit=False` and `autoflush=False`. New rows are staged with `db.add()` then `db.commit()`. Updates (embeddings) mutate tracked objects in place; `db.add()` is not required after a query.

`create_all` will not add a new column to a table that already exists. If the schema changed in development and you have no data to keep, drop `document_chunks` and recreate it.

---

## Ingestion

`chunker.py` uses a character sliding window:

- **chunk size:** 500
- **overlap:** 50 (the next window starts 50 characters before the previous end)

Overlap keeps sentences that sit on a boundary from being split with no neighboring context.

`ingest.py` currently loads:

- `source_docs/PROJECT_DOCUMENTATION.md`
- `source_docs/PROJECT_RUNBOOK.md`

Each chunk is stored with `embedding=None`. To add another document, call `ingest_file("path/to/file.md", db)` and run `embed.py` again.

---

## Embeddings

`embed.py` loads `sentence-transformers/all-MiniLM-L6-v2` once, selects rows where `embedding IS NULL`, encodes `chunk.content`, and assigns `chunk.embedding = vector.tolist()`.

`tolist()` is required: `encode()` returns a NumPy array; pgvector expects a Python list.

Query-time embeddings in `search.py` use the **same model**. Mixing embedding models would make cosine distance meaningless.

---

## Vector search

`search.py`:

1. Opens a SQLAlchemy session.
2. Encodes the query string to a 384-d vector.
3. Orders `document_chunks` by `embedding.cosine_distance(query_embedding)`.
4. Limits to `top_k` (default 5).
5. Closes the session and returns ORM objects.

Cosine **distance** is `1 - cosine similarity`. Lower distance = closer match. `ORDER BY ... cosine_distance` therefore returns the nearest neighbors first.

This is brute-force k-NN over the table (fine for a documentation corpus; production scale would add an HNSW / IVF index on the vector column).

---

## RAG flow

Implemented in `chat.py` as `generate_answer(question, top_k=5)`:

1. **Retrieve** — `search(query=question, top_k=top_k)`.
2. **Context** — join chunk texts with `\n\n---\n\n`.
3. **Prompt** — instruct the model to answer from context only; if the docs do not contain the answer, say so rather than invent facts.
4. **Generate** — `ollama.chat` with `llama3.2:3b`.
5. **Respond** — `{ "answer": ..., "sources": [ { "source_file", "content" }, ... ] }`.

The LLM never queries the database. Grounding is entirely “retrieve first, then generate.” Sources are the same chunks that were stuffed into the prompt, so clients can display citations.

---

## API endpoints

| Method | Path | Body | Response |
| --- | --- | --- | --- |
| `GET` | `/` | — | Welcome message |
| `GET` | `/health` | — | `{ "status": "healthy" }` |
| `POST` | `/search` | `{ "query": str, "top_k": int = 5 }` | Query plus retrieved chunk texts |
| `POST` | `/chat` | `{ "query": str, "top_k": int = 5 }` | Answer plus `sources` |

### Search

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I deploy the application?", "top_k": 5}'
```

### Chat

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What happens after I push my changes to GitHub?", "top_k": 5}'
```

Example chat shape:

```json
{
  "answer": "After you push to main, GitHub Actions runs the test job, then deploy if tests pass.",
  "sources": [
    {
      "source_file": "source_docs/PROJECT_DOCUMENTATION.md",
      "content": "Every git push to main triggers .github/workflows/ci.yml..."
    }
  ]
}
```

CLI check without the HTTP layer:

```bash
python3 -c "from chat import generate_answer; print(generate_answer('How do I deploy the application?'))"
```

---

## Ollama

| Piece | Detail |
| --- | --- |
| Runtime | Local Ollama daemon |
| Model | `llama3.2:3b` (pull with `ollama pull llama3.2:3b`) |
| Python client | `import ollama` → `ollama.chat(...)` |
| Prompt role | Context + question sent as a `system` message |

Generation is local: no OpenAI/Anthropic key is required for chat. Trade-off: the host must have enough RAM for MiniLM **and** the 3B chat model.

To swap models, change the `model=` argument in `chat.py` and pull that tag in Ollama. Keep the **embedding** model unchanged unless you re-embed the whole table.

---

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| `[Errno 48] Address already in use` | Previous uvicorn still bound to 8000 (often after **Ctrl+Z**) | `lsof -nP -iTCP:8000 -sTCP:LISTEN` then `kill -9 <pid>`. Stop servers with **Ctrl+C**. |
| `No DATABASE_URL found` | Missing `.env` or empty variable | Add `DATABASE_URL=...` and confirm `load_dotenv()` can see the file in the project root. |
| `column "embedding" does not exist` / type errors | Table created before pgvector / `Vector(384)` | Enable `CREATE EXTENSION vector`, drop and recreate the table in dev. |
| `Found 0 chunks needing embeddings` | Already embedded, or ingest never ran | Run `ingest.py` first; re-ingest only after deleting rows for that `source_file`. |
| Empty or weak search hits | Embeddings missing, or query uses a different model | Confirm `embedding` is not NULL; do not mix MiniLM with another encoder. |
| Chat hangs or connection refused to Ollama | Daemon not running, or wrong model name | `ollama serve`, `ollama list`, `ollama pull llama3.2:3b`. |
| Answer is “I could not find…” but the docs contain it | Retrieval missed the chunk (windowing / `top_k`) | Increase `top_k`, inspect `/search` results, consider chunk size. |
| Hugging Face download / rate limit warnings | Unauthenticated Hub requests | Set `HF_TOKEN` in the environment. |
| `create_all` does not add new columns | SQLAlchemy never migrates existing tables | Drop table in empty dev DBs, or use Alembic in a longer-lived environment. |

---

## Git workflow

`.gitignore` already excludes `.env`, `venv/`, `__pycache__/`, and `*.pyc`.

```bash
git status                          # confirm .env is not listed
git add README.md                   # or the files you intend to commit
git commit -m "Document RAG pipeline and local setup"
git push
```

Habits that matter for this repo:

1. Create / update `.gitignore` **before** the first `git add` of secrets.
2. After `git add .`, run `git status` again and verify `.env` is untracked.
3. If a database URL or key is ever committed or pasted, **rotate it** in Neon (or the provider) immediately; deleting the file does not remove it from git history.
4. Prefer SSH remotes on a laptop you push from; HTTPS is enough for clone-only machines.

Suggested commit style: short messages that say **why** (`Add chat endpoint that grounds Ollama on pgvector hits`), not a file dump.

---

## Design notes (portfolio)

**What this demonstrates**

- A complete RAG loop: chunk → embed → store → retrieve → generate → cite.
- pgvector in real SQL rather than an in-memory toy index.
- Same embedding model at index time and query time.
- Prompt constraints that reduce hallucination (answer from context or abstain).
- A thin FastAPI surface over scripts you can run one at a time.

**Current limitations (honest)**

- Character chunking, not token- or sentence-aware splitting.
- No ANN index; linear scan is acceptable for a small doc set.
- Ingest skip-if-exists does not update a file when the markdown changes (delete rows for that `source_file` and re-run ingest + embed).
- Chat depends on a local Ollama process; the API is not fully self-contained.
- Automated tests for `/chat` are not in this repo yet.

Natural next steps: token-based chunking, an HNSW index, re-ingest on file hash change, streaming chat responses, and pytest coverage for search ranking and prompt assembly.

---

## License

Personal / portfolio project. Add a license file if you publish this as an open repository.
