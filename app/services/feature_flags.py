# File: app/services/feature_flags.py
# Purpose: Feature flag evaluation with plan gating, kill switch, and rollout
# Dependencies: app.models.ao, sqlalchemy.ext.asyncio

import hashlib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import FeatureFlag, FeatureFlagScope


class FeatureFlagService:
    """
    Evaluate feature flags with the following precedence:
    1. Kill switch (global OFF wins)
    2. User-specific flag
    3. Tenant-specific flag
    4. Global flag
    5. Plan gating
    6. Rollout percentage (consistent hash on user_id)
    """

    @staticmethod
    async def is_enabled(
        db: AsyncSession,
        flag_name: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
        user_plan: str | None = None,
    ) -> bool:
        query = select(FeatureFlag).where(
            FeatureFlag.name == flag_name,
            FeatureFlag.deleted_at.is_(None),
            FeatureFlag.enabled == True,  # noqa: E712
        )
        result = await db.execute(query)
        flags = result.scalars().all()

        if not flags:
            return False

        if any(f.kill_switch for f in flags):
            return False

        scope_priority = {
            FeatureFlagScope.USER: 0,
            FeatureFlagScope.TENANT: 1,
            FeatureFlagScope.GLOBAL: 2,
        }
        flags_sorted = sorted(
            flags, key=lambda f: scope_priority.get(f.scope, 3)
        )

        for flag in flags_sorted:
            if flag.gated_by_plan and flag.gated_by_plan != user_plan:
                continue

            if flag.scope == FeatureFlagScope.USER and str(flag.user_id) != user_id:
                continue
            if (
                flag.scope == FeatureFlagScope.TENANT
                and str(flag.tenant_id) != tenant_id
            ):
                continue

            if flag.rollout_percentage < 100 and user_id:
                user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
                if user_hash >= flag.rollout_percentage:
                    continue

            return True

        return False

    @staticmethod
    async def get_all_for_context(
        db: AsyncSession,
        user_id: str | None = None,
        tenant_id: str | None = None,
        user_plan: str | None = None,
    ) -> dict[str, bool]:
        """Return all active flags for a given context."""
        result = await db.execute(
            select(FeatureFlag).where(FeatureFlag.deleted_at.is_(None))
        )
        flags = result.scalars().all()
        flag_names = {f.name for f in flags}
        return {
            name: await FeatureFlagService.is_enabled(
                db, name, user_id, tenant_id, user_plan
            )
            for name in flag_names
        }
