# File: app/schemas/document.py
# Purpose: Document Pydantic schemas

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    filename: str
    status: str = "pending"
    file_size: int = 0
    mime_type: str = "application/pdf"


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    status: str | None = None
    parse_result: dict[str, Any] | None = None


class DocumentOut(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    user_id: UUID
    original_filename: str
    file_path: str
    page_count: int | None = None
    parse_level_reached: int | None = None
    parse_result: dict[str, Any] | None = None
    extracted_entities: dict[str, Any] | None = None
    validation_result: dict[str, Any] | None = None
    processing_time_ms: int | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class DocumentParseResult(BaseModel):
    document_id: str
    status: str
    level_reached: int
    degraded: bool
    confidence_scores: dict[str, float]
    processing_time_ms: int
    entities: dict[str, Any]
