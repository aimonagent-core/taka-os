#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Lancement TAKA OS Staging..."

# 1. Verifier que .env.staging existe
if [ ! -f "$PROJECT_DIR/.env.staging" ]; then
    echo "❌ Fichier .env.staging manquant !"
    echo "   Copiez .env.staging.example vers .env.staging et configurez les variables."
    exit 1
fi

# 2. Generer les certificats SSL si necessaire
if [ ! -f "$PROJECT_DIR/docker/staging/nginx/ssl/taka.crt" ]; then
    echo "🔐 Generation des certificats SSL..."
    bash "$PROJECT_DIR/docker/staging/nginx/ssl/generate-ssl.sh"
fi

# 3. Build du frontend (production)
echo "📦 Build frontend..."
cd "$PROJECT_DIR/frontend"
npm install
npm run build

# 4. Build du backend (image Docker)
echo "🐳 Build backend Docker..."
cd "$PROJECT_DIR"
docker compose -f docker-compose.staging.yml build backend

# 5. Lancer les services
echo "▶️  Demarrage des services..."
docker compose -f docker-compose.staging.yml up -d

# 6. Attendre que la DB soit prete
echo "⏳ Attente de la base de donnees..."
sleep 5
until docker exec taka-db-staging pg_isready -U takaos > /dev/null 2>&1; do
    echo "   DB pas encore prete..."
    sleep 2
done

# 7. Lancer les migrations
echo "🗄️  Migrations Alembic..."
docker exec taka-backend-staging alembic upgrade head

# 8. Seed des donnees si necessaire
echo "🌱 Verification des seeds..."
docker exec taka-backend-staging python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.services.plan_feature_flags import FeatureFlagService
from app.agents.redacteur.templates import TemplateService

async def seed():
    async with AsyncSessionLocal() as db:
        await FeatureFlagService.seed_default_flags(db)

asyncio.run(seed())
" 2>/dev/null || echo "   Seeding deja effectue ou erreur non bloquante"

# 9. Status
echo ""
echo "✅ TAKA OS Staging est lance !"
echo ""
echo "   🌐 Frontend : https://localhost/ (ou votre domaine)"
echo "   🔌 API      : https://localhost/api/v1/"
echo "   📊 Health   : https://localhost/api/v1/health"
echo "   🗄️  DB       : interne (non exposee)"
echo ""
echo "   ⚠️  Le certificat est auto-signe — acceptez l'exception dans le navigateur"
echo ""
echo "   Commandes utiles :"
echo "     logs  : docker compose -f docker-compose.staging.yml logs -f"
echo "     stop  : docker compose -f docker-compose.staging.yml down"
echo "     shell : docker exec -it taka-backend-staging bash"
