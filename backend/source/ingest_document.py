#!/usr/bin/env python3
"""Chunk, embed, and store a document in the configured Neon/PostgreSQL database."""

import argparse
import json
import re
import sys
from pathlib import Path

from sqlalchemy import text

from config import chunking_settings
from database import engine
from ingest.chunker import chunk_text


SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt"}
TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def read_document(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type '{path.suffix}'. Use: {supported}")

    return path.read_text(encoding="utf-8-sig")


def validate_table_name(table_name: str) -> str:
    if not TABLE_NAME_PATTERN.fullmatch(table_name):
        raise ValueError(
            "table_name must start with a letter or underscore and contain only "
            "letters, numbers, and underscores"
        )
    return table_name


def ingest_document(
    filepath: str | Path,
    table_name: str = "document_chunks",
    chunk_size: int | None = None,
    overlap: int | None = None,
    strategy: str | None = None,
) -> int:
    chunk_size = chunk_size if chunk_size is not None else chunking_settings.chunk_size
    overlap = overlap if overlap is not None else chunking_settings.chunk_overlap
    strategy = strategy or chunking_settings.chunking_strategy
    table_name = validate_table_name(table_name)
    if engine is None:
        raise RuntimeError("DATABASE_URL is not configured")

    path = Path(filepath).expanduser().resolve()
    text_content = read_document(path)
    chunks = chunk_text(
        text_content,
        chunk_size=chunk_size,
        overlap=overlap,
        min_chunk_size=chunking_settings.min_chunk_size,
        max_chunk_size=chunking_settings.max_chunk_size,
        strategy=strategy,
        preserve_headings=chunking_settings.preserve_headings,
        remove_duplicates=chunking_settings.remove_duplicates,
    )
    if not chunks:
        raise ValueError(f"Document contains no text: {path}")

    # SentenceTransformer downloads/caches the model the first time it is used.
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(
        [chunk.embedding_text for chunk in chunks],
        batch_size=chunking_settings.embedding_batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    quoted_table = engine.dialect.identifier_preparer.quote(table_name)
    source_file = str(path)

    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

            # The requested table is created only when this document is ingested.
            connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {quoted_table} (
                    id SERIAL PRIMARY KEY,
                    source_file TEXT NOT NULL,
                    section TEXT NOT NULL DEFAULT '',
                    chunk_index INTEGER NOT NULL DEFAULT 0,
                    document_version INTEGER NOT NULL DEFAULT 1,
                    content_hash TEXT NOT NULL DEFAULT '',
                    content TEXT NOT NULL,
                    embedding_text TEXT NOT NULL DEFAULT '',
                    embedding vector(384)
                )
            """))

            for column_definition in (
                "section TEXT NOT NULL DEFAULT ''",
                "chunk_index INTEGER NOT NULL DEFAULT 0",
                "document_version INTEGER NOT NULL DEFAULT 1",
                "content_hash TEXT NOT NULL DEFAULT ''",
                "embedding_text TEXT NOT NULL DEFAULT ''",
            ):
                column_name = column_definition.split()[0]
                connection.execute(text(
                    f"ALTER TABLE {quoted_table} ADD COLUMN IF NOT EXISTS {column_definition}"
                ))

            current_version = connection.execute(
                text(f"SELECT COALESCE(MAX(document_version), 0) FROM {quoted_table} "
                     "WHERE source_file = :source_file"),
                {"source_file": source_file},
            ).scalar() or 0

            connection.execute(
                text(f'DELETE FROM {quoted_table} WHERE source_file = :source_file'),
                {"source_file": source_file},
            )

            insert_statement = text(f"""
                INSERT INTO {quoted_table} (
                    source_file, section, chunk_index, document_version,
                    content_hash, content, embedding_text, embedding
                )
                VALUES (
                    :source_file, :section, :chunk_index, :document_version,
                    :content_hash, :content, :embedding_text, CAST(:embedding AS vector)
                )
            """)
            for chunk_index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                connection.execute(insert_statement, {
                    "source_file": source_file,
                    "section": chunk.section,
                    "chunk_index": chunk_index,
                    "document_version": current_version + 1,
                    "content_hash": chunk.content_hash,
                    "content": chunk.content,
                    "embedding_text": chunk.embedding_text,
                    "embedding": json.dumps(embedding.tolist()),
                })
    except Exception:
        raise

    return len(chunks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chunk, embed, and store a Markdown or text file in Neon/PostgreSQL."
    )
    parser.add_argument("file_path", help="Path to a .md, .markdown, or .txt file")
    parser.add_argument("--table", default="document_chunks")
    parser.add_argument("--chunk-size", type=int)
    parser.add_argument("--overlap", type=int)
    parser.add_argument(
        "--strategy",
        choices=("markdown_recursive", "recursive", "fixed"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        count = ingest_document(
            args.file_path,
            table_name=args.table,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            strategy=args.strategy,
        )
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Stored {count} chunks from {Path(args.file_path).expanduser().resolve()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
