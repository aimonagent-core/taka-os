"""API endpoints pour la gestion des credentials plateforme."""

from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.dependencies import get_current_user
from app.core.encryption import encrypt_value, decrypt_value
from app.models.ao import User
from app.models.audit import PlatformCredential
from app.agents.deposant.connectors import get_connector
from app.agents.deposant.connectors.base import PlatformCredentials as ConnectorCredentials

router = APIRouter(prefix="/platform-credentials", tags=["platform-credentials"])


class PlatformCredentialCreate(BaseModel):
    platform_type: str
    platform_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    certificate_pem: Optional[str] = None
    base_url: Optional[str] = None
    additional_data: Optional[dict] = None
    webhook_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class PlatformCredentialUpdate(BaseModel):
    platform_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    certificate_pem: Optional[str] = None
    base_url: Optional[str] = None
    additional_data: Optional[dict] = None
    webhook_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


@router.post("")
async def create_credential(
    data: PlatformCredentialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cree de nouveaux credentials pour une plateforme."""
    cred = PlatformCredential(
        tenant_id=current_user.tenant_id,
        created_by_user_id=current_user.id,
        platform_type=data.platform_type,
        platform_name=data.platform_name,
        username=encrypt_value(data.username),
        password=encrypt_value(data.password),
        api_key=encrypt_value(data.api_key),
        certificate_pem=encrypt_value(data.certificate_pem),
        base_url=data.base_url,
        additional_data=data.additional_data,
        webhook_url=data.webhook_url,
        expires_at=data.expires_at,
    )

    db.add(cred)
    await db.flush()

    return _serialize_credential(cred)


@router.get("")
async def list_credentials(
    platform_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les credentials du tenant."""
    conditions = [
        PlatformCredential.tenant_id == current_user.tenant_id,
        PlatformCredential.is_active == True,
    ]
    if platform_type:
        conditions.append(PlatformCredential.platform_type == platform_type)

    stmt = select(PlatformCredential).where(and_(*conditions))
    result = await db.execute(stmt)
    creds = result.scalars().all()

    return [_serialize_credential(c) for c in creds]


@router.get("/{cred_id}")
async def get_credential(
    cred_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detail d'un credential (sans les secrets)."""
    stmt = select(PlatformCredential).where(
        and_(
            PlatformCredential.id == cred_id,
            PlatformCredential.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    cred = result.scalar_one_or_none()

    if not cred:
        raise HTTPException(status_code=404, detail="Credential non trouve")

    return _serialize_credential(cred)


@router.put("/{cred_id}")
async def update_credential(
    cred_id: uuid.UUID,
    data: PlatformCredentialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Met a jour des credentials."""
    stmt = select(PlatformCredential).where(
        and_(
            PlatformCredential.id == cred_id,
            PlatformCredential.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    cred = result.scalar_one_or_none()

    if not cred:
        raise HTTPException(status_code=404, detail="Credential non trouve")

    if data.platform_name is not None:
        cred.platform_name = data.platform_name
    if data.username is not None:
        cred.username = encrypt_value(data.username)
    if data.password is not None:
        cred.password = encrypt_value(data.password)
    if data.api_key is not None:
        cred.api_key = encrypt_value(data.api_key)
    if data.certificate_pem is not None:
        cred.certificate_pem = encrypt_value(data.certificate_pem)
    if data.base_url is not None:
        cred.base_url = data.base_url
    if data.additional_data is not None:
        cred.additional_data = data.additional_data
    if data.webhook_url is not None:
        cred.webhook_url = data.webhook_url
    if data.expires_at is not None:
        cred.expires_at = data.expires_at
    if data.is_active is not None:
        cred.is_active = data.is_active

    if any([data.username, data.password, data.api_key, data.certificate_pem]):
        cred.is_validated = False
        cred.validated_at = None
        cred.last_error = None

    await db.flush()
    return _serialize_credential(cred)


@router.delete("/{cred_id}")
async def delete_credential(
    cred_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Supprime (soft delete) des credentials."""
    stmt = select(PlatformCredential).where(
        and_(
            PlatformCredential.id == cred_id,
            PlatformCredential.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    cred = result.scalar_one_or_none()

    if not cred:
        raise HTTPException(status_code=404, detail="Credential non trouve")

    cred.is_active = False
    await db.flush()
    return {"status": "deleted", "id": str(cred_id)}


@router.post("/{cred_id}/test")
async def test_credential(
    cred_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Teste la connexion avec les credentials."""
    stmt = select(PlatformCredential).where(
        and_(
            PlatformCredential.id == cred_id,
            PlatformCredential.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    cred = result.scalar_one_or_none()

    if not cred:
        raise HTTPException(status_code=404, detail="Credential non trouve")

    connector_creds = ConnectorCredentials(
        username=decrypt_value(cred.username),
        password=decrypt_value(cred.password),
        api_key=decrypt_value(cred.api_key),
        certificate_pem=decrypt_value(cred.certificate_pem),
        base_url=cred.base_url,
        additional_data=cred.additional_data,
    )

    try:
        connector_class = get_connector(cred.platform_type, use_real=True)
        connector = connector_class(connector_creds)

        auth_ok = await connector.authenticate()

        if auth_ok:
            cred.is_validated = True
            cred.validated_at = datetime.now(timezone.utc)
            cred.last_error = None
            await db.flush()
            return {"status": "success", "message": "Connexion validee avec succes"}
        else:
            cred.is_validated = False
            cred.last_error = "Echec d'authentification"
            await db.flush()
            raise HTTPException(status_code=400, detail="Echec d'authentification — verifiez vos credentials")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        cred.is_validated = False
        cred.last_error = str(e)[:500]
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Erreur de connexion : {str(e)}")


@router.get("/platforms/available")
async def list_available_platforms(
    current_user: User = Depends(get_current_user),
):
    """Liste les plateformes supportees avec leur statut."""
    from app.agents.deposant.connectors import list_available_platforms as list_platforms

    platforms = list_platforms()

    names = {
        "boamp": "BOAMP (France)",
        "e_notification": "e-Notification (Belgique)",
        "maroc": "Marches Publics (Maroc)",
        "ted": "TED — Tenders Electronic Daily (EU)",
        "joue": "JOUE (Journal Officiel EU)",
    }

    return {
        "mock": [
            {"type": p, "name": names.get(p, p), "requires_credentials": False}
            for p in platforms["mock"]
        ],
        "real": [
            {"type": p, "name": names.get(p, p), "requires_credentials": True}
            for p in platforms["real"]
        ],
    }


def _serialize_credential(cred: PlatformCredential) -> dict:
    """Serialize un credential en masquant les secrets."""
    username_masked = None
    if cred.username:
        decrypted = decrypt_value(cred.username)
        if decrypted and len(decrypted) > 8:
            username_masked = f"{decrypted[:3]}***{decrypted[-3:]}"
        elif decrypted:
            username_masked = "***"

    return {
        "id": str(cred.id),
        "platform_type": cred.platform_type,
        "platform_name": cred.platform_name,
        "username": username_masked,
        "base_url": cred.base_url,
        "additional_data": cred.additional_data,
        "is_validated": cred.is_validated,
        "validated_at": cred.validated_at.isoformat() if cred.validated_at else None,
        "is_active": cred.is_active,
        "expires_at": cred.expires_at.isoformat() if cred.expires_at else None,
        "created_at": cred.created_at.isoformat() if cred.created_at else None,
    }
