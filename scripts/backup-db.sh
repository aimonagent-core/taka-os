#!/usr/bin/env bash
# File: scripts/backup-db.sh
# Purpose: Backup PostgreSQL database with compression and optional S3 upload
# Dependencies: pg_dump, gzip, awscli (optional)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_ROOT}/.env"

# Load env vars if .env exists
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Defaults
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-taka}"
DB_NAME="${POSTGRES_DB:-taka_db}"
DB_PASS="${POSTGRES_PASSWORD:-}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/taka-backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BACKUP_BUCKET:-}"
S3_ENDPOINT="${S3_BACKUP_ENDPOINT:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[BACKUP] Starting backup of $DB_NAME at $TIMESTAMP"

# Run pg_dump with compression
export PGPASSWORD="$DB_PASS"
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --no-owner --no-privileges | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"
unset PGPASSWORD

FILE_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
echo "[BACKUP] Completed: ${BACKUP_FILE} ($FILE_SIZE)"

# Upload to S3 if configured
if [ -n "$S3_BUCKET" ] && [ -n "$S3_ENDPOINT" ]; then
    echo "[BACKUP] Uploading to S3..."
    aws --endpoint-url "$S3_ENDPOINT" s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "s3://${S3_BUCKET}/${BACKUP_FILE}"
    echo "[BACKUP] S3 upload complete"
fi

# Local rotation
find "$BACKUP_DIR" -name "backup_${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "[BACKUP] Cleaned up backups older than $RETENTION_DAYS days"

# If cron mode, log to syslog
if [ "${CRON_MODE:-0}" = "1" ]; then
    logger -t taka-backup "Database backup completed: ${BACKUP_FILE} ($FILE_SIZE)"
fi

echo "[BACKUP] Done"
