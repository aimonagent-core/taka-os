# TAKA OS — Checklist de Lancement IMMÉDIAT
## Ce qu'il faut faire aujourd'hui, demain, et la semaine prochaine

---

## PHASE 1 — Aujourd'hui (30 minutes)

### 1.1 Créer le repo GitHub

Aller sur https://github.com/new
- Nom du repo : `taka-os`
- Visibilité : **Public** (licence MIT)
- Check : Add a README file
- Check : Add .gitignore → choisir **Python**
- Licence : **MIT License**
- Click : Create repository

### 1.2 Cloner le repo localement

```bash
# Sur ton Mac/PC
git clone https://github.com/TON-USERNAME/taka-os.git
cd taka-os
```

### 1.3 Créer la structure de dossiers minimale

```bash
mkdir -p app/{api/v1/endpoints,core,models,services,schemas,dependencies}
mkdir -p frontend/src/{components,pages,hooks,lib,types}
mkdir -p tests
mkdir -p scripts
mkdir -p docs
mkdir -p .github/workflows
```

### 1.4 Premier commit

```bash
git add .
git commit -m "Initial commit — TAKA OS foundation structure"
git push origin main
```

### 1.5 Copier le Prompt Sprint 0

1. Ouvrir `/mnt/agents/output/prompts/SPRINT_0_FONDATION.md`
2. Sélectionner tout le contenu (Ctrl+A)
3. Copier (Ctrl+C)
4. Ouvrir Kimi Code (IDE)
5. Créer un nouveau fichier ou utiliser le chat
6. Coller le prompt entier
7. Envoyer à Kimi Code

**Résultat attendu :** Kimi Code commence à générer les 37 fichiers du Sprint 0.

---

## PHASE 2 — VPS (2 heures, peut attendre demain)

### 2.1 Choisir un VPS

| Hébergeur | Prix/mois | Localisation | Pourquoi |
|-----------|-----------|--------------|----------|
| **Scaleway** (recommandé) | 7-15€ | France (Paris) | RGPD, pricing transparent |
| **Hetzner** | 5-10€ | Allemagne | Excellent rapport qualité/prix |
| **OVHcloud** | 8-15€ | France | Familier, support FR |
| **DigitalOcean** | 12€ | Pays-Bas | Simple, bien documenté |

**Recommandation :** Scaleway DEV1-M (2 vCPU, 4 Go RAM, 40 Go SSD) = **~15€/mois**

### 2.2 Configurer le VPS (commandes exactes)

```bash
# Se connecter en SSH (Scaleway fournit l'IP et la clé)
ssh root@IP-DU-VPS

# 1. Mettre à jour le système
apt update && apt upgrade -y

# 2. Installer Docker
apt install -y docker.io docker-compose-plugin

# 3. Vérifier Docker
docker --version
docker compose version

# 4. Créer un utilisateur dédié (pas root)
adduser takaos
usermod -aG docker takaos

# 5. Installer Git
apt install -y git

# 6. Cloner le repo
su - takaos
git clone https://github.com/TON-USERNAME/taka-os.git

# 7. Tester Docker Compose (une fois Sprint 0 terminé)
cd taka-os
docker compose up -d
```

### 2.3 Configurer le nom de domaine (optionnel pour l'instant)

Pour l'instant, utiliser l'IP du VPS. Le domaine viendra plus tard (v0.3).

---

## PHASE 3 — Semaine 1 (Sprint 0, exécution par Kimi Code)

### 3.1 Ce que Kimi Code fait

Kimi Code lit le prompt SPRINT_0_FONDATION.md et génère :

```
taka-os/
├── pyproject.toml              <- Dépendances Python
├── .env.template               <- Variables d'environnement
├── docker-compose.yml          <- PostgreSQL + App + Nginx
├── Dockerfile                  <- Image production
├── app/
│   ├── main.py                 <- FastAPI app
│   ├── config.py               <- Pydantic Settings
│   ├── core/
│   │   ├── sentry.py           <- Error tracking
│   │   ├── security.py         <- JWT + bcrypt
│   │   ├── rate_limit.py       <- SlowAPI
│   │   ├── circuit_breaker.py  <- PyBreaker
│   │   └── audit.py            <- Hash chain audit
│   ├── models/
│   │   └── ao.py               <- 12 tables SQLAlchemy
│   ├── api/
│   │   └── v1/
│   │       ├── router.py       <- API router
│   │       └── endpoints/
│   │           ├── auth.py     <- Login/Register
│   │           ├── auth_mfa.py <- MFA TOTP
│   │           ├── tenants.py  <- CRUD tenants
│   │           └── health.py   <- Health check
│   └── services/
│       ├── feature_flags.py    <- Feature gating
│       └── audit_service.py    <- Audit log
├── frontend/
│   ├── package.json            <- React 18 + dépendances
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx            <- Sentry init
│   │   ├── App.tsx
│   │   └── components/
│   │       └── ErrorBoundary.tsx
│   └── index.html
├── scripts/
│   └── backup-db.sh            <- Backup PostgreSQL
└── tests/
    └── test_main.py            <- Tests pytest
```

### 3.2 Ce que le CEO fait en parallèle (pas de blocage)

| Jour | Action CEO | Résultat |
|------|-----------|----------|
| **J1** | Créer compte LinkedIn + Twitter/X pour TAKA OS | Identité sociale |
| **J1** | Rédiger un post "On construit TAKA OS" | Buzz initial |
| **J2** | Lister 10 PME soumissionnaires à contacter | Pipeline beta |
| **J2** | Créer landing page simple (Carrd ou Webflow) | Capture emails |
| **J3** | Contacter 3 beta-testeurs potentiels | Validation marché |
| **J4** | Rédiger modèle économique (MRR 12 mois) | Visions chiffrées |
| **J5** | Analyser concurrence en détail (Agora, Silex) | Positionnement |

### 3.3 Validation du Sprint 0

Après que Kimi Code ait terminé, vérifier :

```bash
# 1. Démarrer les conteneurs
cd taka-os
docker compose up -d

# 2. Vérifier que tout est up
docker compose ps
# Doit montrer : db (healthy), app (healthy), nginx (healthy)

# 3. Tester l'API
curl http://localhost:8000/health
# Réponse : {"status": "ok"}

# 4. Ouvrir Swagger
curl http://localhost:8000/docs
# Doit retourner le JSON OpenAPI

# 5. Tester le login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!"}'

# 6. Tester MFA setup
curl -X POST http://localhost:8000/api/v1/auth/mfa/setup \
  -H "Authorization: Bearer TOKEN"
# Doit retourner un secret et un URI pour QR code

# 7. Tester Sentry (forcer une erreur)
curl http://localhost:8000/api/v1/test-error
# Doit apparaître dans Sentry (dashboard sentry.io)

# 8. Tester rate limiting
for i in {1..110}; do curl -s http://localhost:8000/health > /dev/null; done
# La 101ème doit retourner 429 Too Many Requests

# 9. Exécuter les tests
pytest tests/ -v
# Doit passer 30+ tests

# 10. Tester le backup
./scripts/backup-db.sh
# Doit créer un fichier .sql.gz dans /var/backups/
```

---

## PHASE 4 — Semaines 2-4 (Sprints 1-3)

### 4.1 Répéter le même pattern

```
Semaine 2 : Copier SPRINT_1_SENSORIMOTRICE_MEMOIRE.md -> Kimi Code -> Exécuter -> Valider
Semaine 3 : Copier SPRINT_2_QUALIFIEUR_KANBAN.md -> Kimi Code -> Exécuter -> Valider
Semaine 4 : Copier SPRINT_3_TRACKER_SAAS.md -> Kimi Code -> Exécuter -> Valider -> Déployer
```

### 4.2 Déploiement Semaine 4

```bash
# Sur le VPS
su - takaos
cd taka-os
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
```

---

## RÉCAPITULATIF DES ACTIONS IMMÉDIATES

| Action | Qui | Quand | Durée |
|--------|-----|-------|-------|
| Créer repo GitHub | CEO | Aujourd'hui | 5 min |
| Cloner + structure dossiers | CEO | Aujourd'hui | 5 min |
| Copier SPRINT_0 dans Kimi Code | CEO | Aujourd'hui | 2 min |
| Lancer Kimi Code Sprint 0 | Kimi Code | Aujourd'hui | 2-4h |
| Configurer VPS | CEO | Demain | 1h |
| Lancer parallèle business (LinkedIn, landing) | CEO | Semaine 1 | 1-2h/jour |

---

## Si tu es bloqué à une étape

| Blocage | Solution |
|---------|----------|
| "Je ne sais pas créer un repo GitHub" | Aller sur github.com/new, copier les étapes ci-dessus |
| "Je n'ai pas de VPS" | Commencer en local (`docker compose up` sur ton Mac) |
| "Kimi Code ne comprend pas le prompt" | Couper le prompt en 2 parties (fichiers 1-15, puis 16-30) |
| "J'ai une erreur Docker" | Vérifier que Docker Desktop est ouvert (Mac) ou `sudo systemctl start docker` (Linux) |
| "Je veux tester avant de payer un VPS" | Utiliser Render.com (gratuit pour les petits projets) ou Railway |

---

## Point de départ = COPIER SPRINT_0_FONDATION.md DANS KIMI CODE

C'est la seule action qui bloque tout le reste. Tout le reste peut être fait en parallèle.

**GO.**
