"""
Package scrapers — services d'extraction des appels d'offres.
"""

from app.services.scrapers.base import BaseScraper, BaseScraperV2, RawAOData, ScrapedAO
from app.services.scrapers.boamp import ScraperBOAMP
from app.services.scrapers.schemas import (
    BOAMPApiResponse,
    BOAMPRecord,
    ScraperListResponse,
    ScraperRunReport,
    ScraperStatus,
    ScraperTriggerRequest,
    ScraperTriggerResponse,
)

__all__ = [
    "BaseScraper",
    "BaseScraperV2",
    "RawAOData",
    "ScrapedAO",
    "ScraperBOAMP",
    "BOAMPApiResponse",
    "BOAMPRecord",
    "ScraperListResponse",
    "ScraperRunReport",
    "ScraperStatus",
    "ScraperTriggerRequest",
    "ScraperTriggerResponse",
]
