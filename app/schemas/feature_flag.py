# File: app/schemas/feature_flag.py
# Purpose: Feature flag Pydantic schemas
# Dependencies: pydantic

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.ao import FeatureFlagScope


class FeatureFlagCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    scope: FeatureFlagScope = FeatureFlagScope.GLOBAL
    tenant_id: str | None = None
    user_id: str | None = None
    enabled: bool = False
    gated_by_plan: str | None = Field(None, max_length=50)
    rollout_percentage: int = Field(100, ge=0, le=100)


class FeatureFlagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    scope: str
    enabled: bool
    kill_switch: bool
    gated_by_plan: str | None
    rollout_percentage: int
    created_at: datetime
