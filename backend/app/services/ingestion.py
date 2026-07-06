import re

def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _chunk_by_sentences(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks of whole sentences."""
    sentences = _split_into_sentences(text)
    chunks = []
    start = 0
    while start < len(sentences):
        end = min(start + chunk_size, len(sentences))
        chunk = " ".join(sentences[start:end])
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def _chunk_by_chars(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks of fixed character length."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def chunk_text(text: str, strategy: str = "sentence") -> list[str]:
    """Split document text into chunks using the given strategy.

    Args:
        text: Raw document text to split.
        strategy: Chunking method — 'sentence' or 'char'.

    Returns:
        List of text chunks ready for embedding.

    Raises:
        ValueError: If the strategy is not recognized.
    """
    if strategy == "sentence":
        return _chunk_by_sentences(text, chunk_size=5, overlap=1)
    if strategy == "char":
        return _chunk_by_chars(text, chunk_size=500, overlap=50)
    raise ValueError(f"Unknown chunking strategy: {strategy}")