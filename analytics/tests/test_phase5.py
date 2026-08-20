from __future__ import annotations

import io
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from analytics.app import create_application
from analytics.config import AnalyticsConfig


SECRET = b"lionspath-phase-five-test-secret-32-bytes-minimum"
ADMIN_HEADER = {
    "X-LionsPath-Proxy": "1",
    "X-LionsPath-Admin": "1",
}


def wsgi_get(
    application: Any,
    path: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    environ: dict[str, Any] = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": "",
        "CONTENT_LENGTH": "0",
        "REMOTE_ADDR": "127.0.0.1",
        "wsgi.input": io.BytesIO(b""),
        "wsgi.url_scheme": "https",
        "SERVER_NAME": "lionspath.lcps.k12.va.us",
        "SERVER_PORT": "443",
    }
    for name, value in (headers or {}).items():
        environ[f"HTTP_{name.upper().replace('-', '_')}"] = value
    captured: dict[str, Any] = {}

    def start_response(status: str, response_headers: list[tuple[str, str]]) -> None:
        captured["status"] = status
        captured["headers"] = response_headers

    body = b"".join(application(environ, start_response))
    return (
        int(str(captured["status"]).split(" ", 1)[0]),
        {key: value for key, value in captured["headers"]},
        body,
    )


class DashboardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.external_urls: list[str] = []
        self.iframes = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag == "iframe":
            self.iframes += 1
        for attribute in ("src", "href"):
            value = values.get(attribute)
            if value and str(value).startswith(("http://", "https://", "//")):
                self.external_urls.append(str(value))


class PhaseFiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "analytics.db"
        self.application = create_application(
            AnalyticsConfig(
                database_path=self.database,
                log_pattern=str(Path(self.temp.name) / "access.log*"),
                secret=SECRET,
            )
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_dashboard_and_every_asset_require_admin_marker(self) -> None:
        paths = [
            "/admin/analytics/",
            "/admin/analytics/assets/dashboard.css",
            "/admin/analytics/assets/dashboard.js",
            "/admin/analytics/assets/dashboard-mark.png",
        ]
        for path in paths:
            with self.subTest(path=path):
                denied = wsgi_get(self.application, path)
                allowed = wsgi_get(self.application, path, headers=ADMIN_HEADER)
                self.assertEqual(denied[0], 403)
                self.assertEqual(allowed[0], 200)

    def test_dashboard_redirect_and_method_rules_are_explicit(self) -> None:
        redirect = wsgi_get(
            self.application,
            "/admin/analytics",
            headers=ADMIN_HEADER,
        )
        post = wsgi_get(
            self.application,
            "/admin/analytics/",
            method="POST",
            headers=ADMIN_HEADER,
        )
        self.assertEqual(redirect[0], 308)
        self.assertEqual(redirect[1]["Location"], "/admin/analytics/")
        self.assertEqual(post[0], 405)
        self.assertEqual(post[1]["Allow"], "GET")

    def test_dashboard_is_self_contained_and_has_required_workspaces(self) -> None:
        response = wsgi_get(
            self.application,
            "/admin/analytics/",
            headers=ADMIN_HEADER,
        )
        html = response[2].decode("utf-8")
        parser = DashboardParser()
        parser.feed(html)
        required_ids = {
            "custom-range-form",
            "metric-visitors",
            "trend-chart",
            "pages-table",
            "pathway-grid",
            "features-table",
            "breakdown-list",
            "hour-chart",
            "weekday-list",
            "activity-heatmap",
            "errors-table",
            "download-export",
        }
        self.assertEqual(response[0], 200)
        self.assertEqual(response[1]["Content-Type"], "text/html; charset=utf-8")
        self.assertTrue(required_ids.issubset(parser.ids))
        self.assertEqual(parser.external_urls, [])
        self.assertEqual(parser.iframes, 0)
        self.assertIn('content="noindex, nofollow, noarchive"', html)

    def test_dashboard_security_headers_block_embedding_and_external_assets(self) -> None:
        response = wsgi_get(
            self.application,
            "/admin/analytics/",
            headers=ADMIN_HEADER,
        )
        policy = response[1]["Content-Security-Policy"]
        self.assertIn("default-src 'self'", policy)
        self.assertIn("connect-src 'self'", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        self.assertEqual(response[1]["X-Frame-Options"], "DENY")
        self.assertIn("camera=()", response[1]["Permissions-Policy"])
        self.assertEqual(response[1]["Cache-Control"], "no-store")

    def test_local_assets_include_responsive_layout_and_api_wiring(self) -> None:
        css_response = wsgi_get(
            self.application,
            "/admin/analytics/assets/dashboard.css",
            headers=ADMIN_HEADER,
        )
        js_response = wsgi_get(
            self.application,
            "/admin/analytics/assets/dashboard.js",
            headers=ADMIN_HEADER,
        )
        css = css_response[2].decode("utf-8")
        javascript = js_response[2].decode("utf-8")
        self.assertIn("@media (max-width: 680px)", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn('const API_ROOT = "/admin/analytics/api"', javascript)
        self.assertIn("/report?", javascript)
        self.assertIn("/export", javascript)
        self.assertNotIn("innerHTML", javascript)
        self.assertNotIn("https://", javascript)


if __name__ == "__main__":
    unittest.main()
