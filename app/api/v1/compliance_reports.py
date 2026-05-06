"""API endpoints pour les rapports de conformite."""

from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.models.audit import ComplianceReport, AnomalyDetection, AnomalyStatus
from app.agents.auditor import AnomalyDetector
from app.services.reports.compliance import ComplianceReportGenerator

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.post("/reports")
async def create_compliance_report(
    report_type: str,
    title: str,
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    submission_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Genere un rapport de conformite."""
    generator = ComplianceReportGenerator(db)

    if report_type == "submission_proof":
        if not submission_id:
            raise HTTPException(status_code=400, detail="submission_id requis pour type 'submission_proof'")
        report = await generator.generate_submission_proof(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            submission_id=submission_id,
        )
    elif report_type == "monthly_compliance":
        if not period_start or not period_end:
            raise HTTPException(status_code=400, detail="period_start et period_end requis")
        report = await generator.generate_monthly_report(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            period_start=period_start,
            period_end=period_end,
            title=title,
        )
    else:
        raise HTTPException(status_code=400, detail=f"Type de rapport inconnu : {report_type}")

    return {
        "id": str(report.id),
        "status": report.status,
        "title": report.title,
        "pdf_url": report.pdf_url,
        "pdf_size_bytes": report.pdf_size_bytes,
        "summary_data": report.summary_data,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
    }


@router.get("/reports")
async def list_compliance_reports(
    report_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les rapports de conformite du tenant."""
    conditions = [ComplianceReport.tenant_id == current_user.tenant_id]
    if report_type:
        conditions.append(ComplianceReport.report_type == report_type)

    stmt = (
        select(ComplianceReport)
        .where(and_(*conditions))
        .order_by(ComplianceReport.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    reports = result.scalars().all()

    return {
        "items": [
            {
                "id": str(r.id),
                "report_type": r.report_type,
                "title": r.title,
                "status": r.status,
                "pdf_url": r.pdf_url,
                "pdf_size_bytes": r.pdf_size_bytes,
                "summary_data": r.summary_data,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reports
        ],
    }


@router.get("/reports/{report_id}")
async def get_compliance_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detail d'un rapport de conformite."""
    stmt = select(ComplianceReport).where(
        and_(
            ComplianceReport.id == report_id,
            ComplianceReport.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouve")

    return {
        "id": str(report.id),
        "report_type": report.report_type,
        "title": report.title,
        "status": report.status,
        "period_start": report.period_start.isoformat() if report.period_start else None,
        "period_end": report.period_end.isoformat() if report.period_end else None,
        "pdf_url": report.pdf_url,
        "pdf_size_bytes": report.pdf_size_bytes,
        "summary_data": report.summary_data,
        "regulation_framework": report.regulation_framework,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
        "error_message": report.error_message,
    }


@router.get("/reports/{report_id}/download")
async def download_compliance_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Telecharge le PDF d'un rapport."""
    stmt = select(ComplianceReport).where(
        and_(
            ComplianceReport.id == report_id,
            ComplianceReport.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report or not report.pdf_url:
        raise HTTPException(status_code=404, detail="PDF non trouve")

    if not os.path.exists(report.pdf_url):
        raise HTTPException(status_code=404, detail="Fichier PDF inexistant sur le serveur")

    return FileResponse(
        report.pdf_url,
        media_type="application/pdf",
        filename=f"taka_compliance_{report_id}.pdf",
    )


@router.post("/reports/{report_id}/anomalies")
async def run_anomaly_checks(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute toutes les verifications d'anomalies."""
    detector = AnomalyDetector(db)
    anomalies = await detector.run_all_checks(current_user.tenant_id)

    return {
        "anomalies_detected": len(anomalies),
        "anomalies": [
            {
                "id": str(a.id),
                "type": a.anomaly_type,
                "severity": a.severity.value if hasattr(a.severity, 'value') else str(a.severity),
                "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
                "title": a.title,
                "description": a.description,
                "ai_analysis": a.ai_analysis,
                "ai_recommendation": a.ai_recommendation,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in anomalies
        ],
    }


@router.get("/anomalies")
async def list_anomalies(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les anomalies detectees."""
    conditions = [AnomalyDetection.tenant_id == current_user.tenant_id]
    if status:
        conditions.append(AnomalyDetection.status == status)
    if severity:
        conditions.append(AnomalyDetection.severity == severity)

    stmt = (
        select(AnomalyDetection)
        .where(and_(*conditions))
        .order_by(AnomalyDetection.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    anomalies = result.scalars().all()

    return {
        "items": [
            {
                "id": str(a.id),
                "type": a.anomaly_type,
                "severity": a.severity.value if hasattr(a.severity, 'value') else str(a.severity),
                "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
                "title": a.title,
                "description": a.description,
                "ai_analysis": a.ai_analysis,
                "ai_recommendation": a.ai_recommendation,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in anomalies
        ],
    }


@router.post("/anomalies/{anomaly_id}/resolve")
async def resolve_anomaly(
    anomaly_id: uuid.UUID,
    resolution_note: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marque une anomalie comme resolue."""
    stmt = select(AnomalyDetection).where(
        and_(
            AnomalyDetection.id == anomaly_id,
            AnomalyDetection.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    anomaly = result.scalar_one_or_none()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomalie non trouvee")

    anomaly.status = AnomalyStatus.RESOLVED
    anomaly.resolved_by_user_id = current_user.id
    anomaly.resolved_at = datetime.now(timezone.utc)
    anomaly.resolution_note = resolution_note

    await db.flush()
    return {"status": "resolved", "anomaly_id": str(anomaly_id)}
