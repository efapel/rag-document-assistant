from app.rag.client import client

_EMBED_BATCH_SIZE = 100


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed many texts in as few API calls as possible.

    Returns embeddings in the same order as the input texts.
    """
    if not texts:
        return []

    embeddings: list[list[float]] = []
    for start in range(0, len(texts), _EMBED_BATCH_SIZE):
        batch = texts[start : start + _EMBED_BATCH_SIZE]
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch,
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        embeddings.extend(item.embedding for item in ordered)

    return embeddings


def embed_text(text: str) -> list[float]:
    """Convert a single text into a 1536-dimensional embedding vector."""
    return embed_texts([text])[0]
