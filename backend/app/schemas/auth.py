from uuid import UUID

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class AuthResult(BaseModel):
    profile_id: UUID
