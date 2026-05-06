# =============================================================================
# T6 — Tests du moteur de workflow
# =============================================================================

import pytest
from httpx import AsyncClient


class TestWorkflowList:
    """Tests de la liste des workflows."""

    @pytest.mark.asyncio
    async def test_list_workflows(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un admin authentifie
        WHEN GET /api/v1/workflows
        THEN la liste est retournee.
        """
        response = await client.get(
            "/api/v1/workflows",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "workflows" in data
        assert isinstance(data["workflows"], list)


class TestWorkflowDecisions:
    """Tests des decisions de workflow."""

    @pytest.mark.asyncio
    async def test_decision_requires_auth(
        self,
        client: AsyncClient,
    ) -> None:
        """GIVEN aucune authentification
        WHEN POST /api/v1/workflows/requests/{id}/decide
        THEN statut 401.
        """
        response = await client.post(
            "/api/v1/workflows/requests/00000000-0000-0000-0000-000000000001/decide",
            json={"decision": "approve"},
        )
        assert response.status_code == 401
