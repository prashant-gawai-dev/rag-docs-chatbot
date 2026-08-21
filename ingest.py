import os
from database import SessionLocal
from model import DocumentChunk as DocumentChunkModel
from chunker import chunk_text


def ingest_file(filepath: str, db):
    existing = (
        db.query(DocumentChunkModel)
        .filter(DocumentChunkModel.source_file == filepath)
        .first()
    )
    if existing:
        print(f"{filepath} already ingested, skipping..")
        return

    with open(filepath, "r") as f:
        text = f.read()

    chunks = chunk_text(text)

    for chunk in chunks:
        new_chuncks = DocumentChunkModel(
            source_file=filepath, content=chunk, embedding=None
        )
        db.add(new_chuncks)
    db.commit()
    print(f"Ingested {len(chunks)} chunks from {filepath}")


if __name__ == "__main__":
    db = SessionLocal()
    ingest_file("source_docs/PROJECT_DOCUMENTATION.md", db)
    ingest_file("source_docs/PROJECT_RUNBOOK.md", db)
    db.close()
