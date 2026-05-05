# ANALYSE REGLEMENTAIRE EUROPEENNE — TAKA OS
## Systeme Agentic IA pour Appels d'Offres Publics en Europe
### Date : Mai 2026 | Expertise : Droit europeen des marches publics & Reglementation IA

---

## SOMMAIRE EXECUTIF

TAKA OS est **juridiquement viable en Union europeenne** sous reserve de trois ajustements majeurs pre-MVP. L'architecture open source (MIT), l'hebergement EU et la finalite d'assistance (non-decision automatisee) constituent des atouts reglementaires significatifs. Le risque principal ne vient pas de l'AI Act ni du droit des marches publics, mais de l'**utilisation d'un LLM chinois (Kimi API)** dans un contexte de donnees potentiellement sensibles, et des **obligations de transparence** qui s'appliquent des aout 2026.

| Rang | Risque | Niveau | Delai |
|------|--------|--------|-------|
| 1 | Utilisation de Kimi API (LLM chinois) — souverainete data + RGPD | 🔴 Eleve | MVP |
| 2 | Obligations de transparence AI Act Article 50 (aout 2026) | 🟡 Moyen | MVP |
| 3 | Responsabilite en cas d'erreur/hallucination dans candidature | 🟡 Moyen | MVP |

---

## 1. AI ACT EUROPEEN (REGLEMENT EU 2024/1689)

### 1.1 Classification de TAKA OS

TAKA OS releve de la categorie **« risque limite » (Limited Risk)** au sens de l'Article 50 du AI Act, et **non** de la categorie « haut risque ».

| Critere | Evaluation |
|---------|------------|
| **Système à haut risque (Annexe III) ?** | NON. TAKA OS n'est pas un systeme de biometrie, d'infrastructure critique, d'evaluation scolaire, de gestion de l'emploi, ni d'administration de la justice. Il s'agit d'un outil d'assistance a la redaction et d'analyse documentaire pour des soumissionnaires prives. |
| **Système a risque limite (Art. 50) ?** | **OUI**. TAKA OS integre un chatbot/agent conversationnel (assistant Kanban, scoring GO/NO-GO) et genere du contenu textuel (suggestions de memoires techniques). L'Article 50 s'applique aux « systemes d'IA qui interagissent directement avec des personnes physiques » et aux systemes generant du contenu synthetique. |
| **Système a risque minimal ?** | Non applicable, car la fonction de generation de texte et d'interaction conversationnelle place TAKA OS dans la categorie superieure. |
| **Pratique interdite (Art. 5) ?** | NON. Aucune des 8 pratiques interdites (scoring social, manipulation subliminale, reconnaissance emotionnelle en milieu de travail, etc.) ne s'applique. |

**Texte applicable :** Article 50, Article 3(1) et (3) du Reglement (UE) 2024/1689 ; guidelines de la Commission europeenne sur la definition des systemes d'IA (juillet 2025).

### 1.2 Obligations de transparence (Article 50 — applicable 2 aout 2026)

| Obligation | Applicabilite a TAKA OS | Mesure requise |
|------------|------------------------|----------------|
| **Art. 50(1)** — Informer l'utilisateur qu'il interagit avec une IA | ✅ Applicable (chatbot assistant Kanban, interface de scoring) | Mention claire et visible des la premiere interaction : « Assistant IA — TAKA OS » dans l'interface. Pas de simple mention en footer. |
| **Art. 50(2)** — Marquage machine-readable du contenu genere | ⚠️ Partiellement applicable | Les suggestions de texte pour memoires techniques doivent etre identifiables comme « generees par IA ». Watermarking textuel ou metadata suffisant. |
| **Art. 50(4)** — Deepfakes et texte d'interet public | ❌ Non applicable | TAKA OS ne genere pas de deepfakes ni de contenu mediatique grand public. |

**Sanctions :** Jusqu'a 7,5 M€ ou 1% du CA mondial (Article 99), avec proportionnalite pour les PME/startup.

### 1.3 Exemption open source — analyse detaillee

L'Article 2(12) du AI Act prevoit une exemption pour les systemes d'IA « diffuses sous une licence open source libre », **mais** :

> *« Le present reglement ne s'applique pas aux systemes d'IA diffuses sous une licence libre et open source, a moins qu'ils ne soient mis sur le marche ou mis en service comme systemes d'IA a haut risque ou comme systeme d'IA relevant de l'article 5 ou 50. »*

**Consequence pour TAKA OS :** L'exemption **NE S'APPLIQUE PAS**. Le MIT licence ne protege pas des obligations de l'Article 50 (transparence) car TAKA OS :
- Interagit directement avec des utilisateurs (chatbot/agent)
- Genere du contenu textuel synthetique

**Point positif :** Les obligations restent legeres — uniquement de la transparence, pas de documentation technique lourde, pas d'evaluation de conformite tierce, pas de marquage CE.

### 1.4 Obligations de documentation et traçabilite

| Obligation | TAKA OS (risque limite) | Systeme haut risque (ref.) |
|------------|------------------------|---------------------------|
| Documentation technique (Art. 11) | ❌ Non requise | ✅ Requise |
| Systeme de gestion des risques (Art. 9) | ❌ Non requis | ✅ Requis |
| Gouvernance des donnees (Art. 10) | ❌ Non requis | ✅ Requis |
| Journalisation (Art. 12) | ❌ Non requis | ✅ Requise |
| Surveillance humaine (Art. 14) | ❌ Pas d'obligation legale | ✅ Requise |
| Conformite / marquage CE | ❌ Non requis | ✅ Requis |
| **Transparence (Art. 50)** | **✅ REQUISE** | ✅ Requise aussi |

**Recommandation :** Bien que non legalement obligatoires, les bonnes pratiques suivantes sont fortement recommandees et couvertes par l'approche « privacy by design » :
- Registre des decisions de scoring (GO/NO-GO/MAYBE) avec log des criteres appliques
- Traçabilite des suggestions LLM acceptees/modifiees par l'utilisateur
- Droit de regard humain systematique sur chaque candidature finalisee

### 1.5 Supervision humaine

TAKA OS est conforme au principe de supervision humaine car :
- Le systeme est un **outil d'assistance**, pas un systeme de decision automatisee
- L'utilisateur (soumissionnaire) garde le controle final sur chaque document soumis
- Le scoring GO/NO-GO est une recommandation, pas une decision contraignante
- Le pipeline Kanban implique une revue humaine avant soumission

**Risque residuel :** Si TAKA OS venait a integrer une fonction de « soumission automatique » sans validation, le niveau de risque changerait. Il est recommande de maintenir une validation humaine explicite (checkbox « J'ai verifie ce document ») avant toute exportation.

---

## 2. MARCHES PUBLICS — CADRE JURIDIQUE

### 2.1 Cadre applicable

| Juridiction | Texte principal | Application |
|-------------|----------------|-------------|
| **Union europeenne** | Directive 2014/24/UE (marches publics classiques) | Harmonisation des regles de passation |
| **France** | Code de la commande publique (Ordonnance 2021-631 du 21 mai 2021) | Transposition integrale + regles specifiques |
| **Belgique** | Loi du 17 juin 2016 relative aux marches publics + AR 18/04/2017 + AR 14/01/2013 | Reglementation nationale |

### 2.2 L'utilisation de l'IA dans la preparation des candidatures est-elle autorisee ?

**OUI, sans reserve legislative specifique.** Ni la Directive 2014/24/UE, ni le Code de la commande publique francais, ni la legislation belge n'interdisent l'utilisation d'outils d'intelligence artificielle par les soumissionnaires dans la preparation de leurs candidatures.

**Points de vigilance :**

1. **Article 42 de la Directive 2014/24/UE** (specifications techniques) : les documents de candidature doivent refleter les capacites reelles du candidat. Une assistance IA qui deforme ou exagere les capacites constituerait une fausse declaration.

2. **Article R. 2142-13 du Code de la commande publique** : l'acheteur peut exiger des conditions garantissant les capacites techniques du candidat. L'IA peut etre utilisee pour structurer la reponse, mais pas pour inventer des qualifications.

3. **Principe de bonne foi** (Article 56 de la Directive) : toute candidature doit etre « authentique » et verifiable. Le soumissionnaire reste pleinement responsable du contenu soumis.

### 2.3 Responsabilite en cas d'erreur/hallucination LLM

**Analyse du risque : MODERE (🟡)**

| Scenario | Responsabilite | Consequence |
|----------|---------------|-------------|
| Hallucination dans un memoire technique (chiffre invente, reference fausse) | **Soumissionnaire** — responsabilite pleine | Rejet de l'offre, exclusion de la procedure, possible recours de l'acheteur pour fraude |
| Erreur dans le scoring GO/NO-GO menant a une soumission inadaptee | **Soumissionnaire** — manque de diligence | Perte du temps/investissement, pas de recours contre TAKA OS (logiciel open source, clause de non-responsabilite MIT) |
| Suggestion de texte copiant une tierce partie (plagiat) | **Soumissionnaire** — contrefacon potentielle | Action en justice du tiers, annulation du marche |

**Fondement juridique :** TA Caen, 12 mai 2009 (affaire DCE Cherbourg) : le juge a rappele que le candidat est responsable de la veracite des informations communiquees. L'acheteur public a un « devoir de vigilance sur la veracite des certificats et renseignements » (fiche technique DAJ, 2026).

**Mitigation recommandee pour TAKA OS :**
- **Disclaimer obligatoire** dans l'interface : « TAKA OS est un assistant. Chaque information suggeree doit etre verifiee par l'utilisateur avant inclusion dans une candidature. »
- **Marquage visuel** des suggestions IA (couleur, icone) pour les distinguer du texte saisi manuellement
- **Log d'audit** des modifications apportees par l'utilisateur aux suggestions (traçabilite)
- **Clause de non-responsabilite explicite** dans la licence MIT et dans l'interface utilisateur

### 2.4 Principe d'immutabilite des ecritures comptables et traçabilite

L'**Article 10 de l'Ordonnance 2021-631** (transpose dans le Code de la commande publique) et les articles L. 123-22 et suivants du Code de commerce consacrent le principe d'immutabilite des ecritures comptables. Pour TAKA OS :

| Aspect | Implication |
|--------|-------------|
| **Donnees de scoring** | Doivent etre stockees de maniere non alterable (timestamp + hash) |
| **Suggestions IA** | Traçabilite de la generation (prompt, model version, timestamp) |
| **Modifications utilisateur** | Versioning des documents (qui modifie quoi et quand) |
| **Archivage** | Conservation pendant 10 ans (duree legale pour les documents comptables) |

**Recommandation technique :** Implementer un systeme de « blockchain legere » ou de hashing cryptographique (SHA-256) pour les decisions de scoring et les versions de documents, avec horodatage immuable.

---

## 3. RGPD ET PROTECTION DES DONNEES (REGLEMENT EU 2016/679)

### 3.1 Qualification du traitement

TAKA OS, en mode self-heberge (deploiement par l'entreprise soumissionnaire), constitue un **traitement de donnees a caractere personnel** au sens du RGPD :

| Element | Qualification |
|---------|--------------|
| **Responsable de traitement** | L'entreprise soumissionnaire (utilisateur de TAKA OS) |
| **Sous-traitant** | L'editeur de TAKA OS (si hebergement SaaS) ; non applicable en self-hosted |
| **Donnees traitees** | Donnees d'identification des collaborateurs, donnees financieres de l'entreprise, donnees des contacts clients/references, historique de candidatures |
| **Base legale** | Interet legitime de l'entreprise (Article 6(1)(f)) ou execution d'un contrat (Article 6(1)(b)) |

### 3.2 Avantages du modele open source self-hosted

Le modele de TAKA OS (MIT, self-hosted) presente des **atouts majeurs** au regard du RGPD :

| Critere | TAKA OS self-hosted | Solution SaaS tierce (ex: ChatGPT Enterprise) |
|---------|-------------------|-----------------------------------------------|
| Localisation des donnees | Serveur EU (controle par l'utilisateur) | Depend du fournisseur |
| Transfert international | Aucun (si stack EU) | Risque de transfert vers les USA |
| DPA (Article 28) | Non requis (pas de sous-traitant externe) | Requis, avec garanties SCC |
| Acces tiers aux donnees | Aucun | Possible (prestataire SaaS) |
| Droit a l'oubli | Controle total par l'utilisateur | Depend du fournisseur |
| Portabilite (Art. 20) | Facilite par l'open source (PostgreSQL) | Formats proprietaires possibles |

**Texte applicable :** CNIL, « IA : respecter l'exercice des droits des personnes » (7 fevrier 2025) ; Article 28 RGPD (sous-traitance).

### 3.3 Droit a l'oubli et memoire episodique (TAKA LAB v2)

La **memoire episodique** de TAKA OS (capitalisation des echecs/succes) souleve une question specifique :

| Droit | Application | Mitigation |
|-------|-------------|------------|
| **Droit a l'effacement (Art. 17)** | L'utilisateur peut demander la suppression de ses donnees de candidature | Mecanisme de « desapprentissage » ou suppression des vecteurs associes dans pgvector |
| **Droit a la portabilite (Art. 20)** | Export des donnees en format structue | PostgreSQL + format JSON/CSV natif |
| **Minimisation (Art. 5(1)(c))** | Ne stocker que les donnees strictement necessaires a l'amelioration des suggestions | Anonymisation des donnees de candidature stockees dans la memoire |

**Recommandation technique :** Implementer une fonctionnalite de « purge de memoire » permettant a l'utilisateur de supprimer selectivement ou totalement l'historique episodique, avec suppression des vecteurs pgvector associes.

### 3.4 Le cas specifique de Kimi API (LLM externe)

**⚠️ RISQUE MAJEUR (🔴)**

L'utilisation de **Kimi API (Moonshot AI, Chine)** pour le traitement des donnees constitue le point de vigilance le plus eleve du projet :

| Risque | Niveau | Justification |
|--------|--------|---------------|
| **Transfert de donnees vers la Chine** | 🔴 Critique | Le RGPD interdit les transferts vers des pays non-adeses (Chine) sauf garanties supplementaires (Articles 44-49). Aucune decision d'adequation n'existe pour la Chine. |
| **Acces des autorites chinoises** | 🔴 Critique | La loi chinoise sur la cybersecurite (2017) et la loi sur la securite des donnees (2021) donnent aux autorites chinoises un acces potentiel aux donnees traitees par des operateurs chinois. |
| **Data Act / souverainete** | 🔴 Critique | L'utilisation d'un LLM chinois pour des donnees de marches publics (potentiellement sensibles) entre en conflit avec les objectifs de souverainete numerique europeenne. |
| **Distillation / IP** | 🟡 Eleve | Le White House et le State Department ont accuse formellement Moonshot AI (Kimi) de « distillation industrielle » de modeles occidentaux (avril 2026). |

**Recommandation :** Remplacer Kimi API par un LLM europeen ou un modele open source auto-heberge en EU :
- **Mistral AI** (API hebergee en France/UE) — meilleure option pour la conformite
- **Llama 3/4** (Meta) auto-heberge sur infrastructure EU
- **Mixtral** (open source, possible self-hosting)

### 3.5 Self-hosted vs SaaS — implications RGPD

| Modele | Conformite RGPD | Complexite | Cout |
|--------|----------------|------------|------|
| **Self-hosted (TAKA OS)** | ✅ Excellent — donnees sous controle | Infrastructure a gerer | Serveurs EU |
| **SaaS manage par TAKA** | ✅ Bon — DPA fourni, hebergement EU declare | Nul (TAKA gere) | Abonnement |
| **SaaS avec LLM tiers** | ⚠️ Moyen — chaine de sous-traitance complexe | DPA avec chaque sous-traitant | Variables |

---

## 4. SOUVERAINETE NUMERIQUE EUROPEENNE

### 4.1 Data Act (Reglement EU 2023/2854)

| Aspect | Detail | Impact sur TAKA OS |
|--------|--------|-------------------|
| **Entree en vigueur** | 11 janvier 2024, pleinement applicable depuis 12 septembre 2025 | ✅ Aujourd'hui applicable |
| **Portee** | Services de traitement de donnees (IaaS, PaaS, SaaS) | Applicable si TAKA OS propose un hebergement SaaS |
| **Switching** | Droit de changer de fournisseur cloud sans frais excessifs (a partir janvier 2027) | Neutre — l'open source facilite deja la migration |
| **Interoperabilite** | Interfaces ouvertes, formats standard | Positif — TAKA OS (FastAPI, PostgreSQL) est natif interoperable |

### 4.2 NIS2 (Directive EU 2022/2555)

| Aspect | Detail | Impact sur TAKA OS |
|--------|--------|-------------------|
| **Entree en vigueur** | 16 janvier 2023, transposee par les Etats membres en octobre 2024 | ✅ Applicable |
| **Entites concernees** | Entites importantes et essentielles | TAKA OS comme outil utilise par ces entites doit integrer les exigences de cybersecurite |
| **Cybersecurite** | Gestion des risques, reporting d'incidents, securite de la chaine d'approvisionnement | Obligations a integrer si TAKA OS est deploye chez des entites NIS2 |

### 4.3 GAIA-X et Cloud EU

| Initiative | Objectif | Avantage pour TAKA OS |
|------------|----------|----------------------|
| **GAIA-X** | Infrastructure cloud europeenne souveraine | Compatibilite avec les principes de souverainete de donnees et d'interoperabilite |
| **Cloud de Confiance (France)** | Label SecNumCloud, qualification des hebergeurs | Opportunite de qualification si TAKA OS est heberge sur un Cloud de Confiance |
| **EU Cloud and AI Development Act** | Attendu en 2025-2026, cadre harmonise pour le cloud public sector | Avantage pour les solutions open source EU-hebergees |

### 4.4 LLM non-europeens — restrictions

| Contexte | Situation | Impact |
|----------|-----------|--------|
| **Marches publics sensibles** | Recommandation de l'ANSSI et de la Commission : privilegier les LLM europeens ou self-hosted pour les donnees sensibles | Si TAKA OS est utilise par des entreprises travaillant pour la defense/securite, Kimi API est inapproprie |
| **Open source EU** | Le fait d'etre « open source MIT + heberge en EU » est un avantage dans les criteres d'attribution des marches publics (critere « souverainete numerique ») | ✅ Atout pour TAKA OS si positionne comme solution souveraine |
| **Restrictions US** | Le gouvernement US a accuse les LLM chinois (DeepSeek, Moonshot/Kimi, MiniMax) de distillation industrielle ; plusieurs pays ont restreint leur usage | Risque geopolitique supplementaire sur Kimi |

---

## 5. CADRE SPECIFIQUE BELGIQUE/FRANCE

### 5.1 BOAMP (France) — collecte des donnees

| Aspect | Detail |
|--------|--------|
| **API BOAMP** | API officielle de la DILA, accessible gratuitement sur data.gouv.fr |
| **Licence** | Licence Ouverte Etalab v2.0 (equivalent CC BY) — reutilisation libre, gratuite, avec mention de paternite |
| **Scraping** | L'API est la voie recommandee. Le scraping direct du site BOAMP est techniquement possible mais deconseille (limites de requetes, instability du DOM). |
| **Donnees personnelles** | Avertissement DILA : la reutilisation de donnees personnelles eventuelles est soumise a la loi Informatique et Libertes |

**Verdict :** ✅ L'utilisation de l'API BOAMP est parfaitement legale et conforme. Aucun risque.

### 5.2 e-marchespublics.be (Belgique)

| Aspect | Detail |
|--------|--------|
| **Donnees** | Les avis de marches publics sont des donnees publiques par nature (publicite legale) |
| **e-marchespublics** | Plateforme federale belge ; les donnees de consultation sont publiques |
| **Conditions d'utilisation** | A verifier au cas par cas, mais les donnees d'avis de marche sont publiques par principe |

**Verdict :** ✅ Les donnees publiques de marches sont reutilisables. Preferer les API officielles si disponibles.

### 5.3 Propriete intellectuelle des DCE

**Analyse juridique :**

Le **TA de Caen, 12 mai 2009** a juge qu'un **DCE n'est pas une « oeuvre de l'esprit »** au sens de l'article L.111-1 du Code de la propriete intellectuelle :

> *« Le DCE ne constitue qu'un simple savoir-faire »* — il s'agit de documents fonctionnels, techniques et administratifs qui *« experiment des besoins techniques et des conditions administratives standardisees »*.

**Consequences pour TAKA OS :**

| Action | Legalite |
|--------|----------|
| Parser un DCE (extraction de texte) | ✅ LEGAL — pas d'oeuvre protegee |
| Stocker un DCE dans la base de donnees | ✅ LEGAL — donnee publique |
| Vectoriser un DCE (embeddings) | ✅ LEGAL — transformation technique |
| Reproduire un DCE dans son integralite | ✅ LEGAL — mais mentionner la source (licence ouverte) |
| Reutiliser des clauses type d'un DCE | ✅ LEGAL — savoir-faire non protegeable |

**Point d'attention :** Si un DCE contient des elements creatifs originaux (schema technique original, description redactionnelle elaboree), ces elements specifiques pourraient etre proteges. La vectorisation d'extraits courts a des fins d'analyse reste neanmoins couverte par les exceptions ( courte citation, analyse ).

---

## 6. SYNTHESE DES RISQUES ET MESURES DE MITIGATION

### Matrice des risques

| # | Domaine | Risque | Niveau | Mitigation | Priorite |
|---|---------|--------|--------|------------|----------|
| 1 | **Souverainete data / RGPD** | Utilisation de Kimi API (Chine) : transfert de donnees, acces autorites chinoises, conflit avec souverainete EU | 🔴 Eleve | **Remplacer Kimi par Mistral AI (FR) ou Llama self-hosted (EU)** avant MVP | CRITIQUE |
| 2 | **AI Act Art. 50** | Transparence : obligation d'informer l'utilisateur de l'interaction IA + marquage contenu genere des aout 2026 | 🟡 Moyen | Ajouter un badge « Powered by AI » visible + metadata sur les suggestions | ELEVEE |
| 3 | **Responsabilite / Marches publics** | Hallucination LLM pouvant induire une erreur dans une candidature | 🟡 Moyen | Disclaimer obligatoire + validation humaine systematique + log d'audit | ELEVEE |
| 4 | **RGPD** | Droit a l'oubli sur la memoire episodique (TAKA LAB v2) | 🟡 Moyen | Fonction de purge de memoire + suppression des vecteurs pgvector | MOYENNE |
| 5 | **Immutabilite comptable** | Traçabilite des decisions de scoring et des versions de documents | 🟡 Moyen | Horodatage + hash cryptographique des decisions | MOYENNE |
| 6 | **NIS2 / Cybersecurite** | Exigences de securite pour les utilisateurs NIS2 | 🟡 Moyen | Chiffrement des donnees, authentification forte, audit de securite | MOYENNE |
| 7 | **PI / DCE** | Reutilisation des DCE parsés | 🟢 Faible | Mention de la source (DILA) — deja couvert par la licence ouverte | FAIBLE |
| 8 | **Scraping BOAMP** | Collecte des donnees de marches publics | 🟢 Faible | Utilisation de l'API officielle — parfaitement legale | FAIBLE |

---

## 7. VERDICT GLOBAL ET RECOMMANDATIONS STRATEGIQUES

### 7.1 TAKA OS est-il juridiquement viable en EU ?

**✅ OUI, TAKA OS est juridiquement viable dans l'Union europeenne**, avec les reserves et ajustements suivants :

| Facteur | Evaluation |
|---------|------------|
| **Classification AI Act** | Risque limite (transparence uniquement) — favorable |
| **Droit des marches publics** | Aucune prohibition — l'IA est un outil d'assistance legitime |
| **RGPD** | Modele self-hosted = excellent, sous reserve du choix du LLM |
| **Open source MIT** | Attractif pour la confiance et la souverainete, mais n'exempte pas de l'AI Act |
| **Donnees publiques** | API BOAMP et donnees de marches = reutilisation libre et legale |

### 7.2 Les 3 risques juridiques majeurs a adresser avant le MVP

#### 🔴 RISQUE 1 : Remplacer Kimi API par un LLM europeen (ou self-hosted)

**Pourquoi :** Kimi API (Moonshot AI, Chine) pose un risque RGPD majeur (transfert de donnees vers un pays non-adequat), un risque de souverainete numerique (acces potentiel des autorites chinoises), et un risque geopolitique (accusations de distillation, restrictions croissantes).

**Solution recommandee :**
- **Option A (recommandee) :** Mistral AI API — hebergee en France/UE, modele Mistral Large ou Mistral Medium, conforme RGPD native
- **Option B :** Llama 4 (Meta) auto-heberge sur serveur EU — controle total, zero donnee sortant
- **Option C :** Mixtral 8x22B (open source) self-hosted — modele europeen, excellent rapport qualite/cout

**Cout du non-respect :** Sanctions RGPD jusqu'a 20 M€ ou 4% du CA ; risque geopolitique ; exclusion de certains marches sensibles.

#### 🟡 RISQUE 2 : Implementer les obligations de transparence AI Act (Article 50)

**Pourquoi :** Des le 2 aout 2026, TAKA OS doit informer clairement les utilisateurs qu'ils interagissent avec un systeme d'IA, et marquer le contenu genere comme artificiel.

**Actions concretes :**
1. Badge « 🤖 Assistant IA — TAKA OS » en haut de l'interface chat
2. Message d'ouverture du chatbot : « Je suis un assistant IA. Je peux vous aider a analyser les appels d'offres et preparer vos candidatures. Mes suggestions doivent toujours etre verifiees avant soumission. »
3. Metadata ou watermark sur les suggestions de texte : « [Suggere par TAKA OS — IA] »
4. Footer sur les exports : « Ce document a ete prepare avec l'assistance de TAKA OS, un systeme d'intelligence artificielle. La responsabilite de la soumission incombe entierement au soumissionnaire. »

**Cout du non-respect :** Jusqu'a 7,5 M€ ou 1% du CA mondial.

#### 🟡 RISQUE 3 : Mecanisme de validation humaine et de non-responsabilite

**Pourquoi :** En cas d'hallucination LLM entrainant une erreur dans une candidature, le soumissionnaire est seul responsable. TAKA OS, en tant que logiciel open source, doit se proteger juridiquement et proteger ses utilisateurs.

**Actions concretes :**
1. **Checkbox de validation obligatoire** avant tout export de document : « J'ai verifie l'integralite de ce document et je certifie l'exactitude des informations. »
2. **Clause de non-responsabilite** dans la licence MIT (deja presente) ET dans l'interface
3. **Log d'audit** complet : version du modele utilise, prompt, suggestion, modifications de l'utilisateur, validation finale
4. **Disclaimer permanent** : « TAKA OS est un outil d'aide a la decision. Il ne remplace pas l'expertise humaine ni la verification des informations. »

### 7.3 Feuille de route reglementaire pre-MVP

| Semaine | Action | Responsable |
|---------|--------|-------------|
| S1 | Remplacer Kimi API par Mistral AI API ou Llama self-hosted | Tech Lead |
| S1 | Implementer le badge IA et le message de transparence | Frontend |
| S2 | Ajouter la checkbox de validation humaine + log d'audit | Backend |
| S2 | Rediger les CGU avec clause de non-responsabilite | Juridique |
| S3 | Implementer la fonction de purge memoire (droit a l'oubli) | Backend |
| S3 | Ajouter l'horodatage + hash des decisions de scoring | Backend |
| S4 | Audit de conformite interne (AI Act + RGPD check-list) | DPO / Juridique |

### 7.4 Positionnement strategique reglementaire

TAKA OS dispose d'un **positionnement reglementaire favorable** :

| Atout | Argumentaire |
|-------|-------------|
| **Open source MIT** | Transparence du code, auditabilite, confiance — en phase avec l'ethique europeenne de l'IA |
| **Hebergement EU** | Conformite RGPD native, protection contre les acces extraterritoriaux (Cloud Act US) |
| **Self-hosted possible** | Souverainete totale des donnees, zero dependance a un SaaS etranger |
| **Assistance, pas decision** | Le candidat garde le controle final — conforme au principe de supervision humaine |
| **Stack europeenne** (si Mistral/Llama) | Chaine de valeur EU, compatible avec les criteres de souverainete numerique des marches publics |

**Argument de vente reglementaire :** *« TAKA OS est le seul assistant IA pour marches publics qui combine open source, hebergement europeen, et conformite native au AI Act et au RGPD — garantissant la souverainete de vos donnees de candidature. »*

---

## ANNEXE : REFERENCES REGLEMENTAIRES

| Reference | Titre | Date |
|-----------|-------|------|
| Reglement (UE) 2024/1689 | AI Act — Reglement sur l'intelligence artificielle | 1 aout 2024 (applicabilite echelonnee) |
| Directive 2014/24/UE | Directive marches publics | 26 fevrier 2014 |
| Ordonnance 2021-631 | Reforme du droit des marches publics (France) | 21 mai 2021 |
| Loi 17 juin 2016 | Loi relative aux marches publics (Belgique) | 17 juin 2016 |
| Reglement (UE) 2016/679 | RGPD | 27 avril 2016 |
| Reglement (UE) 2023/2854 | Data Act | 11 janvier 2024 |
| Directive (UE) 2022/2555 | NIS2 | 16 janvier 2023 |
| TA Caen, n° 08-01328 | DCE non protege par le droit d'auteur | 12 mai 2009 |
| Licence Ouverte Etalab v2.0 | Reutilisation des donnees BOAMP | 2017 |
| CNIL, fiche IA | « IA : respecter l'exercice des droits des personnes » | 7 fevrier 2025 |
| AI Office Guidelines | Guidelines sur les GPAI models | Juillet 2025 |

---

*Document redige en mai 2026. Ce document constitue une analyse juridique a titre informatif et ne saurait se substituer a un avis juridique formalise par un avocat ou un conseil specialise. Les reglementations citees sont celles en vigueur a la date de redaction et sont susceptibles d'evolution.*
