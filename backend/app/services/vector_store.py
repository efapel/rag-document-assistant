import chromadb
from app.services import ai


_collection = None

def get_collection() -> chromadb.Collection:
    """Return the ChromaDB collection, creating the client on first use."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path="./chroma_db")
        #HNSW (Hierarchical Navigable Small World)
        _collection = client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection  

def add_document_chunks(document_id: int, chunks: list[str]) -> None:
    """Embed and store a document's chunks in ChromaDB."""
    collection = get_collection()

    embeddings = [ai.embed_text(chunk) for chunk in chunks]
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )

def query_similar_chunks(document_id: int, question: str, top_k: int = 5) -> list[dict]:
    """Retrieve the most semantically similar chunks for a question.

    Args:
        document_id: ID of the document to search within.
        question: User's question to compare against stored chunks.
        top_k: Maximum number of chunks to return.

    Returns:
        List of chunk texts ordered by similarity (most relevant first).
    """
    collection = get_collection()

    # Can't request more chunks than exist for this document
    existing = collection.get(where={"document_id": {"$eq": document_id}})
    n_chunks = len(existing["ids"])

    if n_chunks == 0:
        return []

    actual_top_k = min(top_k, n_chunks)
    question_embedding = ai.embed_text(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=actual_top_k,
        where={"document_id": {"$eq": document_id}}
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    return [
        {
            "text": doc,
            "chunk_index": meta["chunk_index"],
            "similarity_score": round(1 - dist, 4)
        }
        for doc, dist, meta in zip(documents, distances, metadatas)
    ]

def delete_document_chunks(document_id: int) -> None:
    """Delete all chunks belonging to a document from ChromaDB."""
    collection = get_collection()

    existing = collection.get(where={"document_id": {"$eq": document_id}})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])