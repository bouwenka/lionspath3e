from __future__ import annotations

import io
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from analytics.app import MAX_EVENT_BODY_BYTES, create_application
from analytics.config import AnalyticsConfig
from analytics.database import connect_database, initialize_database
from analytics.import_logs import LogImporter
from analytics.rollups import refresh_rollups


SECRET = b"lionspath-phase-four-test-secret-32-bytes-minimum"
ORIGIN = "https://lionspath.lcps.k12.va.us"
CHROME = (
    "Mozilla/5.0 (X11; CrOS x86_64 15917.71.0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def log_line(
    ip: str,
    timestamp: str,
    request: str = "GET / HTTP/1.1",
    status: int = 200,
    user_agent: str = CHROME,
) -> str:
    return (
        f'{ip} - - [{timestamp}] "{request}" {status} 1000 '
        f'"-" "{user_agent}"'
    )


def wsgi_request(
    application: Any,
    method: str,
    path: str,
    *,
    query: str = "",
    payload: Any | None = None,
    raw_body: bytes | None = None,
    headers: dict[str, str] | None = None,
    remote_addr: str = "192.0.2.50",
    proxy: bool = True,
) -> tuple[int, dict[str, str], bytes]:
    if raw_body is None:
        raw_body = b"" if payload is None else json.dumps(payload).encode("utf-8")
    environ: dict[str, Any] = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(raw_body)),
        "REMOTE_ADDR": remote_addr,
        "HTTP_USER_AGENT": CHROME,
        "wsgi.input": io.BytesIO(raw_body),
        "wsgi.url_scheme": "https",
        "SERVER_NAME": "lionspath.lcps.k12.va.us",
        "SERVER_PORT": "443",
    }
    if proxy:
        environ["HTTP_X_LIONSPATH_PROXY"] = "1"
        environ["HTTP_X_FORWARDED_FOR"] = remote_addr
    for name, value in (headers or {}).items():
        key = name.upper().replace("-", "_")
        if key == "CONTENT_TYPE":
            environ["CONTENT_TYPE"] = value
        elif key == "CONTENT_LENGTH":
            environ["CONTENT_LENGTH"] = value
        else:
            environ[f"HTTP_{key}"] = value

    captured: dict[str, Any] = {}

    def start_response(status: str, response_headers: list[tuple[str, str]]) -> None:
        captured["status"] = status
        captured["headers"] = response_headers

    body = b"".join(application(environ, start_response))
    response_headers = {key: value for key, value in captured["headers"]}
    return int(str(captured["status"]).split(" ", 1)[0]), response_headers, body


class PhaseFourTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.database = self.root / "analytics.db"
        self.log_path = self.root / "lionspath_ssl_access.log"
        self.log_path.write_text(
            "\n".join(
                [
                    log_line("192.0.2.10", "14/Aug/2026:14:00:00 +0000"),
                    log_line(
                        "192.0.2.10",
                        "14/Aug/2026:14:10:00 +0000",
                        "GET /employment/ HTTP/1.1",
                    ),
                    log_line(
                        "192.0.2.11",
                        "14/Aug/2026:14:05:00 +0000",
                        "GET /enrollment/?utm_source=qr HTTP/1.1",
                    ),
                    log_line(
                        "192.0.2.12",
                        "14/Aug/2026:14:20:00 +0000",
                        "GET /missing HTTP/1.1",
                        status=404,
                    ),
                    log_line(
                        "192.0.2.13",
                        "14/Aug/2026:14:30:00 +0000",
                        user_agent="Googlebot/2.1",
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        LogImporter(self.database, SECRET).import_paths([self.log_path])
        with closing(connect_database(self.database)) as connection:
            initialize_database(connection)
            refresh_rollups(connection)

        self.config = AnalyticsConfig(
            database_path=self.database,
            log_pattern=str(self.log_path),
            secret=SECRET,
        )
        self.now = datetime(2026, 8, 14, 16, 0, tzinfo=timezone.utc)
        self.application = create_application(
            self.config,
            {ORIGIN},
            rate_limit=20,
            now_provider=lambda: self.now,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def post_event(
        self,
        payload: dict[str, str],
        *,
        headers: dict[str, str] | None = None,
        remote_addr: str = "192.0.2.50",
    ) -> tuple[int, dict[str, str], bytes]:
        request_headers = {"Origin": ORIGIN, **(headers or {})}
        return wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            payload=payload,
            headers=request_headers,
            remote_addr=remote_addr,
        )

    def test_allowlisted_event_is_stored_without_raw_identifiers(self) -> None:
        status, headers, body = self.post_event(
            {"event": "section_view", "section": "enrollment", "source_page": "home"}
        )
        self.assertEqual(status, 204)
        self.assertEqual(body, b"")
        self.assertEqual(headers["Cache-Control"], "no-store")

        with closing(connect_database(self.database)) as connection:
            row = connection.execute("SELECT * FROM events").fetchone()
            columns = {
                item[1]
                for item in connection.execute("PRAGMA table_info(events)").fetchall()
            }
        self.assertEqual(row["event_name"], "section_view")
        self.assertEqual(row["section"], "enrollment")
        self.assertEqual(row["source_page"], "home")
        self.assertEqual(len(row["visitor_day_hash"]), 64)
        self.assertNotIn("ip", columns)
        self.assertNotIn("user_agent", columns)
        self.assertNotIn("192.0.2.50", tuple(row))
        self.assertNotIn(CHROME, tuple(row))

    def test_event_endpoint_rejects_untrusted_or_unstructured_input(self) -> None:
        missing_origin = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            payload={"event": "plan_open"},
        )
        wrong_origin = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            payload={"event": "plan_open"},
            headers={"Origin": "https://example.test"},
        )
        extra_field = self.post_event({"event": "plan_open", "student_answer": "private text"})
        unknown_event = self.post_event({"event": "made_up_event"})
        missing_section = self.post_event({"event": "section_view"})

        self.assertEqual(missing_origin[0], 403)
        self.assertEqual(wrong_origin[0], 403)
        self.assertEqual(extra_field[0], 422)
        self.assertEqual(unknown_event[0], 422)
        self.assertEqual(missing_section[0], 422)

    def test_event_endpoint_enforces_content_type_size_and_rate_limit(self) -> None:
        wrong_type = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            raw_body=b'{"event":"plan_open"}',
            headers={"Origin": ORIGIN, "Content-Type": "text/plain"},
        )
        oversized = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            raw_body=b"x" * (MAX_EVENT_BODY_BYTES + 1),
            headers={"Origin": ORIGIN},
        )
        limited_application = create_application(
            self.config,
            {ORIGIN},
            rate_limit=2,
            now_provider=lambda: self.now,
        )
        rate_statuses = [
            wsgi_request(
                limited_application,
                "POST",
                "/api/analytics/event",
                payload={"event": "plan_open"},
                headers={"Origin": ORIGIN},
            )[0]
            for _ in range(3)
        ]

        self.assertEqual(wrong_type[0], 415)
        self.assertEqual(oversized[0], 413)
        self.assertEqual(rate_statuses, [204, 204, 429])

    def test_forwarded_ip_comes_only_from_the_trusted_proxy(self) -> None:
        direct = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            payload={"event": "plan_open"},
            headers={"Origin": ORIGIN, "X-Forwarded-For": "198.51.100.9"},
            proxy=False,
        )
        self.post_event(
            {"event": "plan_print"},
            headers={"X-Forwarded-For": "198.51.100.11"},
        )
        self.post_event(
            {"event": "plan_pdf_download"},
            headers={"X-Forwarded-For": "198.51.100.12"},
        )
        with closing(connect_database(self.database)) as connection:
            rows = connection.execute(
                "SELECT event_name, visitor_day_hash FROM events ORDER BY id"
            ).fetchall()
        self.assertEqual(direct[0], 403)
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]["visitor_day_hash"], rows[1]["visitor_day_hash"])

    def test_admin_routes_require_proxy_authentication_marker(self) -> None:
        denied = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/health",
        )
        allowed = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/health",
            headers={"X-LionsPath-Admin": "1"},
        )
        write_attempt = wsgi_request(
            self.application,
            "POST",
            "/admin/analytics/api/report",
            headers={"X-LionsPath-Admin": "1"},
        )

        self.assertEqual(denied[0], 403)
        self.assertEqual(allowed[0], 200)
        self.assertEqual(json.loads(allowed[2])["request_rows"], 5)
        self.assertEqual(write_attempt[0], 405)

    def test_report_contains_summary_routes_features_and_health(self) -> None:
        self.post_event({"event": "section_view", "section": "enrollment"})
        self.post_event({"event": "section_view", "section": "employment"})
        self.post_event({"event": "career_assessment_start", "source_page": "home"})
        status, headers, body = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/report",
            query="start=2026-08-14&end=2026-08-14&granularity=hour",
            headers={"X-LionsPath-Admin": "1"},
        )
        report = json.loads(body)

        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(report["summary"]["period"]["days"], 1)
        self.assertEqual(report["summary"]["current"]["server_pageviews"], 3)
        self.assertEqual(report["summary"]["current"]["site_loads"], 3)
        self.assertEqual(report["summary"]["current"]["page_views"], 3)
        self.assertEqual(report["summary"]["current"]["section_views"], 2)
        self.assertEqual(sum(item["site_loads"] for item in report["trend"]["points"]), 3)
        self.assertEqual(report["event_coverage"]["selected_three_e_views"], 2)
        self.assertEqual(report["trend"]["granularity"], "hour")
        self.assertEqual(sum(item["views"] for item in report["three_e"]), 2)
        self.assertTrue(any(item["path"] == "/employment" for item in report["pages"]))
        self.assertTrue(any(item["event"] == "career_assessment_start" for item in report["features"]))
        self.assertTrue(any(item["label"] == "4xx" for item in report["technical_health"]["statuses"]))

        friday = next(item for item in report["time_patterns"]["weekday"] if item["label"] == "Friday")
        sunday = next(item for item in report["time_patterns"]["weekday"] if item["label"] == "Sunday")
        self.assertEqual(friday["views"], 3)
        self.assertEqual(friday["estimated_visitors"], 2)
        self.assertEqual(friday["calendar_days"], 1)
        self.assertEqual(sunday["views"], 0)

    def test_daily_trend_includes_zero_activity_dates(self) -> None:
        status, _headers, body = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/report",
            query="start=2026-08-14&end=2026-08-16&granularity=day",
            headers={"X-LionsPath-Admin": "1"},
        )
        points = json.loads(body)["trend"]["points"]

        self.assertEqual(status, 200)
        self.assertEqual([point["period"] for point in points], ["2026-08-14", "2026-08-15", "2026-08-16"])
        self.assertEqual([point["site_loads"] for point in points], [3, 0, 0])

    def test_report_rejects_invalid_dates_and_granularity(self) -> None:
        reversed_dates = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/report",
            query="start=2026-08-15&end=2026-08-14",
            headers={"X-LionsPath-Admin": "1"},
        )
        bad_granularity = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/report",
            query="start=2026-08-14&end=2026-08-14&granularity=minute",
            headers={"X-LionsPath-Admin": "1"},
        )
        self.assertEqual(reversed_dates[0], 400)
        self.assertEqual(bad_granularity[0], 400)

    def test_csv_export_contains_aggregates_but_no_identifiers(self) -> None:
        self.post_event({"event": "plan_open", "source_page": "home"})
        status, headers, body = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/export",
            query="dataset=features&start=2026-08-14&end=2026-08-14",
            headers={"X-LionsPath-Admin": "1"},
        )
        decoded = body.decode("utf-8")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=", headers["Content-Disposition"])
        self.assertIn("plan_open", decoded)
        self.assertNotIn("visitor_day_hash", decoded)
        self.assertNotIn("visitor_month_hash", decoded)
        self.assertNotIn("192.0.2", decoded)

    def test_unknown_routes_and_unsupported_exports_fail_closed(self) -> None:
        public_get = wsgi_request(
            self.application,
            "GET",
            "/api/analytics/event",
        )
        unknown = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/nope",
            headers={"X-LionsPath-Admin": "1"},
        )
        bad_export = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/export",
            query="dataset=identifiers",
            headers={"X-LionsPath-Admin": "1"},
        )
        self.assertEqual(public_get[0], 405)
        self.assertEqual(unknown[0], 404)
        self.assertEqual(bad_export[0], 400)


if __name__ == "__main__":
    unittest.main()
