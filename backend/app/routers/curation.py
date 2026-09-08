from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.analysis_result import AnalysisResult
from app.models.color_mapping import ColorMapping
from app.models.curation_item import CurationItem
from app.models.payment import Payment
from app.models.profile import Profile
from app.schemas.curation import ColorMappingRead, CurationItemRead, CurationResponse

router = APIRouter(prefix="/profiles/{profile_id}/curation", tags=["curation"])


def _has_successful_payment(profile_id: UUID, account_id: UUID, db: Session) -> bool:
    stmt = (
        select(Payment.id)
        .where(
            Payment.account_id == account_id,
            Payment.profile_id == profile_id,
            Payment.status == "success",
        )
        .limit(1)
    )
    return db.execute(stmt).first() is not None


@router.get("", response_model=CurationResponse)
def get_curation(profile_id: UUID, db: Session = Depends(get_db)) -> CurationResponse:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    if profile.account_id is None:
        raise HTTPException(status_code=403, detail="이메일을 먼저 입력해주세요.")

    analysis_stmt = select(AnalysisResult).where(
        AnalysisResult.profile_id == profile_id
    )
    analysis = db.execute(analysis_stmt).scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="먼저 분석을 실행해주세요.")

    missing = analysis.missing_elements

    if not _has_successful_payment(profile_id, profile.account_id, db):
        return CurationResponse(
            missing_elements=missing, colors=[], items=[], locked=True
        )

    colors = (
        db.execute(select(ColorMapping).where(ColorMapping.element.in_(missing)))
        .scalars()
        .all()
    )
    items = (
        db.execute(select(CurationItem).where(CurationItem.element.in_(missing)))
        .scalars()
        .all()
    )

    return CurationResponse(
        missing_elements=missing,
        colors=[ColorMappingRead.model_validate(c) for c in colors],
        items=[CurationItemRead.model_validate(i) for i in items],
        locked=False,
    )
