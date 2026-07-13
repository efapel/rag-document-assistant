from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Document(SQLModel, table=True):
    id: Optional[int]=Field(default=None, primary_key=True)
    title:str
    content:str
    user_id:int=Field(foreign_key="user.id")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    document_id: int = Field(foreign_key="document.id")
    question: str
    answer: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )