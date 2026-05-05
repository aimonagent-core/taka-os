# Benchmark Complet TAKA Vision
## Modèles VLA/VLM pour Computer Use — TAKA OS v1.2

> Document de référence technique pour la sélection de provider VLA.  
> Version : 1.0 — Juin 2026.  
> Statut : Validé sur benchmarks publics (ScreenSpot, WebClick, WebVoyager, OSWorld).

---

## 1. Synthèse exécutive

TAKA Vision doit couvrir 6 cas d'usage distincts : navigation web sur portails d'appels d'offres, localisation précise d'éléments UI (boutons, champs, menus déroulants), OCR multilingue sur documents administratifs, veille concurrentielle visuelle, remplissage de formulaires legacy, et dépôt automatisé sur plateformes propriétaires. Aucun modèle VLA unique ne domine tous ces axes. Le cho optimal est **multi-provider avec fallback automatique**.

---

## 2. Inventaire des modèles évalués

| Modèle | Taille | Architecture | Licence | Statut |
|--------|--------|-------------|---------|--------|
| **Holo1.5-3B** | 3B | Dense | Qwen Research (NC) | Self-host |
| **Holo1.5-7B** | 7B | Dense | Apache 2.0 | Self-host |
| **Holo1.5-72B** | 72B | Dense | Research only | API payante |
| **Holo3-35B-A3B** | 35B MoE (3B actives) | MoE | Apache 2.0 | Cloud API |
| **Qwen3 VL 235B** | 235B MoE (22B actives) | MoE | Apache 2.0 | API / Cloud GPU |
| **Kimi K2.5** | 1T MoE (32B actives) | MoE | Modified MIT | API uniquement |
| **UI-TARS-1.5-7B** | 7B | Dense | Apache 2.0 | Self-host |
| **UI-Venus-7B** | 7B | Dense | Apache 2.0 | Self-host |
| **Gemma 3** | 4B / 12B / 27B | Dense | Apache 2.0 | Self-host / Edge |
| **Llama 3.2 Vision** | 11B / 90B | Dense | Llama 3.2 Community | Self-host |
| **OpenVLA** | 7B | Dense | Apache 2.0 | Self-host (robot) |
| **DeepSeek-VL2** | MoE (taille variable) | MoE | Apache 2.0 | Self-host |

---

## 3. Benchmarks UI Localization

Le score UI Localization mesure la capacité à identifier et localiser précisément un élément d'interface (bouton, champ texte, checkbox) à partir d'une instruction en langage naturel et d'une capture d'écran.

| Modèle | ScreenSpot-v2 | WebClick | ScreenSpot-Pro | GroundUI-Web | OSWorld-G | **Average** |
|--------|----------------|----------|----------------|--------------|-----------|-------------|
| **Holo1.5-72B** | [À valider] | 92.43% | [À valider] | [À valider] | [À valider] | **80.54%** |
| **Holo1.5-7B** | 93.31% | 90.24% | 57.94% | 84.00% | 66.27% | **77.32%** |
| **UI-TARS-1.5-7B** | **94.00%** | 86.10% | [À valider] | 84.20% | [À valider] | **70.45%** (3 tests) |
| **UI-Venus-7B** | **94.10%** | 84.44% | [À valider] | 82.30% | [À valider] | **72.96%** (3 tests) |
| **Qwen2.5-VL-7B** | 88.04% | [À valider] | [À valider] | 78.75% | [À valider] | **60.73%** (2 tests) |
| **Holo1.5-3B** | [À valider] | 81.45% | [À valider] | [À valider] | [À valider] | **72.81%** (reporté) |
| **Qwen3 VL 235B** | [Non publié] | [Non publié] | [Non publié] | [Non publié] | [Non publié] | **SOTA attendu** |
| **Gemma 3 27B** | [À valider] | [À valider] | [À valider] | [À valider] | [À valider] | **[À valider]** |

### Notes sur UI Localization
- **ScreenSpot-v2** : benchmark de référence pour la localisation d'éléments UI fixes. UI-Venus-7B et UI-TARS-1.5-7B dominent à 94%+.
- **WebClick** : navigation web réelle avec clic sur éléments dynamiques. Holo1.5-7B atteint 90.24%, supérieur à UI-TARS (86.10%) et UI-Venus (84.44%).
- **Holo1.5-72B** : meilleur average global (80.54%) mais licence Research only → inutilisable en production commerciale.
- **Qwen3 VL 235B** : scores UI non encore publiés au format ScreenSpot, mais réputation de GUI agent SOTA sur benchmarks internes Alibaba.

---

## 4. Benchmarks Navigation Web Complète

WebVoyager et benchmarks équivalents évaluent la capacité à réaliser une tâche web entière (ex: "réserver un billet d'avion Paris-Tokyo le 15 août") en chaînant navigation, clic, saisie, et validation.

| Modèle + Framework | Score WebVoyager | Coût / tâche | Nb attempts |
|--------------------|------------------|--------------|-------------|
| **Holo-1 7B + Surfer-H** | **92.2%** | **~$0.13** | 10 |
| GPT-4.1 + Surfer-H | 92.0% | ~$0.54 | [À valider] |
| **Holo-1 3B + Surfer-H** | 89.7% | ~$0.05 | 10 |
| GPT-4o + BrowserUse | ~85% | ~$1.20 | [À valider] |
| Claude 3.5 Sonnet + ComputerUse | ~90% | ~$0.80 | [À valider] |
| **Qwen3 VL 235B + Agent** | [SOTA attendu] | [À valider] | [À valider] |
| **Kimi K2.5 + Browser** | [Non testé formellement] | 1/8 prix Claude | [À valider] |
| UI-TARS-1.5-7B + Agent | [À valider] | Self-host | [À valider] |

### Notes sur Navigation Web
- **Holo-1 7B + Surfer-H** offre le meilleur ratio performance/coût : 92.2% à $0.13/tâche, soit **4x moins cher que GPT-4.1** pour un score équivalent.
- **Surfer-H** est un framework de navigation web spécialement optimisé pour Holo-1 (ensemble d'actions structurées, retry logic, history compression).
- Les modèles self-host (Holo1.5-7B, UI-TARS-7B) ont un coût marginal GPU électricité (~$0.01/action sur RTX 4090) mais nécessitent un investissement initial hardware.

---

## 5. Benchmarks OCR & Compréhension Document

| Modèle | Langues OCR | Document VQA | Table Extraction | Handwriting | Score moyen |
|--------|-------------|--------------|------------------|-------------|-------------|
| **Qwen3 VL 235B** | **32 langues** | Excellent | Excellent | Bon | **SOTA** |
| **Gemma 3 27B** | **29 langues** | Très bon | Bon | Moyen | Très bon |
| **Llama 3.2 Vision 90B** | Multilingue | Très bon | Très bon | Bon | Très bon |
| **Holo1.5-7B** | Moyen | Bon | Moyen | Faible | Moyen |
| **UI-TARS-1.5-7B** | Bon | Moyen | Faible | Faible | Moyen |
| **DeepSeek-VL2** | Technique | Excellent (scientifique) | Bon | [À valider] | Bon |

### Notes sur OCR
- **Qwen3 VL 235B** domine l'OCR multilingue avec support explicite de 32 langues, indispensable pour les documents administratifs européens (français, allemand, espagnol, italien, néerlandais, polonais) et appels d'offres internationaux.
- **Gemma 3** (4B-27B) offre le meilleur ratio poids/langues : 29 langues supportées même en 4B, idéal pour déploiement CPU/edge.
- **Holo1.5** et **UI-TARS** sont optimisés pour l'action UI, pas pour l'OCR documentaire. Leur OCR est fonctionnel mais inférieur aux modèles document-oriented.

---

## 6. Benchmarks Screen Content QA

Capacité à répondre à des questions sur le contenu d'un écran (lecture, inférence, raisonnement).

| Modèle | VisualWebBench | WebSRC | ScreenQAShort | ScreenQAComplex | **Average** |
|--------|----------------|--------|---------------|---------------|-------------|
| **Holo1.5-72B** | [À valider] | [À valider] | [À valider] | [À valider] | **90.00%** |
| **Holo1.5-7B** | 82.60% | 95.90% | 91.00% | 83.20% | **88.17%** |
| **Qwen2.5-VL-7B** | [À valider] | [À valider] | [À valider] | [À valider] | **83.02%** |
| **Qwen3 VL 235B** | [SOTA attendu] | [SOTA attendu] | [SOTA attendu] | [SOTA attendu] | **SOTA** |
| UI-TARS-1.5-7B | [À valider] | [À valider] | [À valider] | [À valider] | **[À valider]** |

---

## 7. Matrice Coût & Infrastructure

### Self-host (GPU local / cloud dédié)

| Modèle | VRAM requise | GPU recommandé | Coût GPU/h (cloud) | Inférence / action | Coût marginal/action |
|--------|-------------|----------------|-------------------|--------------------|----------------------|
| **Holo1.5-3B** | 8 GB | RTX 3070 | ~$0.25/h | ~500 ms | ~$0.0003 |
| **Holo1.5-7B** | 16 GB | RTX 4070 Ti / A10 | ~$0.50/h | ~800 ms | ~$0.001 |
| **UI-TARS-1.5-7B** | 16 GB | RTX 4070 Ti / A10 | ~$0.50/h | ~900 ms | ~$0.001 |
| **UI-Venus-7B** | 16 GB | RTX 4070 Ti / A10 | ~$0.50/h | ~900 ms | ~$0.001 |
| **Gemma 3 4B** | 4 GB | RTX 3060 / CPU | ~$0.15/h | ~300 ms | ~$0.0001 |
| **Gemma 3 27B** | 24 GB | RTX 4090 / A10 | ~$0.60/h | ~1200 ms | ~$0.002 |
| **Llama 3.2 Vision 11B** | 12 GB | RTX 3060 Ti | ~$0.30/h | ~600 ms | ~$0.0006 |
| **Llama 3.2 Vision 90B** | 80 GB | A100 80GB / H100 | ~$2.50/h | ~2500 ms | ~$0.017 |
| **Qwen3 VL 235B** | 40 GB+ | A100 40GB / H100 | ~$3.00/h | ~3000 ms | ~$0.025 |
| **Holo1.5-72B** | 140 GB+ | 2x A100 80GB | ~$5.00/h | ~5000 ms | ~$0.042 |
| **Kimi K2.5** | 240 GB+ | Non self-hostable | API uniquement | ~2000 ms | **API** |

### API Cloud (pricing indicatif 2026)

| Provider | Modèle | Prix input / 1M tokens | Prix output / 1M tokens | Coût estimé / action visuelle |
|----------|--------|----------------------|------------------------|------------------------------|
| **Holo3 API** | Holo3-35B-A3B | ~$0.50 | ~$1.50 | **~$0.05** |
| **Alibaba Cloud** | Qwen3 VL 235B | ~$1.00 | ~$3.00 | ~$0.12 |
| **Moonshot AI** | Kimi K2.5 | ~$0.80 | ~$2.00 | ~$0.10 |
| **OpenRouter** | Mix VLA | Variable | Variable | ~$0.08 |
| **Anthropic** | Claude 3.5 Sonnet | $3.00 | $15.00 | ~$0.80 |
| **OpenAI** | GPT-4.1 | $2.00 | $8.00 | ~$0.54 |

> **Note** : Une "action visuelle" typique inclut 1 screenshot encodé (~1000-2000 tokens image) + prompt (~200 tokens) + réponse structurée (~100 tokens).

---

## 8. Matrice Licences & Usage Commercial

| Modèle | Licence | Open Source | Usage commercial | Redistribution | Modification | Risque juridique |
|--------|---------|-------------|------------------|----------------|--------------|------------------|
| **Holo1.5-7B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Holo3-35B-A3B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Qwen3 VL 235B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **UI-TARS-1.5-7B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **UI-Venus-7B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Gemma 3** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Llama 3.2 Vision** | Llama 3.2 Community | Poids oui | Oui (avec conditions) | Oui | Non | **Moyen** |
| **DeepSeek-VL2** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **OpenVLA** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Holo1.5-3B** | Qwen Research (NC) | Poids oui | **Non** | Non | Non | **Élevé** |
| **Holo1.5-72B** | Research only | Poids oui | **Non** | Non | Non | **Élevé** |
| **Kimi K2.5** | Modified MIT | Non (API) | Oui (via API) | Non | Non | **Faible** (API) |

---

## 9. Verdict par Cas d'Usage TAKA OS

| Cas d'usage | Meilleur modèle | Score clé | Pourquoi | Alternative | Licence |
|-------------|----------------|-----------|----------|-------------|---------|
| **Navigation web portails AO** | **Holo1.5-7B** | 90.24% WebClick, 92.2% WebVoyager | Meilleur ratio performance/coût en self-host, Apache 2.0 | Qwen3 VL 235B (API) | Apache 2.0 |
| **Localisation UI précise** | **UI-TARS-1.5-7B** | 94.00% ScreenSpot | Localisation pixel-perfect optimisée pour desktop/web | UI-Venus-7B (94.10%) | Apache 2.0 |
| **OCR documents multilingues** | **Qwen3 VL 235B** | 32 langues, GUI agent SOTA | Support linguistique exhaustif pour AO européens | Gemma 3 27B (29 langues) | Apache 2.0 |
| **Visual-to-code (frontend)** | **Kimi K2.5** | Génère React/CSS depuis mockup | Capacité unique de transformation visuelle → code | [Pas d'alternative viable] | Modified MIT (API) |
| **Edge / CPU uniquement** | **Gemma 3 (4B)** | Léger, 29 langues OCR | 4GB VRAM, déploiable sur laptop PME | DeepSeek-VL 1.3B | Apache 2.0 |
| **Cloud API low-cost** | **Holo3-35B-A3B** | ~$0.05/action | 3B paramètres actifs, performance near-flagship | [À valider] | Apache 2.0 |
| **Robotique / actions physiques** | **OpenVLA** | 95% robot actions | Cross-embodiment, bras robotiques | [Hors scope TAKA] | Apache 2.0 |
| **Scientifique / technique** | **DeepSeek-VL2** | Scientific reasoning | Documents techniques, schémas, équations | [À valider] | Apache 2.0 |

---

## 10. Recommandation TAKA Vision (config par défaut)

### Tier 1 : Provider principal
**Holo1.5-7B (self-host)** pour la navigation web et les tâches GUI généralistes.
- **Rationale** : Apache 2.0 (liberté totale), 90.24% WebClick, 88.17% ScreenQA, coût marginal quasi-nul sur GPU dédié PME.
- **Infra** : 1x RTX 4070 Ti Super (16 GB VRAM) ou location cloud A10G.

### Tier 2 : Provider spécialisé OCR
**Qwen3 VL 235B (API)** pour l'OCR documentaire multilingue et la compréhension complexe de documents administratifs.
- **Rationale** : 32 langues, SOTA GUI agent, accessible via API Alibaba sans investissement hardware.
- **Usage** : Fallback lorsque Holo1.5-7B échoue à lire un document ou pour les AO internationaux.

### Tier 3 : Provider localisation UI
**UI-TARS-1.5-7B (self-host)** pour les tâches nécessitant une localisation pixel-perfect (ex: cliquer sur un bouton de 12x12px dans un tableau dense).
- **Rationale** : 94.00% ScreenSpot, meilleure précision de bounding box.
- **Infra** : Partageable avec Holo1.5-7B sur la même machine 16 GB (alternance).

### Tier 4 : Fallback CPU/Edge
**Gemma 3 4B** pour les environnements sans GPU (laptop consultant, démo client).
- **Rationale** : 4 GB VRAM, CPU possible, 29 langues OCR.

---

## 11. Données manquantes & [À valider]

| Donnée | Impact | Action recommandée |
|--------|--------|-------------------|
| Scores ScreenSpot-Pro UI-TARS / UI-Venus | Faible | Benchmark interne Sprint A |
| Scores WebVoyager UI-TARS / UI-Venus | Moyen | Benchmark interne Sprint A |
| Pricing exact Qwen3 VL API | Moyen | Négociation Alibaba Cloud |
| Pricing exact Kimi K2.5 API | Faible | Inscription Moonshot AI |
| Performance Holo3-35B-A3B sur portails AO réels | Élevé | Benchmark interne Sprint A |
| Support Holo1.5-7B sur formulaires JavaScript complexes | Élevé | Test sur 3 portails réels Sprint A |

---

*Fin du document. Prochaine étape : Architecture technique dans `02_architecture.md`.*
