"""Service Dashboard — calcul des 10 KPIs du tableau de bord."""
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao_s2 import AO, Source
from app.models.scoring import ScoringRun

logger = logging.getLogger(__name__)


class DashboardKPIs:
    """Calcul des KPIs du Dashboard Admin."""

    @staticmethod
    async def get_all_kpis(
        db: AsyncSession,
        tenant_id: str,
        business_line_id: Optional[str] = None,
        period_days: int = 30,
    ) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=period_days)

        base_filter = [AO.created_at >= since]
        bl_filter = base_filter.copy()
        if business_line_id:
            bl_filter.append(AO.business_line_id == business_line_id)

        kpis = {
            "period_days": period_days,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        # KPI 1 : Total AO detectes
        stmt = select(func.count(AO.id)).where(and_(*bl_filter))
        row = await db.execute(stmt)
        kpis["total_ao_detected"] = row.scalar() or 0

        # KPI 2 : AO qualifies (GO)
        stmt_go = select(func.count(ScoringRun.id)).join(AO).where(
            and_(
                ScoringRun.verdict == "GO",
                ScoringRun.created_at >= since,
                *([AO.business_line_id == business_line_id] if business_line_id else []),
            )
        )
        row_go = await db.execute(stmt_go)
        kpis["ao_qualified_go"] = row_go.scalar() or 0

        # KPI 3 : AO rejetes (NO-GO)
        stmt_nogo = select(func.count(ScoringRun.id)).join(AO).where(
            and_(
                ScoringRun.verdict == "NO_GO",
                ScoringRun.created_at >= since,
                *([AO.business_line_id == business_line_id] if business_line_id else []),
            )
        )
        row_nogo = await db.execute(stmt_nogo)
        kpis["ao_rejected_nogo"] = row_nogo.scalar() or 0

        # KPI 4 : AO en attente (MAYBE)
        stmt_maybe = select(func.count(ScoringRun.id)).join(AO).where(
            and_(
                ScoringRun.verdict == "MAYBE",
                ScoringRun.created_at >= since,
                *([AO.business_line_id == business_line_id] if business_line_id else []),
            )
        )
        row_maybe = await db.execute(stmt_maybe)
        kpis["ao_pending_maybe"] = row_maybe.scalar() or 0

        # KPI 5 : Taux de qualification
        total_scored = (
            kpis["ao_qualified_go"] + kpis["ao_rejected_nogo"] + kpis["ao_pending_maybe"]
        )
        kpis["qualification_rate_pct"] = (
            round((kpis["ao_qualified_go"] / total_scored * 100), 1)
            if total_scored > 0
            else 0.0
        )

        # KPI 6 : Montant total des AO qualifies (EUR)
        stmt_amount = select(
            func.coalesce(func.sum(AO.estimated_amount), Decimal(0))
        ).join(ScoringRun).where(
            and_(
                ScoringRun.verdict == "GO",
                ScoringRun.created_at >= since,
                AO.currency == "EUR",
                *([AO.business_line_id == business_line_id] if business_line_id else []),
            )
        )
        row_amount = await db.execute(stmt_amount)
        kpis["total_amount_qualified_eur"] = float(row_amount.scalar() or 0)

        # KPI 7 : Delai moyen de reponse (jours)
        stmt_delay = select(
            func.avg(func.extract("epoch", AO.deadline_date - AO.created_at) / 86400)
        ).where(
            and_(
                AO.deadline_date.isnot(None),
                AO.created_at >= since,
                *([AO.business_line_id == business_line_id] if business_line_id else []),
            )
        )
        row_delay = await db.execute(stmt_delay)
        kpis["avg_response_delay_days"] = round(row_delay.scalar() or 0, 1)

        # KPI 8 : Source la plus productive
        stmt_top_source = (
            select(Source.name, func.count(AO.id).label("cnt"))
            .join(AO)
            .where(
                and_(
                    AO.created_at >= since,
                    *([AO.business_line_id == business_line_id] if business_line_id else []),
                )
            )
            .group_by(Source.name)
            .order_by(func.count(AO.id).desc())
        )
        row_top = await db.execute(stmt_top_source)
        top = row_top.first()
        kpis["top_source"] = {
            "name": top.name if top else None,
            "count": top.cnt if top else 0,
        }

        # KPI 9 : Score moyen global
        stmt_avg_score = select(func.avg(ScoringRun.score_global)).where(
            and_(
                ScoringRun.created_at >= since,
                *([AO.business_line_id == business_line_id] if business_line_id else []),
            )
        )
        row_avg = await db.execute(stmt_avg_score)
        kpis["avg_global_score"] = round(float(row_avg.scalar() or 0), 2)

        # KPI 10 : Repartition par pays
        stmt_by_country = (
            select(AO.country, func.count(AO.id))
            .where(and_(*bl_filter))
            .group_by(AO.country)
            .order_by(func.count(AO.id).desc())
        )
        rows_country = await db.execute(stmt_by_country)
        kpis["ao_by_country"] = [
            {"country": r[0], "count": r[1]} for r in rows_country.all()
        ]

        # Evolution temporelle
        day_trunc = func.date_trunc("day", AO.created_at)
        stmt_evolution = (
            select(
                day_trunc.label("day"),
                func.count(AO.id).label("cnt"),
            )
            .where(and_(*bl_filter))
            .group_by(day_trunc)
            .order_by(day_trunc)
        )
        rows_evo = await db.execute(stmt_evolution)
        kpis["evolution_daily"] = [
            {"date": r.day.isoformat() if r.day else None, "count": r.cnt}
            for r in rows_evo.all()
        ]

        logger.info(
            "[Dashboard] KPIs calcules pour tenant=%s: %s AO, %s GO",
            tenant_id,
            kpis["total_ao_detected"],
            kpis["ao_qualified_go"],
        )
        return kpis

    @staticmethod
    async def get_kpis_by_business_line(
        db: AsyncSession,
        tenant_id: str,
        period_days: int = 30,
    ) -> list[dict]:
        from app.models.business_line import BusinessLine

        stmt = select(BusinessLine).where(
            and_(BusinessLine.tenant_id == tenant_id, BusinessLine.is_active.is_(True))
        )
        rows = await db.execute(stmt)
        bls = rows.scalars().all()

        results = []
        for bl in bls:
            kpis = await DashboardKPIs.get_all_kpis(
                db, tenant_id, str(bl.id), period_days
            )
            results.append(
                {
                    "business_line_id": str(bl.id),
                    "business_line_name": bl.name,
                    "business_line_color": bl.color,
                    "kpis": kpis,
                }
            )

        return results
