"""Routes API pour le Dashboard Admin."""
import asyncio
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao_s2 import Source
from app.models.ao import User
from app.services.dashboard.kpis import DashboardKPIs
from app.services.plan_feature_flags import FeatureFlagService
from app.services.scrapers.base import BaseScraper
from app.services.scrapers.boamp import ScraperBOAMP
from app.services.scrapers.enotification import ENotificationScraper
from app.services.scrapers.joue import JOUEScraper
from app.services.scrapers.marche_public import MarchePublicScraper
from app.services.scrapers.region_scraper import RegionScraper
from app.services.scrapers.dept_scraper import DepartementScraper
from app.services.scrapers.metropole_scraper import MetropoleScraper
from app.services.scrapers.ted_full_scraper import TedFullScraper
from app.services.scrapers.marches_etat_scraper import MarchesEtatScraper
from app.services.scrapers.aggregateur_fr import AgregateurFRScraper

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

SCRAPER_REGISTRY = {
    "boamp": ScraperBOAMP,
    "joue": JOUEScraper,
    "enotification": ENotificationScraper,
    "marche_public": MarchePublicScraper,
    "regions": RegionScraper,
    "departements": DepartementScraper,
    "metropoles": MetropoleScraper,
    "ted": TedFullScraper,
    "marches_etat": MarchesEtatScraper,
    "agregateur_fr": AgregateurFRScraper,
}


def _get_tenant_tier(user: User) -> str:
    return user.tenant.billing_plan or "free" if user.tenant else "free"


@router.get("/kpis")
async def get_kpis(
    business_line_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne les 10 KPIs du dashboard."""
    await FeatureFlagService.check_feature(
        db, "advanced_dashboard", _get_tenant_tier(current_user)
    )

    kpis = await DashboardKPIs.get_all_kpis(
        db,
        tenant_id=str(current_user.tenant_id),
        business_line_id=business_line_id,
        period_days=period_days,
    )
    return kpis


@router.get("/kpis/by-business-line")
async def get_kpis_by_bl(
    period_days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare les KPIs entre Business Lines."""
    await FeatureFlagService.check_feature(
        db, "advanced_dashboard", _get_tenant_tier(current_user)
    )

    results = await DashboardKPIs.get_kpis_by_business_line(
        db,
        tenant_id=str(current_user.tenant_id),
        period_days=period_days,
    )
    return {"business_lines": results}


@router.get("/health/sources")
async def sources_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verifie l'etat de sante de toutes les sources de veille (parallele, timeout 5s)."""
    stmt = select(Source).where(Source.is_active == True)
    rows = await db.execute(stmt)
    sources = rows.scalars().all()

    async def check_one(source: Source) -> dict:
        scraper_class = SCRAPER_REGISTRY.get(source.name)
        if not scraper_class:
            return {
                "name": source.name,
                "ok": False,
                "latency_ms": 0,
                "error": "Scraper non implemente",
            }
        try:
            async with scraper_class(
                {"name": source.name, "base_url": source.base_url}
            ) as scraper:
                result = await asyncio.wait_for(scraper.health_check(), timeout=5.0)
                result["name"] = source.name
                return result
        except asyncio.TimeoutError:
            return {
                "name": source.name,
                "ok": False,
                "latency_ms": 5000,
                "error": "Timeout apres 5 secondes",
            }
        except Exception as e:
            return {
                "name": source.name,
                "ok": False,
                "latency_ms": 0,
                "error": str(e),
            }

    results = await asyncio.gather(*[check_one(s) for s in sources])
    return {"sources": results, "checked_at": datetime.now(timezone.utc).isoformat()}
