"""Scraper JOUE / TED (Journal Officiel de l'Union Europeenne)."""
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class JOUEScraper(BaseScraper):
    """Scraper pour le Journal Officiel de l'UE (Tenders Electronic Daily)."""

    API_PATH = "/api/v2.0/notices/search"

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        results = []
        page = 1
        max_pages = 10

        if not since:
            since = datetime.now(timezone.utc) - timedelta(days=7)

        search_body = {
            "page": page,
            "size": 100,
            "filters": {"publicationDate": {"gte": since.strftime("%Y-%m-%d")}},
            "sort": {"field": "publicationDate", "order": "DESC"},
        }

        for _ in range(max_pages):
            try:
                response = await self._fetch(
                    f"{self.base_url}{self.API_PATH}",
                    method="POST",
                    json=search_body,
                )
                data = response.json()
                notices = data.get("notices", [])

                if not notices:
                    break

                for notice in notices:
                    try:
                        ao = self._parse_notice(notice)
                        if ao:
                            results.append(ao)
                    except Exception as e:
                        logger.warning("[%s] Erreur parsing notice : %s", self.name, e)
                        continue

                if len(notices) < 100:
                    break
                page += 1
                search_body["page"] = page

            except Exception as e:
                logger.error("[%s] Erreur page %s: %s", self.name, page, e)
                break

        logger.info("[%s] %s AO detectes", self.name, len(results))
        return results

    def _parse_notice(self, notice: dict) -> Optional[RawAOData]:
        ao = RawAOData()
        ao.external_id = str(notice.get("noticeId", notice.get("id", "")))
        if not ao.external_id:
            return None

        title_raw = notice.get("title", "Sans titre")
        ao.title = title_raw[0] if isinstance(title_raw, list) else title_raw
        desc_raw = notice.get("description", None)
        ao.description = desc_raw[0] if isinstance(desc_raw, list) else desc_raw
        ao.cpv_codes = [str(c).strip()[:8] for c in notice.get("cpvCodes", [])]
        ao.country = notice.get("country", "FR")[:2].upper()
        ao.department_code = None
        ao.estimated_amount = self._parse_amount(notice.get("estimatedValue", None))
        ao.currency = notice.get("currency", "EUR")
        ao.publication_date = self._parse_date(notice.get("publicationDate", None))
        ao.deadline_date = self._parse_date(notice.get("deadline", None))
        ao.contract_duration_months = self._parse_duration(notice.get("contractDuration", None))
        buyer_raw = notice.get("buyerName", None)
        ao.buyer_name = buyer_raw[0] if isinstance(buyer_raw, list) else buyer_raw
        ao.external_url = f"https://ted.europa.eu/udl?uri=TED:NOTICE:{ao.external_id}:TEXT:FR:HTML"
        ao.raw_data = notice

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

    def _parse_duration(self, duration_raw) -> Optional[int]:
        if not duration_raw:
            return None
        match = re.search(r"(\d+)", str(duration_raw))
        return int(match.group(1)) if match else None
