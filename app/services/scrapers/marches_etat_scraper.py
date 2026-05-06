"""Scraper pour les Marches Publics de l'Etat (France)."""
import logging
from datetime import datetime
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class MarchesEtatScraper(BaseScraper):
    """Scraper pour les marches publics de l'Etat francais."""

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        """Scanne les AO de l'Etat."""
        results = []
        logger.info("[%s] Scan marches publics Etat", self.name)
        return results
