from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth_utils import hash_password, issue_token, verify_password
from app.db import get_db
from app.models.account import Account
from app.models.profile import Profile
from app.schemas.auth import AuthResult, LoginRequest, SignupRequest

router = APIRouter(tags=["auth"])


def _profile_id_for(account: Account, db: Session) -> UUID:
    profile = db.execute(
        select(Profile).where(Profile.account_id == account.id)
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="연결된 프로필을 찾을 수 없습니다.")
    return profile.id


@router.post("/signup", response_model=AuthResult)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> AuthResult:
    account = db.execute(
        select(Account).where(Account.email == payload.email)
    ).scalar_one_or_none()

    if account is not None and account.role == "member":
        raise HTTPException(status_code=409, detail="이미 가입된 이메일입니다.")

    if account is None:
        account = Account(email=payload.email, role="member")
        db.add(account)
    else:
        account.role = "member"
        account.converted_to_member_at = datetime.now(timezone.utc)

    account.password_hash = hash_password(payload.password)
    issue_token(account)
    db.commit()
    db.refresh(account)

    return AuthResult(profile_id=_profile_id_for(account, db))


@router.post("/login", response_model=AuthResult)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResult:
    account = db.execute(
        select(Account).where(Account.email == payload.email)
    ).scalar_one_or_none()
    if account is None or account.password_hash is None:
        raise HTTPException(
            status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    if not verify_password(payload.password, account.password_hash):
        raise HTTPException(
            status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    issue_token(account)
    db.commit()

    return AuthResult(profile_id=_profile_id_for(account, db))
