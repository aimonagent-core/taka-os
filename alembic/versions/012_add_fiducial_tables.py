"""Migration 012 — Tables fiducial (comptabilite).

Tables creees :
  - plan_comptable        : Plan de compte du tenant
  - journal_entries       : Ecritures comptables (FEC)
  - ao_accounting_links   : Liens AO-comptabilite

Dependances : 011 (API publique + collaboration)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '012_add_fiducial_tables'
down_revision = '011_add_api_collab_workflow_tables'
branch_labels = None
depends_on = None


def upgrade():
    # ── Plan Comptable ──
    op.create_table(
        'plan_comptable',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_number', sa.String(20), nullable=False),
        sa.Column('account_name', sa.String(255), nullable=False),
        sa.Column('account_type', postgresql.ENUM('expense', 'income', 'asset', 'liability', name='account_type'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_default', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_plancompt_tenant_num', 'plan_comptable', ['tenant_id', 'account_number'])

    # ── Journal Entries ──
    op.create_table(
        'journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entry_number', sa.String(50), nullable=False),
        sa.Column('entry_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('account_number', sa.String(20), nullable=False),
        sa.Column('account_label', sa.String(255), nullable=False),
        sa.Column('debit', sa.Numeric(15, 2), nullable=True),
        sa.Column('credit', sa.Numeric(15, 2), nullable=True),
        sa.Column('label', sa.Text(), nullable=False),
        sa.Column('ao_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('event_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ao_id'], ['aos.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_journal_tenant_date', 'journal_entries', ['tenant_id', 'entry_date'])
    op.create_index('idx_journal_tenant_fy', 'journal_entries', ['tenant_id', 'fiscal_year'])
    op.create_index('idx_journal_ao', 'journal_entries', ['ao_id'])

    # ── AO Accounting Links ──
    op.create_table(
        'ao_accounting_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('ao_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('final_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('margin_percent', sa.Numeric(5, 2), server_default='15.0', nullable=False),
        sa.Column('journal_entry_ids', postgresql.JSON(astext_type=sa.Text()), default=list, nullable=False),
        sa.Column('is_exported', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('exported_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('exported_format', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ao_id'], ['aos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('ao_id'),
    )


def downgrade():
    op.drop_table('ao_accounting_links')
    op.drop_index('idx_journal_ao', table_name='journal_entries')
    op.drop_index('idx_journal_tenant_fy', table_name='journal_entries')
    op.drop_index('idx_journal_tenant_date', table_name='journal_entries')
    op.drop_table('journal_entries')
    op.drop_index('idx_plancompt_tenant_num', table_name='plan_comptable')
    op.drop_table('plan_comptable')
    op.execute('DROP TYPE IF EXISTS account_type')
