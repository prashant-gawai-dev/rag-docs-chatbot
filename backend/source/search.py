from sentence_transformers import SentenceTransformer
from database import SessionLocal
from model import DocumentChunk,DocumentChunkV2
import logging

logger = logging.getLogger(__name__)
model = SentenceTransformer("all-MiniLM-L6-v2")


def search(query: str, top_k: int = 5):
    logger.info("search/ Question String received in search/search")

    logger.info("search/ Creating a new database session and stored it in the variable db")
    db = SessionLocal()
    logger.info("search/ Completed |Creating a new database session and stored it in the variable db")

    logger.info("search/ Converting the text in query into a numerical vector and then convert that vector into a normal Python list.")
    query_embedding = model.encode(query).tolist()
    logger.info("search/ Completed | Converting the text in query into a numerical vector and then convert that vector into a normal Python list.")

    logger.info("search/ Collecting result from model and passing query_embedding")
    results = (
        db.query(DocumentChunk)
        .order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        .limit(top_k)
        .all()
    )
    logger.info("search/ Received results from model returned to search.py closing db connection")
    db.close()
    logger.info("search/ Returning back to chat/")

    return results

def GpiPaymentsSearch(query: str, top_k: int = 5):
    logger.info("search/ Question String received in search/search")

    logger.info("search/ Creating a new database session and stored it in the variable db")
    db = SessionLocal()
    logger.info("search/ Completed |Creating a new database session and stored it in the variable db")

    logger.info("search/ Converting the text in query into a numerical vector and then convert that vector into a normal Python list.")
    query_embedding = model.encode(query).tolist()
    logger.info("search/ Completed | Converting the text in query into a numerical vector and then convert that vector into a normal Python list.")

    logger.info("search/ Collecting result from model and passing query_embedding")
    results = (
        db.query(DocumentChunkV2)
        .order_by(
            DocumentChunkV2.embedding.cosine_distance(query_embedding)
        )
        .limit(top_k)
        .all()
    )
    logger.info("search/ Received results from model returned to search.py closing db connection")
    db.close()
    logger.info("search/ Returning back to chat/")

    return results