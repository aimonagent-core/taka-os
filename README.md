# TAKA OS

Système d'exploitation IA open-source pour les appels d'offres publics.

## Quick Start

```bash
git clone https://github.com/USERNAME/taka-os.git
cd taka-os
cp .env.staging.example .env
docker compose up -d
# Accéder à http://localhost
```

## Documentation

- [CHANGELOG](CHANGELOG.md)
- [Guide de déploiement](DEPLOY.md)

## Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15 + pgvector
- **Auth**: JWT + bcrypt + MFA TOTP + 5 rôles RBAC
- **AI**: Mistral AI (embeddings 1024d + LLM)
- **Frontend**: React 18 + TypeScript + Vite + Recharts
- **Billing**: Stripe Checkout (3 tiers)
- **Email**: Resend
- **Cache/Queue**: Redis
- **Monitoring**: Sentry

## Fonctionnalités clés

- **Veille** : 10 sources d'appels d'offres (France, Belgique, Maroc, UE)
- **Scoring IA** : Score multi-dimensionnel avec explicabilité (XAI)
- **Rédaction** : Génération de réponses avec templates métier
- **Dépôt** : Soumission automatique sur plateformes publiques
- **Analytics** : Funnel, ROI estimé, prédictions de gain
- **Collaboration** : Commentaires, mentions @user, workflow d'approbation
- **API Publique** : Clés API sécurisées, rate limiting
- **Fiducial** : Écritures comptables, export FEC
- **PWA** : Installable sur mobile, mode offline

## Licence

MIT License
