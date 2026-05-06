"""Moteur de workflow d'approbation.

Gere le cycle de vie complet des demandes d'approbation :
  - Creation (quand un trigger se produit)
  - Routage vers l'approbateur de l'etape courante
  - Approbation / Rejet / Delegation
  - Passage a l'etape suivante (ou finalisation)
  - Audit trail
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.workflow import (
    ApprovalWorkflow, ApprovalStep, ApprovalRequest,
    ApprovalDecision, WorkflowTrigger,
)
from app.models.ao import User
from app.services.notifications.in_app import NotificationService

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Moteur de workflow d'approbation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notif_service = NotificationService(db)

    async def trigger_workflow(
        self,
        tenant_id: uuid.UUID,
        trigger: WorkflowTrigger | str,
        requester_id: uuid.UUID,
        ao_id: Optional[uuid.UUID] = None,
        response_id: Optional[uuid.UUID] = None,
        comment: Optional[str] = None,
    ) -> Optional[ApprovalRequest]:
        """Declenche un workflow d'approbation."""
        if isinstance(trigger, WorkflowTrigger):
            trigger = trigger.value

        stmt = select(ApprovalWorkflow).where(
            and_(
                ApprovalWorkflow.tenant_id == tenant_id,
                ApprovalWorkflow.trigger == trigger,
                ApprovalWorkflow.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        workflows = result.scalars().all()

        if not workflows:
            logger.info(f"Aucun workflow pour trigger {trigger}")
            return None

        workflow = workflows[0]

        steps_stmt = select(ApprovalStep).where(
            ApprovalStep.workflow_id == workflow.id
        ).order_by(ApprovalStep.step_order)
        steps_result = await self.db.execute(steps_stmt)
        steps = steps_result.scalars().all()

        if not steps:
            logger.warning(f"Workflow {workflow.id} sans etapes")
            return None

        request = ApprovalRequest(
            tenant_id=tenant_id,
            workflow_id=workflow.id,
            requester_id=requester_id,
            ao_id=ao_id,
            response_id=response_id,
            current_step_number=1,
            status="pending",
            comment=comment,
        )
        self.db.add(request)
        await self.db.flush()

        first_step = steps[0]
        approvers = await self._resolve_approvers(first_step, requester_id, tenant_id)
        for approver_id in approvers:
            await self.notif_service.notify_approval_required(
                tenant_id=tenant_id,
                recipient_id=approver_id,
                request_id=request.id,
                step_name=first_step.name,
            )

        logger.info(f"Workflow declenche : {request.id}, step 1/{len(steps)}")
        return request

    async def make_decision(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        decision: str,
        comment: Optional[str] = None,
    ) -> dict:
        """Prend une decision sur une demande d'approbation."""
        stmt = select(ApprovalRequest).where(ApprovalRequest.id == request_id)
        result = await self.db.execute(stmt)
        request = result.scalar_one_or_none()

        if not request or request.status != "pending":
            return {"status": "error", "message": "Demande non trouvee ou non pending"}

        step_stmt = select(ApprovalStep).where(
            and_(
                ApprovalStep.workflow_id == request.workflow_id,
                ApprovalStep.step_order == request.current_step_number,
            )
        )
        step_result = await self.db.execute(step_stmt)
        current_step = step_result.scalar_one_or_none()

        if not current_step:
            return {"status": "error", "message": "Etape non trouvee"}

        approval_decision = ApprovalDecision(
            request_id=request_id,
            step_id=current_step.id,
            approver_id=approver_id,
            decision=decision,
            comment=comment,
        )
        self.db.add(approval_decision)

        if decision == "rejected":
            request.status = "rejected"
            await self.db.flush()

            await self.notif_service.notify_approval_decided(
                tenant_id=request.tenant_id,
                recipient_id=request.requester_id,
                request_id=request.id,
                decision="rejected",
            )

            return {"status": "rejected", "request_id": str(request_id)}

        next_steps_stmt = select(ApprovalStep).where(
            ApprovalStep.workflow_id == request.workflow_id
        ).order_by(ApprovalStep.step_order)
        next_result = await self.db.execute(next_steps_stmt)
        all_steps = next_result.scalars().all()

        if request.current_step_number >= len(all_steps):
            request.status = "approved"
            await self.db.flush()

            await self.notif_service.notify_approval_decided(
                tenant_id=request.tenant_id,
                recipient_id=request.requester_id,
                request_id=request.id,
                decision="approved",
            )

            return {"status": "approved", "request_id": str(request_id)}

        request.current_step_number += 1
        await self.db.flush()

        next_step = all_steps[request.current_step_number - 1]
        approvers = await self._resolve_approvers(next_step, request.requester_id, request.tenant_id)
        for next_approver_id in approvers:
            await self.notif_service.notify_approval_required(
                tenant_id=request.tenant_id,
                recipient_id=next_approver_id,
                request_id=request.id,
                step_name=next_step.name,
            )

        return {"status": "next_step", "request_id": str(request_id), "step": request.current_step_number}

    async def _resolve_approvers(
        self,
        step: ApprovalStep,
        requester_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        """Resout les approbateurs pour une etape."""
        approvers = []

        if step.step_type == "specific_user" and step.specific_user_id:
            approvers.append(step.specific_user_id)

        elif step.step_type == "tenant_admin":
            stmt = select(User).where(
                and_(
                    User.tenant_id == tenant_id,
                    User.role == "tenant_admin",
                )
            )
            result = await self.db.execute(stmt)
            admins = result.scalars().all()
            approvers.extend([a.id for a in admins])

        elif step.step_type == "any_manager":
            stmt = select(User).where(
                and_(
                    User.tenant_id == tenant_id,
                    User.role.in_(["tenant_manager", "tenant_admin"]),
                )
            )
            result = await self.db.execute(stmt)
            managers = result.scalars().all()
            approvers.extend([m.id for m in managers])

        elif step.step_type == "requester_manager":
            stmt = select(User).where(
                and_(
                    User.tenant_id == tenant_id,
                    User.role.in_(["tenant_manager", "tenant_admin"]),
                )
            )
            result = await self.db.execute(stmt)
            managers = result.scalars().all()
            approvers.extend([m.id for m in managers])

        return approvers

    async def get_pending_requests(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> list[ApprovalRequest]:
        """Liste les demandes en attente pour un approbateur."""
        stmt = select(ApprovalRequest).where(
            and_(
                ApprovalRequest.tenant_id == tenant_id,
                ApprovalRequest.status == "pending",
            )
        ).order_by(ApprovalRequest.created_at.desc())

        result = await self.db.execute(stmt)
        return result.scalars().all()
