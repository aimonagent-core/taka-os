"""Migration 013 — Tables scraper_runs et submission_logs.

Tables creees :
  - scraper_runs    : Tracabilite des executions des scrapers
  - submission_logs : Journal des soumissions (deposant)

Dependances : 012 (tables fiducial)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '013_add_scraper_run_and_submission_log'
down_revision = '012_add_fiducial_tables'
branch_labels = None
depends_on = None


def upgrade():
    # ── ScraperRun ──
    op.create_table(
        'scraper_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), server_default='ok', nullable=False),
        sa.Column('count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('inserted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('duplicates', sa.Integer(), server_default='0', nullable=False),
        sa.Column('errors', sa.Integer(), server_default='0', nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('filter_where', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scraper_runs_source', 'scraper_runs', ['source'])
    op.create_index('ix_scraper_runs_started_at', 'scraper_runs', ['started_at'])

    # ── SubmissionLog ──
    op.create_table(
        'submission_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ao_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('is_mock', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('external_submission_id', sa.String(200), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('warning_message', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_submission_logs_ao_id', 'submission_logs', ['ao_id'])
    op.create_index('ix_submission_logs_platform', 'submission_logs', ['platform'])
    op.create_index('ix_submission_logs_submitted_at', 'submission_logs', ['submitted_at'])


def downgrade():
    op.drop_index('ix_submission_logs_submitted_at', table_name='submission_logs')
    op.drop_index('ix_submission_logs_platform', table_name='submission_logs')
    op.drop_index('ix_submission_logs_ao_id', table_name='submission_logs')
    op.drop_table('submission_logs')
    op.drop_index('ix_scraper_runs_started_at', table_name='scraper_runs')
    op.drop_index('ix_scraper_runs_source', table_name='scraper_runs')
    op.drop_table('scraper_runs')
