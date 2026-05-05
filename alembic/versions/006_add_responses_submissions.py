"""Migration 006 — Tables response_templates, generated_responses, submission_platforms, submissions."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '006_add_responses_submissions'
down_revision = '005_fix_embedding_dimension'
branch_labels = None
depends_on = None


def upgrade():
    # --- response_templates ---
    op.create_table(
        'response_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('business_line_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('business_lines.id'), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(30), default='letter', nullable=False),
        sa.Column('template_content', sa.Text(), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_default', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_resp_templates_tenant', 'response_templates', ['tenant_id', 'category', 'is_default'])
    op.create_index('idx_resp_templates_bl', 'response_templates', ['business_line_id', 'category'])

    # --- generated_responses ---
    op.create_table(
        'generated_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('ao_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('aos.id'), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('response_templates.id'), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('structured_content', sa.JSON(), nullable=True),
        sa.Column('tokens_input', sa.Integer(), default=0, nullable=False),
        sa.Column('tokens_output', sa.Integer(), default=0, nullable=False),
        sa.Column('generation_time_ms', sa.Integer(), default=0, nullable=False),
        sa.Column('model_used', sa.String(50), default='mistral-large-latest', nullable=False),
        sa.Column('status', sa.String(20), default='generated', nullable=False),
        sa.Column('hil_status', sa.String(20), default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_gen_resp_ao_category', 'generated_responses', ['ao_id', 'category'])
    op.create_index('idx_gen_resp_status', 'generated_responses', ['status', 'hil_status'])

    # --- submission_platforms ---
    op.create_table(
        'submission_platforms',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('platform_type', sa.String(30), nullable=False),
        sa.Column('base_url', sa.Text(), nullable=False),
        sa.Column('is_mock', sa.Boolean(), default=True, nullable=False),
        sa.Column('api_config', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_sub_plat_tenant_type', 'submission_platforms', ['tenant_id', 'platform_type'])

    # --- submissions ---
    op.create_table(
        'submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('generated_response_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('generated_responses.id'), nullable=False),
        sa.Column('platform_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('submission_platforms.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('platform_reference', sa.String(255), nullable=True),
        sa.Column('platform_response', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0, nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_submissions_status', 'submissions', ['status', 'retry_count'])

    # Seed feature flag generation_ia
    op.execute("""
        INSERT INTO plan_features (id, key, label, min_tier, enabled_globally, created_at, updated_at)
        SELECT gen_random_uuid(), 'generation_ia', 'Generation IA de reponses', 'pro', true, NOW(), NOW()
        WHERE NOT EXISTS (SELECT 1 FROM plan_features WHERE key = 'generation_ia')
    """)

    # Seed plateformes mock pour chaque tenant existant
    op.execute("""
        INSERT INTO submission_platforms (id, tenant_id, name, platform_type, base_url, is_mock, is_active, created_at)
        SELECT gen_random_uuid(), t.id, 'BOAMP (France)', 'boamp', 'https://www.boamp.fr', true, true, NOW()
        FROM tenants t
        WHERE NOT EXISTS (
            SELECT 1 FROM submission_platforms sp WHERE sp.tenant_id = t.id AND sp.platform_type = 'boamp'
        )
    """)
    op.execute("""
        INSERT INTO submission_platforms (id, tenant_id, name, platform_type, base_url, is_mock, is_active, created_at)
        SELECT gen_random_uuid(), t.id, 'JOUE / TED (UE)', 'joue', 'https://ted.europa.eu', true, true, NOW()
        FROM tenants t
        WHERE NOT EXISTS (
            SELECT 1 FROM submission_platforms sp WHERE sp.tenant_id = t.id AND sp.platform_type = 'joue'
        )
    """)
    op.execute("""
        INSERT INTO submission_platforms (id, tenant_id, name, platform_type, base_url, is_mock, is_active, created_at)
        SELECT gen_random_uuid(), t.id, 'e-Notification (Belgique)', 'enotification', 'https://een.publicprocurement.be', true, true, NOW()
        FROM tenants t
        WHERE NOT EXISTS (
            SELECT 1 FROM submission_platforms sp WHERE sp.tenant_id = t.id AND sp.platform_type = 'enotification'
        )
    """)
    op.execute("""
        INSERT INTO submission_platforms (id, tenant_id, name, platform_type, base_url, is_mock, is_active, created_at)
        SELECT gen_random_uuid(), t.id, 'Marches Publics (Maroc)', 'marche_public', 'https://www.marchespublics.gov.ma', true, true, NOW()
        FROM tenants t
        WHERE NOT EXISTS (
            SELECT 1 FROM submission_platforms sp WHERE sp.tenant_id = t.id AND sp.platform_type = 'marche_public'
        )
    """)


def downgrade():
    op.drop_table('submissions')
    op.drop_table('submission_platforms')
    op.drop_table('generated_responses')
    op.drop_table('response_templates')
