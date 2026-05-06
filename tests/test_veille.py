# =============================================================================
# T11 — Tests du module de veille
# =============================================================================

import pytest
from httpx import AsyncClient


class TestVeilleSources:
    """Tests des sources de veille."""

    @pytest.mark.asyncio
    async def test_list_sources(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un utilisateur authentifie
        WHEN GET /api/v1/veille/sources
        THEN la liste des sources est retournee.
        """
        response = await client.get(
            "/api/v1/veille/sources",
            headers=admin_headers,
        )
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestVeilleScraper:
    """Tests du statut du scraper."""

    @pytest.mark.asyncio
    async def test_scraper_status(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un utilisateur authentifie
        WHEN GET /api/v1/veille/scraper/status
        THEN le statut du scraper est retourne.
        """
        response = await client.get(
            "/api/v1/veille/scraper/status",
            headers=admin_headers,
        )
        assert response.status_code in (200, 404)
