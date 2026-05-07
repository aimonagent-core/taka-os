"""
Test E2E — Flow déposant (Sprint 12 Module 4).

Étapes :
1. Créer un tenant + admin
2. Créer une SubmissionPlatform et une GeneratedResponse
3. Soumettre en mode mock via le SubmitterAgent
4. Vérifier les champs mock (warning, L121-1)
5. Créer un PlatformConnector email_direct
6. Tester la connexion
"""

import uuid
from datetime import datetime, timezone

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.deposant.submitter import SubmitterAgent
from app.models.ao import Tenant, User, UserRole
from app.models.ao_s2 import AO, Source
from app.models.platform_connector import PlatformConnector
from app.models.response import GeneratedResponse
from app.models.submission import SubmissionPlatform
from app.services.deposant.connectors.email_connector import EmailDirectConnector
from app.services.deposant.connectors.mock_connector import MockConnector


@pytest.mark.asyncio
@pytest.mark.order(2)
class TestDeposantFlow:
    """Valide le dépot mock et le test de connecteur reel."""

    async def test_mock_submission_flow(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
        test_admin: User,
    ) -> None:
        faker = Faker("fr_FR")
        tenant = test_tenant
        admin = test_admin

        # =====================================================================
        # 1. Créer une Source, une AO et une GeneratedResponse approuvée
        # =====================================================================
        source = Source(
            id=uuid.uuid4(),
            name=f"e2e-dep-source-{uuid.uuid4().hex[:8]}",
            label="Source E2E Deposant",
            base_url="https://example.com",
            country="FR",
        )
        db_session.add(source)
        await db_session.flush()

        ao = AO(
            id=uuid.uuid4(),
            source_id=source.id,
            external_id=f"E2E-DEP-{faker.uuid4()}",
            title="AO Test — Travaux d'installation electrique",
            description="Description test pour le déposant E2E",
            status="published",
            buyer_name="Acheteur Test E2E",
        )
        db_session.add(ao)
        await db_session.flush()

        response = GeneratedResponse(
            id=uuid.uuid4(),
            ao_id=ao.id,
            user_id=admin.id,
            category="letter",
            content="Ceci est une réponse générée pour le test E2E du déposant.",
            status="approved",
            hil_status="validated",
        )
        db_session.add(response)
        await db_session.flush()

        # =====================================================================
        # 2. Créer une SubmissionPlatform
        # =====================================================================
        platform = SubmissionPlatform(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            name="BOAMP Test",
            platform_type="boamp",
            base_url="https://www.boamp.fr",
            is_mock=True,
            is_active=True,
        )
        db_session.add(platform)
        await db_session.commit()

        # =====================================================================
        # 3. Soumettre via SubmitterAgent avec MockConnector injecté
        # =====================================================================
        submitter = SubmitterAgent(connector=MockConnector(config={}))
        submission = await submitter.submit(
            generated_response_id=str(response.id),
            platform_id=str(platform.id),
            user_id=str(admin.id),
            db=db_session,
            tenant_id=str(tenant.id),
        )

        assert submission.status in ("submitted", "pending")
        platform_response = submission.platform_response or {}
        assert platform_response.get("is_mock") is True
        assert "SIMULATION" in (platform_response.get("warning") or "")
        assert "L121-1" in (platform_response.get("_mock_notice") or "")
        assert "Configurer un connecteur" in (platform_response.get("requires_action") or "")

    async def test_connector_real_test_connection(
        self,
        db_session: AsyncSession,
        test_tenant: Tenant,
    ) -> None:
        faker = Faker("fr_FR")
        tenant = test_tenant

        # =====================================================================
        # 1. Créer un PlatformConnector email_direct (config SMTP test)
        # =====================================================================
        connector_db = PlatformConnector(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            platform_type="email_direct",
            config={
                "provider": "smtp",
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "smtp_user": "test@example.com",
                "smtp_password": "secret",
                "from_email": "test@example.com",
                "from_name": "Test E2E",
            },
            is_active=True,
            test_status="never_tested",
        )
        db_session.add(connector_db)
        await db_session.commit()

        # =====================================================================
        # 2. Tester la connexion directement via EmailDirectConnector
        # =====================================================================
        connector = EmailDirectConnector(connector_db.config)
        ok = await connector.test_connection()
        assert ok is False  # smtp.example.com n'existe pas

        # =====================================================================
        # 3. Vérifier que l'état peut être mis à jour manuellement
        # =====================================================================
        connector_db.test_status = "error" if not ok else "ok"
        connector_db.last_tested_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(connector_db)
        assert connector_db.test_status == "error"
        assert connector_db.last_tested_at is not None

        # =====================================================================
        # 4. Test ad-hoc avec GenericAPIConnector (config vide → test ko)
        # =====================================================================
        from app.services.deposant.connectors.api_connector import GenericAPIConnector
        api_connector = GenericAPIConnector({"base_url": "https://invalid.example.com"})
        ok_api = await api_connector.test_connection()
        assert ok_api is False
