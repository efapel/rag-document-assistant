from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlmodel import Session, select
import fitz

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.conversations.models import Conversation
from app.core.database import get_session
from app.documents import schemas
from app.documents.models import Document
from app.rag import vector_store
from app.rag.chunking import chunk_text

router = APIRouter(tags=["documents"])


@router.post("/documents", response_model=schemas.DocumentResponse, status_code=201)
def create_document(
    doc: schemas.DocumentCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    document = Document(title=doc.title, content=doc.content, user_id=user.id)
    session.add(document)
    session.commit()
    session.refresh(document)

    # Chunk and embed into ChromaDB for semantic search
    chunks = chunk_text(text=doc.content)
    vector_store.add_document_chunks(document_id=document.id, chunks=chunks)

    return document


@router.post("/documents/upload", response_model=schemas.DocumentResponse, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = file.file.read()
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is invalid or could not be opened.",
        ) from exc

    try:
        text = ""
        for page in pdf_document:
            text += page.get_text()
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="Text could not be extracted from the uploaded PDF.",
        ) from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Save full text to PostgreSQL as source of truth
    document = Document(title=file.filename, content=text, user_id=user.id)
    session.add(document)
    session.commit()
    session.refresh(document)

    try:
        # Chunk and embed into ChromaDB for semantic search
        chunks = chunk_text(text=text)
        vector_store.add_document_chunks(document_id=document.id, chunks=chunks)
    except Exception as exc:
        session.delete(document)
        session.commit()
        raise HTTPException(
            status_code=502,
            detail="Document was uploaded, but indexing failed. Please try again.",
        ) from exc

    return document


@router.get("/documents", response_model=list[schemas.DocumentResponse])
def list_documents(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    documents = session.exec(select(Document).where(Document.user_id == user.id)).all()
    return documents


@router.get("/documents/{document_id}", response_model=schemas.DocumentResponse)
def get_document(
    document_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    document = session.get(Document, document_id)
    if not document or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    document = session.get(Document, document_id)
    if not document or document.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .where(Conversation.document_id == document_id)
    ).all()
    for conversation in conversations:
        session.delete(conversation)

    # Delete chunks from ChromaDB before removing the document row
    vector_store.delete_document_chunks(document_id=document_id)
    session.delete(document)
    session.commit()

    return {"message": "Document deleted"}
