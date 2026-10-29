import json
import logging
import re

from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from config import chunking_settings
from database import engine

logger = logging.getLogger(__name__)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_table_name(table_name: str) -> str:
    if not TABLE_NAME_PATTERN.fullmatch(table_name):
        raise ValueError("Invalid PostgreSQL table name")
    return table_name


def search(query: str, top_k: int = 5, table_name: str | None = None):
    if not query.strip():
        return []

    table_name = validate_table_name(table_name or chunking_settings.default_search_table)
    quoted_table = engine.dialect.identifier_preparer.quote(table_name)
    query_embedding = embedding_model.encode(query, normalize_embeddings=True).tolist()

    statement = text(f"""
        SELECT source_file, section, content
        FROM {quoted_table}
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
    """)

    with engine.connect() as connection:
        rows = connection.execute(statement, {
            "embedding": json.dumps(query_embedding),
            "top_k": top_k,
        })
        return [dict(row._mapping) for row in rows]
