from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    document_id: int = Field(foreign_key="document.id")
    question: str
    answer: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
