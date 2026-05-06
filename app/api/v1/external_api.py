"""API publique externe — endpoints pour les integrations Enterprise.

Authentification : X-API-Key header (pas de JWT)
Rate limiting : par cle API (Redis)
Permissions : verifiees selon les scopes de la cle

Routes publiques :
  GET  /external/v1/aos            → Liste des AO (filtrable)
  GET  /external/v1/aos/{id}       → Detail d'un AO
  GET  /external/v1/scoring/{ao_id} → Score d'un AO
  POST /external/v1/aos/{id}/status → Marquer gagne/perdu

Routes internes (gestion des cles) :
  GET  /api/v1/api-keys            → Liste des cles
  POST /api/v1/api-keys            → Creer une cle
  POST /api/v1/api-keys/{id}/revoke → Revoker une cle
"""

from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.core.rate_limit_api import ApiKeyRateLimiter
from app.services.api_keys.manager import ExternalApiKeyManager
from app.models.api_publique import ExternalApiKey

# ── Router public (X-API-Key) ──
public_router = APIRouter(prefix="/external/v1", tags=["external-api"])

# ── Router interne (JWT) ──
mgmt_router = APIRouter(prefix="/api-keys", tags=["api-keys"])

_rate_limiter = ApiKeyRateLimiter()


async def verify_external_api_key(
    x_api_key: str = Header(..., description="Cle API au format tak_live_xxx"),
    db: AsyncSession = Depends(get_db),
) -> ExternalApiKey:
    """Dependency : verifie la cle API et le rate limit."""
    manager = ExternalApiKeyManager(db)
    key_obj = await manager.verify_key(x_api_key)

    if not key_obj:
        raise HTTPException(status_code=401, detail="Cle API invalide ou expiree")

    allowed, remaining, reset_at = await _rate_limiter.check_rate_limit(
        key_hash=key_obj.key_hash,
        limit_per_minute=key_obj.rate_limit_per_minute,
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(key_obj.rate_limit_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_at),
            },
        )

    return key_obj


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES PUBLIQUES
# ═══════════════════════════════════════════════════════════════════════════════

@public_router.get("/aos")
async def list_aos_external(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    api_key: ExternalApiKey = Depends(verify_external_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Liste les AO du tenant (acces API externe)."""
    if "ao:read" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Permission 'ao:read' requise")

    from app.models.ao import AO
    from sqlalchemy import select, and_

    conditions = [AO.tenant_id == api_key.tenant_id]
    if status:
        conditions.append(AO.status == status)

    stmt = (
        select(AO)
        .where(and_(*conditions))
        .order_by(AO.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    aos = result.scalars().all()

    return {
        "items": [
            {
                "id": str(ao.id),
                "title": ao.title,
                "reference": ao.reference,
                "status": ao.status,
                "cpv_codes": ao.cpv_codes,
                "deadline": ao.deadline.isoformat() if ao.deadline else None,
                "estimated_value": ao.estimated_value,
                "created_at": ao.created_at.isoformat() if ao.created_at else None,
            }
            for ao in aos
        ],
        "limit": limit,
        "offset": offset,
    }


@public_router.get("/aos/{ao_id}")
async def get_ao_external(
    ao_id: uuid.UUID,
    api_key: ExternalApiKey = Depends(verify_external_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Detail d'un AO."""
    if "ao:read" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Permission 'ao:read' requise")

    from app.models.ao import AO
    from sqlalchemy import select, and_

    stmt = select(AO).where(
        and_(AO.id == ao_id, AO.tenant_id == api_key.tenant_id)
    )
    result = await db.execute(stmt)
    ao = result.scalar_one_or_none()

    if not ao:
        raise HTTPException(status_code=404, detail="AO non trouve")

    return {
        "id": str(ao.id),
        "title": ao.title,
        "description": ao.description,
        "reference": ao.reference,
        "status": ao.status,
        "cpv_codes": ao.cpv_codes,
        "deadline": ao.deadline.isoformat() if ao.deadline else None,
        "estimated_value": ao.estimated_value,
        "location": ao.location,
        "created_at": ao.created_at.isoformat() if ao.created_at else None,
    }


@public_router.get("/scoring/{ao_id}")
async def get_scoring_external(
    ao_id: uuid.UUID,
    api_key: ExternalApiKey = Depends(verify_external_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Score d'un AO."""
    if "scoring:read" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Permission 'scoring:read' requise")

    from app.models.scoring import ScoringRun
    from sqlalchemy import select, and_

    stmt = select(ScoringRun).where(
        and_(
            ScoringRun.ao_id == ao_id,
            ScoringRun.tenant_id == api_key.tenant_id,
        )
    ).order_by(ScoringRun.created_at.desc()).limit(1)

    result = await db.execute(stmt)
    scoring = result.scalar_one_or_none()

    if not scoring:
        raise HTTPException(status_code=404, detail="Score non trouve")

    return {
        "ao_id": str(ao_id),
        "score_global": float(scoring.score_global) if scoring.score_global else None,
        "dimensions": scoring.dimensions,
        "created_at": scoring.created_at.isoformat() if scoring.created_at else None,
    }


@public_router.post("/aos/{ao_id}/status")
async def update_ao_status_external(
    ao_id: uuid.UUID,
    status: str,
    api_key: ExternalApiKey = Depends(verify_external_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Marque un AO comme gagne ou perdu."""
    if "ao:write" not in api_key.permissions:
        raise HTTPException(status_code=403, detail="Permission 'ao:write' requise")

    if status not in ("won", "lost"):
        raise HTTPException(status_code=400, detail="Status doit etre 'won' ou 'lost'")

    from app.models.ao import AO
    from sqlalchemy import select, and_

    stmt = select(AO).where(
        and_(AO.id == ao_id, AO.tenant_id == api_key.tenant_id)
    )
    result = await db.execute(stmt)
    ao = result.scalar_one_or_none()

    if not ao:
        raise HTTPException(status_code=404, detail="AO non trouve")

    ao.status = status
    await db.flush()

    return {"id": str(ao_id), "status": status}


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES INTERNES (gestion des cles API)
# ═══════════════════════════════════════════════════════════════════════════════

from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    name: str
    permissions: list[str]
    is_test: bool = False
    rate_limit: int = 100
    expires_days: Optional[int] = None


@mgmt_router.get("")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les cles API du tenant."""
    manager = ExternalApiKeyManager(db)
    keys = await manager.list_keys(current_user.tenant_id)
    return {
        "keys": [
            {
                "id": str(k.id),
                "name": k.key_name,
                "prefix": k.key_prefix,
                "permissions": k.permissions,
                "rate_limit": k.rate_limit_per_minute,
                "is_active": k.is_active,
                "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                "total_requests": k.total_requests,
                "created_at": k.created_at.isoformat() if k.created_at else None,
            }
            for k in keys
        ],
    }


@mgmt_router.post("")
async def create_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cree une nouvelle cle API."""
    manager = ExternalApiKeyManager(db)
    key, api_key_obj = await manager.create_key(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        name=data.name,
        permissions=data.permissions,
        is_test=data.is_test,
        rate_limit=data.rate_limit,
        expires_days=data.expires_days,
    )
    await db.commit()
    return {
        "key": key,
        "id": str(api_key_obj.id),
        "name": api_key_obj.key_name,
        "prefix": api_key_obj.key_prefix,
    }


@mgmt_router.post("/{key_id}/revoke")
async def revoke_api_key(
    key_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke une cle API."""
    manager = ExternalApiKeyManager(db)
    ok = await manager.revoke_key(key_id, current_user.tenant_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cle non trouvee")
    await db.commit()
    return {"revoked": True}
