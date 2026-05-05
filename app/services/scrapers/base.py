"""Base abstraite pour tous les scrapers de veille."""
import asyncio
import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


class RawAOData:
    """Donnees brutes extraites d'une source — normalisees avant stockage."""

    def __init__(self):
        self.external_id: str = ""
        self.title: str = ""
        self.description: Optional[str] = None
        self.cpv_codes: list[str] = []
        self.country: str = "FR"
        self.department_code: Optional[str] = None
        self.department_name: Optional[str] = None
        self.region: Optional[str] = None
        self.city: Optional[str] = None
        self.estimated_amount: Optional[float] = None
        self.currency: str = "EUR"
        self.publication_date: Optional[datetime] = None
        self.deadline_date: Optional[datetime] = None
        self.contract_duration_months: Optional[int] = None
        self.notice_type: Optional[str] = None
        self.buyer_name: Optional[str] = None
        self.contact_email: Optional[str] = None
        self.contact_phone: Optional[str] = None
        self.external_url: Optional[str] = None
        self.raw_data: dict = {}


class BaseScraper(ABC):
    """Scraper asynchrone avec rate limiting, retry, et gestion d'erreur."""

    def __init__(self, source_config: dict):
        self.config = source_config
        self.name = source_config.get("name", "unknown")
        self.base_url = source_config.get("base_url", "")
        self.client: Optional[httpx.AsyncClient] = None
        self.min_delay = source_config.get("min_delay_seconds", 2.0)
        self.max_delay = source_config.get("max_delay_seconds", 5.0)

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": random.choice(USER_AGENTS)},
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def _delay(self):
        """Delai aleatoire entre requetes pour respecter le serveur."""
        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def _fetch(self, url: str, method: str = "GET", **kwargs) -> httpx.Response:
        """Requete HTTP avec retry exponentiel."""
        if not self.client:
            raise RuntimeError("Client HTTP non initialise — utiliser async with")
        await self._delay()
        logger.info("[%s] %s %s", self.name, method, url)
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    @abstractmethod
    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        """
        Scanne la source et retourne la liste des nouveaux AO detectes.
        Args:
            since: Date de dernier scan — ne retourner que les AO plus recents.
        Returns:
            Liste de RawAOData normalises.
        """
        pass

    async def health_check(self) -> dict:
        """Verifie que la source est accessible."""
        try:
            start = datetime.utcnow()
            await self._fetch(self.base_url, method="HEAD")
            latency = int((datetime.utcnow() - start).total_seconds() * 1000)
            return {"ok": True, "latency_ms": latency, "error": None}
        except Exception as e:
            return {"ok": False, "latency_ms": 0, "error": str(e)}
