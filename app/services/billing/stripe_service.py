"""Service de facturation via Stripe."""
import logging
from datetime import datetime, timezone
from typing import Optional

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.ao import Tenant
from app.models.billing import SubscriptionEvent, TenantSubscription
from app.models.feature_flag import SubscriptionTier

logger = logging.getLogger(__name__)

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key

STRIPE_PRICES = {
    "pro_monthly": settings.stripe_price_pro_monthly or "price_placeholder_pro",
    "pro_yearly": settings.stripe_price_pro_yearly or "price_placeholder_pro_yearly",
    "enterprise_monthly": settings.stripe_price_enterprise_monthly or "price_placeholder_enterprise",
}


class BillingService:
    """Gestion des souscriptions et paiements via Stripe."""

    @staticmethod
    async def create_checkout_session(
        db: AsyncSession,
        tenant_id: str,
        tier_name: str,
        yearly: bool = False,
        success_url: str = "https://localhost/billing/success",
        cancel_url: str = "https://localhost/billing/cancel",
    ) -> dict:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        row = await db.execute(stmt)
        tenant = row.scalar_one_or_none()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} introuvable")

        key = f"{tier_name}_{'yearly' if yearly else 'monthly'}"
        price_id = STRIPE_PRICES.get(key)
        if not price_id or price_id.startswith("price_placeholder"):
            raise ValueError(f"Price Stripe non configure pour {key}")

        subscription = await BillingService._get_or_create_subscription(db, tenant_id)

        session = stripe.checkout.Session.create(
            customer=subscription.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            subscription_data={
                "trial_period_days": 14 if tier_name == "pro" else 0,
            },
            metadata={
                "tenant_id": tenant_id,
                "tier_name": tier_name,
            },
        )

        logger.info(f"[Stripe] Checkout session creee : {session.id} pour tenant={tenant_id}")
        return {"session_id": session.id, "url": session.url}

    @staticmethod
    async def create_portal_session(
        db: AsyncSession,
        tenant_id: str,
        return_url: str = "https://localhost/subscription",
    ) -> str:
        subscription = await BillingService._get_subscription(db, tenant_id)
        if not subscription or not subscription.stripe_customer_id:
            raise ValueError("Pas de customer Stripe pour ce tenant")

        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=return_url,
        )
        return session.url

    @staticmethod
    async def handle_webhook(db: AsyncSession, payload: bytes, sig_header: str) -> bool:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.error(f"[Stripe Webhook] Signature invalide : {e}")
            return False

        event_type = event["type"]
        data = event["data"]["object"]

        logger.info(f"[Stripe Webhook] Evenement recu : {event_type}")

        if event_type == "checkout.session.completed":
            await BillingService._handle_checkout_completed(db, data)
        elif event_type == "invoice.payment_succeeded":
            await BillingService._handle_payment_succeeded(db, data)
        elif event_type == "invoice.payment_failed":
            await BillingService._handle_payment_failed(db, data)
        elif event_type == "customer.subscription.updated":
            await BillingService._handle_subscription_updated(db, data)
        elif event_type == "customer.subscription.deleted":
            await BillingService._handle_subscription_deleted(db, data)

        return True

    @staticmethod
    async def _handle_checkout_completed(db: AsyncSession, session_data: dict):
        tenant_id = session_data.get("metadata", {}).get("tenant_id")
        subscription_id = session_data.get("subscription")

        if not tenant_id:
            return

        sub = await BillingService._get_subscription(db, tenant_id)
        if sub:
            sub.stripe_subscription_id = subscription_id
            sub.status = "active"
            await db.commit()

            event = SubscriptionEvent(
                tenant_subscription_id=sub.id,
                tenant_id=tenant_id,
                event_type="subscription_created",
                stripe_event_id=session_data.get("id"),
                description="Souscription creee via Checkout",
            )
            db.add(event)
            await db.commit()

    @staticmethod
    async def _handle_payment_succeeded(db: AsyncSession, invoice: dict):
        subscription_id = invoice.get("subscription")
        stmt = select(TenantSubscription).where(
            TenantSubscription.stripe_subscription_id == subscription_id
        )
        row = await db.execute(stmt)
        sub = row.scalar_one_or_none()

        if sub:
            sub.status = "active"
            await db.commit()

            event = SubscriptionEvent(
                tenant_subscription_id=sub.id,
                tenant_id=str(sub.tenant_id),
                event_type="payment_succeeded",
                stripe_event_id=invoice.get("id"),
                amount=float(invoice.get("amount_due", 0)) / 100,
                currency=invoice.get("currency", "eur").upper(),
                description="Paiement reussi",
            )
            db.add(event)
            await db.commit()

    @staticmethod
    async def _handle_payment_failed(db: AsyncSession, invoice: dict):
        subscription_id = invoice.get("subscription")
        stmt = select(TenantSubscription).where(
            TenantSubscription.stripe_subscription_id == subscription_id
        )
        row = await db.execute(stmt)
        sub = row.scalar_one_or_none()

        if sub:
            sub.status = "past_due"
            await db.commit()

            event = SubscriptionEvent(
                tenant_subscription_id=sub.id,
                tenant_id=str(sub.tenant_id),
                event_type="payment_failed",
                stripe_event_id=invoice.get("id"),
                description="Echec de paiement",
            )
            db.add(event)
            await db.commit()

    @staticmethod
    async def _handle_subscription_updated(db: AsyncSession, sub_data: dict):
        subscription_id = sub_data.get("id")
        stmt = select(TenantSubscription).where(
            TenantSubscription.stripe_subscription_id == subscription_id
        )
        row = await db.execute(stmt)
        sub = row.scalar_one_or_none()

        if sub:
            sub.status = sub_data.get("status", sub.status)
            if sub_data.get("current_period_start"):
                sub.current_period_start = datetime.fromtimestamp(
                    sub_data["current_period_start"], tz=timezone.utc
                )
            if sub_data.get("current_period_end"):
                sub.current_period_end = datetime.fromtimestamp(
                    sub_data["current_period_end"], tz=timezone.utc
                )
            await db.commit()

    @staticmethod
    async def _handle_subscription_deleted(db: AsyncSession, sub_data: dict):
        subscription_id = sub_data.get("id")
        stmt = select(TenantSubscription).where(
            TenantSubscription.stripe_subscription_id == subscription_id
        )
        row = await db.execute(stmt)
        sub = row.scalar_one_or_none()

        if sub:
            sub.status = "canceled"
            await db.commit()

            stmt_free = select(SubscriptionTier).where(SubscriptionTier.name == "free")
            row_free = await db.execute(stmt_free)
            free_tier = row_free.scalar_one_or_none()
            if free_tier:
                sub.tier_id = free_tier.id
                await db.commit()

            event = SubscriptionEvent(
                tenant_subscription_id=sub.id,
                tenant_id=str(sub.tenant_id),
                event_type="subscription_cancelled",
                description="Souscription annulee",
            )
            db.add(event)
            await db.commit()

    @staticmethod
    async def _get_or_create_subscription(db: AsyncSession, tenant_id: str) -> TenantSubscription:
        stmt = select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id)
        row = await db.execute(stmt)
        sub = row.scalar_one_or_none()

        if not sub:
            tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
            tenant_row = await db.execute(tenant_stmt)
            tenant = tenant_row.scalar_one()

            stripe_customer = stripe.Customer.create(
                name=tenant.name,
                metadata={"tenant_id": tenant_id},
            )

            stmt_free = select(SubscriptionTier).where(SubscriptionTier.name == "free")
            row_free = await db.execute(stmt_free)
            free_tier = row_free.scalar_one()

            sub = TenantSubscription(
                tenant_id=tenant_id,
                tier_id=free_tier.id,
                stripe_customer_id=stripe_customer.id,
                status="active",
            )
            db.add(sub)
            await db.commit()
            await db.refresh(sub)

        return sub

    @staticmethod
    async def _get_subscription(db: AsyncSession, tenant_id: str) -> Optional[TenantSubscription]:
        stmt = select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id)
        row = await db.execute(stmt)
        return row.scalar_one_or_none()
