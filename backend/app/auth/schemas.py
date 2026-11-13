from typing import Literal

from pydantic import BaseModel, EmailStr

from app.core.types import NonEmptyStr, PasswordStr, PositiveId


class UserCreate(BaseModel):
    email: EmailStr
    password: PasswordStr


class UserResponse(BaseModel):
    id: PositiveId
    email: EmailStr


class Token(BaseModel):
    access_token: NonEmptyStr
    token_type: Literal["bearer"] = "bearer"
