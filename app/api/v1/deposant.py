"""
Router API v1 — Endpoints pour le deposant (soumission des dossiers).

VERSION v0.10.0 : Fallback explicite — le mock est signale dans la reponse API.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.deposant.submitter import DeposantSubmitter, SubmissionResult
from app.agents.deposant.tracker import SubmissionTracker
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.models.submission import Submission, SubmissionPlatform
from app.models.platform_connector import PlatformConnector
from app.services.deposant.connector_factory import get_connector as get_platform_connector
from app.services.deposant.connectors.base_connector import BasePlatformConnector
from app.services.deposant.connectors.mock_connector import MockConnector

router = APIRouter(prefix="/deposant", tags=["deposant"])


def _format_submission_response(submission: Submission) -> dict[str, Any]:
    """
    Formate une Submission en reponse API.
    SI c'est un mock, la reponse contient un warning explicite.
    """
    response: dict[str, Any] = {
        "id": str(submission.id),
        "success": submission.status in ("submitted", "pending"),
        "status": submission.status,
        "platform_reference": submission.platform_reference,
        "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
        "error": submission.error_message,
    }

    # Recuperer les infos mock depuis platform_response
    platform_response = submission.platform_response or {}
    is_mock = platform_response.get("is_mock", False)

    # Si mock — AJOUTER LES WARNINGS EXPLICITES
    if is_mock:
        response["is_mock"] = True
        response["warning"] = platform_response.get("warning") or (
            "Ce depot est une SIMULATION. Aucun dossier reel n'a ete soumis."
        )
        response["requires_action"] = platform_response.get("requires_action") or (
            "Configurez un connecteur dans Parametres > Plateformes"
        )
        response["_mock_notice"] = (
            "[ATTENTION] Cette soumission est une simulation locale. "
            "Aucun dossier n'a ete transmis a la plateforme reelle. "
            "Article L121-1 Code de la consommation — obligation d'information."
        )
    else:
        response["is_mock"] = False

    return response


@router.get("/platforms")
async def list_platforms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les plateformes de depot configurees."""
    stmt = select(SubmissionPlatform).where(
        SubmissionPlatform.tenant_id == current_user.tenant_id,
        SubmissionPlatform.is_active == True,
    )
    rows = await db.execute(stmt)
    platforms = rows.scalars().all()

    submitter = DeposantSubmitter()
    platforms_status = await submitter.get_platforms_status(
        db, current_user.tenant_id
    )

    return {
        "platforms": [
            {
                "id": str(p.id),
                "name": p.name,
                "platform_type": p.platform_type,
                "base_url": p.base_url,
                "is_mock": p.is_mock,
                "configured": platforms_status.get(p.platform_type, {}).get("configured", False),
                "has_real_connector": platforms_status.get(p.platform_type, {}).get("has_real_connector", False),
            }
            for p in platforms
        ],
        "configured_count": sum(1 for p in platforms_status.values() if p["configured"]),
        "total_count": len(platforms_status),
        "force_real_submission": submitter.FORCE_REAL_SUBMISSION
        if hasattr(submitter, "FORCE_REAL_SUBMISSION")
        else False,
    }


@router.post("/submit/{response_id}/{platform_id}")
async def submit_response(
    response_id: str,
    platform_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soumet une reponse approuvee sur une plateforme."""
    submitter = DeposantSubmitter()
    try:
        submission = await submitter.submit(
            generated_response_id=response_id,
            platform_id=platform_id,
            user_id=str(current_user.id),
            db=db,
            tenant_id=str(current_user.tenant_id),
        )
        return _format_submission_response(submission)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/retry/{submission_id}")
async def retry_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Relance une soumission en echec."""
    submitter = DeposantSubmitter()
    try:
        submission = await submitter.retry(
            submission_id=submission_id,
            user_id=str(current_user.id),
            db=db,
            tenant_id=str(current_user.tenant_id),
        )
        return _format_submission_response(submission)
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
            "is_mock": (s.platform_response or {}).get("is_mock", False),
            "warning": (s.platform_response or {}).get("warning"),
        }
        for s in subs
    ]


@router.post("/track")
async def track_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verifie les statuts de toutes les soumissions en attente."""
    tracker = SubmissionTracker()
    updates = await tracker.check_all_pending(db)
    return {"updated": len(updates), "details": updates}


@router.get("/submissions/{submission_id}/status")
async def check_submission_status(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Verifie le statut d'une soumission precedente."""
    submitter = DeposantSubmitter()
    try:
        result = await submitter.check_status(submission_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Sprint 12 Module 3 — Endpoints connecteurs generiques
# ============================================================================

@router.post("/connectors/test")
async def test_connector_adhoc(
    body: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Teste une configuration de connecteur sans la sauvegarder.

    Body attendu:
    {
        "platform_type": "email_direct",
        "config": {"smtp_host": "smtp.example.com", ...}
    }
    """
    platform_type = body.get("platform_type")
    config = body.get("config", {})
    if not platform_type:
        raise HTTPException(status_code=422, detail="platform_type requis")

    # Instancie le connecteur directement sans passer par la DB
    from app.services.deposant.connector_factory import _CONNECTOR_MAP
    connector_class = _CONNECTOR_MAP.get(platform_type, MockConnector)
    connector: BasePlatformConnector = connector_class(config)

    try:
        ok = await connector.test_connection()
        return {
            "ok": ok,
            "platform_type": platform_type,
            "message": "Connexion OK" if ok else "Echec de connexion",
        }
    except Exception as exc:
        logger = logging.getLogger(__name__)
        logger.warning("[API] Test connecteur adhoc echoue: %s", exc)
        return {
            "ok": False,
            "platform_type": platform_type,
            "message": f"Erreur: {exc}",
        }


@router.post("/connectors/{connector_id}/test")
async def test_existing_connector(
    connector_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Teste un connecteur existant en base."""
    from sqlalchemy import select
    stmt = select(PlatformConnector).where(
        PlatformConnector.id == connector_id,
        PlatformConnector.tenant_id == current_user.tenant_id,
    )
    row = await db.execute(stmt)
    pc = row.scalar_one_or_none()
    if not pc:
        raise HTTPException(status_code=404, detail="Connecteur introuvable")

    connector = await get_platform_connector(
        tenant_id=current_user.tenant_id,
        platform_type=pc.platform_type,
        session=db,
    )

    try:
        ok = await connector.test_connection()
        pc.test_status = "ok" if ok else "error"
        pc.last_tested_at = datetime.now(timezone.utc)
        await db.commit()
        return {
            "ok": ok,
            "connector_id": connector_id,
            "platform_type": pc.platform_type,
            "test_status": pc.test_status,
            "last_tested_at": pc.last_tested_at.isoformat() if pc.last_tested_at else None,
        }
    except Exception as exc:
        pc.test_status = "error"
        pc.last_tested_at = datetime.now(timezone.utc)
        await db.commit()
        logging.getLogger(__name__).warning("[API] Test connecteur %s echoue: %s", connector_id, exc)
        return {
            "ok": False,
            "connector_id": connector_id,
            "platform_type": pc.platform_type,
            "test_status": "error",
            "message": str(exc),
        }
