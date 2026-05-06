"""Modele pour les notifications in-app."""

from datetime import datetime
from typing import Optional
import uuid
from enum import Enum as PyEnum

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, JSON, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NotificationType(str, PyEnum):
    MENTION = "mention"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_DECIDED = "approval_decided"
    AO_ASSIGNED = "ao_assigned"
    DEADLINE_APPROACHING = "deadline_approaching"
    SYSTEM = "system"
    NEW_AO = "new_ao"
    DEADLINE_WARNING = "deadline_warning"


class InAppNotification(Base):
    """Notification in-app pour un utilisateur."""

    __tablename__ = "in_app_notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    recipient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    notification_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    target_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    link_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_notif_recipient_unread", "recipient_id", "is_read"),
        Index("idx_notif_tenant_type", "tenant_id", "notification_type"),
    )
