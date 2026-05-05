# File: app/models/ao.py
# Purpose: Core SQLAlchemy models with roles, tenants, audit, memory, and feature flags
# Dependencies: app.database.Base, pgvector.sqlalchemy.Vector, sqlalchemy.orm

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    TENANT_MANAGER = "tenant_manager"
    TENANT_COLLABORATOR = "tenant_collaborator"
    VIEWER = "viewer"


class TenantType(str, enum.Enum):
    SOUMISSIONNAIRE = "soumissionnaire"
    ACHETEUR = "acheteur"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class FeatureFlagScope(str, enum.Enum):
    GLOBAL = "global"
    TENANT = "tenant"
    USER = "user"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    INVITATION_SENT = "invitation_sent"
    INVITATION_ACCEPTED = "invitation_accepted"


class MemoryType(str, enum.Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    TRANSACTIONAL = "transactional"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PARSING = "parsing"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ERROR = "error"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[TenantType] = mapped_column(
        Enum(TenantType), nullable=False, default=TenantType.SOUMISSIONNAIRE
    )
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    settings: Mapped[dict | None] = mapped_column(JSON, default=dict)
    billing_plan: Mapped[str | None] = mapped_column(String(50), default="free")
    max_users: Mapped[int | None] = mapped_column(Integer, default=5)
    max_storage_mb: Mapped[int | None] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    users: Mapped[list["User"]] = relationship(
        "User", back_populates="tenant", lazy="selectin"
    )
    feature_flags: Mapped[list["FeatureFlag"]] = relationship(
        "FeatureFlag", back_populates="tenant", lazy="selectin"
    )
    memory_entries: Mapped[list["MemoryTenant"]] = relationship(
        "MemoryTenant", back_populates="tenant", lazy="selectin"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="tenant", lazy="selectin"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.VIEWER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_backup_codes_hash: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="user"
    )
    invitations_sent: Mapped[list["UserInvitation"]] = relationship(
        "UserInvitation",
        foreign_keys="UserInvitation.invited_by_id",
        back_populates="inviter",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="user"
    )
    memory_entries: Mapped[list["MemorySession"]] = relationship(
        "MemorySession", back_populates="user"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="user"
    )


class UserInvitation(Base):
    __tablename__ = "user_invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.VIEWER
    )
    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus), default=InvitationStatus.PENDING
    )
    invited_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")
    inviter: Mapped["User"] = relationship(
        "User", foreign_keys=[invited_by_id], back_populates="invitations_sent"
    )


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[FeatureFlagScope] = mapped_column(
        Enum(FeatureFlagScope), nullable=False, default=FeatureFlagScope.GLOBAL
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    kill_switch: Mapped[bool] = mapped_column(Boolean, default=False)
    gated_by_plan: Mapped[str | None] = mapped_column(String(50))
    rollout_percentage: Mapped[int] = mapped_column(Integer, default=100)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    tenant: Mapped["Tenant | None"] = relationship(
        "Tenant", back_populates="feature_flags"
    )
    user: Mapped["User | None"] = relationship("User")


class MemoryGlobal(Base):
    __tablename__ = "memory_global"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    data_type: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(100))
    ttl_seconds: Mapped[int | None] = mapped_column(Integer)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    importance_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MemoryTenant(Base):
    __tablename__ = "memory_tenant"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    data_type: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(100))
    ttl_seconds: Mapped[int | None] = mapped_column(Integer)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    importance_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant", back_populates="memory_entries"
    )


class MemorySession(Base):
    __tablename__ = "memory_session"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    data_type: Mapped[str | None] = mapped_column(String(50))
    ttl_seconds: Mapped[int | None] = mapped_column(Integer, default=3600)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="memory_entries")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(255))
    payload_before: Mapped[dict | None] = mapped_column(JSON)
    payload_after: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    previous_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tenant: Mapped["Tenant | None"] = relationship(
        "Tenant", back_populates="audit_logs"
    )
    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")


class LLMCallLog(Base):
    __tablename__ = "llm_call_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    total_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    prompt_preview: Mapped[str | None] = mapped_column(Text)
    response_preview: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="success")
    error_message: Mapped[str | None] = mapped_column(Text)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")
    payload: Mapped[dict | None] = mapped_column(JSON)
    source: Mapped[str | None] = mapped_column(String(100))
    trace_id: Mapped[str | None] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class StateSnapshot(Base):
    __tablename__ = "state_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    state_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    snapshot_reason: Mapped[str | None] = mapped_column(String(100))
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(64), nullable=False, default="application/pdf")
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING
    )
    parse_level_reached: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parse_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    extracted_entities: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    validation_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")


class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    memory_type: Mapped[MemoryType] = mapped_column(String(32), nullable=False, index=True)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    ttl_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decay_factor: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    consolidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MemoryConsolidation(Base):
    __tablename__ = "memory_consolidations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    memory_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memory_entries.id"), nullable=False, index=True
    )
    from_entries: Mapped[list[uuid.UUID]] = mapped_column(JSON, nullable=False)
    consolidation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    previous_version: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ValidationAudit(Base):
    __tablename__ = "validation_audit"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    gate_name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    output_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class HumanDecision(Base):
    __tablename__ = "human_decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    autonomy_level: Mapped[int] = mapped_column(Integer, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(32), nullable=False)
    decision_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    context_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class HILRequest(Base):
    __tablename__ = "hil_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    autonomy_level: Mapped[int] = mapped_column(Integer, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(32), nullable=False)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decided_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class AO(Base):
    __tablename__ = "ao"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    reference_number: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    extra_metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")
    documents: Mapped[list["DocumentAO"]] = relationship("DocumentAO", back_populates="ao")


class DocumentAO(Base):
    """Legacy Document model renamed to avoid conflict with new Document model."""
    __tablename__ = "ao_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    ao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ao.id"), nullable=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(100))
    file_size: Mapped[int | None] = mapped_column(Integer)
    vector_embedding: Mapped[Any | None] = mapped_column(Vector(1536), nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    ao: Mapped["AO | None"] = relationship("AO", back_populates="documents")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="active")
    extra_metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    vector_embedding: Mapped[Any | None] = mapped_column(Vector(1536), nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )
