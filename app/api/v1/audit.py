"""API endpoints pour l'audit trail."""

import csv
import io
from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.agents.auditor import AuditEngine

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs")
async def list_audit_logs(
    action_category: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les logs d'audit avec filtres optionnels."""
    engine = AuditEngine(db)
    logs, total = await engine.search_logs(
        tenant_id=current_user.tenant_id,
        action_category=action_category,
        action=action,
        severity=severity,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    return {
        "items": [
            {
                "id": str(log.id),
                "actor_type": log.actor_type,
                "actor_id": str(log.actor_id) if log.actor_id else None,
                "actor_email": log.actor_email,
                "action": log.action,
                "action_category": log.action_category,
                "target_type": log.target_type,
                "target_id": str(log.target_id) if log.target_id else None,
                "target_display": log.target_display,
                "change_summary": log.change_summary,
                "severity": log.severity,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/logs/{target_type}/{target_id}")
async def get_logs_for_target(
    target_type: str,
    target_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recupere l'historique d'audit pour une cible specifique."""
    engine = AuditEngine(db)
    logs = await engine.get_logs_for_target(
        tenant_id=current_user.tenant_id,
        target_type=target_type,
        target_id=target_id,
        limit=limit,
        offset=offset,
    )

    return {
        "items": [
            {
                "id": str(log.id),
                "actor_type": log.actor_type,
                "actor_email": log.actor_email,
                "action": log.action,
                "change_summary": log.change_summary,
                "before_state": log.before_state,
                "after_state": log.after_state,
                "severity": log.severity,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }


@router.get("/stats")
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Statistiques d'activite pour le dashboard."""
    engine = AuditEngine(db)
    stats = await engine.get_activity_stats(
        tenant_id=current_user.tenant_id,
        days=days,
    )
    return stats


@router.get("/export/csv")
async def export_audit_csv(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Exporte l'audit trail au format CSV."""
    engine = AuditEngine(db)
    logs, _ = await engine.search_logs(
        tenant_id=current_user.tenant_id,
        date_from=date_from,
        date_to=date_to,
        limit=10000,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "timestamp", "actor_type", "actor_email", "action", "category",
        "target_type", "target_display", "change_summary", "severity",
    ])

    for log in logs:
        writer.writerow([
            log.created_at.isoformat() if log.created_at else "",
            log.actor_type,
            log.actor_email or "",
            log.action,
            log.action_category,
            log.target_type,
            log.target_display or "",
            log.change_summary or "",
            log.severity,
        ])

    output.seek(0)
    filename = f"audit_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
