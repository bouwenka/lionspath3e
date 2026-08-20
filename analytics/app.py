"""WSGI application for private reports and privacy-limited event ingestion."""

from __future__ import annotations

import csv
import ipaddress
import io
import json
import logging
import os
import re
import sqlite3
import threading
import time
from collections import defaultdict, deque
from contextlib import closing
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

from .config import AnalyticsConfig, load_config
from .database import connect_database, initialize_database
from .privacy import daily_visitor_hash, monthly_visitor_hash
from .queries import (
    DateRange,
    build_report,
    event_usage,
    request_breakdown,
    resolve_date_range,
    time_patterns,
    top_pages,
)


LOGGER = logging.getLogger("lionspath.analytics")
MAX_EVENT_BODY_BYTES = 2048
MAX_QUERY_STRING_BYTES = 2048
MAX_QUERY_FIELDS = 16
LOOPBACK_ADDRESSES = {"127.0.0.1", "::1"}
HEADER_NAME_RE = re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")
DASHBOARD_ROOT = Path(__file__).resolve().parent
DASHBOARD_RESOURCES = {
    "/admin/analytics/": (
        DASHBOARD_ROOT / "templates" / "dashboard.html",
        "text/html; charset=utf-8",
    ),
    "/admin/analytics/assets/dashboard.css": (
        DASHBOARD_ROOT / "static" / "dashboard.css",
        "text/css; charset=utf-8",
    ),
    "/admin/analytics/assets/dashboard.js": (
        DASHBOARD_ROOT / "static" / "dashboard.js",
        "text/javascript; charset=utf-8",
    ),
    "/admin/analytics/assets/dashboard-mark.png": (
        DASHBOARD_ROOT.parent / "assets" / "favicons" / "favicon-64x64.png",
        "image/png",
    ),
}

ALLOWED_SECTIONS = {
    "home", "compass", "enrollment", "employment", "enlistment", "explorer",
    "coach", "evidence", "plan", "training",
}
ALLOWED_EVENTS = {
    "section_view",
    "career_assessment_start",
    "career_assessment_complete",
    "course_explorer_open",
    "plan_open",
    "plan_print",
    "plan_pdf_download",
    "evidence_open",
    "evidence_pdf_download",
    "ai_coach_open",
    "schoolai_launch",
    "voice_coach_launch",
    "counseling_link_open",
}

ADMIN_QUERY_FIELDS = {
    "/admin/analytics/api/health": frozenset(),
    "/admin/analytics/api/report": frozenset({"start", "end", "granularity"}),
    "/admin/analytics/api/pages": frozenset({"start", "end", "limit"}),
    "/admin/analytics/api/features": frozenset({"start", "end"}),
    "/admin/analytics/api/export": frozenset({"start", "end", "dataset"}),
}


class EventRateLimiter:
    def __init__(self, maximum: int = 120, window_seconds: int = 60) -> None:
        self.maximum = max(1, maximum)
        self.window_seconds = max(1, window_seconds)
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        cutoff = current - self.window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= self.maximum:
                return False
            events.append(current)
            if len(self._events) > 10000:
                for candidate, values in list(self._events.items())[:2000]:
                    while values and values[0] <= cutoff:
                        values.popleft()
                    if not values:
                        self._events.pop(candidate, None)
            return True


def _header_environ_name(header_name: str) -> str:
    return "HTTP_" + header_name.upper().replace("-", "_")


class AnalyticsApplication:
    def __init__(
        self,
        config: AnalyticsConfig,
        allowed_origins: Iterable[str] | None = None,
        admin_header: str = "X-LionsPath-Admin",
        admin_header_value: str = "1",
        rate_limit: int = 120,
        now_provider: Callable[[], datetime] | None = None,
        proxy_header: str = "X-LionsPath-Proxy",
        proxy_header_value: str = "1",
    ) -> None:
        self.config = config
        self.allowed_origins = self._validated_origins(
            allowed_origins or {"https://lionspath.lcps.k12.va.us"}
        )
        self._validate_header_configuration(admin_header, admin_header_value)
        self._validate_header_configuration(proxy_header, proxy_header_value)
        if admin_header.lower() == proxy_header.lower():
            raise ValueError("Administrator and proxy marker headers must differ")
        self.admin_header_key = _header_environ_name(admin_header)
        self.admin_header_value = admin_header_value
        self.proxy_header_key = _header_environ_name(proxy_header)
        self.proxy_header_value = proxy_header_value
        self.rate_limiter = EventRateLimiter(rate_limit)
        self.now_provider = now_provider or (lambda: datetime.now(timezone.utc))
        with closing(connect_database(self.config.database_path)) as connection:
            initialize_database(connection)

    def __call__(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/"))
        try:
            if not self._is_proxy(environ):
                return self._json(
                    start_response,
                    403,
                    {"error": "Trusted proxy required"},
                )
            if path == "/api/analytics/event":
                if method == "OPTIONS":
                    return self._response(start_response, 204, b"", extra_headers=[("Allow", "POST, OPTIONS")])
                if method != "POST":
                    return self._json(start_response, 405, {"error": "Method not allowed"}, [("Allow", "POST, OPTIONS")])
                return self._record_event(environ, start_response)

            if path.startswith("/admin/analytics/api/"):
                if not self._is_admin(environ):
                    return self._json(start_response, 403, {"error": "Administrator access required"})
                if method != "GET":
                    return self._json(start_response, 405, {"error": "Method not allowed"}, [("Allow", "GET")])
                return self._admin_api(path, environ, start_response)

            if path == "/admin/analytics" or path in DASHBOARD_RESOURCES:
                if not self._is_admin(environ):
                    return self._json(start_response, 403, {"error": "Administrator access required"})
                if method != "GET":
                    return self._json(start_response, 405, {"error": "Method not allowed"}, [("Allow", "GET")])
                if path == "/admin/analytics":
                    return self._response(
                        start_response,
                        308,
                        b"",
                        extra_headers=[("Location", "/admin/analytics/")],
                    )
                return self._dashboard_resource(path, start_response)

            return self._json(start_response, 404, {"error": "Not found"})
        except ValueError as exc:
            return self._json(start_response, 400, {"error": str(exc)})
        except (OSError, sqlite3.Error) as exc:
            LOGGER.exception("Analytics storage error")
            return self._json(start_response, 503, {"error": "Analytics data is temporarily unavailable"})
        except Exception:
            LOGGER.exception("Unhandled analytics API error")
            return self._json(start_response, 500, {"error": "Analytics request failed"})

    @staticmethod
    def _validate_header_configuration(name: str, value: str) -> None:
        if not HEADER_NAME_RE.fullmatch(name):
            raise ValueError("Analytics trust marker header name is invalid")
        if not value or any(character in value for character in "\r\n"):
            raise ValueError("Analytics trust marker value is invalid")

    @staticmethod
    def _validated_origins(origins: Iterable[str]) -> set[str]:
        validated: set[str] = set()
        for raw_origin in origins:
            origin = str(raw_origin).strip().rstrip("/")
            parsed = urlsplit(origin)
            loopback_http = parsed.scheme == "http" and parsed.hostname in LOOPBACK_ADDRESSES | {"localhost"}
            if (
                parsed.scheme not in {"https", "http"}
                or (parsed.scheme != "https" and not loopback_http)
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.query
                or parsed.fragment
                or parsed.path not in {"", "/"}
            ):
                raise ValueError("Analytics allowed origin must be an HTTPS origin")
            validated.add(origin)
        if not validated:
            raise ValueError("At least one analytics origin is required")
        return validated

    def _is_proxy(self, environ: dict[str, Any]) -> bool:
        return str(environ.get(self.proxy_header_key, "")) == self.proxy_header_value

    def _is_admin(self, environ: dict[str, Any]) -> bool:
        return self._is_proxy(environ) and (
            str(environ.get(self.admin_header_key, "")) == self.admin_header_value
        )

    def _dashboard_resource(
        self,
        path: str,
        start_response: Callable[..., Any],
    ) -> list[bytes]:
        resource_path, content_type = DASHBOARD_RESOURCES[path]
        headers = [
            ("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; object-src 'none'"),
            ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
            ("X-Frame-Options", "DENY"),
        ]
        return self._response(
            start_response,
            200,
            resource_path.read_bytes(),
            content_type,
            headers,
        )

    def _query_parameters(
        self,
        environ: dict[str, Any],
        allowed_fields: frozenset[str],
    ) -> dict[str, str]:
        query = str(environ.get("QUERY_STRING", ""))
        if len(query.encode("utf-8", "replace")) > MAX_QUERY_STRING_BYTES:
            raise ValueError("Analytics query is too long")
        try:
            parsed = parse_qs(
                query,
                keep_blank_values=True,
                max_num_fields=MAX_QUERY_FIELDS,
            )
        except ValueError as exc:
            raise ValueError("Analytics query has too many fields") from exc
        unsupported = set(parsed) - allowed_fields
        if unsupported:
            raise ValueError("Analytics query contains unsupported fields")
        if any(len(values) != 1 for values in parsed.values()):
            raise ValueError("Analytics query contains repeated fields")
        if any(values[0] == "" for values in parsed.values()):
            raise ValueError("Analytics query contains blank fields")
        return {key: values[0] for key, values in parsed.items()}

    def _period(self, connection: sqlite3.Connection, params: dict[str, str]) -> DateRange:
        return resolve_date_range(
            connection,
            params.get("start"),
            params.get("end"),
            self.config.timezone_name,
        )

    def _admin_api(
        self,
        path: str,
        environ: dict[str, Any],
        start_response: Callable[..., Any],
    ) -> list[bytes]:
        allowed_fields = ADMIN_QUERY_FIELDS.get(path)
        if allowed_fields is None:
            return self._json(start_response, 404, {"error": "Analytics API route not found"})
        params = self._query_parameters(environ, allowed_fields)
        with closing(connect_database(self.config.database_path)) as connection:
            initialize_database(connection)
            if path == "/admin/analytics/api/health":
                row = connection.execute(
                    "SELECT COUNT(*), MIN(local_date), MAX(local_date) FROM requests"
                ).fetchone()
                return self._json(
                    start_response,
                    200,
                    {
                        "status": "ok",
                        "request_rows": int(row[0]),
                        "oldest_date": row[1],
                        "newest_date": row[2],
                    },
                )

            period = self._period(connection, params)
            if path == "/admin/analytics/api/report":
                payload = build_report(
                    connection,
                    self.config.database_path,
                    period,
                    params.get("granularity"),
                )
                return self._json(start_response, 200, payload)
            if path == "/admin/analytics/api/pages":
                try:
                    limit = int(params.get("limit", "15"))
                except ValueError as exc:
                    raise ValueError("Page limit must be a number") from exc
                if limit < 1 or limit > 100:
                    raise ValueError("Page limit must be between 1 and 100")
                return self._json(start_response, 200, {"period": period.__dict__, "pages": top_pages(connection, period, limit)})
            if path == "/admin/analytics/api/features":
                return self._json(start_response, 200, {"period": period.__dict__, **event_usage(connection, period)})
            if path == "/admin/analytics/api/export":
                return self._csv_export(connection, period, params.get("dataset", "daily"), start_response)
        return self._json(start_response, 404, {"error": "Analytics API route not found"})

    def _csv_export(
        self,
        connection: sqlite3.Connection,
        period: DateRange,
        dataset: str,
        start_response: Callable[..., Any],
    ) -> list[bytes]:
        if dataset == "daily":
            rows = [dict(row) for row in connection.execute(
                """
                SELECT local_date, total_requests, human_pageviews, bot_requests,
                       asset_requests, estimated_daily_visitors
                FROM analytics_daily
                WHERE local_date BETWEEN ? AND ? ORDER BY local_date
                """,
                (period.start, period.end),
            ).fetchall()]
        elif dataset == "pages":
            rows = top_pages(connection, period, 100)
        elif dataset == "features":
            rows = event_usage(connection, period)["features"]
        elif dataset == "devices":
            rows = request_breakdown(connection, period, "device")
        elif dataset == "hourly":
            rows = time_patterns(connection, period)["hourly"]
        else:
            raise ValueError("Unsupported export dataset")

        safe_rows = [
            {key: self._csv_cell(value) for key, value in row.items()}
            for row in rows
        ]
        output = io.StringIO(newline="")
        if safe_rows:
            writer = csv.DictWriter(
                output,
                fieldnames=list(safe_rows[0].keys()),
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(safe_rows)
        else:
            output.write("no_data\n")
        filename = f"lionspath-{dataset}-{period.start}-to-{period.end}.csv"
        return self._response(
            start_response,
            200,
            output.getvalue().encode("utf-8"),
            content_type="text/csv; charset=utf-8",
            extra_headers=[("Content-Disposition", f'attachment; filename="{filename}"')],
        )

    @staticmethod
    def _csv_cell(value: Any) -> Any:
        if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
            return "'" + value
        return value

    def _client_ip(self, environ: dict[str, Any]) -> str:
        forwarded = str(environ.get("HTTP_X_FORWARDED_FOR", ""))
        candidate = forwarded.split(",", 1)[0].strip()
        if not self._is_proxy(environ) or not candidate or len(candidate) > 64:
            raise ValueError("Trusted client address is unavailable")
        try:
            return ipaddress.ip_address(candidate).compressed
        except ValueError as exc:
            raise ValueError("Trusted client address is invalid") from exc

    def _record_event(
        self,
        environ: dict[str, Any],
        start_response: Callable[..., Any],
    ) -> list[bytes]:
        origin = str(environ.get("HTTP_ORIGIN", "")).rstrip("/")
        if origin not in self.allowed_origins:
            return self._json(start_response, 403, {"error": "Event origin is not allowed"})
        content_type = str(environ.get("CONTENT_TYPE", "")).split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            return self._json(start_response, 415, {"error": "Content-Type must be application/json"})
        try:
            content_length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            return self._json(start_response, 400, {"error": "Invalid request size"})
        if content_length <= 0 or content_length > MAX_EVENT_BODY_BYTES:
            return self._json(start_response, 413, {"error": "Event request is empty or too large"})
        raw_body = environ["wsgi.input"].read(content_length)
        if len(raw_body) != content_length:
            return self._json(start_response, 400, {"error": "Event request body is incomplete"})
        try:
            payload = json.loads(
                raw_body.decode("utf-8"),
                object_pairs_hook=self._unique_json_object,
            )
        except (UnicodeError, json.JSONDecodeError):
            return self._json(start_response, 400, {"error": "Invalid JSON"})
        if not isinstance(payload, dict):
            return self._json(start_response, 422, {"error": "Event payload must be an object"})
        if set(payload) - {"event", "section", "source_page"}:
            return self._json(start_response, 422, {"error": "Event payload contains unsupported fields"})
        if any(value is not None and not isinstance(value, str) for value in payload.values()):
            return self._json(start_response, 422, {"error": "Event fields must be strings"})

        event_name = payload.get("event")
        section = payload.get("section")
        source_page = payload.get("source_page")
        if event_name not in ALLOWED_EVENTS:
            return self._json(start_response, 422, {"error": "Unknown analytics event"})
        if section is not None and section not in ALLOWED_SECTIONS:
            return self._json(start_response, 422, {"error": "Unknown LionPath section"})
        if source_page is not None and source_page not in ALLOWED_SECTIONS:
            return self._json(start_response, 422, {"error": "Unknown source page"})
        if event_name == "section_view" and section is None:
            return self._json(start_response, 422, {"error": "section_view requires a section"})

        now_utc = self.now_provider().astimezone(timezone.utc)
        local_time = now_utc.astimezone(ZoneInfo(self.config.timezone_name))
        ip_address = self._client_ip(environ)
        user_agent = str(environ.get("HTTP_USER_AGENT", ""))[:1024]
        day_hash = daily_visitor_hash(self.config.secret, local_time.date(), ip_address, user_agent)
        month_hash = monthly_visitor_hash(self.config.secret, local_time.date(), ip_address, user_agent)
        if not self.rate_limiter.allow(day_hash):
            return self._json(start_response, 429, {"error": "Event rate limit exceeded"}, [("Retry-After", "60")])

        with closing(connect_database(self.config.database_path)) as connection:
            initialize_database(connection)
            connection.execute(
                """
                INSERT INTO events (
                    occurred_at_utc, timestamp_local, local_date, local_hour,
                    visitor_day_hash, visitor_month_hash, event_name, section,
                    source_page
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    int(now_utc.timestamp()),
                    local_time.isoformat(),
                    local_time.date().isoformat(),
                    local_time.hour,
                    day_hash,
                    month_hash,
                    event_name,
                    section,
                    source_page,
                ),
            )
            connection.commit()
        return self._response(start_response, 204, b"")

    @staticmethod
    def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Event payload contains repeated fields")
            result[key] = value
        return result

    def _json(
        self,
        start_response: Callable[..., Any],
        status: int,
        payload: dict[str, Any],
        extra_headers: list[tuple[str, str]] | None = None,
    ) -> list[bytes]:
        body = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
        return self._response(start_response, status, body, "application/json; charset=utf-8", extra_headers)

    def _response(
        self,
        start_response: Callable[..., Any],
        status: int,
        body: bytes,
        content_type: str = "application/octet-stream",
        extra_headers: list[tuple[str, str]] | None = None,
    ) -> list[bytes]:
        phrase = HTTPStatus(status).phrase
        headers = [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("Pragma", "no-cache"),
            ("X-Content-Type-Options", "nosniff"),
            ("Referrer-Policy", "no-referrer"),
            ("X-Robots-Tag", "noindex, nofollow, noarchive"),
            ("Cross-Origin-Resource-Policy", "same-origin"),
        ]
        if extra_headers:
            headers.extend(extra_headers)
        start_response(f"{status} {phrase}", headers)
        return [body]


def create_application(
    config: AnalyticsConfig,
    allowed_origins: Iterable[str] | None = None,
    admin_header: str = "X-LionsPath-Admin",
    admin_header_value: str = "1",
    rate_limit: int = 120,
    now_provider: Callable[[], datetime] | None = None,
    proxy_header: str = "X-LionsPath-Proxy",
    proxy_header_value: str = "1",
) -> AnalyticsApplication:
    return AnalyticsApplication(
        config,
        allowed_origins,
        admin_header,
        admin_header_value,
        rate_limit,
        now_provider,
        proxy_header,
        proxy_header_value,
    )


_application: AnalyticsApplication | None = None


def application(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
    """Lazy WSGI entry point used by Gunicorn after deployment."""

    global _application
    if _application is None:
        config = load_config()
        origins = {
            value.strip().rstrip("/")
            for value in os.environ.get(
                "LIONPATH_ANALYTICS_ALLOWED_ORIGINS",
                "https://lionspath.lcps.k12.va.us",
            ).split(",")
            if value.strip()
        }
        _application = create_application(
            config,
            origins,
            os.environ.get("LIONPATH_ANALYTICS_ADMIN_HEADER", "X-LionsPath-Admin"),
            os.environ.get("LIONPATH_ANALYTICS_ADMIN_HEADER_VALUE", "1"),
            proxy_header=os.environ.get(
                "LIONPATH_ANALYTICS_PROXY_HEADER", "X-LionsPath-Proxy"
            ),
            proxy_header_value=os.environ.get(
                "LIONPATH_ANALYTICS_PROXY_HEADER_VALUE", "1"
            ),
        )
    return _application(environ, start_response)
