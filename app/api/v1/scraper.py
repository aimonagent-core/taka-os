"""
Router API v1 — Endpoints pour les scrapers BOAMP v2.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.services.scrapers import (
    ScraperBOAMP,
    ScraperListResponse,
    ScraperStatus,
    ScraperTriggerRequest,
    ScraperTriggerResponse,
    ScraperRunReport,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scrapers", tags=["scrapers"])


@router.post(
    "/boamp/run",
    response_model=ScraperTriggerResponse,
    status_code=status.HTTP_200_OK,
    summary="Declenche le scraper BOAMP",
    description="Recupere les dernieres annonces du BOAMP et les stocke en base avec embeddings.",
)
async def run_boamp_scraper(
    request: ScraperTriggerRequest,
    _: User = Depends(get_current_user),
) -> ScraperTriggerResponse:
    """
    Declenche manuellement le scraper BOAMP.
    Necessite authentification.
    """
    started_at = datetime.now(timezone.utc)

    try:
        scraper = ScraperBOAMP()
        report_dict = await scraper.fetch_and_store(
            limit=request.limit,
            where=request.where,
            order_by=request.order_by or "datePublication DESC",
        )

        finished_at = datetime.now(timezone.utc)
        duration = (finished_at - started_at).total_seconds()

        report = ScraperRunReport(
            source="boamp",
            total_fetched=report_dict.get("total_fetched", 0),
            inserted=report_dict.get("inserted", 0),
            duplicates=report_dict.get("duplicates", 0),
            errors=report_dict.get("errors", 0),
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration,
        )

        return ScraperTriggerResponse(
            success=True,
            source="boamp",
            report=report,
        )

    except Exception as exc:
        logger.error(f"[API] Erreur scraper BOAMP — {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du scraping BOAMP: {str(exc)}",
        )


@router.get(
    "/",
    response_model=ScraperListResponse,
    summary="Liste tous les scrapers et leur etat",
)
async def list_scrapers(
    _: User = Depends(get_current_user),
) -> ScraperListResponse:
    """
    Retourne l'etat de tous les scrapers configures.
    """
    boamp_status = ScraperStatus(
        source="boamp",
        is_healthy=True,
        last_run_status="unknown",
    )

    return ScraperListResponse(scrapers=[boamp_status])
