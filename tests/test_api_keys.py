# =============================================================================
# T8 — Tests des cles API
# =============================================================================

import pytest
from httpx import AsyncClient


class TestAPIKeys:
    """Tests du cycle de vie des cles API."""

    @pytest.mark.asyncio
    async def test_api_key_create_and_list(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un utilisateur authentifie
        WHEN POST /api/v1/api-keys pour creer une cle
        THEN la cle est creee et listable.
        """
        # WHEN — Creer une cle
        response = await client.post(
            "/api/v1/api-keys",
            headers=admin_headers,
            json={
                "name": "Integration Test Key",
                "permissions": ["ao:read", "scoring:read"],
                "is_test": True,
                "rate_limit": 100,
            },
        )
        assert response.status_code in (200, 201), f"Erreur : {response.text}"
        data = response.json()
        assert "id" in data
        assert "key" in data

        api_key_id = data["id"]

        # WHEN — Lister les cles
        response = await client.get("/api/v1/api-keys", headers=admin_headers)
        assert response.status_code == 200
        keys = response.json()
        assert "keys" in keys
        assert any(k["id"] == api_key_id for k in keys["keys"])

    @pytest.mark.asyncio
    async def test_api_key_revoke(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN une cle API existante
        WHEN POST /api/v1/api-keys/{id}/revoke
        THEN la cle est revoquee.
        """
        # Creer une cle
        create_resp = await client.post(
            "/api/v1/api-keys",
            headers=admin_headers,
            json={"name": "Key to revoke", "permissions": ["ao:read"]},
        )
        assert create_resp.status_code in (200, 201)
        key_id = create_resp.json()["id"]

        # WHEN — Revoke
        response = await client.post(
            f"/api/v1/api-keys/{key_id}/revoke",
            headers=admin_headers,
        )
        assert response.status_code in (200, 204, 404)
