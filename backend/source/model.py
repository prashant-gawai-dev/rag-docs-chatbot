import logging

from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector

from database import Base

logger = logging.getLogger(__name__)


class DocumentChunk(Base):
    """A text chunk and its embedding for a stored document."""

    # The table schema is created or updated by ingest_document.py.
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_file = Column(String, nullable=False, index=True)
    section = Column(String, nullable=False, default="")
    chunk_index = Column(Integer, nullable=False, default=0)
    document_version = Column(Integer, nullable=False, default=1)
    content_hash = Column(String(64), nullable=False, default="")
    content = Column(Text, nullable=False)
    embedding_text = Column(Text, nullable=False, default="")
    embedding = Column(Vector(384), nullable=True)
