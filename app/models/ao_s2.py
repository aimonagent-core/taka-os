"""Modeles Sprint 2 — Sources, AO, AOFiles, AOChunks."""
from datetime import datetime
from typing import Optional
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Source(Base):
    """Source de veille : BOAMP, JOUE, e-Notification, Marches Publics..."""

    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scan_frequency_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    last_scan_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    aos: Mapped[list["AO"]] = relationship("app.models.ao_s2.AO", back_populates="source", lazy="selectin")

    __table_args__ = (Index("idx_sources_active_country", "is_active", "country"),)


class AO(Base):
    """Appel d'Offres — entite centrale du systeme TAKA OS."""

    __tablename__ = "aos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False, index=True
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    external_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="detected", nullable=False, index=True)
    cpv_codes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(20)), nullable=True)
    cpv_descriptions: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)

    country: Mapped[str] = mapped_column(String(2), nullable=False, default="FR")
    department_code: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, index=True)
    department_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    estimated_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    funding_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    contract_duration_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notice_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    buyer_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    keywords: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(100)), nullable=True)
    scoring_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    business_line_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("business_lines.id"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    source: Mapped["Source"] = relationship("Source", back_populates="aos", lazy="selectin")
    files: Mapped[list["AOFile"]] = relationship(
        "AOFile", back_populates="ao", lazy="selectin", cascade="all, delete-orphan"
    )
    chunks: Mapped[list["AOChunk"]] = relationship(
        "AOChunk", back_populates="ao", lazy="selectin", cascade="all, delete-orphan"
    )
    scoring_runs: Mapped[list["ScoringRun"]] = relationship(
        "ScoringRun", back_populates="ao", lazy="selectin"
    )
    business_line: Mapped[Optional["BusinessLine"]] = relationship(
        "BusinessLine", back_populates="aos", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_aos_status_deadline", "status", "deadline_date"),
        Index("idx_aos_source_external", "source_id", "external_id", unique=True),
        Index("idx_aos_department", "department_code"),
        Index("idx_aos_bl", "business_line_id", "status"),
    )


class AOFile(Base):
    """Document PDF/DOCX attache a un AO."""

    __tablename__ = "ao_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aos.id"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    parsing_confidence: Mapped[float] = mapped_column(Numeric(3, 2), default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ao: Mapped["AO"] = relationship("app.models.ao_s2.AO", back_populates="files", lazy="selectin")


class AOChunk(Base):
    """Chunks vectorises d'un AO pour recherche semantique."""

    __tablename__ = "ao_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aos.id"), nullable=False, index=True
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(1024), nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ao: Mapped["AO"] = relationship("app.models.ao_s2.AO", back_populates="chunks", lazy="selectin")

    __table_args__ = (Index("idx_ao_chunks_ao", "ao_id", "chunk_index"),)
