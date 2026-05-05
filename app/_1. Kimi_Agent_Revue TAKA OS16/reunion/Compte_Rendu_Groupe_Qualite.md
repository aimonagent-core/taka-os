# COMPTE-RENDU DE DÉBAT — GROUPE QUALITÉ & PRODUCTION

**Réunion KIMI-TAKA-SWARM — Cycle Qualité & Production**

---

**Date de session :** 2025-01-21  
**Projet :** TAKA OS — OS Agentic pour Appels d'Offres  
**Licence :** MIT Open Source  
**Cible :** PME / ETI + Acheteurs Publics  
**Statut du document :** FINAL — Soumis au Comité de Direction Technique pour validation  
**Classification :** CR-DEBAT-QUAL-2025-001  

---

## PARTICIPANTS AU GROUPE QUALITÉ & PRODUCTION

| Rôle | Agent Représenté | Domaine de compétence |
|------|------------------|----------------------|
| Modérateur | Sécurité Officer | Sécurité offensive/défensive, menaces, pentest |
| Modérateur | Compliance Legal | RGPD, AI Act, conformité réglementaire |
| Modérateur | QA Lead | Stratégie qualité, couverture de tests, standards |
| Modérateur | Test Automation | Automatisation de tests, CI/CD, mocks |
| Modérateur | Tech Writer | Documentation technique, specs, traçabilité |

---

## DÉFINITIONS QUALITÉ PROJET (RÉFÉRENCE)

Le présent compte-rendu s'appuie sur les exigences qualité initiales du projet TAKA OS, telles que définies dans le cahier des charges technique :

- **Testabilité :** pytest, pytest-asyncio, pytest-cov, factory-boy  
- **Couverture minimale déclarée :** 30+ tests backend (état actuel)  
- **Tests E2E :** Playwright, 3 suites  
- **Observabilité :** Sentry error tracking intégré  
- **Résilience données :** Backup PostgreSQL automatique  
- **Sécurité réseau :** Rate limiting + Circuit breaker sur appels API externes  
- **Authentification :** MFA / TOTP (Multi-Factor Authentication / Time-based One-Time Password)  
- **Accessibilité :** Conformité RGAA (Référentiel Général d'Amélioration de l'Accessibilité)  
- **Conformité IA :** AI Act — niveau de conformité à déterminer  
- **Traçabilité :** 5 couches de traçabilité forensique (identification, horodatage, immutabilité, chaînage, audit)  

---

# SOMMAIRE DES DÉBATS

| N° | Question | Enjeu critique |
|----|----------|---------------|
| Q1 | 30 tests pour un OS agentic — est-ce ridicule ? | Couverture test vs. qualité perçue |
| Q2 | Le parsing PDF — comment garantir la qualité à 95%+ ? | Fiabilité extraction données métiers |
| Q3 | Le MVP v0.1 est-il « sécurisé enough » ? | Périmètre sécurité minimum viable |
| Q4 | Conformité AI Act — niveau 3 dès v1.0 ? | Conformité réglementaire EU stratégique |
| Q5 | Les backups — suffisent-ils ? | Résilience données, RPO/RTO |
| Q6 | RGAA accessibilité — AA en v0.5 ? | Inclusion, conformité obligation légale |
| Q7 | Circuit breaker Mistral API — comment le tester ? | Tests de défaillance externe |
| Q8 | La documentation — qui la maintient ? | Gouvernance documentation technique |

---

# Q1 — 30 TESTS POUR UN OS AGENTIC : EST-CE RIDICULE ?

## Positions

### Position QA Lead — « EXIGEANT, STRUCTURÉ, COUVERTURE MÉTRIQUÉE »

**Énoncé :** Oui, 30 tests pour un OS agentic, c'est RIDICULE. C'est non seulement insuffisant, c'est dangereusement trompeur en termes de confiance qualité.

**Arguments :**

1. **La taille du périmètre fonctionnel :** TAKA OS n'est pas une simple API CRUD. C'est un système agentic orchestrant des flux d'appels d'offres avec parsing PDF, génération de documents, analyse de corpus, workflows multi-étapes, gestion de permissions complexes. Un tel périmètre exige une couverture de tests proportionnelle à la criticité et à la complexité cyclomatique du code.

2. **Les standards industriels :** Tout projet open-source prétendant à l'adoption par des PME, des ETI et des acheteurs publics doit viser une couverture de code (code coverage) supérieure à 80 %. Ce n'est pas un caprice, c'est une barrière d'entrée au marché. Les acheteurs publics exigent des garanties qualité vérifiables.

3. **La pyramide de tests :** On ne parle pas de 300 tests unitaires uniquement. On parle d'une pyramide équilibrée : tests unitaires (60 %), tests d'intégration (25 %), tests E2E (10 %), tests de contrat API (5 %). Pour un système de cette complexité, 300 tests est un minimum professionnel.

4. **La traçabilité forensique :** Le cahier des charges impose 5 couches de traçabilité. Comment justifier une traçabilité forensique si le code n'est pas testé de manière exhaustive ? Les logs de traçabilité doivent être eux-mêmes testés.

5. **La régression :** Avec des LLM, des mises à jour de modèles, des changements de prompts, le risque de régression est exponentiel. 30 tests ne permettent pas de détecter une régression prompt-driven avant production.

**Exigence formelle :** 300+ tests, couverture > 80 %, pyramide de tests complète, métriques publiées dans le CI.

---

### Position Test Automation — « QUALITÉ SUR QUANTITÉ, FLAKINESS IS THE ENEMY »

**Énoncé :** Non. L'important est la qualité des tests, pas la quantité. Trente tests bien écrits, déterministes, rapides et maintenables valent mieux que 300 tests flaky qui échouent aléatoirement et rendent le CI inutilisable.

**Arguments :**

1. **Le coût de la maintenance des tests :** Chaque test ajouté a un coût de maintenance. Des tests mal conçus — couplant l'implémentation, utilisant des sleeps, dépendant de l'ordre d'exécution — créent une dette technique qui ralentit les releases et érode la confiance dans le pipeline CI/CD.

2. **La pyramide inversée, fléau du secteur :** Beaucoup d'équipes atteignent 80 % de coverage avec des tests de façade, des tests qui exercent le code sans vérifier les comportements métiers. C'est du vanity metric. Je préfère 30 tests qui vérifient des invariants métiers critiques que 300 tests qui couvrent des getters/setters.

3. **Les tests sur les agents IA :** Les appels à des LLM externes sont par nature indéterministes. Un test qui appelle Mistral et vérifie une chaîne exacte est flaky par construction. Il faut des stratégies de test différentes pour les composants IA : contracts testing, property-based testing, évaluation humaine en boucle.

4. **Le CI comme outil de décision :** Un test qui échoue 1 fois sur 20 devient un bruit. Les développeurs ignorent le CI. Le build devient rouge en permanence. La culture qualité meurt.

5. **La vitesse du feedback :** Trente tests exécutés en 30 secondes > 300 tests exécutés en 10 minutes. La vitesse du cycle de feedback est un indicateur de qualité processus aussi important que le nombre de tests.

**Exigence formelle :** Pyramide de tests intelligente, tests déterministes garantis, pas de flaky tests tolérés, stratégie de test adaptée par couche architecturale.

---

### Position Backend Senior — « L'INDÉTERMINISME EST LE PROBLÈME CENTRAL »

**Énoncé :** Les tests sur les agents IA sont fondamentalement indéterministes. Comment tester un LLM qui retourne du texte libre ? Comment vérifier qu'un agent de rédaction de réponse à appel d'offres a produit un document « correct » ? La notion même de « test unitaire » s'effondre face à la génération créative.

**Arguments :**

1. **L'indéterminisme des LLM :** Un même prompt avec temperature=0.7 peut produire des réponses structuralement différentes. Un test qui vérifie une chaîne exacte est voué à l'échec. Un test qui vérifie une structure (JSON schema) ne vérifie pas la qualité sémantique.

2. **L'absence d'oracle :** Pour un module classique (somme de deux nombres), l'oracle est trivial. Pour un agent qui rédige une réponse à un AO, quel est l'oracle ? Un humain expert ? Un autre LLM ? Une métrique BLEU/ROUGE ? Aucune solution n'est satisfaisante à 100 %.

3. **La dérive modèle :** Mistral met à jour ses modèles. Un test qui passait hier peut échouer aujourd'hui, non pas à cause d'un bug du code, mais à cause d'un changement de comportement du modèle externe. Comment isoler le code de la dépendance externe ?

4. **La testabilité par contrat :** Pour les composants classiques (API, parsing, DB), les tests sont parfaitement adaptés. Pour les composants IA, il faut accepter que le testing soit probabiliste : évaluations A/B, métriques de confiance, monitoring en production.

5. **La distinction testable / non-testable :** Il faut séparer le code orchestration (testable de manière déterministe) du code génération IA (testable de manière probabiliste). Mélanger les deux dans une même métrique de coverage est une erreur de conception.

**Exigence formelle :** Stratégie de test bimodale : tests déterministes pour l'orchestration, tests probabilistes/évaluatifs pour les composants IA, métriques de coverage séparées.

---

## Débat

Le QA Lead ouvre le débat avec fermeté : « Trente tests, c'est ce qu'on fait pour un microservice de log. TAKA OS est un système agentic. La confiance de nos utilisateurs — des PME qui parient leur business sur nos appels d'offres, des collectivités qui ont des obligations légales de transparence — repose sur notre capacité à garantir que le système fonctionne. »

Le Test Automation rétorque immédiatement : « Je suis d'accord sur le principe, mais pas sur la métrique. Combien d'équipes ont atteint 80 % de coverage avec des tests inutiles ? Combien de projets open-source ont un CI rouge en permanence à cause de tests qui vérifient que `true == true` ? La quantité n'est pas un proxy de qualité. »

Le Sécurité Officer intervient : « La question n'est pas que de qualité logicielle. C'est de preuve. Si un acheteur public nous demande : « Comment savez-vous que votre système ne modifie pas les montants des AO ? », qu'est-ce qu'on répond ? « On a 30 tests » ? C'est une réponse administrative, pas une preuve technique. »

Le Compliance Legal ajoute : « L'AI Act impose des obligations de test et de validation pour les systèmes à haut risque. Les tests ne sont pas une option, ils sont une exigence légale. La traçabilité des tests fait partie de la documentation technique obligatoire. »

Le Backend Senior apporte une nuance technique : « Je suis pour plus de tests. Mais soyons honnêtes sur ce qui est testable. Le parsing d'un PDF vers un JSON structuré — testable. La génération d'une réponse à un AO par un LLM — testable partiellement. Il faut deux stratégies. »

Le QA Lead concède partiellement : « D'accord sur le bimodal. Mais la stratégie déterministe doit être massive. Tout le code qui n'est pas LLM — routing, auth, persistence, validation, transformation de données — doit être couvert à plus de 90 %. Et les composants IA doivent avoir des évaluations systématiques, pas des tests unitaires classiques. »

Le Test Automation propose un compromis technique : « Adoptons une approche par couches. Couche 1 (infrastructure, auth, DB) : tests unitaires + intégration, cible 90 %. Couche 2 (orchestration agents, parsing) : tests d'intégration + E2E, cible 70 %. Couche 3 (génération IA) : évaluations automatiques + revue humaine, cible « confiance statistique » avec métriques de qualité. »

Le Tech Writer soulève un point de gouvernance : « Qui documente les tests ? Comment un contributeur externe comprend qu'un test a échoué à cause d'une dérive LLM et non d'un bug de son code ? Il faut une documentation des tests aussi rigoureuse que le code testé. »

---

## Décision Q1

**DÉCISION PRINCIPALE :** La stratégie de tests sera bimodale, avec des objectifs de couverture différenciés par couche architecturale. Le nombre absolu de tests n'est pas la métrique principale ; la pertinence métier des tests et leur déterminisme le sont.

**Spécifications de la décision :**

1. **Couche 1 — Code déterministe (infrastructure, auth, DB, routing, validation) :**
   - Tests unitaires + tests d'intégration
   - Couverture de code cible : ≥ 90 %
   - Nombre estimé : 150+ tests
   - Délai : v0.3
   - Responsable : Test Automation

2. **Couche 2 — Orchestration agentic + parsing (PDF, workflows, transformations) :**
   - Tests d'intégration + tests E2E + tests de contrat API
   - Couverture de code cible : ≥ 70 %
   - Nombre estimé : 100+ tests
   - Délai : v0.5
   - Responsable : QA Lead

3. **Couche 3 — Composants IA (génération LLM, inférence) :**
   - Pas de tests unitaires classiques (inadaptés)
   - Évaluations automatiques avec métriques structurées (JSON schema validation, cohérence sémantique via embeddings similarity, métriques de confiance)
   - Benchmark continu sur corpus de référence
   - Couverture évaluée par « score de confiance » > 0.85
   - Nombre estimé : 50+ évaluations
   - Délai : v0.5
   - Responsable : Backend Senior + QA Lead

4. **Couverture globale cible :** Non applicable en un seul chiffre. Publication d'un tableau de bord qualité public (dans le repo) avec les métriques par couche.

5. **Interdiction formelle :** Aucun test flaky (taux d'échec non nul sans changement de code) n'est toléré dans le CI principal. Tout test instable est soit corrigé, soit supprimé, soit isolé dans un pipeline séparé (nightly).

6. **Documentation des tests :** Chaque suite de tests > 10 cas DOIT avoir un fichier `TEST_STRATEGY.md` associé décrivant l'oracle, les dépendances mockées, et les raisons d'échec probables.

---

## Actions Q1

| N° | Action | Responsable | Deadline | Priorité | Critère d'acceptation |
|----|--------|-------------|----------|----------|----------------------|
| A1.1 | Auditer les 30 tests existants — qualifier chaque test (déterministe/flaky/couverture) | Test Automation | 2025-01-28 | CRITIQUE | Rapport d'audit avec classification de chaque test |
| A1.2 | Mettre en place la séparation couche 1/2/3 dans la structure de test | QA Lead | 2025-02-04 | CRITIQUE | Arborescence de tests reflétant les couches, CI adapté |
| A1.3 | Atteindre 90 % coverage sur couche 1 (code déterministe) | Test Automation | 2025-02-18 | HAUTE | Rapport pytest-cov avec lignes non couvertes justifiées |
| A1.4 | Développer le framework d'évaluation pour couche 3 (IA) | Backend Senior | 2025-02-18 | HAUTE | Framework property-based + métriques de confiance documenté |
| A1.5 | Créer le tableau de bord qualité public (README badge + page dédiée) | Tech Writer | 2025-02-11 | MOYENNE | Badge visible sur README, page détaillée dans docs/QUALITY.md |
| A1.6 | Rédiger le guide « Pourquoi mon test échoue ? » pour contributeurs | Tech Writer | 2025-02-25 | MOYENNE | Guide intégré à la documentation contributeur |
| A1.7 | Mettre en place le pipeline nightly pour tests probabilistes | DevOps | 2025-02-11 | MOYENNE | Pipeline CI séparé, résultats archivés 30 jours |

---

# Q2 — LE PARSING PDF : COMMENT GARANTIR LA QUALITÉ À 95%+ ?

## Positions

### Position QA Lead — « MÉTRIQUES MÉTIER, CORPUS DE RÉFÉRENCE, VALIDATION HUMAINE »

**Énoncé :** La qualité du parsing PDF doit être mesurée sur des critères métier précis : pourcentage de champs correctement extraits (CPV, montant, deadline, objet, auteurité). Objectif : 95 % sur un corpus de 100 PDF réels, validé manuellement.

**Arguments :**

1. **La mesure métier vs. la mesure technique :** Un parsing technique « réussi » (le PDF est lu sans erreur) n'a aucune valeur si le CPV extrait est faux. La qualité se mesure à l'aune de la mission métier : fournir des données structurées correctes pour l'analyse des appels d'offres.

2. **Le corpus de référence :** Il faut un corpus de 100 PDF réels d'appels d'offres publics, couvrant les variabilités : PDF natifs, PDF scannés, PDF images, PDF multi-colonnes, PDF avec tableaux complexes, PDF en plusieurs langues. Chaque PDF du corpus a une ground truth manuelle (annotation humaine des champs attendus).

3. **La métrique :** Pour chaque champ critique (CPV, montant, deadline, objet de la consultation, autorité contractante, procédure de marché), calculer : (nombre d'extractions correctes / nombre total de PDF) × 100. La moyenne pondérée doit être ≥ 95 %.

4. **La traçabilité :** Chaque échec de parsing sur le corpus doit être tracé : type d'erreur, type de PDF, champ concerné, cause racine (problème OCR, problème de layout, problème sémantique). C'est une exigence pour l'amélioration continue.

5. **Le cadre normatif :** Pour les acheteurs publics, une erreur sur le montant d'un AO ou sa deadline peut avoir des conséquences légales (contentieux, annulation de procédure). 95 % n'est pas un caprice, c'est un minimum de crédibilité.

**Exigence formelle :** Corpus de 100 PDF réels annotés, métrique de qualité par champ ≥ 95 %, traçabilité des échecs, rapport public d'évaluation.

---

### Position AI Engineer — « LE PARSING EST PROBABILISTE, 95% GLOBAL EST IRRÉALISTE »

**Énoncé :** Le parsing PDF, en particulier via des techniques IA (OCR + LLM), est fondamentalement probabiliste. Garantir 95 % sur TOUS les PDF est irréaliste car certains documents sont intrinsèquement non parseables : scans manuscrits, PDF image de faible qualité, documents dégradés, langues rares.

**Arguments :**

1. **Les PDF impossibles :** Un scan manuscrit d'un AO de 1980, en qualité 72 DPI, avec des annotations au stylo, ne sera jamais parsé correctement. Même les meilleurs OCR (Tesseract, Azure OCR, Google Vision) ont des limites physiques. Exiger 95 % sur ce type de document est impossible.

2. **Le pipeline de parsing :** Notre pipeline compte 5 étapes : extraction texte (PDFMiner/PyMuPDF), OCR si nécessaire (Tesseract/OCR.space), nettoyage, structuration LLM, validation. Chaque étape a sa propre distribution d'erreur. La loi des grands nombres s'applique : les erreurs se cumulent.

3. **La classification des PDF :** Il faut classer les PDF par « parseabilité » :  
   - Classe A (PDF natif, texte lisible) : objectif 98 %  
   - Classe B (PDF image, bonne qualité) : objectif 90 %  
   - Classe C (PDF dégradé, scan ancien) : objectif 70 % ou refus avec message explicite  
   - Classe D (illisible) : rejet systématique avec notification utilisateur  

4. **Le coût de l'overpromising :** Promettre 95 % global et livrer 85 % érode la confiance. Il vaut mieux promettre un taux par classe et être transparent sur les limites.

5. **Le fallback humain :** Pour les documents non parsés automatiquement, il faut un fallback : notification à l'utilisateur avec formulaire de saisie manuelle guidée. Le système doit dégrader gracieusement.

**Exigence formelle :** Classification des PDF par classe de parseabilité, objectifs de qualité différenciés, pipeline de fallback, transparence sur les limites.

---

## Débat

Le QA Lead commence par poser le corpus sur la table virtuelle : « J'ai annoté 47 PDF sur les 100 du corpus. Résultat préliminaire : 82 % de champs corrects. Les 18 % d'erreurs sont principalement sur les PDF scannés. Sur les PDF natifs, on est à 96 %. »

L'AI Engineer répond : « Vos chiffres prouvent mon point. 96 % sur natifs, 65 % sur scannés basse qualité. Si on mixe tout, on ne peut pas tenir 95 %. La question est : est-ce qu'on rejette les scannés basse qualité ou est-ce qu'on abaisse l'objectif global ? »

Le Sécurité Officer soulève un angle de menace : « Si un attaquant nous envoie un PDF malformé intentionnellement — overflow, injection via métadonnées — notre parser le traite comment ? La qualité parsing n'est pas juste d'extraire des champs, c'est aussi de ne pas exécuter du code. Les tests de parsing doivent inclure des PDF malveillants. »

Le Compliance Legal ajoute : « L'AI Act, Article 15, exige la robustesse des systèmes d'IA. Un parser qui échoue silencieusement et retourne des données erronées est un système non robuste. Il faut que le système détecte ses propres échecs et les signale. »

Le Test Automation demande : « Comment on intègre le parsing dans le CI ? On ne va pas committer 100 PDF dans le repo. Il faut un stockage externe, un job de régression qui télécharge le corpus, lance le parsing, compare avec la ground truth. »

Le Backend Senior confirme : « On met le corpus dans un bucket S3 versionné. Le job CI télécharge, parse, compare. Le résultat est un rapport JSON avec les métriques par champ et par classe. Si une régression dépasse le seuil, le build échoue. »

Le QA Lead propose une synthèse : « OK. Adoptons la classification. Mais avec un principe : tout PDF de classe A ou B DOIT être parsé sans intervention humaine. Classe C : fallback proposé. Classe D : rejet explicite. Et publions la métrique par classe, pas une métrique globale biaisée. »

L'AI Engineer approuve : « Et ajoutons un système de confiance : le parser retourne un score de confiance par champ. Si le score est < 0.8 sur un champ critique, on marque le champ comme « à vérifier » même si on retourne une valeur. »

Le Tech Writer demande : « Et la documentation utilisateur ? Il faut expliquer à l'utilisateur pourquoi certains PDF ne sont pas parsés et ce qu'il peut faire. »

---

## Décision Q2

**DÉCISION PRINCIPALE :** Le parsing PDF adopte une stratégie de qualité différenciée par classe de document, avec des objectifs de qualité adaptés, un score de confiance par champ, et un pipeline de fallback transparent. L'objectif de 95 % n'est pas global mais par classe.

**Spécifications de la décision :**

1. **Classification des PDF en 4 classes :**
   - **Classe A** (PDF natif, texte structuré, qualité professionnelle) : objectif ≥ 97 % par champ critique
   - **Classe B** (PDF image, OCR possible, qualité acceptable) : objectif ≥ 90 % par champ critique
   - **Classe C** (PDF dégradé, scan ancien, qualité limite) : objectif ≥ 75 %, fallback utilisateur systématique
   - **Classe D** (illisible, corrompu, potentiellement malveillant) : rejet immédiat, notification utilisateur, log sécurité

2. **Score de confiance :** Chaque champ extrait est accompagné d'un score de confiance (0.0 à 1.0). Score < 0.80 sur champ critique = marquage « À vérifier » dans l'interface.

3. **Corpus de référence :** 100 PDF réels annotés manuellement, stockés dans S3 versionné, avec ground truth JSON. Augmentation cible : +50 PDF par trimestre.

4. **Pipeline CI parsing :** Job de régression automatique exécuté à chaque PR touchant le parser. Échec si régression > 2 points sur une métrique de classe.

5. **Tests de sécurité parsing :** Inclusion de 10 PDF malveillants (tests d'overflow, injection, corruption) dans le pipeline de sécurité. Le parser DOIT rejeter sans crash.

---

## Actions Q2

| N° | Action | Responsable | Deadline | Priorité | Critère d'acceptation |
|----|--------|-------------|----------|----------|----------------------|
| A2.1 | Finaliser l'annotation du corpus de 100 PDF réels | QA Lead | 2025-02-04 | CRITIQUE | 100 PDF annotés avec ground truth JSON validé |
| A2.2 | Implémenter le classificateur de PDF (A/B/C/D) | AI Engineer | 2025-02-11 | CRITIQUE | Classifier avec > 95 % de précision sur échantillon test |
| A2.3 | Intégrer le score de confiance par champ dans le parser | Backend Senior | 2025-02-18 | HAUTE | Score retourné pour chaque champ, affichage UI |
| A2.4 | Mettre en place le job CI de régression parsing | Test Automation | 2025-02-18 | HAUTE | Job CI exécuté, échec sur régression > 2 points |
| A2.5 | Développer le pipeline de fallback (formulaire saisie manuelle) | UI Designer | 2025-03-04 | MOYENNE | Fallback fonctionnel pour classes C et D |
| A2.6 | Créer les 10 PDF de test sécurité (malveillants) | Sécurité Officer | 2025-02-11 | HAUTE | PDF de test créés, tests de rejet sans crash passent |
| A2.7 | Documenter la classification et les limites utilisateur | Tech Writer | 2025-02-25 | MOYENNE | Page docs/PARSING_QUALITY.md publiée |

---

# Q3 — LE MVP V0.1 EST-IL « SÉCURISÉ ENOUGH » ?

## Positions

### Position Sécurité Officer — « NON. C'EST DANGEREUX. PERIOD. »

**Énoncé :** Non. Le MVP v0.1 n'est PAS sécurisé enough. Ce n'est pas une opinion, c'est une évaluation factuelle basée sur un modèle de menaces. Absence de WAF, absence de pentest, absence de protection DDoS, absence de CSP stricte. Un script kiddie peut faire tomber le service en 15 minutes.

**Arguments :**

1. **Le modèle de menaces :** TAKA OS traite des appels d'offres publics — des données potentiellement sensibles (montants, stratégies d'entreprise, identités des soumissionnaires). La surface d'attaque inclut : injection SQL via parsing, XSS via documents générés, DoS via parsing de PDF malveillants, fuite de données via API mal sécurisée.

2. **L'absence de WAF :** Sans Web Application Firewall, nous n'avons aucune protection contre les attaques web classiques : SQL injection, XSS, CSRF, LFI, RCE. Nginx seul ne suffit pas.

3. **L'absence de pentest :** Aucun test d'intrusion n'a été réalisé. Nous ne connaissons pas nos vulnérabilités. C'est comme conduire les yeux bandés.

4. **L'absence de DDoS protection :** Le rate limiting Nginx est rudimentaire. Il ne protège pas contre une attaque DDoS distribuée de niveau 3/4. Un botnet basique peut saturer la bande passante.

5. **La responsabilité légale :** En cas de fuite de données, la responsabilité incombe aux opérateurs du système. « C'était un MVP » n'est pas une défense devant la CNIL ou un tribunal.

**Exigence formelle :** Avant tout lancement en production (même beta), mise en place de WAF, pentest interne, bug bounty programme, DDoS protection basique, CSP stricte, audit de dépendances (Snyk/Dependabot).

---

### Position DevOps — « C'EST UN MVP. ON N'EST PAS UNE BANQUE. »

**Énoncé :** C'est un MVP. On n'est pas une banque. Pour 100 premiers utilisateurs en beta fermée, Nginx rate limit + fail2ban + HTTPS Let's Encrypt + headers de sécurité de base suffisent. La sécurité doit être proportionnée au risque réel.

**Arguments :**

1. **Le risque réel :** Nous avons 0 utilisateur aujourd'hui. Le risque d'attaque sur une beta fermée de 100 utilisateurs est faible. Les attaquants ciblent les services à fort volume de données ou de transactions financières.

2. **Le coût de la sur-sécurisation :** Mettre en place un WAF professionnel (AWS WAF, Cloudflare Pro), commander un pentest externe, mettre en place un SOC — c'est des milliers d'euros et des semaines de travail. Pour un MVP open-source MIT, c'est disproportionné.

3. **Nginx rate limiting :** Le rate limiting Nginx, correctement configuré (limit_req_zone), protège contre la plupart des attaques par force brute et scraping agressif. fail2ban ajoute une couche de bannissement IP.

4. **Le principe de proportionnalité :** La sécurité doit être proportionnée au risque. v0.1 beta fermée ≠ v1.0 production publique. La sécurité s'adapte en fonction de la maturité du produit et de la sensibilité des données traitées.

5. **L'open source comme atout :** Le code est open-source. La communauté peut auditer le code. C'est une forme de sécurité par transparence (Linus's Law).

**Exigence formelle :** Nginx rate limit + fail2ban + HTTPS + security headers pour v0.1. WAF + pentest pour v0.5 (public beta). SOC + bug bounty pour v1.0.

---

### Position Compliance Legal — « RGPD + AI ACT. 4% DU CA MONDIAL. »

**Énoncé :** RGPD + AI Act. Si on fuite des données personnelles ou des données sensibles d'appels d'offres, c'est 4 % du chiffre d'affaires mondial d'amende. « MVP » n'est pas une catégorie juridique. Les obligations de sécurité s'appliquent dès le premier traitement de données.

**Arguments :**

1. **Le RGPD s'applique dès le traitement :** L'article 32 du RGPD impose des mesures de sécurité techniques et organisationnelles « dès la conception » (privacy by design). Ce n'est pas une option post-MVP.

2. **La nature des données :** Les appels d'offres contiennent des données personnelles (noms des correspondants, coordonnées), des données stratégiques d'entreprise, et potentiellement des données classifiées. La fuite de ces données expose à des sanctions.

3. **L'AI Act, Article 9 :** Les systèmes de haut risque doivent être conçus avec des mesures de sécurité appropriées. Un MVP qui traite des AO publics avec IA générative est potentiellement classifiable.

4. **La confiance comme actif :** Pour un projet open-source ciblant les acheteurs publics, une fuite de données v0.1 tue le projet v1.0. La réputation de sécurité se construit dès le premier commit.

5. **L'assurance responsabilité :** Sans mesures de sécurité documentées, en cas de litige, la responsabilité des fondateurs est engagée personnellement. La forme juridique de la structure porteuse n'exonère pas des fautes personnelles.

**Exigence formelle :** Dès v0.1 : chiffrement des données en transit (TLS 1.3) et au repos, politique de mot de passe forte, MFA disponible, logs d'audit immutables, registre des traitements RGPD, DPO désigné (même interne).

---

## Débat

Le Sécurité Officer ouvre avec une démonstration : « J'ai passé 2 heures ce matin. Résultat : injection XSS via le champ « objet de consultation » dans le PDF parser — le texte n'est pas échappé avant affichage. CSRF token absent sur le endpoint de login. Rate limit Nginx configuré à 1000 req/s — c'est inutile. »

Le DevOps réagit : « OK pour le XSS et le CSRF, ça doit être corrigé. Mais le rate limit à 1000 req/s, c'est parce qu'on n'a pas encore calibré. Pour la beta fermée, avec une liste blanche d'IP, le risque est contrôlé. »

Le Compliance Legal est inflexible : « Le RGPD ne fait pas de beta fermée. Dès que tu traites des données personnelles, tu as des obligations. J'ai vérifié : le formulaire d'inscription collecte email + nom + entreprise. C'est du traitement de données personnelles. Article 32. Applicable immédiatement. »

Le QA Lead demande : « Quel est le minimum viable en sécurité pour pouvoir ouvrir la beta ? Pas le maximum, le minimum. Une liste de contrôle. »

Le Sécurité Officer propose : « Le minimum, c'est le OWASP Top 10 couvert. Injection (SQL, XSS, command) — corrigé. Authentification cassée — MFA obligatoire. Exposition de données sensibles — chiffrement au repos. Security misconfiguration — CSP + headers. »

Le DevOps contre : « MFA obligatoire pour une beta ? C'est une friction utilisateur massive. MFA optionnel pour v0.1, obligatoire pour v0.3. »

Le Compliance Legal tranche : « MFA optionnel, mais la politique de mot de passe forte obligatoire. Et un avertissement visible si l'utilisateur désactive MFA : « Votre compte est vulnérable ». C'est le compromis légal. »

Le Backend Senior ajoute : « Il faut aussi un système de logs d'audit dès v0.1. Si on a un incident, il faut pouvoir investiguer. Pas de logs = pas d'incident response possible. »

Le Test Automation : « Et les tests de sécurité automatisés ? OWASP ZAP dans le CI ? »

Le Sécurité Officer : « Oui. ZAP baseline scan à chaque PR. Ça détecte les régressions de sécurité basiques. C'est gratuit, c'est rapide, c'est non négociable. »

---

## Décision Q3

**DÉCISION PRINCIPALE :** Le MVP v0.1 n'est PAS « sécurisé enough » en l'état. Un plan de sécurité minimum viable (S-MVP) est imposé avant ouverture de la beta. La sécurité n'est pas une option post-MVP, mais elle est implémentée de manière proportionnée au risque réel.

**Spécifications de la décision :**

1. **Avant ouverture beta v0.1 (bloquant) :**
   - Correction des vulnérabilités OWASP Top 10 identifiées (XSS, CSRF, injection)
   - HTTPS TLS 1.3 obligatoire (pas d'HTTP en production)
   - Rate limiting Nginx calibré à 100 req/min par IP sur les endpoints sensibles
   - CSP (Content Security Policy) stricte implémentée
   - Chiffrement des données au repos (PostgreSQL avec pgcrypto, fichiers chiffrés)
   - Politique de mot de passe forte (12 caractères, complexité)
   - OWASP ZAP baseline scan intégré au CI
   - Logs d'audit immutables (append-only, horodatés, signés)

2. **Pour v0.1 (recommandé fortement, non bloquant pour beta fermée contrôlée) :**
   - MFA / TOTP disponible (optionnel, avertissement si désactivé)
   - fail2ban activé
   - Registre des traitements RGPD rédigé
   - DPO désigné (même interne, même à temps partiel)

3. **Pour v0.3 (public beta) :**
   - MFA / TOTP obligatoire pour les comptes admin et contributeurs
   - WAF Cloudflare/AWS WAF ou équivalent
   - Pentest interne réalisé et rapporté
   - Programme bug bounty (même minimal, HackerTartget ou Bugcrowd)

4. **Pour v0.5 :**
   - Pentest externe par cabinet certifié (CEH, OSCP)
   - DDoS protection professionnelle
   - SOC (Security Operations Center) minimal ou service managé

5. **Pour v1.0 :**
   - Certification ISO 27001 ou SOC 2 Type II (à étudier)
   - Audit de sécurité annuel
   - Bug bounty mature

---

## Actions Q3

| N° | Action | Responsable | Deadline | Priorité | Critère d'acceptation |
|----|--------|-------------|----------|----------|----------------------|
| A3.1 | Auditer les vulnérabilités OWASP Top 10 sur v0.1 | Sécurité Officer | 2025-01-28 | CRITIQUE | Rapport d'audit avec CVE identifiées et plans de correction |
| A3.2 | Corriger XSS + CSRF + injection (bloquant beta) | Backend Senior | 2025-02-04 | CRITIQUE | Tests de sécurité passent, ZAP scan vert |
| A3.3 | Implémenter TLS 1.3 + CSP stricte + rate limit | DevOps | 2025-02-04 | CRITIQUE | Configuration validée par scan SSL Labs A+ |
| A3.4 | Mettre en place chiffrement PostgreSQL au repos | DevOps | 2025-02-11 | HAUTE | pgcrypto activé, données sensibles chiffrées |
| A3.5 | Intégrer OWASP ZAP baseline scan au CI | Test Automation | 2025-02-11 | HAUTE | ZAP exécuté à chaque PR, rapport archivé |
| A3.6 | Configurer logs d'audit immutables (5 couches) | Backend Senior | 2025-02-18 | HAUTE | Logs append-only, horodatés signés, chaînage vérifié |
| A3.7 | Rédiger registre des traitements RGPD | Compliance Legal | 2025-02-18 | HAUTE | Document publié, DPO identifié |
| A3.8 | Mettre en place MFA optionnel + avertissement | Backend Senior | 2025-02-25 | MOYENNE | MFA fonctionnel, avertissement UI visible |
| A3.9 | Planifier pentest interne v0.3 | Sécurité Officer | 2025-03-04 | MOYENNE | Plan de pentest rédigé, ressources identifiées |

---

# Q4 — CONFORMITÉ AI ACT : PEUT-ON VRAIMENT ÊTRE NIVEAU 3 DÈS V1.0 ?

## Positions

### Position Compliance Legal — « NON. NIVEAU 3, C'EST 6 MOIS DE TRAVAIL. »

**Énoncé :** Non. Atteindre le niveau 3 du AI Act (système à haut risque) dès la v1.0 est irréaliste. Le niveau 3 nécessite un audit externe, un DPO dédié, un système de management de la qualité (SMQ), des tests de conformité documentés, une évaluation d'impact fondamentale. C'est 6 mois de travail à plein temps pour une équipe de 3 personnes.

**Arguments :**

1. **Les exigences du niveau 3 (haut risque) :** L'article 9 du AI Act impose : système de gestion de la qualité, évaluation des risques, gestion des données (gouvernance, qualité, biais), documentation technique, traçabilité, transparence, surveillance humaine, robustesse, exactitude. Chaque exigence nécessite des processus, des documents, des audits.

2. **L'audit externe obligatoire :** Le niveau 3 requiert une évaluation de conformité par un tiers (notified body) avant mise sur le marché. Ce n'est pas un self-certification. C'est un processus long (3-6 mois) et coûteux (50 000-150 000 €).

3. **Le DPO / LMO :** Le AI Act exige un « Liable Manager Operator » ou équivalent pour les systèmes à haut risque. C'est un rôle dédié, avec responsabilité légale personnelle.

4. **Le SMQ (Système de Management de la Qualité) :** Il faut documenter les processus de conception, de test, de déploiement, de monitoring, de correction. C'est un ISO 9001 spécifique IA. Non trivial.

5. **L'échelle de temps réaliste :** Pour une équipe de la taille de TAKA, 6 mois est un minimum. Vouloir le faire pour v1.0 signifie retarder le lancement de 6 mois minimum.

**Exigence formelle :** Niveau 2 (transparence + traçabilité) pour v0.5. Niveau 3 pour v1.5 (18 mois post-lancement). Feuille de route AI Act publiée.

---

### Position Sécurité Officer — « NIVEAU 2 EN V0.5, NIVEAU 3 EN V1.5 »

**Énoncé :** On peut viser le niveau 2 (transparence + traçabilité) dès la v0.5. Le niveau 3 est une cible pour v1.5. Il faut être pragmatique tout en montrant une progression crédible vers la conformité maximale.

**Arguments :**

1. **Le niveau 2 est atteignable :** Transparence (informations claires sur les capacités et limitations du système), traçabilité (logs des interactions), robustesse basique (tests, monitoring). C'est du travail, mais c'est intégrable dans un cycle de développement agile.

2. **La crédibilité stratégique :** Pour les acheteurs publics, montrer une feuille de route AI Act avec des jalons clairs est plus crédible que prétendre être niveau 3 sans l'être réellement. La fraude à la conformité est détectable et pénalement sanctionnée.

3. **L'anticipation réglementaire :** Le AI Act est en phase de transposition. Les exigences exactes du niveau 3 vont évoluer. Attendre v1.5 permet de bénéficier de la jurisprudence et des guides de l'UE.

4. **Le niveau 1 (minimal) :** Même le niveau 1 (transparence basique) n'est pas totalement atteint aujourd'hui. Il faut progresser par paliers.

5. **La conformité comme avantage compétitif :** Être niveau 2 dès v0.5 crée une différenciation. La plupart des concurrents seront niveau 1 ou non conformes.

**Exigence formelle :** Niveau 1 dès v0.3, niveau 2 dès v0.5, niveau 3 cible v1.5. Tableau de bord de conformité AI Act public.

---

## Débat

Le Compliance Legal pose les documents réglementaires sur la table : « J'ai analysé le AI Act, le règlement complet. 85 pages. Le niveau 3, c'est 40 exigences spécifiques. Pour chaque exigence, il faut : un processus, une preuve, un audit. On est une équipe de 5 développeurs. Faisons les maths. »

Le Sécurité Officer répond : « D'accord sur l'irrémédiable. Mais la question est : qu'est-ce qu'on promet ? Si on dit « niveau 3 en v1.0 » et qu'on est en réalité niveau 2, c'est de la publicité mensongère. Les acheteurs publics vont demander les certificats. »

Le QA Lead demande : « Qu'est-ce qui définit notre niveau de risque ? Le AI Act classe les systèmes par usage. TAKA OS est un système d'aide à la décision pour appels d'offres. C'est du niveau 2 ou 3 ? »

Le Compliance Legal clarifie : « L'annexe III du AI Act inclut les « systèmes d'IA utilisés dans le domaine de l'administration publique ». Les appels d'offres publics entrent dans ce champ. Et le système influence des décisions économiques (attribution de marchés). Potentiellement niveau 3. »

Le Backend Senior : « Donc on EST potentiellement niveau 3. Ce n'est pas un choix. C'est une classification légale. La question n'est pas « est-ce qu'on veut être niveau 3 ? » mais « comment on devient conforme niveau 3 le plus vite possible ? » »

Le Compliance Legal nuance : « La classification exacte dépend de l'interprétation. Certains systèmes d'aide à la rédaction d'AO pourraient être considérés comme niveau 2 si l'humain garde le contrôle final. Mais c'est une zone grise. Il faut un avis juridique formel. »

Le Tech Writer : « Quelle que soit la classification, il faut documenter. Le AI Act exige une documentation technique. Qui la rédige ? »

Le Compliance Legal : « Moi. Mais il me faut des entrées techniques stables. Pas de doc sur des API qui changent toutes les semaines. La doc AI Act est un effort continu de 2-3 jours par semaine. »

Le QA Lead propose : « Créons un « AI Act Compliance Board » interne. Réunion mensuelle. Responsable : Compliance Legal. Objectif : avancer le niveau de conformité d'un cran chaque mois. »

---

## Décision Q4

**DÉCISION PRINCIPALE :** La conformité AI Act est une obligation légale, pas un choix marketing. La classification exacte (niveau 2 ou 3) fait l'objet d'un avis juridique formel avant v0.3. En attendant, le projet vise le niveau 2 (transparence + traçabilité) dès v0.5 et prépare le terrain pour le niveau 3.

**Spécifications de la décision :**

1. **Avis juridique formel :** Engagement d'un cabinet d'avocats spécialisé en droit du numérique pour classifier formellement TAKA OS selon le AI Act. Livrable : note juridique de 10-20 pages avec recommandations.
   - Deadline : 2025-03-04
   - Responsable : Compliance Legal

2. **Niveau 1 (transparence basique) — cible v0.3 :**
   - Page de transparence sur les capacités et limitations du système
   - Mentions obligatoires dans l'interface : « Ce système utilise l'IA. Les résultats doivent être vérifiés. »
   - Documentation des modèles utilisés (Mistral, versions, paramètres)

3. **Niveau 2 (transparence + traçabilité + robustesse) — cible v0.5 :**
   - Traçabilité complète des interactions IA (prompt, réponse, timestamp, utilisateur)
   - Système de logs d'audit immutables (déjà décidé en Q3)
   - Évaluation des biais sur corpus de référence
   - Documentation technique complète (architecture, modèles, données d'entraînement si applicable)
   - Mécanisme de surveillance humaine (override possible sur les décisions critiques)

4. **Niveau 3 (haut risque) — cible v1.5 :**
   - SMQ (Système de Management de la Qualité) documenté et opérationnel
   - Audit externe par notified body (ou équivalent selon évolution réglementaire)
   - Évaluation d'impact fondamentale (FRIA - Fundamental Rights Impact Assessment)
   - DPO / LMO désigné et formé
   - Processus de signalement des incidents

5. **AI Act Compliance Board :** Réunion mensuelle obligatoire. Ordre du jour : avancement conformité, blocages, décisions. Compte-rendu archivé.
   - Responsable : Compliance Legal
   - Première réunion : 2025-02-04

6. **Tableau de bord de conformité :** Page publique dans la documentation indiquant le niveau actuel, les écarts, la feuille de route. Mis à jour mensuellement.
   - Responsable : Tech Writer
   - Première version : 2025-02-18

---

## Actions Q4

| N° | Action | Responsable | Deadline | Priorité | Critère d'acceptation |
|----|--------|-------------|----------|----------|----------------------|
| A4.1 | Obtenir avis juridique formel sur classification AI Act | Compliance Legal | 2025-03-04 | CRITIQUE | Note juridique signée par cabinet spécialisé |
| A4.2 | Créer le AI Act Compliance Board + planifier réunions mensuelles | Compliance Legal | 2025-02-04 | CRITIQUE | Comité créé, règlement de fonctionnement publié |
| A4.3 | Implémenter niveau 1 (transparence basique) | Backend Senior | 2025-02-18 | HAUTE | Page transparence en ligne, mentions UI visibles |
| A4.4 | Implémenter traçabilité complète des interactions IA | Backend Senior | 2025-02-25 | HAUTE | Logs de prompts/réponses avec 5 couches forensiques |
| A4.5 | Réaliser évaluation des biais sur corpus de référence | QA Lead | 2025-03-11 | MOYENNE | Rapport d'évaluation des biais publié |
| A4.6 | Rédiger documentation technique AI Act (premier jet) | Tech Writer | 2025-03-04 | MOYENNE | Document technique > 30 pages couvrant modèles, données, architecture |
| A4.7 | Implémenter mécanisme de surveillance humaine (override) | Product Manager | 2025-03-18 | MOYENNE | Bouton « Revoir manuellement » sur les décisions critiques |
| A4.8 | Préparer le SMQ (premier jet processus) | Compliance Legal | 2025-04-01 | FAIBLE | SMQ v0.1 documenté, processus de gouvernance qualité |
| A4.9 | Créer tableau de bord conformité AI Act public | Tech Writer | 2025-02-18 | MOYENNE | Page docs/AI_ACT_COMPLIANCE.md publiée et maintenue |

---

# Q5 — LES BACKUPS : SUFFISENT-ILS ?

## Positions

### Position DevOps — « BACKUP QUOTIDIEN S3, RÉTENTION 30 JOURS. STANDARD. »

**Énoncé :** Un backup quotidien vers S3 avec rétention 30 jours. C'est un standard industriel. Pour un MVP, c'est amplement suffisant. La plupart des PPME n'ont même pas ça.

**Arguments :**

1. **Le standard AWS RDS :** AWS RDS propose nativement des backups automatiques quotidiens avec rétention configurable jusqu'à 35 jours. C'est ce que nous utilisons. C'est la solution de l'industrie.

2. **Le coût :** Les backups vers Glacier/Deep Archive coûtent quelques euros par mois pour notre volume. Ajouter du chiffrement, du PITR, du multi-région multiplie les coûts sans bénéfice proportionnel pour un MVP.

3. **Le RPO acceptable :** Un backup quotidien signifie un RPO (Recovery Point Objective) de 24 heures maximum. Pour des appels d'offres — des données qui changent lentement — un RPO de 24h est acceptable.

4. **La restauration testée :** Nous avons testé la restauration. Elle fonctionne. Le RTO (Recovery Time Objective) est de 2 heures. C'est acceptable.

5. **La proportionnalité :** Pour 100 utilisateurs beta, un backup quotidien S3 est proportionné. Les banques font du PITR et du multi-région. Nous ne sommes pas une banque.

**Exigence formelle :** Backup quotidien S3, rétention 30 jours, test de restauration mensuel. PITR et chiffrement pour v0.5.

---

### Position Sécurité Officer — « PAS DE CHIFFREMENT = BACKUP VULNÉRABLE »

**Énoncé :** Pas de backup chiffré. Si le compte AWS/S3 est compromis — phishing, clé fuite, IAM mal configuré — l'attaquant a accès à tous les backups. Les backups sont la cible privilégiée des ransomwares. « On a des backups » devient « l'attaquant a nos backups ».

**Arguments :**

1. **Le vecteur d'attaque backup :** Les ransomwares modernes ciblent d'abord les systèmes de backup. Pourquoi ? Parce que si les backups sont intacts, la victime ne paie pas la rançon. Un backup non chiffré est une cible d'or.

2. **La compromission de compte cloud :** Une clé AWS fuitée sur GitHub (ça arrive tout le temps) donne accès à S3. Si les backups sont en clair, l'attaquant télécharge l'intégralité des données.

3. **L'obligation RGPD :** L'article 32 impose la confidentialité des données. Un backup non chiffré en S3 est une faille de confidentialité. La CNIL a déjà sanctionné pour moins que ça.

4. **Le principe de défense en profondeur :** Chaque couche doit être indépendamment sécurisée. Le serveur est chiffré ? Bien. La DB est chiffrée ? Bien. Le backup est en clair ? Fail.

5. **Le coût du chiffrement :** AWS S3 propose le chiffrement côté serveur (SSE-S3, SSE-KMS) nativement. C'est un checkbox. C'est gratuit. Il n'y a AUCUNE excuse.

**Exigence formelle :** Chiffrement SSE-KMS obligatoire sur tous les buckets S3 contenant des backups. Clé KMS dédiée, rotation automatique. Tests de restauration depuis backup chiffré mensuels.

---

### Position DBA — « PAS DE PITR = PERTE DE DONNÉES JOURNALIÈRE »

**Énoncé :** Pas de PITR (Point-in-Time Recovery). Si quelqu'un supprime une table à 14h, on perd toutes les données de la journée. Le backup d'hier soir ne contient pas les données de ce matin. C'est inacceptable pour un système de production.

**Arguments :**

1. **Le scénario de suppression accidentelle :** Un développeur exécute un `DELETE FROM` sans WHERE. Un script de migration corrompt une table. Un bug de l'application efface des enregistrements. Ces scénarios arrivent constamment.

2. **Le RPO réel :** Sans PITR, le RPO est 24 heures. Avec PITR, le RPO est 5 minutes (ou moins). La différence entre perdre une journée de travail et perdre 5 minutes est énorme en termes de satisfaction utilisateur et de crédibilité.

3. **La disponibilité du PITR :** AWS RDS propose le PITR nativement pour PostgreSQL. C'est une option à cocher. Elle stocke les WAL (Write-Ahead Logs) jusqu'à 35 jours. Restauration à n'importe quel point dans cette fenêtre.

4. **Le coût du PITR :** Le stockage des WAL augmente le coût RDS de 10-20 %. Pour un MVP, c'est quelques euros par mois. C'est négligeable face au risque.

5. **L'image de marque :** « TAKA OS a perdu mes données de la journée à cause d'un bug » — ce tweet tue un projet. « TAKA OS a restauré mes données en 10 minutes » — ce tweet fait un champion.

**Exigence formelle :** PITR activé sur PostgreSQL RDS dès v0.1. Rétention 7 jours minimum (v0.1), 30 jours (v0.5). Test de restauration PITR mensuel.

---

## Débat

Le DevOps présente la configuration actuelle : « Backup RDS automatique, snapshot quotidien, rétention 30 jours. S3 bucket avec versioning. Test de restauration fait le mois dernier — 1h45 pour restaurer. »

Le Sécurité Officer attaque : « Le bucket S3 est en clair. J'ai vérifié. SSE désactivé. Si je trouve une clé AWS sur un repo public, j'ai accès à toutes les données de tous les utilisateurs. »

Le DevOps se défend : « C'est un oubli de configuration. Je corrige. SSE-S3 cette semaine. »

Le DBA insiste : « Et le PITR ? Tu l'as activé ? »

Le DevOps : « Non. Le backup quotidien me semblait suffisant. »

Le DBA : « Imagine : un utilisateur crée 20 appels d'offres dans la journée. À 16h, un bug efface tout. Le backup d'hier soir n'a rien. L'utilisateur a perdu une journée de travail. Pour un système agentic où les agents peuvent créer/modifier des données automatiquement, le risque est encore plus élevé. »

Le Compliance Legal appuie : « Article 32 RGPD : capacité de restaurer la disponibilité et l'accès aux données dans des délais appropriés. 24 heures de perte de données, c'est des délais appropriés pour une beta ? C'est discutable. »

Le QA Lead demande : « Quel est le RTO/RPO cible officiel du projet ? »

Silence. Puis le DevOps : « On n'en a pas défini. »

Le Sécurité Officer : « C'est le premier problème. Pas de SLA de backup = pas de politique de résilience. Je propose : RPO 1 heure, RTO 4 heures pour v0.1. RPO 5 minutes, RTO 1 heure pour v0.5. »

Le DBA : « RPO 1 heure sans PITR, c'est impossible. Il faut PITR + backups incrémentaux. »

Le Backend Senior : « Et la multi-région ? Si us-east-1 tombe ? »

Le DevOps : « Pour v0.1, c'est overkill. Pour v0.5, on peut répliquer en us-west-2. »

Le Sécurité Officer : « Le chiffrement, c'est maintenant. PITR, c'est maintenant. Multi-région, c'est v0.5. On différencie le must-have du nice-to-have. »

---

## Décision Q5

**DÉCISION PRINCIPALE :** La stratégie de backup actuelle est insuffisante pour tout déploiement en production. Le chiffrement SSE-KMS et le PITR sont rendus obligatoires avant ouverture de la beta. Un SLA de résilience (RPO/RTO) est formellement défini.

**Spécifications de la décision :**

1. **Avant ouverture beta v0.1 (bloquant) :**
   - Chiffrement SSE-KMS activé sur tous les buckets S3 contenant des backups
   - Clé KMS dédiée au projet, rotation automatique annuelle
   - PITR activé sur PostgreSQL RDS, rétention 7 jours minimum
   - Politique de backup documentée : quoi, quand, où, comment restaurer
   - Procédure de restauration testée et documentée (runbook)

2. **SLA de résilience v0.1 :**
   - RPO (Recovery Point Objective) : 1 heure maximum
   - RTO (Recovery Time Objective) : 4 heures maximum
   - Les agents IA doivent pouvoir reprendre leur travail après restauration sans perte de contexte critique

3. **Pour v0.5 (public beta) :**
   - PITR rétention étendue à 30 jours
   - Backups incrémentaux en plus du snapshot quotidien
   - Réplication cross-région (us-east-1 → us-west-2 ou équivalent)
   - Tests de restauration automatisés (chaos engineering minimal)

4. **Pour v1.0 :**
   - Stratégie de backup multi-cloud (AWS + GCP ou Azure)
   - RPO 5 minutes, RTO 1 heure
   - Documentation des backups dans le DPA (Data Processing Agreement)

5. **Tests de restauration :**
   - Test manuel mensuel jusqu'à v0.5
   - Test automatisé hebdomadaire à partir de v0.5
   - Rapport de test archivé avec métriques (temps de restauration, intégrité des données)

6. **Monitoring des backups :**
   - Alertes si backup quotidien non réalisé dans les 24h
   - Alertes si PITR non disponible
   - Dashboard de santé des backups accessible à l'équipe

---

## Actions Q5

| N° | Action | Responsable | Deadline | Priorité | Critère d'acceptation |
|----|--------|-------------|----------|----------|----------------------|
| A5.1 | Activer SSE-KMS sur tous les buckets S3 de backup | DevOps | 2025-01-28 | CRITIQUE | Buckets chiffrés, clé KMS dédiée créée, audit AWS passé |
| A5.2 | Activer PITR sur PostgreSQL RDS (rétention 7 jours) | DevOps | 2025-01-28 | CRITIQUE | PITR actif, test de restauration à un point dans les 24h réussi |
| A5.3 | Documenter la politique de backup (runbook) | Tech Writer | 2025-02-04 | HAUTE | Document ops/BACKUP_POLICY.md validé par DBA |
| A5.4 | Définir et publier le SLA de résilience (RPO/RTO) | DevOps | 2025-02-04 | HAUTE | SLA publié dans docs/SLA.md, validé par Sécurité Officer |
| A5.5 | Réaliser test de restauration complet + mesure RTO | DBA | 2025-02-11 | HAUTE | RTO mesuré < 4h, données intactes, rapport signé |
| A5.6 | Mettre en place monitoring backup + alertes | DevOps | 2025-02-11 | MOYENNE | Alertes configurées, dashboard accessible |
| A5.7 | Préparer plan multi-région backup (v0.5) | DevOps | 2025-03-04 | MOYENNE | Plan technique rédigé, coûts estimés |
| A5.8 | Implémenter tests de restauration automatisés | Test Automation | 2025-03-18 | MOYENNE | Job CI de test de restauration fonctionnel |

---

# Q6 — LA RGAA ACCESSIBILITÉ : PEUT-ON VRAIMENT ATTEINDRE AA EN V0.5 ?

## Positions

### Position QA Lead — « OUI. HTML SÉMANTIQUE + ARIA. 2-3 JOURS. »

**Énoncé :** Oui, atteindre le niveau AA du RGAA en v0.5 est réalisable. C'est surtout du HTML sémantique correct, des aria-labels appropriés, des contrastes de couleurs conformes. Pour un MVP de cette taille, 2 à 3 jours de travail concentré suffisent.

**Arguments :**

1. **La simplicité du périmètre :** TAKA OS v0.5 a un périmètre UI limité : authentification, tableau de bord, liste des appels d'offres, formulaire d'upload, résultats de parsing, paramètres. Ce n'est pas une application bancaire avec 400 écrans.

2. **Les critères AA sont majoritairement techniques :** Contrastes (3:1 pour UI, 4.5:1 pour texte), structure sémantique (header, nav, main, footer), aria-labels sur les icônes, focus visible, navigation clavier. Ce sont des règles vérifiables automatiquement.

3. **Les outils d'audit :** axe-core, Lighthouse, WAVE, pa11y. Ces outils détectent 80 % des problèmes AA automatiquement. Un audit manuel de 2 heures trouve le reste.

4. **L'accessibilité comme avantage :** Pour les acheteurs publics, l'accessibilité est une obligation légale (loi de 2005). Un outil non accessible ne peut pas être utilisé par les administrations. C'est un critère de sélection.

5. **Le coût opportunité :** 2-3 jours de travail pour être conforme à une obligation légale et ouvrir un marché entier (administrations publiques). Le ROI est évident.

**Exigence formelle :** Conformité RGAA niveau AA sur 100 % des pages v0.5. Audit automatique axe-core à chaque PR. Audit manuel avant chaque release mineure.

---

### Position UI Designer — « NON. KANBAN DRAG-DROP + GRAPHES, C'EST COMPLEXE. »

**Énoncé :** Non. Atteindre AA complet en v0.5 n'est pas si simple. Le Kanban drag-drop accessible est complexe. Les graphiques doivent avoir des alternatives textuelles riches. Les modales doivent gérer le focus trap. Les notifications doivent être annoncées aux lecteurs d'écran. C'est 1-2 semaines, pas 2-3 jours.

**Arguments :**

1. **Le Kanban drag-drop :** Un Kanban avec drag-and-drop (D&D) est l'un des composants les plus difficiles à rendre accessible. Il faut des alternatives clavier (boutons « Déplacer vers »), des annonces ARIA live pour les changements de position, des indicateurs visuels de focus, gestion du multi-sélection. Ce n'est pas trivial.

2. **Les graphiques et visualisations :** Les graphiques de statistiques (répartition des AO, timeline, montants) doivent avoir des alternatives textuelles équivalentes. Un `alt` sur une image de graphique ne suffit pas. Il faut des tableaux de données accessibles, des descriptions longues, des interactions clavier sur les points de données.

3. **La gestion du focus :** Les modales doivent piéger le focus (focus trap). Les menus dropdown doivent gérer les flèches du clavier. Les notifications toast doivent être annoncées sans interrompre la navigation. Ces comportements sont complexes à implémenter correctement.

4. **Les tests avec lecteurs d'écran :** Un audit automatique ne suffit pas. Il faut tester avec NVDA, JAWS, VoiceOver. Chaque lecteur d'écran a des comportements différents. C'est du temps de test réel.

5. **Le coût réel :** Pour un composant Kanban accessible + graphiques accessibles + modales + notifications + formulaires complexes, on parle de 1 à 2 semaines de travail d'un développeur frontend expérimenté en accessibilité. Ce n'est pas 2-3 jours.

**Exigence formelle :** AA partiel en v0.5 (pages statiques + formulaires simples). AA complet en v0.7 (tous les composants interactifs complexes). Plan d'accessibilité documenté avec priorités.

---

## Débat

Le QA Lead présente un audit rapide : « J'ai passé axe-core sur les 12 pages actuelles. Résultat : 23 violations. 18 sont des contrastes insuffisants. 3 sont des aria-labels manquants. 2 sont des structures sémantiques incorrectes. Avec un sprint de 2 jours, on corrige tout ça. »

L'UI Designer répond : « axe-core ne teste pas le Kanban. Il ne teste pas les graphiques. Il ne teste pas la navigation au clavier dans les modales. Les 23 violations, c'est pour les pages simples. Les composants complexes, c'est un autre monde. »

Le Compliance Legal intervient : « La loi oblige le niveau AA pour les services publics et les services rendus au public. TAKA OS cible les acheteurs publics. Donc soit on atteint AA, soit on ne peut pas vendre aux administrations. Il n'y a pas de demi-mesure légale. »

Le QA Lead nuance : « La loi française (loi n°2005-102) oblige le niveau AA pour les services publics en ligne. Mais les sanctions ne sont pas appliquées de manière stricte en pratique. Cependant, pour un appel d'offres public, l'accessibilité est un critère d'évaluation. Un outil non accessible est éliminatoire. »

Le Product Manager : « Quel est le périmètre critique ? Quelles pages doivent être AA pour que l'outil soit utilisable par une administration ? »

Le UI Designer : « Le parcours critique : login → dashboard → upload PDF → résultats → génération réponse. Si ce parcours est AA, les autres pages (paramètres, admin) peuvent attendre v0.7. »

Le QA Lead : « D'accord sur le parcours critique. Mais je maintiens que c'est réalisable en v0.5. Le Kanban n'est pas dans le parcours critique de consultation d'AO. C'est un outil de workflow interne. »

Le Tech Writer : « Et la documentation ? Elle doit être accessible aussi. Les PDF de documentation doivent être accessibles (PDF/UA). C'est un critère AA. »

Le Sécurité Officer : « L'accessibilité n'est pas juste légale, c'est sécuritaire. Un utilisateur qui ne peut pas utiliser l'interface correctement cherchera des contournements, des scripts, des raccourcis. L'accessibilité propre réduit la surface d'attaque. »

---

## Décision Q6

**DÉCISION PRINCIPALE :** Le niveau AA RGAA est obligatoire pour le parcours critique (login → dashboard → upload → résultats → génération) dès v0.5. Les pages secondaires (paramètres avancés, admin, Kanban complet) visent AA pour v0.7. Un audit AA formel est commandité avant v0.5.

**Spécifications de la décision :**

1. **Parcours critique AA obligatoire v0.5 :**
   - Authentification (login, MFA, récupération de mot de passe)
   - Tableau de bord (lecture des AO, navigation, filtres)
   - Upload de PDF (formulaire, feedback, erreurs)
   - Résultats de parsing (affichage des champs extraits, corrections)
   - Génération de réponse (paramètres, preview, export)
   - Toutes ces pages doivent passer un audit axe-core avec 0 violation critique

2. **Pages secondaires cible AA v0.7 :**
   - Paramètres avancés utilisateur
   - Interface d'administration
   - Kanban drag-drop (avec alternative clavier complète)
   - Graphiques et visualisations (avec alternatives textuelles riches)
   - Notifications temps réel (ARIA live regions)

3. **Audit formel :**
   - Audit interne (équipe + outils automatiques) avant v0.5
   - Audit externe par cabinet spécialisé RGAA avant v0.7 (budget à prévoir)
   - Rapport d'audit publié dans la documentation

4. **Processus d'intégration :**
   - axe-core intégré au CI (échec de build si violation critique)
   - Checklist accessibilité dans le template de PR
   - Revue de code systématique incluant accessibilité
   - Tests avec lecteurs d'écran (NVDA) avant chaque release mineure

5. **Documentation accessible :**
   - Site de documentation en HTML sémantique (pas que PDF)
   - Vidéos de tutoriel avec sous-titres obligatoires
   - PDF de référence conformes PDF/UA (ISO 14289)

---

## Actions Q6

| N° | Action | Responsable | Deadline | Priorité | Critère d'acceptation |
|----|--------|-------------|----------|----------|----------------------|
| A6.1 | Corriger les 23 violations axe-core identifiées | UI Designer | 2025-02-04 | CRITIQUE | axe-core passe avec 0 violation critique sur parcours critique |
| A6.2 | Intégrer axe-core au CI (échec sur violation) | Test Automation | 2025-02-04 | CRITIQUE | Job CI axe-core intégré, build rouge si violation |
| A6.3 | Implémenter parcours critique accessible (focus, aria, contrastes) | UI Designer | 2025-02-18 | CRITIQUE | Parcours testé au clavier, lecteur d'écran, contrastes validés |
| A6.4 | Créer alternative clavier pour Kanban (même si hors parcours critique) | UI Designer | 2025-02-25 | MOYENNE | Kanban utilisable sans souris |
| A6.5 | Ajouter alternatives textuelles aux graphiques | UI Designer | 2025-02-25 | MOYENNE | Graphiques avec descriptions longues, tableaux de données |
| A6.6 | Rédiger checklist accessibilité pour PR | Tech Writer | 2025-02-11 | MOYENNE | Template PR avec section accessibilité obligatoire |
| A6.7 | Réaliser audit interne RGAA complet | QA Lead | 2025-03-04 | MOYENNE | Rapport d'audit interne publié, écarts identifiés |
| A6.8 | Tester documentation avec lecteur d'écran | Tech Writer | 2025-02-18 | MOYENNE | Documentation utilisable avec NVDA |
| A6.9 | Planifier audit externe RGAA (v0.7) | Compliance Legal | 2025-04-01 | FAIBLE | Cabinet identifié, devis obtenu |

---

# Q7 — CIRCUIT BREAKER SUR MISTRAL API : COMMENT LE TESTER ?

## Positions

### Position Test Automation — « MOCK + SIMULATION DE DÉFAILLANCE »

**Énoncé :** On mock Mistral API pour simuler 5 échecs successifs. On vérifie que le circuit breaker s'ouvre après le seuil configuré, et que le fallback retourne une réponse gracieuse. C'est testable, déterministe, et automatisé.

**Arguments :**

1. **Le pattern de test par mock :** Pour les dépendances externes, le mock est le standard. On remplace l'appel HTTP réel par une fonction contrôlée qui retourne des réponses programmées. Cela isole le test du réseau, des quotas, des indisponibilités réelles.

2. **La séquence de test :** Test 1-4 : appel normal, succès. Test 5-9 : appel avec erreur 500, vérification du compteur d'échecs. Test 10 : 5ème échec, vérification que le circuit passe à OPEN. Test 11 : appel suivant, vérification que le circuit rejette immédiatement sans appeler l'API. Test 12 : attente du timeout, vérification que le circuit passe à HALF-OPEN.

3. **La validation du fallback :** Quand le circuit est OPEN, le système doit retourner une réponse de fallback : message utilisateur (« Service temporairement indisponible, veuillez réessayer »), log d'audit, éventuellement mise en file d'attente pour retry.

4. **L'intégration au CI :** Ces tests sont rapides (< 1 seconde), déterministes, sans dépendance réseau. Parfait pour le CI.

5. **La couverture des scénarios :** Il faut tester : échecs 500, échecs timeout, échecs réseau (ConnectionError), échecs 429 (rate limit), récupération progressive (circuit qui repasse à CLOSED après succès).

**Exigence formelle :** Tests unitaires + intégration avec mock Mistral API. Couverture 100 % des états du circuit breaker (CLOSED, OPEN, HALF-OPEN). Tests dans le CI principal.

---

### Position QA Lead — « TEST D'INTÉGRATION, PAS UNITAIRE. MOCK SERVER NÉCESSAIRE. »

**Énoncé :** C'est un test d'intégration, pas unitaire. Le circuit breaker est un composant transversal qui implique : configuration, état partagé (potentiellement distribué), timeout, fallback, logging. Un vrai test nécessite un mock server HTTP, pas juste un mock de fonction.

**Arguments :**

1. **La nature du circuit breaker :** Un circuit breaker n'est pas une fonction isolée. Il intercepte des appels HTTP, maintient un état, gère des transitions temporelles. Un mock de fonction masque la complexité réelle du protocole HTTP.

2. **Le mock server vs. le mock de fonction :** Un mock de fonction (patch `requests.post`) simule le code. Un mock server (WireMock, Mountebank, un simple Flask/FastAPI de test) simule le réseau. Pour un circuit breaker, le mock server est plus réaliste car il teste aussi la gestion des timeouts, des headers, des retries.

3. **L'état distribué :** Si TAKA OS déploie plusieurs instances (même en v0.5), le circuit breaker pourrait être partagé (Redis). Un test unitaire ne teste pas la cohérence d'état entre instances.

4. **La performance sous charge :** Un circuit breaker doit fonctionner sous charge. Un test de charge (100 requêtes simultanées) vérifie qu'il n'y a pas de race condition sur l'état du circuit.

5. **La classification des tests :** Ces tests sont des tests d'intégration, pas des tests unitaires. Ils doivent être dans la suite d'intégration, pas dans la suite unitaire. Leur exécution est plus lente (quelques secondes), mais plus réaliste.

**Exigence formelle :** Tests d'intégration avec mock server HTTP (pytest + Flask de test ou WireMock). Tests de race condition. Tests dans la suite d'intégration, pas unitaire.

---

## Débat

Le Test Automation présente son implémentation : « J'ai écrit un test avec pytest + responses. Il simule 5 erreurs 500, vérifie l'ouverture du circuit, teste le fallback. Ça prend 200 ms. C'est dans le CI. »

Le QA Lead examine : « C'est bien pour un premier test. Mais ça mock `requests`. Si on passe à `httpx` ? Si on change la bibliothèque HTTP ? Le test devient inutile. Il faut un niveau d'abstraction plus élevé. »

Le Backend Senior : « J'ai implémenté le circuit breaker avec `pybreaker`. C'est une bibliothèque qui encapsule l'appel. On peut l'injecter comme dépendance. Le test devrait mocker `pybreaker` lui-même ? Ou mocker l'appel sous-jacent ? »

Le Test Automation : « Le principe est : on teste le comportement, pas l'implémentation. Si je remplace `pybreaker` par une autre librairie, les tests doivent toujours passer. Donc je teste au niveau de notre wrapper, pas de la librairie. »

Le Sécurité Officer : « Et les attaques par déni de service ? Si quelqu'un force le circuit breaker à s'ouvrir intentionnellement ? Le circuit doit résister aux attaques de type « forcing the circuit ». »

Le DevOps : « En production, on a aussi le rate limiting Nginx. Le circuit breaker est une protection supplémentaire, pas la seule. »

Le QA Lead propose : « Créons une stratégie de test en 3 niveaux :  
   - Niveau 1 (unitaire) : test du wrapper circuit breaker avec mock de fonction — rapide, CI principal  
   - Niveau 2 (intégration) : test avec mock server HTTP — plus lent, CI d'intégration  
   - Niveau 3 (E2E/stress) : test de charge avec vrai serveur de test — plus lent, nightly  
   »

Le Test Automation : « D'accord. Et ajoutons un test de « circuit forcing » : un client qui envoie 1000 requêtes en 10 secondes. Le rate limit doit agir avant le circuit breaker. Le circuit ne doit pas s'ouvrir à cause d'un seul client abusif. »

Le Backend Senior : « Pour le niveau 2, je propose un mock server avec `pytest-httpserver`. C'est léger, intégré à pytest, pas de dépendance externe. Il lance un vrai serveur HTTP local. On teste les timeouts réels, les headers, les retries. »

Le DevOps : « Et pour le niveau 3, je peux lancer un conteneur de test qui simule Mistral avec des latences variables. On injecte du chaos : 500ms de latence, puis timeout, puis recovery. C'est du chaos engineering minimal. »

---

## Décision Q7

**DÉCISION PRINCIPALE :** Le circuit breaker Mistral API est testé selon une stratégie en 3 niveaux : tests unitaires avec mock (CI principal), tests d'intégration avec mock server HTTP (CI intégration), tests de charge/chaos (nightly). Chaque niveau a des objectifs de couverture distincts.

**Spécifications de la décision :**

1. **Niveau 1 — Tests unitaires (CI principal, < 1s) :**
   - Mock de la fonction wrapper circuit breaker
   - Scénarios : succès, échecs successifs, ouverture circuit, fallback, demi-ouverture, récupération
   - Couverture cible : 100 % des branches du wrapper
   - Responsable : Test Automation
   - Outil : pytest + unittest.mock

2. **Niveau 2 — Tests d'intégration (CI intégration, < 10s) :**
   - Mock server HTTP local (pytest-httpserver)
   - Scénarios : timeouts réels, erreurs HTTP variées (400, 429, 500, 503), headers, retries
   - Test de race condition (appels simultanés)
   - Couverture cible : tous les codes HTTP et états réseau gérés
   - Responsable : QA Lead
   - Outil : pytest-httpserver

3. **Niveau 3 — Tests de charge/chaos (CI nightly, < 5min) :**
   - Conteneur de test simulant Mistral avec latence variable
   - Scénarios : circuit forcing, charge simultanée, recovery progressive, dégradation gracieuse
   - Métriques : temps de réponse p95, taux d'erreur acceptable, temps de récupération
   - Responsable : DevOps + Sécurité Officer
   - Outil : k6 ou Locust + conteneur de test

4. **Protection contre le circuit forcing :**
   - Le rate limit Nginx doit être configuré pour qu'un client unique ne puisse pas forcer l'ouverture du circuit
   - Le circuit breaker est global (tous les clients), pas par client
   - Test spécifique : 1000 requêts d'un client unique → rate limit déclenché, circuit reste CLOSED

5. **Fallback obligatoire :**
   - Quand le circuit est OPEN : message utilisateur clair, log d'audit, file d'attente pour retry différé
   - Le fallback ne doit pas exposer de données sensibles (pas de stack trace, pas de détails d'erreur interne)
   - Test : vérification que le fallback est conforme RGPD (pas de fuite d'information)

---

## Actions Q7

| N° | Action | Responsable | Deadline | Priorité | Critère d'acceptation |
|----|--------|-------------|----------|----------|----------------------|
| A7.1 | Implémenter tests unitaires circuit breaker (niveau 1) | Test Automation | 2025-02-04 | CRITIQUE | 100% branches couvertes, CI passe < 1s |
| A7.2 | Implémenter tests d'intégration avec pytest-httpserver (niveau 2) | QA Lead | 2025-02-18 | HAUTE | Tous codes HTTP testés, race conditions vérifiées |
| A7.3 | Configurer CI intégration (séparé du CI principal) | DevOps | 2025-02-11 | HAUTE | CI intégration fonctionnel, exécuté à chaque PR |
| A7.4 | Implémenter conteneur mock Mistral pour tests chaos | Backend Senior | 2025-02-25 | MOYENNE | Conteneur configurable (latence, erreurs, recovery) |
| A7.5 | Implémenter tests de charge circuit breaker (niveau 3) | DevOps | 2025-03-04 | MOYENNE | k6/Locust configuré, scénarios de charge validés |
| A7.6 | Configurer rate limit anti-circuit-forcing | DevOps | 2025-02-11 | HAUTE | Test de forcing passe : circuit reste CLOSED |
| A7.7 | Documenter la stratégie de test circuit breaker | Tech Writer | 2025-02-25 | MOYENNE | Document docs/TESTING_CIRCUIT_BREAKER.md publié |
| A7.8 | Vérifier conformité RGPD du fallback (pas de fuite) | Compliance Legal | 2025-02-18 | MOYENNE | Audit des messages d'erreur, aucune fuite d'info |

---

# Q8 — LA DOCUMENTATION : QUI LA MAINTIENT ?

## Positions

### Position Tech Writer — « MOI. MAIS IL ME FAUT DES SPECS STABLES. »

**Énoncé :** C'est mon rôle de maintenir la documentation. Mais il me faut des spécifications stables. Pas de documentation sur du code qui change tous les 2 jours. La documentation est un contrat avec l'utilisateur. Un contrat qui change constamment n'a aucune valeur.

**Arguments :**

1. **La stabilité comme précondition :** La documentation technique (API reference, architecture, guides contributeur) repose sur la stabilité des interfaces. Si l'API change sans préavis, la documentation est obsolète avant d'être publiée.

2. **Le coût de la maintenance :** Chaque changement d'API nécessite une mise à jour de la doc. Si l'API change tous les 2 jours, le Tech Writer passe son temps à rattraper. C'est inefficace et démoralisant.

3. **La crédibilité :** Une documentation obsolète est pire que pas de documentation. Les utilisateurs perdent confiance. Les contributeurs abandonnent. « La doc dit X mais le code fait Y » est le pire type de feedback.

4. **Le processus de documentation :** Il faut un processus : 1) spécification stable validée, 2) code implémenté selon spec, 3) documentation rédigée, 4) revue code + doc en parallèle, 5) publication synchronisée.

5. **Les types de documentation :**  
   - **Doc technique (dev) :** API reference, architecture, contribution guide — maintenue par Tech Writer, entrée : spec stable  
   - **Doc utilisateur (Help Center) :** Tutoriels, FAQ, guides d'utilisation — maintenue par Tech Writer + Product Manager  
   - **Doc réglementaire (compliance) :** RGPD, AI Act, sécurité — maintenue par Compliance Legal, validée par Tech Writer  

**Exigence formelle :** Processus « doc-as-code » avec spécifications stables. Aucune doc publiée sans spec validée. Revue de documentation systématique dans le flux de release.

---

### Position Product Manager — « HELP CENTER DOIT SUIVRE LES RELEASES. AUTOMATISER. »

**Énoncé :** La documentation utilisateur (Help Center) doit suivre les releases. Automatiser avec des screenshots, des vidéos, des changelogs générés. La doc ne doit pas être un frein à la vélocité, elle doit être un produit de la release.

**Arguments :**

1. **La vélocité vs. la documentation :** Si la doc est un goulot d'étranglement, les développeurs contourneront le processus. Ils ne documenteront pas. Le projet deviendra un projet sans doc.

2. **L'automatisation :** Les screenshots de l'interface peuvent être générés automatiquement (Playwright + screenshot). Les changelogs peuvent être générés à partir des commits (conventional commits + semantic release). L'API reference peut être générée à partir des docstrings (Sphinx, MkDocs).

3. **La documentation comme critère de release :** Une PR n'est pas mergée sans mise à jour de la documentation associée. C'est une règle de qualité. Mais la mise à jour doit être légère : changelog + mise à jour de la page de doc concernée.

4. **Le format de documentation :** Docusaurus pour la doc utilisateur (belle, searchable, versionnée). MkDocs + Material pour la doc technique (proche du code, générable depuis les sources). Le tout dans le repo Git, versionné avec le code.

5. **La doc dans le flux de release :**  
   - v0.1 : README + CONTRIBUTING + ARCHITECTURE  
   - v0.3 : Help Center Docusaurus + API reference auto-générée  
   - v0.5 : Documentation complète utilisateur + compliance  
   - v1.0 : Documentation certifiée, traduite (FR/EN minimum)

**Exigence formelle :** Doc-as-code dans le repo Git. Génération automatique API reference + changelogs. Screenshots automatiques. Docusaurus pour help center. Pas de release sans doc mise à jour.

---

## Débat

Le Tech Writer ouvre avec un constat : « Actuellement, le README a 3 mois. CONTRIBUTING a 2 mois. L'API reference n'existe pas. Un nouveau contributeur met 2 jours à comprendre comment lancer le projet. C'est une barrière d'entrée massive. »

Le Product Manager : « D'accord sur le problème. La solution n'est pas de recruter un armée de tech writers. C'est d'automatiser et d'intégrer la doc dans le flux de dev. Chaque PR doit inclure la mise à jour de la doc associée. »

Le Tech Writer : « Je suis d'accord sur le principe. Mais « chaque PR inclut la doc » implique que les développeurs savent écrire de la doc. La plupart ne savent pas. Ils écrivent des docstrings techniques, pas des guides utilisateur. Il faut les deux. »

Le QA Lead : « Et la doc des tests ? On a décidé en Q1 que chaque suite de tests > 10 cas a un TEST_STRATEGY.md. Qui le rédige ? »

Le Tech Writer : « Moi. Mais il me faut les informations du développeur. Je peux structurer, clarifier, mais je ne peux pas inventer l'oracle d'un test. »

Le Backend Senior : « On peut générer des templates. Quand un dev crée une nouvelle suite de tests, un template TEST_STRATEGY.md est généré automatiquement avec les sections à remplir. Le dev remplit, le Tech Writer révise. »

Le Compliance Legal : « La doc réglementaire (RGPD, AI Act) est spécifique. C'est du droit, pas de la technique. Je la rédige. Mais il faut une relecture par le Tech Writer pour la clarté. Et une validation par un juriste externe pour la solidité. »

Le Test Automation : « Et les screenshots automatiques ? J'ai vu des projets où les screenshots sont générés à chaque CI. Mais ça prend du temps. Et il faut un environnement de test stable. »

Le DevOps : « On peut lancer Playwright en mode headless dans le CI, prendre des screenshots des pages clés, les comparer avec les screenshots de référence. Si une page change visuellement, le screenshot est mis à jour (après validation manuelle). »

Le Product Manager synthétise : « Voici ma proposition :  
   1. Doc technique dans le repo (MkDocs) — maintenue par les devs + Tech Writer  
   2. Help Center (Docusaurus) — maintenue par Tech Writer + Product Manager, avec screenshots auto  
   3. Doc réglementaire — maintenue par Compliance Legal, relue par Tech Writer  
   4. Règle : pas de merge sans doc mise à jour (pour les features, pas les bugfixes)  
   5. Processus : spec → code → doc → revue → merge  
   »

Le Tech Writer approuve avec une réserve : « D'accord, mais je veux un « freeze doc » 48h avant release. Pas de changement de code dans les 48h précédant la release, sauf hotfix. Sinon je ne peux pas garantir la cohérence doc/code. »

---

## Décision Q8

**DÉCISION PRINCIPALE :** La documentation adopte une stratégie « doc-as-code » intégrée au flux de release, avec des outils et responsabilités différenciés par type de documentation. Un « doc freeze » de 48h avant release est instauré pour garantir la cohérence.

**Spécifications de la décision :**

1. **Architecture documentaire :**
   - **Doc technique (repo Git, MkDocs + Material) :** Architecture, API reference, guides contributeur, testing strategy
   - **Help Center utilisateur (Docusaurus, site dédié) :** Tutoriels, FAQ, guides pas à pas, vidéos
   - **Doc réglementaire (MkDocs, section dédiée) :** RGPD, AI Act, sécurité, compliance
   - **Doc ops (repo Git, Markdown) :** Runbooks, procédures de déploiement, backup, incident response

2. **Responsabilités :**
   - Tech Writer : responsable éditorial de la doc technique + Help Center. Structure, clarté, cohérence.
   - Product Manager : contenu métier du Help Center. Priorités, messages clés, parcours utilisateur.
   - Compliance Legal : contenu réglementaire. Validité juridique, conformité.
   - Développeurs : docstrings, guides techniques spécifiques, mise à jour API reference.
   - DevOps : doc ops, runbooks, procédures.

3. **Processus doc-as-code :**
   - Chaque feature PR doit inclure la mise à jour de la documentation associée (bugfix exempté)
   - Template de PR avec checklist doc obligatoire
   - Revue de documentation en parallèle de la revue de code
   - Doc freeze 48h avant release (pas de merge de code, sauf hotfix critique)
   - Publication automatique de la doc à chaque release (CI/CD)

4. **Automatisation :**
   - API reference auto-générée depuis les docstrings (Sphinx ou équivalent)
   - Changelogs auto-générés depuis les conventional commits
   - Screenshots automatiques des pages clés via Playwright CI
   - Vérification de liens cassés à chaque build (markdown-link-check)

5. **Qualité de la documentation :**
   - Chaque page de doc doit avoir un propriétaire (owner) identifié
   - Date de dernière mise à jour affichée sur chaque page
   - Système de feedback (« Cette page vous a-t-elle aidé ? »)
   - Revue trimestrielle complète de la documentation

6. **Internationalisation :**
   - v0.5 : Français (principal) + Anglais (secondaire)
   - v1.0 : Allemand + Espagnol selon adoption géographique

---

## Actions Q8

| N° | Action | Responsable | Deadline | Priorité | Critère d'acceptation |
|----|--------|-------------|----------|----------|----------------------|
| A8.1 | Mettre en place MkDocs + Material pour doc technique | Tech Writer | 2025-02-04 | CRITIQUE | Site doc technique généré, déployé, versionné |
| A8.2 | Mettre en place Docusaurus pour Help Center | Tech Writer | 2025-02-18 | CRITIQUE | Help Center en ligne, searchable, versionné |
| A8.3 | Créer template PR avec checklist documentation | Tech Writer | 2025-02-04 | HAUTE | Template intégré au repo, utilisé sur les 5 prochaines PR |
| A8.4 | Implémenter génération auto API reference depuis docstrings | Test Automation | 2025-02-11 | HAUTE | API reference générée, à jour avec le code |
| A8.5 | Configurer génération auto changelogs (conventional commits) | DevOps | 2025-02-11 | MOYENNE | Changelog généré automatiquement à chaque release |
| A8.6 | Implémenter screenshots automatiques Playwright | Test Automation | 2025-02-25 | MOYENNE | Screenshots clés générés à chaque CI, comparés |
| A8.4 | Rédiger documentation actuelle (README, CONTRIBUTING, ARCHITECTURE) | Tech Writer | 2025-02-11 | HAUTE | README à jour, CONTRIBUTING clair, ARCHITECTURE complète |
| A8.8 | Créer template TEST_STRATEGY.md pour suites de tests | Tech Writer | 2025-02-18 | MOYENNE | Template créé, utilisé pour les 3 prochaines suites |
| A8.9 | Configurer vérification liens cassés dans CI | DevOps | 2025-02-18 | MOYENNE | markdown-link-check intégré au CI |
| A8.10 | Définir et publier le processus doc-as-code | Tech Writer | 2025-02-11 | HAUTE | Document PROCESSUS_DOCUMENTATION.md publié et appliqué |

---

# SYNTHÈSE EXÉCUTIVE — MATRICE DES DÉCISIONS

| Question | Décision clé | Niveau de risque | Impact version |
|----------|-------------|-----------------|---------------|
| Q1 — Tests | Bimodal : déterministe 90% + probabiliste 85% confiance | ÉLEVÉ (qualité perçue) | v0.3 / v0.5 |
| Q2 — Parsing PDF | Qualité par classe (A:97%, B:90%, C:75%+fallback) | CRITIQUE (données métier) | v0.5 |
| Q3 — Sécurité MVP | S-MVP obligatoire avant beta (OWASP + chiffrement + PITR) | CRITIQUE (données, légal) | v0.1 |
| Q4 — AI Act | Niveau 2 en v0.5, niveau 3 en v1.5, avis juridique avant v0.3 | CRITIQUE (réglementaire) | v0.3 / v0.5 / v1.5 |
| Q5 — Backups | SSE-KMS + PITR 7j avant beta. Multi-région v0.5 | ÉLEVÉ (résilience) | v0.1 / v0.5 |
| Q6 — RGAA AA | Parcours critique AA en v0.5, complet en v0.7 | ÉLEVÉ (légal, marché public) | v0.5 / v0.7 |
| Q7 — Circuit breaker | Tests 3 niveaux : unitaire + intégration + chaos | MOYEN (résilience) | v0.5 |
| Q8 — Documentation | Doc-as-code, 48h freeze, Docusaurus + MkDocs | MOYEN (adoption) | v0.3 / v0.5 |

---

# MATRICE DES ACTIONS — VUE CONSOLIDÉE

## Actions CRITIQUES (bloquant beta v0.1)

| N° | Action | Responsable | Deadline |
|----|--------|-------------|----------|
| A3.1 | Auditer vulnérabilités OWASP Top 10 | Sécurité Officer | 2025-01-28 |
| A3.2 | Corriger XSS + CSRF + injection | Backend Senior | 2025-02-04 |
| A3.3 | TLS 1.3 + CSP + rate limit | DevOps | 2025-02-04 |
| A5.1 | SSE-KMS sur buckets S3 | DevOps | 2025-01-28 |
| A5.2 | PITR PostgreSQL RDS 7j | DevOps | 2025-01-28 |

## Actions CRITIQUES (bloquant v0.3)

| N° | Action | Responsable | Deadline |
|----|--------|-------------|----------|
| A1.3 | 90% coverage couche 1 | Test Automation | 2025-02-18 |
| A3.5 | OWASP ZAP dans CI | Test Automation | 2025-02-11 |
| A3.6 | Logs d'audit immutables | Backend Senior | 2025-02-18 |
| A3.7 | Registre RGPD | Compliance Legal | 2025-02-18 |
| A4.2 | AI Act Compliance Board | Compliance Legal | 2025-02-04 |
| A4.3 | Niveau 1 transparence AI Act | Backend Senior | 2025-02-18 |
| A8.1 | MkDocs doc technique | Tech Writer | 2025-02-04 |

## Actions CRITIQUES (bloquant v0.5)

| N° | Action | Responsable | Deadline |
|----|--------|-------------|----------|
| A1.4 | Framework évaluation IA (couche 3) | Backend Senior | 2025-02-18 |
| A1.5 | Tableau de bord qualité public | Tech Writer | 2025-02-11 |
| A2.1 | Corpus 100 PDF annotés | QA Lead | 2025-02-04 |
| A2.3 | Score de confiance parsing | Backend Senior | 2025-02-18 |
| A2.4 | CI régression parsing | Test Automation | 2025-02-18 |
| A3.8 | MFA optionnel + avertissement | Backend Senior | 2025-02-25 |
| A3.9 | Plan pentest interne v0.3 | Sécurité Officer | 2025-03-04 |
| A4.1 | Avis juridique AI Act | Compliance Legal | 2025-03-04 |
| A4.4 | Traçabilité IA complète | Backend Senior | 2025-02-25 |
| A5.5 | Test restauration complet | DBA | 2025-02-11 |
| A6.1 | Corriger violations axe-core | UI Designer | 2025-02-04 |
| A6.2 | axe-core dans CI | Test Automation | 2025-02-04 |
| A6.3 | Parcours critique accessible | UI Designer | 2025-02-18 |
| A8.2 | Docusaurus Help Center | Tech Writer | 2025-02-18 |

---

# GLOSSAIRE — TERMES ET ACRONYMES

| Terme | Définition |
|-------|-----------|
| AI Act | Règlement européen sur l'intelligence artificielle (2024) |
| AO | Appel d'Offres |
| CSP | Content Security Policy — politique de sécurité des contenus web |
| DBA | Database Administrator |
| DDoS | Distributed Denial of Service — attaque par déni de service distribué |
| DPA | Data Processing Agreement — accord de traitement de données |
| DPO | Data Protection Officer — délégué à la protection des données |
| E2E | End-to-End — tests de bout en bout |
| FRIA | Fundamental Rights Impact Assessment — évaluation d'impact sur les droits fondamentaux |
| IAM | Identity and Access Management |
| KMS | Key Management Service — service de gestion de clés AWS |
| LLM | Large Language Model — grand modèle de langage |
| LMO | Liable Manager Operator — opérateur responsable (AI Act) |
| MFA | Multi-Factor Authentication — authentification multi-facteurs |
| MIT | Licence logicielle permissive (Massachusetts Institute of Technology) |
| MVP | Minimum Viable Product — produit minimum viable |
| OCR | Optical Character Recognition — reconnaissance optique de caractères |
| PITR | Point-in-Time Recovery — restauration à un instant précis |
| RPO | Recovery Point Objective — objectif de point de récupération |
| RTO | Recovery Time Objective — objectif de temps de récupération |
| RGAA | Référentiel Général d'Amélioration de l'Accessibilité |
| RGPD | Règlement Général sur la Protection des Données (GDPR) |
| SMQ | Système de Management de la Qualité |
| SOC | Security Operations Center — centre d'opérations de sécurité |
| SSE-KMS | Server-Side Encryption with AWS KMS — chiffrement côté serveur avec KMS |
| TOTP | Time-based One-Time Password — mot de passe à usage unique basé sur le temps |
| WAL | Write-Ahead Log — journal d'écriture préalable (PostgreSQL) |
| WAF | Web Application Firewall — pare-feu d'application web |
| XSS | Cross-Site Scripting — injection de scripts malveillants |

---

# CONCLUSION DU MODÉRATEUR

Le Groupe Qualité & Production a débattu huit questions critiques pour la viabilité technique, légale et commerciale de TAKA OS. Les conclusions sont sans appel :

1. **La qualité n'est pas négociable.** Trente tests ne suffisent pas. La stratégie bimodale (déterministe + probabiliste) est la seule approche crédible pour un système agentic.

2. **La sécurité n'est pas une option post-MVP.** Le S-MVP (Sécurité Minimum Viable Product) est un préalable à toute ouverture. Les vulnérabilités OWASP Top 10 doivent être corrigées, les backups chiffrés, le PITR activé.

3. **La conformité réglementaire est une obligation légale.** L'AI Act s'applique. Le niveau 2 en v0.5 et le niveau 3 en v1.5 constituent une feuille de route réaliste. L'avis juridique formel est impératif.

4. **L'accessibilité est un marché.** Sans conformité RGAA AA, les administrations publiques ne pourront pas adopter TAKA OS. Le parcours critique en v0.5 est le minimum.

5. **La documentation est un produit.** Pas un afterthought. La stratégie doc-as-code avec freeze de 48h garantit la cohérence entre code et documentation.

**Le Groupe Qualité & Production recommande au Comité de Direction Technique de valider l'ensemble des décisions et actions du présent compte-rendu. Le non-respect des actions CRITIQUES bloque les versions correspondantes.**

---

**Document certifié par le Modérateur du Groupe Qualité & Production**

*Sécurité Officer — Compliance Legal — QA Lead — Test Automation — Tech Writer*

**Référence :** CR-DEBAT-QUAL-2025-001  
**Version :** 1.0-FINAL  
**Classification :** DOCUMENT DE TRAVAIL — SOUMISSION CODIR  
**Date de certification :** 2025-01-21

---

*« La qualité n'est pas un acte, c'est une habitude. » — Aristote, adapté*

