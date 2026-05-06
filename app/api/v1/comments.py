"""Routes pour les commentaires sur les AO.

Routes :
  GET  /comments/ao/{ao_id}      → Liste des commentaires
  POST /comments/ao/{ao_id}      → Creer un commentaire
  PUT  /comments/{comment_id}    → Modifier un commentaire
  POST /comments/{comment_id}/resolve → Resoudre un thread
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.services.comments.service import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])


class CommentCreate(BaseModel):
    content: str
    parent_id: uuid.UUID | None = None


class CommentUpdate(BaseModel):
    content: str


@router.get("/ao/{ao_id}")
async def get_comments(
    ao_id: uuid.UUID,
    include_resolved: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les commentaires d'un AO (threaded)."""
    service = CommentService(db)
    comments = await service.get_comments_for_ao(ao_id, include_resolved)
    return {"comments": comments}


@router.post("/ao/{ao_id}")
async def create_comment(
    ao_id: uuid.UUID,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cree un commentaire sur un AO."""
    service = CommentService(db)
    comment = await service.create_comment(
        tenant_id=current_user.tenant_id,
        ao_id=ao_id,
        author_id=current_user.id,
        content=data.content,
        parent_id=data.parent_id,
    )
    return {
        "id": str(comment.id),
        "content": comment.content,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }


@router.put("/{comment_id}")
async def update_comment(
    comment_id: uuid.UUID,
    data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Modifie un commentaire (auteur uniquement)."""
    service = CommentService(db)
    comment = await service.update_comment(comment_id, current_user.id, data.content)
    if not comment:
        raise HTTPException(status_code=404, detail="Commentaire non trouve ou non auteur")
    return {"id": str(comment.id), "content": comment.content, "is_edited": comment.is_edited}


@router.post("/{comment_id}/resolve")
async def resolve_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marque un commentaire comme resolu."""
    service = CommentService(db)
    ok = await service.resolve_comment(comment_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Commentaire non trouve")
    return {"status": "resolved"}
