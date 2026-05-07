#!/usr/bin/env bash
# =============================================================================
# dev-frontend.sh — Démarrage frontend TAKA OS en mode développement
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT/frontend"

# --- Vérification backend ---
echo "🔍 Checking backend on http://localhost:8001..."
if ! curl -sf http://localhost:8001/health >/dev/null 2>&1; then
    echo "❌ Backend not responding on :8001. Start it first:"
    echo "   ./scripts/dev-start.sh"
    exit 1
fi

echo "✅ Backend is alive."

# --- Lancement Vite dev server ---
export VITE_API_URL="http://localhost:8001/api/v1"
echo "🚀 Starting Vite dev server on http://localhost:5173"
echo "   API proxy → $VITE_API_URL"
npm run dev
