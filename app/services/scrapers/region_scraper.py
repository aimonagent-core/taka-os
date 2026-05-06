"""Scraper pour les Regions de France."""
import logging
from datetime import datetime
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class RegionScraper(BaseScraper):
    """Scraper pour les marches publics des regions francaises."""

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        """Scanne les AO des regions francaises."""
        results = []
        logger.info("[%s] Scan des regions francaises", self.name)
        # Stub : en production, parser les sites regionaux
        return results
