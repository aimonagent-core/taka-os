"""Modeles pour les workflows d'approbation."""

from datetime import datetime
from typing import Optional
import uuid
from enum import Enum as PyEnum

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Integer, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WorkflowTrigger(str, PyEnum):
    RESPONSE_SUBMIT = "response_submit"
    RESPONSE_GENERATE = "response_generate"
    AO_PIN = "ao_pin"
    MANUAL = "manual"


class ApprovalWorkflow(Base):
    """Definition d'un workflow d'approbation pour un tenant."""

    __tablename__ = "approval_workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger: Mapped[str] = mapped_column(String(30), nullable=False)
    business_line_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("business_lines.id"), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_workflow_tenant_trigger", "tenant_id", "trigger"),
    )


class ApprovalStep(Base):
    """Etape individuelle d'un workflow d'approbation."""

    __tablename__ = "approval_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("approval_workflows.id"), nullable=False)

    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(String(30), nullable=False)
    specific_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_approvalstep_workflow", "workflow_id", "step_order"),
    )


class ApprovalRequest(Base):
    """Demande d'approbation en cours."""

    __tablename__ = "approval_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("approval_workflows.id"), nullable=False)

    requester_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ao_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("aos.id"), nullable=True)
    response_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("generated_responses.id"), nullable=True)

    current_step_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_approvalreq_tenant_status", "tenant_id", "status"),
        Index("idx_approvalreq_requester", "requester_id", "status"),
    )


class ApprovalDecision(Base):
    """Decision prise sur une demande d'approbation."""

    __tablename__ = "approval_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("approval_requests.id"), nullable=False, index=True)
    step_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("approval_steps.id"), nullable=False)
    approver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
