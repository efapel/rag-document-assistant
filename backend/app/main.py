from fastapi import FastAPI,HTTPException,Depends, UploadFile, File
from sqlmodel import Session,select
import fitz

from app import schemas
from app import models
from app import database




app=FastAPI()



@app.on_event("startup")
def on_startup():
    database.create_tables()

@app.get("/health")
async def health_check():
    return {"status":"ok", "message":"AcademiQ is running"}

@app.post("/documents",response_model=schemas.DocumentResponse,status_code=201)
def create_document(doc:schemas.DocumentCreate,session:Session=Depends(database.get_session)):
    document=models.Document(title=doc.title,content=doc.content)
    session.add(document)
    session.commit()
    session.refresh(document)

    return document

@app.post("/documents/upload",response_model=schemas.DocumentResponse, status_code=201)
def upload_document(file: UploadFile = File(...), session: Session = Depends(database.get_session)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = file.file.read()
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""   
    for page in pdf_document:
        text += page.get_text()

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    document = models.Document(title=file.filename, content=text)
    session.add(document)
    session.commit()
    session.refresh(document)

    return document

@app.get("/documents",response_model=list[schemas.DocumentResponse])
def list_documents(session:Session=Depends(database.get_session)):
    documents = session.exec(select(models.Document)).all()
    return documents

@app.get("/documents/{document_id}",response_model=schemas.DocumentResponse)
def get_document(document_id:int,session:Session=Depends(database.get_session)):
    document=session.get(models.Document,document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.delete("/documents/{document_id}")
def delete_document(document_id:int,session:Session=Depends(database.get_session)):
    document=session.get(models.Document,document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    session.delete(document)
    session.commit()
    return {"message": "Document deleted"}
