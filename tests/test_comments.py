# =============================================================================
# T7 — Tests des commentaires
# =============================================================================

import pytest
from httpx import AsyncClient


class TestCommentsCRUD:
    """Tests CRUD des commentaires."""

    @pytest.mark.asyncio
    async def test_comment_create_and_list(
        self,
        client: AsyncClient,
        admin_headers: dict,
        sample_ao: Any,
    ) -> None:
        """GIVEN un AO existant
        WHEN POST /api/v1/comments/ao/{ao_id} puis GET
        THEN le commentaire est cree et listable.
        """
        # WHEN — Creer un commentaire
        response = await client.post(
            f"/api/v1/comments/ao/{sample_ao.id}",
            headers=admin_headers,
            json={"content": "Ce AO est tres interessant pour notre expertise."},
        )
        assert response.status_code in (200, 201), f"Erreur : {response.text}"
        create_data = response.json()
        assert "id" in create_data or "comment" in create_data

        # WHEN — Lister les commentaires de l'AO
        response = await client.get(
            f"/api/v1/comments/ao/{sample_ao.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        list_data = response.json()
        assert "comments" in list_data
        assert isinstance(list_data["comments"], list)

    @pytest.mark.asyncio
    async def test_comment_resolve(
        self,
        client: AsyncClient,
        admin_headers: dict,
        sample_ao: Any,
    ) -> None:
        """GIVEN un commentaire existant
        WHEN POST /api/v1/comments/{id}/resolve
        THEN le commentaire est marque comme resolu.
        """
        # Creer d'abord un commentaire
        create_resp = await client.post(
            f"/api/v1/comments/ao/{sample_ao.id}",
            headers=admin_headers,
            json={"content": "Point a clarifier avec le client"},
        )
        assert create_resp.status_code in (200, 201)
        comment_id = create_resp.json().get("id") or create_resp.json()["comment"]["id"]

        # WHEN — Resoudre
        response = await client.post(
            f"/api/v1/comments/{comment_id}/resolve",
            headers=admin_headers,
        )
        assert response.status_code == 200
