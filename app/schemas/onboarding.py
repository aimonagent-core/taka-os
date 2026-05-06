# =============================================================================
# C5 — Schemas Pydantic v2 pour le endpoint /onboarding/setup
# =============================================================================

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OnboardingSetupRequest(BaseModel):
    """Requete de configuration initiale d'un tenant + admin."""

    model_config = ConfigDict(str_strip_whitespace=True)

    tenant_name: str = Field(
        ..., min_length=1, max_length=255, description="Nom du tenant"
    )
    admin_email: EmailStr = Field(..., description="Email de l'administrateur")
    admin_password: str = Field(
        ..., min_length=8, max_length=128, description="Mot de passe"
    )
    admin_full_name: Optional[str] = Field(
        None, max_length=255, description="Nom complet"
    )
    plan: str = Field(
        default="free", pattern=r"^(free|starter|pro|enterprise)$"
    )


class OnboardingSetupResponse(BaseModel):
    """Reponse apres creation d'un tenant et de son administrateur."""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: str
    tenant_uuid: str
    admin_user_id: str
    admin_email: str
    access_token: str
    token_type: str
    message: str
