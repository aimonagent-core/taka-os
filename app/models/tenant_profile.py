"""Modeles Sprint 11 — Profil et preferences du tenant (onboarding)."""

from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TenantCPVPreference(Base):
    """CPV cibles selectionnes par le tenant lors de l'onboarding."""

    __tablename__ = "tenant_cpv_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    cpv_code: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_tenant_cpv_pref_tenant_code", "tenant_id", "cpv_code", unique=True),
    )
