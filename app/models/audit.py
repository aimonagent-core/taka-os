"""Modeles pour l'audit trail, les credentials plateforme, et les rapports de conformite."""
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum as PyEnum

from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, Boolean, JSON, Index, func, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PlatformType(str, PyEnum):
    """Types de plateformes d'achats publics supportees."""
    BOAMP = "boamp"
    E_NOTIFICATION = "e_notification"
    MARCHE_PUBLIC_MA = "maroc"
    TED = "ted"
    CUSTOM = "custom"


class PlatformCredential(Base):
    """Credentials d'authentification pour une plateforme d'achat public."""
    __tablename__ = "platform_credentials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    platform_type: Mapped[str] = mapped_column(String(30), nullable=False)
    platform_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    username: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    password: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    certificate_pem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_platcred_tenant_platform", "tenant_id", "platform_type"),
        Index("idx_platcred_active", "tenant_id", "is_active"),
    )


class AuditAction(str, PyEnum):
    """Types d'actions auditees."""
    AO_CREATED = "ao_created"
    AO_UPDATED = "ao_updated"
    AO_VIEWED = "ao_viewed"
    AO_SCORED = "ao_scored"
    AO_DISMISSED = "ao_dismissed"
    AO_PINNED = "ao_pinned"
    SCORING_RUN = "scoring_run"
    SCORING_FEEDBACK = "scoring_feedback"
    RESPONSE_GENERATED = "response_generated"
    RESPONSE_EDITED = "response_edited"
    RESPONSE_APPROVED = "response_approved"
    RESPONSE_REJECTED = "response_rejected"
    SUBMISSION_PREPARED = "submission_prepared"
    SUBMITTED = "submitted"
    SUBMISSION_CONFIRMED = "submission_confirmed"
    SUBMISSION_FAILED = "submission_failed"
    SUBMISSION_RETRIED = "submission_retried"
    BL_CREATED = "bl_created"
    BL_UPDATED = "bl_updated"
    TEMPLATE_CREATED = "template_created"
    TEMPLATE_UPDATED = "template_updated"
    CREDENTIAL_CREATED = "credential_created"
    CREDENTIAL_UPDATED = "credential_updated"
    CREDENTIAL_DELETED = "credential_deleted"
    USER_INVITED = "user_invited"
    USER_ROLE_CHANGED = "user_role_changed"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPDATED = "subscription_updated"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    SETTING_CHANGED = "setting_changed"
    FEATURE_FLAG_TOGGLED = "feature_flag_toggled"


class AuditTrail(Base):
    """Entree d'audit trail — chaque action importante du systeme."""
    __tablename__ = "audit_trail"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    action: Mapped[str] = mapped_column(String(50), nullable=False)
    action_category: Mapped[str] = mapped_column(String(30), nullable=False)

    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    target_display: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    before_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    after_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    severity: Mapped[str] = mapped_column(String(10), default="info", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index("idx_audit_tenant_action", "tenant_id", "action"),
        Index("idx_audit_tenant_category", "tenant_id", "action_category"),
        Index("idx_audit_tenant_created", "tenant_id", "created_at"),
        Index("idx_audit_target", "target_type", "target_id"),
        Index("idx_audit_actor", "actor_type", "actor_id"),
    )


class AnomalySeverity(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyStatus(str, PyEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class AnomalyDetection(Base):
    """Anomalie detectee par l'Agent Auditor."""
    __tablename__ = "anomaly_detections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    detected_by: Mapped[str] = mapped_column(String(30), nullable=False)

    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(SQLEnum(AnomalySeverity, name="anomaly_severity"), nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(AnomalyStatus, name="anomaly_status"), default=AnomalyStatus.OPEN, nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_resource_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    affected_resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    detection_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    resolved_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_anomaly_tenant_status", "tenant_id", "status"),
        Index("idx_anomaly_tenant_severity", "tenant_id", "severity"),
        Index("idx_anomaly_type", "anomaly_type", "created_at"),
    )


class ComplianceReport(Base):
    """Rapport de conformite aux marches publics genere par le systeme."""
    __tablename__ = "compliance_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    report_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    pdf_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    summary_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="generating", nullable=False)
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    regulation_framework: Mapped[str] = mapped_column(String(30), default="french_cmp", nullable=False)

    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_compliance_tenant_type", "tenant_id", "report_type"),
        Index("idx_compliance_tenant_period", "tenant_id", "period_start"),
    )


class SubmissionReceipt(Base):
    """Preuve de soumission telechargeable apres un depot reel."""
    __tablename__ = "submission_receipts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, unique=True, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    platform_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    platform_receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    platform_submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    receipt_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    verification_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
