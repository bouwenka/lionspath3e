PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO schema_meta (key, value)
VALUES ('schema_version', '1')
ON CONFLICT(key) DO UPDATE SET value = excluded.value;

CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY,
    occurred_at_utc INTEGER NOT NULL,
    timestamp_utc TEXT NOT NULL,
    timestamp_local TEXT NOT NULL,
    local_date TEXT NOT NULL,
    local_hour INTEGER NOT NULL CHECK (local_hour BETWEEN 0 AND 23),
    local_weekday INTEGER NOT NULL CHECK (local_weekday BETWEEN 0 AND 6),
    visitor_day_hash TEXT NOT NULL,
    visitor_month_hash TEXT NOT NULL,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    normalized_path TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    bytes_sent INTEGER,
    referrer_source TEXT NOT NULL,
    browser TEXT NOT NULL,
    operating_system TEXT NOT NULL,
    device_type TEXT NOT NULL,
    request_class TEXT NOT NULL CHECK (
        request_class IN ('pageview', 'asset', 'api', 'bot', 'other')
    ),
    is_pageview INTEGER NOT NULL CHECK (is_pageview IN (0, 1)),
    is_asset INTEGER NOT NULL CHECK (is_asset IN (0, 1)),
    is_bot INTEGER NOT NULL CHECK (is_bot IN (0, 1)),
    source_log TEXT NOT NULL,
    source_offset INTEGER NOT NULL,
    log_fingerprint TEXT NOT NULL UNIQUE,
    imported_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_requests_occurred_at
    ON requests (occurred_at_utc);
CREATE INDEX IF NOT EXISTS idx_requests_local_date
    ON requests (local_date);
CREATE INDEX IF NOT EXISTS idx_requests_date_hour
    ON requests (local_date, local_hour);
CREATE INDEX IF NOT EXISTS idx_requests_path_date
    ON requests (normalized_path, local_date);
CREATE INDEX IF NOT EXISTS idx_requests_day_visitor
    ON requests (local_date, visitor_day_hash);
CREATE INDEX IF NOT EXISTS idx_requests_month_visitor
    ON requests (substr(local_date, 1, 7), visitor_month_hash);
CREATE INDEX IF NOT EXISTS idx_requests_class_date
    ON requests (request_class, local_date);
CREATE INDEX IF NOT EXISTS idx_requests_status_date
    ON requests (status_code, local_date);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    occurred_at_utc INTEGER NOT NULL,
    timestamp_local TEXT NOT NULL,
    local_date TEXT NOT NULL,
    local_hour INTEGER NOT NULL CHECK (local_hour BETWEEN 0 AND 23),
    visitor_day_hash TEXT NOT NULL,
    visitor_month_hash TEXT NOT NULL,
    session_hint TEXT,
    event_name TEXT NOT NULL,
    section TEXT,
    source_page TEXT,
    metadata_key TEXT,
    metadata_value TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_events_date_name
    ON events (local_date, event_name);
CREATE INDEX IF NOT EXISTS idx_events_occurred_at
    ON events (occurred_at_utc);
CREATE INDEX IF NOT EXISTS idx_events_day_visitor
    ON events (local_date, visitor_day_hash);

CREATE TABLE IF NOT EXISTS import_files (
    source_identity TEXT PRIMARY KEY,
    current_path TEXT NOT NULL,
    byte_offset INTEGER NOT NULL DEFAULT 0,
    last_size INTEGER NOT NULL DEFAULT 0,
    last_mtime_ns INTEGER NOT NULL DEFAULT 0,
    last_imported_at TEXT NOT NULL,
    last_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS import_runs (
    id INTEGER PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed', 'dry-run')),
    source_count INTEGER NOT NULL DEFAULT 0,
    lines_seen INTEGER NOT NULL DEFAULT 0,
    rows_inserted INTEGER NOT NULL DEFAULT 0,
    duplicates_skipped INTEGER NOT NULL DEFAULT 0,
    malformed_skipped INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_import_runs_started
    ON import_runs (started_at DESC);

CREATE TABLE IF NOT EXISTS analytics_daily (
    local_date TEXT PRIMARY KEY,
    total_requests INTEGER NOT NULL,
    human_pageviews INTEGER NOT NULL,
    bot_requests INTEGER NOT NULL,
    asset_requests INTEGER NOT NULL,
    estimated_daily_visitors INTEGER NOT NULL,
    refreshed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics_hourly (
    local_date TEXT NOT NULL,
    local_hour INTEGER NOT NULL,
    total_requests INTEGER NOT NULL,
    human_pageviews INTEGER NOT NULL,
    estimated_visitors INTEGER NOT NULL,
    refreshed_at TEXT NOT NULL,
    PRIMARY KEY (local_date, local_hour)
);

CREATE TABLE IF NOT EXISTS analytics_page_daily (
    local_date TEXT NOT NULL,
    normalized_path TEXT NOT NULL,
    pageviews INTEGER NOT NULL,
    estimated_visitors INTEGER NOT NULL,
    refreshed_at TEXT NOT NULL,
    PRIMARY KEY (local_date, normalized_path)
);

