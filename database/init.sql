-- Runs automatically on first container start (mounted into
-- /docker-entrypoint-initdb.d/ in docker-compose.yml). Alembic owns the
-- actual table schema - this file just sets up what needs to exist
-- before Alembic runs at all.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
