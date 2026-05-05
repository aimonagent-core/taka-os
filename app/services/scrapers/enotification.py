"""Scraper e-Notification (Belgique)."""
import logging
from datetime import datetime, timedelta
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class ENotificationScraper(BaseScraper):
    """Scraper pour e-Notification (plateforme belge de marches publics)."""

    API_PATH = "/rest/appcasting/cft-announces"

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        results = []
        if not since:
            since = datetime.utcnow() - timedelta(days=7)

        params = {
            "since": since.strftime("%Y-%m-%dT%H:%M:%S"),
            "lang": "fr",
        }

        try:
            response = await self._fetch(f"{self.base_url}{self.API_PATH}", params=params)
            data = response.json()
            announces = data if isinstance(data, list) else data.get("announces", [])

            for announce in announces:
                try:
                    ao = self._parse_announce(announce)
                    if ao:
                        results.append(ao)
                except Exception as e:
                    logger.warning("[%s] Erreur parsing announce : %s", self.name, e)
                    continue

        except Exception as e:
            logger.error("[%s] Erreur scan: %s", self.name, e)

        logger.info("[%s] %s AO detectes", self.name, len(results))
        return results

    def _parse_announce(self, announce: dict) -> Optional[RawAOData]:
        ao = RawAOData()
        ao.external_id = str(announce.get("id", announce.get("cftId", "")))
        if not ao.external_id:
            return None

        ao.title = announce.get("title", announce.get("subject", "Sans titre"))
        ao.description = announce.get("description", announce.get("body", None))
        ao.cpv_codes = [str(c).strip()[:8] for c in announce.get("cpv", [])]
        ao.country = "BE"
        ao.department_code = announce.get("nutsCode", None)
        ao.estimated_amount = self._parse_amount(announce.get("estimatedValue", None))
        ao.currency = announce.get("currency", "EUR")
        ao.publication_date = self._parse_date(announce.get("publicationDate", None))
        ao.deadline_date = self._parse_date(announce.get("deadline", None))
        ao.buyer_name = announce.get("contractingAuthority", None)
        ao.external_url = announce.get("url", None)
        ao.raw_data = announce

        return ao

    def _parse_amount(self, amount_raw) -> Optional[float]:
        if not amount_raw:
            return None
        try:
            if isinstance(amount_raw, dict):
                return float(amount_raw.get("amount", 0))
            return float(amount_raw)
        except (ValueError, TypeError):
            return None

    def _parse_date(self, date_raw) -> Optional[datetime]:
        if not date_raw:
            return None
        try:
            if isinstance(date_raw, datetime):
                return date_raw
            return datetime.fromisoformat(str(date_raw).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
