from fastapi import FastAPI,HTTPException

from app import schemas


app=FastAPI()

documents_db:dict[int,dict]={}
counter=0

@app.get("/health")
async def health_check():
    return {"status":"ok", "message":"AcademiQ is running"}

@app.post("/documents",response_model=schemas.DocumentResponse,status_code=201)
async def create_document(doc:schemas.DocumentCreate):
    #TODO after db codes added id will be given automatically
    global counter
    counter += 1
    document={"id":counter,"title":doc.title,"content":doc.content}
    documents_db[counter]=document
    return document

@app.get("/documents",response_model=list[schemas.DocumentResponse])
async def list_documents():
    return list(documents_db.values())

@app.get("/documents/{document_id}",response_model=schemas.DocumentResponse)
async def get_document(document_id:int):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents_db[document_id]

@app.delete("/documents/{document_id}")
async def delete_document(document_id:int):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    del documents_db[document_id]
    return {"message": "Document deleted"}
