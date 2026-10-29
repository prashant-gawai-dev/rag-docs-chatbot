import re
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChunkingSettings(BaseSettings):
    chunk_size: int = 500
    chunk_overlap: int = 75
    min_chunk_size: int = 100
    max_chunk_size: int = 700
    chunking_strategy: str = "markdown_recursive"
    preserve_headings: bool = True
    preserve_metadata: bool = True
    remove_duplicates: bool = True
    clean_text: bool = True
    embedding_batch_size: int = 32
    default_search_table: str = "document_chunks"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_chunking(self):
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        if self.min_chunk_size <= 0:
            raise ValueError("min_chunk_size must be positive")
        if self.max_chunk_size < self.chunk_size:
            raise ValueError("max_chunk_size must be >= chunk_size")
        if self.embedding_batch_size <= 0:
            raise ValueError("embedding_batch_size must be positive")
        if not re.fullmatch(r"^[A-Za-z_][A-Za-z0-9_]*$", self.default_search_table):
            raise ValueError("default_search_table is not a valid PostgreSQL table name")
        if self.chunking_strategy not in {
            "markdown_recursive",
            "recursive",
            "fixed",
        }:
            raise ValueError("Unsupported chunking strategy")
        return self


chunking_settings = ChunkingSettings()
