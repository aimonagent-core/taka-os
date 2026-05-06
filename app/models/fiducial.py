"""Modeles comptables pour Fiducial v0.1.

Tables :
  - plan_comptable : Plan de compte du tenant
  - journal_entries : Ecritures comptables (FEC)
  - ao_accounting_links : Liens entre AO et ecritures comptables
"""

from datetime import datetime
from typing import Optional
import uuid
from enum import Enum as PyEnum

from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, Boolean, JSON, Integer, Index, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AccountType(str, PyEnum):
    EXPENSE = "expense"
    INCOME = "income"
    ASSET = "asset"
    LIABILITY = "liability"


class PlanComptableEntry(Base):
    """Entree du plan de compte d'un tenant."""

    __tablename__ = "plan_comptable"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    account_number: Mapped[str] = mapped_column(String(20), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(SQLEnum(AccountType, name="account_type"), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_plancompt_tenant_num", "tenant_id", "account_number"),
    )


class JournalEntry(Base):
    """Ecriture comptable (ligne de journal)."""

    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    entry_number: Mapped[str] = mapped_column(String(50), nullable=False)
    entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), nullable=False)
    account_label: Mapped[str] = mapped_column(String(255), nullable=False)
    debit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    credit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    ao_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("aos.id"), nullable=True)
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)

    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_journal_tenant_date", "tenant_id", "entry_date"),
        Index("idx_journal_tenant_fy", "tenant_id", "fiscal_year"),
        Index("idx_journal_ao", "ao_id"),
    )


class AoAccountingLink(Base):
    """Lien entre un AO gagne et ses ecritures comptables."""

    __tablename__ = "ao_accounting_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ao_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("aos.id"), nullable=False, unique=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    final_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    margin_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=15.0, nullable=False)
    journal_entry_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    is_exported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    exported_format: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
