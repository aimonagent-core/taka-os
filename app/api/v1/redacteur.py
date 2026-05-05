"""Routes API pour l'Agent Rédacteur."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.redacteur.generator import RedacteurGenerator
from app.agents.redacteur.templates import TemplateService
from app.database import get_db
from app.dependencies import get_current_user, require_manager
from app.models.ao import User
from app.models.response import GeneratedResponse, ResponseTemplate
from app.services.plan_feature_flags import FeatureFlagService

router = APIRouter(prefix="/redacteur", tags=["redacteur"])


@router.get("/templates")
async def list_templates(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les templates de réponse du tenant."""
    stmt = select(ResponseTemplate).where(ResponseTemplate.tenant_id == current_user.tenant_id)
    if category:
        stmt = stmt.where(ResponseTemplate.category == category)
    rows = await db.execute(stmt)
    templates = rows.scalars().all()
    return [
        {
            "id": str(t.id),
            "name": t.name,
            "category": t.category,
            "description": t.description,
            "is_default": t.is_default,
            "business_line_id": str(t.business_line_id) if t.business_line_id else None,
        }
        for t in templates
    ]


@router.post("/templates/seed-defaults")
async def seed_defaults(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Crée les templates par défaut si aucun n'existe (admin uniquement)."""
    templates = await TemplateService.get_or_create_defaults(db, str(current_user.tenant_id))
    return {"created": len(templates), "templates": [{"id": str(t.id), "name": t.name} for t in templates]}


@router.post("/generate/{ao_id}")
async def generate_response(
    ao_id: str,
    category: str = Query("letter", enum=["letter", "technical", "financial", "administrative"]),
    custom_prompt: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Génère une réponse pour un AO donné."""
    tenant_tier = current_user.tenant.billing_plan or "free" if current_user.tenant else "free"
    await FeatureFlagService.check_feature(db, "generation_ia", tenant_tier)

    generator = RedacteurGenerator()
    try:
        response = await generator.generate(
            ao_id=ao_id,
            category=category,
            user_id=str(current_user.id),
            db=db,
            tenant_id=str(current_user.tenant_id),
            custom_prompt=custom_prompt,
        )
        return {
            "id": str(response.id),
            "category": response.category,
            "content": response.content,
            "structured_content": response.structured_content,
            "status": response.status,
            "hil_status": response.hil_status,
            "tokens_input": response.tokens_input,
            "tokens_output": response.tokens_output,
            "generation_time_ms": response.generation_time_ms,
            "created_at": response.created_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/responses")
async def list_responses(
    ao_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les réponses générées (filtrables par AO ou statut)."""
    stmt = select(GeneratedResponse).where(GeneratedResponse.user_id == current_user.id)
    if ao_id:
        stmt = stmt.where(GeneratedResponse.ao_id == ao_id)
    if status:
        stmt = stmt.where(GeneratedResponse.status == status)
    stmt = stmt.order_by(desc(GeneratedResponse.created_at))
    rows = await db.execute(stmt)
    responses = rows.scalars().all()
    return [
        {
            "id": str(r.id),
            "ao_id": str(r.ao_id),
            "category": r.category,
            "status": r.status,
            "hil_status": r.hil_status,
            "content_preview": r.content[:200] + "..." if len(r.content) > 200 else r.content,
            "generation_time_ms": r.generation_time_ms,
            "created_at": r.created_at.isoformat(),
        }
        for r in responses
    ]


@router.get("/responses/{response_id}")
async def get_response(
    response_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne le détail complet d'une réponse générée."""
    stmt = select(GeneratedResponse).where(
        GeneratedResponse.id == response_id,
        GeneratedResponse.user_id == current_user.id,
    )
    row = await db.execute(stmt)
    r = row.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")

    return {
        "id": str(r.id),
        "ao_id": str(r.ao_id),
        "template_id": str(r.template_id) if r.template_id else None,
        "category": r.category,
        "content": r.content,
        "structured_content": r.structured_content,
        "status": r.status,
        "hil_status": r.hil_status,
        "tokens_input": r.tokens_input,
        "tokens_output": r.tokens_output,
        "generation_time_ms": r.generation_time_ms,
        "model_used": r.model_used,
        "created_at": r.created_at.isoformat(),
    }


@router.post("/responses/{response_id}/approve")
async def approve_response(
    response_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approuve une réponse (après review manuelle) — pré-requis au dépôt."""
    stmt = select(GeneratedResponse).where(
        GeneratedResponse.id == response_id,
        GeneratedResponse.user_id == current_user.id,
    )
    row = await db.execute(stmt)
    r = row.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")

    if r.status not in ("generated", "reviewing"):
        raise HTTPException(status_code=400, detail=f"Statut {r.status} — approbation impossible")

    r.status = "approved"
    r.hil_status = "validated"
    await db.commit()
    return {"id": str(r.id), "status": "approved", "message": "Réponse approuvée — prête au dépôt"}


@router.post("/responses/{response_id}/reject")
async def reject_response(
    response_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rejette une réponse générée."""
    stmt = select(GeneratedResponse).where(
        GeneratedResponse.id == response_id,
        GeneratedResponse.user_id == current_user.id,
    )
    row = await db.execute(stmt)
    r = row.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")

    r.status = "rejected"
    r.hil_status = "rejected"
    await db.commit()
    return {"id": str(r.id), "status": "rejected", "reason": reason}
