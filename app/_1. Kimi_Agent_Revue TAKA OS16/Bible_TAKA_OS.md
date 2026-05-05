# TAKA OS — Bible Complète du Projet
## Document de Conception, Cahier des Charges Technique & Fonctionnel, Roadmap, Frontend, Back-office, Onboarding | v1.0 | Mai 2026

---

# PARTIE I — VISION & POSITIONNEMENT

## 1.1 Énoncé de Vision

**TAKA OS** est le premier système d'exploitation agentic open source (MIT) verticalisé sur les **Appels d'Offres publics et privés** en Europe. Il transforme la candidature aux marchés publics d'un processus manuel, dispersé et chronophage en un **cycle cognitif automatisé** : veille → qualification → suivi → capitalisation.

> *"Nous ne vendons pas de l'IA. Nous vendons des agents autonomes qui remplacent les tâches répétitives de la candidature aux AO."*

## 1.2 Positionnement Marché

| Dimension | TAKA OS | Concurrence |
|-----------|---------|-------------|
| **Cible** | PME/ETI soumissionnaires (candidats) | Acheteurs (procurement) |
| **Paradigme** | OS agentic multi-agents avec mémoire | Assistant rédaction / CRM basique |
| **Mémoire** | 4 types persistantes (épisodique, transactionnelle, procédurale, sémantique) | Stateless ou session courte |
| **Décision** | Scoring GO/NO-GO/MAYBE + délibération optionnelle | Intuition humaine |
| **Apprentissage** | TAKA LAB (capitalisation échecs/succès) | Aucun |
| **Souveraineté** | Open source MIT / On-prem / EU-hosted | Cloud US propriétaire |
| **Action** | Upload → Parse → Qualifie → Suit → Capitalise | Fragmenté (Excel + email + drive) |

## 1.3 Marché Cible

| Segment | Taille (France+Belgique) | Budget mensuel | Canal |
|---------|-------------------------|---------------|-------|
| PME BTP (20-50 salariés) | ~25 000 | 49-149€ | Direct / Partenariats |
| ETI Services (50-250) | ~12 000 | 149-499€ | Direct + Events |
| Cabinets conseil | ~5 000 | 299-899€ | LinkedIn + Webinars |
| Artisans multi-sites | ~18 000 | 49€ | Chambres de métiers |

## 1.4 Proposition de Valeur Unique

> **"Inventive AI t'aide à répondre à UN AO. TAKA OS apprend de TOUS tes AO pour que le suivant soit mieux qualifié, mieux préparé, mieux suivi."**

**3 piliers différenciateurs :**
1. **Open Source MIT + Self-hosted + Souveraineté EU** — aucun concurrent ne combine les trois
2. **Architecture 3 couches intégrée** (Veille + Qualification + Kanban) — personne ne fait les 3
3. **Prix 10-20× inférieur** — 49-499€ vs 500-2000€ des solutions AI équivalentes

## 1.5 Modèle Économique — Smart & Cheap

| Plan | Prix/mois | Cible | Inclus |
|------|-----------|-------|--------|
| **Solo** | 49€ | Freelance/Artisan | 1 user, 20 AO/mois, parsing basique |
| **Pro** | 149€ | PME | 3 users, 100 AO/mois, pgvector, similarité |
| **Enterprise** | 499€ | ETI | Illimité, on-premise, support, API |
| **TAKA Advisory** | 299-899€/mois | Cabinets | POC + Run + Support |

**Seuil de rentabilité :** 3 clients Pro = 447€ revenu, ~33€ coût = **414€ marge nette**.

---

# PARTIE II — ARCHITECTURE & STACK

## 2.1 Architecture MVP v0.1 (3 couches)

```
+--------------------------------------------------+
|  COUCHE 3 — AGENTS                               |
|  Sourcer (upload/alerte) | Qualifieur (GO/NO-GO) |
|  Tracker (deadlines/alertes)                    |
+--------------------------------------------------+
|  COUCHE 2 — MÉMOIRE                              |
|  PostgreSQL 15 + pgvector                        |
|  (transactionnel + vectoriel + JSONB)            |
+--------------------------------------------------+
|  COUCHE 1 — SENSORIMOTRICE                       |
|  Upload PDF/UBL/XML | Parsing PDF 4 niveaux      |
|  Notifications email                             |
+--------------------------------------------------+
|  KERNEL                                          |
|  EventBus async | Config Pydantic | Auth JWT      |
|  RBAC 3 rôles | Audit trail append-only          |
+--------------------------------------------------+
```

## 2.2 Stack Technique Verrouillée

| Couche | Technologie | Alternative Rejetée |
|--------|-------------|---------------------|
| Langage | Python 3.12+ | Python 3.14 (NEXA-MIND) |
| Framework | FastAPI + SQLAlchemy 2.0 async | Django, Flask, LangChain |
| Base de données | PostgreSQL 15 + pgvector (HNSW) | Qdrant, Redis, Neo4j |
| LLM | Mistral AI API (France, Apache 2.0) | Kimi API (Chine, RGPD) |
| Client LLM | httpx + Jinja2 templates | LangChain, CrewAI |
| Auth | python-jose + passlib (JWT maison) | Auth0, Clerk |
| EventBus | asyncio in-memory + persistance DB | Redis, RabbitMQ, NATS |
| Parsing PDF | pypdf → pdfplumber → Tesseract OCR | PyMuPDF (AGPL) |
| Frontend | React 18 + TypeScript + Vite | Next.js (trop lourd) |
| Styling | Tailwind CSS 3.4+ | CSS Modules, MUI |
| Composants | shadcn/ui (Radix + Tailwind) | Chakra, MUI |
| State | Zustand + TanStack Query | Redux |
| Formulaires | React Hook Form + Zod | Formik |
| HTTP Client | Axios + intercepteurs JWT | fetch natif |
| Tests | pytest + pytest-asyncio | unittest |
| Lint | ruff | black + isort + flake8 |
| Package | Poetry | pip |
| DevOps | Docker Compose | Kubernetes (overkill) |
| Infra | VPS Hetzner 6-8€ | AWS/GCP (coûts) |

## 2.3 5 Règles Absolues (Leçons NEXA-MIND)

| # | Règle | Conséquence si non-respect |
|---|-------|---------------------------|
| 1 | Un seul fichier modèles : `app/models/ao.py` | Conflits SQLAlchemy, tables dupliquées |
| 2 | `expire_on_commit=False` obligatoire | Lazy loading errors en cascade |
| 3 | Python <3.14 exigé | Crash SQLAlchemy 2.0.36 |
| 4 | Un seul conteneur PostgreSQL+pgvector | VPS 20€ insuffisant |
| 5 | Pas de CrewAI/LangChain/CrewAI en MVP | Latence + bugs d'intégration |

## 2.4 Architecture Post-MVP (v1.2)

```
+--------------------------------------------------+
|  COUCHE 5 — MÉTACOGNITION (TAKA LAB)            |
|  Auto-ajustement scoring | Apprentissage passif  |
+--------------------------------------------------+
|  COUCHE 4 — DÉLIBÉRATION (Parlement)             |
|  3 agents votent | Toggle ON/OFF | Timeout 30s   |
+--------------------------------------------------+
|  COUCHE 3 — AGENTS (Registry)                    |
|  Sourcer | Qualifieur | Writer (copilote)        |
|  Tracker | Depositor (v1.2, TAKA Vision)        |
+--------------------------------------------------+
|  COUCHE 2 — MÉMOIRE (PostgreSQL + pgvector)      |
|  Transactionnel | Épisodique | Procédural       |
|  Sémantique (JSONB)                             |
+--------------------------------------------------+
|  COUCHE 1 — SENSORIMOTRICE                       |
|  Upload | Parsing PDF 4 niveaux | Connecteurs   |
|  TAKA VISION v1.2 (Holo-1/UI-TARS/Qwen3)        |
+--------------------------------------------------+
|  KERNEL + BRIDGE Mistral (httpx + Jinja2)        |
+--------------------------------------------------+
```

---

# PARTIE III — CAHIER DES CHARGES FONCTIONNEL

## 3.1 Parcours Utilisateur Types

### Utilisateur : Manager (Chef d'entreprise, Responsable AO)
- Se connecte via email + mot de passe
- Voir le Dashboard avec KPIs (AO actifs, deadlines, taux GO)
- Uploader un DCE PDF → système parse automatiquement
- Voir le score GO/NO-GO/MAYBE → décider de candidater
- Glisser l'AO dans le pipeline Kanban (8 stages)
- Consulter la mémoire : "Des AO similaires ont-ils été gagnés ?"
- Paramétrer ses règles de qualification (CPV, montants, délais)

### Utilisateur : Viewer (Collaborateur, lecture seule)
- Voir la liste des AO
- Voir les deadlines
- Consulter la fiche détail d'un AO
- Ne peut pas modifier ni qualifier

### Utilisateur : Admin (IT, configuration)
- Gérer les utilisateurs du tenant
- Configurer les stages du pipeline
- Voir les logs d'audit
- Exporter des rapports

## 3.2 Fonctionnalités par Module

### Module Auth & Onboarding
| ID | Fonctionnalité | Priorité | Description |
|----|---------------|----------|-------------|
| AUTH-01 | Inscription tenant | P1 | Création compte entreprise (nom, SIRET, email admin) |
| AUTH-02 | Login email/password | P1 | Authentification JWT avec bcrypt |
| AUTH-03 | Dev-login (mode dev) | P1 | Login sans password pour développement |
| AUTH-04 | Refresh token rotation | P1 | Rotation automatique des refresh tokens |
| AUTH-05 | Logout & révocation | P1 | Révocation du refresh token |
| AUTH-06 | Mot de passe oublié | P2 | Email de réinitialisation |
| AUTH-07 | Onboarding wizard | P1 | Wizard 3 étapes : entreprise → règles → première AO |
| AUTH-08 | Invitation utilisateurs | P2 | Admin invite par email (rôle viewer/manager) |

### Module Tenders (Appels d'Offres)
| ID | Fonctionnalité | Priorité | Description |
|----|---------------|----------|-------------|
| TND-01 | Liste AO filtrable | P1 | Table avec filtres search/stage/qualification/deadline |
| TND-02 | Création manuelle AO | P1 | Formulaire titre/référence/acheteur/deadline/montant |
| TND-03 | Fiche détail AO | P1 | Onglets : Détails / Documents / Qualification / Historique |
| TND-04 | Upload document | P1 | Drag & drop PDF/ZIP/XML, validation MIME/magic bytes |
| TND-05 | Changement stage | P1 | PUT /stage avec validation du stage existant |
| TND-06 | Pipeline Kanban | P1 | 8 colonnes drag-drop, cards avec badges |
| TND-07 | Suppression (soft delete) | P1 | deleted_at, pas de suppression réelle |
| TND-08 | Export CSV/PDF | P2 | Export de la liste filtrée |

### Module Qualification
| ID | Fonctionnalité | Priorité | Description |
|----|---------------|----------|-------------|
| QLF-01 | Scoring règles | P1 | CPV match + montant range + deadline préparation |
| QLF-02 | Mémoire épisodique | P1 | "AO similaires : X gagnés, Y perdus" |
| QLF-03 | LLM fallback | P1 | Appel Mistral si score ambigu (0.3-0.7) |
| QLF-04 | Résultat GO/NO-GO/MAYBE | P1 | Score global + détail par critère |
| QLF-05 | Règles configurables | P1 | CPV whitelist, min/max montant, min préparation jours |
| QLF-06 | Historique qualifications | P2 | Timeline des qualifications d'un AO |

### Module Documents & Parsing
| ID | Fonctionnalité | Priorité | Description |
|----|---------------|----------|-------------|
| DOC-01 | Upload multipart | P1 | 50MB max, types : pdf, zip, xml, ubl |
| DOC-02 | Parsing asynchrone | P1 | Background task, statut pending→processing→completed/failed |
| DOC-03 | Extraction CPV | P1 | Regex + fallback LLM |
| DOC-04 | Extraction montant | P1 | Regex patterns € |
| DOC-05 | Extraction deadline | P1 | dateparser |
| DOC-06 | Extraction critères | P2 | Liste critères d'attribution |
| DOC-07 | Extraction lots | P2 | Nombre de lots + descriptions |
| DOC-08 | Fallback saisie manuelle | P2 | Quand parsing échoue |

### Module Tracker & Alertes
| ID | Fonctionnalité | Priorité | Description |
|----|---------------|----------|-------------|
| TRK-01 | Alertes deadlines | P1 | J-30, J-14, J-7, J-3, J-1 avant deadline submission |
| TRK-02 | Alertes questions | P2 | J-7, J-3, J-1 avant deadline questions |
| TRK-03 | Notifications email | P1 | SMTP configurable, templates HTML |
| TRK-04 | Notifications in-app | P2 | Badge notifications dans l'interface |
| TRK-05 | Marquer comme lu | P2 | PUT /alerts/{id}/read |

### Module Mémoire (pgvector)
| ID | Fonctionnalité | Priorité | Description |
|----|---------------|----------|-------------|
| MEM-01 | Recherche similarité | P1 | Texte → embedding → pgvector top_k=5 |
| MEM-02 | Stockage épisodique | P1 | Tender won/lost → copie dans memory_vectors |
| MEM-03 | Tags | P2 | Filtrage par tags |
| MEM-04 | Suppression RGPD | P2 | Purge avec raison |

### Module Back-office (Admin)
| ID | Fonctionnalité | Priorité | Description |
|----|---------------|----------|-------------|
| ADM-01 | Gestion utilisateurs | P2 | CRUD users, assignation rôles |
| ADM-02 | Gestion tenants | P2 | Liste, création, suspension |
| ADM-03 | Audit trail | P2 | Table filtrable, export CSV/PDF |
| ADM-04 | Logs système | P2 | Health, erreurs, latence |
| ADM-05 | Configuration stages | P2 | Personnaliser les 8 stages |

---

# PARTIE IV — CAHIER DES CHARGES TECHNIQUE

## 4.1 Modèles de Données SQLAlchemy 2.0

### Table `tenants`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| id | Integer | PK, auto | Identifiant unique |
| name | String(255) | NOT NULL | Nom de l'entreprise |
| slug | String(100) | UNIQUE | Slug URL-friendly |
| description | Text | nullable | Description |
| settings | JSONB | default {} | Règles de qualification, préférences |
| created_at | DateTime | default now | Création |
| updated_at | DateTime | default now | Mise à jour |

### Table `users`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| id | Integer | PK, auto | Identifiant |
| tenant_id | Integer | FK → tenants, index | Isolation multi-tenant |
| email | String(255) | UNIQUE per tenant | Email |
| hashed_password | String(255) | NOT NULL | Bcrypt hash |
| full_name | String(255) | nullable | Nom complet |
| role | Enum | NOT NULL | admin/manager/viewer |
| is_active | Boolean | default True | Actif ? |
| created_at | DateTime | default now | Création |
| updated_at | DateTime | default now | Mise à jour |

### Table `pipeline_stages`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| id | Integer | PK, auto | Identifiant |
| tenant_id | Integer | FK, index | Isolation |
| slug | String(50) | NOT NULL | Identifiant technique |
| name | String(100) | NOT NULL | Nom affiché |
| color | String(7) | default #ccc | Couleur hex |
| display_order | Integer | NOT NULL | Ordre d'affichage |
| is_final | Boolean | default False | Stage final (won/lost) |

### Table `tenders`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| id | Integer | PK, auto | Identifiant |
| tenant_id | Integer | FK, index | Isolation |
| reference | String(255) | NOT NULL | Référence acheteur |
| title | String(500) | NOT NULL | Titre |
| buyer_name | String(255) | nullable | Nom acheteur |
| cpv_code | String(20) | nullable | Code CPV |
| cpv_description | String(500) | nullable | Description CPV |
| description | Text | nullable | Description complète |
| amount_estimated | Numeric(15,2) | nullable | Montant estimé |
| currency | String(3) | default EUR | Devise |
| deadline_submission | Date | nullable | Deadline soumission |
| deadline_questions | Date | nullable | Deadline questions |
| status | Enum | default draft | draft/active/archived |
| pipeline_stage_id | Integer | FK | Stage actuel |
| qualification_result | Enum | nullable | GO/NO-GO/MAYBE |
| qualification_score | Numeric(4,3) | nullable | Score global 0-1 |
| qualification_details | JSONB | nullable | Détail par critère |
| metadata | JSONB | default {} | Critères, lots, etc. |
| deleted_at | DateTime | nullable | Soft delete |
| created_at | DateTime | default now | Création |
| updated_at | DateTime | default now | Mise à jour |

### Table `tender_documents`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| id | Integer | PK, auto | Identifiant |
| tender_id | Integer | FK, index | Lié à un AO |
| filename | String(255) | NOT NULL | Nom original |
| file_path | String(500) | NOT NULL | Chemin stockage |
| file_size | Integer | NOT NULL | Taille en bytes |
| mime_type | String(100) | NOT NULL | Type MIME |
| parsed_content | Text | nullable | Contenu extrait |
| parsing_status | Enum | default pending | pending/processing/completed/failed |
| parsing_error | Text | nullable | Message d'erreur |
| metadata | JSONB | default {} | Champs extraits |
| created_at | DateTime | default now | Création |

### Table `memory_vectors`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| id | Integer | PK, auto | Identifiant |
| tenant_id | Integer | FK, index | Isolation |
| tender_id | Integer | FK, nullable | Lié à un AO |
| content | Text | NOT NULL | Contenu textuel |
| embedding | Vector(768) | index | Embedding pgvector |
| memory_type | Enum | NOT NULL | episodic/procedural |
| tags | Text[] | default {} | Tags |
| created_at | DateTime | default now | Création |

### Table `audit_logs`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| id | Integer | PK, auto | Identifiant |
| tenant_id | Integer | FK, index | Isolation |
| user_id | Integer | FK, nullable | Qui a agi |
| action | String(100) | NOT NULL | Type d'action |
| resource_type | String(100) | NOT NULL | Type ressource |
| resource_id | String(100) | NOT NULL | ID ressource |
| payload | JSONB | nullable | Données contexte |
| ip_address | String(45) | nullable | IP |
| hash_chain | String(64) | NOT NULL | SHA-256 du log précédent |
| created_at | DateTime | default now | Création |

### Table `qualification_rules`
| Champ | Type | Contrainte | Description |
|-------|------|-----------|-------------|
| id | Integer | PK, auto | Identifiant |
| tenant_id | Integer | FK, index | Isolation |
| name | String(100) | NOT NULL | Nom de la règle |
| cpv_whitelist | Text[] | default {} | CPV autorisés |
| min_amount | Numeric(15,2) | nullable | Montant min |
| max_amount | Numeric(15,2) | nullable | Montant max |
| min_preparation_days | Integer | default 14 | Jours min préparation |
| required_certifications | Text[] | default {} | Certifications requises |
| scoring_weights | JSONB | default {} | Pondération scoring |
| created_at | DateTime | default now | Création |
| updated_at | DateTime | default now | Mise à jour |

## 4.2 API REST — Spécification

### Auth
| Méthode | Path | Body | Response | Rôle |
|---------|------|------|----------|------|
| POST | /auth/dev-login | {email} | JWT + user | Tous (dev only) |
| POST | /auth/login | {email, password} | JWT + refresh + user | Tous |
| POST | /auth/refresh | Cookie refresh_token | Nouveau JWT | Tous |
| GET | /auth/me | — | User profile | Tous |
| POST | /auth/logout | — | Révocation | Tous |

### Tenders
| Méthode | Path | Body/Filtres | Response | Rôle |
|---------|------|-------------|----------|------|
| GET | /tenders | ?search=&stage=&qualif=&deadline_from=&deadline_to=&limit=&offset=&sort_by=&sort_order= | Liste + pagination | viewer+ |
| POST | /tenders | {titre, référence, acheteur, deadline, montant} | Tender créé | manager+ |
| GET | /tenders/{id} | — | Détail + documents + historique | viewer+ |
| PUT | /tenders/{id} | {champs modifiés} | Tender mis à jour | manager+ |
| DELETE | /tenders/{id} | — | Soft delete | manager+ |
| PUT | /tenders/{id}/stage | {new_stage_slug} | Stage changé | manager+ |
| POST | /tenders/{id}/qualify | — | Lancer qualification | manager+ |
| GET | /tenders/{id}/qualification | — | Résultat qualification | viewer+ |

### Documents
| Méthode | Path | Body | Response | Rôle |
|---------|------|------|----------|------|
| POST | /tenders/{id}/documents | multipart (file) | Document créé | manager+ |
| GET | /documents/{id} | — | Détail document | viewer+ |
| GET | /documents/{id}/download | — | Fichier binaire | viewer+ |
| DELETE | /documents/{id} | — | Suppression | manager+ |
| POST | /documents/{id}/parse | — | Lancer parsing async | manager+ |

### Pipeline
| Méthode | Path | Body | Response | Rôle |
|---------|------|------|----------|------|
| GET | /pipeline-stages | — | Liste stages | viewer+ |
| PUT | /pipeline-stages/reorder | {ordered_slugs[]} | Réordonné | admin |

### Memory
| Méthode | Path | Body | Response | Rôle |
|---------|------|------|----------|------|
| POST | /memory/search | {query, top_k=5} | Résultats similarité | viewer+ |
| GET | /memory/{id} | — | Détail entrée | viewer+ |
| DELETE | /memory/{id} | — | Suppression RGPD | manager+ |

### Admin
| Méthode | Path | Body | Response | Rôle |
|---------|------|------|----------|------|
| GET | /admin/tenants | — | Liste tenants | admin |
| POST | /admin/tenants | {name, slug} | Tenant créé | admin |
| GET | /admin/users | — | Liste users | admin |
| POST | /admin/users | {email, role, tenant_id} | User créé | admin |
| GET | /admin/audit-logs | ?action=&resource_type=&from=&to= | Logs filtrés | admin |

### Alerts
| Méthode | Path | Body | Response | Rôle |
|---------|------|------|----------|------|
| GET | /alerts | — | Liste alertes | viewer+ |
| PUT | /alerts/{id}/read | — | Marqué lu | viewer+ |
| GET | /alerts/unread-count | — | Nombre non lues | viewer+ |

## 4.3 Architecture JWT & Sécurité

### Structure JWT
```json
{
  "sub": "user_id",
  "tenant_id": 1,
  "role": "manager",
  "exp": 1715433600,
  "iat": 1715432700,
  "jti": "unique-token-id"
}
```

### RBAC
| Rôle | Viewer | Manager | Admin |
|------|--------|---------|-------|
| Lire tenders | ✅ | ✅ | ✅ |
| Créer/modifier tenders | ❌ | ✅ | ✅ |
| Qualifier | ❌ | ✅ | ✅ |
| Supprimer | ❌ | ✅ | ✅ |
| Gérer users | ❌ | ❌ | ✅ |
| Voir audit | ❌ | ❌ | ✅ |
| Config stages | ❌ | ❌ | ✅ |

### Audit Trail
- Append-only, jamais de UPDATE/DELETE
- Hash chain SHA-256 (immuabilité)
- Export CSV/PDF pour inspecteur fiscal

### Rate Limiting
| Groupe | Limite | Fenêtre |
|--------|--------|---------|
| Auth | 5 req/min | 1 min |
| API générale | 100 req/min | 1 min |
| Upload | 10 req/min | 1 min |

---

# PARTIE V — FRONTEND

## 5.1 Stack Frontend

| Technologie | Version | Rôle |
|-------------|---------|------|
| React | 18+ | Framework UI |
| TypeScript | 5.3+ | Typage strict |
| Vite | 5+ | Bundler, HMR |
| Tailwind CSS | 3.4+ | Styling utility-first |
| shadcn/ui | latest | Composants base (Radix UI) |
| Zustand | 4.5+ | State management global |
| TanStack Query | 5+ | Data fetching + cache |
| React Router | v6 | Routing SPA |
| React Hook Form | 7+ | Formulaires performants |
| Zod | 3+ | Validation schema |
| Axios | 1.6+ | HTTP client |
| date-fns | 3+ | Manipulation dates |
| @dnd-kit/core | 6+ | Drag & drop Kanban |

## 5.2 Pages & Routes

| Route | Page | Rôle | Description |
|-------|------|------|-------------|
| /login | LoginPage | Tous | Formulaire login + dev login |
| /dashboard | DashboardPage | viewer+ | KPI cards, graphiques, AO récents |
| /tenders | TendersPage | viewer+ | Table filtrable, pagination, actions |
| /tenders/:id | TenderDetailPage | viewer+ | Onglets : Détails/Documents/Qualif/Historique |
| /pipeline | PipelinePage | viewer+ | Kanban 8 colonnes drag-drop |
| /upload | UploadPage | manager+ | Zone drop, progression, résultat parsing |
| /memory | MemoryPage | viewer+ | Recherche similarité, résultats |
| /settings | SettingsPage | manager+ | Profil, règles qualif, stages |
| /audit | AuditLogsPage | admin | Table filtrable logs, export CSV/PDF |

## 5.3 Composants Clés

### Layout
- **Layout.tsx** — Sidebar + Header + Content area
- **Sidebar.tsx** — Navigation (Dashboard, AO, Pipeline, Upload, Mémoire, Paramètres)
- **Header.tsx** — Titre page, actions, profil, notifications
- **MobileNav.tsx** — Navigation mobile (bottom bar)

### Tenders
- **TenderCard.tsx** — Carte Kanban + liste (titre, deadline, montant, badges)
- **TenderTable.tsx** — Tableau sortable, paginable, actions rapides
- **TenderForm.tsx** — Formulaire création/édition (React Hook Form + Zod)
- **TenderFilters.tsx** — Barre filtres avancés (search, stage, qualif, deadline)

### Pipeline
- **PipelineBoard.tsx** — Plateau Kanban complet
- **PipelineColumn.tsx** — Colonne = stage (header + cards)
- **SortableTenderCard.tsx** — Carte draggable (DndKit)

### Qualification
- **QualificationBadge.tsx** — GO=vert, NO-GO=rouge, MAYBE=jaune
- **QualificationResult.tsx** — Barres de score détaillées (technique/financier/expérience)
- **QualificationTrigger.tsx** — Bouton "Qualifier" + spinner

### Documents
- **DocumentList.tsx** — Liste documents avec statut parsing
- **FileUploadZone.tsx** — Zone drag & drop avec progression

### Shared UI
- **KPICard.tsx** — Carte KPI Dashboard (titre, valeur, delta, icône)
- **DeadlineBadge.tsx** — <7j=rouge, <14j=orange, >=14j=vert
- **SearchBar.tsx** — Recherche + filtres intégrés
- **DataTable.tsx** — Table générique (TanStack Table)
- **StatusBadge.tsx** — Badge générique (stage, statut)
- **ConfirmDialog.tsx** — Dialog confirmation (shadcn Dialog)
- **EmptyState.tsx** — État vide illustré
- **LoadingSkeleton.tsx** — Skeleton screens

### AI Act / Conformité
- **AIBadge.tsx** — Badge "Assistant IA — TAKA OS" visible partout
- **AIActDisclaimer.tsx** — Disclaimer dans interface + exports
- **HumanValidation.tsx** — Checkbox validation humaine avant soumission

## 5.4 State Management (Zustand)

### authStore
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  devLogin: (email: string) => Promise<void>;
}
```

### tenderStore
```typescript
interface TenderState {
  tenders: Tender[];
  selectedTender: Tender | null;
  filters: TenderFilters;
  pagination: Pagination;
  setFilters: (filters: Partial<TenderFilters>) => void;
  selectTender: (id: number) => void;
}
```

### pipelineStore
```typescript
interface PipelineState {
  stages: PipelineStage[];
  tendersByStage: Record<string, Tender[]>;
  moveTender: (tenderId: number, targetStage: string) => Promise<void>;
  reorderStages: (orderedSlugs: string[]) => Promise<void>;
}
```

### uiStore
```typescript
interface UIState {
  sidebarOpen: boolean;
  modals: Record<string, boolean>;
  toasts: Toast[];
  addToast: (toast: Toast) => void;
  removeToast: (id: string) => void;
  toggleSidebar: () => void;
}
```

## 5.5 Design System

### Palette Cool Slate
| Rôle | Couleur | Hex |
|------|---------|-----|
| Primary | Heading | #2C3E50 |
| Dark | Body text | #34495E |
| Light | Captions | #7F8C8D |
| Accent | Links, badges GO | #3498DB |
| Success | GO badge | #27AE60 |
| Warning | MAYBE badge | #F39C12 |
| Danger | NO-GO badge, deadline <7j | #E74C3C |

### Typography
| Élément | Police | Taille | Poids |
|---------|--------|--------|-------|
| H1 | Calibri | 28pt (56 half-points) | Bold |
| H2 | Calibri | 22pt | Bold |
| H3 | Calibri | 16pt | SemiBold |
| Body | Calibri | 11pt | Regular |
| Caption | Calibri | 9pt | Regular |

---

# PARTIE VI — BACK-OFFICE & ADMIN

## 6.1 Tableau de Bord Admin (/audit)

### KPIs Système
- Nombre de tenants actifs
- Nombre d'AO total
- Taux de qualification GO
- Nombre d'alertes non lues
- Latence API moyenne
- Coût LLM journalier

### Gestion Utilisateurs
- Table : nom, email, tenant, rôle, dernière connexion, statut
- Actions : modifier rôle, suspendre, réinitialiser mot de passe
- Invitation par email (lien unique)

### Gestion Tenants
- Table : nom, slug, nombre d'AO, nombre d'users, statut
- Actions : créer, suspendre, configurer limites

### Audit Trail
- Table filtrable : date, acteur, action, ressource, résultat
- Filtres : date range, tenant, user, action type
- Export CSV (tout) / PDF (filtré)
- Hash chain vérifiée (intégrité)

### Logs Système
- Health endpoint : DB, disk, memory
- Erreurs 500+ avec stack trace
- Latence par endpoint
- Requêtes par minute

## 6.2 Configuration Tenant

### Règles de Qualification
- CPV whitelist (multi-select avec autocomplete)
- Fourchette montant (min/max)
- Délai minimum de préparation (jours)
- Pondération des critères (sliders)

### Pipeline Stages
- Liste des 8 stages (drag to reorder)
- Édition : nom, couleur, ordre
- Ajout/suppression (min 3, max 12)

### Paramètres Généraux
- Nom entreprise, logo
- Fuseau horaire
- Langue (FR/EN/NL)
- Notifications email (toggle)

---

# PARTIE VII — SIGNUP & ONBOARDING

## 7.1 Flow Signup (Inscription)

```
Landing Page
    ↓ "Commencer gratuitement"
Étape 1 — Compte
    ↓ Email + Password + Confirmation
    ↓ Validation email (token)
Étape 2 — Entreprise
    ↓ Nom entreprise + SIRET + Adresse + Secteur
    ↓ Création tenant (slug auto)
Étape 3 — Règles Qualification
    ↓ CPV principaux (multi-select)
    ↓ Fourchette montant (min/max)
    ↓ Délai préparation minimum
Étape 4 — Première AO
    ↓ Upload premier DCE OU création manuelle
    ↓ Parsing auto + résultat
    ↓ Score GO/NO-GO/MAYBE
    ↓ "Votre première AO est analysée !"
Dashboard
```

## 7.2 Flow Onboarding Wizard

### Étape 1 : Bienvenue (30s)
- "Bienvenue sur TAKA OS — Votre agent de candidature aux AO"
- Video 30s (comment ça marche)
- Skip possible

### Étape 2 : Configuration (2 min)
- CPV : autocomplete avec codes CPV 2024
- Montant : sliders EUR
- Délai : nombre de jours
- Prévisualisation des règles

### Étape 3 : Première Démonstration (3 min)
- Upload d'un DCE d'exemple (fourni par TAKA)
- Parsing en temps réel
- Résultat GO/NO-GO
- "C'est ainsi que TAKA qualifiera vos AO"

### Étape 4 : Invitation Équipe (1 min)
- Emails des collaborateurs
- Rôles suggérés (manager/viewer)
- Skip possible

### Étape 5 : Dashboard
- Tour guidé (tooltips) : "Vos AO", "Pipeline", "Paramètres"
- "Vous êtes prêt ! Prochaine étape : uploader votre premier vrai DCE"

## 7.3 Composants Onboarding

- **OnboardingWizard.tsx** — Stepper horizontal (5 étapes)
- **StepAccount.tsx** — Email + password + validation
- **StepCompany.tsx** — Nom + SIRET + secteur
- **StepRules.tsx** — CPV + montant + délai
- **StepDemo.tsx** — Upload démo + parsing + résultat
- **StepTeam.tsx** — Invitations emails
- **WelcomeModal.tsx** — Modal de bienvenue post-signup
- **GuidedTour.tsx** — Tour guidé dashboard (react-joyride)

---

# PARTIE VIII — ROADMAP DE DÉVELOPPEMENT

## 8.1 Sprint 0 — Fondation (Semaine 1)

**Objectif** : Repo Python fonctionnel avec FastAPI, PostgreSQL+pgvector, auth dev-mode, 8 tables, tests verts, Docker Compose.

| # | Fichier | Description |
|---|---------|-------------|
| A | pyproject.toml | Poetry, Python 3.12+, dépendances |
| B | .env.template | Variables d'environnement |
| C | app/config.py | Pydantic-Settings, préfixe TAKA_OS_ |
| D | app/exceptions.py | TakaException hiérarchie |
| E | app/main.py | Point d'entrée FastAPI |
| F | app/database.py | Engine async, sessionmaker, expire_on_commit=False |
| G | app/models/ao.py | 8 tables SQLAlchemy 2.0 Mapped[] |
| H | alembic/* | Migrations async |
| I | app/kernel/types.py | TakaEvent, EventType, Identity |
| J | app/kernel/bus.py | EventBus ABC + InMemoryEventBus |
| K | app/kernel/security.py | JWT encode/decode, bcrypt |
| L | app/kernel/auth.py | Dev login + login réel |
| M | app/api/deps.py | get_db(), get_current_user_dev(), get_current_user() |
| N | app/api/v1/router.py | Router principal |
| O | app/api/v1/endpoints/auth.py | POST /auth/dev-login, POST /auth/login |
| P | app/api/v1/endpoints/health.py | GET /health |
| Q | app/api/v1/endpoints/pipeline_stages.py | GET /pipeline-stages |
| R | app/services/pipeline.py | create_default_pipeline_stages() |
| S | scripts/seed_dev.py | Tenant Demo Corp + admin + 8 stages |
| T | docker-compose.yml | PostgreSQL pgvector seul |
| U | README.md | Quickstart complet |
| V | tests/conftest.py | Fixtures |
| W | tests/test_bus.py | Test publish/subscribe/isolation |
| X | tests/test_auth.py | Test dev-login/login/me |

**Livrable** : API sur :8000, auth fonctionnel, tests verts.

## 8.2 Sprint 1 — Sensorimotrice + Mémoire (Semaine 2)

**Objectif** : Upload DCE, parsing PDF stratifié, stockage embeddings pgvector, recherche similarité.

| # | Fichier | Description |
|---|---------|-------------|
| A | endpoints/documents.py | Upload multipart, GET, DELETE |
| B | services/upload.py | Validation MIME/magic bytes |
| C | schemas/document.py | Pydantic TenderDocument schemas |
| D | parsing/base_parser.py | Abstract ParserResult |
| E | parsing/pypdf_parser.py | Extraction texte simple |
| F | parsing/pdfplumber_parser.py | Extraction tableaux |
| G | parsing/ocr_parser.py | Tesseract PDF scannés |
| H | parsing/llm_parser.py | Mistral extraction champs |
| I | parsing/pipeline.py | Orchestrateur 4 niveaux |
| J | parsing/extractors.py | CPV, montant, deadline, critères, lots |
| K | parsing/constants.py | Patterns regex |
| L | parsing/worker.py | Background task async |
| M | services/memory.py | Embeddings, stockage, recherche |
| N | endpoints/memory.py | POST /memory/search |
| O | llm/client.py | MistralLLMClient, circuit breaker, retry |
| P | llm/templates.py | Jinja2 templates |
| Q | tests/test_upload.py | Upload valide/invalide/taille |
| R | tests/test_parsing.py | Pipeline 4 niveaux, extraction |
| S | tests/test_memory.py | Similarité, stockage, suppression |
| T | tests/test_llm_client.py | Circuit breaker, retry |

**Livrable** : POST /parse-pdf retourne JSON structuré, recherche similarité <20ms.

## 8.3 Sprint 2 — Qualifieur + Kanban (Semaine 3)

**Objectif** : Scoring GO/NO-GO/MAYBE complet, Pipeline Kanban UI, Dashboard, 9 pages React.

**Backend**
| # | Fichier | Description |
|---|---------|-------------|
| A | qualification/rules_engine.py | RulesEngine CPV/montant/deadline/mémoire |
| B | qualification/llm_scorer.py | LLM fallback cas ambigus |
| C | qualification/qualifier.py | QualifierService orchestre |
| D | schemas/qualification.py | QualificationResult, ScoreBreakdown |
| E | endpoints/qualification.py | POST /tenders/{id}/qualify |
| F | pipeline_service.py | change_stage(), stats, validation |

**Frontend**
| # | Fichier | Description |
|---|---------|-------------|
| G | pages/Dashboard.tsx | KPI cards, graphique pipeline |
| H | pages/TendersList.tsx | Table filtres, pagination |
| I | pages/TenderDetail.tsx | Onglets Détails/Documents/Qualif/Historique |
| J | pages/KanbanBoard.tsx | 8 colonnes drag-drop |
| K | pages/Upload.tsx | Zone drop, progression |
| L | components/KPICard.tsx | Carte KPI |
| M | components/TenderCard.tsx | Carte Kanban + liste |
| N | components/QualificationBadge.tsx | GO/NO-GO/MAYBE |
| O | components/DeadlineBadge.tsx | Couleur deadline |
| P | components/QualificationPanel.tsx | Barres de score |
| Q | components/Layout.tsx | Sidebar + Header + Content |
| R | stores/authStore.ts | JWT, user, login/logout |
| S | stores/tenderStore.ts | Tenders, filtres |
| T | stores/pipelineStore.ts | Stages, DnD |

**Livrable** : DCE uploadé → score GO/NO-GO en <5s (règles) ou <10s (LLM).

## 8.4 Sprint 3 — Tracker + SaaS Packaging (Semaine 4)

**Objectif** : Alertes deadlines, auth production, Docker Compose production, AI Act, tests E2E, README MIT.

| # | Fichier | Description |
|---|---------|-------------|
| A | tracker/scheduler.py | APScheduler 9h quotidien |
| B | tracker/alerter.py | Règles J-30/14/7/3/1 |
| C | tracker/notifications.py | EmailService SMTP |
| D | endpoints/alerts.py | GET /alerts, PUT /alerts/{id}/read |
| E | auth.py (update) | Bcrypt cost 12, refresh rotation, logout |
| F | AIBadge.tsx | Badge IA visible partout |
| G | AIActDisclaimer.tsx | Disclaimer interface + exports |
| H | HumanValidation.tsx | Checkbox validation humaine |
| I | docker-compose.yml (update) | 3 services : DB + App + Nginx |
| J | nginx/nginx.conf | Reverse proxy, SSL, gzip, rate limit |
| K | Dockerfile | Multi-stage Python |
| L | frontend/Dockerfile | Build Vite + Nginx |
| M | pages/Memory.tsx | Recherche similarité |
| N | pages/Settings.tsx | Profil, règles, stages |
| O | pages/AuditLogs.tsx | Table filtrable logs |
| P | App.tsx | Routes, guards auth |
| Q | main.tsx | Entry point, providers |
| R | services/api.ts | Axios + intercepteurs JWT |
| S | seed_dev.py (update) | 2 tenders de test |
| T | README.md (update) | Quickstart 5 commandes |
| U | LICENSE | MIT |
| V | CONTRIBUTING.md | Guide contribution |
| W | test_tracker.py | 8 tests alertes |
| X | test_e2e.py | 5 tests end-to-end |
| Y | test_compliance.py | 6 tests AI Act |

**Livrable** : v0.1 taguée, déployable en 5 minutes sur VPS 6€.

## 8.5 Post-MVP Roadmap (v0.2 → v2.0)

| Version | Période | Focus | Features |
|---------|---------|-------|----------|
| **v0.2** | Mois 2 | Connecteurs | BOAMP API, TED, e-marchespublics |
| **v0.3** | Mois 2-3 | Délibération | Toggle parlement 3 agents |
| **v0.4** | Mois 3 | TAKA LAB | Apprentissage passif scoring |
| **v0.5** | Mois 3 | Agent Writer | Copilote rédaction (RAG mémoires) |
| **v1.0** | Mois 4 | SaaS Scale | Multi-tenant strict, billing, API publique |
| **v1.1** | Mois 5 | TAKA Vision Prep | Benchmark providers VLA |
| **v1.2** | Mois 6-7 | TAKA Vision | Holo-1 7B + UI-TARS + Qwen3, dépôt AO visuel |
| **v1.3** | Mois 8 | GTM France | Sales, marketing, partenariats |
| **v1.4** | Mois 9 | Maroc | Adaptation légale, lancement |
| **v2.0** | Mois 10+ | Scale | Saisie legacy, onboarding observation, Enterprise |

---

# PARTIE IX — TAKA VISION (Module VLA v1.2)

## 9.1 Vision — "Donner des mains à TAKA"

TAKA Vision est le module VLA (Vision-Language-Action) qui permet aux agents TAKA d'interagir visuellement avec n'importe quelle interface graphique : portails de marchés publics, logiciels comptables, formulaires web.

## 9.2 Architecture Agnostique

```
TAKA Vision API (REST interne, sidecar Docker)
├── /v1/vision/localize → Trouve un élément UI
├── /v1/vision/navigate → Navigue vers un objectif
├── /v1/vision/extract → OCR une région
└── /v1/vision/validate → Vérifie le résultat

Providers VLA (switchable via config)
├── HoloProvider (Holo1.5-7B, Apache 2.0) — Navigation web
├── QwenProvider (Qwen3 VL 235B) — OCR multilingue
├── UI_TARSProvider (UI-TARS-7B) — Localisation pixel
└── GemmaProvider (Gemma 3 4B) — Edge/CPU fallback

Fallback Chain
Holo1.5-7B → Qwen3 VL → UI-TARS → Gemma 3 → Humain
```

## 9.3 Cas d'usage (par priorité)

| # | Cas | Provider | Phase | Value |
|---|-----|----------|-------|-------|
| 1 | Dépôt AO sur portail | Holo1.5-7B | v1.2 | 10/10 — Killer feature |
| 2 | Veille concurrentielle visuelle | UI-TARS-7B | v1.2 | 8/10 |
| 3 | Remplissage formulaire web | Holo1.5-7B | v1.2 | 9/10 |
| 4 | Saisie logiciel legacy | Qwen3 VL | v2.0 | 7/10 |
| 5 | Tests & QA visuels | UI-TARS-7B | v2.0 | 5/10 |

## 9.4 Sécurité VLA

- **Coffre-fort credentials** : HashiCorp Vault pattern simplifié
- **Screenshots chiffrés** : AES-256 au repos
- **Anonymisation auto** : Masquage SIRET, comptes bancaires
- **Mode humain au centre** : Validation obligatoire clic sensibles
- **Audit trail visuel** : Screenshot + action + résultat + signature

## 9.5 Comment TAKA devance les VLA seuls

| | Holo-1 Seul | TAKA + Holo-1 |
|---|-------------|---------------|
| Mémoire | Oublie entre sessions | Mémoire procédurale capitalise séquences |
| Décision | Clic immédiat | Parlement agentic débat avant action |
| Apprentissage | Répète erreurs | TAKA LAB détecte patterns, ajuste |
| Traçabilité | Opacité | Audit trail visuel complet |
| Multi-tenant | 1 utilisateur | RBAC, isolation, facturation |
| Fallback | 8% échec silencieux | Chaîne 4 providers + humain = 99.2% |

---

# PARTIE X — ÉQUIPE AGENTIQUE (30 Agents)

## 10.1 Structure des Pôles

| # | Pôle | Agents | Phase | Mission |
|---|------|--------|-------|---------|
| 1 | Direction | 2 | P1 | Vision, stratégie, ops |
| 2 | Produit | 3 | P1 | Roadmap, UX, specs |
| 3 | Eng. Backend | 5 | P1 | Kernel, API, agents, infra |
| 4 | Eng. Frontend | 2 | P1 | React, composants, design system |
| 5 | IA & ML | 4 | P1 | Parsing, scoring, embeddings, LLM |
| 6 | GTM France | 3 | P2 | Vente, closing, support FR |
| 7 | GTM Maroc | 3 | P3 | Vente, partenariats MA |
| 8 | Marketing | 2 | P2 | Brand, content, community |
| 9 | Juridique | 2 | P1 | AI Act, RGPD, licence |
| 10 | Finance | 2 | P3 | Compta, fundraising |
| 11 | Sécurité | 2 | P1 | Pentest, DPO, audit |

## 10.2 Activation Progressive

| Phase | Période | Agents actifs | Cumul | Focus |
|-------|---------|--------------|-------|-------|
| P1 — MVP | Mois 1 | 16 | 16 | Kernel, agents, API, frontend, infra |
| P2 — V1.1 | Mois 2-3 | +9 | 25 | GTM FR, marketing, délibération, TAKA LAB |
| P3 — Multi-marché | Mois 4-6 | +4 | 29 | Maroc, Belgique, finance |
| P4 — Scale | Mois 7+ | +1 | 30 | RH, ops scale |

## 10.3 Agents Critiques (12)

| Agent | Rôle | Chantiers | Sans lui = échec |
|-------|------|-----------|-----------------|
| CTO | Architecture, audit | Tous tech | Pas de direction |
| Lead Backend | Patterns, qualité | Kernel, API | Chaos technique |
| BE Kernel | Auth, RBAC, audit | Sécurité | Pas d'accès |
| BE Agents | Sourcer, Qualifieur, Tracker | Cœur métier | Pas de valeur |
| BE API | Endpoints, SQL, pgvector | Data | Pas de données |
| Lead IA | Choix modèles, gouvernance | Intelligence | Mauvaise qualité IA |
| IA NLP | Parsing PDF | Extraction | Pas de parsing |
| IA Scoring | GO/NO-GO | Qualification | Pas de décision |
| Lead Frontend | React, state | Interface | Pas d'UI |
| CPO | Vision produit | Priorisation | Mauvaise direction |
| PM AO | Specs métier | Vertical AO | Pas de fit marché |
| Security Officer | Pentest, hardening | Sécurité | Fuite données |

---

# PARTIE XI — SÉCURITÉ & CONFORMITÉ

## 11.1 AI Act (Août 2026)

- **Classification** : Système à risque limité (Article 50)
- **Badge IA** : Visible dès 1ère interaction
- **Marquage suggestions** : Suggestions générées par IA identifiées
- **Disclaimer** : "Assistant IA — suggestions à valider"
- **Validation humaine** : Checkbox obligatoire avant action sensible
- **Sanction** : Jusqu'à 7.5M€ ou 1% CA

## 11.2 RGPD

- **Self-hosted** = meilleur modèle RGPD
- **Données sous contrôle** utilisateur (serveur EU)
- **Droit à l'oubli** : suppression vecteurs pgvector
- **Portabilité** : export PostgreSQL natif
- **Minimisation** : pas de données superflues

## 11.3 Marchés Publics

- **Aucune interdiction** IA dans candidature
- **Responsabilité** : utilisateur reste responsable du contenu soumis
- **Immutabilité** : audit trail append-only (principe comptable)
- **Non-responsabilité** : clause MIT + disclaimer

## 11.4 Hardening

| Couche | Mesure |
|--------|--------|
| Auth | JWT 15min, refresh 7j, rotation, httpOnly cookie |
| RBAC | 3 rôles stricts, héritage admin→manager→viewer |
| Multi-tenancy | Row-level filtering, tenant_id dans JWT |
| SQL Injection | SQLAlchemy 2.0 parameterized queries |
| XSS | Content-Type JSON strict, pas de HTML dans réponses |
| CSRF | SameSite Strict, Origin validation |
| File Upload | MIME validation, magic bytes, 50MB max |
| Timing attacks | Bcrypt comparaison constant-time |
| Rate limiting | Sliding window, 100 req/min |
| Audit | Append-only, hash chain SHA-256 |

---

# PARTIE XII — DÉPLOIEMENT & OPS

## 12.1 Docker Compose Production

```yaml
services:
  db:
    image: ankane/pgvector:pg15
    volumes: [pgdata:/var/lib/postgresql/data]
    ports: [5432:5432]
    healthcheck: {test: pg_isready, interval: 5s}
    restart: unless-stopped

  app:
    build: .
    depends_on: [db]
    ports: [8000:8000]
    env_file: [.env]
    command: gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app
    restart: unless-stopped

  web:
    image: nginx:alpine
    ports: [80:80, 443:443]
    volumes: [./nginx/nginx.conf:/etc/nginx/nginx.conf]
    depends_on: [app]
    restart: unless-stopped
```

## 12.2 VPS Recommandé

| Fournisseur | Modèle | vCPU | RAM | Prix/mois | Usage |
|-------------|--------|------|-----|-----------|-------|
| **Hetzner** | CX31 | 4 | 8GB | 8.50€ | 10 clients |
| **Hetzner** | CPX31 | 4 | 8GB | 14.70€ | 20 clients + margin |
| **OVH** | VPS Comfort | 4 | 8GB | 11.50€ | Alternative EU |
| **Scaleway** | DEV1-L | 4 | 8GB | 15.00€ | Alternative FR |

## 12.3 Guide Installation Rapide

```bash
# 1. Clone
git clone https://github.com/taka-os/taka-os.git
cd taka-os

# 2. Config
cp .env.template .env
# Éditer .env avec vos valeurs

# 3. Lancer
docker-compose up -d

# 4. Migrations
docker-compose exec app alembic upgrade head

# 5. Seed
docker-compose exec app python scripts/seed_dev.py

# 6. Accès
open http://localhost:8000/docs  # Swagger
open http://localhost:3000      # Frontend
```

## 12.4 Backup

- **PostgreSQL** : pg_dump quotidien (cron)
- **Rétention** : 7 jours locaux + 30 jours S3
- **Uploads** : synchronisation S3
- **Restauration** : `pg_restore` one-command

## 12.5 Monitoring

- **Health** : GET /health (DB, disk, memory)
- **Logs** : JSON structuré via structlog
- **Métriques** : requests/sec, latence, erreurs
- **Alertes** : email en cas d'erreur 500 ou healthcheck failing

---

# PARTIE XIII — RISQUES & MITIGATIONS

| # | Risque | Probabilité | Impact | Mitigation |
|---|--------|------------|--------|------------|
| 1 | Parsing PDF échoue (taux <80%) | Moyenne | Élevé | Pipeline 4 niveaux + fallback LLM + saisie manuelle |
| 2 | Timeout LLM (API Mistral) | Moyenne | Élevé | Circuit breaker + retry + scoring règles fallback |
| 3 | SQLAlchemy async errors | Faible | Élevé | expire_on_commit=False + pool_size=5 + pool_pre_ping |
| 4 | Hallucination LLM scoring | Moyenne | Moyen | Validation humaine + disclaimer + audit trail |
| 5 | Concurrence Tenderbolt/Nextend | Moyenne | Moyen | Open source + prix 10× inférieur + communauté |
| 6 | Coût infra dépasse revenus | Faible | Élevé | VPS 6-8€, pas de GPU en MVP, facturation usage |
| 7 | Portails changent de design | Élevée | Moyen | Fallback API + diff visuel + alerte humaine |
| 8 | Licences VLA restrictives | Moyenne | Élevé | Holo1.5-7B (Apache 2.0), jamais Holo1-3B (NC) |
| 9 | RGPD screenshots VLA | Moyenne | Élevé | Anonymisation + rétention 30j + consentement |
| 10 | Échec parsing DCE scanné | Moyenne | Moyen | OCR Tesseract + fallback LLM + saisie manuelle |

---

# PARTIE XIV — MÉTRIQUES & KPIs

## 14.1 KPIs Produit (HEART)

| Dimension | Métrique | Cible Mois 3 | Cible Mois 6 |
|-----------|----------|-------------|--------------|
| **H**appiness | NPS | >30 | >50 |
| **E**ngagement | AO traités/semaine/utilisateur | 5 | 10 |
| **A**doption | % users actifs/semaine | 60% | 75% |
| **R**etention | Churn mensuel | <10% | <5% |
| **T**ask success | Taux parsing réussi | 80% | 90% |

## 14.2 KPIs Business

| Métrique | Cible Mois 3 | Cible Mois 6 | Cible Mois 12 |
|----------|-------------|--------------|---------------|
| Clients payants | 5 | 15 | 50 |
| MRR | 2 500€ | 7 500€ | 25 000€ |
| CAC | <500€ | <300€ | <200€ |
| LTV | >3 000€ | >5 000€ | >10 000€ |
| LTV/CAC | >3 | >5 | >10 |

## 14.3 KPIs Technique

| Métrique | Seuil Alert | Seuil Critique |
|----------|------------|----------------|
| Latence API p95 | >500ms | >1s |
| Erreur 5xx | >1% | >5% |
| Parsing taux succès | <75% | <60% |
| Score qualif précision | <85% | <70% |
| Uptime | <99.5% | <99% |

---

# ANNEXE A — Glossaire

| Terme | Définition |
|-------|-----------|
| **AO** | Appel d'Offres — consultation publique pour attributer un marché |
| **DCE** | Dossier de Consultation des Entreprises — document de l'AO |
| **CPV** | Common Procurement Vocabulary — classification européenne des marchés |
| **GO/NO-GO** | Décision de candidature : GO (candidater), NO-GO (abandonner) |
| **MVP** | Minimum Viable Product — version minimale vendable |
| **pgvector** | Extension PostgreSQL pour stockage et recherche vectorielle |
| **VLA** | Vision-Language-Action — modèle IA qui voit, comprend et agit |
| **TAKA LAB** | Module d'auto-amélioration par apprentissage passif |
| **RBAC** | Role-Based Access Control — contrôle d'accès par rôles |
| **JWT** | JSON Web Token — token d'authentification signé |

# ANNEXE B — Références Documents

| Document | Chemin | Description |
|----------|--------|-------------|
| Blueprint Technique | /mnt/agents/output/blueprint_taka_os_v1.md | 14 977 lignes, 4 sections |
| Blueprint Section 1 — Archi & DB | /mnt/agents/output/blueprint_section1_architecture_models.md | 4 139 lignes |
| Blueprint Section 2 — API & Sécurité | /mnt/agents/output/blueprint_section2_api_security.md | 3 142 lignes |
| Blueprint Section 3 — Agents & Mémoire | /mnt/agents/output/blueprint_section3_agents_memory.md | 4 364 lignes |
| Blueprint Section 4 — Frontend & DevOps | /mnt/agents/output/blueprint_section4_frontend_devops.md | 3 207 lignes |
| Prompt Sprint 0 | /mnt/agents/output/prompts/sprint_0_fondation.md | 2 513 lignes |
| Prompt Sprint 1 | /mnt/agents/output/prompts/sprint_1_sensorimotrice_memoire.md | 3 846 lignes |
| Prompt Sprint 2 | /mnt/agents/output/prompts/sprint_2_qualifieur_kanban.md | 4 323 lignes |
| Prompt Sprint 3 | /mnt/agents/output/prompts/sprint_3_tracker_saas.md | 5 478 lignes |
| Équipe Agentique | /mnt/agents/output/taka-team/ | 30 agents, 11 pôles |
| Analyse Holo-1 | /mnt/agents/output/analyse_holo1_taka_os.md | Analyse intégration VLA |
| TAKA Vision | /mnt/agents/output/taka-vision/ | Module VLA v1.2 |

---

*Document produit par l'équipe CTO TAKA OS | Mai 2026*
*Version 1.0 — GO CEO validé | 5 validations OUI*
*Ce document constitue la référence unique pour le développement de TAKA OS*
