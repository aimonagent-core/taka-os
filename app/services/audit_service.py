# File: app/services/audit_service.py
# Purpose: Forensic audit log insertion — UNIFIED on audit_trail (S5)
# Dependencies: app.models.audit, app.core.audit, sqlalchemy.ext.asyncio

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import compute_audit_hash, now_utc
from app.models.ao import AuditAction
from app.models.audit import AuditTrail


class AuditService:
    """
    Insert audit logs maintaining an immutable SHA-256 hash chain.
    Writes UNIFIES into audit_trail (S5). Legacy audit_logs is archived.
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
    ) -> AuditTrail:
        """
        Insert an audit record with hash chain linking into audit_trail.
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

        # Map legacy entity_id (string) to target_id (UUID) when possible
        target_id = None
        if entity_id:
            try:
                target_id = uuid.UUID(entity_id)
            except ValueError:
                pass

        # Derive action_category from action type heuristics
        action_category = "unknown"
        if action.value in ("login", "logout", "mfa_enabled", "mfa_disabled"):
            action_category = "auth"
        elif action.value in ("create", "read", "update", "delete"):
            action_category = "crud"
        elif action.value in ("invitation_sent", "invitation_accepted"):
            action_category = "invitation"

        event_metadata = {
            "hash_chain": {
                "previous_hash": previous_hash,
                "hash": audit_hash,
            },
            "legacy_entity_id": entity_id if target_id is None else None,
        }

        log_entry = AuditTrail(
            tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
            actor_type="user",
            actor_id=uuid.UUID(user_id) if user_id else None,
            action=action.value,
            action_category=action_category,
            target_type=entity_type,
            target_id=target_id,
            before_state=payload_before,
            after_state=payload_after,
            ip_address=ip_address,
            user_agent=user_agent,
            event_metadata=event_metadata,
            severity="info",
        )
        db.add(log_entry)
        return log_entry

    @staticmethod
    async def _get_last_hash(
        db: AsyncSession, tenant_id: str | None
    ) -> str | None:
        """Fetch the hash of the most recent audit record for a tenant."""
        query = (
            select(AuditTrail)
            .where(AuditTrail.tenant_id == (uuid.UUID(tenant_id) if tenant_id else None))
            .order_by(AuditTrail.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        last = result.scalar_one_or_none()
        if last and last.event_metadata:
            return last.event_metadata.get("hash_chain", {}).get("hash")
        return None

    @staticmethod
    async def verify_chain(db: AsyncSession, tenant_id: str | None) -> bool:
        """Verify the integrity of the audit chain for a tenant."""
        from app.core.audit import verify_hash_chain

        result = await db.execute(
            select(AuditTrail)
            .where(AuditTrail.tenant_id == (uuid.UUID(tenant_id) if tenant_id else None))
            .order_by(AuditTrail.created_at.asc())
        )
        records = []
        for r in result.scalars().all():
            hash_chain = r.event_metadata.get("hash_chain", {}) if r.event_metadata else {}
            records.append({
                "hash": hash_chain.get("hash"),
                "previous_hash": hash_chain.get("previous_hash"),
                "created_at": r.created_at,
                "tenant_id": str(r.tenant_id) if r.tenant_id else None,
                "user_id": str(r.actor_id) if r.actor_id else None,
                "action": r.action,
                "entity_type": r.target_type,
                "entity_id": str(r.target_id) if r.target_id else None,
                "payload_before": r.before_state,
                "payload_after": r.after_state,
            })
        return verify_hash_chain(records)
