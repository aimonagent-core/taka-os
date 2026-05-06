"""API endpoints pour les analytics et le dashboard."""
from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.services.analytics.funnel import FunnelEngine
from app.services.analytics.roi import ROICalculator
from app.services.analytics.predictor import GainPredictor
from app.services.analytics.kpi_engine import KPIEngine

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne le dashboard analytics complet."""
    engine = KPIEngine(db)
    dashboard = await engine.get_full_dashboard(current_user.tenant_id)
    return dashboard


@router.get("/funnel")
async def get_funnel(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Funnel de conversion."""
    engine = FunnelEngine(db)
    funnel = await engine.get_funnel(current_user.tenant_id, days=days)
    return funnel


@router.get("/funnel/trend")
async def get_funnel_trend(
    days: int = Query(90, ge=30, le=365),
    granularity: str = Query("weekly", regex="^(daily|weekly|monthly)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trend du funnel sur le temps."""
    engine = FunnelEngine(db)
    trend = await engine.get_funnel_trend(
        current_user.tenant_id,
        days=days,
        granularity=granularity,
    )
    return {"trend": trend}


@router.get("/roi")
async def get_roi(
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ROI global du tenant."""
    calc = ROICalculator(db)
    roi = await calc.calculate_tenant_roi(current_user.tenant_id, months=months)
    return roi


@router.get("/roi/trend")
async def get_roi_trend(
    months: int = Query(12, ge=3, le=24),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evolution mensuelle du ROI."""
    calc = ROICalculator(db)
    trend = await calc.get_roi_trend(current_user.tenant_id, months=months)
    return {"trend": trend}


@router.get("/predictions")
async def get_predictions(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Predictions de gain pour les AO recents."""
    predictor = GainPredictor(db)
    predictions = await predictor.predict_batch(current_user.tenant_id, limit=limit)
    return {"predictions": predictions}


@router.get("/sources")
async def get_source_performance(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Performance par source de veille."""
    engine = KPIEngine(db)
    sources = await engine._get_source_performance(days=days)
    return {"sources": sources}


@router.post("/snapshot")
async def create_snapshot(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Genere un snapshot analytics manuellement."""
    engine = KPIEngine(db)
    await engine.create_daily_snapshot(current_user.tenant_id)
    return {"status": "snapshot_created"}
