from sqlmodel import SQLModel, Field
from typing import Optional

class Document(SQLModel, table=True):
    id: Optional[int]=Field(default=None, primary_key=True)
    title:str
    content:str
    user_id:int=Field(foreign_key="user.id")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str