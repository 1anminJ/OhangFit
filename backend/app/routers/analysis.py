from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.saju import MockSajuAdapter
from app.db import get_db
from app.models.analysis_result import AnalysisResult
from app.models.profile import Profile
from app.schemas.analysis_result import AnalysisResultRead

router = APIRouter(prefix="/profiles/{profile_id}/analysis", tags=["analysis"])

# ponytail: 벤더 API가 정해지기 전까지는 결정론적 목업 어댑터 하나만 씀.
# 나중에 실제 벤더 어댑터로 바꿀 때 이 한 줄만 교체하면 됨.
_adapter = MockSajuAdapter()


def _get_profile_or_404(profile_id: UUID, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    return profile


def _get_analysis(profile_id: UUID, db: Session) -> AnalysisResult | None:
    stmt = select(AnalysisResult).where(AnalysisResult.profile_id == profile_id)
    return db.execute(stmt).scalar_one_or_none()


@router.post("", response_model=AnalysisResultRead)
def create_or_update_analysis(
    profile_id: UUID, db: Session = Depends(get_db)
) -> AnalysisResult:
    profile = _get_profile_or_404(profile_id, db)
    data = _adapter.analyze(
        profile.birth_date,
        None if profile.birth_time_unknown else profile.birth_time,
    )

    result = _get_analysis(profile_id, db)
    if result is None:
        result = AnalysisResult(profile_id=profile_id)
        db.add(result)

    result.five_elements = data.five_elements
    result.missing_elements = data.missing_elements
    result.excess_elements = data.excess_elements
    result.sinsal = data.sinsal
    db.commit()
    db.refresh(result)
    return result


@router.get("", response_model=AnalysisResultRead)
def get_analysis(profile_id: UUID, db: Session = Depends(get_db)) -> AnalysisResult:
    _get_profile_or_404(profile_id, db)
    result = _get_analysis(profile_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="아직 분석되지 않았습니다.")
    return result
