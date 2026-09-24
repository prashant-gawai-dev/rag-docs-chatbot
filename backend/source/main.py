from fastapi import FastAPI
from pydantic import BaseModel
import logging_config
import logging
from sqlalchemy.orm import query
from search import search
from chat import generate_answer

from fastapi.middleware.cors import CORSMiddleware



logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Documents Chatbot",
    description="RAG API using FastAPI, PostgreSQL, pgvector and Ollama",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class ChatRequest(BaseModel):
    query:str
    top_k: int = 5


@app.get("/")
def root():
    return {"message": "Welcome to the RAG Document Search API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/search")
def search_documents(request: SearchRequest):
    results = search(request.query, request.top_k)
    return {
        "query": request.query,
        "results": [
            {
                "content": result.content,
                "source_file": result.source_file,
                } for result in results
                ],
        }

@app.post("/chat")
def chat_documents(request : ChatRequest):
    logger.info("main/ Question received in chat function")
    return generate_answer(
        question=request.query,
        top_k=request.top_k
    )