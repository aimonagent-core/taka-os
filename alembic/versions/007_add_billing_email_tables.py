"""Migration 007 — Billing & Email tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "007_add_billing_email_tables"
down_revision = "006b_seed_tiers"
branch_labels = None
depends_on = None


def upgrade():
    # --- tenant_subscriptions ---
    op.create_table(
        "tenant_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, unique=True),
        sa.Column("tier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subscription_tiers.id"), nullable=False),
        sa.Column("stripe_customer_id", sa.String(100), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(100), nullable=True),
        sa.Column("stripe_price_id", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tenant_sub_tenant_id", "tenant_subscriptions", ["tenant_id"])
    op.create_index("idx_tenant_sub_stripe_cust", "tenant_subscriptions", ["stripe_customer_id"])
    op.create_index("idx_tenant_sub_stripe_sub", "tenant_subscriptions", ["stripe_subscription_id"])

    # --- subscription_events ---
    op.create_table(
        "subscription_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_subscription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant_subscriptions.id"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("stripe_event_id", sa.String(100), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(3), server_default="EUR", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_sub_events_tenant_type", "subscription_events", ["tenant_id", "event_type"])
    op.create_index("idx_sub_events_stripe_event", "subscription_events", ["stripe_event_id"])

    # --- email_logs ---
    op.create_table(
        "email_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("email_type", sa.String(30), nullable=False),
        sa.Column("recipient", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("provider_message_id", sa.String(100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_email_logs_user", "email_logs", ["user_id", "email_type"])
    op.create_index("idx_email_logs_tenant", "email_logs", ["tenant_id"])

    # --- email_preferences ---
    op.create_table(
        "email_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("daily_alert_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("daily_alert_time", sa.String(5), server_default="08:00", nullable=False),
        sa.Column("payment_notifications", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("marketing_emails", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_email_prefs_user", "email_preferences", ["user_id"])


def downgrade():
    op.drop_index("idx_email_prefs_user", table_name="email_preferences")
    op.drop_table("email_preferences")
    op.drop_index("idx_email_logs_tenant", table_name="email_logs")
    op.drop_index("idx_email_logs_user", table_name="email_logs")
    op.drop_table("email_logs")
    op.drop_index("idx_sub_events_stripe_event", table_name="subscription_events")
    op.drop_index("idx_sub_events_tenant_type", table_name="subscription_events")
    op.drop_table("subscription_events")
    op.drop_index("idx_tenant_sub_stripe_sub", table_name="tenant_subscriptions")
    op.drop_index("idx_tenant_sub_stripe_cust", table_name="tenant_subscriptions")
    op.drop_index("idx_tenant_sub_tenant_id", table_name="tenant_subscriptions")
    op.drop_table("tenant_subscriptions")
