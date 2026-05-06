"""Migration 004 — Feature Flags, Subscription Tiers."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004_add_feature_flags"
down_revision = "003_add_business_lines"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "subscription_tiers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(20), unique=True, nullable=False),
        sa.Column("label", sa.String(50), nullable=False),
        sa.Column("max_aos_per_month", sa.Integer(), default=10, nullable=False),
        sa.Column("max_business_lines", sa.Integer(), default=1, nullable=False),
        sa.Column("max_users", sa.Integer(), default=1, nullable=False),
        sa.Column("max_storage_mb", sa.Integer(), default=100, nullable=False),
        sa.Column("monthly_price_eur", sa.Numeric(10, 2), nullable=True),
        sa.Column("yearly_price_eur", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "includes_advanced_scoring", sa.Boolean(), default=False, nullable=False
        ),
        sa.Column("includes_multi_bl", sa.Boolean(), default=False, nullable=False),
        sa.Column("includes_api_access", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "includes_priority_support", sa.Boolean(), default=False, nullable=False
        ),
        sa.Column(
            "includes_custom_branding", sa.Boolean(), default=False, nullable=False
        ),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        """
        INSERT INTO subscription_tiers (id, name, label, max_aos_per_month, max_business_lines, max_users, max_storage_mb, monthly_price_eur, yearly_price_eur, includes_advanced_scoring, includes_multi_bl, includes_api_access, includes_priority_support, includes_custom_branding, is_active, created_at)
        VALUES
            (gen_random_uuid(), 'free', 'Free', 10, 1, 1, 100, 0.00, 0.00, false, false, false, false, false, true, NOW()),
            (gen_random_uuid(), 'pro', 'Pro', 100, 5, 10, 1000, 49.00, 490.00, true, true, false, true, false, true, NOW()),
            (gen_random_uuid(), 'enterprise', 'Enterprise', 999999, 999, 999, 10000, 199.00, 1990.00, true, true, true, true, true, true, NOW())
        ON CONFLICT (name) DO NOTHING
    """
    )

    op.create_table(
        "plan_features",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("key", sa.String(50), unique=True, nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("min_tier", sa.String(20), default="free", nullable=False),
        sa.Column("enabled_globally", sa.Boolean(), default=True, nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_plan_features_enabled", "plan_features", ["enabled_globally"])

    op.execute(
        """
        INSERT INTO plan_features (id, key, label, min_tier, enabled_globally, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'scoring_v2', 'Scoring Engine V2', 'free', true, NOW(), NOW()),
            (gen_random_uuid(), 'multi_bl', 'Multi Business Lines', 'pro', true, NOW(), NOW()),
            (gen_random_uuid(), 'rapports_auto', 'Rapports automatiques', 'pro', true, NOW(), NOW()),
            (gen_random_uuid(), 'api_access', 'Acces API', 'enterprise', true, NOW(), NOW()),
            (gen_random_uuid(), 'advanced_dashboard', 'Dashboard avance', 'pro', true, NOW(), NOW()),
            (gen_random_uuid(), 'scoring_feedback', 'Feedback scoring', 'pro', true, NOW(), NOW()),
            (gen_random_uuid(), 'custom_branding', 'Personnalisation marque', 'enterprise', true, NOW(), NOW()),
            (gen_random_uuid(), 'priority_support', 'Support prioritaire', 'pro', true, NOW(), NOW()),
            (gen_random_uuid(), 'hil_autonomy', 'Autonomie HIL SUPERVISED+', 'enterprise', true, NOW(), NOW())
    """
    )

    op.add_column(
        "tenants",
        sa.Column(
            "subscription_tier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subscription_tiers.id"),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("tenants", "subscription_tier_id")
    op.drop_table("plan_features")
    op.drop_table("subscription_tiers")
