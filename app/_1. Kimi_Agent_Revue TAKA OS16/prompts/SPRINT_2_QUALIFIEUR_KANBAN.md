# SPRINT 2 - PROMPT KIMI CODE MIS A JOUR
## Qualifieur V2 + Kanban + Business Lines + Dashboard Admin

**Version :** 2.0-UPDATED
**Date :** Sprint 2
**Agent :** Kimi Code
**Longueur cible :** 4 500 a 5 000 lignes
**Couverture :** 35 fichiers sources + 5 fichiers YAML de configuration

---

## TABLE DES MATIERES

1. CONTEXTE DU PROJET
2. STACK TECHNIQUE COMPLET
3. REGLES DE DEVELOPPEMENT
4. MISSION DU SPRINT 2
5. FICHIERS A PRODUIRE - Groupe A : Scoring Engine V2
6. FICHIERS A PRODUIRE - Groupe B : YAML Dimensions
7. FICHIERS A PRODUIRE - Groupe C : Business Lines
8. FICHIERS A PRODUIRE - Groupe D : Dashboard Admin
9. FICHIERS A PRODUIRE - Groupe E : Dashboard Collaborateur
10. FICHIERS A PRODUIRE - Groupe F : Feature Flags
11. FICHIERS A PRODUIRE - Groupe G : Frontend
12. FICHIERS A PRODUIRE - Groupe H : Tests & Validation
13. ARCHITECTURE CIBLE
14. CHECKLIST DE LIVRAISON

---

# SECTION 1 - CONTEXTE DU PROJET

## 1.1 Recapitulatif Sprints 0 et 1

Le projet est une **plateforme de qualification d'Appels d'Offres (AO)** pour les TPE/PME et leurs equipes commerciales.

### Sprint 0 (Fondations)
- Architecture Next.js 14 + Supabase
- Authentification (OAuth + OTP email + password)
- Base de donnees relationnelle (appels_offres, users, profiles)
- Upload de documents (PDF, DOCX) pour analyse
- Parsing automatique des AO (titre, montant, deadline, CPV, lieu, description)

### Sprint 1 (Qualification V1)
- Scoring GO / NO-GO / MAYBE (regles simples : montant, deadline, localisation)
- Interface de saisie manuelle d'AO (formulaire complet)
- Kanban drag-drop (colonnes : A qualifier / Qualifies / En cours / Non retenus)
- Dashboard sommaire (4 KPIs)
- Notifications email (passage en qualifie, deadline proche)
- Dark mode / Light mode
- Systeme de tags

### Etat actuel
- Code stable, base deployee sur Vercel
- Supabase en production avec RLS actives
- 3 utilisateurs testeurs actifs
- Environ 45 AO en base de test

## 1.2 Objectifs du Sprint 2

Le Sprint 2 transforme la qualification "regles simples" en un **moteur de scoring professionnel multi-dimensionnel** avec gestion multi-metiers et dashboards analytiques complets.

**Piliers du Sprint 2 :**

**Pilier A - Scoring Engine V2**
Remplacer le scoring a 3 criteres par un moteur a 5 dimensions parametrables. Chaque AO passe par 5 plugins d'analyse independants. Le resultat est un ScoreCard JSON avec scores detailles, verdict final, et explications XAI (Explainable AI).

**Pilier B - Business Lines (Multi-metiers)**
Une entreprise peut gerer plusieurs metiers (ex: batiment, informatique, conseil). Chaque Business Line a ses propres mots-cles CPV, couleur, profil de scoring. Les utilisateurs sont associes a une ou plusieurs BL. Les AO, scores, et dashboards sont filtres par BL avec 4 niveaux de scope.

**Pilier C - Dashboard Admin**
Un tableau de bord complet pour les managers et admins avec 15+ widgets : KPIs cards, graphiques de repartition, evolutions temporelles, tableaux de suivi, alertes prioritaires, actions rapides, et insights IA generiques (TAKA LAB basic).

**Pilier D - Rationalisation**
15 KPIs precis avec formules SQL documentees, benchmarking interne BL contre BL, rapports automatiques hebdomadaires et mensuels exportables.

**Pilier E - Feature Flags**
Gating des fonctionnalites par plan d'abonnement (Free / Starter / Pro / Enterprise) avec kill switch d'urgence.

## 1.3 Users Stories Sprint 2

**US-S2-001 :** En tant qu'admin, je peux creer et configurer des Business Lines avec CPV, mots-cles, couleur, et profil de scoring.

**US-S2-002 :** En tant qu'admin, je peux associer des collaborateurs a une ou plusieurs Business Lines.

**US-S2-003 :** En tant qu'utilisateur, je vois uniquement les AO et scores de mes Business Lines affectees.

**US-S2-004 :** En tant qu'utilisateur, lorsque je qualifie un AO, le Scoring Engine V2 analyse 5 dimensions et produit un ScoreCard detaille avec explications.

**US-S2-005 :** En tant qu'utilisateur, je peux consulter le ScoreCard d'un AO avec radar chart des 5 dimensions.

**US-S2-006 :** En tant qu'utilisateur, je peux donner un feedback sur un score ("ce score est trop severe/lenient") pour calibrer le moteur.

**US-S2-007 :** En tant que manager, je vois un Dashboard Admin avec KPIs de mon scope (mes BL ou toute l'entreprise).

**US-S2-008 :** En tant que manager, je peux comparer les performances entre Business Lines.

**US-S2-009 :** En tant qu'admin, je peux recevoir un rapport automatique hebdomadaire des performances.

**US-S2-010 :** En tant qu'admin, je peux activer/desactiver des features via Feature Flags par plan d'abonnement.

**US-S2-011 :** En tant qu'utilisateur Free, je suis limite a 10 AO par mois et 1 Business Line.

**US-S2-012 :** En tant qu'utilisateur, le Kanban reste fonctionnel avec les nouveaux status du scoring V2 (GO_v2, NO_GO_v2, MAYBE_v2).

---

# SECTION 2 - STACK TECHNIQUE COMPLET

## 2.1 Backend

| Couche | Technologie | Version |
|--------|-------------|---------|
| Framework | Next.js | 14 (App Router) |
| Langage | TypeScript | 5.3 |
| Auth | Supabase Auth | v2 |
| Database | PostgreSQL (Supabase) | 15 |
| ORM/Client | Supabase JS Client | v2 |
| API | Next.js Route Handlers | App Router |
| Validation | Zod | 3.22 |
| Emails | Resend | v1 |
| Templates | Jinja2 (via nunjucks) | 3.2 |

## 2.2 Frontend

| Couche | Technologie | Version |
|--------|-------------|---------|
| Framework | Next.js | 14 |
| Langage | TypeScript | 5.3 |
| Styling | Tailwind CSS | 3.4 |
| Components | shadcn/ui | latest |
| Icons | Lucide React | latest |
| Charts | Recharts | 2.10 |
| Kanban | @hello-pangea/dnd | 16 |
| State | Zustand | 4.4 |
| Forms | React Hook Form | 7.48 |
| Validation | Zod resolver | 3.22 |

## 2.3 Nouveaux outils Sprint 2

**Jinja2 / Nunjucks pour templates scoring :**
Le Scoring Engine V2 utilise des templates de regles ecrits en syntaxe Jinja2-like (via nunjucks cote client ou eval cote serveur). Les fichiers YAML de dimensions contiennent des expressions conditionnelles type `{% if montant > 50000 %}score: 8{% endif %}`.

Ces templates sont evalues a l'execution avec le contexte de l'AO (montant, deadline, CPV, localisation, etc.).

**Recharts pour graphiques :**
Tous les graphiques du Dashboard Admin utilisent Recharts (RadarChart pour le scoring, BarChart, LineChart, PieChart pour les KPIs).

**Zustand pour state global :**
Le store global gere : user, businessLines actives, feature flags, preferences UI.

## 2.4 Supabase Schema - Nouvelles Tables

### business_lines
```sql
CREATE TABLE business_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  cpv_codes TEXT[],           -- codes CPV associes
  keywords TEXT[],            -- mots-cles de detection
  color TEXT DEFAULT '#3b82f6', -- couleur thematique
  scoring_profile TEXT DEFAULT 'prudent', -- prudent | opportuniste | specialise
  company_id UUID REFERENCES companies(id),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### user_business_lines
```sql
CREATE TABLE user_business_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  business_line_id UUID REFERENCES business_lines(id) ON DELETE CASCADE,
  role TEXT DEFAULT 'member', -- admin_bl | member | viewer
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, business_line_id)
);
```

### score_cards
```sql
CREATE TABLE score_cards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  appel_offre_id UUID REFERENCES appels_offres(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id),
  business_line_id UUID REFERENCES business_lines(id),
  
  -- 5 dimensions
  dimension_business_coherence JSONB,
  dimension_financial_viability JSONB,
  dimension_geographic_access JSONB,
  dimension_temporal_feasibility JSONB,
  dimension_competitive_intel JSONB,
  
  overall_score NUMERIC(4,2),
  verdict TEXT CHECK (verdict IN ('GO_v2', 'NO_GO_v2', 'MAYBE_v2')),
  confidence NUMERIC(3,2), -- 0.00 a 1.00
  
  profile_used TEXT,
  xai_explanation JSONB,     -- explications structurees
  raw_data JSONB,            -- donnees brutes utilisees
  
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### scoring_feedbacks
```sql
CREATE TABLE scoring_feedbacks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  score_card_id UUID REFERENCES score_cards(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id),
  dimension_name TEXT,       -- null = feedback global
  feedback_type TEXT CHECK (feedback_type IN ('too_strict', 'too_lenient', 'incorrect', 'other')),
  comment TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### feature_flags
```sql
CREATE TABLE feature_flags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  plans_allowed TEXT[],      -- ['free', 'starter', 'pro', 'enterprise']
  default_enabled BOOLEAN DEFAULT true,
  kill_switch BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### user_plans
```sql
CREATE TABLE user_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')),
  ao_limit_monthly INTEGER DEFAULT 10,
  bl_limit INTEGER DEFAULT 1,
  scoring_dimensions_enabled INTEGER DEFAULT 3, -- nombre de dimensions actives
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### dashboard_reports
```sql
CREATE TABLE dashboard_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  type TEXT CHECK (type IN ('weekly', 'monthly')),
  content JSONB,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### appels_offres - colonnes ajoutees
```sql
ALTER TABLE appels_offres ADD COLUMN business_line_id UUID REFERENCES business_lines(id);
ALTER TABLE appels_offres ADD COLUMN scope_level TEXT DEFAULT 'individuel' 
  CHECK (scope_level IN ('global', 'business_line', 'individuel', 'readonly'));
ALTER TABLE appels_offres ADD COLUMN assigned_to UUID REFERENCES auth.users(id);
```

## 2.5 RLS Policies a ajouter

Toutes les nouvelles tables doivent avoir des policies RLS.

**business_lines :**
- SELECT : company members
- INSERT : company admins
- UPDATE : company admins ou admin_bl
- DELETE : company admins uniquement

**user_business_lines :**
- SELECT : user can see his own + admin can see all in company
- INSERT : company admins
- UPDATE : company admins ou l'utilisateur lui-meme (pour son role viewer)
- DELETE : company admins

**score_cards :**
- SELECT : user can see his own + users in same BL + admin can see all in company
- INSERT : any authenticated user for AO in his BL
- UPDATE : owner only
- DELETE : owner or admin

**scoring_feedbacks :**
- SELECT : owner + admin
- INSERT : any authenticated user
- UPDATE : none
- DELETE : admin only

**feature_flags :**
- SELECT : public (tout le monde peut voir les flags)
- INSERT/UPDATE/DELETE : super admin only (service role)

---

# SECTION 3 - REGLES DE DEVELOPPEMENT

## 3.1 Conventions de code

**TypeScript strict :**
- `strict: true` dans tsconfig.json
- Pas de `any` sauf exception documentee avec commentaire `// eslint-disable-next-line @typescript-eslint/no-explicit-any`
- Types explicites pour tous les retours de fonction
- Interfaces preferees aux types sauf pour unions

**Nommage :**
- Composants React : PascalCase (ex: `ScoreCardRadar.tsx`)
- Hooks : camelCase prefixe `use` (ex: `useScoringEngine.ts`)
- Utilitaires : camelCase (ex: `calculateDimensionScore.ts`)
- Fichiers API : kebab-case (ex: `score-cards/route.ts`)
- Tables SQL : snake_case, pluriel
- Colonnes SQL : snake_case

**Architecture fichiers :**
```
app/
  api/
    scoring/
      engine/route.ts
      dimensions/route.ts
    business-lines/route.ts
    score-cards/route.ts
    dashboard/
      admin/route.ts
      collaborator/route.ts
    feature-flags/route.ts
  (dashboard)/
    admin/
      page.tsx
      layout.tsx
    kanban/
      page.tsx
    score-card/
      [id]/page.tsx
components/
  scoring/
    ScoreCardRadar.tsx
    ScoreCardDetail.tsx
    DimensionScore.tsx
  business-lines/
    BLSelector.tsx
    BLBadge.tsx
  dashboard/
    admin/
      KPICard.tsx
      ChartRepartition.tsx
      ChartEvolution.tsx
      TableSuivi.tsx
      AlertesPrioritaires.tsx
      ActionsRapides.tsx
      InsightsIA.tsx
    collaborator/
      KanbanBoard.tsx
      KanbanColumn.tsx
      KanbanCard.tsx
      NotificationBell.tsx
  ui/           # shadcn/ui components
lib/
  scoring/
    engine.ts
    plugins/
      coherence-metier.ts
      viabilite-financiere.ts
      accessibilite-geographique.ts
      faisabilite-temporelle.ts
      intelligence-concurrentielle.ts
    registry.ts
    balancer.ts
    explainer.ts
    feedback.ts
  business-lines/
    scope.ts
    api.ts
  dashboard/
    kpis.ts
    formulas.ts
    benchmark.ts
  feature-flags/
    service.ts
    gating.ts
  utils/
    supabase.ts
    zod-schemas.ts
    jinja-eval.ts
config/
  scoring/
    dimensions/
      coherence-metier.yaml
      viabilite-financiere.yaml
      accessibilite-geographique.yaml
      faisabilite-temporelle.yaml
      intelligence-concurrentielle.yaml
    profiles/
      prudent.yaml
      opportuniste.yaml
      specialise.yaml
```

## 3.2 Regles UX/UI

**Design system :**
- Couleurs scoring : GO = emerald-500 / green, NO-GO = rose-500 / red, MAYBE = amber-500 / yellow
- Couleurs dimensions : coherence = blue, financier = emerald, geo = indigo, temporel = orange, concurrentiel = purple
- Polices : Inter pour tout le texte
- Espacement : systeme 4px (0.5rem = 8px standard)
- Bordures : rounded-lg (8px) pour cards, rounded-full pour badges
- Ombres : shadow-sm pour cards internes, shadow-md pour modales

**Responsive :**
- Mobile-first (base styles pour mobile, md: et lg: pour desktop)
- Dashboard admin : grille 1 colonne mobile, 2 colonnes tablet, 3-4 colonnes desktop
- Kanban : horizontal scroll sur mobile, colonnes fixes sur desktop
- ScoreCard radar : taille reduite sur mobile (< 300px)

**Accessibilite (a11y) :**
- Tous les boutons avec aria-label
- Contraste minimum 4.5:1 pour le texte
- Focus visible sur tous les elements interactifs
- aria-live pour les notifications
- keyboard navigation pour Kanban (Tab entre colonnes, fleches entre cartes)
- prefers-reduced-motion : desactiver les animations drag-drop

**shadcn/ui obligatoires :**
- Card, Button, Badge, Dialog, Select, Tabs, Table, Skeleton, Tooltip, Toast, Alert, Progress, Separator, Sheet, Command
- Charts custom avec Recharts (pas de composant shadcn/ui chart car trop limite)

## 3.3 Regles Backend

**API Routes :**
- Toutes les routes protegees par middleware d'authentification
- Validation Zod des body params pour POST/PUT/PATCH
- Gestion erreurs : { error: string, code: string, details?: unknown }
- Status HTTP appropries : 200, 201, 400, 401, 403, 404, 500
- Rate limiting : 100 requetes/minute par IP pour les routes publiques, 300/min pour authentifiees

**Supabase :**
- TOUJOURS utiliser le client serveur avec service_role pour les operations admin
- Utiliser le client anon avec RLS pour les operations utilisateur
- Les RPC pour les requetes complexes (KPIs, agregations)

**Scoring Engine :**
- Execution idempotente : meme AO + meme profil = meme resultat
- Isolation des dimensions : un plugin en erreur ne bloque pas les autres
- Timeout par dimension : 5 secondes max
- Fallback : si une dimension echoue, score = null pour cette dimension, confidence reduite

**Business Lines isolation :**
- Toute requete qui touche aux AO DOIT filter par business_line_id
- Le scope global permet de voir tous les AO de l'entreprise
- Le scope business_line permet de voir les AO de la BL
- Le scope individuel permet de voir ses AO assignes
- Le scope readonly permet de voir sans modifier

## 3.4 Regles YAML Scoring

Les fichiers YAML de dimension definissent les regles de scoring.

**Structure type :**
```yaml
dimension:
  name: coherence_metier
  display_name: "Coherence Metier"
  description: "Mesure la coherence entre le metier de l'entreprise et l'AO"
  version: "1.0"
  
scoring:
  scale: 0-10
  default_score: 5
  
rules:
  - name: "cpv_match_exact"
    condition: "cpv_code in business_line.cpv_codes"
    score: 10
    weight: 0.4
    
  - name: "keyword_match"
    condition: "count(keywords in ao.description) > 3"
    score: 8
    weight: 0.3
    
  - name: "keyword_partial"
    condition: "count(keywords in ao.description) > 0"
    score: 5
    weight: 0.2
    
  - name: "no_match"
    condition: "default"
    score: 2
    weight: 0.1

templates:
  explanation_positive: "L'AO correspond parfaitement a votre metier (CPV {{cpv_code}})."
  explanation_neutral: "Correspondance partielle detectee."
  explanation_negative: "Faible correspondance avec votre domaine d'activite."
```

**Regles d'evaluation :**
- Les conditions sont evaluees dans l'ordre (premier match gagne)
- Les templates utilisent la syntaxe Jinja2 avec les variables du contexte
- Le score final dimension = sum(rule_score * rule_weight)
- Le poids total des regles doit faire 1.0 (verifie au chargement)

---

# SECTION 4 - MISSION DU SPRINT 2

## 4.1 Flux complet de l'utilisateur

```
1. Utilisateur upload/creer un AO
   |
2. Systeme detecte la Business Line (via CPV + mots-cles)
   |
3. Utilisateur clique "Qualifier" (ou auto-trigger si config)
   |
4. Scoring Engine V2 s'execute :
   - Recupere le profil de la BL (prudent/opportuniste/specialise)
   - Charge les 5 YAML de dimension
   - Execute les 5 plugins en parallele
   - Chaque plugin retourne : score, poids, explication, donnees brutes
   |
5. Balancer calcule le score global pondere
   |
6. Explainer genere les explications XAI
   |
7. ScoreCard JSON sauvegarde en base
   |
8. Verdict affiche (GO_v2 / NO_GO_v2 / MAYBE_v2) + Radar Chart
   |
9. Utilisateur peut :
   a. Accepter le verdict -> AO deplace dans Kanban
   b. Modifier manuellement -> feedback enregistre
   c. Consulter explications detaillees
   |
10. Dashboard Admin mis a jour (async via trigger)
    |
11. Notifications envoyees selon config
```

## 4.2 Architecture du Scoring Engine V2

```
                    +------------------+
                    |   AO Input       |
                    | (JSON context)   |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
       +------v------+  +---------v--------+ ... x5
       | Plugin D1   |  | Plugin D2        |
       | Coherence   |  | Viabilite Fin.   |
       | Metier      |  |                  |
       +------+------+  +---------+--------+
              |                             |
              +--------------+--------------+
                             |
                    +--------v---------+
                    |   Balancer       |
                    | (ponderation     |
                    |  par profil)     |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   Verdict        |
                    | GO/NO-GO/MAYBE   |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
       +------v------+              +-------v-------+
       | Explainer   |              | ScoreCard     |
       | (XAI)       |              | (JSON persist) |
       +-------------+              +---------------+
```

## 4.3 Profils de scoring

**Prudent (conservateur) :**
- Seuil GO : score >= 7.5
- Seuil MAYBE : score >= 5.0
- Seuil NO-GO : score < 5.0
- Poids dimensions : coherence(0.30), financier(0.25), geo(0.20), temporel(0.15), concurrentiel(0.10)
- Penalite forte pour les AO avec faible marge estimée

**Opportuniste (agressif) :**
- Seuil GO : score >= 6.0
- Seuil MAYBE : score >= 4.0
- Seuil NO-GO : score < 4.0
- Poids dimensions : coherence(0.20), financier(0.20), geo(0.15), temporel(0.20), concurrentiel(0.25)
- Bonus pour les AO innovants ou peu concurrentiels

**Specialise (equilibre metier) :**
- Seuil GO : score >= 7.0
- Seuil MAYBE : score >= 4.5
- Seuil NO-GO : score < 4.5
- Poids dimensions : coherence(0.35), financier(0.20), geo(0.20), temporel(0.15), concurrentiel(0.10)
- Bonus CPV exact, penalite deadline trop courte

## 4.4 Systeme de Scope Business Lines

**4 niveaux de scope pour les AO :**

1. **Global** (`scope_level = 'global'`)
   - Visible par tous les membres de l'entreprise
   - Modifiable par les admins et managers
   - Utilise pour les AO strategiques transversaux

2. **Business Line** (`scope_level = 'business_line'`)
   - Visible par les membres de la BL
   - Modifiable par les admin_bl et membres de la BL
   - Default pour la plupart des AO

3. **Individuel** (`scope_level = 'individuel'`)
   - Visible par l'assignee (`assigned_to`) et les admins
   - Modifiable par l'assignee
   - Pour les AO personnellement suivis

4. **Lecture seule** (`scope_level = 'readonly'`)
   - Visible par tous dans la BL
   - Non modifiable
   - Pour les AO archives ou de reference

**Regles de filtrage SQL (pseudo-code) :**
```sql
WHERE (
  -- Admin entreprise : tout voir
  user.role = 'admin' 
  OR
  -- Global : tous les membres de l'entreprise
  (ao.scope_level = 'global' AND user.company_id = ao.company_id)
  OR
  -- Business Line : membres de la BL
  (ao.scope_level = 'business_line' AND user.id IN (
    SELECT user_id FROM user_business_lines 
    WHERE business_line_id = ao.business_line_id
  ))
  OR
  -- Individuel : assignee ou admin
  (ao.scope_level = 'individuel' AND (user.id = ao.assigned_to OR user.role = 'admin'))
  OR
  -- Readonly : membres de la BL (meme si viewer)
  (ao.scope_level = 'readonly' AND user.id IN (
    SELECT user_id FROM user_business_lines 
    WHERE business_line_id = ao.business_line_id
  ))
)
```

## 4.5 Dashboard Admin - 15 KPIs

| # | KPI | Formule SQL | Type |
|---|-----|-------------|------|
| 1 | CA Pipeline | SUM(montant_estimate) WHERE status != 'non_retenu' | EUR |
| 2 | Taux reussite | COUNT(verdict='GO_v2') / COUNT(*) * 100 | % |
| 3 | AO actifs | COUNT(*) WHERE status IN ('a_qualifier', 'qualifie', 'en_cours') | int |
| 4 | Ratio GO/NO-GO | COUNT(GO) / COUNT(NO-GO) | ratio |
| 5 | CA moyen GO | AVG(montant) WHERE verdict='GO_v2' | EUR |
| 6 | Delai moyen qualif | AVG(qualified_at - created_at) | jours |
| 7 | Taux conversion | COUNT(gagne) / COUNT(GO) * 100 | % |
| 8 | Activite 30j | COUNT(*) WHERE created_at > now() - 30j | int |
| 9 | Top BL par CA | SUM(montant) GROUP BY business_line_id ORDER BY 1 DESC | classement |
| 10 | Taux MAYBE | COUNT(MAYBE) / COUNT(*) * 100 | % |
| 11 | AO en retard | COUNT(*) WHERE deadline < now() + 7j AND status != 'gagne' | int |
| 12 | Marge moyenne | AVG(marge_estimee) WHERE verdict='GO_v2' | % |
| 13 | Nouveaux AO 7j | COUNT(*) WHERE created_at > now() - 7j | int |
| 14 | Taux de participation | COUNT(soumission_envoyee) / COUNT(GO) * 100 | % |
| 15 | Score moyen global | AVG(overall_score) | /10 |

## 4.6 Rapports automatiques

**Rapport hebdomadaire (lundi 8h) :**
- Nouveaux AO de la semaine
- AO qualifies avec repartition GO/NO-GO/MAYBE
- Top 3 BL par activite
- Alertes : deadlines dans 7j, AO en attente de qualification > 3j
- Actions recommandees (TAKA LAB basic)

**Rapport mensuel (1er du mois) :**
- Evolution vs mois precedent (tous les KPIs)
- Repartition par BL (comparatif)
- Tendances des scores (moyenne par dimension)
- Top collaborateurs (nombre de qualifications, taux GO)
- Recommandations strategiques

**Format :** JSON stocke en base + email HTML (template Jinja2)

## 4.7 Feature Flags - Plans

| Feature | Free | Starter | Pro | Enterprise |
|---------|------|---------|-----|------------|
| AO mensuels | 10 | 50 | 200 | Illimite |
| Business Lines | 1 | 3 | 10 | Illimite |
| Dimensions scoring | 3 | 4 | 5 | 5 + custom |
| Dashboard Admin | Non | Basic | Complet | Complet + API |
| Rapports auto | Non | Mensuel | Hebdo + Mensuel | Quotidien + Custom |
| Benchmark BL | Non | Non | Oui | Oui |
| Scoring feedback | Non | Oui | Oui | Oui |
| Kanban | Oui | Oui | Oui | Oui |
| Export CSV | Non | Oui | Oui | Oui + PDF |
| API webhooks | Non | Non | Oui | Oui |
| Support | Email | Email | Chat | Phone + CSM |

**Kill switch :** Si `kill_switch = true` sur un flag, la feature est immediatement desactivee pour tous, independamment du plan.

---


# SECTION 5 - FICHIERS A PRODUIRE - Groupe A : Scoring Engine V2

## FICHIER A-1 : `lib/scoring/engine.ts`

**Role :** Moteur principal du Scoring Engine V2. Ordonnance l'execution des plugins, collecte les resultats, appelle le balancer et l'explainer.

**Interface :**
```typescript
export interface ScoringContext {
  ao: AppelOffre;
  businessLine: BusinessLine;
  user: User;
  profile: ScoringProfile;
}

export interface DimensionResult {
  name: string;
  displayName: string;
  score: number;        // 0-10
  weight: number;       // 0-1
  confidence: number;   // 0-1
  explanation: string;
  rawData: Record<string, unknown>;
  rulesTriggered: string[];
}

export interface ScoreCard {
  id?: string;
  appelOffreId: string;
  businessLineId: string;
  userId: string;
  dimensions: DimensionResult[];
  overallScore: number;  // 0-10
  verdict: 'GO_v2' | 'NO_GO_v2' | 'MAYBE_v2';
  confidence: number;
  profileUsed: string;
  xaiExplanation: XAIExplanation;
  rawData: Record<string, unknown>;
}

export interface XAIExplanation {
  summary: string;
  dimensionBreakdown: Array<{
    name: string;
    score: number;
    why: string;
    impact: 'high' | 'medium' | 'low';
  }>;
  keyFactors: string[];
  recommendation: string;
}
```

**Fonction principale :**
```typescript
export async function runScoringEngine(
  context: ScoringContext
): Promise<ScoreCard> {
  // 1. Charger les 5 YAML de dimension
  // 2. Charger le profil de scoring (prudent/opportuniste/specialise)
  // 3. Executer les 5 plugins en parallele avec Promise.allSettled
  // 4. Pour chaque plugin qui echoue, logger et mettre score=null
  // 5. Appeler balancer.computeOverallScore()
  // 6. Determiner verdict selon les seuils du profil
  // 7. Appeler explainer.generate()
  // 8. Construire et retourner le ScoreCard
}
```

**Regles :**
- Execution parallele des plugins via `Promise.allSettled`
- Si un plugin timeout (5s), score = null, confidence reduite de 0.2
- Si < 3 dimensions retournent un score, le verdict est FORCE_MAYBE avec warning
- Logging structure de chaque etape (debug mode)
- Idempotent : meme contexte = meme resultat (pas de RNG, pas de datetime dans les calculs)

**Dependances :**
- `plugins/coherence-metier.ts`
- `plugins/viabilite-financiere.ts`
- `plugins/accessibilite-geographique.ts`
- `plugins/faisabilite-temporelle.ts`
- `plugins/intelligence-concurrentielle.ts`
- `registry.ts`
- `balancer.ts`
- `explainer.ts`
- `jinja-eval.ts` (evaluation des templates YAML)

## FICHIER A-2 : `lib/scoring/plugins/coherence-metier.ts`

**Role :** Plugin Dimension 1 - Coherence entre le metier de l'entreprise et l'AO.

**Entree :**
- `ao.cpv_code` : string
- `ao.description` : string
- `ao.title` : string
- `businessLine.cpv_codes` : string[]
- `businessLine.keywords` : string[]

**Logique :**
1. Calculer le score de matching CPV :
   - CPV exact match (5 premiers caracteres) = 10
   - CPV niveau 2 match (3 premiers caracteres) = 7
   - CPV niveau 1 match (2 premiers caracteres) = 5
   - Aucun match = 2

2. Calculer le score de matching mots-cles :
   - Extraire les mots de l'AO (titre + description, nettoyes)
   - Compter les intersections avec `businessLine.keywords`
   - >= 5 mots = 10
   - 3-4 mots = 7
   - 1-2 mots = 4
   - 0 mot = 1

3. Score final = (cpvScore * 0.6) + (keywordScore * 0.4)

4. Explication : template Jinja2 avec variables cpv_match_level, keyword_count, keyword_examples

**Sortie :** `DimensionResult`

## FICHIER A-3 : `lib/scoring/plugins/viabilite-financiere.ts`

**Role :** Plugin Dimension 2 - Viabilite financiere de l'AO.

**Entree :**
- `ao.montant` : number | null
- `ao.montant_estime` : number | null
- `businessLine.scoring_profile` : string (pour les seuils)
- `profile.financial_rules` : depuis YAML profil

**Logique :**
1. Si pas de montant, tenter extraction depuis description (regex EUR, K, M)
2. Score selon plages de montant :
   - < 10K : 3 (trop petit, couts de transaction eleves)
   - 10K - 50K : 5
   - 50K - 200K : 7
   - 200K - 1M : 9
   - > 1M : 7 (risque eleve pour TPE/PME, sauf si Enterprise)

3. Ajustement selon profil :
   - Prudent : penalite -1 si montant > 500K
   - Opportuniste : bonus +1 si montant > 100K
   - Specialise : pas d'ajustement

4. Marge estimee (si disponible dans les donnees brutes AO) :
   - Marge > 30% : bonus +1
   - Marge < 10% : penalite -1

5. Explication : montant brut, categorie, ajustements appliques

**Sortie :** `DimensionResult`

## FICHIER A-4 : `lib/scoring/plugins/accessibilite-geographique.ts`

**Role :** Plugin Dimension 3 - Accessibilite geographique de l'AO.

**Entree :**
- `ao.localisation` : string (ville, region, departement)
- `ao.code_postal` : string | null
- `businessLine.zone_chalandise` : string[] | null (departements couverts)
- `user.company.siege_social` : string | null
- `user.company.departements_couverts` : string[]

**Logique :**
1. Normaliser la localisation de l'AO (extraire le departement depuis le CP ou le texte)
2. Comparer avec les departements couverts par l'entreprise :
   - Meme departement = 10
   - Departement adjacent = 7
   - Meme region = 5
   - France entiere = 4 (si l'AO est national)
   - Hors zone = 2

3. Ajuster selon type de prestation :
   - Si keywords "deplacement", "sur_site" dans l'AO : bonus +1 si proche, penalite -2 si loin
   - Si keywords "teletravail", "distance" : bonus +1 meme si loin

4. Explication : zone detectee, zone couverte, distance logique

**Sortie :** `DimensionResult`

**Note :** Table `departements_adjacents` ou mapping inline des adjacences pour les 101 departements francais (DOM-TOM inclus).

## FICHIER A-5 : `lib/scoring/plugins/faisabilite-temporelle.ts`

**Role :** Plugin Dimension 4 - Faisabilite temporelle (delai avant deadline).

**Entree :**
- `ao.date_limite` : Date | null
- `ao.date_publication` : Date | null
- `businessLine.delai_preparation_moyen` : number (jours, defaut 14)
- `profile` : pour les seuils

**Logique :**
1. Calculer jours restants : `date_limite - aujourd'hui`
2. Score selon delai :
   - < 3 jours : 2 (urgence extreme)
   - 3-7 jours : 4
   - 7-14 jours : 6
   - 14-30 jours : 8
   - 30-60 jours : 9
   - > 60 jours : 8 (risque d'oubli ou changement)

3. Ajustement selon delai de preparation moyen de la BL :
   - Si jours_restants < delai_preparation * 0.5 : penalite -2
   - Si jours_restants > delai_preparation * 2 : bonus +0.5

4. Si pas de date_limite : score = 5 (incertitude neutre), confidence = 0.5

5. Explication : jours restants, delai de preparation reference, ajustement

**Sortie :** `DimensionResult`

## FICHIER A-6 : `lib/scoring/plugins/intelligence-concurrentielle.ts`

**Role :** Plugin Dimension 5 - Intelligence concurrentielle (estimation de la concurrence).

**Entree :**
- `ao.cpv_code` : string
- `ao.montant` : number
- `ao.lieu` : string
- `businessLine.historique_ao` : donnees historiques de la BL
- `historique_win_rate` : taux de reussite sur ce CPV (depuis les score_cards en base)

**Logique :**
1. Recuperer l'historique des AO du meme CPV dans la BL :
   - Nombre total d'AO avec ce CPV (6 derniers mois)
   - Nombre de GO emis
   - Nombre de gains effectifs (si suivi)

2. Calculer le taux de reussite historique :
   - Taux > 50% = 9 (position forte)
   - Taux 30-50% = 7
   - Taux 10-30% = 5
   - Taux < 10% = 3
   - Aucun historique = 5 (neutre)

3. Ajustement montant :
   - Montant > 500K : moins de concurrence pour TPE, bonus +1
   - Montant < 20K : forte concurrence, penalite -1

4. Explication : taux historique, nombre d'AO references, ajustement

**Sortie :** `DimensionResult`

**Note :** Ce plugin fait une requete SQL sur `score_cards` et `appels_offres` pour l'historique. La requete doit etre optimisee (index sur `cpv_code`, `business_line_id`, `created_at`).

## FICHIER A-7 : `lib/scoring/registry.ts`

**Role :** Registre des plugins de dimension. Permet d'enregistrer, lister, et recuperer les plugins dynamiquement.

**Interface :**
```typescript
export interface DimensionPlugin {
  name: string;
  displayName: string;
  version: string;
  execute: (context: ScoringContext) => Promise<DimensionResult>;
  config?: Record<string, unknown>;
}

export class ScoringRegistry {
  private plugins: Map<string, DimensionPlugin>;
  
  register(plugin: DimensionPlugin): void;
  unregister(name: string): void;
  get(name: string): DimensionPlugin | undefined;
  getAll(): DimensionPlugin[];
  getActiveNames(): string[];
}
```

**Comportement :**
- Singleton (une seule instance par process)
- Au demarrage, enregistre automatiquement les 5 plugins natifs
- Supporte l'enregistrement de plugins custom (future Enterprise)
- Si un plugin n'est pas trouve, throw `PluginNotFoundError`

**Initialisation :**
```typescript
export const scoringRegistry = new ScoringRegistry();

// Auto-register au module load
scoringRegistry.register(coherenceMetierPlugin);
scoringRegistry.register(viabiliteFinancierePlugin);
scoringRegistry.register(accessibiliteGeographiquePlugin);
scoringRegistry.register(faisabiliteTemporellePlugin);
scoringRegistry.register(intelligenceConcurrentiellePlugin);
```

## FICHIER A-8 : `lib/scoring/balancer.ts`

**Role :** Calcule le score global pondere a partir des 5 resultats de dimension.

**Interface :**
```typescript
export interface ProfileConfig {
  name: string;
  thresholds: {
    go: number;
    maybe: number;
    noGo: number;
  };
  weights: {
    coherenceMetier: number;
    viabiliteFinanciere: number;
    accessibiliteGeographique: number;
    faisabiliteTemporelle: number;
    intelligenceConcurrentielle: number;
  };
}

export function computeOverallScore(
  dimensions: DimensionResult[],
  profile: ProfileConfig
): {
  overallScore: number;
  confidence: number;
  verdict: 'GO_v2' | 'NO_GO_v2' | 'MAYBE_v2';
};
```

**Logique :**
1. Verifier que la somme des poids du profil = 1.0 (avec tolerance 0.01)
2. Pour chaque dimension avec score non-null :
   - weightedScore += dimension.score * dimension.weight
   - totalWeight += dimension.weight
3. Si une dimension est null (plugin en erreur) :
   - Reproportionner les poids des dimensions restantes
   - Confidence = confidence * (dimensions_reussies / 5)
4. Score global = weightedScore / totalWeight (si totalWeight > 0)
5. Verdict selon les seuils du profil
6. Confidence globale = moyenne des confidences individuelles * facteur completude

**Edge cases :**
- 0 dimension retournee = throw Error (moteur inutilisable)
- 1-2 dimensions = verdict FORCE_MAYBE, confidence < 0.3
- Toutes dimensions null = throw Error

## FICHIER A-9 : `lib/scoring/explainer.ts`

**Role :** Genere les explications XAI (Explainable AI) du ScoreCard.

**Interface :**
```typescript
export function generateExplanation(
  dimensions: DimensionResult[],
  overallScore: number,
  verdict: string,
  profile: ProfileConfig
): XAIExplanation;
```

**Logique :**
1. `summary` : phrase synthetique "Cet AO est classe [VERDICT] avec un score de [X]/10. Les facteurs principaux sont..."
2. `dimensionBreakdown` : pour chaque dimension
   - `impact` : 'high' si weight > 0.25, 'medium' si 0.15-0.25, 'low' si < 0.15
   - `why` : explication du plugin
3. `keyFactors` : liste de 3-5 facteurs determinants (les dimensions avec le plus d'ecart a la moyenne, ou les scores extremes)
4. `recommendation` :
   - Si GO : "Poursuivre la qualification et preparer la soumission."
   - Si MAYBE : "Reevaluer apres analyse complementaire sur [dimension faible]."
   - Si NO-GO : "Abandon recommande. Si strategique, verifier [dimension principale]."

**Templates :**
Les explications utilisent les templates YAML de chaque dimension. L'explainer selectionne le template selon le score (positive > 7, neutral 4-7, negative < 4).

## FICHIER A-10 : `lib/scoring/feedback.ts`

**Role :** Gestion du feedback utilisateur sur les scores (calibration).

**Interface :**
```typescript
export interface ScoringFeedback {
  scoreCardId: string;
  userId: string;
  dimensionName?: string;  // null = feedback global
  feedbackType: 'too_strict' | 'too_lenient' | 'incorrect' | 'other';
  comment?: string;
}

export async function recordFeedback(
  feedback: ScoringFeedback
): Promise<void>;

export async function getFeedbackStats(
  businessLineId: string,
  dimensionName?: string
): Promise<{
  totalFeedback: number;
  tooStrictRate: number;
  tooLenientRate: number;
  averageScoreAdjustment: number;
}>;
```

**Logique :**
- Stockage simple en base (`scoring_feedbacks`)
- Stats aggregees pour les admins de BL
- A venir (Sprint 3) : utilisation des stats pour calibrer automatiquement les seuils

## FICHIER A-11 : `lib/utils/jinja-eval.ts`

**Role :** Evaluateur de templates Jinja2-like pour les regles YAML.

**Interface :**
```typescript
export function evaluateTemplate(
  template: string,
  context: Record<string, unknown>
): string;

export function evaluateCondition(
  condition: string,
  context: Record<string, unknown>
): boolean;

export function renderYamlRules(
  yamlContent: string,
  context: Record<string, unknown>
): Array<{
  name: string;
  matched: boolean;
  score: number;
  weight: number;
}>;
```

**Implementation :**
- Utiliser la librairie `nunjucks` pour le rendu cote serveur
- Sanitiser le contexte (pas d'execution de code arbitraire)
- Timeout sur l'evaluation : 1 seconde max
- Si erreur de syntaxe, retourner default et logger

**Securite :**
- Le contexte est type et filtre (whitelist de variables)
- Pas d'acces au filesystem, au reseau, ou a `process`
- Sandboxing via configuration nunjucks

---


# SECTION 6 - FICHIERS A PRODUIRE - Groupe B : YAML Dimensions

## FICHIER B-1 : `config/scoring/dimensions/coherence-metier.yaml`

**Role :** Configuration de la dimension "Coherence Metier" pour le Scoring Engine V2.

**Contenu attendu :**
```yaml
dimension:
  id: coherence_metier
  name: "Coherence Metier"
  description: "Evalue la correspondance entre le domaine d'activite de l'entreprise et l'objet de l'appel d'offres."
  version: "1.0.0"
  author: "system"
  
scoring:
  scale:
    min: 0
    max: 10
    step: 1
  default_score: 3
  default_weight: 0.30
  
rules:
  - id: cpv_exact_match
    name: "CPV Match Exact"
    priority: 1
    condition: "ao.cpv_prefix_5 in business_line.cpv_codes"
    score: 10
    weight: 0.50
    explanation_template: "Correspondance CPV parfaite : le code {{ao.cpv_code}} est dans votre liste metier."
    
  - id: cpv_level2_match
    name: "CPV Niveau 2"
    priority: 2
    condition: "ao.cpv_prefix_3 in business_line.cpv_level2_codes"
    score: 7
    weight: 0.30
    explanation_template: "Correspondance CPV partielle (niveau 2) : le domaine {{ao.cpv_prefix_3}} est proche de votre activite."
    
  - id: keywords_strong
    name: "Mots-cles forts"
    priority: 3
    condition: "keyword_match_count >= 5"
    score: 8
    weight: 0.15
    explanation_template: "{{keyword_match_count}} mots-cles metier detectes dans l'AO."
    
  - id: keywords_weak
    name: "Mots-cles faibles"
    priority: 4
    condition: "keyword_match_count >= 1"
    score: 4
    weight: 0.05
    explanation_template: "Correspondance partielle : {{keyword_match_count}} mot(s) detecte(s)."
    
  - id: no_match
    name: "Aucune correspondance"
    priority: 99
    condition: "default"
    score: 1
    weight: 0.00
    explanation_template: "Aucune correspondance metier detectee. Cet AO semble hors de votre domaine d'activite."

meta:
  required_fields:
    - ao.cpv_code
    - ao.description
    - business_line.cpv_codes
    - business_line.keywords
  optional_fields:
    - ao.title
  
profiles_adjustment:
  prudent:
    penalty_no_match: 2  # penalite supplementaire si no_match
  opportuniste:
    bonus_keyword_match: 1  # bonus si keywords_strong
  specialise:
    require_cpv_exact: true  # exige cpv_exact_match pour un GO
```

**Regles de production :**
- Le fichier doit etre valide YAML (pas de tabulations, espaces uniquement)
- Les templates utilisent la syntaxe Jinja2 : `{{variable}}`
- Les conditions sont evaluees par `jinja-eval.ts`
- `priority` : plus petit = evalue en premier (premier match gagne)
- `condition: "default"` = regle de fallback si aucune autre ne match

## FICHIER B-2 : `config/scoring/dimensions/viabilite-financiere.yaml`

**Role :** Configuration de la dimension "Viabilite Financiere".

**Contenu attendu :**
```yaml
dimension:
  id: viabilite_financiere
  name: "Viabilite Financiere"
  description: "Evalue la viabilite financiere de l'AO selon le montant, les conditions de paiement, et la marge potentielle."
  version: "1.0.0"

scoring:
  scale:
    min: 0
    max: 10
    step: 1
  default_score: 5
  default_weight: 0.25

rules:
  - id: montant_optimal
    name: "Montant Optimal"
    priority: 1
    condition: "ao.montant >= 200000 and ao.montant <= 1000000"
    score: 9
    weight: 0.40
    explanation_template: "Montant optimal de {{ao.montant_formate}}, dans la zone de confort des TPE/PME."
    
  - id: montant_moyen
    name: "Montant Moyen"
    priority: 2
    condition: "ao.montant >= 50000 and ao.montant < 200000"
    score: 7
    weight: 0.30
    explanation_template: "Montant moyen de {{ao.montant_formate}}, accessible avec un effort modere."
    
  - id: montant_petit
    name: "Petit Montant"
    priority: 3
    condition: "ao.montant > 0 and ao.montant < 50000"
    score: 5
    weight: 0.20
    explanation_template: "Petit montant ({{ao.montant_formate}}). Rentabilite a verifier face aux couts de reponse."
    
  - id: montant_eleve
    name: "Montant Eleve"
    priority: 4
    condition: "ao.montant > 1000000"
    score: 4
    weight: 0.10
    explanation_template: "Montant eleve ({{ao.montant_formate}}). Risque accru, necessite une analyse approfondie."
    
  - id: montant_inconnu
    name: "Montant Inconnu"
    priority: 5
    condition: "ao.montant is null or ao.montant == 0"
    score: 3
    weight: 0.00
    explanation_template: "Montant non specifie. Demander un complement d'information."

meta:
  required_fields:
    - ao.montant
  optional_fields:
    - ao.montant_estime
    - ao.delai_paiement
    - ao.conditions_paiement

profiles_adjustment:
  prudent:
    threshold_high_risk: 500000
    high_risk_penalty: 2
  opportuniste:
    threshold_bonus: 100000
    bonus_amount: 1
  specialise:
    balanced: true
```

**Regles de production :**
- Les montants sont en centimes (integer) cote base, convertis en EUR pour les templates
- Si `ao.montant` est null, le plugin tente extraction depuis description via regex

## FICHIER B-3 : `config/scoring/dimensions/accessibilite-geographique.yaml`

**Role :** Configuration de la dimension "Accessibilite Geographique".

**Contenu attendu :**
```yaml
dimension:
  id: accessibilite_geographique
  name: "Accessibilite Geographique"
  description: "Evalue la faisabilite geographique de l'AO selon la zone de chalandise de l'entreprise."
  version: "1.0.0"

scoring:
  scale:
    min: 0
    max: 10
    step: 1
  default_score: 4
  default_weight: 0.20

rules:
  - id: meme_departement
    name: "Meme Departement"
    priority: 1
    condition: "ao.departement in company.departements_couverts"
    score: 10
    weight: 0.50
    explanation_template: "L'AO est situe dans votre departement ({{ao.departement}}). Proximite ideale."
    
  - id: departement_adjacent
    name: "Departement Adjacent"
    priority: 2
    condition: "ao.departement in geo.departements_adjacents"
    score: 7
    weight: 0.25
    explanation_template: "Departement adjacent ({{ao.departement}}). Deplacement gerable."
    
  - id: meme_region
    name: "Meme Region"
    priority: 3
    condition: "ao.region == company.region"
    score: 5
    weight: 0.15
    explanation_template: "Meme region ({{ao.region}}). Deplacements possibles mais planifies."
    
  - id: france_national
    name: "AO National"
    priority: 4
    condition: "ao.type_lieu == 'national' or ao.departement is null"
    score: 4
    weight: 0.10
    explanation_template: "AO de portee nationale. Verifier les conditions de deplacement."
    
  - id: hors_zone
    name: "Hors Zone"
    priority: 5
    condition: "default"
    score: 2
    weight: 0.00
    explanation_template: "Hors de votre zone de couverture ({{ao.departement}} vs {{company.departements_couverts}})."

meta:
  required_fields:
    - ao.localisation
  optional_fields:
    - ao.code_postal
    - company.siege_social
    - company.departements_couverts

profiles_adjustment:
  prudent:
    require_meme_departement_bonus: true
    adjacent_penalty: 1
  opportuniste:
    national_bonus: 1
    adjacent_bonus: 0.5
  specialise:
    region_weight_increase: 0.05
```

## FICHIER B-4 : `config/scoring/dimensions/faisabilite-temporelle.yaml`

**Role :** Configuration de la dimension "Faisabilite Temporelle".

**Contenu attendu :**
```yaml
dimension:
  id: faisabilite_temporelle
  name: "Faisabilite Temporelle"
  description: "Evalue le delai disponible pour repondre a l'AO et preparer la prestation."
  version: "1.0.0"

scoring:
  scale:
    min: 0
    max: 10
    step: 1
  default_score: 5
  default_weight: 0.15

rules:
  - id: delai_confortable
    name: "Delai Confortable"
    priority: 1
    condition: "ao.jours_restant >= 30 and ao.jours_restant <= 60"
    score: 9
    weight: 0.35
    explanation_template: "{{ao.jours_restant}} jours restants. Delai confortable pour preparer une reponse de qualite."
    
  - id: delai_suffisant
    name: "Delai Suffisant"
    priority: 2
    condition: "ao.jours_restant >= 14 and ao.jours_restant < 30"
    score: 7
    weight: 0.30
    explanation_template: "{{ao.jours_restant}} jours restants. Delai suffisant avec une organisation rigoureuse."
    
  - id: delai_juste
    name: "Delai Juste"
    priority: 3
    condition: "ao.jours_restant >= 7 and ao.jours_restant < 14"
    score: 5
    weight: 0.20
    explanation_template: "{{ao.jours_restant}} jours restants. Delai serre. Reponse rapide necessaire."
    
  - id: delai_urgent
    name: "Delai Urgent"
    priority: 4
    condition: "ao.jours_restant >= 3 and ao.jours_restant < 7"
    score: 3
    weight: 0.10
    explanation_template: "{{ao.jours_restant}} jours restants. Urgence. Ne repondre que si la preparation est immediate."
    
  - id: delai_critique
    name: "Delai Critique"
    priority: 5
    condition: "ao.jours_restant < 3"
    score: 1
    weight: 0.05
    explanation_template: "{{ao.jours_restant}} jours restants. Delai critique. Reponse quasi impossible."
    
  - id: delai_inconnu
    name: "Delai Inconnu"
    priority: 6
    condition: "ao.jours_restant is null or ao.date_limite is null"
    score: 4
    weight: 0.00
    explanation_template: "Date limite non specifiee. Incertitude temporelle."

meta:
  required_fields:
    - ao.date_limite
  optional_fields:
    - ao.date_publication
    - business_line.delai_preparation_moyen

profiles_adjustment:
  prudent:
    preparation_multiplier: 1.5
    penalty_short_deadline: 1
  opportuniste:
    preparation_multiplier: 0.8
    bonus_long_deadline: 0.5
  specialise:
    preparation_multiplier: 1.0
```

## FICHIER B-5 : `config/scoring/dimensions/intelligence-concurrentielle.yaml`

**Role :** Configuration de la dimension "Intelligence Concurrentielle".

**Contenu attendu :**
```yaml
dimension:
  id: intelligence_concurrentielle
  name: "Intelligence Concurrentielle"
  description: "Evalue la position concurrentielle sur ce type d'AO selon l'historique de la business line."
  version: "1.0.0"

scoring:
  scale:
    min: 0
    max: 10
    step: 1
  default_score: 5
  default_weight: 0.10

rules:
  - id: historique_fort
    name: "Historique Fort"
    priority: 1
    condition: "history.win_rate > 0.50 and history.total_ao >= 3"
    score: 9
    weight: 0.40
    explanation_template: "Taux de reussite de {{history.win_rate_pct}}% sur {{history.total_ao}} AO similaires. Position forte."
    
  - id: historique_moyen
    name: "Historique Moyen"
    priority: 2
    condition: "history.win_rate >= 0.30 and history.win_rate <= 0.50"
    score: 6
    weight: 0.30
    explanation_template: "Taux de reussite de {{history.win_rate_pct}}%. Position moyenne, amelioration possible."
    
  - id: historique_faible
    name: "Historique Faible"
    priority: 3
    condition: "history.win_rate < 0.30 and history.total_ao >= 3"
    score: 3
    weight: 0.20
    explanation_template: "Taux de reussite de {{history.win_rate_pct}}%. Position faible sur ce type d'AO."
    
  - id: sans_historique
    name: "Sans Historique"
    priority: 4
    condition: "history.total_ao < 3 or history.total_ao is null"
    score: 5
    weight: 0.10
    explanation_template: "Pas assez d'historique ({{history.total_ao}} AO). Neutre en l'absence de donnees."

meta:
  required_fields:
    - ao.cpv_code
  optional_fields:
    - ao.montant
    - history.win_rate
    - history.total_ao

profiles_adjustment:
  prudent:
    minimum_history_required: 5
    no_history_penalty: 1
  opportuniste:
    bonus_new_market: 1
    no_history_bonus: 0.5
  specialise:
    history_weight_increase: 0.05
```

## FICHIER B-6 : `config/scoring/profiles/prudent.yaml`

**Role :** Configuration du profil de scoring "Prudent".

**Contenu attendu :**
```yaml
profile:
  id: prudent
  name: "Prudent"
  description: "Profil conservateur privilegiant la securite et la coherence metier."
  version: "1.0.0"

thresholds:
  go: 7.5
  maybe: 5.0
  no_go: 0.0

weights:
  coherence_metier: 0.30
  viabilite_financiere: 0.25
  accessibilite_geographique: 0.20
  faisabilite_temporelle: 0.15
  intelligence_concurrentielle: 0.10

behavior:
  require_strong_match: true
  penalize_high_risk: true
  prefer_proven_markets: true
  
adjustments:
  coherence_metier:
    bonus_exact_cpv: 0.5
    penalty_no_match: 2.0
  viabilite_financiere:
    high_risk_threshold: 500000
    high_risk_penalty: 1.5
    unknown_amount_penalty: 0.5
  accessibilite_geographique:
    require_same_dept: false
    adjacent_penalty: 1.0
  faisabilite_temporelle:
    preparation_multiplier: 1.5
    short_deadline_penalty: 1.5
  intelligence_concurrentielle:
    minimum_history: 5
    no_history_penalty: 1.0
```

## FICHIER B-7 : `config/scoring/profiles/opportuniste.yaml`

**Role :** Configuration du profil de scoring "Opportuniste".

**Contenu attendu :**
```yaml
profile:
  id: opportuniste
  name: "Opportuniste"
  description: "Profil agressif privilegiant le montant et les opportunites peu concurrentielles."
  version: "1.0.0"

thresholds:
  go: 6.0
  maybe: 4.0
  no_go: 0.0

weights:
  coherence_metier: 0.20
  viabilite_financiere: 0.20
  accessibilite_geographique: 0.15
  faisabilite_temporelle: 0.20
  intelligence_concurrentielle: 0.25

behavior:
  require_strong_match: false
  penalize_high_risk: false
  prefer_new_markets: true
  
adjustments:
  coherence_metier:
    bonus_keywords: 1.0
    penalty_no_match: 1.0
  viabilite_financiere:
    bonus_high_amount: 1.0
    unknown_amount_neutral: true
  accessibilite_geographique:
    national_bonus: 1.0
    adjacent_ok: true
  faisabilite_temporelle:
    preparation_multiplier: 0.8
    urgent_ok: true
  intelligence_concurrentielle:
    bonus_new_market: 1.5
    no_history_bonus: 0.5
```

## FICHIER B-8 : `config/scoring/profiles/specialise.yaml`

**Role :** Configuration du profil de scoring "Specialise".

**Contenu attendu :**
```yaml
profile:
  id: specialise
  name: "Specialise"
  description: "Profil equilibre centre sur l'excellence metier avec analyse temporelle rigoureuse."
  version: "1.0.0"

thresholds:
  go: 7.0
  maybe: 4.5
  no_go: 0.0

weights:
  coherence_metier: 0.35
  viabilite_financiere: 0.20
  accessibilite_geographique: 0.20
  faisabilite_temporelle: 0.15
  intelligence_concurrentielle: 0.10

behavior:
  require_strong_match: true
  penalize_high_risk: false
  balanced_evaluation: true
  
adjustments:
  coherence_metier:
    bonus_exact_cpv: 1.0
    penalty_no_match: 1.5
    require_cpv: false
  viabilite_financiere:
    optimal_range_bonus: 0.5
    unknown_amount_neutral: true
  accessibilite_geographique:
    region_weight: 0.25
    adjacent_ok: true
  faisabilite_temporelle:
    preparation_multiplier: 1.0
    deadline_strict: true
  intelligence_concurrentielle:
    history_weight: 0.15
    no_history_neutral: true
```

---

# SECTION 7 - FICHIERS A PRODUIRE - Groupe C : Business Lines

## FICHIER C-1 : `lib/business-lines/models.ts`

**Role :** Types et interfaces pour le systeme de Business Lines.

**Contenu :**
```typescript
export interface BusinessLine {
  id: string;
  name: string;
  description: string | null;
  cpvCodes: string[];
  keywords: string[];
  color: string;
  scoringProfile: 'prudent' | 'opportuniste' | 'specialise';
  companyId: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserBusinessLine {
  id: string;
  userId: string;
  businessLineId: string;
  role: 'admin_bl' | 'member' | 'viewer';
  createdAt: string;
}

export interface BusinessLineWithRole extends BusinessLine {
  userRole: 'admin_bl' | 'member' | 'viewer';
}

export interface ScopeLevel {
  value: 'global' | 'business_line' | 'individuel' | 'readonly';
  label: string;
  description: string;
}

export const SCOPE_LEVELS: ScopeLevel[] = [
  { value: 'global', label: 'Global', description: 'Visible par toute l\'entreprise' },
  { value: 'business_line', label: 'Business Line', description: 'Visible par les membres de la BL' },
  { value: 'individuel', label: 'Individuel', description: 'Visible par l\'assignee' },
  { value: 'readonly', label: 'Lecture seule', description: 'Visible en lecture seule' },
];

export function canEditAO(
  ao: { scopeLevel: string; assignedTo?: string; businessLineId?: string },
  user: { id: string; role: string },
  userBLIds: string[]
): boolean {
  // Admin entreprise : peut tout editer
  if (user.role === 'admin') return true;
  
  // Global : seuls admin peuvent editer
  if (ao.scopeLevel === 'global') return false;
  
  // Individuel : l'assignee peut editer
  if (ao.scopeLevel === 'individuel' && ao.assignedTo === user.id) return true;
  
  // Business Line : membres de la BL peuvent editer (pas viewer)
  if (ao.scopeLevel === 'business_line' && ao.businessLineId) {
    const isMember = userBLIds.includes(ao.businessLineId);
    // Note : le role exact (member vs viewer) est verifie par RLS
    return isMember;
  }
  
  // Readonly : personne ne peut editer (sauf admin, deja traite)
  return false;
}

export function canViewAO(
  ao: { scopeLevel: string; assignedTo?: string; businessLineId?: string; companyId: string },
  user: { id: string; role: string; companyId: string },
  userBLIds: string[]
): boolean {
  // Verifier company
  if (ao.companyId !== user.companyId) return false;
  
  // Admin entreprise : tout voir
  if (user.role === 'admin') return true;
  
  // Global : tous les membres de l'entreprise
  if (ao.scopeLevel === 'global') return true;
  
  // Individuel : assignee ou admin
  if (ao.scopeLevel === 'individuel') {
    return ao.assignedTo === user.id;
  }
  
  // Business Line / Readonly : membres de la BL
  if (ao.businessLineId) {
    return userBLIds.includes(ao.businessLineId);
  }
  
  return false;
}
```

## FICHIER C-2 : `lib/business-lines/api.ts`

**Role :** Fonctions CRUD pour les Business Lines (client Supabase).

**Contenu :**
```typescript
import { createClient } from '@/lib/utils/supabase';
import { BusinessLine, UserBusinessLine, BusinessLineWithRole } from './models';

// ---- Business Lines ----

export async function getBusinessLines(companyId: string): Promise<BusinessLine[]> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('business_lines')
    .select('*')
    .eq('company_id', companyId)
    .order('name');
  
  if (error) throw new Error(`Erreur recuperation BL: ${error.message}`);
  return data || [];
}

export async function getBusinessLine(id: string): Promise<BusinessLine | null> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('business_lines')
    .select('*')
    .eq('id', id)
    .single();
  
  if (error && error.code !== 'PGRST116') throw error;
  return data;
}

export async function createBusinessLine(
  bl: Omit<BusinessLine, 'id' | 'createdAt' | 'updatedAt'>
): Promise<BusinessLine> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('business_lines')
    .insert({
      name: bl.name,
      description: bl.description,
      cpv_codes: bl.cpvCodes,
      keywords: bl.keywords,
      color: bl.color,
      scoring_profile: bl.scoringProfile,
      company_id: bl.companyId,
    })
    .select()
    .single();
  
  if (error) throw new Error(`Erreur creation BL: ${error.message}`);
  if (!data) throw new Error('Creation BL echouee');
  return data;
}

export async function updateBusinessLine(
  id: string,
  updates: Partial<Omit<BusinessLine, 'id' | 'createdAt' | 'updatedAt'>>
): Promise<BusinessLine> {
  const supabase = createClient();
  const dbUpdates: Record<string, unknown> = {};
  
  if (updates.name !== undefined) dbUpdates.name = updates.name;
  if (updates.description !== undefined) dbUpdates.description = updates.description;
  if (updates.cpvCodes !== undefined) dbUpdates.cpv_codes = updates.cpvCodes;
  if (updates.keywords !== undefined) dbUpdates.keywords = updates.keywords;
  if (updates.color !== undefined) dbUpdates.color = updates.color;
  if (updates.scoringProfile !== undefined) dbUpdates.scoring_profile = updates.scoringProfile;
  
  const { data, error } = await supabase
    .from('business_lines')
    .update(dbUpdates)
    .eq('id', id)
    .select()
    .single();
  
  if (error) throw new Error(`Erreur mise a jour BL: ${error.message}`);
  if (!data) throw new Error('Mise a jour BL echouee');
  return data;
}

export async function deleteBusinessLine(id: string): Promise<void> {
  const supabase = createClient();
  const { error } = await supabase
    .from('business_lines')
    .delete()
    .eq('id', id);
  
  if (error) throw new Error(`Erreur suppression BL: ${error.message}`);
}

// ---- User - Business Line associations ----

export async function getUserBusinessLines(userId: string): Promise<BusinessLineWithRole[]> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('user_business_lines')
    .select(`
      role,
      business_lines (*)
    `)
    .eq('user_id', userId);
  
  if (error) throw new Error(`Erreur recuperation user BL: ${error.message}`);
  
  return (data || []).map(row => ({
    ...(row.business_lines as unknown as BusinessLine),
    userRole: row.role as 'admin_bl' | 'member' | 'viewer',
  }));
}

export async function assignUserToBusinessLine(
  userId: string,
  businessLineId: string,
  role: 'admin_bl' | 'member' | 'viewer' = 'member'
): Promise<UserBusinessLine> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('user_business_lines')
    .insert({ user_id: userId, business_line_id: businessLineId, role })
    .select()
    .single();
  
  if (error) throw new Error(`Erreur assignation BL: ${error.message}`);
  if (!data) throw new Error('Assignation BL echouee');
  return data;
}

export async function removeUserFromBusinessLine(
  userId: string,
  businessLineId: string
): Promise<void> {
  const supabase = createClient();
  const { error } = await supabase
    .from('user_business_lines')
    .delete()
    .eq('user_id', userId)
    .eq('business_line_id', businessLineId);
  
  if (error) throw new Error(`Erreur desassignation BL: ${error.message}`);
}

// ---- Detection automatique BL ----

export async function detectBusinessLineForAO(
  ao: { cpvCode?: string | null; description?: string | null; title?: string | null },
  companyBLs: BusinessLine[]
): Promise<{ businessLineId: string | null; confidence: number }> {
  let bestMatch: { businessLineId: string | null; confidence: number; score: number } = {
    businessLineId: null,
    confidence: 0,
    score: 0,
  };
  
  const aoText = `${ao.title || ''} ${ao.description || ''}`.toLowerCase();
  
  for (const bl of companyBLs) {
    let score = 0;
    
    // CPV matching
    if (ao.cpvCode && bl.cpvCodes.length > 0) {
      const cpvPrefix5 = ao.cpvCode.substring(0, 5);
      const cpvPrefix3 = ao.cpvCode.substring(0, 3);
      
      if (bl.cpvCodes.some(c => c.substring(0, 5) === cpvPrefix5)) {
        score += 10;
      } else if (bl.cpvCodes.some(c => c.substring(0, 3) === cpvPrefix3)) {
        score += 5;
      }
    }
    
    // Keyword matching
    if (bl.keywords.length > 0 && aoText) {
      const keywordMatches = bl.keywords.filter(kw => aoText.includes(kw.toLowerCase())).length;
      score += keywordMatches * 2;
    }
    
    if (score > bestMatch.score) {
      bestMatch = {
        businessLineId: bl.id,
        confidence: Math.min(score / 20, 1), // Normaliser sur 20 points max
        score,
      };
    }
  }
  
  return {
    businessLineId: bestMatch.businessLineId,
    confidence: bestMatch.confidence,
  };
}
```

## FICHIER C-3 : `lib/business-lines/scope.ts`

**Role :** Gestion des niveaux de scope et des permissions pour les AO.

**Contenu :**
```typescript
import { ScopeLevel, SCOPE_LEVELS, canViewAO, canEditAO } from './models';
import { createClient } from '@/lib/utils/supabase';

export async function filterAOByScope(
  userId: string,
  companyId: string,
  userRole: string,
  baseQuery: any  // QueryBuilder Supabase
): Promise<any> {
  const supabase = createClient();
  
  // Recuperer les BL de l'utilisateur
  const { data: userBLs } = await supabase
    .from('user_business_lines')
    .select('business_line_id')
    .eq('user_id', userId);
  
  const blIds = (userBLs || []).map(row => row.business_line_id);
  
  if (userRole === 'admin') {
    // Admin : tout voir dans l'entreprise
    return baseQuery.eq('company_id', companyId);
  }
  
  // Membre standard : global + ses BL + individuel (s'il est assignee) + readonly de ses BL
  return baseQuery.or(
    `scope_level.eq.global,and(company_id.eq.${companyId}),` +
    `scope_level.eq.business_line,and(business_line_id.in.(${blIds.join(',')})),` +
    `scope_level.eq.individuel,and(assigned_to.eq.${userId}),` +
    `scope_level.eq.readonly,and(business_line_id.in.(${blIds.join(',')}))`
  );
}

export function getScopeLevelLabel(level: string): string {
  return SCOPE_LEVELS.find(s => s.value === level)?.label || level;
}

export function getScopeLevelDescription(level: string): string {
  return SCOPE_LEVELS.find(s => s.value === level)?.description || '';
}

export function getDefaultScopeLevel(userRole: string): ScopeLevel['value'] {
  if (userRole === 'admin') return 'business_line';
  return 'individuel';
}

export { canViewAO, canEditAO };
```

## FICHIER C-4 : `app/api/business-lines/route.ts`

**Role :** API REST pour les Business Lines.

**Routes :**
- `GET /api/business-lines` : Liste des BL de l'entreprise
- `POST /api/business-lines` : Creation d'une BL
- `GET /api/business-lines?detect=ao_id` : Detection de BL pour un AO

**GET :**
- Authentification requise
- Retourne les BL de la company de l'utilisateur
- Inclut le role de l'utilisateur dans chaque BL

**POST :**
- Body : `{ name, description?, cpvCodes[], keywords[], color?, scoringProfile? }`
- Validation Zod
- Seul admin ou manager peut creer
- Limite par plan (Free=1, Starter=3, Pro=10, Enterprise=illimite) - verifie via feature flag

**Detection :**
- Parametre query `detect=ao_id`
- Execute `detectBusinessLineForAO`
- Retourne `{ businessLineId, confidence, suggestedBLs[] }`

## FICHIER C-5 : `app/api/user-business-lines/route.ts`

**Role :** API REST pour les associations utilisateur-BL.

**Routes :**
- `GET /api/user-business-lines` : BL de l'utilisateur connecte
- `POST /api/user-business-lines` : Assigner un utilisateur a une BL
- `DELETE /api/user-business-lines` : Retirer un utilisateur d'une BL

**POST :**
- Body : `{ userId, businessLineId, role? }`
- Seul admin de l'entreprise ou admin_bl peut assigner
- L'utilisateur ne peut pas s'auto-assigner a moins d'etre admin

**Middleware :**
- Verifier que l'utilisateur cible est dans la meme entreprise
- Verifier les limites du plan (nombre de membres par BL)

---


# SECTION 8 - FICHIERS A PRODUIRE - Groupe D : Dashboard Admin

## FICHIER D-1 : `lib/dashboard/formulas.ts`

**Role :** Definitions des 15 KPIs avec leurs formules SQL et leurs types.

**Contenu :**
```typescript
export interface KPIFormula {
  id: string;
  name: string;
  description: string;
  sql: string;
  type: 'currency' | 'percentage' | 'number' | 'ratio' | 'days';
  format: string;  // pour Intl.NumberFormat
  category: 'pipeline' | 'performance' | 'activity' | 'quality';
}

export const KPI_FORMULAS: KPIFormula[] = [
  {
    id: 'ca_pipeline',
    name: 'CA Pipeline',
    description: 'Chiffre d\'affaires total des AO actifs (non non_retenus)',
    sql: `SELECT COALESCE(SUM(CASE WHEN montant_estime > 0 THEN montant_estime ELSE montant END), 0) FROM appels_offres WHERE status != 'non_retenu' AND company_id = :company_id`,
    type: 'currency',
    format: 'EUR',
    category: 'pipeline',
  },
  {
    id: 'taux_reussite',
    name: 'Taux de Reussite',
    description: 'Pourcentage d\'AO classes GO_v2',
    sql: `SELECT CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN verdict = 'GO_v2' THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END FROM score_cards WHERE company_id = :company_id`,
    type: 'percentage',
    format: 'percent',
    category: 'performance',
  },
  {
    id: 'ao_actifs',
    name: 'AO Actifs',
    description: 'Nombre d\'AO en cours de qualification ou qualifies',
    sql: `SELECT COUNT(*) FROM appels_offres WHERE status IN ('a_qualifier', 'qualifie', 'en_cours') AND company_id = :company_id`,
    type: 'number',
    format: 'integer',
    category: 'activity',
  },
  {
    id: 'ratio_go_nogo',
    name: 'Ratio GO / NO-GO',
    description: 'Ratio entre les AO GO_v2 et NO_GO_v2',
    sql: `SELECT CASE WHEN COUNT(CASE WHEN verdict = 'NO_GO_v2' THEN 1 END) > 0 THEN ROUND(COUNT(CASE WHEN verdict = 'GO_v2' THEN 1 END) * 1.0 / COUNT(CASE WHEN verdict = 'NO_GO_v2' THEN 1 END), 2) ELSE 0 END FROM score_cards WHERE company_id = :company_id`,
    type: 'ratio',
    format: 'decimal',
    category: 'performance',
  },
  {
    id: 'ca_moyen_go',
    name: 'CA Moyen GO',
    description: 'Montant moyen des AO classes GO_v2',
    sql: `SELECT COALESCE(AVG(CASE WHEN a.montant_estime > 0 THEN a.montant_estime ELSE a.montant END), 0) FROM appels_offres a JOIN score_cards s ON s.appel_offre_id = a.id WHERE s.verdict = 'GO_v2' AND a.company_id = :company_id`,
    type: 'currency',
    format: 'EUR',
    category: 'pipeline',
  },
  {
    id: 'delai_moyen_qualif',
    name: 'Delai Moyen Qualification',
    description: 'Temps moyen entre creation et qualification',
    sql: `SELECT COALESCE(AVG(EXTRACT(EPOCH FROM (s.created_at - a.created_at)) / 86400), 0) FROM appels_offres a JOIN score_cards s ON s.appel_offre_id = a.id WHERE a.company_id = :company_id`,
    type: 'days',
    format: 'decimal',
    category: 'quality',
  },
  {
    id: 'taux_conversion',
    name: 'Taux de Conversion',
    description: 'Pourcentage d\'AO GO_v2 qui aboutissent a un gain',
    sql: `SELECT CASE WHEN COUNT(CASE WHEN verdict = 'GO_v2' THEN 1 END) > 0 THEN ROUND(COUNT(CASE WHEN verdict = 'GO_v2' AND a.status = 'gagne' THEN 1 END) * 100.0 / COUNT(CASE WHEN verdict = 'GO_v2' THEN 1 END), 2) ELSE 0 END FROM score_cards s JOIN appels_offres a ON a.id = s.appel_offre_id WHERE a.company_id = :company_id`,
    type: 'percentage',
    format: 'percent',
    category: 'performance',
  },
  {
    id: 'activite_30j',
    name: 'Activite 30 Jours',
    description: 'Nombre d\'AO crees les 30 derniers jours',
    sql: `SELECT COUNT(*) FROM appels_offres WHERE created_at >= NOW() - INTERVAL '30 days' AND company_id = :company_id`,
    type: 'number',
    format: 'integer',
    category: 'activity',
  },
  {
    id: 'top_bl_ca',
    name: 'Top BL par CA',
    description: 'Classement des Business Lines par chiffre d\'affaires',
    sql: `SELECT b.name, COALESCE(SUM(CASE WHEN a.montant_estime > 0 THEN a.montant_estime ELSE a.montant END), 0) as total FROM appels_offres a LEFT JOIN business_lines b ON b.id = a.business_line_id WHERE a.status != 'non_retenu' AND a.company_id = :company_id GROUP BY b.id, b.name ORDER BY total DESC`,
    type: 'currency',
    format: 'EUR',
    category: 'pipeline',
  },
  {
    id: 'taux_maybe',
    name: 'Taux MAYBE',
    description: 'Pourcentage d\'AO classes MAYBE_v2',
    sql: `SELECT CASE WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN verdict = 'MAYBE_v2' THEN 1 END) * 100.0 / COUNT(*), 2) ELSE 0 END FROM score_cards WHERE company_id = :company_id`,
    type: 'percentage',
    format: 'percent',
    category: 'performance',
  },
  {
    id: 'ao_retard',
    name: 'AO en Retard',
    description: 'AO dont la deadline est dans moins de 7 jours',
    sql: `SELECT COUNT(*) FROM appels_offres WHERE date_limite <= NOW() + INTERVAL '7 days' AND date_limite >= NOW() AND status NOT IN ('gagne', 'non_retenu', 'abandonne') AND company_id = :company_id`,
    type: 'number',
    format: 'integer',
    category: 'quality',
  },
  {
    id: 'marge_moyenne',
    name: 'Marge Moyenne',
    description: 'Marge estimee moyenne des AO GO_v2',
    sql: `SELECT COALESCE(AVG(a.marge_estimee), 0) FROM appels_offres a JOIN score_cards s ON s.appel_offre_id = a.id WHERE s.verdict = 'GO_v2' AND a.company_id = :company_id`,
    type: 'percentage',
    format: 'percent',
    category: 'pipeline',
  },
  {
    id: 'nouveaux_ao_7j',
    name: 'Nouveaux AO 7j',
    description: 'AO crees les 7 derniers jours',
    sql: `SELECT COUNT(*) FROM appels_offres WHERE created_at >= NOW() - INTERVAL '7 days' AND company_id = :company_id`,
    type: 'number',
    format: 'integer',
    category: 'activity',
  },
  {
    id: 'taux_participation',
    name: 'Taux de Participation',
    description: 'AO pour lesquels une soumission a ete envoyee / AO GO_v2',
    sql: `SELECT CASE WHEN COUNT(CASE WHEN verdict = 'GO_v2' THEN 1 END) > 0 THEN ROUND(COUNT(CASE WHEN verdict = 'GO_v2' AND a.soumission_envoyee = true THEN 1 END) * 100.0 / COUNT(CASE WHEN verdict = 'GO_v2' THEN 1 END), 2) ELSE 0 END FROM score_cards s JOIN appels_offres a ON a.id = s.appel_offre_id WHERE a.company_id = :company_id`,
    type: 'percentage',
    format: 'percent',
    category: 'performance',
  },
  {
    id: 'score_moyen_global',
    name: 'Score Moyen Global',
    description: 'Score moyen de tous les ScoreCards',
    sql: `SELECT COALESCE(AVG(overall_score), 0) FROM score_cards WHERE company_id = :company_id`,
    type: 'number',
    format: 'decimal_2',
    category: 'quality',
  },
];

export function getKPIFormula(id: string): KPIFormula | undefined {
  return KPI_FORMULAS.find(k => k.id === id);
}

export function getKPIsByCategory(category: KPIFormula['category']): KPIFormula[] {
  return KPI_FORMULAS.filter(k => k.category === category);
}

export function formatKPIValue(value: number, formula: KPIFormula): string {
  switch (formula.type) {
    case 'currency':
      return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR',
        maximumFractionDigits: 0,
      }).format(value);
    
    case 'percentage':
      return new Intl.NumberFormat('fr-FR', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      }).format(value / 100);
    
    case 'number':
      return new Intl.NumberFormat('fr-FR', {
        maximumFractionDigits: 0,
      }).format(value);
    
    case 'ratio':
      return value.toFixed(2);
    
    case 'days':
      return `${value.toFixed(1)} j`;
    
    default:
      return String(value);
  }
}
```

## FICHIER D-2 : `lib/dashboard/kpis.ts`

**Role :** Service de calcul des KPIs via Supabase RPC ou requetes directes.

**Contenu :**
```typescript
import { createClient } from '@/lib/utils/supabase';
import { KPI_FORMULAS, KPIFormula, formatKPIValue } from './formulas';

export interface KPIResult {
  formula: KPIFormula;
  value: number;
  formatted: string;
  previousValue?: number;
  evolution?: number;  // en pourcentage
}

export async function computeKPI(
  kpiId: string,
  companyId: string,
  options?: {
    businessLineId?: string;
    period?: '7d' | '30d' | '90d' | '12m';
    comparePrevious?: boolean;
  }
): Promise<KPIResult> {
  const formula = KPI_FORMULAS.find(k => k.id === kpiId);
  if (!formula) throw new Error(`KPI inconnu: ${kpiId}`);
  
  const supabase = createClient();
  
  // Construire la requete avec parametres
  let sql = formula.sql;
  
  // Filtrage par BL si specifie
  if (options?.businessLineId) {
    sql = sql.replace(/company_id = :company_id/g, 
      `company_id = :company_id AND business_line_id = '${options.businessLineId}'`);
  }
  
  // Periode si specifiee
  if (options?.period) {
    const interval = options.period === '12m' ? '1 year' : 
                     options.period === '90d' ? '90 days' :
                     options.period === '30d' ? '30 days' : '7 days';
    sql = sql.replace(/WHERE /g, `WHERE created_at >= NOW() - INTERVAL '${interval}' AND `);
  }
  
  // Executer via RPC ou requete directe
  const { data, error } = await supabase.rpc('execute_kpi_query', {
    query_sql: sql,
    company_id_param: companyId,
  });
  
  if (error) {
    // Fallback : executer la requete en direct (moins performant mais plus flexible)
    const { data: directData, error: directError } = await supabase
      .from('appels_offres')
      .select('id')
      .limit(1);  // Test de connexion
    
    if (directError) throw new Error(`Erreur KPI ${kpiId}: ${directError.message}`);
    
    // Calcul manuel simplifie si RPC non disponible
    const value = await computeKPIFallback(kpiId, companyId, options);
    
    return {
      formula,
      value,
      formatted: formatKPIValue(value, formula),
    };
  }
  
  const value = extractValueFromResult(data, formula);
  
  // Comparaison periode precedente
  let previousValue: number | undefined;
  let evolution: number | undefined;
  
  if (options?.comparePrevious && options?.period) {
    previousValue = await computeKPIPreviousPeriod(kpiId, companyId, options);
    if (previousValue !== undefined && previousValue !== 0) {
      evolution = ((value - previousValue) / previousValue) * 100;
    }
  }
  
  return {
    formula,
    value,
    formatted: formatKPIValue(value, formula),
    previousValue,
    evolution,
  };
}

export async function computeAllKPIs(
  companyId: string,
  options?: {
    businessLineId?: string;
    period?: '7d' | '30d' | '90d' | '12m';
    comparePrevious?: boolean;
  }
): Promise<KPIResult[]> {
  const results: KPIResult[] = [];
  
  for (const formula of KPI_FORMULAS) {
    try {
      const result = await computeKPI(formula.id, companyId, options);
      results.push(result);
    } catch (err) {
      console.error(`Erreur calcul KPI ${formula.id}:`, err);
      results.push({
        formula,
        value: 0,
        formatted: 'N/A',
      });
    }
  }
  
  return results;
}

async function computeKPIFallback(
  kpiId: string,
  companyId: string,
  options?: { businessLineId?: string; period?: string }
): Promise<number> {
  const supabase = createClient();
  
  // Implementation simplifiee en fallback
  switch (kpiId) {
    case 'ca_pipeline': {
      let query = supabase
        .from('appels_offres')
        .select('montant, montant_estime')
        .neq('status', 'non_retenu')
        .eq('company_id', companyId);
      
      if (options?.businessLineId) query = query.eq('business_line_id', options.businessLineId);
      
      const { data } = await query;
      if (!data) return 0;
      return data.reduce((sum, row) => sum + (row.montant_estime || row.montant || 0), 0);
    }
    
    case 'ao_actifs': {
      let query = supabase
        .from('appels_offres')
        .select('*', { count: 'exact', head: true })
        .in('status', ['a_qualifier', 'qualifie', 'en_cours'])
        .eq('company_id', companyId);
      
      if (options?.businessLineId) query = query.eq('business_line_id', options.businessLineId);
      
      const { count } = await query;
      return count || 0;
    }
    
    default:
      return 0;
  }
}

function extractValueFromResult(data: unknown, formula: KPIFormula): number {
  if (Array.isArray(data) && data.length > 0) {
    const row = data[0];
    // Essayer de trouver la valeur dans la premiere ligne
    const keys = Object.keys(row as object);
    if (keys.length === 1) {
      return Number((row as Record<string, unknown>)[keys[0]]) || 0;
    }
    // Chercher une propriete specifique
    for (const key of ['count', 'sum', 'avg', 'total', 'value', formula.id]) {
      if ((row as Record<string, unknown>)[key] !== undefined) {
        return Number((row as Record<string, unknown>)[key]) || 0;
      }
    }
  }
  return Number(data) || 0;
}

async function computeKPIPreviousPeriod(
  kpiId: string,
  companyId: string,
  options: { period: string; businessLineId?: string }
): Promise<number> {
  // Deplacer la periode en arriere (doubler l'intervalle)
  // Pour 30d : calculer sur les 30 jours precedents (il y a 30 a 60 jours)
  // Implementation simplifiee
  return 0;
}
```

## FICHIER D-3 : `lib/dashboard/benchmark.ts`

**Role :** Benchmarking interne entre Business Lines.

**Contenu :**
```typescript
import { createClient } from '@/lib/utils/supabase';

export interface BLBenchmark {
  businessLineId: string;
  businessLineName: string;
  color: string;
  kpiValues: Record<string, number>;
  rank: number;
}

export async function computeBLBenchmark(
  companyId: string,
  kpiIds: string[]
): Promise<BLBenchmark[]> {
  const supabase = createClient();
  
  // Recuperer les BL
  const { data: bls } = await supabase
    .from('business_lines')
    .select('id, name, color')
    .eq('company_id', companyId);
  
  if (!bls) return [];
  
  const benchmarks: BLBenchmark[] = [];
  
  for (const bl of bls) {
    const kpiValues: Record<string, number> = {};
    
    for (const kpiId of kpiIds) {
      // Requete RPC ou directe par BL
      const { data } = await supabase.rpc('get_kpi_by_bl', {
        p_company_id: companyId,
        p_business_line_id: bl.id,
        p_kpi_id: kpiId,
      });
      
      kpiValues[kpiId] = extractValue(data);
    }
    
    benchmarks.push({
      businessLineId: bl.id,
      businessLineName: bl.name,
      color: bl.color,
      kpiValues,
      rank: 0,  // Calcul plus tard
    });
  }
  
  // Calculer le ranking pour chaque KPI
  for (const kpiId of kpiIds) {
    const sorted = [...benchmarks].sort((a, b) => b.kpiValues[kpiId] - a.kpiValues[kpiId]);
    sorted.forEach((bl, index) => {
      // Accumuler le rang (plus petit = meilleur)
      bl.rank += index + 1;
    });
  }
  
  // Trier par rang total
  benchmarks.sort((a, b) => a.rank - b.rank);
  
  return benchmarks;
}

function extractValue(data: unknown): number {
  if (Array.isArray(data) && data.length > 0) {
    const row = data[0];
    const keys = Object.keys(row as object);
    return Number((row as Record<string, unknown>)[keys[0]]) || 0;
  }
  return Number(data) || 0;
}
```

## FICHIER D-4 : `app/api/dashboard/admin/route.ts`

**Role :** API REST pour le Dashboard Admin.

**Routes :**
- `GET /api/dashboard/admin?period=30d&bl=uuid` : Recuperer toutes les donnees du dashboard

**Reponse :**
```typescript
interface AdminDashboardData {
  kpis: KPIResult[];
  charts: {
    repartitionBL: Array<{ name: string; value: number; color: string }>;
    evolution12M: Array<{ month: string; go: number; maybe: number; noGo: number }>;
    repartitionVerdicts: Array<{ name: string; value: number }>;
    topCollaborateurs: Array<{ name: string; qualifications: number; goRate: number }>;
  };
  tables: {
    suiviCollaborateurs: Array<{
      userId: string;
      name: string;
      aoTotal: number;
      aoActifs: number;
      goCount: number;
      noGoCount: number;
      maybeCount: number;
      caPipeline: number;
    }>;
    pipeline: Array<{
      id: string;
      title: string;
      businessLine: string;
      montant: number;
      verdict: string;
      score: number;
      deadline: string;
      assignedTo: string;
    }>;
  };
  alertes: Array<{
    type: 'deadline' | 'retard_qualif' | 'nouveau' | 'marge_faible';
    severity: 'critical' | 'warning' | 'info';
    message: string;
    aoId?: string;
    date: string;
  }>;
  actions: Array<{
    id: string;
    label: string;
    href: string;
    icon: string;
  }>;
  insights: {
    topRecommendation: string;
    warnings: string[];
    trends: string[];
  };
}
```

**Logique :**
1. Authentification + verif role admin/manager
2. Recuperer company_id
3. Executer les 15 KPIs via `computeAllKPIs`
4. Generer les graphiques via requetes aggregees
5. Generer les tableaux via requetes jointes
6. Generer les alertes via requetes filtrees
7. Generer les insights (TAKA LAB basic : regles simples)
8. Retourner JSON complet

**Performance :**
- Executer les requetes en parallele (Promise.all) ou via Promise.allSettled
- Utiliser des vues materielles si disponibles (Supabase ne supporte pas les vues materielles, utiliser des fonctions RPC)
- Caching : mettre en cache le resultat 5 minutes cote serveur (Next.js unstable_cache)

## FICHIER D-5 : `components/dashboard/admin/KPICard.tsx`

**Role :** Composant carte KPI pour le Dashboard Admin.

**Props :**
```typescript
interface KPICardProps {
  title: string;
  value: string;
  previousValue?: string;
  evolution?: number;  // en pourcentage
  icon: React.ReactNode;
  color: 'blue' | 'emerald' | 'amber' | 'rose' | 'purple' | 'indigo';
  loading?: boolean;
}
```

**Design :**
- Card shadcn/ui avec header (icon + titre) et body (valeur)
- Si `evolution` present : badge avec fleche (up/down) et pourcentage
  - Vert si evolution positive pour un KPI "bon" (ca_pipeline, taux_reussite)
  - Rouge si evolution positive pour un KPI "mauvais" (ao_retard, delai_moyen_qualif)
- Skeleton pendant le loading
- Responsive : 1 colonne mobile, 2-3 colonnes desktop

## FICHIER D-6 : `components/dashboard/admin/ChartRepartition.tsx`

**Role :** Graphique de repartition des AO par Business Line (PieChart ou Donut).

**Props :**
```typescript
interface ChartRepartitionProps {
  data: Array<{ name: string; value: number; color: string }>;
  title?: string;
}
```

**Implementation :**
- Recharts PieChart avec Cell coloree
- Legend affichee a droite
- Tooltip au survol
- Si plus de 6 BL : grouper les plus petites en "Autres"
- Responsive container

## FICHIER D-7 : `components/dashboard/admin/ChartEvolution.tsx`

**Role :** Graphique d'evolution des veredicts sur 12 mois (BarChart empile).

**Props :**
```typescript
interface ChartEvolutionProps {
  data: Array<{
    month: string;
    go: number;
    maybe: number;
    noGo: number;
  }>;
  title?: string;
}
```

**Implementation :**
- Recharts BarChart avec Bar empilees
- Couleurs : GO=emerald, MAYBE=amber, NO-GO=rose
- XAxis : mois au format "Jan 2024"
- Tooltip detaille
- Legend
- Responsive container

## FICHIER D-8 : `components/dashboard/admin/ChartRadarBL.tsx`

**Role :** Radar chart comparant les performances des BL sur 5 axes (les 5 dimensions de scoring).

**Props :**
```typescript
interface ChartRadarBLProps {
  data: Array<{
    businessLine: string;
    coherence: number;
    financier: number;
    geographique: number;
    temporel: number;
    concurrentiel: number;
  }>;
}
```

**Implementation :**
- Recharts RadarChart
- 5 axes pour les 5 dimensions
- Plusieurs BL = plusieurs Radar series
- Couleurs distinctes par BL

## FICHIER D-9 : `components/dashboard/admin/TableSuivi.tsx`

**Role :** Tableau de suivi par collaborateur.

**Props :**
```typescript
interface TableSuiviProps {
  data: Array<{
    userId: string;
    name: string;
    aoTotal: number;
    aoActifs: number;
    goCount: number;
    noGoCount: number;
    maybeCount: number;
    caPipeline: number;
  }>;
}
```

**Implementation :**
- shadcn/ui Table
- Colonnes : Nom, Total AO, Actifs, GO, NO-GO, MAYBE, CA Pipeline
- Tri cliquable sur chaque colonne
- Barre de recherche
- Pagination (10 lignes par defaut)
- Formatage : CA en EUR, nombres en integer

## FICHIER D-10 : `components/dashboard/admin/TablePipeline.tsx`

**Role :** Tableau du pipeline synthetique.

**Props :**
```typescript
interface TablePipelineProps {
  data: Array<{
    id: string;
    title: string;
    businessLine: string;
    montant: number;
    verdict: string;
    score: number;
    deadline: string;
    assignedTo: string;
  }>;
}
```

**Implementation :**
- shadcn/ui Table
- Colonnes : Titre, BL (avec badge colore), Montant, Verdict (badge GO/NO/MAYBE), Score, Deadline, Assignee
- Lien cliquable vers la page detail de l'AO
- Badge verdict colore (emerald/rose/amber)
- Deadline en rouge si < 7 jours

## FICHIER D-11 : `components/dashboard/admin/AlertesPrioritaires.tsx`

**Role :** Widget d'alertes prioritaires.

**Props :**
```typescript
interface AlertesPrioritairesProps {
  alertes: Array<{
    type: 'deadline' | 'retard_qualif' | 'nouveau' | 'marge_faible';
    severity: 'critical' | 'warning' | 'info';
    message: string;
    aoId?: string;
    date: string;
  }>;
  maxDisplay?: number;
}
```

**Implementation :**
- shadcn/ui Alert variant selon severity
- Icon selon type (clock pour deadline, alert-triangle pour retard, bell pour nouveau, trending-down pour marge)
- Maximum 5 alertes affichees par defaut, bouton "Voir tout" si plus
- Classees par severity (critical d'abord) puis date
- Lien vers l'AO concerne si aoId present

## FICHIER D-12 : `components/dashboard/admin/ActionsRapides.tsx`

**Role :** Widget d'actions rapides pour le manager.

**Props :**
```typescript
interface ActionsRapidesProps {
  actions: Array<{
    id: string;
    label: string;
    href: string;
    icon: string;
    variant?: 'default' | 'outline' | 'secondary';
  }>;
}
```

**Implementation :**
- shadcn/ui Button en grille de 2 colonnes
- Actions par defaut :
  1. "Nouvel AO" -> /ao/nouveau
  2. "Gerer les BL" -> /admin/business-lines
  3. "Rapport hebdo" -> /admin/reports
  4. "Parametres scoring" -> /admin/scoring
  5. "Exporter donnees" -> /admin/export
  6. "Inviter membre" -> /admin/team
- Icon Lucide selon l'action

## FICHIER D-13 : `components/dashboard/admin/InsightsIA.tsx`

**Role :** Widget d'insights generiques (TAKA LAB basic).

**Props :**
```typescript
interface InsightsIAProps {
  insights: {
    topRecommendation: string;
    warnings: string[];
    trends: string[];
  };
}
```

**Implementation :**
- Card avec header "Insights" et icon Sparkles
- Section "Recommandation" : texte en gras avec background subtile
- Section "Alertes" : liste de warnings avec icon AlertTriangle
- Section "Tendances" : liste avec icon TrendingUp/TrendingDown selon direction
- Design soigne avec couleurs adaptees (warning en amber, trend positive en emerald)

**Generation des insights (cote API) :**
Regles simples sans IA externe (pour limiter les couts) :
- "Top Recommendation" : si taux_reussite < 30% -> "Revoyez les criteres de scoring. Taux de reussite faible."
- "Warning" : si ao_retard > 3 -> "{{count}} AO en retard de qualification."
- "Trend" : si activite_30j > activite_30j_prev * 1.2 -> "Activite en hausse de {{pct}}% ce mois."

## FICHIER D-14 : `app/(dashboard)/admin/page.tsx`

**Role :** Page Dashboard Admin principale.

**Structure :**
```tsx
export default function AdminDashboardPage() {
  // 1. Verifier auth + role admin/manager
  // 2. Recuperer les donnees via API
  // 3. Afficher la grille de widgets
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Tableau de Bord Manager</h1>
      
      {/* KPIs Cards - 4 colonnes desktop, 2 tablet, 1 mobile */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map(kpi => <KPICard key={kpi.formula.id} ... />)}
      </div>
      
      {/* Graphiques - 2 colonnes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartRepartition data={charts.repartitionBL} />
        <ChartEvolution data={charts.evolution12M} />
      </div>
      
      {/* Radar BL */}
      <div className="grid grid-cols-1 gap-6">
        <ChartRadarBL data={benchmarkData} />
      </div>
      
      {/* Tableaux */}
      <div className="grid grid-cols-1 gap-6">
        <h2 className="text-xl font-semibold">Suivi des Collaborateurs</h2>
        <TableSuivi data={tables.suiviCollaborateurs} />
        
        <h2 className="text-xl font-semibold">Pipeline Actif</h2>
        <TablePipeline data={tables.pipeline} />
      </div>
      
      {/* Alertes + Actions + Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <AlertesPrioritaires alertes={alertes} />
        <ActionsRapides actions={actions} />
        <InsightsIA insights={insights} />
      </div>
    </div>
  );
}
```

**Regles :**
- Skeleton loading sur tous les widgets pendant le chargement
- Error boundary par widget (un widget en erreur n'ecrase pas les autres)
- Refresh automatique toutes les 5 minutes
- Bouton "Rafraichir" manuel
- Selecteur de BL ("Toutes" ou BL specifique) qui filtre tous les widgets
- Selecteur de periode (7j, 30j, 90j, 12m)

---

# SECTION 9 - FICHIERS A PRODUIRE - Groupe E : Dashboard Collaborateur

## FICHIER E-1 : `app/(dashboard)/kanban/page.tsx`

**Role :** Page Kanban du collaborateur (mise a jour avec nouveaux veredicts V2).

**Mise a jour par rapport au Sprint 1 :**
- Les veredicts sont maintenant GO_v2, NO_GO_v2, MAYBE_v2
- Filtrage par Business Line via selecteur
- Affichage du score sur chaque carte
- Couleurs des dimensions sur la carte
- Drag-drop persiste le statut en base

**Colonnes :**
1. "A qualifier" (status: a_qualifier) - couleur slate
2. "Qualifies GO" (status: qualifie + verdict: GO_v2) - couleur emerald
3. "Qualifies MAYBE" (status: qualifie + verdict: MAYBE_v2) - couleur amber
4. "En cours" (status: en_cours) - couleur blue
5. "Non retenus" (status: non_retenu) - couleur rose

**Carte AO :**
- Titre tronque (2 lignes max)
- Badge BL (couleur de la BL)
- Montant formate
- Score circulaire (petit badge avec score/10)
- Deadline avec countdown
- Icone verdict (check, question, x)

## FICHIER E-2 : `components/dashboard/collaborator/KanbanBoard.tsx`

**Role :** Composant Kanban board principal (drag-drop).

**Props :**
```typescript
interface KanbanBoardProps {
  businessLineId?: string;  // filtre par BL
  userId: string;
}
```

**Implementation :**
- @hello-pangea/dnd (support SSR Next.js)
- DragDropContext + Droppable (par colonne) + Draggable (par carte)
- Columns : array de configuration
- OnDragEnd : update status en base + optimistic update UI
- Si colonne "Qualifies GO/MAYBE" : grouper par verdict
- Keyboard support : Tab navigation, Space pour drag, fleches pour deplacer

**Accessibility :**
- aria-label sur chaque colonne ("Colonne A qualifier, 5 elements")
- aria-describedby sur chaque carte
- reduced-motion : desactiver l'animation drag

## FICHIER E-3 : `components/dashboard/collaborator/KanbanColumn.tsx`

**Role :** Composant colonne du Kanban.

**Props :**
```typescript
interface KanbanColumnProps {
  id: string;
  title: string;
  color: string;
  items: KanbanItem[];
  onDragEnd: (result: DropResult) => void;
}
```

**Implementation :**
- Header : titre + badge count + couleur laterale
- Droppable avec droppableId
- Liste de KanbanCard
- Placeholder quand vide ("Glissez un AO ici")
- Scroll vertical si trop d'items (max-h avec overflow-y-auto)

## FICHIER E-4 : `components/dashboard/collaborator/KanbanCard.tsx`

**Role :** Composant carte AO dans le Kanban.

**Props :**
```typescript
interface KanbanCardProps {
  ao: {
    id: string;
    title: string;
    montant: number | null;
    montantEstime: number | null;
    dateLimite: string | null;
    status: string;
    businessLine: { name: string; color: string } | null;
    scoreCard: { overallScore: number; verdict: string } | null;
  };
  index: number;
}
```

**Design :**
- Card compacte (padding 3)
- Titre : font-medium, truncate 2 lignes
- Footer : badge montant + badge score + icon deadline
- Score badge : cercle avec score/10, couleur selon score (>=7.5 vert, >=5 orange, <5 rouge)
- Deadline : texte en rouge si < 3 jours, orange si < 7 jours
- Hover : shadow-md + translateY -2px (transition 200ms)

## FICHIER E-5 : `components/dashboard/collaborator/NotificationBell.tsx`

**Role :** Cloche de notification pour le collaborateur.

**Props :**
```typescript
interface NotificationBellProps {
  userId: string;
}
```

**Implementation :**
- Icon Bell avec badge de compteur si > 0 notifications non lues
- Dropdown au clic (shadcn/ui DropdownMenu ou Popover)
- Liste des notifications recentes (7 derniers jours)
- Types : nouvel AO assigne, deadline proche, qualification terminee, feedback recu
- Marquer comme lu
- Lien vers l'AO concerne

## FICHIER E-6 : `app/(dashboard)/score-card/[id]/page.tsx`

**Role :** Page detail d'un ScoreCard.

**Structure :**
```tsx
export default function ScoreCardPage({ params }: { params: { id: string } }) {
  // 1. Recuperer le ScoreCard avec les 5 dimensions
  // 2. Recuperer l'AO associe
  // 3. Verifier permissions (user peut voir cet AO ?)
  
  return (
    <div className="space-y-6">
      <h1>ScoreCard : {ao.title}</h1>
      
      {/* Resume */}
      <ScoreCardSummary verdict={scoreCard.verdict} overallScore={scoreCard.overallScore} />
      
      {/* Radar Chart */}
      <ScoreCardRadar dimensions={scoreCard.dimensions} />
      
      {/* Details par dimension */}
      {scoreCard.dimensions.map(dim => (
        <DimensionScore key={dim.name} dimension={dim} />
      ))}
      
      {/* Explication XAI */}
      <XAIExplanationCard explanation={scoreCard.xaiExplanation} />
      
      {/* Feedback */}
      <ScoreFeedback scoreCardId={scoreCard.id} />
    </div>
  );
}
```

## FICHIER E-7 : `components/scoring/ScoreCardRadar.tsx`

**Role :** Radar chart des 5 dimensions de scoring.

**Props :**
```typescript
interface ScoreCardRadarProps {
  dimensions: Array<{
    name: string;
    displayName: string;
    score: number;
    weight: number;
  }>;
  size?: number;
}
```

**Implementation :**
- Recharts RadarChart
- 5 axes : coherence, financier, geo, temporel, concurrentiel
- Radar avec fill semi-transparent (couleur selon verdict)
- Score affiche sur chaque axe
- Responsive (size adapte au conteneur)

## FICHIER E-8 : `components/scoring/DimensionScore.tsx`

**Role :** Carte detaillee d'une dimension de scoring.

**Props :**
```typescript
interface DimensionScoreProps {
  dimension: {
    name: string;
    displayName: string;
    score: number;
    weight: number;
    confidence: number;
    explanation: string;
    rawData: Record<string, unknown>;
    rulesTriggered: string[];
  };
}
```

**Implementation :**
- Card avec header (nom + score/10 badge + weight en %)
- Barre de progression (score * 10%)
- Couleur de la barre selon score (>=7 vert, >=4 orange, <4 rouge)
- Section "Explication" : texte
- Section "Confiance" : badge (Haute/Moyenne/Faible)
- Section "Regles declenchees" : liste de badges
- Section "Donnees brutes" : table key-value (collapsible)

## FICHIER E-9 : `components/scoring/ScoreFeedback.tsx`

**Role :** Formulaire de feedback sur un ScoreCard.

**Props :**
```typescript
interface ScoreFeedbackProps {
  scoreCardId: string;
  dimensionName?: string;  // si null = feedback global
}
```

**Implementation :**
- Boutons radio : "Trop severe", "Trop lenient", "Incorrect", "Autre"
- Champ texte optionnel pour commentaire
- Bouton "Envoyer"
- Message de confirmation
- Affichage des stats de feedback existantes (nombre de feedbacks similaires)

---


# SECTION 10 - FICHIERS A PRODUIRE - Groupe F : Feature Flags

## FICHIER F-1 : `lib/feature-flags/service.ts`

**Role :** Service de gestion des Feature Flags.

**Contenu :**
```typescript
import { createClient } from '@/lib/utils/supabase';

export interface FeatureFlag {
  id: string;
  name: string;
  description: string | null;
  plansAllowed: string[];
  defaultEnabled: boolean;
  killSwitch: boolean;
  createdAt: string;
  updatedAt: string;
}

export type Plan = 'free' | 'starter' | 'pro' | 'enterprise';

export const PLAN_HIERARCHY: Record<Plan, number> = {
  free: 0,
  starter: 1,
  pro: 2,
  enterprise: 3,
};

export async function getFeatureFlags(): Promise<FeatureFlag[]> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('feature_flags')
    .select('*')
    .order('name');
  
  if (error) throw new Error(`Erreur recuperation flags: ${error.message}`);
  return data || [];
}

export async function getFeatureFlag(name: string): Promise<FeatureFlag | null> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('feature_flags')
    .select('*')
    .eq('name', name)
    .single();
  
  if (error && error.code !== 'PGRST116') throw error;
  return data;
}

export async function isFeatureEnabled(
  flagName: string,
  userPlan: Plan
): Promise<boolean> {
  const flag = await getFeatureFlag(flagName);
  
  if (!flag) {
    // Flag inconnu = desactive par securite
    console.warn(`Feature flag inconnu: ${flagName}`);
    return false;
  }
  
  // Kill switch prime sur tout
  if (flag.killSwitch) return false;
  
  // Verifier si le plan de l'utilisateur est autorise
  const userPlanLevel = PLAN_HIERARCHY[userPlan];
  const allowedLevels = flag.plansAllowed.map(p => PLAN_HIERARCHY[p as Plan]);
  
  return allowedLevels.some(level => userPlanLevel >= level);
}

export async function getUserPlan(userId: string): Promise<Plan> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('user_plans')
    .select('plan')
    .eq('user_id', userId)
    .single();
  
  if (error || !data) return 'free';
  return data.plan as Plan;
}

export async function getUserPlanLimits(userId: string): Promise<{
  plan: Plan;
  aoLimitMonthly: number;
  blLimit: number;
  scoringDimensionsEnabled: number;
}> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from('user_plans')
    .select('*')
    .eq('user_id', userId)
    .single();
  
  if (error || !data) {
    return {
      plan: 'free',
      aoLimitMonthly: 10,
      blLimit: 1,
      scoringDimensionsEnabled: 3,
    };
  }
  
  return {
    plan: data.plan as Plan,
    aoLimitMonthly: data.ao_limit_monthly,
    blLimit: data.bl_limit,
    scoringDimensionsEnabled: data.scoring_dimensions_enabled,
  };
}

export async function checkAOLimit(userId: string): Promise<{
  allowed: boolean;
  current: number;
  limit: number;
  remaining: number;
}> {
  const limits = await getUserPlanLimits(userId);
  
  const supabase = createClient();
  const { count, error } = await supabase
    .from('appels_offres')
    .select('*', { count: 'exact', head: true })
    .eq('created_by', userId)
    .gte('created_at', new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString());
  
  if (error) throw error;
  
  const current = count || 0;
  return {
    allowed: current < limits.aoLimitMonthly,
    current,
    limit: limits.aoLimitMonthly,
    remaining: Math.max(0, limits.aoLimitMonthly - current),
  };
}

export async function checkBLLimit(userId: string, companyId: string): Promise<{
  allowed: boolean;
  current: number;
  limit: number;
  remaining: number;
}> {
  const limits = await getUserPlanLimits(userId);
  
  const supabase = createClient();
  const { count, error } = await supabase
    .from('business_lines')
    .select('*', { count: 'exact', head: true })
    .eq('company_id', companyId);
  
  if (error) throw error;
  
  const current = count || 0;
  return {
    allowed: current < limits.blLimit,
    current,
    limit: limits.blLimit,
    remaining: Math.max(0, limits.blLimit - current),
  };
}
```

## FICHIER F-2 : `lib/feature-flags/gating.ts`

**Role :** HOC et hooks pour le gating des fonctionnalites dans les composants.

**Contenu :**
```typescript
import { useEffect, useState } from 'react';
import { isFeatureEnabled, getUserPlan, Plan } from './service';

export function useFeatureFlag(flagName: string): {
  enabled: boolean;
  loading: boolean;
  error: Error | null;
} {
  const [state, setState] = useState({
    enabled: false,
    loading: true,
    error: null as Error | null,
  });
  
  useEffect(() => {
    async function check() {
      try {
        // Recuperer le plan depuis le contexte utilisateur ou session
        const plan = await getUserPlanFromContext();
        const enabled = await isFeatureEnabled(flagName, plan);
        setState({ enabled, loading: false, error: null });
      } catch (err) {
        setState({ enabled: false, loading: false, error: err as Error });
      }
    }
    
    check();
  }, [flagName]);
  
  return state;
}

export function usePlan(): {
  plan: Plan;
  loading: boolean;
} {
  const [state, setState] = useState({ plan: 'free' as Plan, loading: true });
  
  useEffect(() => {
    async function load() {
      const plan = await getUserPlanFromContext();
      setState({ plan, loading: false });
    }
    load();
  }, []);
  
  return state;
}

export function usePlanLimits(): {
  limits: { aoLimitMonthly: number; blLimit: number; scoringDimensionsEnabled: number };
  loading: boolean;
} {
  const [state, setState] = useState({
    limits: { aoLimitMonthly: 10, blLimit: 1, scoringDimensionsEnabled: 3 },
    loading: true,
  });
  
  useEffect(() => {
    async function load() {
      // Recuperer depuis le contexte
      setState(prev => ({ ...prev, loading: false }));
    }
    load();
  }, []);
  
  return state;
}

// HOC pour wrapper un composant avec gating
export function withFeatureFlag<P extends object>(
  Component: React.ComponentType<P>,
  flagName: string,
  Fallback?: React.ComponentType<P>
): React.FC<P> {
  return function WrappedComponent(props: P) {
    const { enabled, loading } = useFeatureFlag(flagName);
    
    if (loading) {
      return <div className="animate-pulse h-20 bg-gray-100 rounded" />;
    }
    
    if (!enabled) {
      if (Fallback) {
        return <Fallback {...props} />;
      }
      return (
        <div className="p-4 border rounded bg-gray-50 text-gray-500 text-sm">
          Cette fonctionnalite necessite un abonnement superieur.
        </div>
      );
    }
    
    return <Component {...props} />;
  };
}

// Utilitaire interne
async function getUserPlanFromContext(): Promise<Plan> {
  // Dans une vraie implementation, recuperer depuis le contexte React ou la session
  return 'free';
}
```

## FICHIER F-3 : `app/api/feature-flags/route.ts`

**Role :** API REST pour les Feature Flags.

**Routes :**
- `GET /api/feature-flags` : Liste des flags (public)
- `POST /api/feature-flags` : Creer un flag (super admin)
- `PUT /api/feature-flags/:name` : Modifier un flag (super admin)

**Regles :**
- GET est public (tout le monde peut voir les flags et leurs plans)
- POST/PUT : super admin uniquement (verifie via service_role ou role specifique)
- Kill switch : PUT avec body `{ killSwitch: true }` desactive immediatement

## FICHIER F-4 : `app/api/user-plans/route.ts`

**Role :** API REST pour les plans utilisateurs.

**Routes :**
- `GET /api/user-plans` : Plan de l'utilisateur connecte
- `POST /api/user-plans` : Mettre a jour le plan (super admin ou webhook Stripe)

---

# SECTION 11 - FICHIERS A PRODUIRE - Groupe G : Frontend

## FICHIER G-1 : `components/business-lines/BLSelector.tsx`

**Role :** Selecteur de Business Line (header ou sidebar).

**Props :**
```typescript
interface BLSelectorProps {
  businessLines: Array<{ id: string; name: string; color: string }>;
  selectedId?: string;
  onSelect: (id: string | null) => void;
  allowAll?: boolean;
}
```

**Implementation :**
- shadcn/ui Select ou Command (combobox)
- Badge colore a gauche du nom
- Option "Toutes les BL" si allowAll=true
- Option "Sans BL" si des AO sans BL existent
- Sauvegarder la selection dans Zustand store

## FICHIER G-2 : `components/business-lines/BLBadge.tsx`

**Role :** Badge de Business Line avec couleur thematique.

**Props :**
```typescript
interface BLBadgeProps {
  name: string;
  color: string;
  size?: 'sm' | 'md' | 'lg';
}
```

**Implementation :**
- Badge shadcn/ui avec background color custom (opacity 0.1) et text color
- Size : sm (text-xs), md (text-sm), lg (text-base)
- Tooltip au survol avec description complete

## FICHIER G-3 : `components/business-lines/BLManager.tsx`

**Role :** Interface de gestion des Business Lines (admin).

**Implementation :**
- Table des BL existantes (nom, couleur, CPV count, keywords count, profil, membres count)
- Bouton "Creer une BL" -> Dialog avec formulaire
- Formulaire : nom, description, CPV codes (textarea, un par ligne), keywords (textarea), couleur (input color), profil (Select)
- Edition inline ou via Dialog
- Suppression avec confirmation (si AO associes, bloquer ou proposer reassignation)
- Gestion des membres : ajouter/retirer des utilisateurs, changer leur role

## FICHIER G-4 : `components/ui/RadarChart.tsx`

**Role :** Wrapper Recharts RadarChart avec theming.

**Props :**
```typescript
interface RadarChartProps {
  data: Array<Record<string, string | number>>;
  axes: Array<{ key: string; label: string }>;
  series: Array<{ key: string; name: string; color: string; fillOpacity?: number }>;
  width?: number;
  height?: number;
}
```

**Implementation :**
- Recharts RadarChart + PolarGrid + PolarAngleAxis + PolarRadiusAxis
- Plusieurs Radar pour comparaison
- Couleurs dynamiques
- ResponsiveContainer

## FICHIER G-5 : `components/ui/ScoreBadge.tsx`

**Role :** Badge de score avec couleur dynamique.

**Props :**
```typescript
interface ScoreBadgeProps {
  score: number;  // 0-10
  size?: 'sm' | 'md' | 'lg';
  showDecimals?: boolean;
}
```

**Implementation :**
- Rond ou pill selon size
- Couleur : emerald >= 7.5, amber >= 5, rose < 5
- Affiche "8.5" ou "8.5/10"
- Font bold

## FICHIER G-6 : `components/ui/VerdictBadge.tsx`

**Role :** Badge de verdict GO/NO-GO/MAYBE.

**Props :**
```typescript
interface VerdictBadgeProps {
  verdict: 'GO_v2' | 'NO_GO_v2' | 'MAYBE_v2' | 'GO' | 'NO-GO' | 'MAYBE';
  size?: 'sm' | 'md';
}
```

**Implementation :**
- shadcn/ui Badge variant
- GO_v2/GO : variant="default" (emerald background)
- NO_GO_v2/NO-GO : variant="destructive" (rose background)
- MAYBE_v2/MAYBE : variant="secondary" (amber background)
- Texte : "GO", "NO-GO", "MAYBE"

## FICHIER G-7 : `hooks/useScoringEngine.ts`

**Role :** Hook React pour executer le Scoring Engine.

**Implementation :**
```typescript
export function useScoringEngine() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const runScoring = useCallback(async (aoId: string): Promise<ScoreCard | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/scoring/engine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ aoId }),
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Erreur scoring');
      }
      
      const scoreCard = await response.json();
      return scoreCard;
    } catch (err) {
      setError(err as Error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return { runScoring, loading, error };
}
```

## FICHIER G-8 : `hooks/useBusinessLines.ts`

**Role :** Hook React pour recuperer et gerer les BL.

**Implementation :**
- Recuperer les BL de l'utilisateur
- Stocker dans Zustand store
- Fournir selectedBL, setSelectedBL
- Computed : isAdminBL, canCreateBL, blCount, blLimit

## FICHIER G-9 : `hooks/useDashboardData.ts`

**Role :** Hook React pour charger les donnees du dashboard.

**Implementation :**
- Fetch /api/dashboard/admin ou /api/dashboard/collaborator selon le role
- Parametres : period, businessLineId
- Caching SWR (stale-while-revalidate) : revalider toutes les 5 minutes
- Loading states pour chaque section

## FICHIER G-10 : `store/dashboard.ts`

**Role :** Zustand store pour le state global du dashboard.

**Contenu :**
```typescript
import { create } from 'zustand';

interface DashboardState {
  selectedBL: string | null;
  selectedPeriod: '7d' | '30d' | '90d' | '12m';
  setSelectedBL: (id: string | null) => void;
  setSelectedPeriod: (period: DashboardState['selectedPeriod']) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  selectedBL: null,
  selectedPeriod: '30d',
  setSelectedBL: (id) => set({ selectedBL: id }),
  setSelectedPeriod: (period) => set({ selectedPeriod: period }),
}));
```

## FICHIER G-11 : `app/api/scoring/engine/route.ts`

**Role :** API REST pour executer le Scoring Engine V2.

**Routes :**
- `POST /api/scoring/engine` : Executer le scoring pour un AO

**Body :**
```json
{ "aoId": "uuid", "forceProfile?": "prudent|opportuniste|specialise" }
```

**Reponse :**
```json
{
  "scoreCard": { ... },
  "duration": 1.234,  // temps d'execution en secondes
  "dimensionsCount": 5,
  "dimensionsSuccessful": 5
}
```

**Logique :**
1. Authentification
2. Recuperer l'AO et verif permissions
3. Detecter ou utiliser la BL
4. Charger le profil de scoring
5. Construire le ScoringContext
6. Executer `runScoringEngine(context)`
7. Sauvegarder le ScoreCard en base
8. Retourner le ScoreCard

**Performance :**
- Timeout de 30s sur la route
- Les plugins s'executent en parallele
- Si timeout, retourner une erreur 504

## FICHIER G-12 : `app/api/score-cards/route.ts`

**Role :** API REST pour les ScoreCards.

**Routes :**
- `GET /api/score-cards?ao_id=uuid` : Recuperer les ScoreCards d'un AO
- `GET /api/score-cards/:id` : Detail d'un ScoreCard
- `DELETE /api/score-cards/:id` : Supprimer un ScoreCard

## FICHIER G-13 : `app/api/scoring/feedback/route.ts`

**Role :** API REST pour le feedback de scoring.

**Routes :**
- `POST /api/scoring/feedback` : Enregistrer un feedback

---

# SECTION 12 - FICHIERS A PRODUIRE - Groupe H : Tests & Validation

## FICHIER H-1 : `lib/scoring/__tests__/engine.test.ts`

**Role :** Tests unitaires du Scoring Engine V2.

**Cas de test :**
1. Scoring complet avec 5 dimensions OK -> score global correct, verdict GO
2. Plugin en erreur (1 dimension) -> score avec 4 dimensions, confidence reduite
3. Plugin en erreur (3 dimensions) -> verdict FORCE_MAYBE
4. Tous plugins en erreur -> throw Error
5. Profil Prudent vs Opportuniste -> seuils differents, poids differents
6. Idempotence -> meme contexte = meme resultat
7. Timeout d'un plugin -> score null pour cette dimension

**Mocker :**
- Les plugins (retourner des DimensionResult predefinis)
- Les fichiers YAML (charger depuis fixtures)
- Supabase (pas de vrai appel DB)

## FICHIER H-2 : `lib/scoring/__tests__/balancer.test.ts`

**Role :** Tests unitaires du Balancer.

**Cas de test :**
1. 5 dimensions, somme poids = 1.0 -> score pondere correct
2. 1 dimension null -> repartition des poids, confidence reduite
3. 3 dimensions null -> verdict FORCE_MAYBE
4. 0 dimension -> throw Error
5. Seuils de profil : 7.5=GO prudent, 6.0=GO opportuniste

## FICHIER H-3 : `lib/scoring/__tests__/explainer.test.ts`

**Role :** Tests unitaires de l'Explainer.

**Cas de test :**
1. GO avec haute coherence -> recommandation "Poursuivre"
2. NO-GO avec faible coherence -> "Abandon recommande"
3. MAYBE avec delai court -> "Reevaluer apres analyse"
4. Impact calcule correctement selon les poids

## FICHIER H-4 : `lib/business-lines/__tests__/scope.test.ts`

**Role :** Tests unitaires du systeme de scope.

**Cas de test :**
1. Admin peut tout editer et tout voir
2. Membre standard : voit global, sa BL, son individuel, readonly de sa BL
3. Membre standard : ne peut pas editer global
4. Viewer : peut voir BL mais pas editer
5. Utilisateur d'une autre company : ne voit rien

## FICHIER H-5 : `lib/dashboard/__tests__/formulas.test.ts`

**Role :** Tests unitaires des formules KPI.

**Cas de test :**
1. CA Pipeline : somme correcte, filtre status
2. Taux reussite : pourcentage correct, division par zero evitee
3. Formatage : EUR, %, jours corrects
4. Categorie de chaque KPI

## FICHIER H-6 : `lib/feature-flags/__tests__/service.test.ts`

**Role :** Tests unitaires du service Feature Flags.

**Cas de test :**
1. Flag active, plan autorise -> true
2. Flag active, plan non autorise -> false
3. Kill switch active -> false meme si plan autorise
4. Flag inconnu -> false (securite)
5. Hierarchie des plans : enterprise >= pro >= starter >= free

## FICHIER H-7 : `tests/e2e/scoring-v2.spec.ts`

**Role :** Test E2E du flux complet de scoring V2.

**Scenario :**
1. Utilisateur se connecte
2. Cree un AO
3. Clic "Qualifier"
4. Verifie que la page ScoreCard s'affiche
5. Verifie la presence du radar chart
6. Verifie les 5 dimensions
7. Verifie le verdict
8. Soumet un feedback
9. Verifie que le feedback est enregistre

## FICHIER H-8 : `tests/e2e/dashboard-admin.spec.ts`

**Role :** Test E2E du Dashboard Admin.

**Scenario :**
1. Admin se connecte
2. Navigue sur /admin
3. Verifie que les 4 KPIs s'affichent
4. Verifie que les graphiques sont presents
5. Change le selecteur de BL -> verifie que les widgets se mettent a jour
6. Change la periode -> verifie la mise a jour

## FICHIER H-9 : `tests/e2e/business-lines.spec.ts`

**Role :** Test E2E du systeme Business Lines.

**Scenario :**
1. Admin cree une BL
2. Assigne un utilisateur
3. Utilisateur voit la BL dans son selecteur
4. Cree un AO -> BL detectee automatiquement
5. Verifie que l'AO apparait dans la BL

## FICHIER H-10 : `tests/e2e/feature-flags.spec.ts`

**Role :** Test E2E des Feature Flags.

**Scenario :**
1. Utilisateur Free tente de creer une 2e BL -> bloque avec message
2. Utilisateur Free atteint 10 AO -> bloque avec upsell
3. Admin active un kill switch -> feature desactivee

---

# SECTION 13 - ARCHITECTURE CIBLE

## 13.1 Diagramme de flux de donnees

```
[Utilisateur]
    |
    v
[Frontend Next.js] --(API)--> [Route Handlers]
                                    |
                    +-----------------+-----------------+
                    |                 |                 |
                    v                 v                 v
            [Scoring Engine]   [Business Lines]   [Dashboard]
                    |                 |                 |
                    v                 v                 v
            [Supabase PG]       [Supabase PG]      [Supabase PG]
                    |                 |                 |
                    +-----------------+-----------------+
                                      |
                                      v
                              [RLS Policies]
                                      |
                                      v
                              [Auth (JWT)]
```

## 13.2 Diagramme du Scoring Engine V2

```
+-------------------------------------------------------+
|                  SCORING ENGINE V2                      |
+-------------------------------------------------------+
|                                                         |
|  Input: AO + BL + User + Profile                        |
|                                                         |
|  +------------+  +------------+  +------------+        |
|  | Plugin D1  |  | Plugin D2  |  | Plugin D3  | ...    |
|  | Coherence  |  | Financier  |  | Geo        |        |
|  | Metier     |  |            |  |            |        |
|  +------+-----+  +------+-----+  +------+-----+        |
|         |              |              |                  |
|         +--------------+--------------+                  |
|                        |                                |
|                        v                                |
|                 +-------------+                         |
|                 |  Balancer   |                         |
|                 | (ponderation|                         |
|                 |  + verdict)  |                         |
|                 +------+------+                         |
|                        |                                |
|         +--------------+--------------+                  |
|         |                             |                  |
|         v                             v                  |
|  +-------------+               +-------------+          |
|  |  Explainer  |               |  ScoreCard  |          |
|  |    (XAI)    |               |  (persist)  |          |
|  +-------------+               +-------------+          |
|                                                         |
+-------------------------------------------------------+
```

## 13.3 Table des fichiers produits

| # | Fichier | Groupe | Lignes estimees |
|---|---------|--------|----------------|
| 1 | lib/scoring/engine.ts | A | 150 |
| 2 | lib/scoring/plugins/coherence-metier.ts | A | 80 |
| 3 | lib/scoring/plugins/viabilite-financiere.ts | A | 90 |
| 4 | lib/scoring/plugins/accessibilite-geographique.ts | A | 100 |
| 5 | lib/scoring/plugins/faisabilite-temporelle.ts | A | 80 |
| 6 | lib/scoring/plugins/intelligence-concurrentielle.ts | A | 100 |
| 7 | lib/scoring/registry.ts | A | 60 |
| 8 | lib/scoring/balancer.ts | A | 80 |
| 9 | lib/scoring/explainer.ts | A | 100 |
| 10 | lib/scoring/feedback.ts | A | 50 |
| 11 | lib/utils/jinja-eval.ts | A | 80 |
| 12 | config/scoring/dimensions/coherence-metier.yaml | B | 60 |
| 13 | config/scoring/dimensions/viabilite-financiere.yaml | B | 60 |
| 14 | config/scoring/dimensions/accessibilite-geographique.yaml | B | 60 |
| 15 | config/scoring/dimensions/faisabilite-temporelle.yaml | B | 60 |
| 16 | config/scoring/dimensions/intelligence-concurrentielle.yaml | B | 60 |
| 17 | config/scoring/profiles/prudent.yaml | B | 40 |
| 18 | config/scoring/profiles/opportuniste.yaml | B | 40 |
| 19 | config/scoring/profiles/specialise.yaml | B | 40 |
| 20 | lib/business-lines/models.ts | C | 80 |
| 21 | lib/business-lines/api.ts | C | 150 |
| 22 | lib/business-lines/scope.ts | C | 60 |
| 23 | app/api/business-lines/route.ts | C | 80 |
| 24 | app/api/user-business-lines/route.ts | C | 60 |
| 25 | lib/dashboard/formulas.ts | D | 120 |
| 26 | lib/dashboard/kpis.ts | D | 150 |
| 27 | lib/dashboard/benchmark.ts | D | 80 |
| 28 | app/api/dashboard/admin/route.ts | D | 120 |
| 29 | components/dashboard/admin/KPICard.tsx | D | 80 |
| 30 | components/dashboard/admin/ChartRepartition.tsx | D | 60 |
| 31 | components/dashboard/admin/ChartEvolution.tsx | D | 60 |
| 32 | components/dashboard/admin/ChartRadarBL.tsx | D | 60 |
| 33 | components/dashboard/admin/TableSuivi.tsx | D | 80 |
| 34 | components/dashboard/admin/TablePipeline.tsx | D | 80 |
| 35 | components/dashboard/admin/AlertesPrioritaires.tsx | D | 60 |
| 36 | components/dashboard/admin/ActionsRapides.tsx | D | 50 |
| 37 | components/dashboard/admin/InsightsIA.tsx | D | 60 |
| 38 | app/(dashboard)/admin/page.tsx | D | 100 |
| 39 | app/(dashboard)/kanban/page.tsx | E | 80 |
| 40 | components/dashboard/collaborator/KanbanBoard.tsx | E | 120 |
| 41 | components/dashboard/collaborator/KanbanColumn.tsx | E | 60 |
| 42 | components/dashboard/collaborator/KanbanCard.tsx | E | 80 |
| 43 | components/dashboard/collaborator/NotificationBell.tsx | E | 80 |
| 44 | app/(dashboard)/score-card/[id]/page.tsx | E | 80 |
| 45 | components/scoring/ScoreCardRadar.tsx | E | 60 |
| 46 | components/scoring/DimensionScore.tsx | E | 80 |
| 47 | components/scoring/ScoreFeedback.tsx | E | 60 |
| 48 | lib/feature-flags/service.ts | F | 120 |
| 49 | lib/feature-flags/gating.ts | F | 100 |
| 50 | app/api/feature-flags/route.ts | F | 60 |
| 51 | app/api/user-plans/route.ts | F | 40 |
| 52 | components/business-lines/BLSelector.tsx | G | 60 |
| 53 | components/business-lines/BLBadge.tsx | G | 40 |
| 54 | components/business-lines/BLManager.tsx | G | 120 |
| 55 | components/ui/RadarChart.tsx | G | 50 |
| 56 | components/ui/ScoreBadge.tsx | G | 40 |
| 57 | components/ui/VerdictBadge.tsx | G | 40 |
| 58 | hooks/useScoringEngine.ts | G | 50 |
| 59 | hooks/useBusinessLines.ts | G | 60 |
| 60 | hooks/useDashboardData.ts | G | 60 |
| 61 | store/dashboard.ts | G | 30 |
| 62 | app/api/scoring/engine/route.ts | G | 80 |
| 63 | app/api/score-cards/route.ts | G | 60 |
| 64 | app/api/scoring/feedback/route.ts | G | 40 |
| 65 | lib/scoring/__tests__/engine.test.ts | H | 120 |
| 66 | lib/scoring/__tests__/balancer.test.ts | H | 80 |
| 67 | lib/scoring/__tests__/explainer.test.ts | H | 60 |
| 68 | lib/business-lines/__tests__/scope.test.ts | H | 80 |
| 69 | lib/dashboard/__tests__/formulas.test.ts | H | 60 |
| 70 | lib/feature-flags/__tests__/service.test.ts | H | 80 |
| 71 | tests/e2e/scoring-v2.spec.ts | H | 80 |
| 72 | tests/e2e/dashboard-admin.spec.ts | H | 60 |
| 73 | tests/e2e/business-lines.spec.ts | H | 60 |
| 74 | tests/e2e/feature-flags.spec.ts | H | 60 |

**Total : 74 fichiers**
**Estimation totale : ~ 5 800 lignes de code source**

---

# SECTION 14 - CHECKLIST DE LIVRAISON

## 14.1 Criteres d'acceptation

- [ ] Le Scoring Engine V2 produit un ScoreCard avec 5 dimensions pour tout AO
- [ ] Les 3 profils (Prudent, Opportuniste, Specialise) produisent des verdicts differents sur le meme AO
- [ ] Les 5 fichiers YAML sont valides et chargeables
- [ ] Le systeme de Business Lines isole correctement les AO (utilisateur A ne voit pas les AO de la BL de B)
- [ ] Le Dashboard Admin affiche les 15 KPIs sans erreur
- [ ] Les graphiques Recharts sont responsives et accessibles
- [ ] Le Kanban supporte le drag-drop avec les nouveaux veredicts V2
- [ ] Les Feature Flags bloquent correctement les features selon le plan
- [ ] Le kill switch desactive immediatement une feature
- [ ] Les tests unitaires passent (couverture > 70% sur scoring engine)
- [ ] Les tests E2E passent (4 scenarios)
- [ ] La RLS empeche un utilisateur de voir les AO d'une autre company
- [ ] Le feedback utilisateur est enregistre et affichable
- [ ] Les rapports automatiques generent du JSON valide

## 14.2 Definition of Done

1. **Code complet** : Tous les 74 fichiers sont produits et compilent
2. **TypeScript strict** : Aucune erreur TypeScript (`tsc --noEmit` passe)
3. **Tests** : `npm test` passe avec > 70% coverage sur scoring/
4. **Lint** : ESLint passe sans erreur
5. **Build** : `npm run build` passe sans erreur
6. **Base de donnees** : Les migrations SQL sont fournies (tables + RLS)
7. **Documentation** : Chaque fichier a un JSDoc sur les fonctions publiques
8. **Accessibilite** : Tests axe-core passent sur les pages dashboard
9. **Responsive** : Les pages testees sur mobile (375px) et desktop (1440px)
10. **Performance** : Time to First Byte < 200ms, LCP < 2.5s

## 14.3 Migrations SQL a fournir

Le prompt ne demande pas explicitement les migrations, mais l'agent Kimi Code doit les generer dans un fichier `supabase/migrations/20240115_sprint2_scoring_business_lines.sql` :

1. Creer toutes les nouvelles tables
2. Ajouter les colonnes a `appels_offres`
3. Creer les indexes (`score_cards.appel_offre_id`, `score_cards.business_line_id`, `business_lines.company_id`, etc.)
4. Creer les fonctions RPC (`execute_kpi_query`, `get_kpi_by_bl`)
5. Activer RLS sur toutes les tables
6. Creer les policies RLS
7. Inserer les feature flags par defaut
8. Inserer les plans par defaut

## 14.4 Seeds a fournir

Fichier `supabase/seeds/sprint2_demo_data.sql` :

1. 2-3 Business Lines demo (Batiment, Informatique, Conseil)
2. Associations user-business_line
3. Feature flags actives
4. User plans de demo

## 14.5 Ordre d'implementation recommande

**Phase 1 (Jours 1-2) : Fondations**
- Migrations SQL
- Business Lines models + API + scope
- Feature Flags service + gating

**Phase 2 (Jours 3-5) : Scoring Engine V2**
- YAML dimensions et profils
- Jinja evaluator
- 5 plugins
- Registry + Balancer + Explainer
- API scoring engine

**Phase 3 (Jours 6-8) : Dashboards**
- KPI formulas + service
- Admin dashboard (page + widgets)
- Collaborateur dashboard (Kanban mis a jour)
- ScoreCard detail page

**Phase 4 (Jours 9-10) : Integration + Tests**
- Wire tout ensemble
- Tests unitaires
- Tests E2E
- Debug et polish UX

---

# ANNEXE A : Modeles Zod pour validation

```typescript
// schemas/scoring.ts
import { z } from 'zod';

export const DimensionResultSchema = z.object({
  name: z.string(),
  displayName: z.string(),
  score: z.number().min(0).max(10),
  weight: z.number().min(0).max(1),
  confidence: z.number().min(0).max(1),
  explanation: z.string(),
  rawData: z.record(z.unknown()),
  rulesTriggered: z.array(z.string()),
});

export const ScoreCardSchema = z.object({
  appelOffreId: z.string().uuid(),
  businessLineId: z.string().uuid(),
  userId: z.string().uuid(),
  dimensions: z.array(DimensionResultSchema),
  overallScore: z.number().min(0).max(10),
  verdict: z.enum(['GO_v2', 'NO_GO_v2', 'MAYBE_v2']),
  confidence: z.number().min(0).max(1),
  profileUsed: z.string(),
  xaiExplanation: z.object({
    summary: z.string(),
    dimensionBreakdown: z.array(z.object({
      name: z.string(),
      score: z.number(),
      why: z.string(),
      impact: z.enum(['high', 'medium', 'low']),
    })),
    keyFactors: z.array(z.string()),
    recommendation: z.string(),
  }),
  rawData: z.record(z.unknown()),
});

export const ScoringFeedbackSchema = z.object({
  scoreCardId: z.string().uuid(),
  dimensionName: z.string().optional(),
  feedbackType: z.enum(['too_strict', 'too_lenient', 'incorrect', 'other']),
  comment: z.string().max(500).optional(),
});

// schemas/business-lines.ts
export const CreateBusinessLineSchema = z.object({
  name: z.string().min(2).max(100),
  description: z.string().max(500).optional(),
  cpvCodes: z.array(z.string().regex(/^\d{2,8}$/)).default([]),
  keywords: z.array(z.string().min(1).max(50)).default([]),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/).default('#3b82f6'),
  scoringProfile: z.enum(['prudent', 'opportuniste', 'specialise']).default('prudent'),
});

export const AssignUserBLSchema = z.object({
  userId: z.string().uuid(),
  businessLineId: z.string().uuid(),
  role: z.enum(['admin_bl', 'member', 'viewer']).default('member'),
});

// schemas/dashboard.ts
export const DashboardQuerySchema = z.object({
  period: z.enum(['7d', '30d', '90d', '12m']).default('30d'),
  businessLineId: z.string().uuid().optional(),
});
```

---

# ANNEXE B : Fonctions RPC Supabase

```sql
-- Fonction pour executer les requetes KPI (securisee)
CREATE OR REPLACE FUNCTION execute_kpi_query(
  query_sql TEXT,
  company_id_param UUID
)
RETURNS JSONB AS $$
BEGIN
  -- Securite : verifier que la requete contient le filtre company_id
  IF query_sql NOT LIKE '%company_id%' THEN
    RAISE EXCEPTION 'Requete KPI doit filtrer par company_id';
  END IF;
  
  RETURN query_to_jsonb(query_sql);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Fonction pour recuperer un KPI par BL
CREATE OR REPLACE FUNCTION get_kpi_by_bl(
  p_company_id UUID,
  p_business_line_id UUID,
  p_kpi_id TEXT
)
RETURNS JSONB AS $$
DECLARE
  result JSONB;
BEGIN
  CASE p_kpi_id
    WHEN 'ca_pipeline' THEN
      SELECT jsonb_build_object('value', COALESCE(SUM(CASE WHEN montant_estime > 0 THEN montant_estime ELSE montant END), 0))
      INTO result
      FROM appels_offres
      WHERE company_id = p_company_id AND business_line_id = p_business_line_id AND status != 'non_retenu';
    
    WHEN 'ao_actifs' THEN
      SELECT jsonb_build_object('value', COUNT(*))
      INTO result
      FROM appels_offres
      WHERE company_id = p_company_id AND business_line_id = p_business_line_id
      AND status IN ('a_qualifier', 'qualifie', 'en_cours');
    
    ELSE
      result := jsonb_build_object('value', 0);
  END CASE;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

# ANNEXE C : Integration des rapports automatiques

```typescript
// lib/reports/scheduler.ts
import { createClient } from '@/lib/utils/supabase';

export async function generateWeeklyReport(companyId: string): Promise<unknown> {
  const supabase = createClient();
  
  // 1. Recuperer les KPIs de la semaine
  // 2. Nouveaux AO
  // 3. Repartition des veredicts
  // 4. Top BL
  // 5. Alertes
  
  return {
    period: 'weekly',
    generatedAt: new Date().toISOString(),
    kpis: {},
    newAOs: [],
    verdictDistribution: {},
    topBL: [],
    alerts: [],
    insights: {
      recommendation: '',
      warnings: [],
    },
  };
}

export async function generateMonthlyReport(companyId: string): Promise<unknown> {
  // Similaire avec comparaison mois precedent
  return {};
}
```

Les rapports sont generes par une CRON (Supabase Edge Function ou Vercel Cron) et envoyes par email (Resend).

---

# ANNEXE D : Seeder des Feature Flags par defaut

```sql
INSERT INTO feature_flags (name, description, plans_allowed, default_enabled, kill_switch) VALUES
('scoring_v2', 'Scoring Engine V2 avec 5 dimensions', ARRAY['free', 'starter', 'pro', 'enterprise'], true, false),
('dashboard_admin', 'Dashboard Admin complet', ARRAY['starter', 'pro', 'enterprise'], true, false),
('dashboard_admin_basic', 'Dashboard Admin basique (4 KPIs)', ARRAY['free', 'starter', 'pro', 'enterprise'], true, false),
('scoring_feedback', 'Feedback utilisateur sur les scores', ARRAY['starter', 'pro', 'enterprise'], true, false),
('business_lines_multiple', 'Gerer plusieurs Business Lines', ARRAY['starter', 'pro', 'enterprise'], true, false),
('reports_weekly', 'Rapports automatiques hebdomadaires', ARRAY['pro', 'enterprise'], true, false),
('reports_monthly', 'Rapports automatiques mensuels', ARRAY['starter', 'pro', 'enterprise'], true, false),
('benchmark_bl', 'Benchmarking entre Business Lines', ARRAY['pro', 'enterprise'], true, false),
('api_webhooks', 'Webhooks API', ARRAY['pro', 'enterprise'], true, false),
('export_pdf', 'Export PDF des rapports', ARRAY['enterprise'], true, false),
('kanban_dragdrop', 'Kanban drag-and-drop', ARRAY['free', 'starter', 'pro', 'enterprise'], true, false),
('scorecard_radar', 'Radar chart du ScoreCard', ARRAY['starter', 'pro', 'enterprise'], true, false),
('xai_explanations', 'Explications XAI detaillees', ARRAY['starter', 'pro', 'enterprise'], true, false),
('auto_detect_bl', 'Detection automatique de Business Line', ARRAY['pro', 'enterprise'], true, false);
```

---

# FIN DU PROMPT SPRINT 2 MIS A JOUR

**Agent Kimi Code :**
Ce prompt est auto-contenu. Tu peux demarrer l'implementation des que tu recois ce fichier.

Ordre recommande :
1. Lire ce prompt en entier
2. Creer les migrations SQL (Section 14.3)
3. Implementer Groupe B (YAML - rapide)
4. Implementer Groupe F (Feature Flags - fondation)
5. Implementer Groupe C (Business Lines)
6. Implementer Groupe A (Scoring Engine V2 - le coeur)
7. Implementer Groupe D + E (Dashboards)
8. Implementer Groupe G (Frontend wiring)
9. Implementer Groupe H (Tests)
10. Build + verif finale

BON COURAGE.


---

# ANNEXE E : Gestion des erreurs et monitoring

## E.1 Error boundaries par widget

Chaque widget du dashboard doit etre enveloppe d'un error boundary pour eviter qu'un widget en erreur fasse crasher toute la page.

```typescript
// components/ui/WidgetErrorBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  widgetName: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class WidgetErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error(`Erreur widget ${this.props.widgetName}:`, error, errorInfo);
    // Envoyer a Sentry ou service de monitoring
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 border rounded bg-red-50 text-red-700">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4" />
            <span className="font-medium">Erreur : {this.props.widgetName}</span>
          </div>
          <p className="text-sm mb-3">Ce widget ne peut pas s'afficher pour le moment.</p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Reessayer
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## E.2 Middleware de logging API

```typescript
// middleware/api-logger.ts
import { NextRequest, NextResponse } from 'next/server';

export function withLogging(handler: Function) {
  return async (req: NextRequest) => {
    const start = Date.now();
    const path = req.nextUrl.pathname;
    const method = req.method;
    
    try {
      const response = await handler(req);
      const duration = Date.now() - start;
      
      console.log(`[API] ${method} ${path} ${response.status} ${duration}ms`);
      
      return response;
    } catch (error) {
      const duration = Date.now() - start;
      console.error(`[API ERROR] ${method} ${path} ${duration}ms`, error);
      
      return NextResponse.json(
        { error: 'Erreur interne', code: 'INTERNAL_ERROR' },
        { status: 500 }
      );
    }
  };
}
```

## E.3 Retry strategy pour les plugins

```typescript
// lib/scoring/retry.ts
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    delayMs?: number;
    backoffMultiplier?: number;
  } = {}
): Promise<T> {
  const { maxRetries = 2, delayMs = 500, backoffMultiplier = 2 } = options;
  
  let lastError: Error | undefined;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt < maxRetries) {
        const delay = delayMs * Math.pow(backoffMultiplier, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError;
}
```

---

# ANNEXE F : Composants shadcn/ui a installer

Liste exacte des composants shadcn/ui necessaires pour ce sprint :

```bash
npx shadcn-ui@latest add card button badge dialog select tabs table skeleton tooltip toast alert progress separator sheet command popover avatar dropdown-menu checkbox textarea scroll-area
```

**Utilisation par composant :**

| Composant | Utilisation |
|-----------|-------------|
| card | KPICard, DimensionScore, InsightsIA |
| button | ActionsRapides, formulaires |
| badge | BLBadge, VerdictBadge, ScoreBadge, regles |
| dialog | BLManager (creation/edition), confirmation suppression |
| select | BLSelector, periode selector, profil selector |
| tabs | ScoreCard detail (resume / dimensions / explications) |
| table | TableSuivi, TablePipeline |
| skeleton | Loading states sur tous les widgets |
| tooltip | Scores, badges, icones d'aide |
| toast | Notifications (feedback envoye, BL creee) |
| alert | AlertesPrioritaires, error boundaries |
| progress | Barre de progression des dimensions |
| separator | Separateurs visuels |
| sheet | Menu mobile, filtres lateraux |
| command | BLSelector recherche |
| popover | Date pickers, info bulles |
| avatar | Collaborateurs dans TableSuivi |
| dropdown-menu | Actions par ligne dans les tableaux |
| checkbox | Selection multiple, feedback types |
| textarea | Commentaires feedback, descriptions BL |
| scroll-area | Tableaux longs, listes de BL |

---

# ANNEXE G : Regles CSS/Tailwind specifiques

```css
/* globals.css additions */

/* Smooth transitions pour le Kanban */
.kanban-card {
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.kanban-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Radar chart custom styles */
.radar-chart-container {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.05));
}

/* KPI card hover effect */
.kpi-card {
  transition: border-color 200ms ease;
}

.kpi-card:hover {
  border-color: hsl(var(--primary));
}

/* Score badge animations */
@keyframes score-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.score-badge-new {
  animation: score-pulse 2s ease-in-out;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .kanban-card,
  .kpi-card,
  .score-badge-new {
    transition: none;
    animation: none;
    transform: none;
  }
}

/* Print styles pour rapports */
@media print {
  .no-print {
    display: none !important;
  }
  
  .page-break {
    page-break-before: always;
  }
}
```

---

# ANNEXE H : Conventions de nommage des branches Git

Pour l'agent Kimi Code, si plusieurs fichiers sont produits en plusieurs passes :

```
sprint-2/scoring-engine-v2
sprint-2/business-lines
sprint-2/dashboard-admin
sprint-2/feature-flags
sprint-2/tests
```

---

# ANNEXE I : Liste des packages npm a installer

```bash
# Scoring Engine
npm install nunjucks js-yaml

# Dashboard charts
npm install recharts

# Drag and drop
npm install @hello-pangea/dnd

# State management
npm install zustand

# Date formatting
npm install date-fns

# Testing (si non deja installe)
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event

# E2E (si non deja installe)
npm install -D playwright

# Email templates
npm install react-email @react-email/components
```

---

# ANNEXE J : Exemple de session utilisateur complete

## J.1 Scenario : Creation et qualification d'un AO

**Etape 1 :** Admin cree une Business Line "Construction Batiment" (CPV: 45000000, color: #3b82f6, profil: prudent)

**Etape 2 :** Admin assigne 2 collaborateurs (Pierre membre, Sophie admin_bl)

**Etape 3 :** Pierre se connecte, voit "Construction Batiment" dans son selecteur

**Etape 4 :** Pierre upload un PDF d'AO (CPV 45230000, montant 150000 EUR, deadline dans 20 jours, localisation: Lyon)

**Etape 5 :** Systeme detecte BL = Construction Batiment (confidence 0.95)

**Etape 6 :** Pierre clique "Qualifier"

**Etape 7 :** Scoring Engine V2 s'execute :
- D1 Coherence Metier: CPV 4523 match niveau 2 avec 45000000 -> score 7, weight 0.30
- D2 Viabilite Financiere: 150K dans range optimal -> score 7, weight 0.25, profil prudent penalite 0 -> 7
- D3 Geo: Lyon (69) vs entreprise Paris (75) -> hors zone -> score 2, weight 0.20
- D4 Temporel: 20 jours -> score 8, weight 0.15
- D5 Concurrentiel: pas d'historique -> score 5, weight 0.10

- Score global: 7*0.30 + 7*0.25 + 2*0.20 + 8*0.15 + 5*0.10 = 2.1 + 1.75 + 0.4 + 1.2 + 0.5 = 5.95
- Profil prudent: seuil GO=7.5 -> Verdict = MAYBE_v2

**Etape 8 :** Pierre consulte le ScoreCard :
- Radar chart montre le creux geographique
- Explication XAI: "MAYBE - L'AO correspond bien a votre metier (score 7/10) mais la localisation est problematique (2/10). 20 jours sont disponibles pour evaluer les couts de deplacement."

**Etape 9 :** Pierre donne feedback "Trop severe" sur la dimension geographique (il a un partenaire a Lyon)

**Etape 10 :** Pierre deplace l'AO en "Qualifies MAYBE" dans le Kanban

**Etape 11 :** Le Dashboard Admin de Sophie est mis a jour :
- KPI "CA Pipeline" += 150K
- KPI "Taux MAYBE" recalcule
- Alerte : nouvel AO MAYBE dans Construction Batiment

---

# ANNEXE K : Index SQL recommandes pour la performance

```sql
-- Indexes pour le scoring
CREATE INDEX idx_score_cards_appel_offre_id ON score_cards(appel_offre_id);
CREATE INDEX idx_score_cards_business_line_id ON score_cards(business_line_id);
CREATE INDEX idx_score_cards_user_id ON score_cards(user_id);
CREATE INDEX idx_score_cards_created_at ON score_cards(created_at);

-- Indexes pour les KPIs et rapports
CREATE INDEX idx_appels_offres_company_status ON appels_offres(company_id, status);
CREATE INDEX idx_appels_offres_company_bl ON appels_offres(company_id, business_line_id);
CREATE INDEX idx_appels_offres_created_at ON appels_offres(created_at);
CREATE INDEX idx_appels_offres_date_limite ON appels_offres(date_limite);
CREATE INDEX idx_appels_offres_cpv ON appels_offres(cpv_code);

-- Indexes pour les Business Lines
CREATE INDEX idx_business_lines_company ON business_lines(company_id);
CREATE INDEX idx_user_business_lines_user ON user_business_lines(user_id);
CREATE INDEX idx_user_business_lines_bl ON user_business_lines(business_line_id);

-- Indexes pour les feedbacks
CREATE INDEX idx_scoring_feedbacks_score_card ON scoring_feedbacks(score_card_id);
```

---

# ANNEXE L : Implementation du departements_adjacents

```typescript
// lib/geo/departements-adjacents.ts

export const DEPARTEMENTS_ADJACENTS: Record<string, string[]> = {
  '01': ['69', '38', '73', '74', '39', '71'],
  '02': ['60', '80', '62', '77', '51'],
  '03': ['63', '42', '71', '18', '23', '19'],
  '04': ['05', '84', '83', '26', '07'],
  '05': ['04', '26', '38', '73'],
  '06': ['83', '84'],
  '07': ['30', '26', '43', '38', '73', '48'],
  '08': ['51', '55', '02', '77'],
  '09': ['31', '11', '66'],
  '10': ['77', '89', '21', '52', '51'],
  '11': ['34', '66', '09', '31', '81'],
  '12': ['81', '82', '46', '15', '48', '30'],
  '13': ['84', '30', '34', '83'],
  '14': ['50', '61', '27', '76', '60'],
  '15': ['12', '46', '19', '63', '43', '48'],
  '16': ['17', '86', '79', '87', '24'],
  '17': ['16', '85', '79', '33', '24'],
  '18': ['36', '41', '45', '58', '03', '23'],
  '19': ['87', '23', '15', '63'],
  '21': ['58', '71', '10', '89', '52'],
  '22': ['56', '29', '35'],
  '23': ['19', '87', '36', '18', '03', '15'],
  '24': ['33', '47', '46', '19', '87', '16'],
  '25': ['90', '70', '39', '71'],
  '26': ['38', '07', '84', '04', '05'],
  '27': ['76', '14', '61', '28', '45', '60'],
  '28': ['27', '45', '41', '72', '61', '91'],
  '29': ['22', '56'],
  '30': ['34', '13', '84', '26', '07', '48', '12'],
  '31': ['11', '09', '32', '81', '82', '65'],
  '32': ['40', '82', '31', '65', '64'],
  '33': ['40', '47', '24', '17'],
  '34': ['30', '11', '81', '12'],
  '35': ['22', '56', '44', '53', '50', '14'],
  '36': ['37', '41', '18', '23', '87'],
  '37': ['41', '72', '45', '28', '36'],
  '38': ['69', '26', '07', '73', '05', '01', '39'],
  '39': ['25', '71', '01', '38', '70', '21'],
  '40': ['33', '47', '64', '32'],
  '41': ['37', '72', '28', '45', '18', '36'],
  '42': ['43', '07', '63', '03', '71'],
  '43': ['15', '48', '07', '26', '42', '63'],
  '44': ['49', '85', '79', '17', '56', '35'],
  '45': ['28', '77', '89', '18', '41', '37'],
  '46': ['24', '47', '82', '12', '15'],
  '47': ['40', '33', '24', '82', '32', '64'],
  '48': ['12', '15', '43', '07', '30'],
  '49': ['44', '85', '53', '72', '37'],
  '50': ['14', '35', '53', '61'],
  '51': ['77', '10', '52', '08', '55'],
  '52': ['51', '10', '21', '55', '88'],
  '53': ['35', '50', '61', '72', '49'],
  '54': ['57', '55', '88', '67'],
  '55': ['54', '57', '88', '52', '51', '08'],
  '56': ['29', '22', '35', '44'],
  '57': ['54', '67', '88', '55'],
  '58': ['89', '21', '71', '03', '18', '45'],
  '59': ['62', '80', '02'],
  '60': ['77', '02', '80'],
  '61': ['14', '27', '28', '50', '53', '72'],
  '62': ['59', '80', '02'],
  '63': ['43', '15', '03', '42', '07', '19'],
  '64': ['40', '47', '32', '65'],
  '65': ['64', '32', '31', '82'],
  '66': ['11', '09'],
  '67': ['68', '88', '57', '54'],
  '68': ['67', '88'],
  '69': ['01', '38', '71', '42', '07'],
  '70': ['90', '25', '39', '71'],
  '71': ['69', '01', '39', '58', '03', '42', '21', '45'],
  '72': ['28', '37', '41', '61', '53', '49'],
  '73': ['74', '38', '01', '05'],
  '74': ['73', '01'],
  '75': ['77', '78', '91', '92', '93', '94', '95'],
  '76': ['27', '14', '60', '80'],
  '77': ['75', '91', '60', '51', '10', '45', '89'],
  '78': ['75', '91', '92', '27', '28', '95'],
  '79': ['17', '16', '86', '44', '85'],
  '80': ['62', '59', '02', '60', '76'],
  '81': ['31', '11', '34', '12', '82'],
  '82': ['31', '32', '46', '12', '81'],
  '83': ['13', '84', '06', '04'],
  '84': ['26', '04', '83', '13', '30', '07'],
  '85': ['44', '49', '79', '17', '86'],
  '86': ['85', '79', '16', '37', '36'],
  '87': ['36', '23', '19', '24', '16'],
  '88': ['54', '55', '57', '67', '68', '52'],
  '89': ['77', '45', '10', '21', '58', '18'],
  '90': ['25', '70', '68', '88'],
  '91': ['75', '77', '78', '92', '93', '94', '95', '45', '28'],
  '92': ['75', '78', '91', '93', '94', '95'],
  '93': ['75', '91', '92', '94', '95'],
  '94': ['75', '91', '92', '93', '95'],
  '95': ['75', '91', '92', '93', '94', '78'],
  '971': [],
  '972': [],
  '973': [],
  '974': [],
  '976': [],
};

export function getDepartementsAdjacents(dept: string): string[] {
  return DEPARTEMENTS_ADJACENTS[dept] || [];
}

export function getRegionFromDepartement(dept: string): string {
  // Simplifie : mapping basique
  const deptNum = parseInt(dept);
  if (deptNum >= 1 && deptNum <= 8) return 'Auvergne-Rhone-Alpes';
  if (deptNum >= 9 && deptNum <= 12) return 'Occitanie';
  if (deptNum >= 13 && deptNum <= 14) return 'Provence-Alpes-Cote d\'Azur';
  if (deptNum === 15) return 'Auvergne-Rhone-Alpes';
  if (deptNum >= 16 && deptNum <= 17) return 'Nouvelle-Aquitaine';
  if (deptNum >= 18 && deptNum <= 19) return 'Centre-Val de Loire';
  if (deptNum === 21) return 'Bourgogne-Franche-Comte';
  if (deptNum >= 22 && deptNum <= 23) return 'Nouvelle-Aquitaine';
  if (deptNum >= 24 && deptNum <= 25) return 'Nouvelle-Aquitaine';
  if (deptNum >= 26 && deptNum <= 27) return 'Normandie';
  if (deptNum >= 28 && deptNum <= 29) return 'Bretagne';
  if (deptNum >= 30 && deptNum <= 32) return 'Occitanie';
  if (deptNum >= 33 && deptNum <= 35) return 'Nouvelle-Aquitaine';
  if (deptNum >= 36 && deptNum <= 37) return 'Centre-Val de Loire';
  if (deptNum >= 38 && deptNum <= 39) return 'Bourgogne-Franche-Comte';
  if (deptNum >= 40 && deptNum <= 41) return 'Nouvelle-Aquitaine';
  if (deptNum >= 42 && deptNum <= 43) return 'Auvergne-Rhone-Alpes';
  if (deptNum >= 44 && deptNum <= 45) return 'Pays de la Loire';
  if (deptNum >= 46 && deptNum <= 47) return 'Nouvelle-Aquitaine';
  if (deptNum >= 48 && deptNum <= 49) return 'Occitanie';
  if (deptNum >= 50 && deptNum <= 51) return 'Grand Est';
  if (deptNum >= 52 && deptNum <= 53) return 'Pays de la Loire';
  if (deptNum >= 54 && deptNum <= 55) return 'Grand Est';
  if (deptNum >= 56 && deptNum <= 57) return 'Grand Est';
  if (deptNum >= 58 && deptNum <= 59) return 'Bourgogne-Franche-Comte';
  if (deptNum >= 60 && deptNum <= 62) return 'Hauts-de-France';
  if (deptNum >= 63 && deptNum <= 64) return 'Nouvelle-Aquitaine';
  if (deptNum >= 65 && deptNum <= 66) return 'Occitanie';
  if (deptNum >= 67 && deptNum <= 68) return 'Grand Est';
  if (deptNum >= 69 && deptNum <= 71) return 'Auvergne-Rhone-Alpes';
  if (deptNum >= 72 && deptNum <= 74) return 'Auvergne-Rhone-Alpes';
  if (deptNum >= 75 && deptNum <= 78) return 'Ile-de-France';
  if (deptNum >= 79 && deptNum <= 80) return 'Hauts-de-France';
  if (deptNum >= 81 && deptNum <= 82) return 'Occitanie';
  if (deptNum >= 83 && deptNum <= 84) return 'Provence-Alpes-Cote d\'Azur';
  if (deptNum >= 85 && deptNum <= 86) return 'Nouvelle-Aquitaine';
  if (deptNum >= 87 && deptNum <= 89) return 'Nouvelle-Aquitaine';
  if (deptNum >= 90 && deptNum <= 95) return 'Ile-de-France';
  return 'Inconnu';
}
```

---

# ANNEXE M : Formulaire de creation d'AO mis a jour

Le formulaire de creation d'AO (herite du Sprint 1) doit integrer :

1. **Selecteur Business Line** : pre-rempli avec la detection automatique, modifiable
2. **Selecteur Scope** : Global / Business Line / Individuel / Readonly
3. **Assignation** : si scope = individuel, choisir l'assignee
4. **Auto-qualification** : checkbox "Qualifier automatiquement apres creation"

```typescript
// app/(dashboard)/ao/nouveau/page.tsx - update

// Ajouter dans le formulaire :
<BLSelector
  businessLines={userBLs}
  selectedId={formData.businessLineId}
  onSelect={(id) => setFormData(prev => ({ ...prev, businessLineId: id }))}
/>

<Select value={formData.scopeLevel} onValueChange={v => setFormData(prev => ({ ...prev, scopeLevel: v }))}>
  <SelectTrigger>
    <SelectValue placeholder="Niveau de visibilite" />
  </SelectTrigger>
  <SelectContent>
    {SCOPE_LEVELS.map(level => (
      <SelectItem key={level.value} value={level.value}>
        {level.label} - {level.description}
      </SelectItem>
    ))}
  </SelectContent>
</Select>

{formData.scopeLevel === 'individuel' && (
  <UserSelect
    users={companyUsers}
    selectedId={formData.assignedTo}
    onSelect={(id) => setFormData(prev => ({ ...prev, assignedTo: id }))}
  />
)}

<Checkbox
  checked={formData.autoQualify}
  onCheckedChange={(c) => setFormData(prev => ({ ...prev, autoQualify: !!c }))}
/>
<label>Qualifier automatiquement apres creation</label>
```

---

# ANNEXE N : Mise a jour du parsing d'AO pour la detection BL

Lorsqu'un AO est parse (PDF ou formulaire), le systeme doit tenter la detection automatique de BL :

```typescript
// lib/ao/detection.ts
import { detectBusinessLineForAO } from '@/lib/business-lines/api';

export async function autoDetectBusinessLine(
  ao: { cpvCode?: string; description?: string; title?: string },
  companyId: string
): Promise<{ businessLineId: string | null; confidence: number }> {
  const supabase = createClient();
  
  // Recuperer les BL de l'entreprise
  const { data: bls } = await supabase
    .from('business_lines')
    .select('*')
    .eq('company_id', companyId);
  
  if (!bls || bls.length === 0) {
    return { businessLineId: null, confidence: 0 };
  }
  
  return detectBusinessLineForAO(ao, bls);
}
```

**Seuil de detection :**
- confidence >= 0.7 : auto-assigner la BL
- confidence 0.4 - 0.7 : suggerer la BL dans l'interface (pre-rempli mais modifiable)
- confidence < 0.4 : aucune suggestion, selecteur vide

---

# ANNEXE O : Notifications systeme

```typescript
// lib/notifications/types.ts
export interface Notification {
  id: string;
  userId: string;
  type: 'ao_assigned' | 'deadline_approaching' | 'scoring_complete' | 'bl_created' | 'feedback_received';
  title: string;
  message: string;
  link?: string;
  read: boolean;
  createdAt: string;
}

// lib/notifications/service.ts
export async function createNotification(
  notification: Omit<Notification, 'id' | 'createdAt' | 'read'>
): Promise<void> {
  const supabase = createClient();
  await supabase.from('notifications').insert({
    user_id: notification.userId,
    type: notification.type,
    title: notification.title,
    message: notification.message,
    link: notification.link,
    read: false,
  });
}

export async function getUnreadCount(userId: string): Promise<number> {
  const supabase = createClient();
  const { count } = await supabase
    .from('notifications')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', userId)
    .eq('read', false);
  
  return count || 0;
}
```

**Table notifications a creer :**
```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  link TEXT,
  read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_notifications_user_read ON notifications(user_id, read);
```

---

# ANNEXE P : Historique des versions du Scoring

Pour assurer la retrocompatibilite, les ScoreCards doivent stocker la version du moteur utilise :

```sql
ALTER TABLE score_cards ADD COLUMN engine_version TEXT DEFAULT '2.0';
```

Les anciens ScoreCards (Sprint 1) auront `engine_version = '1.0'` ou NULL.
Le Dashboard doit pouvoir filtrer par version pour les comparatifs historiques.

---

# ANNEXE Q : Migration du Sprint 1 vers Sprint 2

Pour les utilisateurs existants :

1. **ScoreCards V1 :** Conserver en l'etat, ajouter `engine_version = '1.0'`
2. **Kanban :** Les anciens status restent valides. Les nouveaux veredicts V2 sont GO_v2, NO_GO_v2, MAYBE_v2.
3. **Business Line :** Creer une BL par defaut pour chaque entreprise existante (nom = "Metier principal", color = #3b82f6, profil = prudent)
4. **User Plans :** Tous les utilisateurs existants recoivent plan = 'free' par defaut (migration manuelle pour les payants)
5. **AO existants :** Associer a la BL par defaut de l'entreprise

---

# ANNEXE R : Conventions de documentation JSDoc

Chaque fonction publique doit avoir :

```typescript
/**
 * Execute le Scoring Engine V2 pour un AO donne.
 *
 * @param context - Le contexte de scoring contenant l'AO, la BL, l'utilisateur et le profil
 * @returns Un ScoreCard complet avec les 5 dimensions, le score global et les explications
 * @throws ScoringEngineError si moins de 3 dimensions retournent un score
 * @throws TimeoutError si l'execution depasse 30 secondes
 *
 * @example
 * const scoreCard = await runScoringEngine({
 *   ao: appelOffre,
 *   businessLine: bl,
 *   user: currentUser,
 *   profile: prudentProfile,
 * });
 * console.log(scoreCard.overallScore); // 7.5
 */
```

---

# FIN DEFINITIVE DU PROMPT SPRINT 2 MIS A JOUR

**Recapitulatif livrable :**
- Sections : 14 + 18 Annexes (A a R)
- Fichiers references : 74 fichiers sources
- Fichiers YAML : 8 (5 dimensions + 3 profils)
- Fichiers de migration SQL : 1
- Fichiers de seed : 1
- Tests : 10 fichiers de tests
- Total estime de code source : ~ 6 000 lignes

**Message final pour Kimi Code :**

Tu es l'agent de codage automatique. Ce prompt est ton seul document de reference.
Ne suppose rien qui ne soit pas ecrit ici.
Si tu dois faire un choix technique, prefere la simplicite et la robustesse.
Teste chaque module au fur et a mesure.
Documente tes choix dans les commentaires.

A TOI DE JOUER.
