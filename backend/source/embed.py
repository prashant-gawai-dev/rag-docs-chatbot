from sentence_transformers import SentenceTransformer
from database import SessionLocal
from model import DocumentChunk, DocumentChunkV2

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_all_chunks(db, model_class=DocumentChunk):
    chunks = db.query(model_class).filter(model_class.embedding.is_(None)).all()
    print(f"Found {len(chunks)} chunks needing embeddings")

    for chunk in chunks:
        vector = model.encode(chunk.content)
        chunk.embedding = vector.tolist()

    db.commit()
    print("Done")

if __name__ == "__main__":
    db = SessionLocal()
    embed_all_chunks(db, DocumentChunk)      # table 1: document_chunks
    embed_all_chunks(db, DocumentChunkV2)    # table 2: document_chunks_v2
    db.close()