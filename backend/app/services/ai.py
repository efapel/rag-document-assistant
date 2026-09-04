from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are an academic assistant. "
    "Answer the question based only on the provided context. "
    "If the context doesn't contain the answer, say so."
)


def answer_question_with_context(
    question: str, 
    chunks: list[dict],
    history: list[dict] | None = None
    ) -> str:

    """Generate an answer using semantically retrieved chunks as context.

    Args:
        question: User's question to answer.
        chunks: Relevant text chunks retrieved from ChromaDB.

    Returns:
        LLM-generated answer based solely on the provided chunks.
    """
    # Format chunks with numbering so LLM can reference them
    context = "\n\n---\n\n".join(
       f"[Chunk {i + 1}]:\n{chunk['text']}" for i, chunk in enumerate(chunks)
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Replay previous turns so the model can resolve pronouns and follow-ups
    for turn in history or []:
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["answer"]})

    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion:\n{question}",
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content


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