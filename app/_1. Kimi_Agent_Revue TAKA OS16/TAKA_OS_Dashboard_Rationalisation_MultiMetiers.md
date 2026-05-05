# TAKA OS — Dashboard avec Rationalisation Multi-Métiers
## Specification Produit Complete — Version 1.0

---

# PARTIE I — MODELE ORGANISATIONNEL MULTI-METIERS

## 1.1 Realite terrain : les groupes multi-sectoriels

Les grands groupes soumissionnaires partagent une caracteristique : activite structuree en divisions metiers distinctes, chacune avec sa propre organisation commerciale et ses charges d'affaires dedies. Le dashboard actuel monolithique par tenant ne reflete pas cette realite. Il faut ajouter une dimension "secteur/metier" et un mecanisme de "scope" pour les collaborateurs.

### 1.1.1 Exemple A — Equans (filiale de Bouygues, 90 000 salaries)

| Division | Perimetre metier | CPV typiques | Charges d'affaires |
|----------|------------------|--------------|--------------------|
| Telecom | Reseaux fibre, 5G, data centers | 45232100, 45232200, 64212000 | ~120 |
| Surete | Videosurveillance, detection intrusion, telesurveillance | 35121000, 35122000, 35125000 | ~45 |
| Controle d'acces | Badgeage, biometrie, portiques | 35123000, 35124000 | ~30 |
| CVC | Chauffage, ventilation, climatisation | 45331000, 45332000, 45333000 | ~85 |
| Electricite | HTA, BT, eclairage public | 45310000, 45311000, 45210000 | ~110 |

Chaque division a son propre directeur commercial (DCE), ses propres references et CPV. Le DG France exige un reporting hebdomadaire par division. Le responsable Telecom ne doit voir que les AO de sa division. Le charge d'affaires fibre optique a Lyon ne voit que ses AO assignes.

### 1.1.2 Exemple B — Sogetrel (filiale d'Eiffage, 4 500 salaries)

| Division | Perimetre metier | Budget AO annuel |
|----------|------------------|--------------------|
| Infrastructures Telecom | Fibre optique, reseaux mobiles RAN | ~45M EUR |
| Surete & Smart Building | VSS, controle d'acces, GTC | ~28M EUR |
| Energie & Services | Bornes recharge VE, compteurs intelligents, Smart Grid | ~35M EUR |

Chaque division a son budget AO propre et ses objectifs CA. La direction generale compare trimestriellement les 3 divisions pour reallouer les ressources.

### 1.1.3 Exemple C — SPIE (50 000 salaries)

| Division | Perimetre metier | Organisation |
|----------|------------------|--------------|
| SPIE Industrie | Automation, robotique, instrumentation | 4 zones geographiques |
| SPIE Energie | Maintenance electrique HT, ENR | 5 zones geographiques |
| SPIE CityNetworks | Eclairage public, telecoms urbaines | 3 zones geographiques |

La DG France SPIE effectue un reporting mensuel par division avec KPIs normalises.

### 1.1.4 Synthese des besoins

| Besoin | Equans | Sogetrel | SPIE | Priorite |
|--------|--------|----------|------|----------|
| Vue consolidée multi-divisions | DG France | DG | DG France | Critique |
| Vue filtree par division | DCE par division | Responsable division | Responsable zone | Critique |
| Vue individuelle charge d'affaires | Charge d'affaires | Charge d'affaires | Commercial terrain | Critique |
| Reporting comparatif division | Hebdo | Trimestriel | Mensuel | Haute |
| Segregation CPV par division | Oui | Oui | Oui | Haute |

## 1.2 Modele de donnees etendu : Business Line

### 1.2.1 Table `business_lines`

```python
class BusinessLine(Base):
    __tablename__ = "business_lines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Ex: "Telecom", "Surete", "Controle d'acces", "CVC", "Electricite"

    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    # Ex: "telecom", "surete", "controle-acces" — utilise dans les URLs

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6")
    # Couleur hex pour Kanban et graphiques. Telecom=#3B82F6, Surete=#EF4444, CVC=#10B981

    cpv_codes: Mapped[list[str]] = mapped_column(ARRAY(String(20)), default=[])
    # Codes CPV associes par defaut. Ex Telecom: ["45232100", "45232200", "64212000"]

    keywords: Mapped[list[str]] = mapped_column(ARRAY(String(100)), default=[])
    # Mots-cles pour matching IA. Ex Surete: ["videosurveillance", "detection intrusion"]

    scoring_profile: Mapped[str] = mapped_column(String(20), default="specialise")
    # "prudent" (forte selectivite), "opportuniste" (volume), "specialise" (equilibre)

    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    annual_target_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    monthly_target_tenders: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=10)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Contraintes** : UNIQUE(tenant_id, slug), UNIQUE(tenant_id, name). Index composite sur (tenant_id, is_active).

### 1.2.2 Table `user_business_lines` (association N:N)

```python
class UserBusinessLine(Base):
    __tablename__ = "user_business_lines"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    business_line_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business_lines.id", ondelete="CASCADE"), primary_key=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    # Une seule BL primaire par utilisateur (contrainte partielle WHERE is_primary=true)

    can_edit: Mapped[bool] = mapped_column(Boolean, default=True)
    # Peut creer, modifier, qualifier les AO de cette BL

    can_assign: Mapped[bool] = mapped_column(Boolean, default=False)
    # Peut assigner des AO a d'autres collaborateurs sur cette BL (droit manager)

    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    assigned_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
```

**Regles d'assignation automatique** :
- Admin tenant : TOUTES les BLs avec can_edit=True, can_assign=True
- Manager : BLs qu'il gere avec can_edit=True, can_assign=True
- Collaborateur : Ses BLs avec can_edit=True, can_assign=False
- Viewer : Ses BLs avec can_edit=False, can_assign=False

### 1.2.3 Extension de la table `tenders`

```python
class Tender(Base):
    # --- Champs existants ---
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100))
    cpv_code: Mapped[Optional[str]] = mapped_column(String(20))
    amount_estimated: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    deadline_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # --- Nouveaux champs multi-metiers ---
    business_line_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("business_lines.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    auto_classified: Mapped[bool] = mapped_column(Boolean, default=False)
    # True si la BL a ete determinee automatiquement par IA

    classification_confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    # Score de confiance du matching IA (0.000 a 1.000)
```

**Regles de classification automatique** : Si le CPV de l'AO correspond a un code CPV d'une BL du tenant, l'AO est automatiquement rattache (auto_classified=True). Si plusieurs BLs partagent le meme CPV, celle avec le plus de keywords matches est choisie. L'admin peut toujours modifier manuellement.

## 1.3 Niveaux de visibilite (Scope)

### 1.3.1 Matrice des niveaux de scope

| Niveau | Portee | Utilisateurs | Description |
|--------|--------|-------------|-------------|
| **Global** | Tout le tenant | Admin, DG, DSI | Voit tous les AO de toutes les BLs, tous les collaborateurs, tous les KPIs consolides. Peut reassigner entre divisions. |
| **Business Line** | Un ou plusieurs secteurs | Manager, DCE | Voit uniquement les AO de ses BLs assignees. Peut qualifier, assigner et modifier les AO de ses BLs. |
| **Individuel** | Ses AO assignes | Charge d'affaires | Ne voit que les AO ou il est assigned_to. Peut qualifier, uploader, deplacer les cartes Kanban. |
| **Lecture seule** | Vue sans action | Viewer, auditeur | Peut consulter les KPIs et rapports des BLs assignees mais ne peut rien modifier. |

### 1.3.2 Regles de visibilite detaillees

**Regle 1 — Admin Global** : Un `tenant_admin` voit TOUJOURS en scope Global. Le selecteur de BL affiche "Toutes les divisions" par defaut avec possibilite de filtrer sur une BL specifique.

**Regle 2 — Manager Business Line** : Un `tenant_manager` voit les BLs ou il est `manager_id` OU ou `can_assign=True` dans `user_business_lines`. Le selecteur ne montre que ses BLs assignees. Pas d'option "Toutes les divisions".

**Regle 3 — Collaborateur Individuel** : Un `tenant_collaborator` voit les BLs avec `can_edit=True`. Au sein de ces BLs, il ne voit que les AO ou `assigned_to_id = son user_id`.

**Regle 4 — Viewer** : Un `tenant_viewer` voit les BLs avec `can_edit=False` en lecture seule sur tous les AO de ces BLs.

**Regle 5 — Cumul** : Un utilisateur peut cumuler des roles differents par BL. Exemple : DCE Telecom + collaborateur Surete. L'interface adapte dynamiquement le scope selon le selecteur BL choisi.

### 1.3.3 Selecteur de scope dans l'interface

Le selecteur de BL est un composant React dans le header top bar, a droite de la recherche.

| Type d'utilisateur | Options du selecteur | Defaut |
|--------------------|----------------------|--------|
| Admin | "Toutes les divisions" + liste de toutes les BLs actives | "Toutes les divisions" |
| Manager (2+ BLs) | Liste de ses BLs assignees | Sa BL primaire |
| Manager (1 BL) | Pas de selecteur | Sa BL unique |
| Collaborateur (2+ BLs) | Liste de ses BLs (can_edit=True) | Sa BL primaire |
| Collaborateur (1 BL) | Pas de selecteur | Sa BL unique |
| Viewer (2+ BLs) | Liste de ses BLs (can_edit=False) | Sa BL primaire |

**Comportement** : Ouverture par clic sur le bouton affichant la BL courante (badge colore 12px + nom + chevron). Dropdown avec icone couleur, nom BL, badge nombre AO actifs. Selection → rechargement dashboard (animation fondu 200ms). Derniere selection persiste dans localStorage.

---

# PARTIE II — DASHBOARD ADMIN (VUE TRANSVERSALE N+1)

## 2.1 Layout global

### 2.1.1 Structure de la page

Le dashboard admin occupe 100vw x 100vh :
- **Top Bar** (64px) : Logo + barre recherche globale (Cmd+K, command palette) + selecteur BL + icone notifications (badge rouge) + avatar profil
- **Sidebar gauche** (240px, collapsible a 64px) : menu navigation avec 8 items (Dashboard, AO, Equipe, Analytics, Business Lines, TAKA LAB, Memoire, Parametres)
- **Zone principale** (reste) : grille CSS 12 colonnes, gap 20px, padding 24px

**Responsive** : Desktop >=1280px (12 cols), Tablet >=768px (6 cols), Mobile <768px (1 col).

### 2.1.2 Sidebar

| Icône | Label | Route | Description |
|-------|-------|-------|-------------|
| LayoutDashboard | Tableau de bord | `/dashboard` | Vue d'ensemble avec tous les widgets |
| ClipboardList | Appels d'offres | `/tenders` | Liste AO avec filtres avances et Kanban |
| Users | Equipe | `/team` | Gestion collaborateurs, assignations BL |
| PieChart | Analytics | `/analytics` | Rapports detailles, graphiques, export PDF/CSV |
| Building2 | Business Lines | `/business-lines` | CRUD des divisions metiers |
| Bot | TAKA LAB | `/taka-lab` | IA : scoring, qualification auto, recommandations |
| Database | Memoire | `/memory` | Base de connaissances AO similaires |
| Settings | Parametres | `/settings` | Configuration tenant, integrations, facturation |

## 2.2 Widgets du Dashboard Admin (15 widgets)

### RANG 1 — KPIs Cards (4 cartes)

4 cartes occupant chacune 3/12 colonnes, hauteur 140px. Style commun : fond blanc, bordure 1px #E5E7EB, border-radius 12px, ombre 0 1px 3px rgba(0,0,0,0.08), bordure superieure epaisse 4px couleur KPI, icone 24px dans cercle 40px fond colore 10%.

---

**Widget 1 : CA Pipeline**

| Attribut | Valeur |
|----------|--------|
| Titre | "CA Pipeline" |
| Icône | Banknote |
| Couleur | #3B82F6 (bleu) |
| Formule | `SUM(amount_estimated) WHERE stage IN ('preparation', 'submitted')` |

**Contenu** : Valeur principale formatee en EUR (ex: "8 450 000 EUR", 28px gras). Sous-texte evolution vs N-1 avec fleche ("▲ +12,3% vs mois dernier" vert ou "▼ -5,2%" rouge). Date de calcul.

**Interactions** : Clic → `/tenders?filter=pipeline_actif&sort=amount_desc`. Hover → elevation + curseur pointer. Tooltip sur evolution → detail du calcul.

**Drill-down** : Liste AO constituant le CA triee par montant decroissant. Bouton Export CSV. Graphique barres horizontales par BL.

---

**Widget 2 : Taux de reussite global**

| Attribut | Valeur |
|----------|--------|
| Titre | "Taux de reussite" |
| Icône | Target |
| Couleur variable | >= objectif: #10B981, >= objectif-5pts: #F59E0B, < objectif-5pts: #EF4444 |
| Formule | `COUNT(won) / COUNT(won + lost) * 100` sur 12 mois glissants |

**Contenu** : Pourcentage 1 decimale (ex: "22,4%", 28px gras colore). Sous-texte : "Objectif : 25% | Actuel : 22,4% | Ecart : -2,6pts". Periode : "Sur 12 mois glissants (Mai 2025 — Mai 2026)".

**Interactions** : Clic → `/analytics?tab=reussite&period=12m`.

**Drill-down** : Graphique barres groupees par BL avec ligne de reference a l'objectif. Tableau detaille par BL, collaborateur, CPV, trimestre. Selecteur periode (3/6/12/24 mois).

---

**Widget 3 : AO en cours**

| Attribut | Valeur |
|----------|--------|
| Titre | "AO en cours" |
| Icône | FileText |
| Couleur | #8B5CF6 (violet) |
| Formule | `COUNT() WHERE stage NOT IN ('won', 'lost', 'abandoned', 'archived')` |

**Contenu** : Nombre entier ("147", 28px gras). Sous-texte : "Dont 8 en deadline J-7" (rouge si >5, orange 1-5, vert si 0). Repartition : "Preparation : 62 | Soumis : 45 | En attente : 40".

**Interactions** : Clic → `/tenders?filter=actifs`. Clic sous-texte deadline → `/tenders?filter=deadline_urgente`.

---

**Widget 4 : Qualifications (30j)**

| Attribut | Valeur |
|----------|--------|
| Titre | "Qualifications (30j)" |
| Icône | GitPullRequest |
| Couleur | #F59E0B (orange) |
| Formule | `COUNT(GO) / COUNT(GO + NO-GO + MAYBE) * 100` sur 30 jours glissants |

**Contenu** : "% GO" (ex: "45%", 28px gras). Sous-texte : "GO : 45% | MAYBE : 30% | NO-GO : 25%" (cercles colores). "Base sur 60 qualifications sur les 30 derniers jours".

**Interactions** : Clic → `/analytics?tab=qualifications&period=30d`.

---

### RANG 2 — Graphiques principaux (2 widgets cote a cote)

**Widget 5 : Repartition par division**

| Attribut | Valeur |
|----------|--------|
| Titre | "Repartition par division" |
| Sous-titre | "AO actifs et CA remporte sur 12 derniers mois" |
| Colonnes | 6/12 |
| Hauteur | 380px |

**Contenu** : Graphique barres empilees horizontales. Axe Y : noms des BLs (Telecom, Surete, CVC, Electricite, Controle d'acces) avec pastille couleur 12px. Axe X : nombre d'AO. Barres empilees par statut : Detecte (bleu clair), En cours (bleu), Soumis (orange), Gagne (vert), Perdu (rouge). Largeur barres 32px.

Tableau recapitulatif sous le graphique :

| Division | AO actifs | AO gagnes (12m) | Taux reussite | CA remporte | Objectif | Ecart |
|----------|-----------|-----------------|---------------|-------------|----------|-------|
| Telecom | 52 | 18 | 35,2% | 4 200 000 EUR | 5 000 000 | -16,0% |
| Surete | 38 | 12 | 28,5% | 2 800 000 EUR | 3 000 000 | -6,7% |
| CVC | 31 | 8 | 22,4% | 1 500 000 EUR | 2 000 000 | -25,0% |
| Electricite | 26 | 10 | 30,1% | 3 100 000 EUR | 3 500 000 | -11,4% |
| Controle d'acces | 0 | 0 | — | 0 EUR | 500 000 | — |

**Interactions** : Clic sur une barre BL → filtre dashboard sur cette BL (mise a jour selecteur). Hover section barre → tooltip valeur + %. Clic ligne tableau → profil detaille BL. Bouton "Voir en detail" → `/analytics?tab=business-lines`.

---

**Widget 6 : Evolution mensuelle**

| Attribut | Valeur |
|----------|--------|
| Titre | "Evolution mensuelle" |
| Sous-titre | "Tendance sur 12 mois glissants" |
| Colonnes | 6/12 |
| Hauteur | 380px |

**Contenu** : Line chart avec 3 series. Axe X : mois Mai 2025 a Mai 2026. Axe Y : nombre d'AO. Courbe 1 — AO detectes (#3B82F6, trait plein 2px, points ronds 6px). Courbe 2 — AO qualifies GO (#10B981, trait plein 2px, points carres 6px). Courbe 3 — AO gagnes (#F59E0B, trait plein 2px, points triangles 6px). Legende en haut avec checkbox afficher/masquer. Grille horizontale pointillee #E5E7EB.

**Interactions** : Hover point → tooltip mois + valeur + evolution vs mois precedent. Clic mois → liste AO du mois. Toggle periode "3M | 6M | 12M | 24M". Filtre par BL via selecteur global.

---

### RANG 3 — Tableaux de suivi (2 widgets)

**Widget 7 : Performance des charges d'affaires**

| Attribut | Valeur |
|----------|--------|
| Titre | "Performance des charges d'affaires" |
| Colonnes | 7/12 |
| Hauteur | 420px (scrollable) |

**Contenu** : Tableau 8 colonnes triables. Lignes alternees #F9FAFB/blanc. Hover ligne #F3F4F6.

| Colonne | Contenu | Triable | Largeur |
|---------|---------|---------|---------|
| Collaborateur | Avatar 28px + Nom + email | Oui | 200px |
| Division | Badge couleur BL | Oui | 140px |
| AO actifs | Nombre entier | Oui | 90px |
| AO gagnes (12m) | Nombre entier | Oui | 110px |
| AO perdus | Nombre entier | Oui | 90px |
| Taux reussite | % 1 decimale + barre progression | Oui | 130px |
| CA remporte | Montage formate (ex: "2,4M EUR") | Oui | 130px |
| Actions | Bouton Voir (Eye) | Non | 80px |

**Barre progression taux reussite** : fond #E5E7EB, remplissage vert >=30%, orange 20-29%, rouge <20% + badge "Attention" clignotant.

**Donnees exemple (Equans)** :

| Collaborateur | Division | AO actifs | Gagnes | Perdus | Taux | CA remporte |
|---------------|----------|-----------|--------|--------|------|-------------|
| Jean Dupont | Telecom | 12 | 8 | 15 | 34,8% | 2 450 000 EUR |
| Marie Martin | Surete | 8 | 5 | 12 | 29,4% | 1 820 000 EUR |
| Pierre Leroy | CVC | 6 | 3 | 8 | 27,3% | 950 000 EUR |
| Sophie Bernard | Telecom | 10 | 6 | 10 | 37,5% | 1 800 000 EUR |
| Ahmed Hassan | Electricite | 7 | 4 | 9 | 30,8% | 1 200 000 EUR |
| Claire Dubois | Surete | 5 | 2 | 7 | 22,2% | 680 000 EUR |

**Interactions** : Clic ligne → `/team/:userId` (profil detaille). Tri colonne ▲/▼. Filtre texte par nom. Pagination 10 lignes/page. Export CSV.

---

**Widget 8 : Pipeline synthetique**

| Attribut | Valeur |
|----------|--------|
| Titre | "Pipeline synthetique" |
| Colonnes | 5/12 |
| Hauteur | 420px |

**Contenu** : Grille 8 colonnes miniatures (Detecte | Qualifie | En prep. | Soumis | Gagne | Perdu | Abandonne | En attente). Chaque colonne : header 52px fond #F9FAFB avec nom stage majuscules 13px gras couleur stage + badge compteur 22px + montant total "Sigma 3,2M EUR" 12px gris. Bordure inferieure epaisse 3px couleur stage.

**Code couleur stages** : Detecte=#3B82F6, Qualifie=#10B981, En prep.=#F59E0B, Soumis=#8B5CF6, Gagne=#059669, Perdu=#EF4444, Abandonne=#9CA3AF, En attente=#64748B.

**Interactions** : Clic colonne → `/tenders?view=kanban&stage=detecte`. Tooltip compteur → repartition par BL. Hover → fond legerement plus fonce.

---

### RANG 4 — Alertes et Actions (2 widgets)

**Widget 9 : Alertes prioritaires**

| Attribut | Valeur |
|----------|--------|
| Titre | "Alertes prioritaires" |
| Colonnes | 7/12 |
| Hauteur | 320px |

**Contenu** : Liste verticale scrollable de cartes alerte (max 6 visibles). Chaque carte : icone priorite 24px dans cercle 36px + titre + description + badge metadonnees (date, BL, collaborateur) + fleche navigation.

**Priorites** :
- **Critique (Rouge)** : #FEE2E2 fond, #DC2626 icone AlertTriangle. Deadline J-3 ou moins, inaction >14j sur AO qualifie GO.
- **Attention (Orange)** : #FEF3C7 fond, #D97706 icone AlertCircle. Deadline J-7 a J-3, qualification MAYBE non mise a jour depuis 7j.
- **Information (Bleu)** : #DBEAFE fond, #2563EB icone Info. Nouvel AO detecte score >80%, recommandation IA.

**Exemples d'alertes** :
1. [CRITIQUE] "Deadline J-3 : Deploiement fibre optique — Mairie de Lyon (1,85M EUR)" — Telecom | Jean Dupont | Action : Finaliser DCE
2. [CRITIQUE] "NO-GO confirme sur Hôpital Nord Grenoble — a archiver" — CVC | Pierre Leroy
3. [ATTENTION] "Nouvel AO CPV 45233200 detecte — score 85% GO" — Source BOAMP
4. [ATTENTION] "Pierre Leroy n'a pas qualifie ses 3 AO cette semaine"
5. [INFO] "TAKA LAB : Vous gagnez 40% plus d'AO Telecom que CVC"
6. [INFO] "Objectif Telecom atteint a 92% — 450K EUR restants"

**Interactions** : Clic alerte → navigation AO concerne. Fermeture croix → marque comme lue. Tabs "Toutes | Critiques | Attention | Info". Bouton "Tout marquer comme lu".

---

**Widget 10 : Actions rapides**

| Attribut | Valeur |
|----------|--------|
| Titre | "Actions rapides" |
| Colonnes | 5/12 |
| Hauteur | 320px |

**Contenu** : Grille 2x3 boutons carte carree (~140x80px). Icone 32px centree + label 14px.

| Bouton | Icone | Action au clic |
|--------|-------|----------------|
| Nouvel AO | PlusCircle | Modal creation rapide (titre, CPV, montant, deadline, BL) |
| Uploader DCE | Upload | Modal drag-and-drop PDF (declenche analyse IA) |
| Lancer veille | Radar | Declenche polling BOAMP/TED/Places (spinner pendant execution) |
| Exporter | Download | Modal choix format (PDF/CSV/Excel), periode, scope |
| Gerer equipe | Users | Navigation `/team` (gestion collaborateurs, invitations, assignations BL) |
| Config. BL | Settings2 | Navigation `/business-lines` (CRUD BLs, CPV, keywords, objectifs) |

**Style** : Fond blanc, bordure 1px #E5E7EB, border-radius 10px. Hover : fond #F9FAFB, bordure #3B82F6, elevation 0 2px 8px rgba(59,130,246,0.15). Active : fond #EFF6FF, scale(0.98). Transition 150ms.

---

### RANG 5 — Memoire et IA (2 widgets)

**Widget 11 : Insights TAKA LAB**

| Attribut | Valeur |
|----------|--------|
| Titre | "Insights TAKA LAB" |
| Colonnes | 7/12 |
| Hauteur | 280px |
| Badge | "IA" avec icone Sparkles |

**Contenu** : 3 a 5 insights Mistral AI sous forme de cartes empilees. Chaque insight : icone type 32px + titre 14px gras + description 13px #6B7280 2-3 lignes + badge confiance + bouton action.

**Exemples** :
1. **Performance comparative** (TrendingUp vert) : "Opportunite de renforcement CVC — Vous gagnez 40% plus d'AO Telecom que CVC (35% vs 22%). Envisagez +1 charge d'affaires CVC ou ajustez le scoring." Confiance 92%. Action → `/taka-lab?insight=cvc-vs-telecom`
2. **Urgence** (Clock orange) : "3 AO avec deadline cette semaine — Mairie de Lyon Fibre, Hopital Saint-Etienne VSS, Metropole Rouen CVC." Confiance 100%. Action → `/tenders?filter=deadline_7j`
3. **Opportunite CPV** (Target bleu) : "CPV 45310000 (Travaux batiment) : taux de succes 45%, > moyenne 28%. 4 nouveaux AO detectes." Confiance 78%. Action → `/tenders?cpv=45310000`

**Niveaux confiance** : >=90% vert "Tres fiable", 70-89% orange "Fiable", <70% gris "A verifier".

**Interactions** : Clic "En savoir plus" → TAKA LAB detaille. Clic "Appliquer" → execute action recommandee. Rafraichir → relance analyse IA (limite 1 fois/heure).

---

**Widget 12 : Memoire des AO similaires**

| Attribut | Valeur |
|----------|--------|
| Titre | "Memoire des AO similaires" |
| Colonnes | 5/12 |
| Hauteur | 280px |

**Contenu** : 3-4 entrees memoire. Chaque carte : pastille statut (gagne=vert, perdu=rouge, 8px) + titre tronque 50 caracteres 13px gras + metadonnees (CPV, montant, date, BL) + lien "Voir le profil".

**Exemples** :
1. [GAGNE] Mairie de Villeurbanne — Renovation eclairage public. CPV 45232100 | 1,2M EUR | Mars 2025 | Electricite. Pattern : "CPV recurrent Metropole Lyon, taux reussite 60%"
2. [PERDU] Centre commercial Part-Dieu — Systeme VSS. CPV 35121000 | 850K EUR | Avril 2025 | Surete. Pattern : "Echec delai trop court (8j), privilegier AO >15j"
3. [GAGNE] Residence Les Oliviers — Deploiement CVC. CPV 45331000 | 420K EUR | Fev. 2025 | CVC. Pattern : "AO recurrent secteur tertiaire, bien preparer references"

**Interactions** : Clic entree → fiche AO detaillee. Clic "Pattern" → tooltip explication. Bouton "Voir toute la memoire" → `/memory`.

## 2.3 Vue detaillee "Profil d'un charge d'affaires"

Clic sur un collaborateur dans Widget 7 → navigation `/team/:userId`.

### 2.3.1 Header du profil (160px, fond degrade subtil)

- Avatar 80px circulaire avec bordure 3px couleur BL
- Nom complet 24px gras + email 14px gris + badge division (pastille couleur + nom BL) + badge statut (Actif vert / En conge orange / Inactif gris / Suspendu rouge) + "Membre depuis Janvier 2024"

**Boutons d'action** (alignes droite) :
- **Reassigner ses AO** (outline bleu, Shuffle) : modal selection nouveau proprietaire pour AO actifs. Option "Conserver l'historique" cochee par defaut.
- **Modifier son scope** (outline gris, Settings) : modal checklist BLs avec cases "Assigne", "Primaire", "Peut editer", "Peut assigner". Sauvegarde atomique.
- **Desactiver compte** (outline rouge, Lock) : soft delete avec confirmation + motif. `is_active=False`, donnees conservees.
- **Envoyer message** (primaire bleu, Mail) : modal objet + contenu + option notification email.

### 2.3.2 Onglets (5 onglets horizontalux avec indicateur anime)

**Onglet 1 — Vue d'ensemble** : 4 KPIs cards personnels (AO actifs, taux reussite 12m, CA remporte 12m, qualifications ce mois) + graphique barres empilees activite 4 semaines + donut repartition par statut.

**Onglet 2 — Ses AO** : Tableau complet des AO assignes avec colonnes (Titre, Reference, Division, Montant, Deadline, Qualification, Stage, Date assignation). Filtres : BL, stage, qualification, deadline, montant. Pagination 15 lignes. Export CSV.

**Onglet 3 — Activite** : Timeline verticale chronologique. Evenements : Qualification (CheckCircle vert), Deplacement (ArrowRight bleu), Upload (FileUp violet), Note (MessageSquare orange), Assignation (UserPlus gris), Creation (PlusCircle bleu clair). Filtres : type, periode, BL.

**Onglet 4 — Performance** : Courbe taux reussite mensuel 12 mois + ligne reference moyenne BL (pointilles). Bar charts : CA remporte par mois + nombre qualifications par mois. Tableau performance mensuelle avec colonnes (Mois, Gagnes, Perdus, Taux, CA, Qualifications, vs Moyenne BL).

**Onglet 5 — Objectifs** : 3 jauges circulaires (CA annuel realise/cible, Soumissions realise/cible, Taux reussite realise/cible). Couleurs : vert >=80%, orange 50-79%, rouge <50%. Historique objectifs annee N et N-1.

---

# PARTIE III — DASHBOARD COLLABORATEUR (CHARGE D'AFFAIRES)

## 3.1 Vue par defaut : Kanban

Le collaborateur arrive directement sur sa vue Kanban (`/my-board`).

### 3.1.1 Selecteur business line

- **1 BL assignee** : pas de selecteur, vue directe
- **2+ BLs** : dropdown avec ses BLs (`can_edit=True`) + option "Toutes mes divisions"

### 3.1.2 Colonnes Kanban

8 colonnes fixes : Detecte | Qualifie | En preparation | Soumis | Gagne | Perdu | Abandonne | En attente.

Dimensions : min-width 280px, max-width 320px, hauteur 100% zone dispo, gap 16px, scroll horizontal natif, scroll vertical par colonne independant.

**Header colonne** (52px, fond #F9FAFB, bordure basse 2px couleur stage) : nom stage majuscules 13px gras + badge compteur circulaire 22px + montant total "Sigma 3,2M EUR" 12px gris + icone "+" creation AO.

**Zone de drop** : HTML5 Drag & Drop. Fond legerement colore (opacite 5%) au survol. Colonnes Gagne/Perdu/Abandonne declenchent confirmation modale au drop.

### 3.1.3 Cartes Kanban

Dimensions : largeur 100% colonne, hauteur auto, padding 14px, border-radius 10px, bordure gauche epaisse 3px couleur BL.

**Contenu carte** :
- Titre tronque 2 lignes 13px gras #111827
- CPV + reference acheteur 11px #6B7280
- Montant 14px gras #111827 (ou "Montant non renseigne" italique gris)
- Badge qualification : pill border-radius 999px. GO=#D1FAE5/#065F46, MAYBE=#FEF3C7/#92400E, NO-GO=#FEE2E2/#991B1B
- Compte rebours deadline : >J-14 vert, J-14 a J-7 orange, J-6 a J-1 rouge clignotant, Jour J="AUJOURD'HUI" fond #DC2626 blanc, Depasse="EN RETARD" fond #7F1D1D blanc
- Pastille BL : cercle 8px couleur + nom 11px gris
- Avatar assigne : cercle 24px initiales, tooltip nom complet

**Interactions** : Clic → Drawer lateral (3.2). Drag & drop → changement stage. Hover → elevation 0 4px 12px rgba(0,0,0,0.1). Clic droit → menu contextuel (Qualifier, Assigner a, Ajouter note, Dupliquer, Archiver).

### 3.1.4 Vue Liste (alternative)

Bouton toggle "Kanban | Liste" en haut de page. Style toggle : selectionne fond bleu #2563EB texte blanc, autre fond gris #F3F4F6 texte gris.

**Tableau Liste** :

| Colonne | Largeur | Triable |
|---------|---------|---------|
| Titre (80 chars) | 25% | Oui |
| Reference | 12% | Oui |
| Division (badge) | 10% | Oui |
| Montant | 10% | Oui |
| Deadline + J-X | 10% | Oui |
| Qualification (badge) | 10% | Oui |
| Stage (badge couleur) | 10% | Oui |
| Actions (Voir, Editer) | 8% | Non |

Filtres : BL (ses BLs uniquement), stage (multi-select), qualification (multi-select), deadline (cette semaine/ce mois/J-7/depassee/toutes), montant (input min/max). Pagination 20 lignes.

## 3.2 Actions sur une carte — Drawer lateral

### 3.2.1 Structure du Drawer

- Largeur 520px desktop, 100% mobile
- Animation translateX(100%) → translateX(0), 250ms ease-out
- Backdrop noir 30% opacite, clic ou Echap pour fermer
- Bouton X en haut

**Header** : Titre AO 18px gras (2 lignes max) + badge stage + badge qualification + breadcrumb "AO > {BL} > {Reference}"

**Onglets** (5) : Details | Documents | Qualification | Historique | Notes

### 3.2.2 Onglet Details

Fiche structuree avec champs : Titre, Reference acheteur, Reference interne, Business line (selecteur), Assigne a (selecteur utilisateurs), CPV, Montant estime, Deadline, Date detection, Source, Description, Acheteur, Lieu execution, Duree marche, Date notification attendue. Chaque champ modifiable a un crayon Pencil 14px → transforme en input au clic. Modifiable par admin/manager. Champs Source, Date detection non modifiables (automatiques).

### 3.2.3 Onglet Documents

Zone upload : rectangle pointille 2px dashed #E5E7EB, icone Upload, texte "Glisser un fichier ici ou cliquer pour parcourir". Accepte PDF, DOC, DOCX, XLS, XLSX (max 20 Mo).

Tableau documents : Nom, Taille, Date upload, Uploader. Actions : Telecharger (Download), Previsualiser (Eye, ouvre PDF.js dans panel), Supprimer (Trash rouge).

### 3.2.4 Onglet Qualification

ScoreCard 5 dimensions :

| Dimension | Score | Barre progression | Poids |
|-----------|-------|---------------------|-------|
| Adequatite technique | 85% | 85% | 25% |
| Competitivite prix | 72% | 72% | 20% |
| Disponibilite | 90% | 90% | 20% |
| Risque contractuel | 65% | 65% | 20% |
| Rentabilite estimee | 88% | 88% | 15% |

Score global : moyenne ponderee (ex: 80,6%). Verdict : >=75% GO (vert CheckCircle), 50-74% MAYBE (orange AlertCircle), <50% NO-GO (rouge XCircle). Description explicative sous le verdict.

Boutons : "Relancer analyse IA" (RefreshCw), "Modifier manuellement" (Pencil), "Valider le verdict" (Check primaire).

### 3.2.5 Onglet Historique

Timeline verticale chronologique filtree sur l'AO courant. Toutes actions de tous utilisateurs (creation, modifications, qualifications, deplacements, uploads, notes). Meme format que l'onglet Activite du profil.

### 3.2.6 Onglet Notes

Interface commentaires type chat. Textarea redimensionnable en bas (placeholder "Ajouter une note..."). Bouton Envoyer (primaire) + Joindre fichier (outline). Messages en bulles avec avatar, nom, date, contenu. @mentions supportees (tapez @ → liste collaborateurs). Reactions emoji (👍, ✅, ❌, 👀).

## 3.3 Notifications du collaborateur

### 3.3.1 Icone et panel

Icone cloche (Bell) dans top bar avec badge rouge 16px (nombre non lues, "9+" si >9). Clic → dropdown panel 400px x 500px max.

**Header panel** : "Notifications" 16px gras + badge non lues + bouton "Tout marquer comme lu".

**Types de notifications** :

| Type | Icone | Couleur | Exemple |
|------|-------|---------|---------|
| Nouvel AO assigne | FilePlus | Bleu | "Nouvel AO assigne : Deploiement fibre optique — Mairie de Lyon" |
| Deadline urgente | Clock | Rouge | "Deadline J-7 : Hopital de Saint-Etienne — Systeme VSS" |
| Qualification terminee | CheckCircle | Vert | "Qualification terminee : Metropole Rouen — CVC, Score 78% GO" |
| Note ajoutee | MessageSquare | Violet | "Marie Martin a ajoute une note sur Mairie de Lyon — Fibre" |
| Mention | AtSign | Orange | "Vous avez ete mentionne dans un commentaire sur 'Residence Les Jardins'" |
| Objectif | Target | Bleu | "Felicitations ! 80% de votre objectif CA mensuel atteint" |

Style : fond blanc, non-lues #F0F9FF. Bordure gauche 3px coloree. Icone 20px. Texte principal 13px + heure 11px gris. Clic → navigation element concerne + marque lue. Swipe gauche ou croix → suppression. Footer : lien "Voir toutes les notifications" → `/notifications` avec pagination infinie.

---

# PARTIE IV — RATIONALISATION ET CONSOLIDATION

## 4.1 Principe de rationalisation

### 4.1.1 Definition

La rationalisation est la capacite du systeme TAKA OS a agreger, consolider et comparer les donnees d'AO issues de multiples business lines et collaborateurs pour fournir aux decideurs (DG, DCE, managers) une vision transversale factuelle pour l'allocation des ressources et l'optimisation des taux de reussite.

### 4.1.2 Les 3 niveaux de rationalisation

1. **Intra-business line** : Le responsable division compare ses charges d'affaires. Exemple : DCE Telecom Equans compare ses 4 charges d'affaires fibre optique, constate que Sophie Bernard (37,5% reussite) surpasse Jean Dupont (34,8%) et reaffecte 2 AO.

2. **Inter-business lines** : Le DG compare les divisions. Exemple : Telecom a 35% reussite et 4,2M EUR CA, CVC est a 22% et 1,5M EUR. Decision : reaffecter un poste CVC vers Telecom + plan formation CVC.

3. **Temporelle** : Comparaison dans le temps. Exemple : taux reussite global passe de 19% janvier a 24% mai, confirmant l'efficacite du nouveau processus qualification IA.

## 4.2 KPIs rationalises (formules exactes)

### 4.2.1 Tableau complet des KPIs

| KPI | Formule SQL | Granularite | Frequence |
|-----|-------------|-------------|-----------|
| Taux de reussite | `COUNT(won) / NULLIF(COUNT(won + lost), 0) * 100` | Global, par BL, par collaborateur, par CPV, par mois | Temps reel |
| Taux qualification GO | `COUNT(GO) / NULLIF(COUNT(GO + NO-GO + MAYBE), 0) * 100` | Global, par BL, par collaborateur, par periode | Temps reel |
| CA remporte | `SUM(amount_estimated) WHERE stage='won'` | Global, par BL, par collaborateur, par annee, trimestre | Temps reel |
| CA pipeline | `SUM(amount_estimated) WHERE stage IN ('preparation','submitted','qualified')` | Global, par BL | Temps reel |
| Delai moyen decision | `AVG(EXTRACT(EPOCH FROM (qualified_at - detected_at))/86400)` | Par BL, par collaborateur | Calcule |
| Taux conversion GO→Soumis | `COUNT(submitted AND GO) / NULLIF(COUNT(GO), 0) * 100` | Par BL, par collaborateur | Temps reel |
| Taux conversion Soumis→Gagne | `COUNT(won) / NULLIF(COUNT(submitted), 0) * 100` | Par BL, global | Temps reel |
| Reussite par CPV | Taux reussite filtre `WHERE cpv_code = :cpv` | Par CPV, par BL | Temps reel |
| Reussite par montant | Taux reussite avec `CASE WHEN amount < 100K THEN '<100K' ... END` | Par tranche | Temps reel |
| Productivite collaborateur | `COUNT(qualifications) / EXTRACT(MONTH FROM AGE(NOW(), created_at))` | Par collaborateur | Mensuel |
| Part de marche interne | `CA_BL / CA_Total * 100` | Par BL | Mensuel |
| Taux abandon | `COUNT(abandoned) / COUNT(*) * 100` | Global, par BL | Temps reel |
| Valeur moyenne AO gagne | `AVG(amount_estimated) WHERE stage='won'` | Global, par BL, par collaborateur | Temps reel |
| Taux de reponse | `COUNT(submitted) / NULLIF(COUNT(submitted + abandoned), 0) * 100` | Global, par BL | Temps reel |
| Ecart objectifs CA | `(CA_Realise - CA_Cible) / CA_Cible * 100` | Par BL, par collaborateur | Mensuel |

### 4.2.2 Seuils d'alerte par KPI

| KPI | Vert | Orange | Rouge | Destinataire |
|-----|------|--------|-------|--------------|
| Taux reussite | >= 30% | 20-29% | < 20% | Manager + Admin |
| Taux qualification GO | >= 50% | 30-49% | < 30% | Manager |
| CA pipeline | >= objectif | 70-99% | < 70% | Admin |
| Delai moyen decision | <= 5 jours | 5-10 jours | > 10 jours | Manager |
| Taux conversion GO→Soumis | >= 70% | 50-69% | < 50% | Manager |
| Taux conversion Soumis→Gagne | >= 25% | 15-24% | < 15% | Admin |
| Productivite | >= 8/mois | 4-7/mois | < 4/mois | Manager |

## 4.3 Rapports automatiques

### 4.3.1 Rapport hebdomadaire (email + notification in-app)

**Destinataires** : Admin + Managers | **Frequence** : Lundi 08h00 | **Canal** : Email + in-app

Contenu type :
- **Chiffres cles** : tableau 6 KPIs (Semaine / Sem.-1 / Evolution) : AO detectes, qualifies, soumis, gagnes, CA remporte, % GO
- **Alertes** (3-5 prioritaires) : deadlines urgentes, inactions, NO-GO a archiver
- **Par division** : Telecom 5 detectes | 2 GO | 35% reussite / Surete 4 detectes | 2 GO | 28% / CVC 2 detectes | 1 GO | 22% / Electricite 1 detecte | 0 GO | 31%
- Boutons : "Voir dashboard complet" | "Gerer les alertes"

### 4.3.2 Rapport mensuel PDF

**Destinataires** : Admin | **Frequence** : 1er du mois 07h00 | **Format** : PDF A4, 8-12 pages

**Plan** : Page couverture (mois, annee, logo) → Resume executif (6 KPIs + evolutions) → Graphique evolution mensuelle courbes 12 mois → Repartition par BL (tableau + graphique) → Performance collaborateurs (tableau complet) → Pipeline synthetique 8 colonnes → Top 10 CPV plus frequents avec taux reussite → Recommandations IA TAKA LAB (2-3 insights) → Objectifs mois suivant (cibles vs realise N-1).

### 4.3.3 Rapport annuel

**Destinataires** : Direction generale | **Frequence** : Genere manuellement (decembre/janvier) | **Format** : PDF A4 paysage, 20-30 pages

Contenu : CA total par BL avec evolution N vs N-1 → Taux reussite global avec benchmark sectoriel → Benchmark interne BL vs BL (tableau + radar chart) → Top 10 CPV plus rentables (taux * volume * montant moyen) → Cartographie performances geographiques → Recommandations strategiques IA → Budget AO recommande N+1 par BL.

## 4.4 Benchmarking interne

### 4.4.1 Tableau comparatif des BL

Accessible via `/analytics?tab=benchmark`.

| Business Line | Taux reussite | CA remporte (12m) | Productivite | Score objectif | Score TAKA |
|---------------|---------------|-------------------|--------------|----------------|------------|
| Telecom | 35,2% | 4 200 000 EUR | 12,3 AO/mois | 95% | A (Excellent) |
| Electricite | 30,1% | 3 100 000 EUR | 9,8 AO/mois | 88% | B (Bon) |
| Surete | 28,5% | 2 800 000 EUR | 8,2 AO/mois | 82% | B (Bon) |
| CVC | 22,4% | 1 500 000 EUR | 6,1 AO/mois | 68% | C (A ameliorer) |
| Controle d'acces | — | 0 EUR | 0 AO/mois | 0% | — (Inactif) |

### 4.4.2 Algorithme de scoring TAKA LAB

```
Score_TAKA = (Taux_reussite / Taux_reussite_max) * 0,40
           + (CA_remporte / CA_max) * 0,35
           + (Productivite / Productivite_max) * 0,25

Note = CASE
    WHEN Score_TAKA >= 0,90 THEN 'A (Excellent)'
    WHEN Score_TAKA >= 0,75 THEN 'B (Bon)'
    WHEN Score_TAKA >= 0,50 THEN 'C (A ameliorer)'
    WHEN Score_TAKA >= 0,25 THEN 'D (Insuffisant)'
    ELSE 'E (Critique)'
END
```

Valeurs maximales calculees sur l'ensemble des BL actives du tenant. La meilleure BL obtient 100% sur chaque critere, les autres sont proportionnelles.

### 4.4.3 Radar chart comparatif

Graphique radar (spider chart) sur 6 axes : Taux reussite, CA remporte, Productivite, Taux conversion GO→Soumis, Taux conversion Soumis→Gagne, Taux qualification GO. Chaque BL est une ligne de couleur differente. La surface couverte represente visuellement les forces et faiblesses relatives.

---

# PARTIE V — INTERFACE EDITEUR (SUPER ADMIN)

## 5.1 Dashboard editeur

### 5.1.1 Acces et securite

Accessible uniquement aux `super_admin` (equipe TAKA OS). Route `/admin` avec 2FA obligatoire.

**Sidebar editeur** : Vue d'ensemble (`/admin`) | Tenants (`/admin/tenants`) | Utilisateurs globaux (`/admin/users`) | Metriques produit (`/admin/metrics`) | Facturation (`/admin/billing`) | Configuration systeme (`/admin/system`) | Logs (`/admin/logs`) | Securite (`/admin/security`).

### 5.1.2 KPIs globaux

4 cartes : Tenants actifs (`COUNT WHERE is_active=true`) | Utilisateurs totaux (`COUNT users`) | MRR (`SUM monthly_subscription_amount`) | Taux churn (`COUNT churnes / COUNT actifs debut mois * 100`).

### 5.1.3 Tableau des tenants

| Colonne | Description | Largeur |
|---------|-------------|---------|
| ID | UUID court (8 premiers chars) | 80px |
| Nom | Nom tenant (cliquable) | 180px |
| Type | Badge "Soumissionnaire" (bleu) ou "Acheteur" (vert) | 120px |
| Business Lines | Nombre BLs actives / total | 100px |
| Utilisateurs | Nombre utilisateurs actifs | 90px |
| AO actifs | Nombre AO en cours | 90px |
| Formule | Free / Starter / Pro / Enterprise | 110px |
| MRR | Montant mensuel paye | 100px |
| Statut | Actif (vert) / Suspendu (orange) / Essai (bleu) / Inactif (gris) | 100px |
| Cree le | Date inscription | 110px |
| Actions | Voir / Editer / Suspendre | 150px |

**Filtres** : type, formule, statut, periode creation, nombre utilisateurs (tranches). Recherche par nom, email admin, ID. Pagination 25 lignes/page.

**Exemple** :

| ID | Nom | Type | BL | Users | AO | Formule | MRR | Statut |
|----|-----|------|-----|-------|-----|---------|-----|--------|
| a3f7b2d1 | Equans France | Soumissionnaire | 5/5 | 45 | 320 | Enterprise | 1 200 EUR | Actif |
| e8c4a9f2 | Sogetrel | Soumissionnaire | 3/3 | 22 | 145 | Pro | 450 EUR | Actif |
| b1d6e3a5 | Mairie de Lyon | Acheteur | 0/0 | 8 | 12 | Free | 0 EUR | Actif |
| f5a2c8b4 | SPIE Industrie | Soumissionnaire | 4/4 | 38 | 210 | Enterprise | 1 200 EUR | Actif |

### 5.1.4 Actions sur un tenant

- **Voir** (Eye) → `/admin/tenants/:tenantId` : profil complet (KPIs, utilisateurs, BLs, AO). Lecture seule.
- **Editer** (Pencil) → modal : nom, formule, limites (max users, AO, uploads Mo, BLs), features actives (checkboxes TAKA LAB, PDF, API, SSO, Webhooks), date fin essai, notes internes.
- **Suspendre** (Pause) → confirmation avec motif. Statut "Suspendu" : acces ecriture bloque, lecture seule. Email auto a l'admin. Bouton devient "Reactiver".
- **Impersonate** (UserCheck) → connexion en tant qu'admin du tenant. Bandeau orange "Mode impersonation — Tenant : Equans — [Terminer]". Actions logguees. Timeout 30min inactivite.

## 5.2 Configuration systeme

### 5.2.1 Feature flags par tenant

| Feature Flag | Description | Defaut | Disponible |
|--------------|-------------|--------|------------|
| `taka_lab_enabled` | Acces TAKA LAB (IA Mistral) | false | Pro, Enterprise |
| `pdf_reports_enabled` | Rapports PDF | false | Pro, Enterprise |
| `api_access_enabled` | API REST complet | false | Enterprise |
| `sso_enabled` | Authentification SAML/OIDC | false | Enterprise |
| `webhooks_enabled` | Webhooks evenementiels | false | Enterprise |
| `custom_branding_enabled` | Logo et couleurs perso. | false | Enterprise |
| `advanced_analytics_enabled` | Analytics avances (benchmark, predictions) | false | Pro, Enterprise |
| `multi_bl_enabled` | Multi-business lines (>1) | true | Tous (max 1 Free) |
| `auto_classification_enabled` | Classification auto BL par IA | true | Starter+ |
| `memory_enabled` | Base memoire similaire | false | Pro, Enterprise |

### 5.2.2 Limites par formule

| Limite | Free | Starter | Pro | Enterprise |
|--------|------|---------|-----|------------|
| Max utilisateurs | 3 | 10 | 50 | Illimite |
| Max business lines | 1 | 3 | 10 | Illimite |
| Max AO actifs | 20 | 100 | 500 | Illimite |
| Max uploads (Mo) | 100 | 1 000 | 10 000 | Illimite |
| Max appels API/jour | 0 | 100 | 10 000 | Illimite |
| Rapports PDF/mois | 0 | 1 | 10 | Illimite |
| TAKA LAB requetes/mois | 10 | 100 | 1 000 | Illimite |
| Support | Email | Email | Email+Chat | Dedie |
| Prix mensuel | 0 EUR | 49 EUR | 199 EUR | Sur devis |

### 5.2.3 Integrations systeme

| Service | Configuration | Statut |
|---------|---------------|--------|
| Mistral AI | Cle API, modele, max tokens, timeout | Actif/Inactif |
| BOAMP | URL endpoint, frequence polling, credentials | Actif/Inactif |
| TED | URL endpoint, frequence polling | Actif/Inactif |
| Places | URL endpoint, credentials | Actif/Inactif |
| SMTP | Host, port, user, password, from address | Actif/Inactif |
| Stockage S3 | Bucket, region, credentials | Actif/Inactif |
| Redis Cache | Host, port, password, DB index | Actif/Inactif |

---

# PARTIE VI — ARCHITECTURE TECHNIQUE DE LA RATIONALISATION

## 6.1 Requetes SQL de consolidation

### 6.1.1 CA remporte par business line

```sql
SELECT
    bl.id AS business_line_id,
    bl.name AS business_line_name,
    bl.color AS business_line_color,
    bl.slug AS business_line_slug,
    COUNT(t.id) AS ao_gagnes_count,
    COALESCE(SUM(t.amount_estimated), 0) AS ca_remporte,
    ROUND(AVG(t.amount_estimated), 2) AS ca_moyen_par_ao,
    bl.annual_target_revenue AS objectif_ca_annuel,
    CASE
        WHEN bl.annual_target_revenue > 0
        THEN ROUND(COALESCE(SUM(t.amount_estimated), 0) / bl.annual_target_revenue * 100, 1)
        ELSE NULL
    END AS taux_objectif_pct
FROM business_lines bl
LEFT JOIN tenders t
    ON t.business_line_id = bl.id
    AND t.tenant_id = :tenant_id
    AND t.pipeline_stage_id = (SELECT id FROM pipeline_stages WHERE slug = 'won' AND tenant_id = :tenant_id)
    AND t.created_at >= :date_debut_12m
    AND t.created_at <= :date_fin
WHERE bl.tenant_id = :tenant_id
    AND bl.is_active = true
GROUP BY bl.id, bl.name, bl.color, bl.slug, bl.annual_target_revenue
ORDER BY ca_remporte DESC;
```

**Parametres** : `:tenant_id` (UUID), `:date_debut_12m` (NOW() - INTERVAL '12 months'), `:date_fin` (NOW()).
**Index** : `tenders(tenant_id, business_line_id, pipeline_stage_id, created_at)` — index composite couvrant.
**Performance** : < 50ms pour 10 000 AO et 10 BLs.

### 6.1.2 Performance par collaborateur

```sql
SELECT
    u.id AS user_id,
    u.full_name AS collaborateur_nom,
    u.email AS collaborateur_email,
    u.role AS user_role,
    bl.id AS business_line_id,
    bl.name AS business_line_nom,
    bl.color AS business_line_couleur,
    COUNT(DISTINCT t_actifs.id) AS ao_actifs,
    COUNT(DISTINCT CASE WHEN ps.slug = 'won' THEN t_histo.id END) AS ao_gagnes_12m,
    COUNT(DISTINCT CASE WHEN ps.slug = 'lost' THEN t_histo.id END) AS ao_perdus_12m,
    ROUND(
        COUNT(DISTINCT CASE WHEN ps.slug = 'won' THEN t_histo.id END)::numeric /
        NULLIF(COUNT(DISTINCT CASE WHEN ps.slug IN ('won', 'lost') THEN t_histo.id END), 0) * 100,
        1
    ) AS taux_reussite_pct,
    COALESCE(SUM(CASE WHEN ps.slug = 'won' THEN t_histo.amount_estimated END), 0) AS ca_remporte_12m,
    COUNT(DISTINCT CASE WHEN ps.slug = 'submitted' THEN t_histo.id END) AS ao_soumis_12m,
    ROUND(
        COUNT(DISTINCT CASE WHEN ps.slug = 'submitted' THEN t_histo.id END)::numeric /
        NULLIF(COUNT(DISTINCT CASE WHEN t_histo.qualification_result = 'GO' THEN t_histo.id END), 0) * 100,
        1
    ) AS taux_conversion_go_soumis_pct
FROM users u
INNER JOIN user_business_lines ubl ON ubl.user_id = u.id AND ubl.can_edit = true
INNER JOIN business_lines bl ON bl.id = ubl.business_line_id AND bl.is_active = true
LEFT JOIN tenders t_actifs
    ON t_actifs.assigned_to_id = u.id
    AND t_actifs.tenant_id = :tenant_id
    AND t_actifs.pipeline_stage_id NOT IN (
        SELECT id FROM pipeline_stages
        WHERE slug IN ('won', 'lost', 'abandoned', 'archived') AND tenant_id = :tenant_id
    )
LEFT JOIN tenders t_histo
    ON t_histo.assigned_to_id = u.id
    AND t_histo.tenant_id = :tenant_id
    AND t_histo.created_at >= :date_debut_12m
LEFT JOIN pipeline_stages ps ON ps.id = t_histo.pipeline_stage_id AND ps.tenant_id = :tenant_id
WHERE u.tenant_id = :tenant_id
    AND u.role IN ('tenant_manager', 'tenant_collaborator')
    AND u.is_active = true
GROUP BY u.id, u.full_name, u.email, u.role, bl.id, bl.name, bl.color
ORDER BY taux_reussite_pct DESC NULLS LAST, ca_remporte_12m DESC;
```

**Parametres** : `:tenant_id`, `:date_debut_12m` (12 mois glissants).
**Performance** : < 100ms pour 50 collaborateurs et 10 000 AO.

### 6.1.3 Materialized view pour les KPIs du dashboard

```sql
CREATE MATERIALIZED VIEW mv_dashboard_kpis AS
WITH ao_stats AS (
    SELECT
        t.tenant_id, t.business_line_id, t.assigned_to_id,
        t.pipeline_stage_id, ps.slug AS stage_slug,
        t.qualification_result, t.amount_estimated,
        t.created_at, t.qualified_at, t.detected_at
    FROM tenders t JOIN pipeline_stages ps ON ps.id = t.pipeline_stage_id
),
bl_kpis AS (
    SELECT
        tenant_id, business_line_id,
        COUNT(*) FILTER (WHERE stage_slug NOT IN ('won','lost','abandoned','archived')) AS ao_actifs,
        COUNT(*) FILTER (WHERE stage_slug = 'won' AND created_at >= NOW() - INTERVAL '12 months') AS ao_gagnes_12m,
        COUNT(*) FILTER (WHERE stage_slug = 'lost' AND created_at >= NOW() - INTERVAL '12 months') AS ao_perdus_12m,
        COALESCE(SUM(amount_estimated) FILTER (WHERE stage_slug = 'won' AND created_at >= NOW() - INTERVAL '12 months'), 0) AS ca_remporte_12m,
        COALESCE(SUM(amount_estimated) FILTER (WHERE stage_slug IN ('preparation','submitted','qualified')), 0) AS ca_pipeline,
        COUNT(*) FILTER (WHERE qualification_result = 'GO' AND created_at >= NOW() - INTERVAL '30 days') AS go_30j,
        COUNT(*) FILTER (WHERE qualification_result IN ('GO','NO-GO','MAYBE') AND created_at >= NOW() - INTERVAL '30 days') AS total_qualif_30j
    FROM ao_stats
    GROUP BY tenant_id, business_line_id
)
SELECT
    tenant_id, business_line_id, ao_actifs, ao_gagnes_12m, ao_perdus_12m,
    ca_remporte_12m, ca_pipeline,
    ROUND(ao_gagnes_12m::numeric / NULLIF(ao_gagnes_12m + ao_perdus_12m, 0) * 100, 1) AS taux_reussite_12m,
    ROUND(go_30j::numeric / NULLIF(total_qualif_30j, 0) * 100, 1) AS taux_go_30j,
    NOW() AS calculated_at
FROM bl_kpis;

CREATE UNIQUE INDEX idx_mv_dashboard_kpis_tenant_bl ON mv_dashboard_kpis(tenant_id, business_line_id);
CREATE INDEX idx_mv_dashboard_kpis_tenant ON mv_dashboard_kpis(tenant_id);

-- Rafraichissement : cron toutes les heures ou trigger apres modification d'AO
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_kpis;
```

## 6.2 API Endpoints

### 6.2.1 Dashboard admin

| Methode | Endpoint | Description | Parametres | Roles |
|---------|----------|-------------|------------|-------|
| GET | `/api/v1/dashboard/admin/kpis` | KPIs consolidés | `period`, `business_line_id` | tenant_admin |
| GET | `/api/v1/dashboard/admin/by-business-line` | KPIs par BL | `period`, `business_line_id` | tenant_admin |
| GET | `/api/v1/dashboard/admin/by-user` | Performance par collaborateur | `period`, `business_line_id` | tenant_admin |
| GET | `/api/v1/dashboard/admin/timeline` | Timeline activite globale | `limit`, `offset`, `business_line_id` | tenant_admin |
| GET | `/api/v1/dashboard/admin/alerts` | Alertes prioritaires | `priority`, `limit` | tenant_admin |
| GET | `/api/v1/dashboard/admin/insights` | Insights IA TAKA LAB | `limit` | tenant_admin |
| GET | `/api/v1/dashboard/admin/pipeline` | Pipeline synthetique | `business_line_id` | tenant_admin |

### 6.2.2 Dashboard collaborateur

| Methode | Endpoint | Description | Parametres | Roles |
|---------|----------|-------------|------------|-------|
| GET | `/api/v1/dashboard/collaborator/kpis` | KPIs personnels | `period` | tenant_collaborator |
| GET | `/api/v1/dashboard/collaborator/assigned` | AO assignes | `stage`, `qualification`, `business_line_id`, `deadline_from`, `deadline_to`, `sort`, `limit`, `offset` | tenant_collaborator |
| GET | `/api/v1/dashboard/collaborator/activity` | Timeline personnelle | `limit`, `offset` | tenant_collaborator |
| GET | `/api/v1/dashboard/collaborator/notifications` | Notifications | `unread_only`, `limit`, `offset` | tenant_collaborator |
| PUT | `/api/v1/dashboard/collaborator/notifications/:id/read` | Marquer comme lue | — | tenant_collaborator |

### 6.2.3 Business lines

| Methode | Endpoint | Description | Roles |
|---------|----------|-------------|-------|
| GET | `/api/v1/business-lines` | Liste BLs du tenant | all (tenant) |
| GET | `/api/v1/business-lines/:id` | Detail d'une BL | all (tenant, si visible) |
| POST | `/api/v1/business-lines` | Creer une BL | tenant_admin |
| PUT | `/api/v1/business-lines/:id` | Modifier une BL | tenant_admin |
| DELETE | `/api/v1/business-lines/:id` | Desactiver (soft delete) | tenant_admin |
| GET | `/api/v1/business-lines/:id/users` | Utilisateurs de la BL | tenant_admin, tenant_manager |
| GET | `/api/v1/business-lines/:id/tenders` | AO de la BL | all (tenant, si visible) |

### 6.2.4 Gestion scopes utilisateurs

| Methode | Endpoint | Description | Roles |
|---------|----------|-------------|-------|
| GET | `/api/v1/users/:id/scope` | Scope actuel | tenant_admin, tenant_manager |
| PUT | `/api/v1/users/:id/scope` | Modifier le scope | tenant_admin |
| POST | `/api/v1/users/:id/reassign-tenders` | Reassigner les AO | tenant_admin, tenant_manager |
| PUT | `/api/v1/users/:id/deactivate` | Desactiver compte | tenant_admin |

### 6.2.5 Rapports

| Methode | Endpoint | Description | Parametres | Roles |
|---------|----------|-------------|------------|-------|
| GET | `/api/v1/reports/weekly` | Rapport hebdo | `date` | tenant_admin |
| GET | `/api/v1/reports/monthly` | Rapport mensuel PDF | `month`, `year`, `business_line_id` | tenant_admin |
| GET | `/api/v1/reports/annual` | Rapport annuel PDF | `year` | tenant_admin |
| GET | `/api/v1/reports/benchmark` | Donnees benchmarking | `period` | tenant_admin |

## 6.3 Performance et index

### 6.3.1 Strategie d'indexation

| Table | Index | Colonnes | Type | Justification |
|-------|-------|----------|------|---------------|
| tenders | `idx_tenders_tenant_bl_stage` | `(tenant_id, business_line_id, pipeline_stage_id)` | B-tree | Requete principale dashboard |
| tenders | `idx_tenders_tenant_qualif_date` | `(tenant_id, qualification_result, created_at)` | B-tree | KPIs qualification |
| tenders | `idx_tenders_assigned_stage` | `(assigned_to_id, pipeline_stage_id)` | B-tree | Vue Kanban collaborateur |
| tenders | `idx_tenders_tenant_created` | `(tenant_id, created_at DESC)` | B-tree | Rapports historiques |
| tenders | `idx_tenders_cpv` | `(cpv_code)` | B-tree | Filtrage CPV |
| business_lines | `idx_bl_tenant_active` | `(tenant_id, is_active)` | B-tree | Liste BLs actives |
| business_lines | `idx_bl_tenant_slug` | `(tenant_id, slug)` | UNIQUE | Unicite slug par tenant |
| user_business_lines | `idx_ubl_user` | `(user_id)` | B-tree | BLs d'un utilisateur |
| user_business_lines | `idx_ubl_bl` | `(business_line_id)` | B-tree | Utilisateurs d'une BL |
| user_business_lines | `idx_ubl_user_primary` | `(user_id, is_primary)` WHERE is_primary=true | UNIQUE | Une seule BL primaire |

### 6.3.2 Materialized views et cache

| View / Cache | Contenu | Rafraichissement | TTL |
|--------------|---------|------------------|-----|
| `mv_dashboard_kpis` | KPIs par BL (actifs, gagnes, perdus, CA, taux) | Cron horaire + trigger | 1 heure |
| `mv_user_performance` | Performance par collaborateur (12 mois) | Cron horaire | 1 heure |
| `mv_cpv_success_rate` | Taux reussite par CPV | Tous les nuits | 24 heures |
| Redis `dashboard:{tenant_id}:kpis` | KPIs consolidées JSON | Invalidation MV | 1 heure |
| Redis `dashboard:{tenant_id}:bl:{id}` | KPIs par BL JSON | Invalidation MV | 1 heure |

### 6.3.3 Plan de montee en charge

| Phase | Seuil | Optimisation |
|-------|-------|-------------|
| v0.1 MVP | < 1 000 AO/tenant | Index B-tree + requetes directes, pas de cache |
| v0.5 | < 10 000 AO/tenant | Materialized views, cache Redis 1h |
| v1.0 | < 100 000 AO/tenant | Partitionnement par `(tenant_id, DATE(created_at))`, read replicas |
| v2.0 | > 100 000 AO/tenant | ClickHouse/BigQuery analytique, PostgreSQL transactionnel |

### 6.3.4 Securite multi-tenants

**Regle fondamentale** : Toute requete SQL DOIT inclure `tenant_id = :current_tenant_id` comme premier filtre.

**Middleware d'application** :
```python
async def scope_middleware(request):
    user = request.state.user
    request.state.tenant_id = user.tenant_id

    if user.role == "tenant_admin":
        request.state.visible_bl_ids = None  # Global
    elif user.role == "tenant_manager":
        request.state.visible_bl_ids = await get_manager_bl_ids(user.id)
    elif user.role == "tenant_collaborator":
        request.state.visible_bl_ids = await get_collaborator_bl_ids(user.id)
    elif user.role == "tenant_viewer":
        request.state.visible_bl_ids = await get_viewer_bl_ids(user.id)
```

**Application du scope** :
```python
query = select(Tender).where(Tender.tenant_id == request.state.tenant_id)

if request.state.visible_bl_ids is not None:
    query = query.where(Tender.business_line_id.in_(request.state.visible_bl_ids))

if request.state.user.role == "tenant_collaborator":
    query = query.where(Tender.assigned_to_id == request.state.user.id)
```

---

# ANNEXE — Glossaire

| Terme | Definition |
|-------|------------|
| **Business Line (BL)** | Division metier au sein d'un tenant (ex: Telecom, Surete, CVC). Entite centrale de la rationalisation multi-metiers. |
| **Scope** | Niveau de visibilite d'un utilisateur (Global, Business Line, Individuel, Lecture seule). |
| **Tenant** | Entreprise cliente inscrite sur TAKA OS (ex: Equans, Sogetrel). Isolation complete des donnees. |
| **Charge d'affaires** | Collaborateur operationnel responsable du suivi et de la qualification des AO. |
| **DCE** | Dossier de Consultation des Entreprises. Document complet d'un appel d'offres. |
| **CPV** | Common Procurement Vocabulary. Code europeen classifiant les marches publics. |
| **ScoreCard** | Grille d'evaluation en 5 dimensions generee par TAKA LAB. |
| **TAKA LAB** | Module IA utilisant Mistral pour la qualification automatique et les recommandations strategiques. |
| **Kanban** | Vue visuelle du pipeline en 8 colonnes (Detecte, Qualifie, En preparation, Soumis, Gagne, Perdu, Abandonne, En attente). |
| **Rationalisation** | Capacite a consolider et comparer les donnees de multiples BLs pour une prise de decision eclairee. |
| **Materialized View** | Vue materialisee PostgreSQL : snapshot pre-calcule pour des performances optimales. |
| **MRR** | Monthly Recurring Revenue. Revenu mensuel recurrent des abonnements tenants. |
| **Impersonate** | Capacite pour l'equipe TAKA OS de se connecter en tant qu'admin d'un tenant pour le support. |
| **Soft Delete** | Suppression logique (is_active=false) preservant les donnees pour l'historique. |
