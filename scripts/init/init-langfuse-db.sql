-- ──────────────────────────────────────────────
-- scripts/init-langfuse-db.sql
-- Creates the separate 'langfuse' database on fresh Postgres init
-- ──────────────────────────────────────────────
SELECT 'CREATE DATABASE langfuse'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'langfuse')\gexec

SELECT 'CREATE DATABASE n8n'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'n8n')\gexec

