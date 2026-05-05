"""Modeles Sprint 2 — Business Lines, BL Members, BL CPV Keywords."""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BusinessLine(Base):
    """Ligne metier d'un tenant — ex: 'BTP', 'Informatique', 'Conseil'."""

    __tablename__ = "business_lines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6", nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="Briefcase", nullable=False)

    default_profile: Mapped[str] = mapped_column(String(20), default="prudent", nullable=False)

    cpv_keywords: Mapped[list[str]] = mapped_column(ARRAY(String(50)), default=list, nullable=False)
    free_text_keywords: Mapped[list[str]] = mapped_column(
        ARRAY(String(100)), default=list, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_monthly_aos: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    aos: Mapped[list["AO"]] = relationship("app.models.ao_s2.AO", back_populates="business_line", lazy="selectin")
    members: Mapped[list["BLMember"]] = relationship(
        "BLMember", back_populates="business_line", lazy="selectin", cascade="all, delete-orphan"
    )
    cpv_keywords_entries: Mapped[list["BLCPVKeyword"]] = relationship(
        "BLCPVKeyword",
        back_populates="business_line",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("idx_bl_tenant_active", "tenant_id", "is_active"),)


class BLMember(Base):
    """Association utilisateur <-> Business Line avec role."""

    __tablename__ = "bl_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("business_lines.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    business_line: Mapped["BusinessLine"] = relationship(
        "BusinessLine", back_populates="members", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_bl_members_user", "user_id", "is_primary"),
        Index("idx_bl_members_unique", "business_line_id", "user_id", unique=True),
    )


class BLCPVKeyword(Base):
    """Mots-cles CPV detailles par Business Line avec poids."""

    __tablename__ = "bl_cpv_keywords"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("business_lines.id"), nullable=False, index=True
    )

    cpv_code: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0, nullable=False)

    business_line: Mapped["BusinessLine"] = relationship(
        "BusinessLine", back_populates="cpv_keywords_entries", lazy="selectin"
    )

    __table_args__ = (Index("idx_bl_cpv_bl_code", "business_line_id", "cpv_code"),)
