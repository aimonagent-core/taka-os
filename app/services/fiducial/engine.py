"""Moteur comptable pour Fiducial v0.1.

Gere :
- Creation du plan de compte par defaut pour un nouveau tenant
- Generation d'ecritures comptables quand un AO est gagne
- Export FEC (Fichier des Ecritures Comptables)
"""

import csv
import io
import logging
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.fiducial import PlanComptableEntry, JournalEntry, AoAccountingLink, AccountType
from app.models.ao_s2 import AO

logger = logging.getLogger(__name__)


class FiducialEngine:
    """Moteur comptable TAKA OS."""

    DEFAULT_CHART = [
        ("411000", "Clients", AccountType.ASSET),
        ("512000", "Banque", AccountType.ASSET),
        ("622600", "Honoraires", AccountType.EXPENSE),
        ("706000", "Prestations de services", AccountType.INCOME),
        ("708000", "Produits divers", AccountType.INCOME),
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def init_default_chart(self, tenant_id: uuid.UUID) -> int:
        """Cree le plan de compte par defaut pour un tenant."""
        created = 0
        for number, name, acc_type in self.DEFAULT_CHART:
            stmt = select(PlanComptableEntry).where(
                and_(
                    PlanComptableEntry.tenant_id == tenant_id,
                    PlanComptableEntry.account_number == number,
                )
            )
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                continue

            entry = PlanComptableEntry(
                tenant_id=tenant_id,
                account_number=number,
                account_name=name,
                account_type=acc_type,
                is_default=True,
            )
            self.db.add(entry)
            created += 1

        await self.db.flush()
        logger.info(f"Plan de compte initialise pour tenant {tenant_id}: {created} comptes")
        return created

    async def record_won_ao(
        self,
        tenant_id: uuid.UUID,
        ao_id: uuid.UUID,
        final_amount: float,
        margin_percent: float = 15.0,
    ) -> AoAccountingLink:
        """Enregistre un AO gagne en comptabilite.

        Genere l'ecriture : 411 (Client) / 706 (Prestation)
        """
        ao_stmt = select(AO).where(
            and_(AO.id == ao_id, AO.tenant_id == tenant_id)
        )
        ao_result = await self.db.execute(ao_stmt)
        ao = ao_result.scalar_one_or_none()

        if not ao:
            raise ValueError(f"AO {ao_id} non trouve")

        fiscal_year = datetime.now(timezone.utc).year
        entry_num = await self._get_next_entry_number(tenant_id, fiscal_year)

        # Debit 411 (Client)
        entry_debit = JournalEntry(
            tenant_id=tenant_id,
            entry_number=entry_num,
            entry_date=datetime.now(timezone.utc),
            account_number="411000",
            account_label="Clients",
            debit=final_amount,
            credit=None,
            label=f"Creance client - {ao.title[:100] if ao.title else ''}",
            ao_id=ao_id,
            fiscal_year=fiscal_year,
        )
        self.db.add(entry_debit)

        # Credit 706 (Prestation)
        entry_credit = JournalEntry(
            tenant_id=tenant_id,
            entry_number=entry_num,
            entry_date=datetime.now(timezone.utc),
            account_number="706000",
            account_label="Prestations de services",
            debit=None,
            credit=final_amount,
            label=f"Prestation - {ao.title[:100] if ao.title else ''}",
            ao_id=ao_id,
            fiscal_year=fiscal_year,
        )
        self.db.add(entry_credit)

        await self.db.flush()

        link = AoAccountingLink(
            ao_id=ao_id,
            tenant_id=tenant_id,
            final_amount=final_amount,
            margin_percent=margin_percent,
            journal_entry_ids=[str(entry_debit.id), str(entry_credit.id)],
        )
        self.db.add(link)
        await self.db.flush()

        logger.info(f"AO {ao_id} enregistre en comptabilite : {final_amount} EUR")
        return link

    async def _get_next_entry_number(
        self,
        tenant_id: uuid.UUID,
        fiscal_year: int,
    ) -> str:
        """Genere le prochain numero d'ecriture."""
        stmt = select(func.count(JournalEntry.id)).where(
            and_(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.fiscal_year == fiscal_year,
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar() or 0
        seq = (count // 2) + 1
        return f"{fiscal_year}-{seq:04d}"

    async def export_fec(
        self,
        tenant_id: uuid.UUID,
        fiscal_year: int,
    ) -> str:
        """Exporte le FEC (Fichier des Ecritures Comptables) au format CSV tabule."""
        fec_headers = [
            "JournalCode", "JournalLib", "EcritureNum", "EcritureDate",
            "CompteNum", "CompteLib", "CompAuxNum", "CompAuxLib",
            "PieceRef", "PieceDate", "EcritureLib", "Debit", "Credit",
            "EcritureLet", "DateLet", "ValidDate", "Montantdevise", "Idevise"
        ]

        stmt = select(JournalEntry).where(
            and_(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.fiscal_year == fiscal_year,
            )
        ).order_by(JournalEntry.entry_date, JournalEntry.entry_number)

        result = await self.db.execute(stmt)
        entries = result.scalars().all()

        output = io.StringIO()
        output.write('\ufeff')
        writer = csv.writer(output, delimiter='\t', lineterminator='\n')
        writer.writerow(fec_headers)

        for entry in entries:
            row = [
                "VE",
                "Ventes",
                entry.entry_number,
                entry.entry_date.strftime("%Y%m%d") if entry.entry_date else "",
                entry.account_number,
                entry.account_label,
                "",
                "",
                str(entry.ao_id) if entry.ao_id else "",
                entry.entry_date.strftime("%Y%m%d") if entry.entry_date else "",
                entry.label,
                str(entry.debit) if entry.debit else "0",
                str(entry.credit) if entry.credit else "0",
                "",
                "",
                entry.entry_date.strftime("%Y%m%d") if entry.entry_date else "",
                "",
                "EUR",
            ]
            writer.writerow(row)

        return output.getvalue()

    async def get_accounting_summary(
        self,
        tenant_id: uuid.UUID,
        fiscal_year: int,
    ) -> dict:
        """Resume comptable pour le dashboard."""
        revenue_stmt = select(func.sum(JournalEntry.credit)).where(
            and_(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.fiscal_year == fiscal_year,
                JournalEntry.account_number.like("7%"),
            )
        )
        revenue_result = await self.db.execute(revenue_stmt)
        total_revenue = float(revenue_result.scalar() or 0)

        expense_stmt = select(func.sum(JournalEntry.debit)).where(
            and_(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.fiscal_year == fiscal_year,
                JournalEntry.account_number.like("6%"),
            )
        )
        expense_result = await self.db.execute(expense_stmt)
        total_expenses = float(expense_result.scalar() or 0)

        receivables_stmt = select(func.sum(JournalEntry.debit)).where(
            and_(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.fiscal_year == fiscal_year,
                JournalEntry.account_number == "411000",
            )
        )
        receivables_result = await self.db.execute(receivables_stmt)
        outstanding = float(receivables_result.scalar() or 0)

        ao_count_stmt = select(func.count(func.distinct(JournalEntry.ao_id))).where(
            and_(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.fiscal_year == fiscal_year,
            )
        )
        ao_count_result = await self.db.execute(ao_count_stmt)
        ao_count = ao_count_result.scalar() or 0

        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_income": total_revenue - total_expenses,
            "outstanding_receivables": outstanding,
            "ao_count": ao_count,
            "fiscal_year": fiscal_year,
        }
