#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/takaos_$TIMESTAMP.sql"

echo "💾 Backup PostgreSQL..."

mkdir -p "$BACKUP_DIR"

docker exec taka-db-staging pg_dump -U takaos takaos > "$BACKUP_FILE"

echo "✅ Backup cree : $BACKUP_FILE"
echo "   Taille : $(du -h "$BACKUP_FILE" | cut -f1)"

# Garder les 7 derniers backups
cd "$BACKUP_DIR"
ls -t takaos_*.sql 2>/dev/null | tail -n +8 | xargs -r rm --
echo "   🗑️  Anciens backups (>7 jours) supprimes"
