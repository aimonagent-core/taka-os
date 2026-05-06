# =============================================================================
# Sprint 11 — Schemas Pydantic pour l'onboarding entreprise multi-etapes
# =============================================================================

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CPVPreferenceItem(BaseModel):
    """Un CPV selectionne par le tenant."""
    cpv_code: str = Field(..., max_length=20)
    label: str = Field(..., max_length=200)
    weight: float = Field(default=1.0, ge=0.0, le=10.0)


class OnboardingEnterpriseRequest(BaseModel):
    """Requete complete de configuration initiale d'un tenant + admin (Sprint 11)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # --- Etape 1 : Identite ---
    tenant_name: str = Field(..., min_length=1, max_length=255)
    siret: str = Field(..., pattern=r"^\d{14}$", description="SIRET 14 chiffres")
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8, max_length=128)
    admin_full_name: Optional[str] = Field(None, max_length=255)

    # --- Etape 2 : Domaine d'activite ---
    domaine_activite: list[str] = Field(default_factory=list, max_length=20)

    # --- Etape 3 : CPV cibles ---
    cpv_preferences: list[CPVPreferenceItem] = Field(default_factory=list, max_length=10)

    # --- Etape 4 : Contexte operationnel ---
    effectif: Optional[str] = Field(None, pattern=r"^(1-10|11-50|51-200|201-500|500+)$")
    ca_annuel: Optional[float] = Field(None, ge=0)
    zones_geo: list[str] = Field(default_factory=list, max_length=200)
    types_marche_acceptes: list[str] = Field(
        default_factory=list,
        description="Travaux, Services, Fournitures, Concession"
    )

    plan: str = Field(default="free", pattern=r"^(free|starter|pro|enterprise)$")


class OnboardingEnterpriseResponse(BaseModel):
    """Reponse apres creation d'un tenant entreprise et de son administrateur."""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: str
    tenant_uuid: str
    admin_user_id: str
    admin_email: str
    access_token: str
    token_type: str
    onboarding_completed: bool
    message: str


class OnboardingStatusResponse(BaseModel):
    """Statut d'avancement de l'onboarding d'un tenant."""

    tenant_id: str
    onboarding_completed: bool
    onboarding_completed_at: Optional[str] = None
    has_cpv_preferences: bool
    has_business_line: bool
    fields_filled: dict
