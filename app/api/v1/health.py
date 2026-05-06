"""
Router API v1 — Endpoints de health check et monitoring.

Fournit:
- /health/scrapers : Etat detaille de chaque scraper
- /health/scrapers/{source}/history : Historique des runs
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.audit import ScraperRun
from app.models.ao import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/scrapers",
    summary="Etat des scrapers",
    description="Retourne l'etat de tous les scrapers : dernier run, nombre d'AO extraits, statut.",
)
async def health_scrapers(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Retourne l'etat detaille de chaque scraper.
    Recupere les informations depuis la table scraper_runs.
    """
    scraper_statuses: list[dict[str, Any]] = []

    # Liste des sources de scrapers configurees
    sources = ["boamp"]

    for source in sources:
        try:
            # Recuperer le dernier run pour cette source
            result = await session.execute(
                select(ScraperRun)
                .where(ScraperRun.source == source)
                .order_by(ScraperRun.started_at.desc())
                .limit(1)
            )
            last_run: Optional[ScraperRun] = result.scalar_one_or_none()

            if last_run:
                status = last_run.status
                scraper_statuses.append(
                    {
                        "source": source,
                        "is_healthy": status == "ok",
                        "last_run_at": last_run.started_at.isoformat()
                        if last_run.started_at
                        else None,
                        "last_run_count": last_run.count,
                        "last_run_status": status,
                        "error_message": last_run.error_message,
                    }
                )
            else:
                # Jamais execute
                scraper_statuses.append(
                    {
                        "source": source,
                        "is_healthy": True,  # Pas d'erreur = healthy
                        "last_run_at": None,
                        "last_run_count": None,
                        "last_run_status": "never_run",
                        "error_message": None,
                    }
                )

        except Exception as exc:
            logger.error(f"[Health] Erreur recuperation statut scraper {source} — {exc}")
            scraper_statuses.append(
                {
                    "source": source,
                    "is_healthy": False,
                    "last_run_at": None,
                    "last_run_count": None,
                    "last_run_status": "error",
                    "error_message": str(exc),
                }
            )

    return {
        "status": "ok",
        "scrapers": scraper_statuses,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/scrapers/{source}/history",
    summary="Historique des runs d'un scraper",
)
async def scraper_history(
    source: str,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Retourne l'historique des executions d'un scraper.

    Args:
        source: Nom de la source (ex: "boamp").
        limit: Nombre d'entrees a retourner.
    """
    try:
        result = await session.execute(
            select(ScraperRun)
            .where(ScraperRun.source == source)
            .order_by(ScraperRun.started_at.desc())
            .limit(limit)
        )
        runs = result.scalars().all()

        history = []
        for run in runs:
            duration = None
            if run.finished_at and run.started_at:
                duration = (run.finished_at - run.started_at).total_seconds()

            history.append(
                {
                    "id": run.id,
                    "source": run.source,
                    "status": run.status,
                    "count": run.count,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                    "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                    "duration_seconds": round(duration, 2) if duration else None,
                    "error_message": run.error_message,
                }
            )

        return {
            "source": source,
            "history": history,
            "total": len(history),
        }

    except Exception as exc:
        logger.error(f"[Health] Erreur historique scraper {source} — {exc}")
        raise
