"""Routes API pour la gestion des Business Lines."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_manager
from app.models.ao import User
from app.services.business_lines.service import BusinessLineService
from app.services.plan_feature_flags import FeatureFlagService

router = APIRouter(prefix="/business-lines", tags=["business-lines"])


def _get_tenant_tier(user: User) -> str:
    return user.tenant.billing_plan or "free" if user.tenant else "free"


@router.post("/")
async def create_business_line(
    name: str,
    description: Optional[str] = None,
    color: str = "#3B82F6",
    default_profile: str = "prudent",
    cpv_keywords: List[str] = None,
    free_text_keywords: List[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Cree une nouvelle Business Line (admin uniquement)."""
    await FeatureFlagService.check_feature(db, "multi_bl", _get_tenant_tier(current_user))

    bl = await BusinessLineService.create_bl(
        db=db,
        tenant_id=str(current_user.tenant_id),
        name=name,
        description=description,
        color=color,
        default_profile=default_profile,
        cpv_keywords=cpv_keywords or [],
        free_text_keywords=free_text_keywords or [],
    )
    return {"id": str(bl.id), "name": bl.name, "message": "Business Line creee"}


@router.get("/")
async def list_business_lines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les Business Lines du tenant."""
    bls = await BusinessLineService.get_bl_for_tenant(db, str(current_user.tenant_id))
    return [
        {
            "id": str(bl.id),
            "name": bl.name,
            "description": bl.description,
            "color": bl.color,
            "default_profile": bl.default_profile,
            "cpv_keywords": bl.cpv_keywords,
            "member_count": len(bl.members),
        }
        for bl in bls
    ]


@router.post("/{bl_id}/assign/{user_id}")
async def assign_user(
    bl_id: str,
    user_id: str,
    role: str = "member",
    is_primary: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Assigne un utilisateur a une Business Line."""
    member = await BusinessLineService.assign_user_to_bl(
        db, bl_id, user_id, role, is_primary
    )
    return {"id": str(member.id), "role": member.role, "is_primary": member.is_primary}


@router.get("/my-scope")
async def get_my_scope(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne le scope Business Lines de l'utilisateur connecte."""
    scope = await BusinessLineService.get_user_bl_scope(db, str(current_user.id))
    return scope
