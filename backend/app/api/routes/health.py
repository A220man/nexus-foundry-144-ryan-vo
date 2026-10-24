"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Basic health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db_session)) -> dict:
    """Readiness check including database connectivity."""
    settings = get_settings()
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False

    return {
        "status": "ready" if db_healthy else "not ready",
        "service": settings.app_name,
        "version": settings.app_version,
        "database": "connected" if db_healthy else "disconnected",
    }
