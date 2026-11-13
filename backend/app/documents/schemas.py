from pydantic import BaseModel

from app.core.types import NonEmptyStr, PositiveId, ShortText


class DocumentCreate(BaseModel):
    title: ShortText
    content: NonEmptyStr


class DocumentResponse(BaseModel):
    id: PositiveId
    title: NonEmptyStr
    content: NonEmptyStr
