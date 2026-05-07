"""Migration 017 — Ajoute deadline_notified aux AO et index notifications.

Permet de tracker les AO dont la deadline a deja ete notifiee pour eviter
les doublons de notifications deadline_warning.
"""

from alembic import op
import sqlalchemy as sa

revision = "017_add_deadline_notified_and_notification_index"
down_revision = "016_add_procedure_type_mapping"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. deadline_notified sur aos
    op.add_column(
        "aos",
        sa.Column("deadline_notified", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )

    # 2. Index composite sur in_app_notifications pour requetes rapides
    op.create_index(
        "idx_notif_tenant_type_unread",
        "in_app_notifications",
        ["tenant_id", "notification_type", "is_read"],
    )


def downgrade() -> None:
    op.drop_index("idx_notif_tenant_type_unread", table_name="in_app_notifications")
    op.drop_column("aos", "deadline_notified")
