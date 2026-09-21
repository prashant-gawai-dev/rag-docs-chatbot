from sentence_transformers import SentenceTransformer
from database import SessionLocal
from model import DocumentChunk

model = SentenceTransformer("all-MiniLM-L6-v2")


def search(query: str, top_k: int = 5):
    db = SessionLocal()

    query_embedding = model.encode(query).tolist()

    results = (
        db.query(DocumentChunk)
        .order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        .limit(top_k)
        .all()
    )

    db.close()

    return results

    