"""Migration 006b — Seed subscription tiers complets (free, pro, enterprise)."""

from alembic import op
import sqlalchemy as sa

revision = "006b_seed_tiers"
down_revision = "006_add_responses_submissions"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO subscription_tiers (
            id, name, label, max_aos_per_month, max_business_lines,
            max_users, max_storage_mb, monthly_price_eur, yearly_price_eur,
            includes_advanced_scoring, includes_multi_bl, includes_api_access,
            includes_priority_support, includes_custom_branding,
            is_active, created_at
        )
        VALUES
            (gen_random_uuid(), 'free', 'Free',
             10, 1, 1, 100,
             0.00, 0.00,
             false, false, false, false, false,
             true, NOW()),
            (gen_random_uuid(), 'pro', 'Pro',
             100, 5, 10, 1000,
             49.00, 490.00,
             true, true, false, true, false,
             true, NOW()),
            (gen_random_uuid(), 'enterprise', 'Enterprise',
             999999, 999, 999, 10000,
             199.00, 1990.00,
             true, true, true, true, true,
             true, NOW())
        ON CONFLICT (name) DO NOTHING
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM subscription_tiers
        WHERE name IN ('free', 'pro', 'enterprise')
        """
    )
