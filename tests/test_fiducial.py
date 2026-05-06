# =============================================================================
# T5 — Tests du module fiducial (comptabilite)
# =============================================================================

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestFiducialInit:
    """Tests d'initialisation du plan de compte."""

    @pytest.mark.asyncio
    async def test_init_chart(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un admin authentifie
        WHEN POST /api/v1/fiducial/init
        THEN le plan de compte est initialise.
        """
        response = await client.post(
            "/api/v1/fiducial/init",
            headers=admin_headers,
        )
        assert response.status_code in (200, 201), f"Erreur : {response.text}"
        data = response.json()
        assert "created" in data
        assert data["created"] >= 1


class TestFiducialFECExport:
    """Tests de l'export FEC."""

    @pytest.mark.asyncio
    async def test_fec_export_exists(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un utilisateur authentifie
        WHEN GET /api/v1/fiducial/fec/{year}
        THEN un fichier est retourne ou une 404 si vide.
        """
        response = await client.get(
            "/api/v1/fiducial/fec/2024",
            headers=admin_headers,
        )
        assert response.status_code in (200, 404)
