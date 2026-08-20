from __future__ import annotations

import gzip
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from analytics.backfill import run_backfill
from analytics.config import AnalyticsConfig
from analytics.database import connect_database, initialize_database
from analytics.import_logs import LogImporter
from analytics.rollups import refresh_rollups
from analytics.validate import scan_log_file, validate_log_import


SECRET = b"lionspath-phase-three-test-secret-32-bytes-minimum"
CHROME = (
    "Mozilla/5.0 (X11; CrOS x86_64 15917.71.0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def line(
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


class PhaseThreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.database = self.root / "analytics.db"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_plain(self, path: Path, lines: list[str]) -> None:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_gzip(self, path: Path, lines: list[str]) -> None:
        with gzip.open(path, "wb") as stream:
            stream.write(("\n".join(lines) + "\n").encode("utf-8"))

    def test_historical_rollups_are_accurate_and_repeatable(self) -> None:
        path = self.root / "lionspath_ssl_access.log.3.gz"
        lines = [
            line("192.0.2.10", "14/Aug/2026:14:00:00 +0000"),
            line(
                "192.0.2.11",
                "14/Aug/2026:14:05:00 +0000",
                "GET /enrollment/?utm_source=qr HTTP/1.1",
            ),
            line(
                "192.0.2.10",
                "14/Aug/2026:14:06:00 +0000",
                "GET /assets/cte-logo.png HTTP/1.1",
            ),
            line(
                "192.0.2.12",
                "14/Aug/2026:14:07:00 +0000",
                user_agent="Googlebot/2.1",
            ),
            line(
                "192.0.2.10",
                "14/Aug/2026:14:08:00 +0000",
                "GET /missing HTTP/1.1",
                status=404,
            ),
            line("192.0.2.10", "15/Aug/2026:14:00:00 +0000"),
        ]
        self.write_gzip(path, lines)
        LogImporter(self.database, SECRET).import_paths([path])

        with closing(connect_database(self.database)) as connection:
            initialize_database(connection)
            first = refresh_rollups(connection)
            second = refresh_rollups(connection)
            daily = connection.execute(
                """
                SELECT local_date, total_requests, human_pageviews, bot_requests,
                       asset_requests, estimated_daily_visitors
                FROM analytics_daily ORDER BY local_date
                """
            ).fetchall()
            hourly = connection.execute(
                """
                SELECT total_requests, human_pageviews, estimated_visitors
                FROM analytics_hourly
                WHERE local_date = '2026-08-14' AND local_hour = 10
                """
            ).fetchone()
            pages = connection.execute(
                """
                SELECT normalized_path, pageviews, estimated_visitors
                FROM analytics_page_daily
                WHERE local_date = '2026-08-14'
                ORDER BY normalized_path
                """
            ).fetchall()

        self.assertEqual(first.daily_rows, 2)
        self.assertEqual(second.daily_rows, 2)
        self.assertEqual(tuple(daily[0]), ("2026-08-14", 5, 2, 1, 1, 2))
        self.assertEqual(tuple(daily[1]), ("2026-08-15", 1, 1, 0, 0, 1))
        self.assertEqual(tuple(hourly), (5, 2, 2))
        self.assertEqual(
            [tuple(row) for row in pages],
            [("/", 1, 1), ("/enrollment", 1, 1)],
        )

    def test_validation_reconciles_gzip_fingerprints_and_known_counts(self) -> None:
        path = self.root / "lionspath_ssl_access.log.3.gz"
        lines = [
            line("192.0.2.1", "14/Aug/2026:14:00:00 +0000"),
            line("192.0.2.2", "14/Aug/2026:14:01:00 +0000"),
            line(
                "192.0.2.3",
                "14/Aug/2026:14:02:00 +0000",
                "GET /?utm_source=qr HTTP/1.1",
            ),
            line(
                "192.0.2.4",
                "14/Aug/2026:14:03:00 +0000",
                "GET /assets/lionpath-app.js HTTP/1.1",
            ),
        ]
        self.write_gzip(path, lines)
        LogImporter(self.database, SECRET).import_paths([path])

        scan = scan_log_file(path)
        result = validate_log_import(
            path,
            self.database,
            expected_total=4,
            expected_home_gets=2,
        )
        self.assertEqual(scan.raw_lines, 4)
        self.assertEqual(scan.direct_home_gets, 2)
        self.assertEqual(result.imported_requests, 4)
        self.assertEqual(result.missing_requests, 0)
        self.assertTrue(result.total_matches_expected)
        self.assertTrue(result.home_matches_expected)
        self.assertTrue(result.passed)

    def test_validation_reports_missing_rows_and_expected_count_mismatch(self) -> None:
        imported = self.root / "lionspath_ssl_access.log"
        missing = self.root / "lionspath_ssl_access.log.1"
        self.write_plain(imported, [line("192.0.2.1", "14/Aug/2026:14:00:00 +0000")])
        self.write_plain(missing, [line("192.0.2.2", "14/Aug/2026:14:01:00 +0000")])
        LogImporter(self.database, SECRET).import_paths([imported])
        result = validate_log_import(
            missing,
            self.database,
            expected_total=2,
            expected_home_gets=1,
        )
        self.assertEqual(result.missing_requests, 1)
        self.assertFalse(result.total_matches_expected)
        self.assertTrue(result.home_matches_expected)
        self.assertFalse(result.database_complete)
        self.assertFalse(result.passed)

    def test_backfill_discovers_all_logs_imports_and_builds_rollups(self) -> None:
        first = self.root / "lionspath_ssl_access.log.2.gz"
        second = self.root / "lionspath_ssl_access.log.1"
        self.write_gzip(first, [line("192.0.2.1", "14/Aug/2026:14:00:00 +0000")])
        self.write_plain(second, [line("192.0.2.2", "15/Aug/2026:14:00:00 +0000")])
        config = AnalyticsConfig(
            database_path=self.database,
            log_pattern=str(self.root / "lionspath_ssl_access.log*"),
            secret=SECRET,
        )
        result = run_backfill(
            config,
            validate_file=first,
            expected_total=1,
            expected_home_gets=1,
        )
        self.assertEqual(result.files_discovered, 2)
        self.assertEqual(result.import_result.rows_inserted, 2)
        self.assertEqual(result.rollup_result.daily_rows, 2)
        self.assertTrue(result.validation_result.passed)

        repeated = run_backfill(config)
        self.assertEqual(repeated.import_result.rows_inserted, 0)
        self.assertEqual(repeated.import_result.duplicates_skipped, 1)
        with closing(sqlite3.connect(self.database)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM requests").fetchone()[0], 2)

    def test_backfill_dry_run_leaves_no_database(self) -> None:
        path = self.root / "lionspath_ssl_access.log.1"
        self.write_plain(path, [line("192.0.2.1", "14/Aug/2026:14:00:00 +0000")])
        config = AnalyticsConfig(
            database_path=self.database,
            log_pattern=str(self.root / "lionspath_ssl_access.log*"),
            secret=SECRET,
        )
        result = run_backfill(config, dry_run=True)
        self.assertTrue(result.dry_run)
        self.assertEqual(result.import_result.rows_inserted, 1)
        self.assertIsNone(result.rollup_result)
        self.assertFalse(self.database.exists())


if __name__ == "__main__":
    unittest.main()

