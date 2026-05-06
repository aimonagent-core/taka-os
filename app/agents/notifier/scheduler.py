"""Scheduler pour l'envoi quotidien des alertes AO par email."""
import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.ao import AO, User
from app.models.ao_s2 import Source
from app.models.billing import EmailLog, EmailPreference
from app.services.email.service import EmailService

logger = logging.getLogger(__name__)


class DailyAlertScheduler:
    """Planifie et execute l'envoi des alertes quotidiennes."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Demarre le scheduler."""
        self.scheduler.add_job(
            self._send_daily_alerts,
            trigger=CronTrigger(hour=8, minute=0),
            id="daily_ao_alert",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("[Scheduler] Daily alert scheduler demarre (08:00 UTC)")

    def shutdown(self):
        """Arrete le scheduler."""
        self.scheduler.shutdown()
        logger.info("[Scheduler] Daily alert scheduler arrete")

    @staticmethod
    async def _send_daily_alerts():
        """Envoie les alertes quotidiennes a tous les utilisateurs abonnes."""
        logger.info("[Scheduler] Debut envoi alertes quotidiennes")

        async for db in get_db():
            since = datetime.now(timezone.utc) - timedelta(hours=24)

            # Recuperer les utilisateurs avec alertes activees
            stmt = (
                select(User, EmailPreference)
                .join(EmailPreference, User.id == EmailPreference.user_id)
                .where(EmailPreference.daily_alert_enabled.is_(True))
            )
            rows = await db.execute(stmt)
            users = rows.all()

            for user, prefs in users:
                await DailyAlertScheduler._send_alert_for_user(db, user, since)

            logger.info(f"[Scheduler] {len(users)} utilisateurs traites")
            break  # get_db est un generateur, on sort apres une iteration

    @staticmethod
    async def _send_alert_for_user(db: AsyncSession, user: User, since: datetime):
        """Envoie l'alerte pour un utilisateur specifique."""
        from app.models.business_line import BusinessLine

        # Recuperer les nouveaux AO pour le tenant
        stmt = (
            select(AO)
            .where(
                AO.tenant_id == user.tenant_id,
                AO.created_at >= since,
            )
            .order_by(AO.created_at.desc())
            .limit(20)
        )
        rows = await db.execute(stmt)
        aos = rows.scalars().all()

        if not aos:
            return

        # Construire la liste HTML
        ao_items = []
        for ao in aos:
            ao_items.append(
                f"""
                <div style="border:1px solid #e5e5e5;padding:1rem;margin:0.5rem 0;border-radius:6px;">
                    <strong>{ao.title or 'Sans titre'}</strong><br>
                    <span style="color:#666;font-size:0.9rem;">{ao.country or 'FR'} — {ao.estimated_amount or 'Montant non precise'} EUR</span><br>
                    <a href="https://app.taka-os.com/ao/{ao.id}" style="color:#2563eb;">Voir l'AO</a>
                </div>
                """
            )

        ao_list_html = "\n".join(ao_items)

        await EmailService.send_daily_alert(
            db,
            recipient=user.email,
            aos_count=len(aos),
            ao_list_html=ao_list_html,
            tenant_id=str(user.tenant_id),
            user_id=str(user.id),
        )


# Singleton
scheduler = DailyAlertScheduler()
