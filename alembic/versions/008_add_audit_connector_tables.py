"""Migration 008 — Ajout des tables audit, credentials plateforme, anomalies, rapports."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "008_add_audit_connector_tables"
down_revision = "007_add_billing_email_tables"
branch_labels = None
depends_on = None


def upgrade():
    # Platform Credentials
    op.create_table(
        "platform_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform_type", sa.String(30), nullable=False),
        sa.Column("platform_name", sa.String(100), nullable=True),
        sa.Column("username", sa.Text(), nullable=True),
        sa.Column("password", sa.Text(), nullable=True),
        sa.Column("api_key", sa.Text(), nullable=True),
        sa.Column("certificate_pem", sa.Text(), nullable=True),
        sa.Column("additional_data", sa.JSON(), nullable=True),
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column("webhook_url", sa.String(500), nullable=True),
        sa.Column("is_validated", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_platcred_tenant_platform", "platform_credentials", ["tenant_id", "platform_type"])
    op.create_index("idx_platcred_active", "platform_credentials", ["tenant_id", "is_active"])

    # Audit Logs
    op.create_table(
        "audit_trail",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_type", sa.String(20), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_email", sa.String(255), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("action_category", sa.String(30), nullable=False),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("target_display", sa.String(255), nullable=True),
        sa.Column("before_state", sa.JSON(), nullable=True),
        sa.Column("after_state", sa.JSON(), nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("severity", sa.String(10), server_default="info", nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_tenant_action", "audit_trail", ["tenant_id", "action"])
    op.create_index("idx_audit_tenant_category", "audit_trail", ["tenant_id", "action_category"])
    op.create_index("idx_audit_tenant_created", "audit_trail", ["tenant_id", "created_at"])
    op.create_index("idx_audit_target", "audit_trail", ["target_type", "target_id"])
    op.create_index("idx_audit_actor", "audit_trail", ["actor_type", "actor_id"])

    # Anomaly Detections
    op.create_table(
        "anomaly_detections",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("detected_by", sa.String(30), nullable=False),
        sa.Column("anomaly_type", sa.String(50), nullable=False),
        sa.Column("severity", postgresql.ENUM("low", "medium", "high", "critical", name="anomaly_severity"), nullable=False),
        sa.Column("status", postgresql.ENUM("open", "investigating", "false_positive", "resolved", name="anomaly_status"), server_default="open", nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("affected_resource_type", sa.String(30), nullable=True),
        sa.Column("affected_resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("detection_data", sa.JSON(), nullable=True),
        sa.Column("ai_analysis", sa.Text(), nullable=True),
        sa.Column("ai_recommendation", sa.Text(), nullable=True),
        sa.Column("resolved_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_anomaly_tenant_status", "anomaly_detections", ["tenant_id", "status"])
    op.create_index("idx_anomaly_tenant_severity", "anomaly_detections", ["tenant_id", "severity"])
    op.create_index("idx_anomaly_type", "anomaly_detections", ["anomaly_type", "created_at"])

    # Compliance Reports
    op.create_table(
        "compliance_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_type", sa.String(30), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pdf_url", sa.String(500), nullable=True),
        sa.Column("pdf_size_bytes", sa.Integer(), nullable=True),
        sa.Column("summary_data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(20), server_default="generating", nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("regulation_framework", sa.String(30), server_default="french_cmp", nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_compliance_tenant_type", "compliance_reports", ["tenant_id", "report_type"])
    op.create_index("idx_compliance_tenant_period", "compliance_reports", ["tenant_id", "period_start"])

    # Submission Receipts
    op.create_table(
        "submission_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform_reference", sa.String(255), nullable=True),
        sa.Column("platform_receipt_url", sa.String(500), nullable=True),
        sa.Column("platform_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("receipt_data", sa.JSON(), nullable=True),
        sa.Column("pdf_url", sa.String(500), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("verification_method", sa.String(30), nullable=True),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id"),
    )
    op.create_index("idx_receipt_tenant", "submission_receipts", ["tenant_id"])


def downgrade():
    op.drop_index("idx_receipt_tenant", table_name="submission_receipts")
    op.drop_table("submission_receipts")
    op.drop_index("idx_compliance_tenant_period", table_name="compliance_reports")
    op.drop_index("idx_compliance_tenant_type", table_name="compliance_reports")
    op.drop_table("compliance_reports")
    op.drop_index("idx_anomaly_type", table_name="anomaly_detections")
    op.drop_index("idx_anomaly_tenant_severity", table_name="anomaly_detections")
    op.drop_index("idx_anomaly_tenant_status", table_name="anomaly_detections")
    op.drop_table("anomaly_detections")
    op.drop_index("idx_audit_actor", table_name="audit_trail")
    op.drop_index("idx_audit_target", table_name="audit_trail")
    op.drop_index("idx_audit_tenant_created", table_name="audit_trail")
    op.drop_index("idx_audit_tenant_category", table_name="audit_trail")
    op.drop_index("idx_audit_tenant_action", table_name="audit_trail")
    op.drop_table("audit_trail")
    op.drop_index("idx_platcred_active", table_name="platform_credentials")
    op.drop_index("idx_platcred_tenant_platform", table_name="platform_credentials")
    op.drop_table("platform_credentials")
    op.execute("DROP TYPE IF EXISTS anomaly_severity")
    op.execute("DROP TYPE IF EXISTS anomaly_status")
