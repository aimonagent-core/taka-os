"""Moteur d'agregation des KPIs pour le dashboard Analytics."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.ao_s2 import AO, Source
from app.models.scoring import ScoringRun

logger = logging.getLogger(__name__)


class KPIEngine:
    """Moteur de calcul des KPIs pour le dashboard Analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_full_dashboard(self, tenant_id: uuid.UUID) -> dict:
        """Retourne tous les KPIs pour le dashboard."""
        from app.services.analytics.funnel import FunnelEngine
        from app.services.analytics.roi import ROICalculator
        from app.services.analytics.predictor import GainPredictor

        funnel_engine = FunnelEngine(self.db)
        roi_calc = ROICalculator(self.db)
        predictor = GainPredictor(self.db)

        funnel_data = await funnel_engine.get_funnel(tenant_id, days=30)
        roi_data = await roi_calc.calculate_tenant_roi(tenant_id, months=6)
        source_performance = await self._get_source_performance(days=30)
        predictions = await predictor.predict_batch(tenant_id, limit=10)
        trends = await funnel_engine.get_funnel_trend(tenant_id, days=90, granularity="weekly")

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "funnel": funnel_data,
            "roi": roi_data,
            "sources": source_performance,
            "predictions": predictions,
            "trends": trends,
        }

    async def _get_source_performance(self, days: int = 30) -> list[dict]:
        from_date = datetime.now(timezone.utc) - timedelta(days=days)

        source_stmt = select(Source).where(Source.is_active == True)
        source_result = await self.db.execute(source_stmt)
        sources = source_result.scalars().all()

        results = []
        for source in sources:
            detected_stmt = select(func.count(AO.id)).where(
                and_(AO.source_id == source.id, AO.created_at >= from_date)
            )
            detected_result = await self.db.execute(detected_stmt)
            detected = detected_result.scalar() or 0

            results.append({
                "source_id": str(source.id),
                "source_name": source.name,
                "total_detected": detected,
            })

        results.sort(key=lambda x: x["total_detected"], reverse=True)
        return results

    async def create_daily_snapshot(self, tenant_id: uuid.UUID) -> None:
        from app.models.analytics import AnalyticsSnapshot

        dashboard = await self.get_full_dashboard(tenant_id)
        snapshot = AnalyticsSnapshot(
            tenant_id=tenant_id,
            snapshot_type="daily",
            snapshot_date=datetime.now(timezone.utc).date(),
            data=dashboard,
        )
        self.db.add(snapshot)
        await self.db.flush()
        logger.info(f"Analytics snapshot cree pour tenant {tenant_id}")
