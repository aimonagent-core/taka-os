#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Alembic crée cette table avec version_num VARCHAR(32) par défaut,
    -- ce qui est trop court pour certains noms de migration (> 32 caractères).
    -- On la pré-créée avec VARCHAR(128) pour éviter l'erreur.
    CREATE TABLE IF NOT EXISTS alembic_version (
        version_num VARCHAR(128) NOT NULL,
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
    );
EOSQL

echo "Extensions PostgreSQL créées : vector, uuid-ossp"
echo "Table alembic_version pré-créée avec VARCHAR(128)"
