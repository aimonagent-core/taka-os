# TAKA API

TAKA - Plateforme d'appels d'offres automatises par IA.

## Stack Technique

- **Backend**: FastAPI 0.115+, SQLAlchemy 2.0 (async), PostgreSQL 16 + pgvector
- **Auth**: JWT (python-jose) + bcrypt + pyotp MFA
- **Rate Limiting**: SlowAPI with Redis fallback
- **Monitoring**: Sentry SDK
- **Circuit Breaker**: PyCircuitBreaker
- **Frontend**: React 18 + TypeScript + Vite
- **Tests**: pytest, pytest-asyncio, httpx
- **CI/CD**: GitHub Actions

## Demarrage Rapide

```bash
# 1. Copier les variables d'environnement
cp .env.template .env

# 2. Lancer l'ensemble de la stack
docker-compose up --build

# 3. Verifier la sante du backend
curl http://localhost:8000/api/v1/health/live
```

## Structure du Projet

```
taka/
├── app/
│   ├── main.py              # Point d'entree FastAPI
│   ├── config.py            # Configuration Pydantic Settings
│   ├── database.py          # SQLAlchemy async + pgvector
│   ├── dependencies.py      # Dependances FastAPI reutilisables
│   ├── core/                # Securite, audit, Sentry, rate limit, circuit breaker
│   ├── models/              # Modeles SQLAlchemy (15+ tables)
│   ├── schemas/             # Schemas Pydantic v2
│   ├── api/v1/              # Routes API v1
│   └── services/            # Services metier (feature flags, audit)
├── tests/                   # Tests pytest avec couverture > 80%
├── scripts/                 # Backup/restore PostgreSQL
├── frontend/                # Application React 18 + Vite
├── docker-compose.yml       # Stack complete (DB, Redis, backend, frontend)
└── .github/workflows/ci.yml # Pipeline CI/CD
```

## Roles Utilisateur

Les 5 roles sont hierarchiques :
1. `super_admin` > 
2. `tenant_admin` > 
3. `tenant_manager` > 
4. `tenant_collaborator` > 
5. `viewer`

## Fonctionnalites Cles

- **Authentification JWT** avec refresh tokens et MFA TOTP
- **Multi-tenant** avec isolation par tenant_id
- **Feature Flags** avec kill switch, plan gating, et rollout percentage
- **Memoire Persistante** a 3 niveaux (global, tenant, session)
- **Audit Forensique** avec hash chain SHA-256
- **Rate Limiting** par utilisateur/IP avec Redis
- **Circuit Breaker** sur tous les appels externes
- **Soft Delete** sur toutes les entites

## Licence

Proprietaire - TAKA Team
