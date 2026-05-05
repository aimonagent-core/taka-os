#!/usr/bin/env bash
# File: scripts/restore-db.sh
# Purpose: Restore PostgreSQL database from a backup file
# Dependencies: psql, gunzip, awscli (optional)

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup_file_or_s3_path> [--test]"
    echo "  backup_file: local path or s3://bucket/path"
    echo "  --test: restore to a temporary database for validation"
    exit 1
fi

BACKUP_SOURCE="$1"
TEST_MODE=0
if [ "${2:-}" = "--test" ]; then
    TEST_MODE=1
fi

ENV_FILE="$(dirname "$(dirname "$(realpath "$0")")")/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-taka}"
DB_NAME="${POSTGRES_DB:-taka_db}"
DB_PASS="${POSTGRES_PASSWORD:-}"

export PGPASSWORD="$DB_PASS"

# Determine backup file path
if [[ "$BACKUP_SOURCE" == s3://* ]]; then
    LOCAL_BACKUP="/tmp/restore_$(basename "$BACKUP_SOURCE")"
    echo "[RESTORE] Downloading from S3..."
    aws s3 cp "$BACKUP_SOURCE" "$LOCAL_BACKUP"
else
    LOCAL_BACKUP="$BACKUP_SOURCE"
fi

# Decompress if needed
if [[ "$LOCAL_BACKUP" == *.gz ]]; then
    echo "[RESTORE] Decompressing..."
    gunzip -c "$LOCAL_BACKUP" > /tmp/restore_dump.sql
    SQL_FILE="/tmp/restore_dump.sql"
else
    SQL_FILE="$LOCAL_BACKUP"
fi

# Test mode: create temp DB
if [ "$TEST_MODE" -eq 1 ]; then
    TEST_DB="${DB_NAME}_test_restore_$(date +%s)"
    echo "[RESTORE] TEST MODE - Creating temp database $TEST_DB"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $TEST_DB;"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" -f "$SQL_FILE"
    TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")
    echo "[RESTORE] Test restore successful. Tables restored: $TABLE_COUNT"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE $TEST_DB;"
    echo "[RESTORE] Temp database dropped"
else
    echo "[RESTORE] WARNING: This will overwrite database $DB_NAME"
    echo "[RESTORE] Press Ctrl+C within 5 seconds to cancel..."
    sleep 5
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"
    echo "[RESTORE] Database restored successfully"
fi

unset PGPASSWORD
rm -f /tmp/restore_dump.sql

echo "[RESTORE] Done"
