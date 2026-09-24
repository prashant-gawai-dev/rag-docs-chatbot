import os
from database import SessionLocal
from model import DocumentChunk, DocumentChunkV2
from chunker import chunk_text

def ingest_file(filepath: str, db, model_class=DocumentChunk):
    existing = (
        db.query(model_class)
        .filter(model_class.source_file == filepath)
        .first()
    )
    if existing:
        print(f"{filepath} already ingested, skipping..")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)

    for chunk in chunks:
        new_chunk = model_class(
            source_file=filepath, content=chunk, embedding=None
        )
        db.add(new_chunk)
    db.commit()
    print(f"Ingested {len(chunks)} chunks from {filepath}")

if __name__ == "__main__":
    db = SessionLocal()
    ingest_file("source_docs/PROJECT_DOCUMENTATION.md", db)                  
    ingest_file("source_docs/PROJECT_RUNBOOK.md", db)                        
    ingest_file("source_docs/goldenpi_payment_escalation_knowledge_doc.md", db, DocumentChunkV2)       
    db.close()