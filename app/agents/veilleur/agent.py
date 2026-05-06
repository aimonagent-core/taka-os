"""Agent Veilleur — coordonne la detection et l'ingestion des nouveaux AO."""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.ao_s2 import AO, Source
from app.pipeline.ingestion import IngestionPipeline
from app.services.scrapers.boamp import BOAMPScraper
from app.services.scrapers.enotification import ENotificationScraper
from app.services.scrapers.joue import JOUEScraper
from app.services.scrapers.marche_public import MarchePublicScraper
from app.services.scrapers.region_scraper import RegionScraper
from app.services.scrapers.dept_scraper import DepartementScraper
from app.services.scrapers.metropole_scraper import MetropoleScraper
from app.services.scrapers.ted_full_scraper import TedFullScraper
from app.services.scrapers.marches_etat_scraper import MarchesEtatScraper
from app.services.scrapers.aggregateur_fr import AgregateurFRScraper

logger = logging.getLogger(__name__)

SCRAPER_REGISTRY = {
    "boamp": BOAMPScraper,
    "joue": JOUEScraper,
    "enotification": ENotificationScraper,
    "marche_public": MarchePublicScraper,
    "regions": RegionScraper,
    "departements": DepartementScraper,
    "metropoles": MetropoleScraper,
    "ted": TedFullScraper,
    "marches_etat": MarchesEtatScraper,
    "agregateur_fr": AgregateurFRScraper,
}


class VeilleurAgent:
    """Agent de veille multi-source pour TAKA OS."""

    def __init__(self):
        self.pipeline = IngestionPipeline()
        self._running = False

    async def scan_source(self, source_id: str, db: AsyncSession) -> dict:
        """
        Scanne une source specifique.
        Returns: {"detected": int, "new": int, "errors": int, "duration_ms": int}
        """
        start = datetime.now(timezone.utc)
        result = {"detected": 0, "new": 0, "errors": 0, "duration_ms": 0}

        stmt = select(Source).where(Source.id == source_id, Source.is_active.is_(True))
        row = await db.execute(stmt)
        source = row.scalar_one_or_none()
        if not source:
            logger.warning("[Veilleur] Source %s introuvable ou inactive", source_id)
            return result

        scraper_class = SCRAPER_REGISTRY.get(source.name)
        if not scraper_class:
            logger.error("[Veilleur] Scraper inconnu pour source '%s'", source.name)
            result["errors"] += 1
            return result

        try:
            async with scraper_class(
                {"name": source.name, "base_url": source.base_url}
            ) as scraper:
                since = source.last_scan_at
                raw_aos = await scraper.scan(since=since)
                result["detected"] = len(raw_aos)

                for raw_ao in raw_aos:
                    try:
                        is_new = await self._process_ao(raw_ao, source, db)
                        if is_new:
                            result["new"] += 1
                    except Exception as e:
                        logger.error(
                            "[Veilleur] Erreur traitement AO %s: %s", raw_ao.external_id, e
                        )
                        result["errors"] += 1

                source.last_scan_at = datetime.now(timezone.utc)
                await db.commit()

        except Exception as e:
            logger.error("[Veilleur] Erreur scan source %s: %s", source.name, e)
            source.last_error = str(e)
            await db.commit()
            result["errors"] += 1

        result["duration_ms"] = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        logger.info(
            "[Veilleur] Source %s: %s nouveaux AO en %sms",
            source.name,
            result["new"],
            result["duration_ms"],
        )
        return result

    async def scan_all(self, db: AsyncSession) -> dict:
        """
        Scanne TOUTES les sources actives en sequence (respect rate-limit).
        Returns: {"total_detected": int, "total_new": int, "sources": dict}
        """
        stmt = select(Source).where(Source.is_active.is_(True))
        rows = await db.execute(stmt)
        sources = rows.scalars().all()

        total = {"total_detected": 0, "total_new": 0, "sources": {}}

        for source in sources:
            source_result = await self.scan_source(str(source.id), db)
            total["total_detected"] += source_result["detected"]
            total["total_new"] += source_result["new"]
            total["sources"][source.name] = source_result

        logger.info(
            "[Veilleur] Scan complet: %s nouveaux AO sur %s sources",
            total["total_new"],
            len(sources),
        )
        return total

    async def _process_ao(self, raw_ao, source: Source, db: AsyncSession) -> bool:
        """
        Traite un AO detecte : deduplication + pipeline ingestion.
        Returns: True si nouveau AO insere, False si deja existant.
        """
        stmt = select(AO).where(
            AO.source_id == source.id,
            AO.external_id == raw_ao.external_id,
        )
        row = await db.execute(stmt)
        existing = row.scalar_one_or_none()
        if existing:
            logger.debug("[Veilleur] AO deja connu: %s", raw_ao.external_id)
            return False

        ao = AO(
            source_id=source.id,
            external_id=raw_ao.external_id,
            external_url=raw_ao.external_url,
            title=raw_ao.title,
            description=raw_ao.description,
            status="detected",
            cpv_codes=raw_ao.cpv_codes,
            country=raw_ao.country,
            department_code=raw_ao.department_code,
            department_name=raw_ao.department_name,
            region=raw_ao.region,
            city=raw_ao.city,
            estimated_amount=raw_ao.estimated_amount,
            currency=raw_ao.currency,
            publication_date=raw_ao.publication_date,
            deadline_date=raw_ao.deadline_date,
            contract_duration_months=raw_ao.contract_duration_months,
            notice_type=raw_ao.notice_type,
            buyer_name=raw_ao.buyer_name,
            contact_email=raw_ao.contact_email,
            contact_phone=raw_ao.contact_phone,
            raw_data=raw_ao.raw_data,
            keywords=[],
        )
        db.add(ao)
        await db.commit()
        await db.refresh(ao)

        asyncio.create_task(self.pipeline.process_ao(str(ao.id)))

        return True

    async def health_check(self, db: AsyncSession) -> dict:
        """Verifie l'etat de toutes les sources."""
        stmt = select(Source).where(Source.is_active.is_(True))
        rows = await db.execute(stmt)
        sources = rows.scalars().all()

        checks = {}
        for source in sources:
            scraper_class = SCRAPER_REGISTRY.get(source.name)
            if scraper_class:
                try:
                    async with scraper_class(
                        {"name": source.name, "base_url": source.base_url}
                    ) as scraper:
                        checks[source.name] = await scraper.health_check()
                except Exception as e:
                    checks[source.name] = {"ok": False, "latency_ms": 0, "error": str(e)}
            else:
                checks[source.name] = {
                    "ok": False,
                    "latency_ms": 0,
                    "error": "Scraper non implemente",
                }

        return checks
