from uuid import UUID

from pydantic import BaseModel


class LeadCreate(BaseModel):
    profile_id: UUID
    email: str


class LeadRead(BaseModel):
    account_id: UUID
    email: str
    role: str
    magic_link_url: str


class ProfileLookup(BaseModel):
    profile_id: UUID
