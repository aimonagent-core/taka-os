# File: app/schemas/tenant.py
# Purpose: Tenant-related Pydantic schemas
# Dependencies: pydantic

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.ao import TenantType


class TenantCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    type: TenantType = TenantType.SOUMISSIONNAIRE
    slug: str | None = Field(None, max_length=100)


class TenantUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1, max_length=255)
    type: TenantType | None = None
    settings: dict[str, Any] | None = None
    billing_plan: str | None = Field(None, max_length=50)
    max_users: int | None = Field(None, ge=1)
    is_active: bool | None = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    slug: str
    settings: dict[str, Any] | None
    billing_plan: str | None
    max_users: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
