# TAKA OS — Protocole de Suivi Pas à Pas (CEO ↔ CTO ↔ Kimi Code)

## Rôles

| Rôle | Responsabilité |
|------|---------------|
| **CEO (Toi)** | Exécute les actions concrètes (GitHub, VPS, Kimi Code), reporte les résultats, valide les livrables |
| **CTO (Moi)** | Guide technique, valide les décisions, résout les blocages, met à jour les specs si besoin |
| **Kimi Code** | Développe le code selon les prompts, produit les fichiers |
| **KIMI-TAKA-SWARM** | Agents de revue (audit qualité, sécurité, tests) activés à la fin de chaque sprint |

## Rituel de Suivi

### 1. Format de Reporting CEO → CTO

Quand tu accomplis une action, réponds avec ce format :

```
[ACTION] Ce que j'ai fait
[STATUT] OK / KO / BLOQUÉ
[RÉSULTAT] Ce qui s'est passé (copier-coller l'output si pertinent)
[QUESTION] Si tu as une question / blocage
```

### 2. Format de Suivi Kimi Code → CEO → CTO

Quand Kimi Code produit du code, réponds avec :

```
[KIMI CODE] Sprint X — Fichiers produits : N fichiers
[STATUT] Terminé / En cours / Erreur
[VALIDATION] J'ai vérifié : [ ] Docker démarre [ ] Tests passent [ ] API répond
[CAPTURE] (screenshot ou copier-coller des logs si erreur)
[QUESTION] Si besoin d'aide
```

### 3. Mes Réponses CTO

Je réponds toujours avec :
- **Validation** : OK ou Correction demandée
- **Prochaine étape** : Action immédiate suivante
- **Rappel du contexte** : Pourquoi on fait ça

## Plan d'Exécution Détaillé (Checklist)

### Phase 0 — Préparation (Aujourd'hui, 15 min)
- [ ] Créer repo GitHub `taka-os` (public, MIT, .gitignore Python)
- [ ] Cloner en local, créer structure dossiers
- [ ] Premier commit
- [ ] Copier SPRINT_0_FONDATION.md dans Kimi Code
- [ ] Lancer Kimi Code Sprint 0

### Phase 1 — Sprint 0 (Semaine 1, 4-6h de travail)
- [ ] Kimi Code génère les 37 fichiers
- [ ] CEO vérifie : Docker compose up fonctionne
- [ ] CEO vérifie : Swagger /docs accessible
- [ ] CEO vérifie : Login JWT fonctionne
- [ ] CEO vérifie : MFA setup fonctionne
- [ ] CEO vérifie : Sentry reçoit erreurs
- [ ] CEO vérifie : pytest passe 30+ tests
- [ ] CEO pousse sur GitHub
- [ ] CTO active agents de revue (audit qualité)
- [ ] Correction si besoin

### Phase 2 — Sprint 1 (Semaine 2)
- [ ] Copier SPRINT_1_SENSORIMOTRICE_MEMOIRE.md dans Kimi Code
- [ ] Lancer Kimi Code
- [ ] Vérifier upload PDF + parsing 4 niveaux
- [ ] Vérifier embeddings pgvector
- [ ] Vérifier MFA + E2E Playwright
- [ ] Vérifier N Gates validation
- [ ] Pousse sur GitHub

### Phase 3 — Sprint 2 (Semaine 3)
- [ ] Copier SPRINT_2_QUALIFIEUR_KANBAN.md dans Kimi Code
- [ ] Vérifier scoring 5D
- [ ] Vérifier Kanban drag-drop
- [ ] Vérifier Dashboard Admin
- [ ] Vérifier Business Lines

### Phase 4 — Sprint 3 (Semaine 4)
- [ ] Copier SPRINT_3_TRACKER_SAAS.md dans Kimi Code
- [ ] Vérifier i18n
- [ ] Vérifier RGAA
- [ ] Vérifier production Docker
- [ ] Déployer sur VPS
- [ ] Lancer beta avec 3 testeurs

## Fréquence de Check-in

| Moment | Action |
|--------|--------|
| Après chaque action CEO | CEO reporte immédiatement |
| Toutes les 2-3h pendant Sprint | CEO reporte avancement Kimi Code |
| Fin de chaque Sprint | Revue complète + activation agents swarm |
| En cas de blocage > 30 min | CEO demande aide immédiatement |

## Règles d'Or

1. **Ne pas sauter d'étape.** Chaque sprint suppose le précédent terminé.
2. **Ne pas modifier le prompt.** Si Kimi Code ne comprend pas, couper en 2, ne pas réécrire.
3. **Tester immédiatement.** Quand Kimi Code produit du code, tester tout de suite.
4. **Git commit à chaque étape.** Ne jamais travailler sans commit.
5. **Demander de l'aide vite.** Si bloqué > 30 min, reporte immédiatement.

## Commandes Essentielles (à avoir sous la main)

```bash
# Vérifier que tout tourne
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Tests
pytest tests/ -v
cd frontend && npx playwright test

# Git
git add . && git commit -m "[Sprint X] Description" && git push

# Logs
docker compose logs -f app
docker compose logs -f db

# Backup
./scripts/backup-db.sh
```

## Contacts d'Urgence (Blocs CTO)

| Blocage | Solution |
|---------|----------|
| Kimi Code ne comprend pas le prompt | Couper le prompt en 2 parties |
| Docker ne démarre pas | Vérifier port 5432/8000/80 libres |
| Tests qui échouent | Copier-coller l'erreur, je diagnostique |
| Erreur 500 API | Vérifier logs Docker |
| Frontend qui ne build pas | Vérifier Node 20+ et npm install |
