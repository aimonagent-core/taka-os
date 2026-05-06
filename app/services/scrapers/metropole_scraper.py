"""Scraper pour les Metropoles francaises."""
import logging
from datetime import datetime
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class MetropoleScraper(BaseScraper):
    """Scraper pour les marches publics des metropoles."""

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        """Scanne les AO des metropoles."""
        results = []
        logger.info("[%s] Scan des metropoles", self.name)
        return results
