from __future__ import annotations

import gzip
import sqlite3
import tempfile
import unittest
from contextlib import closing
from dataclasses import asdict
from datetime import date
from pathlib import Path

from analytics.classify import (
    classify_referrer,
    classify_request,
    classify_user_agent,
    normalize_path,
)
from analytics.import_logs import LogImporter, discover_log_files, recent_log_files
from analytics.parser import (
    LogParseError,
    build_request_record,
    parse_apache_timestamp,
    parse_combined_log_line,
)
from analytics.privacy import daily_visitor_hash, line_fingerprint, monthly_visitor_hash


SECRET = b"lionspath-phase-two-test-secret-32-bytes-minimum"
CHROMEOS_UA = (
    "Mozilla/5.0 (X11; CrOS x86_64 15917.71.0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
IPHONE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
    "AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1"
)


def log_line(
    ip: str = "172.226.142.25",
    timestamp: str = "14/Aug/2026:00:09:46 +0000",
    request: str = "GET / HTTP/1.1",
    status: int = 200,
    size: str = "46440",
    referrer: str = "-",
    user_agent: str = CHROMEOS_UA,
) -> str:
    return (
        f'{ip} - - [{timestamp}] "{request}" {status} {size} '
        f'"{referrer}" "{user_agent}"'
    )


class ParserTests(unittest.TestCase):
    def test_combined_log_parsing_and_timezone_conversion(self) -> None:
        entry = parse_combined_log_line(
            log_line(request="GET /?utm_source=cards&student=discard-me HTTP/1.1")
        )
        record = build_request_record(entry, SECRET)

        self.assertEqual(entry.remote_addr, "172.226.142.25")
        self.assertEqual(record.timestamp_utc, "2026-08-14T00:09:46Z")
        self.assertEqual(record.local_date, "2026-08-13")
        self.assertEqual(record.local_hour, 20)
        self.assertEqual(record.path, "/")
        self.assertEqual(record.normalized_path, "/")
        self.assertEqual(record.request_class, "pageview")
        self.assertEqual(record.device_type, "Desktop / Chromebook")
        self.assertEqual(record.operating_system, "ChromeOS")

    def test_timestamp_honors_daylight_saving_time(self) -> None:
        winter = parse_apache_timestamp("15/Jan/2026:15:00:00 +0000")
        summer = parse_apache_timestamp("15/Jul/2026:15:00:00 +0000")
        winter_record = build_request_record(
            parse_combined_log_line(log_line(timestamp=winter.strftime("%d/%b/%Y:%H:%M:%S %z"))),
            SECRET,
        )
        summer_record = build_request_record(
            parse_combined_log_line(log_line(timestamp=summer.strftime("%d/%b/%Y:%H:%M:%S %z"))),
            SECRET,
        )
        self.assertEqual(winter_record.local_hour, 10)
        self.assertEqual(summer_record.local_hour, 11)

    def test_malformed_log_line_is_rejected(self) -> None:
        with self.assertRaises(LogParseError):
            parse_combined_log_line("this is not an Apache access log")

    def test_asset_bot_and_api_classification(self) -> None:
        asset = build_request_record(
            parse_combined_log_line(log_line(request="GET /assets/cte-logo.png HTTP/1.1")),
            SECRET,
        )
        bot = build_request_record(
            parse_combined_log_line(log_line(user_agent="curl/8.5.0")),
            SECRET,
        )
        api_class, pageview, is_asset, _ = classify_request(
            "POST", "/api/analytics/event", 204, CHROMEOS_UA
        )
        self.assertEqual(asset.request_class, "asset")
        self.assertEqual(asset.is_pageview, 0)
        self.assertEqual(bot.request_class, "bot")
        self.assertEqual(bot.is_bot, 1)
        self.assertEqual(api_class, "api")
        self.assertFalse(pageview)
        self.assertFalse(is_asset)

    def test_path_normalization_discards_queries(self) -> None:
        self.assertEqual(normalize_path("/employment/?utm_source=qr&token=secret"), "/employment")
        self.assertEqual(normalize_path("https://example.org//index.html?x=1"), "/")

    def test_referrer_is_reduced_to_a_safe_source(self) -> None:
        self.assertEqual(classify_referrer("-"), "Direct")
        self.assertEqual(
            classify_referrer("https://classroom.google.com/c/secret-id"),
            "Google Classroom",
        )
        self.assertEqual(
            classify_referrer("https://sites.google.com/lcps.k12.va.us/private?id=42"),
            "Google Search",
        )

    def test_mobile_classification(self) -> None:
        client = classify_user_agent(IPHONE_UA)
        self.assertEqual(client.browser, "Safari")
        self.assertEqual(client.operating_system, "iOS")
        self.assertEqual(client.device_type, "Mobile")

    def test_request_record_does_not_retain_raw_identifiers(self) -> None:
        entry = parse_combined_log_line(log_line())
        values = asdict(build_request_record(entry, SECRET))
        serialized = repr(values)
        self.assertNotIn(entry.remote_addr, serialized)
        self.assertNotIn(entry.user_agent, serialized)
        self.assertNotIn("remote_addr", values)
        self.assertNotIn("user_agent", values)


class PrivacyTests(unittest.TestCase):
    def test_daily_hash_rotates_and_monthly_hash_does_not_rotate_daily(self) -> None:
        first = date(2026, 8, 14)
        next_day = date(2026, 8, 15)
        next_month = date(2026, 9, 1)
        day_one = daily_visitor_hash(SECRET, first, "192.0.2.1", CHROMEOS_UA)
        day_two = daily_visitor_hash(SECRET, next_day, "192.0.2.1", CHROMEOS_UA)
        month_one = monthly_visitor_hash(SECRET, first, "192.0.2.1", CHROMEOS_UA)
        same_month = monthly_visitor_hash(SECRET, next_day, "192.0.2.1", CHROMEOS_UA)
        month_two = monthly_visitor_hash(SECRET, next_month, "192.0.2.1", CHROMEOS_UA)
        self.assertNotEqual(day_one, day_two)
        self.assertEqual(month_one, same_month)
        self.assertNotEqual(month_one, month_two)

    def test_fingerprint_is_stable_for_rotation_but_preserves_offsets(self) -> None:
        raw = log_line().encode("utf-8")
        self.assertEqual(line_fingerprint(raw, 0), line_fingerprint(raw, 0))
        self.assertNotEqual(line_fingerprint(raw, 0), line_fingerprint(raw, 100))


class ImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.database = self.root / "analytics.db"
        self.importer = LogImporter(self.database, SECRET, commit_interval=1)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_log(self, path: Path, lines: list[str], final_newline: bool = True) -> None:
        payload = "\n".join(lines) + ("\n" if final_newline else "")
        path.write_text(payload, encoding="utf-8")

    def database_count(self) -> int:
        with closing(sqlite3.connect(self.database)) as connection:
            return int(connection.execute("SELECT COUNT(*) FROM requests").fetchone()[0])

    def test_plain_and_gzip_imports_are_idempotent(self) -> None:
        plain = self.root / "lionspath_ssl_access.log.1"
        lines = [
            log_line(),
            log_line(
                timestamp="14/Aug/2026:00:10:46 +0000",
                request="GET /assets/cte-logo.png HTTP/1.1",
            ),
        ]
        self.write_log(plain, lines)
        first = self.importer.import_paths([plain])
        self.assertEqual(first.rows_inserted, 2)

        compressed = self.root / "lionspath_ssl_access.log.2.gz"
        with gzip.open(compressed, "wb") as stream:
            stream.write(plain.read_bytes())
        duplicate = self.importer.import_paths([compressed])
        self.assertEqual(duplicate.rows_inserted, 0)
        self.assertEqual(duplicate.duplicates_skipped, 2)
        self.assertEqual(self.database_count(), 2)

    def test_rotation_checkpoint_and_gzip_do_not_duplicate_or_lose_rows(self) -> None:
        current = self.root / "lionspath_ssl_access.log"
        self.write_log(current, [log_line()])
        self.assertEqual(self.importer.import_paths([current]).rows_inserted, 1)

        rotated = self.root / "lionspath_ssl_access.log.1"
        current.rename(rotated)
        self.write_log(
            current,
            [log_line(timestamp="14/Aug/2026:00:11:46 +0000", request="GET /help HTTP/1.1")],
        )
        second = self.importer.import_paths([rotated, current])
        self.assertEqual(second.rows_inserted, 1)
        self.assertEqual(self.database_count(), 2)

        compressed = self.root / "lionspath_ssl_access.log.2.gz"
        with gzip.open(compressed, "wb") as stream:
            stream.write(rotated.read_bytes())
        rotated.unlink()
        third = self.importer.import_paths([compressed])
        self.assertEqual(third.rows_inserted, 0)
        self.assertEqual(third.duplicates_skipped, 1)
        self.assertEqual(self.database_count(), 2)

    def test_partial_live_line_is_deferred_until_complete(self) -> None:
        current = self.root / "lionspath_ssl_access.log"
        self.write_log(current, [log_line()], final_newline=False)
        first = self.importer.import_paths([current])
        self.assertEqual(first.rows_inserted, 0)
        self.assertEqual(first.deferred_partial_lines, 1)

        with current.open("ab") as stream:
            stream.write(b"\n")
        second = self.importer.import_paths([current])
        self.assertEqual(second.rows_inserted, 1)
        self.assertEqual(self.database_count(), 1)

    def test_malformed_lines_are_skipped_without_stopping(self) -> None:
        path = self.root / "lionspath_ssl_access.log"
        self.write_log(path, ["bad line", log_line()])
        result = self.importer.import_paths([path])
        self.assertEqual(result.malformed_skipped, 1)
        self.assertEqual(result.rows_inserted, 1)
        self.assertEqual(self.database_count(), 1)

    def test_dry_run_does_not_create_database(self) -> None:
        path = self.root / "lionspath_ssl_access.log"
        self.write_log(path, [log_line()])
        result = self.importer.import_paths([path], dry_run=True)
        self.assertEqual(result.rows_inserted, 1)
        self.assertFalse(self.database.exists())

    def test_discovery_separates_recent_and_historical_logs(self) -> None:
        current = self.root / "lionspath_ssl_access.log"
        previous = self.root / "lionspath_ssl_access.log.1"
        historical = self.root / "lionspath_ssl_access.log.2.gz"
        self.write_log(current, [log_line()])
        self.write_log(previous, [log_line()])
        with gzip.open(historical, "wb") as stream:
            stream.write((log_line() + "\n").encode("utf-8"))
        pattern = str(self.root / "lionspath_ssl_access.log*")
        self.assertEqual(len(discover_log_files(pattern)), 3)
        self.assertEqual({path.name for path in recent_log_files(pattern)}, {current.name, previous.name})

    def test_database_contains_hashes_not_raw_ip_or_user_agent(self) -> None:
        path = self.root / "lionspath_ssl_access.log"
        self.write_log(path, [log_line()])
        self.importer.import_paths([path])
        with closing(sqlite3.connect(self.database)) as connection:
            row = connection.execute(
                "SELECT visitor_day_hash, visitor_month_hash, browser, operating_system FROM requests"
            ).fetchone()
            schema = " ".join(
                column[1]
                for column in connection.execute("PRAGMA table_info(requests)").fetchall()
            )
        self.assertEqual(len(row[0]), 64)
        self.assertEqual(len(row[1]), 64)
        self.assertNotIn("ip_address", schema)
        self.assertNotIn("user_agent", schema)


if __name__ == "__main__":
    unittest.main()
