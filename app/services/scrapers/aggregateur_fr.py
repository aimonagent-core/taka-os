"""Scraper pour les agregateurs francais de marches publics."""
import logging
from datetime import datetime
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class AgregateurFRScraper(BaseScraper):
    """Scraper pour les agregateurs FR (e-marchespublics, achatpublic)."""

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        """Scanne les agregateurs."""
        results = []
        logger.info("[%s] Scan agregateurs FR", self.name)
        return results
