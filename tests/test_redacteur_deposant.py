"""Tests E2E pour les routes Redacteur et Deposant (Sprint 3)."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import Tenant, User
from app.models.ao_s2 import AO, Source
from app.models.scoring import ScoringRun


# --- Tests Redacteur ---

class TestRedacteur:

    @pytest.mark.asyncio
    async def test_generate_response_no_auth(self, client: AsyncClient):
        """Test génération sans auth → 401."""
        response = await client.post(
            "/api/v1/redacteur/generate/00000000-0000-0000-0000-000000000001?category=letter"
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_templates_no_auth(self, client: AsyncClient):
        """Test liste templates sans auth → 401."""
        response = await client.get("/api/v1/redacteur/templates")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_approve_response_no_auth(self, client: AsyncClient):
        """Test approbation sans auth → 401."""
        response = await client.post(
            "/api/v1/redacteur/responses/00000000-0000-0000-0000-000000000001/approve"
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_reject_response_no_auth(self, client: AsyncClient):
        """Test rejet sans auth → 401."""
        response = await client.post(
            "/api/v1/redacteur/responses/00000000-0000-0000-0000-000000000001/reject"
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_seed_defaults_admin(self, client: AsyncClient, admin_headers: dict):
        """Test création templates par défaut en tant qu'admin."""
        response = await client.post(
            "/api/v1/redacteur/templates/seed-defaults",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "created" in data
        assert data["created"] == 4

    @pytest.mark.asyncio
    async def test_list_templates_auth(self, client: AsyncClient, auth_headers: dict):
        """Test liste templates avec auth."""
        response = await client.get("/api/v1/redacteur/templates", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_generate_fails_no_go(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict, test_tenant: Tenant
    ):
        """Test génération échoue si AO n'est pas GO/MAYBE."""
        source = Source(
            name="test-source",
            label="Test Source",
            base_url="https://test.example.com",
            country="FR",
        )
        db_session.add(source)
        await db_session.commit()
        await db_session.refresh(source)

        ao = AO(
            source_id=source.id,
            external_id="TEST-NOGO-001",
            title="Test AO NO-GO",
            country="FR",
            scoring_result={"verdict": "NO_GO", "score_global": 3.0},
        )
        db_session.add(ao)
        await db_session.commit()
        await db_session.refresh(ao)

        response = await client.post(
            f"/api/v1/redacteur/generate/{ao.id}?category=letter",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "non qualifié" in response.json()["detail"]


# --- Tests Deposant ---

class TestDeposant:

    @pytest.mark.asyncio
    async def test_list_platforms_no_auth(self, client: AsyncClient):
        """Test liste plateformes sans auth → 401."""
        response = await client.get("/api/v1/deposant/platforms")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_submit_no_auth(self, client: AsyncClient):
        """Test soumission sans auth → 401."""
        response = await client.post(
            "/api/v1/deposant/submit/00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000002"
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_submissions_no_auth(self, client: AsyncClient):
        """Test liste soumissions sans auth → 401."""
        response = await client.get("/api/v1/deposant/submissions")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_track_no_auth(self, client: AsyncClient):
        """Test tracker sans auth → 401."""
        response = await client.post("/api/v1/deposant/track")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_platforms_auth(self, client: AsyncClient, auth_headers: dict):
        """Test liste plateformes avec auth — retourne les mocks seedés."""
        response = await client.get("/api/v1/deposant/platforms", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(p["is_mock"] for p in data)


# --- Tests Integration (mock platforms) ---

class TestMockPlatforms:

    @pytest.mark.asyncio
    async def test_mock_boamp_submit(self):
        """Test le simulateur BOAMP directement."""
        from app.agents.deposant.mock_platforms import MockBOAMPPlatform

        platform = MockBOAMPPlatform()
        result = await platform.submit({"test": "dossier"})

        assert result.success is True or result.success is False
        if result.success:
            assert result.reference.startswith("BOAMP-")
        else:
            assert result.error is not None

    @pytest.mark.asyncio
    async def test_mock_joue_check_status(self):
        """Test le check status JOUE."""
        from app.agents.deposant.mock_platforms import MockJouePlatform

        platform = MockJouePlatform()
        status = await platform.check_status("TED-123456")

        assert "status" in status
        assert status["status"] in ("received", "processing", "published")

    @pytest.mark.asyncio
    async def test_mock_marche_public_submit(self):
        """Test le simulateur Maroc."""
        from app.agents.deposant.mock_platforms import MockMarchePublicPlatform

        platform = MockMarchePublicPlatform()
        result = await platform.submit({"test": "dossier"})

        assert result.success is True or result.success is False
        if result.success:
            assert result.reference.startswith("MA-")


# --- Tests Pipeline E2E ---

class TestPipelineE2E:

    @pytest.mark.asyncio
    async def test_event_bus_publish(self):
        """Test que le EventBus publie et les handlers reçoivent."""
        from app.core.events import event_bus, EVENT_AO_SCORED

        received = []

        async def handler(payload):
            received.append(payload)

        event_bus.subscribe(EVENT_AO_SCORED, handler)
        await event_bus.publish(EVENT_AO_SCORED, {"ao_id": "test-123"})

        assert len(received) == 1
        assert received[0]["ao_id"] == "test-123"
