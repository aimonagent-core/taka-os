"""Modeles pour la facturation Stripe et les souscriptions."""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, Boolean, JSON, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TenantSubscription(Base):
    """Souscription active d'un tenant (lie tenant ↔ tier + Stripe)."""
    __tablename__ = "tenant_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, unique=True, index=True)
    tier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subscription_tiers.id"), nullable=False)

    # --- Stripe ---
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # --- Statut ---
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    # 'active', 'trialing', 'past_due', 'canceled', 'unpaid'
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SubscriptionEvent(Base):
    """Historique des evenements de facturation (audit trail)."""
    __tablename__ = "subscription_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant_subscriptions.id"), nullable=False, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # 'subscription_created', 'payment_succeeded', 'payment_failed',
    # 'subscription_updated', 'subscription_cancelled', 'subscription_renewed'
    stripe_event_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_sub_events_tenant_type", "tenant_id", "event_type"),
    )


class EmailLog(Base):
    """Log des emails envoyes (tracking + audit)."""
    __tablename__ = "email_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    email_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # 'welcome', 'daily_alert', 'payment_confirmation', 'password_reset',
    # 'mfa_backup_codes', 'subscription_cancelled'
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)

    # --- Statut ---
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    # 'pending', 'sent', 'delivered', 'bounced', 'failed'
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_email_logs_user", "user_id", "email_type"),
    )


class EmailPreference(Base):
    """Preferences email par utilisateur."""
    __tablename__ = "email_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)

    daily_alert_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    daily_alert_time: Mapped[str] = mapped_column(String(5), default="08:00", nullable=False)  # Format HH:MM

    payment_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    marketing_emails: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
