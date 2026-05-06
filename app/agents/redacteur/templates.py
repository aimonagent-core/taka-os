"""Gestion des templates de réponse par Business Line."""
import logging
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao_s2 import AO
from app.models.response import ResponseTemplate

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATES = {
    "letter": {
        "name": "Lettre de candidature",
        "description": "Lettre de motivation et présentation de l'entreprise",
        "system_prompt": """Tu es un expert en réponse à appels d'offres publics.
Rédige une lettre de candidature professionnelle, concise (max 1 page), structurée :
1. Objet de la candidature
2. Présentation de l'entreprise et de son expertise sur le CPV concerné
3. Motivation et alignement avec le besoin
4. Engagement sur les délais et la qualité
5. Formule de politesse
Utilise un ton professionnel mais chaleureux.""",
        "template_content": """{{ acheteur }}
{{ adresse_acheteur }}

Objet : Candidature à l'appel d'offres n° {{ reference_ao }} — {{ titre_ao }}

Madame, Monsieur,

Nous soumettons notre candidature pour l'appel d'offres portant sur "{{ titre_ao }}".

Notre entreprise, {{ nom_entreprise }}, dispose d'une expertise reconnue dans le domaine {{ domaine }} (CPV {{ cpv }}). Nous avons réalisé {{ nb_references }} marchés similaires ces 3 dernières années, pour un montant total de {{ montant_total }} €.

Nous sommes particulièrement motivés par ce projet car {{ motivation }}. Notre proposition technique s'appuie sur {{ atout_technique }}.

Nous nous engageons à respecter les délais fixés ({{ delai }}) et à garantir la qualité des prestations conformément aux référentiels en vigueur.

Dans l'attente de votre réponse, nous vous prions d'agréer, Madame, Monsieur, l'expression de nos salutations distinguées.

{{ signature }}
{{ contact }}
""",
    },
    "technical": {
        "name": "Dossier technique",
        "description": "Note technique détaillant la méthodologie et les moyens",
        "system_prompt": """Tu es un chef de projet technique spécialisé dans les appels d'offres.
Rédige une note technique structurée :
1. Compréhension du besoin
2. Méthodologie de réalisation (phases, livrables)
3. Moyens humains et techniques mobilisés
4. Planning prévisionnel
5. Gestion des risques et assurance qualité
6. Références significatives
Sois factuel, précis, et démontre la faisabilité.""",
        "template_content": """1. COMPRÉHENSION DU BESOIN
{{ titre_ao }}
Le présent marché vise à {{ description_resume }}.

2. MÉTHODOLOGIE
Phase 1 — Lancement et diagnostic (semaines 1-2)
Phase 2 — Réalisation des prestations (semaines 3-{{ delai_semaines }})
Phase 3 — Recette et livraison (dernières semaines)

3. MOYENS MOBILISÉS
- Chef de projet : {{ chef_projet }}
- Équipe technique : {{ equipe }}
- Outils et matériels : {{ moyens }}

4. PLANNING
{{ planning }}

5. ASSURANCE QUALITÉ ET RISQUES
{{ qualite }}

6. RÉFÉRENCES
{{ references }}
""",
    },
    "financial": {
        "name": "Offre financière",
        "description": "Détail du prix et de la répartition",
        "system_prompt": """Tu es un directeur financier. Rédige une offre financière claire avec un détail des postes de dépenses, une ventilation du prix, et une justification de la cohérence avec le montant estimé de l'AO.""",
        "template_content": """DÉTAIL DE L'OFFRE FINANCIÈRE

Montant total HT : {{ montant_ht }} €
TVA ({{ tva }}%) : {{ montant_tva }} €
Montant total TTC : {{ montant_ttc }} €

VENTILATION DES POSTES :
- Prestations techniques : {{ prestations }} €
- Fournitures et matériels : {{ fournitures }} €
- Frais de déplacement et logistique : {{ deplacements }} €
- Assurance et garanties : {{ assurance }} €
- Marge et frais généraux : {{ marge }} €

JUSTIFICATION :
Notre offre est établie sur la base d'une analyse détaillée du CDC. Le montant proposé est cohérent avec les moyens techniques et humains mobilisés.
""",
    },
    "administrative": {
        "name": "Pièces administratives",
        "description": "Liste et résumé des pièces administratives requises",
        "system_prompt": """Liste les pièces administratives typiquement requises pour une candidature à un AO public dans le secteur concerné. Ne génère pas de contenu fictif.""",
        "template_content": """PIÈCES ADMINISTRATIVES À FOURNIR :

1. Justificatifs d'identité et de capacité juridique
   - Kbis de moins de 3 mois
   - Attestation d'inscription au répertoire des métiers (si applicable)

2. Justificatifs de capacité financière
   - Attestation d'assurance responsabilité civile
   - Attestation d'assurance décennale (si BTP)
   - Bilan comptable des 3 derniers exercices

3. Justificatifs de capacité technique
   - Certifications ISO 9001, ISO 14001 (si requis)
   - Références clients sur 3 ans
   - CV des personnels clés

4. Déclarations sur l'honneur
   - Non-condamnation
   - Non-faillite
   - Respect des obligations fiscales et sociales
""",
    },
}


class TemplateService:
    """Service de gestion des templates de réponse."""

    @staticmethod
    async def get_or_create_defaults(db: AsyncSession, tenant_id: str) -> list[ResponseTemplate]:
        """Crée les templates par défaut si aucun n'existe pour le tenant."""
        stmt = select(ResponseTemplate).where(
            and_(ResponseTemplate.tenant_id == tenant_id, ResponseTemplate.is_active.is_(True))
        )
        rows = await db.execute(stmt)
        existing = rows.scalars().all()
        if existing:
            return existing

        templates = []
        for category, data in DEFAULT_TEMPLATES.items():
            t = ResponseTemplate(
                tenant_id=tenant_id,
                name=data["name"],
                description=data["description"],
                category=category,
                template_content=data["template_content"],
                system_prompt=data["system_prompt"],
                is_default=True,
            )
            db.add(t)
            templates.append(t)

        await db.commit()
        for t in templates:
            await db.refresh(t)
        logger.info("[Templates] %s templates par défaut créés pour tenant=%s", len(templates), tenant_id)
        return templates

    @staticmethod
    async def get_for_ao(
        db: AsyncSession,
        ao: AO,
        category: str = "letter",
        fallback_tenant_id: Optional[str] = None,
    ) -> ResponseTemplate:
        """
        Retourne le meilleur template pour un AO donné.
        Priorité : BL spécifique > template par défaut du tenant.
        Args:
            ao: L'AO à rédiger
            category: 'letter', 'technical', 'financial', 'administrative'
            fallback_tenant_id: tenant_id explicite si ao n'a pas de BL
        """
        # --- Priorité 1 : template spécifique à la Business Line de l'AO ---
        if ao.business_line_id:
            stmt = select(ResponseTemplate).where(
                ResponseTemplate.business_line_id == ao.business_line_id,
                ResponseTemplate.category == category,
                ResponseTemplate.is_active == True,
            )
            rows = await db.execute(stmt)
            bl_template = rows.scalar_one_or_none()
            if bl_template:
                return bl_template

            # Si BL présente mais pas de template spécifique, utiliser le tenant
            # de la BL comme fallback
            from app.models.business_line import BusinessLine
            stmt_bl = select(BusinessLine).where(BusinessLine.id == ao.business_line_id)
            row_bl = await db.execute(stmt_bl)
            bl = row_bl.scalar_one_or_none()
            if bl:
                fallback_tenant_id = str(bl.tenant_id)

        # --- Priorité 2 : template par défaut du tenant ---
        tenant_id = fallback_tenant_id
        if not tenant_id:
            # Dernier recours : impossible de déterminer le tenant
            raise ValueError(
                f"AO {ao.id} n'a pas de Business Line et aucun tenant_id "
                f"fourni. Impossible de sélectionner un template."
            )

        stmt = select(ResponseTemplate).where(
            ResponseTemplate.tenant_id == tenant_id,
            ResponseTemplate.category == category,
            ResponseTemplate.is_default == True,
            ResponseTemplate.is_active == True,
        )
        rows = await db.execute(stmt)
        default_template = rows.scalar_one_or_none()
        if default_template:
            return default_template

        # --- Priorité 3 : créer les templates par défaut pour ce tenant ---
        defaults = await TemplateService.get_or_create_defaults(db, tenant_id)
        for d in defaults:
            if d.category == category:
                return d

        raise ValueError(f"Aucun template trouvé pour category={category}, tenant={tenant_id}")
