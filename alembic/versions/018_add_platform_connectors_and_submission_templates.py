"""Migration 018 — Ajoute platform_connectors et submission_templates.

Connecteurs generiques pour soumission reelle sur differentes plateformes.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "018_add_platform_connectors_and_submission_templates"
down_revision = "017_add_deadline_notified_and_notification_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Table platform_connectors
    op.create_table(
        "platform_connectors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("platform_type", sa.String(50), nullable=False),
        sa.Column("config", postgresql.JSON, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("test_status", sa.String(20), nullable=False, server_default="never_tested"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_platconn_tenant_type", "platform_connectors", ["tenant_id", "platform_type"])
    op.create_index("idx_platconn_active", "platform_connectors", ["tenant_id", "is_active"])

    # Table submission_templates
    op.create_table(
        "submission_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("platform_connector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("platform_connectors.id"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("fields", postgresql.JSON, nullable=False, server_default="{}"),
        sa.Column("documents_required", postgresql.JSON, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_subtmpl_tenant_connector", "submission_templates", ["tenant_id", "platform_connector_id"])


def downgrade() -> None:
    op.drop_index("idx_subtmpl_tenant_connector", table_name="submission_templates")
    op.drop_table("submission_templates")
    op.drop_index("idx_platconn_active", table_name="platform_connectors")
    op.drop_index("idx_platconn_tenant_type", table_name="platform_connectors")
    op.drop_table("platform_connectors")
