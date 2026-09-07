from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.profile import Profile
from app.schemas.profile import ProfileBase, ProfileCreate, ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _assign_fields(profile: Profile, validated: ProfileBase) -> None:
    profile.birth_date = validated.birth_date
    profile.birth_time = validated.birth_time
    profile.birth_time_unknown = validated.birth_time_unknown
    profile.gender = validated.gender.value
    profile.birth_region = validated.birth_region


@router.post("", response_model=ProfileRead, status_code=201)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)) -> Profile:
    profile = Profile()
    _assign_fields(profile, payload)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileRead)
def get_profile(profile_id: UUID, db: Session = Depends(get_db)) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    return profile


@router.patch("/{profile_id}", response_model=ProfileRead)
def update_profile(
    profile_id: UUID, payload: ProfileUpdate, db: Session = Depends(get_db)
) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")

    current = {
        "birth_date": profile.birth_date,
        "birth_time": profile.birth_time,
        "birth_time_unknown": profile.birth_time_unknown,
        "gender": profile.gender,
        "birth_region": profile.birth_region,
    }
    current.update(payload.model_dump(exclude_unset=True))

    try:
        validated = ProfileCreate(**current)
    except ValidationError as exc:
        # ponytail: exc.errors() 안의 "input" 값은 date/time 등 raw 파이썬 객체라
        # FastAPI 기본 JSONResponse가 그대로 직렬화하지 못함 -> jsonable_encoder로 변환
        raise HTTPException(status_code=422, detail=jsonable_encoder(exc.errors())) from exc

    _assign_fields(profile, validated)
    db.commit()
    db.refresh(profile)
    return profile
