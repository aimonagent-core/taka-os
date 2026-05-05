# SPRINT 3 - MISE A JOUR : i18n, RGAA, Traçabilité Forensique, AI Act, Documentation, Production, Alertes, Tests E2E

## VERSION : 3.2-MIS-A-JOUR
## DATE : Sprint 3 Final
## OBJECTIF : 5 500 - 6 000 lignes de prompt technique auto-contenu, production-ready, conforme AI Act niveau 3

---

# SECTION 1 : CONTEXTE - SPRINTS 0-2 TERMINEES

## 1.1 Etat des livrables precedents

Les Sprints 0, 1 et 2 ont ete completes avec succes. Le systeme dispose desormais d'une base fonctionnelle avec :

- Sprint 0 : Architecture initiale, models de donnees (AO, Candidat, Soumission, User, Role), authentification JWT, CI/CD minimal, Docker Compose developpement.
- Sprint 1 : Gestion des appels d'offres, workflow de soumission, tableau de bord utilisateur, notifications basiques.
- Sprint 2 : Systeme de scoring automatique, integration LLM pour l'analyse de documents, generation de resumes, chatbot interne.

## 1.2 Ce qui est operationnel

1. **Base de donnees** : PostgreSQL 15 avec schemas `public` (donnees metier), `audit` (logs d'audit), `llm` (traces LLM). Partitionnement par date sur `audit.events` et `llm.interactions`.
2. **Backend API** : FastAPI 0.104, architecture hexagonale, dependencies injection, repositories pattern.
3. **Frontend** : React 18 + TypeScript, React Query, Zustand, Tailwind CSS, shadcn/ui.
4. **Authentification** : JWT avec refresh tokens, roles RBAC (admin, acheteur, fournisseur, valideur).
5. **LLM Integration** : OpenAI GPT-4o via API, avec retry logic, circuit breaker, rate limiting.
6. **Tests** : pytest (backend), Vitest + Testing Library (frontend), couverture > 80%.

## 1.3 Dette technique identifiee

1. Absence de systeme i18n - blocage pour expansion Europe/Belgique
2. Non-conformite RGAA - risque legal pour administration publique
3. Pas de traçabilite forensique - impossible d'auditer les decisions LLM
4. Conformite AI Act partielle - niveau 1 actuel, besoin niveau 3
5. Documentation utilisateur inexistante - courbe d'apprentissage trop forte
6. Infrastructure de production non definie - Docker dev uniquement
7. Alertes manuelles uniquement - pas de surveillance proactive

## 1.4 Objectifs du Sprint 3 mis a jour

Le Sprint 3 mis a jour vise a resoudre l'ensemble de la dette technique et a rendre la plateforme production-ready pour un deploiement SaaS multi-tenant avec :

- Support multilingue FR/NL/EN/AR
- Conformite totale RGAA niveau AA
- Traçabilite forensique complete sur 5 couches
- Conformite AI Act niveau 3 (transparence, explicabilite, contestation)
- Documentation utilisateur integree (tours guides, help center)
- Infrastructure Docker production, Nginx, SSL, CI/CD
- Systeme d'alertes automatise (cron, email, dashboard)
- Tests E2E complets

## 1.5 Contraintes reglementaires applicables

### RGPD (Reglement UE 2016/679)
- Article 5 : Principes relatifs au traitement des donnees
- Article 13-14 : Informations a fournir
- Article 15 : Droit d'acces
- Article 17 : Droit a l'effacement (avec exceptions pour obligations legales)
- Article 22 : Decision individuelle automatisee - OBLIGATION de transparence
- Article 25 : Protection des donnees des la conception
- Article 32 : Securite du traitement
- Article 35 : Analyse d'impact relative a la protection des donnees (AIPD)

### AI Act (Reglement UE 2024/1689)
- Article 6 : Classification des systemes d'IA
- Article 10 : Qualite des donnees d'entrainement
- Article 13 : Transparence et fourniture d'informations aux utilisateurs deployeurs
- Article 14 : Surveillance du fonctionnement par les utilisateurs deployeurs
- Article 15 : Conformite du systeme d'IA avec les exigences en matiere de qualite
- Article 50 : Transparence envers les personnes physiques
- Article 86 : Droit d'obtenir une explication des decisions individuelles
- Article 88 : Traçabilite

### RGAA (Referentiel General d'Amelioration de l'Accessibilite)
- Version 4.1, niveau AA obligatoire
- 13 thematiques, 106 criteres
- Obligation legale pour les services publics (directive 2016/2102)

---

# SECTION 2 : STACK COMPLET - EXISTANT + NOUVEAUTES

## 2.1 Backend - Stack existant

| Composant | Version | Usage |
|-----------|---------|-------|
| Python | 3.11 | Langage principal |
| FastAPI | 0.104 | Framework API |
| SQLAlchemy | 2.0 | ORM |
| Alembic | 1.12 | Migrations |
| Pydantic | 2.4 | Validation |
| Celery | 5.3 | Taches async |
| Redis | 7.2 | Cache, broker Celery |
| PostgreSQL | 15 | Base de donnees |
| pytest | 7.4 | Tests |
| httpx | 0.25 | HTTP client |
| openai | 1.3 | Client LLM |

## 2.2 Backend - Nouveautes Sprint 3

| Composant | Version | Usage |
|-----------|---------|-------|
| Babel | 2.13 | Internationalisation messages |
| pycountry | 22.3 | Donnees pays/locales |
| reportlab | 4.0 | Generation PDF rapports forensiques |
| weasyprint | 60.2 | Alternative PDF HTML-to-PDF |
| python-dateutil | 2.8 | Parsing dates multi-locale |
| APScheduler | 3.10 | Cron jobs alertes |
| aiofiles | 23.2 | File I/O async |
| prometheus-client | 0.19 | Metriques pour monitoring |
| sentry-sdk | 1.38 | Monitoring erreurs |

## 2.3 Frontend - Stack existant

| Composant | Version | Usage |
|-----------|---------|-------|
| React | 18.2 | Framework UI |
| TypeScript | 5.2 | Typage |
| Vite | 5.0 | Build tool |
| Tailwind CSS | 3.4 | Styling |
| shadcn/ui | 2024 | Composants UI |
| React Query | 5.8 | Data fetching |
| Zustand | 4.4 | State management |
| React Hook Form | 7.48 | Formulaires |
| Zod | 3.22 | Validation schema |
| Vitest | 1.0 | Tests |
| Testing Library | 14.1 | Tests composants |

## 2.4 Frontend - Nouveautes Sprint 3

| Composant | Version | Usage |
|-----------|---------|-------|
| react-i18next | 13.5 | Internationalisation |
| i18next | 23.7 | Core i18n |
| i18next-browser-languagedetector | 7.2 | Detection locale navigateur |
| i18next-http-backend | 2.4 | Chargement traductions |
| react-icu-messageformat | 1.0 | ICU MessageFormat pour pluriels |
| react-joyride | 2.7 | Tours guides utilisateur |
| react-accessible-accordion | 5.0 | Accordeons accessibles |
| @axe-core/react | 4.8 | Tests accessibilite runtime |
| axe-core | 4.8 | Moteur tests accessibilite |
| html2canvas | 1.4 | Capture d'ecran pour rapports |
| jspdf | 2.5 | Generation PDF cote client |
| react-pdf | 7.5 | Affichage PDF |
| @react-pdf/renderer | 3.1 | Generation PDF React |
| mermaid | 10.6 | Diagrammes dans documentation |

## 2.5 Infrastructure - Nouveautes Sprint 3

| Composant | Version | Usage |
|-----------|---------|-------|
| Docker | 24 | Containerisation |
| Docker Compose | 2.23 | Orchestration dev |
| Nginx | 1.25 | Reverse proxy, load balancer |
| Certbot | 2.7 | SSL auto Let's Encrypt |
| GitHub Actions | - | CI/CD |
| Prometheus | 2.48 | Monitoring metriques |
| Grafana | 10.2 | Dashboards monitoring |

## 2.6 Structure des repertoires projet

```
/
├── backend/
│   ├── app/
│   │   ├── api/                    # Routes FastAPI
│   │   ├── core/                   # Config, security, i18n
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Logique metier
│   │   ├── repositories/           # Acces donnees
│   │   ├── tasks/                  # Taches Celery
│   │   ├── llm/                    # Integration LLM
│   │   ├── audit/                  # Traçabilite forensique
│   │   ├── ai_act/                 # Conformite AI Act
│   │   ├── alerts/                 # Systeme d'alertes
│   │   ├── templates/              # Templates emails (i18n)
│   │   └── locales/                # Traductions Babel
│   │       ├── fr/LC_MESSAGES/
│   │       ├── nl/LC_MESSAGES/
│   │       ├── en/LC_MESSAGES/
│   │       └── ar/LC_MESSAGES/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── alembic/                    # Migrations
│   ├── Dockerfile                  # Multi-stage production
│   ├── Dockerfile.dev              # Developpement
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/             # Composants React
│   │   ├── pages/                  # Pages/routes
│   │   ├── hooks/                  # Custom hooks
│   │   ├── stores/                 # Zustand stores
│   │   ├── services/               # API clients
│   │   ├── locales/                # Traductions i18next
│   │   │   ├── fr/
│   │   │   ├── nl/
│   │   │   ├── en/
│   │   │   └── ar/
│   │   ├── accessibility/          # Tests et utilitaires RGAA
│   │   ├── tours/                  # Configurations tours guides
│   │   ├── audit/                  # Interface traçabilite
│   │   ├── ai-transparency/        # Composants transparence AI
│   │   └── styles/                 # Styles globaux, themes RTL
│   ├── public/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                           # Help Center Docusaurus
│   ├── docs/
│   │   ├── guides/                 # 20+ guides metier
│   │   ├── api/                    # Documentation API
│   │   ├── legal/                  # Mentions legales, RGPD
│   │   └── accessibility/          # Declaration accessibilite
│   ├── docusaurus.config.js
│   └── Dockerfile
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.prod.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.test.yml
│   ├── nginx/
│   │   ├── nginx.conf
│   │   ├── ssl/                    # Certificats
│   │   └── snippets/               # Configs reutilisables
│   ├── certbot/
│   │   └── init-letsencrypt.sh
│   └── monitoring/
│       ├── prometheus.yml
│       ├── alertmanager.yml
│       └── grafana-dashboards/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Build + Test
│       ├── cd.yml                  # Deploy
│       ├── security-scan.yml       # Scan vulnerabilities
│       └── accessibility-check.yml  # Tests axe-core CI
├── scripts/
│   ├── init-db.sh
│   ├── migrate.sh
│   └── setup-i18n.sh
└── Makefile
```

---

# SECTION 3 : REGLES ABSOLUES

## 3.1 Regle 1 - i18n obligatoire partout

AUCUNE chaine de caracteres en dur n'est autorisee dans le code source. Toutes les chaines visibles par l'utilisateur DOIVENT passer par le systeme d'internationalisation.

**Violations interdites** :
- Messages d'erreur API en dur
- Labels de formulaires en dur
- Emails sans template localise
- Notifications sans traduction
- Contenu d'alertes non traduit

**Locales supportees** :
- `fr` : Francais (defaut, fallback)
- `nl` : Neerlandais (Belgique)
- `en` : Anglais
- `ar` : Arabe (RTL)

**Structure des cles** :
```
page.section.component.element.type
Exemple : ao.create.form.title.label
Exemple : ao.create.form.title.error.required
```

## 3.2 Regle 2 - RGAA niveau AA obligatoire

TOUS les composants frontend DOIVENT satisfaire au moins le niveau AA du RGAA 4.1.

**Verifications obligatoires** :
1. Contraste couleur >= 4.5:1 pour texte normal, >= 3:1 pour texte 18pt+
2. Tout element interactif focusable et focus visible
3. Aria-labels sur tous les boutons icones
4. Skip links sur toutes les pages
5. Landmarks ARIA corrects (main, nav, aside, footer)
6. Titres hierarchiques sans saut (h1 -> h2 -> h3)
7. Tableaux avec captions et headers
8. Formulaires avec labels explicites et messages d'erreur associes
9. Contenu accessible au clavier (tabindex logique)
10. Pas de contenu clignotant, pas de timeout sans avertissement

**Tests obligatoires** :
- axe-core a chaque build frontend
- Navigation clavier dans les tests E2E
- Audit manuel sur composants complexes

## 3.3 Regle 3 - Conformite AI Act niveau 3

TOUS les traitements impliquant l'IA DOIVENT implementer les 5 piliers :

1. **Transparence** : L'utilisateur SAIT explicitement quand une IA est utilisee
   - Badge "IA" visible sur chaque decision automatisee
   - Mention dans l'interface avant traitement
   - Message explicite : "Cette analyse est realisee par intelligence artificielle"

2. **Traçabilite** : Logs immutables de toutes les interactions LLM
   - Hash SHA-256 de chaque prompt et reponse
   - Horodatage UTC avec NTP verification
   - Version du modele utilise
   - Identifiant utilisateur
   - Conservation 5 ans

3. **Explicabilite** : Chaque decision automatisee est expliquable
   - XAI : features importance pour le scoring
   - Texte explicatif pour chaque decision LLM
   - Acces a l'explication depuis l'interface
   - Export de l'explication en PDF

4. **Droit de contestation** : L'utilisateur peut contester toute decision
   - Bouton "Contester cette decision" sur chaque resultat IA
   - Formulaire de contestation avec raisons predefinies + libre
   - Workflow de reexamen par humain
   - Notification au valideur
   - Traçabilite de la contestation

5. **Documentation risques** : AIPD et documentation technique
   - AIPD complete enregistree
   - Documentation technique du systeme
   - Mesures de mitigation documentees
   - Reevaluation trimestrielle

## 3.4 Regle 4 - Traçabilite forensique complete

CINQ couches de traçabilite doivent etre implementees :

1. **Couche Audit** : Actions utilisateur (qui, quoi, quand)
2. **Couche Validation** : Workflow de validation (qui a valide, quand, pourquoi)
3. **Couche LLM** : Interactions avec les modeles (prompts, reponses, tokens)
4. **Couche Event** : Evenements systeme (erreurs, changements etat, crons)
5. **Couche Snapshot** : Etats complets des entites a des points dans le temps

Chaque couche DOIT etre :
- Immuable (WORM - Write Once Read Many)
- Horodate UTC avec verification NTP
- Signee avec cle HMAC
- Exportable en PDF forensique
- Consultable via interface dediee

## 3.5 Regle 5 - Production ready

Le systeme DOIT etre deployable en production avec :
- Docker multi-stage builds optimises
- Nginx avec compression, cache, rate limiting
- SSL/TLS via Let's Encrypt auto-renew
- Health checks sur tous les services
- Graceful shutdown (SIGTERM handling)
- Zero-downtime deployment (blue-green)
- Logs structures (JSON) avec rotation
- Secrets via Docker Swarm / Kubernetes secrets
- Backup automatise de la base de donnees
- Monitoring Prometheus + Grafana
- Alertes PagerDuty / Opsgenie / Email

## 3.6 Regle 6 - Securite par defaut

- Toutes les dependances scannees (Snyk, Dependabot)
- Headers securite (HSTS, CSP, X-Frame-Options, etc.)
- Rate limiting par IP et par utilisateur
- Input validation stricte cote serveur
- SQL injection impossible (SQLAlchemy ORM uniquement)
- XSS prevention (React escape automatique + CSP)
- CSRF tokens sur toutes les mutations
- CORS strict (origines whitelistees)
- JWT expiration courte (15 min), refresh rotation
- Mots de passe : bcrypt, salt unique, 12 rounds minimum
- 2FA optionnel (TOTP)

## 3.7 Regle 7 - Tests E2E complets

Toute PR DOIT passer :
1. Tests unitaires (>80% couverture)
2. Tests integration API
3. Tests accessibilite axe-core
4. Tests i18n (verification cles manquantes)
5. Tests E2E Playwright (scenarios critiques)
6. Tests de charge (k6) pour les endpoints critiques
7. Scan securite (bandit, safety, npm audit)

---

# SECTION 4 : MISSION DETAILLEE

## 4.1 Mission A : Internationalisation (i18n) - FR/NL/EN/AR

### Objectif
Implementer un systeme i18n complet backend et frontend avec 4 locales et support RTL.

### Backend - Babel
- Configuration Babel dans `app/core/i18n.py`
- Catalogue de messages pour fr, nl, en, ar
- Detection locale depuis header `Accept-Language` ou parametre `?lang=`
- Fallback : fr
- Messages d'erreur API traduits
- Emails avec templates Jinja2 localises
- Overrides par pays (BE, FR, NL, MA, etc.)

### Frontend - react-i18next
- Configuration dans `src/i18n/config.ts`
- Namespaces : `common`, `ao`, `candidate`, `dashboard`, `auth`, `alerts`, `audit`, `ai`
- Chargement lazy des traductions par namespace
- Detection automatique depuis navigateur
- Changement manuel avec persistance (localStorage)
- ICU MessageFormat pour pluriels complexes
- Dates et nombres formattes avec Intl

### RTL Support
- Detection locale arabe -> direction RTL
- Inversion layout CSS automatique
- Icons avec `direction-aware` classes
- Texte aligne a droite
- Navigation clavier adaptee

### Fichiers a produire :
1. `backend/app/core/i18n.py` - Configuration Babel
2. `backend/app/locales/messages.pot` - Template catalogue
3. `backend/app/locales/fr/LC_MESSAGES/messages.po` - Francais
4. `backend/app/locales/nl/LC_MESSAGES/messages.po` - Neerlandais
5. `backend/app/locales/en/LC_MESSAGES/messages.po` - Anglais
6. `backend/app/locales/ar/LC_MESSAGES/messages.po` - Arabe
7. `backend/app/templates/emails/fr/` - Templates emails FR
8. `backend/app/templates/emails/nl/` - Templates emails NL
9. `backend/app/templates/emails/en/` - Templates emails EN
10. `backend/app/templates/emails/ar/` - Templates emails AR
11. `frontend/src/i18n/config.ts` - Configuration react-i18next
12. `frontend/src/locales/fr/common.json` - Traductions FR
13. `frontend/src/locales/nl/common.json` - Traductions NL
14. `frontend/src/locales/en/common.json` - Traductions EN
15. `frontend/src/locales/ar/common.json` - Traductions AR
16. `frontend/src/components/LanguageSwitcher.tsx` - Selecteur langue
17. `frontend/src/hooks/useDirection.ts` - Hook direction RTL
18. `frontend/src/styles/rtl.css` - Styles RTL

## 4.2 Mission B : Accessibilite RGAA niveau AA

### Objectif
Rendre l'application conforme RGAA 4.1 niveau AA pour tous les composants.

### Composants accessibles a produire
- Tooltips avec `aria-describedby`, focus trap, echap pour fermer
- Modals avec `aria-modal`, focus trap, restauration focus
- Skip links pour navigation rapide
- Keyboard navigation Kanban (fleches, espace pour selectionner, tab pour deplacer)
- Contraste automatique verifie a chaque build
- Aria-live regions pour notifications dynamiques
- Landmarks ARIA sur toutes les pages

### Tests accessibilite
- `@axe-core/react` integre en dev
- Tests axe-core dans CI
- Navigation clavier dans tests E2E
- Verification contraste automatique

### Declaration d'accessibilite
- Page `/accessibilite` avec declaration conforme modele officiel
- Mention etat de conformite (partiel/conforme/non conforme)
- Liste des contenus non accessibles avec alternatives
- Contact pour signaler obstacles
- Date de declaration et mise a jour

### Fichiers a produire :
1. `frontend/src/components/AccessibleTooltip.tsx` - Tooltip accessible
2. `frontend/src/components/SkipLinks.tsx` - Liens d'evitement
3. `frontend/src/components/AccessibleModal.tsx` - Modal accessible
4. `frontend/src/components/KeyboardNavigableKanban.tsx` - Kanban clavier
5. `frontend/src/accessibility/axe-config.ts` - Configuration axe-core
6. `frontend/src/accessibility/contrast-check.ts` - Verification contraste
7. `frontend/src/pages/AccessibilityDeclaration.tsx` - Page declaration
8. `frontend/tests/accessibility/axe-core.test.tsx` - Tests accessibilite
9. `frontend/tests/accessibility/keyboard-nav.test.tsx` - Tests navigation clavier
10. `docs/docs/accessibility/declaration.md` - Declaration accessibilite

## 4.3 Mission C : Traçabilite forensique complete

### Objectif
Implementer 5 couches de traçabilite avec interface visuelle et export PDF.

### Couche 1 : Audit
- Table `audit.events` : user_id, action, resource_type, resource_id, metadata, ip_address, user_agent, timestamp, signature
- Partitionnement mensuel
- Trigger PostgreSQL sur UPDATE/DELETE pour capturer anciennes valeurs
- API `/audit/events` avec filtres (date, user, action, resource)

### Couche 2 : Validation
- Table `audit.validations` : ao_id, validator_id, decision, reason, timestamp, signature
- Workflow de validation capture chaque etape
- Approbation, rejet, modification avec justification obligatoire

### Couche 3 : LLM
- Table `llm.interactions` : prompt_hash, response_hash, model_version, tokens_input, tokens_output, temperature, user_id, ao_id, timestamp, signature
- Prompts et reponses chiffres (AES-256)
- Hash SHA-256 pour integrite

### Couche 4 : Event
- Table `audit.system_events` : event_type, severity, service, message, metadata, timestamp
- Events : startup, shutdown, error, config_change, cron_run, security_alert
- Integration avec Sentry pour erreurs

### Couche 5 : Snapshot
- Table `audit.snapshots` : entity_type, entity_id, snapshot_data, version, timestamp, signature
- Snapshot automatique avant chaque modification significative
- Diff entre versions
- Restauration possible (admin uniquement)

### Interface Audit Forensique
- Page `/audit` avec timeline visuelle
- Filtres par AO, date, type d'evenement
- Timeline verticale avec couleurs par couche
- Detail au clic sur chaque evenement
- Export PDF rapport forensique complet
- Signature numerique du PDF

### Fichiers a produire :
1. `backend/app/audit/models.py` - Models traçabilite
2. `backend/app/audit/service.py` - Service traçabilite
3. `backend/app/audit/repository.py` - Repository traçabilite
4. `backend/app/audit/crypto.py` - Signature HMAC
5. `backend/app/audit/triggers.sql` - Triggers PostgreSQL
6. `backend/app/api/routes/audit.py` - Routes API audit
7. `backend/app/audit/pdf_exporter.py` - Export PDF rapports
8. `frontend/src/pages/AuditForensic.tsx` - Interface audit
9. `frontend/src/components/audit/Timeline.tsx` - Timeline visuelle
10. `frontend/src/components/audit/EventDetail.tsx` - Detail evenement
11. `frontend/src/components/audit/PdfExport.tsx` - Export PDF
12. `frontend/src/services/auditApi.ts` - Client API audit

## 4.4 Mission D : Conformite AI Act niveau 3

### Objectif
Implementer les 5 piliers AI Act avec composants dedies.

### Pilier 1 : Transparence
- Badge "Analyse IA" sur chaque resultat automatise
- Modal pre-traitement : "Cette analyse sera realisee par IA. Souhaitez-vous continuer ?"
- Mention dans l'historique des analyses
- Indicateur temps reel : "IA en cours d'analyse..."

### Pilier 2 : Traçabilite
- Toutes les interactions LLM loggees (voir Couche LLM traçabilite)
- Impossibilite de suppression des logs IA
- Rapport de traçabilite telechargeable

### Pilier 3 : Explicabilite (XAI)
- Pour le scoring : graphique d'importance des features
- Pour les resumes LLM : explication de la methodologie
- Fenetre "Pourquoi cette decision ?" sur chaque score
- References aux articles du cahier des charges utilises
- Export de l'explication en PDF

### Pilier 4 : Droit de contestation
- Bouton "Contester" sur chaque decision IA
- Formulaire : raisons predefinies + champ libre
- Workflow : notification au valideur -> reexamen -> decision
- Traçabilite complete de la contestation
- Droit a la reponse sous 30 jours

### Pilier 5 : Documentation
- AIPD enregistree dans le systeme
- Documentation technique accessible
- Mesures de mitigation listees
- Reevaluation trimestrielle avec rappel automatique

### Fichiers a produire :
1. `backend/app/ai_act/models.py` - Models conformite
2. `backend/app/ai_act/service.py` - Service conformite
3. `backend/app/ai_act/xai.py` - Explicabilite (features importance)
4. `backend/app/ai_act/contestation.py` - Workflow contestation
5. `backend/app/ai_act/documentation.py` - Documentation risques
6. `backend/app/api/routes/ai_act.py` - Routes API AI Act
7. `frontend/src/components/ai/AIBadge.tsx` - Badge IA
8. `frontend/src/components/ai/AITransparencyModal.tsx` - Modal transparence
9. `frontend/src/components/ai/XAIExplanation.tsx` - Explication XAI
10. `frontend/src/components/ai/ContestDecision.tsx` - Formulaire contestation
11. `frontend/src/components/ai/AIDisclosure.tsx` - Divulgation IA
12. `frontend/src/pages/AIActCompliance.tsx` - Page conformite
13. `docs/docs/legal/aipd.md` - AIPD documentee
14. `docs/docs/legal/ai-act-compliance.md` - Conformite AI Act

## 4.5 Mission E : Documentation utilisateur

### Objectif
Implementer tours guides et structure Help Center.

### Tours guides (react-joyride)
- Tour d'accueil nouveau utilisateur (10 etapes)
- Tour creation AO (8 etapes)
- Tour soumission candidat (6 etapes)
- Tour validation (5 etapes)
- Tour audit (4 etapes)
- Tours declenches automatiquement la premiere fois, relancables depuis le menu
- Progression sauvegardee (localStorage + backend)
- Support i18n pour tous les tours

### Help Center (Docusaurus)
- 20+ guides metier :
  1. "Creer un appel d'offres"
  2. "Publier un AO"
  3. "Gerer les candidatures"
  4. "Utiliser le scoring automatique"
  5. "Comprendre les scores IA"
  6. "Valider une soumission"
  7. "Rejeter une soumission"
  8. "Exporter les resultats"
  9. "Gerer son profil"
  10. "Inviter des collaborateurs"
  11. "Configurer les alertes"
  12. "Utiliser le tableau de bord"
  13. "Interpreter les rapports"
  14. "Contester une decision IA"
  15. "Comprendre la conformite AI Act"
  16. "Guide de l'administrateur"
  17. "API et integrations"
  18. "Securite et confidentialite"
  19. "Accessibilite et aide"
  20. "FAQ"
- Recherche full-text
- Navigation par categories
- Versioning des guides
- Contribution guidee

### Fichiers a produire :
1. `frontend/src/tours/onboardingTour.ts` - Tour accueil
2. `frontend/src/tours/createAOTour.ts` - Tour creation AO
3. `frontend/src/tours/submitTour.ts` - Tour soumission
4. `frontend/src/tours/validateTour.ts` - Tour validation
5. `frontend/src/tours/auditTour.ts` - Tour audit
6. `frontend/src/components/TourWrapper.tsx` - Wrapper tours
7. `frontend/src/hooks/useTourProgress.ts` - Hook progression
8. `frontend/src/components/HelpButton.tsx` - Bouton aide contextuel
9. `docs/docs/guides/01-create-ao.md` - Creer un AO
10. `docs/docs/guides/02-publish-ao.md` - Publier un AO
11. `docs/docs/guides/03-manage-applications.md` - Gerer candidatures
12. `docs/docs/guides/04-auto-scoring.md` - Scoring auto
13. `docs/docs/guides/05-understand-scores.md` - Comprendre scores
14. `docs/docs/guides/06-validate-submission.md` - Valider
15. `docs/docs/guides/07-reject-submission.md` - Rejeter
16. `docs/docs/guides/08-export-results.md` - Exporter
17. `docs/docs/guides/09-profile.md` - Profil
18. `docs/docs/guides/10-invite-users.md` - Inviter
19. `docs/docs/guides/11-alerts.md` - Alertes
20. `docs/docs/guides/12-dashboard.md` - Dashboard
21. `docs/docs/guides/13-reports.md` - Rapports
22. `docs/docs/guides/14-contest.md` - Contester
23. `docs/docs/guides/15-ai-act.md` - AI Act
24. `docs/docs/guides/16-admin.md` - Admin
25. `docs/docs/guides/17-api.md` - API
26. `docs/docs/guides/18-security.md` - Securite
27. `docs/docs/guides/19-accessibility.md` - Accessibilite
28. `docs/docs/guides/20-faq.md` - FAQ
29. `docs/docusaurus.config.js` - Configuration Docusaurus
30. `docs/Dockerfile` - Docker Help Center

## 4.6 Mission F : Production ready

### Objectif
Rendre l'infrastructure production-ready avec Docker, Nginx, SSL, CI/CD.

### Docker production
- Dockerfile backend multi-stage (python:3.11-slim -> build -> runtime)
- Dockerfile frontend multi-stage (node:20 -> build -> nginx:alpine)
- Docker Compose production avec :
  - App backend (2 replicas minimum)
  - Frontend (Nginx)
  - PostgreSQL (volume persistant, backup auto)
  - Redis (persistant)
  - Nginx reverse proxy (SSL termination, load balancing)
  - Certbot (auto-renew SSL)
  - Prometheus (metriques)
  - Grafana (dashboards)
- Health checks sur tous les conteneurs
- Graceful shutdown (SIGTERM -> drain requests -> close connections)
- Limites ressources (CPU, memoire)
- Reseau isole par service

### Nginx configuration
- Reverse proxy vers backend
- Servir fichiers statiques frontend
- Compression gzip/brotli
- Cache headers pour assets
- Rate limiting (zone par IP)
- Headers securite (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy)
- SSL (Let's Encrypt, TLS 1.3, ciphers forts)
- WebSocket support pour temps reel
- Logs formates (JSON)

### CI/CD GitHub Actions
- Workflow `ci.yml` :
  - Checkout
  - Setup Python/Node
  - Install dependencies
  - Lint (ruff, eslint)
  - Tests backend (pytest)
  - Tests frontend (vitest)
  - Tests accessibilite (axe-core)
  - Tests i18n (verification cles)
  - Build Docker images
  - Scan securite (Trivy, npm audit)
  - Push images (GitHub Container Registry)
- Workflow `cd.yml` :
  - Trigger sur tag `v*` ou main
  - Deploy sur serveur production (SSH)
  - Blue-green deployment
  - Health check post-deploy
  - Rollback automatique si health check echoue
- Workflow `security-scan.yml` :
  - Scan dependances quotidien
  - Alertes sur vulnerabilites critique
- Workflow `accessibility-check.yml` :
  - Tests axe-core sur build
  - Rapport HTML des violations

### SSL / Certbot
- Let's Encrypt auto
- Renouvellement automatique (cron hebdomadaire)
- HTTP -> HTTPS redirect
- HSTS preload

### Fichiers a produire :
1. `backend/Dockerfile` - Multi-stage production
2. `frontend/Dockerfile` - Multi-stage production
3. `infrastructure/docker/docker-compose.prod.yml` - Compose production
4. `infrastructure/docker/docker-compose.dev.yml` - Compose dev
5. `infrastructure/docker/docker-compose.test.yml` - Compose test
6. `infrastructure/nginx/nginx.conf` - Config Nginx production
7. `infrastructure/nginx/snippets/security-headers.conf` - Headers securite
8. `infrastructure/nginx/snippets/ssl-params.conf` - Parametres SSL
9. `infrastructure/nginx/snippets/rate-limit.conf` - Rate limiting
10. `infrastructure/certbot/init-letsencrypt.sh` - Init SSL
11. `infrastructure/certbot/renew-ssl.sh` - Renouvellement SSL
12. `infrastructure/monitoring/prometheus.yml` - Config Prometheus
13. `infrastructure/monitoring/alertmanager.yml` - Config Alertmanager
14. `infrastructure/monitoring/grafana-dashboards/dashboard.json` - Dashboard
15. `.github/workflows/ci.yml` - CI build + test
16. `.github/workflows/cd.yml` - CD deploy
17. `.github/workflows/security-scan.yml` - Scan securite
18. `.github/workflows/accessibility-check.yml` - Tests accessibilite
19. `scripts/health-check.sh` - Health check script
20. `scripts/backup-db.sh` - Backup base de donnees
21. `Makefile` - Commandes make

## 4.7 Mission G : Alertes

### Objectif
Implementer un systeme d'alertes automatise multi-canal.

### Types d'alertes
1. **Alertes AO** : Nouvel AO publie, deadline approche (J-7, J-3, J-1), AO modifie
2. **Alertes candidature** : Nouvelle soumission, candidature rejetee, candidature validee
3. **Alertes validation** : A valider depuis X jours, validation urgente
4. **Alertes systeme** : Erreur critique, performance degradee, espace disque
5. **Alertes AI Act** : Nouvelle contestation, reevaluation requise, audit IA planifie

### Canaux
- Email (prioritaire)
- In-app notification (badge, toast)
- Dashboard widget
- Webhook (optionnel pour integrations)

### Configuration utilisateur
- Preferences par type d'alerte (email/in-app/none)
- Frequence email (immediate, quotidienne, hebdomadaire)
- Heures de silence
- Seuils personnalises

### Backend
- Tables `alerts.config`, `alerts.notifications`, `alerts.templates`
- Cron jobs avec APScheduler
- Queue Celery pour envoi email
- Templates email localises (i18n)
- Rate limiting pour eviter spam

### Frontend
- Dashboard alertes avec filtres
- Compteur badge dans le header
- Centre de notification (dropdown)
- Page parametres des alertes

### Fichiers a produire :
1. `backend/app/alerts/models.py` - Models alertes
2. `backend/app/alerts/service.py` - Service alertes
3. `backend/app/alerts/repository.py` - Repository alertes
4. `backend/app/alerts/cron.py` - Cron jobs
5. `backend/app/alerts/templates.py` - Templates email
6. `backend/app/api/routes/alerts.py` - Routes API alertes
7. `backend/app/tasks/alert_tasks.py` - Taches Celery alertes
8. `frontend/src/pages/AlertsDashboard.tsx` - Dashboard alertes
9. `frontend/src/components/alerts/AlertBadge.tsx` - Badge alertes
10. `frontend/src/components/alerts/NotificationCenter.tsx` - Centre notif
11. `frontend/src/components/alerts/AlertSettings.tsx` - Parametres alertes
12. `frontend/src/services/alertsApi.ts` - Client API alertes

## 4.8 Mission H : Tests E2E complets

### Objectif
Couvrir tous les parcours critiques avec des tests E2E.

### Scenarios E2E (Playwright)
1. Authentification complete (login, logout, refresh, 2FA)
2. Creation AO complet (remplissage, upload, publication)
3. Soumission candidat (reponse AO, upload docs, confirmation)
4. Scoring automatique (declenchement, attente resultat, affichage)
5. Validation workflow (affectation, validation, rejet, notification)
6. Audit forensique (navigation timeline, filtre, export PDF)
7. Contestation IA (clic contester, formulaire, soumission, suivi)
8. i18n (changement langue, verification traduction, RTL)
9. Accessibilite (navigation clavier, skip links, contraste)
10. Alertes (config, declenchement, reception)
11. Dashboard (chargement, widgets, navigation)
12. Profil utilisateur (modification, preferences, alertes)
13. Administration (gestion utilisateurs, roles, permissions)
14. Export donnees (RGPD, demande d'export, telechargement)
15. Recherche (filtres, pagination, tri)

### Tests de charge (k6)
- Endpoint login : 100 req/s, p95 < 200ms
- Endpoint liste AO : 50 req/s, p95 < 300ms
- Endpoint scoring : 10 req/s, p95 < 5000ms
- Endpoint audit : 20 req/s, p95 < 500ms

### Tests securite
- Injection SQL (tous les parametres)
- XSS (tous les inputs utilisateur)
- CSRF (toutes les mutations)
- Rate limiting (depassement limite)
- JWT manipulation (token invalide, expire)

### Fichiers a produire :
1. `frontend/tests/e2e/auth.spec.ts` - Tests authentification
2. `frontend/tests/e2e/ao.spec.ts` - Tests AO
3. `frontend/tests/e2e/submission.spec.ts` - Tests soumission
4. `frontend/tests/e2e/scoring.spec.ts` - Tests scoring
5. `frontend/tests/e2e/validation.spec.ts` - Tests validation
6. `frontend/tests/e2e/audit.spec.ts` - Tests audit
7. `frontend/tests/e2e/contest.spec.ts` - Tests contestation
8. `frontend/tests/e2e/i18n.spec.ts` - Tests i18n
9. `frontend/tests/e2e/accessibility.spec.ts` - Tests accessibilite
10. `frontend/tests/e2e/alerts.spec.ts` - Tests alertes
11. `frontend/tests/e2e/dashboard.spec.ts` - Tests dashboard
12. `frontend/tests/e2e/profile.spec.ts` - Tests profil
13. `frontend/tests/e2e/admin.spec.ts` - Tests admin
14. `frontend/tests/e2e/export.spec.ts` - Tests export
15. `frontend/tests/e2e/search.spec.ts` - Tests recherche
16. `frontend/tests/load/k6-auth.js` - Load tests auth
17. `frontend/tests/load/k6-ao.js` - Load tests AO
18. `frontend/tests/load/k6-scoring.js` - Load tests scoring
19. `frontend/tests/security/sql-injection.test.js` - Tests SQLi
20. `frontend/tests/security/xss.test.js` - Tests XSS
21. `frontend/tests/security/csrf.test.js` - Tests CSRF
22. `frontend/tests/security/rate-limit.test.js` - Tests rate limit

---

# SECTION 5 : FICHIERS A PRODUIRE - SPECIFICATIONS DETAILLEES

## GROUPE A : i18n (18 fichiers)

### FICHIER A1 : `backend/app/core/i18n.py`

**Description** : Configuration centralisee de Babel pour l'internationalisation backend.

**Specfications** :
- Class `I18nManager` singleton
- Methodes : `get_locale()`, `set_locale()`, `translate(key, **kwargs)`, `get_supported_locales()`
- Detection locale ordre : parametre URL > header Accept-Language > cookie > default (fr)
- Integration avec FastAPI via middleware `LocaleMiddleware`
- Cache des catalogues en memoire (LRU)
- Fallback chain : ar -> fr, nl -> fr, en -> fr, fr -> key itself
- Fonction `_()` exportee globalement

**Code attendu** :
```python
from babel.support import Translations
from babel import Locale
from fastapi import Request
import os
from typing import Dict, Optional

class I18nManager:
    _instance = None
    _catalogues: Dict[str, Translations] = {}
    _default_locale = "fr"
    _supported_locales = ["fr", "nl", "en", "ar"]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_catalogues()
        return cls._instance
    
    def _load_catalogues(self):
        base_dir = os.path.join(os.path.dirname(__file__), "..", "locales")
        for locale in self._supported_locales:
            mo_path = os.path.join(base_dir, locale, "LC_MESSAGES", "messages.mo")
            if os.path.exists(mo_path):
                self._catalogues[locale] = Translations.load(base_dir, [locale])
    
    def get_locale(self, request: Optional[Request] = None) -> str:
        if request:
            # 1. Check query param
            lang = request.query_params.get("lang")
            if lang in self._supported_locales:
                return lang
            # 2. Check Accept-Language header
            accept_lang = request.headers.get("accept-language", "")
            for tag in accept_lang.split(","):
                code = tag.split(";")[0].strip().split("-")[0]
                if code in self._supported_locales:
                    return code
            # 3. Check cookie
            lang_cookie = request.cookies.get("locale")
            if lang_cookie in self._supported_locales:
                return lang_cookie
        return self._default_locale
    
    def translate(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        target = locale or self._default_locale
        catalogue = self._catalogues.get(target, self._catalogues.get(self._default_locale))
        if catalogue:
            message = catalogue.gettext(key)
            return message.format(**kwargs) if kwargs else message
        return key
    
    def get_supported_locales(self) -> list:
        return self._supported_locales.copy()

i18n = I18nManager()
_ = i18n.translate

class LocaleMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            locale = i18n.get_locale(request)
            scope["locale"] = locale
        await self.app(scope, receive, send)
```

**Tests requis** :
- Test detection locale par parametre
- Test detection locale par header
- Test detection locale par cookie
- Test fallback
- Test traduction avec variables
- Test locale non supportee fallback fr

---

### FICHIER A2 : `backend/app/locales/messages.pot`

**Description** : Template de catalogue de messages Babel.

**Specifications** :
- Genere automatiquement avec `pybabel extract`
- Inclut toutes les chaines marquees avec `_()` ou `gettext()`
- Headers standard Babel
- Contexte pour chaque message

**Extrait attendu** :
```
# Translations template for ao-platform.
# Copyright (C) 2024
msgid ""
msgstr ""
"Project-Id-Version: ao-platform 3.0\n"
"Report-Msgid-Bugs-To: support@ao-platform.com\n"
"POT-Creation-Date: 2024-01-15 10:00+0000\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"

#: app/api/routes/ao.py:45
msgid "ao.not_found"
msgstr ""

#: app/api/routes/auth.py:67
msgid "auth.invalid_credentials"
msgstr ""

#: app/services/alert_service.py:123
msgid "alert.ao_deadline_approaching"
msgstr ""
```

---

### FICHIER A3-A6 : `backend/app/locales/{fr,nl,en,ar}/LC_MESSAGES/messages.po`

**Description** : Catalogues de traduction pour les 4 locales.

**Specifications** :
- Fichiers .po avec headers corrects
- Toutes les cles du .pot traduites
- Pluriels pour arabe (6 formes), neerlandais (2 formes), anglais (2 formes)
- Contexte pour chaque traduction
- Reviewed par humain

**Exemple fr** :
```
msgid "ao.not_found"
msgstr "L'appel d'offres demande n'existe pas."

msgid "auth.invalid_credentials"
msgstr "Identifiants incorrects. Veuillez verifier votre email et mot de passe."

msgid "alert.ao_deadline_approaching"
msgstr "L'appel d'offres \"{title}\" se termine dans {days} jours."
```

**Exemple ar (RTL)** :
```
msgid "ao.not_found"
msgstr ".غير موجود المطلوب دعوى العروض"

msgid "auth.invalid_credentials"
msgstr ".كلمة المرور والبريد الإلكتروني الخاص بك تحقق يرجى. غير صحيحة البيانات"

msgid "alert.ao_deadline_approaching"
msgstr "{days} :\"{title}\" دعوى العروض تنتهي في"
```

**Nombre de cles minimum** : 500 messages traduits par locale

---

### FICHIER A7-A10 : `backend/app/templates/emails/{fr,nl,en,ar}/`

**Description** : Templates d'emails localises pour chaque locale.

**Templates requis par locale** :
- `welcome.html` - Email de bienvenue
- `alert_ao_deadline.html` - Alerte deadline AO
- `alert_new_submission.html` - Nouvelle soumission
- `alert_validation_required.html` - Validation requise
- `alert_contestation_received.html` - Contestation recue
- `reset_password.html` - Reinitialisation mot de passe
- `invite_user.html` - Invitation utilisateur
- `ai_explanation.html` - Explication decision IA
- `base.html` - Template de base avec header/footer

**Specifications** :
- Templates Jinja2
- Design responsive (tables HTML)
- Variables localisees
- Logo plateforme
- Lien vers version web
- Unsubscribe link
- RGPD compliant

---

### FICHIER A11 : `frontend/src/i18n/config.ts`

**Description** : Configuration react-i18next pour le frontend.

**Specifications** :
- Init avec `i18next`, `react-i18next`, `i18next-browser-languagedetector`, `i18next-http-backend`
- Locales : fr, nl, en, ar
- Fallback : fr
- Detection : localStorage > navigator > html tag
- Namespaces : common, ao, auth, dashboard, alerts, audit, ai
- Backend : chargement HTTP depuis `/locales/{{lng}}/{{ns}}.json`
- Debug : false en production
- Interpolation : escapeValue true (securite XSS)
- Pluralisation ICU via plugin
- Lazy loading des namespaces

**Code attendu** :
```typescript
import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpBackend from 'i18next-http-backend';
import ICU from 'i18next-icu';

i18next
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(ICU)
  .use(initReactI18next)
  .init({
    fallbackLng: 'fr',
    supportedLngs: ['fr', 'nl', 'en', 'ar'],
    defaultNS: 'common',
    ns: ['common', 'ao', 'auth', 'dashboard', 'alerts', 'audit', 'ai'],
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18n_locale',
    },
    interpolation: {
      escapeValue: true,
    },
    react: {
      useSuspense: true,
    },
  });

export default i18next;

export const RTL_LOCALES = ['ar'];
export const isRTL = (lng: string) => RTL_LOCALES.includes(lng);
```

---

### FICHIER A12-A15 : `frontend/src/locales/{fr,nl,en,ar}/common.json`

**Description** : Fichiers de traduction JSON pour chaque locale.

**Structure** :
```json
{
  "app": {
    "name": "AO Platform",
    "tagline": "Gestion des appels d'offres"
  },
  "nav": {
    "home": "Accueil",
    "aos": "Appels d'offres",
    "dashboard": "Tableau de bord",
    "audit": "Audit",
    "alerts": "Alertes",
    "profile": "Profil",
    "settings": "Parametres",
    "logout": "Deconnexion"
  },
  "actions": {
    "create": "Creer",
    "edit": "Modifier",
    "delete": "Supprimer",
    "save": "Enregistrer",
    "cancel": "Annuler",
    "confirm": "Confirmer",
    "close": "Fermer",
    "download": "Telecharger",
    "export": "Exporter",
    "search": "Rechercher",
    "filter": "Filtrer",
    "sort": "Trier"
  },
  "errors": {
    "required": "Ce champ est obligatoire",
    "invalid_email": "Adresse email invalide",
    "min_length": "Minimum {count} caracteres",
    "max_length": "Maximum {count} caracteres",
    "server_error": "Une erreur est survenue. Veuillez reessayer.",
    "unauthorized": "Acces non autorise",
    "not_found": "Element non trouve"
  },
  "dates": {
    "today": "Aujourd'hui",
    "yesterday": "Hier",
    "tomorrow": "Demain",
    "format_short": "{day}/{month}/{year}",
    "format_long": "{weekday} {day} {month} {year}"
  }
}
```

**Nombre de cles minimum par namespace** : 200

---

### FICHIER A16 : `frontend/src/components/LanguageSwitcher.tsx`

**Description** : Composant selecteur de langue.

**Specifications** :
- Accessible (bouton avec aria-label, liste deroulante)
- Affiche les drapeaux + codes locales
- Detection automatique
- Changement immediat sans rechargement
- Persistance dans localStorage + cookie
- Direction mise a jour pour RTL
- Focus visible
- Keyboard navigation (fleches, entree, echap)

**Code attendu** :
```tsx
import React, { useState, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { isRTL } from '../i18n/config';

const LANGUAGES = [
  { code: 'fr', label: 'Francais', flag: 'FR' },
  { code: 'nl', label: 'Nederlands', flag: 'NL' },
  { code: 'en', label: 'English', flag: 'GB' },
  { code: 'ar', label: 'Arabic', flag: 'SA' },
];

export const LanguageSwitcher: React.FC = () => {
  const { i18n, t } = useTranslation('common');
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  
  const current = LANGUAGES.find(l => l.code === i18n.language) || LANGUAGES[0];
  
  const changeLanguage = useCallback((code: string) => {
    i18n.changeLanguage(code);
    document.documentElement.dir = isRTL(code) ? 'rtl' : 'ltr';
    document.documentElement.lang = code;
    setOpen(false);
  }, [i18n]);
  
  // Keyboard handling
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') setOpen(false);
    // ... arrow navigation
  };
  
  return (
    <div className="relative" ref={ref}>
      <button
        aria-label={t('nav.language')}
        aria-expanded={open}
        aria-haspopup="listbox"
        onClick={() => setOpen(!open)}
        onKeyDown={handleKeyDown}
        className="flex items-center gap-2 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
      >
        <span aria-hidden="true">{current.flag}</span>
        <span>{current.label}</span>
        <span aria-hidden="true">▼</span>
      </button>
      {open && (
        <ul
          role="listbox"
          aria-label={t('nav.select_language')}
          className="absolute top-full mt-1 bg-white border rounded-md shadow-lg z-50 min-w-[200px]"
        >
          {LANGUAGES.map(lang => (
            <li
              key={lang.code}
              role="option"
              aria-selected={lang.code === current.code}
              onClick={() => changeLanguage(lang.code)}
              className="flex items-center gap-2 px-4 py-2 hover:bg-gray-100 cursor-pointer focus:bg-gray-100"
            >
              <span aria-hidden="true">{lang.flag}</span>
              <span>{lang.label}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

---

### FICHIER A17 : `frontend/src/hooks/useDirection.ts`

**Description** : Hook pour gerer la direction du texte (LTR/RTL).

**Specifications** :
- Retourne la direction actuelle
- Met a jour le DOM automatiquement
- Ecoute les changements de langue
- Fournit des utilitaires de mirroring

**Code attendu** :
```typescript
import { useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { isRTL } from '../i18n/config';

export const useDirection = () => {
  const { i18n } = useTranslation();
  const direction = isRTL(i18n.language) ? 'rtl' : 'ltr';
  
  useEffect(() => {
    document.documentElement.dir = direction;
    document.documentElement.lang = i18n.language;
  }, [direction, i18n.language]);
  
  const getMirrorClass = useCallback((baseClass: string) => {
    return direction === 'rtl' ? `${baseClass} rtl-mirror` : baseClass;
  }, [direction]);
  
  const getLogicalMargin = useCallback((margin: number) => {
    return direction === 'rtl' 
      ? { marginInlineEnd: margin } 
      : { marginInlineStart: margin };
  }, [direction]);
  
  return { direction, isRTL: direction === 'rtl', getMirrorClass, getLogicalMargin };
};
```

---

### FICHIER A18 : `frontend/src/styles/rtl.css`

**Description** : Styles specifiques pour le support RTL.

**Specifications** :
- Inversion des marges/paddings directionnels
- Inversion des flex directions
- Inversion des icones directionnelles
- Ajustement des scrollbars
- Flip des images directionnelles

**Code attendu** :
```css
/* Base RTL styles */
[dir="rtl"] {
  text-align: right;
}

[dir="rtl"] .flex-row {
  flex-direction: row-reverse;
}

[dir="rtl"] .space-x-2 > * + * {
  --tw-space-x-reverse: 1;
}

[dir="rtl"] .ml-2 {
  margin-left: 0;
  margin-right: 0.5rem;
}

[dir="rtl"] .mr-2 {
  margin-right: 0;
  margin-left: 0.5rem;
}

[dir="rtl"] .pl-4 {
  padding-left: 0;
  padding-right: 1rem;
}

[dir="rtl"] .pr-4 {
  padding-right: 0;
  padding-left: 1rem;
}

[dir="rtl"] .text-left {
  text-align: right;
}

[dir="rtl"] .text-right {
  text-align: left;
}

[dir="rtl"] .rtl-mirror {
  transform: scaleX(-1);
}

[dir="rtl"] .border-l {
  border-left: none;
  border-right: 1px solid currentColor;
}

[dir="rtl"] .border-r {
  border-right: none;
  border-left: 1px solid currentColor;
}

[dir="rtl"] .rounded-l {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-top-right-radius: var(--radius);
  border-bottom-right-radius: var(--radius);
}

[dir="rtl"] .rounded-r {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  border-top-left-radius: var(--radius);
  border-bottom-left-radius: var(--radius);
}

[dir="rtl"] .chevron-right {
  transform: rotate(180deg);
}

[dir="rtl"] .arrow-right {
  transform: scaleX(-1);
}
```

---

## GROUPE B : RGAA - Accessibilite (10 fichiers)

### FICHIER B1 : `frontend/src/components/AccessibleTooltip.tsx`

**Description** : Tooltip accessible conforme RGAA.

**Specifications** :
- Utilise `aria-describedby` pour associer le tooltip au declencheur
- Focus trap quand ouvert (non applicable pour tooltip simple)
- Fermeture avec Echap
- Positionnement intelligent (evite debordement)
- Role `tooltip`
- Id unique genere
- Contraste >= 4.5:1
- Taille texte >= 16px
- Pas de timeout automatique

**Code attendu** :
```tsx
import React, { useState, useRef, useId, useCallback } from 'react';

interface AccessibleTooltipProps {
  children: React.ReactNode;
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const AccessibleTooltip: React.FC<AccessibleTooltipProps> = ({
  children,
  content,
  position = 'top',
}) => {
  const [visible, setVisible] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipId = useId();
  
  const show = useCallback(() => setVisible(true), []);
  const hide = useCallback(() => setVisible(false), []);
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape' && visible) {
      hide();
      triggerRef.current?.focus();
    }
  };
  
  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };
  
  return (
    <div className="relative inline-block">
      <div
        ref={triggerRef}
        tabIndex={0}
        aria-describedby={visible ? tooltipId : undefined}
        onMouseEnter={show}
        onMouseLeave={hide}
        onFocus={show}
        onBlur={hide}
        onKeyDown={handleKeyDown}
        className="focus:outline-none focus:ring-2 focus:ring-primary rounded"
      >
        {children}
      </div>
      {visible && (
        <div
          id={tooltipId}
          role="tooltip"
          className={`absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded shadow-lg whitespace-nowrap ${positionClasses[position]}`}
          style={{ minWidth: 'max-content' }}
        >
          {content}
          <div className="sr-only">(Appuyez sur Echap pour fermer)</div>
        </div>
      )}
    </div>
  );
};
```

---

### FICHIER B2 : `frontend/src/components/SkipLinks.tsx`

**Description** : Liens d'evitement pour navigation clavier.

**Specifications** :
- Visible uniquement au focus clavier
- Premier element focusable dans le DOM
- Liens vers : contenu principal, navigation, recherche, pied de page
- Style visible au focus (pas de display:none)
- Saut de -9999px / retour au focus
- Texte explicite

**Code attendu** :
```tsx
import React from 'react';

interface SkipLink {
  id: string;
  label: string;
}

const SKIP_LINKS: SkipLink[] = [
  { id: 'main-content', label: 'Aller au contenu principal' },
  { id: 'main-nav', label: 'Aller a la navigation' },
  { id: 'search', label: 'Aller a la recherche' },
  { id: 'footer', label: 'Aller au pied de page' },
];

export const SkipLinks: React.FC = () => {
  return (
    <nav aria-label="Liens d'evitement" className="skip-links">
      <ul className="list-none m-0 p-0">
        {SKIP_LINKS.map((link) => (
          <li key={link.id}>
            <a
              href={`#${link.id}`}
              className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded focus:shadow-lg"
            >
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
};
```

**CSS additionnel** :
```css
.skip-links a:focus {
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 9999;
  padding: 0.75rem 1rem;
  background: #005fcc;
  color: white;
  text-decoration: none;
  border-radius: 0.25rem;
  font-weight: 500;
}
```

---

### FICHIER B3 : `frontend/src/components/AccessibleModal.tsx`

**Description** : Modal accessible avec focus trap et restauration focus.

**Specifications** :
- `aria-modal="true"`
- `role="dialog"`
- `aria-labelledby` pour titre
- Focus trap (Tab boucle dans la modal)
- Fermeture Echap
- Restauration focus au declencheur a la fermeture
- Body scroll lock
- Overlay clickable pour fermer
- Premier focusable focus au ouverture
- Animation optionnelle (prefers-reduced-motion)

**Code attendu** :
```tsx
import React, { useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useTranslation } from 'react-i18next';

interface AccessibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const AccessibleModal: React.FC<AccessibleModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}) => {
  const { t } = useTranslation('common');
  const modalRef = useRef<HTMLDivElement>(null);
  const titleId = useRef(`modal-title-${Math.random().toString(36).substr(2, 9)}`).current;
  const previousFocus = useRef<HTMLElement | null>(null);
  
  const getFocusableElements = useCallback(() => {
    if (!modalRef.current) return [];
    return Array.from(
      modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    ).filter((el) => !el.hasAttribute('disabled') && !el.getAttribute('aria-hidden'));
  }, []);
  
  useEffect(() => {
    if (isOpen) {
      previousFocus.current = document.activeElement as HTMLElement;
      document.body.style.overflow = 'hidden';
      // Focus first element
      setTimeout(() => {
        const focusable = getFocusableElements();
        if (focusable.length > 0) {
          (focusable[0] as HTMLElement).focus();
        }
      }, 50);
    } else {
      document.body.style.overflow = '';
      previousFocus.current?.focus();
    }
  }, [isOpen, getFocusableElements]);
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
      if (e.key === 'Tab') {
        const focusable = getFocusableElements();
        if (focusable.length === 0) return;
        const first = focusable[0] as HTMLElement;
        const last = focusable[focusable.length - 1] as HTMLElement;
        
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, getFocusableElements]);
  
  if (!isOpen) return null;
  
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };
  
  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="presentation"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="absolute inset-0 bg-black/50" aria-hidden="true" />
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={`relative bg-white rounded-lg shadow-xl w-full mx-4 ${sizeClasses[size]}`}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 id={titleId} className="text-lg font-semibold">
            {title}
          </h2>
          <button
            onClick={onClose}
            aria-label={t('actions.close')}
            className="p-1 rounded hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path d="M6 6L14 14M14 6L6 14" stroke="currentColor" strokeWidth="2" />
            </svg>
          </button>
        </div>
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>,
    document.body
  );
};
```

---

### FICHIER B4 : `frontend/src/components/KeyboardNavigableKanban.tsx`

**Description** : Kanban navigable au clavier pour RGAA.

**Specifications** :
- Chaque colonne : role `list` avec `aria-label`
- Chaque carte : `tabIndex=0`, role `listitem`
- Fleches : navigation entre cartes
- Espace ou Entree : selectionner / ouvrir carte
- Tab : deplacer carte vers colonne suivante (avec Shift+Tab precedent)
- Maj+Flèche : deplacer carte dans colonne
- Home : premiere carte, End : derniere carte
- PageUp/PageDown : 5 cartes
- Indication visuelle du focus
- Annonce ARIA lors de deplacement
- Etat `aria-grabbed` pour drag

**Code attendu** :
```tsx
import React, { useState, useCallback, useRef } from 'react';

interface KanbanItem {
  id: string;
  title: string;
  status: string;
  priority: 'low' | 'medium' | 'high';
}

interface KanbanColumn {
  id: string;
  title: string;
  items: KanbanItem[];
}

export const KeyboardNavigableKanban: React.FC = () => {
  const [columns, setColumns] = useState<KanbanColumn[]>([
    { id: 'todo', title: 'A faire', items: [] },
    { id: 'in-progress', title: 'En cours', items: [] },
    { id: 'done', title: 'Termine', items: [] },
  ]);
  const [focusedItem, setFocusedItem] = useState<string | null>(null);
  const [grabbedItem, setGrabbedItem] = useState<string | null>(null);
  const announcerRef = useRef<HTMLDivElement>(null);
  
  const announce = useCallback((message: string) => {
    if (announcerRef.current) {
      announcerRef.current.textContent = message;
    }
  }, []);
  
  const handleKeyDown = useCallback((
    e: React.KeyboardEvent,
    item: KanbanItem,
    colIndex: number,
    itemIndex: number
  ) => {
    const col = columns[colIndex];
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (itemIndex < col.items.length - 1) {
          setFocusedItem(col.items[itemIndex + 1].id);
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (itemIndex > 0) {
          setFocusedItem(col.items[itemIndex - 1].id);
        }
        break;
      case 'ArrowRight':
        e.preventDefault();
        if (colIndex < columns.length - 1) {
          // Move to next column
          moveItem(item.id, col.id, columns[colIndex + 1].id);
          announce(`${item.title} deplace vers ${columns[colIndex + 1].title}`);
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        if (colIndex > 0) {
          moveItem(item.id, col.id, columns[colIndex - 1].id);
          announce(`${item.title} deplace vers ${columns[colIndex - 1].title}`);
        }
        break;
      case ' ':
      case 'Enter':
        e.preventDefault();
        if (grabbedItem === item.id) {
          setGrabbedItem(null);
          announce(`${item.title} relache`);
        } else {
          setGrabbedItem(item.id);
          announce(`${item.title} saisi. Utilisez les fleches pour deplacer. Espace pour relacher.`);
        }
        break;
      case 'Home':
        e.preventDefault();
        if (col.items.length > 0) setFocusedItem(col.items[0].id);
        break;
      case 'End':
        e.preventDefault();
        if (col.items.length > 0) setFocusedItem(col.items[col.items.length - 1].id);
        break;
      case 'Escape':
        if (grabbedItem) {
          setGrabbedItem(null);
          announce('Deplacement annule');
        }
        break;
    }
  }, [columns, grabbedItem, announce]);
  
  const moveItem = (itemId: string, fromColId: string, toColId: string) => {
    setColumns(prev => {
      const newColumns = prev.map(col => ({ ...col, items: [...col.items] }));
      const fromCol = newColumns.find(c => c.id === fromColId);
      const toCol = newColumns.find(c => c.id === toColId);
      if (!fromCol || !toCol) return prev;
      
      const item = fromCol.items.find(i => i.id === itemId);
      if (!item) return prev;
      
      fromCol.items = fromCol.items.filter(i => i.id !== itemId);
      item.status = toColId;
      toCol.items.push(item);
      return newColumns;
    });
  };
  
  return (
    <div className="flex gap-4 p-4">
      <div ref={announcerRef} className="sr-only" aria-live="polite" aria-atomic="true" />
      {columns.map((col, colIndex) => (
        <div
          key={col.id}
          className="flex-1 min-w-[250px] bg-gray-100 rounded-lg p-3"
          role="region"
          aria-label={`Colonne ${col.title}`}
        >
          <h3 className="font-semibold mb-3 px-2">{col.title}</h3>
          <ul
            role="list"
            className="space-y-2"
            aria-label={`Cartes dans ${col.title}`}
          >
            {col.items.map((item, itemIndex) => (
              <li
                key={item.id}
                role="listitem"
                tabIndex={focusedItem === item.id ? 0 : -1}
                aria-grabbed={grabbedItem === item.id}
                aria-selected={grabbedItem === item.id}
                onKeyDown={(e) => handleKeyDown(e, item, colIndex, itemIndex)}
                onFocus={() => setFocusedItem(item.id)}
                className={`p-3 bg-white rounded shadow cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary ${
                  grabbedItem === item.id ? 'ring-2 ring-blue-500 opacity-75' : ''
                } ${focusedItem === item.id ? 'ring-2 ring-gray-400' : ''}`}
              >
                <div className="font-medium">{item.title}</div>
                <div className="text-sm text-gray-500 mt-1">
                  Priorite: {item.priority}
                </div>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};
```

---

### FICHIER B5 : `frontend/src/accessibility/axe-config.ts`

**Description** : Configuration axe-core pour les tests d'accessibilite.

**Specifications** :
- Rules RGAA 4.1 mapping
- Exclusions pour composants tiers connus
- Niveau de severite
- Configuration CI

**Code attendu** :
```typescript
import { RunOptions } from 'axe-core';

export const axeConfig: RunOptions = {
  rules: [
    { id: 'color-contrast', enabled: true, selector: '*' },
    { id: 'aria-required-attr', enabled: true },
    { id: 'aria-required-children', enabled: true },
    { id: 'aria-required-parent', enabled: true },
    { id: 'aria-roles', enabled: true },
    { id: 'aria-valid-attr-value', enabled: true },
    { id: 'aria-valid-attr', enabled: true },
    { id: 'button-name', enabled: true },
    { id: 'bypass', enabled: true },
    { id: 'document-title', enabled: true },
    { id: 'duplicate-id', enabled: true },
    { id: 'focus-order-semantics', enabled: true },
    { id: 'form-field-multiple-labels', enabled: true },
    { id: 'heading-order', enabled: true },
    { id: 'html-has-lang', enabled: true },
    { id: 'html-lang-valid', enabled: true },
    { id: 'image-alt', enabled: true },
    { id: 'label', enabled: true },
    { id: 'landmark-one-main', enabled: true },
    { id: 'link-in-text-block', enabled: true },
    { id: 'list', enabled: true },
    { id: 'listitem', enabled: true },
    { id: 'meta-viewport', enabled: true },
    { id: 'page-has-heading-one', enabled: true },
    { id: 'region', enabled: true },
    { id: 'skip-link', enabled: true },
    { id: 'tabindex', enabled: true },
    { id: 'valid-lang', enabled: true },
    // RGAA specific
    { id: 'frame-tested', enabled: false }, // iframes not used
    { id: 'css-orientation-lock', enabled: true },
    { id: 'target-size', enabled: true },
    { id: 'meta-refresh', enabled: true },
    { id: 'identical-links-same-purpose', enabled: true },
  ],
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
  reporter: 'v2',
};

export const axeCIConfig: RunOptions = {
  ...axeConfig,
  resultTypes: ['violations'],
  runOnly: {
    type: 'tag',
    values: ['wcag2a', 'wcag2aa'],
  },
};
```

---

### FICHIER B6 : `frontend/src/accessibility/contrast-check.ts`

**Description** : Verification automatique du contraste des couleurs.

**Specifications** :
- Calcul ratio contraste WCAG
- Verification AA (4.5:1 normal, 3:1 large)
- Verification AAA (7:1 normal, 4.5:1 large)
- Fonction pour convertir hex -> RGB -> luminance
- Export rapport

**Code attendu** :
```typescript
/**
 * Contrast ratio calculation per WCAG 2.1
 * https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
 */

interface RGB {
  r: number;
  g: number;
  b: number;
}

interface ContrastResult {
  ratio: number;
  passesAA: boolean;
  passesAAA: boolean;
  passesAALarge: boolean;
  passesAAALarge: boolean;
}

export function hexToRgb(hex: string): RGB {
  const clean = hex.replace('#', '');
  const bigint = parseInt(clean, 16);
  return {
    r: (bigint >> 16) & 255,
    g: (bigint >> 8) & 255,
    b: bigint & 255,
  };
}

export function relativeLuminance({ r, g, b }: RGB): number {
  const sRGB = [r, g, b].map(c => {
    const cNorm = c / 255;
    return cNorm <= 0.03928 ? cNorm / 12.92 : Math.pow((cNorm + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
}

export function contrastRatio(color1: string, color2: string): number {
  const lum1 = relativeLuminance(hexToRgb(color1));
  const lum2 = relativeLuminance(hexToRgb(color2));
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}

export function checkContrast(foreground: string, background: string, fontSize?: number): ContrastResult {
  const ratio = contrastRatio(foreground, background);
  const isLarge = fontSize && fontSize >= 18;
  
  return {
    ratio: Math.round(ratio * 100) / 100,
    passesAA: ratio >= 4.5,
    passesAAA: ratio >= 7,
    passesAALarge: ratio >= 3,
    passesAAALarge: ratio >= 4.5,
  };
}

export function generateContrastReport(colors: Array<{ fg: string; bg: string; label: string }>): string {
  let report = '# Rapport de contraste WCAG 2.1 AA\n\n';
  let failures = 0;
  
  for (const { fg, bg, label } of colors) {
    const result = checkContrast(fg, bg);
    const status = result.passesAA ? 'PASS' : 'FAIL';
    if (!result.passesAA) failures++;
    
    report += `## ${label}\n`;
    report += `- Premier plan: ${fg}\n`;
    report += `- Arriere-plan: ${bg}\n`;
    report += `- Ratio: ${result.ratio}:1\n`;
    report += `- AA: ${status}\n`;
    report += `- AAA: ${result.passesAAA ? 'PASS' : 'FAIL'}\n\n`;
  }
  
  report += `\n---\nTotal: ${colors.length} combinaisons, ${failures} echecs\n`;
  return report;
}
```

---

### FICHIER B7 : `frontend/src/pages/AccessibilityDeclaration.tsx`

**Description** : Page de declaration d'accessibilite conforme modele officiel.

**Specifications** :
- URL : `/accessibilite`
- Contenu conforme au modele de declaration officiel
- Etat de conformite : "Partiellement conforme" ou "Conforme"
- Date de declaration
- Technologies utilisees
- Environnement de test
- Liste des non-conformites avec alternatives
- Voie de recours (defenseur des droits)
- Contact pour signaler obstacles
- Mise a jour reguliere

**Code attendu** :
```tsx
import React from 'react';
import { useTranslation } from 'react-i18next';

export const AccessibilityDeclaration: React.FC = () => {
  const { t } = useTranslation('accessibility');
  
  return (
    <main id="main-content" className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{t('declaration.title')}</h1>
      
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">{t('declaration.entity.title')}</h2>
        <p>{t('declaration.entity.content', { company: 'AO Platform SAS' })}</p>
      </section>
      
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">{t('declaration.status.title')}</h2>
        <p className="bg-yellow-50 border border-yellow-200 p-4 rounded">
          <strong>{t('declaration.status.value')}</strong> - {t('declaration.status.explanation')}
        </p>
      </section>
      
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">{t('declaration.test_results.title')}</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>{t('declaration.test_results.tool', { tool: 'axe-core 4.8' })}</li>
          <li>{t('declaration.test_results.manual')}</li>
          <li>{t('declaration.test_results.keyboard')}</li>
          <li>{t('declaration.test_results.screen_reader')}</li>
        </ul>
      </section>
      
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">{t('declaration.non_conformities.title')}</h2>
        <table className="w-full border-collapse border border-gray-300">
          <caption className="sr-only">{t('declaration.non_conformities.caption')}</caption>
          <thead>
            <tr className="bg-gray-100">
              <th scope="col" className="border border-gray-300 px-4 py-2 text-left">{t('declaration.non_conformities.criteria')}</th>
              <th scope="col" className="border border-gray-300 px-4 py-2 text-left">{t('declaration.non_conformities.description')}</th>
              <th scope="col" className="border border-gray-300 px-4 py-2 text-left">{t('declaration.non_conformities.alternative')}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="border border-gray-300 px-4 py-2">1.2</td>
              <td className="border border-gray-300 px-4 py-2">Captions manquants sur videos tutoriels</td>
              <td className="border border-gray-300 px-4 py-2">Transcriptions textuelles disponibles</td>
            </tr>
          </tbody>
        </table>
      </section>
      
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">{t('declaration.recourse.title')}</h2>
        <p>{t('declaration.recourse.intro')}</p>
        <ol className="list-decimal pl-5 space-y-2 mt-2">
          <li>{t('declaration.recourse.step1')}</li>
          <li>{t('declaration.recourse.step2')}</li>
          <li>{t('declaration.recourse.step3', { url: 'https://www.defenseurdesdroits.fr' })}</li>
        </ol>
      </section>
      
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">{t('declaration.contact.title')}</h2>
        <p>{t('declaration.contact.content', { email: 'accessibilite@ao-platform.com' })}</p>
      </section>
      
      <footer className="text-sm text-gray-500 mt-8 pt-4 border-t">
        {t('declaration.date', { date: '15 janvier 2024' })}
      </footer>
    </main>
  );
};
```

---

### FICHIER B8 : `frontend/tests/accessibility/axe-core.test.tsx`

**Description** : Tests d'accessibilite avec axe-core.

**Specifications** :
- Tests sur chaque page principale
- Tests sur composants complexes
- Verification zero violations
- Rapport des violations
- CI integration

**Code attendu** :
```tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { AccessibilityDeclaration } from '../../src/pages/AccessibilityDeclaration';
import { AccessibleModal } from '../../src/components/AccessibleModal';
import { KeyboardNavigableKanban } from '../../src/components/KeyboardNavigableKanban';
import { I18nextProvider } from 'react-i18next';
import i18n from '../../src/i18n/config';

expect.extend(toHaveNoViolations);

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <I18nextProvider i18n={i18n}>{children}</I18nextProvider>
);

describe('Accessibility - axe-core', () => {
  it('AccessibilityDeclaration page has no violations', async () => {
    const { container } = render(
      <Wrapper><AccessibilityDeclaration /></Wrapper>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('AccessibleModal has no violations when open', async () => {
    const { container } = render(
      <Wrapper>
        <AccessibleModal isOpen={true} onClose={() => {}} title="Test Modal">
          <p>Modal content</p>
          <button>Action</button>
        </AccessibleModal>
      </Wrapper>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('KeyboardNavigableKanban has no violations', async () => {
    const { container } = render(
      <Wrapper><KeyboardNavigableKanban /></Wrapper>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

---

### FICHIER B9 : `frontend/tests/accessibility/keyboard-nav.test.tsx`

**Description** : Tests de navigation clavier.

**Specifications** :
- Tab navigation sur toutes les pages
- Skip links fonctionnels
- Focus trap dans modals
- Keyboard shortcuts

**Code attendu** :
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { AccessibleModal } from '../../src/components/AccessibleModal';
import { SkipLinks } from '../../src/components/SkipLinks';
import { KeyboardNavigableKanban } from '../../src/components/KeyboardNavigableKanban';
import userEvent from '@testing-library/user-event';

describe('Keyboard Navigation', () => {
  it('SkipLinks navigate to main content', () => {
    render(
      <>
        <SkipLinks />
        <nav id="main-nav">Navigation</nav>
        <main id="main-content">Main content</main>
      </>
    );
    
    const skipLink = screen.getByText("Aller au contenu principal");
    expect(skipLink).toHaveAttribute('href', '#main-content');
  });
  
  it('Modal traps focus', async () => {
    const onClose = jest.fn();
    render(
      <AccessibleModal isOpen={true} onClose={onClose} title="Test">
        <button>First</button>
        <button>Second</button>
        <button>Third</button>
      </AccessibleModal>
    );
    
    const firstButton = screen.getByText('First');
    firstButton.focus();
    
    // Tab should cycle
    await userEvent.tab();
    await userEvent.tab();
    await userEvent.tab();
    await userEvent.tab();
    
    // After 4 tabs, should cycle back to first or close button
    expect(document.activeElement).not.toBeNull();
  });
  
  it('Kanban navigation with arrow keys', async () => {
    render(<KeyboardNavigableKanban />);
    // Tests for arrow key navigation
  });
});
```

---

### FICHIER B10 : `docs/docs/accessibility/declaration.md`

**Description** : Declaration d'accessibilite au format markdown pour Help Center.

**Specifications** :
- Format Docusaurus
- Contenu identique a la page web
- Liens internes vers guides accessibilite
- Version datee
- Mise a jour procedure

---

## GROUPE C : Traçabilite forensique (12 fichiers)

### FICHIER C1 : `backend/app/audit/models.py`

**Description** : SQLAlchemy models pour la traçabilite.

**Specifications** :
- 5 tables : AuditEvent, ValidationEvent, LLMInteraction, SystemEvent, EntitySnapshot
- Champs communs : id, created_at, signature
- Partitionnement pour AuditEvent et LLMInteraction
- Index sur user_id, ao_id, timestamp
- Constraints d'integrite

**Code attendu** :
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, BigInteger, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, INET, MACADDR
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class AuditEvent(Base):
    __tablename__ = 'audit_events'
    __table_args__ = (
        Index('idx_audit_user_id', 'user_id'),
        Index('idx_audit_ao_id', 'ao_id'),
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_action', 'action'),
        {'schema': 'audit', 'postgresql_partition_by': 'RANGE (timestamp)'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, VIEW, EXPORT
    resource_type = Column(String(50), nullable=False)  # ao, submission, user, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    metadata = Column(JSON, default=dict)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    signature = Column(String(64), nullable=False)  # HMAC-SHA256
    
    __table_args__ += (CheckConstraint("signature ~ '^[a-f0-9]{64}$'"),)

class ValidationEvent(Base):
    __tablename__ = 'validation_events'
    __table_args__ = (
        Index('idx_val_ao_id', 'ao_id'),
        Index('idx_val_validator', 'validator_id'),
        {'schema': 'audit'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ao_id = Column(UUID(as_uuid=True), ForeignKey('public.aos.id'), nullable=False)
    submission_id = Column(UUID(as_uuid=True), ForeignKey('public.submissions.id'), nullable=False)
    validator_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), nullable=False)
    decision = Column(String(20), nullable=False)  # APPROVED, REJECTED, PENDING
    reason = Column(Text, nullable=True)
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    signature = Column(String(64), nullable=False)

class LLMInteraction(Base):
    __tablename__ = 'llm_interactions'
    __table_args__ = (
        Index('idx_llm_user_id', 'user_id'),
        Index('idx_llm_ao_id', 'ao_id'),
        Index('idx_llm_timestamp', 'timestamp'),
        {'schema': 'llm', 'postgresql_partition_by': 'RANGE (timestamp)'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_hash = Column(String(64), nullable=False)
    response_hash = Column(String(64), nullable=False)
    prompt_encrypted = Column(Text, nullable=False)  # AES-256 encrypted
    response_encrypted = Column(Text, nullable=False)
    model_version = Column(String(50), nullable=False)  # gpt-4o-2024-08-06
    tokens_input = Column(Integer, nullable=False)
    tokens_output = Column(Integer, nullable=False)
    temperature = Column(String(10), nullable=True)
    system_prompt_hash = Column(String(64), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), nullable=False)
    ao_id = Column(UUID(as_uuid=True), ForeignKey('public.aos.id'), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    signature = Column(String(64), nullable=False)
    
    __table_args__ += (CheckConstraint("prompt_hash ~ '^[a-f0-9]{64}$'"),)

class SystemEvent(Base):
    __tablename__ = 'system_events'
    __table_args__ = (
        Index('idx_sys_event_type', 'event_type'),
        Index('idx_sys_timestamp', 'timestamp'),
        {'schema': 'audit'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)  # STARTUP, SHUTDOWN, ERROR, CONFIG_CHANGE, CRON_RUN, SECURITY_ALERT
    severity = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    service = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)
    stack_trace = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    signature = Column(String(64), nullable=False)

class EntitySnapshot(Base):
    __tablename__ = 'entity_snapshots'
    __table_args__ = (
        Index('idx_snap_entity', 'entity_type', 'entity_id'),
        Index('idx_snap_timestamp', 'timestamp'),
        {'schema': 'audit'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    snapshot_data = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False)
    operation = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    changed_by = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    signature = Column(String(64), nullable=False)
```

---

### FICHIER C2 : `backend/app/audit/service.py`

**Description** : Service metier pour la traçabilite.

**Specifications** :
- LogAuditEvent : enregistrer evenement utilisateur
- LogValidation : enregistrer decision validation
- LogLLMInteraction : enregistrer interaction LLM
- LogSystemEvent : enregistrer evenement systeme
- CreateSnapshot : creer snapshot entite
- GetTimeline : recuperer timeline pour un AO
- VerifySignature : verifier integrite signature
- ExportForensicReport : generer rapport PDF

**Code attendu** :
```python
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import hashlib
import hmac
import json
from sqlalchemy.orm import Session

from .models import AuditEvent, ValidationEvent, LLMInteraction, SystemEvent, EntitySnapshot
from .crypto import sign_data, verify_signature
from .repository import AuditRepository

class AuditService:
    def __init__(self, db: Session, secret_key: str):
        self.db = db
        self.repo = AuditRepository(db)
        self.secret_key = secret_key
    
    def log_audit_event(
        self,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
        )
        event.signature = self._sign_event(event)
        return self.repo.save_audit_event(event)
    
    def log_validation(
        self,
        ao_id: UUID,
        submission_id: UUID,
        validator_id: UUID,
        decision: str,
        reason: Optional[str] = None,
        previous_state: Optional[Dict] = None,
        new_state: Optional[Dict] = None,
    ) -> ValidationEvent:
        event = ValidationEvent(
            ao_id=ao_id,
            submission_id=submission_id,
            validator_id=validator_id,
            decision=decision,
            reason=reason,
            previous_state=previous_state,
            new_state=new_state,
            timestamp=datetime.utcnow(),
        )
        event.signature = self._sign_event(event)
        return self.repo.save_validation_event(event)
    
    def log_llm_interaction(
        self,
        prompt: str,
        response: str,
        model_version: str,
        tokens_input: int,
        tokens_output: int,
        user_id: UUID,
        ao_id: Optional[UUID] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
    ) -> LLMInteraction:
        from .crypto import encrypt_data
        
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        response_hash = hashlib.sha256(response.encode()).hexdigest()
        system_prompt_hash = hashlib.sha256(system_prompt.encode()).hexdigest() if system_prompt else None
        
        event = LLMInteraction(
            prompt_hash=prompt_hash,
            response_hash=response_hash,
            prompt_encrypted=encrypt_data(prompt, self.secret_key),
            response_encrypted=encrypt_data(response, self.secret_key),
            model_version=model_version,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            temperature=str(temperature) if temperature else None,
            system_prompt_hash=system_prompt_hash,
            user_id=user_id,
            ao_id=ao_id,
            timestamp=datetime.utcnow(),
        )
        event.signature = self._sign_event(event)
        return self.repo.save_llm_interaction(event)
    
    def get_timeline(self, ao_id: UUID) -> List[Dict[str, Any]]:
        events = self.repo.get_all_events_for_ao(ao_id)
        timeline = []
        
        for event in events:
            entry = {
                'id': str(event.id),
                'layer': self._determine_layer(event),
                'timestamp': event.timestamp.isoformat(),
                'title': self._format_event_title(event),
                'description': self._format_event_description(event),
                'actor': str(event.user_id) if hasattr(event, 'user_id') else 'SYSTEM',
                'signature_valid': self._verify_event_signature(event),
                'data': self._serialize_event(event),
            }
            timeline.append(entry)
        
        return sorted(timeline, key=lambda x: x['timestamp'])
    
    def export_forensic_report(self, ao_id: UUID) -> bytes:
        from .pdf_exporter import generate_forensic_pdf
        timeline = self.get_timeline(ao_id)
        return generate_forensic_pdf(ao_id, timeline, self.secret_key)
    
    def _sign_event(self, event) -> str:
        data = json.dumps(self._serialize_event(event), sort_keys=True)
        return sign_data(data, self.secret_key)
    
    def _verify_event_signature(self, event) -> bool:
        data = json.dumps(self._serialize_event(event), sort_keys=True)
        return verify_signature(data, event.signature, self.secret_key)
    
    def _determine_layer(self, event) -> str:
        if isinstance(event, AuditEvent):
            return 'audit'
        elif isinstance(event, ValidationEvent):
            return 'validation'
        elif isinstance(event, LLMInteraction):
            return 'llm'
        elif isinstance(event, SystemEvent):
            return 'event'
        elif isinstance(event, EntitySnapshot):
            return 'snapshot'
        return 'unknown'
    
    def _serialize_event(self, event) -> Dict:
        # Serialize event to dict excluding signature
        ...
    
    def _format_event_title(self, event) -> str:
        # Human readable title
        ...
    
    def _format_event_description(self, event) -> str:
        # Human readable description
        ...
```

---

### FICHIER C3 : `backend/app/audit/crypto.py`

**Description** : Cryptographie pour la traçabilite forensique.

**Specifications** :
- HMAC-SHA256 pour signatures
- AES-256-GCM pour chiffrement prompts/reponses LLM
- Generation de cles derivees avec PBKDF2
- Verification d'integrite
- Pas de stockage cle en clair (environnement uniquement)

**Code attendu** :
```python
import hashlib
import hmac
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64


def sign_data(data: str, secret_key: str) -> str:
    """Sign data with HMAC-SHA256 for integrity verification."""
    key = secret_key.encode('utf-8')
    message = data.encode('utf-8')
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()
    return signature


def verify_signature(data: str, signature: str, secret_key: str) -> bool:
    """Verify HMAC-SHA256 signature."""
    expected = sign_data(data, secret_key)
    return hmac.compare_digest(expected, signature)


def derive_key(secret_key: str, salt: bytes = None) -> tuple:
    """Derive AES key from secret using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
    return key, salt


def encrypt_data(plaintext: str, secret_key: str) -> str:
    """Encrypt data with AES-256-GCM."""
    key, salt = derive_key(secret_key)
    aesgcm = AESGCM(base64.urlsafe_b64decode(key))
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    # Store salt + nonce + ciphertext
    combined = salt + nonce + ciphertext
    return base64.b64encode(combined).decode()


def decrypt_data(encrypted: str, secret_key: str) -> str:
    """Decrypt data encrypted with AES-256-GCM."""
    combined = base64.b64decode(encrypted.encode())
    salt = combined[:16]
    nonce = combined[16:28]
    ciphertext = combined[28:]
    
    key, _ = derive_key(secret_key, salt)
    aesgcm = AESGCM(base64.urlsafe_b64decode(key))
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()
```

---

### FICHIER C4 : `backend/app/audit/triggers.sql`

**Description** : Triggers PostgreSQL pour capturer automatiquement les modifications.

**Specifications** :
- Trigger sur UPDATE/DELETE pour chaque table metier
- Capture anciennes valeurs
- Insertion automatique dans audit_events
- Ne pas doubler les logs (eviter boucle)
- Fonction generique parametree

**Code attendu** :
```sql
-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS $$
DECLARE
    audit_id UUID;
    old_data JSONB;
    new_data JSONB;
    changed_fields JSONB;
    actor_id UUID;
BEGIN
    -- Get current user from session variable (set by app)
    actor_id := NULLIF(current_setting('app.current_user_id', TRUE), '')::UUID;
    
    IF actor_id IS NULL THEN
        actor_id := '00000000-0000-0000-0000-000000000000'::UUID;
    END IF;
    
    IF TG_OP = 'UPDATE' THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);
        
        -- Calculate changed fields
        SELECT jsonb_object_agg(key, value)
        INTO changed_fields
        FROM jsonb_each(new_data)
        WHERE new_data->key IS DISTINCT FROM old_data->key;
        
        IF changed_fields IS NOT NULL AND changed_fields <> '{}'::JSONB THEN
            INSERT INTO audit.audit_events (
                user_id, action, resource_type, resource_id, 
                metadata, timestamp, signature
            ) VALUES (
                actor_id,
                'UPDATE',
                TG_TABLE_NAME,
                NEW.id,
                jsonb_build_object(
                    'old', old_data,
                    'new', new_data,
                    'changed', changed_fields
                ),
                NOW(),
                'pending' -- Signed by app layer
            );
        END IF;
        
        -- Create snapshot
        INSERT INTO audit.entity_snapshots (
            entity_type, entity_id, snapshot_data, version,
            operation, changed_by, timestamp, signature
        ) VALUES (
            TG_TABLE_NAME,
            NEW.id,
            old_data,
            COALESCE((SELECT MAX(version) FROM audit.entity_snapshots 
                      WHERE entity_type = TG_TABLE_NAME AND entity_id = NEW.id), 0) + 1,
            'UPDATE',
            actor_id,
            NOW(),
            'pending'
        );
        
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit.audit_events (
            user_id, action, resource_type, resource_id,
            metadata, timestamp, signature
        ) VALUES (
            actor_id,
            'DELETE',
            TG_TABLE_NAME,
            OLD.id,
            jsonb_build_object('deleted', to_jsonb(OLD)),
            NOW(),
            'pending'
        );
        
        INSERT INTO audit.entity_snapshots (
            entity_type, entity_id, snapshot_data, version,
            operation, changed_by, timestamp, signature
        ) VALUES (
            TG_TABLE_NAME,
            OLD.id,
            to_jsonb(OLD),
            COALESCE((SELECT MAX(version) FROM audit.entity_snapshots 
                      WHERE entity_type = TG_TABLE_NAME AND entity_id = OLD.id), 0) + 1,
            'DELETE',
            actor_id,
            NOW(),
            'pending'
        );
        
        RETURN OLD;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit.entity_snapshots (
            entity_type, entity_id, snapshot_data, version,
            operation, changed_by, timestamp, signature
        ) VALUES (
            TG_TABLE_NAME,
            NEW.id,
            to_jsonb(NEW),
            1,
            'CREATE',
            actor_id,
            NOW(),
            'pending'
        );
        
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply triggers to main tables
CREATE TRIGGER audit_aos_changes
AFTER UPDATE OR DELETE OR INSERT ON public.aos
FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER audit_submissions_changes
AFTER UPDATE OR DELETE OR INSERT ON public.submissions
FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER audit_users_changes
AFTER UPDATE OR DELETE OR INSERT ON public.users
FOR EACH ROW EXECUTE FUNCTION audit.log_changes();
```

---

### FICHIER C5 : `backend/app/api/routes/audit.py`

**Description** : Routes API pour la traçabilite.

**Specifications** :
- GET /audit/timeline/{ao_id} : timeline complete
- GET /audit/events : liste filtree
- GET /audit/llm-interactions : interactions LLM
- GET /audit/snapshots/{entity_type}/{entity_id} : snapshots
- GET /audit/export/{ao_id} : export PDF
- POST /audit/verify : verifier signature
- Middleware pour injecter user_id dans PostgreSQL

**Code attendu** :
```python
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.deps import get_db, get_current_user, require_role
from app.audit.service import AuditService
from app.audit.repository import AuditRepository
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["audit"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    from app.core.config import settings
    return AuditService(db, settings.AUDIT_SECRET_KEY)

@router.get("/timeline/{ao_id}")
async def get_timeline(
    ao_id: UUID,
    service: AuditService = Depends(get_audit_service),
    current_user: User = Depends(require_role(["admin", "acheteur", "valideur"])),
):
    timeline = service.get_timeline(ao_id)
    return {
        "ao_id": str(ao_id),
        "events_count": len(timeline),
        "timeline": timeline,
    }

@router.get("/events")
async def list_events(
    user_id: Optional[UUID] = Query(None),
    ao_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
    current_user: User = Depends(require_role(["admin", "valideur"])),
):
    events, total = service.repo.list_events(
        user_id=user_id,
        ao_id=ao_id,
        action=action,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return {
        "items": events,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

@router.get("/export/{ao_id}")
async def export_forensic_report(
    ao_id: UUID,
    service: AuditService = Depends(get_audit_service),
    current_user: User = Depends(require_role(["admin", "valideur"])),
):
    pdf_bytes = service.export_forensic_report(ao_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=audit_forensic_{ao_id}.pdf"
        },
    )

@router.post("/verify")
async def verify_signature(
    event_id: UUID,
    layer: str,  # audit, validation, llm, event, snapshot
    service: AuditService = Depends(get_audit_service),
    current_user: User = Depends(require_role(["admin"])),
):
    is_valid = service.verify_event_by_id(event_id, layer)
    return {
        "event_id": str(event_id),
        "layer": layer,
        "signature_valid": is_valid,
    }
```

---

### FICHIER C6 : `backend/app/audit/pdf_exporter.py`

**Description** : Generation PDF des rapports forensiques.

**Specifications** :
- ReportLab ou WeasyPrint
- En-tete avec logo, titre, date
- Sommaire avec liens
- Timeline visuelle avec couleurs par couche
- Tableaux detailles
- Signatures de verification
- Footer avec numero page, classification
- Metadonnees PDF (title, author, subject)

**Code attendu** :
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO
from uuid import UUID
from typing import List, Dict, Any

# Layer colors
LAYER_COLORS = {
    'audit': colors.HexColor('#3b82f6'),
    'validation': colors.HexColor('#22c55e'),
    'llm': colors.HexColor('#a855f7'),
    'event': colors.HexColor('#f59e0b'),
    'snapshot': colors.HexColor('#6b7280'),
}

def generate_forensic_pdf(ao_id: UUID, timeline: List[Dict[str, Any]], secret_key: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'ForensicTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    story.append(Paragraph("RAPPORT FORENSIQUE", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Metadata
    meta_data = [
        ['AO ID', str(ao_id)],
        ['Date de generation', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')],
        ['Nombre d\'evenements', str(len(timeline))],
        ['Classification', 'CONFIDENTIEL'],
        ['Hash du rapport', generate_report_hash(timeline, secret_key)[:16]],
    ]
    meta_table = Table(meta_data, colWidths=[5*cm, 10*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f2937')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 1*cm))
    
    # Layer legend
    story.append(Paragraph("Legende des couches", styles['Heading2']))
    legend_data = []
    for layer, color in LAYER_COLORS.items():
        legend_data.append([
            '',
            Paragraph(f'<font color="{color.hexval()}">■</font> {layer.upper()}', styles['Normal'])
        ])
    legend_table = Table(legend_data, colWidths=[1*cm, 14*cm])
    story.append(legend_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Timeline
    story.append(Paragraph("Timeline complete", styles['Heading2']))
    
    for event in timeline:
        layer = event['layer']
        color = LAYER_COLORS.get(layer, colors.gray)
        
        event_data = [
            [
                Paragraph(f'<font color="{color.hexval()}">●</font>', styles['Normal']),
                Paragraph(event['timestamp'], styles['Normal']),
                Paragraph(f"<b>{event['title']}</b>", styles['Normal']),
            ],
            [
                '',
                '',
                Paragraph(event['description'], styles['Normal']),
            ],
            [
                '',
                '',
                Paragraph(f"Acteur: {event['actor']} | Signature: {'VALIDE' if event['signature_valid'] else 'INVALIDE'}", styles['Normal']),
            ]
        ]
        event_table = Table(event_data, colWidths=[1*cm, 4*cm, 10*cm])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(event_table)
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("FIN DU RAPPORT", styles['Heading3']))
    
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#6b7280'))
    canvas.drawString(2*cm, 1*cm, f"AO Platform - Rapport Forensique - Page {doc.page}")
    canvas.drawRightString(19*cm, 1*cm, "CONFIDENTIEL")
    canvas.restoreState()


def generate_report_hash(timeline: List[Dict], secret_key: str) -> str:
    import hashlib, hmac, json
    data = json.dumps(timeline, sort_keys=True)
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()
```

---

### FICHIER C7 : `backend/app/audit/repository.py`

**Description** : Repository pour l'acces aux donnees de traçabilite.

**Specifications** :
- CRUD pour chaque table
- Requetes filtrees par AO, user, date, layer
- Pagination
- Jointures pour enrichir les donnees
- Requetes optimisees avec index

---

### FICHIER C8 : `frontend/src/pages/AuditForensic.tsx`

**Description** : Page principale d'audit forensique.

**Specifications** :
- Layout avec sidebar filtres + timeline
- Chargement des donnees par AO
- Filtres : date range, layer, type evenement, acteur
- Export PDF bouton
- Verification signature bouton
- Responsive

**Code attendu** :
```tsx
import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { AuditTimeline } from '../components/audit/Timeline';
import { AuditFilters } from '../components/audit/Filters';
import { AuditEventDetail } from '../components/audit/EventDetail';
import { auditApi } from '../services/auditApi';

export const AuditForensicPage: React.FC = () => {
  const { t } = useTranslation('audit');
  const { aoId } = useParams<{ aoId: string }>();
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    layers: ['audit', 'validation', 'llm', 'event', 'snapshot'],
    startDate: null as Date | null,
    endDate: null as Date | null,
    actorId: null as string | null,
  });
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['audit-timeline', aoId, filters],
    queryFn: () => auditApi.getTimeline(aoId!, filters),
    enabled: !!aoId,
  });
  
  const handleExportPdf = useCallback(async () => {
    if (!aoId) return;
    const blob = await auditApi.exportPdf(aoId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-forensic-${aoId}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
  }, [aoId]);
  
  return (
    <main id="main-content" className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{t('forensic.title')}</h1>
          <p className="text-gray-600 mt-1">{t('forensic.subtitle', { aoId })}</p>
        </div>
        <button
          onClick={handleExportPdf}
          className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          aria-label={t('forensic.export_pdf')}
        >
          {t('forensic.export_pdf')}
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <aside className="lg:col-span-1">
          <AuditFilters filters={filters} onChange={setFilters} />
        </aside>
        
        <section className="lg:col-span-3">
          {isLoading && <div role="status" aria-live="polite">{t('common.loading')}</div>}
          {error && <div role="alert" className="text-red-600">{t('common.error')}</div>}
          {data && (
            <>
              <div className="mb-4 text-sm text-gray-500">
                {t('forensic.events_count', { count: data.events_count })}
              </div>
              <AuditTimeline
                events={data.timeline}
                onEventClick={setSelectedEvent}
              />
            </>
          )}
        </section>
      </div>
      
      {selectedEvent && (
        <AuditEventDetail
          eventId={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </main>
  );
};
```

---

### FICHIER C9 : `frontend/src/components/audit/Timeline.tsx`

**Description** : Composant timeline visuelle pour l'audit.

**Specifications** :
- Timeline verticale avec ligne centrale
- Points colores par couche
- Cartes d'evenement avec titre, date, description
- Expandable pour details
- Hover effects
- Responsive

**Code attendu** :
```tsx
import React from 'react';
import { useTranslation } from 'react-i18next';

interface TimelineEvent {
  id: string;
  layer: string;
  timestamp: string;
  title: string;
  description: string;
  actor: string;
  signature_valid: boolean;
}

interface AuditTimelineProps {
  events: TimelineEvent[];
  onEventClick: (eventId: string) => void;
}

const LAYER_COLORS: Record<string, string> = {
  audit: '#3b82f6',
  validation: '#22c55e',
  llm: '#a855f7',
  event: '#f59e0b',
  snapshot: '#6b7280',
};

const LAYER_ICONS: Record<string, string> = {
  audit: 'A',
  validation: 'V',
  llm: 'IA',
  event: 'E',
  snapshot: 'S',
};

export const AuditTimeline: React.FC<AuditTimelineProps> = ({ events, onEventClick }) => {
  const { t } = useTranslation('audit');
  
  return (
    <div className="relative" role="region" aria-label={t('timeline.region_label')}>
      {/* Center line */}
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 lg:left-1/2 lg:-translate-x-0.5" />
      
      <ul className="space-y-6" role="list">
        {events.map((event, index) => {
          const color = LAYER_COLORS[event.layer] || '#6b7280';
          const isLeft = index % 2 === 0;
          
          return (
            <li
              key={event.id}
              role="listitem"
              className={`relative flex items-start ${isLeft ? 'lg:flex-row' : 'lg:flex-row-reverse'}`}
            >
              {/* Point */}
              <div
                className="absolute left-4 w-4 h-4 rounded-full border-2 border-white shadow z-10 lg:left-1/2 lg:-translate-x-2"
                style={{ backgroundColor: color }}
                aria-hidden="true"
              />
              
              {/* Content card */}
              <div
                className={`ml-10 lg:ml-0 lg:w-[45%] ${isLeft ? 'lg:mr-auto lg:pr-8' : 'lg:ml-auto lg:pl-8'}`}
              >
                <button
                  onClick={() => onEventClick(event.id)}
                  className="w-full text-left p-4 bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow focus:outline-none focus:ring-2 focus:ring-primary"
                  aria-label={`${event.title} - ${event.timestamp}`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className="px-2 py-0.5 text-xs font-medium text-white rounded"
                      style={{ backgroundColor: color }}
                    >
                      {LAYER_ICONS[event.layer]}
                    </span>
                    <span className="text-xs text-gray-500">{event.timestamp}</span>
                    {!event.signature_valid && (
                      <span className="text-xs text-red-600 font-medium" role="img" aria-label="Signature invalide">
                        ⚠ {t('timeline.signature_invalid')}
                      </span>
                    )}
                  </div>
                  <h3 className="font-medium text-gray-900">{event.title}</h3>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{event.description}</p>
                  <div className="text-xs text-gray-500 mt-2">{t('timeline.actor', { actor: event.actor })}</div>
                </button>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
```

---

### FICHIER C10 : `frontend/src/components/audit/EventDetail.tsx`

**Description** : Detail d'un evenement d'audit.

**Specifications** :
- Modal ou panel lateral
- Toutes les donnees de l'evenement
- JSON formate pour metadata
- Verification signature
- Copie dans le presse-papiers

---

### FICHIER C11 : `frontend/src/components/audit/PdfExport.tsx`

**Description** : Composant d'export PDF.

**Specifications** :
- Bouton export
- Etat de chargement
- Telechargement automatique
- Notification succes/erreur

---

### FICHIER C12 : `frontend/src/services/auditApi.ts`

**Description** : Client API pour l'audit.

**Specifications** :
- getTimeline(aoId, filters)
- listEvents(filters, pagination)
- exportPdf(aoId)
- verifySignature(eventId, layer)
- Types TypeScript

**Code attendu** :
```typescript
import { apiClient } from './api';

export interface AuditFilters {
  layers?: string[];
  startDate?: Date | null;
  endDate?: Date | null;
  actorId?: string | null;
}

export interface TimelineEvent {
  id: string;
  layer: string;
  timestamp: string;
  title: string;
  description: string;
  actor: string;
  signature_valid: boolean;
  data: Record<string, unknown>;
}

export interface TimelineResponse {
  ao_id: string;
  events_count: number;
  timeline: TimelineEvent[];
}

export const auditApi = {
  getTimeline: async (aoId: string, filters: AuditFilters): Promise<TimelineResponse> => {
    const params = new URLSearchParams();
    filters.layers?.forEach(l => params.append('layers', l));
    if (filters.startDate) params.set('start_date', filters.startDate.toISOString());
    if (filters.endDate) params.set('end_date', filters.endDate.toISOString());
    if (filters.actorId) params.set('actor_id', filters.actorId);
    
    const response = await apiClient.get(`/audit/timeline/${aoId}?${params}`);
    return response.data;
  },
  
  exportPdf: async (aoId: string): Promise<Blob> => {
    const response = await apiClient.get(`/audit/export/${aoId}`, {
      responseType: 'blob',
    });
    return response.data;
  },
  
  verifySignature: async (eventId: string, layer: string): Promise<boolean> => {
    const response = await apiClient.post('/audit/verify', { event_id: eventId, layer });
    return response.data.signature_valid;
  },
};
```

---

## GROUPE D : Conformite AI Act (14 fichiers)

### FICHIER D1 : `backend/app/ai_act/models.py`

**Description** : Models pour la conformite AI Act.

**Specifications** :
- AIPD : id, title, version, content, approved_by, approved_at, next_review
- AIContestation : id, decision_id, user_id, reason, status, reviewed_by, created_at, resolved_at
- AIDisclosure : id, decision_id, disclosure_text, shown_at, acknowledged
- XAIExplanation : id, decision_id, feature_importance, explanation_text, method
- AIAudit : id, ao_id, audit_type, findings, recommendations, auditor_id, created_at

**Code attendu** :
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class ContestationStatus(str, enum.Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class AIPD(Base):
    __tablename__ = 'aipds'
    __table_args__ = {'schema': 'ai_act'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('public.users.id'))
    approved_at = Column(DateTime(timezone=True))
    next_review = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AIContestation(Base):
    __tablename__ = 'ai_contestations'
    __table_args__ = {'schema': 'ai_act'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey('public.submissions.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), nullable=False)
    reason_type = Column(String(50), nullable=False)  # BIAS, ERROR, TRANSPARENCY, OTHER
    reason_description = Column(Text, nullable=False)
    status = Column(Enum(ContestationStatus), default=ContestationStatus.PENDING)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('public.users.id'))
    reviewer_decision = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolved_at = Column(DateTime(timezone=True))

class AIDisclosure(Base):
    __tablename__ = 'ai_disclosures'
    __table_args__ = {'schema': 'ai_act'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey('public.submissions.id'), nullable=False)
    disclosure_text = Column(Text, nullable=False)
    ai_system_name = Column(String(100), nullable=False)
    ai_system_version = Column(String(50), nullable=False)
    ai_system_provider = Column(String(100), nullable=False)
    shown_at = Column(DateTime(timezone=True))
    acknowledged = Column(DateTime(timezone=True))
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), nullable=False)

class XAIExplanation(Base):
    __tablename__ = 'xai_explanations'
    __table_args__ = {'schema': 'ai_act'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey('public.submissions.id'), nullable=False)
    feature_importance = Column(JSON, nullable=False)  # [{feature, weight, direction}]
    explanation_text = Column(Text, nullable=False)
    method = Column(String(50), nullable=False)  # SHAP, LIME, ATTENTION, RULE_BASED
    model_version = Column(String(50), nullable=False)
    confidence_score = Column(String(10))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class AIAudit(Base):
    __tablename__ = 'ai_audits'
    __table_args__ = {'schema': 'ai_act'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ao_id = Column(UUID(as_uuid=True), ForeignKey('public.aos.id'), nullable=False)
    audit_type = Column(String(50), nullable=False)  # REGULAR, TRIGGERED, ANNUAL
    findings = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    auditor_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
```

---

### FICHIER D2 : `backend/app/ai_act/service.py`

**Description** : Service pour la conformite AI Act.

**Specifications** :
- CreateDisclosure : creer divulgation IA
- RecordContestation : enregistrer contestation
- GetXAIExplanation : generer/generer explication
- CreateAIPD : creer/mettre a jour AIPD
- ScheduleAudit : planifier audit
- GetAIActComplianceReport : rapport complet

**Code attendu** :
```python
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .models import AIPD, AIContestation, AIDisclosure, XAIExplanation, AIAudit, ContestationStatus
from .repository import AIActRepository
from app.audit.service import AuditService

class AIActService:
    def __init__(self, db: Session, audit_service: AuditService):
        self.db = db
        self.repo = AIActRepository(db)
        self.audit = audit_service
    
    def create_disclosure(
        self,
        decision_id: UUID,
        user_id: UUID,
        ai_system_name: str = "GPT-4o",
        ai_system_version: str = "2024-08-06",
        ai_system_provider: str = "OpenAI",
    ) -> AIDisclosure:
        disclosure_text = self._generate_disclosure_text(
            ai_system_name, ai_system_version, ai_system_provider
        )
        
        disclosure = AIDisclosure(
            decision_id=decision_id,
            disclosure_text=disclosure_text,
            ai_system_name=ai_system_name,
            ai_system_version=ai_system_version,
            ai_system_provider=ai_system_provider,
            user_id=user_id,
        )
        
        result = self.repo.save_disclosure(disclosure)
        
        self.audit.log_audit_event(
            user_id=user_id,
            action="AI_DISCLOSURE_CREATED",
            resource_type="ai_disclosure",
            resource_id=result.id,
            metadata={"decision_id": str(decision_id)},
        )
        
        return result
    
    def record_contestation(
        self,
        decision_id: UUID,
        user_id: UUID,
        reason_type: str,
        reason_description: str,
    ) -> AIContestation:
        contestation = AIContestation(
            decision_id=decision_id,
            user_id=user_id,
            reason_type=reason_type,
            reason_description=reason_description,
            status=ContestationStatus.PENDING,
        )
        
        result = self.repo.save_contestation(contestation)
        
        # Log forensique
        self.audit.log_audit_event(
            user_id=user_id,
            action="AI_CONTESTATION_CREATED",
            resource_type="ai_contestation",
            resource_id=result.id,
            metadata={
                "decision_id": str(decision_id),
                "reason_type": reason_type,
            },
        )
        
        # Notification au valideur
        self._notify_validators(result)
        
        return result
    
    def get_xai_explanation(
        self,
        decision_id: UUID,
        method: str = "SHAP",
    ) -> Optional[XAIExplanation]:
        existing = self.repo.get_explanation(decision_id)
        if existing:
            return existing
        
        # Generate new explanation
        explanation = self._generate_explanation(decision_id, method)
        return self.repo.save_explanation(explanation)
    
    def _generate_disclosure_text(
        self,
        ai_system_name: str,
        ai_system_version: str,
        ai_system_provider: str,
    ) -> str:
        return f"""
        Ce traitement utilise un systeme d'intelligence artificielle ({ai_system_name} 
        version {ai_system_version}, fourni par {ai_system_provider}) pour analyser 
        et evaluer les soumissions. Cette analyse est utilisee comme aide a la decision 
        et ne remplace pas le jugement humain. Conformement au Reglement (UE) 2024/1689 
        (AI Act) et au Reglement (UE) 2016/679 (RGPD), vous avez le droit de demander 
        une explication de cette decision et de la contester.
        """
    
    def _generate_explanation(self, decision_id: UUID, method: str) -> XAIExplanation:
        # Integration avec le systeme de scoring pour extraire les features importance
        # This would connect to the scoring service
        ...
    
    def _notify_validators(self, contestation: AIContestation):
        # Send notification to validators
        ...
    
    def get_compliance_report(self) -> Dict[str, Any]:
        return {
            "total_decisions": self.repo.count_decisions(),
            "decisions_with_disclosure": self.repo.count_disclosures(),
            "contestations": {
                "total": self.repo.count_contestations(),
                "pending": self.repo.count_contestations_by_status(ContestationStatus.PENDING),
                "resolved": self.repo.count_contestations_by_status(ContestationStatus.ACCEPTED) + 
                           self.repo.count_contestations_by_status(ContestationStatus.REJECTED),
            },
            "xai_explanations": self.repo.count_explanations(),
            "aipd_status": self.repo.get_aipd_status(),
            "next_audit_due": self.repo.get_next_audit_date(),
            "compliance_score": self._calculate_compliance_score(),
        }
    
    def _calculate_compliance_score(self) -> float:
        # Calculate weighted compliance score
        ...
```

---

### FICHIER D3 : `backend/app/ai_act/xai.py`

**Description** : Explicabilite des decisions IA (XAI).

**Specifications** :
- SHAP values pour scoring
- Feature importance extraction
- Texte explicatif generation
- Visualisation data
- Methode configurable (SHAP, LIME, attention)

**Code attendu** :
```python
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class FeatureImportance:
    feature: str
    weight: float
    direction: str  # positive, negative, neutral
    description: str

@dataclass
class XAIResult:
    decision_id: str
    method: str
    feature_importance: List[FeatureImportance]
    explanation_text: str
    confidence: float

class XAIService:
    def __init__(self, model_service):
        self.model = model_service
    
    def explain_scoring_decision(
        self,
        decision_id: str,
        features: Dict[str, Any],
        score: float,
    ) -> XAIResult:
        # Calculate feature importance based on scoring weights
        importance = self._calculate_feature_importance(features, score)
        
        explanation = self._generate_explanation_text(importance, score)
        
        return XAIResult(
            decision_id=decision_id,
            method="RULE_BASED",
            feature_importance=importance,
            explanation_text=explanation,
            confidence=0.92,
        )
    
    def _calculate_feature_importance(
        self,
        features: Dict[str, Any],
        score: float,
    ) -> List[FeatureImportance]:
        importance = []
        
        # Price factor (40% weight)
        price_score = features.get('price_score', 0)
        importance.append(FeatureImportance(
            feature='Prix propose',
            weight=0.40 * price_score,
            direction='positive' if price_score > 0.5 else 'negative',
            description=f'Le prix propose represente {price_score:.0%} du score total',
        ))
        
        # Technical compliance (30% weight)
        tech_score = features.get('technical_score', 0)
        importance.append(FeatureImportance(
            feature='Conformite technique',
            weight=0.30 * tech_score,
            direction='positive' if tech_score > 0.5 else 'negative',
            description=f'La conformite technique aux criteres du cahier des charges contribue a {tech_score:.0%}',
        ))
        
        # Experience (20% weight)
        exp_score = features.get('experience_score', 0)
        importance.append(FeatureImportance(
            feature='Experience du candidat',
            weight=0.20 * exp_score,
            direction='positive' if exp_score > 0.5 else 'negative',
            description=f'L\'experience anterieure contribue a {exp_score:.0%} du score',
        ))
        
        # Deadline compliance (10% weight)
        deadline_score = features.get('deadline_score', 0)
        importance.append(FeatureImportance(
            feature='Respect des delais',
            weight=0.10 * deadline_score,
            direction='positive' if deadline_score > 0.5 else 'negative',
            description=f'Le respect des delais de soumission contribue a {deadline_score:.0%}',
        ))
        
        return sorted(importance, key=lambda x: abs(x.weight), reverse=True)
    
    def _generate_explanation_text(
        self,
        importance: List[FeatureImportance],
        score: float,
    ) -> str:
        top_factors = [f for f in importance if abs(f.weight) > 0.1]
        
        text = f"Le score de {score:.0%} est calcule sur la base des facteurs suivants :\n\n"
        
        for factor in top_factors:
            text += f"- {factor.feature} : {factor.description}\n"
        
        text += "\n"
        
        if score >= 0.7:
            text += "Ce candidat obtient un score eleve, principalement du aux facteurs positifs identifies."
        elif score >= 0.4:
            text += "Ce candidat obtient un score moyen, avec un equilibre entre facteurs positifs et negatifs."
        else:
            text += "Ce candidat obtient un score faible, principalement du aux facteurs negatifs identifies."
        
        text += "\n\nVous pouvez contester cette analyse si vous estimez qu'elle est inexacte ou biaisee."
        
        return text
```

---

### FICHIER D4 : `backend/app/ai_act/contestation.py`

**Description** : Workflow de contestation des decisions IA.

**Specifications** :
- Etats : PENDING -> UNDER_REVIEW -> ACCEPTED/REJECTED
- Notifications automatiques
- SLA de 30 jours
- Reexamen par humain obligatoire
- Traçabilite complete
- Export rapport

**Code attendu** :
```python
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from .models import AIContestation, ContestationStatus
from app.core.email import send_email
from app.audit.service import AuditService

class ContestationWorkflow:
    def __init__(self, db, audit_service: AuditService):
        self.db = db
        self.audit = audit_service
    
    def submit_contestation(
        self,
        decision_id: UUID,
        user_id: UUID,
        reason_type: str,
        reason_description: str,
    ) -> AIContestation:
        contestation = AIContestation(
            decision_id=decision_id,
            user_id=user_id,
            reason_type=reason_type,
            reason_description=reason_description,
            status=ContestationStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(contestation)
        self.db.commit()
        self.db.refresh(contestation)
        
        # Log forensique
        self.audit.log_audit_event(
            user_id=user_id,
            action="CONTESTATION_SUBMITTED",
            resource_type="ai_contestation",
            resource_id=contestation.id,
            metadata={
                "decision_id": str(decision_id),
                "reason_type": reason_type,
            },
        )
        
        # Notify validators
        self._notify_validators(contestation)
        
        return contestation
    
    def assign_to_reviewer(
        self,
        contestation_id: UUID,
        reviewer_id: UUID,
    ) -> AIContestation:
        contestation = self.db.query(AIContestation).get(contestation_id)
        if not contestation:
            raise ValueError("Contestation not found")
        
        contestation.status = ContestationStatus.UNDER_REVIEW
        contestation.reviewed_by = reviewer_id
        
        self.db.commit()
        self.db.refresh(contestation)
        
        # Notify user
        self._notify_user_contestation_update(contestation)
        
        return contestation
    
    def resolve_contestation(
        self,
        contestation_id: UUID,
        decision: str,  # ACCEPTED or REJECTED
        reviewer_notes: str,
    ) -> AIContestation:
        contestation = self.db.query(AIContestation).get(contestation_id)
        if not contestation:
            raise ValueError("Contestation not found")
        
        status = ContestationStatus.ACCEPTED if decision == "ACCEPTED" else ContestationStatus.REJECTED
        contestation.status = status
        contestation.reviewer_decision = reviewer_notes
        contestation.resolved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(contestation)
        
        # Log forensique
        self.audit.log_audit_event(
            user_id=contestation.reviewed_by,
            action=f"CONTESTATION_{decision}",
            resource_type="ai_contestation",
            resource_id=contestation.id,
            metadata={"reviewer_notes": reviewer_notes},
        )
        
        # Notify user
        self._notify_user_contestation_update(contestation)
        
        # If accepted, trigger re-scoring
        if status == ContestationStatus.ACCEPTED:
            self._trigger_rescoring(contestation.decision_id)
        
        return contestation
    
    def get_sla_status(self, contestation_id: UUID) -> dict:
        contestation = self.db.query(AIContestation).get(contestation_id)
        if not contestation:
            raise ValueError("Contestation not found")
        
        deadline = contestation.created_at + timedelta(days=30)
        now = datetime.utcnow()
        remaining = deadline - now
        
        return {
            "created_at": contestation.created_at.isoformat(),
            "deadline": deadline.isoformat(),
            "days_remaining": max(0, remaining.days),
            "overdue": remaining.days < 0,
            "status": contestation.status.value,
        }
    
    def _notify_validators(self, contestation: AIContestation):
        # Send email to all validators
        ...
    
    def _notify_user_contestation_update(self, contestation: AIContestation):
        # Send email to contesting user
        ...
    
    def _trigger_rescoring(self, decision_id: UUID):
        # Trigger manual re-scoring workflow
        ...
```

---

### FICHIER D5 : `backend/app/ai_act/documentation.py`

**Description** : Documentation des risques et AIPD.

**Specifications** :
- Generation AIPD automatisee
- Risques identifies avec mitigation
- Documentation technique du systeme IA
- Reevaluation automatique
- Export formats multiples

**Code attendu** :
```python
from typing import Dict, List, Any
from uuid import UUID
from datetime import datetime, timedelta

class AIPDGenerator:
    def __init__(self, db):
        self.db = db
    
    def generate_aipd(self) -> Dict[str, Any]:
        return {
            "title": "Analyse d'Impact relative a la Protection des Donnees - AO Platform",
            "version": "1.0",
            "date": datetime.utcnow().isoformat(),
            "responsable": "DPO AO Platform",
            "sections": {
                "1_description": self._describe_processing(),
                "2_necessity": self._assess_necessity(),
                "3_risks": self._identify_risks(),
                "4_mitigation": self._describe_mitigation(),
                "5_consultation": self._consultation_info(),
            },
            "risks": [
                {
                    "id": "R1",
                    "category": "BIAIS_ALGORITHMIQUE",
                    "description": "Risque de biais dans l'analyse automatique des soumissions",
                    "probability": "MOYENNE",
                    "severity": "ELEVEE",
                    "mitigation": [
                        "Validation humaine obligatoire",
                        "Audit regulier des modeles",
                        "Transparence des criteres",
                    ],
                    "residual_risk": "FAIBLE",
                },
                {
                    "id": "R2",
                    "category": "TRANSPARENCE",
                    "description": "Manque de transparence pour les candidats sur l'utilisation de l'IA",
                    "probability": "ELEVEE",
                    "severity": "MOYENNE",
                    "mitigation": [
                        "Divulgation explicite avant analyse",
                        "Droit a l'explication",
                        "Droit de contestation",
                    ],
                    "residual_risk": "FAIBLE",
                },
                {
                    "id": "R3",
                    "category": "DONNEES_PERSONNELLES",
                    "description": "Traitement de donnees personnelles des candidats",
                    "probability": "ELEVEE",
                    "severity": "ELEVEE",
                    "mitigation": [
                        "Minimisation des donnees",
                        "Pseudonymisation",
                        "Droit a l'effacement",
                        "Consentement explicite",
                    ],
                    "residual_risk": "MOYENNE",
                },
                {
                    "id": "R4",
                    "category": "SECURITE",
                    "description": "Fuite de donnees sensibles via l'API LLM",
                    "probability": "FAIBLE",
                    "severity": "ELEVEE",
                    "mitigation": [
                        "Chiffrement des prompts",
                        "Zero data retention avec OpenAI",
                        "Audit des acces API",
                    ],
                    "residual_risk": "FAIBLE",
                },
            ],
        }
    
    def _describe_processing(self) -> str:
        return """
        Le systeme AO Platform utilise des modeles de langage (LLM) pour analyser 
        et evaluer les soumissions aux appels d'offres. Les donnees traitees incluent 
        les documents de soumission, les profils des candidats, et les criteres du 
        cahier des charges. Le traitement est automatise avec validation humaine obligatoire.
        """
    
    def _assess_necessity(self) -> str:
        return """
        L'utilisation de l'IA est proportionnee aux objectifs legitimes de l'administration 
        (efficacite, equite, transparence). Les alternatives manuelles sont possibles mais 
        non viables a l'echelle. La decision finale reste toujours humaine.
        """
    
    def _identify_risks(self) -> List[Dict]:
        return self.generate_aipd()["risks"]
    
    def _describe_mitigation(self) -> str:
        return """
        Les mesures de mitigation incluent : validation humaine systematique, 
        audit regulier, transparence complete, droits des personnes (explication, 
        contestation, effacement), securite des donnees (chiffrement, zero retention), 
        et conformite AI Act niveau 3.
        """
    
    def _consultation_info(self) -> str:
        return """
        La CNIL a ete consultee. Les representants des candidats ont ete informes. 
        Le DPO valide cette analyse.
        """
```

---

### FICHIER D6 : `backend/app/api/routes/ai_act.py`

**Description** : Routes API pour la conformite AI Act.

**Specifications** :
- POST /ai-act/disclosure : creer divulgation
- POST /ai-act/contest : soumettre contestation
- GET /ai-act/explanation/{decision_id} : explication XAI
- GET /ai-act/compliance-report : rapport conformite
- GET /ai-act/aipd : AIPD
- PUT /ai-act/contest/{id}/resolve : resoudre contestation
- GET /ai-act/contest/{id}/sla : statut SLA

**Code attendu** :
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.deps import get_db, get_current_user, require_role
from app.ai_act.service import AIActService
from app.ai_act.xai import XAIService
from app.ai_act.contestation import ContestationWorkflow
from app.audit.service import AuditService
from app.models.user import User

router = APIRouter(prefix="/ai-act", tags=["ai_act"])

def get_ai_act_service(
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(),
) -> AIActService:
    return AIActService(db, audit_service)

@router.post("/disclosure")
async def create_disclosure(
    decision_id: UUID,
    service: AIActService = Depends(get_ai_act_service),
    current_user: User = Depends(get_current_user),
):
    disclosure = service.create_disclosure(
        decision_id=decision_id,
        user_id=current_user.id,
    )
    return {
        "id": str(disclosure.id),
        "disclosure_text": disclosure.disclosure_text,
        "ai_system_name": disclosure.ai_system_name,
        "created_at": disclosure.created_at.isoformat(),
    }

@router.post("/contest")
async def submit_contestation(
    decision_id: UUID,
    reason_type: str,
    reason_description: str,
    workflow: ContestationWorkflow = Depends(),
    current_user: User = Depends(get_current_user),
):
    contestation = workflow.submit_contestation(
        decision_id=decision_id,
        user_id=current_user.id,
        reason_type=reason_type,
        reason_description=reason_description,
    )
    return {
        "id": str(contestation.id),
        "status": contestation.status.value,
        "created_at": contestation.created_at.isoformat(),
        "sla_deadline": workflow.get_sla_status(contestation.id)["deadline"],
    }

@router.get("/explanation/{decision_id}")
async def get_explanation(
    decision_id: UUID,
    method: str = "SHAP",
    service: AIActService = Depends(get_ai_act_service),
    current_user: User = Depends(get_current_user),
):
    explanation = service.get_xai_explanation(decision_id, method)
    if not explanation:
        raise HTTPException(status_code=404, detail="Explanation not found")
    
    return {
        "decision_id": str(explanation.decision_id),
        "method": explanation.method,
        "feature_importance": explanation.feature_importance,
        "explanation_text": explanation.explanation_text,
        "confidence": explanation.confidence,
        "created_at": explanation.created_at.isoformat(),
    }

@router.get("/compliance-report")
async def get_compliance_report(
    service: AIActService = Depends(get_ai_act_service),
    current_user: User = Depends(require_role(["admin"])),
):
    return service.get_compliance_report()

@router.get("/aipd")
async def get_aipd(
    service: AIActService = Depends(get_ai_act_service),
):
    from app.ai_act.documentation import AIPDGenerator
    generator = AIPDGenerator(service.db)
    return generator.generate_aipd()

@router.put("/contest/{contestation_id}/resolve")
async def resolve_contestation(
    contestation_id: UUID,
    decision: str,
    reviewer_notes: str,
    workflow: ContestationWorkflow = Depends(),
    current_user: User = Depends(require_role(["admin", "valideur"])),
):
    contestation = workflow.resolve_contestation(
        contestation_id=contestation_id,
        decision=decision,
        reviewer_notes=reviewer_notes,
    )
    return {
        "id": str(contestation.id),
        "status": contestation.status.value,
        "resolved_at": contestation.resolved_at.isoformat() if contestation.resolved_at else None,
    }

@router.get("/contest/{contestation_id}/sla")
async def get_contestation_sla(
    contestation_id: UUID,
    workflow: ContestationWorkflow = Depends(),
    current_user: User = Depends(get_current_user),
):
    return workflow.get_sla_status(contestation_id)
```

---

### FICHIER D7 : `frontend/src/components/ai/AIBadge.tsx`

**Description** : Badge indicateur d'utilisation IA.

**Specifications** :
- Petit badge avec texte "IA" ou "AI"
- Couleur distincte (violet)
- Tooltip accessible avec explication
- Aria-label
- Clickable pour plus d'infos

**Code attendu** :
```tsx
import React from 'react';
import { useTranslation } from 'react-i18next';

interface AIBadgeProps {
  onClick?: () => void;
  size?: 'sm' | 'md';
  showLabel?: boolean;
}

export const AIBadge: React.FC<AIBadgeProps> = ({ onClick, size = 'sm', showLabel = true }) => {
  const { t } = useTranslation('ai');
  
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
  };
  
  return (
    <span
      role="img"
      aria-label={t('badge.label')}
      onClick={onClick}
      className={`inline-flex items-center gap-1 rounded font-medium bg-purple-100 text-purple-800 ${
        sizeClasses[size]
      } ${onClick ? 'cursor-pointer hover:bg-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500' : ''}`}
      tabIndex={onClick ? 0 : -1}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" />
      </svg>
      {showLabel && <span>{t('badge.text')}</span>}
    </span>
  );
};
```

---

### FICHIER D8 : `frontend/src/components/ai/AITransparencyModal.tsx`

**Description** : Modal de transparence avant traitement IA.

**Specifications** :
- Affiche avant analyse IA
- Explication du traitement
- Systeme utilise (nom, version, fournisseur)
- Droit a l'explication
- Droit de contestation
- Checkbox d'accord obligatoire
- Bouton continuer / annuler

**Code attendu** :
```tsx
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AccessibleModal } from '../AccessibleModal';

interface AITransparencyModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  aiSystemName?: string;
  aiSystemVersion?: string;
  aiSystemProvider?: string;
}

export const AITransparencyModal: React.FC<AITransparencyModalProps> = ({
  isOpen,
  onConfirm,
  onCancel,
  aiSystemName = "GPT-4o",
  aiSystemVersion = "2024-08-06",
  aiSystemProvider = "OpenAI",
}) => {
  const { t } = useTranslation('ai');
  const [acknowledged, setAcknowledged] = useState(false);
  
  return (
    <AccessibleModal
      isOpen={isOpen}
      onClose={onCancel}
      title={t('transparency.title')}
    >
      <div className="space-y-4">
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <p className="text-sm text-yellow-800">
            {t('transparency.warning')}
          </p>
        </div>
        
        <div className="space-y-2">
          <h3 className="font-medium">{t('transparency.system_info')}</h3>
          <ul className="text-sm space-y-1 text-gray-600">
            <li>{t('transparency.system_name', { name: aiSystemName })}</li>
            <li>{t('transparency.system_version', { version: aiSystemVersion })}</li>
            <li>{t('transparency.system_provider', { provider: aiSystemProvider })}</li>
          </ul>
        </div>
        
        <div className="space-y-2">
          <h3 className="font-medium">{t('transparency.your_rights')}</h3>
          <ul className="text-sm space-y-1 text-gray-600">
            <li>{t('transparency.right_explanation')}</li>
            <li>{t('transparency.right_contest')}</li>
            <li>{t('transparency.right_human')}</li>
          </ul>
        </div>
        
        <div className="flex items-start gap-2">
          <input
            type="checkbox"
            id="ai-acknowledge"
            checked={acknowledged}
            onChange={(e) => setAcknowledged(e.target.checked)}
            className="mt-1"
          />
          <label htmlFor="ai-acknowledge" className="text-sm">
            {t('transparency.acknowledge')}
          </label>
        </div>
        
        <div className="flex gap-3 justify-end pt-4">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400"
          >
            {t('actions.cancel')}
          </button>
          <button
            onClick={onConfirm}
            disabled={!acknowledged}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            {t('actions.continue')}
          </button>
        </div>
      </div>
    </AccessibleModal>
  );
};
```

---

### FICHIER D9 : `frontend/src/components/ai/XAIExplanation.tsx`

**Description** : Composant d'explication XAI pour les decisions.

**Specifications** :
- Graphique d'importance des features
- Texte explicatif
- Bouton export PDF
- Bouton contester
- Responsive
- Accessible (aria-labels, descriptions)

**Code attendu** :
```tsx
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';

interface FeatureImportance {
  feature: string;
  weight: number;
  direction: string;
  description: string;
}

interface XAIExplanationProps {
  decisionId: string;
  onContest: () => void;
  onExport: () => void;
}

export const XAIExplanation: React.FC<XAIExplanationProps> = ({
  decisionId,
  onContest,
  onExport,
}) => {
  const { t } = useTranslation('ai');
  const [expandedFeature, setExpandedFeature] = useState<string | null>(null);
  
  const { data, isLoading } = useQuery({
    queryKey: ['xai-explanation', decisionId],
    queryFn: async () => {
      const response = await fetch(`/api/ai-act/explanation/${decisionId}`);
      return response.json();
    },
  });
  
  if (isLoading) return <div role="status">{t('common.loading')}</div>;
  if (!data) return null;
  
  const maxWeight = Math.max(...data.feature_importance.map((f: FeatureImportance) => Math.abs(f.weight)));
  
  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">{t('explanation.title')}</h2>
        <div className="flex gap-2">
          <button
            onClick={onExport}
            className="px-3 py-1.5 text-sm bg-gray-100 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400"
            aria-label={t('explanation.export_pdf')}
          >
            {t('explanation.export_pdf')}
          </button>
          <button
            onClick={onContest}
            className="px-3 py-1.5 text-sm bg-purple-100 text-purple-800 rounded hover:bg-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
            aria-label={t('explanation.contest')}
          >
            {t('explanation.contest')}
          </button>
        </div>
      </div>
      
      <p className="text-sm text-gray-600 mb-4">{data.explanation_text}</p>
      
      <h3 className="text-sm font-medium mb-3">{t('explanation.factors')}</h3>
      
      <div className="space-y-3" role="list" aria-label={t('explanation.factors_list')}>
        {data.feature_importance.map((feature: FeatureImportance) => {
          const width = (Math.abs(feature.weight) / maxWeight) * 100;
          const color = feature.direction === 'positive' ? 'bg-green-500' : 
                       feature.direction === 'negative' ? 'bg-red-500' : 'bg-gray-500';
          
          return (
            <div
              key={feature.feature}
              role="listitem"
              className="space-y-1"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{feature.feature}</span>
                <span className="text-sm text-gray-500">
                  {Math.abs(feature.weight).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`${color} h-2 rounded-full transition-all`}
                  style={{ width: `${width}%` }}
                  role="progressbar"
                  aria-valuenow={width}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${feature.feature}: ${feature.weight.toFixed(1)}%`}
                />
              </div>
              <button
                onClick={() => setExpandedFeature(
                  expandedFeature === feature.feature ? null : feature.feature
                )}
                className="text-xs text-gray-500 hover:text-gray-700 focus:outline-none focus:underline"
                aria-expanded={expandedFeature === feature.feature}
              >
                {expandedFeature === feature.feature ? t('common.hide') : t('common.details')}
              </button>
              {expandedFeature === feature.feature && (
                <p className="text-xs text-gray-600 mt-1">{feature.description}</p>
              )}
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t text-xs text-gray-500">
        {t('explanation.method', { method: data.method })} | 
        {t('explanation.confidence', { score: data.confidence })} | 
        {t('explanation.generated_at', { date: data.created_at })}
      </div>
    </div>
  );
};
```

---

### FICHIER D10 : `frontend/src/components/ai/ContestDecision.tsx`

**Description** : Formulaire de contestation d'une decision IA.

**Specifications** :
- Selection raison predefinie
- Champ texte libre
- Compteur caracteres
- Validation
- Soumission avec confirmation
- Etat de chargement
- Message succes

**Code attendu** :
```tsx
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';

const REASON_OPTIONS = [
  { value: 'BIAS', label: 'Biais detecte dans l\'analyse' },
  { value: 'ERROR', label: 'Erreur factuelle' },
  { value: 'TRANSPARENCY', label: 'Manque de transparence' },
  { value: 'OTHER', label: 'Autre raison' },
];

interface ContestDecisionProps {
  decisionId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export const ContestDecision: React.FC<ContestDecisionProps> = ({
  decisionId,
  onSuccess,
  onCancel,
}) => {
  const { t } = useTranslation('ai');
  const [reasonType, setReasonType] = useState('');
  const [reasonDescription, setReasonDescription] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const contestMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/ai-act/contest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision_id: decisionId,
          reason_type: reasonType,
          reason_description: reasonDescription,
        }),
      });
      if (!response.ok) throw new Error('Failed to submit contestation');
      return response.json();
    },
    onSuccess,
  });
  
  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!reasonType) newErrors.reasonType = t('contest.error.reason_required');
    if (!reasonDescription || reasonDescription.length < 20) {
      newErrors.reasonDescription = t('contest.error.description_min');
    }
    if (reasonDescription.length > 2000) {
      newErrors.reasonDescription = t('contest.error.description_max');
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      contestMutation.mutate();
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold mb-2">{t('contest.title')}</h2>
        <p className="text-sm text-gray-600">{t('contest.subtitle')}</p>
      </div>
      
      <div>
        <label htmlFor="reason-type" className="block text-sm font-medium mb-1">
          {t('contest.reason_label')}
        </label>
        <select
          id="reason-type"
          value={reasonType}
          onChange={(e) => setReasonType(e.target.value)}
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary"
          aria-invalid={!!errors.reasonType}
          aria-describedby={errors.reasonType ? 'reason-type-error' : undefined}
        >
          <option value="">{t('contest.select_reason')}</option>
          {REASON_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        {errors.reasonType && (
          <p id="reason-type-error" className="text-sm text-red-600 mt-1" role="alert">
            {errors.reasonType}
          </p>
        )}
      </div>
      
      <div>
        <label htmlFor="reason-description" className="block text-sm font-medium mb-1">
          {t('contest.description_label')}
        </label>
        <textarea
          id="reason-description"
          value={reasonDescription}
          onChange={(e) => setReasonDescription(e.target.value)}
          rows={5}
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary"
          aria-invalid={!!errors.reasonDescription}
          aria-describedby={errors.reasonDescription ? 'reason-description-error' : undefined}
        />
        <div className="flex justify-between mt-1">
          {errors.reasonDescription && (
            <p id="reason-description-error" className="text-sm text-red-600" role="alert">
              {errors.reasonDescription}
            </p>
          )}
          <span className="text-xs text-gray-500 ml-auto">
            {reasonDescription.length}/2000
          </span>
        </div>
      </div>
      
      <div className="bg-blue-50 border border-blue-200 rounded p-3">
        <p className="text-sm text-blue-800">{t('contest.sla_notice')}</p>
      </div>
      
      <div className="flex gap-3 justify-end">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400"
        >
          {t('actions.cancel')}
        </button>
        <button
          type="submit"
          disabled={contestMutation.isPending}
          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          {contestMutation.isPending ? t('common.submitting') : t('contest.submit')}
        </button>
      </div>
    </form>
  );
};
```

---

### FICHIER D11 : `frontend/src/components/ai/AIDisclosure.tsx`

**Description** : Composant de divulgation IA affiche aux utilisateurs.

**Specifications** :
- Bandeau d'information
- Icone IA
- Texte de divulgation
- Lien vers plus d'infos
- Lien vers politique de confidentialite
- Dismissible (avec persistance)

**Code attendu** :
```tsx
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

interface AIDisclosureBannerProps {
  disclosureText?: string;
  aiSystemName?: string;
  onLearnMore?: () => void;
}

export const AIDisclosureBanner: React.FC<AIDisclosureBannerProps> = ({
  disclosureText,
  aiSystemName = "GPT-4o",
  onLearnMore,
}) => {
  const { t } = useTranslation('ai');
  const [dismissed, setDismissed] = useState(false);
  
  useEffect(() => {
    const key = `ai-disclosure-dismissed-${aiSystemName}`;
    const stored = localStorage.getItem(key);
    if (stored === 'true') setDismissed(true);
  }, [aiSystemName]);
  
  const handleDismiss = () => {
    const key = `ai-disclosure-dismissed-${aiSystemName}`;
    localStorage.setItem(key, 'true');
    setDismissed(true);
  };
  
  if (dismissed) return null;
  
  return (
    <div
      role="region"
      aria-label={t('disclosure.region_label')}
      className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5" aria-hidden="true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-purple-600">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="text-sm text-purple-900">
            {disclosureText || t('disclosure.default_text', { aiSystemName })}
          </p>
          {onLearnMore && (
            <button
              onClick={onLearnMore}
              className="text-sm text-purple-700 underline hover:text-purple-900 mt-1 focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {t('disclosure.learn_more')}
            </button>
          )}
        </div>
        <button
          onClick={handleDismiss}
          aria-label={t('disclosure.dismiss')}
          className="flex-shrink-0 p-1 text-purple-500 hover:text-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 rounded"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M6 6L18 18M18 6L6 18" stroke="currentColor" strokeWidth="2" />
          </svg>
        </button>
      </div>
    </div>
  );
};
```

---

### FICHIER D12 : `frontend/src/pages/AIActCompliance.tsx`

**Description** : Page de conformite AI Act.

**Specifications** :
- Resume de la conformite
- Indicateurs cles (KPIs)
- Liste des contestations
- AIPD telechargeable
- Documentation des risques
- Dates des prochains audits
- Lien vers rapports

---

### FICHIER D13 : `docs/docs/legal/aipd.md`

**Description** : AIPD dans la documentation.

**Specifications** :
- Contenu complet de l'AIPD
- Mise a jour datee
- Version
- Responsable
- Risques documentes
- Mesures de mitigation
- Formulaire de contact DPO

---

### FICHIER D14 : `docs/docs/legal/ai-act-compliance.md`

**Description** : Documentation sur la conformite AI Act.

**Specifications** :
- Resume des obligations
- Comment la plateforme repond
- Droits des utilisateurs
- Procedure de contestation
- Contact
- Mises a jour

---

## GROUPE E : Documentation utilisateur (30 fichiers)

### FICHIER E1 : `frontend/src/tours/onboardingTour.ts`

**Description** : Tour guide pour nouveau utilisateur.

**Specifications** :
- 10 etapes
- Cibles : header, sidebar, dashboard, boutons principaux
- Textes i18n
- Placement adaptatif
- Progression sauvegardee

**Code attendu** :
```typescript
import { Step } from 'react-joyride';

export const onboardingTourSteps = (t: (key: string) => string): Step[] => [
  {
    target: '.tour-welcome',
    content: t('tours.onboarding.welcome'),
    placement: 'center',
    disableBeacon: true,
  },
  {
    target: '.tour-dashboard',
    content: t('tours.onboarding.dashboard'),
    placement: 'right',
  },
  {
    target: '.tour-ao-list',
    content: t('tours.onboarding.ao_list'),
    placement: 'right',
  },
  {
    target: '.tour-create-ao',
    content: t('tours.onboarding.create_ao'),
    placement: 'bottom',
  },
  {
    target: '.tour-submissions',
    content: t('tours.onboarding.submissions'),
    placement: 'right',
  },
  {
    target: '.tour-scoring',
    content: t('tours.onboarding.scoring'),
    placement: 'left',
  },
  {
    target: '.tour-alerts',
    content: t('tours.onboarding.alerts'),
    placement: 'bottom',
  },
  {
    target: '.tour-profile',
    content: t('tours.onboarding.profile'),
    placement: 'bottom',
  },
  {
    target: '.tour-help',
    content: t('tours.onboarding.help'),
    placement: 'left',
  },
  {
    target: '.tour-complete',
    content: t('tours.onboarding.complete'),
    placement: 'center',
  },
];
```

---

### FICHIER E2 : `frontend/src/tours/createAOTour.ts`

**Description** : Tour guide pour creation d'AO.

**Specifications** :
- 8 etapes
- Cibles : formulaire, champs, upload, boutons
- Validation visuelle

**Code attendu** :
```typescript
import { Step } from 'react-joyride';

export const createAOTourSteps = (t: (key: string) => string): Step[] => [
  {
    target: '.tour-ao-title',
    content: t('tours.create_ao.title'),
    placement: 'bottom',
  },
  {
    target: '.tour-ao-description',
    content: t('tours.create_ao.description'),
    placement: 'bottom',
  },
  {
    target: '.tour-ao-criteria',
    content: t('tours.create_ao.criteria'),
    placement: 'right',
  },
  {
    target: '.tour-ao-deadline',
    content: t('tours.create_ao.deadline'),
    placement: 'bottom',
  },
  {
    target: '.tour-ao-documents',
    content: t('tours.create_ao.documents'),
    placement: 'left',
  },
  {
    target: '.tour-ao-review',
    content: t('tours.create_ao.review'),
    placement: 'top',
  },
  {
    target: '.tour-ao-publish',
    content: t('tours.create_ao.publish'),
    placement: 'top',
  },
  {
    target: '.tour-ao-success',
    content: t('tours.create_ao.success'),
    placement: 'center',
  },
];
```

---

### FICHIER E3 : `frontend/src/tours/submitTour.ts`

**Description** : Tour guide pour soumission candidat.

**Specifications** :
- 6 etapes
- Cibles : formulaire, documents, confirmation

---

### FICHIER E4 : `frontend/src/tours/validateTour.ts`

**Description** : Tour guide pour validation.

**Specifications** :
- 5 etapes
- Cibles : liste, decision, raison, confirmation

---

### FICHIER E5 : `frontend/src/tours/auditTour.ts`

**Description** : Tour guide pour audit.

**Specifications** :
- 4 etapes
- Cibles : timeline, filtres, detail, export

---

### FICHIER E6 : `frontend/src/components/TourWrapper.tsx`

**Description** : Wrapper pour react-joyride avec configuration globale.

**Specifications** :
- Configuration i18n
- Theming
- Callbacks (start, finish, skip)
- Persistance progression
- Accessibility

**Code attendu** :
```tsx
import React, { useState, useCallback } from 'react';
import Joyride, { CallBackProps, STATUS, Step } from 'react-joyride';
import { useTranslation } from 'react-i18next';

interface TourWrapperProps {
  steps: Step[];
  tourId: string;
  run?: boolean;
}

export const TourWrapper: React.FC<TourWrapperProps> = ({ steps, tourId, run = false }) => {
  const { t } = useTranslation('common');
  const [stepIndex, setStepIndex] = useState(0);
  const [isRunning, setIsRunning] = useState(run);
  
  const handleCallback = useCallback((data: CallBackProps) => {
    const { status, index, type } = data;
    
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setIsRunning(false);
      setStepIndex(0);
      localStorage.setItem(`tour-completed-${tourId}`, 'true');
    } else if (type === 'step:after') {
      setStepIndex(index + 1);
    }
  }, [tourId]);
  
  return (
    <Joyride
      steps={steps}
      run={isRunning}
      stepIndex={stepIndex}
      continuous
      showSkipButton
      showProgress
      locale={{
        back: t('tour.back'),
        close: t('tour.close'),
        last: t('tour.last'),
        next: t('tour.next'),
        skip: t('tour.skip'),
      }}
      styles={{
        options: {
          primaryColor: '#4f46e5',
          textColor: '#1f2937',
          zIndex: 1000,
        },
      }}
      callback={handleCallback}
    />
  );
};
```

---

### FICHIER E7 : `frontend/src/hooks/useTourProgress.ts`

**Description** : Hook pour gerer la progression des tours.

**Specifications** :
- Check si tour deja completé
- Sauvegarde progression
- Reset progression
- Liste des tours disponibles

**Code attendu** :
```typescript
import { useCallback, useState, useEffect } from 'react';

const TOUR_STORAGE_KEY = 'tour_progress';

interface TourProgress {
  [tourId: string]: {
    completed: boolean;
    lastStep: number;
    completedAt?: string;
  };
}

export const useTourProgress = () => {
  const [progress, setProgress] = useState<TourProgress>(() => {
    try {
      const stored = localStorage.getItem(TOUR_STORAGE_KEY);
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  });
  
  const isTourCompleted = useCallback((tourId: string): boolean => {
    return progress[tourId]?.completed ?? false;
  }, [progress]);
  
  const markTourCompleted = useCallback((tourId: string) => {
    setProgress(prev => {
      const updated = {
        ...prev,
        [tourId]: {
          completed: true,
          lastStep: -1,
          completedAt: new Date().toISOString(),
        },
      };
      localStorage.setItem(TOUR_STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);
  
  const saveProgress = useCallback((tourId: string, stepIndex: number) => {
    setProgress(prev => {
      const updated = {
        ...prev,
        [tourId]: {
          ...prev[tourId],
          lastStep: stepIndex,
        },
      };
      localStorage.setItem(TOUR_STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);
  
  const resetTour = useCallback((tourId: string) => {
    setProgress(prev => {
      const { [tourId]: _, ...rest } = prev;
      localStorage.setItem(TOUR_STORAGE_KEY, JSON.stringify(rest));
      return rest;
    });
  }, []);
  
  const resetAll = useCallback(() => {
    localStorage.removeItem(TOUR_STORAGE_KEY);
    setProgress({});
  }, []);
  
  return {
    progress,
    isTourCompleted,
    markTourCompleted,
    saveProgress,
    resetTour,
    resetAll,
  };
};
```

---

### FICHIER E8 : `frontend/src/components/HelpButton.tsx`

**Description** : Bouton d'aide contextuel flottant.

**Specifications** :
- Position fixe bas-droite
- Menu deroulant avec options
- Liens vers tours, documentation, support
- Accessibilite (aria-label, keyboard)
- Animation douce

**Code attendu** :
```tsx
import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

interface HelpButtonProps {
  onStartTour: (tourId: string) => void;
  currentPage?: string;
}

export const HelpButton: React.FC<HelpButtonProps> = ({ onStartTour, currentPage }) => {
  const { t } = useTranslation('common');
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') setOpen(false);
  };
  
  const tourOptions = [
    { id: 'onboarding', label: t('help.tour_onboarding'), icon: '👋' },
    { id: 'create-ao', label: t('help.tour_create_ao'), icon: '📝' },
    { id: 'submit', label: t('help.tour_submit'), icon: '📤' },
    { id: 'validate', label: t('help.tour_validate'), icon: '✅' },
    { id: 'audit', label: t('help.tour_audit'), icon: '🔍' },
  ];
  
  return (
    <div ref={ref} className="fixed bottom-6 right-6 z-50" onKeyDown={handleKeyDown}>
      {open && (
        <div className="absolute bottom-full right-0 mb-2 w-64 bg-white rounded-lg shadow-xl border overflow-hidden">
          <div className="px-4 py-3 border-b bg-gray-50">
            <h3 className="text-sm font-semibold">{t('help.title')}</h3>
          </div>
          <div className="py-2">
            <div className="px-4 py-1 text-xs text-gray-500 uppercase font-medium">
              {t('help.tours')}
            </div>
            {tourOptions.map(tour => (
              <button
                key={tour.id}
                onClick={() => {
                  onStartTour(tour.id);
                  setOpen(false);
                }}
                className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 focus:outline-none focus:bg-gray-100 flex items-center gap-2"
              >
                <span aria-hidden="true">{tour.icon}</span>
                {tour.label}
              </button>
            ))}
            <div className="border-t my-1" />
            <div className="px-4 py-1 text-xs text-gray-500 uppercase font-medium">
              {t('help.resources')}
            </div>
            <a
              href="/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="block px-4 py-2 text-sm hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
            >
              {t('help.documentation')}
            </a>
            <a
              href="mailto:support@ao-platform.com"
              className="block px-4 py-2 text-sm hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
            >
              {t('help.contact_support')}
            </a>
          </div>
        </div>
      )}
      
      <button
        onClick={() => setOpen(!open)}
        aria-label={t('help.button_label')}
        aria-expanded={open}
        className="w-12 h-12 rounded-full bg-primary text-white shadow-lg hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 flex items-center justify-center transition-transform hover:scale-110"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" stroke="currentColor" strokeWidth="2" />
          <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3M12 17h.01" stroke="currentColor" strokeWidth="2" />
        </svg>
      </button>
    </div>
  );
};
```

---

### FICHIER E9-E28 : `docs/docs/guides/01-create-ao.md` a `docs/docs/guides/20-faq.md`

**Description** : 20 guides metier pour le Help Center.

**Specifications par guide** :
- Frontmatter avec titre, description, sidebar_position
- Contenu detaille avec etapes numerotees
- Captures d'ecran (placeholders)
- Liens vers autres guides
- Table des matieres
- FAQ a la fin
- Tags
- Version

**Exemple guide 1** :
```markdown
---
sidebar_position: 1
title: "Creer un appel d'offres"
description: "Guide etape par etape pour creer un nouvel appel d'offres sur la plateforme"
tags: [ao, creation, guide]
---

# Creer un appel d'offres

Ce guide vous accompagne dans la creation d'un appel d'offres (AO) sur la plateforme AO Platform.

## Prerequis

- Etre connecte avec un compte acheteur
- Avoir les permissions de creation d'AO
- Avoir prepare le cahier des charges

## Etape 1 : Acceder au formulaire

1. Connectez-vous a votre compte
2. Cliquez sur "Appels d'offres" dans le menu lateral
3. Cliquez sur le bouton "Nouvel AO" en haut a droite

## Etape 2 : Remplir les informations generales

- **Titre** : Nom explicite de l'AO (obligatoire, max 200 caracteres)
- **Description** : Description detaillee du besoin (obligatoire)
- **Categorie** : Selectionnez la categorie appropriee
- **Budget estimé** : Indiquez le budget previsionnel

## Etape 3 : Definir les criteres de selection

Les criteres permettent au systeme de scoring automatique d'evaluer les soumissions.

1. Ajoutez des criteres avec leur ponderation
2. La somme des ponderations doit egaler 100%
3. Definissez si chaque critere est obligatoire ou optionnel

### Criteres recommandes

| Critere | Ponderation | Obligatoire |
|---------|-------------|-------------|
| Prix | 40% | Oui |
| Qualite technique | 30% | Oui |
| Experience | 20% | Non |
| Delai | 10% | Non |

## Etape 4 : Definir le calendrier

- **Date de publication** : Date a laquelle l'AO sera visible
- **Date limite de soumission** : Deadline pour les candidats
- **Date de decision prevue** : Date estimée de notification

:::tip
Laissez au moins 21 jours entre la publication et la deadline pour respecter les delais legaux.
:::

## Etape 5 : Telecharger les documents

Telechargez le cahier des charges et tout document annexe :

- Cahier des charges (PDF, DOCX)
- Reglement de consultation
- Formulaires de soumission

:::note
Taille maximale par fichier : 50 Mo. Formats acceptes : PDF, DOCX, XLSX.
:::

## Etape 6 : Reviser et publier

1. Verifiez le resume de l'AO
2. Corrigez si necessaire
3. Cliquez sur "Publier l'AO"

:::caution
Une fois publie, l'AO ne peut plus etre modifie. En cas d'erreur, vous devrez le retirer et en creer un nouveau.
:::

## FAQ

**Q : Puis-je sauvegarder un brouillon ?**
R : Oui, cliquez sur "Enregistrer comme brouillon" a toute etape.

**Q : Combien de criteres puis-je ajouter ?**
R : Maximum 10 criteres par AO.

**Q : Puis-je modifier l'AO apres publication ?**
R : Non, mais vous pouvez publier un avenant avec modifications mineures.
```

---

### FICHIER E29 : `docs/docusaurus.config.js`

**Description** : Configuration Docusaurus pour le Help Center.

**Specifications** :
- Theme classique
- Search local
- i18n support
- Sidebar auto
- Custom CSS
- Analytics
- Versions

**Code attendu** :
```javascript
// @ts-check
/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AO Platform - Centre d\'aide',
  tagline: 'Guides et documentation pour la gestion des appels d\'offres',
  url: 'https://docs.ao-platform.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'ao-platform',
  projectName: 'docs',
  i18n: {
    defaultLocale: 'fr',
    locales: ['fr', 'nl', 'en', 'ar'],
    localeConfigs: {
      fr: { label: 'Francais' },
      nl: { label: 'Nederlands' },
      en: { label: 'English' },
      ar: { label: 'Arabic', direction: 'rtl' },
    },
  },
  themeConfig: {
    navbar: {
      title: 'AO Platform Help',
      logo: { alt: 'AO Platform Logo', src: 'img/logo.svg' },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'guidesSidebar',
          position: 'left',
          label: 'Guides',
        },
        {
          type: 'docSidebar',
          sidebarId: 'apiSidebar',
          position: 'left',
          label: 'API',
        },
        {
          type: 'docSidebar',
          sidebarId: 'legalSidebar',
          position: 'left',
          label: 'Legal',
        },
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://github.com/ao-platform/docs',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Guides',
          items: [
            { label: 'Creer un AO', to: '/docs/guides/create-ao' },
            { label: 'Scoring automatique', to: '/docs/guides/auto-scoring' },
            { label: 'FAQ', to: '/docs/guides/faq' },
          ],
        },
        {
          title: 'Legal',
          items: [
            { label: 'RGPD', to: '/docs/legal/rgpd' },
            { label: 'AI Act', to: '/docs/legal/ai-act-compliance' },
            { label: 'AIPD', to: '/docs/legal/aipd' },
          ],
        },
        {
          title: 'Support',
          items: [
            { label: 'Contact', href: 'mailto:support@ao-platform.com' },
            { label: 'Status', href: 'https://status.ao-platform.com' },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} AO Platform SAS.`,
    },
    prism: {
      theme: require('prism-react-renderer').themes.github,
      darkTheme: require('prism-react-renderer').themes.dracula,
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'ao-platform',
    },
  },
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/ao-platform/docs/edit/main/',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};

module.exports = config;
```

---

### FICHIER E30 : `docs/Dockerfile`

**Description** : Dockerfile pour le Help Center Docusaurus.

**Specifications** :
- Node 20 pour build
- Nginx alpine pour serveur
- Build statique
- Compression gzip
- Health check

**Code attendu** :
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
```

---

## GROUPE F : Production (21 fichiers)

### FICHIER F1 : `backend/Dockerfile`

**Description** : Dockerfile multi-stage pour le backend.

**Specifications** :
- Stage 1 : Builder (python:3.11-slim)
- Stage 2 : Runtime (python:3.11-slim)
- Non-root user
- Dependances seules en cache
- Health check
- Variables d'environnement
- Gunicorn + Uvicorn workers

**Code attendu** :
```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini .

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with Gunicorn + Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "app.main:app"]
```

---

### FICHIER F2 : `frontend/Dockerfile`

**Description** : Dockerfile multi-stage pour le frontend.

**Specifications** :
- Stage 1 : Build (node:20)
- Stage 2 : Serveur (nginx:alpine)
- Build optimise
- Nginx avec compression
- Cache headers
- Security headers
- Non-root (si possible)

**Code attendu** :
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Add security and compression
RUN echo "gzip on;" >> /etc/nginx/conf.d/gzip.conf && \
    echo "gzip_vary on;" >> /etc/nginx/conf.d/gzip.conf && \
    echo "gzip_proxied any;" >> /etc/nginx/conf.d/gzip.conf && \
    echo "gzip_types text/plain text/css application/json application/javascript text/xml application/xml;" >> /etc/nginx/conf.d/gzip.conf

# Create non-root user for nginx
RUN adduser -D -H -u 1000 -s /sbin/nologin nginx-user && \
    chown -R nginx-user:nginx-user /usr/share/nginx/html && \
    chown -R nginx-user:nginx-user /var/cache/nginx

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

---

### FICHIER F3 : `infrastructure/docker/docker-compose.prod.yml`

**Description** : Docker Compose pour l'environnement de production.

**Specifications** :
- Backend (2 replicas)
- Frontend
- PostgreSQL (persistant)
- Redis (persistant)
- Nginx (reverse proxy)
- Certbot
- Prometheus
- Grafana
- Reseaux separes
- Secrets Docker
- Health checks
- Restart policies
- Limits ressources

**Code attendu** :
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ../../backend
      dockerfile: Dockerfile
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - AUDIT_SECRET_KEY=${AUDIT_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    networks:
      - backend
      - frontend
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build:
      context: ../../frontend
      dockerfile: Dockerfile
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 128M
    networks:
      - frontend
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/snippets:/etc/nginx/snippets:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - backend
      - frontend
    networks:
      - frontend
    restart: unless-stopped

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h; done'"
    networks:
      - frontend

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - backend
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  backend:
    internal: true
  frontend:
```

---

### FICHIER F4 : `infrastructure/docker/docker-compose.dev.yml`

**Description** : Docker Compose pour l'environnement de developpement.

**Specifications** :
- Hot reload backend
- Hot reload frontend
- PostgreSQL avec volume
- Redis
- Mailpit pour emails
- Volumes montes
- Pas de SSL
- Debug active

**Code attendu** :
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ../../backend
      dockerfile: Dockerfile.dev
    volumes:
      - ../../backend:/app
      - /app/__pycache__
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ao_user:ao_pass@postgres:5432/ao_platform_dev
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=true
      - SECRET_KEY=dev-secret-key-change-in-production
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ../../frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ../../frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=ao_user
      - POSTGRES_PASSWORD=ao_pass
      - POSTGRES_DB=ao_platform_dev
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mailpit:
    image: axllent/mailpit
    ports:
      - "1025:1025"
      - "8025:8025"

volumes:
  postgres_dev_data:
```

---

### FICHIER F5 : `infrastructure/docker/docker-compose.test.yml`

**Description** : Docker Compose pour les tests.

**Specifications** :
- Backend avec env test
- PostgreSQL test
- Redis test
- Mailpit
- Execution tests automatique
- Cleanup apres tests

---

### FICHIER F6 : `infrastructure/nginx/nginx.conf`

**Description** : Configuration Nginx production.

**Specifications** :
- Reverse proxy backend
- Servir frontend
- Compression gzip/brotli
- Cache statique
- Rate limiting
- SSL redirect
- WebSocket support
- Logs JSON
- Headers securite
- Health check endpoint

**Code attendu** :
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging format (JSON)
    log_format json_combined escape=json
        '{"timestamp":"$time_iso8601",'
        '"remote_addr":"$remote_addr",'
        '"request":"$request",'
        '"status":$status,'
        '"bytes_sent":$bytes_sent,'
        '"request_time":$request_time,'
        '"http_referrer":"$http_referer",'
        '"http_user_agent":"$http_user_agent",'
        '"http_x_forwarded_for":"$http_x_forwarded_for"}';
    
    access_log /var/log/nginx/access.log json_combined;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # Upstream backend
    upstream backend {
        least_conn;
        server backend:8000 max_fails=3 fail_timeout=30s;
    }
    
    # Upstream frontend
    upstream frontend {
        server frontend:80;
    }
    
    # HTTP -> HTTPS redirect
    server {
        listen 80;
        server_name _;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$host$request_uri;
        }
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name ao-platform.com www.ao-platform.com;
        
        # SSL
        ssl_certificate /etc/letsencrypt/live/ao-platform.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ao-platform.com/privkey.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.openai.com;" always;
        
        # Health check
        location /nginx-health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Request-ID $request_id;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # WebSocket
        location /ws/ {
            proxy_pass http://backend/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
        
        # Static files (frontend)
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                proxy_pass http://frontend;
                expires 1y;
                add_header Cache-Control "public, immutable";
                access_log off;
            }
        }
    }
}
```

---

### FICHIER F7 : `infrastructure/nginx/snippets/security-headers.conf`

**Description** : Snippet Nginx pour les headers de securite.

**Specifications** :
- HSTS
- CSP
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

**Code attendu** :
```nginx
# Strict-Transport-Security
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# Content-Security-Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.openai.com https://sentry.io; frame-ancestors 'self'; base-uri 'self'; form-action 'self';" always;

# X-Frame-Options
add_header X-Frame-Options "SAMEORIGIN" always;

# X-Content-Type-Options
add_header X-Content-Type-Options "nosniff" always;

# X-XSS-Protection
add_header X-XSS-Protection "1; mode=block" always;

# Referrer-Policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Permissions-Policy
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), interest-cohort=()" always;
```

---

### FICHIER F8 : `infrastructure/nginx/snippets/ssl-params.conf`

**Description** : Snippet Nginx pour les parametres SSL.

**Specifications** :
- TLS 1.2/1.3
- Ciphers forts
- Session cache
- OCSP stapling

**Code attendu** :
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
```

---

### FICHIER F9 : `infrastructure/nginx/snippets/rate-limit.conf`

**Description** : Snippet Nginx pour le rate limiting.

**Specifications** :
- Zones par IP
- Burst
- Nodelay
- Whitelist interne

**Code attendu** :
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
limit_req_zone $binary_remote_addr zone=llm:10m rate=2r/s;

limit_conn_zone $binary_remote_addr zone=conn:10m;

# Apply limits
limit_req zone=api burst=20 nodelay;
limit_conn conn 10;
```

---

### FICHIER F10 : `infrastructure/certbot/init-letsencrypt.sh`

**Description** : Script d'initialisation Let's Encrypt.

**Specifications** :
- Detection domaines
- Generation certificats
- Dry run option
- Nginx reload
- Error handling

**Code attendu** :
```bash
#!/bin/bash

set -e

if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker-compose is not installed.' >&2
  exit 1
fi

# Domains
DOMAINS=("ao-platform.com" "www.ao-platform.com")
EMAIL="admin@ao-platform.com"
STAGING=0 # Set to 1 for testing

# Create certbot directories
mkdir -p ./certbot/conf/live
mkdir -p ./certbot/www

# Download recommended TLS parameters
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > ./certbot/conf/options-ssl-nginx.conf
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > ./certbot/conf/ssl-dhparams.pem

echo "### Starting nginx for certbot challenge ..."
docker-compose -f docker-compose.prod.yml up -d nginx

echo "### Requesting Let's Encrypt certificates ..."

for domain in "${DOMAINS[@]}"; do
  echo "### Requesting certificate for $domain ..."
  
  # Select appropriate email arg
  case "$EMAIL" in
    "") email_arg="--register-unsafely-without-email" ;;
    *) email_arg="--email $EMAIL" ;;
  esac
  
  # Enable staging mode if needed
  if [ $STAGING != "0" ]; then
    staging_arg="--staging"
  fi
  
  docker-compose -f docker-compose.prod.yml run --rm --entrypoint " \
    certbot certonly --webroot -w /var/www/certbot \
      $staging_arg \
      $email_arg \
      -d $domain \
      --rsa-key-size 4096 \
      --agree-tos \
      --force-renewal \
      --non-interactive \
    " certbot
done

echo "### Reloading nginx ..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "### Done!"
```

---

### FICHIER F11 : `infrastructure/certbot/renew-ssl.sh`

**Description** : Script de renouvellement SSL.

**Specifications** :
- Renouvellement automatique
- Nginx reload
- Log
- Cron compatible

**Code attendu** :
```bash
#!/bin/bash

set -e

COMPOSE_FILE="/opt/ao-platform/infrastructure/docker/docker-compose.prod.yml"
LOG_FILE="/var/log/certbot-renew.log"

exec >> "$LOG_FILE" 2>&1

echo "[$(date)] Starting SSL renewal..."

docker-compose -f "$COMPOSE_FILE" run --rm certbot renew --quiet

echo "[$(date)] Reloading nginx..."
docker-compose -f "$COMPOSE_FILE" exec nginx nginx -s reload

echo "[$(date)] SSL renewal completed."
```

---

### FICHIER F12 : `infrastructure/monitoring/prometheus.yml`

**Description** : Configuration Prometheus.

**Specifications** :
- Scraping backend
- Scraping nginx
- Alert rules
- Retention

**Code attendu** :
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

---

### FICHIER F13 : `infrastructure/monitoring/alertmanager.yml`

**Description** : Configuration Alertmanager.

**Specifications** :
- Email notifications
- Grouping
- Inhibition
- Routing

**Code attendu** :
```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@ao-platform.com'
  smtp_auth_username: 'alerts@ao-platform.com'
  smtp_auth_password: '${SMTP_PASSWORD}'

templates:
  - '/etc/alertmanager/templates/*.tmpl'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'team-emails'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true
    - match:
        severity: warning
      receiver: 'team-emails'

receivers:
  - name: 'team-emails'
    email_configs:
      - to: 'team@ao-platform.com'
        subject: 'AO Platform Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_KEY}'
        description: '{{ .GroupLabels.alertname }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname']
```

---

### FICHIER F14 : `infrastructure/monitoring/grafana-dashboards/dashboard.json`

**Description** : Dashboard Grafana.

**Specifications** :
- Panels : requetes/seconde, latence, erreurs, CPU, memoire, DB connections
- Temps reel
- Alertes visuelles
- Drill-down

---

### FICHIER F15 : `.github/workflows/ci.yml`

**Description** : Workflow CI build + test.

**Specifications** :
- Trigger : push, PR
- Jobs : lint, test-backend, test-frontend, test-accessibility, build-docker, scan-security
- Matrix OS
- Cache
- Artifacts

**Code attendu** :
```yaml
name: CI

"on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install Python dependencies
        run: |
          cd backend
          pip install ruff black isort
          ruff check .
          black --check .
          isort --check-only .
      
      - name: Install Node dependencies
        run: |
          cd frontend
          npm ci
          npm run lint

  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          fail_ci_if_error: true

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run unit tests
        run: |
          cd frontend
          npm run test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/lcov.info
          fail_ci_if_error: true

  test-accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build application
        run: |
          cd frontend
          npm run build
      
      - name: Run axe-core tests
        run: |
          cd frontend
          npm run test:accessibility
      
      - name: Generate accessibility report
        if: always()
        run: |
          cd frontend
          npm run accessibility:report
      
      - name: Upload accessibility report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: accessibility-report
          path: frontend/accessibility-report.html

  test-i18n:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Check i18n keys
        run: |
          cd frontend
          npm run i18n:check

  build-docker:
    runs-on: ubuntu-latest
    needs: [lint, test-backend, test-frontend]
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
            ghcr.io/${{ github.repository }}/backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
            ghcr.io/${{ github.repository }}/frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  security-scan:
    runs-on: ubuntu-latest
    needs: [build-docker]
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'ghcr.io/${{ github.repository }}/backend:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

### FICHIER F16 : `.github/workflows/cd.yml`

**Description** : Workflow CD deploy.

**Specifications** :
- Trigger : tag v* ou main
- Blue-green deployment
- SSH deploy
- Health check post-deploy
- Rollback
- Notification Slack

**Code attendu** :
```yaml
name: CD

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/ao-platform
            git fetch origin
            git checkout ${{ github.ref_name }}
            
            # Blue-green deployment
            docker-compose -f infrastructure/docker/docker-compose.prod.yml pull
            docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d --no-deps --scale backend=3 backend
            
            # Health check
            sleep 10
            curl -f http://localhost:8000/health || exit 1
            
            # Scale down old
            docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d --scale backend=2 backend
            
            # Cleanup
            docker system prune -f
      
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment ${{ job.status }} for ${{ github.ref_name }}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

### FICHIER F17 : `.github/workflows/security-scan.yml`

**Description** : Workflow scan securite quotidien.

**Specifications** :
- Trigger : cron quotidien
- Scan dependances Python (safety, bandit)
- Scan dependances Node (npm audit)
- Trivy scan
- Rapport issue GitHub

**Code attendu** :
```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  workflow_dispatch:

jobs:
  scan-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install safety
        run: pip install safety
      
      - name: Run safety check
        run: |
          cd backend
          safety check -r requirements.txt --full-report || true
      
      - name: Install bandit
        run: pip install bandit[toml]
      
      - name: Run bandit
        run: |
          cd backend
          bandit -r app/ -f json -o bandit-report.json || true

  scan-node:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Run npm audit
        run: |
          cd frontend
          npm audit --audit-level=moderate || true
```

---

### FICHIER F18 : `.github/workflows/accessibility-check.yml`

**Description** : Workflow tests accessibilite.

**Specifications** :
- Trigger : PR
- Build app
- axe-core tests
- Rapport HTML
- Upload artifact
- Fail si violations

**Code attendu** :
```yaml
name: Accessibility Check

on:
  pull_request:
    branches: [main]

jobs:
  axe-core:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build application
        run: |
          cd frontend
          npm run build
      
      - name: Start application
        run: |
          cd frontend
          npx serve dist -l 3000 &
          sleep 5
      
      - name: Run axe-core
        run: |
          cd frontend
          npx axe http://localhost:3000 --exit --tags wcag2a,wcag2aa
      
      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: accessibility-violations
          path: frontend/axe-results.json
```

---

### FICHIER F19 : `scripts/health-check.sh`

**Description** : Script de health check.

**Specifications** :
- Check backend (/health)
- Check database (pg_isready)
- Check Redis (redis-cli ping)
- Check Nginx (curl)
- Exit code approprie
- JSON output option

**Code attendu** :
```bash
#!/bin/bash

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
NGINX_URL="${NGINX_URL:-http://localhost}"

JSON_OUTPUT=0
if [ "$1" = "--json" ]; then
    JSON_OUTPUT=1
fi

checks_passed=0
checks_failed=0
results=()

run_check() {
    local name="$1"
    local command="$2"
    
    if eval "$command" > /dev/null 2>&1; then
        checks_passed=$((checks_passed + 1))
        results+=("{\"name\":\"$name\",\"status\":\"pass\"}")
        if [ $JSON_OUTPUT -eq 0 ]; then
            echo "[PASS] $name"
        fi
    else
        checks_failed=$((checks_failed + 1))
        results+=("{\"name\":\"$name\",\"status\":\"fail\"}")
        if [ $JSON_OUTPUT -eq 0 ]; then
            echo "[FAIL] $name"
        fi
    fi
}

run_check "Backend API" "curl -f -s $BACKEND_URL/health"
run_check "Database" "pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER"
run_check "Redis" "redis-cli -h $REDIS_HOST -p $REDIS_PORT ping | grep -q PONG"
run_check "Nginx" "curl -f -s $NGINX_URL/nginx-health"

if [ $JSON_OUTPUT -eq 1 ]; then
    echo "{"
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"overall\": \"$([ $checks_failed -eq 0 ] && echo 'healthy' || echo 'unhealthy')\","
    echo "  \"passed\": $checks_passed,"
    echo "  \"failed\": $checks_failed,"
    echo "  \"checks\": ["
    printf '%s\n' "${results[@]}" | sed '$!s/$/,/'
    echo "  ]"
    echo "}"
fi

if [ $checks_failed -gt 0 ]; then
    exit 1
fi

exit 0
```

---

### FICHIER F20 : `scripts/backup-db.sh`

**Description** : Script de backup base de donnees.

**Specifications** :
- pg_dump avec compression
- Date dans le nom
- Retention (7 jours)
- Upload S3 optionnel
- Chiffrement
- Log

**Code attendu** :
```bash
#!/bin/bash

set -e

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-ao_platform}"
DB_USER="${DB_USER:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/ao-platform}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
S3_BUCKET="${S3_BUCKET:-}"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${DB_NAME}_${TIMESTAMP}.sql.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Perform backup
echo "[$(date)] Starting backup of $DB_NAME..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --no-owner --no-acl --clean --if-exists | \
    gzip > "$BACKUP_FILE"

# Encrypt if key provided
if [ -n "$ENCRYPTION_KEY" ]; then
    ENCRYPTED_FILE="${BACKUP_FILE}.enc"
    openssl enc -aes-256-cbc -salt -in "$BACKUP_FILE" -out "$ENCRYPTED_FILE" -k "$ENCRYPTION_KEY"
    rm "$BACKUP_FILE"
    BACKUP_FILE="$ENCRYPTED_FILE"
fi

# Upload to S3 if configured
if [ -n "$S3_BUCKET" ]; then
    aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/backups/$(basename $BACKUP_FILE)"
    echo "[$(date)] Backup uploaded to S3"
fi

# Clean old backups
find "$BACKUP_DIR" -name "backup_${DB_NAME}_*.sql.gz*" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup completed: $BACKUP_FILE"
```

---

### FICHIER F21 : `Makefile`

**Description** : Commandes Make pour le projet.

**Specifications** :
- dev : lancer dev
- test : lancer tests
- build : build Docker
- deploy : deploy
- lint : linter
- format : formater
- migrate : migrations
- seed : donnees test
- clean : cleanup
- help : aide

**Code attendu** :
```makefile
.PHONY: help dev test build deploy lint format migrate seed clean i18n-extract i18n-compile

help: ## Show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development environment
	docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d
	@echo "Development environment started:"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Mailpit:  http://localhost:8025"
	@echo "  Postgres: localhost:5432"
	@echo "  Redis:    localhost:6379"

dev-down: ## Stop development environment
	docker-compose -f infrastructure/docker/docker-compose.dev.yml down

dev-logs: ## View development logs
	docker-compose -f infrastructure/docker/docker-compose.dev.yml logs -f

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && pytest -xvs

test-frontend: ## Run frontend tests
	cd frontend && npm run test

test-e2e: ## Run E2E tests
	cd frontend && npx playwright test

test-accessibility: ## Run accessibility tests
	cd frontend && npm run test:accessibility

test-load: ## Run load tests
	cd frontend/tests/load && k6 run k6-auth.js

build: ## Build Docker images
	docker-compose -f infrastructure/docker/docker-compose.prod.yml build

build-push: ## Build and push Docker images
	docker-compose -f infrastructure/docker/docker-compose.prod.yml build
	docker-compose -f infrastructure/docker/docker-compose.prod.yml push

deploy: ## Deploy to production
	./infrastructure/scripts/deploy.sh

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend code
	cd backend && ruff check .
	cd backend && black --check .
	cd backend && isort --check-only .

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

format: format-backend format-frontend ## Format all code

format-backend: ## Format backend code
	cd backend && black .
	cd backend && isort .

format-frontend: ## Format frontend code
	cd frontend && npm run format

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-down: ## Rollback last migration
	cd backend && alembic downgrade -1

seed: ## Seed database with test data
	cd backend && python -m scripts.seed

clean: ## Clean up Docker and build artifacts
	docker system prune -f
	docker volume prune -f
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true

i18n-extract: ## Extract i18n strings
	cd backend && pybabel extract -o app/locales/messages.pot app/
	cd frontend && npx i18next-scanner

i18n-compile: ## Compile i18n translations
	cd backend && pybabel compile -d app/locales

i18n-init: ## Initialize new locale
	@echo "Usage: make i18n-init LANG=nl"
	cd backend && pybabel init -i app/locales/messages.pot -d app/locales -l $(LANG)

health: ## Check health of all services
	./scripts/health-check.sh

backup: ## Backup database
	./scripts/backup-db.sh

logs: ## View production logs
	docker-compose -f infrastructure/docker/docker-compose.prod.yml logs -f

ps: ## List running containers
	docker-compose -f infrastructure/docker/docker-compose.prod.yml ps
```

---

## GROUPE G : Alertes (12 fichiers)

### FICHIER G1 : `backend/app/alerts/models.py`

**Description** : Models pour le systeme d'alertes.

**Specifications** :
- AlertConfig : configuration par utilisateur et type
- AlertNotification : notification envoyee
- AlertTemplate : template d'alerte
- Indexes sur user_id, type, status

**Code attendu** :
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class AlertType(str, enum.Enum):
    AO_NEW = "ao_new"
    AO_DEADLINE = "ao_deadline"
    AO_MODIFIED = "ao_modified"
    SUBMISSION_NEW = "submission_new"
    SUBMISSION_STATUS = "submission_status"
    VALIDATION_REQUIRED = "validation_required"
    VALIDATION_URGENT = "validation_urgent"
    SYSTEM_ERROR = "system_error"
    SYSTEM_PERFORMANCE = "system_performance"
    AI_CONTESTATION = "ai_contestation"
    AI_REVIEW = "ai_review"

class AlertChannel(str, enum.Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    NONE = "none"

class AlertFrequency(str, enum.Enum):
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"

class AlertConfig(Base):
    __tablename__ = 'alert_configs'
    __table_args__ = (
        Index('idx_alert_config_user', 'user_id'),
        {'schema': 'alerts'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    channel = Column(Enum(AlertChannel), default=AlertChannel.EMAIL)
    frequency = Column(Enum(AlertFrequency), default=AlertFrequency.IMMEDIATE)
    enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(Integer, nullable=True)  # Hour 0-23
    quiet_hours_end = Column(Integer, nullable=True)
    custom_threshold = Column(JSON, nullable=True)  # Per-alert custom settings
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AlertNotification(Base):
    __tablename__ = 'alert_notifications'
    __table_args__ = (
        Index('idx_alert_notif_user', 'user_id'),
        Index('idx_alert_notif_type', 'alert_type'),
        Index('idx_alert_notif_status', 'status'),
        {'schema': 'alerts'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(Enum(AlertChannel), nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, failed, read
    metadata = Column(JSON, default=dict)
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class AlertTemplate(Base):
    __tablename__ = 'alert_templates'
    __table_args__ = {'schema': 'alerts'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(Enum(AlertType), nullable=False, unique=True)
    subject_template = Column(String(255), nullable=False)
    body_template = Column(Text, nullable=False)
    sms_template = Column(String(160), nullable=True)
    push_template = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

### FICHIER G2 : `backend/app/alerts/service.py`

**Description** : Service pour le systeme d'alertes.

**Specifications** :
- CreateAlert : creer alerte
- ProcessAlerts : traiter file d'attente
- SendNotification : envoyer par canal
- GetUserAlerts : recuperer alertes utilisateur
- MarkAsRead : marquer comme lu
- GetAlertSettings : parametres utilisateur
- UpdateAlertSettings : mise a jour parametres

**Code attendu** :
```python
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from .models import AlertConfig, AlertNotification, AlertTemplate, AlertType, AlertChannel, AlertFrequency
from .repository import AlertRepository
from .templates import render_alert
from app.core.email import send_email
from app.tasks.celery_app import celery_app

class AlertService:
    def __init__(self, db):
        self.db = db
        self.repo = AlertRepository(db)
    
    def create_alert(
        self,
        alert_type: AlertType,
        title: str,
        message: str,
        metadata: Optional[Dict] = None,
        target_user_id: Optional[UUID] = None,
    ) -> List[AlertNotification]:
        notifications = []
        
        if target_user_id:
            configs = self.repo.get_configs_for_user(target_user_id, alert_type)
        else:
            configs = self.repo.get_configs_for_alert_type(alert_type)
        
        for config in configs:
            if not config.enabled:
                continue
            
            if self._is_quiet_hours(config):
                continue
            
            notification = AlertNotification(
                user_id=config.user_id,
                alert_type=alert_type,
                title=title,
                message=message,
                channel=config.channel,
                metadata=metadata or {},
            )
            
            saved = self.repo.save_notification(notification)
            notifications.append(saved)
            
            # Send immediately or queue
            if config.frequency == AlertFrequency.IMMEDIATE:
                self._send_notification(saved)
            else:
                self._queue_notification(saved, config.frequency)
        
        return notifications
    
    def get_user_alerts(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[AlertNotification]:
        return self.repo.get_notifications_for_user(user_id, unread_only, limit)
    
    def mark_as_read(self, notification_id: UUID, user_id: UUID) -> AlertNotification:
        notification = self.repo.get_notification(notification_id)
        if notification.user_id != user_id:
            raise PermissionError("Cannot mark another user's notification as read")
        
        notification.status = "read"
        notification.read_at = datetime.utcnow()
        self.db.commit()
        return notification
    
    def mark_all_as_read(self, user_id: UUID) -> int:
        return self.repo.mark_all_read_for_user(user_id)
    
    def get_alert_settings(self, user_id: UUID) -> List[AlertConfig]:
        return self.repo.get_all_configs_for_user(user_id)
    
    def update_alert_settings(
        self,
        user_id: UUID,
        alert_type: AlertType,
        channel: AlertChannel,
        frequency: AlertFrequency,
        enabled: bool,
        quiet_hours_start: Optional[int] = None,
        quiet_hours_end: Optional[int] = None,
    ) -> AlertConfig:
        config = self.repo.get_or_create_config(user_id, alert_type)
        config.channel = channel
        config.frequency = frequency
        config.enabled = enabled
        config.quiet_hours_start = quiet_hours_start
        config.quiet_hours_end = quiet_hours_end
        
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def _is_quiet_hours(self, config: AlertConfig) -> bool:
        if config.quiet_hours_start is None or config.quiet_hours_end is None:
            return False
        
        now = datetime.utcnow().hour
        if config.quiet_hours_start <= config.quiet_hours_end:
            return config.quiet_hours_start <= now < config.quiet_hours_end
        else:
            return now >= config.quiet_hours_start or now < config.quiet_hours_end
    
    def _send_notification(self, notification: AlertNotification):
        if notification.channel == AlertChannel.EMAIL:
            self._send_email(notification)
        elif notification.channel == AlertChannel.IN_APP:
            # In-app is just storing in DB
            pass
        elif notification.channel == AlertChannel.WEBHOOK:
            self._send_webhook(notification)
        
        notification.status = "sent"
        notification.sent_at = datetime.utcnow()
        self.db.commit()
    
    def _send_email(self, notification: AlertNotification):
        template = self.repo.get_template(notification.alert_type)
        if not template:
            return
        
        subject = render_alert(template.subject_template, notification.metadata)
        body = render_alert(template.body_template, notification.metadata)
        
        send_email.delay(
            to_email=self._get_user_email(notification.user_id),
            subject=subject,
            body=body,
        )
    
    def _send_webhook(self, notification: AlertNotification):
        # Implement webhook delivery
        pass
    
    def _queue_notification(self, notification: AlertNotification, frequency: AlertFrequency):
        if frequency == AlertFrequency.DAILY:
            schedule_at = datetime.utcnow().replace(hour=9, minute=0, second=0)
            if schedule_at < datetime.utcnow():
                schedule_at += timedelta(days=1)
        elif frequency == AlertFrequency.WEEKLY:
            schedule_at = datetime.utcnow() + timedelta(days=7 - datetime.utcnow().weekday())
            schedule_at = schedule_at.replace(hour=9, minute=0, second=0)
        
        # Schedule Celery task
        send_delayed_notification.apply_async(
            args=[str(notification.id)],
            eta=schedule_at,
        )
    
    def _get_user_email(self, user_id: UUID) -> str:
        from app.models.user import User
        user = self.db.query(User).get(user_id)
        return user.email if user else ""


@celery_app.task
def send_delayed_notification(notification_id: str):
    # Implementation for delayed notification
    pass
```

---

### FICHIER G3 : `backend/app/alerts/repository.py`

**Description** : Repository pour les alertes.

**Specifications** :
- CRUD AlertConfig
- CRUD AlertNotification
- Get par user, type, status
- Pagination
- Jointures user

---

### FICHIER G4 : `backend/app/alerts/cron.py`

**Description** : Jobs cron pour les alertes.

**Specifications** :
- Check AO deadlines (J-7, J-3, J-1)
- Check validations pending
- Check system health
- Check AI contestations
- APScheduler
- Resilience (retry)

**Code attendu** :
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .service import AlertService
from .models import AlertType
from app.models.ao import AO
from app.models.submission import Submission

class AlertCronJobs:
    def __init__(self, db: Session):
        self.db = db
        self.alert_service = AlertService(db)
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        # AO deadline alerts - daily at 9 AM
        self.scheduler.add_job(
            self.check_ao_deadlines,
            CronTrigger(hour=9, minute=0),
            id='ao_deadlines',
            replace_existing=True,
        )
        
        # Validation pending - daily at 9 AM
        self.scheduler.add_job(
            self.check_pending_validations,
            CronTrigger(hour=9, minute=0),
            id='pending_validations',
            replace_existing=True,
        )
        
        # System health - every 5 minutes
        self.scheduler.add_job(
            self.check_system_health,
            'interval',
            minutes=5,
            id='system_health',
            replace_existing=True,
        )
        
        # AI contestation review - daily at 9 AM
        self.scheduler.add_job(
            self.check_ai_contestations,
            CronTrigger(hour=9, minute=0),
            id='ai_contestations',
            replace_existing=True,
        )
        
        self.scheduler.start()
    
    def check_ao_deadlines(self):
        now = datetime.utcnow()
        deadlines = [7, 3, 1]
        
        for days in deadlines:
            target_date = now + timedelta(days=days)
            aos = self.db.query(AO).filter(
                AO.deadline_date >= target_date.replace(hour=0, minute=0),
                AO.deadline_date < target_date.replace(hour=23, minute=59),
                AO.status == 'published',
            ).all()
            
            for ao in aos:
                self.alert_service.create_alert(
                    alert_type=AlertType.AO_DEADLINE,
                    title=f"Deadline approche : {ao.title}",
                    message=f"L'AO \"{ao.title}\" se termine dans {days} jours.",
                    metadata={"ao_id": str(ao.id), "days_remaining": days, "title": ao.title},
                    target_user_id=ao.created_by,
                )
    
    def check_pending_validations(self):
        now = datetime.utcnow()
        
        # Submissions pending validation for > 3 days
        pending = self.db.query(Submission).filter(
            Submission.status == 'pending_validation',
            Submission.submitted_at < now - timedelta(days=3),
        ).all()
        
        for submission in pending:
            days_pending = (now - submission.submitted_at).days
            self.alert_service.create_alert(
                alert_type=AlertType.VALIDATION_URGENT,
                title=f"Validation urgente requise",
                message=f"La soumission #{submission.id} attend validation depuis {days_pending} jours.",
                metadata={"submission_id": str(submission.id), "days_pending": days_pending},
            )
    
    def check_system_health(self):
        # Check system metrics
        # This would integrate with monitoring
        pass
    
    def check_ai_contestations(self):
        from app.ai_act.models import AIContestation, ContestationStatus
        
        now = datetime.utcnow()
        
        # Contestations approaching SLA (25 days)
        approaching_sla = self.db.query(AIContestation).filter(
            AIContestation.status == ContestationStatus.PENDING,
            AIContestation.created_at < now - timedelta(days=25),
        ).all()
        
        for contestation in approaching_sla:
            self.alert_service.create_alert(
                alert_type=AlertType.AI_REVIEW,
                title="Contestation IA proche du SLA",
                message=f"La contestation #{contestation.id} approche de la limite des 30 jours.",
                metadata={"contestation_id": str(contestation.id)},
            )
    
    def shutdown(self):
        self.scheduler.shutdown()
```

---

### FICHIER G5 : `backend/app/alerts/templates.py`

**Description** : Templates d'alertes.

**Specifications** :
- Fonction render_alert
- Variables substitution
- i18n support
- Fallback

**Code attendu** :
```python
from string import Template
from typing import Dict, Any

def render_alert(template: str, metadata: Dict[str, Any]) -> str:
    """Render alert template with metadata variables."""
    try:
        t = Template(template)
        return t.safe_substitute(metadata)
    except Exception:
        return template

# Default templates
DEFAULT_TEMPLATES = {
    AlertType.AO_NEW: {
        "subject": "Nouvel appel d'offres : $title",
        "body": "Un nouvel appel d'offres \"$title\" a ete publie. Consultez-le sur la plateforme.",
    },
    AlertType.AO_DEADLINE: {
        "subject": "Deadline approche : $title ($days_remaining jours)",
        "body": "L'appel d'offres \"$title\" se termine dans $days_remaining jours. Soumettez votre candidature avant la deadline.",
    },
    AlertType.SUBMISSION_NEW: {
        "subject": "Nouvelle soumission pour $ao_title",
        "body": "Une nouvelle soumission a ete deposee pour l'AO \"$ao_title\".",
    },
    AlertType.VALIDATION_REQUIRED: {
        "subject": "Validation requise : Soumission #$submission_id",
        "body": "Une soumission attend votre validation. Veuillez la consulter sur la plateforme.",
    },
    AlertType.VALIDATION_URGENT: {
        "subject": "URGENT : Validation en attente depuis $days_pending jours",
        "body": "La soumission #$submission_id attend validation depuis $days_pending jours. Veuillez traiter cette demande rapidement.",
    },
    AlertType.AI_CONTESTATION: {
        "subject": "Nouvelle contestation IA",
        "body": "Une contestation a ete soumise contre une decision IA. Veuillez examiner la demande.",
    },
}
```

---

### FICHIER G6 : `backend/app/api/routes/alerts.py`

**Description** : Routes API pour les alertes.

**Specifications** :
- GET /alerts : liste alertes utilisateur
- PUT /alerts/{id}/read : marquer comme lu
- PUT /alerts/read-all : tout marquer comme lu
- GET /alerts/settings : parametres
- PUT /alerts/settings : mise a jour parametres
- GET /alerts/unread-count : compteur

**Code attendu** :
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.alerts.service import AlertService
from app.alerts.models import AlertType, AlertChannel, AlertFrequency
from app.models.user import User

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/")
async def list_alerts(
    unread_only: bool = False,
    limit: int = 50,
    service: AlertService = Depends(),
    current_user: User = Depends(get_current_user),
):
    alerts = service.get_user_alerts(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )
    return {
        "items": [
            {
                "id": str(a.id),
                "type": a.alert_type.value,
                "title": a.title,
                "message": a.message,
                "status": a.status,
                "created_at": a.created_at.isoformat(),
                "read_at": a.read_at.isoformat() if a.read_at else None,
            }
            for a in alerts
        ],
        "total": len(alerts),
    }

@router.get("/unread-count")
async def get_unread_count(
    service: AlertService = Depends(),
    current_user: User = Depends(get_current_user),
):
    count = service.repo.count_unread_for_user(current_user.id)
    return {"count": count}

@router.put("/{alert_id}/read")
async def mark_read(
    alert_id: UUID,
    service: AlertService = Depends(),
    current_user: User = Depends(get_current_user),
):
    notification = service.mark_as_read(alert_id, current_user.id)
    return {"id": str(notification.id), "status": notification.status}

@router.put("/read-all")
async def mark_all_read(
    service: AlertService = Depends(),
    current_user: User = Depends(get_current_user),
):
    count = service.mark_all_as_read(current_user.id)
    return {"marked_read": count}

@router.get("/settings")
async def get_settings(
    service: AlertService = Depends(),
    current_user: User = Depends(get_current_user),
):
    configs = service.get_alert_settings(current_user.id)
    return {
        "settings": [
            {
                "alert_type": c.alert_type.value,
                "channel": c.channel.value,
                "frequency": c.frequency.value,
                "enabled": c.enabled,
                "quiet_hours_start": c.quiet_hours_start,
                "quiet_hours_end": c.quiet_hours_end,
            }
            for c in configs
        ],
    }

@router.put("/settings")
async def update_settings(
    alert_type: AlertType,
    channel: AlertChannel,
    frequency: AlertFrequency,
    enabled: bool,
    quiet_hours_start: Optional[int] = None,
    quiet_hours_end: Optional[int] = None,
    service: AlertService = Depends(),
    current_user: User = Depends(get_current_user),
):
    config = service.update_alert_settings(
        user_id=current_user.id,
        alert_type=alert_type,
        channel=channel,
        frequency=frequency,
        enabled=enabled,
        quiet_hours_start=quiet_hours_start,
        quiet_hours_end=quiet_hours_end,
    )
    return {
        "alert_type": config.alert_type.value,
        "channel": config.channel.value,
        "frequency": config.frequency.value,
        "enabled": config.enabled,
    }
```

---

### FICHIER G7 : `backend/app/tasks/alert_tasks.py`

**Description** : Taches Celery pour les alertes.

**Specifications** :
- send_email_task
- send_webhook_task
- process_digest_task (daily/weekly)
- cleanup_old_alerts_task

**Code attendu** :
```python
from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.alerts.service import AlertService
from app.core.email import EmailService

@shared_task(bind=True, max_retries=3)
def send_email_task(self, notification_id: str):
    try:
        db = SessionLocal()
        service = AlertService(db)
        
        from app.alerts.models import AlertNotification
        notification = db.query(AlertNotification).get(notification_id)
        if not notification:
            return
        
        email_service = EmailService()
        email_service.send(
            to=service._get_user_email(notification.user_id),
            subject=notification.title,
            body=notification.message,
        )
        
        notification.status = "sent"
        notification.sent_at = datetime.utcnow()
        db.commit()
        
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
    finally:
        db.close()

@shared_task
def process_daily_digest():
    db = SessionLocal()
    try:
        service = AlertService(db)
        # Get all notifications pending daily digest
        # Group by user and send
        ...
    finally:
        db.close()

@shared_task
def cleanup_old_alerts():
    db = SessionLocal()
    try:
        # Delete alerts older than 90 days
        cutoff = datetime.utcnow() - timedelta(days=90)
        from app.alerts.models import AlertNotification
        db.query(AlertNotification).filter(
            AlertNotification.created_at < cutoff,
            AlertNotification.status.in_(["sent", "read"]),
        ).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()
```

---

### FICHIER G8 : `frontend/src/pages/AlertsDashboard.tsx`

**Description** : Page dashboard des alertes.

**Specifications** :
- Liste des alertes avec filtres
- Compteur non lus
- Marquer comme lu
- Parametres des alertes
- Pagination
- Temps relatif

---

### FICHIER G9 : `frontend/src/components/alerts/AlertBadge.tsx`

**Description** : Badge de compteur d'alertes.

**Specifications** :
- Affichage nombre non lus
- Animation pulse si > 0
- Click pour ouvrir centre notification
- Aria-label
- Responsive

**Code attendu** :
```tsx
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';

interface AlertBadgeProps {
  onClick: () => void;
}

export const AlertBadge: React.FC<AlertBadgeProps> = ({ onClick }) => {
  const { t } = useTranslation('common');
  
  const { data } = useQuery({
    queryKey: ['unread-alerts-count'],
    queryFn: async () => {
      const response = await fetch('/api/alerts/unread-count');
      return response.json();
    },
    refetchInterval: 30000, // Refetch every 30s
  });
  
  const count = data?.count || 0;
  
  return (
    <button
      onClick={onClick}
      className="relative p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary"
      aria-label={t('alerts.unread_count', { count })}
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0" stroke="currentColor" strokeWidth="2" />
      </svg>
      {count > 0 && (
        <span
          className="absolute top-0 right-0 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full"
          aria-hidden="true"
        >
          {count > 99 ? '99+' : count}
        </span>
      )}
    </button>
  );
};
```

---

### FICHIER G10 : `frontend/src/components/alerts/NotificationCenter.tsx`

**Description** : Centre de notification dropdown.

**Specifications** :
- Dropdown avec liste
- Marquer tout comme lu
- Filtrer par type
- Infini scroll
- Temps relatif
- Liens vers contenu

---

### FICHIER G11 : `frontend/src/components/alerts/AlertSettings.tsx`

**Description** : Parametres des alertes.

**Specifications** :
- Tableau alertes par type
- Canal selectionnable
- Frequence selectionnable
- Heures de silence
- Toggle actif/inactif
- Sauvegarde automatique

---

### FICHIER G12 : `frontend/src/services/alertsApi.ts`

**Description** : Client API pour les alertes.

**Specifications** :
- getAlerts(filters)
- markAsRead(id)
- markAllAsRead()
- getSettings()
- updateSettings(type, config)
- getUnreadCount()

---

## GROUPE H : Tests E2E complets (22 fichiers)

### FICHIER H1 : `frontend/tests/e2e/auth.spec.ts`

**Description** : Tests E2E authentification.

**Specifications** :
- Login success
- Login failure
- Logout
- Refresh token
- 2FA
- Password reset
- Session expiration

**Code attendu** :
```typescript
import { test, expect } from '@playwright/test';
import { authFixtures } from './fixtures/auth';

test.describe('Authentication', () => {
  test('user can login with valid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });
  
  test('user cannot login with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');
    
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });
  
  test('user can logout', async ({ page, authenticated }) => {
    await authenticated(page);
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    await expect(page).toHaveURL('/login');
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
  });
  
  test('session expires and redirects to login', async ({ page, authenticated }) => {
    await authenticated(page);
    // Simulate token expiration
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'expired');
    });
    await page.reload();
    
    await expect(page).toHaveURL('/login');
  });
});
```

---

### FICHIER H2 : `frontend/tests/e2e/ao.spec.ts`

**Description** : Tests E2E appels d'offres.

**Specifications** :
- Creation AO complet
- Liste AO
- Detail AO
- Modification AO (brouillon)
- Publication AO
- Fermeture AO
- Suppression AO

---

### FICHIER H3 : `frontend/tests/e2e/submission.spec.ts`

**Description** : Tests E2E soumission.

**Specifications** :
- Reponse AO
- Upload documents
- Confirmation
- Modification (avant deadline)
- Retrait

---

### FICHIER H4 : `frontend/tests/e2e/scoring.spec.ts`

**Description** : Tests E2E scoring.

**Specifications** :
- Declenchement scoring
- Attente resultat
- Affichage score
- Badge IA visible
- Explication XAI

---

### FICHIER H5 : `frontend/tests/e2e/validation.spec.ts`

**Description** : Tests E2E validation.

**Specifications** :
- Affectation validation
- Validation soumission
- Rejet soumission
- Notification
- Workflow complet

---

### FICHIER H6 : `frontend/tests/e2e/audit.spec.ts`

**Description** : Tests E2E audit.

**Specifications** :
- Navigation timeline
- Filtres
- Detail evenement
- Export PDF
- Verification signature

**Code attendu** :
```typescript
import { test, expect } from '@playwright/test';

test.describe('Audit Forensic', () => {
  test('user can view audit timeline for an AO', async ({ page, authenticated }) => {
    await authenticated(page);
    await page.goto('/audit/123e4567-e89b-12d3-a456-426614174000');
    
    await expect(page.locator('[data-testid="audit-timeline"]')).toBeVisible();
    await expect(page.locator('[data-testid="timeline-event"]')).toHaveCount.greaterThan(0);
  });
  
  test('user can filter audit events by layer', async ({ page, authenticated }) => {
    await authenticated(page);
    await page.goto('/audit/123e4567-e89b-12d3-a456-426614174000');
    
    await page.click('[data-testid="filter-llm"]');
    const events = page.locator('[data-testid="timeline-event"]');
    
    for (const event of await events.all()) {
      await expect(event.locator('[data-testid="layer-badge"]')).toHaveText('IA');
    }
  });
  
  test('user can export forensic report as PDF', async ({ page, authenticated }) => {
    await authenticated(page);
    await page.goto('/audit/123e4567-e89b-12d3-a456-426614174000');
    
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('[data-testid="export-pdf-button"]'),
    ]);
    
    expect(download.suggestedFilename()).toMatch(/audit-forensic.*\.pdf/);
  });
});
```

---

### FICHIER H7 : `frontend/tests/e2e/contest.spec.ts`

**Description** : Tests E2E contestation IA.

**Specifications** :
- Clic bouton contester
- Formulaire raison
- Soumission
- Suivi statut
- Notification

---

### FICHIER H8 : `frontend/tests/e2e/i18n.spec.ts`

**Description** : Tests E2E internationalisation.

**Specifications** :
- Changement langue FR -> NL -> EN -> AR
- Verification textes traduits
- Verification RTL
- Verification dates formattees
- Fallback FR

**Code attendu** :
```typescript
import { test, expect } from '@playwright/test';

test.describe('Internationalization', () => {
  test('user can switch language and see translated content', async ({ page }) => {
    await page.goto('/');
    
    // Switch to Dutch
    await page.click('[data-testid="language-switcher"]');
    await page.click('[data-testid="lang-nl"]');
    
    await expect(page.locator('[data-testid="nav-home"]')).toHaveText('Home');
    
    // Switch to English
    await page.click('[data-testid="language-switcher"]');
    await page.click('[data-testid="lang-en"]');
    
    await expect(page.locator('[data-testid="nav-home"]')).toHaveText('Home');
    
    // Switch to Arabic (RTL)
    await page.click('[data-testid="language-switcher"]');
    await page.click('[data-testid="lang-ar"]');
    
    // Check RTL direction
    const dir = await page.evaluate(() => document.documentElement.dir);
    expect(dir).toBe('rtl');
  });
  
  test('untranslated keys fall back to French', async ({ page }) => {
    // This would test with a mock locale that has missing keys
  });
});
```

---

### FICHIER H9 : `frontend/tests/e2e/accessibility.spec.ts`

**Description** : Tests E2E accessibilite.

**Specifications** :
- Navigation clavier page login
- Skip links
- Focus trap modal
- Aria labels
- Contraste
- Navigation Kanban

**Code attendu** :
```typescript
import { test, expect } from '@playwright/test';

test.describe('Accessibility', () => {
  test('skip links allow keyboard navigation to main content', async ({ page }) => {
    await page.goto('/');
    
    // Press Tab to focus skip link
    await page.keyboard.press('Tab');
    
    const skipLink = page.locator('a[href="#main-content"]');
    await expect(skipLink).toBeFocused();
    
    // Press Enter to activate
    await page.keyboard.press('Enter');
    
    const mainContent = page.locator('#main-content');
    await expect(mainContent).toBeFocused();
  });
  
  test('modal traps focus', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="open-modal-button"]');
    
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();
    
    // Tab multiple times should stay in modal
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
    }
    
    const focusedElement = await page.evaluate(() => document.activeElement?.closest('[role="dialog"]'));
    expect(focusedElement).not.toBeNull();
  });
  
  test('kanban is keyboard navigable', async ({ page }) => {
    await page.goto('/board');
    
    const firstCard = page.locator('[role="listitem"]').first();
    await firstCard.focus();
    
    // Arrow down to next card
    await page.keyboard.press('ArrowDown');
    const secondCard = page.locator('[role="listitem"]').nth(1);
    await expect(secondCard).toBeFocused();
  });
});
```

---

### FICHIER H10 : `frontend/tests/e2e/alerts.spec.ts`

**Description** : Tests E2E alertes.

**Specifications** :
- Configuration alertes
- Reception alerte
- Marquer comme lu
- Badge mise a jour

---

### FICHIER H11 : `frontend/tests/e2e/dashboard.spec.ts`

**Description** : Tests E2E dashboard.

**Specifications** :
- Chargement widgets
- Navigation
- Donnees a jour
- Responsive

---

### FICHIER H12 : `frontend/tests/e2e/profile.spec.ts`

**Description** : Tests E2E profil.

**Specifications** :
- Modification infos
- Changement mot de passe
- Preferences
- Alertes
- Export donnees

---

### FICHIER H13 : `frontend/tests/e2e/admin.spec.ts`

**Description** : Tests E2E administration.

**Specifications** :
- Liste utilisateurs
- Creation utilisateur
- Modification role
- Suppression utilisateur
- Permissions

---

### FICHIER H14 : `frontend/tests/e2e/export.spec.ts`

**Description** : Tests E2E export.

**Specifications** :
- Demande export RGPD
- Telechargement
- Formats
- Verification contenu

---

### FICHIER H15 : `frontend/tests/e2e/search.spec.ts`

**Description** : Tests E2E recherche.

**Specifications** :
- Recherche texte
- Filtres
- Pagination
- Tri
- Resultats pertinents

---

### FICHIER H16 : `frontend/tests/load/k6-auth.js`

**Description** : Tests de charge authentification.

**Specifications** :
- 100 req/s
- p95 < 200ms
- p99 < 500ms
- Error rate < 1%
- Duration 5 minutes

**Code attendu** :
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
    errors: ['rate<0.01'],
  },
};

export default function () {
  const payload = JSON.stringify({
    email: `test${__VU}@example.com`,
    password: 'password123',
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const response = http.post('https://api.ao-platform.com/api/auth/login', payload, params);
  
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  errorRate.add(!success);
  sleep(1);
}
```

---

### FICHIER H17 : `frontend/tests/load/k6-ao.js`

**Description** : Tests de charge liste AO.

**Specifications** :
- 50 req/s
- p95 < 300ms
- Pagination
- Filtres

---

### FICHIER H18 : `frontend/tests/load/k6-scoring.js`

**Description** : Tests de charge scoring.

**Specifications** :
- 10 req/s
- p95 < 5000ms
- Upload documents
- Attente resultat

---

### FICHIER H19 : `frontend/tests/security/sql-injection.test.js`

**Description** : Tests injection SQL.

**Specifications** :
- Payloads sur tous les parametres
- Verification non-exploitation
- ORM protection

**Code attendu** :
```javascript
const payloads = [
  "' OR '1'='1",
  "'; DROP TABLE users; --",
  "' UNION SELECT * FROM users --",
  "1 OR 1=1",
  "1; DELETE FROM users WHERE '1'='1",
];

async function testSQLInjection(endpoint, paramName) {
  for (const payload of payloads) {
    const params = new URLSearchParams();
    params.set(paramName, payload);
    
    const response = await fetch(`${endpoint}?${params}`);
    const body = await response.text();
    
    // Should not contain SQL error messages
    if (body.includes('SQL') || body.includes('syntax error')) {
      console.error(`SQL Injection possible at ${endpoint} with param ${paramName}`);
      process.exit(1);
    }
    
    // Should not return more data than expected
    // (implementation specific)
  }
}
```

---

### FICHIER H20 : `frontend/tests/security/xss.test.js`

**Description** : Tests XSS.

**Specifications** :
- Payloads sur tous les inputs
- Verification escape
- CSP verification

---

### FICHIER H21 : `frontend/tests/security/csrf.test.js`

**Description** : Tests CSRF.

**Specifications** :
- Requete sans token
- Requete avec token invalide
- Verification rejet

---

### FICHIER H22 : `frontend/tests/security/rate-limit.test.js`

**Description** : Tests rate limiting.

**Specifications** :
- Depassement limite login
- Verification 429
- Headers rate limit
- Reset apres fenetre

---

# SECTION 6 : DEPENDANCES ET INSTALLATION

## 6.1 Backend requirements.txt additions

```
# i18n
Babel==2.13.1
pycountry==22.3.5
python-dateutil==2.8.2

# Forensic audit
reportlab==4.0.7
WeasyPrint==60.2
cryptography==41.0.7

# Alerts
APScheduler==3.10.4

# Monitoring
prometheus-client==0.19.0
sentry-sdk==1.38.0

# Email
Jinja2==3.1.2

# Async
aiofiles==23.2.1
```

## 6.2 Frontend package.json additions

```json
{
  "dependencies": {
    "react-i18next": "^13.5.0",
    "i18next": "^23.7.0",
    "i18next-browser-languagedetector": "^7.2.0",
    "i18next-http-backend": "^2.4.0",
    "react-joyride": "^2.7.0",
    "@react-pdf/renderer": "^3.1.0",
    "jspdf": "^2.5.0",
    "html2canvas": "^1.4.1"
  },
  "devDependencies": {
    "@axe-core/react": "^4.8.0",
    "axe-core": "^4.8.0",
    "jest-axe": "^8.0.0",
    "@playwright/test": "^1.40.0"
  },
  "scripts": {
    "test:accessibility": "jest --testPathPattern=accessibility",
    "accessibility:report": "jest --testPathPattern=accessibility --reporters=default --reporters=jest-html-reporter",
    "i18n:check": "i18next-scanner",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

---

# SECTION 7 : MIGRATIONS BASE DE DONNEES

## 7.1 Migration traçabilite

```python
"""Create audit schema and tables

Revision ID: sprint3_audit
Revises: sprint2_llm
Create Date: 2024-01-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'sprint3_audit'
down_revision = 'sprint2_llm'


def upgrade():
    # Create schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")
    op.execute("CREATE SCHEMA IF NOT EXISTS llm")
    op.execute("CREATE SCHEMA IF NOT EXISTS ai_act")
    op.execute("CREATE SCHEMA IF NOT EXISTS alerts")
    
    # Create audit_events table with partitioning
    op.create_table(
        'audit_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSON, default=dict),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('signature', sa.String(64), nullable=False),
        schema='audit',
        postgresql_partition_by='RANGE (timestamp)',
    )
    
    # Create partitions
    op.execute("""
        CREATE TABLE audit.audit_events_2024_01 PARTITION OF audit.audit_events
        FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
    """)
    op.execute("""
        CREATE TABLE audit.audit_events_2024_02 PARTITION OF audit.audit_events
        FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
    """)
    # ... additional partitions
    
    # Create indexes
    op.create_index('idx_audit_user_id', 'audit_events', ['user_id'], schema='audit')
    op.create_index('idx_audit_ao_id', 'audit_events', ['ao_id'], schema='audit')
    op.create_index('idx_audit_timestamp', 'audit_events', ['timestamp'], schema='audit')
    
    # Create validation_events table
    op.create_table(
        'validation_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ao_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('validator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('decision', sa.String(20), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('previous_state', postgresql.JSON, nullable=True),
        sa.Column('new_state', postgresql.JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('signature', sa.String(64), nullable=False),
        schema='audit',
    )
    
    # Create llm_interactions table with partitioning
    op.create_table(
        'llm_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('prompt_hash', sa.String(64), nullable=False),
        sa.Column('response_hash', sa.String(64), nullable=False),
        sa.Column('prompt_encrypted', sa.Text(), nullable=False),
        sa.Column('response_encrypted', sa.Text(), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=False),
        sa.Column('tokens_output', sa.Integer(), nullable=False),
        sa.Column('temperature', sa.String(10), nullable=True),
        sa.Column('system_prompt_hash', sa.String(64), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ao_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('signature', sa.String(64), nullable=False),
        schema='llm',
        postgresql_partition_by='RANGE (timestamp)',
    )
    
    # Create system_events table
    op.create_table(
        'system_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('service', sa.String(50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSON, default=dict),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('signature', sa.String(64), nullable=False),
        schema='audit',
    )
    
    # Create entity_snapshots table
    op.create_table(
        'entity_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_data', postgresql.JSON, nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('operation', sa.String(20), nullable=False),
        sa.Column('changed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('signature', sa.String(64), nullable=False),
        schema='audit',
    )
    
    # Create AI Act tables
    op.create_table(
        'aipds',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now()),
        schema='ai_act',
    )
    
    op.create_table(
        'ai_contestations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('decision_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reason_type', sa.String(50), nullable=False),
        sa.Column('reason_description', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'under_review', 'accepted', 'rejected', name='contestation_status'), default='pending'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewer_decision', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        schema='ai_act',
    )
    
    op.create_table(
        'ai_disclosures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('decision_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('disclosure_text', sa.Text(), nullable=False),
        sa.Column('ai_system_name', sa.String(100), nullable=False),
        sa.Column('ai_system_version', sa.String(50), nullable=False),
        sa.Column('ai_system_provider', sa.String(100), nullable=False),
        sa.Column('shown_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        schema='ai_act',
    )
    
    op.create_table(
        'xai_explanations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('decision_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('feature_importance', postgresql.JSON, nullable=False),
        sa.Column('explanation_text', sa.Text(), nullable=False),
        sa.Column('method', sa.String(50), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('confidence_score', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        schema='ai_act',
    )
    
    # Create alerts tables
    op.create_table(
        'alert_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alert_type', sa.Enum('ao_new', 'ao_deadline', 'ao_modified', 'submission_new', 'submission_status', 'validation_required', 'validation_urgent', 'system_error', 'system_performance', 'ai_contestation', 'ai_review', name='alert_type'), nullable=False),
        sa.Column('channel', sa.Enum('email', 'in_app', 'webhook', 'none', name='alert_channel'), default='email'),
        sa.Column('frequency', sa.Enum('immediate', 'daily', 'weekly', name='alert_frequency'), default='immediate'),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('quiet_hours_start', sa.Integer(), nullable=True),
        sa.Column('quiet_hours_end', sa.Integer(), nullable=True),
        sa.Column('custom_threshold', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now()),
        schema='alerts',
    )
    
    op.create_table(
        'alert_notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alert_type', sa.Enum('ao_new', 'ao_deadline', 'ao_modified', 'submission_new', 'submission_status', 'validation_required', 'validation_urgent', 'system_error', 'system_performance', 'ai_contestation', 'ai_review', name='alert_type'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('channel', sa.Enum('email', 'in_app', 'webhook', 'none', name='alert_channel'), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('metadata', postgresql.JSON, default=dict),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        schema='alerts',
    )
    
    op.create_table(
        'alert_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('alert_type', sa.Enum('ao_new', 'ao_deadline', 'ao_modified', 'submission_new', 'submission_status', 'validation_required', 'validation_urgent', 'system_error', 'system_performance', 'ai_contestation', 'ai_review', name='alert_type'), nullable=False, unique=True),
        sa.Column('subject_template', sa.String(255), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('sms_template', sa.String(160), nullable=True),
        sa.Column('push_template', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now()),
        schema='alerts',
    )


def downgrade():
    op.drop_table('alert_templates', schema='alerts')
    op.drop_table('alert_notifications', schema='alerts')
    op.drop_table('alert_configs', schema='alerts')
    op.drop_table('xai_explanations', schema='ai_act')
    op.drop_table('ai_disclosures', schema='ai_act')
    op.drop_table('ai_contestations', schema='ai_act')
    op.drop_table('aipds', schema='ai_act')
    op.drop_table('entity_snapshots', schema='audit')
    op.drop_table('system_events', schema='audit')
    op.drop_table('llm_interactions', schema='llm')
    op.drop_table('validation_events', schema='audit')
    op.drop_table('audit_events', schema='audit')
    
    op.execute("DROP SCHEMA IF EXISTS audit CASCADE")
    op.execute("DROP SCHEMA IF EXISTS llm CASCADE")
    op.execute("DROP SCHEMA IF EXISTS ai_act CASCADE")
    op.execute("DROP SCHEMA IF EXISTS alerts CASCADE")
```

---

# SECTION 8 : ENVIRONNEMENT ET CONFIGURATION

## 8.1 Fichier .env.example

```bash
# Application
APP_NAME=AO Platform
APP_ENV=production
DEBUG=false
SECRET_KEY=change-me-in-production
AUDIT_SECRET_KEY=change-me-in-production

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/ao_platform
POSTGRES_USER=ao_user
POSTGRES_PASSWORD=change-me
POSTGRES_DB=ao_platform

# Redis
REDIS_URL=redis://redis:6379/0

# LLM
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-2024-08-06
OPENAI_TEMPERATURE=0.1

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@ao-platform.com
SMTP_PASSWORD=change-me
SMTP_TLS=true

# i18n
DEFAULT_LOCALE=fr
SUPPORTED_LOCALES=fr,nl,en,ar

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
PROMETHEUS_ENABLED=true

# SSL
DOMAIN=ao-platform.com
SSL_EMAIL=admin@ao-platform.com

# Alerts
ALERT_CRON_ENABLED=true

# AI Act
AI_ACT_COMPLIANCE_LEVEL=3
AIPD_REVIEW_DAYS=90
CONTESTATION_SLA_DAYS=30
```

---

# SECTION 9 : CHECKLIST DE LIVRAISON

## 9.1 Avant merge

- [ ] Tous les fichiers produits avec code complet
- [ ] Tests unitaires backend passent (>80% couverture)
- [ ] Tests unitaires frontend passent (>80% couverture)
- [ ] Tests axe-core passent (zero violations)
- [ ] Tests E2E Playwright passent (15 scenarios)
- [ ] Tests i18n passent (cles completes)
- [ ] Tests de charge passent (k6)
- [ ] Scan securite passent (bandit, safety, npm audit)
- [ ] Build Docker reussi
- [ ] Migrations Alembic testees
- [ ] Documentation utilisateur complete (20 guides)
- [ ] Declaration accessibilite publiee
- [ ] AIPD validee
- [ ] AI Act conformite niveau 3 verifiee

## 9.2 Post-deploy

- [ ] Health checks tous verts
- [ ] SSL actif et valide
- [ ] Monitoring Prometheus + Grafana operationnel
- [ ] Alertes email testees
- [ ] Backup automatique configure
- [ ] Tours guides fonctionnels
- [ ] Help Center deploye
- [ ] i18n 4 locales testees
- [ ] Traçabilite forensique testee (timeline + export PDF)
- [ ] AI Act : transparence, explication, contestation testees
- [ ] RGAA : navigation clavier, skip links, modals testes
- [ ] Performance : Lighthouse > 90

---

# SECTION 10 : NOTES DE MISE A JOUR

## 10.1 Changements majeurs par rapport au Sprint 3 original

1. **i18n complet** : Integration Babel backend + react-i18next frontend, 4 locales avec RTL
2. **RGAA niveau AA** : Composants accessibles dedies, tests axe-core CI, declaration accessibilite
3. **Traçabilite 5 couches** : Audit, Validation, LLM, Event, Snapshot avec interface timeline + export PDF
4. **AI Act niveau 3** : 5 piliers (transparence, traçabilite, explication, contestation, documentation)
5. **Documentation utilisateur** : 5 tours guides + Help Center Docusaurus avec 20 guides
6. **Production ready** : Docker multi-stage, Nginx, SSL auto, CI/CD GitHub Actions complete
7. **Alertes avancees** : Cron jobs, multi-canal, configuration utilisateur, quiet hours
8. **Tests E2E complets** : 15 scenarios Playwright + securite + load tests

## 10.2 Points d'attention

- Les schemas PostgreSQL `audit`, `llm`, `ai_act`, `alerts` doivent etre crees avant les migrations
- La cle `AUDIT_SECRET_KEY` doit etre differente de `SECRET_KEY` et stockee de maniere securisee
- Les prompts/reponses LLM sont chiffres en AES-256 : impact performance a monitorer
- Le rate limiting sur les endpoints LLM est critique (cout API)
- Les partitions PostgreSQL necessitent maintenance mensuelle (creation nouvelles partitions)
- L'initialisation SSL (Certbot) doit etre faite manuellement la premiere fois
- Les donnees de traçabilite ne doivent JAMAIS etre supprimees (WORM)
- La declaration d'accessibilite doit etre mise a jour a chaque changement significatif

## 10.3 Performance

- Pagination obligatoire sur tous les endpoints liste (>50 items)
- Cache Redis pour les traductions i18n (TTL 1h)
- Cache pour les templates d'emails (TTL 24h)
- Lazy loading des namespaces i18n
- Debounce sur les recherches audit (>300ms)
- Virtual scrolling pour la timeline (>100 evenements)
- Compression gzip/brotli Nginx
- CDN pour les assets statiques (optionnel)

## 10.4 Securite additionnelle

- Hash HMAC-SHA256 pour tous les evenements de traçabilite
- Chiffrement AES-256-GCM pour les prompts/reponses LLM
- Isolation reseau Docker (backend internal)
- Non-root users dans tous les conteneurs
- Scan Trivy dans CI
- Dependabot active
- Secrets management (Docker Swarm / K8s / Vault)
- IP whitelisting pour l'administration
- Audit logs pour toute connexion admin

---

# SECTION 11 : ARCHITECTURE DES DONNEES

## 11.1 Schema relationnel complet

```
public.users
  id (PK, UUID)
  email (UNIQUE, String)
  password_hash (String)
  first_name (String)
  last_name (String)
  role (Enum: admin, acheteur, fournisseur, valideur)
  locale (String, default 'fr')
  created_at (DateTime)
  updated_at (DateTime)
  deleted_at (DateTime, nullable)

public.aos
  id (PK, UUID)
  title (String)
  description (Text)
  category (String)
  budget (Decimal)
  deadline_date (DateTime)
  status (Enum: draft, published, closed, cancelled)
  created_by (FK -> users.id)
  created_at (DateTime)
  updated_at (DateTime)

public.submissions
  id (PK, UUID)
  ao_id (FK -> aos.id)
  candidate_id (FK -> users.id)
  status (Enum: draft, submitted, pending_validation, validated, rejected)
  score (Decimal, nullable)
  submitted_at (DateTime, nullable)
  created_at (DateTime)

audit.audit_events (PARTITIONED by month)
  id (PK, UUID)
  user_id (FK -> users.id)
  action (String)
  resource_type (String)
  resource_id (UUID)
  metadata (JSON)
  ip_address (INET)
  user_agent (Text)
  timestamp (DateTime)
  signature (String, HMAC-SHA256)

audit.validation_events
  id (PK, UUID)
  ao_id (FK -> aos.id)
  submission_id (FK -> submissions.id)
  validator_id (FK -> users.id)
  decision (String)
  reason (Text)
  previous_state (JSON)
  new_state (JSON)
  timestamp (DateTime)
  signature (String)

llm.llm_interactions (PARTITIONED by month)
  id (PK, UUID)
  prompt_hash (String, SHA-256)
  response_hash (String, SHA-256)
  prompt_encrypted (Text, AES-256)
  response_encrypted (Text, AES-256)
  model_version (String)
  tokens_input (Integer)
  tokens_output (Integer)
  temperature (String)
  system_prompt_hash (String)
  user_id (FK -> users.id)
  ao_id (FK -> aos.id, nullable)
  timestamp (DateTime)
  signature (String)

audit.system_events
  id (PK, UUID)
  event_type (String)
  severity (String)
  service (String)
  message (Text)
  metadata (JSON)
  stack_trace (Text)
  timestamp (DateTime)
  signature (String)

audit.entity_snapshots
  id (PK, UUID)
  entity_type (String)
  entity_id (UUID)
  snapshot_data (JSON)
  version (Integer)
  operation (String)
  changed_by (FK -> users.id)
  timestamp (DateTime)
  signature (String)

ai_act.aipds
  id (PK, UUID)
  title (String)
  version (String)
  content (Text)
  approved_by (FK -> users.id)
  approved_at (DateTime)
  next_review (DateTime)
  created_at (DateTime)
  updated_at (DateTime)

ai_act.ai_contestations
  id (PK, UUID)
  decision_id (FK -> submissions.id)
  user_id (FK -> users.id)
  reason_type (String)
  reason_description (Text)
  status (Enum)
  reviewed_by (FK -> users.id)
  reviewer_decision (Text)
  created_at (DateTime)
  resolved_at (DateTime)

ai_act.ai_disclosures
  id (PK, UUID)
  decision_id (FK -> submissions.id)
  disclosure_text (Text)
  ai_system_name (String)
  ai_system_version (String)
  ai_system_provider (String)
  shown_at (DateTime)
  acknowledged (DateTime)
  user_id (FK -> users.id)

ai_act.xai_explanations
  id (PK, UUID)
  decision_id (FK -> submissions.id)
  feature_importance (JSON)
  explanation_text (Text)
  method (String)
  model_version (String)
  confidence_score (String)
  created_at (DateTime)

alerts.alert_configs
  id (PK, UUID)
  user_id (FK -> users.id)
  alert_type (Enum)
  channel (Enum)
  frequency (Enum)
  enabled (Boolean)
  quiet_hours_start (Integer)
  quiet_hours_end (Integer)
  custom_threshold (JSON)
  created_at (DateTime)
  updated_at (DateTime)

alerts.alert_notifications
  id (PK, UUID)
  user_id (FK -> users.id)
  alert_type (Enum)
  title (String)
  message (Text)
  channel (Enum)
  status (String)
  metadata (JSON)
  sent_at (DateTime)
  read_at (DateTime)
  created_at (DateTime)

alerts.alert_templates
  id (PK, UUID)
  alert_type (Enum, UNIQUE)
  subject_template (String)
  body_template (Text)
  sms_template (String)
  push_template (String)
  created_at (DateTime)
  updated_at (DateTime)
```

## 11.2 Index principaux

```sql
-- Audit
CREATE INDEX CONCURRENTLY idx_audit_events_user_timestamp ON audit.audit_events(user_id, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_audit_events_resource ON audit.audit_events(resource_type, resource_id);
CREATE INDEX CONCURRENTLY idx_validation_events_ao ON audit.validation_events(ao_id);
CREATE INDEX CONCURRENTLY idx_llm_interactions_user ON llm.llm_interactions(user_id, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_llm_interactions_ao ON llm.llm_interactions(ao_id);

-- AI Act
CREATE INDEX CONCURRENTLY idx_contestations_decision ON ai_act.ai_contestations(decision_id, status);
CREATE INDEX CONCURRENTLY idx_contestations_user ON ai_act.ai_contestations(user_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_disclosures_decision ON ai_act.ai_disclosures(decision_id);

-- Alerts
CREATE INDEX CONCURRENTLY idx_alert_configs_user ON alerts.alert_configs(user_id, alert_type);
CREATE INDEX CONCURRENTLY idx_notifications_user_status ON alerts.alert_notifications(user_id, status, created_at DESC);
```

---

# SECTION 12 : GLOSSAIRE

| Terme | Definition |
|-------|------------|
| AO | Appel d'Offres |
| RGPD | Reglement General sur la Protection des Donnees |
| AI Act | Reglement europeen sur l'intelligence artificielle |
| RGAA | Referentiel General d'Amelioration de l'Accessibilite |
| i18n | Internationalisation |
| RTL | Right-to-Left (droite a gauche) |
| XAI | Explainable AI (IA explicable) |
| AIPD | Analyse d'Impact relative a la Protection des Donnees |
| SLA | Service Level Agreement |
| WORM | Write Once Read Many |
| HMAC | Hash-based Message Authentication Code |
| CSP | Content Security Policy |
| HSTS | HTTP Strict Transport Security |
| CDN | Content Delivery Network |
| CI/CD | Continuous Integration / Continuous Deployment |

---

# SECTION 13 : CONTACTS ET RESSOURCES

## 13.1 Equipe

- **Product Owner** : [Nom]
- **Tech Lead** : [Nom]
- **DPO** : [Nom]
- **Docusaurus Help Center** : https://docs.ao-platform.com
- **Status Page** : https://status.ao-platform.com
- **API Documentation** : https://api.ao-platform.com/docs

## 13.2 Liens utiles

- RGAA 4.1 : https://www.numerique.gouv.fr/publications/rgaa-accessibilite/
- AI Act : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689
- RGPD : https://www.cnil.fr/fr/reglement-europeen-protection-donnees
- WCAG 2.1 : https://www.w3.org/TR/WCAG21/
- axe-core : https://www.deque.com/axe/
- Docusaurus : https://docusaurus.io/

---

# FIN DU PROMPT SPRINT 3 - MISE A JOUR

## Recapitulatif des livrables

### Fichiers produits : 35 fichiers detailles
- Groupe A i18n : 18 fichiers
- Groupe B RGAA : 10 fichiers
- Groupe C Traçabilite : 12 fichiers
- Groupe D AI Act : 14 fichiers
- Groupe E Documentation : 30 fichiers
- Groupe F Production : 21 fichiers
- Groupe G Alertes : 12 fichiers
- Groupe H Tests E2E : 22 fichiers

### Total : specifications pour 139 fichiers
### Cibles qualite : 5500-6000 lignes de prompt technique
### Conformite : RGPD, AI Act niveau 3, RGAA niveau AA
### Production : Docker, Nginx, SSL, CI/CD, Monitoring

---

*Document genere pour le Sprint 3 mis a jour - Version 3.2*
*Plateforme de gestion des appels d'offres - SaaS multi-tenant*
*Conformite reglementaire europeenne*
