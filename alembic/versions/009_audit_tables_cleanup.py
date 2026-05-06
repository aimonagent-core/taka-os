"""Migration 009 — Cleanup et unification audit (legacy -> audit_trail).

- Migre les donnees audit_logs (S2) vers audit_trail (S5)
- Renomme audit_logs en audit_logs_legacy pour archive
- S'assure que les index existent sur audit_trail
- Idempotent : peut etre re-executee sans erreur.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '009_audit_tables_cleanup'
down_revision = '008_add_audit_connector_tables'


def upgrade():
    # 1. S'assurer que les types ENUM existent
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'anomaly_severity') THEN
                CREATE TYPE anomaly_severity AS ENUM ('low', 'medium', 'high', 'critical');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'anomaly_status') THEN
                CREATE TYPE anomaly_status AS ENUM ('open', 'investigating', 'false_positive', 'resolved');
            END IF;
        END
        $$;
    """)

    # 2. Migrer les donnees legacy audit_logs -> audit_trail (idempotent via NOT EXISTS)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables
                       WHERE table_schema = 'public' AND table_name = 'audit_logs') THEN
                INSERT INTO audit_trail (
                    id, tenant_id, actor_type, actor_id, actor_email,
                    action, action_category, target_type, target_id, target_display,
                    before_state, after_state, change_summary, ip_address, user_agent,
                    request_id, event_metadata, severity, created_at
                )
                SELECT
                    gen_random_uuid(),
                    al.tenant_id,
                    'user',
                    al.user_id,
                    NULL,
                    al.action::text,
                    CASE
                        WHEN al.action::text IN ('LOGIN', 'LOGOUT', 'MFA_ENABLED', 'MFA_DISABLED') THEN 'auth'
                        WHEN al.action::text IN ('CREATE', 'READ', 'UPDATE', 'DELETE') THEN 'crud'
                        WHEN al.action::text IN ('INVITATION_SENT', 'INVITATION_ACCEPTED') THEN 'invitation'
                        ELSE 'unknown'
                    END,
                    al.entity_type,
                    CASE
                        WHEN al.entity_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                        THEN al.entity_id::uuid
                        ELSE NULL
                    END,
                    NULL,
                    al.payload_before,
                    al.payload_after,
                    NULL,
                    al.ip_address,
                    al.user_agent,
                    NULL,
                    jsonb_build_object(
                        'hash_chain_legacy', jsonb_build_object(
                            'previous_hash', al.previous_hash,
                            'hash', al.hash
                        ),
                        'legacy_entity_id', CASE
                            WHEN al.entity_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                            THEN NULL
                            ELSE al.entity_id
                        END,
                        'migrated_from', 'audit_logs',
                        'migrated_at', NOW()
                    ),
                    'info',
                    al.created_at
                FROM audit_logs al
                WHERE NOT EXISTS (
                    SELECT 1 FROM audit_trail at2
                    WHERE at2.event_metadata->>'migrated_from' = 'audit_logs'
                      AND (at2.event_metadata->'hash_chain_legacy'->>'hash') = al.hash
                );
            END IF;
        END
        $$;
    """)

    # 3. Renommer audit_logs en audit_logs_legacy (archive)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables
                       WHERE table_schema = 'public' AND table_name = 'audit_logs')
               AND NOT EXISTS (SELECT 1 FROM information_schema.tables
                               WHERE table_schema = 'public' AND table_name = 'audit_logs_legacy') THEN
                ALTER TABLE audit_logs RENAME TO audit_logs_legacy;
            END IF;
        END
        $$;
    """)

    # 4. S'assurer que les index audit_trail existent
    for idx_name, cols in [
        ("idx_audit_tenant_action", "tenant_id, action"),
        ("idx_audit_tenant_category", "tenant_id, action_category"),
        ("idx_audit_tenant_created", "tenant_id, created_at"),
        ("idx_audit_target", "target_type, target_id"),
        ("idx_audit_actor", "actor_type, actor_id"),
    ]:
        op.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_indexes
                              WHERE indexname = '{idx_name}') THEN
                    CREATE INDEX {idx_name} ON audit_trail ({cols});
                END IF;
            END
            $$;
        """)

    # 5. S'assurer que submission_receipts a bien la contrainte unique
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint
                          WHERE conname = 'submission_receipts_submission_id_key') THEN
                ALTER TABLE submission_receipts ADD CONSTRAINT submission_receipts_submission_id_key
                    UNIQUE (submission_id);
            END IF;
        END
        $$;
    """)


def downgrade():
    # Cleanup est idempotent — downgrade ne fait rien de destructif.
    # Pour un vrai retour arriere, il faudrait gerer manuellement audit_logs_legacy.
    pass
