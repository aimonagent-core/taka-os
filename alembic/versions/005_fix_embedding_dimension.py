"""Migration 005 — Corrige la dimension d'embedding ao_chunks : 768 → 1024"""
from alembic import op

revision = "005_fix_embedding_dimension"
down_revision = "004_add_feature_flags"
branch_labels = None
depends_on = None


def upgrade():
    # pgvector permet ALTER TYPE vector(768) → vector(1024)
    op.execute("ALTER TABLE ao_chunks ALTER COLUMN embedding TYPE vector(1024)")
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1024)")
    op.execute("ALTER TABLE memory_entries ALTER COLUMN embedding TYPE vector(1024)")


def downgrade():
    op.execute("ALTER TABLE ao_chunks ALTER COLUMN embedding TYPE vector(768)")
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768)")
    op.execute("ALTER TABLE memory_entries ALTER COLUMN embedding TYPE vector(768)")
