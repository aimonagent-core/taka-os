#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛑 Arret TAKA OS Staging..."

cd "$PROJECT_DIR"
docker compose -f docker-compose.staging.yml down

echo "✅ Services arretes."
