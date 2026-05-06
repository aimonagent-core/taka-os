# =============================================================================
# T4 — Tests du module de scoring
# =============================================================================

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestScoringRun:
    """Tests de l'execution du scoring."""

    @pytest.mark.asyncio
    async def test_scoring_run_success(
        self,
        client: AsyncClient,
        admin_headers: dict,
        sample_ao: Any,
    ) -> None:
        """GIVEN un AO existant et un utilisateur authentifie
        WHEN POST /api/v1/scoring/run/{ao_id}
        THEN un scoring est cree avec statut 200 et score_global.
        """
        response = await client.post(
            f"/api/v1/scoring/run/{sample_ao.id}",
            headers=admin_headers,
            params={"profile": "prudent"},
        )
        assert response.status_code in (200, 201), f"Erreur : {response.text}"
        data = response.json()
        assert "id" in data
        assert "score_global" in data
        assert "verdict" in data


class TestScoringFeedback:
    """Tests du feedback utilisateur sur le scoring."""

    @pytest.mark.asyncio
    async def test_submit_feedback(
        self,
        client: AsyncClient,
        admin_headers: dict,
        sample_ao_scored: dict,
    ) -> None:
        """GIVEN un scoring existant
        WHEN POST /api/v1/scoring/{scoring_id}/feedback
        THEN le feedback est enregistre.
        """
        scoring_id = sample_ao_scored["scoring"].id

        response = await client.post(
            f"/api/v1/scoring/{scoring_id}/feedback",
            headers=admin_headers,
            json={
                "feedback_type": "general",
                "rating": 4,
                "comment": "Le score me semble juste",
            },
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert "id" in data
