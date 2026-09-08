from uuid import UUID

from pydantic import BaseModel


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResult(BaseModel):
    profile_id: UUID
