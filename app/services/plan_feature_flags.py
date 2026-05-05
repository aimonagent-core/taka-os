"""Service Feature Flags — verification d'acces aux fonctionnalites."""
import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature_flag import PlanFeatureFlag, SubscriptionTier

logger = logging.getLogger(__name__)

TIER_ORDER = {"free": 0, "pro": 1, "enterprise": 2}


class FeatureFlagService:
    """Service de gestion des Feature Flags (Sprint 2)."""

    @staticmethod
    async def is_enabled(
        db: AsyncSession, flag_key: str, tenant_tier: str = "free"
    ) -> bool:
        stmt = select(PlanFeatureFlag).where(PlanFeatureFlag.key == flag_key)
        rows = await db.execute(stmt)
        flag = rows.scalar_one_or_none()

        if not flag:
            return False

        if not flag.enabled_globally:
            return False

        min_tier_level = TIER_ORDER.get(flag.min_tier, 0)
        user_tier_level = TIER_ORDER.get(tenant_tier, 0)

        return user_tier_level >= min_tier_level

    @staticmethod
    async def check_feature(
        db: AsyncSession,
        flag_key: str,
        tenant_tier: str = "free",
        raise_if_disabled: bool = True,
    ) -> bool:
        enabled = await FeatureFlagService.is_enabled(db, flag_key, tenant_tier)
        if not enabled and raise_if_disabled:
            raise HTTPException(
                status_code=403,
                detail=f"Feature '{flag_key}' non disponible sur le plan {tenant_tier}. "
                f"Passez au plan superieur pour y acceder.",
            )
        return enabled

    @staticmethod
    async def get_all_for_tier(db: AsyncSession, tenant_tier: str = "free") -> dict:
        stmt = select(PlanFeatureFlag).where(PlanFeatureFlag.enabled_globally.is_(True))
        rows = await db.execute(stmt)
        flags = rows.scalars().all()

        result = {}
        user_level = TIER_ORDER.get(tenant_tier, 0)
        for flag in flags:
            min_level = TIER_ORDER.get(flag.min_tier, 0)
            result[flag.key] = {
                "enabled": user_level >= min_level,
                "label": flag.label,
                "min_tier": flag.min_tier,
            }
        return result

    @staticmethod
    async def seed_default_flags(db: AsyncSession):
        defaults = [
            {
                "key": "scoring_v2",
                "label": "Scoring Engine V2",
                "min_tier": "free",
                "enabled_globally": True,
            },
            {
                "key": "multi_bl",
                "label": "Multi Business Lines",
                "min_tier": "pro",
                "enabled_globally": True,
            },
            {
                "key": "rapports_auto",
                "label": "Rapports automatiques",
                "min_tier": "pro",
                "enabled_globally": True,
            },
            {
                "key": "api_access",
                "label": "Acces API",
                "min_tier": "enterprise",
                "enabled_globally": True,
            },
            {
                "key": "advanced_dashboard",
                "label": "Dashboard avance (10+ KPIs)",
                "min_tier": "pro",
                "enabled_globally": True,
            },
            {
                "key": "scoring_feedback",
                "label": "Feedback scoring utilisateur",
                "min_tier": "pro",
                "enabled_globally": True,
            },
            {
                "key": "custom_branding",
                "label": "Personnalisation marque",
                "min_tier": "enterprise",
                "enabled_globally": True,
            },
            {
                "key": "priority_support",
                "label": "Support prioritaire",
                "min_tier": "pro",
                "enabled_globally": True,
            },
            {
                "key": "hil_autonomy",
                "label": "Autonomie HIL niveau SUPERVISED+",
                "min_tier": "enterprise",
                "enabled_globally": True,
            },
        ]

        for d in defaults:
            stmt = select(PlanFeatureFlag).where(PlanFeatureFlag.key == d["key"])
            rows = await db.execute(stmt)
            existing = rows.scalar_one_or_none()
            if not existing:
                flag = PlanFeatureFlag(**d)
                db.add(flag)
                logger.info("[FF] Cree: %s (min_tier=%s)", d["key"], d["min_tier"])

        await db.commit()
