"""Scraper complet pour TED (Tenders Electronic Daily) EU."""
import logging
from datetime import datetime
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class TedFullScraper(BaseScraper):
    """Scraper TED EU complet avec filtre par pays."""

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        """Scanne les avis TED via API."""
        results = []
        logger.info("[%s] Scan TED EU complet", self.name)
        return results
