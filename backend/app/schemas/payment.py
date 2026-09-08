from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PaymentRead(BaseModel):
    id: UUID
    profile_id: UUID
    amount: int
    status: str
    paid_at: datetime | None

    model_config = {"from_attributes": True}
