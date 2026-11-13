from typing import Annotated

from pydantic import Field, StringConstraints


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
