# File: app/services/audit_service.py
# Purpose: Forensic audit log insertion with hash chain integrity
# Dependencies: app.models.ao, app.core.audit, sqlalchemy.ext.asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import compute_audit_hash, now_utc
from app.models.ao import AuditAction, AuditLog


class AuditService:
    """
    Insert audit logs maintaining an immutable SHA-256 hash chain.
    Each new record references the hash of the previous record for the same tenant.
    """

    @staticmethod
    async def log(
        db: AsyncSession,
        action: AuditAction,
        entity_type: str,
        entity_id: str | None = None,
        payload_before: dict | None = None,
        payload_after: dict | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """
        Insert an audit record with hash chain linking.
        Must be called within an active DB transaction.
        """
        previous_hash = await AuditService._get_last_hash(db, tenant_id)

        timestamp = now_utc()
        record_data = {
            "tenant_id": str(tenant_id) if tenant_id else None,
            "user_id": str(user_id) if user_id else None,
            "action": action.value,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload_before": payload_before,
            "payload_after": payload_after,
        }

        audit_hash = compute_audit_hash(previous_hash, record_data, timestamp)

        log_entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload_before=payload_before,
            payload_after=payload_after,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_hash=previous_hash,
            hash=audit_hash,
        )
        db.add(log_entry)
        return log_entry

    @staticmethod
    async def _get_last_hash(
        db: AsyncSession, tenant_id: str | None
    ) -> str | None:
        """Fetch the hash of the most recent audit log for a tenant."""
        query = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        last = result.scalar_one_or_none()
        return last.hash if last else None

    @staticmethod
    async def verify_chain(db: AsyncSession, tenant_id: str | None) -> bool:
        """Verify the integrity of the audit chain for a tenant."""
        from app.core.audit import verify_hash_chain

        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.asc())
        )
        records = [
            {
                "hash": r.hash,
                "previous_hash": r.previous_hash,
                "created_at": r.created_at,
                **{
                    k: getattr(r, k)
                    for k in (
                        "tenant_id",
                        "user_id",
                        "action",
                        "entity_type",
                        "entity_id",
                        "payload_before",
                        "payload_after",
                    )
                },
            }
            for r in result.scalars().all()
        ]
        return verify_hash_chain(records)
