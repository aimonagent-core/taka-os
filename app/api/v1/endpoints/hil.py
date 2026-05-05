# File: app/api/v1/endpoints/hil.py
# Purpose: Human-in-the-loop endpoints
# Dependencies: fastapi, sqlalchemy, app.services.hil

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import HILRequest, User
from app.schemas.hil import HILDecisionCreate, HILRequestOut
from app.services.hil.hil_service import HILService

router = APIRouter()


@router.get("/pending", response_model=list[HILRequestOut])
async def get_pending_hil(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[HILRequest]:
    svc = HILService(db)
    return await svc.get_pending(user_id=current_user.id)


@router.post("/{hil_id}/resolve", response_model=dict[str, Any])
async def resolve_hil(
    hil_id: UUID,
    payload: HILDecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    svc = HILService(db)
    try:
        hil = await svc.resolve(
            hil_id=hil_id,
            decision=payload.decision,
            resolver_id=current_user.id,
            notes=payload.notes or "",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {
        "hil_id": str(hil_id),
        "status": hil.status,
        "decision": payload.decision,
        "resolved_at": hil.decided_at.isoformat() if hil.decided_at else None,
    }


@router.post("/{hil_id}/reject", response_model=dict[str, Any])
async def reject_hil(
    hil_id: UUID,
    payload: HILDecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    svc = HILService(db)
    try:
        hil = await svc.reject(
            hil_id=hil_id,
            resolver_id=current_user.id,
            reason=payload.notes or "",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {
        "hil_id": str(hil_id),
        "status": hil.status,
        "resolved_at": hil.decided_at.isoformat() if hil.decided_at else None,
    }


@router.post("/{hil_id}/escalate", response_model=dict[str, Any])
async def escalate_hil(
    hil_id: UUID,
    to_user_id: UUID,
    reason: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    svc = HILService(db)
    try:
        new_hil = await svc.escalate(
            hil_id=hil_id,
            to_user_id=to_user_id,
            reason=reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {
        "original_hil_id": str(hil_id),
        "new_hil_id": str(new_hil.id),
        "status": new_hil.status,
    }
