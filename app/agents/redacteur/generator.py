"""Agent Rédacteur — génère des réponses IA à partir d'un AO et d'un template."""
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao_s2 import AO
from app.models.business_line import BusinessLine
from app.models.response import GeneratedResponse, ResponseTemplate
from app.models.scoring import ScoringRun
from app.services.llm.mistral_client import MistralAIClient

logger = logging.getLogger(__name__)

MAX_OUTPUT_TOKENS = 4000


class RedacteurGenerator:
    """Générateur de réponses à appels d'offres via Mistral AI."""

    def __init__(self):
        self.mistral = MistralAIClient()

    async def generate(
        self,
        ao_id: str,
        category: str,
        user_id: str,
        db: AsyncSession,
        custom_prompt: Optional[str] = None,
        tenant_id: Optional[str] = None,
        template: Optional[ResponseTemplate] = None,
    ) -> GeneratedResponse:
        """Génère une réponse pour un AO donné."""
        start = datetime.now(timezone.utc)

        # Charger l'AO avec relations
        stmt = select(AO).where(AO.id == ao_id)
        row = await db.execute(stmt)
        ao = row.scalar_one_or_none()
        if not ao:
            raise ValueError(f"AO {ao_id} introuvable")

        # Vérifier que l'AO est qualifié (GO ou MAYBE)
        verdict = None
        if ao.scoring_result:
            verdict = ao.scoring_result.get("verdict")
        if verdict not in ("GO", "MAYBE"):
            raise ValueError(f"AO {ao_id} verdict={verdict} — non qualifié pour rédaction")

        # Charger le template si non fourni
        if template is None:
            from app.agents.redacteur.templates import TemplateService

            # Déterminer le tenant_id pour le fallback
            ao_tenant_id = tenant_id
            if not ao_tenant_id and ao.business_line_id:
                stmt_bl = select(BusinessLine).where(BusinessLine.id == ao.business_line_id)
                row_bl = await db.execute(stmt_bl)
                bl = row_bl.scalar_one_or_none()
                if bl:
                    ao_tenant_id = str(bl.tenant_id)

            template = await TemplateService.get_for_ao(
                db, ao, category, fallback_tenant_id=ao_tenant_id
            )

        # Construire le contexte d'enrichissement
        context = await self._build_context(ao, db)

        # Remplacer les variables du template
        filled_template = self._fill_template(template.template_content, context)

        # Assembler le prompt complet
        system_prompt = template.system_prompt
        if custom_prompt:
            system_prompt += f"\n\nInstructions additionnelles : {custom_prompt}"

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""Voici le contexte de l'appel d'offres :

TITRE : {ao.title}
DESCRIPTION : {ao.description or 'Non fournie'}
CPV : {', '.join(ao.cpv_codes or [])}
MONTANT ESTIMÉ : {ao.estimated_amount} {ao.currency if ao.estimated_amount else ''}
DÉLAI : {ao.deadline_date.isoformat() if ao.deadline_date else 'Non précisé'}
ACHETEUR : {ao.buyer_name or 'Non précisé'}

Voici le template à compléter :
{filled_template}

Génère le document final complet, professionnel et prêt à l'emploi.""",
            },
        ]

        # Appel Mistral
        try:
            result = await self.mistral.chat_completion(
                messages=messages,
                max_tokens=MAX_OUTPUT_TOKENS,
                temperature=0.3,
            )
            choice = result.get("choices", [{}])[0]
            response_text = choice.get("message", {}).get("content", "")
            usage = result.get("usage", {})
        except Exception as e:
            logger.error("[Redacteur] Erreur génération Mistral : %s", e)
            raise RuntimeError(f"Échec de la génération IA : {e}")

        # Parser la réponse structurée (si sections détectées)
        structured = self._parse_sections(response_text)

        duration_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

        generated = GeneratedResponse(
            ao_id=ao.id,
            template_id=template.id,
            user_id=user_id,
            category=category,
            content=response_text,
            structured_content=structured,
            tokens_input=usage.get("prompt_tokens", 0),
            tokens_output=usage.get("completion_tokens", 0),
            generation_time_ms=duration_ms,
            model_used="mistral-large-latest",
            status="generated",
            hil_status="pending",
        )
        db.add(generated)
        await db.commit()
        await db.refresh(generated)

        logger.info(
            "[Redacteur] Réponse %s générée pour AO %s en %sms",
            generated.id,
            ao_id,
            duration_ms,
        )
        return generated

    async def _build_context(self, ao: AO, db: AsyncSession) -> dict:
        """Construit le contexte d'enrichissement pour le template."""
        ctx = {
            "titre_ao": ao.title,
            "reference_ao": ao.external_id,
            "acheteur": ao.buyer_name or "Madame, Monsieur",
            "adresse_acheteur": f"{ao.city or ''} ({ao.department_code or ''})",
            "domaine": ao.cpv_descriptions[0] if ao.cpv_descriptions else "le domaine concerné",
            "cpv": ", ".join(ao.cpv_codes[:3] if ao.cpv_codes else []),
            "motivation": "ce projet correspond parfaitement à notre cœur de métier",
            "atout_technique": "notre expertise reconnue et notre méthodologie éprouvée",
            "delai": f"{ao.contract_duration_months} mois" if ao.contract_duration_months else "le délai imparti",
            "delai_semaines": ao.contract_duration_months * 4 if ao.contract_duration_months else 12,
            "nom_entreprise": "NOTRE ENTREPRISE",
            "signature": "Le Responsable Commercial",
            "contact": "contact@entreprise.fr | 01 23 45 67 89",
            "montant_ht": "[À COMPLÉTER]",
            "montant_tva": "[À COMPLÉTER]",
            "montant_ttc": "[À COMPLÉTER]",
            "tva": "20",
            "prestations": "[À COMPLÉTER]",
            "fournitures": "[À COMPLÉTER]",
            "deplacements": "[À COMPLÉTER]",
            "assurance": "[À COMPLÉTER]",
            "marge": "[À COMPLÉTER]",
            "chef_projet": "[À COMPLÉTER]",
            "equipe": "[À COMPLÉTER]",
            "moyens": "[À COMPLÉTER]",
            "planning": "[À COMPLÉTER]",
            "qualite": "[À COMPLÉTER]",
            "references": "[À COMPLÉTER]",
            "nb_references": "12",
            "montant_total": "4.5M",
            "description_resume": ao.description[:200] if ao.description else "la réalisation des prestations décrites",
        }

        if ao.business_line_id:
            stmt = select(BusinessLine).where(BusinessLine.id == ao.business_line_id)
            row = await db.execute(stmt)
            bl = row.scalar_one_or_none()
            if bl:
                ctx["domaine"] = bl.name
                ctx["nom_entreprise"] = bl.name

        stmt_score = (
            select(ScoringRun)
            .where(ScoringRun.ao_id == ao.id)
            .order_by(ScoringRun.created_at.desc())
        )
        row_score = await db.execute(stmt_score)
        score = row_score.scalar_one_or_none()
        if score:
            ctx["score_global"] = float(score.score_global)
            ctx["verdict"] = score.verdict
            ctx["recommandations"] = score.recommendations or []

        return ctx

    def _fill_template(self, template: str, context: dict) -> str:
        """Remplacement basique des variables {{ var }} dans le template."""

        def replace_var(match):
            key = match.group(1).strip()
            return str(context.get(key, f"[{key}]"))

        return re.sub(r"\{\{\s*(\w+)\s*\}\}", replace_var, template)

    def _parse_sections(self, text: str) -> Optional[dict]:
        """Détecte les sections numérotées dans le texte généré."""
        sections = []
        pattern = r"(?:^|\n)(\d+\.\s+[^\n]+)\n([^\n]*(?:\n(?!(?:\d+\.\s+|\n))[^\n]*)*)"
        for match in re.finditer(pattern, text):
            sections.append({
                "title": match.group(1).strip(),
                "content": match.group(2).strip(),
            })
        return {"sections": sections} if sections else None
