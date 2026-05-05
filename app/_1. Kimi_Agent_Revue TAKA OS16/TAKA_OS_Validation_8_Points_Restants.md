# TAKA OS — Validation Conceptuelle : 8 Points Critiques de Robustesse

**Version** : 1.0 — **Date** : 2025-01 — **Statut** : Valide a l'usage interne

---

# POINT 1 — i18n / MULTI-PAYS (FR/NL/EN/AR)

## 1.1 Cadre multi-pays

TAKA OS cible 3 pays avec des exigences distinctes :

**France** : Langue FR. Portails : BOAMP, TED, e-marchespublics. Cadre legal : Code des marches publics, AI Act, RGPD.
**Belgique** : Langues FR + NL. Portails : e-AWB, e-Proc, TED. Cadre legal : Loi WB 15/12/2013, RGPD, APD.
**Maroc** : Langues FR + AR. Portails : PORTNET, TED. Cadre legal : Decret 2-12-349, loi 09-08 (donnees).

## 1.2 Architecture i18n — Backend

```python
# backend/core/i18n.py
import json
from pathlib import Path
from babel import Locale
from fastapi import Request

class I18nService:
    def __init__(self, locales_dir: Path = Path("locales")):
        self.translations = {}
        self.fallback_chain = ["fr_BE", "fr", "en"]
        for f in locales_dir.glob("*.json"):
            self.translations[f.stem] = json.load(f.open())

    def resolve_locale(self, request: Request) -> str:
        if (p := request.query_params.get("lang")) and p in self.translations:
            return p
        for lang in request.headers.get("Accept-Language", "fr").split(","):
            code = lang.split(";")[0].strip().replace("-", "_")
            if code in self.translations:
                return code
        return "fr"

    def t(self, key: str, locale: str = "fr", **kwargs) -> str:
        msg = self.translations.get(locale, {}).get(key, key)
        try:
            return msg.format(**kwargs)
        except KeyError:
            return msg

    def format_date(self, d, locale: str = "fr") -> str:
        return d.strftime("%d/%m/%Y") if locale.startswith("fr") else d.strftime("%Y/%m/%d")

    def format_currency(self, amount: float, currency: str = "EUR", locale: str = "fr") -> str:
        s = {"EUR": "\u20ac", "MAD": "MAD"}
        sym = s.get(currency, currency)
        return f"{amount:,.2f} {sym}".replace(",", " ").replace(".", ",") if locale == "fr" else f"{sym} {amount:,.2f}"
```

## 1.3 Architecture i18n — Frontend

```typescript
// frontend/src/i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import ICU from 'i18next-icu';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n.use(HttpBackend).use(LanguageDetector).use(ICU).use(initReactI18next).init({
  fallbackLng: 'fr',
  supportedLngs: ['fr', 'fr_BE', 'nl', 'nl_BE', 'en', 'ar'],
  ns: ['common', 'dashboard', 'kanban', 'qualification', 'errors'],
  defaultNS: 'common',
  backend: { loadPath: '/locales/{{lng}}/{{ns}}.json' },
  detection: { order: ['localStorage', 'navigator', 'querystring'], caches: ['localStorage'] },
});

// frontend/src/hooks/useDirection.ts
const RTL_LOCALES = ['ar', 'ar_MA'];
export function useDirection() {
  const { i18n } = useTranslation();
  const isRTL = RTL_LOCALES.includes(i18n.language);
  useEffect(() => { document.documentElement.dir = isRTL ? 'rtl' : 'ltr'; }, [isRTL, i18n.language]);
  return { isRTL, direction: isRTL ? 'rtl' : 'ltr' as const };
}
```

Exemple de fichier de traduction ICU avec pluriels complexes :

```json
{
  "fr/dashboard.json": {
    "ao_detected": "{count, plural, one {1 AO detecte} other {# AO detectes}}",
    "score_display": "Score : {score}%",
    "deadline_approaching": "{days, plural, one {J-1} other {J-#}} — Deadline proche"
  },
  "nl/dashboard.json": {
    "ao_detected": "{count, plural, one {1 AO gedetecteerd} other {# AO's gedetecteerd}}",
    "score_display": "Score: {score}%"
  },
  "ar/dashboard.json": {
    "ao_detected": "{count, plural, zero {لا يوجد طلب عروض} one {طلب عروض واحد} other {# طلب عروض}}",
    "score_display": "النتيجة: {score}%"
  }
}
```

## 1.4 Configuration YAML des locales

```yaml
# config/i18n.yaml
locales:
  fr:
    name: "Francais"; direction: "ltr"; date_format: "DD/MM/YYYY"
    currency: "EUR"; first_day_of_week: 1; weekend_days: [6, 7]
    portals: ["BOAMP", "TED", "e-marchespublics"]
    legal_framework: "code_marches_publics_FR"
  fr_BE:
    parent: "fr"; currency: "EUR"; first_day_of_week: 1
    portals: ["e-AWB", "e-Proc", "TED"]
    legal_framework: "loi_relative_marches_publics_BE"
  nl:
    name: "Nederlands"; direction: "ltr"; date_format: "DD-MM-YYYY"
    currency: "EUR"; first_day_of_week: 1
  nl_BE:
    parent: "nl"; currency: "EUR"
    portals: ["e-AWB", "e-Proc", "TED"]
  ar:
    name: "Arabiya"; direction: "rtl"; date_format: "YYYY/MM/DD"
    currency: "MAD"; first_day_of_week: 6; weekend_days: [5, 6]
    portals: ["PORTNET", "TED"]
    legal_framework: "decret_marches_publics_MA"
    hijri_calendar: true
default_locale: "fr"
fallback_chain: ["fr_BE", "fr", "en"]
```

## 1.5 Middleware FastAPI pour locale

```python
# backend/middleware/i18n_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class I18nMiddleware(BaseHTTPMiddleware):
    """Injecte la locale dans le state de chaque requete."""
    async def dispatch(self, request: Request, call_next):
        locale = i18n_service.resolve_locale(request)
        request.state.locale = locale
        request.state.i18n = lambda key, **kw: i18n_service.t(key, locale, **kw)
        response = await call_next(request)
        response.headers["Content-Language"] = locale
        return response

# Utilisation dans les endpoints
@router.get("/tenders")
async def list_tenders(request: Request):
    _ = request.state.i18n
    tenders = await get_tenders()
    return {"message": _("tenders.count", count=len(tenders)), "data": tenders}
```

## 1.6 Structure des fichiers de traduction

```
public/locales/
├── fr/
│   ├── common.json       (boutons, libelles generiques)
│   ├── dashboard.json    (widgets KPIs)
│   ├── kanban.json       (pipeline stages, actions)
│   ├── qualification.json (scoring, dimensions, verdicts)
│   ├── errors.json       (messages d'erreur API)
│   └── emails.json       (templates notifications)
├── nl/
│   ├── common.json
│   ├── dashboard.json
│   └── ...
└── ar/
    ├── common.json
    └── ...
```

Chaque namespace est charge paresseusement via `i18next-http-backend` pour minimiser
le bundle initial. Le namespace `common` est precharge ; les autres sont charges a la
navigation vers la page concernee.

## 1.7 Adaptations specifiques

**Belgique — Bilinguisme** : composant `LanguageSwitcher` toujours visible, documents generes
en FR et NL pour les marches federaux, gestion des attestations ONSS et Banque-Carrefour.

**Maroc — RTL** : direction `rtl` pour l'interface arabe via CSS logical properties, documents
FR+AR, connecteur PORTNET, conversion EUR/MAD via API Bank Al-Maghrib, week-end vendredi-samedi.

```python
# backend/core/morocco_adapter.py
class MoroccoAdapter:
    def is_weekend(self, dt) -> bool:
        return dt.weekday() in (4, 5)  # Vendredi, samedi
    def add_business_days(self, start, days: int):
        current, added = start, 0
        while added < days:
            current += timedelta(days=1)
            if not self.is_weekend(current): added += 1
        return current
```

## 1.6 Table PostgreSQL pour traductions dynamiques

```sql
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    entity_type VARCHAR(50) NOT NULL, entity_id UUID NOT NULL,
    field_name VARCHAR(100) NOT NULL, locale VARCHAR(10) NOT NULL,
    content TEXT NOT NULL, is_auto_translated BOOLEAN DEFAULT false,
    UNIQUE(tenant_id, entity_type, entity_id, field_name, locale)
);
CREATE INDEX idx_translations_lookup ON translations(tenant_id, entity_type, entity_id, locale);
```

## 1.7 Phasing

| Version | i18n | Pays |
|---------|------|------|
| v0.1 | FR | France |
| v0.2 | FR + EN | France + Belgique (FR) |
| v0.5 | FR + NL + EN | France + Belgique complet |
| v1.0 | FR + NL + EN + AR | France + Belgique + Maroc |

---

# POINT 2 — ACCESSIBILITE RGAA (OBLIGATION LEGALE)

## 2.1 Contexte legal

Le RGAA est **obligatoire** en France pour les services publics en ligne, les grandes entreprises
(>250 salaries), et les structures donnant acces a des services essentiels. Sanction : 5 000 EUR
d'amende par service inaccessible (article 47 loi 2005-102). Produit non accessible = risque de
disqualification sur les marches publics.

RGAA = WCAG 2.1 AA avec 13 thematiques : (1) Images, (2) Multimedia, (3) Structuration,
(4) Presentation, (5) Tableaux, (6) Liens, (7) Navigation, (8) Consultation, (9) Formulaires,
(10) Controle de saisie, (11) Securite financiere, (12) Formulaires a etapes,
(13) Documents telechargeables.

## 2.2 Implementation technique

```tsx
// Skip link
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50
   focus:bg-primary focus:px-4 focus:py-2 focus:rounded-md">
  Aller au contenu principal
</a>

// Bouton accessible
<Button aria-label="Qualifier cet appel d'offres" aria-describedby="ao-description">
  Qualifier
</Button>

// Modal avec focus trap et aria-modal
<Dialog role="dialog" aria-modal="true" aria-labelledby="modal-title"
        aria-describedby="modal-description">...</Dialog>

// Kanban accessible avec aria-live
<div aria-live="polite" aria-atomic="true" className="sr-only">{moveAnnouncement}</div>
```

Tests d'accessibilite avec axe-core en CI :

```typescript
// frontend/src/tests/a11y/Dashboard.a11y.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

describe('Dashboard — RGAA', () => {
  it('pas de violations critiques', async () => {
    const { container } = render(<Dashboard />);
    expect(await axe(container)).toHaveNoViolations();
  });
  it('KPIs avec role=status et aria-label', () => {
    const els = screen.getAllByRole('status');
    els.forEach(el => expect(el).toHaveAttribute('aria-label'));
  });
});
```

## 2.3 Palette de couleurs accessible

```css
:root {
  --primary: #1a56db;      /* Ratio blanc: 5.8:1 */
  --success: #057a55;      /* Ratio blanc: 5.2:1 */
  --warning: #b45309;      /* Ratio blanc: 4.6:1 */
  --danger: #dc2626;       /* Ratio blanc: 5.4:1 */
  --text-primary: #111827; /* Ratio blanc: 15.8:1 */
  --text-secondary: #4b5563;
}
*:focus-visible { outline: 3px solid var(--primary); outline-offset: 2px; }
```

## 2.4 Composant de vérification de contraste

```typescript
// frontend/src/components/a11y/ColorContrastChecker.tsx
import { hex, score } from 'wcag-contrast';

const PALETTE = {
  primary: '#1a56db', success: '#057a55', warning: '#b45309',
  danger: '#dc2626', textPrimary: '#111827', textSecondary: '#4b5563',
  bgPrimary: '#ffffff', bgSecondary: '#f9fafb',
};

export function ColorContrastChecker() {
  const checks = [
    ['textPrimary', 'bgPrimary'], ['textSecondary', 'bgPrimary'],
    ['primary', 'bgPrimary'], ['success', 'bgSecondary'],
    ['danger', 'bgSecondary'], ['warning', 'bgSecondary'],
  ];
  return (
    <div role="region" aria-label="Verificateur de contraste">
      {checks.map(([fg, bg]) => {
        const ratio = hex(PALETTE[fg], PALETTE[bg]);
        const grade = score(ratio);
        const pass = grade === 'AAA' || grade === 'AA';
        return (
          <div key={`${fg}-${bg}`} className={`flex gap-2 ${pass ? 'text-green-700' : 'text-red-700'}`}>
            <span>{fg} sur {bg}: {ratio}:1 ({grade})</span>
          </div>
        );
      })}
    </div>
  );
}
```

Verification automatisee en CI :

```yaml
# .github/workflows/a11y.yml
name: Accessibilite RGAA
on: [push, pull_request]
jobs:
  test-a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run test:a11y
      - run: npm run lighthouse:ci
      - uses: actions/upload-artifact@v4
        if: failure()
        with: { name: rapport-a11y, path: reports/a11y/ }
```

## 2.5 Checklist RGAA par page

**Page Login** : labels associes (11.1), erreurs liees aux champs (11.2), boutons explicites (6.1),
focus visible (10.7), titre descriptif (3.1).

**Page Dashboard** : KPIs avec `role="status"` (1.2), graphiques avec alternative textuelle (1.3),
pas d'info par couleur seule (4.1), notifications `aria-live` (6.2), navigation `role="navigation"` (7.1).

**Page Kanban** : cartes deplacables au clavier (6.1), annulation Ctrl+Z (10.8), grille `role="grid"` (5.1).

**Page Qualification** : sliders avec `aria-valuemin/max/now` (9.1), verdict GO/NO-GO avec couleur+icone+texte (4.1),
formulaire a etapes avec progression (12.1).

## 2.5 Phasing

| Version | Niveau | Actions |
|---------|--------|---------|
| v0.1 | A | Labels, contraste, navigation clavier, skip link |
| v0.3 | AA | Tous criteres sauf 11; audit externe |
| v0.5 | AA complet | Certification RGAA AA, declaration publiee |
| v1.0 | AAA (partiel) | Audio description, langue des signes |

---

# POINT 3 — FEATURE FLAGS / OPEN CORE

## 3.1 Modele de donnees

```python
# backend/models/feature_flag.py
class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(String(20), default="tenant")
    default_value: Mapped[bool] = mapped_column(default=False)
    min_plan: Mapped[str] = mapped_column(String(20), default="free")
    introduced_in: Mapped[str] = mapped_column(String(10))
    is_active: Mapped[bool] = mapped_column(default=True)  # Kill switch
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

class TenantFeatureOverride(Base):
    __tablename__ = "tenant_feature_overrides"
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    flag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("feature_flags.id"))
    override_value: Mapped[bool] = mapped_column(Boolean, nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    overridden_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    __table_args__ = (UniqueConstraint("tenant_id", "flag_id"),)
```

```sql
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL, name VARCHAR(255) NOT NULL,
    description TEXT, scope VARCHAR(20) DEFAULT 'tenant',
    default_value BOOLEAN DEFAULT false,
    min_plan VARCHAR(20) DEFAULT 'free',
    introduced_in VARCHAR(10), is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}', created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE tenant_feature_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    flag_id UUID NOT NULL REFERENCES feature_flags(id) ON DELETE CASCADE,
    override_value BOOLEAN, reason TEXT, overridden_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, flag_id)
);
```

## 3.2 Configuration YAML

```yaml
features:
  basic_dashboard:       { scope: tenant, min_plan: free,  since: v0.1 }
  manual_upload:         { scope: tenant, min_plan: free,  since: v0.1 }
  basic_qualification:   { scope: tenant, min_plan: free,  since: v0.1, meta: { max_ao: 10 } }
  kanban_basic:          { scope: tenant, min_plan: free,  since: v0.1 }
  advanced_dashboard:    { scope: tenant, min_plan: starter, since: v0.2 }
  veille_boamp:          { scope: tenant, min_plan: starter, since: v0.2 }
  qualification_5d:      { scope: tenant, min_plan: starter, since: v0.4, meta: { max_ao: 50 } }
  memory_episodic:       { scope: tenant, min_plan: starter, since: v0.2 }
  veille_multi_portals:  { scope: tenant, min_plan: pro,    since: v0.2 }
  taka_lab:              { scope: tenant, min_plan: pro,    since: v0.4 }
  parliament:            { scope: tenant, min_plan: pro,    since: v0.3 }
  redaction_memoire:     { scope: tenant, min_plan: pro,    since: v0.5, meta: { max_ao: 500 } }
  integrations_crm:      { scope: tenant, min_plan: pro,    since: v1.0 }
  taka_vision:           { scope: tenant, min_plan: enterprise, since: v1.2 }
  business_lines:        { scope: tenant, min_plan: enterprise, since: v0.5 }
  sso_ldap:              { scope: tenant, min_plan: enterprise, since: v1.0 }
  api_access:            { scope: tenant, min_plan: enterprise, since: v1.0 }
  white_label:           { scope: tenant, min_plan: enterprise, since: v1.0 }
  dedicated_support:     { scope: tenant, min_plan: enterprise, since: v0.5 }
```

## 3.3 Modele Open Core

**Core (MIT, gratuit)** : EventBus, Auth, RBAC, Audit, Memory limitee (50 souvenirs), upload manuel,
qualification basique, kanban 5 stages, dashboard basique.

**Proprietaire (payant)** : Veille multi-portails, scoring 5D, TAKA LAB, Parlement d'agents,
TAKA Vision, redaction IA, integrations CRM/ERP, multi-metiers, SSO/LDAP, support SLA.

**Plugins premium (marketplace)** : Connecteurs Peppol/EBICS, templates documentaires, audits conformite.

## 3.4 Service de gating

```python
class FeatureFlagService:
    async def is_enabled(self, tenant_id: uuid.UUID, flag_key: str) -> bool:
        flag = await self._get_flag(flag_key)
        if not flag or not flag.is_active: return False
        tenant = await self._get_tenant(tenant_id)
        plans = {"free": 0, "starter": 1, "pro": 2, "enterprise": 3}
        if plans.get(tenant.plan, 0) < plans.get(flag.min_plan, 0): return False
        override = await self._get_tenant_override(tenant_id, flag.id)
        return override if override is not None else flag.default_value
```

```python
# Endpoint avec gating
@router.post("/tenders/{id}/qualify-5d")
async def qualify_5d(tender_id: uuid.UUID, flag_service: FeatureFlagService = Depends()):
    if not await flag_service.is_enabled(current_user.tenant_id, "qualification_5d"):
        raise HTTPException(status_code=403, detail="Plan Starter requis")
```

```typescript
// Frontend
const { isEnabled } = useFeatureFlags();
{isEnabled('qualification_5d') && <Qualification5DPanel />}
```

## 3.5 Notification kill switch

```python
# backend/services/notifications/kill_switch_alerts.py
import httpx

async def notify_kill_switch_slack(webhook_url: str, flag_key: str, action: str,
                                   reason: str, changed_by: str) -> None:
    payload = {
        "text": f"[TAKA OS] Kill Switch {action}",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": f"Kill Switch {action}: {flag_key}"}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*Feature:* {flag_key}"},
                {"type": "mrkdwn", "text": f"*Par:* {changed_by}"},
            ]},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Raison:* {reason}"}},
        ],
    }
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=payload, timeout=10)
```

## 3.6 Kill switch

Desactivation instantanee sans deploiement. Panel editeur ou API d'urgence. Notification Slack
automatique a l'equipe.

## 3.6 Phasing

| Version | Feature Flags |
|---------|--------------|
| v0.1 | Infra + 4 flags gratuits |
| v0.2 | + flags Starter |
| v0.3 | + flags Pro (debut) |
| v0.4 | Qualification 5D + TAKA LAB |
| v0.5 | + flags Enterprise (debut) |
| v1.0 | Tous les flags actifs |
| v1.2 | TAKA Vision |

---

# POINT 4 — DOCUMENTATION UTILISATEUR

## 4.1 Architecture a trois niveaux

**Niveau 1 — In-app** : tooltips contextuels, boutons "?", empty states pedagogiques,
tours guides (driver.js), bannieres informatives.

**Niveau 2 — Help Center** : Docusaurus sur `docs.takaos.fr`, guides par role, FAQ,
videos tutorielles, changelog versionne.

**Niveau 3 — API Docs** : Swagger UI sur `developers.takaos.fr`, collections Postman,
SDK Python/JS, documentation webhooks.

## 4.2 Tours guides

```typescript
import { driver, DriveStep } from 'driver.js';
const STEPS: DriveStep[] = [
  { element: '#dashboard-stats', popover: { title: 'Bienvenue', description: 'Vos indicateurs cles.' } },
  { element: '#upload-dce-button', popover: { title: 'Uploader', description: 'Importez votre premier DCE.' } },
  { element: '#qualification-panel', popover: { title: 'Scoring 5D', description: 'Qualification automatique.' } },
  { element: '#kanban-board', popover: { title: 'Kanban', description: 'Suivez vos AO.' } },
];
```

## 4.3 Videos tutorielles

| Video | Duree | Public |
|-------|-------|--------|
| TAKA OS en 5 minutes | 5 min | Prospect |
| Onboarding complet | 15 min | Nouvel utilisateur |
| Qualifier un AO | 8 min | Soumissionnaire |
| Configurer la veille | 6 min | Admin |
| Comprendre le scoring 5D | 12 min | Admin |
| API et Webhooks | 10 min | Developpeur |

## 4.4 Phasing

| Version | Documentation |
|---------|--------------|
| v0.1 | README + Swagger + tooltips |
| v0.2 | Help Center v1 (10 guides) |
| v0.3 | Tours guides + 20 guides + 5 videos |
| v0.5 | Help Center complet + API docs + SDK |
| v1.0 | i18n FR/NL/EN/AR |

---

# POINT 5 — MEMOIRE PERSISTANTE (ETAT CANONIQUE)

## 5.1 Principe

L'etat canonique est la source de verite unique persistante en dehors du contexte LLM.
Cycle agent : lit l'etat depuis PostgreSQL -> appelle LLM -> ecrit nouvel etat -> continue.

5 types de memoire : global (config systeme), tenant (donnees metier), episodique (evenements),
semantique (graphe de connaissances), procedurale (SOPs).

## 5.2 Memoire episodique

```python
class EpisodicMemory(Base):
    __tablename__ = "memory_episodic"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    tender_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("tenders.id"))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Optional[any]] = mapped_column(VECTOR(768))
    cpv_code: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    amount_range: Mapped[Optional[str]] = mapped_column(String(20))
    outcome: Mapped[str] = mapped_column(String(20))
    key_learning: Mapped[Optional[str]] = mapped_column(Text)
    importance: Mapped[float] = mapped_column(default=1.0)
    access_count: Mapped[int] = mapped_column(default=0)
    ttl_days: Mapped[Optional[int]]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
```

Recuperation par similarite cosinus :

```python
async def retrieve_similar(self, tenant_id, query_text, cpv_code=None, limit=5):
    emb = await self.embedding.embed(query_text)
    sql = """SELECT *, 1 - (embedding <=> :emb) AS sim FROM memory_episodic
             WHERE tenant_id = :t AND (embedding <=> :emb) < :max_dist"""
    if cpv_code: sql += " AND cpv_code = :cpv"
    sql += " ORDER BY embedding <=> :emb LIMIT :limit"
    return await self.session.execute(text(sql), {"emb": str(emb), "t": str(tenant_id),
        "max_dist": 0.3, "cpv": cpv_code, "limit": limit})
```

## 5.3 Memoire semantique

```python
class SemanticMemory(Base):
    __tablename__ = "memory_semantic"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[str] = mapped_column(String(100))
    entity_name: Mapped[str] = mapped_column(String(255))
    relations: Mapped[dict] = mapped_column(JSONB, default=dict)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)
    embedding: Mapped[Optional[any]] = mapped_column(VECTOR(768))
    source: Mapped[str] = mapped_column(default="learned")
    confidence: Mapped[float] = mapped_column(default=1.0)
```

Avec Neo4j (v1.1+) :

```cypher
CREATE (c:CPV {code: "45233200", name: "Travaux de construction"})
MATCH (c1:CPV {code: "45233200"}), (c2:CPV {code: "45233210"})
CREATE (c1)-[:IS_PARENT_OF]->(c2)
MATCH (c:CPV {code: "45233200"})-[:IS_SIMILAR_TO|IS_PARENT_OF*1..2]-(s:CPV)
RETURN s.code, s.name LIMIT 10
```

## 5.4 Memoire procedurale

Stocke les SOPs (Standard Operating Procedures) comme sequences d'etapes JSONB.
Source : "learned" (extrait des actions reussies), "manual" (saisie admin), "imported".

```python
class ProceduralMemory(Base):
    __tablename__ = "memory_procedural"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50), index=True)
    triggers: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    steps: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    source: Mapped[str] = mapped_column(default="learned")
    success_rate: Mapped[Optional[float]]
    usage_count: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
```

## 5.5 Oubli selectif

```python
class MemoryForgettingService:
    async def forget_expired(self, tenant_id):
        """Supprime les souvenirs dont le TTL est depasse."""
        ...
    async def decay_low_importance(self, tenant_id):
        """importance *= 0.95 ^ jours depuis dernier acces. Si < 0.1, archive."""
        ...
    async def consolidate_similar(self, tenant_id):
        """Si 5+ souvenirs meme CPV + meme resultat -> fusion en souvenir consolide."""
        ...
```

## 5.6 Schema SQL

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE memory_episodic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID NOT NULL,
    event_type VARCHAR(50), tender_id UUID, content TEXT NOT NULL,
    embedding VECTOR(768), cpv_code VARCHAR(20), amount_range VARCHAR(20),
    outcome VARCHAR(20), key_learning TEXT, importance FLOAT DEFAULT 1.0,
    access_count INTEGER DEFAULT 0, ttl_days INTEGER, created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_episodic_tenant ON memory_episodic(tenant_id);
CREATE INDEX idx_episodic_embedding ON memory_episodic USING ivfflat (embedding vector_cosine_ops);

CREATE TABLE memory_semantic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID NOT NULL,
    entity_type VARCHAR(50), entity_id VARCHAR(100), entity_name VARCHAR(255),
    relations JSONB, properties JSONB, embedding VECTOR(768),
    source VARCHAR(20), confidence FLOAT DEFAULT 1.0, created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE memory_procedural (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID NOT NULL,
    name VARCHAR(255), category VARCHAR(50), triggers VARCHAR(100)[],
    steps JSONB, source VARCHAR(20), success_rate FLOAT, usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true, created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE memory_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), category VARCHAR(50),
    key VARCHAR(255) UNIQUE, value JSONB, description TEXT, created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE memory_tenant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID NOT NULL,
    category VARCHAR(50), key VARCHAR(255), value JSONB,
    UNIQUE(tenant_id, category, key)
);
```

## 5.7 Phasing

| Version | Memoire |
|---------|---------|
| v0.1 | Episodique basique (50 souvenirs) |
| v0.2 | + pgvector embeddings |
| v0.3 | + Semantic (JSONB) |
| v0.4 | + Procedural |
| v0.5 | Oubli selectif |
| v1.0 | Global + Tenant |
| v1.1 | Neo4j optionnel |

---

# POINT 6 — VALIDATION AVANT COMMIT (N GATES)

## 6.1 Pipeline a N gates

Chaque action traverse sequentiellement :
1. **Syntaxe** — JSON valide, champs requis, types corrects
2. **Semantique** — CPV valide, montant > 0, deadline dans le futur
3. **RBAC** — permissions, scope business line, quota plan
4. **Idempotence** — cle d'idempotence ou hash SHA-256
5. **Deterministe** — linting, analyse statique (bandit), sandbox Docker (timeout 10s)
6. **Human-in-the-loop** — si confiance < 0.7 ou action critique

## 6.2 Implementation

```python
class ValidationGate(ABC):
    @abstractmethod
    async def validate(self, action: AgentAction, ctx: ValidationContext) -> GateResult: ...

class SyntaxGate(ValidationGate):
    name = "syntax"
    async def validate(self, action, ctx):
        if not action.action_type or action.action_type not in self._allowed(): return failed("action_type invalide")
        if not isinstance(action.payload, dict): return failed("payload non-objet")
        return passed()

class SemanticGate(ValidationGate):
    name = "semantic"
    async def validate(self, action, ctx):
        if "amount" in action.payload and action.payload["amount"] <= 0: return failed("Montant positif requis")
        if "deadline" in action.payload:
            d = date.fromisoformat(action.payload["deadline"])
            if d < date.today(): return failed("Deadline dans le futur requise")
        return passed()

class RBACGate(ValidationGate):
    name = "rbac"
    PERM_MAP = {"qualify_tender": "tenders:qualify", "update_scoring": "scoring:manage",
                "export_data": "data:export", "invite_user": "users:invite"}
    async def validate(self, action, ctx):
        perm = self.PERM_MAP.get(action.action_type)
        if perm and not await ctx.check_permission(perm): return failed(f"Permission {perm} requise")
        return passed()

class IdempotenceGate(ValidationGate):
    name = "idempotence"
    async def validate(self, action, ctx):
        h = sha256(action.to_json().encode()).hexdigest()
        if await ctx.is_duplicate(h): return failed("Action deja executee")
        return passed(metadata={"hash": h})

class DeterministicGate(ValidationGate):
    name = "deterministic"
    async def validate(self, action, ctx):
        if not action.generated_code: return skipped()
        # Linting
        if action.code_language == "python":
            r = subprocess.run(["python", "-m", "py_compile", "-"], input=action.generated_code,
                             capture_output=True, text=True, timeout=5)
            if r.returncode != 0: return failed(f"Syntaxe: {r.stderr}")
        # Securite
        for p in ["os.system", "eval(", "exec(", "__import__", "subprocess"]:
            if p in action.generated_code: return failed(f"Pattern dangereux: {p}")
        # Sandbox Docker
        r = await run_sandbox(action.generated_code)
        if r["returncode"] != 0: return failed(f"Sandbox: {r['stderr']}")
        return passed()

class HILGate(ValidationGate):
    name = "human_in_the_loop"
    CRITICAL = {"delete_tender", "export_data", "invite_user", "depot_portail"}
    THRESHOLD = 0.70
    async def validate(self, action, ctx):
        if action.action_type in self.CRITICAL or action.confidence_score < self.THRESHOLD:
            aid = await ctx.request_approval(action, f"Confiance: {action.confidence_score:.0%}")
            return pending_approval(aid)
        return passed()
```

Orchestrateur du pipeline :

```python
class ValidationPipeline:
    def __init__(self):
        self.gates = [SyntaxGate(), SemanticGate(), RBACGate(),
                      IdempotenceGate(), DeterministicGate(), HILGate()]
    async def execute(self, action, ctx) -> PipelineResult:
        for gate in self.gates:
            r = await gate.validate(action, ctx)
            if r.status == FAILED: return PipelineResult(success=False, failed_gate=gate.name, reason=r.reason)
            if r.status == PENDING: return PipelineResult(success=True, pending=True, approval_id=r.metadata["aid"])
        return PipelineResult(success=True)
```

## 6.3 Table d'audit

```sql
CREATE TABLE validation_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID NOT NULL,
    action_type VARCHAR(50), action_payload JSONB, action_hash VARCHAR(64),
    gate_syntax_status VARCHAR(20), gate_semantic_status VARCHAR(20),
    gate_rbac_status VARCHAR(20), gate_idempotence_status VARCHAR(20),
    gate_deterministic_status VARCHAR(20), gate_hil_status VARCHAR(20),
    final_status VARCHAR(20), approval_id UUID, validated_by UUID,
    execution_time_ms INTEGER, created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_val_audit_tenant ON validation_audit(tenant_id, created_at);
```

## 6.4 Sandbox Docker pour code genere

```python
async def run_sandbox(code: str, language: str = "python", timeout: int = 10) -> dict:
    """Execute le code dans un conteneur Docker isole sans acces reseau."""
    import asyncio
    docker_cmd = [
        "docker", "run", "--rm", "--network", "none",
        "--memory", "128m", "--cpus", "0.5",
        "--read-only", "--tmpfs", "/tmp:noexec,nosuid,size=10m",
        "-v", "/dev/null:/dev/null",
        "python:3.12-slim", "python", "-c", code,
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *docker_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {
            "returncode": proc.returncode,
            "stdout": stdout.decode("utf-8", errors="replace")[:1000],
            "stderr": stderr.decode("utf-8", errors="replace")[:1000],
            "timed_out": False,
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {"returncode": -1, "stdout": "", "stderr": "Timeout", "timed_out": True}
```

Contraintes du sandbox :
- Pas d'acces reseau (`--network none`)
- Limite memoire 128 Mo (`--memory 128m`)
- Limite CPU 0.5 core (`--cpus 0.5`)
- Filesystem en lecture seule (`--read-only`)
- Timeout 10 secondes maximum
- Sortie tronquee a 1000 caracteres

## 6.5 Phasing

| Version | Validation |
|---------|------------|
| v0.1 | Gates 1-3 |
| v0.2 | + Gate 4 (idempotence) |
| v0.3 | + Gate 6 (HIL) |
| v0.5 | + Gate 5 (sandbox) |
| v1.0 | 6 gates + audit complet |

---

# POINT 7 — POLITIQUES D'ESCALADE ET BORNES D'AUTONOMIE

## 7.1 Niveaux d'autonomie

| Niveau | Nom | Description |
|--------|-----|-------------|
| 1 | Suggestions uniquement | Jamais sans validation humaine |
| 2 | Auto + validation si doute | Action seule si confiance > seuil |
| 3 | Auto + notification | Action seule, notification apres |
| 4 | Autonomie complete | Aucune supervision |

## 7.2 Matrice action x autonomie

| Action | Niveau defaut | Configurable | Justification |
|--------|--------------|--------------|---------------|
| Qualifier AO | 1 | Oui -> 2 | Impact financier |
| Kanban move | 2 | Oui | Impact operationnel modere |
| Veille detect | 3 | Non | Detection sans modification |
| Rediger memoire | 1 | Oui -> 2 | Document contractuel |
| Depot portail | 1 | Non | Acte juridique irremediable |
| Indexer memoire | 4 | Non | Pas d'impact externe |
| TAKA LAB | 2 | Oui -> 1 | Impact futures decisions |
| Export donnees | 1 | Non | RGPD |
| Publier AO | 1 | Non | Obligation legale |

## 7.3 Configuration YAML

```yaml
autonomy_policies:
  soumissionnaire:
    qualification: { level: 2, confidence_threshold: 0.75 }
    kanban_move: { level: 3 }
    memoire_indexation: { level: 4 }
    taka_lab: { level: 2, confidence_threshold: 0.85 }
    redaction_memoire: { level: 1 }
    depot_portail: { level: 1, hil_required: true }
    export_data: { level: 1, hil_required: true }
  acheteur:
    publication_ao: { level: 1, hil_required: true }
    reponse_questions: { level: 2, confidence_threshold: 0.80 }
    classement_candidatures: { level: 1, hil_required: true }

# Minimums editeur — non contournables
editor_minimums:
  depot_portail: { level: 1, hil_required: true }
  export_data: { level: 1, hil_required: true }
  publication_ao: { level: 1, hil_required: true }
  invite_user: { level: 1, hil_required: true }
```

## 7.4 Service d'autonomie

```python
class AutonomyService:
    EDITOR_MINIMUMS = {
        "depot_portail": {"level": 1, "hil": True},
        "export_data": {"level": 1, "hil": True},
        "publication_ao": {"level": 1, "hil": True},
        "invite_user": {"level": 1, "hil": True},
    }
    async def check(self, tenant_id, action_key, confidence, role="soumissionnaire"):
        if action_key in self.EDITOR_MINIMUMS:
            return AutonomyDecision(can_proceed=False, level=1, requires_approval=True)
        policy = await self._get_policy(tenant_id, action_key, role)
        if policy.level == 1: return AutonomyDecision(False, 1, True)
        if policy.level == 2:
            t = policy.confidence_threshold or 0.75
            return AutonomyDecision(confidence >= t, 2, confidence < t)
        if policy.level == 3: return AutonomyDecision(True, 3, False)
        return AutonomyDecision(True, 4, False)
```

## 7.5 Kill switch

```python
class KillSwitchService:
    async def activate(self, tenant_id, reason, by, duration_min=60):
        await self.redis.setex(f"kill_switch:{tenant_id}", duration_min*60,
            json.dumps({"status": "ACTIVE", "reason": reason, "by": str(by)}))
        await self.event_bus.publish("kill_switch.activated", {"tenant_id": str(tenant_id), "reason": reason})
    async def is_active(self, tenant_id) -> bool:
        return await self.redis.get(f"kill_switch:{tenant_id}") is not None
```

## 7.6 Interface Human-in-the-loop

```tsx
// frontend/src/components/hil/HumanValidationPanel.tsx
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { CheckCircle, XCircle, HelpCircle } from 'lucide-react';

interface ValidationRequest {
  id: string; agent_name: string; action_type: string;
  description: string; details: Record<string, string>;
  confidence: number; threshold: number;
}

export function HumanValidationPanel({ request, onValidate }) {
  const [note, setNote] = useState('');
  const confidenceColor = request.confidence >= 0.8 ? 'bg-green-100 text-green-800' :
    request.confidence >= 0.6 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800';
  return (
    <Card className="border-2 border-amber-200">
      <CardHeader className="bg-amber-50">
        <div className="flex justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-amber-600" />
            Validation requise — {request.agent_name}
          </CardTitle>
          <Badge className={confidenceColor}>
            Confiance: {Math.round(request.confidence * 100)}%
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 pt-4">
        <div className="rounded-md bg-muted p-3">
          <p className="text-sm font-medium mb-2">{request.description}</p>
          <dl className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(request.details).map(([k, v]) => (
              <div key={k}><dt className="text-muted-foreground">{k}:</dt>
                <dd className="font-medium">{v}</dd></div>
            ))}
          </dl>
        </div>
        <Textarea placeholder="Note optionnelle..." value={note} onChange={e => setNote(e.target.value)} />
        <div className="flex gap-2">
          <Button onClick={() => onValidate(request.id, 'approved', note)} className="flex-1 bg-green-600">
            <CheckCircle className="w-4 h-4 mr-1" /> Valider
          </Button>
          <Button onClick={() => onValidate(request.id, 'maybe', note)} variant="outline" className="flex-1">
            <HelpCircle className="w-4 h-4 mr-1" /> Peut-etre
          </Button>
          <Button onClick={() => onValidate(request.id, 'rejected', note)} variant="destructive" className="flex-1">
            <XCircle className="w-4 h-4 mr-1" /> Refuser
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

## 7.7 Phasing

| Version | Autonomie |
|---------|-----------|
| v0.1 | Niveau 1 tout |
| v0.2 | Niveaux 1-2 |
| v0.3 | Niveaux 1-3 |
| v0.4 | TAKA LAB niveau 2 |
| v0.5 | Config admin complete |
| v1.0 | Kill switch + escalade N+1 |

---

# POINT 8 — TRACABILITE FORENSIQUE

## 8.1 Principe

Pour chaque decision TAKA OS, reconstitution de : Qui (agent/utilisateur), Quoi (action/parametres),
Quand (UTC), Pourquoi (regle/modele/prompt), Avec quoi (etat memoire), Resultat.

## 8.2 Architecture a 5 couches

1. **Audit log** (PostgreSQL) : qui a fait quoi, quand
2. **Validation audit** (PostgreSQL) : gates traversees
3. **LLM call log** (PostgreSQL) : prompts, reponses, couts
4. **Event log** (PostgreSQL, append-only) : evenements bus, hash chain
5. **State snapshots** (PostgreSQL JSONB) : etat avant/apres

## 8.3 Tables de traçabilite

```sql
-- LLM call log
CREATE TABLE llm_call_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID NOT NULL,
    agent_name VARCHAR(50), model_name VARCHAR(50),
    system_prompt TEXT, user_prompt TEXT, prompt_tokens INTEGER,
    response_raw TEXT, response_tokens INTEGER, response_parsed JSONB,
    latency_ms INTEGER, cost_eur DECIMAL(10,8),
    temperature DECIMAL(3,2), memory_context JSONB, created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_llm_tenant ON llm_call_log(tenant_id, created_at);

-- Event log append-only avec hash chain
CREATE TABLE event_log (
    id BIGSERIAL PRIMARY KEY, tenant_id UUID NOT NULL,
    event_type VARCHAR(100), topic VARCHAR(100),
    payload JSONB, source VARCHAR(50), source_id UUID,
    previous_hash VARCHAR(64), current_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_event_tenant ON event_log(tenant_id, created_at);

-- State snapshots
CREATE TABLE state_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID NOT NULL,
    snapshot_type VARCHAR(20) CHECK (snapshot_type IN ('before','after')),
    action_id UUID, action_type VARCHAR(50),
    tender_state JSONB, scoring_state JSONB, memory_state JSONB,
    kanban_state JSONB, config_state JSONB, created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_snap_action ON state_snapshots(action_id, snapshot_type);
```

## 8.4 Hash chain immuable

```python
def compute_hash(event_type, payload, source, timestamp, previous_hash=None):
    data = json.dumps({
        "event_type": event_type,
        "payload_hash": sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
        "source": source, "timestamp": timestamp.isoformat(),
        "previous_hash": previous_hash or "genesis",
    }, sort_keys=True)
    return sha256(data.encode()).hexdigest()

def verify_chain(events):
    prev = None
    for i, e in enumerate(events):
        h = compute_hash(e["event_type"], e["payload"], e["source"], e["created_at"], prev)
        if e.get("current_hash") != h: return False, i
        prev = h
    return True, None
```

## 8.5 Requete forensique

```sql
WITH decision AS (
    SELECT * FROM audit_logs
    WHERE entity_id = 'uuid-ao-123' AND action = 'qualify' ORDER BY created_at DESC LIMIT 1
), llm AS (
    SELECT * FROM llm_call_log WHERE tenant_id = (SELECT tenant_id FROM decision)
    AND created_at BETWEEN (SELECT created_at - interval '5m' FROM decision)
                       AND (SELECT created_at + interval '1m' FROM decision)
), validation AS (
    SELECT * FROM validation_audit WHERE tenant_id = (SELECT tenant_id FROM decision)
    AND action_payload->>'tender_id' = 'uuid-ao-123'
)
SELECT jsonb_build_object(
    'decision', (SELECT row_to_json(d) FROM decision d),
    'llm_calls', (SELECT jsonb_agg(row_to_json(l)) FROM llm l),
    'validations', (SELECT jsonb_agg(row_to_json(v)) FROM validation v)
) AS report;
```

## 8.6 Phasing

| Version | Tracabilite |
|---------|-------------|
| v0.1 | Audit log basique |
| v0.2 | + Hash chain SHA-256 |
| v0.3 | + LLM call log |
| v0.4 | + State snapshots |
| v0.5 | Vue forensic + API |
| v1.0 | Interface complete + export PDF |
| v1.1 | ML sur logs, detection anomalies |

---

# PHASING GLOBAL CONSOLIDE

| Version | i18n | RGAA | Feature Flags | Documentation | Memoire | N Gates | Autonomie | Forensique |
|---------|------|------|---------------|---------------|---------|---------|-----------|------------|
| v0.1 | FR | A | Infra + 4 flags | README + Swagger | Episodique basique | Gates 1-3 | Niveau 1 | Audit log |
| v0.2 | FR+EN | A+ | + flags Starter | Help Center v1 | + pgvector | + Gate 4 | Niveaux 1-2 | + Hash chain |
| v0.3 | FR+EN | AA (en cours) | + flags Pro | Tours + Videos | + Semantic | + HIL | Niveaux 1-3 | + LLM log |
| v0.4 | FR+EN | AA (objectif) | Qualif 5D + LAB | 20 guides | + Procedural | + Sandbox | TAKA LAB n2 | + Snapshots |
| v0.5 | FR+NL+EN | AA complet | + flags Ent. | Complet + SDK | Oubli selectif | Pipeline complet | Config admin | Vue + API |
| v1.0 | +AR | AA certifie | Tous actifs | i18n complete | Global+Tenant | 6 gates audit | Kill switch | Interface + PDF |
| v1.1 | Tous | AAA partiel | Plugins | Communautaire | Neo4j optionnel | Monitoring | Escalade N+1 | ML anomalies |

---

## 8.7 Export forensique PDF

Le rapport forensique peut etre exporte en PDF pour communication aux parties prenantes
ou pour archiving legal. Le template PDF inclut : en-tete avec identifiant unique du rapport,
timestamp de generation, timeline visuelle des evenements, details de chaque couche
(audit, LLM, validation, snapshots), et signature electronique de l'export.

```python
async def generate_pdf_report(tenant_id: uuid.UUID, tender_id: uuid.UUID) -> str:
    report = await generate_tender_report(tenant_id, tender_id)
    template = load_template("forensic_report.html")
    html = template.render(report=report, generated_at=datetime.now(timezone.utc))
    pdf_path = f"/tmp/forensic_{tender_id}_{int(datetime.now().timestamp())}.pdf"
    await html_to_pdf(html, pdf_path)
    return pdf_path
```

## 8.8 Phasing

| Reglementation | Point | Obligation | Cible |
|----------------|-------|------------|-------|
| AI Act (EU 2024/1689) | Point 8 | Tracabilite decisions IA | v1.0 |
| RGPD (2016/679) | Point 8, 7 | Droit explication, sortie donnees | v0.5 |
| RGAA/WCAG 2.1 AA | Point 2 | Accessibilite services publics | v0.5 |
| Code marches publics FR | Point 7 | Validation humaine actes juridiques | v0.1 |
| Loi marches publics BE | Point 1, 7 | Bilinguisme, validation | v0.5 |
| Decret 2-12-349 MA | Point 1, 7 | Adaptation locale | v1.0 |

---

*Document produit par l'equipe architecture TAKA OS — Janvier 2025.*
