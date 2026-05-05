# Compte-Rendu de Débat — Groupe Produit & Expérience Utilisateur
## Réunion KIMI-TAKA-SWARM — Session Produit & UX

**Date** : Session Synchrone Agentic  
**Projet** : TAKA OS — OS Agentic pour Appels d'Offres  
**Cible** : PME/ETI Soumissionnaires + Acheteurs Publics  
**Participants** : Frontend Senior, UI/UX Designer, Product Manager, UX Researcher  
**Objectif** : Arbitrer 8+ questions de produit et d'expérience utilisateur pour le MVP et les versions v0.1 à v0.3  

---

## Table des Matières

1. [Contexte & Enjeux](#1-contexte--enjeux)
2. [Questions Débattues](#2-questions-débattues)
   - Q1 : Le Kanban est-il le bon paradigme pour les AO ?
   - Q2 : Le ScoreCard 5D est-il trop complexe ?
   - Q3 : L'onboarding 5 étapes — les utilisateurs vont-ils le terminer ?
   - Q4 : Le sélecteur de Business Line — qui le voit ?
   - Q5 : Le panel HIL — modal bloquante ou notification asynchrone ?
   - Q6 : Le dashboard Éditeur — utile dès le MVP ?
   - Q7 : Les notifications — email, in-app, ou les deux ?
   - Q8 : Le produit tour — dès v0.1 ou v0.3 ?
   - Q9 : La densité d'information sur les dashboards — minimalisme ou exhaustivité ?
   - Q10 : Le système de rôles et permissions — granularité ou simplicité ?
   - Q11 : La recherche cross-AO — comment l'architecturer ?
   - Q12 : Les états vides et messages d'erreur — ton et stratégie
3. [Frictions Utilisateur Identifiées](#3-frictions-utilisateur-identifiées)
4. [Décisions UX/UI Validées](#4-décisions-uxui-validées)
5. [Plan d'Action & Suivi](#5-plan-daction--suivi)
6. [Prochaines Étapes](#6-prochaines-étapes)

---

## 1. Contexte & Enjeux

Le projet TAKA OS ambitionne de devenir le système d'exploitation agentic dédié à l'univers des Appels d'Offres. La dualité de sa cible — à la fois soumissionnaires (PME/ETI qui répondent aux AO) et acheteurs publics (administrations qui les publient et les évaluent) — crée une tension produit majeure : comment offrir une expérience unifiée tout en respectant les logiques métier opposées de ces deux univers.

Le groupe Produit & Expérience s'est réuni pour arbitrer les zones de friction identifiées lors des phases de conception préliminaires. Chaque question a été débattue sous l'angle de quatre voix : le **Product Manager** (vision marché et viabilité), le **UX Researcher** (comportements utilisateurs et frictions), l'**UI/UX Designer** (cohérence visuelle et affordances), et le **Frontend Senior** (faisabilité technique et performance perçue).

L'enjeu central de cette session : éviter le piège du "dashboarditis" (accumulation de widgets sans parcours cohérent) tout en livrant une valeur métier immédiate, mesurable, et compréhensible pour un utilisateur lambda peu familiers avec les outils agentic.

---

## 2. Questions Débattues

---

### Q1 — Le Kanban est-il le bon paradigme pour les AO ?

#### Positions

**Product Manager** — *"Le Kanban est la métaphore familière"*  
Les utilisateurs cibles utilisent déjà Trello, Notion, Monday.com ou Asana dans leur quotidien. La métaphore du Kanban drag-and-drop est immédiatement compréhensible. Un AO, malgré sa complexité intrinsèque, peut être conceptualisé comme une "carte" qui traverse un pipeline de décision. Le coût cognitif d'apprentissage est quasi nul. Proposer autre chose, c'est créer de la friction là où il n'y en a pas besoin.

**UX Researcher** — *"Un AO n'est pas une tâche. La linéarité est un mensonge"*  
Un Appel d'Offres n'est pas une tâche au sens Kanban classique. Les transitions d'état ne sont pas linéaires. Un AO peut passer directement de "Soumis" à "Perdu" sans jamais traverser "En cours d'évaluation". Pire, un AO "Perdu" peut être "Reconsidéré" suite à un recours. Le Kanban impose une linéarité qui déforme la réalité métier et crée de l'anxiété cognitive quand les règles implicites du board sont violées.

De plus, le Kanban masque la dimension temporelle critique des AO : les deadlines DCE, les dates de remise, les phases de consultation. Un utilisateur ne se demande pas "dans quelle colonne est mon AO ?" mais "combien de temps me reste-t-il pour répondre ?" et "quels AO arrivent à échéance cette semaine ?".

**UI/UX Designer** — *"Offrir les deux vues dès le départ : Kanban + Timeline"*  
La solution n'est pas de choisir mais de proposer un dual-view. Vue Kanban pour la gestion opérationnelle quotidienne (déplacer des AO d'une colonne à l'autre), vue Timeline (type Gantt simplifié) pour la vision temporelle et stratégique. L'utilisateur bascule selon son intention. C'est le pattern "Board / Timeline / List / Calendar" que l'on trouve chez les outils modernes (Linear, Height, Asana).

**Frontend Senior** — *"Deux vues = double maintenance. Priorisons une vue robuste"*  
Chaque vue est un état d'interface à maintenir, tester, et faire évoluer. Deux vues dès le MVP signifient deux sources de bugs potentiels, deux logiques de filtrage, deux rendus à optimiser. Si le Kanban est le paradigme dominant du marché, faisons-le parfaitement — avec une timeline intégrée *dans* la carte AO (badge deadline), pas comme vue alternative. Une vue Timeline peut attendre v0.2 si les retours utilisateurs la demandent explicitement.

#### Débat

Le Product Manager martèle l'argument du "coût cognitif nul" : dans un marché où la concurrence est le tableur Excel et l'email, tout écart aux patterns connus est un risque d'adoption. L'UX Researcher contre-attaque avec des données comportementales : dans les tests informels menés avec 4 PME, 3 ont exprimé leur frustration face aux outils Kanban pour gérer des "objets complexes" avec des deadlines multiples. Elles préfèrent des vues calendaires ou des listes triables par urgence.

L'UI Designer propose une synthèse élégante : un Kanban dont les colonnes sont enrichies d'indicateurs temporels (deadline la plus proche dans chaque colonne), et un toggle en haut de page permettant de basculer vers une vue "Planning" simplifiée. Le Frontend Senior tempère : le toggle est une bonne idée, mais la vue Planning doit être un affichage *dérivé* des mêmes données, pas un nouveau composant complexe.

Le débat se cristallise autour d'une question : est-ce que la vue Kanban est un frein à l'adoption, ou est-ce que l'absence de vue temporelle est le vrai problème ? Le consensus émerge que le Kanban est acceptable comme vue par défaut, mais que l'absence de marqueurs temporels visibles serait un échec UX majeur.

#### Décision

**Vue Kanban par défaut pour le MVP, avec indicateurs temporels intégrés dans chaque carte (deadline, jours restants, urgence colorimétrique). Toggle "Vue Planning" en haut de page qui affiche une timeline simplifiée (type roadmap) sans drag-and-drop complexe. La vue Planning est un affichage alternatif des mêmes données Kanban, pas une nouvelle structure de données.**

- **Responsable** : UI/UX Designer
- **Deadline** : v0.1 (MVP) pour le Kanban enrichi ; v0.2 pour le toggle Vue Planning
- **Justification** : Réduction du risque d'adoption par la métaphore familière, tout en adressant la friction temporelle par des indicateurs intégrés. Le toggle Planning offre une promesse de valeur pour les utilisateurs avancés sans complexifier le MVP.

#### Action

1. Concevoir les micro-interactions du Kanban (drag ghost, drop zone, animation de transition entre colonnes)
2. Définir la sémantique colorimétrique des deadlines (vert > 7j, orange 3-7j, rouge < 3j, grisé passé)
3. Prototyper le toggle Vue Planning en wireframe basse fidélité
4. Valider le pattern avec 3 utilisateurs test (soumissionnaires) avant implémentation v0.2

---

### Q2 — Le ScoreCard avec 5 dimensions est-il trop complexe pour un utilisateur lambda ?

#### Positions

**UX Researcher** — *"Le verdict en 2 phrases, pas un rapport de 5 pages"*  
Le soumissionnaire type, une PME de 20 personnes, n'a ni le temps ni l'expertise pour digérer une ScoreCard à 5 dimensions (probablement : Compatibilité Métier, Rentabilité, Capacité de Réponse, Risque Juridique, Positionnement Concurrentiel). Ce qu'elle veut : "Dois-je répondre ou non ?" et "Pourquoi, en deux phrases ?". Le scoring agentic doit être un **oracle**, pas un **tableau de bord d'analyse**. Chaque dimension supplémentaire dilue la décision et crée de la paralysie analytique.

**Product Manager** — *"Le ScoreCard est pour l'admin qui configure. Le collaborateur voit le verdict"*  
Il y a confusion de personas. La ScoreCard 5D est un outil de *configuration* pour l'administrateur soumissionnaire qui calibre les pondérations et les seuils de scoring. Le collaborateur (celui qui lit l'AO au quotidien) ne voit que le résultat agrégé : GO (score > 70%), NO-GO (score < 40%), ou MAYBE (zone intermédiaire). Chaque verdict est accompagné d'une explication générée agentic de 2-3 phrases max, contextualisée. La complexité est masquée par l'abstraction.

**UI/UX Designer** — *"2 niveaux de détail : verdict + expansion"*  
Proposer une interface à deux niveaux de détail : niveau 1 (condensé) = badge GO/NO-GO/MAYBE + explication courte + score global. Niveau 2 (détaillé) = ScoreCard 5D dépliable avec sliders et visualisation radar (spider chart), accessible via un chevron "Voir le détail". Les deux niveaux cohabitent sans imposer la complexité. C'est le pattern "progressive disclosure" appliqué au scoring.

**Frontend Senior** — *"Le radar chart est lourd. Un score horizontal suffit"*  
Le spider chart / radar chart est visuellement impactant mais peu lisible pour les non-initiés. Les humains comparent mieux des longueurs (barres horizontales) que des aires et des angles. Proposer 5 barres horizontales normalisées avec des labels explicites. C'est plus accessible, plus rapide à parser, et moins coûteux en performance de rendu.

#### Débat

L'UX Researcher insiste sur le risque de "décision fatigue" : si un utilisateur doit lire 5 critères avant de comprendre pourquoi un AO est un NO-GO, il finira par ignorer le scoring. Le Product Manager rappelle que le scoring agentic est la *différenciation* de TAKA OS : sans transparence sur les critères, l'utilisateur ne fait pas confiance au verdict. On ne peut pas dire "NO-GO" sans dire "pourquoi", et le "pourquoi" a besoin de granularité.

L'UI Designer tranche avec la progressive disclosure : l'utilisateur qui ne veut que le verdict l'a immédiatement. L'utilisateur qui veut comprendre (ou contester) le verdict peut déplier. Le Frontend Senior ajoute une nuance technique : les barres horizontales permettent d'afficher les seuils configurables par l'admin (lignes verticales "minimum acceptable"), ce qui rend la ScoreCard encore plus compréhensible.

Le débat dérive sur la question de la confiance : est-ce que l'utilisateur lambda fait confiance à un agentic score sans voir les critères ? L'UX Researcher cite des études (Google Material Design, Nielsen Norman Group) montrant que les utilisateurs font davantage confiance aux systèmes qui expliquent leur raisonnement, même brièvement. Le consensus émerge que la transparence est non négociable, mais que la *présentation* de cette transparence doit être graduée.

#### Décision

**Deux niveaux de détail obligatoires. Niveau 1 (affichage par défaut) : verdict GO/NO-GO/MAYBE avec badge colorimétrique + score global (0-100) + explication agentic de 2 phrases max. Niveau 2 (dépliable) : ScoreCard 5D avec 5 barres horizontales normalisées + seuils configurables visibles + labels explicites. Le détail est accessible par un clic sur la carte scoring, jamais affiché par défaut.**

- **Responsable** : UX Researcher (validation des labels et formulation des explications agentic) ; UI/UX Designer (conception des deux niveaux)
- **Deadline** : v0.1 (MVP) pour le niveau 1 ; v0.2 pour le niveau 2 dépliable
- **Justification** : Respect du principe de progressive disclosure. L'utilisateur pressé est servi immédiatement, l'utilisateur curieux est satisfait sans être submergé. La confiance dans le système agentic repose sur la transparence accessible, pas sur la transparence imposée.

#### Action

1. Rédiger le corpus des explications agentic types pour chaque combinaison de verdicts (GO/NO-GO/MAYBE x 5 dimensions dominantes)
2. Concevoir le composant ScoreCard v1 (niveau 1) avec les 3 états de verdict et leurs palettes
3. Concevoir le composant ScoreCard v2 (niveau 2) avec barres horizontales + seuils
4. Tester la compréhension des barres horizontales auprès de 5 utilisateurs non-techniques
5. Valider que la formulation des explications agentic est perçue comme "utile" et non "patronisante"

---

### Q3 — L'onboarding 5 étapes — les utilisateurs vont-ils le terminer ?

#### Positions

**UX Researcher** — *"60% abandonnent après l'étape 3. Il faut skipper et revenir"*  
Les données de l'industrie sont claires : les wizards de plus de 3 étapes ont un taux d'abandon exponentiel. À l'étape 3, on perd 40-50% des utilisateurs. À l'étape 5, il ne reste que 20-25% des starters. Pourquoi ? Parce que l'utilisateur n'a pas encore perçu de valeur à l'étape 3 : il a juste donné des données sans rien recevoir en retour. La solution : permettre le skip à chaque étape, sauvegarder la progression, et offrir un bouton "Terminer la configuration" omniprésent dans l'interface post-onboarding.

**Product Manager** — *"Sans config (CPV, zones), le produit ne marche pas. Les données sont critiques"*  
Le scoring agentic de TAKA OS repose sur des paramètres de configuration : les codes CPV (Common Procurement Vocabulary), les zones géographiques d'intervention, la taille d'entreprise, les capacités financières. Sans ces données, l'agent ne peut pas scorer un AO. Un onboarding incomplet = un produit inutile. Permettre le skip systématique, c'est accepter que des utilisateurs arrivent sur un dashboard vide avec un message "Configurez votre profil" — ce qui est une expérience de déception garantie.

**UI/UX Designer** — *"Defaults intelligents + onboarding segmenté par persona"*  
Ne pas forcer l'utilisateur à tout configurer manuellement. Proposer des defaults intelligents : détection SIRET = auto-remplissage taille, secteur, zone. Proposer des templates de profil ("BTP régional", "Informatique nationale", "Services aux collectivités"). L'onboarding 5 étapes devient alors un "affinage" d'un profil pré-rempli, pas une construction from scratch. De plus, segmenter : le soumissionnaire a besoin de CPV et zones ; l'acheteur a besoin d'autres paramètres (type de procédure, seuils). Pourquoi imposer 5 étapes identiques aux deux personas ?

**Frontend Senior** — *"L'onboarding est un funnel. Mesurons-le avant de le couper"*  
L'argument du "60% abandonnent" est une statistique globale de l'industrie, pas une donnée TAKA OS. Avant de réduire l'onboarding ou d'autoriser le skip, installons un tracking précis du funnel. Peut-être que les utilisateurs TAKA OS (motivés par la douleur des AO) sont plus résilients que la moyenne. Réduire l'onboarding avant d'avoir des données, c'est optimiser sans mesurer. Proposition : onboarding complet pour v0.1, avec tracking granulaire, puis décision data-informed à v0.2.

#### Débat

L'UX Researcher oppose une vérité d'expérience : les utilisateurs B2B SaaS ne sont pas plus résilients que les B2C. Ils sont pires, parce qu'ils ont une alternative immédiate (Excel, email, leur ancien process). Le Product Manager rétorque que la douleur des AO est si forte que l'utilisateur est prêt à investir 5 minutes pour la résoudre. Le débat tourne autour de la nature de la motivation : est-elle "résoudre une douleur" (forte, permet long onboarding) ou "explorer une promesse" (faible, exige valeur immédiate) ?

L'UI Designer tranche avec les defaults intelligents : si l'utilisateur ne perçoit pas l'effort, l'abandon baisse. Un profil pré-rempli à 70% réduit le coût cognitif perçu. Le Frontend Senior accepte le compromis : defaults intelligents + tracking, mais pas de skip généralisé dès le MVP.

Le débat s'intensifie sur la question du "quid pro quo" : à quelle étape l'utilisateur reçoit-il sa première valeur ? Le Product Manager propose de décaler le scoring : dès l'étape 3, l'agent simule un scoring sur un AO exemple avec les données déjà saisies. L'UX Researcher approuve : la "première valeur perçue" (Aha! moment) doit arriver avant la fin du wizard.

#### Décision

**Onboarding obligatoire mais optimisé. Defaults intelligents par détection SIRET et templates de profil. Segmentation persona : 5 étapes pour soumissionnaire (avec scoring simulé à l'étape 3 comme Aha! moment), 4 étapes pour acheteur. Skip possible uniquement sur les étapes 4-5 (non critiques), avec sauvegarde de progression. Tracking complet du funnel onboarding pour validation data-informed à v0.2.**

- **Responsable** : Product Manager (définition des étapes critiques vs optionnelles) ; UX Researcher (formulation des messages et réduction de la friction)
- **Deadline** : v0.1 (MVP) pour l'onboarding optimisé avec tracking
- **Justification** : L'onboarding est un investissement nécessaire pour la valeur produit, mais il doit être perçu comme un "affinage" (grâce aux defaults) plutôt qu'une "construction from scratch". Le scoring simulé à l'étape 3 crée le Aha! moment qui motive la complétion.

#### Action

1. Définir les 3 templates de profil par défaut avec leurs CPV et zones pré-remplis
2. Intégrer l'API SIRET pour auto-remplissage (taille, secteur, forme juridique)
3. Concevoir l'écran de scoring simulé (étape 3) avec un AO exemple réaliste
4. Implémenter le tracking funnel (step_start, step_complete, step_skip, onboarding_complete)
5. Rédiger les messages de "reprendre plus tard" pour les utilisateurs qui ferment l'app
6. Prévoir le mécanisme de sauvegarde de progression (localStorage + backend)

---

### Q4 — Le sélecteur de Business Line en top bar — visible pour tout le monde ou seulement admin ?

#### Positions

**UI/UX Designer** — *"Tout le monde. Même un collaborateur avec 2 BL doit pouvoir filtrer"*  
La Business Line est une dimension fondamentale de la navigation. Un collaborateur peut être rattaché à plusieurs BL (ex : une PME qui fait du BTP et de l'informatique). Masquer le sélecteur au collaborateur, c'est l'obliger à naviguer dans un Kanban brouillé avec des AO de natures différentes. Le sélecteur en top bar est un pattern standard ( Salesforce, HubSpot, Figma ) : il contextualise l'ensemble de l'interface. Supprimer ce filtre global, c'est créer une expérience de "KPIs mélangés" qui désoriente.

**Product Manager** — *"Non. Le collaborateur n'a qu'une vue Kanban, le filtre est implicite"*  
Le collaborateur n'est pas un analyste transverse. Son quotidien : traiter les AO qui lui sont assignés. Ces AO appartiennent, par définition, à une Business Line déjà définie par l'administrateur qui les a assignés. Le filtre BL est donc implicite dans l'assignation. Ajouter un sélecteur BL pour le collaborateur, c'est ajouter une complexité inutile : "Pourquoi je ne vois pas cet AO ? Ah, c'est parce que j'ai changé de BL hier et j'ai oublié." Le collaborateur a besoin de simplicité, pas de contrôle analytique.

**UX Researcher** — *"Le collaborateur multi-BL existe. Nier ce cas, c'est créer un edge case frustrant"*  
Les PME/ETI cibles sont souvent multi-métiers. Un collaborateur peut être assigné à des AO du BTP (été) et de l'informatique (hiver). Ce n'est pas un edge case, c'est une réalité saisonnière. Sans sélecteur BL, le collaborateur voit ses AO mélangés dans un même Kanban, sans indication visuelle de la BL. C'est une expérience de "context switching" permanente. Au minimum, afficher un badge BL sur chaque carte AO, et permettre un filtre par BL *dans* le Kanban.

**Frontend Senior** — *"Le sélecteur global impacte toutes les requêtes. Un filtre local au Kanban est plus sûr"*  
Un sélecteur global en top bar signifie que chaque changement de BL rechargera potentiellement plusieurs widgets du dashboard (Kanban, stats, notifications). C'est un risque de cohérence et de performance. Un filtre local au Kanban est plus prévisible : il n'affecte que la vue Kanban. Si le besoin est de filtrer les AO par BL, intégrons le filtre dans la barre d'outils du Kanban, pas dans la navigation globale.

#### Débat

Le Product Manager maintient sa position : le collaborateur a une seule fonction, traiter ses AO assignés. L'assignation = le filtre. L'UI Designer contre-attaque : l'assignation est faite par l'admin, pas par le collaborateur. Si l'admin a fait une erreur d'assignation, ou si le collaborateur veut "voir ce qui se passe dans l'autre BL", il n'a aucun moyen de le faire. Le Product Manager rétorque que "voir l'autre BL" n'est pas le job du collaborateur, c'est celui de l'admin.

L'UX Researcher apporte une nuance comportementale : les utilisateurs ne se définissent pas par leur rôle assigné, mais par leurs objectifs. Un collaborateur qui sait qu'un AO de l'autre BL est en retard et va impacter sa BL (même ressource partagée) a besoin de visibilité transverse. C'est une réalité organisationnelle des PME. Le Frontend Senior synthétise : le besoin de visibilité transverse existe, mais le sélecteur global est un marteau pour écraser une mouche. Un badge BL sur chaque carte + filtre local Kanban suffit.

Le débat se résout sur une question de principe : est-ce que TAKA OS est un outil de *contrôle* (l'admin décide ce que le collaborateur voit) ou un outil de *collaboration* (le collaborateur a de la visibilité) ? Le consensus penche vers la collaboration, mais avec des garde-fous.

#### Décision

**Le sélecteur de Business Line en top bar est visible uniquement pour les rôles Admin (Admin Soumissionnaire et Admin Acheteur). Pour les collaborateurs, le sélecteur est remplacé par un filtre "Business Line" intégré dans la barre d'outils du Kanban. Chaque carte AO affiche un badge BL coloré pour la reconnaissance immédiate. Le collaborateur avec une seule BL ne voit pas le filtre (pas de complexité inutile). Le collaborateur multi-BL voit le filtre actif avec les BL auxquelles il est rattaché.**

- **Responsable** : UI/UX Designer (positionnement et style du sélecteur admin + filtre collaborateur)
- **Deadline** : v0.1 (MVP)
- **Justification** : Respect du principe de moindre privilège et de contexte adaptatif. L'admin a besoin de visibilité transverse (sélecteur global), le collaborateur a besoin de simplicité (filtre local) tout en conservant la capacité à naviguer entre ses BL assignées.

#### Action

1. Définir la palette colorimétrique des badges BL (5 couleurs max, accessibles daltonisme)
2. Concevoir le sélecteur top bar pour admin (dropdown avec compteur d'AO actifs par BL)
3. Concevoir le filtre BL intégré Kanban pour collaborateur (chips sélectionnables)
4. Implémenter la logique "masquer si mono-BL" pour alléger l'interface
5. Valider la lisibilité des badges BL sur fond blanc et fond gris

---

### Q5 — Le panel de validation HIL (Human-in-the-Loop) — quand et comment l'afficher ?

#### Positions

**Product Manager** — *"Modal centrale, bloquante, quand l'agent demande validation"*  
Le Human-in-the-Loop est un moment critique du workflow agentic. L'agent a besoin d'une décision humaine pour continuer (valider un résumé d'AO, confirmer une classification, approuver une réponse type). C'est une action **synchrone** : tant que l'utilisateur ne valide pas, l'agent ne peut pas avancer. Une modal centrale, bloquante, avec fond dimmed, signale la criticité de cette interaction. C'est le pattern HIL standard (ChatGPT avec confirmation, Midjourney avec choix de variation). La bloquantitude garantit l'attention et la qualité de la réponse.

**UX Researcher** — *"Non bloquant. Notification sidebar + bouton Valider dans le contexte"*  
L'utilisateur d'une PME n'est pas devant TAKA OS en continu. Il consulte l'outil entre deux tâches. Une modal bloquante, c'est l'interruption forcée. C'est l'équivalent du "pop-up publicitaire" : même si la justification est métier, l'expérience est agressive. L'utilisateur en réunion, en appel, ou en focus profond ne veut pas être arraché à sa tâche par un agent qui "réclame" une validation. La solution : notification asynchrone (toast ou sidebar) qui attend l'attention de l'utilisateur. Le bouton "Valider" est intégré dans le contexte de l'AO concerné, pas dans une modal générique.

**UI/UX Designer** — *"Différencier HIL critique vs HIL informatif"*  
Toutes les validations HIL ne se valent pas. Il y a les HIL *critiques* (l'agent ne peut pas continuer sans validation : ex. validation d'une réponse à soumettre) et les HIL *informatifs* (l'agent a fait une proposition, l'utilisateur peut valider ou ignorer : ex. classification d'un AO). Les HIL critiques justifient une modal bloquante. Les HIL informatifs justifient une notification asynchrone. C'est une taxonomie HIL à définir.

**Frontend Senior** — *"La modal bloquante est plus simple à implémenter. L'asynchrone nécessite un système d'états"*  
Techniquement, une modal bloquante est un état binaire (affiché / caché). Un système HIL asynchrone nécessite : un système de notifications persistantes, un état "en attente de validation" par AO, une gestion de la concurrence (plusieurs HIL sur le même AO), une synchronisation temps réel. C'est un ordre de complexité supérieur. Si le MVP a besoin de HIL, commençons par la modal bloquante, et évolutions vers l'asynchrone à v0.2.

#### Débat

Le Product Manager argumente que la qualité du workflow agentic dépend de la qualité des validations. Si l'utilisateur ignore une validation HIL, l'agent produit du contenu de mauvaise qualité, ce qui dégrade la confiance dans le produit. L'UX Researcher rétorque que la confiance ne se construit pas par la contrainte, mais par la pertinence. Un agent qui propose des validations pertinentes et bien contextualisées sera validé rapidement, même en asynchrone. Un agent qui interrompt constamment sera perçu comme un nuisible.

L'UI Designer propose une matrice de décision : chaque type d'action HIL reçoit un score d'urgence (1-5). Seuls les scores 4-5 déclenchent une modal. Les scores 1-3 déclenchent une notification sidebar. Le Product Manager accepte le principe mais demande : qui définit le score d'urgence ? L'agent ? L'admin ? Le Product Manager lui-même ? L'UX Researcher suggère que le score soit déterminé par l'impact métier de la décision : "soumettre une réponse" = 5, "classifier un AO" = 2.

Le Frontend Senior souligne un risque technique : si plusieurs HIL sont en attente, une sidebar de notifications peut devenir une "liste de tâches" que l'utilisateur n'arrive pas à vider. C'est la même anxiété que la boîte email. Le consensus émerge qu'il faut un système HIL avec : priorisation, regroupement par AO, et expiration (un HIL non traité après X heures est résolu par défaut ou escaladé).

#### Décision

**Système HIL différencié à deux vitesses. HIL critiques (impact métier élevé : validation de soumission, validation financière) : modal centrale semi-bloquante (l'utilisateur peut fermer mais reçoit un avertissement "Cette action bloque l'agent"). HIL informatifs (classification, résumé, tagging) : notification sidebar persistante avec bouton de validation contextualisé. Taxonomie HIL à définir avec 3 niveaux d'urgence. Un HIL informatif non traité après 24h expire et l'agent applique sa proposition par défaut.**

- **Responsable** : Product Manager (définition de la taxonomie HIL et des règles d'urgence) ; UX Researcher (conception de la sidebar et des micro-copy de notification)
- **Deadline** : v0.1 (MVP) pour les HIL critiques en modal ; v0.2 pour la sidebar HIL asynchrone
- **Justification** : Respect du contexte utilisateur. Les décisions critiques méritent l'attention totale (modal). Les décisions informatives doivent s'adapter au rythme de travail de l'utilisateur (asynchrone). L'expiration évite l'accumulation de dette HIL.

#### Action

1. Définir la taxonomie HIL v1 avec 5 types d'actions et leur niveau d'urgence
2. Concevoir la modal HIL critique (layout, CTA, avertissement de blocage)
3. Concevoir la sidebar de notifications HIL (position, animation d'entrée, badge de compteur)
4. Implémenter la logique d'expiration des HIL informatifs (24h par défaut, configurable)
5. Rédiger les micro-copy de la modal (ton informatif, pas accusateur)
6. Prévoir le cas de concurrence : plusieurs HIL sur le même AO

---

### Q6 — Le dashboard Éditeur (super admin) — est-il vraiment utile dès le MVP ?

#### Positions

**UI/UX Designer** — *"Non. Le CEO veut des métriques brutes, pas des jolis graphiques"*  
Le super admin (fondateur, CEO, ou responsable produit de l'éditeur TAKA) a des besoins radicalement différents des utilisateurs finaux. Il ne veut pas un dashboard avec des graphiques à camembert et des courbes d'engagement. Il veut un **tableau brut de données** : liste des tenants actifs, nombre d'AO traités par tenant, tickets de support ouverts, factures en retard, erreurs système. C'est un outil de **supervision opérationnelle**, pas de **reporting stratégique**. Un dashboard graphique est un détournement de ressources UI pour un persona qui n'en a pas besoin.

**Product Manager** — *"Oui. Le CEO est aussi le 1er support client"*  
Dans une startup early-stage, le CEO fait le support client. Il reçoit les emails "ça ne marche pas" et doit diagnostiquer rapidement. Pour cela, il a besoin de visibilité : tenants actifs/inactifs, erreurs remontées, volume d'AO par tenant, statut des paiements. Un dashboard Éditeur avec 15+ widgets n'est pas du "dashboarditis", c'est un **cockpit de survie**. Le CEO ne va pas lancer des requêtes SQL à 23h pour savoir quel client a un problème. Il a besoin d'une vue d'ensemble immédiate.

**UX Researcher** — *"Le besoin existe, mais les 15 widgets sont une hypothèse non validée"*  
Personne n'a interrogé les futurs super admins sur leurs 15 widgets. C'est une hypothèse de conception. Peut-être qu'ils en utilisent 3 régulièrement et ignorent les 12 autres. La règle de Pareto s'applique aux dashboards : 20% des widgets produisent 80% de la valeur. Avant de concevoir 15 widgets, faisons un tri : quels sont les 3 widgets indispensables pour le MVP ? Les autres peuvent attendre, ou être ajoutés à la demande.

**Frontend Senior** — *"15 widgets = 15 requêtes API potentielles. C'est un risque de perf"*  
Un dashboard avec 15 widgets indépendants signifie potentiellement 15 appels API au chargement. Même avec du caching et du lazy-loading, c'est un temps de chargement significatif et une charge serveur. Pour le MVP, privilégions un tableau de données unique avec filtres et tri. C'est plus rapide à charger, plus rapide à implémenter, et couvre 80% des besoins.

#### Débat

Le Product Manager insiste sur la réalité du early-stage : le CEO/super admin est le 1er support, le 1er commercial, et le 1er Ops. Il a besoin de réponses rapides. L'UI Designer rétorque que "réponses rapides" ne signifie pas "15 widgets". Un tableau de données bien filtré est plus rapide à parser que 15 widgets colorés.

L'UX Researcher propose une méthode : lister les 15 widgets, demander à l'équipe fondatrice de classer par priorité (Must Have / Should Have / Nice to Have), et ne garder que les Must Have pour le MVP. Le Frontend Senior appuie : un tableau de données avec colonnes triables, filtres rapides, et export CSV couvre l'essentiel. Les widgets graphiques (courbes, camemberts) sont du "nice to have" pour le reporting, pas pour l'opérationnel.

Le débat dérive sur la question du temps : le super admin passe-il plus de temps à *diagnostiquer* (tableau brut) ou à *présenter* (graphiques) ? Dans une phase MVP, la réponse est évidente : le diagnostic prime. Le consensus émerge que le besoin de dashboard Éditeur est réel et critique, mais que la forme "tableau de données + 3 KPIs cards" est plus adaptée que "15 widgets graphiques".

#### Décision

**Le dashboard Éditeur est indispensable dès le MVP, mais sous la forme d'un tableau de données principal avec 3 KPIs cards en top (tenants actifs, AO traités ce mois, tickets support ouverts). Les widgets graphiques sont dépriorisés à v0.2. Le tableau de données liste les tenants avec colonnes : nom, statut, nombre d'utilisateurs, volume AO, dernière activité, statut facturation, actions rapides (voir détail, suspendre, contacter). Filtres par statut, date, et volume. Export CSV.**

- **Responsable** : Product Manager (définition des colonnes et filtres) ; UI/UX Designer (conception du tableau et des KPI cards)
- **Deadline** : v0.1 (MVP)
- **Justification** : Le super admin est un persona critique pour la survie du produit en phase early-stage. Un tableau de données est plus actionnable qu'un dashboard graphique pour les tâches de support et d'ops. Les 3 KPIs cards donnent la vue d'ensemble immédiate sans surcharge cognitive.

#### Action

1. Définir les 3 KPIs cards du dashboard Éditeur (MVP)
2. Définir les colonnes du tableau de données tenants (MVP)
3. Concevoir les filtres rapides (statut, période, volume AO)
4. Concevoir les actions rapides par tenant (boutons d'action inline)
5. Prévoir l'export CSV et l'affichage responsive du tableau
6. Lister les 12 widgets dépriorisés pour roadmap v0.2-v0.3

---

### Q7 — Les notifications — email, in-app, ou les deux ?

#### Positions

**Product Manager** — *"Email pour les deadlines. In-app pour tout le reste"*  
Les notifications doivent suivre le principe de l'urgence. Une deadline d'AO (ex : DCE qui ferme dans 48h) est critique et urgente : elle mérite un email. Une classification d'AO réalisée par l'agent est informative : elle mérite une notification in-app. L'email est le canal de l'urgence absolue, l'in-app est le canal de l'activité normale. Cette séparation claire évite la fatigue de notification et garantit que l'email est perçu comme important (pas du spam).

**UX Researcher** — *"Email = spam. In-app + option push (Web Push API)"*  
Les professionnels reçoivent déjà 100+ emails par jour. Ajouter des emails de notification SaaS, même pour des deadlines, c'est ajouter du bruit. Les utilisateurs désactivent rapidement les notifications email (ou les ignorent). L'efficacité de l'email comme canal d'urgence est en déclin structurel. La solution : notification in-app comme canal principal, avec **Web Push API** pour les vraies urgences (deadline imminente). Le push est plus visible que l'email, plus contextuel, et moins encombrant. L'utilisateur garde le contrôle : opt-in pour le push, paramétrage granulaire des types de notification.

**UI/UX Designer** — *"Email est encore le roi B2B. Mais formaté intelligemment"*  
Les données de l'industrie B2B SaaS montrent que l'email reste le canal le plus fiable pour l'activation et la rétention. Mais l'email doit être **contextualisé** et **actionnable** : pas de "Vous avez une notification", mais "L'AO 'Construction Ecole Jean Jaurès' ferme dans 2 jours. Voir le détail." L'email devient une extension de l'interface, pas un canal séparé. In-app pour le temps réel, email digest pour le récapitulatif, email immédiat pour l'urgence.

**Frontend Senior** — *"Web Push API = complexité cross-navigateur. Email = universel"*  
La Web Push API, bien que standardisée, a des comportements hétérogènes selon les navigateurs (Safari est plus restrictif que Chrome, Firefox a son propre système). Implémenter le push nécessite : service worker, gestion des permissions, fallback email, gestion des utilisateurs qui refusent la permission. C'est un investissement technique significatif pour un MVP. L'email, malgré ses défauts, est universel et immédiat à implémenter.

#### Débat

Le Product Manager et l'UX Researcher s'opposent frontalement sur la perception de l'email. Le PM voit l'email comme un canal fiable ; le UX Researcher le voit comme un canal saturé. L'UI Designer propose une synthèse : l'email n'est pas mort, mais il doit être **redessiné**. Fini les notifications génériques. L'email TAKA OS doit être un "mini-dashboard" : sujet explicite, contenu contextualisé, CTA clair, et option "Ne plus recevoir ce type d'email".

L'UX Researcher reste sceptique : même un email bien formaté est un email de plus dans une boîte pleine. Le push in-app (Web Push) est plus interruptif et donc plus efficace pour les urgences. Le Frontend Senior rappelle que le push Web nécessite que l'utilisateur ait l'app ouverte dans un onglet — ce qui n'est pas garanti. L'email, lui, arrive même si l'utilisateur n'a pas ouvert TAKA OS depuis une semaine.

Le débat tourne autour d'une question fondamentale : est-ce que TAKA OS doit "tirer" l'utilisateur vers l'app (email/push), ou est-ce que l'utilisateur doit "pousser" vers l'app quand il en a besoin ? Le consensus émerge que pour une PME avec des deadlines d'AO, le "tirer" est nécessaire — mais de manière intelligente et contrôlable.

#### Décision

**Système de notification hybride à trois canaux. Niveau 1 (in-app) : toutes les notifications affichées dans le centre de notifications de l'application, accessible par une cloche en top bar. Niveau 2 (email digest) : email quotidien récapitulatif (opt-out possible) avec les deadlines du jour et les actions en attente. Niveau 3 (email immédiat) : email instantané uniquement pour les événements critiques (deadline < 24h, HIL critique en attente, erreur système). Web Push API dépriorisé à v0.3 (en attente de validation du besoin par les retours utilisateurs). L'utilisateur contrôle ses préférences de notification par type d'événement.**

- **Responsable** : UX Researcher (définition des types d'événements et de leur canal) ; Product Manager (rédaction des templates email)
- **Deadline** : v0.1 (MVP) pour in-app + email digest + email immédiat critique
- **Justification** : Couverture maximale de l'urgence sans spam. L'email digest réduit la fréquence tout en maintenant l'engagement. L'email immédiat critique garantit que l'utilisateur ne manque pas une deadline. Le push est un investissement v0.3 si les retours utilisateurs le justifient.

#### Action

1. Définir la matrice événement × canal (quel événement sur quel canal)
2. Concevoir le centre de notifications in-app (cloche, dropdown, badge, marquage lu/non lu)
3. Rédiger le template email digest (design responsive, sections : deadlines, HIL en attente, activité récente)
4. Rédiger le template email immédiat critique (sujet explicite, contenu minimal, CTA unique)
5. Concevoir l'écran de préférences de notification (par type d'événement, par canal)
6. Implémenter la logique de regroupement (pas plus d'1 email immédiat par heure pour éviter le spam)

---

### Q8 — Le produit tour (tutoriel interactif) pour les nouveaux — nécessaire dès v0.1 ?

#### Positions

**UX Researcher** — *"Oui. Sans guidance, l'utilisateur ne comprend pas la valeur agentic"*  
Le scoring agentic est un concept nouveau pour la plupart des PME soumissionnaires. Elles ne savent pas ce qu'un "agent" peut faire pour elles, ni comment interpréter un score, ni pourquoi elles devraient faire confiance à un algorithme. Sans tour guidé, l'utilisateur arrive sur un dashboard avec des scores et des badges sans comprendre la logique. C'est l'équivalent d'arriver dans un cockpit sans manuel. Le tour interactif (bubbles, highlights, tooltips contextuels) est l'assurance que l'utilisateur comprend la promesse de valeur dans ses 5 premières minutes.

**UI/UX Designer** — *"Non. On n'a pas de feedback utilisateur. Attendre v0.3"*  
Un produit tour basé sur des hypothèses est un produit tour qui enseigne les mauvaises choses. On ne sait pas encore où les utilisateurs butent. Peut-être qu'ils comprennent immédiatement le scoring mais bloquent sur le Kanban. Peut-être que la friction principale est l'importation des données. Sans données de comportement réel, un tour v0.1 serait une guesslist. Attendre v0.2-v0.3 permet de construire un tour basé sur les vraies frictions identifiées par le tracking et les interviews.

**Product Manager** — *"Un tour minimal est nécessaire. Pas un walkthrough complet, mais un "Hello, voici la magie""*  
L'UX Researcher a raison sur le besoin, le UI Designer a raison sur le risque d'hypothèses. Le compromis : un tour **minimal** dès v0.1, pas un walkthrough de 15 étapes. 3 étapes maximum : (1) "Voici votre premier AO scoré", (2) "Voici le Kanban", (3) "Voici comment valider une proposition de l'agent". C'est un tour de *contextualisation*, pas d'apprentissage exhaustif. Le tour complet attendra v0.3.

**Frontend Senior** — *"Un tour = dépendances de librairie + maintenance. Tooltips natifs suffisent"*  
Implémenter un produit tour nécessite souvent une librairie dédiée (ex. Shepherd.js, Reactour) qui ajoute du poids au bundle et des dépendances à maintenir. Alternative : utiliser les tooltips natifs et les empty states bien conçus. Un empty state du Kanban qui dit "Votre premier AO apparaîtra ici. Importez-en un !" est un tour implicite, sans librairie. Un tour explicite peut attendre.

#### Débat

L'UX Researcher maintient que les empty states et tooltips ne remplacent pas un tour structuré : l'utilisateur doit comprendre le *lien* entre le scoring, le Kanban, et l'agent. Ce lien n'est pas évident dans des éléments dispersés. L'UI Designer argue que si ce lien n'est pas évident, c'est un problème de *design de l'interface*, pas de *manque de tour*. Un bon design est self-explanatory.

Le Product Manager propose le test du "first-time user" : demander à 3 personnes qui ne connaissent pas TAKA OS d'ouvrir l'app sans tour et de verbaliser leurs blocages. Si elles comprennent la valeur en 2 minutes, pas besoin de tour. Si elles sont perdues, un tour minimal est justifié. Le Frontend Senior accepte le compromis tour minimal si c'est implémenté avec des composants natifs (pas de librairie externe).

Le débat se résout sur la distinction entre "tour d'accueil" (bienvenue, voici l'app) et "tour de valeur" (voici la magie, voici pourquoi vous allez aimer). Le consensus est que le tour de valeur est nécessaire, mais doit être ultra-compact.

#### Décision

**Tour minimal de 3 étapes dès v0.1, apparaissant uniquement au premier lancement (first-time user). Étape 1 : contextualisation du scoring ("Votre premier AO a été analysé par l'agent" avec highlight de la carte scoring). Étape 2 : contextualisation du Kanban ("Vos AO sont organisés par étape" avec highlight d'une colonne). Étape 3 : contextualisation du HIL ("L'agent vous demande parfois de valider" avec highlight du bouton de notification). Pas de librairie externe : implémenté avec des overlays CSS natifs et du localStorage pour le flag "tour_vu". Tour complet basé sur les vraies frictions repoussé à v0.3.**

- **Responsable** : UI/UX Designer (conception des 3 étapes et des overlays) ; UX Researcher (rédaction des micro-copy)
- **Deadline** : v0.1 (MVP) pour le tour minimal ; v0.3 pour le tour complet
- **Justification** : L'utilisateur first-time doit comprendre la promesse de valeur agentic en 2 minutes, sans quoi l'activation chute. 3 étapes sont suffisantes pour la contextualisation sans être intrusives. L'absence de librairie externe réduit la dette technique.

#### Action

1. Rédiger les micro-copy des 3 étapes du tour minimal
2. Concevoir l'overlay CSS natif avec highlight (border pulsante, fond dimmed, tooltip positionné)
3. Implémenter le flag localStorage "taka_tour_v1_seen"
4. Prévoir le bouton "Revoir le tour" dans les paramètres utilisateur
5. Définir les critères de succès du tour (taux de complétion, taux d'activation post-tour)
6. Collecter les frictions v0.1-v0.2 pour alimenter le tour complet v0.3

---

### Q9 — La densité d'information sur les dashboards — minimalisme ou exhaustivité ?

#### Positions

**UI/UX Designer** — *"Minimalisme informationnel. Moins, c'est plus"*  
Les dashboards SaaS souffrent du syndrome de la "boîte à outils" : tout est affiché, rien n'est priorisé. L'utilisateur PME arrive sur un écran avec 15 widgets, 40 badges, 8 graphiques, et 3 sidebars. Résultat : il ne sait pas où regarder. L'interface doit adopter le principe du **progressive disclosure** appliqué à l'ensemble du dashboard. Un écran initial avec 3 éléments maximum. Les autres sont à un clic ou un scroll. Le minimalisme n'est pas l'absence d'information, c'est la **hiérarchisation de l'attention**.

**UX Researcher** — *"Les PME veulent tout voir. Elles détestent cliquer pour trouver"*  
Le persona PME est multitâche et pressé. Il n'a pas le temps de naviguer dans 3 niveaux de profondeur pour trouver une information. Il veut que l'information soit **visible** dès le premier écran. Les études sur les dashboards B2B montrent que les utilisateurs avancés préfèrent une densité élevée : ils scannent rapidement et extraient ce dont ils ont besoin. Le minimalisme est une prétention de designer pour des utilisateurs qui ne partagent pas ses valeurs esthétiques. La vraie question n'est pas "combien d'éléments ?" mais "sont-ils scannables ?".

**Product Manager** — *"Densité adaptable par persona et par niveau d'expertise"*  
Le collaborateur junior a besoin de minimalisme (il découvre). L'admin expérimenté a besoin de densité (il supervise). La solution n'est pas de choisir, mais de proposer un **mode compact / mode étendu**. Mode compact (par défaut) : widgets essentiels, espacement généreux, visualisation claire. Mode étendu (toggle) : plus de colonnes, plus de métriques, vue tableau dense. C'est le pattern que l'on trouve chez Notion (List / Board / Calendar) ou Jira (Compact / Comfortable).

**Frontend Senior** — *"La densité impacte le temps de rendu. Un dashboard dense = plus de DOM, plus de latence"*  
Un dashboard dense avec 40+ éléments interactifs génère un DOM lourd, des calculs de layout complexes, et des re-rendus fréquents. C'est particulièrement vrai si chaque widget fait des requêtes API indépendantes. La performance perçue (temps avant interaction possible) est un facteur UX majeur. Un dashboard minimaliste charge plus vite et paraît plus "fluide". La densité doit être une *option*, pas le défaut.

#### Débat

L'UI Designer et l'UX Researcher s'opposent sur la nature du persona. Le Designer pense que la PME est submergée ; le Researcher pense qu'elle est efficace quand tout est visible. Le Product Manager propose la variable cachée : le **niveau d'expertise**. Un utilisateur qui ouvre TAKA OS tous les jours préfère la densité. Un utilisateur qui l'ouvre une fois par semaine préfère le minimalisme. Mais comment détecter le niveau d'expertise ? Par la fréquence d'utilisation ? Par le rôle ?

Le Frontend Senior ajoute une dimension technique : la densité ne doit pas ralentir l'interface. Solution : lazy-loading des widgets non critiques, virtualisation des listes longues, et skeleton screens pendant le chargement. Le Designer accepte le mode compact/étendu à condition que le mode compact soit vraiment minimaliste (pas juste un mode étendu avec de l'espacement).

Le débat converge sur une règle : le dashboard par défaut montre ce que l'utilisateur fait **aujourd'hui**. Le reste est accessible via expansion ou navigation. C'est la règle du "aujourd'hui d'abord".

#### Décision

**Dashboard en mode Compact par défaut, avec toggle Mode Étendu. Mode Compact : 3 widgets maximum visibles (Kanban principal + 2 KPI cards), sidebar réduite, espacement généreux. Mode Étendu : widgets additionnels affichés, colonnes supplémentaires dans les tableaux, sidebar complète. Le toggle est persistant par utilisateur (sauvegardé en préférences). Pour le MVP, seul le Mode Compact est implémenté. Le Mode Étendu est une évolution v0.2. Les empty states sont conçus en mode Compact (jamais d'écran vide désorientant).**

- **Responsable** : UI/UX Designer (conception des deux modes) ; Frontend Senior (optimisation du rendu et lazy-loading)
- **Deadline** : v0.1 (MVP) pour le Mode Compact ; v0.2 pour le Mode Étendu
- **Justification** : Le Mode Compact réduit la charge cognitive initiale et le temps de chargement. Le Mode Étendu satisfait les utilisateurs avancés sans imposer la densité aux novices. La persistance du mode respecte les préférences individuelles.

#### Action

1. Concevoir le Mode Compact du dashboard Soumissionnaire (3 zones maximum)
2. Concevoir le Mode Compact du dashboard Acheteur
3. Définir les widgets additionnels du Mode Étendu (roadmap v0.2)
4. Implémenter le toggle Compact/Étendu avec persistance utilisateur
5. Optimiser le rendu : lazy-loading des widgets, virtualisation des listes > 50 éléments
6. Tester le temps de chargement du dashboard Compact (objectif : < 2s TTI)

---

### Q10 — Le système de rôles et permissions — granularité ou simplicité ?

#### Positions

**Product Manager** — *"5 rôles, c'est déjà complexe. Ne pas ajouter de sous-rôles"*  
Le modèle de rôles de TAKA OS définit 5 rôles : Super Admin (Éditeur), Admin Soumissionnaire, Collaborateur Soumissionnaire, Admin Acheteur, Collaborateur Acheteur. C'est déjà une granularité significative pour un MVP. Ajouter des sous-rôles (ex : "Collaborateur Junior", "Collaborateur Senior", "Admin avec droit de facturation") crée une matrice de permissions complexe à maintenir, à tester, et à expliquer. Les PME n'ont pas de département IAM. Elles veulent assigner un rôle et oublier. Gardons 5 rôles stricts pour le MVP.

**UX Researcher** — *"La réalité des PME est plus nuancée. Un collaborateur peut être 'lecteur' sur une BL et 'éditeur' sur une autre"*  
Les PME ont des structures organiques, pas bureaucratiques. Une même personne peut être "responsable" sur les AO BTP (créer, modifier, soumettre) et "observateur" sur les AO Informatique (voir, commenter). Le modèle binaire Collaborateur/Admin est trop rigide. Sans granularité par BL, l'admin est obligé de donner des droits excessifs ou de créer des comptes multiples. C'est une friction majeure qui pousse les utilisateurs à partager des credentials (security risk).

**UI/UX Designer** — *"Simplifier l'interface de gestion des rôles, pas les rôles eux-mêmes"*  
La complexité ne vient pas des rôles, mais de l'interface de gestion. Une matrice de permissions type IAM enterprise est indigeste. Proposer une interface visuelle : liste des utilisateurs, drag-and-drop des permissions sur les BL, visualisation claire ("Marie : BTP = Éditeur, Info = Lecteur"). La complexité backend est masquée par la simplicité frontend. C'est le pattern "puissance cachée, simplicité visible".

**Frontend Senior** — *"Chaque niveau de granularité = complexité auth + tests + edge cases"*  
Passer de 5 rôles fixes à un système de permissions par BL et par action, c'est changer l'architecture de l'autorisation. Cela impacte : le middleware d'authentification, les guards de routes, les filtres API, les validations côté serveur, et les tests de non-régression. Pour le MVP, un système de rôles simple est plus sûr. La granularité peut être ajoutée à v0.2 avec une migration de données planifiée.

#### Débat

Le Product Manager et l'UX Researcher s'affrontent sur la nature des PME cibles. Le PM pense que les PME sont simples ; le Researcher pense qu'elles sont organiques. L'UI Designer apporte une solution d'interface, mais le Frontend Senior rappelle que l'interface simple ne résout pas la complexité backend.

Le débat se résout sur une question : est-ce que le risque de "droits excessifs" est un problème réel pour les PME de 20 personnes ? Dans une petite structure, la confiance est élevée et la segmentation des droits est moins critique que dans une enterprise. Le consensus est que la granularité par BL est un **besoin réel** mais pas un **besoin MVP**. Le MVP peut vivre avec 5 rôles fixes. La granularité est une évolution v0.2.

Cependant, l'UX Researcher obtient une concession : le modèle de données doit être conçu dès le MVP pour accepter la granularité future, sans l'implémenter. C'est une "porte ouverte" pour v0.2.

#### Décision

**5 rôles fixes pour le MVP, avec une architecture de permissions ouverte à la granularité future. Les rôles sont : Super Admin (Éditeur), Admin Soumissionnaire, Collaborateur Soumissionnaire, Admin Acheteur, Collaborateur Acheteur. Pas de sous-rôles, pas de permissions par BL. L'interface de gestion des utilisateurs est une liste simple avec rôle + BL assignée (mono-BL pour le MVP). L'architecture backend prévoit déjà une table de permissions fine (action × ressource × utilisateur) non exploitée en v0.1.**

- **Responsable** : Product Manager (définition des 5 rôles et de leurs permissions) ; Frontend Senior (conception de l'architecture auth extensible)
- **Deadline** : v0.1 (MVP) pour les 5 rôles ; v0.2 pour la granularité par BL
- **Justification** : La simplicité de gestion des rôles est un facteur d'adoption pour les PME. L'architecture extensible garantit que la granularité pourra être ajoutée sans refactoring majeur.

#### Action

1. Définir la matrice permissions × rôles pour les 5 rôles (CRUD sur AO, scoring, HIL, facturation, etc.)
2. Concevoir l'écran de gestion des utilisateurs (liste, ajout, modification de rôle, BL assignée)
3. Implémenter l'architecture auth avec RBAC extensible (table roles, permissions, user_permissions)
4. Documenter la roadmap granularité pour v0.2 (permissions par BL, par action, par AO)
5. Tester les scénarios de sécurité (tentative d'accès non autorisé, escalation de privilèges)

---

### Q11 — La recherche cross-AO — comment l'architecturer ?

#### Positions

**UX Researcher** — *"La recherche est le cœur du produit. Les utilisateurs pensent en mots-clés, pas en filtres"*  
Quand un utilisateur cherche un AO, il pense : "l'école de Marseille", "le marché de janvier", "le DCE qui ferme vendredi". Il ne pense pas : "CPV 45212200 + zone = PACA + statut = En Cours". La recherche doit être **sémantique** et **full-text** sur l'ensemble des champs (titre, description, CPV, lieu, mots-clés extraits par l'agent). La barre de recherche globale est le point d'entrée privilégié. Les filtres avancés sont un complément, pas un substitut.

**Product Manager** — *"La recherche sémantique est un produit à part entière. Commençons par la recherche filtrée"*  
La recherche full-text sémantique sur des documents d'AO (souvent des PDF de 200+ pages) est un investissement considérable. Il faut : indexation Elasticsearch/OpenSearch, extraction de texte, OCR si scan, ranking pertinence, highlighting. C'est un projet de v0.3, pas de v0.1. Pour le MVP, proposer une recherche par filtres structurés (CPV, zone, statut, date, montant) + recherche texte simple sur le titre et le résumé agentic. C'est 80% de la valeur pour 20% de l'effort.

**UI/UX Designer** — *"La barre de recherche globale + chips de filtres rapides"*  
Proposer une barre de recherche unique en top bar, avec autocomplétion et suggestions. À côté, des "chips" de filtres rapides ("Avec deadline cette semaine", "MAYBE scoring", "Non assigné") qui appliquent des filtres prédéfinis d'un clic. C'est le pattern de Gmail (recherche + chips) ou de GitHub (search + qualifiers). La recherche texte et les filtres cohabitent sans s'opposer.

**Frontend Senior** — *"La recherche globale doit être performante. Debounce + index côté client si possible"*  
Une recherche qui envoie une requête API à chaque caractère tapé est lente et coûteuse. Implémenter un debounce (attente 300ms après la dernière frappe) et une recherche côté client si le nombre d'AO est < 100 (ce qui sera le cas pour la plupart des PME au début). Pour les grands volumes, passer à une recherche serveur avec indexation. C'est une stratégie progressive.

#### Débat

L'UX Researcher et le Product Manager s'opposent sur l'ampleur de la recherche. Le Researcher pense que la recherche est le cœur de l'expérience ; le PM pense que c'est un investissement à étaler. L'UI Designer propose une interface qui s'adapte à l'évolution technique : même barre de recherche, backend qui s'améliore.

Le Frontend Senior souligne une réalité technique : pour la plupart des utilisateurs MVP (PME avec < 50 AO actifs), une recherche côté client sur un tableau en mémoire est instantanée et ne nécessite pas d'indexation complexe. C'est un argument fort pour différer la recherche serveur avancée.

Le débat se résout sur la distinction entre "recherche de découverte" (trouver un AO dans une base large) et "recherche de vérification" (retrouver un AO connu). Les utilisateurs MVP font surtout de la vérification. La découverte full-text peut attendre.

#### Décision

**Recherche par barre globale avec autocomplétion et filtres rapides (chips) pour le MVP. La recherche couvre : titre de l'AO, résumé agentic, CPV, zone, statut Kanban. Implémentation côté client pour les tenants avec < 100 AO, recherche serveur avec indexation pour les tenants plus larges (v0.2). Pas de recherche sémantique dans les documents PDF pour le MVP (v0.3). Les filtres avancés (date, montant, scoring) sont disponibles dans un panneau latéral dépliable.**

- **Responsable** : UX Researcher (définition des comportements de recherche et des filtres rapides) ; Frontend Senior (implémentation côté client + debounce)
- **Deadline** : v0.1 (MVP) pour la recherche globale + filtres rapides ; v0.2 pour la recherche serveur
- **Justification** : La recherche est un outil quotidien. Une barre globale simple avec autocomplétion couvre 80% des besoins. L'implémentation côté client est instantanée pour les petits volumes. La recherche documentaire est un investissement v0.3 justifié par les retours utilisateurs.

#### Action

1. Concevoir la barre de recherche globale (position, style, autocomplétion, placeholder)
2. Définir les 5-7 filtres rapides (chips) les plus pertinents
3. Implémenter la recherche côté client avec debounce et highlighting des résultats
4. Concevoir le panneau de filtres avancés (date range, montant, scoring, statut)
5. Préparer l'architecture pour la recherche serveur v0.2 (API, indexation)
6. Tester la pertinence de l'autocomplétion avec 10 requêtes types

---

### Q12 — Les états vides et messages d'erreur — ton et stratégie

#### Positions

**UX Researcher** — *"Les états vides sont des opportunités de conversion, pas des punitions"*  
Un état vide (Kanban sans AO, dashboard sans données, scorecard sans historique) est le moment le plus critique de l'expérience. Si l'utilisateur voit "Aucune donnée", il interprète cela comme un échec du produit. Les états vides doivent être **contextualités**, **actionnables**, et **encouragents**. Exemple : "Votre Kanban est vide — importez votre premier AO et l'agent le scorera en 30 secondes" avec un CTA clair. Le ton doit être chaleureux et orienté solution, pas technique ni désolé.

**UI/UX Designer** — *"Consistance visuelle des états vides. Un pattern, pas 12 illustrations différentes"*  
Chaque état vide ne mérite pas une illustration custom. Proposer un pattern unique : illustration légère (Lottie ou SVG), titre explicite, description contextualisée, CTA principal, lien secondaire ("En savoir plus"). L'illustration est la même (persona neutre, ton amical), seul le texte change. C'est plus rapide à implémenter, plus cohérent, et évite le "design fatigue" de 12 illustrations différentes.

**Product Manager** — *"Les états vides doivent orienter vers l'activation. Chaque empty state = un funnel"*  
Un état vide n'est pas juste un message, c'est un **point de conversion**. Kanban vide = CTA "Importer un AO". ScoreCard vide = CTA "Configurer le scoring". Dashboard vide = CTA "Inviter un collaborateur". Chaque état vide doit avoir un objectif métier clair et un tracking associé (taux de conversion de l'état vide vers l'action proposée). Si un état vide a un taux de conversion < 10%, il faut le redesiner.

**Frontend Senior** — *"Les erreurs techniques doivent être humaines mais informatives"*  
Quand l'agent échoue à scorer un AO, quand l'import PDF échoue, quand l'API est indisponible, l'utilisateur ne doit pas voir "Error 500" ou "NullPointerException". Il doit voir un message explicite : "L'agent n'a pas pu analyser ce document. Causes possibles : fichier trop volumineux, format non supporté, ou document scanné non OCRisé. Solutions : réessayer avec un PDF plus léger, ou contacter le support." Le message d'erreur doit contenir : le problème en français, les causes probables, les actions possibles, et un bouton d'escalade (support).

#### Débat

L'UX Researcher et le Product Manager sont alignés sur le principe : les états vides sont des opportunités. Le Designer apporte la contrainte de cohérence visuelle. Le Frontend Senior élargit le débat aux erreurs techniques.

Le débat s'intensifie sur le ton : faut-il être "friendly" ("Oups, rien ici !") ou "professionnel" ("Aucun Appel d'Offres n'a encore été importé") ? L'UX Researcher penche vers le professionnel chaleureux : pas de "Oups" qui infantilise un chef d'entreprise. Le Product Manager appuie : le ton doit être **confiant** et **compétent**, car TAKA OS se positionne comme un expert métier, pas comme une app de social media.

Le Frontend Senior soulève un point technique : les messages d'erreur doivent être traduisibles (i18n) et paramétrables. Si l'agent échoue pour une raison spécifique, le message doit refléter cette raison, pas un générique "Erreur agent". Cela nécessite un système de codes d'erreur agentic.

#### Décision

**Système d'états vides unifié avec pattern visuel cohérent : illustration SVG légère + titre explicite + description actionable + CTA principal + lien secondaire optionnel. Ton : professionnel chaleureux (ni infantilisant ni bureaucratique). Chaque état vide a un objectif d'activation mesuré. Système de messages d'erreur structuré : problème + causes probables + actions possibles + bouton support. Codes d'erreur agentic pour les échecs de scoring/import.**

- **Responsable** : UX Researcher (rédaction des copy d'états vides et d'erreurs) ; UI/UX Designer (conception du pattern visuel unifié)
- **Deadline** : v0.1 (MVP)
- **Justification** : Les états vides sont des moments de vérité de l'expérience. Un état vide mal conçu = churn. Un état vide bien conçu = activation. Les erreurs agentic doivent être transparentes pour maintenir la confiance.

#### Action

1. Rédiger le catalogue des états vides (Kanban, Dashboard, ScoreCard, Notifications, HIL, Recherche)
2. Concevoir le pattern visuel unifié (illustration, layout, typographie)
3. Définir les objectifs d'activation par état vide et les KPIs de conversion
4. Rédiger le catalogue des messages d'erreur agentic (codes, formulations, actions)
5. Implémenter le composant EmptyState réutilisable avec props (titre, description, CTA, image)
6. Implémenter le composant ErrorState réutilisable avec props (erreur, causes, actions, code)
7. Traduire l'ensemble en français et préparer la structure i18n

---

## 3. Frictions Utilisateur Identifiées

Au cours du débat, les quatre agents ont identifié des frictions transverses qui dépassent le cadre des questions individuelles. Ces frictions sont des hypothèses à valider avec des utilisateurs réels, mais elles orientent déjà les décisions de conception.

### Friction F1 — "L'anxiété de la deadline"
Les utilisateurs vivent dans la peur de manquer une deadline d'AO. Toute interface qui ne montre pas clairement "combien de temps il me reste" crée de l'anxiété. Le Kanban seul ne résout pas cette friction. Les indicateurs temporels doivent être omniprésents.

### Friction F2 — "La méfiance envers l'agent"
Un utilisateur ne fait pas confiance à un score sans comprendre d'où il vient. La transparence du scoring est non négociable, mais elle doit être graduée (progressive disclosure). Un score opaque est rejeté ; un score trop détaillé est ignoré.

### Friction F3 — "L'interruption par l'agent"
L'agent qui réclame constamment des validations HIL est perçu comme un collègue importun, pas comme un assistant. La distinction HIL critique / HIL informatif est essentielle pour éviter la fatigue de validation.

### Friction F4 — "La démultiplication des outils"
Les PME utilisent déjà des outils (Excel, email, Drive, Trello). TAKA OS ne doit pas ajouter un 5ème outil, mais remplacer 3 d'entre eux. L'onboarding doit clairement articuler : "TAKA OS remplace vos spreadsheets et vos listes d'AO par email."

### Friction F5 — "La peur de la conformité"
Les acheteurs publics craignent que l'agentic ne crée des biais ou des non-conformités. L'interface doit rassurer sur la traçabilité et la conformité (logs, explicabilité, audit trail visible).

### Friction F6 — "La courbe d'apprentissage du scoring"
Le scoring 5D est un concept nouveau. Sans contextualisation, l'utilisateur ne sait pas comment interpréter un "MAYBE". Le tour minimal v0.1 doit expliquer le scoring en 30 secondes.

### Friction F7 — "La surcharge du dashboard"
Un dashboard avec trop de widgets crée de la paralysie analytique. L'utilisateur ne sait pas où commencer. Le Mode Compact est une réponse directe à cette friction.

### Friction F8 — "L'email comme spam"
Les utilisateurs B2B sont saturés d'emails. Toute notification email mal calibrée sera ignorée ou conduira à la désinscription. Le ton et la fréquence des emails sont aussi importants que leur contenu.

---

## 4. Décisions UX/UI Validées

| ID | Décision | Portée | Responsable | Deadline |
|---|---|---|---|---|
| D1 | Kanban par défaut + indicateurs temporels intégrés + toggle Vue Planning | Dashboards | UI/UX Designer | v0.1 Kanban ; v0.2 Planning |
| D2 | ScoreCard 2 niveaux : verdict condensé (N1) + barres horizontales dépliables (N2) | Scoring | UX Researcher + UI Designer | v0.1 N1 ; v0.2 N2 |
| D3 | Onboarding obligatoire optimisé : defaults SIRET + templates + scoring simulé étape 3 | Onboarding | Product Manager + UX Researcher | v0.1 |
| D4 | Sélecteur BL top bar pour admins uniquement ; filtre BL local pour collaborateurs multi-BL | Navigation | UI/UX Designer | v0.1 |
| D5 | HIL différencié : modal semi-bloquante (critique) + sidebar asynchrone (informatif) + expiration 24h | Agentic | Product Manager + UX Researcher | v0.1 modal ; v0.2 sidebar |
| D6 | Dashboard Éditeur : tableau de données + 3 KPIs cards. Widgets graphiques repoussés | Super Admin | Product Manager + UI Designer | v0.1 |
| D7 | Notifications hybrides : in-app (tout) + email digest (quotidien) + email immédiat (critique) | Notifications | UX Researcher + Product Manager | v0.1 |
| D8 | Tour minimal 3 étapes dès v0.1 ; tour complet repoussé à v0.3 | Onboarding | UI Designer + UX Researcher | v0.1 |
| D9 | Dashboard Mode Compact par défaut ; Mode Étendu toggle persistant | Dashboards | UI/UX Designer + Frontend Senior | v0.1 Compact ; v0.2 Étendu |
| D10 | 5 rôles fixes MVP ; architecture auth extensible pour granularité v0.2 | Permissions | Product Manager + Frontend Senior | v0.1 |
| D11 | Recherche globale + chips filtres rapides ; recherche serveur v0.2 ; recherche PDF v0.3 | Recherche | UX Researcher + Frontend Senior | v0.1 |
| D12 | Pattern états vides unifié + messages d'erreur structurés (problème + causes + actions) | UX globale | UX Researcher + UI Designer | v0.1 |

---

## 5. Plan d'Action & Suivi

### Actions immédiates (MVP — v0.1)

| # | Action | Responsable | Livrable | Deadline |
|---|---|---|---|---|
| A1 | Définir la taxonomie des 5 dimensions du ScoreCard et leurs labels utilisateur | Product Manager | Document de spécification | Sprint 1 |
| A2 | Concevoir les micro-interactions Kanban (drag, drop, animations) | UI/UX Designer | Prototype Figma | Sprint 1 |
| A3 | Rédiger le corpus des explications agentic condensées (2 phrases max) | UX Researcher | Document de copy | Sprint 1 |
| A4 | Intégrer l'auto-remplissage SIRET et définir les 3 templates de profil | Product Manager | Spéc API + templates | Sprint 1 |
| A5 | Concevoir le tour minimal 3 étapes (overlays CSS) | UI/UX Designer | Maquettes + prototype | Sprint 2 |
| A6 | Implémenter le composant EmptyState et ErrorState réutilisables | Frontend Senior | Composants React + Storybook | Sprint 2 |
| A7 | Concevoir le centre de notifications in-app (cloche, dropdown, badge) | UI/UX Designer | Maquettes | Sprint 2 |
| A8 | Rédiger les templates email (digest et immédiat) | UX Researcher + Product Manager | Copy + wireframes email | Sprint 2 |
| A9 | Concevoir le tableau de données Éditeur avec 3 KPIs cards | UI/UX Designer | Maquettes | Sprint 2 |
| A10 | Définir la matrice permissions × rôles (5 rôles) | Product Manager | Matrice de permissions | Sprint 1 |
| A11 | Concevoir la barre de recherche globale + autocomplétion + chips filtres | UI/UX Designer | Maquettes + interaction | Sprint 2 |
| A12 | Implémenter le Mode Compact du dashboard Soumissionnaire | Frontend Senior | Composant dashboard | Sprint 2-3 |
| A13 | Implémenter la modal HIL critique (layout, CTA, avertissement) | Frontend Senior | Composant modal | Sprint 2 |
| A14 | Concevoir le filtre BL local intégré Kanban (chips) | UI/UX Designer | Maquettes | Sprint 2 |
| A15 | Implémenter le tracking complet du funnel onboarding | Frontend Senior | Events analytics | Sprint 2 |

### Actions v0.2 (Post-MVP)

| # | Action | Responsable | Deadline |
|---|---|---|---|
| B1 | Vue Planning (timeline simplifiée) avec toggle | UI/UX Designer | v0.2 |
| B2 | ScoreCard niveau 2 dépliable (barres horizontales 5D) | Frontend Senior | v0.2 |
| B3 | Sidebar HIL asynchrone avec notifications persistantes | UI/UX Designer + Frontend Senior | v0.2 |
| B4 | Mode Étendu du dashboard (widgets additionnels) | UI/UX Designer | v0.2 |
| B5 | Granularité des permissions par BL | Product Manager + Frontend Senior | v0.2 |
| B6 | Recherche serveur avec indexation pour grands volumes | Frontend Senior | v0.2 |
| B7 | Personnalisation des préférences de notification par utilisateur | UX Researcher + Frontend Senior | v0.2 |

### Actions v0.3 (Évolution)

| # | Action | Responsable | Deadline |
|---|---|---|---|
| C1 | Tour complet basé sur les vraies frictions utilisateurs | UX Researcher + UI Designer | v0.3 |
| C2 | Recherche sémantique dans les documents PDF (OCR + indexation) | Product Manager + Frontend Senior | v0.3 |
| C3 | Web Push API pour notifications urgentes | Frontend Senior | v0.3 |
| C4 | Dashboard Éditeur avec widgets graphiques (courbes, camemberts) | UI/UX Designer | v0.3 |

---

## 6. Prochaines Étapes

1. **Revue de conception** : Présentation des maquettes v0.1 au groupe Technique & Architecture pour validation faisabilité (échéance : fin Sprint 1)
2. **Tests utilisateurs** : 5 entretiens avec des PME soumissionnaires pour valider les hypothèses de frictions F1-F8 (échéance : mi-Sprint 2)
3. **Sprint de prototypage** : Construction d'un prototype clickable des 5 dashboards + Kanban + ScoreCard pour démo interne (échéance : fin Sprint 2)
4. **Revue des analytics** : Mise en place du plan de tracking (funnel onboarding, conversion états vides, taux de complétion HIL) avant le début du développement v0.1 (échéance : Sprint 1)
5. **Session de validation copy** : Relecture collective de l'ensemble des micro-copy, messages d'erreur, et explications agentic pour alignement ton et cohérence (échéance : Sprint 2)

---

## Annexe — Glossaire des termes produit utilisés

| Terme | Définition |
|---|---|
| **AO** | Appel d'Offres — consultation publique ou privée pour l'attribution d'un marché |
| **BL** | Business Line — segment d'activité métier (ex : BTP, Informatique, Services) |
| **CPV** | Common Procurement Vocabulary — nomenclature européenne des marchés publics |
| **HIL** | Human-in-the-Loop — intervention humaine requise dans un workflow agentic |
| **ScoreCard 5D** | Évaluation d'un AO sur 5 dimensions configurables par l'admin |
| **Tenant** | Instance client isolée dans l'architecture multi-tenant de TAKA OS |
| **Wizard** | Assistant pas à pas pour l'onboarding ou la configuration |
| **Vue Planning** | Affichage temporel des AO (type timeline / roadmap / Gantt simplifié) |
| **Mode Compact** | Vue dashboard réduite aux éléments essentiels |
| **Mode Étendu** | Vue dashboard dense avec tous les widgets et métriques |
| **Progressive Disclosure** | Principe d'affichage progressif de la complexité selon le besoin |
| **Aha! Moment** | Instant où l'utilisateur perçoit la valeur du produit |

---

*Document produit par le Groupe Produit & Expérience Utilisateur — Réunion KIMI-TAKA-SWARM*  
*Orienté utilisateur. Pensé en parcours. Critique sur l'expérience.*

---

## Annexe A — Analyse Détaillée des Parcours Utilisateurs

### Parcours P1 — Première Connexion Soumissionnaire (PME)

**Contexte** : Jean-Pierre, 52 ans, dirige une PME de BTP de 18 salariés. Il a entendu parler de TAKA OS via un forum des entreprises. Il s'inscrit un soir à 21h, entre deux chantiers.

**Étape 1 — Landing & Inscription** (30 secondes)  
Jean-Pierre arrive sur la page d'accueil. Il veut comprendre immédiatement ce que fait TAKA OS. La promesse doit être visible en moins de 3 secondes : "TAKA OS analyse vos Appels d'Offres et vous dit lesquels méritent d'être traités." Pas de jargon agentic. Pas de "plateforme SaaS innovante". Un bénéfice concret, chiffré si possible ("Gagnez 5 heures par semaine sur la sélection des AO").

**Étape 2 — Onboarding Optimisé** (3 minutes)  
Jean-Pierre saisit son SIRET. TAKA détecte automatiquement : entreprise de BTP, taille intermédiaire, zone d'activité à définir. Le template "BTP régional" est proposé. Il clique, et 70% de son profil est rempli. Il n'a plus qu'à ajuster : zones géographiques (cocher une carte), types de marchés (travaux, maintenance, Maîtrise d'Oeuvre), et seuil financier minimum (300k€). À l'étape 3, il voit un AO exemple scoré : "Construction collège Marseille — Score 78% GO — Votre profil BTP correspond à 92%." C'est son Aha! moment.

**Étape 3 — Premier Kanban** (1 minute)  
Le Kanban s'affiche. 3 colonnes visibles : "Nouveaux AO", "En Analyse", "À Soumettre". Jean-Pierre importe son premier AO réel (upload PDF). L'agent traite. 45 secondes plus tard, la carte apparaît dans "Nouveaux AO" avec un badge "MAYBE 62%" et un indicateur "Deadline : 12 jours". Il déplace la carte vers "En Analyse" d'un glisser-déposer fluide. L'agent génère un résumé structuré. Jean-Pierre comprend immédiatement la métaphore.

**Étape 4 — Première Validation HIL** (30 secondes)  
L'agent propose une classification CPV. Notification sidebar : "L'agent suggère CPV 45212200 — Travaux de construction. Valider ou modifier ?" Jean-Pierre clique "Valider" depuis la sidebar, sans interruption. L'agent continue son analyse.

**Friction identifiée dans ce parcours** : Si le PDF est un scan non OCRisé, l'agent échoue. L'erreur doit être humaine et orientée solution : "Ce document semble être une image scannée. Pour l'analyser, assurez-vous que le PDF contient du texte sélectionnable. Astuce : utilisez un scan avec OCR ou demandez le DCE en format natif à l'acheteur."

### Parcours P2 — Usage Quotidien Collaborateur Soumissionnaire

**Contexte** : Marie, 34 ans, assistante de direction, traitement des AO deux fois par semaine. Elle ouvre TAKA OS le mardi matin.

**Étape 1 — Vue d'ensemble immédiate** (10 secondes)  
Marie ouvre l'app. Le dashboard Mode Compact montre : (1) un compteur "3 AO avec deadline cette semaine", (2) un badge "1 HIL en attente", (3) le Kanban positionné sur la colonne "En Analyse". Elle sait immédiatement ses priorités.

**Étape 2 — Traitement du HIL** (1 minute)  
Elle clique sur la notification HIL. L'agent demande validation d'un résumé pour l'AO "Rénovation Mairie Toulon". Elle lit le résumé, apporte une modification mineure, valide. L'agent génère la suite.

**Étape 3 — Mise à jour du Kanban** (30 secondes)  
Marie déplace deux AO d'une colonne à l'autre. L'agent propose automatiquement des actions contextuelles : "Générer le mémoire technique ?", "Programmer un rappel 48h avant deadline ?" Elle accepte le rappel pour l'un des AO.

**Friction identifiée** : Marie a 2 Business Lines (BTP et services aux collectivités). Sans filtre BL visible, ses AO sont mélangés. Le badge BL sur chaque carte lui permet de différencier visuellement. Le filtre BL local lui permet de se concentrer sur le BTP le matin, les services l'après-midi.

### Parcours P3 — Usage Admin Acheteur Public

**Contexte** : Thomas, 45 ans, responsable des marchés dans une collectivité territoriale. Il utilise TAKA OS pour suivre les consultations en cours et évaluer les offres reçues.

**Étape 1 — Dashboard Acheteur** (10 secondes)  
Thomas voit : consultations ouvertes, offres reçues par consultation, timeline des prochaines échéances (ouverture des plis, commissions d'évaluation). Le ton est différent du soumissionnaire : moins de "scoring", plus de "suivi de procédure".

**Étape 2 — Évaluation des Offres** (5 minutes)  
Thomas ouvre une consultation. Les offres reçues sont listées avec des indicateurs de conformité (offre complète / incomplète), scoring qualitatif si critères définis, et bouton "Ouvrir le dossier". L'agent a pré-analysé chaque offre : conformité formelle, éléments manquants, comparaison avec le DCE.

**Étape 3 — HIL Critique** (30 secondes)  
L'agent détecte une anomalie dans une offre : "L'offre A semble ne pas inclure le DPGF exigé. Confirmer l'irrégularité ?" C'est un HIL critique. Modal semi-bloquante car cela impacte la procédure. Thomas confirme. L'agent documente l'irrégularité dans le rapport de commission.

**Friction identifiée** : Thomas est soumis à des contraintes légales strictes (code des marchés publics). Toute suggestion de l'agent doit être traçable et vérifiable. L'interface doit montrer clairement : "Suggestion agentic — À vérifier par le responsable".

### Parcours P4 — Super Admin Éditeur (Support Client)

**Contexte** : Le fondateur de TAKA OS, le week-end, vérifie que les nouveaux tenants vont bien.

**Étape 1 — Vue Éditeur** (5 secondes)  
Il ouvre le dashboard Éditeur. 3 KPIs cards : "42 tenants actifs", "1 240 AO traités ce mois", "3 tickets support ouverts". Le tableau de données montre la liste des tenants triée par dernière activité.

**Étape 2 — Diagnostic Rapide** (1 minute)  
Il remarque un tenant sans activité depuis 7 jours. Action rapide : "Voir détail". Il consulte : nombre d'utilisateurs (1), dernier AO importé (aucun), onboarding complété (non). Diagnostic probable : l'utilisateur n'a pas terminé l'onboarding. Il clique "Contacter" et envoie un email personnalisé depuis l'interface.

**Friction identifiée** : Le super admin n'a pas besoin de graphiques, mais de données actionnables. Le tableau brut est plus rapide que 15 widgets. Les actions rapides inline économisent des clics.

---

## Annexe B — Principes de Conception UX Validés

Au fil du débat, le groupe a validé un ensemble de principes transverses qui guideront l'ensemble des décisions de conception futures.

### Principe 1 — "La deadline est reine"
Toute information temporelle (deadline, échéance, retard) doit être visible sans interaction. Les indicateurs temporels sont omniprésents : badges colorés, compteurs, alertes. Un utilisateur ne doit jamais avoir à cliquer pour savoir s'il est en retard.

### Principe 2 — "La valeur avant la complexité"
L'utilisateur perçoit la valeur de TAKA OS (le scoring, le gain de temps) avant d'avoir à comprendre sa complexité (le 5D, l'agentic, le workflow). L'onboarding est conçu pour créer un Aha! moment dès l'étape 3.

### Principe 3 — "Progressive Disclosure Universelle"
Aucune interface n'impose sa complexité. Tout élément complexe est masqué par défaut et révélable sur demande. Cela s'applique au ScoreCard, aux filtres avancés, aux détails d'un AO, et aux paramètres.

### Principe 4 — "Le contexte avant le contrôle"
L'interface s'adapte au contexte de l'utilisateur (rôle, BL, heure, niveau d'expertise) plutôt que de forcer l'utilisateur à configurer manuellement. Le Mode Compact/Étendu, le filtre BL adaptatif, et les defaults intelligents illustrent ce principe.

### Principe 5 — "L'agent est un collaborateur, pas un supérieur"
L'agent agentic ne commande pas, ne réprimande pas, ne patronise pas. Il propose, suggère, et attend la validation. Les messages agentic sont rédigés en ton collaboratif : "Je propose...", "J'ai remarqué...", "Que pensez-vous de...". Jamais "Erreur", "Échec", "Non conforme" sans explication constructive.

### Principe 6 — "La transparence graduée"
La confiance dans l'agent se construit par la transparence, mais cette transparence doit être accessible sans être imposée. Le verdict est immédiat ; le détail est un clic away.

### Principe 7 — "L'action est à un clic"
Tout état vide, toute notification, toute alerte doit contenir une action immédiate. Pas de messages passifs. Un état vide sans CTA est une impasse UX.

### Principe 8 — "La performance est une fonction UX"
Un dashboard qui met 5 secondes à charger est perçu comme cassé, même si les données sont correctes. Le temps d'interaction (TTI) est un critère de qualité au même titre que l'esthétique. Le lazy-loading, le debounce, et la recherche côté client sont des choix UX, pas seulement des choix techniques.

---

## Annexe C — Matrice des Frictions × Solutions

| Friction | Impact utilisateur | Solution décidée | Où implémenter |
|---|---|---|---|
| F1 — Anxiété deadline | Stress, manque de visibilité | Indicateurs temporels omniprésents (badge couleur, jours restants) | Kanban, cartes AO, dashboard |
| F2 — Méfiance scoring | Rejet du verdict agentic | Progressive disclosure : verdict condensé + détail dépliable | ScoreCard, carte AO |
| F3 — Interruption agent | Fatigue de validation | HIL différencié : modal critique vs sidebar informatif + expiration | Tout le workflow agentic |
| F4 — Démuliplication outils | Adoption lente | Positionnement clair : "TAKA remplace vos spreadsheets" | Onboarding, landing page |
| F5 — Peur conformité | Méfiance acheteur public | Traçabilité visible : logs, badges "À vérifier", audit trail | Interface acheteur, HIL |
| F6 — Courbe apprentissage scoring | Non-compréhension du score | Tour minimal étape 2, explications agentic 2 phrases | Onboarding, ScoreCard |
| F7 — Surcharge dashboard | Paralysie analytique | Mode Compact par défaut, 3 widgets max | Dashboards |
| F8 — Email spam | Désactivation des notifications | Système hybride : in-app principal, email digest, email immédiat critique | Centre de notifications |
| F9 — Navigation BL confuse | Désorientation multi-métiers | Badge BL sur cartes + filtre local Kanban | Kanban, top bar |
| F10 — Onboarding abandonné | Activation faible | Defaults SIRET + templates + scoring simulé étape 3 | Wizard onboarding |
| F11 — Rôles trop rigides | Partage de credentials | Architecture extensible, 5 rôles MVP, granularité v0.2 | Gestion utilisateurs |
| F12 — Erreurs techniques opaques | Perte de confiance | Messages structurés : problème + causes + actions + support | Tous les états d'erreur |

---

## Annexe D — Récapitulatif des Responsabilités par Agent

### Frontend Senior
- Implémentation des composants UI (Kanban, ScoreCard, Modal HIL, EmptyState, ErrorState)
- Optimisation performance (lazy-loading, debounce, virtualisation, recherche côté client)
- Architecture auth extensible (RBAC, permissions futures)
- Tracking analytics (funnel onboarding, événements clés)
- Mode Compact/Étendu avec persistance

### UI/UX Designer
- Maquettes et prototypes de tous les écrans MVP
- Système de design (typographie, couleurs, espacement, composants)
- Micro-interactions (drag-drop, animations, transitions)
- Pattern états vides et erreurs unifiés
- Tour minimal 3 étapes (overlays CSS)
- Sélecteur BL et filtre BL local

### Product Manager
- Définition des 5 dimensions ScoreCard et taxonomie HIL
- Spécification des 5 rôles et matrice permissions
- Templates de profil et defaults SIRET
- Dashboard Éditeur (colonnes, filtres, actions rapides)
- Templates email (digest et immédiat)
- Priorisation fonctionnelle et arbitrage final

### UX Researcher
- Corpus des explications agentic condensées
- Rédaction des micro-copy, empty states, messages d'erreur
- Conception du centre de notifications et de la sidebar HIL
- Tests utilisateurs (5 entretiens PME)
- Validation ton et cohérence linguistique
- Définition comportements de recherche et filtres rapides

---

## Annexe E — Hypothèses à Valider avec des Utilisateurs Réels

Avant et pendant le développement v0.1, les hypothèses suivantes doivent être testées avec des utilisateurs du monde réel (PME soumissionnaires et acheteurs publics) :

**H1 — Le Kanban est familièrement compris**  
Hypothèse : Les utilisateurs comprennent immédiatement la métaphore Kanban sans explication.  
Test : Observer 5 utilisateurs first-time déplacer une carte sans tutoriel.

**H2 — Le scoring simulé crée un Aha! moment**  
Hypothèse : Voir un AO scoré à l'étape 3 de l'onboarding motive la complétion.  
Test : Mesurer le taux de complétion de l'onboarding avec et sans scoring simulé.

**H3 — L'explication 2 phrases est suffisante**  
Hypothèse : Les utilisateurs comprennent et font confiance au verdict avec 2 phrases d'explication.  
Test : Demander à 5 utilisateurs d'expliquer pourquoi un AO est GO/NO-GO après lecture de l'explication.

**H4 — La sidebar HIL est préférée à la modal**  
Hypothèse : Les utilisateurs traitent les HIL informatifs plus rapidement en sidebar qu'en modal.  
Test : Mesurer le temps de validation et le taux de validation pour chaque type de HIL.

**H5 — Le Mode Compact réduit la charge cognitive**  
Hypothèse : Les utilisateurs novices accomplissent leur première tâche plus vite en Mode Compact.  
Test : Mesurer le temps de première tâche (importer un AO, valider un HIL) selon le mode.

**H6 — Les emails digest ne sont pas perçus comme spam**  
Hypothèse : Un email quotidien récapitulatif est ouvert et perçu comme utile.  
Test : Mesurer le taux d'ouverture et le taux de clic sur les emails digest sur 30 jours.

**H7 — Le tour minimal 3 étapes est complété sans frustration**  
Hypothèse : 80% des utilisateurs complètent le tour minimal sans cliquer "Passer".  
Test : Tracking du funnel tour + entretiens de satisfaction post-tour.

**H8 — Le tableau de données Éditeur est suffisant pour le support**  
Hypothèse : Le fondateur peut diagnostiquer un problème client en moins de 2 minutes avec le tableau.  
Test : Simulation de scénarios de support avec le prototype.

---

## Annexe F — Checklist de Validation du MVP v0.1

Avant release v0.1, le groupe Produit & Expérience doit valider les éléments suivants :

### Onboarding
- [ ] Wizard 5 étapes avec defaults SIRET fonctionnels
- [ ] 3 templates de profil opérationnels
- [ ] Scoring simulé à l'étape 3 visible et fonctionnel
- [ ] Skip possible étapes 4-5 avec sauvegarde
- [ ] Tracking funnel onboarding actif

### Kanban
- [ ] Kanban 8 colonnes avec drag-drop fluide
- [ ] Indicateurs temporels visibles sur chaque carte
- [ ] Sémantique colorimétrique des deadlines appliquée
- [ ] Filtre BL local visible pour collaborateurs multi-BL
- [ ] Badge BL coloré sur chaque carte

### ScoreCard
- [ ] Verdict GO/NO-GO/MAYBE affiché par défaut
- [ ] Score global (0-100) visible
- [ ] Explication agentic 2 phrases max
- [ ] Détail 5D dépliable (préparation v0.2)

### HIL
- [ ] Modal HIL critique fonctionnelle
- [ ] Avertissement de blocage affiché si fermeture modal
- [ ] Taxonomie HIL documentée

### Notifications
- [ ] Centre de notifications in-app opérationnel
- [ ] Template email digest rédigé
- [ ] Template email immédiat critique rédigé
- [ ] Préférences de notification configurables

### Dashboards
- [ ] Dashboard Soumissionnaire Mode Compact fonctionnel
- [ ] Dashboard Acheteur Mode Compact fonctionnel
- [ ] Dashboard Éditeur tableau de données + 3 KPIs

### Recherche
- [ ] Barre de recherche globale avec autocomplétion
- [ ] 5 filtres rapides (chips) fonctionnels
- [ ] Recherche côté client performante (< 300ms)

### UX Globale
- [ ] Composant EmptyState réutilisable déployé sur tous les états vides
- [ ] Composant ErrorState réutilisable déployé sur tous les états d'erreur
- [ ] Tour minimal 3 étapes fonctionnel (first-time only)
- [ ] Copy français validé (pas de jargon technique non expliqué)
- [ ] Accessibilité basique respectée (contraste, focus, aria-labels)

---

*Fin du Compte-Rendu — Document structuré par le Groupe Produit & Expérience Utilisateur*  
*Réunion KIMI-TAKA-SWARM — Session Produit & UX*
