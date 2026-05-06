"""Migration 011 — API publique, collaboration, workflow, notifications.

Tables creees :
  - external_api_keys       : Cles API publiques
  - comments                : Commentaires sur AO
  - comment_mentions        : Mentions @utilisateur
  - approval_workflows      : Workflows d'approbation
  - approval_steps          : Etapes des workflows
  - approval_requests       : Demandes en cours
  - approval_decisions      : Decisions prises
  - in_app_notifications    : Notifications in-app

Dependances : 010 (analytics snapshots)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '011_add_api_collab_workflow_tables'
down_revision = '010_add_analytics_tables'
branch_labels = None
depends_on = None


def upgrade():
    # ── External API Keys ──
    op.create_table(
        'external_api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_prefix', sa.String(12), nullable=False),
        sa.Column('key_hash', sa.String(64), nullable=False),
        sa.Column('key_name', sa.String(100), nullable=False),
        sa.Column('permissions', postgresql.JSON(astext_type=sa.Text()), default=list, nullable=False),
        sa.Column('rate_limit_per_minute', sa.Integer(), server_default='100', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_requests', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_errors', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_extapikey_tenant_active', 'external_api_keys', ['tenant_id', 'is_active'])
    op.create_index('idx_extapikey_hash', 'external_api_keys', ['key_hash'])

    # ── Comments ──
    op.create_table(
        'comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ao_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('open', 'resolved', name='comment_status'), server_default='open', nullable=False),
        sa.Column('is_edited', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ao_id'], ['aos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_comments_ao', 'comments', ['ao_id', 'created_at'])
    op.create_index('idx_comments_author', 'comments', ['author_id', 'created_at'])
    op.create_index('idx_comments_parent', 'comments', ['parent_id'])

    # ── Comment Mentions ──
    op.create_table(
        'comment_mentions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('comment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mentioned_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mentioned_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_notified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mentioned_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mentioned_by_user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_mention_user', 'comment_mentions', ['mentioned_user_id', 'is_notified'])

    # ── Approval Workflows ──
    op.create_table(
        'approval_workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('trigger', sa.String(30), nullable=False),
        sa.Column('business_line_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_workflow_tenant_trigger', 'approval_workflows', ['tenant_id', 'trigger'])

    # ── Approval Steps ──
    op.create_table(
        'approval_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_type', sa.String(30), nullable=False),
        sa.Column('specific_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workflow_id'], ['approval_workflows.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_approvalstep_workflow', 'approval_steps', ['workflow_id', 'step_order'])

    # ── Approval Requests ──
    op.create_table(
        'approval_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ao_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('response_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('current_step_number', sa.Integer(), server_default='1', nullable=False),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workflow_id'], ['approval_workflows.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_approvalreq_tenant_status', 'approval_requests', ['tenant_id', 'status'])
    op.create_index('idx_approvalreq_requester', 'approval_requests', ['requester_id', 'status'])

    # ── Approval Decisions ──
    op.create_table(
        'approval_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('decision', sa.String(20), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['request_id'], ['approval_requests.id'], ondelete='CASCADE'),
    )

    # ── In-App Notifications ──
    op.create_table(
        'in_app_notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_type', sa.String(30), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('target_type', sa.String(30), nullable=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('link_url', sa.String(500), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_sent', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('event_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_notif_recipient_unread', 'in_app_notifications', ['recipient_id', 'is_read'])
    op.create_index('idx_notif_tenant_type', 'in_app_notifications', ['tenant_id', 'notification_type'])


def downgrade():
    op.drop_index('idx_notif_tenant_type', table_name='in_app_notifications')
    op.drop_index('idx_notif_recipient_unread', table_name='in_app_notifications')
    op.drop_table('in_app_notifications')
    op.drop_table('approval_decisions')
    op.drop_index('idx_approvalreq_requester', table_name='approval_requests')
    op.drop_index('idx_approvalreq_tenant_status', table_name='approval_requests')
    op.drop_table('approval_requests')
    op.drop_index('idx_approvalstep_workflow', table_name='approval_steps')
    op.drop_table('approval_steps')
    op.drop_index('idx_workflow_tenant_trigger', table_name='approval_workflows')
    op.drop_table('approval_workflows')
    op.drop_index('idx_mention_user', table_name='comment_mentions')
    op.drop_table('comment_mentions')
    op.drop_index('idx_comments_parent', table_name='comments')
    op.drop_index('idx_comments_author', table_name='comments')
    op.drop_index('idx_comments_ao', table_name='comments')
    op.drop_table('comments')
    op.drop_index('idx_extapikey_hash', table_name='external_api_keys')
    op.drop_index('idx_extapikey_tenant_active', table_name='external_api_keys')
    op.drop_table('external_api_keys')
    op.execute('DROP TYPE IF EXISTS comment_status')
