"""
Schemas Pydantic v2 pour le scraper BOAMP et les reponses API scraper.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class BOAMPRecord(BaseModel):
    """
    Schema d'un enregistrement brut retourne par l'API data.economie.gouv.fr.
    """
    model_config = ConfigDict(extra="allow")

    uid: str
    titre: Optional[str] = None
    objet: Optional[str] = None
    datePublication: Optional[str] = None
    dateCloture: Optional[str] = None
    montant: Optional[float] = None
    acheteur: Optional[str] = None
    lieuExecution: Optional[str] = None
    cpv: Optional[str] = None
    libelleCpv: Optional[str] = None
    procedure: Optional[str] = None
    nature: Optional[str] = None
    format: Optional[str] = None
    uris: Optional[list[str]] = None


class BOAMPApiResponse(BaseModel):
    """
    Schema de la reponse complete de l'API data.economie.gouv.fr.
    """
    model_config = ConfigDict(extra="allow")

    total_count: Optional[int] = None
    results: list[BOAMPRecord] = Field(default_factory=list)


class ScraperRunReport(BaseModel):
    """
    Rapport d'une execution de scraper.
    """
    source: str
    total_fetched: int
    inserted: int
    duplicates: int
    errors: int
    started_at: datetime
    finished_at: datetime
    duration_seconds: float


class ScraperStatus(BaseModel):
    """
    Etat d'un scraper pour le endpoint health.
    """
    source: str
    is_healthy: bool
    last_run_at: Optional[datetime] = None
    last_run_count: Optional[int] = None
    last_run_status: Optional[str] = None  # "ok" | "error" | "never_run"
    error_message: Optional[str] = None


class ScraperTriggerRequest(BaseModel):
    """
    Body de la requete pour declencher un scraper via l'API.
    """
    limit: int = Field(default=100, ge=1, le=1000)
    where: Optional[str] = None
    order_by: Optional[str] = "dateparution DESC"


class ScraperTriggerResponse(BaseModel):
    """
    Reponse du endpoint de declenchement d'un scraper.
    """
    success: bool
    source: str
    report: ScraperRunReport


class ScraperListResponse(BaseModel):
    """
    Reponse listant tous les scrapers disponibles.
    """
    scrapers: list[ScraperStatus]
