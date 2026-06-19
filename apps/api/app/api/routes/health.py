from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.storage import ensure_bucket

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    ensure_bucket()
    return {"status": "ready"}
