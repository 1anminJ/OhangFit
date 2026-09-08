from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.routers.analysis import router as analysis_router
from app.routers.auth import router as auth_router
from app.routers.curation import router as curation_router
from app.routers.leads import router as leads_router
from app.routers.payments import router as payments_router
from app.routers.profiles import router as profiles_router

app = FastAPI(title="Ohang Fit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict:
    """docker-compose PostgreSQL 연결 확인용."""
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(profiles_router)
app.include_router(analysis_router)
app.include_router(curation_router)
app.include_router(leads_router)
app.include_router(payments_router)
app.include_router(auth_router)
