"""Migration 010 — Ajout table analytics_snapshots + index sources.

Tables :
  - analytics_snapshots (NOUVEAU)
  - sources : ajout colonnes schedule, weight
  - aos : index supplementaires pour analytics
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "010_add_analytics_tables"
down_revision = "009_audit_tables_cleanup"


def upgrade():
    # analytics_snapshots
    op.execute("""
        CREATE TABLE IF NOT EXISTS analytics_snapshots (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            tenant_id UUID NOT NULL,
            snapshot_type VARCHAR(20) DEFAULT 'daily' NOT NULL,
            snapshot_date TIMESTAMP WITH TIME ZONE NOT NULL,
            data JSON NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshot_tenant_date
        ON analytics_snapshots (tenant_id, snapshot_date)
    """)

    # Sources
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'sources' AND column_name = 'schedule') THEN
                ALTER TABLE sources ADD COLUMN schedule VARCHAR(50);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'sources' AND column_name = 'weight') THEN
                ALTER TABLE sources ADD COLUMN weight INTEGER DEFAULT 0 NOT NULL;
            END IF;
        END
        $$;
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_sources_active_tenant ON sources (is_active)")

    # AO indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_ao_status_tenant ON aos (status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ao_created_tenant ON aos (created_at)")

    # ScoringRuns
    op.execute("CREATE INDEX IF NOT EXISTS idx_scoring_ao_tenant ON scoring_runs (ao_id)")


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_scoring_ao_tenant")
    op.execute("DROP INDEX IF EXISTS idx_ao_created_tenant")
    op.execute("DROP INDEX IF EXISTS idx_ao_status_tenant")
    op.execute("DROP INDEX IF EXISTS idx_sources_active_tenant")
    op.execute("ALTER TABLE sources DROP COLUMN IF EXISTS weight")
    op.execute("ALTER TABLE sources DROP COLUMN IF EXISTS schedule")
    op.execute("DROP INDEX IF EXISTS idx_snapshot_tenant_date")
    op.execute("DROP TABLE IF EXISTS analytics_snapshots")
