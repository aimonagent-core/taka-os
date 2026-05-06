"""Export CSV des AO et donnees associees."""

import csv
import io
import logging
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.ao_s2 import AO, Source

logger = logging.getLogger(__name__)


class CSVExporter:
    """Exporteur CSV pour TAKA OS."""

    AO_HEADERS = [
        "id", "title", "description", "reference", "cpv_codes",
        "status", "deadline", "estimated_value", "currency",
        "location", "buyer_name", "source_name", "created_at",
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_aos(
        self,
        tenant_id: uuid.UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        source_id: Optional[uuid.UUID] = None,
    ) -> str:
        """Exporte les AO en CSV."""
        conditions = [AO.tenant_id == tenant_id]
        if date_from:
            conditions.append(AO.created_at >= date_from)
        if date_to:
            conditions.append(AO.created_at <= date_to)
        if status:
            conditions.append(AO.status == status)
        if source_id:
            conditions.append(AO.source_id == source_id)

        stmt = select(AO).where(and_(*conditions)).order_by(AO.created_at.desc())
        result = await self.db.execute(stmt)
        aos = result.scalars().all()

        # Preload sources for mapping
        source_ids = {ao.source_id for ao in aos if ao.source_id}
        source_map = {}
        if source_ids:
            src_stmt = select(Source).where(Source.id.in_(source_ids))
            src_result = await self.db.execute(src_stmt)
            for src in src_result.scalars().all():
                source_map[src.id] = src.name

        output = io.StringIO()
        output.write('\ufeff')
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(self.AO_HEADERS)

        for ao in aos:
            raw = ao.raw_data or {}
            row = [
                str(ao.id),
                ao.title or "",
                ao.description or "",
                ao.external_id or "",
                "|".join(ao.cpv_codes) if ao.cpv_codes else "",
                ao.status or "",
                ao.deadline_date.isoformat() if ao.deadline_date else "",
                str(ao.estimated_amount) if ao.estimated_amount else "",
                ao.currency or "EUR",
                ao.city or "",
                ao.buyer_name or "",
                source_map.get(ao.source_id, ""),
                ao.created_at.isoformat() if ao.created_at else "",
            ]
            writer.writerow(row)

        return output.getvalue()
