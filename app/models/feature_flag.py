"""Modeles Sprint 2 — Subscription Tiers et Plan Features (Feature Flags V2).

Note : une table 'feature_flags' existe deja (legacy Sprint 0/1).
Ces nouvelles tables utilisent des noms differents pour eviter les conflits.
"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Boolean, DateTime, Index, Integer, JSON, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SubscriptionTier(Base):
    """Plan d'abonnement : Free, Pro, Enterprise."""

    __tablename__ = "subscription_tiers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(50), nullable=False)

    max_aos_per_month: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_business_lines: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_storage_mb: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    monthly_price_eur: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    yearly_price_eur: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    includes_advanced_scoring: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    includes_multi_bl: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    includes_api_access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    includes_priority_support: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    includes_custom_branding: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("idx_sub_tiers_active", "is_active"),)


class PlanFeatureFlag(Base):
    """Feature flag individuel avec gating par plan (Sprint 2)."""

    __tablename__ = "plan_features"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    min_tier: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    enabled_globally: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (Index("idx_plan_features_enabled", "enabled_globally"),)
