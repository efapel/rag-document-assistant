from pydantic import BaseModel
from datetime import datetime


class DocumentOut(BaseModel):
    id: int
    filename: str
    original_name: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    question: str
    document_id: int | None = None  # None = tüm dokümanlarda ara


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]  # hangi chunk'lardan geldi
