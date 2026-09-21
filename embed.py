from sentence_transformers import SentenceTransformer
from database import SessionLocal
from model import DocumentChunk

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_all_chunks(db):
    chunks = db.query(DocumentChunk).filter(DocumentChunk.embedding.is_(None)).all()
    print(f"Found {len(chunks)} chunks needing embeddings")

    for chunk in chunks:
        vector = model.encode(chunk.content)
        chunk.embedding = vector.tolist()

    db.commit()
    print("Done")

if __name__ == "__main__":
    db = SessionLocal()
    embed_all_chunks(db)
    db.close()