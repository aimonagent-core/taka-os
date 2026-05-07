"""Migration 016 — Ajoute type_marche aux AO et cree la table procedure_type_mappings.

Permet de classifier les AO par type de marche (Travaux, Services, Fournitures,
Concession, Mixte) via un systeme de regles base sur CPV + mots-cles.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision = "016_add_procedure_type_mapping"
down_revision = "015_add_tenant_onboarding_and_cpv_preferences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Ajout du champ type_marche sur la table aos
    op.add_column(
        "aos",
        sa.Column("type_marche", sa.String(50), nullable=True)
    )
    op.create_index("idx_aos_type_marche", "aos", ["type_marche"])

    # 2. Creation de la table de mapping
    op.create_table(
        "procedure_type_mappings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("keywords", JSON, server_default="[]", nullable=False),
        sa.Column("cpv_prefixes", JSON, server_default="[]", nullable=False),
        sa.Column("type_marche", sa.String(50), nullable=False),
        sa.Column("priority", sa.Integer, server_default=sa.text("100"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 3. Seed des regles de mapping initiales
    op.execute("""
        INSERT INTO procedure_type_mappings (keywords, cpv_prefixes, type_marche, priority)
        VALUES
            ('[]', '["45"]', 'Travaux', 10),
            ('[]', '["71"]', 'Travaux', 10),
            ('[]', '["50", "51"]', 'Services', 10),
            ('[]', '["30", "31", "32", "33", "34", "35", "36", "37", "38", "39"]', 'Fournitures', 10),
            ('["concession", "delegation de service public", "dsp", "affermage"]', '[]', 'Concession', 20),
            ('["travaux", "construction", "batiment", "maconnerie", "beton", "gros oeuvre"]', '[]', 'Travaux', 20),
            ('["prestation de service", "etude", "conseil", "expertise", "audit", "formation"]', '[]', 'Services', 20),
            ('["fourniture", "materiel", "equipement", "logiciel", "produit", "achat"]', '[]', 'Fournitures', 20),
            ('["mixte", "travaux et fournitures", "fournitures et services"]', '[]', 'Mixte', 30)
    """)


def downgrade() -> None:
    op.drop_index("idx_aos_type_marche", table_name="aos")
    op.drop_column("aos", "type_marche")
    op.drop_table("procedure_type_mappings")
