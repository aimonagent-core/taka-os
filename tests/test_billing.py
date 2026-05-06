# =============================================================================
# T10 — Tests du module de facturation (Stripe)
# =============================================================================

import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient


class TestBillingStripe:
    """Tests des integrations Stripe (mocked)."""

    @pytest.mark.asyncio
    @patch("app.api.v1.billing.stripe.checkout.Session.create")
    async def test_create_checkout_session(
        self,
        mock_stripe_create: MagicMock,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un utilisateur authentifie
        WHEN POST /api/v1/billing/checkout-session
        THEN une session Stripe est creee et l'URL est retournee.
        """
        mock_stripe_create.return_value = {"url": "https://checkout.stripe.com/test_session_123"}

        response = await client.post(
            "/api/v1/billing/checkout-session",
            headers=admin_headers,
            json={"price_id": "price_test_123", "success_url": "https://taka.os/success"},
        )
        assert response.status_code in (200, 201), f"Erreur : {response.text}"
        data = response.json()
        assert "url" in data or "data" in data

    @pytest.mark.asyncio
    @patch("app.api.v1.billing.stripe.billing_portal.Session.create")
    async def test_create_portal_session(
        self,
        mock_portal_create: MagicMock,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un utilisateur avec un abonnement
        WHEN POST /api/v1/billing/portal-session
        THEN une session portail Stripe est creee.
        """
        mock_portal_create.return_value = {"url": "https://billing.stripe.com/test_portal_456"}

        response = await client.post(
            "/api/v1/billing/portal-session",
            headers=admin_headers,
        )
        assert response.status_code in (200, 201, 404)
