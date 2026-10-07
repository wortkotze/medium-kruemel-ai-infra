-- ──────────────────────────────────────────────
-- scripts/init-hub-db.sql
-- Initializes Krümel AI Hub status monitoring schema & tables
-- Executed automatically on clean container initialization
-- ──────────────────────────────────────────────
\c litellm;

CREATE TABLE IF NOT EXISTS hub_status_logs (
    id BIGSERIAL PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    latency_ms INTEGER,
    http_code INTEGER,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hub_status_svc_time ON hub_status_logs(service_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_hub_status_time ON hub_status_logs(created_at DESC);
