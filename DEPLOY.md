# Guide de déploiement TAKA OS v1.0.0

## Prérequis
- Docker Desktop 4.20+ ou Docker Engine 24.0+
- Docker Compose v2+
- 4 CPU, 8 GB RAM minimum
- 20 GB d'espace disque

## Déploiement local (développement)

```bash
git clone <repo>
cd taka-os
cp .env.staging.example .env
# Éditer .env avec vos clés (Stripe, Mistral, Resend)
docker compose -f docker-compose.yml up -d --build
```

## Migrations

```bash
docker compose run --rm backend alembic upgrade head
```

## Premiers pas

1. Créer un compte via `/register`
2. Compléter l'onboarding wizard
3. Vérifier le dashboard à `/`

## Variables d'environnement obligatoires

- `MISTRAL_API_KEY` — Clé API Mistral AI
- `SECRET_KEY` — Clé secrète JWT (générer : `openssl rand -hex 32`)
- `DATABASE_URL` — URL PostgreSQL (défaut dans docker-compose)

## Variables optionnelles

- `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOK_SECRET` — Paiements
- `RESEND_API_KEY` — Emails
- `REDIS_URL` — Rate limiting (défaut : `redis://redis:6379/0`)
- `SENTRY_DSN` — Monitoring d'erreurs

## Health checks

```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

## Upgrade

```bash
git pull origin main
docker compose build backend
docker compose run --rm backend alembic upgrade head
docker compose up -d
```
