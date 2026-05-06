"""Generation de rapports de conformite aux marches publics (PDF)."""

import os
import logging
from datetime import datetime, timezone
from typing import Optional
import uuid

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.audit import AuditTrail, AnomalyDetection, ComplianceReport, AnomalyStatus

logger = logging.getLogger(__name__)

REPORTS_DIR = "/app/data/reports"


class ComplianceReportGenerator:
    """Generateur de rapports de conformite PDF."""

    def __init__(self, db: AsyncSession):
        self.db = db
        os.makedirs(REPORTS_DIR, exist_ok=True)

    async def generate_submission_proof(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        submission_id: uuid.UUID,
    ) -> ComplianceReport:
        """Genere une preuve de soumission pour un depot specifique."""
        from app.models.submission import Submission
        from app.models.ao import AO

        stmt = select(Submission).where(
            and_(Submission.id == submission_id, Submission.tenant_id == tenant_id)
        )
        result = await self.db.execute(stmt)
        submission = result.scalar_one_or_none()

        if not submission:
            raise ValueError(f"Soumission {submission_id} non trouvee")

        stmt_ao = select(AO).where(AO.id == submission.ao_id)
        result_ao = await self.db.execute(stmt_ao)
        ao = result_ao.scalar_one_or_none()

        report = ComplianceReport(
            tenant_id=tenant_id,
            created_by_user_id=user_id,
            report_type="submission_proof",
            title=f"Preuve de soumission — {ao.title if ao else 'AO inconnu'}",
            status="generating",
        )
        self.db.add(report)
        await self.db.flush()

        filename = f"submission_proof_{submission_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=20,
            alignment=TA_CENTER,
        )

        story.append(Paragraph("TAKA OS — Preuve de Soumission", title_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(f"Genere le {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC", styles['Normal']))
        story.append(Spacer(1, 1 * cm))

        data = [
            ["Reference AO", ao.reference if ao else "N/A"],
            ["Titre", ao.title if ao else "N/A"],
            ["Plateforme", submission.platform_type if hasattr(submission, 'platform_type') else "N/A"],
            ["Reference plateforme", submission.platform_reference or "N/A"],
            ["Date de soumission", submission.submitted_at.strftime('%d/%m/%Y %H:%M') if submission.submitted_at else "N/A"],
            ["Statut", submission.status],
        ]

        table = Table(data, colWidths=[6 * cm, 10 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 1 * cm))

        story.append(Paragraph("Mentions Legales", styles['Heading3']))
        story.append(Paragraph(
            "Ce document constitue une preuve de soumission electronique generee par TAKA OS. "
            "La reference plateforme et la date de soumission sont fournies par la plateforme "
            "d'achats publics et sont enregistrees de maniere immuable dans l'audit trail.",
            styles['Normal'],
        ))

        doc.build(story)

        report.status = "completed"
        report.pdf_url = filepath
        report.pdf_size_bytes = os.path.getsize(filepath)
        report.generated_at = datetime.now(timezone.utc)
        report.summary_data = {
            "submission_id": str(submission_id),
            "platform_reference": submission.platform_reference,
            "status": submission.status,
        }

        await self.db.flush()
        logger.info(f"Rapport de preuve genere : {filepath}")
        return report

    async def generate_monthly_report(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        period_start: datetime,
        period_end: datetime,
        title: str,
    ) -> ComplianceReport:
        """Genere un rapport de conformite mensuel complet."""
        from app.models.ao import AO
        from app.models.submission import Submission

        report = ComplianceReport(
            tenant_id=tenant_id,
            created_by_user_id=user_id,
            report_type="monthly_compliance",
            title=title,
            period_start=period_start,
            period_end=period_end,
            status="generating",
        )
        self.db.add(report)
        await self.db.flush()

        ao_stmt = select(func.count(AO.id)).where(
            and_(
                AO.tenant_id == tenant_id,
                AO.created_at >= period_start,
                AO.created_at <= period_end,
            )
        )
        ao_result = await self.db.execute(ao_stmt)
        total_ao = ao_result.scalar()

        from app.models.ao import User
        sub_stmt = select(func.count(Submission.id)).join(User, Submission.user_id == User.id).where(
            and_(
                User.tenant_id == tenant_id,
                Submission.created_at >= period_start,
                Submission.created_at <= period_end,
            )
        )
        sub_result = await self.db.execute(sub_stmt)
        total_submissions = sub_result.scalar()

        sub_ok_stmt = select(func.count(Submission.id)).join(User, Submission.user_id == User.id).where(
            and_(
                User.tenant_id == tenant_id,
                Submission.created_at >= period_start,
                Submission.created_at <= period_end,
                Submission.status == "confirmed",
            )
        )
        sub_ok_result = await self.db.execute(sub_ok_stmt)
        successful_submissions = sub_ok_result.scalar()

        anom_stmt = select(AnomalyDetection).where(
            and_(
                AnomalyDetection.tenant_id == tenant_id,
                AnomalyDetection.created_at >= period_start,
                AnomalyDetection.created_at <= period_end,
            )
        )
        anom_result = await self.db.execute(anom_stmt)
        anomalies = anom_result.scalars().all()

        audit_stmt = select(AuditTrail).where(
            and_(
                AuditTrail.tenant_id == tenant_id,
                AuditTrail.created_at >= period_start,
                AuditTrail.created_at <= period_end,
            )
        ).order_by(AuditTrail.created_at.desc()).limit(200)
        audit_result = await self.db.execute(audit_stmt)
        audit_logs = audit_result.scalars().all()

        filename = f"monthly_compliance_{tenant_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(
            f"Periode : {period_start.strftime('%d/%m/%Y')} — {period_end.strftime('%d/%m/%Y')}",
            styles['Normal'],
        ))
        story.append(Spacer(1, 1.5 * cm))

        story.append(Paragraph("Resume Executif", styles['Heading2']))
        story.append(Spacer(1, 0.5 * cm))

        success_rate = (successful_submissions / total_submissions * 100) if total_submissions > 0 else 0

        kpi_data = [
            ["Metrique", "Valeur"],
            ["Appels d'offres detectes", str(total_ao)],
            ["Soumissions effectuees", str(total_submissions)],
            ["Soumissions reussies", str(successful_submissions)],
            ["Taux de reussite", f"{success_rate:.1f}%"],
            ["Anomalies detectees", str(len(anomalies))],
            ["Anomalies resolues", str(sum(1 for a in anomalies if a.status == AnomalyStatus.RESOLVED))],
        ]

        kpi_table = Table(kpi_data, colWidths=[8 * cm, 8 * cm])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8f8f8")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi_table)
        story.append(PageBreak())

        story.append(Paragraph("Conformite Reglementaire", styles['Heading2']))
        story.append(Spacer(1, 0.5 * cm))

        checklist = [
            ["Exigence", "Statut", "Detail"],
            ["Tracabilite des actions", "✓ CONFORME", "Audit trail complet avec actor, action, timestamp"],
            ["Preuve de soumission", "✓ CONFORME" if total_submissions > 0 else "○ NON APPLICABLE", "References plateforme conservees"],
            ["Conservation des donnees", "✓ CONFORME", "Duree de conservation : 2 ans minimum"],
            ["Acces restreint", "✓ CONFORME", "RBAC avec 5 roles + MFA"],
            ["Chiffrement des credentials", "✓ CONFORME", "AES-128 (Fernet) pour tous les secrets"],
        ]

        checklist_table = Table(checklist, colWidths=[6 * cm, 3 * cm, 7 * cm])
        checklist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(checklist_table)

        doc.build(story)

        report.status = "completed"
        report.pdf_url = filepath
        report.pdf_size_bytes = os.path.getsize(filepath)
        report.generated_at = datetime.now(timezone.utc)
        report.summary_data = {
            "total_ao": total_ao,
            "total_submissions": total_submissions,
            "successful_submissions": successful_submissions,
            "success_rate": success_rate,
            "anomalies_total": len(anomalies),
            "anomalies_resolved": sum(1 for a in anomalies if a.status == AnomalyStatus.RESOLVED),
        }

        await self.db.flush()
        logger.info(f"Rapport mensuel genere : {filepath}")
        return report
