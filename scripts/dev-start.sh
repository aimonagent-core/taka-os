#!/usr/bin/env bash
# =============================================================================
# dev-start.sh — Démarrage backend TAKA OS en mode développement
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# --- Vérification taka-db Docker ---
if ! docker ps --format '{{.Names}}' | grep -q '^taka-db$'; then
    echo "❌ taka-db n'est pas en cours d'exécution. Démarrez-le d'abord :"
    echo "   docker compose up -d db"
    exit 1
fi

# --- Vérification taka-redis Docker ---
if ! docker ps --format '{{.Names}}' | grep -q '^taka-redis$'; then
    echo "⚠️  taka-redis n'est pas en cours d'exécution. Démarrez-le d'abord :"
    echo "   docker compose up -d redis"
    exit 1
fi

# --- Exports environnement ---
export DATABASE_URL="postgresql+asyncpg://taka:takapass@localhost:5433/takaos"
export REDIS_URL="redis://localhost:6380/0"
export SECRET_KEY="${SECRET_KEY:-dev-secret-key-change-me-in-production}"

# --- Venv binaries ---
VENV_BIN="$PROJECT_ROOT/.venv/bin"
if [ ! -f "$VENV_BIN/uvicorn" ]; then
    echo "❌ Virtualenv not found at $PROJECT_ROOT/.venv"
    echo "   Run: uv venv --python 3.12 && poetry install"
    exit 1
fi

# --- Alembic migrations ---
echo "🔄 Running alembic upgrade head..."
"$VENV_BIN/alembic" upgrade head

# --- Uvicorn dev server ---
echo "🚀 Starting uvicorn on http://localhost:8001 (auto-reload)"
"$VENV_BIN/uvicorn" app.main:app --host 0.0.0.0 --port 8001 --reload
