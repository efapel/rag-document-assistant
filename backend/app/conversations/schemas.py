from pydantic import BaseModel

from app.core.types import ChunkIndex, NonEmptyStr, PositiveId, SimilarityScore


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
