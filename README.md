# RAG Docs Chatbot

A full-stack retrieval-augmented generation (RAG) application for answering questions from Markdown and text documents. The backend chunks documents, creates 384-dimensional embeddings, stores chunks in PostgreSQL/Neon with pgvector, retrieves relevant evidence, and uses a local Ollama model to generate grounded answers.

## Features

- React and Vite chat interface
- FastAPI search, chat, health, and document-ingestion endpoints
- Markdown-aware recursive chunking with configurable token limits and overlap
- Heading-path, source, chunk, version, and content-hash metadata
- Context-enriched embeddings while preserving original chunk text
- Dynamic PostgreSQL tables for separate document collections
- Default search-table configuration with per-request table overrides
- Local answer generation with Ollama; no hosted LLM API key required
- Neon connection pooling and database retry handling

## Technology stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19, Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL or Neon |
| Vector search | pgvector |
| ORM | SQLAlchemy 2 |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) |
| Answer generation | Ollama (`llama3.2:3b`) |
| Configuration | Pydantic Settings and `.env` |

## How it works

```text
Document (.md, .markdown, or .txt)
        |
        v
Clean and validate text
        |
        v
Markdown-aware recursive token chunking
        |
        v
Add headings and source metadata
        |
        v
Generate contextual embeddings
        |
        v
Store chunks + embeddings in pgvector
        |
        v
Question -> query embedding -> nearest chunks -> Ollama -> answer
```

Chunking uses tokens rather than characters. The default pipeline targets 500 tokens per chunk, uses 75-token overlap, and limits normal chunks to 700 tokens.

## Project structure

```text
rag-docs-chatbot/
├── backend/source/
│   ├── api/
│   │   ├── main.py          # FastAPI application and routes
│   │   ├── chat.py          # Evidence-grounded answer generation
│   │   └── logging_config.py
│   ├── ingest/
│   │   └── chunker.py       # Markdown/token-aware chunking
│   ├── search/
│   │   └── search.py        # Query embedding and pgvector retrieval
│   ├── config.py            # Validated environment configuration
│   ├── database.py          # SQLAlchemy engine and sessions
│   ├── ingest_document.py   # Ingestion CLI and shared ingestion function
│   ├── model.py             # SQLAlchemy document chunk model
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── .env                     # Local configuration; never commit secrets
├── start_app.sh             # Start both applications
└── stop_app.sh              # Stop project processes
```

## Prerequisites

- Python 3.12 or newer
- Node.js and npm
- PostgreSQL with the `vector` extension, or Neon PostgreSQL
- Ollama with the required chat model
- Internet access for the first embedding-model download

## Installation

### 1. Create Python and frontend environments

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/source/requirements.txt
cd frontend
npm install
cd ..
```

### 2. Configure PostgreSQL

Create a database and ensure the connection account can create the `vector` extension and tables. For example, run this when required:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Pull the Ollama model

```bash
ollama pull llama3.2:3b
ollama serve
```

If Ollama is already running, skip the last command. Keep Ollama available while using `/chat`.

## Environment configuration

Create a root `.env` file and keep database credentials private.

```env
APP_ENV=local
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST/DATABASE?sslmode=require
VITE_API_BASE_URL=http://127.0.0.1:8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DEFAULT_SEARCH_TABLE=knowledge_docs

CHUNK_SIZE=500
CHUNK_OVERLAP=75
MIN_CHUNK_SIZE=100
MAX_CHUNK_SIZE=700
CHUNKING_STRATEGY=markdown_recursive
PRESERVE_HEADINGS=true
PRESERVE_METADATA=true
REMOVE_DUPLICATES=true
CLEAN_TEXT=true
EMBEDDING_BATCH_SIZE=32
```

Configuration reference:

| Setting | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL/Neon SQLAlchemy connection URL |
| `DEFAULT_SEARCH_TABLE` | Default collection used by search and chat |
| `CHUNK_SIZE` | Target chunk size in tokens |
| `CHUNK_OVERLAP` | Overlapping tokens between chunks |
| `MIN_CHUNK_SIZE` | Preferred minimum chunk size |
| `MAX_CHUNK_SIZE` | Maximum normal chunk size |
| `CHUNKING_STRATEGY` | `markdown_recursive`, `recursive`, or `fixed` |
| `PRESERVE_HEADINGS` | Prefix chunks with their Markdown heading path |
| `PRESERVE_METADATA` | Preserve source and section metadata |
| `REMOVE_DUPLICATES` | Remove repeated chunk content |
| `CLEAN_TEXT` | Normalize extracted text |
| `EMBEDDING_BATCH_SIZE` | Number of chunks encoded per batch |
| `VITE_API_BASE_URL` | Backend URL used by the frontend |

`DEFAULT_SEARCH_TABLE` and dynamic table names must start with a letter or underscore and contain only letters, numbers, and underscores.

## Running the application

From the repository root:

```bash
chmod +x start_app.sh stop_app.sh
./start_app.sh
```

The launcher:

- Creates the Python virtual environment if needed
- Installs backend dependencies
- Installs frontend dependencies if absent
- Starts the frontend at <http://localhost:5173>
- Starts FastAPI at <http://127.0.0.1:8000>

The interactive API documentation is available at <http://127.0.0.1:8000/docs>.

Stop both applications with:

```bash
./stop_app.sh
```

To run the backend manually:

```bash
PYTHONPATH=backend/source .venv/bin/python -m uvicorn api.main:app --app-dir backend/source --host 127.0.0.1 --port 8000 --reload
```

To run the frontend manually:

```bash
cd frontend
npm run dev
```

## Ingest a document

Supported formats are `.md`, `.markdown`, and `.txt`.

### Command line

```bash
cd backend/source
python ingest_document.py /absolute/path/to/document.md --table knowledge_docs
```

Override chunking for one ingestion:

```bash
python ingest_document.py /absolute/path/to/document.md \
  --table knowledge_docs \
  --chunk-size 500 \
  --overlap 75 \
  --strategy markdown_recursive
```

### API

```bash
curl -X POST http://127.0.0.1:8000/documents/ingest \
  -H 'Content-Type: application/json' \
  -d '{
    "file_path": "/absolute/path/to/document.md",
    "table_name": "knowledge_docs",
    "chunk_size": 500,
    "overlap": 75,
    "strategy": "markdown_recursive"
  }'
```

The ingestion workflow:

1. Reads and validates the document.
2. Cleans and chunks its text.
3. Preserves heading context and metadata.
4. Generates embeddings in configured batches.
5. Creates the requested table and `vector(384)` column if necessary.
6. Removes existing chunks for the same source path.
7. Inserts the new document version.

Re-ingestion replaces chunks for the same resolved file path instead of creating duplicate copies.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | API welcome message |
| `GET` | `/health` | Backend health check |
| `POST` | `/search` | Find nearest document chunks |
| `POST` | `/chat` | Retrieve evidence and generate an answer |
| `POST` | `/documents/ingest` | Chunk and ingest a local document |

### Search

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What should support do when payment succeeds but the order is missing?",
    "top_k": 5
  }'
```

Use `table_name` to search another collection:

```json
{
  "query": "payment reconciliation",
  "top_k": 5,
  "table_name": "payment_docs"
}
```

### Chat

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What should support do when payment succeeds but the order is missing?",
    "top_k": 5
  }'
```

Chat uses the same optional `table_name` field and returns the answer plus retrieved source metadata.

## Chunking strategies

- `markdown_recursive` — split by Markdown headings, then paragraphs, sentences, and token boundaries
- `recursive` — split using textual paragraph and sentence boundaries
- `fixed` — deterministic fixed-size token chunks for baseline comparisons

Markdown heading paths are retained with chunks. Context text used for embedding can include heading context, while the original document text remains stored separately.

When chunking or embedding configuration changes, re-run ingestion for affected documents. Chunks created with a previous embedding model must be regenerated before using that model for search.

## Database schema

Dynamic ingestion tables contain:

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | `SERIAL` | Row identifier |
| `source_file` | `TEXT` | Absolute resolved document path |
| `section` | `TEXT` | Markdown heading path |
| `chunk_index` | `INTEGER` | Position within the document |
| `document_version` | `INTEGER` | Ingestion generation |
| `content_hash` | `TEXT` | Deduplication and change detection |
| `content` | `TEXT` | Original chunk text |
| `embedding_text` | `TEXT` | Heading-enriched text encoded into the vector |
| `embedding` | `vector(384)` | Normalized embedding |

SQLAlchemy uses pre-ping and connection recycling to tolerate temporary database connection interruptions.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `Connection refused` on port 8000 | Run `./start_app.sh` and inspect `backend.log` |
| Port already in use | Run `./stop_app.sh`, then start again |
| `DATABASE_URL is not configured` | Add a valid database URL to the root `.env` |
| Table or extension errors | Confirm pgvector is installed and the database role has required privileges |
| Ollama connection fails | Run `ollama serve`, then `ollama list` |
| Model not found | Run `ollama pull llama3.2:3b` |
| Empty search results | Confirm the document was ingested and embeddings are not null |
| Search uses the wrong collection | Pass `table_name`, or update `DEFAULT_SEARCH_TABLE` |
| Slow first ingestion or search | The embedding model is downloading or loading for the first time |
| Hugging Face rate-limit warning | Add an optional `HF_TOKEN` to the environment |

View application logs:

```bash
tail -f backend.log
tail -f frontend.log
```

Check backend health:

```bash
curl http://127.0.0.1:8000/health
```

## Security

- Never commit `.env`, database credentials, API keys, or tokenized database URLs.
- Never expose server-only values through variables prefixed with `VITE_`; Vite includes them in browser bundles.
- Dynamic table names are validated before SQL identifier interpolation.
- Rotate database credentials immediately if exposed in logs, screenshots, commits, or chat history.

## Validation

Compile the backend modules:

```bash
PYTHONPATH=backend/source .venv/bin/python -m compileall backend/source
```

Build the frontend:

```bash
cd frontend
npm run build
```

## License

Add a license file before publishing the repository as an open-source project.