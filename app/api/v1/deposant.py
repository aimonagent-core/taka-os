"""Routes API pour l'Agent Déposant."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.deposant.submitter import DeposantSubmitter
from app.agents.deposant.tracker import SubmissionTracker
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.models.submission import Submission, SubmissionPlatform

router = APIRouter(prefix="/deposant", tags=["deposant"])


@router.get("/platforms")
async def list_platforms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les plateformes de dépôt configurées."""
    stmt = select(SubmissionPlatform).where(
        SubmissionPlatform.tenant_id == current_user.tenant_id,
        SubmissionPlatform.is_active == True,
    )
    rows = await db.execute(stmt)
    platforms = rows.scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "platform_type": p.platform_type,
            "base_url": p.base_url,
            "is_mock": p.is_mock,
        }
        for p in platforms
    ]


@router.post("/submit/{response_id}/{platform_id}")
async def submit_response(
    response_id: str,
    platform_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soumet une réponse approuvée sur une plateforme."""
    submitter = DeposantSubmitter()
    try:
        submission = await submitter.submit(
            generated_response_id=response_id,
            platform_id=platform_id,
            user_id=str(current_user.id),
            db=db,
            tenant_id=str(current_user.tenant_id),
        )
        return {
            "id": str(submission.id),
            "status": submission.status,
            "platform_reference": submission.platform_reference,
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "error": submission.error_message,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/retry/{submission_id}")
async def retry_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Relance une soumission en échec."""
    submitter = DeposantSubmitter()
    try:
        submission = await submitter.retry(
            submission_id=submission_id,
            user_id=str(current_user.id),
            db=db,
            tenant_id=str(current_user.tenant_id),
        )
        return {
            "id": str(submission.id),
            "status": submission.status,
            "retry_count": submission.retry_count,
            "platform_reference": submission.platform_reference,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/submissions")
async def list_submissions(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les soumissions du tenant."""
    stmt = select(Submission).where(Submission.user_id == current_user.id)
    if status:
        stmt = stmt.where(Submission.status == status)
    stmt = stmt.order_by(desc(Submission.created_at))
    rows = await db.execute(stmt)
    subs = rows.scalars().all()
    return [
        {
            "id": str(s.id),
            "response_id": str(s.generated_response_id),
            "platform_id": str(s.platform_id),
            "status": s.status,
            "platform_reference": s.platform_reference,
            "retry_count": s.retry_count,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            "created_at": s.created_at.isoformat(),
        }
        for s in subs
    ]


@router.post("/track")
async def track_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Vérifie les statuts de toutes les soumissions en attente."""
    tracker = SubmissionTracker()
    updates = await tracker.check_all_pending(db)
    return {"updated": len(updates), "details": updates}
