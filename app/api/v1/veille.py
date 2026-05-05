"""Routes API pour la veille et la gestion des AO."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.veilleur.agent import VeilleurAgent
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.ao_s2 import AO, AOChunk, Source
from app.models.scoring import ScoringRun
from app.models.ao import User

router = APIRouter(prefix="/veille", tags=["veille"])


def _get_tenant_tier(user: User) -> str:
    return user.tenant.billing_plan or "free" if user.tenant else "free"


@router.get("/sources")
async def list_sources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste toutes les sources de veille actives."""
    stmt = select(Source).where(Source.is_active.is_(True))
    rows = await db.execute(stmt)
    sources = rows.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "label": s.label,
            "country": s.country,
            "scan_frequency_minutes": s.scan_frequency_minutes,
            "last_scan_at": s.last_scan_at.isoformat() if s.last_scan_at else None,
        }
        for s in sources
    ]


@router.post("/scan/{source_id}")
async def trigger_scan(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Declenche manuellement un scan d'une source (admin uniquement)."""
    agent = VeilleurAgent()
    result = await agent.scan_source(source_id, db)
    return result


@router.get("/aos")
async def list_aos(
    status: Optional[str] = Query(None),
    business_line_id: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    verdict: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste paginee des AO avec filtres."""
    filters = []

    if status:
        filters.append(AO.status == status)
    if business_line_id:
        filters.append(AO.business_line_id == business_line_id)
    if country:
        filters.append(AO.country == country)
    if verdict:
        filters.append(AO.scoring_result.isnot(None))

    if search:
        filters.append(
            or_(
                AO.title.ilike(f"%{search}%"),
                AO.description.ilike(f"%{search}%"),
            )
        )

    stmt = select(AO)
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(desc(AO.created_at))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    rows = await db.execute(stmt)
    aos = rows.scalars().all()

    count_stmt = select(func.count(AO.id))
    if filters:
        count_stmt = count_stmt.where(and_(*filters))
    total_row = await db.execute(count_stmt)
    total = total_row.scalar() or 0

    return {
        "items": [
            {
                "id": str(ao.id),
                "title": ao.title,
                "status": ao.status,
                "country": ao.country,
                "estimated_amount": float(ao.estimated_amount) if ao.estimated_amount else None,
                "currency": ao.currency,
                "deadline_date": ao.deadline_date.isoformat() if ao.deadline_date else None,
                "department_code": ao.department_code,
                "buyer_name": ao.buyer_name,
                "scoring_result": ao.scoring_result,
                "business_line_id": str(ao.business_line_id) if ao.business_line_id else None,
                "created_at": ao.created_at.isoformat(),
            }
            for ao in aos
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.get("/aos/{ao_id}")
async def get_ao_detail(
    ao_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne le detail complet d'un AO avec ses scores."""
    stmt = select(AO).where(AO.id == ao_id)
    row = await db.execute(stmt)
    ao = row.scalar_one_or_none()
    if not ao:
        raise HTTPException(status_code=404, detail="AO non trouve")

    stmt_scores = select(ScoringRun).where(ScoringRun.ao_id == ao_id).order_by(
        desc(ScoringRun.created_at)
    )
    rows_scores = await db.execute(stmt_scores)
    scores = rows_scores.scalars().all()

    return {
        "id": str(ao.id),
        "source": {
            "name": ao.source.name if ao.source else None,
            "label": ao.source.label if ao.source else None,
        },
        "external_id": ao.external_id,
        "external_url": ao.external_url,
        "title": ao.title,
        "description": ao.description,
        "status": ao.status,
        "cpv_codes": ao.cpv_codes,
        "country": ao.country,
        "department_code": ao.department_code,
        "department_name": ao.department_name,
        "region": ao.region,
        "city": ao.city,
        "estimated_amount": float(ao.estimated_amount) if ao.estimated_amount else None,
        "currency": ao.currency,
        "publication_date": ao.publication_date.isoformat() if ao.publication_date else None,
        "deadline_date": ao.deadline_date.isoformat() if ao.deadline_date else None,
        "contract_duration_months": ao.contract_duration_months,
        "notice_type": ao.notice_type,
        "buyer_name": ao.buyer_name,
        "contact_email": ao.contact_email,
        "contact_phone": ao.contact_phone,
        "keywords": ao.keywords,
        "scoring_result": ao.scoring_result,
        "business_line_id": str(ao.business_line_id) if ao.business_line_id else None,
        "business_line": {
            "name": ao.business_line.name,
            "color": ao.business_line.color,
        } if ao.business_line else None,
        "scoring_runs": [
            {
                "id": str(s.id),
                "profile": s.profile,
                "score_global": float(s.score_global),
                "verdict": s.verdict,
                "confidence": float(s.confidence),
                "details": s.details,
                "recommendations": s.recommendations,
                "created_at": s.created_at.isoformat(),
            }
            for s in scores
        ],
        "created_at": ao.created_at.isoformat(),
        "updated_at": ao.updated_at.isoformat(),
    }


@router.get("/aos/{ao_id}/chunks")
async def get_ao_chunks(
    ao_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne les chunks vectorises d'un AO (pour debug/analyse)."""
    stmt = select(AOChunk).where(AOChunk.ao_id == ao_id).order_by(AOChunk.chunk_index)
    rows = await db.execute(stmt)
    chunks = rows.scalars().all()
    return {
        "chunks": [
            {
                "id": str(c.id),
                "chunk_index": c.chunk_index,
                "chunk_text": c.chunk_text[:200] + "..." if len(c.chunk_text) > 200 else c.chunk_text,
                "has_embedding": c.embedding is not None,
            }
            for c in chunks
        ]
    }
