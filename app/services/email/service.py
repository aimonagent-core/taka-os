"""Service d'envoi d'emails via Resend."""
import logging
from typing import Optional

import resend
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.billing import EmailLog

logger = logging.getLogger(__name__)

if settings.resend_api_key:
    resend.api_key = settings.resend_api_key


class EmailService:
    """Envoi d'emails avec tracking."""

    @staticmethod
    async def send_email(
        db: AsyncSession,
        recipient: str,
        subject: str,
        html_body: str,
        email_type: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Envoie un email et log le resultat."""
        if not settings.resend_api_key:
            logger.warning("[Email] Resend API key non configuree — email non envoye")
            return False

        log = EmailLog(
            tenant_id=tenant_id,
            user_id=user_id,
            email_type=email_type,
            recipient=recipient,
            subject=subject,
            status="pending",
        )
        db.add(log)
        await db.commit()

        try:
            params: resend.Emails.SendParams = {
                "from": f"{settings.from_name} <{settings.from_email}>",
                "to": [recipient],
                "subject": subject,
                "html": html_body,
            }
            response = resend.Emails.send(params)
            message_id = response.get("id") if isinstance(response, dict) else str(response)

            log.status = "sent"
            log.provider_message_id = message_id
            await db.commit()
            logger.info(f"[Email] Envoye a {recipient} — {email_type}")
            return True

        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            await db.commit()
            logger.error(f"[Email] Echec envoi a {recipient} : {e}")
            return False

    @staticmethod
    async def send_welcome_email(
        db: AsyncSession,
        recipient: str,
        user_name: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        from app.services.email.templates import welcome_template
        html = welcome_template(user_name)
        return await EmailService.send_email(
            db, recipient, "Bienvenue sur TAKA OS", html, "welcome",
            tenant_id=tenant_id, user_id=user_id,
        )

    @staticmethod
    async def send_payment_confirmation(
        db: AsyncSession,
        recipient: str,
        plan_name: str,
        amount: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        from app.services.email.templates import payment_confirmation_template
        html = payment_confirmation_template(plan_name, amount)
        return await EmailService.send_email(
            db, recipient, "Confirmation de paiement — TAKA OS", html, "payment_confirmation",
            tenant_id=tenant_id, user_id=user_id,
        )

    @staticmethod
    async def send_daily_alert(
        db: AsyncSession,
        recipient: str,
        aos_count: int,
        ao_list_html: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        from app.services.email.templates import daily_alert_template
        html = daily_alert_template(aos_count, ao_list_html)
        return await EmailService.send_email(
            db, recipient, f"Votre veille du jour — {aos_count} nouveaux AO", html, "daily_alert",
            tenant_id=tenant_id, user_id=user_id,
        )

    @staticmethod
    async def send_subscription_cancelled(
        db: AsyncSession,
        recipient: str,
        plan_name: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        from app.services.email.templates import subscription_cancelled_template
        html = subscription_cancelled_template(plan_name)
        return await EmailService.send_email(
            db, recipient, "Votre souscription a ete annulee — TAKA OS", html, "subscription_cancelled",
            tenant_id=tenant_id, user_id=user_id,
        )
