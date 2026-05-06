"""Routes API pour le Dashboard Admin + Sprint 11 Dashboard Entreprise."""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao_s2 import AO, Source
from app.models.ao import Tenant, User
from app.services.dashboard.kpis import DashboardKPIs
from app.services.matching import MatchingService
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


# =============================================================================
# Sprint 11 — Dashboard Entreprise
# =============================================================================

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne les 4 KPIs + graph data pour le dashboard entreprise."""
    tenant_id = str(current_user.tenant_id)
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())  # lundi
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    last_week_start = week_start - timedelta(days=7)

    # 1. AO cette semaine
    stmt_this_week = select(func.count(AO.id)).where(
        and_(AO.created_at >= week_start, AO.status == "detected")
    )
    row = await db.execute(stmt_this_week)
    ao_this_week = row.scalar() or 0

    # AO semaine derniere (pour delta)
    stmt_last_week = select(func.count(AO.id)).where(
        and_(
            AO.created_at >= last_week_start,
            AO.created_at < week_start,
            AO.status == "detected",
        )
    )
    row_last = await db.execute(stmt_last_week)
    ao_last_week = row_last.scalar() or 0

    delta = None
    if ao_last_week > 0:
        delta = round(((ao_this_week - ao_last_week) / ao_last_week) * 100, 1)

    # 2. Deadlines imminentes (< 7 jours)
    imminent_deadline = now + timedelta(days=7)
    stmt_deadlines = select(func.count(AO.id)).where(
        and_(
            AO.deadline_date.isnot(None),
            AO.deadline_date <= imminent_deadline,
            AO.deadline_date >= now,
            AO.status == "detected",
        )
    )
    row_dl = await db.execute(stmt_deadlines)
    imminent_deadlines = row_dl.scalar() or 0

    # 3. Taux de match moyen (sur les 20 derniers AO)
    tenant = current_user.tenant
    stmt_recent = (
        select(AO)
        .where(AO.status == "detected")
        .order_by(AO.created_at.desc())
        .limit(20)
    )
    rows = await db.execute(stmt_recent)
    recent_aos = rows.scalars().all()

    match_scores = []
    for ao in recent_aos:
        score_data = await MatchingService.compute_score(db, ao, tenant)
        match_scores.append(score_data["total_score"])

    match_rate_pct = round(sum(match_scores) / len(match_scores), 1) if match_scores else 0.0

    # 4. Nouveautes depuis derniere connexion
    last_login = current_user.last_login_at or now - timedelta(days=1)
    stmt_new = select(func.count(AO.id)).where(
        and_(AO.created_at >= last_login, AO.status == "detected")
    )
    row_new = await db.execute(stmt_new)
    new_since_last_login = row_new.scalar() or 0

    # Graphique : repartition par type de marche (notice_type)
    stmt_by_type = (
        select(AO.notice_type, func.count(AO.id))
        .where(AO.status == "detected")
        .group_by(AO.notice_type)
        .order_by(func.count(AO.id).desc())
    )
    rows_type = await db.execute(stmt_by_type)
    type_colors = {
        "Travaux": "#3b82f6",
        "Services": "#22c55e",
        "Fournitures": "#6b7280",
        "Concession": "#a855f7",
    }
    ao_by_type = [
        {"label": r[0] or "Non specifie", "value": r[1], "color": type_colors.get(r[0], "#9ca3af")}
        for r in rows_type.all()
    ]

    # Evolution hebdomadaire (7 derniers jours)
    daily = []
    for i in range(6, -1, -1):
        day_start = now - timedelta(days=i)
        day_start = day_start.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        stmt_day = select(func.count(AO.id)).where(
            and_(AO.created_at >= day_start, AO.created_at < day_end, AO.status == "detected")
        )
        row_day = await db.execute(stmt_day)
        daily.append({
            "label": day_start.strftime("%a"),
            "value": row_day.scalar() or 0,
        })

    return {
        "period_days": 7,
        "generated_at": now.isoformat(),
        "ao_this_week": ao_this_week,
        "ao_this_week_delta": delta,
        "imminent_deadlines": imminent_deadlines,
        "match_rate_pct": match_rate_pct,
        "new_since_last_login": new_since_last_login,
        "ao_by_type": ao_by_type,
        "weekly_evolution": daily,
    }


@router.get("/recent-ao")
async def get_recent_ao(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne les N AO les plus pertinents pour le tenant avec score de matching."""
    tenant = current_user.tenant
    results = await MatchingService.get_recent_ao_with_scores(db, tenant, limit=limit)

    now = datetime.now(timezone.utc)

    def _days_until(deadline):
        if not deadline:
            return None
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        delta = deadline - now
        return max(0, int(delta.total_seconds() / 86400))

    def _badge(days):
        if days is None:
            return "none"
        if days <= 7:
            return "urgent"
        if days <= 14:
            return "soon"
        return "normal"

    return {
        "items": [
            {
                "id": str(r["ao"].id),
                "external_id": r["ao"].external_id,
                "title": r["ao"].title,
                "buyer_name": r["ao"].buyer_name,
                "deadline_date": r["ao"].deadline_date.isoformat() if r["ao"].deadline_date else None,
                "days_until_deadline": _days_until(r["ao"].deadline_date),
                "deadline_badge": _badge(_days_until(r["ao"].deadline_date)),
                "match_score": r["score"],
                "ao_type": r["ao"].notice_type,
                "notice_type": r["ao"].notice_type,
                "url": r["ao"].external_url,
                "is_new": r["ao"].created_at >= (current_user.last_login_at or now - timedelta(days=1)),
            }
            for r in results
        ],
    }


@router.get("/matching-score/{ao_id}")
async def get_matching_score(
    ao_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calcule le % de match entre un AO et le profil du tenant connecte."""
    stmt = select(AO).where(AO.id == ao_id)
    row = await db.execute(stmt)
    ao = row.scalar_one_or_none()

    if not ao:
        raise HTTPException(status_code=404, detail="AO non trouve")

    tenant = current_user.tenant
    score_data = await MatchingService.compute_score(db, ao, tenant)

    return {
        "ao_id": ao_id,
        "tenant_id": str(tenant.id),
        "total_score": score_data["total_score"],
        "breakdown": score_data["breakdown"],
        "matched_cpv": score_data["matched_cpv"],
        "matched_department": score_data["matched_department"],
        "matched_type_marche": score_data["matched_type_marche"],
        "deadline_bonus": score_data["deadline_bonus"],
        "keyword_matches": score_data["keyword_matches"],
    }
