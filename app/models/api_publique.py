"""Modele pour les cles API publiques (externes)."""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, DateTime, Boolean, JSON, Integer, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExternalApiKey(Base):
    """Cle API publique pour acceder a l'API TAKA OS depuis un systeme externe."""

    __tablename__ = "external_api_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    key_name: Mapped[str] = mapped_column(String(100), nullable=False)

    permissions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    total_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_extapikey_tenant_active", "tenant_id", "is_active"),
        Index("idx_extapikey_hash", "key_hash"),
    )
