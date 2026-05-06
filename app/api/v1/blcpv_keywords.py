"""Routes API pour l'autocomplete des CPV (BLCPVKeyword)."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.models.business_line import BLCPVKeyword

router = APIRouter(prefix="/blcpv-keywords", tags=["CPV Keywords"])


@router.get("/search")
async def search_blcpv_keywords(
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recherche autocomplete sur les CPV (code + label).

    Ex: ?search=electricite&limit=10
    """
    stmt = select(BLCPVKeyword)

    if search:
        search_lower = f"%{search.lower()}%"
        stmt = stmt.where(
            BLCPVKeyword.cpv_code.ilike(search_lower)
            | BLCPVKeyword.label.ilike(search_lower)
        )

    stmt = stmt.order_by(BLCPVKeyword.cpv_code).limit(limit)
    rows = await db.execute(stmt)
    keywords = rows.scalars().all()

    return {
        "items": [
            {
                "id": str(k.id),
                "cpv_code": k.cpv_code,
                "label": k.label,
                "weight": float(k.weight),
            }
            for k in keywords
        ],
        "count": len(keywords),
    }
