from __future__ import annotations

import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from analytics.app import create_application
from analytics.config import AnalyticsConfig
from analytics.database import connect_database
from analytics.refresh import run_refresh


SECRET = b"lionspath-phase-six-test-secret-32-bytes-minimum"
CHROME = (
    "Mozilla/5.0 (X11; CrOS x86_64 15917.71.0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def log_line(ip: str, timestamp: str, path: str = "/") -> str:
    return (
        f'{ip} - - [{timestamp}] "GET {path} HTTP/1.1" 200 1000 '
        f'"-" "{CHROME}"'
    )


class ScheduledRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.database = self.root / "analytics.db"
        self.pattern = str(self.root / "lionspath_ssl_access.log*")
        self.config = AnalyticsConfig(
            database_path=self.database,
            log_pattern=self.pattern,
            secret=SECRET,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_log(self, name: str, lines: list[str]) -> None:
        (self.root / name).write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_refresh_imports_recent_logs_and_rebuilds_only_recent_dates(self) -> None:
        self.write_log(
            "lionspath_ssl_access.log.2",
            [log_line("192.0.2.1", "01/Aug/2026:14:00:00 +0000")],
        )
        self.write_log(
            "lionspath_ssl_access.log.1",
            [
                log_line("192.0.2.2", "13/Aug/2026:14:00:00 +0000"),
                log_line("192.0.2.3", "14/Aug/2026:14:00:00 +0000", "/enrollment"),
            ],
        )
        self.write_log(
            "lionspath_ssl_access.log",
            [log_line("192.0.2.4", "15/Aug/2026:14:00:00 +0000", "/employment")],
        )

        first = run_refresh(self.config)
        second = run_refresh(self.config)

        self.assertEqual(
            first.files_selected,
            ("lionspath_ssl_access.log.1", "lionspath_ssl_access.log"),
        )
        self.assertEqual(first.import_result.rows_inserted, 3)
        self.assertEqual(first.rollup_result.start_date, "2026-08-13")
        self.assertEqual(first.rollup_result.end_date, "2026-08-15")
        self.assertEqual(first.rollup_result.daily_rows, 3)
        self.assertEqual(second.import_result.rows_inserted, 0)

        with closing(connect_database(self.database)) as connection:
            request_dates = connection.execute(
                "SELECT local_date, COUNT(*) FROM requests GROUP BY local_date ORDER BY local_date"
            ).fetchall()
        self.assertEqual(
            [tuple(row) for row in request_dates],
            [("2026-08-13", 1), ("2026-08-14", 1), ("2026-08-15", 1)],
        )

    def test_refresh_rejects_invalid_window_and_missing_logs(self) -> None:
        with self.assertRaises(ValueError):
            run_refresh(self.config, rollup_days=0)
        with self.assertRaises(ValueError):
            run_refresh(self.config, rollup_days=32)
        with self.assertRaises(RuntimeError):
            run_refresh(self.config)

    def test_unix_socket_proxy_marker_enables_forwarded_client_address(self) -> None:
        application = create_application(self.config)
        with self.assertRaises(ValueError):
            application._client_ip(
                {"REMOTE_ADDR": "", "HTTP_X_FORWARDED_FOR": "198.51.100.8"}
            )
        proxied = application._client_ip(
            {
                "REMOTE_ADDR": "",
                "HTTP_X_FORWARDED_FOR": "198.51.100.8, 127.0.0.1",
                "HTTP_X_LIONSPATH_PROXY": "1",
            }
        )
        self.assertEqual(proxied, "198.51.100.8")


class DeploymentConfigurationTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")

    def test_apache_uses_authenticated_unix_socket_routes_and_strips_headers(self) -> None:
        apache = self.read("deployment/apache/lionspath.conf")
        self.assertIn('RequestHeader unset X-LionsPath-Admin', apache)
        self.assertIn('RequestHeader unset X-LionsPath-Proxy', apache)
        self.assertIn('RequestHeader unset X-Forwarded-For', apache)
        self.assertIn('<Location "/admin/analytics">', apache)
        self.assertIn('AuthUserFile /etc/lionspath/analytics.htpasswd', apache)
        self.assertIn('Require valid-user', apache)
        self.assertIn('RequestHeader set X-LionsPath-Admin "1"', apache)
        self.assertIn('<Location "/api/analytics/event">', apache)
        self.assertIn('<LimitExcept POST OPTIONS>', apache)
        self.assertIn('unix:/run/lionspath-analytics.sock|', apache)
        self.assertIn('ProxyRequests Off', apache)
        self.assertIn('^/(analytics|deployment|docs|tmp|', apache)
        self.assertNotIn('^/(admin|analytics|', apache)

    def test_systemd_units_use_non_root_identity_socket_activation_and_hardening(self) -> None:
        service = self.read("deployment/systemd/lionspath-analytics.service")
        socket = self.read("deployment/systemd/lionspath-analytics.socket")
        importer = self.read("deployment/systemd/lionspath-analytics-import.service")
        timer = self.read("deployment/systemd/lionspath-analytics-import.timer")

        self.assertIn("User=lionspath-analytics", service)
        self.assertIn("Group=lionspath-analytics", service)
        self.assertIn("--bind fd://3", service)
        self.assertNotIn("--bind 0.0.0.0", service)
        self.assertNotIn("--bind 127.0.0.1", service)
        self.assertIn("NoNewPrivileges=true", service)
        self.assertIn("ProtectSystem=strict", service)
        self.assertIn("RestrictAddressFamilies=AF_UNIX", service)
        self.assertIn("StateDirectory=lionspath", service)

        self.assertIn("ListenStream=/run/lionspath-analytics.sock", socket)
        self.assertIn("SocketUser=www-data", socket)
        self.assertIn("SocketGroup=www-data", socket)
        self.assertIn("SocketMode=0660", socket)

        self.assertIn("SupplementaryGroups=adm", importer)
        self.assertIn("python -m analytics.refresh --rollup-days 3", importer)
        self.assertIn("ReadOnlyPaths=/var/log/apache2", importer)
        self.assertIn("OnUnitActiveSec=5min", timer)
        self.assertIn("Persistent=true", timer)

    def test_environment_template_and_requirements_contain_no_secret(self) -> None:
        environment = self.read("deployment/analytics/analytics.env.example")
        requirements = self.read("analytics/requirements.txt")
        self.assertIn("LIONPATH_ANALYTICS_SECRET_FILE=/etc/lionspath/analytics.secret", environment)
        self.assertNotIn("LIONPATH_ANALYTICS_SECRET=", environment)
        self.assertIn("gunicorn==26.0.0", requirements)

    def test_preflight_is_read_only(self) -> None:
        preflight = self.read("deployment/analytics/preflight.sh")
        forbidden = [
            "apt install",
            "a2enmod",
            "systemctl enable",
            "systemctl start",
            "useradd",
            "htpasswd -c",
            "openssl rand",
            "cp deployment/",
        ]
        for command in forbidden:
            with self.subTest(command=command):
                self.assertNotIn(command, preflight)
        self.assertIn("No server changes were made", preflight)


if __name__ == "__main__":
    unittest.main()
