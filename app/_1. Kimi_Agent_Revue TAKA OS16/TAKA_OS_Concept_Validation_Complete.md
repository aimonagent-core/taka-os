# TAKA OS — Validation Conceptuelle Complete
## Vertical Appels d'Offres | Modele Organisationnel | Flows | Interfaces par Role

**Version** : 1.0
**Date** : Mai 2026
**Classification** : Document de validation conceptuelle pre-developpement
**Statut** : GO — Validation CEO
**Licence** : MIT

---

## Resume Executif

Ce document valide l'approche "vertical separe" de TAKA OS : developper d'abord le vertical Appels d'Offres (v1), puis deriver le vertical Fiducial (v2) a partir de la base technique AO. Il definit le modele organisationnel complet a 5 roles, les flows d'onboarding detailles, les interfaces par role, et l'architecture de segregation multi-tenant a 2 types de tenants (soumissionnaire et acheteur public).

**Decision fondatrice** : Le CEO a decide de concentrer les ressources de developpement sur le vertical AO en premier, pour valider le produit sur un marche de 200+ Mds EUR/an avant d'elargir a d'autres verticals.

---

# PARTIE I — ANALYSE CRITIQUE : APPROCHE VERTICAL SEPARE

## 1.1 Vision Produit

### TAKA OS — Appels d'Offres (v1) — M1 a M6

Plateforme agentique open source (licence MIT) verticalisee sur les Appels d'Offres publics et prives en France, Belgique et Maroc. Le produit cible deux populations distinctes :

- **Les soumissionnaires** (PME/ETI) : entreprises qui repondent aux marches publics. Ils utilisent TAKA OS pour detecter les AO pertinents, qualifier les opportunites (scoring GO/NO-GO/MAYBE), rediger les documents de candidature (memoire technique, DCE, attestations), suivre les deadlines et capitaliser sur les echecs/succes passes.
- **Les acheteurs publics** (collectivites, etablissements publics) : organismes qui publient des AO. Ils utilisent TAKA OS pour rediger les CCTP/CCAG, gerer les candidatures, repondre aux questions des soumissionnaires et produire les rapports de conformite.

### TAKA OS — Fiducial (v2) — M7 a M12

Plateforme derivee du kernel TAKA OS, adaptee aux experts-comptables et cabinets financiers. Elle reutilise la meme base technique (auth, memoire, event bus, audit) mais implemente des agents metiers differents : veille reglementaire comptable, generation de liasses fiscales, automatisation des clotures, analyse des ecarts, conformite fiscale.

### Principe directeur

Le kernel TAKA OS (EventBus, RBAC, Multi-tenancy, Vault, Audit, Memory Mesh) est concu comme generique et reutilisable. Les verticals (AO, Fiducial, Juridique, RH, etc.) sont des "skins metiers" qui s'enrichissent progressivement autour d'un noyau commun stable.

---

## 1.2 Analyse en Avantages (+)

### Avantage 1 — Focus marché sur un TAM de 200+ Mds EUR/an

Le marche des marches publics en France represente plus de 200 milliards d'euros par an en volume d'achats publics. Plus de 130 000 PME/ETI soumissionnent regulierement. Ce marche est suffisamment vaste pour justifier un produit dedie, et suffisamment fragmente (process manuels, outils generiques inadaptes) pour qu'une solution verticalisee apporte une valeur differentiante immediate. Contrairement a un produit generique "TAKA OS pour tout", le message est clair : "TAKA OS = les Appels d'Offres".

### Avantage 2 — Concentration des ressources de developpement

L'equipe de developpement peut se concentrer sur un seul domaine metier a la fois. Pas de dilution entre la comprehension des DCE, des CPV, des CCAG pour les AO, et la comprehension des liasses fiscales, des plans comptables, des echeances declaratives pour le Fiducial. Chaque ligne de code sert le meme objectif. Chaque test utilisateur se fait dans le meme contexte. Chaque retour client enrichit le meme produit.

### Avantage 3 — Message marketing clair et immediat

Le positionnement "TAKA OS — Le systeme d'exploitation agentic pour les Appels d'Offres" est comprehensible en 5 secondes. Il ne necessite pas d'expliquer ce qu'est un "OS agentic" ni de justifier la polyvalence du produit. La landing page peut cibler des mots-cles precis : "scoring AO", "qualification marches publics", "memoire technique IA", "veille BOAMP". Le SEO est plus efficace. Les campagnes d'acquisition sont plus ciblees. Le cout d'acquisition client (CAC) est reduit.

### Avantage 4 — Base technique solide pour deriver Fiducial

Le kernel TAKA OS developpe pour AO est reellement generique :
- Le systeme d'authentification JWT + RBAC fonctionnera pour Fiducial sans modification
- Le multi-tenancy par `tenant_id` s'applique identiquement
- Le Vault pour les credentials API est transverse
- L'audit trail append-only avec hash chain est transverse
- L'EventBus (asyncio puis NATS) est generique
- La Memory Mesh (episodique + transactionnelle) est reutilisable
- Le parsing PDF, l'OCR, les templates Jinja2 sont transverses

Le travail pour Fiducial consistera principalement a : creer de nouveaux agents metiers, de nouveaux connecteurs (API Dougs, Pennylane), de nouveaux templates documentaires, et de nouvelles regles de scoring. Le kernel ne sera pas recrit.

### Avantage 5 — Temps de validation marché plus court

En se concentrant sur un seul vertical, le Time-to-Market (TTM) pour la v0.1 fonctionnelle est estime a 4 semaines (S1-S4 du blueprint). Le premier client payant peut etre acquis au mois 2. Les premiers retours utilisateurs concrets arrivent au mois 2-3. Cette velocite permet d'ajuster le produit rapidement avant d'investir dans un second vertical. Si le vertical AO echoue a trouver son Product-Market Fit, l'investissement est contenu. Si on avait developpe AO + Fiducial en parallele, l'echec serait deux fois plus couteux.

### Avantage 6 — Communauté open source ciblee et engagee

Le projet open source sous licence MIT attire naturellement des contributeurs passionnes par le domaine. Les developpeurs travaillant dans les marches publics (SSII, editeurs de logiciels de DC, cabinets specialises) ont une motivation intrinseque a contribuer. Une communaute ciblee produit des contributions de meilleure qualite qu'une communaute diffuse. Les issues GitHub sont precises. Les pull requests sont pertinentes. Les retours sont actionnables.

### Avantage 7 — Courbe d'apprentissage agentic maitrisable

TAKA OS est le premier systeme d'exploitation agentic open source. La complexite de l'orchestration de 6 agents specialises (Veilleur, Scorer, Redacteur, Deposant, Auditor, Compliance Officer) est deja significative. En se concentrant sur un seul vertical, l'equipe maitrise la courbe d'apprentissage progressivement. L'experience acquise sur la gestion des etats d'agents, la resolution de conflits, la recovery d'erreurs, et le monitoring sera directement applicable au vertical Fiducial.

### Avantage 8 — Partenariats commerciaux cibles

Un vertical AO permet de nouer des partenariats precis et a forte valeur : chambres de commerce (CCI France), groupements d'acheteurs (UGAP, Sante_publique), plateformes de dematerialisation (e-marchespublics, Attractivite), cabinets specialises en reponse aux AO. Ces partenariats sont plus faciles a etablir quand le message produit est clair. Un partenariat avec une CCI sur le theme "aidez les PME locales a repondre aux marches publics" est immediat et comprehensible.

---

## 1.3 Analyse en Inconvenients (-)

### Risque 1 — "Silo technique" : la base AO peut devenir trop specifique

Si l'architecture du kernel n'est pas suffisamment abstraite des le depart, les tables metier AO (`tenders`, `tender_documents`, `qualification_rules`, `pipeline_stages`) peuvent polluer le modele de donnees. Lors de la derivation vers Fiducial, le nettoyage pourrait etre couteux. Par exemple, si la table `memory_vectors` stocke des embeddings specifiques a la terminologie des marches publics (CPV, CCAG, DCE), leur reutilisation pour des documents comptables sera limitee.

**Mitigation** : Le kernel doit rester strictement separe des agents metiers. Les embeddings doivent etre accompagnes d'un champ `domain` qui permet de filtrer par vertical. Les tables metier doivent etre dans un schema ou un prefixe distinct (`ao_tenders`, `fiducial_declarations`).

### Risque 2 — Double travail si l'architecture n'est pas assez abstraite

Si le modele de donnees du MVP v0.1 est "code en dur" pour les AO sans reflexion d'abstraction, la migration vers une architecture multi-verticals au moment de lancer Fiducial necessitera une refactorisation profonde. Cela peut representer 3 a 4 semaines de travail pur de refactoring, sans valeur ajoutee utilisateur.

**Mitigation** : Des la v0.1, le champ `tenant_type` doit exister dans la table `tenants`. Les agents doivent etre enregistres dans un registre generique (`agent_registry`) et non codes en dur dans l'orchestrateur. L'EventBus doit utiliser des topics generiques (`ao.new_detected` → `vertical.ao.event.detected`).

### Risque 3 — Perte des early-adopters experts-comptables

En retardant le vertical Fiducial de 6 a 12 mois, les experts-comptables interesses par TAKA OS a sa sortie peuvent se tourner vers des solutions concurrentes qui emergent sur ce creneau (Pennylane, Dougs, ou des startups IA comptables). L'attente peut faire perdre le "premier mouvant" sur ce segment.

**Mitigation** : Maintenir une liste d'attente Fiducial des le lancement d'AO. Communiquer regulierement sur la roadmap Fiducial. Offrir un acces beta prioritaire aux experts-comptables qui s'inscrivent pendant la phase AO. Ne pas laisser le segment "orphelin" — le marquer comme "prochainement" de maniere visible.

### Risque 4 — Concurrence Fiduciale qui progresse pendant la phase AO

Pendant les 6 a 12 mois consacres au vertical AO, des acteurs concurrents peuvent avancer sur le marche des outils IA pour experts-comptables. Des startups francaises beneficient d'un financement significatif sur ce segment. Chaque mois de retard est un mois ou la concurrence consolide sa position.

**Mitigation** : Le kernel TAKA OS est open source (MIT). Meme pendant la phase AO, la communaute peut commencer a experimenter des agents Fiducial sur le kernel. Publier une documentation claire sur l'extension du kernel a de nouveaux verticals. Le signal "extensible" est aussi important que le vertical lui-meme.

### Risque 5 — Complexite accrue de la gestion de deux types de tenants

Le fait d'avoir des tenants soumissionnaires et des tenants acheteurs publics dans la meme instance multiplie la complexite : deux flows d'onboarding differents, deux dashboards differents, deux jeux de permissions, deux modeles de donnees metiers partiellement distincts. Cette complexite "interne" au vertical AO est deja significative avant meme d'ajouter Fiducial.

**Mitigation** : L'architecture de segregation (Partie V) doit etre solide des le depart. Les feature flags par type de tenant doivent etre implementes des la v0.2. Les composants frontend doivent etre conditionnels (`if tenantType === 'soumissionnaire'`). La documentation technique doit maintenir une matrice de compatibilite claire.

### Risque 6 — Incertitude sur la reutilisation reelle du kernel

L'hypothese fondamentale de l'approche vertical separe est que le kernel sera reutilisable pour Fiducial. Cependant, les besoins metiers Fiducial pourraient reveler des lacunes architecturales du kernel qu'on n'aurait pas anticipees. Par exemple, le marche comptable necessite peut-etre une granularite de permissions differente (acces par dossier client, pas par tenant), ou un modele de memoire different (graphe de relations comptables plus complexe).

**Mitigation** : Conduire une etude de faisabilite Fiducial legere (2-3 jours) des le mois 3 de la phase AO, pendant que le kernel est suffisamment mature mais pas fige. Valider les hypotheses de reutilisation avec un prototype de 3 agents Fiducial sur le kernel existant.

---

## 1.4 Recommandation CTO

L'approche vertical separe est **VALIDEE** avec 5 points d'action pour mitiger les risques identifies :

### Action 1 — Abstraction kernel des la v0.1 (Mitigation risques 1 et 2)

Le champ `tenant_type` (soumissionnaire/acheteur) doit etre present dans le modele `Tenant` des le premier commit. L'EventBus doit utiliser une convention de nommage de topics extensible (`vertical.{domain}.{entity}.{action}` au lieu de `ao.new_detected`). La table `agents` doit etre un registre generique avec un champ `vertical` et non une enumeration codee en dur. Investir 2 jours de plus sur la v0.1 pour cette abstraction represente un ROI considerable sur le long terme.

### Action 2 — Roadmap publique Fiducial visible des le M2 (Mitigation risque 3)

Des le mois 2, publier sur le site web et le GitHub une roadmap claire indiquant : "Vertical Fiducial — Q4 2026". Ouvrir une liste d'attente avec un formulaire d'interet. Envoyer une newsletter mensuelle aux inscrits avec les avancees du kernel (qui les concernent indirectement). Cette communication coute quasi-zero en ressources de developpement mais retient l'attention du segment Fiducial.

### Action 3 — Etude de faisabilite Fiducial au M3 (Mitigation risque 6)

Au mois 3 (sortie de la v0.2 avec EventBus + connecteurs), consacrer 2-3 jours a un prototype Fiducial minimal sur le kernel existant. Objectif : valider que 3 agents Fiducial simples (Veilleur reglementaire, Generateur de liasse, Auditeur de conformite fiscale) peuvent s'executer sur le kernel AO sans modification structurelle. Documenter les frictions. Ajuster le kernel en consequence avant qu'il ne soit trop fige.

### Action 4 — Feature flags systematiques par type de tenant (Mitigation risque 5)

Implementer un systeme de feature flags des la v0.2, stocke en base (table `feature_flags`), avec trois niveaux : `global` (applique a tous les tenants), `by_tenant_type` (soumissionnaire vs acheteur), et `by_tenant` (override par tenant). Chaque feature du tableau de la Partie V doit etre representee par un flag. L'API doit filtrer les routes et les reponses en fonction des flags actifs pour le tenant courant. Le frontend doit conditionner l'affichage des composants.

### Action 5 — Documentation "Extension Guide" des le M4 (Mitigation risques 2 et 4)

Ecrire et maintenir un guide d'extension du kernel a de nouveaux verticals. Ce document explique : comment creer un nouveau registre d'agents, comment ajouter des tables metier, comment definir des events, comment implementer un nouvel onboarding, comment configurer les feature flags. Ce guide est a destination des contributeurs externes qui voudraient creer leur propre vertical (Juridique, RH, etc.) au-dela meme de Fiducial. Un kernel bien documente comme plateforme d'extension est un actif communautaire puissant.

---

# PARTIE II — MODELE ORGANISATIONNEL COMPLET

## 2.1 Architecture des 5 Roles

TAKA OS — Vertical AO definit 5 roles distincts, repartis en deux categories de tenants. Chaque role a un perimetre d'action precis, un ensemble de permissions exclusives, et une interface dediee.

### NIVEAU 1 — Editeur (Super Admin)

**Identite** : Le createur de TAKA OS (le CEO) et les equipes techniques de l'editeur (equipe core dev, support niveau 3, DevOps).

**Perimetre d'action** : L'ensemble du systeme, tous les tenants, toutes les donnees.

**Responsabilites detaillees** :
- Gerer les instances (tenants) clients : creer, modifier, suspendre, supprimer
- Acceder a tout le systeme en lecture/ecriture sans restriction
- Visualiser les metriques globales de la plateforme : MAU (Monthly Active Users), MRR (Monthly Recurring Revenue), churn rate, taux de qualification moyen, temps moyen de reponse des agents
- Gerer la configuration systeme : feature flags (activer/desactiver par tenant ou globalement), version du code deployee, variables d'environnement
- Gerer le billing et les factures : integrer avec Stripe/Pennylane, consulter les paiements, gerer les remboursements, resoudre les litiges
- Acceder au support et aux logs d'erreur : consulter Sentry, les logs applicatifs, les metriques de performance (Grafana/Prometheus)
- Impersonate n'importe quel utilisateur pour le support : se connecter temporairement en tant qu'un utilisateur client pour reproduire un bug ou guider l'utilisateur
- Gerer les mises a jour et les migrations de base de donnees
- Configurer les integrations globales (cles API Mistral, BOAMP, TED)
- Suspendre un tenant en cas de non-paiement ou de violation des conditions d'utilisation

**Interface** : `/editor` — Panel d'administration editeur, separe du frontend client.

**Exemples d'utilisation** :
- "Un client sur le plan Enterprise ne parvient pas a qualifier un AO. L'editeur impersonate l'admin du tenant pour constater le probleme en direct."
- "Le taux d'erreur 500 sur l'agent Scorer depasse 5%. L'editeur consulte les logs, identifie un timeout Mistral, et ajuste la configuration de retry."
- "Un client demande la suppression de son compte (RGPD). L'editeur lance la procedure de suppression complete des donnees du tenant."

---

### NIVEAU 2 — Client Soumissionnaire (Admin)

**Identite** : Le dirigeant, le responsable des Appels d'Offres, ou le business developer de l'entreprise soumissionnaire. C'est le "proprietaire" du tenant soumissionnaire.

**Perimetre d'action** : Son tenant uniquement. Tous les AO et tous les utilisateurs de son tenant.

**Responsabilites detaillees** :
- Gerer les collaborateurs de son tenant : inviter par email, desactiver, changer de role (promouvoir un collaborateur en manager, retrograder un manager), supprimer un compte
- Configurer les regles de qualification : definir la whitelist de codes CPV, les montants minimum et maximum des AO a considerer, les zones geographiques d'intervention, les seuils de scoring GO/MAYBE/NO-GO
- Choisir le profil de scoring parmi 3 options : Prudent (seuils eleves, focus coherence metier), Opportuniste (seuils bas, focus concurrence), ou Sppecialise (seuils moyens, focus expertise technique)
- Parametrer le pipeline Kanban : renommer les stages par defaut (Detecte > Qualifie > En preparation > Redaction > Relecture > Soumis > Gagne > Perdu), en ajouter, en supprimer, changer l'ordre
- Configurer les alertes : activer/desactiver les notifications email pour les deadlines (J-30, J-14, J-7, J-3, J-1), les nouveaux AO detectes, les changements de statut
- Acceder a tous les AO de son tenant : voir la liste complete, filtrer, trier, exporter
- Acceder au dashboard analytics : taux de gain global, CA total remporte, nombre de reponses par mois, taux de conversion par CPV, temps moyen de traitement
- Exporter les donnees : export CSV de la liste des AO, export PDF des fiches de qualification, export JSON complet du tenant (portabilite RGPD)
- Gerer l'abonnement et la facturation de son tenant : changer de formule (Free/Pro/Enterprise), mettre a jour les coordonnees de facturation, consulter l'historique des factures, resilier l'abonnement

**Interface** : `/dashboard` — Dashboard complet avec onglet "Parametres" et "Equipe".

**Exemples d'utilisation** :
- "Marie Dupont, responsable AO chez BuildCorp (BTP, 45 salaries), configure le profil Prudent avec un seuil GO a 0.80, limite aux CPV 45000000 (travaux de batiment), et une zone geographique limitee a l'Ile-de-France et les Hauts-de-France."
- "Elle invite son collaborateur Pierre Martin (charge d'affaires) avec le role Collaborateur, et sa directrice commerciale Sophie Legrand avec le role Manager."

---

### NIVEAU 3 — Client Soumissionnaire (Collaborateur)

**Identite** : Un employe de l'entreprise soumissionnaire qui travaille operationnellement sur les AO : charge d'affaires, assistant AO, redacteur technique, coordinateur de reponse.

**Perimetre d'action** : Son tenant uniquement. Les AO qui lui sont assignes ou visibles selon les regles de visibilite definies par l'admin.

**Responsabilites detaillees** :
- Voir les AO assignes ou visibles : consulter la liste filtree, acceder aux fiches detaillees
- Uploader des DCE PDF : deposer les documents de consultation sur la plateforme pour analyse
- Lancer la qualification : declencher l'agent Scorer sur un AO, consulter le resultat (GO/MAYBE/NO-GO) et l'explication detaillee
- Deplacer les cartes dans le Kanban : changer le statut d'un AO d'un stage a un autre (ex : "En preparation" → "Redaction")
- Rediger et soumettre des documents : utiliser l'agent Redacteur pour generer un memoire technique, editer le resultat, le marquer comme "pret"
- Ajouter des notes et commentaires sur les AO : laisser des remarques textuelles, mentionner un collegue (@pierre.martin), consulter l'historique des echanges
- Consulter la memoire episodique : voir les AO similaires passes, les lecons apprises, les references de projets gagnes

**Restrictions explicites** :
- Ne PEUT PAS changer les regles de qualification (CPV, montants, zones, profil de scoring)
- Ne PEUT PAS inviter des utilisateurs ou gerer les roles
- Ne PEUT PAS voir les analytics globaux du tenant (taux de gain, CA remporte)
- Ne PEUT PAS changer l'abonnement ou acceder a la facturation
- Ne PEUT PAS configurer le pipeline Kanban (renommer/ajouter/supprimer des stages)
- Ne PEUT PAS modifier les alertes

**Interface** : `/dashboard` — Dashboard simplifie, vue Kanban par defaut.

**Exemples d'utilisation** :
- "Pierre Martin upload le DCE d'un AO pour la construction d'un college a Amiens (CPV 45214200, 4.2 M EUR). Il lance la qualification, obtient un score MAYBE (0.67). Il ajoute un commentaire : 'Verifier disponibilite de notre chef de chantier M. Bernard pour ce creneau'."
- "Il deplace la carte dans le Kanban de 'Qualifie' a 'En preparation' apres validation orale de sa responsable."

---

### NIVEAU 4 — Client Acheteur Public (Admin)

**Identite** : Le responsable des marches, le directeur des achats, ou le secretaire general de la collectivite/organisme public. C'est le "proprietaire" du tenant acheteur.

**Perimetre d'action** : Son tenant uniquement. Tous les AO publies et toutes les candidatures de son tenant.

**Responsabilites detaillees** :
- Publier les AO sur la plateforme : creer un nouvel AO avec toutes les informations requises (titre, objet, CPV, montant, calendrier, documents)
- Gerer les collaborateurs de son tenant acheteur : inviter des agents, definir leurs roles, desactiver des comptes
- Configurer les criteres d'attribution et les ponderations : definir les criteres (prix, valeur technique, delai, environnement, innovation) et leurs coefficients (ex : prix 40%, technique 50%, delai 10%)
- Suivre les candidatures recues : consulter la liste des soumissionnaires, leur statut, leurs documents, noter chaque candidature
- Acceder au dashboard acheteur : nombre d'AO publies actifs, nombre de candidatures recues par AO, taux de reponse moyen, delai moyen entre publication et premiere candidature
- Gerer les documents de consultation : uploader le CCTP (Cahier des Clauses Techniques Particulieres), le RC (Reglement de Consultation), le DCE complet, la DPGF (Detail Prijs Global et Forfaitaire)
- Acceder aux rapports de conformite : consulter les audits automatises de conformite aux marches publics, telecharger les rapports pour le DGS
- Exporter les donnees : export CSV des candidatures, export PDF des rapports de conformite, export des statistiques d'appel d'offres
- Gerer l'abonnement et la facturation de son tenant

**Interface** : `/acheteur/dashboard` — Dashboard acheteur avec onglet "Publication" et "Candidatures".

**Exemples d'utilisation** :
- "Jeanne Moreau, responsable des marches de la Communaute d'Agglomeration d'Amiens, publie un AO pour la rehabilitation d'un gymnase (CPV 45212231, 1.8 M EUR). Elle configure les criteres : prix 45%, valeur technique 40%, delai 15%."
- "Elle consulte les 7 candidatures recues, consulte les memoires techniques, et note chaque dossier sur les 3 criteres pour preparer le rapport de la commission d'attribution."

---

### NIVEAU 5 — Client Acheteur Public (Collaborateur)

**Identite** : Un agent, un technicien, ou un employe de la collectivite qui aide a gerer les AO. Il peut etre charge de la redaction des CCTP, de la gestion des questions des soumissionnaires, ou du classement des candidatures.

**Perimetre d'action** : Son tenant uniquement. Les AO de son service ou departement, selon les regles de visibilite.

**Responsabilites detaillees** :
- Aider a rediger les CCTP, CCAG : utiliser les templates de documents, proposer des formulations, completer les sections techniques
- Publier des clarifications et reponses aux questions : repondre aux questions des soumissionnaires via l'interface dediee, publier des rectificatifs d'AO
- Classement des candidatures : consulter les dossiers des soumissionnaires, les noter selon les criteres definis par l'admin, ajouter des commentaires internes
- Ajouter des notes et commentaires : annoter les candidatures, signaler des anomalies, proposer des observations
- Creer des brouillons d'AO : preparer la redaction d'un nouvel AO, mais la publication necessite une validation de l'admin
- Consulter les questions en attente : voir la liste des questions soumises par les soumissionnaires et leur statut (repondu/en attente)

**Restrictions explicites** :
- Ne PEUT PAS publier un AO seul : la publication necessite la validation d'un admin acheteur (workflow de validation a 1 ou 2 signatures)
- Ne PEUT PAS modifier les criteres d'attribution ou les ponderations
- Ne PEUT PAS inviter des utilisateurs ou gerer les roles
- Ne PEUT PAS modifier l'abonnement ou acceder a la facturation
- Ne PEUT PAS voir les analytics globaux du tenant

**Interface** : `/acheteur/dashboard` — Meme structure que l'admin, avec les actions de publication restreintes.

**Exemples d'utilisation** :
- "Thomas Petit, technicien batiment de la Communaute d'Agglomeration d'Amiens, consulte les 3 questions en attente de reponse sur l'AO de rehabilitation du gymnase. Il redige les reponses techniques et les soumet a Jeanne Moreau (admin) pour validation avant publication."

---

## 2.2 Matrice de Permissions Detaillee

La matrice suivante definit, pour chaque role (lignes) et chaque permission (colonnes), le niveau d'acces accorde. Les niveaux sont definis comme suit :

- **CRUD** : Create, Read, Update, Delete — plein controle
- **Execute** : Peut declencher l'action mais pas la configurer
- **Read** : Lecture uniquement
- **Admin** : Acces aux fonctions d'administration (configuration, gestion des acces)
- **None** : Aucun acces — la fonction est masquee ou refusee

### Matrice complete

| Permission | Editeur (Super Admin) | Admin Soumissionnaire | Collaborateur Soum. | Admin Acheteur | Collaborateur Achet. |
|---|---|---|---|---|---|
| **Tenants (creer/lire/modifier/supprimer)** | CRUD | None | None | None | None |
| **Utilisateurs (inviter/gerer roles/supprimer)** | CRUD | Admin (son tenant) | None | Admin (son tenant) | None |
| **Appels d'Offres (creer/lire/modifier/supprimer)** | CRUD (tous tenants) | CRUD (son tenant) | Read + Execute | CRUD (son tenant) | Read + Create (brouillon) |
| **Documents (upload/lire/supprimer)** | CRUD | CRUD | Upload + Read | CRUD | Upload + Read |
| **Regles de qualification (configurer/lire)** | Read | Admin | Read | None | None |
| **Pipeline Kanban (configurer/deplacer cartes)** | Read | Admin | Execute (deplacer) | Admin | Execute (deplacer) |
| **Memoire (lire/ecrire)** | Read (tous tenants) | Read + Write | Read | None | None |
| **Analytics (lire/exporter)** | Read + Export (global) | Read + Export (tenant) | None | Read + Export (tenant) | None |
| **Parametres tenant (modifier/lire)** | CRUD | Admin | None | Admin | None |
| **Abonnement/facturation (gerer/lire)** | CRUD (global) | Admin (son tenant) | None | Admin (son tenant) | None |
| **Configuration systeme (modifier/lire)** | Admin | None | None | None | None |
| **Audit logs (lire)** | Read (global) | Read (son tenant) | None | Read (son tenant) | None |

### Detail des permissions par ressource

#### Tenants

| Role | Creer | Lire | Modifier | Supprimer | Notes |
|---|---|---|---|---|---|
| Editeur | Oui (panel /editor) | Oui (tous) | Oui (suspension, formule) | Oui (procedure RGPD) | Peut impersonate n'importe quel tenant |
| Admin Soum. | Non | Non | Non | Non | Ne voit pas d'autres tenants |
| Collaborateur Soum. | Non | Non | Non | Non | Ne voit pas d'autres tenants |
| Admin Acheteur | Non | Non | Non | Non | Ne voit pas d'autres tenants |
| Collaborateur Achet. | Non | Non | Non | Non | Ne voit pas d'autres tenants |

#### Utilisateurs

| Role | Inviter | Gerer roles | Desactiver | Supprimer | Notes |
|---|---|---|---|---|---|
| Editeur | Oui | Oui | Oui | Oui | Gestion globale des comptes |
| Admin Soum. | Oui (email + role) | Oui (Manager/Collab.) | Oui | Non (anonymisation) | Limite a son tenant |
| Collaborateur Soum. | Non | Non | Non | Non | Ne peut pas gerer l'equipe |
| Admin Acheteur | Oui (email + role) | Oui (Manager/Collab.) | Oui | Non (anonymisation) | Limite a son tenant |
| Collaborateur Achet. | Non | Non | Non | Non | Ne peut pas gerer l'equipe |

#### Appels d'Offres

| Role | Creer | Lire | Modifier | Supprimer | Qualifier | Changer stage | Notes |
|---|---|---|---|---|---|---|---|
| Editeur | Oui | Tous tenants | Oui | Oui | Oui | Oui | Support et debug |
| Admin Soum. | Upload DCE | Tous (tenant) | Oui | Oui (soft delete) | Oui | Oui | Controle total sur ses AO |
| Collaborateur Soum. | Upload DCE | Assignes/visibles | Notes uniquement | Non | Oui | Oui (deplacer cartes) | Ne voit que ses AO |
| Admin Acheteur | Publier AO | Tous (tenant) | Oui (brouillon) | Oui (retracter) | Non | Oui | Gestion complete des AO publies |
| Collaborateur Achet. | Brouillon uniquement | Service/dept. | Son brouillon | Non | Non | Oui (deplacer cartes) | Publication necessite validation |

#### Documents

| Role | Upload | Lire | Supprimer | Notes |
|---|---|---|---|---|
| Editeur | Oui | Tous | Oui | Acces complet |
| Admin Soum. | Oui (DCE, memoires) | Tous (tenant) | Oui | Gestion des documents de son tenant |
| Collaborateur Soum. | Oui (DCE) | Assignes | Non (soft delete) | Upload pour qualification |
| Admin Acheteur | Oui (CCTP, RC, DCE) | Tous (tenant) | Oui | Documents de consultation |
| Collaborateur Achet. | Oui (CCTP, pieces) | Service/dept. | Non | Preparation des documents |

#### Regles de qualification

| Role | Configurer | Lire | Tester | Notes |
|---|---|---|---|---|
| Editeur | Non (metier) | Oui (support) | Oui | Lecture pour support uniquement |
| Admin Soum. | Oui (5 dimensions) | Oui | Oui (AO exemple) | Configuration complete |
| Collaborateur Soum. | Non | Oui (appliquees) | Non | Voit les regles actives |
| Admin Acheteur | Non | Non | Non | Non applicable aux acheteurs |
| Collaborateur Achet. | Non | Non | Non | Non applicable aux acheteurs |

#### Pipeline Kanban

| Role | Configurer stages | Deplacer cartes | Voir | Notes |
|---|---|---|---|---|
| Editeur | Read | Oui | Oui | Observation |
| Admin Soum. | Oui (CRUD stages) | Oui | Oui | Personnalisation complete |
| Collaborateur Soum. | Non | Oui | Oui | Operationnel |
| Admin Acheteur | Oui (CRUD stages) | Oui | Oui | Stages specifiques acheteur |
| Collaborateur Achet. | Non | Oui | Oui | Operationnel |

#### Memoire episodique

| Role | Lire | Ecrire | Rechercher | Notes |
|---|---|---|---|---|
| Editeur | Tous tenants | Non | Oui | Support et debug |
| Admin Soum. | Son tenant | Oui (feedback) | Oui | Capitalisation echecs/succes |
| Collaborateur Soum. | Son tenant (limite) | Non | Oui | Reference operationnelle |
| Admin Acheteur | Non | Non | Non | Non applicable |
| Collaborateur Achet. | Non | Non | Non | Non applicable |

#### Analytics

| Role | Lire | Exporter | Portee | Notes |
|---|---|---|---|---|
| Editeur | Oui (global) | Oui (CSV/PDF) | Tous tenants | MAU, MRR, churn, taux moyens |
| Admin Soum. | Oui (tenant) | Oui (CSV/PDF) | Son tenant | Taux gain, CA, delais, CPV |
| Collaborateur Soum. | Non | Non | N/A | Pas d'acces analytics |
| Admin Acheteur | Oui (tenant) | Oui (CSV/PDF) | Son tenant | Candidatures, taux reponse |
| Collaborateur Achet. | Non | Non | N/A | Pas d'acces analytics |

#### Parametres tenant

| Role | Modifier | Lire | Notes |
|---|---|---|---|
| Editeur | Oui (tous) | Oui | Configuration systeme |
| Admin Soum. | Oui (son tenant) | Oui | Profil scoring, alertes, pipeline |
| Collaborateur Soum. | Non | Partiel | Voir regles actives uniquement |
| Admin Acheteur | Oui (son tenant) | Oui | Criteres attribution, workflow validation |
| Collaborateur Achet. | Non | Partiel | Voir parametres actifs |

#### Abonnement et facturation

| Role | Gerer | Lire | Exporter | Notes |
|---|---|---|---|---|
| Editeur | Oui (Stripe/Pennylane) | Oui (tous) | Oui | Gestion financiere globale |
| Admin Soum. | Oui (son tenant) | Oui | Oui (PDF) | Changer de formule, CB, factures |
| Collaborateur Soum. | Non | Non | Non | Pas d'acces |
| Admin Acheteur | Oui (son tenant) | Oui | Oui (PDF) | Changer de formule, CB, factures |
| Collaborateur Achet. | Non | Non | Non | Pas d'acces |

#### Configuration systeme

| Role | Modifier | Lire | Notes |
|---|---|---|---|
| Editeur | Oui (feature flags, versions) | Oui | Controle total |
| Admin Soum. | Non | Non | Masque |
| Collaborateur Soum. | Non | Non | Masque |
| Admin Acheteur | Non | Non | Masque |
| Collaborateur Achet. | Non | Non | Masque |

#### Audit logs

| Role | Lire | Portee | Notes |
|---|---|---|---|
| Editeur | Oui | Global | Tous les tenants, toutes les actions |
| Admin Soum. | Oui | Son tenant | Actions des utilisateurs de son tenant |
| Collaborateur Soum. | Non | N/A | Pas d'acces |
| Admin Acheteur | Oui | Son tenant | Actions des utilisateurs de son tenant |
| Collaborateur Achet. | Non | N/A | Pas d'acces |

---

## 2.3 Modele de Donnees — Extension

L'extension du modele de donnees existant s'articule autour de trois modifications principales : l'enrichissement de l'enumeration des roles utilisateur, l'ajout du type de tenant, et la creation d'une table de gestion des invitations.

### Extension de l'enumeration UserRole

```python
from enum import Enum

class UserRole(str, Enum):
    """Enumeration des 5 roles utilisateur de TAKA OS — Vertical AO.
    
    Le role determine les permissions via la matrice RBAC.
    Un utilisateur a un seul role par tenant (pas de roles multiples).
    """
    SUPER_ADMIN = "super_admin"           # Niveau 1 — Editeur (acces global)
    TENANT_ADMIN = "tenant_admin"         # Niveau 2 et 4 — Admin client
    TENANT_MANAGER = "tenant_manager"     # Niveau 3 et 5 — Manager client
    TENANT_COLLABORATOR = "tenant_collaborator"  # Niveau 3 et 5 — Collaborateur
    VIEWER = "viewer"                     # Lecture seule (extension future)
```

### Extension de l'enumeration TenantType

```python
class TenantType(str, Enum):
    """Type de tenant — determine les features disponibles,
    le flow d'onboarding, et les interfaces affichees.
    """
    SOUMISSIONNAIRE = "soumissionnaire"   # Entreprise qui repond aux AO
    ACHETEUR = "acheteur"                 # Collectivite qui publie des AO
    FIDUCIAL = "fiducial"                 # Reserve — vertical futur
```

### Extension du modele Tenant

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, Text, Numeric
from datetime import datetime
import uuid

class Tenant(Base):
    """Modele Tenant etendu avec le type de tenant et les parametres metier.
    
    Chaque tenant est isole des autres par le champ tenant_id
    present sur toutes les tables metier. Le tenant_type determine
    quelles features sont accessibles via le systeme de feature flags.
    """
    __tablename__ = "tenants"
    
    # Champs existants
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    siret: Mapped[str | None] = mapped_column(String(14), unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    
    # Nouveau champ — type de tenant
    tenant_type: Mapped[TenantType] = mapped_column(
        SQLEnum(TenantType), 
        nullable=False, 
        default=TenantType.SOUMISSIONNAIRE
    )
    
    # Champs d'abonnement
    plan: Mapped[str] = mapped_column(String(50), default="free")  # free/pro/enterprise
    plan_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    plan_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100))
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100))
    
    # Parametres soumissionnaire (applicables si tenant_type = soumissionnaire)
    scoring_profile: Mapped[str | None] = mapped_column(
        String(20), 
        default="prudent"  # prudent/opportuniste/specialise
    )
    cpv_whitelist: Mapped[list[str] | None] = mapped_column(
        default=list  # Liste des codes CPV acceptes
    )
    min_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    max_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    regions: Mapped[list[str] | None] = mapped_column(
        default=list  # Codes INSEE des regions
    )
    departments: Mapped[list[str] | None] = mapped_column(
        default=list  # Codes INSEE des departements
    )
    
    # Parametres acheteur (applicables si tenant_type = acheteur)
    collectivity_type: Mapped[str | None] = mapped_column(
        String(50)
        # mairie, departement, region, epci, hopital, etablissement_scolaire, etc.
    )
    service_name: Mapped[str | None] = mapped_column(String(255))
    ao_per_year_estimate: Mapped[int | None] = mapped_column(default=0)
    
    # Statut et dates
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    suspension_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relations
    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    invitations: Mapped[list["UserInvitation"]] = relationship(back_populates="tenant")
```

### Nouvelle table UserInvitation

```python
class UserInvitation(Base):
    """Gestion des invitations par email avec token securise.
    
    Quand un admin invite un collaborateur, un token JWT est genere
    avec une duree de validite de 7 jours. L'email contient un lien
    securise permettant au destinataire de creer son compte.
    """
    __tablename__ = "user_invitations"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id"), 
        nullable=False
    )
    
    # Informations de l'invite
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    
    # Role attribue
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), 
        nullable=False,
        default=UserRole.TENANT_COLLABORATOR
    )
    
    # Token securise
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    token_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False
    )
    
    # Statut
    status: Mapped[str] = mapped_column(
        String(20), 
        default="pending"  # pending/accepted/expired/cancelled
    )
    
    # Qui a envoye l'invitation
    invited_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), 
        nullable=False
    )
    
    # Dates
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    
    # Relations
    tenant: Mapped["Tenant"] = relationship(back_populates="invitations")
```

### Extension du modele User

```python
class User(Base):
    """Modele User etendu avec le role precis et les preferences."""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id"), 
        nullable=False
    )
    
    # Identite
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    
    # Authentification
    hashed_password: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Role — etendu avec les 5 niveaux
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), 
        nullable=False,
        default=UserRole.TENANT_COLLABORATOR
    )
    
    # Preferences
    preferences: Mapped[dict | None] = mapped_column(
        default=dict  # JSON : langue, theme, notifications, dashboard_default_view
    )
    
    # Onboarding
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarding_step: Mapped[int | None] = mapped_column(default=0)
    
    # Dates
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relations
    tenant: Mapped["Tenant"] = relationship(back_populates="users")
```

### Table FeatureFlag (nouvelle)

```python
class FeatureFlag(Base):
    """Systeme de feature flags pour activer/desactiver les fonctionnalites
    par tenant ou globalement. Essentiel pour la gestion des 2 types de tenants
    et la preparation aux futurs verticals.
    """
    __tablename__ = "feature_flags"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    
    # Niveau d'application
    scope: Mapped[str] = mapped_column(
        String(20), 
        nullable=False  # global, by_tenant_type, by_tenant
    )
    
    # Valeur par defaut
    default_value: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Overrides (stocke en JSON)
    overrides: Mapped[dict | None] = mapped_column(
        default=dict
        # Ex: {"soumissionnaire": true, "acheteur": false}
        # Ex: {"tenant_uuid_1": true, "tenant_uuid_2": false}
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
```

### Table AuditLog (existante — conservee)

```python
class AuditLog(Base):
    """Journal d'audit append-only avec hash chain SHA-256.
    Chaque action significative est enregistree de maniere immuable.
    """
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tenants.id"), 
        nullable=True  # Null pour les actions globales (editeur)
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    user_role: Mapped[str | None] = mapped_column(String(50))
    
    # Action
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(100))
    
    # Details
    details: Mapped[dict | None] = mapped_column(default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    
    # Hash chain (integrite)
    previous_hash: Mapped[str | None] = mapped_column(String(64))
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
```


---

# PARTIE III — FLOWS D'ONBOARDING ET PARAMETRAGE

## 3.1 Flow Creation d'Instance par l'Editeur (Super Admin)

Ce flow decrit la creation d'un nouveau tenant client par l'equipe editeur. C'est la premiere etape de la relation avec tout nouveau client, qu'il soit soumissionnaire ou acheteur public.

### Etape 1 — Connexion au panel editeur

L'editeur (super admin) se connecte a l'URL `/editor` avec ses identifiants. L'authentification passe par le meme systeme JWT que les clients, mais avec un claim supplementaire `scope: "global"` qui lui permet d'acceder a toutes les ressources sans restriction de `tenant_id`. Le panel editeur est une interface distincte du frontend client, avec son propre design system (mais base sur les memes composants shadcn/ui pour la coherence).

### Etape 2 — Acces a la section "Tenants"

L'editeur clique sur "Tenants" dans la sidebar de navigation. Le tableau de bord affiche la liste de tous les tenants actifs avec leurs informations cles : nom, type (soumissionnaire/acheteur), formule (Free/Pro/Enterprise), nombre d'utilisateurs, date de creation, statut (actif/suspendu/en periode d'essai). Un bouton "Nouveau Client" est visible en haut a droite de l'ecran.

### Etape 3 — Clic sur "Nouveau Client"

Un modal s'ouvre avec un formulaire en plusieurs champs. L'editeur commence par selectionner le type de tenant via deux cartes visuelles mutuellement exclusives :
- Carte "Soumissionnaire" — avec une icone entreprise et le texte "Entreprise qui repond aux Appels d'Offres"
- Carte "Acheteur Public" — avec une icone mairie et le texte "Collectivite ou organisme public qui publie des AO"

Le choix ici determine l'ensemble du flow : onboarding envoye, features activees, templates de documents, et pipelines proposes.

### Etape 4 — Remplissage des informations du tenant

L'editeur remplit les champs obligatoires et optionnels du formulaire :

**Champs obligatoires** :
- Nom de l'entreprise / collectivite (ex : "BuildCorp SAS", "Communaute d'Agglomeration d'Amiens")
- SIRET (14 chiffres, valide via l'API Sirene de l'INSEE en temps reel)
- Email du contact principal (ex : "m.dupont@buildcorp.fr", "marches@amiens-agglo.fr")
- Formule d'abonnement : Free (1 utilisateur, 5 AO/mois) / Pro (10 utilisateurs, AO illimites, veille automatique) / Enterprise (utilisateurs illimites, SLA support, API access)

**Champs optionnels** :
- Nom du contact principal (ex : "Marie Dupont")
- Telephone (ex : "03 22 33 44 55")
- Adresse postale (completee automatiquement via l'API Sirene si le SIRET est valide)
- Notes internes (visible uniquement par l'editeur, ex : "Client reference par la CCI Amiens, interesse par la veille BOAMP")
- Date de debut de periode d'essai (defaut : aujourd'hui, 14 jours de periode d'essai pour les plans Pro et Enterprise)

### Etape 5 — Validation et creation du tenant

L'editeur clique sur "Creer le tenant". Le backend effectue les operations suivantes de maniere atomique :

1. Verification d'unicite du SIRET (pas de doublon de tenant actif pour le meme SIRET)
2. Validation du format email et du telephone
3. Creation du tenant en base avec les valeurs par defaut correspondant au type :
   - Pour un soumissionnaire : `scoring_profile = "prudent"`, `pipeline_stages` = les 8 stages par defaut, `cpv_whitelist = []` (tous les CPV acceptes par defaut)
   - Pour un acheteur : `collectivity_type = null` (a definir lors de l'onboarding), `workflow_validation = "single"` (1 signature par defaut)
4. Creation automatique du premier utilisateur (admin) avec le role `tenant_admin`, statut `pending` (mot de passe a definir via le lien d'invitation)
5. Generation d'un token d'invitation JWT (duree de validite : 7 jours)
6. Enregistrement dans les audit logs avec hash chain

### Etape 6 — Envoi de l'email d'invitation

Le systeme envoie automatiquement un email au contact principal avec :
- Objet : "Votre acces TAKA OS est pret — Configurez votre compte"
- Corps : Message de bienvenue personnalise avec le nom de l'entreprise, un lien securise contenant le token (`https://takaos.io/onboarding?token=xyz`), et une date d'expiration (7 jours)
- Le lien redirige vers le wizard d'onboarding adapte au type de tenant (soumissionnaire ou acheteur)

### Etape 7 — Mise a jour du dashboard editeur

Le nouveau tenant apparait immediatement dans le tableau de la liste des tenants. Le compteur "Tenants actifs" s'incremente. Une notification toast confirme : "Tenant 'BuildCorp SAS' cree avec succes. Email d'invitation envoye a m.dupont@buildcorp.fr." Si l'email echoue (bounce), une alerte rouge apparait avec un bouton "Renvoyer l'email".

---

## 3.2 Flow Onboarding Soumissionnaire (Premiere Connexion)

Ce wizard d'onboarding s'affiche lors de la premiere connexion d'un admin soumissionnaire apres clic sur le lien d'invitation. Il se deroule en 5 etapes, avec une barre de progression en haut de l'ecran. L'utilisateur peut revenir en arriere a tout moment. Les donnees sont sauvegardees a chaque etape (pas de perte si fermeture du navigateur).

### Etape 1 — Profil Entreprise

L'ecran affiche le titre "Parlons de votre entreprise" avec un sous-titre "Ces informations nous permettent de personnaliser votre experience TAKA OS."

**Formulaire** :
- Nom de l'entreprise (pre-rempli depuis la creation du tenant, modifiable)
- SIRET (pre-rempli, modifiable avec validation API Sirene)
- Forme juridique (select : SAS, SARL, SA, EURL, SASU, SCI, Auto-entrepreneur, Autre)
- Effectif (select : 1-10, 11-50, 51-250, 251-1000, 1000+)
- CA annuel dernier exercice (input numerique en EUR, optionnel)

**Multi-select secteurs d'activite** (avec autocomplete) :
- Batiment et travaux publics (BTP)
- Electricite, plomberie, chauffage, climatisation
- Informatique et telecom
- securite et surete
- Restauration collective et traiteur
- Nettoyage et facility management
- Transports et logistique
- Conseil et ingenierie
- Equipement medical et pharmaceutique
- Fournitures de bureau et mobilier
- Services financiers et assurances
- Autre (champ texte libre)

**Multi-select certifications** :
- ISO 9001 (Qualite)
- ISO 14001 (Environnement)
- ISO 27001 (Securite de l'information)
- MASE (Manuel d'Assurance Securite Environnement)
- UIC (Union des Industriels de la Construction)
- Qualibat
- OPQIBI
- Agrement securite incendie
- Label RSE
- Autre (champ texte libre)

**Action** : Le bouton "Continuer" sauvegarde les donnees et passe a l'etape 2.

### Etape 2 — Zones d'Intervention

Titre : "Ou intervenez-vous ?" — Sous-titre : "Definissez vos zones geographiques pour ne recevoir que les AO pertinents."

**Carte interactive de France** :
- Une carte de France metropolitaine + DOM-TOM est affichee
- Les regions sont cliquables (survol = highlight, clic = selection avec couleur de remplissage)
- Les regions selectionnees s'ajoutent a une liste en dessous de la carte avec une croix pour deselectionner
- Compteur : "3 regions selectionnees"

**Regions predefinies** (codes INSEE) :
- Auvergne-Rhone-Alpes (84), Bourgogne-Franche-Comte (27), Bretagne (53), Centre-Val de Loire (24), Corse (94), Grand Est (44), Hauts-de-France (32), Ile-de-France (11), Normandie (28), Nouvelle-Aquitaine (75), Occitanie (76), Pays de la Loire (52), Provence-Alpes-Cote d'Azur (93), Guadeloupe (01), Martinique (02), Guyane (03), La Reunion (04), Mayotte (06)

**Multi-select departements** (optionnel, granularite plus fine) :
- Un champ autocomplete permet de chercher et selectionner des departements specifiques
- Exemple : selectionner uniquement le Somme (80) et l'Oise (60) au lieu de toute la region Hauts-de-France

**Distance maximale acceptable** :
- Slider de 0 a 1000 km, avec des marqueurs predefinis : 50 km, 100 km, 200 km, 500 km
- Label : "Ne pas m'alerter pour les AO situes au-dela de : [200] km de mon siege social"
- Cette distance est utilisee comme critere de filtrage geographique par l'agent Veilleur

**Action** : Bouton "Retour" (etape 1), Bouton "Continuer" (etape 3).

### Etape 3 — CPV et Competences

Titre : "Vos codes CPV et competences" — Sous-titre : "Le systeme europeen des CPV (Common Procurement Vocabulary) classe tous les marches publics. Selectionnez ceux qui correspondent a votre activite."

**Recherche de codes CPV avec autocomplete** :
- Champ de recherche avec autocomplete base sur la base CPV europeenne complete (9000+ codes)
- A chaque frappe (debounce 300ms), une recherche floue est effectuee sur les libelles et les codes
- Exemple de recherche : "travaux batiment" propose : 45000000 (Travaux de construction), 45210000 (Travaux de construction de batiments), 45212200 (Ouvrages de construction d'habitations), etc.
- Chaque CPV selectionne apparait sous forme de tag avec le code + libelle court, et une croix de suppression
- Section "CPV frequents" affichee en dessous avec les 20 codes CPV les plus courants en France (clic rapide)

**Mots-cles metiers (tags input)** :
- Champ de saisie libre ou l'utilisateur tape des mots-cles separes par des virgules ou des touches Entree
- Chaque mot-cle devient un tag colore
- Exemples suggerees : "genie civil", "menuiserie", "peinture industrielle", "reseaux informatiques", "surveillance", "restauration scolaire"
- Ces mots-cles enrichissent la recherche semantique de l'agent Veilleur

**Experiences passes (types d'AO deja gagnes)** :
- Champ texte structure (repetable) : Titre du projet / Client / Montant / Date
- Exemple : "Construction d'un groupe scolaire / Ville de Lille / 2.4 M EUR / Mars 2025"
- Ces references alimentent la memoire episodique et ameliorent la qualite des memaires techniques generes

**Action** : Bouton "Retour", Bouton "Continuer".

### Etape 4 — Profil de Scoring

Titre : "Comment qualifier vos opportunites ?" — Sous-titre : "Choisissez le profil de scoring qui correspond a votre strategie commerciale. Vous pourrez le modifier a tout moment."

**Selection du profil (3 cartes cliquables)** :

| Profil | Seuil GO | Seuil MAYBE | Description |
|---|---|---|---|
| **Prudent** | >= 0.80 | 0.60 - 0.79 | Privelegie la coherence metier (30%) et la viabilite financiere (25%). Moins de faux positifs, mais risque de manquer des opportunites. |
| **Specialise** | >= 0.75 | 0.45 - 0.74 | Privelegie la coherence metier (40%) et l'intelligence concurrentielle (15%). Pour les entreprises avec une expertise technique reconnue. |
| **Opportuniste** | >= 0.55 | 0.35 - 0.54 | Privelegie l'intelligence concurrentielle (30%) et accepte plus de risques. Pour les entreprises en phase de croissance cherchant a elargir leur portefeuille. |

Chaque carte affiche un graphique en radar simplifie des 5 dimensions ponderees. Le profil "Prudent" est selectionne par defaut.

**Ajustement personnalise (optionnel)** :
- Un toggle "Personnaliser les seuils" revele des sliders pour ajuster les seuils GO et MAYBE
- Slider GO : de 0.50 a 0.95 (pas par 0.05)
- Slider MAYBE minimum : de 0.30 a 0.70
- Un message de validation s'affiche en rouge si MAYBE >= GO

**Visualisation en temps reel** :
- Un AO exemple est presente (extrait reel anonymise) avec son score calcule selon les seuils actuels
- Exemple : "Rehabilitation d'une ecole primaire — 1.2 M EUR — Travaux de maconnerie"
- Le score simule change dynamiquement quand l'utilisateur modifie les sliders
- Un badge colore indique le verdict : "GO" (vert), "MAYBE" (orange), ou "NO-GO" (rouge)

**Action** : Bouton "Retour", Bouton "Continuer".

### Etape 5 — Pipeline et Alertes

Titre : "Votre workflow de suivi" — Sous-titre : "Configurez votre pipeline Kanban et vos alertes pour ne rien manquer."

**Pipeline Kanban par defaut (8 stages)** :

Le tableau affiche les 8 stages par defaut dans l'ordre, chacun avec un nom, une couleur, et des actions :

| Ordre | Nom | Couleur | Description |
|---|---|---|---|
| 1 | Detecte | Gris (#6B7280) | AO detecte par la veille, non encore qualifie |
| 2 | Qualifie | Bleu (#3B82F6) | AO qualifie (GO ou MAYBE), en attente de decision |
| 3 | En preparation | Violet (#8B5CF6) | Equipe mobilisee, strategie de reponse definie |
| 4 | Redaction | Rose (#EC4899) | Memoire technique et documents en cours de redaction |
| 5 | Relecture | Jaune (#F59E0B) | Documents finalises, phase de relecture interne |
| 6 | Pret a soumettre | Orange (#F97316) | Dossier complet, attente validation finale |
| 7 | Soumis | Vert (#10B981) | Candidature deposee sur le portail acheteur |
| 8 | Gagne / Perdu | Noir / Rouge | AO attribue (archive automatique) |

L'utilisateur peut :
- Renommer chaque stage (clic sur le nom)
- Changer la couleur (picker de couleur)
- Ajouter un nouveau stage (bouton "+ Ajouter un stage", max 12)
- Supprimer un stage (icone corbeille, avec confirmation)
- Reordonner par drag-and-drop

**Configuration des alertes email** :

Alertes sur les deadlines (checkboxes) :
- [x] J-30 (1 mois avant la deadline)
- [x] J-14 (2 semaines)
- [x] J-7 (1 semaine)
- [x] J-3 (3 jours)
- [x] J-1 (1 jour — derniere chance)

Alertes sur les nouveaux AO (checkboxes) :
- [x] Nouveaux AO correspondant a mes criteres (email quotidien)
- [ ] Nouveaux AO en urgence (deadline < 15 jours) — email immediat
- [ ] Tous les nouveaux AO de ma zone geographique (email quotidien, non filtre)

**Frequence de veille** :
- Radio buttons : Toutes les 6 heures (4x/jour) / Toutes les 12 heures (2x/jour) / Une fois par jour (24h)
- La veille automatique declenche l'agent Veilleur qui interroge les portails BOAMP, TED et e-marchespublics

**Action finale** : Bouton "Retour", Bouton "Terminer".

### Completion de l'onboarding

Au clic sur "Terminer" :
1. Toutes les donnees des 5 etapes sont persiste en base
2. Le flag `onboarding_completed` passe a `True`
3. Un message de felicitations s'affiche : "Bienvenue sur TAKA OS, [Prenom] ! Votre espace est pret."
4. Un bouton "Acceder a mon dashboard" redirige vers `/dashboard`
5. Un product tour interactif (5 etapes) se lance automatiquement sur le dashboard pour guider l'utilisateur
6. L'editeur recoit une notification : "Le client BuildCorp SAS a complete son onboarding"

---

## 3.3 Flow Onboarding Acheteur Public (Premiere Connexion)

Ce wizard d'onboarding s'affiche lors de la premiere connexion d'un admin acheteur public. Il se deroule en 4 etapes, avec la meme barre de progression et la meme logique de sauvegarde progressive.

### Etape 1 — Profil Collectivite

Titre : "Parlons de votre collectivite" — Sous-titre : "Ces informations permettent de configurer votre espace acheteur public."

**Formulaire** :
- Nom de la collectivite (pre-rempli depuis la creation du tenant, modifiable)
- SIRET (pre-rempli, modifiable)
- Type de collectivite (select obligatoire) :
  - Commune / Mairie
  - Departement
  - Region
  - EPCI (Metropole, Communaute d'Agglomeration, Communaute de Communes)
  - Etablissement public de sante (Hopital, CHU, CHS)
  - Etablissement public d'enseignement
  - Etablissement public administratif
  - Groupement d'interet public (GIP)
  - Organisme de securite sociale
  - Entreprise publique nationale
  - Autre (champ texte)
- Service responsable des marches (input texte, ex : "Direction des Achats et des Marches", "Service des Moyens Generaux")
- Nom du responsable des marches (input, ex : "Jeanne Moreau")
- Fonction du responsable (input, ex : "Directrice des Achats")
- Nombre d'AO publies par an (estimation, select : 1-10, 11-50, 51-100, 101-500, 500+)

**Action** : Bouton "Continuer".

### Etape 2 — Types de Marches

Titre : "Vos types de marches" — Sous-titre : "Quelles procedures et quels secteurs couvrez-vous ?"

**Types de procedure utilises (checkboxes)** :
- [x] Appel d'offres ouvert (publication au BOAMP, candidature libre)
- [ ] Appel d'offres restreint (pre-selection des candidats)
- [ ] Dialogue competitif (pour des projets complexes)
- [ ] Procedure avec negociation
- [ ] Procedure adaptee (pour les marches < 40K EUR)
- [ ] Procedure concurrentielle avec negociation
- [ ] Accord-cadre
- [ ] Marche subsquent

**Seuils de publicite applicables** :
- Seuils EU (affichage obligatoire au Tenders Electronic Daily) :
  - Travaux : > 5.382 M EUR (2024)
  - Fournitures et services : > 143K EUR (2024)
- Seuils nationaux (affichage obligatoire au BOAMP) :
  - Travaux : > 215K EUR HT
  - Fournitures et services : > 90K EUR HT / 40K EUR pour les collectivites < 3500 habitants

Un petit texte informatif rappelle ces seuils, avec une note : "TAKA OS vous aidera a determiner automatiquement la procedure applicable en fonction du montant estime."

**Secteurs d'achat (checkboxes)** :
- [x] Travaux (construction, rehabilitation, entretien)
- [x] Fournitures (materiel, equipement, mobilier)
- [x] Services (prestations intellectuelles, maintenance, restauration)
- [ ] Alimentation
- [ ] Informatique et telecom
- [ ] Transports
- [ ] Energie et eaux
- [ ] Sante et hygiene
- [ ] securite et surete
- [ ] Autre

**Action** : Bouton "Retour", Bouton "Continuer".

### Etape 3 — Criteres d'Attribution

Titre : "Vos criteres d'attribution" — Sous-titre : "Configurez les ponderations par defaut pour l'evaluation des candidatures. Vous pourrez les ajuster pour chaque AO."

**Ponderation par defaut** (sliders dont la somme doit faire 100%) :

| Critere | Slider (%) | Valeur par defaut |
|---|---|---|
| Prix | [==========] | 40% |
| Valeur technique | [========] | 35% |
| Delai d'execution | [==] | 15% |
| Environnement / RSE | [=] | 5% |
| Innovation | [=] | 5% |

Un indicateur en temps reel affiche la somme. Si elle n'est pas egale a 100%, un message d'erreur bloque le passage a l'etape suivante. Un bouton "Reinitialiser les valeurs par defaut" restaure les ponderations initiales.

**CCAG utilises habituellement** (checkboxes) :
- [x] CCAG-Travaux (Cahier des Clauses Administratives Generales applicables aux marches de travaux)
- [ ] CCAG-Fournitures (pour les marches de fournitures courantes)
- [x] CCAG-Services (pour les marches de services)
- [ ] CCAG-Techniques (pour les marches de maintenance technique)
- [ ] CCAG-PI (pour les prestations intellectuelles)
- [ ] CCAG-MIC (pour les marches d'informatique et de communication)

**Templates de CCTP disponibles** (selection multiple) :
- Le systeme propose des templates pre-rediges de CCTP (Cahiers des Clauses Techniques Particulieres) par secteur
- Exemples : "Travaux de construction d'un batiment scolaire", "Fourniture de mobilier de bureau", "Prestation de nettoyage", "Maintenance des installations de chauffage"
- L'utilisateur peut selectionner ceux qui l'interessent pour son catalogue personnel

**Action** : Bouton "Retour", Bouton "Continuer".

### Etape 4 — Workflow de Validation

Titre : "Votre workflow de validation" — Sous-titre : "Qui valide la publication d'un appel d'offres dans votre organisme ?"

**Mode de validation (radio buttons)** :
- Option 1 : "Validation par une seule personne" — l'admin acheteur peut publier directement
- Option 2 : "Validation a deux signatures" — le collaborateur prepare, l'admin valide et publie
- Option 3 : "Validation par un comite" — un comite d'attribution doit valider avant publication (pour les marches > seuil EU)

**Alertes a configurer (checkboxes)** :
- [x] Nouvelle candidature recue (email immediat)
- [x] Question d'un soumissionnaire (email immediat)
- [x] Deadline de remise des offres approche (J-7, J-3, J-1)
- [ ] Seuil minimum de candidatures non atteint (alerte si < 3 candidatures a J-7)
- [ ] Delai d'attribution depasse (alerte si la date d'attribution prevue est depassee)

**Action finale** : Bouton "Retour", Bouton "Terminer".

### Completion de l'onboarding acheteur

Au clic sur "Terminer" :
1. Toutes les donnees sont persiste en base
2. Le flag `onboarding_completed` passe a `True`
3. Message de felicitations : "Votre espace acheteur est configure. Vous pouvez maintenant publier votre premier appel d'offres."
4. Redirection vers `/acheteur/dashboard`
5. Product tour interactif (4 etapes) presentant l'interface acheteur
6. L'editeur recoit une notification de completion

---

## 3.4 Flow Invitation de Collaborateurs

Ce flow est commun aux deux types de tenants (soumissionnaire et acheteur). Seuls les admins (Niveau 2 et 4) peuvent inviter des collaborateurs.

### Etape 1 — Acces a la section "Equipe"

L'admin du tenant clique sur "Equipe" dans la sidebar de navigation. L'ecran affiche :
- Le nombre d'utilisateurs actifs / le nombre d'utilisateurs inclus dans le plan (ex : "3 / 10 utilisateurs")
- Un tableau des membres de l'equipe : nom, email, role, statut (actif/pending/desactive), date d'ajout
- Un bouton "Inviter un collaborateur" en haut a droite

### Etape 2 — Remplissage du formulaire d'invitation

Un modal s'ouvre avec le formulaire suivant :

**Champs obligatoires** :
- Adresse email (input avec validation email, ex : "pierre.martin@buildcorp.fr")
- Prenom (ex : "Pierre")
- Nom (ex : "Martin")
- Role (radio buttons) :
  - "Manager" — peut gerer les AO, les documents, deplacer les cartes, mais ne peut pas changer les regles de qualification ni inviter des utilisateurs
  - "Collaborateur" — peut voir les AO assignes, uploader des documents, deplacer les cartes, mais pas acceder aux parametres

**Champs optionnels** :
- Message personnalise (textarea, ex : "Bonjour Pierre, je t'invite a rejoindre notre espace TAKA OS pour travailler sur les AO de ce trimestre. — Marie")
- AO assignes par defaut (multi-select des AO actifs du tenant, pour pre-assigner le nouveau collaborateur)

### Etape 3 — Generation et envoi de l'invitation

L'admin clique sur "Envoyer l'invitation". Le backend execute :
1. Verification que le nombre d'utilisateurs actifs + pending n'excede pas la limite du plan
2. Verification que l'email n'est pas deja utilise dans ce tenant
3. Generation d'un token JWT securise contenant : `tenant_id`, `email`, `role`, `invited_by`, `exp` (7 jours)
4. Creation de l'entree `UserInvitation` en base avec le statut "pending"
5. Envoi de l'email d'invitation contenant :
   - Objet : "[Prenom admin] vous invite a rejoindre [Nom entreprise] sur TAKA OS"
   - Corps : Message personnalise + presentation de TAKA OS + lien securise (`https://takaos.io/invite?token=xyz`) + date d'expiration (7 jours)
   - Bouton d'action : "Rejoindre l'equipe"
6. Enregistrement dans l'audit log

### Etape 4 — Acceptation de l'invitation par le collaborateur

Le collaborateur recoit l'email et clique sur le lien securise. Plusieurs cas de figure :

**Cas 1 : Le collaborateur n'a pas encore de compte TAKA OS**
- Redirection vers une page de creation de compte
- Formulaire : prenom (pre-rempli), nom (pre-rempli), email (pre-rempli, non modifiable), mot de passe (8 caracteres minimum, 1 majuscule, 1 chiffre, 1 caractere special)
- Checkbox : "J'accepte les Conditions Generales d'Utilisation"
- Bouton "Creer mon compte et rejoindre l'equipe"
- Apres validation, le compte est cree avec le role defini dans l'invitation

**Cas 2 : Le collaborateur a deja un compte TAKA OS (autre tenant)**
- Redirection vers une page de connexion
- Apres authentification, un message s'affiche : "Vous etes invite a rejoindre [Nom entreprise] en tant que [Role]. Acceptez-vous ?"
- Boutons : "Accepter" / "Refuser"
- Si acceptation, le compte est associe au nouveau tenant (un utilisateur peut appartenir a plusieurs tenants avec des roles differents)

**Cas 3 : Le token a expire (plus de 7 jours)**
- Page d'erreur : "Cette invitation a expire. Contactez [Nom admin] pour recevoir une nouvelle invitation."
- Bouton : "Demander une nouvelle invitation" (envoie une notification a l'admin)

### Etape 5 — Premiere connexion et product tour

Apres acceptation de l'invitation et creation/connexion du compte :
1. Le collaborateur arrive sur son dashboard
2. Le statut de l'invitation passe a "accepted" et la date `accepted_at` est enregistree
3. Un product tour interactif se lance automatiquement (4-5 etapes selon le role) :
   - "Voici votre dashboard personnel"
   - "Cette carte montre vos AO assignes"
   - "Cliquez ici pour uploader un DCE"
   - "Le Kanban vous permet de suivre l'avancement"
   - "Vos notifications apparaissent ici"
4. Si le collaborateur a ete pre-assigne a des AO, ceux-ci sont visibles immediatement

### Etape 6 — Notification a l'admin

L'admin qui a envoye l'invitation recoit :
- Une notification dans l'interface (icone cloche, badge +1)
- Un email optionnel (selon ses preferences) : "Pierre Martin a accepte votre invitation et rejoint votre equipe."
- L'equipe est mise a jour en temps reel : le nouveau membre apparait dans le tableau avec le statut "actif"

---

## 3.5 Flow Parametrage des Regles de Qualification (Admin Soumissionnaire)

Ce flow permet a l'admin soumissionnaire de configurer finement le scoring des AO. C'est l'un des parametres les plus critiques du produit, car il determine la qualite des recommandations GO/NO-GO/MAYBE.

### Etape 1 — Acces a l'interface

L'admin soumissionnaire clique sur "Parametres" dans la sidebar, puis sur l'onglet "Regles de Qualification". L'ecran affiche un avertissement en haut : "Ces parametres affectent le scoring de tous les nouveaux AO. Modifiez-les avec discernement."

### Etape 2 — Interface a 5 onglets (les 5 dimensions de scoring)

L'interface est organisee en 5 onglets, correspondant aux 5 dimensions du scoring :

**Onglet 1 — Coherence Metier**
- Poids du critere (slider 0-100%, defaut selon le profil : Prudent 30%, Specialise 40%, Opportuniste 15%)
- CPV prioritaires (multi-select avec autocomplete, les CPV selectionnes ici recoivent un bonus de coherence)
- Mots-cles metiers (tags input, bonus de coherence si presents dans l'AO)
- Seuil minimum de correspondance (slider 0-100%, en-dessous = penalite de score)
- Experiences de reference requises (checkbox : "Penaliser les AO sans experience similaire dans la memoire")

**Onglet 2 — Viabilite Financiere**
- Poids du critere (slider, defaut : 25% / 20% / 20% selon profil)
- Ratio CA maximal acceptable (input : "Ne pas recommander les AO dont le montant est superieur a [X] fois notre CA annuel")
- Tresorerie minimum requise (input en EUR, optionnel, connecte a Chift si disponible)
- Capacite d'endettement (input en EUR, optionnel)
- Penalite pour les AO avec caution provisoire elevee (slider 0-50%)

**Onglet 3 — Accessibilite Geographique**
- Poids du critere (slider, defaut : 15% / 10% / 15% selon profil)
- Distance maximale (input en km, synchronise avec la configuration onboarding)
- Zones prioritaires (regions/departements sur carte interactive, bonus si l'AO est dans une zone prioritaire)
- Cout de deplacement estime (input en EUR/km, utilise pour estimer la rentabilite)
- Penalite pour les AO en zone difficile d'acces (checkbox + slider)

**Onglet 4 — Faisabilite Temporelle**
- Poids du critere (slider, defaut : 20% / 15% / 20% selon profil)
- Delai minimum de preparation souhaite (input en jours, ex : 21 jours entre detection et remise)
- Charge de travail actuelle (input : nombre d'AO en cours de preparation, utilise pour evaluer la disponibilite)
- Penalite pour les AO en urgence (deadline < 15 jours)
- Penalite pour les AO avec chevauchement de calendrier avec des AO deja gagnes

**Onglet 5 — Intelligence Concurrentielle**
- Poids du critere (slider, defaut : 10% / 15% / 30% selon profil)
- Nombre de concurrents historiques maximum tolerable (input, ex : "Ne pas recommander si > 8 candidats historiques")
- Taux de succes minimum historique par CPV (input en %, ex : "Ne pas recommander si notre taux de succes sur ce CPV est < 15%")
- Preference pour les AO techniques / specialises (checkbox : "Privilegier les AO avec barrieres a l'entree technique")
- Penalite pour les AO generiques / tres concurrentiels

### Etape 3 — Bouton "Tester"

En bas de chaque onglet, un bouton "Tester avec un AO exemple" permet de valider les regles en temps reel :
- Un modal s'ouvre avec un select d'AO reels anonymises (tires de la base publique BOAMP)
- L'utilisateur selectionne un AO (ex : "Construction d'un centre aquatique — 8.5 M EUR — Lille")
- Le systeme execute le scoring engine avec les regles actuellement configurees
- Le resultat s'affiche : score global, score par dimension, verdict GO/MAYBE/NO-GO, et explication detaillee
- L'utilisateur peut ajuster les sliders et re-tester immediatement

### Etape 4 — Sauvegarde

Le bouton "Sauvegarder les regles" en bas de la page persiste toutes les modifications en base :
1. Validation que la somme des poids des 5 dimensions = 100%
2. Validation des seuils (MAYBE minimum < GO minimum)
3. Sauvegarde dans la table `qualification_rules` avec un numero de version
4. Enregistrement dans l'audit log : qui a modifie quoi et quand
5. Message de confirmation : "Regles de qualification mises a jour. Elles s'appliqueront aux prochains AO detectes."

### Etape 5 — Historique des modifications

Un bouton "Voir l'historique" ouvre un drawer lateral affichant :
- La liste chronologique des modifications (date, auteur, description du changement)
- Possibilite de comparer deux versions (diff visuel)
- Possibilite de restaurer une version precedente (bouton "Restaurer cette version")
- Exemple d'entree : "2025-06-15 14:32 — Marie Dupont — Modifie 'Distance maximale' : 200 km → 300 km. Modifie 'Poids Coherence Metier' : 30% → 35%"

---

## 3.6 Flow Publication d'un AO (Admin Acheteur)

Ce flow permet a un admin acheteur de creer et publier un appel d'offres sur la plateforme. C'est le coeur metier du cote acheteur.

### Etape 1 — Creation d'un nouvel AO

L'admin acheteur clique sur "Nouvel AO" depuis le dashboard ou le menu "Mes AO publies". Un wizard multi-etapes s'ouvre. La progression est sauvegardee a chaque etape (possibilite de reprendre un brouillon).

### Etape 2 — Informations generales

Titre de l'etape : "Informations generales"

**Formulaire** :
- Titre de l'appel d'offres (input, ex : "Rehabilitation du gymnase municipal Marcel Cerdan")
- Objet detaille (textarea riche, ex : "Travaux de rehabilitation complete du gymnase comprenant : mise aux normes electriques, remplacement du parquet sportif, peinture interieure, mise en accessibilite PMR, et installation d'un nouveau chauffage. Duree des travaux estimee : 6 mois.")
- Code CPV principal (autocomplete sur la base CPV, ex : "45212231 — Travaux de construction d'installations sportives")
- Code CPV secondaire (optionnel, autocomplete)
- Montant estime HT (input numerique en EUR, ex : 1850000)
- Devise (select, defaut : EUR)
- Type de marche (radio, automatiquement determine par le montant) :
  - < 40K EUR : Procedure adaptee
  - 40K - 215K EUR : Procedure formalisee
  - > 215K EUR : Appel d'offres ouvert

Un bloc d'aide contextuelle s'affiche : "Selon le montant estime de 1 850 000 EUR HT, cet AO releve d'un appel d'offres ouvert avec publication obligatoire au BOAMP et au Tenders Electronic Daily (TED)."

### Etape 3 — Calendrier

Titre de l'etape : "Calendrier de la consultation"

**Dates obligatoires** :
- Date de publication (date picker, defaut : aujourd'hui)
- Date limite de reception des questions (date picker, ex : 10 jours avant la remise)
- Date limite de remise des offres (date picker, ex : "2025-08-15 12:00")
- Date d'ouverture des plis (date picker, heure, ex : "2025-08-15 14:00")
- Date prevue d'attribution (date picker, ex : "2025-09-30")

**Dates optionnelles** :
- Date de visite des lieux (si applicable)
- Date de reunion d'information (si applicable)
- Date de debut d'execution souhaitee
- Duree d'execution (input en mois, ex : 6)

Un calendrier visuel (timeline horizontale) affiche toutes les dates positionnees relativement. Des alertes automatiques verifient la coherence :
- Si la date de remise est < 30 jours apres la publication, un avertissement orange s'affiche
- Si la date d'attribution est > 4 mois apres la remise, un avertissement s'affiche

### Etape 4 — Criteres d'attribution et ponderation

Titre de l'etape : "Criteres d'attribution"

Les ponderations configurees lors de l'onboarding sont pre-remplies, mais modifiables pour cet AO specifique.

**Sliders de ponderation** (somme = 100%) :
- Prix (%) : defaut 40%, modifiable
- Valeur technique (%) : defaut 35%, modifiable
- Delai d'execution (%) : defaut 15%, modifiable
- Environnement / RSE (%) : defaut 5%, modifiable
- Innovation (%) : defaut 5%, modifiable

Un indicateur de somme en temps reel valide l'equilibre.

**Sous-criteres de la valeur technique** (optionnel) :
- Qualite technique de l'offre (poids dans la valeur technique)
- Experience et references du candidat
- Qualifications du personnel
- Methodologie d'execution
- Moyens materiels

Chaque sous-critere a un champ de description (textarea) pour guider la commission d'attribution.

### Etape 5 — Documents de consultation

Titre de l'etape : "Documents"

**Zone de upload multi-fichiers** (drag-and-drop ou clic) :
- CCTP (Cahier des Clauses Techniques Particulieres) — obligatoire
- RC (Reglement de Consultation) — obligatoire
- DCE (Dossier de Consultation des Entreprises) — recommande
- DPGF (Detail Prijs Global et Forfaitaire) — si applicable
- Plan d'execution — si applicable
- Formulaires DC1 et DC2 — generes automatiquement par TAKA OS

Chaque fichier upload affiche :
- Nom du fichier
- Taille
- Type (PDF, DOCX, XLSX)
- Icome de suppression
- Barre de progression pendant l'upload
- Verification antivirus (scan apres upload)

**Generation automatique de DC1/DC2** :
- Un bouton "Generer les DC1/DC2" cree automatiquement les formulaires de declaration de candidature standardises en format PDF pre-remplis avec les informations de l'AO
- Ces formulaires sont telechargeables par les soumissionnaires

### Etape 6 — Recapitulatif et publication

Titre de l'etape : "Recapitulatif"

Un ecran synthetique affiche toutes les informations de l'AO sous forme de sections repliables :
- Informations generales (titre, CPV, montant)
- Calendrier (timeline visuelle)
- Criteres d'attribution (graphique camembert des ponderations)
- Documents (liste des fichiers uploades)

**Workflow de validation** :
- Si le mode de validation est "1 signature" (admin seul) :
  - Bouton "Publier l'AO" (vert, prominent)
  - Bouton "Enregistrer comme brouillon" (secondaire)
- Si le mode de validation est "2 signatures" :
  - Bouton "Soumettre pour validation" (envoie une notification au second validateur)
  - Le second validateur recoit une notification et peut approuver ou rejeter
- Si le mode de validation est "Comite" :
  - Bouton "Soumettre au comite" (planifie une reunion de validation)

**Au clic sur "Publier"** :
1. L'AO est enregistre en base avec le statut "publie"
2. Un numero d'attribution interne est genere (format : TAKA-2025-XXXXX)
3. L'AO est indexe pour la recherche par les soumissionnaires
4. Les soumissionnaires abonnes aux alertes CPV correspondants recoivent une notification
5. L'AO est envoye automatiquement aux portaux BOAMP et TED (si les connecteurs sont actives)
6. L'audit log enregistre la publication
7. Un message de confirmation s'affiche : "Votre appel d'offres a ete publie avec succes. Reference : TAKA-2025-00427."
8. Redirection vers le detail de l'AO publie avec les statistiques en temps reel (nombre de vues, nombre de telechargements du DCE)


---

# PARTIE IV — INTERFACES PAR ROLE

## 4.1 Dashboard Editeur (`/editor/dashboard`)

Le panel editeur est une interface d'administration technique et commerciale, distincte du frontend client. Son objectif est de donner a l'equipe editrice une vision complete et en temps reel de la sante de la plateforme, de l'activite des clients, et des alertes techniques.

### Widget 1 — KPI Globaux (cartes en haut de page)

Une rangée de 5 cartes KPI affiche les metriques cles, avec mise a jour en temps reel (websocket) :

| KPI | Valeur exemple | Variation | Description |
|---|---|---|---|
| Tenants actifs | 47 | +5 ce mois | Nombre de tenants avec statut `is_active = true` et `is_suspended = false` |
| MAU (Monthly Active Users) | 312 | +12% vs N-1 | Nombre d'utilisateurs uniques ayant effectue au moins une action dans les 30 derniers jours |
| MRR (Monthly Recurring Revenue) | 8 450 EUR | +890 EUR | Recurrence mensuelle calculee sur les abonnements Pro et Enterprise actifs |
| Churn rate | 3.2% | -0.5% | Taux de resiliation sur les 30 derniers jours (tenants suspendus / tenants actifs au debut de periode) |
| NPS moyen | 42 | +3 | Score Net Promoter calcule sur les reponses au sondage post-qualification mensuel |

Chaque carte est cliquable et ouvre un graphique detaille en modal.

### Widget 2 — Graphique de croissance des tenants (courbe)

Un graphique en aires empilees (stacked area chart) affiche l'evolution du nombre de tenants sur les 12 derniers mois, avec deux series :
- Courbe bleue : Tenants soumissionnaires
- Courbe verte : Tenants acheteurs publics
- Ligne pointillee noire : Total cumule

L'axe X represente les mois (Mai 2025 - Mai 2026). L'axe Y represente le nombre de tenants. Un tooltip au survol affiche le detail par type pour chaque mois. Un bouton "Export CSV" telecharge les donnees brutes.

### Widget 3 — Tableau des derniers tenants inscrits

Un tableau pagine (10 lignes par page) affiche les derniers tenants crees, tries par date de creation decroissante :

| Colonne | Description |
|---|---|
| Nom | Nom de l'entreprise/collectivite |
| Type | Badge colore : bleu "Soumissionnaire" ou vert "Acheteur" |
| Date d'inscription | Format : "15 juin 2025, 14:32" |
| Statut | Badge : "Actif" (vert), "Periode d'essai" (orange), "Suspendu" (rouge), "En attente d'onboarding" (gris) |
| Formule | "Free", "Pro", "Enterprise" avec icone correspondante |
| Utilisateurs | "3 / 10" (actifs / limite du plan) |
| Actions | Bouton "Voir" (oeil), "Impersonate" (masque), "Suspendre" (pause) |

Chaque ligne est cliquable pour acceder au detail complet du tenant.

### Widget 4 — Tableau d'activite recente

Un tableau de 20 lignes max affiche les actions utilisateurs les plus recentes sur toute la plateforme, en temps reel :

| Colonne | Description |
|---|---|
| Heure | "14:32:15" (heure exacte) |
| Utilisateur | Prenom Nom + email tronque |
| Tenant | Nom du tenant (clicable) |
| Action | Description lisible : "A qualifie l'AO 'Construction college Amiens' — Verdict : GO (0.84)", "A publie l'AO 'Rehabilitation gymnase' (TAKA-2025-00427)", "A invite pierre.martin@buildcorp.fr" |
| IP | Adresse IP (anonymisee : dernier octet masque) |

Un filtre permet de chercher par tenant, par utilisateur, ou par type d'action.

### Widget 5 — Alertes systeme

Une section "Alertes" affiche les problemes requerant l'attention de l'equipe editeur :

| Niveau | Icone | Exemple | Action |
|---|---|---|---|
| Critique | Cercle rouge | "5 erreurs 500 sur l'agent Scorer dans les 10 dernieres minutes — Timeout Mistral AI" | Bouton "Voir les logs" |
| Haut | Triangle orange | "Tenant 'BuildCorp SAS' : facture impayee depuis 15 jours — Risque de suspension" | Bouton "Gerer" |
| Moyen | Info bleu | "3 tokens d'invitation expires ce jour — Considerer un renvoi" | Bouton "Voir" |
| Faible | Info gris | "Utilisateur actif en hausse de 25% ce mois — Prevoir scaling VPS" | Bouton "Details" |

Les alertes sont classees par criticite et par date. Chaque alerte peut etre "acquittee" (marquee comme traitee).

### Widget 6 — Boutons d'action rapide

Une barre d'actions fixe en bas de l'ecran contient :
- Bouton "Creer un tenant" (vert, avec icone +) — ouvre le modal de creation
- Bouton "Configuration systeme" (engrenage) — acces aux feature flags et variables d'environnement
- Bouton "Logs d'erreur" (fichier) — redirection vers Sentry ou le viewer de logs interne
- Bouton "Billing Stripe" (carte) — ouverture du dashboard Stripe dans un nouvel onglet
- Bouton "Documentation API" (livre) — ouverture de la documentation OpenAPI (Swagger UI)

---

## 4.2 Dashboard Admin Soumissionnaire (`/dashboard`)

Le dashboard admin soumissionnaire est l'interface principale de travail pour le responsable AO de l'entreprise. Il combine des indicateurs de performance, une vue operationnelle des AO en cours, et des acces rapides aux actions les plus frequentes.

### Widget 1 — KPI metiers (4 cartes)

| KPI | Valeur exemple | Contexte |
|---|---|---|
| AO actifs | 12 | Nombre d'AO dans le pipeline (non archives) sur les 30 derniers jours |
| Taux GO ce mois | 23% | 3 GO sur 13 AO qualifiees ce mois |
| CA total remporte (annee) | 4.2 M EUR | Somme des montants des AO gagnes (statut = won) sur l'annee civile en cours |
| Deadlines dans 7 jours | 2 | Nombre d'AO avec date de remise dans les 7 prochains jours — clicable pour voir la liste |

La carte "Deadlines" est surlignee en rouge/orange si > 0, pour attirer l'attention sur l'urgence.

### Widget 2 — Graphique du pipeline (histogramme)

Un histogramme horizontal affiche la repartition des AO par stage du pipeline Kanban :

```
Detecte        [====] 3
Qualifie       [=====] 4
En preparation [==] 2
Redaction      [=] 1
Relecture      [==] 2
Pret a soumettre [ ] 0
Soumis         [==] 2
Gagne / Perdu  [====] 5 (3 G / 2 P)
```

Chaque barre est coloree selon la couleur du stage configuree par l'utilisateur. Le survol d'une barre affiche le nombre exact et la liste des titres d'AO. Un clic sur une barre filtre le tableau des AO en dessous pour ne montrer que ceux du stage selectionne.

### Widget 3 — Graphique taux de gain par CPV (camembert)

Un graphique circulaire (donut chart) affiche le taux de gain (nombre d'AO gagnes / nombre d'AO soumis) par code CPV principal, sur les 12 derniers mois :

- Tranche 1 : "45xxxxx — Travaux de construction" : 35% (vert)
- Tranche 2 : "50xxxxx — Services de reparation" : 20% (bleu)
- Tranche 3 : "33xxxxx — Equipements medicaux" : 15% (orange)
- Tranche 4 : "70xxxxx — Services immobiliers" : 10% (gris)
- Tranche 5 : "Autres" : 20% (gris clair)

Le centre du donut affiche le taux de gain global (25%). Le survol d'une tranche affiche le detail : nombre de gagnes, nombre de perdus, CA total remporte pour ce CPV.

### Widget 4 — Tableau des AO recents

Un tableau de 15 lignes affiche les AO les plus recemment ajoutes ou modifies, avec les colonnes suivantes :

| Colonne | Description |
|---|---|
| Reference | Numero interne (ex : "TAKA-AO-2025-0041") |
| Titre | Titre tronque a 60 caracteres avec tooltip complet |
| CPV | Code et libelle court |
| Montant | "1 850 000 EUR" |
| Qualification | Badge : "GO" (vert), "MAYBE" (orange), "NO-GO" (rouge), "En attente" (gris) |
| Stage | Badge colore du pipeline Kanban |
| Deadline | "J-12" (compte a rebours) ou date absolue si > 30 jours |
| Actions | Icones : Voir (oeil), Qualifier (etoile), Editer (crayon) |

Un champ de recherche full-text en haut du tableau permet de filtrer par titre, CPV, ou reference. Des filtres lateraux permettent de filtrer par qualification, stage, et date.

### Widget 5 — Widget memoire (AO similaires)

Une carte "Intelligence memoire" affiche, pour l'AO actuellement consulte (ou le dernier AO qualifie), une liste des AO similaires trouves dans la memoire episodique :

"Vous consultez : Construction d'un groupe scolaire — 2.4 M EUR

AO similaires dans votre historique :
- Construction d'une ecole maternelle — 1.8 M EUR — GAGNE (mars 2024) — Score : 0.92
- Amenagement d'un college — 3.1 M EUR — PERDU (juin 2024) — Score : 0.87
- Rehabilitation d'ecole primaire — 950 K EUR — GAGNE (octobre 2024) — Score : 0.81"

Chaque entree est clicable pour acceder au detail de l'AO historique. Un bouton "Voir les lecons apprises" affiche les notes et feedback enregistres lors de la cloture de l'AO.

### Widget 6 — Boutons d'action rapide et notifications

**Boutons d'action rapide** (barre horizontale en haut du dashboard) :
- Bouton "Uploader un DCE" (bleu) — ouvre le modal d'upload de PDF
- Bouton "Lancer la veille" (vert) — declenche manuellement l'agent Veilleur (polling des portails BOAMP/TED)
- Bouton "Nouvel AO manuel" (gris) — cree un AO manuellement sans upload de DCE

**Notifications** (dropdown depuis l'icone cloche en header) :
- "Nouvel AO detecte : 'Travaux de voirie — Amiens' (CPV 45233141) — Score MAYBE (0.72)"
- "Deadline J-3 : 'Construction college — TAKA-AO-2025-0038' — Dossier a finaliser"
- "Pierre Martin a commente l'AO 'Rehabilitation gymnase' : 'Le CCTP est incomplet, manque la section electricite'"

---

## 4.3 Dashboard Collaborateur Soumissionnaire (`/dashboard`)

Le dashboard collaborateur soumissionnaire reprend la structure de l'admin mais avec des fonctionnalites reduites, conformement a la matrice de permissions. L'objectif est de donner au collaborateur une vue operationnelle immediate sans le bruit de la configuration.

### Differences avec le dashboard admin

**Retire** :
- Les KPI globaux (taux GO, CA remporte) — le collaborateur ne voit pas les analytics globaux
- Le graphique taux de gain par CPV
- Les boutons de configuration ("Parametres", "Equipe", "Facturation")
- Le bouton "Lancer la veille" (reserve a l'admin)

**Modifie** :
- Le widget pipeline n'affiche que les AO assignes au collaborateur (pas tout le tenant)
- Le tableau des AO recents n'affiche que les AO assignes au collaborateur ou visibles selon les regles de visibilite
- Le widget memoire affiche les AO similaires pour les AO assignes au collaborateur

**Ajoute** :
- Une section "Mes taches" en haut de page affichant les actions prioritaires du collaborateur :
  - "Qualifier l'AO 'Construction college Amiens' — Deadline dans 5 jours"
  - "Finaliser le memoire technique pour 'Rehabilitation gymnase' — En attente de votre relecture"
  - "Repondre au commentaire de Marie Dupont sur 'Voirie municipale'"

### Vue par defaut : Kanban

Contrairement a l'admin qui voit une vue "Liste" par defaut, le collaborateur arrive sur une vue Kanban en colonnes :

```
+-------------+-------------+-------------+-------------+
|  DETECTE    |  QUALIFIE   | EN PREP.    |  REDACTION  |
|    (3)      |    (2)      |    (1)      |    (2)      |
+-------------+-------------+-------------+-------------+
| [Carte AO]  | [Carte AO]  | [Carte AO]  | [Carte AO]  |
| Reference   | Reference   | Reference   | Reference   |
| Titre       | Titre       | Titre       | Titre       |
| Montant     | Montant     | Montant     | Montant     |
| Deadline    | Qualif      | Assigne a   | Qualif      |
| Badge CPV   | Deadline    | moi         | Progress    |
+-------------+-------------+-------------+-------------+
```

Chaque carte AO est draggable d'une colonne a l'autre (drag-and-drop). Le changement de stage est immediatement persiste en base et notifie les autres membres de l'equipe.

### Notifications

Le collaborateur ne recoit les notifications que pour les AO qui le concernent directement :
- Un AO lui est assigne
- Un commentaire est ajoute sur un de ses AO
- La deadline d'un de ses AO approche (J-7, J-3, J-1)
- Un document qu'il a uploade a ete analyse par l'agent Qualifier

---

## 4.4 Dashboard Admin Acheteur (`/acheteur/dashboard`)

Le dashboard admin acheteur est concu pour le responsable des marches de la collectivite. Il met l'accent sur le suivi des AO publies, des candidatures recues, et de la conformite.

### Widget 1 — KPI acheteur (4 cartes)

| KPI | Valeur exemple | Contexte |
|---|---|---|
| AO publies actifs | 5 | Nombre d'AO avec statut "publie" et date de remise non passee |
| Candidatures recues (total) | 23 | Nombre total de candidatures sur tous les AO actifs |
| Taux de reponse moyen | 4.6 | Nombre moyen de candidatures par AO publie |
| Questions en attente | 3 | Nombre de questions de soumissionnaires sans reponse |

La carte "Questions en attente" est surlignee en orange si > 0, car elle represente une obligation de reponse dans les delais legaux.

### Widget 2 — Graphique AO par statut (histogramme)

Un histogramme vertical affiche la repartition des AO par statut :

- Brouillon [===] 3
- Publie actif [=====] 5
- Attribution en cours [==] 2
- Attribue [====] 4
- Clos (perime) [==] 2

Chaque barre est cliquable pour filtrer le tableau des AO en dessous.

### Widget 3 — Graphique candidatures par AO (histogramme)

Un histogramme horizontal affiche le nombre de candidatures recues pour chaque AO publie actif :

```
Rehabilitation gymnase     [=======] 7
Fourniture mobilier        [===] 3
Maintenance chauffage      [====] 4
Construction parking       [==] 2
Restauration scolaire      [=====] 5
```

Un seuil visuel (ligne verticale pointillee) indique le minimum souhaite de 3 candidatures. Les AO en-dessous de ce seuil sont surlignes en orange.

### Widget 4 — Tableau des AO recents

Un tableau de 15 lignes affiche les AO publies, tries par date de publication decroissante :

| Colonne | Description |
|---|---|
| Reference | "TAKA-2025-00427" |
| Titre | Titre tronque avec tooltip |
| Date publication | "15 juin 2025" |
| Date remise | "15 aout 2025" (avec compte a rebours "J-30") |
| Candidatures | "7 / 3 minimum" (vert si >= 3, rouge si < 3) |
| Statut | Badge : "Publie", "Attribution en cours", "Attribue" |
| Actions | Voir (oeil), Modifier (crayon), Telecharger candidatures (telechargement) |

### Widget 5 — Widget "Questions en attente"

Une carte dediee affiche les questions des soumissionnaires qui n'ont pas encore recu de reponse :

| AO | Question | Auteur | Date | Delai |
|---|---|---|---|---|
| TAKA-2025-00427 | "Le plan de chauffage n'est pas lisible. Pouvez-vous le retransmettre ?" | EURL ThermoPlus | Il y a 2 jours | J-5 |
| TAKA-2025-00427 | "La clause de penaute est de 15%. Est-elle negociable ?" | SAS BuildWell | Il y a 1 jour | J-6 |
| TAKA-2025-00419 | "Le DPGF semble incomplet (manque poste 12)." | SA GroupeVinci | Il y a 3 jours | J-8 |

Chaque question est clicable pour acceder directement a l'interface de reponse. Le delai affiche le nombre de jours restants avant la date limite de reponse aux questions.

### Widget 6 — Boutons d'action rapide et notifications

**Boutons d'action rapide** :
- Bouton "Publier un AO" (vert) — lance le wizard de publication (Section 3.6)
- Bouton "Repondre aux questions" (orange si questions en attente, gris sinon) — acces rapide a l'interface Q&R
- Bouton "Generer un rapport de conformite" — lance l'agent Auditor

**Notifications** :
- "Nouvelle candidature sur 'Rehabilitation gymnase' — 8 candidatures au total (seuil atteint)"
- "Question de SAS BuildWell sur l'AO 'Rehabilitation gymnase' — J-6 avant la deadline de reponse"
- "La date de remise de l'AO 'Fourniture mobilier' est dans 7 jours (J-7)"
- "L'AO 'Construction parking' n'a recu que 2 candidatures (minimum : 3) — Envisager une prorogation"

---

## 4.5 Dashboard Collaborateur Acheteur (`/acheteur/dashboard`)

Le dashboard collaborateur acheteur partage la structure de celui de l'admin, avec des restrictions de permissions conformes a la matrice.

### Differences avec le dashboard admin acheteur

**Retire** :
- Le bouton "Publier un AO" est grise ou absent (le collaborateur ne peut pas publier directement)
- Le bouton "Generer un rapport de conformite" (reserve a l'admin)
- Les KPI globaux (taux de reponse, nombre total de candidatures) — remplaces par des KPI limites a son service

**Modifie** :
- Le tableau des AO affiche uniquement les AO de son service/departement (selon la configuration de visibilite)
- Le graphique des candidatures est filtre par ses AO visibles
- Les notifications sont limitees a ses AO

**Ajoute** :
- Un bouton "Proposer un nouvel AO" (bleu) — ouvre le wizard de creation en mode "brouillon". L'AO est sauvegarde avec le statut "brouillon" et une notification est envoyee a l'admin pour validation.
- Une section "Mes brouillons" affichant les AO que le collaborateur a prepares et soumis pour validation, avec leur statut : "En attente de validation", "Valide et publie", "Rejete".

### Actions autorisees

Le collaborateur acheteur peut :
- Consulter tous les AO de son service en lecture
- Repondre aux questions des soumissionnaires (soumis a validation si configure dans le workflow)
- Classement et notation des candidatures (saisie des notes par critere pour chaque candidature)
- Ajouter des commentaires internes sur les candidatures
- Preparer des brouillons d'AO
- Consulter les rapports de conformite (lecture uniquement)

Le collaborateur acheteur ne peut PAS :
- Publier un AO directement
- Modifier les criteres d'attribution d'un AO publie
- Gerer les utilisateurs du tenant
- Modifier l'abonnement
- Supprimer un AO

---

## 4.6 Navigation Sidebar par Role

La sidebar de navigation est le composant central de l'interface. Son contenu varie en fonction du role de l'utilisateur connecte. Chaque element de menu a une icone (lucide-react), un label, et optionnellement un badge de notification.

### Sidebar Editeur (`/editor`)

```
[Logo TAKA OS]  TAKA OS — Editeur

[DASHBOARD]
- Dashboard              [icone layout-dashboard]

[TENANTS]
- Tenants                [icone building-2]     [badge "47"]
- Creer un tenant        [icone plus-circle]

[ANALYTICS]
- Analytics globaux      [icone bar-chart-3]
- Rapports financiers    [icone banknote]

[SYSTEME]
- Configuration          [icone settings]       [badge si alertes]
- Feature flags          [icone toggle-left]
- Logs d'erreur          [icone file-text]      [badge rouge si erreurs]
- API & Integrations     [icone plug]

[SUPPORT]
- Tickets support        [icone message-square] [badge "3" si non lus]
- Documentation          [icone book-open]

[COMPTE]
- Mon compte             [icone user]
- Deconnexion            [icone log-out]
```

### Sidebar Admin Soumissionnaire (`/dashboard`)

```
[Logo TAKA OS]  TAKA OS

[DASHBOARD]
- Dashboard              [icone layout-dashboard]  [badge si deadlines]

[APPELS D'OFFRES]
- Mes AO                 [icone file-text]         [badge "12" actifs]
- Vue Kanban             [icone columns]
- Vue Liste              [icone list]
- Qualification          [icone star]

[DOCUMENTS]
- Upload DCE             [icone upload]
- Mes documents          [icone folder-open]

[INTELLIGENCE]
- Memoire                [icone brain]
- Veille                 [icone search]            [badge si nouveaux AO]

[EQUIPE]
- Mon equipe             [icone users]             [badge si invitations en attente]
- Inviter un collaborateur [icone user-plus]

[PARAMETRES]
- Regles de qualification [icone sliders]
- Pipeline Kanban        [icone git-branch]
- Alertes                [icone bell]
- Mon entreprise         [icone building]

[FACTURATION]
- Mon abonnement         [icone credit-card]
- Factures               [icone receipt]

[COMPTE]
- Mon compte             [icone user]
- Deconnexion            [icone log-out]
```

### Sidebar Collaborateur Soumissionnaire (`/dashboard`)

```
[Logo TAKA OS]  TAKA OS

[DASHBOARD]
- Dashboard              [icone layout-dashboard]

[APPELS D'OFFRES]
- Mes AO (Kanban)        [icone columns]           [vue par defaut]
- Mes AO (Liste)         [icone list]

[DOCUMENTS]
- Upload DCE             [icone upload]

[COMPTE]
- Mon compte             [icone user]
- Deconnexion            [icone log-out]
```

**Elements absents par rapport a l'admin** :
- Pas d'acces "Qualification" (le collaborateur peut lancer une qualification mais pas configurer les regles)
- Pas d'acces "Memoire" en ecriture
- Pas d'acces "Veille" (declenchement)
- Pas d'acces "Equipe"
- Pas d'acces "Parametres"
- Pas d'acces "Facturation"

### Sidebar Admin Acheteur (`/acheteur/dashboard`)

```
[Logo TAKA OS]  TAKA OS — Acheteur

[DASHBOARD]
- Dashboard              [icone layout-dashboard]  [badge si questions en attente]

[APPELS D'OFFRES]
- Mes AO publies         [icone file-text]         [badge "5" actifs]
- Nouvel AO              [icone plus-circle]
- Brouillons             [icone file-clock]

[CANDIDATURES]
- Candidatures recues    [icone inbox]             [badge "23" total]
- Classement             [icone trophy]

[QUESTIONS]
- Questions / Reponses   [icone message-circle]    [badge "3" en attente]

[EQUIPE]
- Mon equipe             [icone users]
- Inviter un collaborateur [icone user-plus]

[PARAMETRES]
- Criteres d'attribution [icone sliders]
- Workflow de validation [icone git-pull-request]
- Mon organisme          [icone building]

[COMPTE]
- Mon compte             [icone user]
- Deconnexion            [icone log-out]
```

### Sidebar Collaborateur Acheteur (`/acheteur/dashboard`)

```
[Logo TAKA OS]  TAKA OS — Acheteur

[DASHBOARD]
- Dashboard              [icone layout-dashboard]

[APPELS D'OFFRES]
- AO publies             [icone file-text]         [lecture seule]
- Proposer un AO         [icone file-plus]
- Mes brouillons         [icone file-clock]

[CANDIDATURES]
- Candidatures           [icone inbox]             [lecture + notation]
- Mon classement         [icone trophy]

[QUESTIONS]
- Questions / Reponses   [icone message-circle]

[COMPTE]
- Mon compte             [icone user]
- Deconnexion            [icone log-out]
```

**Elements absents par rapport a l'admin acheteur** :
- Pas d'acces "Nouvel AO" (remplace par "Proposer un AO" en brouillon)
- Pas d'acces "Equipe"
- Pas d'acces "Parametres"
- Pas d'acces "Facturation"
- Les menus sont en lecture ou en action restreinte

---

# PARTIE V — ARCHITECTURE DE SEGREGATION

## 5.1 Modele Multi-Tenant a 2 Types

TAKA OS adopte une architecture multi-tenant ou tous les tenants (soumissionnaires et acheteurs) partagent la meme base de donnees PostgreSQL. L'isolation des donnees s'effectue a trois niveaux : applicatif, base de donnees, et feature.

### Principe d'isolation par tenant_id

Chaque table metier contient un champ `tenant_id` (UUID, foreign key vers `tenants.id`). Toute requete SQL filtre systematiquement sur ce champ. Un utilisateur authentifie ne peut acceder qu'aux donnees dont le `tenant_id` correspond a celui de son tenant.

```sql
-- Exemple de requete avec isolation tenant
SELECT * FROM tenders 
WHERE tenant_id = 'uuid-du-tenant-courant' 
  AND status = 'active';
```

Le `tenant_id` est extrait du token JWT lors de l'authentification et injecte dans le contexte de la requete (pattern "dependency injection" via FastAPI Depends).

### Determination des features par tenant_type

Le champ `tenant_type` (soumissionnaire / acheteur) determine quelles fonctionnalites sont accessibles. Cette determination s'effectue via le systeme de feature flags :

```python
# Exemple de verification de feature
async def can_access_feature(feature_name: str, tenant: Tenant) -> bool:
    flag = await FeatureFlag.get_by_name(feature_name)
    if flag.scope == "global":
        return flag.default_value
    if flag.scope == "by_tenant_type":
        return flag.overrides.get(tenant.tenant_type.value, flag.default_value)
    if flag.scope == "by_tenant":
        return flag.overrides.get(str(tenant.id), flag.default_value)
    return flag.default_value
```

### Tables communes (tous les types de tenants)

Ces tables sont utilisees par les deux types de tenants et par l'editeur :

| Table | Description | Tenant-type specifique |
|---|---|---|
| `tenants` | Informations du tenant, abonnement, parametres | Oui (champs conditionnels) |
| `users` | Comptes utilisateurs, roles, preferences | Non |
| `user_invitations` | Invitations en attente | Non |
| `feature_flags` | Configuration des fonctionnalites | Indirectement (overrides) |
| `audit_logs` | Journal d'audit immuable | Non (tenant_id peut etre null pour les actions globales) |
| `system_config` | Configuration systeme (editeur uniquement) | Non |

### Tables specifiques Soumissionnaire

Ces tables ne contiennent des donnees que pour les tenants de type `soumissionnaire` :

| Table | Description | Contrainte |
|---|---|---|
| `tenders` | Appels d'offres detectes/uploades | `CHECK (tenant_type = 'soumissionnaire')` via trigger |
| `tender_documents` | Documents associes aux AO (DCE, PDF) | FK vers `tenders` |
| `qualification_rules` | Regles de scoring des 5 dimensions | FK vers `tenants` (un seul jeu de regles par tenant) |
| `qualification_results` | Resultats de scoring (GO/MAYBE/NO-GO) | FK vers `tenders` |
| `pipeline_stages` | Stages personnalises du Kanban | FK vers `tenants` |
| `pipeline_cards` | Cartes AO positionnees dans le Kanban | FK vers `tenders` et `pipeline_stages` |
| `memory_vectors` | Embeddings pgvector pour la memoire episodique | `domain = 'ao'` |
| `memory_episodes` | Episodes metiers (echecs, succes, references) | FK vers `tenants` |
| `alerts` | Alertes configurees par le tenant | FK vers `tenants` |

### Tables specifiques Acheteur

Ces tables ne contiennent des donnees que pour les tenants de type `acheteur` :

| Table | Description | Contrainte |
|---|---|---|
| `appel_offres_public` | AO publies par l'acheteur | `CHECK (tenant_type = 'acheteur')` via trigger |
| `appel_offres_documents` | Documents de consultation (CCTP, RC, DCE) | FK vers `appel_offres_public` |
| `candidatures` | Candidatures recues pour chaque AO | FK vers `appel_offres_public` |
| `candidature_documents` | Documents des candidats (memoires techniques, DC1/DC2) | FK vers `candidatures` |
| `candidature_notations` | Notations par critere pour chaque candidature | FK vers `candidatures` |
| `questions_reponses` | Questions des soumissionnaires et reponses de l'acheteur | FK vers `appel_offres_public` |
| `criteres_attribution` | Criteres et ponderations par AO | FK vers `appel_offres_public` |
| `workflow_validations` | Workflow de validation (qui valide quoi) | FK vers `tenants` |

### Vue d'ensemble du schema

```
+-------------------------------------+
|           TABLES COMMUNES           |
|  tenants | users | audit_logs | ... |
+-------------------------------------+
           | tenant_id
    +------+------+
    |             |
+---v---+     +---v--------+
| TABLES |     | TABLES     |
| SOUMISSIONNAIRE |     | ACHETEUR   |
| tenders          |     | appel_offres_public |
| qualification_*. |     | candidatures |
| pipeline_*       |     | questions_reponses |
| memory_*         |     | criteres_attribution |
+--------+     +----------+
```

---

## 5.2 Securite et Isolation

### Niveau 1 — Isolation applicative (MVP v0.1 a v0.9)

Avant la v1.0, l'isolation s'effectue au niveau applicatif. Chaque endpoint FastAPI utilise une dependency qui :

1. Extrait le `tenant_id` du token JWT
2. Verifie que l'utilisateur appartient bien a ce tenant
3. Injecte le `tenant_id` dans le contexte de la requete
4. Filtre automatiquement toutes les requetes SQLAlchemy sur ce `tenant_id`

```python
# Dependency FastAPI d'isolation tenant
async def get_current_tenant(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Tenant:
    payload = decode_jwt(token)
    tenant_id = payload.get("tenant_id")
    user_id = payload.get("sub")
    
    # Verification que l'utilisateur appartient au tenant
    user = await db.get(User, user_id)
    if str(user.tenant_id) != tenant_id:
        raise HTTPException(403, "Acces interdit a ce tenant")
    
    tenant = await db.get(Tenant, tenant_id)
    if tenant.is_suspended:
        raise HTTPException(403, "Tenant suspendu")
    
    return tenant

# Utilisation dans un endpoint
@app.get("/api/tenders")
async def list_tenders(
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Tender).where(Tender.tenant_id == tenant.id)
    )
    return result.scalars().all()
```

### Niveau 2 — Row-Level Security PostgreSQL (v1.0+)

A partir de la v1.0, PostgreSQL Row-Level Security (RLS) est active sur toutes les tables metier. Cela garantit l'isolation au niveau de la base de donnees, meme en cas de bug applicatif.

```sql
-- Activation RLS sur la table tenders
ALTER TABLE tenders ENABLE ROW LEVEL SECURITY;

-- Politique : un utilisateur ne voit que les tenders de son tenant
CREATE POLICY tenant_isolation_policy ON tenders
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Le tenant_id est injecte via un parametre de session PostgreSQL
-- SET app.current_tenant_id = 'uuid-du-tenant';
```

**Avantages de RLS** :
- Securite renforcee : meme une requete SQL directe (hors application) respecte l'isolation
- Audit simplifie : les politiques RLS sont visibles et verifiables
- Pas de risque d'oubli de filtre `tenant_id` dans une requete

**Conditions prealables** :
- PostgreSQL 15+ (version minimale du blueprint)
- Extension pgvector compatible avec RLS
- Performance testee avec 100+ tenants et 10 000+ AO

### Matrice de visibilite par role

| Role | Portee des donnees | Condition supplementaire |
|---|---|---|
| Editeur (super_admin) | Tous les tenants | Pas de filtre `tenant_id` (acces global) |
| Admin Soumissionnaire | Son tenant uniquement | Tous les AO et utilisateurs du tenant |
| Collaborateur Soum. | Son tenant + AO assignes | Filtre sur `assigned_to = user_id` ou `visibility = 'all'` |
| Admin Acheteur | Son tenant uniquement | Tous les AO publies et candidatures |
| Collaborateur Achet. | Son tenant + service/dept | Filtre sur `service_id` ou `created_by = user_id` |

---

## 5.3 Feature Flags par Type de Tenant

Le tableau suivant recense l'ensemble des fonctionnalites de TAKA OS — Vertical AO et leur disponibilite par type de tenant. Ce tableau est la reference pour le systeme de feature flags.

| Feature | Code feature | Soumissionnaire | Acheteur | Plan minimum |
|---|---|---|---|---|
| **Detection et Veille** |
| Upload DCE (PDF) | `feature.upload_dce` | Oui | Non | Free |
| Veille BOAMP/TED automatique | `feature.veille_auto` | Oui | Non (ils publient) | Pro |
| Classification CPV automatique | `feature.cpv_classify` | Oui | Oui (saisie assistee) | Free |
| **Qualification** |
| Scoring GO/NO-GO/MAYBE | `feature.scoring` | Oui | Non | Free |
| Explication du score par LLM | `feature.scoring_explain` | Oui | Non | Pro |
| Personnalisation des regles | `feature.scoring_config` | Oui | Non | Pro |
| Profils de scoring (3 profils) | `feature.scoring_profiles` | Oui | Non | Pro |
| **Pipeline** |
| Pipeline Kanban (soumissionnaire) | `feature.pipeline_soum` | Oui | Non | Free |
| Pipeline Kanban (acheteur) | `feature.pipeline_achet` | Non | Oui | Free |
| Stages personnalisables | `feature.pipeline_custom` | Oui | Oui | Pro |
| **Publication** |
| Publication d'AO | `feature.ao_publish` | Non | Oui | Free |
| Generation DC1/DC2 | `feature.dc_generator` | Non | Oui | Pro |
| Publication BOAMP/TED auto | `feature.ao_publish_portals` | Non | Oui | Enterprise |
| Workflow de validation | `feature.validation_workflow` | Non | Oui | Pro |
| **Candidatures** |
| Depot de candidature | `feature.candidature_submit` | Oui | Non (ils recoivent) | Free |
| Gestion des candidatures recues | `feature.candidature_manage` | Non | Oui | Free |
| Classement et notation | `feature.candidature_notation` | Non | Oui | Free |
| **Documents** |
| Generation memoire technique | `feature.gen_memoire` | Oui | Non | Pro |
| Generation DCE (offre financiere) | `feature.gen_dce` | Oui | Non | Pro |
| Generation attestations | `feature.gen_attestation` | Oui | Non | Pro |
| Templates CCTP | `feature.cctp_templates` | Non | Oui | Pro |
| **Communication** |
| Questions / Reponses | `feature.q_and_a` | Non | Oui | Free |
| Notifications email | `feature.email_alerts` | Oui | Oui | Free |
| **Memoire et Intelligence** |
| Memoire episodique | `feature.memory_episodic` | Oui | Non | Pro |
| Recherche semantique | `feature.memory_search` | Oui | Non | Pro |
| Capitalisation echecs/succes | `feature.memory_learn` | Oui | Non | Pro |
| **Analytics** |
| Dashboard analytics | `feature.analytics` | Oui | Oui | Pro |
| Export CSV/PDF | `feature.export` | Oui | Oui | Pro |
| Rapports de conformite | `feature.compliance_reports` | Oui (lecture) | Oui | Enterprise |
| **Administration** |
| Gestion de l'equipe | `feature.team_management` | Oui | Oui | Pro |
| Parametres du tenant | `feature.tenant_settings` | Oui | Oui | Free |
| Facturation | `feature.billing` | Oui | Oui | Free |

### Implementation des feature flags

Les feature flags sont evalues a trois endroits :

1. **Backend (FastAPI)** : Dans les dependencies des endpoints
```python
@app.post("/api/tenders/upload")
async def upload_dce(
    file: UploadFile,
    tenant: Tenant = Depends(get_current_tenant),
    flags: FeatureFlags = Depends(get_feature_flags)
):
    if not flags.is_enabled("feature.upload_dce", tenant):
        raise HTTPException(403, "Fonctionnalite non disponible pour ce type de tenant")
    # ... suite du traitement
```

2. **Frontend (React)** : Dans les composants d'interface
```tsx
// Composant conditionnel base sur les feature flags
function Sidebar() {
  const { flags, tenant } = useFeatureFlags();
  
  return (
    <nav>
      {flags.isEnabled("feature.scoring", tenant) && (
        <SidebarItem icon={Star} label="Qualification" />
      )}
      {flags.isEnabled("feature.ao_publish", tenant) && (
        <SidebarItem icon={PlusCircle} label="Nouvel AO" />
      )}
    </nav>
  );
}
```

3. **Base de donnees (PostgreSQL)** : Via des vues filtrees
```sql
-- Vue qui n'expose que les donnees des features actives
CREATE VIEW tenders_visible AS
SELECT t.*
FROM tenders t
JOIN tenants ten ON t.tenant_id = ten.id
WHERE ten.tenant_type = 'soumissionnaire'
  AND ten.is_active = true;
```

---

## 5.4 Considerations de Performance et Scalabilite

### Indexation

Des index composites sont crees sur toutes les tables metier pour garantir les performances avec 100+ tenants et 10 000+ AO :

```sql
-- Index principal d'isolation
CREATE INDEX idx_tenders_tenant_id ON tenders(tenant_id);
CREATE INDEX idx_tenders_tenant_status ON tenders(tenant_id, status);
CREATE INDEX idx_tenders_tenant_deadline ON tenders(tenant_id, deadline_date);

-- Index pour la recherche full-text
CREATE INDEX idx_tenders_search ON tenders USING gin(to_tsvector('french', title || ' ' || COALESCE(description, '')));

-- Index pgvector pour la recherche semantique
CREATE INDEX idx_memory_vectors_embedding ON memory_vectors USING hnsw (embedding vector_cosine_ops);
```

### Partitionnement

La table `audit_logs` est partitionnee par mois pour gerer le volume croissant :

```sql
-- Partitionnement mensuel des audit logs
CREATE TABLE audit_logs_partitioned (
    LIKE audit_logs INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE audit_logs_2025_06 PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
```

### Limites de securite

| Limite | Valeur | Description |
|---|---|---|
| Max tenants par instance | 500 (v1.0) | Limite recommandee avant scaling horizontal |
| Max utilisateurs par tenant | Illimite (Enterprise) | Limite enforcee par le plan d'abonnement |
| Max AO par tenant | 10 000 (soft limit) | Alertes a 80%, blocage d'upload a 100% |
| Max taille fichier upload | 50 Mo | Limite technique du parser PDF |
| Max fichiers par AO | 5 | Limite UI/UX |
| Duree de retention audit logs | 7 ans | Conformite reglementaire francaise |
| Duree de validite invitation | 7 jours | Securite |
| Max rate API | 100 req/min par tenant | Protection contre les abus |

---

## 5.5 Transition vers le Vertical Fiducial

L'architecture de segregation prepare la transition vers le vertical Fiducial (v2). Les elements suivants sont deja en place pour faciliter cette transition :

1. **Le champ `tenant_type` inclut deja la valeur `FIDUCIAL`** dans l'enumeration, meme si elle n'est pas encore utilisee. Cela evite une migration de donnees lors du lancement du v2.

2. **Le systeme de feature flags est generique** et peut activer des features Fiducial pour les tenants de type `fiducial` sans modification de code.

3. **La table `feature_flags` accepte des overrides par tenant_type**, ce qui permet d'activer progressivement les features Fiducial pour les tenants de ce type.

4. **Le kernel (auth, event bus, audit, vault) est totalement generique** et ne necessite aucune modification pour supporter le vertical Fiducial.

5. **Les tables metier Fiducial** (`dossiers_clients`, `declarations_fiscales`, `liasses`, etc.) suivront le meme pattern : `tenant_id` pour l'isolation, `feature_flag` pour la disponibilite, triggers pour les contraintes de type.

---

*Fin du document de validation conceptuelle.*

*Document produit par l'equipe CTO TAKA OS | Mai 2026*
*Reference : TAKA-OS-VAL-001 | Version 1.0 | Licence MIT*
