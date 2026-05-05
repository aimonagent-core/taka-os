"""Scraper BOAMP — API data.economie.gouv.fr."""
import logging
import re
from datetime import datetime
from typing import Optional

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class BOAMPScraper(BaseScraper):
    """Scraper pour le Bulletin Officiel des Annonces des Marches Publics (France)."""

    API_PATH = "/api/explore/v2.1/catalog/datasets/boamp/records"

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        results = []
        offset = 0
        limit = 100
        max_pages = 10

        for page in range(max_pages):
            params = {
                "limit": limit,
                "offset": offset,
                "order_by": "dateparution desc",
            }
            if since:
                params["where"] = f"dateparution >= '{since.isoformat()}'"

            url = f"{self.base_url}{self.API_PATH}"
            try:
                response = await self._fetch(url, params=params)
                data = response.json()
                records = data.get("results", [])

                if not records:
                    break

                for record in records:
                    try:
                        ao = self._parse_record(record)
                        if ao:
                            results.append(ao)
                    except Exception as e:
                        logger.warning("[%s] Erreur parsing record : %s", self.name, e)
                        continue

                offset += limit
                if len(records) < limit:
                    break

            except Exception as e:
                logger.error("[%s] Erreur page %s: %s", self.name, page, e)
                break

        logger.info("[%s] %s AO detectes", self.name, len(results))
        return results

    def _parse_record(self, record: dict) -> Optional[RawAOData]:
        """Parse un record BOAMP en RawAOData normalise."""
        fields = record.get("record", {}).get("fields", record)

        ao = RawAOData()
        ao.external_id = str(fields.get("idweb", fields.get("_id", "")))
        if not ao.external_id:
            return None

        ao.title = fields.get("titre", "Sans titre")
        ao.description = fields.get("objet", fields.get("description", None))
        ao.cpv_codes = self._extract_cpv(fields.get("codecpv", ""))
        ao.country = "FR"
        ao.department_code = self._extract_department(fields.get("departement", ""))
        ao.department_name = fields.get("departement", None)
        ao.region = fields.get("region", None)
        ao.city = fields.get("ville", None)
        ao.estimated_amount = self._parse_amount(fields.get("montant", None))
        ao.currency = "EUR"
        ao.publication_date = self._parse_date(fields.get("dateparution", None))
        ao.deadline_date = self._parse_date(
            fields.get("datedeclair", fields.get("datelimitereponse", None))
        )
        ao.contract_duration_months = self._parse_duration(fields.get("dureemarche", None))
        ao.notice_type = self._map_notice_type(fields.get("typedannece", ""))
        ao.buyer_name = fields.get("acheteur", fields.get("nomacheteur", None))
        ao.contact_email = fields.get("mel", None)
        ao.contact_phone = fields.get("tel", None)
        ao.external_url = fields.get("urllink", None)
        ao.raw_data = fields

        return ao

    def _extract_cpv(self, cpv_raw) -> list[str]:
        if not cpv_raw:
            return []
        if isinstance(cpv_raw, list):
            return [str(c).strip()[:8] for c in cpv_raw if c]
        return [str(cpv_raw).strip()[:8]]

    def _extract_department(self, dept_raw) -> Optional[str]:
        if not dept_raw:
            return None
        dept_str = str(dept_raw).strip()
        match = re.match(r"(\d{2,3})", dept_str)
        return match.group(1) if match else None

    def _parse_amount(self, amount_raw) -> Optional[float]:
        if not amount_raw:
            return None
        try:
            if isinstance(amount_raw, (int, float)):
                return float(amount_raw)
            cleaned = (
                str(amount_raw)
                .replace(" ", "")
                .replace("\u202f", "")
                .replace("EUR", "")
                .replace("€", "")
            )
            return float(cleaned)
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
            for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(str(date_raw)[:10], fmt)
                except ValueError:
                    continue
            return None

    def _parse_duration(self, duration_raw) -> Optional[int]:
        if not duration_raw:
            return None
        match = re.search(r"(\d+)", str(duration_raw))
        return int(match.group(1)) if match else None

    def _map_notice_type(self, type_raw: str) -> Optional[str]:
        mapping = {
            "appel_offre_ouvert": "appel_offre_ouvert",
            "appel_offre_restreint": "appel_offre_restreint",
            "procedure_adaptee": "procedure_adaptee",
            "marche_negocie": "marche_negocie",
        }
        type_lower = str(type_raw).lower().strip()
        return mapping.get(type_lower, "appel_offre_ouvert")
