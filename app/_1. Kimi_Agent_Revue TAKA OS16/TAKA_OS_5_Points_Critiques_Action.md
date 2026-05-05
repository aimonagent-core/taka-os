# TAKA OS — 5 Points Critiques à Boucher Avant Sprint 0
## Document d'action technique — Prêt pour Kimi Code

---

## Introduction

Ces 5 points sont des **prérequis non-négociables** avant de lancer le développement du MVP. Ils ne sont pas des features utilisateur — ce sont des **fondations de production**. Sans eux, TAKA OS reste un prototype. Avec eux, c'est un SaaS B2B crédible.

**Effort total : 9 à 12 jours de développement.**
**Répartition :** Sprint 0 (3 points) + Sprint 1 (2 points).

---

# POINT 1 — SENTRY + ERROR BOUNDARIES (0.5-1 jour)

## Pourquoi c'est critique

Sans monitoring d'erreurs, tu voles à l'aveugle. Quand un utilisateur te dit "ça marche pas", tu n'as aucune visibilité sur ce qui s'est passé. Sentry te donne : stack trace, contexte, nombre d'occurrences, utilisateur impacté, version concernée.

## Quoi faire exactement

### A. Backend — Intégration Sentry (15 min)

**Fichier :** `app/core/sentry.py`

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from app.config import settings


def init_sentry() -> None:
    if not settings.SENTRY_DSN:
        return  # Sentry désactivé en dev si pas de DSN
    
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,  # "development", "staging", "production"
        release=settings.APP_VERSION,      # "v0.1.0"
        traces_sample_rate=0.1,            # 10% des requêtes tracées (perf)
        profiles_sample_rate=0.05,       # 5% profile CPU
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        attach_stacktrace=True,
        include_source_context=True,
        before_send=filter_sensitive_data,
    )

def filter_sensitive_data(event: dict, hint: dict) -> dict | None:
    """Filtre les données sensibles avant envoi à Sentry."""
    if "exception" in event:
        # Masquer les tokens, mots de passe, SIRET dans les stack traces
        event = _redact_strings(event, ["password", "token", "secret", "siret"])
    return event

def _redact_strings(data: dict, sensitive_keys: list[str]) -> dict:
    """Remplace les valeurs sensibles par [REDACTED]."""
    import json
    text = json.dumps(data)
    for key in sensitive_keys:
        # Pattern simple : "key": "valeur" → "key": "[REDACTED]"
        text = json.dumps(data)
    return json.loads(text)
```

**Fichier :** `app/main.py` (modification)

```python
from app.core.sentry import init_sentry

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_sentry()  # Initialisation au démarrage
    yield
    # Shutdown

app = FastAPI(
    title="TAKA OS",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)
```

**Fichier :** `app/config.py` (ajout)

```python
class Settings(BaseSettings):
    # ... existant ...
    SENTRY_DSN: str | None = None  # Optionnel en dev, obligatoire en prod
    ENVIRONMENT: str = "development"  # development | staging | production
    APP_VERSION: str = "v0.1.0"
```

**Docker :** Pas de changement. Sentry est purement SaaS, juste une lib Python.

### B. Frontend — Intégration Sentry (15 min)

**Fichier :** `frontend/src/main.tsx` (modification)

```tsx
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_ENVIRONMENT,
    release: import.meta.env.VITE_APP_VERSION,
    integrations: [new BrowserTracing()],
    tracesSampleRate: 0.1,
  });
}
```

**Fichier :** `.env.production`

```
VITE_SENTRY_DSN=https://xxx@oYYY.ingest.sentry.io/ZZZ
VITE_ENVIRONMENT=production
VITE_APP_VERSION=v0.1.0
```

### C. Error Boundaries React (15 min)

**Fichier :** `frontend/src/components/error-boundary.tsx`

```tsx
import { Component, ReactNode } from "react";
import * as Sentry from "@sentry/react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    Sentry.captureException(error, { extra: errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="p-8 text-center">
            <h2 className="text-xl font-bold text-red-600 mb-4">
              Une erreur est survenue
            </h2>
            <p className="text-gray-600 mb-4">
              L'équipe TAKA OS a été notifiée. Veuillez rafraîchir la page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              Rafraîchir
            </button>
            <p className="mt-4 text-xs text-gray-400">
              ID d'erreur : {Sentry.lastEventId()}
            </p>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
```

**Fichier :** `frontend/src/App.tsx` (modification)

```tsx
import { ErrorBoundary } from "@/components/error-boundary";

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>...</Routes>
      </Router>
    </ErrorBoundary>
  );
}
```

### D. Dépenses

- **Sentry :** Gratuit jusqu'à 5 000 erreurs/mois (suffisant pour v0.1-v0.3).
- Passage au plan payant ($26/mois) quand on dépasse 5 000 erreurs.

### E. Quand le faire

**Sprint 0 — Semaine 1, Jour 3** (après le setup de base). 2 heures max.

---

# POINT 2 — BACKUP POSTGRESQL AUTO (1 jour)

## Pourquoi c'est critique

Un SaaS B2B sans backup automatique = **irresponsable**. Si le VPS crash, si quelqu'un fait `DROP DATABASE`, si un ransomware touche le serveur — sans backup, c'est la mort du projet. Les clients ne pardonneront jamais une perte de données.

## Quoi faire exactement

### A. Solution retenue : `pg_dump` + Cron + S3

**Pourquoi pas Barman/Wal-G ?** Trop complexe pour un VPS 20€. On garde simple : backup logique quotidien, rétention 30 jours.

### B. Script de backup

**Fichier :** `scripts/backup-db.sh`

```bash
#!/bin/bash
# Backup automatique PostgreSQL TAKA OS
# A exécuter via cron quotidien

set -euo pipefail

# Configuration
DB_NAME="${POSTGRES_DB:-takaos}"
DB_USER="${POSTGRES_USER:-takaos}"
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="/var/backups/takaos"
S3_BUCKET="${S3_BACKUP_BUCKET:-}"  # Optionnel : si renseigné, upload vers S3
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/takaos_backup_${DATE}.sql.gz"

# Créer le répertoire
mkdir -p "$BACKUP_DIR"

# Backup avec pg_dump
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --clean --if-exists --create \
    | gzip > "$BACKUP_FILE"

# Vérifier le backup
if gunzip -t "$BACKUP_FILE" 2>/dev/null; then
    echo "[OK] Backup créé : $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
else
    echo "[ERREUR] Backup corrompu : $BACKUP_FILE" >&2
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Upload vers S3 (optionnel)
if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
    aws s3 cp "$BACKUP_FILE" "s3://${S3_BUCKET}/backups/"
    echo "[OK] Upload S3 terminé"
fi

# Nettoyage des vieux backups (local)
find "$BACKUP_DIR" -name "takaos_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Nettoyage S3 (optionnel)
if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
    aws s3 ls "s3://${SUCKET}/backups/" | \
        awk '{print $4}' | \
        while read -r file; do
            # Logique de rétention S3 plus complexe (à simplifier)
            : # TODO : implémenter rétention S3
        done
fi

echo "[OK] Backup terminé avec succès"
```

### C. Cron (dans le conteneur ou sur l'hôte)

**Option 1 — Cron sur l'hôte VPS** (recommandé)

```bash
# En root sur le VPS
0 3 * * * /opt/takaos/scripts/backup-db.sh >> /var/log/takaos-backup.log 2>&1
```

**Option 2 — Conteneur cron dédié** (si on veut tout dans Docker)

Ajouter dans `docker-compose.yml` :

```yaml
  backup:
    image: postgres:15-alpine
    volumes:
      - ./scripts/backup-db.sh:/backup.sh:ro
      - backups:/var/backups/takaos
    environment:
      - POSTGRES_DB=takaos
      - POSTGRES_USER=takaos
      - POSTGRES_HOST=db
    command: >
      sh -c "echo '0 3 * * * /backup.sh' | crontab - && crond -f"
    depends_on:
      - db
    restart: unless-stopped

volumes:
  backups:
    driver: local
```

### D. Test de restauration (obligatoire)

**Script :** `scripts/restore-db.sh`

```bash
#!/bin/bash
# Test de restauration — À exécuter manuellement ou en CI

BACKUP_FILE="$1"  # ex: /var/backups/takaos/takaos_backup_20250505_030000.sql.gz

gunzip < "$BACKUP_FILE" | psql -h db -U takaos -d takaos_restore_test

echo "Restauration testée avec succès"
```

**Règle d'or :** Un backup non testé est un backup qui ne marche pas. Tester la restauration **une fois par mois** minimum.

### E. Alertes si backup échoue

Ajouter dans le script `backup-db.sh` :

```bash
# À la fin du script
if [ $? -ne 0 ]; then
    # Envoyer alerte webhook (Slack, Discord, ou email)
    curl -X POST "${ALERT_WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"[TAKA OS] ERREUR BACKUP — $DATE\"}"
fi
```

### F. Dépenses

- **Stockage local VPS :** Inclus dans le VPS 20€ (50-100 Go SSD).
- **Stockage S3 Scaleway :** ~0.012€/Go/mois. Un backup de 500 Mo = 0.006€/mois. Négligeable.
- **Sans S3 :** 0€. Juste le stockage local (risque : si le VPS meurt, les backups meurent aussi).

**Recommandation :** S3 Scaleway (France, RGPD compatible) pour les backups. 0.01€/mois.

### G. Quand le faire

**Sprint 0 — Semaine 1, Jour 4.** 1 jour de développement (script + cron + test).

---

# POINT 3 — RATE LIMITING + CIRCUIT BREAKER (2-3 jours)

## Pourquoi c'est critique

Un SaaS multi-tenant sans rate limiting = **un seul client peut tout faire tomber**. Un bot, un utilisateur malveillant, ou un simple bug côté client qui boucle sur les appels API — et tout le système est mort.

Le circuit breaker protège contre les défaillances en cascade : si Mistral API est down, TAKA OS ne doit pas planter.

## Quoi faire exactement

### A. Rate Limiting (backend) — SlowAPI

**Pourquoi SlowAPI ?** C'est un middleware FastAPI natif, simple, basé sur Redis (ou in-memory pour MVP).

**Fichier :** `app/core/rate_limit.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from app.config import settings

# Limiter in-memory pour MVP (Redis pour v1.0+)
limiter = Limiter(
    key_func=get_remote_address,  # Par IP (v0.1) — par tenant_id (v0.5+)
    default_limits=["100/minute"],  # Global : 100 requêtes/minute par IP
)

def setup_rate_limiting(app: FastAPI) -> None:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**Fichier :** `app/main.py` (modification)

```python
from app.core.rate_limit import setup_rate_limiting, limiter

app = FastAPI(...)
setup_rate_limiting(app)

# Application des limites par endpoint
@router.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # 5 tentatives de login par minute
async def login(request: Request, ...):
    ...

@router.post("/api/v1/tenders")
@limiter.limit("20/minute")  # 20 créations d'AO par minute
async def create_tender(request: Request, ...):
    ...

@router.get("/api/v1/tenders")
@limiter.limit("60/minute")  # 60 lectures par minute
async def list_tenders(request: Request, ...):
    ...

@router.post("/api/v1/llm/qualify")
@limiter.limit("10/minute")  # 10 appels LLM par minute (coûteux)
async def qualify_tender(request: Request, ...):
    ...
```

**Fichier :** `requirements.txt` (ajout)

```
slowapi==0.1.9
```

### B. Rate Limiting par tenant (v0.5+)

Pour le MVP (v0.1), on rate limite par IP. Pour les versions suivantes, par tenant :

```python
# Dans v0.5 — rate limiting par tenant
async def get_tenant_key(request: Request) -> str:
    """Retourne la clé de rate limit par tenant."""
    tenant_id = request.state.tenant_id  # Injecté par le middleware auth
    return f"tenant:{tenant_id}"

# Limiter par tenant
limiter = Limiter(
    key_func=get_tenant_key,
    default_limits=["1000/hour"],  # 1000 requêtes/heure par tenant
)
```

### C. Circuit Breaker — PyCircuitBreaker

**Pourquoi ?** Si Mistral API est down ou lente, on ne veut pas que TAKA OS attende indéfiniment. Le circuit breaker coupe les appels après N échecs, retourne une réponse par défaut, et réessaie après un délai.

**Fichier :** `app/core/circuit_breaker.py`

```python
from py_circuit_breaker import CircuitBreaker, CircuitBreakerListener
import httpx
from app.config import settings

class LLMCircuitBreaker(CircuitBreakerListener):
    def on_state_change(self, name: str, new_state: str):
        # Logger le changement d'état
        print(f"[CIRCUIT BREAKER] {name} → {new_state}")

# Circuit breaker pour les appels Mistral API
mistral_breaker = CircuitBreaker(
    name="mistral_api",
    failure_threshold=5,        # 5 échecs avant ouverture
    recovery_timeout=60,        # 60 secondes avant essai de fermeture
    expected_exception=httpx.HTTPError,
    listener=LLMCircuitBreaker(),
)

# Circuit breaker pour les appels BOAMP
boamp_breaker = CircuitBreaker(
    name="boamp_api",
    failure_threshold=3,
    recovery_timeout=120,
    expected_exception=(httpx.HTTPError, httpx.TimeoutException),
)
```

**Utilisation :**

```python
from app.core.circuit_breaker import mistral_breaker

@mistral_breaker
async def call_mistral_api(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.MISTRAL_API_KEY}"},
            json={"model": "mistral-large-latest", "messages": [{"role": "user", "content": prompt}]},
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# Fallback quand le circuit est ouvert
async def qualify_with_fallback(tender_data: dict) -> dict:
    try:
        return await call_mistral_api(build_qualification_prompt(tender_data))
    except CircuitBreakerOpen:
        # Circuit ouvert — retourner une réponse par défaut
        return {
            "verdict": "MAYBE",
            "score": 50.0,
            "explanation": "Service IA temporairement indisponible. Qualification manuelle recommandée.",
            "fallback": True,
        }
```

**Fichier :** `requirements.txt` (ajout)

```
py-circuit-breaker==0.2.0
```

### D. Timeout global sur les endpoints

```python
from fastapi import HTTPException
import asyncio

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=30)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout")
```

### E. Dépenses

- **SlowAPI :** Gratuit (open source).
- **PyCircuitBreaker :** Gratuit (open source).
- **Redis (pour rate limit distribué v1.0+) :** Inclus dans le VPS ( Redis peut tourner dans le conteneur existant).

### F. Quand le faire

**Sprint 0 — Semaine 1, Jour 4-5.** 1.5 à 2 jours.

---

# POINT 4 — TESTS E2E PLAYWRIGHT (3-4 jours)

## Pourquoi c'est critique

30 tests unitaires pour un OS agentic = **insuffisant**. Les tests E2E (End-to-End) simulent un vrai utilisateur qui clique, remplit des formulaires, upload des fichiers, et vérifie que tout fonctionne ensemble. C'est la différence entre "ça compile" et "ça marche".

## Quoi faire exactement

### A. Setup Playwright

**Fichier :** `frontend/package.json` (ajout)

```json
{
  "devDependencies": {
    "@playwright/test": "^1.42.0"
  }
}
```

**Commandes :**

```bash
cd frontend
npm install -D @playwright/test
npx playwright install  # Installe les navigateurs (Chromium, Firefox, WebKit)
```

### B. Configuration Playwright

**Fichier :** `frontend/playwright.config.ts`

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
  ],
  webServer: {
    command: "cd ../backend && uvicorn app.main:app --reload",
    url: "http://localhost:8000",
    reuseExistingServer: !process.env.CI,
  },
});
```

### C. Tests E2E à écrire (priorisés)

**Fichier :** `frontend/e2e/auth.spec.ts`

```typescript
import { test, expect } from "@playwright/test";

test.describe("Authentification", () => {
  test("inscription d'un nouvel utilisateur", async ({ page }) => {
    await page.goto("/signup");
    await page.fill("[name=email]", "test@example.com");
    await page.fill("[name=password]", "SecurePass123!");
    await page.fill("[name=confirmPassword]", "SecurePass123!");
    await page.click("button[type=submit]");
    
    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator("text=Bienvenue")).toBeVisible();
  });

  test("login avec identifiants valides", async ({ page }) => {
    await page.goto("/login");
    await page.fill("[name=email]", "test@example.com");
    await page.fill("[name=password]", "SecurePass123!");
    await page.click("button[type=submit]");
    
    await expect(page).toHaveURL("/dashboard");
  });

  test("login avec mauvais mot de passe affiche une erreur", async ({ page }) => {
    await page.goto("/login");
    await page.fill("[name=email]", "test@example.com");
    await page.fill("[name=password]", "wrongpassword");
    await page.click("button[type=submit]");
    
    await expect(page.locator("text=Mot de passe incorrect")).toBeVisible();
  });
});
```

**Fichier :** `frontend/e2e/tender-flow.spec.ts`

```typescript
import { test, expect } from "@playwright/test";

test.describe("Flow complet AO", () => {
  test("upload DCE + qualification + Kanban", async ({ page }) => {
    // 1. Login
    await page.goto("/login");
    await page.fill("[name=email]", "test@example.com");
    await page.fill("[name=password]", "SecurePass123!");
    await page.click("button[type=submit]");
    await expect(page).toHaveURL("/dashboard");

    // 2. Upload DCE
    await page.click("text=Uploader un DCE");
    await page.setInputFiles("[type=file]", "./fixtures/sample-ao.pdf");
    await page.click("text=Lancer l'analyse");
    
    // 3. Attendre le parsing
    await expect(page.locator("text=Analyse terminée")).toBeVisible({ timeout: 30000 });
    
    // 4. Qualification
    await page.click("text=Qualifier");
    await expect(page.locator("[data-testid=scorecard]")).toBeVisible();
    await expect(page.locator("text=GO")).toBeVisible();
    
    // 5. Déplacer vers Kanban
    await page.click("text=Ajouter au pipeline");
    await page.goto("/kanban");
    
    // 6. Vérifier la carte dans la colonne "Détecté"
    const column = page.locator("[data-column=detected]");
    await expect(column.locator("text=sample-ao")).toBeVisible();
  });
});
```

**Fichier :** `frontend/e2e/kanban.spec.ts`

```typescript
import { test, expect } from "@playwright/test";

test.describe("Kanban", () => {
  test("déplacer une carte entre colonnes", async ({ page }) => {
    await page.goto("/kanban");
    
    const card = page.locator("[data-testid=kanban-card]").first();
    const targetColumn = page.locator("[data-column=qualified]");
    
    await card.dragTo(targetColumn);
    
    await expect(targetColumn.locator("[data-testid=kanban-card]")).toHaveCount(1);
  });
});
```

### D. Fixtures et données de test

**Fichier :** `frontend/e2e/fixtures/sample-ao.pdf`
Un vrai PDF de DCE (appel d'offres) anonymisé pour les tests.

**Fichier :** `scripts/seed-test-db.py`
Script qui initialise la base de données avec des données de test avant chaque suite E2E.

```python
# Seed la base avec : 1 tenant, 1 admin, 3 AO de test, 1 business line
```

### E. Intégration CI/CD

**Fichier :** `.github/workflows/e2e.yml`

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Install Playwright
        run: cd frontend && npx playwright install --with-deps
      - name: Start backend
        run: docker compose up -d
      - name: Run E2E tests
        run: cd frontend && npx playwright test
      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

### F. Quand le faire

**Sprint 1 — Semaine 2, Jour 1-3.** 3 jours.
Pas avant Sprint 0 car on a besoin du frontend fonctionnel (pages login, dashboard, kanban, upload).

---

# POINT 5 — MFA / TOTP (2-3 jours)

## Pourquoi c'est critique

Un SaaS B2B sans MFA en 2025 = **non-credible**. Les PME/ETI ont des obligations de sécurité. Les grands groupes (Equans, SPIE) exigent MFA + SSO. Même les petites entreprises s'y attendent après avoir vu leur banque imposer MFA.

MFA = Multi-Factor Authentication = mot de passe + code TOTP (app Authy/Google Authenticator) ou SMS.

## Quoi faire exactement

### A. Architecture MFA

**Option retenue :** TOTP (Time-based One-Time Password) via `pyotp`. Plus fiable que SMS (coût, interception), plus simple que WebAuthn/FIDO2.

**Flow :**
1. User s'inscrit avec email + mot de passe
2. TAKA OS génère un secret TOTP (QR code)
3. User scanne le QR code avec Google Authenticator / Authy
4. Prochain login : email + mot de passe + code TOTP (6 chiffres)

### B. Modèle de données

**Fichier :** `app/models/auth.py` (extension)

```python
from sqlalchemy.dialects.postgresql import ARRAY

class User(Base):
    # ... champs existants ...
    
    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(default=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # Secret TOTP chiffré
    mfa_verified: Mapped[bool] = mapped_column(default=False)  # True quand l'user a scanné le QR
    mfa_backup_codes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)  # 10 codes de secours
    
    # Méthodes MFA
    def generate_mfa_secret(self) -> str:
        """Génère un nouveau secret TOTP."""
        import pyotp
        secret = pyotp.random_base32()
        self.mfa_secret = secret  # À chiffrer avec Vault dans v0.3
        self.mfa_enabled = True
        self.mfa_verified = False
        return secret
    
    def verify_totp(self, code: str) -> bool:
        """Vérifie un code TOTP."""
        if not self.mfa_secret:
            return False
        import pyotp
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(code, valid_window=1)  # Tolérance ±1 période (30s)
    
    def generate_backup_codes(self) -> list[str]:
        """Génère 10 codes de secours (à usage unique)."""
        import secrets
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.mfa_backup_codes = [hashlib.sha256(c.encode()).hexdigest() for c in codes]
        return codes  # Retourne les codes en clair une seule fois
```

### C. Endpoints MFA

**Fichier :** `app/api/v1/auth_mfa.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.auth import MFASetupResponse, MFAVerifyRequest
from app.services.auth import AuthService

router = APIRouter(prefix="/api/v1/auth/mfa", tags=["MFA"])

@router.post("/setup")
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(),
) -> MFASetupResponse:
    """Active MFA et retourne le QR code pour configuration."""
    if current_user.mfa_enabled and current_user.mfa_verified:
        raise HTTPException(400, "MFA déjà activé")
    
    secret = current_user.generate_mfa_secret()
    await auth_service.save_user(current_user)
    
    # Générer l'URI otpauth pour QR code
    import pyotp
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name="TAKA OS",
    )
    
    return MFASetupResponse(
        secret=secret,
        qr_code_uri=provisioning_uri,
        backup_codes=current_user.generate_backup_codes(),
    )

@router.post("/verify")
async def verify_mfa_setup(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(),
) -> dict:
    """Vérifie le code TOTP lors de la configuration initiale."""
    if current_user.verify_totp(request.code):
        current_user.mfa_verified = True
        await auth_service.save_user(current_user)
        return {"message": "MFA activé avec succès"}
    raise HTTPException(400, "Code TOTP invalide")

@router.post("/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(),
) -> dict:
    """Désactive MFA (nécessite mot de passe + code TOTP)."""
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    current_user.mfa_verified = False
    current_user.mfa_backup_codes = None
    await auth_service.save_user(current_user)
    return {"message": "MFA désactivé"}
```

### D. Modification du login pour MFA

**Fichier :** `app/api/v1/auth.py` (modification)

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: str | None = None  # Optionnel si MFA pas activé

@router.post("/login")
async def login(request: LoginRequest, response: Response):
    user = await authenticate_user(request.email, request.password)
    
    if user.mfa_enabled and user.mfa_verified:
        # MFA requis
        if not request.mfa_code:
            raise HTTPException(403, "Code MFA requis")
        if not user.verify_totp(request.mfa_code):
            raise HTTPException(403, "Code MFA invalide")
    
    # Générer JWT
    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}
```

### E. Frontend — QR Code et saisie TOTP

**Composant :** `frontend/src/components/mfa-setup.tsx`

```tsx
import { useState } from "react";
import { QRCodeSVG } from "qrcode.react";

export function MFASetup({ secret, qrUri, onVerify }: {
  secret: string;
  qrUri: string;
  onVerify: (code: string) => void;
}) {
  const [code, setCode] = useState("");
  
  return (
    <div className="space-y-4">
      <p>Scannez ce QR code avec Google Authenticator :</p>
      <QRCodeSVG value={qrUri} size={200} />
      <p className="text-sm text-gray-500">Code secret : {secret}</p>
      
      <div className="space-y-2">
        <label>Code à 6 chiffres :</label>
        <input
          type="text"
          maxLength={6}
          value={code}
          onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
          className="w-32 text-center text-2xl tracking-widest border rounded"
        />
        <button
          onClick={() => onVerify(code)}
          disabled={code.length !== 6}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          Vérifier
        </button>
      </div>
    </div>
  );
}
```

**Composant :** `frontend/src/components/mfa-input.tsx` (sur la page login)

```tsx
export function MFAInput({ onSubmit }: { onSubmit: (code: string) => void }) {
  const [code, setCode] = useState("");
  
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">
        Code d'authentification (6 chiffres)
      </label>
      <input
        type="text"
        inputMode="numeric"
        maxLength={6}
        autoFocus
        value={code}
        onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
        className="w-full text-center text-2xl tracking-[0.5em] border rounded py-2"
        placeholder="000000"
      />
      <button
        onClick={() => onSubmit(code)}
        disabled={code.length !== 6}
        className="w-full py-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        Valider
      </button>
      <p className="text-xs text-gray-500 text-center">
        Ouvrez Google Authenticator pour obtenir le code
      </p>
    </div>
  );
}
```

### F. Codes de secours

Générer 10 codes à usage unique (au cas où l'utilisateur perd son téléphone) :

```python
def generate_backup_codes() -> list[str]:
    import secrets
    return [f"{secrets.randbelow(1_000_000):06d}" for _ in range(10)]

# Stockage : hash SHA-256 des codes (pas en clair)
# Vérification : hasher le code saisi et comparer
```

### G. Dépenses

- **pyotp :** Gratuit (open source).
- **qrcode.react :** Gratuit (open source).
- **Aucun coût SaaS :** On ne dépend pas d'un service tiers (Auth0, Twilio) pour le TOTP.

### H. Quand le faire

**Sprint 1 — Semaine 2, Jour 4-5.** 2 jours.
Après le Sprint 0 (foundation) car on a besoin de l'authentification JWT de base fonctionnelle.

---

# TABLEAU RÉCAPITULATIF

| # | Point | Effort | Sprint | Fichiers créés/modifiés | Dépense |
|---|-------|--------|--------|------------------------|---------|
| 1 | Sentry + Error Boundaries | 0.5-1j | **Sprint 0** J3 | `app/core/sentry.py`, `main.tsx`, `error-boundary.tsx` | 0€ (5K err/mois) |
| 2 | Backup PostgreSQL auto | 1j | **Sprint 0** J4 | `scripts/backup-db.sh`, `restore-db.sh`, `docker-compose.yml` | 0.01€/mois (S3) |
| 3 | Rate limiting + Circuit breaker | 2-3j | **Sprint 0** J4-5 | `app/core/rate_limit.py`, `circuit_breaker.py`, `main.py` | 0€ |
| 4 | Tests E2E Playwright | 3-4j | **Sprint 1** J1-3 | `frontend/e2e/*.spec.ts`, `playwright.config.ts`, CI/CD | 0€ |
| 5 | MFA / TOTP | 2-3j | **Sprint 1** J4-5 | `app/models/auth.py`, `app/api/v1/auth_mfa.py`, composants MFA | 0€ |

**Total : 9-12 jours | 0€ de coût SaaS supplémentaire (tout est open source)**

---

# CONCLUSION

Ces 5 points sont **des fondations**, pas des fonctionnalités. Ils ne font pas partie du contrat utilisateur (un user ne paiera pas pour du MFA), mais ils font partie du **contrat de confiance**. Sans eux, TAKA OS n'est pas crédible face à :
- Un DSI qui demande "Comment sécurisez-vous les données ?"
- Un utilisateur qui perd ses AO à cause d'un bug
- Un client qui voit le site down sans savoir pourquoi

**Lancer ces 5 points en parallèle des Sprints 0 et 1.** Ne pas attendre la v0.5.
