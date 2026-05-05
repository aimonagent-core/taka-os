# File: app/schemas/audit.py
# Purpose: Audit log Pydantic schemas
# Dependencies: pydantic

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    entity_type: str
    entity_id: str | None
    user_id: str | None
    tenant_id: str | None
    created_at: datetime
    hash: str
