import ollama
from search import search, GpiPaymentsSearch
import logging

logger = logging.getLogger(__name__)

def generate_answer(question: str, top_k: int = 5) -> dict:
    logger.info("chat/ Question received in chat/generate_answer")
    # 1. Retrive relevant chunks from pgvector
    logger.info("chat/ Enterring Search.py....")
    results = GpiPaymentsSearch(query=question, top_k=top_k)
    logger.info("chat/ back to chat and search is completed")
    # 2.combine retrieved chunks into a single context string
    logger.info("chat/ combining all result.content values into one string, separated by \n\n---\n\n")

    context = "\n\n---\n\n".join(
        result.content for result in results)

    # 3.Build the RAG prompt 

    logger.info("chat/ Building RAG promt for ollama...")
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
    
    logger.info("chat/ Sending RAG promt in terms of context and question to ollama...")

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
    logger.info("chat/ Response receved from ollama...")
    logger.info("chat/ Getting the response text and clean extra whitespace....")

    answer = response["message"]["content"].strip()
    logger.info("chat/ Removing 'assistant' if the response unnecessarily starts with it...")

    if answer.startswith("assistant"):
        answer = answer[len("assistant"):].strip()
    logger.info("chat/ Final answer is ready...")
    
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

