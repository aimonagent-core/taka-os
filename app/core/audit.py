# File: app/core/audit.py
# Purpose: Forensic audit utilities with SHA-256 hash chain
# Dependencies: hashlib, datetime

import hashlib
from datetime import datetime, timezone
from typing import Any


def compute_audit_hash(
    previous_hash: str | None,
    record_data: dict[str, Any],
    timestamp: datetime,
) -> str:
    """
    Compute SHA-256 hash for an audit record.
    The hash covers: previous_hash + canonical record_data + ISO timestamp.
    This creates an immutable chain.
    """
    canonical_data = "|".join(
        f"{k}={str(v)}" for k, v in sorted(record_data.items()) if v is not None
    )
    payload = f"{previous_hash or 'genesis'}|{canonical_data}|{timestamp.isoformat()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_hash_chain(records: list[dict[str, Any]]) -> bool:
    """
    Verify integrity of a sequence of audit records.
    Each record must have 'hash' and 'previous_hash' keys.
    """
    for i, rec in enumerate(records):
        expected_prev = records[i - 1]["hash"] if i > 0 else None
        if rec.get("previous_hash") != expected_prev:
            return False
        rec_hash = compute_audit_hash(
            rec["previous_hash"],
            {
                k: v
                for k, v in rec.items()
                if k not in ("hash", "previous_hash", "created_at")
            },
            rec["created_at"],
        )
        if rec_hash != rec["hash"]:
            return False
    return True


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
