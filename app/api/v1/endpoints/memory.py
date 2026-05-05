# File: app/api/v1/endpoints/memory.py
# Purpose: Memory search and management endpoints
# Dependencies: fastapi, sqlalchemy, app.services.memory

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import MemoryEntry, User
from app.schemas.memory import MemoryEntryOut, MemorySearchResult
from app.services.llm.mistral_client import MistralAIClient
from app.services.memory.memory_service import MemoryService

router = APIRouter()


@router.get("/search", response_model=list[MemorySearchResult])
async def search_memory(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    svc = MemoryService(db, MistralAIClient(api_key=settings.mistral_api_key))
    results = await svc.search(q, user_id=current_user.id, limit=limit)
    return [
        {
            "id": str(r.id),
            "entry_type": r.memory_type if r.memory_type else None,
            "content": str(r.content.get("text", ""))[:500] if isinstance(r.content, dict) else str(r.content)[:500],
            "layer": "stm" if (r.ttl_seconds or 0) < 86400 * 7 else "im" if (r.ttl_seconds or 0) < 86400 * 365 else "ltm",
            "relevance_score": r.decay_factor,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in results
    ]


@router.get("", response_model=list[MemoryEntryOut])
async def list_memory(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[MemoryEntry]:
    from sqlalchemy import select

    stmt = (
        select(MemoryEntry)
        .where(MemoryEntry.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(MemoryEntry.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/{entry_id}/promote")
async def promote_to_ltm(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    svc = MemoryService(db, MistralAIClient(api_key=settings.mistral_api_key))
    ok = await svc.promote_to_ltm(entry_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory entry not found")
    return {"status": "promoted", "entry_id": str(entry_id), "layer": "ltm"}
