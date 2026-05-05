"""Scraper Marches Publics .gov.ma (Maroc)."""
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseScraper, RawAOData

logger = logging.getLogger(__name__)


class MarchePublicScraper(BaseScraper):
    """Scraper pour les marches publics du Maroc (HTML scraping)."""

    LIST_PATH = "/ma/ac_appeloffre.asp"

    async def scan(self, since: Optional[datetime] = None) -> list[RawAOData]:
        results = []
        if not since:
            since = datetime.utcnow() - timedelta(days=7)

        try:
            response = await self._fetch(f"{self.base_url}{self.LIST_PATH}")
            soup = BeautifulSoup(response.text, "html.parser")

            rows = soup.find_all("tr", class_=["ligne1", "ligne2"])
            if not rows:
                rows = soup.select("table tr")

            for row in rows:
                try:
                    ao = self._parse_row(row)
                    if ao and ao.publication_date and ao.publication_date >= since:
                        results.append(ao)
                except Exception as e:
                    logger.warning("[%s] Erreur parsing row : %s", self.name, e)
                    continue

        except Exception as e:
            logger.error("[%s] Erreur scan: %s", self.name, e)

        logger.info("[%s] %s AO detectes", self.name, len(results))
        return results

    def _parse_row(self, row) -> Optional[RawAOData]:
        cells = row.find_all(["td", "th"])
        if len(cells) < 3:
            return None

        ao = RawAOData()
        texts = [cell.get_text(strip=True) for cell in cells]
        links = row.find_all("a", href=True)

        ao.title = texts[1] if len(texts) > 1 else texts[0] if texts else "Sans titre"
        if len(ao.title) < 5:
            return None

        if links:
            href = links[0]["href"]
            ao.external_id = (
                href.split("id=")[-1].split("&")[0]
                if "id=" in href
                else href.split("/")[-1]
            )
            ao.external_url = href if href.startswith("http") else f"{self.base_url}{href}"
        else:
            ao.external_id = f"ma_{hash(ao.title) % 10000000}"

        for text in texts:
            date = self._extract_date(text)
            if date:
                if not ao.publication_date:
                    ao.publication_date = date
                elif not ao.deadline_date and date > ao.publication_date:
                    ao.deadline_date = date

        for text in texts:
            amount = self._extract_amount(text)
            if amount:
                ao.estimated_amount = amount
                break

        ao.country = "MA"
        ao.currency = "MAD"
        ao.raw_data = {"cells": texts}

        return ao

    def _extract_date(self, text: str) -> Optional[datetime]:
        if not text:
            return None
        match = re.search(r"(\d{2})[/-](\d{2})[/-](\d{4})", text)
        if match:
            try:
                return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            except ValueError:
                return None
        return None

    def _extract_amount(self, text: str) -> Optional[float]:
        if not text:
            return None
        match = re.search(r"([\d\s]+(?:\.\d+)?)\s*(?:DH|MAD|dirhams?)", text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(" ", "").replace("\u202f", ""))
            except ValueError:
                return None
        return None
