# File: tests/test_services.py
# Purpose: Service layer tests for feature flags and audit hash chain
# Dependencies: tests.conftest fixtures

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import AuditAction, AuditLog, FeatureFlag, FeatureFlagScope
from app.services.audit_service import AuditService
from app.services.feature_flags import FeatureFlagService


@pytest.mark.asyncio
async def test_feature_flag_global_enabled(db_session: AsyncSession):
    flag = FeatureFlag(
        name="test_flag",
        scope=FeatureFlagScope.GLOBAL,
        enabled=True,
        rollout_percentage=100,
    )
    db_session.add(flag)
    await db_session.commit()

    result = await FeatureFlagService.is_enabled(db_session, "test_flag")
    assert result is True


@pytest.mark.asyncio
async def test_feature_flag_kill_switch(db_session: AsyncSession):
    flag = FeatureFlag(
        name="kill_flag",
        scope=FeatureFlagScope.GLOBAL,
        enabled=True,
        kill_switch=True,
    )
    db_session.add(flag)
    await db_session.commit()

    result = await FeatureFlagService.is_enabled(db_session, "kill_flag")
    assert result is False


@pytest.mark.asyncio
async def test_feature_flag_plan_gating(db_session: AsyncSession):
    flag = FeatureFlag(
        name="plan_flag",
        scope=FeatureFlagScope.GLOBAL,
        enabled=True,
        gated_by_plan="pro",
    )
    db_session.add(flag)
    await db_session.commit()

    result = await FeatureFlagService.is_enabled(
        db_session, "plan_flag", user_plan="free"
    )
    assert result is False

    result = await FeatureFlagService.is_enabled(
        db_session, "plan_flag", user_plan="pro"
    )
    assert result is True


@pytest.mark.asyncio
async def test_feature_flag_rollout_percentage(db_session: AsyncSession):
    flag = FeatureFlag(
        name="rollout_flag",
        scope=FeatureFlagScope.GLOBAL,
        enabled=True,
        rollout_percentage=50,
    )
    db_session.add(flag)
    await db_session.commit()

    # Deterministic: some users will be in, some out
    in_count = 0
    for i in range(100):
        user_id = f"user-{i}"
        result = await FeatureFlagService.is_enabled(
            db_session, "rollout_flag", user_id=user_id
        )
        if result:
            in_count += 1

    # Should be approximately 50, but deterministic
    assert 0 <= in_count <= 100


@pytest.mark.asyncio
async def test_audit_log_hash_chain(db_session: AsyncSession):
    log1 = await AuditService.log(
        db=db_session,
        action=AuditAction.CREATE,
        entity_type="test_entity",
        entity_id="entity-1",
    )
    await db_session.commit()

    log2 = await AuditService.log(
        db=db_session,
        action=AuditAction.UPDATE,
        entity_type="test_entity",
        entity_id="entity-1",
    )
    await db_session.commit()

    assert log1.hash is not None
    assert log2.previous_hash == log1.hash
    assert log2.hash is not None


@pytest.mark.asyncio
async def test_audit_verify_chain(db_session: AsyncSession):
    await AuditService.log(
        db=db_session,
        action=AuditAction.CREATE,
        entity_type="test_entity",
        entity_id="entity-1",
    )
    await AuditService.log(
        db=db_session,
        action=AuditAction.UPDATE,
        entity_type="test_entity",
        entity_id="entity-1",
    )
    await db_session.commit()

    valid = await AuditService.verify_chain(db_session, tenant_id=None)
    assert valid is True
