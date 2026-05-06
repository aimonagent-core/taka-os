"""Migration 015 — Ajoute les champs onboarding au tenant et la table tenant_cpv_preferences.

Ajoute les champs necessaires au formulaire d'onboarding entreprise :
- siret, domaine_activite, effectif, ca_annuel, zones_geo, types_marche_acceptes
- onboarding_completed / onboarding_completed_at

Cree la table de jointure tenant_cpv_preferences pour stocker les CPV cibles.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON, NUMERIC

revision = "015_add_tenant_onboarding_and_cpv_preferences"
down_revision = "014_fix_alembic_version_varchar_128"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Nouveaux champs sur la table tenants
    # -------------------------------------------------------------------------
    op.add_column(
        "tenants",
        sa.Column("siret", sa.String(14), nullable=True)
    )
    op.add_column(
        "tenants",
        sa.Column("domaine_activite", JSON, server_default="[]", nullable=False)
    )
    op.add_column(
        "tenants",
        sa.Column("effectif", sa.String(20), nullable=True)
    )
    op.add_column(
        "tenants",
        sa.Column("ca_annuel", NUMERIC(15, 2), nullable=True)
    )
    op.add_column(
        "tenants",
        sa.Column("zones_geo", JSON, server_default="[]", nullable=False)
    )
    op.add_column(
        "tenants",
        sa.Column("types_marche_acceptes", JSON, server_default="[]", nullable=False)
    )
    op.add_column(
        "tenants",
        sa.Column("onboarding_completed", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )
    op.add_column(
        "tenants",
        sa.Column("onboarding_completed_at", sa.DateTime(timezone=True), nullable=True)
    )

    # -------------------------------------------------------------------------
    # 2. Table tenant_cpv_preferences
    # -------------------------------------------------------------------------
    op.create_table(
        "tenant_cpv_preferences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("cpv_code", sa.String(20), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("weight", NUMERIC(3, 2), server_default=sa.text("1.0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "idx_tenant_cpv_pref_tenant_code",
        "tenant_cpv_preferences",
        ["tenant_id", "cpv_code"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # 3. Index sur les nouveaux champs tenants
    # -------------------------------------------------------------------------
    op.create_index("idx_tenants_onboarding_completed", "tenants", ["onboarding_completed"])


def downgrade() -> None:
    op.drop_index("idx_tenants_onboarding_completed", table_name="tenants")
    op.drop_table("tenant_cpv_preferences")

    op.drop_column("tenants", "onboarding_completed_at")
    op.drop_column("tenants", "onboarding_completed")
    op.drop_column("tenants", "types_marche_acceptes")
    op.drop_column("tenants", "zones_geo")
    op.drop_column("tenants", "ca_annuel")
    op.drop_column("tenants", "effectif")
    op.drop_column("tenants", "domaine_activite")
    op.drop_column("tenants", "siret")
