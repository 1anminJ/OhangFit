from uuid import UUID

from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    profile_id: UUID
    email: str = Field(min_length=1, max_length=255)


class LeadRead(BaseModel):
    account_id: UUID
    email: str
    role: str
    magic_link_url: str


class ProfileLookup(BaseModel):
    profile_id: UUID
