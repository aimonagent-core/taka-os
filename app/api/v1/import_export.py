"""Routes pour l'import/export de donnees.

Export :
  GET  /import-export/export/aos/csv    → Export CSV des AO
  GET  /import-export/export/aos/excel  → Export Excel multi-onglets

Import :
  POST /import-export/import/aos/csv    → Import CSV d'AO
"""

from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.services.export.csv_exporter import CSVExporter
from app.services.export.excel_exporter import ExcelExporter
from app.services.importer.csv_importer import CSVImporter

router = APIRouter(prefix="/import-export", tags=["import-export"])


@router.get("/export/aos/csv")
async def export_aos_csv(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Export CSV des AO."""
    exporter = CSVExporter(db)
    csv_data = await exporter.export_aos(
        tenant_id=current_user.tenant_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
    )

    from fastapi.responses import PlainTextResponse
    filename = f"taka_ao_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return PlainTextResponse(
        csv_data,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/aos/excel")
async def export_aos_excel(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Export Excel multi-onglets."""
    exporter = ExcelExporter(db)
    excel_bytes = await exporter.export_full_report(
        tenant_id=current_user.tenant_id,
        date_from=date_from,
        date_to=date_to,
    )

    from fastapi.responses import Response
    filename = f"taka_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return Response(
        excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/import/aos/csv")
async def import_aos_csv(
    file: UploadFile = File(...),
    source_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(["tenant_admin", "tenant_manager"])),
):
    """Import CSV d'AO en bulk."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Fichier CSV requis (.csv)")

    content = await file.read()
    try:
        csv_text = content.decode('utf-8')
    except UnicodeDecodeError:
        csv_text = content.decode('iso-8859-1')

    importer = CSVImporter(db)
    result = await importer.import_aos_from_csv(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        csv_content=csv_text,
        source_id=source_id,
    )

    return result
