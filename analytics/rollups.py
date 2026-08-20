"""Persistent aggregate tables used by the future analytics dashboard."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date

from .database import utc_now_text


@dataclass(frozen=True)
class RollupResult:
    start_date: str | None
    end_date: str | None
    daily_rows: int
    hourly_rows: int
    page_rows: int


def _validated_date(value: str | None) -> str | None:
    if value is None:
        return None
    return date.fromisoformat(value).isoformat()


def _request_date_range(
    connection: sqlite3.Connection,
    start_date: str | None,
    end_date: str | None,
) -> tuple[str | None, str | None]:
    start = _validated_date(start_date)
    end = _validated_date(end_date)
    available = connection.execute(
        "SELECT MIN(local_date), MAX(local_date) FROM requests"
    ).fetchone()
    if not available or available[0] is None:
        return None, None
    start = start or str(available[0])
    end = end or str(available[1])
    if start > end:
        raise ValueError("Rollup start date must be on or before the end date")
    return start, end


def refresh_rollups(
    connection: sqlite3.Connection,
    start_date: str | None = None,
    end_date: str | None = None,
) -> RollupResult:
    start, end = _request_date_range(connection, start_date, end_date)
    if start is None or end is None:
        return RollupResult(None, None, 0, 0, 0)

    refreshed_at = utc_now_text()
    with connection:
        connection.execute(
            "DELETE FROM analytics_daily WHERE local_date BETWEEN ? AND ?",
            (start, end),
        )
        connection.execute(
            "DELETE FROM analytics_hourly WHERE local_date BETWEEN ? AND ?",
            (start, end),
        )
        connection.execute(
            "DELETE FROM analytics_page_daily WHERE local_date BETWEEN ? AND ?",
            (start, end),
        )

        connection.execute(
            """
            INSERT INTO analytics_daily (
                local_date, total_requests, human_pageviews, bot_requests,
                asset_requests, estimated_daily_visitors, refreshed_at
            )
            SELECT
                local_date,
                COUNT(*),
                SUM(CASE WHEN is_pageview = 1 THEN 1 ELSE 0 END),
                SUM(CASE WHEN is_bot = 1 THEN 1 ELSE 0 END),
                SUM(CASE WHEN is_asset = 1 THEN 1 ELSE 0 END),
                COUNT(DISTINCT CASE WHEN is_bot = 0 THEN visitor_day_hash END),
                ?
            FROM requests
            WHERE local_date BETWEEN ? AND ?
            GROUP BY local_date
            """,
            (refreshed_at, start, end),
        )
        connection.execute(
            """
            INSERT INTO analytics_hourly (
                local_date, local_hour, total_requests, human_pageviews,
                estimated_visitors, refreshed_at
            )
            SELECT
                local_date,
                local_hour,
                COUNT(*),
                SUM(CASE WHEN is_pageview = 1 THEN 1 ELSE 0 END),
                COUNT(DISTINCT CASE WHEN is_bot = 0 THEN visitor_day_hash END),
                ?
            FROM requests
            WHERE local_date BETWEEN ? AND ?
            GROUP BY local_date, local_hour
            """,
            (refreshed_at, start, end),
        )
        connection.execute(
            """
            INSERT INTO analytics_page_daily (
                local_date, normalized_path, pageviews, estimated_visitors,
                refreshed_at
            )
            SELECT
                local_date,
                normalized_path,
                COUNT(*),
                COUNT(DISTINCT visitor_day_hash),
                ?
            FROM requests
            WHERE local_date BETWEEN ? AND ? AND is_pageview = 1
            GROUP BY local_date, normalized_path
            """,
            (refreshed_at, start, end),
        )

    daily_rows = int(
        connection.execute(
            "SELECT COUNT(*) FROM analytics_daily WHERE local_date BETWEEN ? AND ?",
            (start, end),
        ).fetchone()[0]
    )
    hourly_rows = int(
        connection.execute(
            "SELECT COUNT(*) FROM analytics_hourly WHERE local_date BETWEEN ? AND ?",
            (start, end),
        ).fetchone()[0]
    )
    page_rows = int(
        connection.execute(
            "SELECT COUNT(*) FROM analytics_page_daily WHERE local_date BETWEEN ? AND ?",
            (start, end),
        ).fetchone()[0]
    )
    connection.execute("PRAGMA optimize")
    return RollupResult(start, end, daily_rows, hourly_rows, page_rows)

