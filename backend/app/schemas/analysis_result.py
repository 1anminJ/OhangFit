from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AnalysisResultRead(BaseModel):
    id: UUID
    profile_id: UUID
    five_elements: dict[str, int]
    missing_elements: list[str]
    excess_elements: list[str]
    sinsal: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
