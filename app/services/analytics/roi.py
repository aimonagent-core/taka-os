"""Calculateur de ROI (Return On Investment)."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.ao_s2 import AO
from app.models.billing import TenantSubscription
from app.models.feature_flag import SubscriptionTier

logger = logging.getLogger(__name__)


class ROICalculator:
    """Calculateur de ROI pour TAKA OS."""

    DEFAULT_MARGIN_RATE = 0.15
    DEFAULT_HOURLY_COST = 50.0
    DEFAULT_HOURS_SAVED_PER_AO = 8.0

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_tenant_roi(self, tenant_id: uuid.UUID, months: int = 6) -> dict:
        """Calcule le ROI global d'un tenant."""
        from_date = datetime.now(timezone.utc) - timedelta(days=30 * months)

        ao_stmt = select(AO).where(
            and_(
                AO.estimated_amount.isnot(None),
                AO.created_at >= from_date,
            )
        )
        ao_result = await self.db.execute(ao_stmt)
        aos = ao_result.scalars().all()

        total_ao_value = sum(float(ao.estimated_amount or 0) for ao in aos)
        estimated_gain = total_ao_value * self.DEFAULT_MARGIN_RATE

        sub_stmt = select(TenantSubscription).where(
            TenantSubscription.tenant_id == tenant_id
        )
        sub_result = await self.db.execute(sub_stmt)
        subscription = sub_result.scalar_one_or_none()

        monthly_cost = 0.0
        if subscription and subscription.tier_id:
            tier_stmt = select(SubscriptionTier).where(
                SubscriptionTier.id == subscription.tier_id
            )
            tier_result = await self.db.execute(tier_stmt)
            tier = tier_result.scalar_one_or_none()
            if tier and tier.monthly_price_eur:
                monthly_cost = float(tier.monthly_price_eur)

        taka_cost = monthly_cost * months
        total_ao_detected = len(aos)
        time_saved_value = total_ao_detected * self.DEFAULT_HOURS_SAVED_PER_AO * self.DEFAULT_HOURLY_COST

        total_cost = taka_cost or 1.0
        net_benefit = estimated_gain + time_saved_value - total_cost
        roi_ratio = net_benefit / total_cost
        roi_percent = round(roi_ratio * 100, 1)

        return {
            "period_months": months,
            "total_ao_detected": total_ao_detected,
            "total_ao_value": total_ao_value,
            "estimated_gain": round(estimated_gain, 2),
            "taka_subscription_cost": round(taka_cost, 2),
            "time_cost_saved": round(time_saved_value, 2),
            "total_cost": round(total_cost, 2),
            "net_benefit": round(net_benefit, 2),
            "roi_percent": roi_percent,
            "roi_ratio": round(roi_ratio, 2),
        }

    async def get_roi_trend(self, tenant_id: uuid.UUID, months: int = 12) -> list[dict]:
        """Evolution mensuelle du ROI."""
        results = []
        for i in range(months - 1, -1, -1):
            month_roi = await self.calculate_tenant_roi(tenant_id, months=1)
            month_date = datetime.now(timezone.utc) - timedelta(days=30 * i)
            results.append({
                "month": month_date.strftime("%Y-%m"),
                **month_roi,
            })
        return results
