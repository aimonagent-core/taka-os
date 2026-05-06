# =============================================================================
# T12 — Tests du health check
# =============================================================================

import pytest
from httpx import AsyncClient


class TestHealth:
    """Tests des endpoints de health check."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient) -> None:
        """GIVEN l'application demarree
        WHEN GET /health
        THEN statut 200.
        """
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ("ok", "success")

    @pytest.mark.asyncio
    async def test_health_db_endpoint(self, client: AsyncClient) -> None:
        """GIVEN l'application demarree
        WHEN GET /health/db
        THEN statut 200 confirmant la connexion DB.
        """
        response = await client.get("/health/db")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        assert data.get("migrations") is True
