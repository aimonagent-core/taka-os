# 🚀 TAKA OS — Guide de Deploiement Staging

## Prerequis

- Docker + Docker Compose v2+
- 4 GB RAM minimum
- 20 GB disque
- Acces Internet (pour pull images + API Mistral)

## Lancement rapide

```bash
# 1. Cloner le repo
git clone https://github.com/aimonagent-core/taka-os.git
cd taka-os

# 2. Configurer l'environnement
cp .env.staging.example .env.staging
nano .env.staging  # Remplir les variables (SECRET_KEY, MISTRAL_API_KEY, ...)

# 3. Lancer
bash scripts/staging-up.sh
```

## Acces

| Service | URL | Notes |
|---------|-----|-------|
| Frontend | `https://localhost/` | Certificat auto-signe |
| API | `https://localhost/api/v1/` | Bearer token requis |
| Health | `https://localhost/api/v1/health` | Sans auth |
| API Docs | `https://localhost/api/v1/docs` | Swagger UI |

## Architecture

```
[Internet] → [Nginx (443)] → { / → Frontend, /api/* → Backend }
                      ↓
              [Backend:8000] ← [DB:5432] + [Redis:6379]
```

## Commandes

```bash
# Logs
docker compose -f docker-compose.staging.yml logs -f

# Backup manuel
bash scripts/backup-db.sh

# Redemarrer
bash scripts/staging-down.sh && bash scripts/staging-up.sh

# Migrations
docker exec taka-backend-staging alembic upgrade head

# Shell backend
docker exec -it taka-backend-staging bash
```

## Mise a jour

```bash
cd /opt/taka-os
git pull origin main
bash scripts/staging-down.sh
bash scripts/staging-up.sh
```

## Production (v1.0+)

Pour la production, remplacer :
1. SSL auto-signe → Let's Encrypt (`certbot`)
2. `.env.staging` → `.env.production`
3. `docker-compose.staging.yml` → `docker-compose.production.yml`
4. Ajouter Sentry, monitoring, alerting
5. Multi-instance backend avec load balancer

## Troubleshooting

| Probleme | Solution |
|----------|----------|
| Certificat invalide | Accepter l'exception navigateur ou utiliser Let's Encrypt |
| DB inaccessible | `docker exec taka-db-staging pg_isready -U takaos` |
| Migration echoue | `docker exec taka-backend-staging alembic downgrade -1 && alembic upgrade head` |
| Frontend 404 | Verifier que `frontend/dist` existe apres `npm run build` |
