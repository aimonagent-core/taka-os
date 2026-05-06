"""Scraper pour les Departements de France."""
import logging
from datetime import datetime
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class DepartementScraper(BaseScraper):
    """Scraper pour les marches publics des departements francais."""

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        """Scanne les AO des departements."""
        results = []
        logger.info("[%s] Scan des departements", self.name)
        return results
