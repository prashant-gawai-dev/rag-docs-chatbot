import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

load_dotenv(os.getenv("APP_ENV_FILE") or None)

# Import for application-wide logging configuration side effects.
from api import logging_config  # noqa: F401
from api.chat import generate_answer
from search.search import search



logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Documents Chatbot",
    description="RAG API using FastAPI, PostgreSQL, pgvector and Ollama",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:5174,http://127.0.0.1:5174",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    table_name: str | None = None

class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    table_name: str | None = None

class IngestDocumentRequest(BaseModel):
    file_path: str
    table_name: str = "document_chunks"
    chunk_size: int | None = None
    overlap: int | None = None
    strategy: str | None = None

@app.get("/")
def root():
    return {"message": "Welcome to the RAG Document Search API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/search")
def search_documents(request: SearchRequest):
    try:
        results = search(request.query, request.top_k, request.table_name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception("Document search failed")
        raise HTTPException(status_code=500, detail="Document search failed") from error

    return {"query": request.query, "results": results}

@app.post("/chat")
def chat_documents(request : ChatRequest):
    logger.info("main/ Question received in chat function")
    return generate_answer(
        question=request.query,
        top_k=request.top_k,
        table_name=request.table_name
    )

@app.post("/documents/ingest")
def ingest_document_endpoint(request: IngestDocumentRequest):
    from ingest_document import ingest_document

    try:
        chunk_count = ingest_document(
            filepath=request.file_path,
            table_name=request.table_name,
            chunk_size=request.chunk_size,
            overlap=request.overlap,
            strategy=request.strategy,
        )
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except SQLAlchemyError as error:
        logger.exception("Document ingestion database operation failed")
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Please retry ingestion.",
        ) from error

    return {
        "message": "Document ingested successfully",
        "file_path": request.file_path,
        "table_name": request.table_name,
        "chunk_count": chunk_count,
    }