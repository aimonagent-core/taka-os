"""Scheduler APScheduler pour declenchement automatique de l'Agent Veilleur."""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.ao_s2 import Source
from app.agents.veilleur.agent import VeilleurAgent

logger = logging.getLogger(__name__)


class VeilleurScheduler:
    """Planificateur de scans de veille. Un job par source active."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.agent = VeilleurAgent()
        self._jobs = {}

    async def start(self):
        """Demarre le scheduler et enregistre les jobs pour chaque source active."""
        async with AsyncSessionLocal() as db:
            stmt = select(Source).where(Source.is_active.is_(True))
            rows = await db.execute(stmt)
            sources = rows.scalars().all()

            for source in sources:
                self._schedule_source(source)

        self.scheduler.start()
        logger.info("[Scheduler] %s jobs de veille actifs", len(self._jobs))

    def _schedule_source(self, source: Source):
        """Cree un job APScheduler pour une source."""
        job_id = f"veille_{source.name}"
        trigger = IntervalTrigger(minutes=source.scan_frequency_minutes)

        self.scheduler.add_job(
            func=self._run_scan,
            trigger=trigger,
            id=job_id,
            name=f"Veille {source.label}",
            replace_existing=True,
            kwargs={"source_id": str(source.id)},
            misfire_grace_time=300,
        )
        self._jobs[source.name] = job_id
        logger.info(
            "[Scheduler] Job '%s' → toutes les %smin",
            job_id,
            source.scan_frequency_minutes,
        )

    async def _run_scan(self, source_id: str):
        """Callback execute par APScheduler."""
        logger.info("[Scheduler] Scan source %s", source_id)
        async with AsyncSessionLocal() as db:
            try:
                result = await self.agent.scan_source(source_id, db)
                logger.info("[Scheduler] Resultat: %s", result)
            except Exception as e:
                logger.error("[Scheduler] Erreur scan %s: %s", source_id, e)

    def stop(self):
        """Arrete le scheduler."""
        self.scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Arrete")

    def get_status(self) -> dict:
        """Retourne le statut des jobs."""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                }
            )
        return {
            "running": self.scheduler.running,
            "jobs": jobs_info,
        }
