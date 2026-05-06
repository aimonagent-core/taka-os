"""Routes pour les workflows d'approbation.

Routes :
  GET  /workflows                 → Liste des workflows
  POST /workflows                 → Creer un workflow
  GET  /workflows/requests        → Demandes en cours
  GET  /workflows/requests/my     → Mes demandes
  POST /workflows/requests/{id}/decide → Approuver/Rejeter
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.ao import User
from app.services.workflow.engine import WorkflowEngine
from app.models.workflow import WorkflowTrigger

router = APIRouter(prefix="/workflows", tags=["workflows"])


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    trigger: str
    business_line_id: uuid.UUID | None = None
    steps: list[dict]


class DecisionCreate(BaseModel):
    decision: str
    comment: str | None = None


@router.get("")
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["tenant_admin", "tenant_manager"])),
):
    """Liste les workflows du tenant."""
    from app.models.workflow import ApprovalWorkflow
    from sqlalchemy import select

    stmt = select(ApprovalWorkflow).where(
        ApprovalWorkflow.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    workflows = result.scalars().all()

    return {"workflows": [{"id": str(w.id), "name": w.name, "trigger": w.trigger, "is_active": w.is_active} for w in workflows]}


@router.post("")
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["tenant_admin", "tenant_manager"])),
):
    """Cree un workflow d'approbation."""
    from app.models.workflow import ApprovalWorkflow, ApprovalStep

    workflow = ApprovalWorkflow(
        tenant_id=current_user.tenant_id,
        created_by_user_id=current_user.id,
        name=data.name,
        description=data.description,
        trigger=data.trigger,
        business_line_id=data.business_line_id,
    )
    db.add(workflow)
    await db.flush()

    for i, step_data in enumerate(data.steps, 1):
        step = ApprovalStep(
            workflow_id=workflow.id,
            step_order=i,
            step_type=step_data["step_type"],
            specific_user_id=step_data.get("specific_user_id"),
            name=step_data["name"],
            description=step_data.get("description"),
        )
        db.add(step)

    await db.flush()
    return {"id": str(workflow.id), "name": workflow.name}


@router.get("/requests")
async def get_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les demandes d'approbation en cours."""
    engine = WorkflowEngine(db)
    requests = await engine.get_pending_requests(current_user.id, current_user.tenant_id)

    return {
        "requests": [
            {
                "id": str(r.id),
                "status": r.status,
                "current_step": r.current_step_number,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in requests
        ],
    }


@router.post("/requests/{request_id}/decide")
async def make_decision(
    request_id: uuid.UUID,
    data: DecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approuve ou rejette une demande."""
    engine = WorkflowEngine(db)
    result = await engine.make_decision(
        request_id=request_id,
        approver_id=current_user.id,
        decision=data.decision,
        comment=data.comment,
    )
    return result
