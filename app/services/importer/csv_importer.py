"""Import CSV bulk d'AO et de contacts."""

import csv
import io
import logging
import uuid as uuid_mod
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.ao_s2 import AO, Source

logger = logging.getLogger(__name__)


class CSVImporter:
    """Importeur CSV pour TAKA OS."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_aos_from_csv(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        csv_content: str,
        source_id: Optional[uuid.UUID] = None,
    ) -> dict:
        """Importe des AO depuis un CSV.

        Format attendu :
          title,description,reference,cpv_codes,deadline,estimated_value,currency,location,source_name
        """
        reader = csv.DictReader(io.StringIO(csv_content))

        imported = 0
        errors = 0
        details = []
        row_num = 1

        # Trouver une source par defaut si non fournie
        if not source_id:
            src_stmt = select(Source).where(
                and_(Source.tenant_id == tenant_id, Source.is_active == True)
            ).limit(1)
            src_result = await self.db.execute(src_stmt)
            first_source = src_result.scalar_one_or_none()
            source_id = first_source.id if first_source else None

        for row in reader:
            row_num += 1

            try:
                title = row.get("title", "").strip()
                if not title:
                    raise ValueError("title est obligatoire")

                deadline = self._parse_date(row.get("deadline", ""))

                cpv_raw = row.get("cpv_codes", "")
                cpv_codes = [c.strip() for c in cpv_raw.replace("|", ",").split(",") if c.strip()]

                value_str = row.get("estimated_value", "").replace(" ", "").replace("€", "").replace(",", ".")
                estimated_amount = float(value_str) if value_str else None

                ao = AO(
                    tenant_id=tenant_id,
                    source_id=source_id,
                    external_id=row.get("reference", f"IMPORT-{uuid_mod.uuid4().hex[:8]}")[:255],
                    title=title[:500],
                    description=row.get("description", ""),
                    status="imported",
                    cpv_codes=cpv_codes,
                    deadline_date=deadline,
                    estimated_amount=estimated_amount,
                    currency=row.get("currency", "EUR"),
                    city=row.get("location", ""),
                    raw_data={
                        "imported_by": str(user_id),
                        "import_row": row_num,
                    },
                )
                self.db.add(ao)
                imported += 1
                details.append({"row": row_num, "status": "success", "reference": ao.external_id})

            except Exception as e:
                errors += 1
                details.append({"row": row_num, "status": "error", "message": str(e)})
                logger.warning(f"Import row {row_num} failed: {e}")

        await self.db.flush()

        return {
            "imported": imported,
            "errors": errors,
            "total": row_num - 1,
            "details": details,
        }

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date dans plusieurs formats."""
        if not date_str:
            return None

        formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y %H:%M"]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        return None
