from unittest import result
import ollama
from sqlalchemy.orm import query
from search import search

def generate_answer(question: str, top_k: int = 5) -> dict:
    
    # 1. Retrive relevant chunks from pgvector
    results = search(query=question, top_k=top_k)

    # 2.combine retrieved chunks into a single context string
    context = "\n\n---\n\n".join(
        result.content for result in results)

    # 3.Build the RAG prompt 

    
    prompt = f"""
    You are a technical assistant for the project documentation.

    Your job is to answer the user's question using the CONTEXT provided below.

    IMPORTANT RULES:
    1. Use the context as your primary source of information.
    2. Answer directly and clearly.
    3. Do not say that information is missing if the context contains relevant information.
    4. Do not invent information that is not present in the context.
    5. If the context genuinely does not contain the answer, say:
    "I could not find the answer in the provided documentation."

    Context:  {context}

    Question: {question}
    Answer:
    """
    # 4. send context and question to ollama
    response = ollama.chat(
        model="llama3.2:3b", 
        messages=[
            {
                "role": "system",
                "content": prompt
            }
            ]
            )
    # 5. Return the answer
    answer = response["message"]["content"].strip()

    if answer.startswith("assistant"):
        answer = answer[len("assistant"):].strip()

    return {
        "answer": answer,
        "sources": [
            {
                "source_file": result.source_file,
                "content": result.content
            }
            for result in results
        ]
    }

