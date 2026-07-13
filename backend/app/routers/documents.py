from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlmodel import Session, select
import fitz

from app import schemas
from app import models
from app import database
from app.services.ai import answer_question_with_context
from app.services.ingestion import chunk_text
from app.services import vector_store
from app.services.auth import get_current_user

router = APIRouter(tags=["documents"])


@router.post("/documents", response_model=schemas.DocumentResponse, status_code=201)
def create_document(
    doc: schemas.DocumentCreate,
    user:models.User=Depends(get_current_user),
    session: Session = Depends(database.get_session),
):
    document = models.Document(title=doc.title, content=doc.content,user_id=user.id)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.post("/documents/upload", response_model=schemas.DocumentResponse, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    user:models.User=Depends(get_current_user),
    session: Session = Depends(database.get_session),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = file.file.read()
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""
    for page in pdf_document:
        text += page.get_text()

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Save full text to PostgreSQL as source of truth
    document = models.Document(title=file.filename, content=text,user_id=user.id)
    session.add(document)
    session.commit()
    session.refresh(document)

    # Chunk and embed into ChromaDB for semantic search
    chunks = chunk_text(text=text)
    vector_store.add_document_chunks(document_id=document.id, chunks=chunks)

    return document


@router.post("/ask", response_model=schemas.AnswerResponse)
def ask_question(
    req: schemas.QuestionRequest,
    user:models.User=Depends(get_current_user),
    session: Session = Depends(database.get_session),
):
    document = session.get(models.Document, req.document_id)
    if not document or document.user_id !=user.id:
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
        select(models.Conversation)
        .where(models.Conversation.user_id == user.id)
        .where(models.Conversation.document_id == req.document_id)
        .order_by(models.Conversation.created_at.desc())
        .limit(3)
    ).all()
    
    history = [
    {"question": c.question, "answer": c.answer}
    for c in reversed(recent)
    ]

    answer = answer_question_with_context(question=req.question, chunks=relevant_chunks,history=history)

     # Persist this turn so it becomes context for the next question
    session.add(models.Conversation(
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


@router.get("/documents", response_model=list[schemas.DocumentResponse])
def list_documents(
    session: Session = Depends(database.get_session),
    user: models.User = Depends(get_current_user)
):
    documents = session.exec(select(models.Document).where(models.Document.user_id==user.id)).all()
    return documents


@router.get("/documents/{document_id}", response_model=schemas.DocumentResponse)
def get_document(
    document_id: int, 
    user: models.User = Depends(get_current_user),
    session: Session = Depends(database.get_session)
):
    document = session.get(models.Document, document_id)
    if not document or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    user:models.User = Depends(get_current_user),
    session: Session = Depends(database.get_session)):
    document = session.get(models.Document, document_id)
    if not document or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete chunks from ChromaDB before removing the document row
    vector_store.delete_document_chunks(document_id=document_id)
    session.delete(document)
    session.commit()

    return {"message": "Document deleted"}