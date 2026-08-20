from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from analytics.app import MAX_QUERY_STRING_BYTES, create_application
from analytics.config import AnalyticsConfig, load_secret
from analytics.database import connect_database
from analytics.import_logs import LogImporter
from analytics.rollups import refresh_rollups
from analytics.tests.test_phase4 import ORIGIN, log_line, wsgi_request


SECRET = b"lionspath-phase-seven-test-secret-32-bytes-minimum"
FILE_SECRET = b"lionspath-file-only-secret-is-at-least-32-bytes"
ADMIN_HEADERS = {
    "X-LionsPath-Admin": "1",
}
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class PhaseSevenApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.database = self.root / "analytics.db"
        self.log_path = self.root / "lionspath_ssl_access.log"
        self.log_path.write_text(
            log_line(
                "192.0.2.70",
                "14/Aug/2026:14:00:00 +0000",
                "GET /=2+3 HTTP/1.1",
            )
            + "\n",
            encoding="utf-8",
        )
        LogImporter(self.database, SECRET).import_paths([self.log_path])
        with closing(connect_database(self.database)) as connection:
            refresh_rollups(connection)
        self.config = AnalyticsConfig(
            database_path=self.database,
            log_pattern=str(self.log_path),
            secret=SECRET,
        )
        self.application = create_application(self.config, {ORIGIN})

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_admin_and_event_routes_require_the_trusted_proxy_marker(self) -> None:
        spoofed_admin = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/health",
            headers=ADMIN_HEADERS,
            proxy=False,
        )
        missing_admin = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/health",
        )
        authenticated = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/health",
            headers=ADMIN_HEADERS,
        )
        direct_event = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            payload={"event": "plan_open"},
            headers={"Origin": ORIGIN},
            proxy=False,
        )

        self.assertEqual(spoofed_admin[0], 403)
        self.assertEqual(missing_admin[0], 403)
        self.assertEqual(authenticated[0], 200)
        self.assertEqual(direct_event[0], 403)

    def test_forwarded_address_must_be_a_valid_ip_from_the_proxy(self) -> None:
        invalid = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            payload={"event": "plan_open"},
            headers={"Origin": ORIGIN, "X-Forwarded-For": "not-an-ip"},
        )
        valid_ipv6 = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            payload={"event": "plan_open"},
            headers={"Origin": ORIGIN, "X-Forwarded-For": "2001:db8::25"},
        )

        self.assertEqual(invalid[0], 400)
        self.assertEqual(valid_ipv6[0], 204)

    def test_admin_queries_reject_ambiguity_unknown_fields_and_excess(self) -> None:
        repeated = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/report",
            query="start=2026-08-14&start=2026-08-13&end=2026-08-14",
            headers=ADMIN_HEADERS,
        )
        unknown = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/report",
            query="student=private",
            headers=ADMIN_HEADERS,
        )
        too_long = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/report",
            query="start=" + ("2" * MAX_QUERY_STRING_BYTES),
            headers=ADMIN_HEADERS,
        )
        excessive_limit = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/pages",
            query="limit=101",
            headers=ADMIN_HEADERS,
        )
        blank = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/report",
            query="start=",
            headers=ADMIN_HEADERS,
        )

        self.assertEqual(repeated[0], 400)
        self.assertEqual(unknown[0], 400)
        self.assertEqual(too_long[0], 400)
        self.assertEqual(excessive_limit[0], 400)
        self.assertEqual(blank[0], 400)

    def test_event_payload_rejects_duplicate_non_string_and_incomplete_fields(self) -> None:
        duplicate = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            raw_body=b'{"event":"plan_open","event":"plan_print"}',
            headers={"Origin": ORIGIN},
        )
        non_string = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            payload={"event": ["plan_open"]},
            headers={"Origin": ORIGIN},
        )
        incomplete = wsgi_request(
            self.application,
            "POST",
            "/api/analytics/event",
            raw_body=b'{"event":"plan_open"}',
            headers={"Origin": ORIGIN, "Content-Length": "200"},
        )

        self.assertEqual(duplicate[0], 400)
        self.assertEqual(non_string[0], 422)
        self.assertEqual(incomplete[0], 400)

    def test_csv_exports_neutralize_spreadsheet_formulas(self) -> None:
        response = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/export",
            query="dataset=pages&start=2026-08-14&end=2026-08-14",
            headers=ADMIN_HEADERS,
        )
        exported = response[2].decode("utf-8")

        self.assertEqual(response[0], 200)
        self.assertIn("'=2+3", exported)
        self.assertNotIn(",=2+3,", exported)

    def test_security_headers_apply_to_api_responses(self) -> None:
        response = wsgi_request(
            self.application,
            "GET",
            "/admin/analytics/api/health",
            headers=ADMIN_HEADERS,
        )

        self.assertEqual(response[1]["Cache-Control"], "no-store")
        self.assertEqual(response[1]["X-Robots-Tag"], "noindex, nofollow, noarchive")
        self.assertEqual(response[1]["Cross-Origin-Resource-Policy"], "same-origin")

    def test_configuration_rejects_unsafe_origins_and_marker_names(self) -> None:
        with self.assertRaises(ValueError):
            create_application(self.config, {"http://example.test"})
        with self.assertRaises(ValueError):
            create_application(self.config, {ORIGIN}, admin_header="Bad Header")
        localhost = create_application(self.config, {"http://127.0.0.1:8765"})
        self.assertIn("http://127.0.0.1:8765", localhost.allowed_origins)

    def test_secret_is_loaded_only_from_a_restricted_file_path(self) -> None:
        secret_file = self.root / "analytics.secret"
        secret_file.write_bytes(FILE_SECRET)
        secret_file.chmod(0o600)
        with patch.dict(
            os.environ,
            {"LIONPATH_ANALYTICS_SECRET": "environment-secrets-are-not-accepted"},
        ):
            self.assertEqual(load_secret(secret_file), FILE_SECRET)
            with self.assertRaises(RuntimeError):
                load_secret(self.root / "missing.secret")


class PhaseSevenDeploymentTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")

    def test_apache_removes_spoofable_and_credential_headers(self) -> None:
        apache = self.read("deployment/apache/lionspath.conf")
        self.assertIn("ProxyAddHeaders On", apache)
        self.assertIn("AuthBasicAuthoritative On", apache)
        self.assertIn("RequestHeader unset Authorization", apache)
        self.assertIn("RequestHeader unset X-Forwarded-For", apache)
        self.assertIn("RequestHeader unset X-LionsPath-Proxy", apache)
        self.assertIn("RequestHeader unset X-LionsPath-Admin", apache)
        self.assertIn('Header always set Cache-Control "no-store"', apache)
        self.assertIn('Header always set X-Robots-Tag "noindex, nofollow, noarchive"', apache)

    def test_services_have_no_network_and_private_runtime_files(self) -> None:
        service = self.read("deployment/systemd/lionspath-analytics.service")
        importer = self.read("deployment/systemd/lionspath-analytics-import.service")
        environment = self.read("deployment/analytics/analytics.env.example")

        for unit in (service, importer):
            self.assertIn("PrivateNetwork=true", unit)
            self.assertIn("NoNewPrivileges=true", unit)
            self.assertIn("ProtectSystem=strict", unit)
            self.assertIn("UMask=0077", unit)
            self.assertIn("SystemCallArchitectures=native", unit)
            self.assertIn("CapabilityBoundingSet=", unit)
        self.assertIn("StateDirectoryMode=0700", service)
        self.assertNotIn("LIONPATH_ANALYTICS_SECRET=", environment)
        self.assertIn("LIONPATH_ANALYTICS_SECRET_FILE=", environment)


if __name__ == "__main__":
    unittest.main()
