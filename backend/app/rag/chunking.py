import re

from app.rag.embeddings import embed_texts
import numpy as np

def sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))

def _split_into_sentences(text: str) -> list[str]:
    """Clean PDF artifacts and split text into normalized sentences."""
    if not text:
        return []

    cleaned = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    cleaned = re.sub(r'\n\s*\n+', '.\n', cleaned)

    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"“0-9])', cleaned)

    # 5. Çok kısa gürültüleri (tek harf, boşluk veya salt sembol) filtrele
    return [s.strip() for s in sentences if len(s.strip()) > 3]


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


def _chunk_by_semantic_maxmin(text: str,
    hard_thr: float = 0.55,
    c: float = 1.2,
    init_const: float = 1.0,
    max_sentences: int = 15) -> list[list[float]]:
   
    sentences = _split_into_sentences(text)
    if not sentences:
        return []

    embeddings = embed_texts(sentences)

    chunks = []
    current_sentences = [sentences[0]]
    current_embeddings = [embeddings[0]]

    for i in range(1, len(sentences)):
        s_candidate = sentences[i]
        emb_candidate = embeddings[i]

        cardinality = len(current_sentences)

        # Zorunlu sınır: Chunk çok uzadıysa doğrudan böl
        if cardinality >= max_sentences:
            chunks.append(" ".join(current_sentences))
            current_sentences = [s_candidate]
            current_embeddings = [emb_candidate]
            continue

        if cardinality == 1:
            sim_init = float(np.dot(current_embeddings[0], emb_candidate))
            if init_const * sim_init > hard_thr:
                current_sentences.append(s_candidate)
                current_embeddings.append(emb_candidate)
            else:
                chunks.append(" ".join(current_sentences))
                current_sentences = [s_candidate]
                current_embeddings = [emb_candidate]
            continue

        
        similarities_with_candidate = [
            float(np.dot(emb, emb_candidate)) for emb in current_embeddings
        ]
        max_sim = max(similarities_with_candidate)

        
        curr_matrix = np.array(current_embeddings)
        sim_matrix = np.dot(curr_matrix, curr_matrix.T)

        np.fill_diagonal(sim_matrix, np.inf)
        min_sim_chunk = float(np.min(sim_matrix))

        dynamic_thr = max(c * min_sim_chunk * sigmoid(cardinality), hard_thr)

        if max_sim >= dynamic_thr:
            current_sentences.append(s_candidate)
            current_embeddings.append(emb_candidate)
        else:
            chunks.append(" ".join(current_sentences))
            current_sentences = [s_candidate]
            current_embeddings = [emb_candidate]

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks

    



def chunk_text(text: str, strategy: str = "semantic_maxmin") -> list[str]:
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
        return _chunk_by_sentences(text, chunk_size=10, overlap=1)
    elif strategy == "char":
        return _chunk_by_chars(text, chunk_size=500, overlap=50)
    elif strategy == "semantic_maxmin":
            return _chunk_by_semantic_maxmin(text)
    raise ValueError(f"Unknown chunking strategy: {strategy}")
