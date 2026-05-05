"""Migration 002 — Creation des tables AO, Sources, ScoringRuns, AOFiles, AOChunks."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "002_add_ao_sources_scoring"
down_revision = "9497e2cc63f8"
branch_labels = None
depends_on = None


def upgrade():
    # Table sources
    op.create_table(
        "sources",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("country", sa.String(2), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("scan_frequency_minutes", sa.Integer(), default=30, nullable=False),
        sa.Column("last_scan_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
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
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        "idx_sources_active_country", "sources", ["is_active", "country"]
    )

    # Table aos
    op.create_table(
        "aos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id"),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("external_url", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), default="detected", nullable=False),
        sa.Column("cpv_codes", postgresql.ARRAY(sa.String(20)), nullable=True),
        sa.Column("cpv_descriptions", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("country", sa.String(2), default="FR", nullable=False),
        sa.Column("department_code", sa.String(3), nullable=True),
        sa.Column("department_name", sa.String(100), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("estimated_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("currency", sa.String(3), default="EUR", nullable=False),
        sa.Column("funding_type", sa.String(50), nullable=True),
        sa.Column("publication_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contract_duration_months", sa.Integer(), nullable=True),
        sa.Column("notice_type", sa.String(50), nullable=True),
        sa.Column("buyer_name", sa.Text(), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(50), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column("keywords", postgresql.ARRAY(sa.String(100)), nullable=True),
        sa.Column("scoring_result", sa.JSON(), nullable=True),
        sa.Column(
            "business_line_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_lines.id"),
            nullable=True,
        ),
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
        sa.UniqueConstraint("source_id", "external_id"),
    )
    op.create_index("idx_aos_status_deadline", "aos", ["status", "deadline_date"])
    op.create_index("idx_aos_source_external", "aos", ["source_id", "external_id"])
    op.create_index("idx_aos_department", "aos", ["department_code"])
    op.create_index("idx_aos_bl", "aos", ["business_line_id", "status"])

    # Table ao_files
    op.create_table(
        "ao_files",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "ao_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("aos.id"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("parsing_confidence", sa.Numeric(3, 2), default=0.0, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Table ao_chunks
    op.create_table(
        "ao_chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "ao_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("aos.id"),
            nullable=False,
        ),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ao_chunks_ao", "ao_chunks", ["ao_id", "chunk_index"])

    # Table scoring_runs
    op.create_table(
        "scoring_runs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "ao_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("aos.id"),
            nullable=False,
        ),
        sa.Column("profile", sa.String(20), nullable=False),
        sa.Column("score_global", sa.Numeric(4, 2), nullable=False),
        sa.Column("score_coherence", sa.Numeric(4, 2), nullable=False),
        sa.Column("score_financiere", sa.Numeric(4, 2), nullable=False),
        sa.Column("score_geographique", sa.Numeric(4, 2), nullable=False),
        sa.Column("score_temporelle", sa.Numeric(4, 2), nullable=False),
        sa.Column("score_concurrentielle", sa.Numeric(4, 2), nullable=False),
        sa.Column("verdict", sa.String(10), nullable=False),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column("triggered_by", sa.String(50), default="auto", nullable=False),
        sa.Column("execution_time_ms", sa.Integer(), default=0, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_scoring_runs_ao_profile", "scoring_runs", ["ao_id", "profile"]
    )
    op.create_index(
        "idx_scoring_runs_verdict", "scoring_runs", ["verdict", "confidence"]
    )

    # Table scoring_feedbacks
    op.create_table(
        "scoring_feedbacks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "scoring_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scoring_runs.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("feedback_type", sa.String(20), nullable=False),
        sa.Column("user_comment", sa.Text(), nullable=True),
        sa.Column("user_override_verdict", sa.String(10), nullable=True),
        sa.Column("applied", sa.Boolean(), default=False, nullable=False),
        sa.Column("calibration_delta", sa.Numeric(4, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_scoring_feedbacks_user", "scoring_feedbacks", ["user_id", "applied"]
    )

    # Seed sources
    op.execute(
        """
        INSERT INTO sources (id, name, label, base_url, country, is_active, scan_frequency_minutes, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'boamp', 'BOAMP (France)', 'https://www.data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/boamp/records', 'FR', true, 15, NOW(), NOW()),
            (gen_random_uuid(), 'joue', 'JOUE / TED (UE)', 'https://ted.europa.eu/api/v2.0/notices/search', 'FR', true, 30, NOW(), NOW()),
            (gen_random_uuid(), 'enotification', 'e-Notification (Belgique)', 'https://een.publicprocurement.be/rest/appcasting/cft-announces', 'BE', true, 30, NOW(), NOW()),
            (gen_random_uuid(), 'marche_public', 'Marches Publics (Maroc)', 'https://www.marchespublics.gov.ma/ma/ac_appeloffre.asp', 'MA', true, 60, NOW(), NOW())
    """
    )


def downgrade():
    op.drop_table("scoring_feedbacks")
    op.drop_table("scoring_runs")
    op.drop_table("ao_chunks")
    op.drop_table("ao_files")
    op.drop_table("aos")
    op.drop_table("sources")
