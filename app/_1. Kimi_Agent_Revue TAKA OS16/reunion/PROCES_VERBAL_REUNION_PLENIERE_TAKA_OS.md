# PROCÈS-VERBAL DE LA RÉUNION PLÉNIÈRE KIMI-TAKA-SWARM
## Projet TAKA OS — Arbitrage Pré-Sprint 0

**Document de synthèse** | **Classification : Interne — Décisionnel**

---

# PARTIE I — VUE D'ENSEMBLE DE LA RÉUNION

---

## 1.1 Informations Générales

| Attribut | Valeur |
|----------|--------|
| **Nom de la réunion** | Réunion Plénière d'Arbitrage KIMI-TAKA-SWARM — Projet TAKA OS |
| **Date** | Session plénière consolidée (asynchrone par groupes thématiques) |
| **Format** | 4 groupes thématiques en parallèle + synthèse plénière centralisée |
| **Objectif principal** | Arbitrer les décisions architecturales, produit, business et qualité avant le lancement du développement (Sprint 0) |
| **Statut documentaire** | Procès-verbal définitif de synthèse |

---

## 1.2 Participants

La réunion a réuni **30 agents répartis sur 11 pôles d'expertise**, organisés en **4 groupes thématiques de débat** :

### Groupe Architecture & Technique (7 agents)
| Rôle | Agent | Responsabilités |
|------|-------|-----------------|
| Architecte Système | Agent #1 | Vision globale, cohérence technique, arbitrage d'architecture |
| Architecte Data | Agent #2 | Modélisation données, pgvector, partitionnement, ETL |
| Backend Senior | Agent #3 | FastAPI, modèles, API design, performance backend |
| DevOps Engineer | Agent #4 | CI/CD, infrastructure, Docker, Kubernetes, monitoring |
| AI Engineer | Agent #5 | Intégration LLM, providers, prompts, orchestration IA |
| ML Engineer | Agent #6 | Embeddings, classification, scoring probabiliste |
| DBA / Infra Engineer | Agent #7 | PostgreSQL, backups, PITR, haute disponibilité |

### Groupe Produit & Expérience (4 agents)
| Rôle | Agent | Responsabilités |
|------|-------|-----------------|
| Product Owner | Agent #8 | Vision produit, prioritisation, backlog |
| UX Designer | Agent #9 | Parcours utilisateurs, wireframes, accessibilité |
| Frontend Lead | Agent #10 | React, composants, state management |
| CX Specialist | Agent #11 | Onboarding, support, notifications, tour guidé |

### Groupe Business & Stratégie (5 agents)
| Rôle | Agent | Responsabilités |
|------|-------|-----------------|
| CEO / Stratège | Agent #12 | Vision business, pitch investisseurs, différenciation |
| Revenue Officer | Agent #13 | Pricing, modèle économique, rentabilité |
| Market Analyst | Agent #14 | Cible, segmentation, pays, acquisition |
| Legal & Compliance | Agent #15 | AI Act, RGPD, CLA, marque déposée |
| Community Manager | Agent #16 | Open source, communauté, contribution |

### Groupe Qualité & Production (5 agents)
| Rôle | Agent | Responsabilités |
|------|-------|-----------------|
| QA Lead | Agent #17 | Stratégie de test, coverage, E2E |
| Security Engineer | Agent #18 | OWASP, chiffrement, audit sécurité |
| Compliance Officer | Agent #19 | RGAA, AI Act, transparence, registre |
| DevOps QA | Agent #20 | CI/CD qualité, chaos engineering, circuit breaker |
| Technical Writer | Agent #21 | Documentation, doc-as-code, Docusaurus |

### Pôles transverses représentés (9 pôles supplémentaires)
- Pôle Data Science & Analytics
- Pôle SRE & Observabilité
- Pôle Support & Customer Success
- Pôle Juridique & RGPD
- Pôle Marketing & Communication
- Pôle Finance & Administration
- Pôle R&D & Innovation
- Pôle Partenariats & Intégrations
- Pôle Formation & Adoption

---

## 1.3 Méthodologie de la Réunion

La réunion a suivi une méthodologie structurée en **4 phases** :

### Phase 1 — Préparation (J-3)
Chaque groupe a reçu un cahier des questions thématiques (8 à 12 questions par groupe) avec :
- Contexte et enjeu de chaque question
- Options techniques/business/stratégiques identifiées
- Critères de décision (impact, risque, délai, coût)

### Phase 2 — Débat intra-groupe (J-2 à J-1)
Chaque groupe a débattu en autonomie de ses questions spécifiques :
- **Architecture & Technique** : 12 questions (860 lignes de débat)
- **Produit & Expérience** : 12 questions (932 lignes de débat)
- **Business & Stratégie** : 8 questions (830 lignes de débat)
- **Qualité & Production** : 8 questions (1 236 lignes de débat)

### Phase 3 — Soumission des décisions au registre
Chaque groupe a soumis ses décisions avec justification, version cible et niveau de risque.

### Phase 4 — Synthèse plénière et arbitrage transverse
Identification des convergences, des frictions transverses, et arbitrage final par consensus majoritaire avec validation du comité exécutif.

---

## 1.4 Objectifs Spécifiques de la Réunion

1. **Valider l'architecture technique fondatrice** du projet TAKA OS (stack, base de données, event bus, modèles)
2. **Définir le périmètre MVP v0.1** et la roadmap jusqu'à v1.0
3. **Trancher les arbitrages produit** (UX, onboarding, dashboard, notifications)
4. **Fixer la stratégie business** (pricing, cible, pays, acquisition, open source)
5. **Établir les critères de qualité et sécurité** non négociables avant beta
6. **Identifier les points de friction transverses** et arbitrer en plénière
7. **Produire le plan d'action consolidé** avec responsables et deadlines
8. **Émettre le verdict GO/NO-GO** pour le lancement du Sprint 0

---

## 1.5 Principes Directeurs Adoptés en Ouverture de Réunion

Les 30 agents ont validé les principes suivants comme boussole de décision :

| Principe | Description |
|----------|-------------|
| **Simplicity First** | Privilégier la solution simple qui marche maintenant, itérer ensuite |
| **Data-Driven Decisions** | Chaque décision technique doit être mesurable et instrumentée |
| **Security by Design** | La sécurité n'est pas une option, c'est une exigence progressive |
| **Compliance Graduelle** | Conformité AI Act et RGAA sur une roadmap glissante, pas au détriment du MVP |
| **Open Core** | Kernel 100% open source, features premium propriétaires (ratio 60/40) |
| **i18n-Ready** | Architecture prête pour l'internationalisation, activation progressive |
| **Fail Fast, Recover Fast** | Circuit breaker, retry, observabilité dès les premières versions |

---


# PARTIE II — TABLEAU CONSOLIDÉ DES DÉCISIONS

---

## 2.1 Présentation du Tableau Maître

Le tableau ci-dessous consolide **les 40 décisions** prises par les 4 groupes lors de leurs débats respectifs. Chaque décision est identifiée par un identifiant unique, classée par thème, avec sa version cible, son niveau de risque évalué (Faible / Moyen / Élevé / Critique), et son statut final (GO / NO-GO / DIFFERE).

---

## 2.2 Tableau Consolidé des Décisions

| ID | Thème | Groupe | Décision | Version | Risque | Statut |
|----|-------|--------|----------|---------|--------|--------|
| A-Q1 | Event Bus | Architecture | asyncio pur pour v0.1 + persistance PostgreSQL. LISTEN/NOTIFY en v0.2. NATS en v0.5. Redis exclu définitivement. | v0.1 | Moyen | GO |
| A-Q2 | pgvector | Architecture | Extension pgvector activée dès v0.1. Index HNSW par défaut pour les embeddings. Partitionnement conditionnel en v0.3 si >1M vecteurs. | v0.1 | Faible | GO |
| A-Q3 | Modèles | Architecture | Split des modèles par domaine en 9 fichiers dès v0.2. Fin de la règle "un seul fichier models.py". Migrations Alembic indépendantes par domaine. | v0.2 | Moyen | GO |
| A-Q4 | LLM Provider | Architecture | Multi-provider obligatoire : Mistral (principal) + OpenRouter (fallback). Ollama hors scope MVP (auto-hébergement reporté v1.x). Clé API chiffrée AES-256 en vault. | v0.1 | Moyen | GO |
| A-Q5 | Container Orchestration | Architecture | Docker Compose jusqu'à v0.6 minimum. 5 seuils mesurables avant migration Kubernetes : (1) >1000 requêtes/min, (2) >3 instances backend, (3) SLA 99.9%, (4) équipe SRE dédiée, (5) budget infra >2000€/mois. | v0.6 | Faible | GO |
| A-Q6 | Frontend React | Architecture | Versions exactes pinnées dans package-lock.json et yarn.lock (pas de ^ ni ~). Migration React 19 planifiée en v0.5 avec batterie de tests A/B. React 18.2 pour v0.1-v0.4. | v0.5 | Moyen | GO |
| A-Q7 | Mémoire TTL | Architecture | TTL fixe de 365 jours pour les souvenirs IA en v0.2. Oubli probabiliste (décroissance exponentielle) en v0.4. Paramètre configurable par tenant. | v0.2 | Faible | GO |
| A-Q8 | Circuit Breaker | Architecture | Seuils : 3 échecs consécutifs sur 30 secondes. Réessai automatique après 60 secondes. 6 circuits indépendants (un par agent IA). Monitoring Prometheus + AlertManager. | v0.2 | Moyen | GO |
| A-Q9 | Base de données | Architecture | PostgreSQL 16+ comme source de vérité unique. Pas de secondaire (MongoDB/Elasticsearch exclu). Réplication lecture en v0.4 si besoin de scaling. | v0.1 | Faible | GO |
| A-Q10 | Stack Backend | Architecture | Python 3.12+ obligatoire. FastAPI 0.110+ avec lifespan events. Pydantic V2 partout. SQLAlchemy 2.0 async. Uvicorn + Gunicorn en production. | v0.1 | Faible | GO |
| A-Q11 | API Gateway | Architecture | Pas d'API Gateway dédiée en v0.1-v0.3. Nginx reverse proxy + rate limiting par IP. Kong ou Traefik en v0.4 si multi-services. | v0.4 | Faible | DIFFERE |
| A-Q12 | Message Queue | Architecture | Pas de broker dédié en v0.1. File d'attente PostgreSQL (SKIP LOCKED) pour les jobs asynchrones. Celery + Redis possible en v0.3 si volumétrie >10k jobs/jour. | v0.3 | Moyen | DIFFERE |
| P-Q1 | Vue Kanban | Produit | Vue Kanban par défaut pour tous les utilisateurs. Indicateurs temporels intégrés (date de création, SLA, temps écoulé). Toggle Vue Planning (timeline Gantt) en v0.2. Pas de vue Liste en v0.1. | v0.1 | Faible | GO |
| P-Q2 | ScoreCard IA | Produit | 2 niveaux d'affichage : (1) Verdict condensé en 2 phrases maximum par défaut, (2) Détail 5D (Découpage, Délai, Défauts, Dépenses, Droit) dépliable au clic. Score numérique 0-100 avec code couleur. | v0.1 | Faible | GO |
| P-Q3 | Onboarding | Produit | Wizard obligatoire à la première connexion, mais optimisé : pré-remplissage SIRET via API Entreprise, skip possible des étapes 4 (préférences avancées) et 5 (invitations). 3 étapes minimum obligatoires. | v0.1 | Moyen | GO |
| P-Q4 | Sélecteur Business Line | Produit | Admin : top bar global sticky avec sélecteur de BL visible sur toutes les pages. Collaborateur : filtre local dans le Kanban si multi-BL, sinon BL unique implicite. Pas de switch BL global pour les collaborateurs. | v0.1 | Faible | GO |
| P-Q5 | HIL (Human-in-the-Loop) | Produit | Modal semi-bloquante pour les actions critiques (validation juridique, envoi d'offre). Sidebar asynchrone pour les informations complémentaires (contexte, historique). Expiration 24h avec relance email. | v0.2 | Moyen | GO |
| P-Q6 | Dashboard Éditeur | Produit | Tableau de données brut (liste des dossiers avec filtres) + 3 KPIs cards (taux de réponse, délai moyen, taux de succès). Pas de widgets graphiques (courbes, camemberts) en v0.1. Graphiques en v0.3. | v0.1 | Faible | GO |
| P-Q7 | Notifications | Produit | Système hybride : (1) in-app (badge + centre de notifications), (2) email digest quotidien récapitulatif, (3) email immédiat pour les alertes critiques (HIL expirant, erreur parsing). Paramétrable par utilisateur. | v0.1 | Faible | GO |
| P-Q8 | Tour Guidé | Produit | Tour minimal obligatoire de 3 étapes dès la première connexion : (1) "Voici votre Kanban", (2) "Déposez un PDF ici", (3) "Voici votre ScoreCard". Tour complet de 8 étapes en v0.3. Skip possible. | v0.1 | Faible | GO |
| P-Q9 | Thème UI | Produit | Mode clair par défaut. Mode sombre en v0.2. Thème personnalisable par BL en v0.4. Design system Figma synchronisé avec Storybook. | v0.2 | Faible | DIFFERE |
| P-Q10 | Mobile | Produit | Web responsive uniquement en v0.1-v0.6. Pas d'application mobile native. PWA minimal en v0.4 (installable, offline basique). | v0.4 | Moyen | DIFFERE |
| P-Q11 | Search Global | Produit | Barre de recherche globale en v0.2. Elasticlun.js côté client pour v0.1 (recherche limitée aux 50 derniers dossiers). Full-text PostgreSQL en v0.2. | v0.2 | Faible | DIFFERE |
| P-Q12 | Export | Produit | Export CSV basique en v0.2. Export PDF stylisé en v0.4. API d'export JSON ouverte pour les intégrations. | v0.2 | Faible | DIFFERE |
| B-Q1 | Open Source | Business | Ratio 60/40 : kernel (moteur IA, parsing, scoring, API core) 100% open source sous licence AGPL. Features premium (collaboration multi-BL, analytics avancées, SSO, SLA) propriétaires. CLA obligatoire pour les contributeurs. Marque "TAKA" déposée. | v0.1 | Moyen | GO |
| B-Q2 | Pricing | Business | Formule Pro à 99€/mois par utilisateur (HT). Early-bird à 49€/mois pour 6 mois, limité à 200 places avec code promo. Formule Starter gratuite limitée à 3 dossiers/mois en v0.3. | v0.1 | Moyen | GO |
| B-Q3 | Cible | Business | Cœur de cible : PME de 5 à 250 salariés (80% des efforts marketing). Grands groupes : programme Enterprise Early Access (5% des ressources) en v0.5 avec features dédiées (SSO, audit logs, CSM). | v0.1 | Faible | GO |
| B-Q4 | Pays | Business | Lancement simultané sur 3 pays : France (60% du trafic), Belgique (25%), Maroc (15%). i18n FR/NL/EN/AR. Conformité fiscale locale par pays. Support en français et anglais en v0.1. | v0.1 | Moyen | GO |
| B-Q5 | Acquisition | Business | Mix 60/40 : (60%) Acquisition organique via communauté OS + SEO technique (contenu sur le parsing PDF, l'IA agentic, les AO). (40%) LinkedIn Ads ciblées "Responsable AO" + "Directeur d'Agence". Budget mensuel : 3000€/mois en croissance. | v0.1 | Moyen | GO |
| B-Q6 | Différenciation | Business | Promesse de valeur unique : "+20% d'AO gagnés grâce à l'IA agentic" avec preuves chiffrées (case studies, taux de réussite vs benchmark). Positionnement : "Le copilote IA des réponses aux appels d'offres". | v0.1 | Faible | GO |
| B-Q7 | Rentabilité | Business | Seuil de rentabilité : 85 clients payants (99€/mois). Objectifs : 20 clients (M3), 85 clients (M6, rentable), 200 clients (M12). CAC cible : <150€. LTV cible : >1800€. MRR cible : 19 800€ à M12. | v0.1 | Moyen | GO |
| B-Q8 | AI Act | Business | Badge "IA utilisée" visible sur chaque résultat généré. Registre de transparence public dès v0.2 (données d'entraînement, modèles utilisés, biais connus). Mention obligatoire dans les conditions d'utilisation. | v0.2 | Moyen | GO |
| Q-Q1 | Tests | Qualité | Stratégie bimodale : (A) Couche déterministe (API, parsing, base de données) : 90% coverage obligatoire. (B) Couche probabiliste (IA, scoring, embeddings) : 85% confiance (tests de régression, golden dataset, A/B). Pytest + pytest-asyncio. | v0.1 | Moyen | GO |
| Q-Q2 | Parsing PDF | Qualité | Classification en 4 niveaux de confiance : A (97%+ — publication directe), B (90-97% — relecture recommandée), C (75-90% — relecture obligatoire), D (<75% — rejet + alerte). Seuils ajustables par tenant. Benchmark mensuel contre corpus de référence. | v0.1 | Moyen | GO |
| Q-Q3 | Sécurité MVP | Qualité | S-MVP (Security Minimum Viable Product) obligatoire avant ouverture beta publique : audit OWASP Top 10, chiffrement données sensibles AES-256, PITR (Point-in-Time Recovery) PostgreSQL. Bug bounty program en v0.5. | Beta | Élevé | GO |
| Q-Q4 | AI Act Conformité | Qualité | Niveau 1 (transparence) en v0.1. Niveau 2 (documentation + supervision humaine) en v0.5. Niveau 3 (audit externe complet) en v1.5. Avis juridique spécialisé AI Act avant v0.3 (deadline : avant beta publique). | v0.5 | Élevé | GO |
| Q-Q5 | Backups | Qualité | SSE-KMS (chiffrement côté serveur avec clés gérées) + PITR 7 jours avant beta. Multi-région (backup secondaire en zone géographique distincte) en v0.5. Test de restauration mensuel obligatoire. RTO <4h, RPO <15min. | Beta | Moyen | GO |
| Q-Q6 | RGAA | Qualité | Parcours critique (onboarding, login, Kanban, ScoreCard) conforme niveau AA en v0.5. Conformité RGAA complète (tous les parcours) en v0.7. Audit interne à chaque release majeure. Lecteur d'écran testé (NVDA/VoiceOver). | v0.5 | Moyen | GO |
| Q-Q7 | Circuit Breaker | Qualité | Tests 3 niveaux : (1) Unitaire (mock des dépendances), (2) Intégration (services réels en conteneurs), (3) Chaos (failure injection avec toxiproxy). Validation avant chaque release mineure. | v0.2 | Moyen | GO |
| Q-Q8 | Documentation | Qualité | Doc-as-code obligatoire (Markdown + Git). Freeze documentation 48h avant chaque release. Docusaurus pour la doc utilisateur. MkDocs pour la doc technique/développeur. Swagger/OpenAPI auto-généré pour l'API. | v0.1 | Faible | GO |

---

## 2.3 Répartition par Statut

| Statut | Nombre | Pourcentage |
|--------|--------|-------------|
| GO | 33 | 82.5% |
| NO-GO | 0 | 0% |
| DIFFERE | 7 | 17.5% |
| **Total** | **40** | **100%** |

---

## 2.4 Répartition par Niveau de Risque

| Risque | Nombre | Décisions concernées |
|--------|--------|---------------------|
| Faible | 14 | A-Q2, A-Q5, A-Q9, A-Q10, P-Q1, P-Q2, P-Q4, P-Q6, P-Q7, P-Q8, B-Q3, B-Q6, Q-Q8, P-Q11 |
| Moyen | 22 | A-Q1, A-Q3, A-Q4, A-Q7, A-Q8, A-Q12, P-Q3, P-Q5, P-Q10, B-Q1, B-Q2, B-Q4, B-Q5, B-Q7, Q-Q1, Q-Q2, Q-Q5, Q-Q6, Q-Q7, A-Q6, P-Q9, P-Q12 |
| Élevé | 3 | Q-Q3, Q-Q4, Q-Q5 |
| Critique | 1 | — |

---

## 2.5 Décisions DIFFEREES avec Critères de Levée

| ID | Décision | Critères de levée | Version estimée |
|----|----------|-------------------|-----------------|
| A-Q11 | API Gateway dédiée | Nombre de services >3 OU besoin d'authentification centralisée inter-services | v0.4 |
| A-Q12 | Message Queue dédiée | Volumétrie >10k jobs asynchrones/jour OU latence moyenne >2s | v0.3 |
| P-Q9 | Thème personnalisé par BL | >3 BL par tenant demandent la personnalisation | v0.4 |
| P-Q10 | Application mobile / PWA | >30% des connexions depuis mobile OU demande Enterprise | v0.4 |
| P-Q11 | Search global full-text | >100 dossiers par utilisateur OU volumétrie totale >10k dossiers | v0.2 |
| P-Q12 | Export PDF stylisé | >50% des utilisateurs utilisent l'export CSV | v0.4 |

---


# PARTIE III — POINTS DE CONVERGENCE TRANSVERSES

---

## 3.1 Définition

Les points de convergence sont les décisions ou principes sur lesquels **les 4 groupes sont tombés d'accord spontanément**, sans friction ni arbitrage nécessaire. Ces accords transverses forment le socle commun du projet TAKA OS et constituent les fondations non négociables.

---

## 3.2 Liste des Points de Convergence Identifiés

### C1 — Multi-tenant avec tenant_id partout

| Aspect | Détail |
|--------|--------|
| **Description** | L'architecture doit être multi-tenant dès v0.1 avec un tenant_id présent dans toutes les tables applicatives. |
| **Unanimité** | Architecture (100%), Produit (100%), Business (100%), Qualité (100%) |
| **Implémentation** | Colonne `tenant_id` UUID dans chaque table. Index composite (tenant_id, id). Row-Level Security (RLS) PostgreSQL en v0.2. |
| **Justification** | Le modèle SaaS impose l'isolation des données par client. Impossible de migrer a posteriori sans downtime majeur. |
| **Décision référente** | A-Q9 (PostgreSQL source de vérité), P-Q4 (sélecteur BL), B-Q3 (PME cible multi-tenant) |

### C2 — PostgreSQL comme source de vérité unique

| Aspect | Détail |
|--------|--------|
| **Description** | PostgreSQL 16+ est la seule base de données persistante en v0.1-v0.3. Pas de MongoDB, Elasticsearch, ou secondaire. |
| **Unanimité** | Architecture (100%), Qualité (100%), Produit (100%), Business (100%) |
| **Implémentation** | Une instance principale avec extensions : pgvector (embeddings), uuid-ossp, pg_stat_statements. Réplication lecture possible en v0.4. |
| **Justification** | Simplification drastique de l'architecture. Réduction des surfaces d'attaque. Backups unifiés. Pas de cohérence éventuelle à gérer. |
| **Décision référente** | A-Q1 (persistance PG EventBus), A-Q2 (pgvector), A-Q9 (PG unique), Q-Q5 (backups PG), Q-Q7 (chaos tests PG) |

### C3 — Python 3.12+, FastAPI, Pydantic V2

| Aspect | Détail |
|--------|--------|
| **Description** | Le backend s'appuie exclusivement sur Python 3.12+, FastAPI 0.110+, Pydantic V2, SQLAlchemy 2.0 async. |
| **Unanimité** | Architecture (100%), Qualité (100%), Produit (100%), Business (100%) |
| **Implémentation** | pyproject.toml avec contraintes strictes. CI vérifiant la compatibilité 3.12+. Lifespan events FastAPI pour l'init/destroy. |
| **Justification** | Pydantic V2 offre 5-10x performances supérieures à V1. SQLAlchemy 2.0 async permet le mode sans fil d'attente pour les I/O. |
| **Décision référente** | A-Q10 (Stack Backend), Q-Q1 (tests pytest-asyncio), Q-Q8 (doc API auto-générée) |

### C4 — React 18.2 avec versions pinnées

| Aspect | Détail |
|--------|--------|
| **Description** | Frontend en React 18.2 avec versions exactes pinnées. Migration React 19 planifiée en v0.5. |
| **Unanimité** | Architecture (100%), Produit (100%), Qualité (100%), Business (100%) |
| **Implémentation** | package.json sans ^ ni ~. package-lock.json versionné. CI vérifiant la cohérence lock. Tests de régression visuelle Chromatic en v0.3. |
| **Justification** | Stabilité du build reproductible. Évite les régressions silencieuses par mise à jour mineure. React 19 encore trop jeune pour production v0.1. |
| **Décision référente** | A-Q6 (React pinné), P-Q8 (Tour guidé React), Q-Q1 (tests E2E Playwright) |

### C5 — i18n FR / NL / EN / AR

| Aspect | Détail |
|--------|--------|
| **Description** | Architecture prête pour 4 langues : Français, Néerlandais, Anglais, Arabe. Activation progressive par pays. |
| **Unanimité** | Produit (100%), Business (100%), Architecture (100%), Qualité (100%) |
| **Implémentation** | i18n library (react-i18next côté client, Babel côté backend). Clés de traduction YAML. RTL pour AR. Locale-aware pour dates/nombres. |
| **Justification** | 3 pays simultanés dès le lancement (FR, BE, MA). Coût marginal si architecture dès le début. Coût exponentiel si migration tardive. |
| **Décision référente** | B-Q4 (Pays), P-Q3 (Onboarding i18n), A-Q10 (locale backend), Q-Q6 (RGAA avec i18n) |

### C6 — Scoring en YAML avec système V2

| Aspect | Détail |
|--------|--------|
| **Description** | Le scoring des appels d'offres utilise un système de règles déclaratif en YAML (scoring V2). Évaluation par moteur de règles, pas par LLM direct. |
| **Unanimité** | Architecture (100%), Produit (100%), Qualité (100%), Business (100%) |
| **Implémentation** | Fichiers YAML de scoring par secteur d'activité. Versionning des règles. Cache des règles compilées. Éditeur de règles en v0.5. |
| **Justification** | Déterminisme du scoring (reproductible). Performance (pas d'appel LLM pour chaque évaluation). Ajustabilité par métier sans redéploiement. |
| **Décision référente** | A-Q3 (modèles YAML), P-Q2 (ScoreCard), Q-Q1 (couche déterministe testable), B-Q6 (différenciation chiffrée) |

### C7 — Circuit Breaker avec monitoring Prometheus

| Aspect | Détail |
|--------|--------|
| **Description** | Circuit breaker sur tous les services externes (LLM, parsing, notifications) avec 6 circuits indépendants et monitoring Prometheus. |
| **Unanimité** | Architecture (100%), Qualité (100%), Produit (100%), Business (100%) |
| **Implémentation** | 3 échecs/30s, réessai 60s. Métriques Prometheus : taux d'ouverture, latence, succès. AlertManager pour les ouvertures prolongées. |
| **Justification** | Protection contre les cascades de panne. Dégradation gracieuse (mode fallback). Observabilité complète des dépendances. |
| **Décision référente** | A-Q8 (CB specs), Q-Q7 (CB tests chaos), A-Q5 (monitoring infra) |

### C8 — Sécurité progressive (Security by Design)

| Aspect | Détail |
|--------|--------|
| **Description** | La sécurité est une exigence croissante, pas un blocage au lancement. Roadmap de maturité : v0.1 (base), beta (S-MVP), v0.5 (durcie), v1.0 (audit). |
| **Unanimité** | Qualité (100%), Architecture (100%), Business (100%), Produit (100%) |
| **Implémentation** | v0.1 : HTTPS, authentification JWT, injection SQL protégée (SQLAlchemy). Beta : OWASP, chiffrement, PITR. v0.5 : MFA, audit logs, rate limiting avancé. |
| **Justification** | Sécurité absolue dès v0.1 = mort du MVP par surcharge. Sécurité négligée = faille critique en production. Approche graduelle = équilibre. |
| **Décision référente** | Q-Q3 (S-MVP), Q-Q4 (AI Act), Q-Q5 (backups chiffrés), A-Q4 (clés API chiffrées) |

### C9 — Badge "IA utilisée" + Transparence

| Aspect | Détail |
|--------|--------|
| **Description** | Tout contenu généré par IA porte un badge explicite "Contenu généré par intelligence artificielle". Registre de transparence public. |
| **Unanimité** | Business (100%), Qualité (100%), Produit (100%), Architecture (100%) |
| **Implémentation** | Badge visuel sur chaque ScoreCard, résumé, suggestion. Footer avec modèle utilisé et date. Page /transparence avec registre complet. |
| **Justification** | Obligation légale AI Act (niveau 1). Confiance utilisateur. Différenciation éthique. Protection juridique de l'éditeur. |
| **Décision référente** | B-Q8 (AI Act badge), Q-Q4 (conformité), P-Q2 (ScoreCard), B-Q1 (Open Source transparence) |

### C10 — PostgreSQL pour l'Event Bus (pas de Redis)

| Aspect | Détail |
|--------|--------|
| **Description** | L'Event Bus utilise PostgreSQL (asyncio pur + persistance) en v0.1, LISTEN/NOTIFY en v0.2. Redis est exclu définitivement comme broker d'événements. |
| **Unanimité** | Architecture (100%), Qualité (100%), Business (100%), Produit (100%) |
| **Implémentation** | Table `events` dans PostgreSQL avec pub/sub asyncio. LISTEN/NOTIFY natif PG pour le push asynchrone. NATS en v0.5 si scaling >10k events/min. |
| **Justification** | Élimination d'une dépendance infra (Redis). Cohérence transactionnelle (event + data dans la même transaction). Simplicité opérationnelle. |
| **Décision référente** | A-Q1 (EventBus), A-Q9 (PG unique), Q-Q5 (backups unifiés) |

### C11 — Docker Compose jusqu'à v0.6

| Aspect | Détail |
|--------|--------|
| **Description** | L'orchestration de conteneurs reste sur Docker Compose jusqu'à v0.6 minimum. 5 seuils mesurables doivent être atteints avant de migrer vers Kubernetes. |
| **Unanimité** | Architecture (100%), Business (100%), Qualité (100%), Produit (100%) |
| **Implémentation** | docker-compose.yml de production (pas dev-only). Health checks, restart policies, resource limits. 5 seuils : 1000 req/min, 3 instances, SLA 99.9%, SRE dédié, budget >2000€/mois. |
| **Justification** | Kubernetes ajoute une complexité opérationnelle incompatible avec une équipe de démarrage. Docker Compose suffit pour 0-1000 utilisateurs. Migration transparente possible. |
| **Décision référente** | A-Q5 (Docker vs K8s), Q-Q3 (S-MVP simplifié), B-Q7 (rentabilité à 85 clients) |

### C12 — Doc-as-code avec freeze 48h

| Aspect | Détail |
|--------|--------|
| **Description** | Toute la documentation est gérée as-code (Markdown dans Git). Freeze de 48h avant release pour synchronisation doc/code. |
| **Unanimité** | Qualité (100%), Architecture (100%), Produit (100%), Business (100%) |
| **Implémentation** | Docusaurus (doc utilisateur), MkDocs (doc technique), Swagger/OpenAPI (doc API). CI vérifiant la fraîcheur de la doc. |
| **Justification** | Doc synchronisée avec le code. Versionning de la doc. Review possible via PR. Pas de documentation orpheline. |
| **Décision référente** | Q-Q8 (Documentation), A-Q10 (API auto-doc), P-Q8 (Tour guidé documenté) |

### C13 — Couverture de tests différenciée

| Aspect | Détail |
|--------|--------|
| **Description** | Deux stratégies de test selon la nature du code : 90% coverage pour le code déterministe, 85% confiance pour le code probabiliste (IA). |
| **Unanimité** | Qualité (100%), Architecture (100%), Produit (100%), Business (100%) |
| **Implémentation** | Pytest + coverage pour le déterministe. Golden dataset + régression tests + A/B pour le probabiliste. Seuils bloquants en CI. |
| **Justification** | Le code déterministe (API, parsing structuré) peut viser 100% coverage. Le code probabiliste (LLM, scoring contextuel) ne peut pas être testé de manière exhaustive — on teste la qualité/statistique. |
| **Décision référente** | Q-Q1 (Tests bimodaux), Q-Q2 (Parsing classification), A-Q8 (CB tests) |

### C14 — Wizard d'onboarding optimisé

| Aspect | Détail |
|--------|--------|
| **Description** | L'onboarding est un wizard obligatoire à la première connexion, mais optimisé avec pré-remplissage et skip d'étapes optionnelles. |
| **Unanimité** | Produit (100%), Business (100%), Architecture (100%), Qualité (100%) |
| **Implémentation** | 5 étapes : (1) Bienvenue, (2) Entreprise (SIRET pré-rempli), (3) BL par défaut, (4) Préférences avancées (skip), (5) Invitations (skip). Barre de progression. |
| **Justification** | Onboarding obligatoire = données minimales collectées. Optimisation = friction réduite. Skip = respect du choix utilisateur. |
| **Décision référente** | P-Q3 (Onboarding), P-Q8 (Tour guidé), B-Q6 (différenciation par UX), Q-Q6 (RGAA onboarding) |

### C15 — Open Core 60/40

| Aspect | Détail |
|--------|--------|
| **Description** | Modèle économique Open Core : kernel (moteur, parsing, scoring, API) 100% open source AGPL. Features premium (multi-BL, analytics, SSO) propriétaires. |
| **Unanimité** | Business (100%), Architecture (100%), Qualité (100%), Produit (100%) |
| **Implémentation** | 2 repositories : `taka-os` (AGPL, kernel) et `taka-platform` (propriétaire, features premium). CLA pour les contributeurs. Marque déposée. |
| **Justification** | Communauté OS = acquisition organique + contributions + crédibilité. Premium = modèle économique viable. Ratio 60/40 = équilibre communauté/revenus. |
| **Décision référente** | B-Q1 (Open Source), B-Q5 (Acquisition), A-Q3 (modèles séparables), Q-Q8 (doc publique) |

---

## 3.3 Matrice de Convergence Transverse

| Convergence | Architecture | Produit | Business | Qualité |
|-------------|:------------:|:-------:|:--------:|:-------:|
| C1 — Multi-tenant | ✅ | ✅ | ✅ | ✅ |
| C2 — PostgreSQL unique | ✅ | ✅ | ✅ | ✅ |
| C3 — Python/FastAPI/PydanticV2 | ✅ | ✅ | ✅ | ✅ |
| C4 — React 18.2 pinné | ✅ | ✅ | ✅ | ✅ |
| C5 — i18n FR/NL/EN/AR | ✅ | ✅ | ✅ | ✅ |
| C6 — Scoring YAML V2 | ✅ | ✅ | ✅ | ✅ |
| C7 — Circuit Breaker + Prometheus | ✅ | ✅ | ✅ | ✅ |
| C8 — Sécurité progressive | ✅ | ✅ | ✅ | ✅ |
| C9 — Badge IA + Transparence | ✅ | ✅ | ✅ | ✅ |
| C10 — EventBus PostgreSQL (pas Redis) | ✅ | ✅ | ✅ | ✅ |
| C11 — Docker Compose jusqu'à v0.6 | ✅ | ✅ | ✅ | ✅ |
| C12 — Doc-as-code 48h freeze | ✅ | ✅ | ✅ | ✅ |
| C13 — Tests bimodaux 90/85 | ✅ | ✅ | ✅ | ✅ |
| C14 — Wizard onboarding optimisé | ✅ | ✅ | ✅ | ✅ |
| C15 — Open Core 60/40 | ✅ | ✅ | ✅ | ✅ |

---

**Conclusion Partie III** : Les 15 points de convergence forment le socle indiscutable du projet TAKA OS. Aucun de ces points ne nécessite de réouverture de débat. Ils sont gelés et constituent les fondations du Sprint 0.

---


# PARTIE IV — POINTS DE FRICTION TRANSVERSES

---

## 4.1 Définition

Les points de friction sont les sujets sur lesquels **au moins deux groupes expriment des positions divergentes** nécessitant un arbitrage en plénière. Chaque friction est traitée selon le format suivant :
- **Positions des groupes** : arguments pour et contre
- **Débat structuré** : échanges argumentaires
- **Arbitrage plénière** : décision tranchée avec justification
- **Action résultante** : qui fait quoi et quand

---

## 4.2 F1 — Split des modèles par domaine (Architecture dit GO v0.2, Qualité dit DIFFERE v0.3)

### Contexte
La base de code du backend contient actuellement un fichier `models.py` unique de ~800 lignes. Le groupe Architecture propose de le scinder en 9 fichiers par domaine métier dès la v0.2. Le groupe Qualité craint les risques de régression.

### Positions des Groupes

#### Architecture & Technique (POUR le split en v0.2)
| Argument | Détail |
|----------|--------|
| A1 — Cohérence métier | Chaque domaine (user, bl, dossier, document, parsing, scoring, notification, audit, config) a sa propre logique. Le split reflète l'architecture métier. |
| A2 — Parallélisation du travail | 9 fichiers = 9 streams de développement en parallèle sans conflits de merge sur un fichier unique. |
| A3 — Réduction du couplage | Un fichier unique crée des dépendances implicites. Le split force l'explicite. |
| A4 — Migrations indépendantes | Alembic peut gérer des branches de migration par domaine. Réduction des conflits de migration. |
| A5 — Testabilité | Tests par domaine indépendants. Un échec dans le domaine scoring n'impacte pas le domaine user. |

#### Qualité & Production (CONTRE le split en v0.2 — propose v0.3)
| Argument | Détail |
|----------|--------|
| Q1 — Risque de régression | Le split est une refactoring lourde. Risque d'erreur de mapping de colonnes, de relations cassées, de migrations invalides. |
| Q2 — Instabilité de la v0.2 | La v0.2 est la première version avec HIL (Human-in-the-Loop) et mémoire TTL. Ajouter le split models = trop de changements structurels simultanés. |
| Q3 — Couverture de tests | La couverture actuelle repose sur un fichier unique. Le split nécessite de réécrire les fixtures, les factories, les tests d'intégration. Coût estimé : 3-4 jours. |
| Q4 — Dette technique acceptable | Un fichier de 800 lignes n'est pas une dette critique. Le seuil de dette est à 1500 lignes. Attendre. |

### Débat Structuré

| Tour | Agent | Argument |
|------|-------|----------|
| 1 | Architecte Data | "Le fichier models.py grandit de ~50 lignes par semaine. À M6, on aura 2000 lignes. Le split sera 3x plus coûteux." |
| 2 | QA Lead | "Mais le split en v0.2 coïncide avec HIL et TTL. C'est 3 chantiers structuraux en même temps." |
| 3 | Backend Senior | "Le split peut être automatisé : 1 PR par domaine, 1 par semaine. Pas d'explosion." |
| 4 | Security Engineer | "Chaque PR de split = risque de régression sécurité (RLS, permissions). À tester manuellement." |
| 5 | Product Owner | "Si le split retarde la v0.2 de 2 semaines, on retarde HIL et le tour guidé. Impact utilisateur." |
| 6 | Architecte Système | "Compromis : split en v0.2 mais 1 seul domaine par sprint. 9 domaines sur 3 sprints." |
| 7 | QA Lead | "Acceptable si chaque domaine splitté = tests de non-régression obligatoires avant merge." |

### Arbitrage Plénière

**Décision** : **GO — Split des modèles en v0.2 avec contrainte de rythme**

| Paramètre | Valeur |
|-----------|--------|
| **Version cible** | v0.2 |
| **Rythme** | 1 domaine par sprint (2 semaines). 9 domaines = 9 sprints (~M2 à M6). |
| **Ordre de priorité** | (1) user, (2) dossier, (3) document, (4) scoring, (5) bl, (6) parsing, (7) notification, (8) audit, (9) config |
| **Condition de non-régression** | Tests d'intégration complets + migration Alembic testée sur dump de production anonymisé |
| **Gardien** | QA Lead valide chaque PR de split avant merge |
| **Rollback** | Alembic downgrade testé et documenté pour chaque domaine |

### Action Résultante

| # | Action | Responsable | Deadline |
|---|--------|-------------|----------|
| F1-A1 | Créer le plan de split avec ordre des 9 domaines et dépendances | Architecte Data | J+3 |
| F1-A2 | Implémenter le split domaine "user" (premier) avec tests complets | Backend Senior | S1 v0.2 |
| F1-A3 | Valider chaque PR de split (9 validations au total) | QA Lead | Par sprint |
| F1-A4 | Documenter les migrations et procédures de rollback | DBA | Par sprint |

---

## 4.3 F2 — Prix Early-bird à 49€/mois (Business dit GO, Produit dit NO-GO)

### Contexte
Le groupe Business propose un tarif early-bird à 49€/mois pour les 200 premiers clients (6 mois) afin de capter les early adopters et générer du feedback. Le groupe Produit craint que ce prix bas dévalore la perception du produit.

### Positions des Groupes

#### Business & Stratégie (POUR le 49€ early-bird)
| Argument | Détail |
|----------|--------|
| B1 — Acquisition early adopters | Les early adopters sont les plus précieux pour le feedback. Un prix attractif les incite à essayer malgré le risque MVP. |
| B2 — Momentum marketing | "200 premiers à 49€" crée l'urgence et la rareté. Levier psychologique fort. |
| B3 — CAC réduit | À 49€, le CAC peut être <100€ (bouche-à-oreille + communauté OS). Rentabilité client plus rapide. |
| B4 — Feedback loop | 200 utilisateurs payants = feedback qualitatif précieux. Coût du feedback : ~10 000€ de réduction de revenus, vs 50 000€ d'étude de marché. |
| B5 — Upgrade path | Après 6 mois à 49€, passage automatique à 99€. Taux de churn acceptable si valeur démontrée. |

#### Produit & Expérience (CONTRE le 49€ — propose 99€ sans early-bird)
| Argument | Détail |
|----------|--------|
| P1 — Perception de valeur | Un SaaS B2B à 49€/mois est perçu comme "cheap". Les responsables AO ont un budget de 500-2000€/mois pour leurs outils. 49€ signale la low-value. |
| P2 — Ancrage psychologique | Le premier prix est l'ancre. Les clients qui paient 49€ considéreront que 99€ est "cher" (x2). Difficile de remonter. |
| P3 — Support coûteux | 200 clients early-bird génèrent le même volume de support que 200 clients full-price. Coût de support ~30€/mois/client. À 49€, la marge est de 19€ vs 69€. |
| P4 — Qualité du feedback | Les clients à 49€ ne sont pas représentatifs des clients à 99€. Leurs besoins divergent (plus petites structures, plus sensibles au prix). |
| P5 — Différenciation concurrence | Les concurrents (AOCx, BidGate, etc.) sont à 150-300€/mois. À 99€, on est "premium accessible". À 49€, on entre en concurrence directe avec les outils génériques (Notion, Trello). |

### Débat Structuré

| Tour | Agent | Argument |
|------|-------|----------|
| 1 | Revenue Officer | "Sans early-bird, on lance à 99€ avec zéro réputation. Taux de conversion estimé : 0.5%. Avec 49€ : 3-5%." |
| 2 | UX Designer | "Mais les 200 early adopters à 49€ vont tweeter 'TAKA à 49€, c'est pas cher'. L'ancre est publique." |
| 3 | CEO / Stratège | "L'early-bird est une catégorie séparée : 'Plan Early Adopter'. Pas le prix standard. Mention explicite : 'Prix spécial phase de lancement'." |
| 4 | Product Owner | "Le support à 200 clients avec marge 19€ = 3800€/mois de marge totale. Un support engineer coûte 4000€/mois. On est déficitaires sur le support." |
| 5 | Market Analyst | "Limitons à 100 places early-bird au lieu de 200. Scarcity + marge support tenable." |
| 6 | CX Specialist | "100 clients early-bird avec onboarding premium + canal Slack dédié = feedback de qualité supérieure." |
| 7 | Revenue Officer | "Compromis : 49€ pour 100 places, onboarding avec entretien téléphonique obligatoire, accès Slack privé. Après 6 mois : 99€ ou offre Starter gratuite." |

### Arbitrage Plénière

**Décision** : **GO — Early-bird 49€/mois mais avec contraintes strictes**

| Paramètre | Valeur |
|-----------|--------|
| **Tarif early-bird** | 49€/mois (HT) |
| **Nombre de places** | **100** (réduit de 200) |
| **Durée** | 6 mois |
| **Conditions d'éligibilité** | Entreprise de 5-50 salariés. Premier abonnement. Paiement par prélèvement SEPA (engagement). |
| **Avantages inclus** | Onboarding téléphonique 30min, canal Slack privé #early-adopters, accès prioritaire aux nouvelles features, invitation mensuelle au produit webinar. |
| **Renouvellement** | Passage automatique à 99€/mois après 6 mois. Notification 30j avant. Option downgrade vers Plan Starter (gratuit, 3 dossiers/mois) en v0.3. |
| **Communication** | Mention explicite "Prix Early Adopter — Phase de lancement" sur toute la page de pricing. Pas d'affichage du 49€ comme prix standard. |
| **Anonymisation publique** | Le prix de 49€ n'est pas affiché publiquement (landing page générique = 99€). Code promo requis pour voir le tarif 49€. |

### Action Résultante

| # | Action | Responsable | Deadline |
|---|--------|-------------|----------|
| F2-A1 | Créer la page de pricing avec tarif caché 49€ (code promo) | Product Owner | J+7 |
| F2-A2 | Mettre en place le système de codes promo limités (100 max) | Revenue Officer | J+7 |
| F2-A3 | Créer le canal Slack #early-adopters et process d'invitation | Community Manager | J+3 |
| F2-A4 | Établir le script d'onboarding téléphonique 30min | CX Specialist | J+5 |
| F2-A5 | Configurer le mécanisme de passage 49€ → 99€ automatique | Revenue Officer | J+10 |

---

## 4.4 F3 — S-MVP sécurité avant beta (Qualité dit OBLIGATOIRE, Architecture dit IMPOSSIBLE en 4 semaines)

### Contexte
Le groupe Qualité exige que le Security MVP (S-MVP) soit complet avant l'ouverture beta publique : audit OWASP Top 10, chiffrement AES-256 des données sensibles, PITR PostgreSQL. Le groupe Architecture estime que cela représente 6-8 semaines de travail, incompatible avec le Sprint 0 de 4 semaines.

### Positions des Groupes

#### Qualité & Production (POUR S-MVP obligatoire avant beta)
| Argument | Détail |
|----------|--------|
| Q1 — Obligation légale | RGPD + données sensibles (SIRET, documents d'AO) = chiffrement obligatoire. Un leak pré-beta = mort du projet. |
| Q2 — Confiance investisseurs | Les VC demandent un SOC 2 ou équivalent. S-MVP = prérequis à la levée de fonds Série A. |
| Q3 — Récupération post-incident | Un incident de sécurité en beta = perte irréversible de confiance. Le marché B2B est petit et bavard. |
| Q4 — Coût du retard | Corriger une faille en production est 10-100x plus coûteux qu'en pré-beta. |
| Q5 — Reproductibilité | S-MVP obligatoire avant beta = culture sécurité instaurée dès le début. Pas de "on s'en occupera plus tard". |

#### Architecture & Technique (CONTRE S-MVP complet avant beta — propose v0.2)
| Argument | Détail |
|----------|--------|
| A1 — Charge de travail réaliste | Audit OWASP complet : 2 semaines. Chiffrement AES-256 + vault : 2 semaines. PITR + backups : 1 semaine. Tests + validation : 1 semaine. Total : 6 semaines. Sprint 0 = 4 semaines. |
| A2 — Délai de mise sur le marché | Retarder la beta de 6 semaines = retarder le premier revenu de 6 semaines = 85 clients atteints en M7.5 au lieu de M6. Objectif rentabilité décalé. |
| A3 — Beta privée ≠ beta publique | La beta peut être fermée (100 early-bird invités manuellement). Risque contrôlé. S-MVP en v0.2 pour l'ouverture publique. |
| A4 — Complexité PITR | PITR PostgreSQL en cloud = dépend du provider (AWS RDS, Scaleway, OVH). Chaque provider a sa procédure. 1 semaine minimum par provider. |
| A5 — Sécurité incrémentale | v0.1 : HTTPS + JWT + injections protégées. v0.2 : chiffrement + PITR. v0.3 : audit OWASP. Chaque version est plus sûre que la précédente. |

### Débat Structuré

| Tour | Agent | Argument |
|------|-------|----------|
| 1 | Security Engineer | "Un leak de documents d'AO = fuite de secrets commerciaux. Nos clients sont des entreprises du BTP et du numérique. C'est mortel." |
| 2 | DevOps Engineer | "La beta est 100 early-bird en invité manuel. On contrôle qui entre. Si on détecte un problème, on ferme en 5 minutes." |
| 3 | Compliance Officer | "RGPD article 32 : mesures techniques appropriées. Chiffrement est 'approprié' pour des données sensibles." |
| 4 | Backend Senior | "On peut faire du chiffrement au niveau application en 3 jours : SQLAlchemy TypeDecorator + Fernet (AES-128). Pas AES-256 mais mieux que rien." |
| 5 | DBA | "PITR avec pg_dump + WAL archives toutes les heures = 1 jour de setup. Pas du vrai PITR à la seconde, mais recoverable." |
| 6 | QA Lead | "Compromis : S-MVP light pour beta privée (chiffrement application + backups horaires + HTTPS + JWT). S-MVP complet pour beta publique." |
| 7 | Security Engineer | "Acceptable si la beta privée est VRAIMENT privée : invitation manuelle, NDA implicite (conditions d'utilisation), pas de données réelles sensibles." |
| 8 | CEO / Stratège | "Et si on demande aux early-bird de ne PAS charger de documents sensibles pendant la phase privée ? Clause dans les CGU." |

### Arbitrage Plénière

**Décision** : **GO — Sécurité différenciée : S-MVP Light pour beta privée, S-MVP Complet pour beta publique**

| Phase | Type de beta | Sécurité requise | Deadline |
|-------|-------------|------------------|----------|
| **v0.1** | Alpha interne (équipe + familles) | HTTPS + JWT + injection protégée | Sprint 0 |
| **Beta privée** | 100 early-bird (invitation manuelle) | S-MVP Light : chiffrement application (Fernet/AES-128) + backups horaires + HTTPS + JWT + conditions d'utilisation restrictives | v0.2 |
| **Beta publique** | Ouverture sans invitation | S-MVP Complet : audit OWASP + chiffrement AES-256 + vault + PITR 7j + MFA optionnel | v0.3 |

| Paramètre | Valeur |
|-----------|--------|
| **S-MVP Light** | Chiffrement colonnes sensibles (SIRET, email, contenu document) via Fernet (AES-128). Clé master en variable d'environnement. Backups pg_dump horaires. HTTPS forcé. JWT HS256 avec expiration 24h. |
| **S-MVP Complet** | Audit OWASP Top 10 avec rapport. Chiffrement AES-256-GCM via HashiCorp Vault ou AWS KMS. PITR PostgreSQL natif 7 jours. MFA TOTP. Rate limiting avancé. CSP headers stricts. |
| **Condition beta privée** | Early-birds doivent accepter les CGU restrictives : "Ne pas charger de documents classifiés ou sensibles. Données de test recommandées." |
| **Durée beta privée** | Maximum 8 semaines (100 early-birds, feedback collecté, S-MVP complet construit en parallèle). |

### Action Résultante

| # | Action | Responsable | Deadline |
|---|--------|-------------|----------|
| F3-A1 | Implémenter le chiffrement application (Fernet) pour les colonnes sensibles | Backend Senior | S2 v0.1 |
| F3-A2 | Configurer les backups pg_dump horaires + stockage S3 chiffré | DevOps Engineer | S2 v0.1 |
| F3-A3 | Rédiger les CGU restrictives pour beta privée | Legal & Compliance | J+5 |
| F3-A4 | Planifier l'audit OWASP Top 10 (prestataire externe ou interne) | Security Engineer | J+10 |
| F3-A5 | Configurer PITR PostgreSQL natif + Vault pour clés | DevOps Engineer + DBA | v0.3 |
| F3-A6 | Mettre en place MFA TOTP optionnel | Backend Senior | v0.3 |
| F3-A7 | Valider S-MVP Light avant ouverture beta privée | QA Lead + Security Engineer | v0.2 |
| F3-A8 | Valider S-MVP Complet avant ouverture beta publique | QA Lead + Security Engineer | v0.3 |

---

## 4.5 F4 — i18n dès v0.1 (Produit dit OUI, Architecture dit NON)

### Contexte
Le groupe Produit souhaite que l'interface soit disponible en 4 langues dès v0.1 (FR/NL/EN/AR) car le lancement simultané sur 3 pays (FR, BE, MA) l'exige. Le groupe Architecture argue que l'i18n complexifie le MVP et propose le français uniquement en v0.1, i18n en v0.2.

### Positions des Groupes

#### Produit & Expérience (POUR i18n en v0.1)
| Argument | Détail |
|----------|--------|
| P1 — Lancement 3 pays | FR 60%, BE 25%, MA 15%. Sans NL (Belgique) et AR (Maroc), on exclut 40% du marché cible dès le départ. |
| P2 — Perception locale | Un SaaS en français uniquement en Belgique néerlandophone = perception d'outre-Manche. Perte de crédibilité. |
| P3 — Coût de l'ajout tardif | Ajouter i18n a posteriori = réécrire tous les composants React, toutes les API responses, tous les emails. Coût estimé : 3-4 semaines en v0.2 vs 1 semaine en v0.1. |
| P4 — Architecture ready | react-i18next existe. Les clés de traduction sont des strings. Coût marginal si dès le départ. |
| P5 — SEO multi-pays | Le SEO en NL et EN est essentiel pour la Belgique et les expatriés. Pas de contenu NL = pas de ranking Google.be. |

#### Architecture & Technique (CONTRE i18n en v0.1 — propose v0.2)
| Argument | Détail |
|----------|--------|
| A1 — Complexité MVP | L'i18n touche : labels UI, messages d'erreur API, emails, dates, nombres, devise, RTL (AR), validation de formulaires. C'est 20-30% de surcharge cognitive. |
| A2 — Traductions de qualité | Des traductions Google Translate = ridicule. Traductions professionnelles NL/AR = 3000-5000€. Budget non prévu en v0.1. |
| A3 — Tests multipliés | Chaque test E2E doit tourner en 4 langues. Coverage identique ×4 = CI 4x plus longue. |
| A4 — Support multi-lingue | Support client en NL et AR ? Impossible avec l'équipe actuelle (francophones uniquement). |
| A5 — Belgique ≠ Néerlandais | 40% des Belges sont francophones. Le Maroc est majoritairement francophone en business. FR suffit pour 80% de la cible v0.1. |

### Débat Structuré

| Tour | Agent | Argument |
|------|-------|----------|
| 1 | UX Designer | "En Belgique, le marché B2B est 60% néerlandophone (Flandre). Sans NL, on ignore le plus gros morceau." |
| 2 | Architecte Système | "L'équipe parle français. Le support en néerlandais sera Google Translate. L'expérience sera mauvaise = churn." |
| 3 | Market Analyst | "Les néerlandophones belges parlent anglais en business. Proposons EN en v0.1, NL en v0.2." |
| 4 | Product Owner | "L'AR est plus critique : les dates arabes sont RTL, les nombres utilisent des caractères arabes. C'est un chantier à part." |
| 5 | Frontend Lead | "react-i18next + i18n Ally dans VS Code = quasi-transparent pour le dev. Les clés sont extraites automatiquement." |
| 6 | Backend Senior | "Les messages d'erreur API doivent être traduits. Ça touche Pydantic, FastAPI, exceptions custom. 2 semaines de travail." |
| 7 | CEO / Stratège | "Compromis : architecture i18n-ready en v0.1 (clés extractables, locale détectée), mais contenu FR uniquement. EN + NL en v0.2. AR en v0.3." |

### Arbitrage Plénière

**Décision** : **GO — Architecture i18n-ready en v0.1, activation progressive FR → EN → NL → AR**

| Langue | Activation | Justification |
|--------|-----------|-------------|
| **FR** | v0.1 (actif) | Marché principal (France + Belgique francophone + Maroc business). Équipe francophone. |
| **EN** | v0.2 (actif) | Belgique flamande (anglais business), internationalisation future, investisseurs anglophones. |
| **NL** | v0.3 (actif) | Flandre belge. Traductions professionnelles requises. |
| **AR** | v0.4 (actif) | Maroc (RTL, calendrier Hijri, nombres arabes). Chantier spécifique. |

| Paramètre | Valeur |
|-----------|--------|
| **Architecture v0.1** | Toutes les strings UI doivent utiliser react-i18next (useTranslation). Aucune string hardcodée. Locale détectée (navigator.language) avec fallback FR. |
| **Backend v0.1** | Messages d'erreur structurés (code + params) permettant la traduction côté client. Pas de traduction serveur en v0.1. |
| **Emails v0.1** | Templates MJML avec variables {{lang}}. v0.1 : template FR uniquement. v0.2 : templates EN ajoutés. |
| **Dates et nombres** | Intl.DateTimeFormat et Intl.NumberFormat utilisés partout. Devise en EUR pour FR/BE, MAD pour MA (v0.4). |
| **RTL (AR)** | Architecture prête (dir="rtl" conditionnel) mais non activée. Tests visuels AR en v0.3. |
| **Traductions** | FR : rédaction interne. EN : rédaction interne + relecture native. NL/AR : agence de traduction spécialisée (budget 5000€). |

### Action Résultante

| # | Action | Responsable | Deadline |
|---|--------|-------------|----------|
| F4-A1 | Configurer react-i18next avec extraction automatique des clés | Frontend Lead | S1 v0.1 |
| F4-A2 | Réécrire tous les composants existants avec useTranslation | Frontend Lead | S2-S3 v0.1 |
| F4-A3 | Structurer les messages d'erreur API (code + params) | Backend Senior | S2 v0.1 |
| F4-A4 | Créer les templates MJML avec support i18n | Frontend Lead | S2 v0.1 |
| F4-A5 | Traduire l'interface en EN (v0.2) | Product Owner + UX Designer | v0.2 |
| F4-A6 | Contrat agence traduction NL + AR | Market Analyst | v0.3 |
| F4-A7 | Tests visuels RTL pour AR | QA Lead | v0.4 |

---

## 4.6 F5 — Tests E2E Playwright (Qualité dit S1, Produit dit S2)

### Contexte
Le groupe Qualité souhaite des tests End-to-End avec Playwright dès le Sprint 1 pour garantir la stabilité des parcours critiques. Le groupe Produit argue que le frontend n'est pas assez stable avant le Sprint 2 pour justifier l'investissement E2E.

### Positions des Groupes

#### Qualité & Production (POUR E2E dès Sprint 1)
| Argument | Détail |
|----------|--------|
| Q1 — Régression early | Les premiers sprints sont les plus instables. Un test E2E qui casse = détection immédiate d'une régression. |
| Q2 — Parcours critiques | Login → Upload PDF → Parsing → ScoreCard. Si ce parcours casse, le produit est inutilisable. E2E = garde-fou. |
| Q3 — Coût de l'ajout tardif | Ajouter E2E en S2 = réécrire les tests car l'UI a changé. Coût doublé. |
| Q4 — CI/CD bloquant | E2E en CI = merge impossible si parcours critique cassé. Qualité garantie par construction. |
| Q5 — Playwright facile | Playwright + codegen = tests générés semi-automatiquement. 1 jour pour le parcours critique. |

#### Produit & Expérience (CONTRE E2E en S1 — propose S2)
| Argument | Détail |
|----------|--------|
| P1 — Instabilité UI | Le design system n'est pas figé en S1. Les composants changent de structure (className, aria-label, data-testid). Les tests E2E deviennent des cibles mouvantes. |
| P2 — Coût de maintenance | 1 test E2E qui casse par changement UI = 30 min de debug. En S1, 3-4 changements UI par sprint = 2h de maintenance E2E par sprint. |
| P3 — Couverture maigre | En S1, seuls login + upload existent. Le ScoreCard n'existe pas. Les tests E2E couvriraient 20% du parcours final. |
| P4 — Tests unitaires suffisants | En S1, les tests unitaires (Jest + React Testing Library) couvrent les composants individuellement. E2E est un luxe. |
| P5 — Ressources limitées | 1 QA pour 4 développeurs. E2E en S1 = 20% du temps QA sur du code qui va changer. |

### Débat Structuré

| Tour | Agent | Argument |
|------|-------|----------|
| 1 | QA Lead | "Sans E2E, une régression sur le login découvert en S3 = 2 sprints de code potentiellement corrompu." |
| 2 | UX Designer | "Mais en S1, le login change 3 fois (OAuth ajouté, MFA envisagé, design system mis à jour)." |
| 3 | DevOps QA | "Compromis : tests E2E 'smoke' uniquement en S1 (login + page d'accueil). Pas de parcours complet." |
| 4 | Frontend Lead | "Même le smoke test casse si on change la structure du formulaire. Et on va la changer." |
| 5 | QA Lead | "data-testid est stable. On peut changer les classes, les labels, mais pas les testid. Convention d'équipe : testid = contrat." |
| 6 | Product Owner | "Acceptable si : (1) data-testid obligatoire sur tous les éléments interactifs, (2) E2E limité à 2 tests en S1, (3) E2E complet en S2." |
| 7 | QA Lead | "2 tests E2E en S1 : (1) login réussi, (2) navigation Kanban visible. Le reste en S2." |

### Arbitrage Plénière

**Décision** : **GO — E2E limité en S1, E2E complet en S2**

| Phase | Scope E2E | Nombre de tests | Justification |
|-------|-----------|-----------------|---------------|
| **S1** | Smoke tests uniquement | 2 tests | Login réussi + Kanban visible. data-testid obligatoire sur tous les éléments interactifs. |
| **S2** | Parcours critique | 5 tests | Login → Onboarding → Upload PDF → Parsing visible → ScoreCard affichée. |
| **S3** | Parcours secondaires | 8 tests | Notifications, HIL, sélecteur BL, recherche, export. |
| **S4+** | Couverture complète | 15+ tests | Tous les parcours utilisateurs + tests de régression visuelle (Chromatic). |

| Paramètre | Valeur |
|-----------|--------|
| **Convention data-testid** | Tout élément interactif (bouton, input, lien, select) DOIT avoir un data-testid stable. Changement de testid = breaking change. |
| **Outil** | Playwright avec TypeScript. codegen pour le squelette, manuel pour les assertions. |
| **CI** | E2E en CI sur chaque PR (GitHub Actions). Timeout 5 minutes. headless: true. |
| **Environnement de test** | Docker Compose avec base de test seedée. Pas de mock d'API (tests d'intégration véritable). |
| **Budget maintenance** | 20% du temps QA = maintenance E2E. 80% = tests manuels exploratoires. |

### Action Résultante

| # | Action | Responsable | Deadline |
|---|--------|-------------|----------|
| F5-A1 | Configurer Playwright + CI E2E | DevOps QA | S1 |
| F5-A2 | Écrire les 2 smoke tests (login + Kanban) | QA Lead | S1 |
| F5-A3 | Documenter la convention data-testid | Frontend Lead | S1 |
| F5-A4 | Auditer data-testid sur tous les composants existants | Frontend Lead | S1 |
| F5-A5 | Écrire les 5 tests parcours critique | QA Lead | S2 |
| F5-A6 | Intégrer tests E2E comme gate de merge | DevOps QA | S2 |

---

## 4.7 F6 — Dashboard Éditeur : Tableau vs Graphiques (Produit dit TABLEAU, Business dit GRAPHIQUE)

### Contexte
Le groupe Produit propose un dashboard éditeur sous forme de tableau de données brut + 3 KPIs cards pour le support en v0.1. Le groupe Business (CEO) souhaite des graphiques visuels pour les présentations aux investisseurs et le pitch clients.

### Positions des Groupes

#### Produit & Expérience (POUR tableau brut en v0.1)
| Argument | Détail |
|----------|--------|
| P1 — Usage réel | Le support a besoin de données brutes (liste des dossiers, filtres, tri). Les graphiques sont décoratifs pour l'usage support. |
| P2 — Complexité technique | Graphiques = bibliothèque D3/Recharts + données agrégées + cache. Tableau = HTML natif + SQL direct. 1 jour vs 1 semaine. |
| P3 — Performance | 1000 dossiers en tableau paginé = instantané. 1000 dossiers en graphique temps réel = lourd + latence. |
| P4 — Priorité utilisateur | Les 3 KPIs (taux réponse, délai moyen, taux succès) suffisent pour une vue d'ensemble. Le reste = filtrage dans le tableau. |
| P5 — Widgets en v0.3 | Les graphiques arrivent en v0.3 avec les analytics avancées. Pas besoin de rush. |

#### Business & Stratégie (POUR graphiques dès v0.1)
| Argument | Détail |
|----------|--------|
| B1 — Pitch investisseurs | Les investisseurs demandent des dashboards "sexy". Un tableau Excel-like = produit amateur. |
| B2 — Démonstration client | En démo, les graphiques font "wow". Le tableau fait "bof". La perception prime sur la fonction. |
| B3 — Différenciation concurrente | Les concurrents ont des dashboards graphiques. Si on n'en a pas, on paraît en retard. |
| B4 — KPIs visuels | 3 cards textuelles = limité. Une courbe de conversion au fil du temps = storytelling puissant. |
| B5 — Coût marginal | Recharts + données déjà disponibles = 2 jours de développement. Pas un chantier. |

### Débat Structuré

| Tour | Agent | Argument |
|------|-------|----------|
| 1 | CEO / Stratège | "J'ai un pitch avec 3 VC en semaine 6. Le dashboard est la première chose qu'ils voient après le login." |
| 2 | Product Owner | "Mais le dashboard en v0.1 est pour le SUPPORT, pas pour les VC. Les VC ne se connectent pas au produit." |
| 3 | Revenue Officer | "Les early-birds sont des utilisateurs réels. Ils voient le dashboard. Un tableau = impression beta. Un graphique = impression mature." |
| 4 | UX Designer | "Un graphique mal fait (pas assez de données, pas assez d'historique) = plus négatif qu'un tableau clair." |
| 5 | CEO / Stratège | "Proposons 2 dashboards : (1) Support = tableau brut, (2) Executive = 3 graphiques (courbe d'activité, répartition par statut, radar compétences)." |
| 6 | Frontend Lead | "2 dashboards = 2x le travail. Compromis : 1 dashboard avec toggle 'Vue Support / Vue Executive'. Même données, présentation différente." |
| 7 | Product Owner | "Acceptable si la Vue Executive est 3 graphiques simples (line chart, pie chart, bar chart) avec données des 30 derniers jours. Pas de temps réel." |

### Arbitrage Plénière

**Décision** : **GO — Dashboard hybride avec toggle "Vue Support / Vue Executive"**

| Vue | Description | Audience | Priorité |
|-----|-------------|----------|----------|
| **Vue Support** (par défaut) | Tableau de données brut (dossiers, filtres, tri, recherche) + 3 KPIs cards. | Support, utilisateurs opérationnels | v0.1 |
| **Vue Executive** (toggle) | 3 graphiques simples : (1) Courbe d'activité (dossiers/mois), (2) Répartition par statut (camembert), (3) Radar des domaines d'AO. | CEO, investisseurs, managers | v0.1 |

| Paramètre | Valeur |
|-----------|--------|
| **Bibliothèque graphique** | Recharts (React). Simple, léger, responsive. Pas de D3 custom. |
| **Données** | Agrégation PostgreSQL (GROUP BY date_trunc). Cache 5 minutes. Pas de temps réel. |
| **Historique** | 30 derniers jours minimum. 90 jours en v0.3. 12 mois en v0.5. |
| **Toggle** | Switch dans le header du dashboard. Préférence sauvegardée (localStorage). |
| **Export** | Vue Exportable en PNG (pour les présentations) en v0.3. |
| **Responsive** | Graphiques adaptatifs (Recharts ResponsiveContainer). Minimum 320px de large. |

### Action Résultante

| # | Action | Responsable | Deadline |
|---|--------|-------------|----------|
| F6-A1 | Implémenter la Vue Support (tableau + KPIs) | Frontend Lead | S3 v0.1 |
| F6-A2 | Implémenter la Vue Executive (3 graphiques Recharts) | Frontend Lead | S4 v0.1 |
| F6-A3 | Créer le toggle Vue Support / Vue Executive | Frontend Lead | S4 v0.1 |
| F6-A4 | Ajouter les requêtes d'agrégation PostgreSQL | Backend Senior | S3 v0.1 |
| F6-A5 | Tests E2E du toggle et des 2 vues | QA Lead | S4 v0.1 |

---

## 4.8 Synthèse des Arbitrages

| Friction | Groupe A | Groupe B | Arbitrage | Version |
|----------|----------|----------|-----------|---------|
| F1 — Split modèles | Architecture (GO v0.2) | Qualité (DIFFERE v0.3) | GO v0.2, 1 domaine par sprint, QA valide | v0.2 |
| F2 — Early-bird 49€ | Business (GO, 200 places) | Produit (NO-GO, 99€) | GO 49€, **100 places**, onboarding premium, code promo caché | v0.1 |
| F3 — S-MVP sécurité | Qualité (Obligatoire beta) | Architecture (v0.2 impossible) | S-MVP Light beta privée (100 invités), S-MVP Complet beta publique | v0.2 / v0.3 |
| F4 — i18n v0.1 | Produit (GO, 4 langues) | Architecture (FR uniquement) | Architecture i18n-ready v0.1, activation FR v0.1, EN v0.2, NL v0.3, AR v0.4 | v0.1 à v0.4 |
| F5 — E2E Playwright | Qualité (S1 complet) | Produit (S2 stable) | Smoke E2E en S1 (2 tests), complet en S2 (5 tests) | S1 / S2 |
| F6 — Dashboard graphique | Business (GO graphiques) | Produit (tableau brut) | Toggle Vue Support (tableau) / Vue Executive (graphiques) | v0.1 |

---

**Conclusion Partie IV** : Les 6 frictions ont fait l'objet d'un débat structuré et ont abouti à des compromis viables. Aucune friction n'est restée en suspens. Les arbitrages sont clairs, datés, et attribués.

---


# PARTIE V — PLAN D'ACTION CONSOLIDÉ

---

## 5.1 Présentation

Le plan d'action consolidé regroupe l'ensemble des actions issues :
- Des décisions GO directes (Partie II)
- Des arbitrages de frictions (Partie IV)
- Des actions bloquantes identifiées par le comité exécutif

Les actions sont organisées en **3 phases** :
1. **Actions bloquant le lancement** : à réaliser AVANT le démarrage du Sprint 0
2. **Actions Sprint 0** : exécutées pendant les 4 semaines du Sprint 0 (v0.1)
3. **Actions post-Sprint 0** : exécutées après le Sprint 0, jusqu'à la beta publique

---

## 5.2 Actions Bloquant le Lancement (à faire AVANT Sprint 0)

Ces actions sont des prérequis absolus. Le Sprint 0 ne démarre pas tant que ces actions ne sont pas validées.

| # | Action | Responsable | Deadline | Critère de validation |
|---|--------|-------------|----------|----------------------|
| BL-01 | Créer les repositories GitHub : `taka-os` (AGPL) et `taka-platform` (propriétaire) avec CI/GitHub Actions | DevOps Engineer | J+2 | Repos accessibles, CI verte sur hello-world |
| BL-02 | Configurer l'environnement de développement Docker Compose (PG 16, PGAdmin, Redis optionnel, MinIO S3 local) | DevOps Engineer | J+3 | `docker-compose up` fonctionnel en <60s |
| BL-03 | Mettre en place le linter/formatter (Ruff, Black, Prettier, ESLint) avec hooks pre-commit | DevOps Engineer | J+3 | Pre-commit bloquant sur toute violation |
| BL-04 | Définir la convention de commit (Conventional Commits) et le workflow Git (trunk-based, PR obligatoire, 2 reviewers) | Architecte Système | J+2 | Document publié + team briefing |
| BL-05 | Créer le MCD (Modèle Conceptuel de Données) v0.1 avec les 9 domaines identifiés | Architecte Data | J+5 | MCD validé par tous les leads |
| BL-06 | Rédiger le cahier des charges fonctionnel v0.1 (user stories, critères d'acceptation) | Product Owner | J+5 | 15 user stories priorisées |
| BL-07 | Établir la charte graphique et le design system Figma v0.1 (couleurs, typographie, composants de base) | UX Designer | J+5 | 10 composants Figma publiés |
| BL-08 | Configurer le projet Docusaurus (doc utilisateur) et MkDocs (doc technique) vides | Technical Writer | J+3 | Sites statiques déployés sur GitHub Pages |
| BL-09 | Obtenir le SIRET de l'entreprise éditrice et ouvrir le compte bancaire pro | CEO / Stratège | J+5 | RIB disponible pour Stripe |
| BL-10 | Configurer le compte Stripe (paiement) en mode test | Revenue Officer | J+5 | Paiement test réussi (carte 4242 4242 4242 4242) |
| BL-11 | Acheter le nom de domaine `taka-os.io` + certificat SSL wildcard | CEO / Stratège | J+2 | DNS configuré, HTTPS valide |
| BL-12 | Rédiger les Conditions Générales d'Utilisation v0.1 (CGU) + Politique de Confidentialité | Legal & Compliance | J+7 | Document relu par avocat externe |
| BL-13 | Configurer le compte Mistral AI (clé API) et OpenRouter (clé API fallback) | AI Engineer | J+2 | Appel API test réussi, latence <2s |
| BL-14 | Créer l'instance Scaleway/OVH de production (PostgreSQL 16, 2 vCPU, 4GB RAM minimum) | DevOps Engineer | J+3 | Instance accessible, PG 16 installé |
| BL-15 | Configurer le monitoring de base (Prometheus + Grafana, dashboards infra) | DevOps Engineer | J+5 | Dashboards PG, API, container visibles |
| BL-16 | Valider la stack technique complète (hello-world end-to-end : React → FastAPI → PostgreSQL → réponse) | Backend Senior + Frontend Lead | J+5 | Requête `/health` fonctionnelle |
| BL-17 | Plan de split des modèles (9 domaines, ordre, dépendances) — issu F1 | Architecte Data | J+3 | Document technique approuvé |
| BL-18 | Créer le registre de transparence (template vide) — issu C9 | Legal & Compliance | J+5 | Page /transparence accessible |
| BL-19 | Établir le budget prévisionnel Sprint 0 (infrastructure, outils, traductions, juridique) | CEO / Stratège | J+3 | Budget validé, cash-flow ok |
| BL-20 | Valider le plan de réunion de suivi (daily 15min, review hebdo, rétro fin de sprint) | Product Owner | J+2 | Calendrier partagé, invitations envoyées |

---

## 5.3 Actions Sprint 0 (v0.1 — Semaines 1 à 4)

Le Sprint 0 a pour objectif de livrer la v0.1 : connexion, upload PDF basique, parsing basique, ScoreCard basique, Kanban basique.

### Semaine 1 — Fondations

| # | Action | Responsable | Story Points | Critère d'acceptation |
|---|--------|-------------|-------------|----------------------|
| S0-S1-01 | Initialiser le projet FastAPI (structure, config, healthcheck) | Backend Senior | 3 | `GET /health` retourne 200 |
| S0-S1-02 | Initialiser le projet React (Vite, TypeScript, Tailwind, react-i18next) | Frontend Lead | 3 | `npm run dev` fonctionnel |
| S0-S1-03 | Créer la base de données PostgreSQL (schema v0.1 : user, tenant, bl, dossier, document) | DBA | 5 | Migrations Alembic passent |
| S0-S1-04 | Authentification JWT (inscription, connexion, refresh token) | Backend Senior | 5 | JWT valide 24h, refresh 7j |
| S0-S1-05 | Page de login (formulaire, validation, erreurs) | Frontend Lead | 3 | Connexion réussie → redirect Kanban |
| S0-S1-06 | i18n-ready : extraire toutes les clés de traduction FR | Frontend Lead | 3 | Aucune string hardcodée |
| S0-S1-07 | Tests unitaires backend : auth + user (coverage >80%) | Backend Senior | 3 | pytest --cov >80% |
| S0-S1-08 | Tests unitaires frontend : composants login (Jest + RTL) | Frontend Lead | 3 | `npm test` passe |
| S0-S1-09 | CI/CD GitHub Actions : lint + test + build | DevOps Engineer | 5 | Pipeline verte sur chaque PR |
| S0-S1-10 | Déployer v0.1-alpha sur l'instance de staging | DevOps Engineer | 2 | URL staging accessible |

### Semaine 2 — Upload et Parsing

| # | Action | Responsable | Story Points | Critère d'acceptation |
|---|--------|-------------|-------------|----------------------|
| S0-S2-01 | Endpoint API : upload PDF (multipart, validation taille <10MB) | Backend Senior | 3 | Upload réussi, fichier stocké S3 |
| S0-S2-02 | Intégration parsing PDF (PyPDF2 / pdfplumber) : extraction texte brut | ML Engineer | 5 | Texte extrait avec >90% de fiabilité sur corpus test |
| S0-S2-03 | Classification parsing (A/B/C/D) avec score de confiance | ML Engineer | 5 | Classification correcte sur 20 PDFs test |
| S0-S2-04 | Composant Upload (drag & drop, barre de progression, feedback) | Frontend Lead | 3 | Upload 5MB <3s, feedback visuel |
| S0-S2-05 | Tableau Kanban basique (3 colonnes : À analyser / En cours / Traité) | Frontend Lead | 5 | Dossier créé visible dans Kanban |
| S0-S2-06 | EventBus asyncio (table events PostgreSQL, pub/sub basique) | Backend Senior | 5 | Event émis et consommé en <100ms |
| S0-S2-07 | Tests intégration : upload → parsing → event | QA Lead | 5 | Parcours complet testé |
| S0-S2-08 | E2E smoke tests (login + Kanban visible) — issu F5 | QA Lead | 3 | Playwright passe en CI |
| S0-S2-09 | Doc utilisateur : guide "Premier upload" | Technical Writer | 2 | Publié sur Docusaurus |
| S0-S2-10 | Badge "IA utilisée" sur le parsing — issu C9 | Frontend Lead | 1 | Badge visible sous chaque résultat |

### Semaine 3 — ScoreCard et LLM

| # | Action | Responsable | Story Points | Critère d'acceptation |
|---|--------|-------------|-------------|----------------------|
| S0-S3-01 | Intégration Mistral API (prompt de scoring, gestion erreur) | AI Engineer | 5 | Réponse LLM <3s, format JSON |
| S0-S3-02 | Fallback OpenRouter en cas d'échec Mistral | AI Engineer | 3 | Fallback automatique <5s |
| S0-S3-03 | Système de scoring YAML V2 (moteur de règles déclaratif) | ML Engineer | 8 | Règles YAML exécutées, score calculé |
| S0-S3-04 | ScoreCard UI : verdict condensé (2 phrases) + détail 5D dépliable | Frontend Lead | 5 | Score affiché, détail dépliable |
| S0-S3-05 | Circuit Breaker (6 circuits indépendants, Prometheus metrics) | Backend Senior | 5 | CB ouvre après 3 échecs, métriques visibles |
| S0-S3-06 | Notifications in-app (badge, centre de notifications) | Frontend Lead | 3 | Notification reçue après parsing terminé |
| S0-S3-07 | Mémoire TTL (365j) pour les souvenirs IA | AI Engineer | 3 | Données stockées avec expiration |
| S0-S3-08 | KPIs cards dashboard (taux réponse, délai moyen, taux succès) | Frontend Lead | 3 | 3 cards avec données réelles |
| S0-S3-09 | Chiffrement application (Fernet) pour colonnes sensibles — issu F3 | Backend Senior | 3 | Colonnes chiffrées, déchiffrement OK |
| S0-S3-10 | Backups pg_dump horaires + S3 — issu F3 | DevOps Engineer | 3 | Backup quotidien testé, restauration OK |
| S0-S3-11 | Tour guidé minimal 3 étapes — issu P-Q8 | Frontend Lead | 3 | Tour visible première connexion |
| S0-S3-12 | Wizard onboarding optimisé (SIRET pré-rempli, skip étapes 4-5) | Frontend Lead | 5 | Parcours <2 minutes |

### Semaine 4 — Polish, Sécurité, Documentation

| # | Action | Responsable | Story Points | Critère d'acceptation |
|---|--------|-------------|-------------|----------------------|
| S0-S4-01 | Rate limiting Nginx (100 req/min par IP) | DevOps Engineer | 2 | 101ème req bloquée |
| S0-S4-02 | CSP headers, X-Frame-Options, HSTS | DevOps Engineer | 2 | SecurityHeaders.com note A |
| S0-S4-03 | Validation OWASP Top 10 (revue manuelle) — S-MVP Light | Security Engineer | 5 | 10 vulnérabilités vérifiées, aucune critique |
| S0-S4-04 | Documentation technique API (Swagger auto-généré) | Technical Writer | 2 | Swagger UI accessible |
| S0-S4-05 | Documentation utilisateur complète v0.1 | Technical Writer | 3 | 10 guides publiés |
| S0-S4-06 | Freeze documentation 48h avant release | Technical Writer | 1 | Doc synchronisée avec code |
| S0-S4-07 | Tests E2E parcours critique (5 tests) — issu F5 | QA Lead | 5 | Playwright passe en CI |
| S0-S4-08 | Tests de charge (k6) : 100 users simultanés, latence <500ms | DevOps QA | 3 | Résultats k6 publiés |
| S0-S4-09 | Bug bash interne (équipe + 5 testeurs externes) | Product Owner | 2 | 20+ bugs rapportés et triés |
| S0-S4-10 | Release v0.1 taguée + notes de release | DevOps Engineer | 1 | GitHub release publiée |
| S0-S4-11 | Déploiement production v0.1 | DevOps Engineer | 2 | URL production accessible |
| S0-S4-12 | Annonce communauté OS (Discord, Twitter, LinkedIn) | Community Manager | 1 | Post publié, 50+ réactions |

---

## 5.4 Actions Post-Sprint 0 (v0.2 à Beta Publique)

| # | Action | Responsable | Deadline (version) | Source |
|---|--------|-------------|-------------------|--------|
| PS-01 | Split modèles : domaine "user" | Backend Senior | v0.2 | F1 |
| PS-02 | Split modèles : domaines "dossier" + "document" | Backend Senior | v0.2 | F1 |
| PS-03 | HIL : modal semi-bloquante (validation critique) | Frontend Lead | v0.2 | P-Q5 |
| PS-04 | HIL : sidebar asynchrone (info complémentaire) | Frontend Lead | v0.2 | P-Q5 |
| PS-05 | Mémoire TTL : oubli probabiliste (décroissance) | AI Engineer | v0.4 | A-Q7 |
| PS-06 | EventBus LISTEN/NOTIFY PostgreSQL | Backend Senior | v0.2 | A-Q1 |
| PS-07 | Vue Planning (timeline Gantt) toggle Kanban | Frontend Lead | v0.2 | P-Q1 |
| PS-08 | Mode sombre | Frontend Lead | v0.2 | P-Q9 |
| PS-09 | Email digest quotidien | Backend Senior | v0.2 | P-Q7 |
| PS-10 | Email immédiat alertes critiques | Backend Senior | v0.2 | P-Q7 |
| PS-11 | S-MVP Complet (OWASP + AES-256 + PITR + MFA) | Security Engineer + DevOps | v0.3 | F3 |
| PS-12 | Avis juridique AI Act spécialisé | Legal & Compliance | v0.3 | Q-Q4 |
| PS-13 | Registre de transparence complet | Legal & Compliance | v0.2 | B-Q8 |
| PS-14 | Multi-région backups | DevOps Engineer | v0.5 | Q-Q5 |
| PS-15 | Tests chaos circuit breaker (toxiproxy) | DevOps QA | v0.2 | Q-Q7 |
| PS-16 | Export CSV | Backend Senior | v0.2 | P-Q12 |
| PS-17 | Search global full-text PostgreSQL | Backend Senior | v0.2 | P-Q11 |
| PS-18 | i18n EN active | Frontend Lead | v0.2 | F4 |
| PS-19 | i18n NL active + traductions agence | Market Analyst | v0.3 | F4 |
| PS-20 | i18n AR active + tests RTL | QA Lead | v0.4 | F4 |
| PS-21 | RGAA niveau AA parcours critique | Frontend Lead | v0.5 | Q-Q6 |
| PS-22 | React 19 migration | Frontend Lead | v0.5 | A-Q6 |
| PS-23 | NATS EventBus | DevOps Engineer | v0.5 | A-Q1 |
| PS-24 | Partitionnement pgvector (>1M vecteurs) | DBA | v0.3 | A-Q2 |
| PS-25 | API Gateway (Kong/Traefik) | DevOps Engineer | v0.4 | A-Q11 |
| PS-26 | Message Queue dédiée (Celery + Redis) | Backend Senior | v0.3 | A-Q12 |
| PS-27 | PWA minimal | Frontend Lead | v0.4 | P-Q10 |
| PS-28 | Export PDF stylisé | Frontend Lead | v0.4 | P-Q12 |
| PS-29 | Tour guidé complet 8 étapes | Frontend Lead | v0.3 | P-Q8 |
| PS-30 | Plan Starter gratuit (3 dossiers/mois) | Revenue Officer | v0.3 | B-Q2 |
| PS-31 | Programme Enterprise Early Access | CEO / Stratège | v0.5 | B-Q3 |
| PS-32 | LinkedIn Ads campagne 1 | Market Analyst | v0.2 | B-Q5 |
| PS-33 | SEO technique (blog, contenu parsing) | Community Manager | v0.2 | B-Q5 |
| PS-34 | Bug bounty program | Security Engineer | v0.5 | Q-Q3 |
| PS-35 | AI Act Niveau 2 (documentation + supervision) | Legal & Compliance | v0.5 | Q-Q4 |
| PS-36 | Audit RGAA externe | Compliance Officer | v0.7 | Q-Q6 |
| PS-37 | Dashboard Vue Executive (graphiques) | Frontend Lead | v0.1 (S4) | F6 |
| PS-38 | Tests E2E complets (15+ tests) | QA Lead | v0.3 | F5 |
| PS-39 | Marque "TAKA" déposée | Legal & Compliance | v0.2 | B-Q1 |
| PS-40 | CLA (Contributor License Agreement) | Legal & Compliance | v0.2 | B-Q1 |

---

## 5.5 Calendrier Macro

| Phase | Période | Livrable | Jalons |
|-------|---------|----------|--------|
| **Pré-lancement** | J à J+7 | Repos, stack, docs, legal | BL-01 à BL-20 validés |
| **Sprint 0** | S1 à S4 (4 semaines) | v0.1 Alpha interne | Connexion, upload, parsing basique, ScoreCard, Kanban |
| **v0.2** | S5 à S8 (4 semaines) | Beta privée (100 early-bird) | HIL, split modèles, i18n EN, S-MVP Light, CB, docs |
| **v0.3** | S9 à S12 (4 semaines) | Beta publique | S-MVP Complet, i18n NL, export, search, React 19 prep |
| **v0.4** | S13 à S16 (4 semaines) | General Availability | PWA, i18n AR, API Gateway, thème personnalisé, NL/AR |
| **v0.5** | S17 à S20 (4 semaines) | Enterprise Ready | SSO, MFA, audit logs, AI Act Niv.2, RGAA AA, multi-région |
| **v1.0** | S21 à S24 (4 semaines) | Version majeure | Stabilisation, performance, audit externe, SOC 2 prep |
| **v1.5** | S25 à S36 (12 semaines) | Maturité | AI Act Niv.3, international, partenariats, scaling |

---

## 5.6 Budget Consolidé Sprint 0

| Poste | Montant | Justification |
|-------|---------|-------------|
| Infrastructure cloud (Scaleway) | 200€/mois | PG 16, 2 vCPU, 4GB, 50GB SSD |
| Outils SaaS (GitHub, Figma, Notion) | 150€/mois | GitHub Teams, Figma Pro, Notion |
| LLM API (Mistral + OpenRouter) | 300€/mois | ~50k tokens/jour en test |
| Juridique (CGU, CLA, marque) | 2000€ (ponctuel) | Avocat IT + INPI marque |
| Traductions EN (v0.2) | 1500€ (ponctuel) | Agence native anglais |
| Marketing pré-lancement | 500€/mois | Contenu, réseaux, annonces |
| **Total Sprint 0** | **~5000€ + 1150€/mois** | — |

---

**Conclusion Partie V** : 20 actions bloquantes, 43 actions Sprint 0, 40 actions post-Sprint 0. Budget Sprint 0 : ~10 000€. Planification sur 24 semaines jusqu'à v1.0.

---


# PARTIE VI — VERDICT FINAL DE LA RÉUNION

---

## 6.1 Décision Binaire

**VERDICT : GO — Le lancement du développement est APPROUVÉ.**

---

## 6.2 Justification du Verdict GO

La réunion plénière KIMI-TAKA-SWARM, réunissant 30 agents sur 11 pôles d'expertise, a produit une synthèse exhaustive des débats des 4 groupes thématiques. Les conditions suivantes justifient le verdict **GO** :

### Condition 1 — Architecture validée et cohérente
L'architecture technique a fait l'objet de 12 décisions validées (GO ou DIFFERE avec critères). Le socle PostgreSQL + Python 3.12 + FastAPI + React 18 est robuste, éprouvé, et adapté au périmètre MVP. L'absence de Redis et l'utilisation de PostgreSQL comme source de vérité unique réduisent la complexité opérationnelle de 40%.

### Condition 2 — Frictions arbitrées avec compromis viables
Les 6 frictions transverses identifiées ont toutes fait l'objet d'un arbitrage clair avec compromis acceptable :
- F1 (Split modèles) : 1 domaine par sprint, QA valide
- F2 (Early-bird) : 49€/100 places/onboarding premium
- F3 (Sécurité) : S-MVP Light pour beta privée, Complet pour publique
- F4 (i18n) : Architecture ready v0.1, activation progressive
- F5 (E2E) : Smoke S1, complet S2
- F6 (Dashboard) : Toggle Support/Executive

Aucune friction n'est restée en suspens. Aucun blocage irréductible.

### Condition 3 — Plan d'action exécutable
20 actions bloquantes avant Sprint 0, 43 actions pendant Sprint 0, 40 actions post-Sprint 0. Chaque action a un responsable identifié et une deadline précise. Le budget Sprint 0 (~10 000€) est maîtrisé et financé.

### Condition 4 — Qualité non négociable mais progressive
La stratégie de sécurité et de conformité est graduée : v0.1 (base), beta privée (S-MVP Light), beta publique (S-MVP Complet), v0.5 (durcie). Cette approche évite le blocage par la sécurité tout en maintenant une trajectoire de conformité légale.

### Condition 5 — Business model validé
Le pricing (99€/mois, early-bird 49€/100 places), la cible (PME 5-250 salariés), les 3 pays (FR/BE/MA), et le modèle Open Core 60/40 constituent un business model cohérent avec un chemin vers la rentabilité à 85 clients (M6).

### Condition 6 — 15 convergences transverses
Les 15 points de convergence montrent un alignement profond des 4 groupes sur les fondations du projet. Ces accords forment un socle stable sur lequel construire.

---

## 6.3 Points de Vigilance (Non Bloquants)

Le verdict GO est assorti des points de vigilance suivants, qui seront surveillés par le comité de pilotage :

| # | Point de vigilance | Groupe responsable | Fréquence de suivi |
|---|---------------------|--------------------|-------------------|
| V1 | **Rythme du split des modèles** : risque de retard si 1 domaine/sprint n'est pas tenu | Architecture + Qualité | Weekly |
| V2 | **Qualité des traductions EN/NL/AR** : traductions automatiques = risque réputation | Produit + Business | Bi-mensuel |
| V3 | **Consommation API LLM** : Mistral + OpenRouter peuvent coûter plus que prévu (300€/mois) | AI Engineer + Revenue | Weekly |
| V4 | **S-MVP Light respecté** : chiffrement Fernet + backups horaires doivent être validés avant beta privée | Qualité | A chaque milestone |
| V5 | **Taux de conversion early-bird** : objectif 3-5%. Si <2%, réviser le pricing ou le ciblage | Business | Mensuel |
| V6 | **Stabilité frontend v0.1** : React 18 + versions pinnées = pas de mise à jour de sécurité automatique. Veille manuelle obligatoire | Architecture | Hebdomadaire |
| V7 | **Coverage tests probabilistes** : objectif 85% confiance. Si <75%, réviser les golden datasets | Qualité | Par sprint |
| V8 | **Docker Compose scaling** : si >500 req/min avant v0.6, anticiper la migration K8s | Architecture + DevOps | Mensuel |
| V9 | **Support client multi-lingue** : NL et AR non supportés en v0.1-v0.2. Risque de churn en Belgique flamande | Business + Produit | Mensuel |
| V10 | **Circuit Breaker tuning** : 3 échecs/30s peut être trop agressif ou trop laxiste selon les providers. Ajustement nécessaire en v0.2 | Architecture + Qualité | Par sprint |

---

## 6.4 Points Bloquants Hypothétiques (Mitigation)

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Mistral API indisponible >24h | Moyen | Élevé | Fallback OpenRouter + mode dégradé (scoring YAML sans LLM) |
| Fuite de données en beta privée | Faible | Critique | Chiffrement Fernet + beta vraiment privée (invitation manuelle) + CGU restrictives |
| Retard S-MVP Complet (v0.3) | Moyen | Élevé | S-MVP Light + bug bounty + audit interne = buffer de confiance |
| Consommation LLM >1000€/mois | Moyen | Moyen | Cache des réponses LLM (Redis LRU) + scoring YAML prioritaire |
| Concurrent lance produit similaire | Faible | Élevé | Communauté OS = barrière à l'entrée + différenciation agentic |
| Difficulté recrutement dev NL/AR | Moyen | Faible | Traductions agence + support EN intermédiaire |

---

## 6.5 Prochaines Réunions Planifiées

| Réunion | Date | Objectif | Participants |
|---------|------|----------|------------|
| Daily Standup | Chaque jour (15min) | Blocages, synchronisation | Équipe core (7 agents tech) |
| Review Hebdo | Vendredi 16h (1h) | Démonstration, feedback | Tous les agents techniques + PO |
| Rétro Sprint 0 | Fin S4 (2h) | Apprentissages, ajustements | Tous les agents |
| Comité de Pilotage | M2, M4, M6 (2h) | Stratégie, budget, arbitrages | CEO, PO, Architecte, Revenue, QA Lead |
| Réunion Plénière v0.2 | Début v0.2 (4h) | Validation beta privée, ajustements | 30 agents, 11 pôles |
| Réunion Plénière v0.3 | Début v0.3 (4h) | Validation beta publique, S-MVP Complet | 30 agents, 11 pôles |

---

## 6.6 Signatures et Validation

Ce procès-verbal de réunion plénière a été validé par les représentants des 4 groupes thématiques :

| Groupe | Représentant | Validation | Date |
|--------|-------------|------------|------|
| Architecture & Technique | Architecte Système (Agent #1) | ✅ GO | Session plénière |
| Produit & Expérience | Product Owner (Agent #8) | ✅ GO | Session plénière |
| Business & Stratégie | CEO / Stratège (Agent #12) | ✅ GO | Session plénière |
| Qualité & Production | QA Lead (Agent #17) | ✅ GO | Session plénière |

**Décision finale du Comité Exécutif** :

> **GO** pour le lancement du Sprint 0 du projet TAKA OS. Les conditions sont réunies. Les risques sont identifiés et mitigés. Le plan d'action est exécutable. Les arbitrages sont clairs. Le projet est déclaré **OUVERT**.

---

# ANNEXES

---

## Annexe A — Glossaire des Acronymes

| Acronyme | Signification |
|----------|---------------|
| AO | Appel d'Offres |
| BL | Business Line |
| CB | Circuit Breaker |
| CGU | Conditions Générales d'Utilisation |
| CI/CD | Intégration Continue / Déploiement Continu |
| CLA | Contributor License Agreement |
| CSM | Customer Success Manager |
| E2E | End-to-End (tests) |
| HIL | Human-in-the-Loop |
| HNSW | Hierarchical Navigable Small World (index pgvector) |
| HSTS | HTTP Strict Transport Security |
| JWT | JSON Web Token |
| KPI | Key Performance Indicator |
| LLM | Large Language Model |
| MFA | Multi-Factor Authentication |
| MJML | Mailjet Markup Language (emails responsive) |
| MRR | Monthly Recurring Revenue |
| NL | Néerlandais |
| NDA | Non-Disclosure Agreement |
| OS | Open Source |
| PG | PostgreSQL |
| PITR | Point-in-Time Recovery |
| PWA | Progressive Web App |
| QA | Quality Assurance |
| RGAA | Référentiel Général d'Amélioration de l'Accessibilité |
| RGPD | Règlement Général sur la Protection des Données |
| RLS | Row-Level Security |
| RPO | Recovery Point Objective |
| RTO | Recovery Time Objective |
| RTL | Right-to-Left (pour l'Arabe) |
| SaaS | Software as a Service |
| SEO | Search Engine Optimization |
| SLA | Service Level Agreement |
| S-MVP | Security Minimum Viable Product |
| SOC 2 | Service Organization Control 2 |
| SRE | Site Reliability Engineering |
| SSE-KMS | Server-Side Encryption with Key Management Service |
| SSR | Server-Side Rendering |
| TTL | Time-To-Live |
| VC | Venture Capital |
| WAL | Write-Ahead Log (PostgreSQL) |
| YAML | YAML Ain't Markup Language |

---

## Annexe B — Références des Décisions Sources

| Groupe | Document source | Agent rapporteur | Volume |
|--------|-----------------|-------------------|--------|
| Architecture & Technique | `debat_architecture_technique.md` | Architecte Système | 860 lignes |
| Produit & Expérience | `debat_produit_experience.md` | Product Owner | 932 lignes |
| Business & Stratégie | `debat_business_strategie.md` | CEO / Stratège | 830 lignes |
| Qualité & Production | `debat_qualite_production.md` | QA Lead | 1 236 lignes |
| **Total débats** | **4 documents** | **4 agents** | **3 858 lignes** |

---

## Annexe C — Tableau de Bord de Suivi des Décisions

| ID | Décision | Statut | Dernière mise à jour | Prochaine revue |
|----|----------|--------|---------------------|-----------------|
| A-Q1 | EventBus asyncio | GO | Session plénière | Review hebdo S1 |
| A-Q2 | pgvector HNSW | GO | Session plénière | Review hebdo S1 |
| A-Q3 | Split modèles | GO v0.2 | Session plénière | Weekly F1 |
| A-Q4 | Multi-provider LLM | GO | Session plénière | Review hebdo S1 |
| A-Q5 | Docker Compose v0.6 | GO | Session plénière | Mensuel scaling |
| A-Q6 | React 19 v0.5 | GO | Session plénière | Mensuel veille |
| A-Q7 | Mémoire TTL 365j | GO | Session plénière | Review hebdo S3 |
| A-Q8 | Circuit Breaker 3/30/60 | GO | Session plénière | Par sprint |
| P-Q1 | Vue Kanban | GO | Session plénière | Review hebdo S1 |
| P-Q2 | ScoreCard 2 niveaux | GO | Session plénière | Review hebdo S2 |
| P-Q3 | Onboarding wizard | GO | Session plénière | Review hebdo S2 |
| P-Q4 | Sélecteur BL | GO | Session plénière | Review hebdo S1 |
| P-Q5 | HIL modal/sidebar | GO v0.2 | Session plénière | Review hebdo S5 |
| P-Q6 | Dashboard tableau + KPIs | GO | Session plénière | Review hebdo S3 |
| P-Q7 | Notifications hybrides | GO | Session plénière | Review hebdo S2 |
| P-Q8 | Tour guidé 3 étapes | GO | Session plénière | Review hebdo S3 |
| B-Q1 | Open Core 60/40 | GO | Session plénière | Mensuel |
| B-Q2 | Pricing 99€/49€ | GO | Session plénière | Mensuel conversion |
| B-Q3 | Cible PME 5-250 | GO | Session plénière | Mensuel |
| B-Q4 | Pays FR/BE/MA | GO | Session plénière | Mensuel |
| B-Q5 | Acquisition SEO/Ads | GO | Session plénière | Mensuel |
| B-Q6 | Différenciation +20% | GO | Session plénière | Mensuel |
| B-Q7 | Rentabilité 85 clients | GO | Session plénière | Mensuel |
| B-Q8 | Badge IA + registre | GO v0.2 | Session plénière | Review hebdo S4 |
| Q-Q1 | Tests bimodaux 90/85 | GO | Session plénière | Par sprint |
| Q-Q2 | Parsing classification | GO | Session plénière | Par sprint |
| Q-Q3 | S-MVP beta | GO | Session plénière | A chaque milestone |
| Q-Q4 | AI Act niveaux | GO | Session plénière | Mensuel juridique |
| Q-Q5 | Backups SSE-KMS + PITR | GO | Session plénière | Mensuel |
| Q-Q6 | RGAA AA v0.5 | GO | Session plénière | Mensuel |
| Q-Q7 | CB tests 3 niveaux | GO | Session plénière | Par sprint |
| Q-Q8 | Doc-as-code 48h | GO | Session plénière | Par release |

---

## Annexe D — Contacts et Escalade

| Niveau | Contact | Rôle | Cas d'escalade |
|--------|---------|------|---------------|
| Niveau 1 | Product Owner | Coordination quotidienne | Blocages inter-équipes, priorisation |
| Niveau 2 | Architecte Système | Arbitrage technique | Décisions architecture, stack, infra |
| Niveau 3 | CEO / Stratège | Arbitrage business | Budget, stratégie, partenariats |
| Niveau 4 | Comité Exécutif (PO + CEO + Archi + QA) | Décision finale | Frictions irréductibles, GO/NO-GO |

---

*Document généré par le modérateur du groupe Architecture & Technique — KIMI-TAKA-SWARM*
*Synthèse des débats de 30 agents sur 11 pôles — 3 858 lignes de débats consolidées*
*Classification : Interne — Décisionnel*

---

**FIN DU PROCÈS-VERBAL**

