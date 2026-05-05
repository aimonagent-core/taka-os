# File: app/schemas/memory.py
# Purpose: Memory Pydantic schemas

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MemoryEntryBase(BaseModel):
    memory_type: str
    content: dict[str, Any]
    priority: int = 3
    source_type: str = "document"


class MemoryEntryOut(MemoryEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    source_id: UUID | None = None
    content_hash: str
    embedding: list[float] | None = None
    ttl_seconds: int | None = None
    access_count: int = 0
    decay_factor: float = 1.0
    created_at: datetime


class MemorySearchResult(BaseModel):
    id: str
    entry_type: str | None = None
    content: str
    layer: str
    relevance_score: float | None = None
    created_at: str | None = None
