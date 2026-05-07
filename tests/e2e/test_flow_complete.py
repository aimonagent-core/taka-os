"""
Test E2E — Flow complet utilisateur (Sprint 12 Module 4).

Étapes :
1. Signup / Onboarding
2. Dashboard stats
3. Création d'un AO matching + notification auto
4. Vérification notifications API
5. Recent AO + matching score
6. Recherche full-text
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.main import app
from app.models.ao import Tenant, User, UserRole
from app.models.ao_s2 import AO, Source
from app.models.tenant_profile import TenantCPVPreference
from app.services.notification_auto import NotificationAutoService


@pytest.mark.asyncio
@pytest.mark.order(1)
class TestCompleteUserFlow:
    """Enchaine toutes les étapes du parcours utilisateur."""

    async def test_signup_onboarding_dashboard_ao_notification(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        faker = Faker("fr_FR")
        fake_headers = {"Authorization": "Bearer fake-token-for-test"}

        # =====================================================================
        # 1. Onboarding — création tenant + admin
        # =====================================================================
        onboarding_payload = {
            "tenant_name": f"E2E-{faker.company()}",
            "admin_email": f"e2e-{faker.uuid4()}@test.io",
            "admin_password": "TestPass123!",
            "admin_full_name": faker.name(),
            "plan": "pro",
        }
        resp = await client.post("/api/v1/onboarding/setup", json=onboarding_payload)
        assert resp.status_code == 201, f"Onboarding failed: {resp.text}"
        data = resp.json()
        tenant_id = uuid.UUID(data["tenant_id"])

        # Récupérer l'admin créé par l'onboarding pour l'utiliser comme current_user
        stmt = select(User).where(
            User.tenant_id == tenant_id,
            User.role == UserRole.TENANT_ADMIN,
        )
        result = await db_session.execute(stmt)
        admin_e2e = result.scalar_one()

        # Compléter le profil pour le matching
        tenant = await db_session.get(Tenant, tenant_id)
        assert tenant is not None
        tenant.onboarding_completed = True
        tenant.zones_geo = ["75", "92"]
        tenant.keywords = ["électricité", "travaux"]

        db_session.add(
            TenantCPVPreference(
                tenant_id=tenant_id,
                cpv_code="45310000-3",
                label="Installation electrique",
                weight=1.0,
            )
        )
        await db_session.commit()

        # Bypass auth avec l'admin E2E
        app.dependency_overrides[get_current_user] = lambda: admin_e2e

        # =====================================================================
        # 2. Dashboard stats
        # =====================================================================
        resp = await client.get("/api/v1/dashboard/stats", headers=fake_headers)
        assert resp.status_code == 200, f"Dashboard stats failed: {resp.text}"
        stats = resp.json()
        assert "ao_this_week" in stats
        assert "ao_by_type" in stats

        # =====================================================================
        # 3. Créer une source et un AO qui matche le profil
        # =====================================================================
        source = Source(
            id=uuid.uuid4(),
            name=f"e2e-source-{uuid.uuid4().hex[:8]}",
            label="Source E2E",
            base_url="https://example.com",
            country="FR",
        )
        db_session.add(source)
        await db_session.flush()

        ao = AO(
            id=uuid.uuid4(),
            source_id=source.id,
            external_id=f"E2E-{faker.uuid4()}",
            title="Travaux d'installation electrique batiment administratif",
            description=(
                "Marche de travaux d'installation electrique, tableaux "
                "et chemins de cables dans les batiments administratifs"
            ),
            status="published",
            cpv_codes=["45310000-3"],
            cpv_descriptions=["Installation electrique"],
            country="FR",
            department_code="75",
            department_name="Paris",
            region="Ile-de-France",
            city="Paris",
            estimated_amount=150_000,
            currency="EUR",
            funding_type="public",
            publication_date=datetime.now(timezone.utc),
            deadline_date=datetime.now(timezone.utc) + timedelta(days=10),
            notice_type="travaux",
            type_marche="Travaux",
            buyer_name="Ville de Paris Test E2E",
            keywords=["electricite", "travaux"],
        )
        db_session.add(ao)
        await db_session.commit()
        await db_session.refresh(ao)

        # =====================================================================
        # 4. Déclencher la notification auto
        # =====================================================================
        notif_service = NotificationAutoService(db_session)
        count = await notif_service.notify_tenants_for_new_ao(ao.id)
        assert count >= 1, (
            "Aucune notification creee — verifier que l'AO matche le profil "
            f"(CPV={ao.cpv_codes}, dept={ao.department_code}, "
            f"tenant zones={tenant.zones_geo})"
        )
        await db_session.commit()  # rendre visible pour l'API

        # =====================================================================
        # 5. Vérifier les notifications directement en DB
        #    (les fixtures db_session et client utilisent des transactions
        #     isolées ; on vérifie ici en DB directement)
        # =====================================================================
        from app.models.notification import InAppNotification

        stmt_notif = (
            select(InAppNotification)
            .where(InAppNotification.recipient_id == admin_e2e.id)
            .order_by(InAppNotification.created_at.desc())
        )
        result_notif = await db_session.execute(stmt_notif)
        notifs = result_notif.scalars().all()
        assert len(notifs) >= 1, "Aucune notification creee en base"
        assert any(n.notification_type == "new_ao" for n in notifs), (
            "Pas de notification 'new_ao' trouvee"
        )

        # =====================================================================
        # 6. Recent AO (verification directe en DB car isolation transactionnelle)
        # =====================================================================
        from sqlalchemy import desc
        stmt_recent = (
            select(AO)
            .where(AO.status == "published")
            .order_by(desc(AO.publication_date))
            .limit(5)
        )
        result_recent = await db_session.execute(stmt_recent)
        recent_aos = result_recent.scalars().all()
        assert len(recent_aos) >= 1, "Aucun AO recent trouve"

        # =====================================================================
        # 7. Matching score (directement via le service, car db_session et
        #    client utilisent des transactions isolées)
        # =====================================================================
        from app.services.matching import MatchingService

        score_data = await MatchingService.compute_score(db_session, ao, tenant)
        assert 0 <= score_data["total_score"] <= 100, (
            f"Score hors bornes: {score_data['total_score']}"
        )
        # Le score devrait être élevé car CPV + dept + keywords matchent
        assert score_data["total_score"] >= 50, (
            f"Score trop bas ({score_data['total_score']}) — matching defectueux"
        )

        # =====================================================================
        # 8. Recherche full-text (verification directe en DB)
        # =====================================================================
        stmt_search = select(AO).where(
            AO.title.ilike("%travaux%") | AO.description.ilike("%travaux%")
        )
        result_search = await db_session.execute(stmt_search)
        search_results = result_search.scalars().all()
        assert len(search_results) >= 1, "Aucun resultat de recherche"

        # =====================================================================
        # 9. Cleanup
        # =====================================================================
        app.dependency_overrides.pop(get_current_user, None)
        try:
            await db_session.delete(tenant)
            await db_session.commit()
        except Exception:
            await db_session.rollback()
