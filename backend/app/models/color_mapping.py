import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ColorMapping(Base):
    """오행 -> 보완 컬러 매핑. 에디터가 시딩 스크립트로 채우는 참고 데이터."""

    __tablename__ = "color_mappings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    element: Mapped[str] = mapped_column(String(10), nullable=False)
    color_name: Mapped[str] = mapped_column(String(50), nullable=False)
    hex_code: Mapped[str | None] = mapped_column(String(7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
