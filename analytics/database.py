"""SQLite helpers for the LionsPath analytics importer."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import astuple
from datetime import datetime, timezone
from pathlib import Path

from .parser import RequestRecord


SCHEMA_PATH = Path(__file__).with_name("schema.sql")

INSERT_REQUEST_SQL = """
INSERT INTO requests (
    occurred_at_utc, timestamp_utc, timestamp_local, local_date, local_hour,
    local_weekday, visitor_day_hash, visitor_month_hash, method, path,
    normalized_path, status_code, bytes_sent, referrer_source, browser,
    operating_system, device_type, request_class, is_pageview, is_asset, is_bot,
    source_log, source_offset, log_fingerprint
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)
ON CONFLICT(log_fingerprint) DO NOTHING
"""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def connect_database(path: Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    if os.name == "posix":
        os.chmod(path, 0o600)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    connection.commit()


def insert_request(
    connection: sqlite3.Connection,
    record: RequestRecord,
    source_log: str,
    source_offset: int,
    fingerprint: str,
) -> bool:
    values = astuple(record) + (source_log, source_offset, fingerprint)
    cursor = connection.execute(INSERT_REQUEST_SQL, values)
    return cursor.rowcount == 1


def get_checkpoint(
    connection: sqlite3.Connection,
    source_identity: str,
) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM import_files WHERE source_identity = ?",
        (source_identity,),
    ).fetchone()


def save_checkpoint(
    connection: sqlite3.Connection,
    source_identity: str,
    current_path: str,
    byte_offset: int,
    size: int,
    mtime_ns: int,
    status: str,
) -> None:
    connection.execute(
        """
        INSERT INTO import_files (
            source_identity, current_path, byte_offset, last_size, last_mtime_ns,
            last_imported_at, last_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_identity) DO UPDATE SET
            current_path = excluded.current_path,
            byte_offset = excluded.byte_offset,
            last_size = excluded.last_size,
            last_mtime_ns = excluded.last_mtime_ns,
            last_imported_at = excluded.last_imported_at,
            last_status = excluded.last_status
        """,
        (
            source_identity,
            current_path,
            byte_offset,
            size,
            mtime_ns,
            utc_now_text(),
            status,
        ),
    )


def begin_import_run(connection: sqlite3.Connection, source_count: int) -> int:
    cursor = connection.execute(
        "INSERT INTO import_runs (started_at, status, source_count) VALUES (?, 'running', ?)",
        (utc_now_text(), source_count),
    )
    connection.commit()
    return int(cursor.lastrowid)


def finish_import_run(
    connection: sqlite3.Connection,
    run_id: int,
    status: str,
    lines_seen: int,
    rows_inserted: int,
    duplicates_skipped: int,
    malformed_skipped: int,
    error_message: str | None = None,
) -> None:
    connection.execute(
        """
        UPDATE import_runs
        SET finished_at = ?, status = ?, lines_seen = ?, rows_inserted = ?,
            duplicates_skipped = ?, malformed_skipped = ?, error_message = ?
        WHERE id = ?
        """,
        (
            utc_now_text(),
            status,
            lines_seen,
            rows_inserted,
            duplicates_skipped,
            malformed_skipped,
            error_message[:1000] if error_message else None,
            run_id,
        ),
    )
    connection.commit()
