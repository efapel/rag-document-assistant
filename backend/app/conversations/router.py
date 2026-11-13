from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.database import get_session
from app.documents.models import Document
from app.conversations import schemas
from app.conversations.models import Conversation
from app.rag import vector_store
from app.rag.llm import answer_question_with_context

router = APIRouter(tags=["documents"])


@router.post("/ask", response_model=schemas.AnswerResponse)
def ask_question(
    req: schemas.QuestionRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    document = session.get(Document, req.document_id)
    if not document or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    relevant_chunks = vector_store.query_similar_chunks(
        document_id=req.document_id,
        question=req.question,
    )

    if not relevant_chunks:
        raise HTTPException(
            status_code=422,
            detail="No indexed content found for this document. Please re-upload the PDF.",
        )

    # Fetch the last 3 turns for this user and document, oldest first
    recent = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .where(Conversation.document_id == req.document_id)
        .order_by(Conversation.created_at.desc())
        .limit(3)
    ).all()

    history = [
        {"question": c.question, "answer": c.answer}
        for c in reversed(recent)
    ]

    answer = answer_question_with_context(
        question=req.question, chunks=relevant_chunks, history=history
    )

    # Persist this turn so it becomes context for the next question
    session.add(Conversation(
        user_id=user.id,
        document_id=req.document_id,
        question=req.question,
        answer=answer,
    ))
    session.commit()

    return {
        "answer": answer,
        "document_id": document.id,
        "document_title": document.title,
        "source_chunks": relevant_chunks,
    }
