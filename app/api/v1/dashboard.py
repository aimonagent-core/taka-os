"""Routes API pour le Dashboard Admin."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.veilleur.agent import VeilleurAgent
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.services.dashboard.kpis import DashboardKPIs
from app.services.plan_feature_flags import FeatureFlagService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


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
    """Verifie l'etat de sante de toutes les sources de veille."""
    agent = VeilleurAgent()
    checks = await agent.health_check(db)
    return {"sources": checks}
