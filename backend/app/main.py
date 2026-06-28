from fastapi import FastAPI,HTTPException,Depends
from sqlmodel import Session,select

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
