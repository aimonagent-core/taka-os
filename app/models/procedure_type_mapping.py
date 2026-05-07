"""Modele Sprint 12 — Mapping procedure/type de marche pour classification des AO."""

from datetime import datetime
import uuid

from sqlalchemy import DateTime, JSON, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProcedureTypeMapping(Base):
    """Regle de mapping pour classifier un AO selon ses CPV et mots-cles."""

    __tablename__ = "procedure_type_mappings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    cpv_prefixes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    type_marche: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
