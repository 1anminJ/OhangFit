import secrets
from datetime import datetime, timezone

import bcrypt

from app.models.account import Account


def issue_token(account: Account) -> str:
    """계정에 새 토큰을 발급하고 이전 토큰을 무효화한다 (매직링크/로그인 세션 공용)."""
    token = secrets.token_urlsafe(32)
    account.access_token = token
    account.token_created_at = datetime.now(timezone.utc)
    return token


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())
