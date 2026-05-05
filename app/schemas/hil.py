# File: app/schemas/hil.py
# Purpose: HIL Pydantic schemas

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HILRequestBase(BaseModel):
    decision_type: str
    context: dict[str, Any] = {}


class HILRequestCreate(HILRequestBase):
    pass


class HILRequestOut(HILRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: UUID
    autonomy_level: int
    status: str
    expires_at: datetime | None = None
    decided_by: UUID | None = None
    decided_at: datetime | None = None
    decision_value: dict[str, Any] | None = None
    created_at: datetime


class HILDecisionCreate(BaseModel):
    decision: str
    notes: str | None = None
