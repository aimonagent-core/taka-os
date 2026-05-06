# =============================================================================
# Sprint 11 — Schemas Pydantic pour le dashboard entreprise
# =============================================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KPICard(BaseModel):
    """Une carte KPI pour le dashboard."""
    label: str
    value: int | float | str
    delta: Optional[float] = None
    delta_label: Optional[str] = None
    alert: bool = False


class ChartDataPoint(BaseModel):
    """Point de donnee pour les graphiques."""
    label: str
    value: int | float
    color: Optional[str] = None


class DashboardStatsResponse(BaseModel):
    """Reponse de l'endpoint /dashboard/stats."""

    period_days: int = 7
    generated_at: str

    # KPIs header
    ao_this_week: int
    ao_this_week_delta: Optional[float] = None
    imminent_deadlines: int
    match_rate_pct: float
    new_since_last_login: int

    # Graphique repartition par type de marche
    ao_by_type: list[ChartDataPoint]

    # Evolution hebdomadaire
    weekly_evolution: list[ChartDataPoint]


class RecentAOItem(BaseModel):
    """Un AO dans la liste recente du dashboard."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    external_id: str
    title: str
    buyer_name: Optional[str] = None
    deadline_date: Optional[str] = None
    days_until_deadline: Optional[int] = None
    deadline_badge: str = "none"  # "urgent" | "soon" | "normal"
    match_score: float = 0.0
    ao_type: Optional[str] = None
    notice_type: Optional[str] = None
    url: Optional[str] = None
    is_new: bool = False


class MatchingScoreResponse(BaseModel):
    """Reponse de l'endpoint /dashboard/matching-score/{ao_id}."""

    ao_id: str
    tenant_id: str
    total_score: float = Field(..., ge=0.0, le=100.0)
    breakdown: dict
    matched_cpv: list[str] = Field(default_factory=list)
    matched_department: bool = False
    matched_type_marche: bool = False
    deadline_bonus: bool = False
    keyword_matches: list[str] = Field(default_factory=list)
