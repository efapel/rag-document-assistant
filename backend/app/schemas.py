from pydantic import BaseModel

class DocumentCreate(BaseModel):
    title:str
    content:str

class DocumentResponse(BaseModel):
    id:int
    title:str
    content:str

    
class QuestionRequest(BaseModel):
    question: str
    document_id: int

class AnswerResponse(BaseModel):
    answer: str
    document_id: int
    document_title: str
