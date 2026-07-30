from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, StringConstraints


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ShortText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]
PasswordStr = Annotated[
    str,
    StringConstraints(min_length=6, max_length=128),
]
PositiveId = Annotated[int, Field(gt=0)]
ChunkIndex = Annotated[int, Field(ge=0)]
SimilarityScore = Annotated[float, Field(ge=0.0, le=1.0)]

class DocumentCreate(BaseModel):
    title: ShortText
    content: NonEmptyStr


class DocumentResponse(BaseModel):
    id: PositiveId
    title: NonEmptyStr
    content: NonEmptyStr

    
class QuestionRequest(BaseModel):
    question: NonEmptyStr
    document_id: PositiveId


class SourceChunks(BaseModel):
    text: NonEmptyStr
    chunk_index: ChunkIndex
    similarity_score: SimilarityScore


class AnswerResponse(BaseModel):
    answer: NonEmptyStr
    document_id: PositiveId
    document_title: NonEmptyStr
    source_chunks: list[SourceChunks]


class UserCreate(BaseModel):
    email: EmailStr
    password: PasswordStr


class UserResponse(BaseModel):
    id: PositiveId
    email: EmailStr


class Token(BaseModel):
    access_token: NonEmptyStr
    token_type: Literal["bearer"] = "bearer"