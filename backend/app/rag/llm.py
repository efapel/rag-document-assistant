from app.rag.client import client

SYSTEM_PROMPT = (
    "You are an academic assistant. "
    "Answer the question based only on the provided context. "
    "If the context doesn't contain the answer, say so."
)


def answer_question_with_context(
    question: str,
    chunks: list[dict],
    history: list[dict] | None = None,
) -> str:
    """Generate an answer using semantically retrieved chunks as context.

    Args:
        question: User's question to answer.
        chunks: Relevant text chunks retrieved from ChromaDB.
        history: Previous question/answer turns, oldest first.

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
