# =============================================================================
# T2 — Tests de migration Alembic
# Verifie que 'alembic upgrade head' fonctionne sur une base PostgreSQL vierge
# =============================================================================

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class TestMigrations:
    """Tests de migration Alembic — base vierge a head."""

    @pytest.mark.migrations
    @pytest.mark.asyncio
    async def test_upgrade_head_creates_all_tables(self, db_engine: AsyncEngine) -> None:
        """GIVEN une base PostgreSQL vierge
        WHEN alembic upgrade head est execute (par conftest.py)
        THEN toutes les tables du modele sont presentes.
        """
        async with db_engine.begin() as conn:
            result = await conn.execute(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = 'public' ORDER BY tablename"
                )
            )
            tables = {row[0] for row in result.fetchall()}

        # --- Tables core ---
        assert "tenants" in tables, "Table 'tenants' manquante"
        assert "users" in tables, "Table 'users' manquante"
        assert "user_invitations" in tables, "Table 'user_invitations' manquante"
        assert "feature_flags" in tables, "Table 'feature_flags' manquante"

        # --- Tables memory ---
        assert "memory_global" in tables, "Table 'memory_global' manquante"
        assert "memory_tenant" in tables, "Table 'memory_tenant' manquante"
        assert "memory_session" in tables, "Table 'memory_session' manquante"
        assert "memory_entries" in tables, "Table 'memory_entries' manquante"
        assert "memory_consolidations" in tables, "Table 'memory_consolidations' manquante"

        # --- Tables documents ---
        assert "documents" in tables, "Table 'documents' manquante"
        assert "document_chunks" in tables, "Table 'document_chunks' manquante"

        # --- Tables AO ---
        assert "ao" in tables, "Table 'ao' manquante"
        assert "ao_documents" in tables, "Table 'ao_documents' manquante"
        assert "conversations" in tables, "Table 'conversations' manquante"
        assert "messages" in tables, "Table 'messages' manquante"

        # --- Tables logs ---
        assert "llm_call_logs" in tables, "Table 'llm_call_logs' manquante"
        assert "event_logs" in tables, "Table 'event_logs' manquante"
        assert "state_snapshots" in tables, "Table 'state_snapshots' manquante"

        # --- Tables audit ---
        assert "validation_audit" in tables, "Table 'validation_audit' manquante"
        assert "human_decisions" in tables, "Table 'human_decisions' manquante"
        assert "hil_requests" in tables, "Table 'hil_requests' manquante"

    @pytest.mark.migrations
    @pytest.mark.asyncio
    async def test_pgvector_extension_installed(self, db_engine: AsyncEngine) -> None:
        """GIVEN la base est migree
        WHEN on verifie les extensions
        THEN l'extension 'vector' est installee.
        """
        async with db_engine.begin() as conn:
            result = await conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            row = result.fetchone()
        assert row is not None, "Extension pgvector non installee"
        assert row[0] == "vector"

    @pytest.mark.migrations
    @pytest.mark.asyncio
    async def test_alembic_version_recorded(self, db_engine: AsyncEngine) -> None:
        """GIVEN la base est migree
        WHEN on verifie la table alembic_version
        THEN elle contient la revision head.
        """
        async with db_engine.begin() as conn:
            result = await conn.execute(
                text("SELECT version_num FROM alembic_version")
            )
            rows = result.fetchall()
        assert len(rows) >= 1, "Table alembic_version vide"
        versions = {r[0] for r in rows}
        assert "9497e2cc63f8" in versions, f"Revision 001 manquante : {versions}"
