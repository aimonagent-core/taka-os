"""Funnel de conversion — du pipeline AO."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.ao_s2 import AO
from app.models.scoring import ScoringRun
from app.models.submission import Submission

logger = logging.getLogger(__name__)


class FunnelEngine:
    """Moteur de calcul du funnel de conversion."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_funnel(self, tenant_id: uuid.UUID, days: int = 30) -> dict:
        """Calcule le funnel de conversion complet."""
        from_date = datetime.now(timezone.utc) - timedelta(days=days)

        conditions = [AO.created_at >= from_date]

        detected_stmt = select(func.count(AO.id)).where(and_(*conditions))
        detected_result = await self.db.execute(detected_stmt)
        total_detected = detected_result.scalar() or 0

        scored_stmt = (
            select(func.count(func.distinct(ScoringRun.ao_id)))
            .join(AO, AO.id == ScoringRun.ao_id)
            .where(AO.created_at >= from_date)
        )
        scored_result = await self.db.execute(scored_stmt)
        total_scored = scored_result.scalar() or 0

        qualified_stmt = (
            select(func.count(func.distinct(ScoringRun.ao_id)))
            .join(AO, AO.id == ScoringRun.ao_id)
            .where(
                and_(
                    AO.created_at >= from_date,
                    ScoringRun.verdict == "GO",
                )
            )
        )
        qualified_result = await self.db.execute(qualified_stmt)
        total_qualified = qualified_result.scalar() or 0

        submitted_stmt = select(func.count(Submission.id)).where(
            Submission.created_at >= from_date
        )
        submitted_result = await self.db.execute(submitted_stmt)
        total_submitted = submitted_result.scalar() or 0

        confirmed_stmt = select(func.count(Submission.id)).where(
            and_(
                Submission.created_at >= from_date,
                Submission.status == "confirmed",
            )
        )
        confirmed_result = await self.db.execute(confirmed_stmt)
        total_confirmed = confirmed_result.scalar() or 0

        def safe_rate(num: int, den: int) -> float:
            return round((num / den * 100), 1) if den > 0 else 0.0

        return {
            "period_days": days,
            "total_detected": total_detected,
            "total_scored": total_scored,
            "total_qualified": total_qualified,
            "total_submitted": total_submitted,
            "total_confirmed": total_confirmed,
            "conversion_rates": {
                "detected_to_scored": safe_rate(total_scored, total_detected),
                "scored_to_qualified": safe_rate(total_qualified, total_scored),
                "qualified_to_submitted": safe_rate(total_submitted, total_qualified),
                "submitted_to_confirmed": safe_rate(total_confirmed, total_submitted),
                "overall_detected_to_confirmed": safe_rate(total_confirmed, total_detected),
            },
        }

    async def get_funnel_trend(
        self,
        tenant_id: uuid.UUID,
        days: int = 90,
        granularity: str = "weekly",
    ) -> list[dict]:
        """Evolution du funnel sur le temps."""
        from_date = datetime.now(timezone.utc) - timedelta(days=days)

        if granularity == "weekly":
            trunc = func.date_trunc("week", AO.created_at)
            period_fmt = "%Y-W%W"
        elif granularity == "monthly":
            trunc = func.date_trunc("month", AO.created_at)
            period_fmt = "%Y-%m"
        else:
            trunc = func.date_trunc("day", AO.created_at)
            period_fmt = "%Y-%m-%d"

        stmt = (
            select(
                trunc.label("period"),
                func.count(AO.id).label("detected"),
            )
            .where(AO.created_at >= from_date)
            .group_by(trunc)
            .order_by(trunc)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "period": row.period.strftime(period_fmt) if row.period else "",
                "detected": row.detected,
            }
            for row in rows
        ]
