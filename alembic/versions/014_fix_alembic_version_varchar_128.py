"""Migration 014 — Fix alembic_version.version_num VARCHAR(32) → VARCHAR(128).

BUG : Alembic cree la table alembic_version avec version_num en VARCHAR(32).
Les revisions 011, 012, 013 ont des noms de 33 à 36 caractères,
ce qui provoque une StringDataRightTruncationError lors de upgrade head.

Fix : ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(128);
"""

from alembic import op

revision = "014_fix_alembic_version_varchar_128"
down_revision = "013_add_scraper_run_and_submission_log"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(128);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(32);
        """
    )
