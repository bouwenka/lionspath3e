"""Aggregate reporting queries for the private LionsPath analytics API."""

from __future__ import annotations

import os
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


PAGE_TITLES = {
    "/": "Home",
    "/home": "Home",
    "/compass": "Career Compass",
    "/enrollment": "Enrollment",
    "/employment": "Employment",
    "/enlistment": "Enlistment",
    "/explorer": "Course Explorer",
    "/coach": "AI Coach",
    "/evidence": "Evidence / Readiness",
    "/plan": "My 3E Pathway Plan",
    "/training": "Help / Training",
}

FEATURE_TITLES = {
    "section_view": "Section Views",
    "career_assessment_start": "Career Assessment Starts",
    "career_assessment_complete": "Career Assessment Completions",
    "course_explorer_open": "Course Explorer Opens",
    "plan_open": "My Plan Opens",
    "plan_print": "Plan Prints",
    "plan_pdf_download": "Plan PDF Downloads",
    "evidence_open": "Evidence Opens",
    "evidence_pdf_download": "Evidence PDF Downloads",
    "ai_coach_open": "AI Coach Opens",
    "schoolai_launch": "SchoolAI Launches",
    "voice_coach_launch": "Voice Coach Launches",
    "counseling_link_open": "Counseling Link Opens",
}


@dataclass(frozen=True)
class DateRange:
    start: str
    end: str

    @property
    def days(self) -> int:
        return (date.fromisoformat(self.end) - date.fromisoformat(self.start)).days + 1


def _latest_available_date(connection: sqlite3.Connection, timezone_name: str) -> str:
    row = connection.execute(
        """
        SELECT MAX(local_date) FROM (
            SELECT MAX(local_date) AS local_date FROM requests
            UNION ALL
            SELECT MAX(local_date) AS local_date FROM events
        )
        """
    ).fetchone()
    if row and row[0]:
        return str(row[0])
    return datetime.now(ZoneInfo(timezone_name)).date().isoformat()


def resolve_date_range(
    connection: sqlite3.Connection,
    start: str | None,
    end: str | None,
    timezone_name: str = "America/New_York",
) -> DateRange:
    latest = date.fromisoformat(_latest_available_date(connection, timezone_name))
    end_date = date.fromisoformat(end) if end else latest
    start_date = date.fromisoformat(start) if start else end_date - timedelta(days=6)
    if start_date > end_date:
        raise ValueError("Start date must be on or before end date")
    if (end_date - start_date).days > 7305:
        raise ValueError("Date range cannot exceed 20 years")
    return DateRange(start_date.isoformat(), end_date.isoformat())


def previous_date_range(period: DateRange) -> DateRange:
    start_date = date.fromisoformat(period.start)
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period.days - 1)
    return DateRange(previous_start.isoformat(), previous_end.isoformat())


def _percentage_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 1)


def _visitor_estimate(connection: sqlite3.Connection, period: DateRange) -> int:
    row = connection.execute(
        """
        WITH visitors AS (
            SELECT substr(local_date, 1, 7) AS month_key, visitor_month_hash AS visitor
            FROM requests
            WHERE local_date BETWEEN ? AND ? AND is_bot = 0
            UNION
            SELECT substr(local_date, 1, 7) AS month_key, visitor_month_hash AS visitor
            FROM events
            WHERE local_date BETWEEN ? AND ?
        ), monthly AS (
            SELECT month_key, COUNT(DISTINCT visitor) AS visitors
            FROM visitors
            GROUP BY month_key
        )
        SELECT COALESCE(SUM(visitors), 0) FROM monthly
        """,
        (period.start, period.end, period.start, period.end),
    ).fetchone()
    return int(row[0] or 0)


def _activity_rows(
    connection: sqlite3.Connection,
    period: DateRange,
) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT visitor_day_hash AS visitor, occurred_at_utc AS occurred_at
             , 1 AS is_content_view
        FROM requests
        WHERE local_date BETWEEN ? AND ? AND is_pageview = 1
        UNION ALL
        SELECT visitor_day_hash AS visitor, occurred_at_utc AS occurred_at,
               CASE WHEN event_name = 'section_view' THEN 1 ELSE 0 END AS is_content_view
        FROM events
        WHERE local_date BETWEEN ? AND ?
        ORDER BY visitor, occurred_at
        """,
        (period.start, period.end, period.start, period.end),
    ).fetchall()


def _session_stats(rows: Iterable[sqlite3.Row]) -> dict[str, Any]:
    session_count = 0
    activity_count = 0
    content_view_count = 0
    duration_total = 0
    current_visitor: str | None = None
    session_start = 0
    previous_time = 0
    current_events = 0

    def close_session() -> None:
        nonlocal session_count, duration_total, current_events
        if current_events:
            session_count += 1
            duration_total += max(0, previous_time - session_start)
            current_events = 0

    for row in rows:
        visitor = str(row["visitor"])
        occurred_at = int(row["occurred_at"])
        activity_count += 1
        content_view_count += int(row["is_content_view"])
        if visitor != current_visitor or (current_events and occurred_at - previous_time > 1800):
            close_session()
            current_visitor = visitor
            session_start = occurred_at
        previous_time = occurred_at
        current_events += 1
    close_session()

    return {
        "sessions": session_count,
        "activity_count": activity_count,
        "content_view_count": content_view_count,
        "pages_per_session": round(content_view_count / session_count, 1) if session_count else 0.0,
        "average_session_duration_seconds": round(duration_total / session_count) if session_count else 0,
    }


def summary_for_period(connection: sqlite3.Connection, period: DateRange) -> dict[str, Any]:
    request_row = connection.execute(
        """
        SELECT
            COUNT(*) AS total_requests,
            COALESCE(SUM(is_pageview), 0) AS server_pageviews,
            COALESCE(SUM(is_bot), 0) AS bot_requests,
            COALESCE(SUM(is_asset), 0) AS asset_requests,
            COALESCE(SUM(CASE WHEN status_code BETWEEN 400 AND 499 THEN 1 ELSE 0 END), 0) AS errors_4xx,
            COALESCE(SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END), 0) AS errors_5xx
        FROM requests
        WHERE local_date BETWEEN ? AND ?
        """,
        (period.start, period.end),
    ).fetchone()
    section_views = int(
        connection.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE local_date BETWEEN ? AND ? AND event_name = 'section_view'
            """,
            (period.start, period.end),
        ).fetchone()[0]
    )
    sessions = _session_stats(_activity_rows(connection, period))
    return {
        "estimated_visitors": _visitor_estimate(connection, period),
        "page_views": int(request_row["server_pageviews"]),
        "site_loads": int(request_row["server_pageviews"]),
        "server_pageviews": int(request_row["server_pageviews"]),
        "section_views": section_views,
        "sessions": sessions["sessions"],
        "pages_per_session": sessions["pages_per_session"],
        "average_session_duration_seconds": sessions["average_session_duration_seconds"],
        "total_requests": int(request_row["total_requests"]),
        "bot_requests": int(request_row["bot_requests"]),
        "asset_requests": int(request_row["asset_requests"]),
        "errors_4xx": int(request_row["errors_4xx"]),
        "errors_5xx": int(request_row["errors_5xx"]),
    }


def summary_with_comparison(
    connection: sqlite3.Connection,
    period: DateRange,
) -> dict[str, Any]:
    previous = previous_date_range(period)
    current_values = summary_for_period(connection, period)
    previous_values = summary_for_period(connection, previous)
    comparisons = {
        key: _percentage_change(float(value), float(previous_values.get(key, 0)))
        for key, value in current_values.items()
        if isinstance(value, (int, float))
    }
    return {
        "period": {"start": period.start, "end": period.end, "days": period.days},
        "previous_period": {"start": previous.start, "end": previous.end},
        "current": current_values,
        "previous": previous_values,
        "change_percent": comparisons,
        "visitor_method": "Monthly rotating privacy hashes; ranges crossing months sum monthly estimates.",
    }


def choose_granularity(period: DateRange, requested: str | None = None) -> str:
    allowed = {"hour", "day", "week", "month", "year"}
    if requested and requested != "auto":
        if requested not in allowed:
            raise ValueError("Unsupported trend granularity")
        return requested
    if period.days <= 2:
        return "hour"
    if period.days <= 90:
        return "day"
    if period.days <= 730:
        return "week"
    if period.days <= 3650:
        return "month"
    return "year"


def _bucket(local_date: str, local_hour: int, granularity: str) -> str:
    parsed = date.fromisoformat(local_date)
    if granularity == "hour":
        return f"{local_date}T{local_hour:02d}:00"
    if granularity == "day":
        return local_date
    if granularity == "week":
        iso = parsed.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    if granularity == "month":
        return local_date[:7]
    return local_date[:4]


def usage_trend(
    connection: sqlite3.Connection,
    period: DateRange,
    requested_granularity: str | None = None,
) -> dict[str, Any]:
    granularity = choose_granularity(period, requested_granularity)
    rows = connection.execute(
        """
        SELECT local_date, local_hour, visitor_day_hash, visitor_month_hash
        FROM requests
        WHERE local_date BETWEEN ? AND ? AND is_pageview = 1
        """,
        (period.start, period.end),
    ).fetchall()
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"page_views": 0, "visitors": set()}
    )
    visitor_field = "visitor_day_hash" if granularity in {"hour", "day"} else "visitor_month_hash"
    for row in rows:
        key = _bucket(str(row["local_date"]), int(row["local_hour"]), granularity)
        grouped[key]["page_views"] += 1
        grouped[key]["visitors"].add(str(row[visitor_field]))
    if granularity != "hour":
        cursor = date.fromisoformat(period.start)
        end_date = date.fromisoformat(period.end)
        while cursor <= end_date:
            grouped[_bucket(cursor.isoformat(), 0, granularity)]
            cursor += timedelta(days=1)
    points = [
        {
            "period": key,
            "site_loads": grouped[key]["page_views"],
            "page_views": grouped[key]["page_views"],
            "estimated_visitors": len(grouped[key]["visitors"]),
        }
        for key in sorted(grouped)
    ]
    return {"granularity": granularity, "points": points}


def friendly_page_title(path: str) -> str:
    if path in PAGE_TITLES:
        return PAGE_TITLES[path]
    cleaned = path.strip("/").replace("-", " ").replace("_", " ")
    return cleaned.title() if cleaned else "Home"


def top_pages(connection: sqlite3.Connection, period: DateRange, limit: int = 15) -> list[dict[str, Any]]:
    page_visitors: dict[str, set[str]] = defaultdict(set)
    page_views: dict[str, int] = defaultdict(int)
    request_rows = connection.execute(
        """
        SELECT normalized_path, visitor_day_hash
        FROM requests
        WHERE local_date BETWEEN ? AND ? AND is_pageview = 1
        """,
        (period.start, period.end),
    ).fetchall()
    event_rows = connection.execute(
        """
        SELECT section, visitor_day_hash
        FROM events
        WHERE local_date BETWEEN ? AND ? AND event_name = 'section_view' AND section IS NOT NULL
        """,
        (period.start, period.end),
    ).fetchall()
    for row in request_rows:
        path = str(row["normalized_path"])
        page_views[path] += 1
        page_visitors[path].add(str(row["visitor_day_hash"]))
    for row in event_rows:
        path = "/" + str(row["section"]).strip("/")
        page_views[path] += 1
        page_visitors[path].add(str(row["visitor_day_hash"]))
    total = sum(page_views.values())
    ranked = sorted(page_views, key=lambda value: (-page_views[value], value))[:max(1, min(limit, 100))]
    return [
        {
            "path": path,
            "title": friendly_page_title(path),
            "views": page_views[path],
            "estimated_visitors": len(page_visitors[path]),
            "traffic_percent": round((page_views[path] / total) * 100, 1) if total else 0.0,
        }
        for path in ranked
    ]


def event_usage(connection: sqlite3.Connection, period: DateRange) -> dict[str, Any]:
    rows = connection.execute(
        """
        SELECT event_name, COALESCE(section, '') AS section, COUNT(*) AS uses,
               COUNT(DISTINCT visitor_day_hash) AS visitors
        FROM events
        WHERE local_date BETWEEN ? AND ?
        GROUP BY event_name, COALESCE(section, '')
        ORDER BY uses DESC, event_name, section
        """,
        (period.start, period.end),
    ).fetchall()
    features = [
        {
            "event": str(row["event_name"]),
            "title": FEATURE_TITLES.get(str(row["event_name"]), str(row["event_name"]).replace("_", " ").title()),
            "section": str(row["section"]),
            "uses": int(row["uses"]),
            "estimated_visitors": int(row["visitors"]),
        }
        for row in rows
    ]
    three_e_counts = {"enrollment": 0, "employment": 0, "enlistment": 0}
    for item in features:
        if item["event"] == "section_view" and item["section"] in three_e_counts:
            three_e_counts[item["section"]] += item["uses"]
    three_e_total = sum(three_e_counts.values())
    coverage_row = connection.execute(
        """
        SELECT MIN(local_date) AS first_date, MAX(local_date) AS last_date, COUNT(*) AS events
        FROM events
        """
    ).fetchone()
    three_e = [
        {
            "section": key,
            "title": key.title(),
            "views": value,
            "percent": round((value / three_e_total) * 100, 1) if three_e_total else 0.0,
        }
        for key, value in three_e_counts.items()
    ]
    return {
        "features": features,
        "three_e": three_e,
        "coverage": {
            "first_event_date": coverage_row["first_date"],
            "last_event_date": coverage_row["last_date"],
            "all_time_events": int(coverage_row["events"] or 0),
            "selected_events": sum(item["uses"] for item in features),
            "selected_three_e_views": three_e_total,
        },
    }


def request_breakdown(
    connection: sqlite3.Connection,
    period: DateRange,
    column: str,
) -> list[dict[str, Any]]:
    allowed = {
        "device": "device_type",
        "browser": "browser",
        "os": "operating_system",
        "referrer": "referrer_source",
    }
    if column not in allowed:
        raise ValueError("Unsupported breakdown")
    database_column = allowed[column]
    rows = connection.execute(
        f"""
        SELECT {database_column} AS label, COUNT(*) AS views,
               COUNT(DISTINCT visitor_day_hash) AS visitors
        FROM requests
        WHERE local_date BETWEEN ? AND ? AND is_pageview = 1
        GROUP BY {database_column}
        ORDER BY views DESC, label
        """,
        (period.start, period.end),
    ).fetchall()
    total = sum(int(row["views"]) for row in rows)
    return [
        {
            "label": str(row["label"]),
            "views": int(row["views"]),
            "estimated_visitors": int(row["visitors"]),
            "percent": round((int(row["views"]) / total) * 100, 1) if total else 0.0,
        }
        for row in rows
    ]


def time_patterns(connection: sqlite3.Connection, period: DateRange) -> dict[str, Any]:
    hourly_rows = connection.execute(
        """
        SELECT local_hour, COUNT(*) AS views
        FROM requests
        WHERE local_date BETWEEN ? AND ? AND is_pageview = 1
        GROUP BY local_hour ORDER BY local_hour
        """,
        (period.start, period.end),
    ).fetchall()
    weekday_rows = connection.execute(
        """
        SELECT local_weekday, COUNT(*) AS views,
               COUNT(DISTINCT substr(local_date, 1, 7) || ':' || visitor_month_hash) AS visitors
        FROM requests
        WHERE local_date BETWEEN ? AND ? AND is_pageview = 1
        GROUP BY local_weekday ORDER BY local_weekday
        """,
        (period.start, period.end),
    ).fetchall()
    heatmap_rows = connection.execute(
        """
        SELECT local_weekday, local_hour, COUNT(*) AS views
        FROM requests
        WHERE local_date BETWEEN ? AND ? AND is_pageview = 1
        GROUP BY local_weekday, local_hour
        ORDER BY local_weekday, local_hour
        """,
        (period.start, period.end),
    ).fetchall()
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    calendar_days = Counter()
    cursor = date.fromisoformat(period.start)
    end_date = date.fromisoformat(period.end)
    while cursor <= end_date:
        calendar_days[cursor.weekday()] += 1
        cursor += timedelta(days=1)
    weekday_lookup = {int(row["local_weekday"]): row for row in weekday_rows}
    return {
        "hourly": [{"hour": int(row["local_hour"]), "views": int(row["views"])} for row in hourly_rows],
        "weekday": [
            {
                "weekday": weekday,
                "label": weekday_names[weekday],
                "views": int(weekday_lookup[weekday]["views"]) if weekday in weekday_lookup else 0,
                "estimated_visitors": int(weekday_lookup[weekday]["visitors"]) if weekday in weekday_lookup else 0,
                "calendar_days": calendar_days[weekday],
                "average_views": round(
                    (int(weekday_lookup[weekday]["views"]) if weekday in weekday_lookup else 0)
                    / calendar_days[weekday],
                    1,
                ) if calendar_days[weekday] else 0.0,
            }
            for weekday in range(7)
        ],
        "heatmap": [
            {
                "weekday": int(row["local_weekday"]),
                "hour": int(row["local_hour"]),
                "views": int(row["views"]),
            }
            for row in heatmap_rows
        ],
    }


def technical_health(connection: sqlite3.Connection, period: DateRange) -> dict[str, Any]:
    statuses = connection.execute(
        """
        SELECT (status_code / 100) || 'xx' AS label, COUNT(*) AS requests
        FROM requests
        WHERE local_date BETWEEN ? AND ?
        GROUP BY status_code / 100 ORDER BY status_code / 100
        """,
        (period.start, period.end),
    ).fetchall()
    errors = connection.execute(
        """
        SELECT status_code, normalized_path, COUNT(*) AS requests
        FROM requests
        WHERE local_date BETWEEN ? AND ? AND status_code >= 400
        GROUP BY status_code, normalized_path
        ORDER BY requests DESC, status_code DESC, normalized_path
        LIMIT 20
        """,
        (period.start, period.end),
    ).fetchall()
    bots = connection.execute(
        """
        SELECT
            SUM(CASE WHEN is_bot = 0 THEN 1 ELSE 0 END) AS human,
            SUM(CASE WHEN is_bot = 1 THEN 1 ELSE 0 END) AS bot
        FROM requests WHERE local_date BETWEEN ? AND ?
        """,
        (period.start, period.end),
    ).fetchone()
    return {
        "statuses": [{"label": str(row["label"]), "requests": int(row["requests"])} for row in statuses],
        "top_errors": [
            {
                "status": int(row["status_code"]),
                "path": str(row["normalized_path"]),
                "requests": int(row["requests"]),
            }
            for row in errors
        ],
        "traffic": {"human_requests": int(bots["human"] or 0), "bot_requests": int(bots["bot"] or 0)},
    }


def diagnostics(connection: sqlite3.Connection, database_path: Path) -> dict[str, Any]:
    latest_run = connection.execute(
        "SELECT * FROM import_runs ORDER BY id DESC LIMIT 1"
    ).fetchone()
    request_range = connection.execute(
        "SELECT MIN(timestamp_local), MAX(timestamp_local), COUNT(*) FROM requests"
    ).fetchone()
    return {
        "last_import": dict(latest_run) if latest_run else None,
        "oldest_timestamp": request_range[0],
        "newest_timestamp": request_range[1],
        "request_rows": int(request_range[2] or 0),
        "database_bytes": os.path.getsize(database_path) if Path(database_path).is_file() else 0,
    }


def build_report(
    connection: sqlite3.Connection,
    database_path: Path,
    period: DateRange,
    granularity: str | None = None,
) -> dict[str, Any]:
    events = event_usage(connection, period)
    return {
        "summary": summary_with_comparison(connection, period),
        "trend": usage_trend(connection, period, granularity),
        "pages": top_pages(connection, period),
        "features": events["features"],
        "three_e": events["three_e"],
        "event_coverage": events["coverage"],
        "devices": request_breakdown(connection, period, "device"),
        "browsers": request_breakdown(connection, period, "browser"),
        "operating_systems": request_breakdown(connection, period, "os"),
        "referrers": request_breakdown(connection, period, "referrer"),
        "time_patterns": time_patterns(connection, period),
        "technical_health": technical_health(connection, period),
        "diagnostics": diagnostics(connection, database_path),
    }

