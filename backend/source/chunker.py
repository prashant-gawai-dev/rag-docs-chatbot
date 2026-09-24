def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


if __name__ == "__main__":
    test_chunks = chunk_text("a" * 1200)
    print(f"Number of chunks: {len(test_chunks)}")
    for i, c in enumerate(test_chunks):
        print(f"Chunk {i}: length {len(c)}")
