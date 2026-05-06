"""Routes pour le module fiducial (comptabilite).

Routes :
  POST /fiducial/init                    → Initialiser le plan de compte
  GET  /fiducial/chart                   → Plan de compte
  POST /fiducial/ao/{ao_id}/record       → Enregistrer un AO gagne
  GET  /fiducial/fec/{fiscal_year}       → Exporter le FEC
  GET  /fiducial/summary/{fiscal_year}   → Resume comptable
"""

from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.services.fiducial.engine import FiducialEngine

router = APIRouter(prefix="/fiducial", tags=["fiducial"])


class RecordWonAORequest(BaseModel):
    final_amount: float
    margin_percent: float = 15.0


@router.post("/init")
async def init_chart(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(["tenant_admin"])),
):
    """Initialise le plan de compte par defaut."""
    engine = FiducialEngine(db)
    count = await engine.init_default_chart(current_user.tenant_id)
    return {"created": count, "message": f"{count} comptes crees"}


@router.get("/chart")
async def get_chart(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Plan de compte du tenant."""
    from app.models.fiducial import PlanComptableEntry
    from sqlalchemy import select

    stmt = select(PlanComptableEntry).where(
        PlanComptableEntry.tenant_id == current_user.tenant_id
    ).order_by(PlanComptableEntry.account_number)

    result = await db.execute(stmt)
    entries = result.scalars().all()

    return {
        "accounts": [
            {
                "number": e.account_number,
                "name": e.account_name,
                "type": e.account_type.value,
            }
            for e in entries
        ],
    }


@router.post("/ao/{ao_id}/record")
async def record_won_ao(
    ao_id: uuid.UUID,
    data: RecordWonAORequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(["tenant_admin", "tenant_manager"])),
):
    """Enregistre un AO gagne en comptabilite."""
    engine = FiducialEngine(db)
    link = await engine.record_won_ao(
        tenant_id=current_user.tenant_id,
        ao_id=ao_id,
        final_amount=data.final_amount,
        margin_percent=data.margin_percent,
    )
    return {
        "ao_id": str(ao_id),
        "final_amount": data.final_amount,
        "journal_entries": link.journal_entry_ids,
    }


@router.get("/fec/{fiscal_year}")
async def export_fec(
    fiscal_year: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Exporte le FEC au format CSV tabule."""
    engine = FiducialEngine(db)
    fec_data = await engine.export_fec(current_user.tenant_id, fiscal_year)

    from fastapi.responses import PlainTextResponse
    filename = f"FEC_{current_user.tenant_id}_{fiscal_year}.txt"
    return PlainTextResponse(
        fec_data,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/summary/{fiscal_year}")
async def get_accounting_summary(
    fiscal_year: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Resume comptable."""
    engine = FiducialEngine(db)
    summary = await engine.get_accounting_summary(current_user.tenant_id, fiscal_year)
    return summary
