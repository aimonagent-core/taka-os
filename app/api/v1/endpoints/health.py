# File: app/api/v1/endpoints/health.py
# Purpose: Health check and system status endpoints
# Dependencies: app.core.circuit_breaker, app.database, app.config.settings

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.circuit_breaker import get_breaker_status
from app.database import get_db

router = APIRouter()


def _standard_response(
    status_str: str,
    data: dict | None,
    message: str | None = None,
    meta: dict | None = None,
) -> dict:
    return {
        "status": status_str,
        "data": data,
        "message": message,
        "meta": meta,
    }


@router.get("/live")
async def health_live() -> dict:
    """Liveness probe - lightweight."""
    return _standard_response(
        "success", {"alive": True}, "Service is alive"
    )


@router.get("/ready")
async def health_ready(db: AsyncSession = Depends(get_db)) -> dict:
    """Readiness probe - checks DB connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return _standard_response(
            "success", {"ready": True}, "Service is ready"
        )
    except Exception as exc:
        return _standard_response(
            "error", {"ready": False}, str(exc)
        )


@router.get("/status")
async def health_status(db: AsyncSession = Depends(get_db)) -> dict:
    """Full status with circuit breakers and version."""
    breaker_status = get_breaker_status()
    return _standard_response(
        "success",
        {
            "version": settings.app_version,
            "environment": settings.environment,
            "circuit_breakers": breaker_status,
        },
        "System status",
    )
