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


def answer_question_with_context(question: str, chunks: list[dict]) -> str:

    """Generate an answer using semantically retrieved chunks as context.

    Args:
        question: User's question to answer.
        chunks: Relevant text chunks retrieved from ChromaDB.

    Returns:
        LLM-generated answer based solely on the provided chunks.
    """
    # Format chunks with numbering so LLM can reference them
    context = "\n\n---\n\n".join(
        f"[Chunk {i + 1}]:\n{chunk}" for i, chunk in enumerate(chunks)
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
        ]
    )
    return response.choices[0].message.content

def embed_text(text: str) -> list[float]:
    """Convert text into a 1536-dimensional embedding vector."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    #text-embedding-3-small --> 1536 dimension
    #text-embedding-3-large -->3072 dimension
    return response.data[0].embedding