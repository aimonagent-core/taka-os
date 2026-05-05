"""Modeles Sprint 2 — ScoringRuns, ScoringFeedbacks."""
from datetime import datetime
from typing import Optional
import uuid

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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScoringRun(Base):
    """Execution du scoring sur un AO — resultat complet par profil."""

    __tablename__ = "scoring_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aos.id"), nullable=False, index=True
    )
    profile: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    score_global: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    score_coherence: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    score_financiere: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    score_geographique: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    score_temporelle: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    score_concurrentielle: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)

    verdict: Mapped[str] = mapped_column(String(10), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)

    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    recommendations: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)

    triggered_by: Mapped[str] = mapped_column(String(50), default="auto", nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ao: Mapped["AO"] = relationship("app.models.ao_s2.AO", back_populates="scoring_runs", lazy="selectin")

    __table_args__ = (
        Index("idx_scoring_runs_ao_profile", "ao_id", "profile", unique=True),
        Index("idx_scoring_runs_verdict", "verdict", "confidence"),
    )


class ScoringFeedback(Base):
    """Feedback utilisateur sur un scoring pour calibration."""

    __tablename__ = "scoring_feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scoring_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scoring_runs.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)
    user_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_override_verdict: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    calibration_delta: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("idx_scoring_feedbacks_user", "user_id", "applied"),)
