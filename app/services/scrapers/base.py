"""Base abstraite pour tous les scrapers de veille."""
import asyncio
import hashlib
import json
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

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


@dataclass
class ScrapedAO:
    """
    Dataclass representant un appel d'offres extrait par un scraper.
    C'est le format universel de transit entre scrapers et la base de donnees.
    """
    external_id: str
    source: str
    title: str
    description: Optional[str] = None
    cpv_code: Optional[str] = None
    cpv_label: Optional[str] = None
    publication_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None
    estimated_amount: Optional[float] = None
    currency: str = "EUR"
    buyer_name: Optional[str] = None
    location: Optional[str] = None
    procedure_type: Optional[str] = None
    ao_type: Optional[str] = None
    url: Optional[str] = None
    raw_data: Optional[dict] = None


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
        """Verifie que la source est accessible (HEAD puis fallback GET)."""
        try:
            start = datetime.now(timezone.utc)
            await self._fetch(self.base_url, method="HEAD")
            latency = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return {"ok": True, "latency_ms": latency, "error": None}
        except Exception:
            try:
                start = datetime.now(timezone.utc)
                await self._fetch(self.base_url, method="GET")
                latency = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
                return {"ok": True, "latency_ms": latency, "error": None}
            except Exception as e:
                return {"ok": False, "latency_ms": 0, "error": str(e)}

    def compute_hash(self, data: dict[str, Any]) -> str:
        """Calcule le SHA-256 d'un dictionnaire pour la deduplication."""
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


class BaseScraperV2(ABC):
    """
    Classe abstraite que tous les scrapers v2 doivent heriter.
    Utilise ScrapedAO au lieu de RawAOData.

    Attributs de classe a definir:
        source_name: str — Identifiant de la source (ex: "boamp", "ted")
        base_url: str — URL de base pour les requetes
        rate_limit: float — Delai minimum en secondes entre deux requetes
    """

    source_name: str = ""
    base_url: str = ""
    rate_limit: float = 1.0

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def fetch(
        self, limit: int = 100, **kwargs: Any
    ) -> list[ScrapedAO]:
        """
        Recupere les annonces depuis la source.

        Args:
            limit: Nombre maximum d'annonces a recuperer.
            **kwargs: Parametres specifiques au scraper.

        Returns:
            Liste de ScrapedAO.
        """
        raise NotImplementedError

    async def fetch_and_store(
        self, limit: int = 100, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Recupere et stocke les annonces en base.
        A surcharger si besoin d'une logique specifique.

        Returns:
            Rapport d'execution.
        """
        raise NotImplementedError
