import hashlib
import re
from dataclasses import dataclass

from transformers import AutoTokenizer


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)


@dataclass
class DocumentChunk:
    section: str
    content: str
    embedding_text: str
    content_hash: str


def clean_document(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def token_count(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def markdown_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    heading_path: list[str] = []
    current: list[str] = []

    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            if current:
                sections.append((" > ".join(heading_path), "\n".join(current).strip()))
                current = []

            level = len(match.group(1))
            heading = match.group(2)
            heading_path = heading_path[: level - 1]
            heading_path.append(heading)
            current.append(line)
        else:
            current.append(line)

    if current:
        sections.append((" > ".join(heading_path), "\n".join(current).strip()))

    return [(section, body) for section, body in sections if body.strip()]


def split_by_tokens(text: str, chunk_size: int, overlap: int) -> list[str]:
    if token_count(text) <= chunk_size:
        return [text.strip()] if text.strip() else []

    paragraphs = [part.strip() for part in re.split(r"\n\n+", text) if part.strip()]
    units = paragraphs if len(paragraphs) > 1 else re.split(r"(?<=[.!?])\s+", text)
    pieces: list[str] = []
    current = ""

    for unit in units:
        candidate = f"{current}\n\n{unit}".strip() if current else unit.strip()
        if token_count(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            pieces.append(current)
        if token_count(unit) <= chunk_size:
            current = unit
        else:
            pieces.extend(split_long_text_by_tokens(unit, chunk_size, overlap))
            current = ""

    if current:
        pieces.append(current)

    overlapped = []
    for index, piece in enumerate(pieces):
        if index == 0:
            overlapped.append(piece)
            continue
        overlap_text = tokens_to_text(piece_token_prefix(pieces[index - 1], overlap))
        combined = f"{overlap_text}\n\n{piece}".strip()
        overlapped.append(combined if token_count(combined) <= chunk_size else piece)

    return overlapped


def split_long_text_by_tokens(text: str, chunk_size: int, overlap: int) -> list[str]:
    tokens = tokenizer.encode(text, add_special_tokens=False)
    pieces = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        pieces.append(tokenizer.decode(tokens[start:end], skip_special_tokens=True).strip())
        if end >= len(tokens):
            break
        start = end - overlap
    return pieces


def piece_token_prefix(text: str, token_count_value: int) -> list[int]:
    if token_count_value <= 0:
        return []
    return tokenizer.encode(text, add_special_tokens=False)[-token_count_value:]


def tokens_to_text(tokens: list[int]) -> str:
    return tokenizer.decode(tokens, skip_special_tokens=True).strip()


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 75,
    min_chunk_size: int = 100,
    max_chunk_size: int = 700,
    strategy: str = "markdown_recursive",
    preserve_headings: bool = True,
    remove_duplicates: bool = True,
) -> list[DocumentChunk]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = clean_document(text)
    if not text:
        return []

    if strategy == "markdown_recursive":
        parts = markdown_sections(text)
        if not parts:
            parts = [("", text)]
    elif strategy in {"recursive", "fixed"}:
        parts = [("", text)]
    else:
        raise ValueError("Unsupported chunking strategy")

    chunks: list[DocumentChunk] = []
    for section, body in parts:
        body_parts = split_by_tokens(body, min(max_chunk_size, chunk_size), overlap)
        for part in body_parts:
            part = clean_document(part)
            if not part or token_count(part) > max_chunk_size:
                continue

            headings = section if preserve_headings else ""
            context = f"Topic: {headings}\n\n{part}" if headings else part
            digest = hashlib.sha256(context.encode("utf-8")).hexdigest()
            chunks.append(DocumentChunk(section, part, context, digest))

    if remove_duplicates:
        unique = []
        seen_hashes = set()
        for chunk in chunks:
            if chunk.content_hash not in seen_hashes:
                seen_hashes.add(chunk.content_hash)
                unique.append(chunk)
        chunks = unique

    return chunks
