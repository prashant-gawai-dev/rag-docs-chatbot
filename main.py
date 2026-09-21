from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import query
from search import search
from chat import generate_answer

app = FastAPI(
    title="RAG Documents Chatbot",
    description="RAG API using FastAPI, PostgreSQL, pgvector and Ollama",
    version="1.0.0",
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
    return generate_answer(
        question=request.query,
        top_k=request.top_k
    )
