from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """모든 모델의 베이스 클래스. alembic autogenerate가 이 metadata를 기준으로 diff를 잡음."""


def get_db() -> Generator[Session, None, None]:
    """요청 단위 DB 세션 의존성 (FastAPI Depends(get_db)로 사용)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
