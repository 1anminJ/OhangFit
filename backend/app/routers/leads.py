from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.adapters.email import MockEmailAdapter
from app.auth_utils import issue_token
from app.db import get_db
from app.models.account import Account
from app.models.profile import Profile
from app.schemas.lead import LeadCreate, LeadRead, ProfileLookup

router = APIRouter(tags=["leads"])

# ponytail: 벤더 API가 정해지기 전까지는 목업 어댑터 하나만 씀.
_email_adapter = MockEmailAdapter()


@router.post("/leads", response_model=LeadRead)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)) -> LeadRead:
    profile = db.get(Profile, payload.profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")

    account = db.execute(
        select(Account).where(Account.email == payload.email)
    ).scalar_one_or_none()
    if account is None:
        account = Account(email=payload.email, role="lead")
        db.add(account)
        db.flush()  # account.id 확보

    token = issue_token(account)
    # profiles.account_id는 unique 제약(계정당 활성 프로필 1개) — 재사용 시 이전
    # 연결은 끊고 이번 프로필로 옮긴다.
    db.execute(
        update(Profile).where(Profile.account_id == account.id).values(account_id=None)
    )
    profile.account_id = account.id
    db.commit()
    db.refresh(account)

    magic_link_url = f"/magic-link/{token}"
    _email_adapter.send_magic_link(account.email, token)

    return LeadRead(
        account_id=account.id,
        email=account.email,
        role=account.role,
        magic_link_url=magic_link_url,
    )


@router.get("/leads/by-token/{token}", response_model=ProfileLookup)
def get_profile_by_token(token: str, db: Session = Depends(get_db)) -> ProfileLookup:
    account = db.execute(
        select(Account).where(Account.access_token == token)
    ).scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=404, detail="유효하지 않은 링크입니다.")

    profile = db.execute(
        select(Profile).where(Profile.account_id == account.id)
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="연결된 프로필을 찾을 수 없습니다.")

    return ProfileLookup(profile_id=profile.id)
