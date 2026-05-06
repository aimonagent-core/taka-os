# File: app/schemas/audit.py
# Purpose: Audit schemas (unified on audit_trail)
# Dependencies: pydantic

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    """Schema de reponse pour les entrees d'audit trail (legacy name kept for compat)."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_type: str
    actor_id: Optional[str]
    actor_email: Optional[str]
    action: str
    action_category: str
    target_type: str
    target_id: Optional[str]
    target_display: Optional[str]
    change_summary: Optional[str]
    severity: str
    created_at: datetime
