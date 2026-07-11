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


class SourceChunks(BaseModel):
    text:str
    chunk_index:int
    similarity_score:float


class AnswerResponse(BaseModel):
    answer: str
    document_id: int
    document_title: str
    source_chunks: list[SourceChunks]


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"