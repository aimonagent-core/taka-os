"""Migration 003 — Business Lines, BL Members, BL CPV Keywords."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003_add_business_lines"
down_revision = "002_add_ao_sources_scoring"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "business_lines",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.String(7), default="#3B82F6", nullable=False),
        sa.Column("icon", sa.String(50), default="Briefcase", nullable=False),
        sa.Column("default_profile", sa.String(20), default="prudent", nullable=False),
        sa.Column(
            "cpv_keywords", postgresql.ARRAY(sa.String(50)), default=list, nullable=False
        ),
        sa.Column(
            "free_text_keywords",
            postgresql.ARRAY(sa.String(100)),
            default=list,
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("max_monthly_aos", sa.Integer(), default=100, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_bl_tenant_active", "business_lines", ["tenant_id", "is_active"])

    op.create_table(
        "bl_members",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "business_line_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_lines.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), default="member", nullable=False),
        sa.Column("is_primary", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_line_id", "user_id"),
    )
    op.create_index("idx_bl_members_user", "bl_members", ["user_id", "is_primary"])

    op.create_table(
        "bl_cpv_keywords",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "business_line_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_lines.id"),
            nullable=False,
        ),
        sa.Column("cpv_code", sa.String(20), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("weight", sa.Numeric(3, 2), default=1.0, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_bl_cpv_bl_code", "bl_cpv_keywords", ["business_line_id", "cpv_code"])


def downgrade():
    op.drop_table("bl_cpv_keywords")
    op.drop_table("bl_members")
    op.drop_table("business_lines")
