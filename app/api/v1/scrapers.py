"""API endpoints pour la gestion des sources de veille."""
from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.models.ao_s2 import Source
from app.services.scrapers.base import BaseScraper
from app.services.scrapers.region_scraper import RegionScraper
from app.services.scrapers.dept_scraper import DepartementScraper
from app.services.scrapers.metropole_scraper import MetropoleScraper
from app.services.scrapers.ted_full_scraper import TedFullScraper
from app.services.scrapers.marches_etat_scraper import MarchesEtatScraper
from app.services.scrapers.aggregateur_fr import AgregateurFRScraper

router = APIRouter(prefix="/scrapers", tags=["scrapers"])

SCRAPER_REGISTRY = {
    "RegionScraper": RegionScraper,
    "DepartementScraper": DepartementScraper,
    "MetropoleScraper": MetropoleScraper,
    "TedFullScraper": TedFullScraper,
    "MarchesEtatScraper": MarchesEtatScraper,
    "AgregateurFRScraper": AgregateurFRScraper,
}


@router.get("/sources")
async def list_sources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les sources de veille."""
    stmt = select(Source).where(Source.is_active == True).order_by(Source.last_scan_at.desc())
    result = await db.execute(stmt)
    sources = result.scalars().all()

    return {
        "sources": [
            {
                "id": str(s.id),
                "name": s.name,
                "label": s.label,
                "url": s.base_url,
                "type": s.country,
                "country": s.country,
                "is_active": s.is_active,
                "last_scraped_at": s.last_scan_at.isoformat() if s.last_scan_at else None,
                "config": s.config,
            }
            for s in sources
        ],
    }


@router.post("/sources/{source_id}/scrape")
async def manual_scrape(
    source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lance un scraping manuel pour une source."""
    stmt = select(Source).where(Source.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvee")

    scraper_class = None
    for name, cls in SCRAPER_REGISTRY.items():
        if name.lower().replace("scraper", "") in source.name.lower():
            scraper_class = cls
            break

    if not scraper_class:
        raise HTTPException(status_code=400, detail=f"Pas de scraper pour {source.name}")

    scraper = scraper_class({"name": source.name, "base_url": source.base_url})
    count = await scraper.scan(since=source.last_scan_at)

    return {
        "source_id": str(source_id),
        "source_name": source.name,
        "new_aos": len(count),
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/stats")
async def get_scraper_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Statistiques des scrapers."""
    from app.models.ao_s2 import AO
    from datetime import datetime, timezone, timedelta

    from_date = datetime.now(timezone.utc) - timedelta(days=30)

    stmt = (
        select(
            Source.name,
            func.count(AO.id).label("ao_count"),
        )
        .join(AO, AO.source_id == Source.id)
        .where(AO.created_at >= from_date)
        .group_by(Source.name)
        .order_by(func.count(AO.id).desc())
    )

    result = await db.execute(stmt)
    stats = result.all()

    return {
        "period_days": 30,
        "sources": [
            {"source_name": name, "ao_detected": count}
            for name, count in stats
        ],
        "total_sources": len(stats),
    }
