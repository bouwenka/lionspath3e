"""Privacy-safe reconciliation of SQLite imports against raw Apache logs."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from contextlib import closing
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from analytics.config import DEFAULT_DATABASE_PATH
    from analytics.import_logs import open_log_stream
    from analytics.parser import LogParseError, parse_combined_log_line
    from analytics.privacy import line_fingerprint
else:
    from .config import DEFAULT_DATABASE_PATH
    from .import_logs import open_log_stream
    from .parser import LogParseError, parse_combined_log_line
    from .privacy import line_fingerprint


SQLITE_BATCH_SIZE = 800


@dataclass(frozen=True)
class LogScanResult:
    file: str
    raw_lines: int
    valid_requests: int
    malformed_lines: int
    direct_home_gets: int
    fingerprints: tuple[str, ...]


@dataclass(frozen=True)
class ValidationResult:
    file: str
    raw_lines: int
    valid_requests: int
    malformed_lines: int
    direct_home_gets: int
    imported_requests: int
    missing_requests: int
    expected_total: int | None
    expected_home_gets: int | None
    expected_malformed_lines: int | None
    total_matches_expected: bool | None
    home_matches_expected: bool | None
    malformed_matches_expected: bool | None
    database_complete: bool
    passed: bool


def _batches(values: tuple[str, ...], size: int = SQLITE_BATCH_SIZE) -> Iterable[tuple[str, ...]]:
    for index in range(0, len(values), size):
        yield values[index:index + size]


def scan_log_file(path: Path) -> LogScanResult:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    raw_lines = 0
    valid_requests = 0
    malformed_lines = 0
    direct_home_gets = 0
    fingerprints: list[str] = []

    with open_log_stream(path) as stream:
        while True:
            offset = int(stream.tell())
            raw_line = stream.readline()
            if not raw_line:
                break
            raw_lines += 1
            try:
                entry = parse_combined_log_line(raw_line.decode("utf-8", "replace"))
            except (LogParseError, UnicodeError, ValueError):
                malformed_lines += 1
                continue
            valid_requests += 1
            fingerprints.append(line_fingerprint(raw_line, offset))
            if entry.method == "GET" and entry.request_target == "/":
                direct_home_gets += 1

    return LogScanResult(
        file=path.name,
        raw_lines=raw_lines,
        valid_requests=valid_requests,
        malformed_lines=malformed_lines,
        direct_home_gets=direct_home_gets,
        fingerprints=tuple(fingerprints),
    )


def validate_log_import(
    path: Path,
    database_path: Path,
    expected_total: int | None = None,
    expected_home_gets: int | None = None,
    expected_malformed_lines: int | None = None,
) -> ValidationResult:
    scan = scan_log_file(path)
    database_path = Path(database_path)
    if not database_path.is_file():
        raise FileNotFoundError(database_path)

    imported = 0
    with closing(sqlite3.connect(database_path)) as connection:
        for batch in _batches(scan.fingerprints):
            placeholders = ",".join("?" for _ in batch)
            imported += int(
                connection.execute(
                    f"SELECT COUNT(*) FROM requests WHERE log_fingerprint IN ({placeholders})",
                    batch,
                ).fetchone()[0]
            )

    missing = scan.valid_requests - imported
    total_match = None if expected_total is None else scan.raw_lines == expected_total
    home_match = (
        None if expected_home_gets is None else scan.direct_home_gets == expected_home_gets
    )
    malformed_match = (
        None
        if expected_malformed_lines is None
        else scan.malformed_lines == expected_malformed_lines
    )
    database_complete = missing == 0
    passed = (
        database_complete
        and (
            scan.malformed_lines == 0
            if expected_malformed_lines is None
            else malformed_match is True
        )
        and total_match is not False
        and home_match is not False
    )
    return ValidationResult(
        file=scan.file,
        raw_lines=scan.raw_lines,
        valid_requests=scan.valid_requests,
        malformed_lines=scan.malformed_lines,
        direct_home_gets=scan.direct_home_gets,
        imported_requests=imported,
        missing_requests=missing,
        expected_total=expected_total,
        expected_home_gets=expected_home_gets,
        expected_malformed_lines=expected_malformed_lines,
        total_matches_expected=total_match,
        home_matches_expected=home_match,
        malformed_matches_expected=malformed_match,
        database_complete=database_complete,
        passed=passed,
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reconcile an Apache log file against LionsPath analytics SQLite data."
    )
    parser.add_argument("--file", required=True, type=Path, help="Plain or gzip log file")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ.get("LIONPATH_ANALYTICS_DB", DEFAULT_DATABASE_PATH)),
        help="SQLite analytics database",
    )
    parser.add_argument("--expected-total", type=int, help="Expected raw request lines")
    parser.add_argument("--expected-home", type=int, help="Expected exact GET / requests")
    parser.add_argument(
        "--expected-malformed",
        type=int,
        help="Expected non-request lines, such as Apache 408 entries with a '-' request",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        result = validate_log_import(
            args.file,
            args.db,
            args.expected_total,
            args.expected_home,
            args.expected_malformed,
        )
        payload = asdict(result)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Validation {'PASSED' if result.passed else 'FAILED'}: {result.file}")
            print(f"  Raw request lines: {result.raw_lines:,}")
            print(f"  Valid requests: {result.valid_requests:,}")
            print(f"  Exact GET / requests: {result.direct_home_gets:,}")
            print(f"  Imported requests found: {result.imported_requests:,}")
            print(f"  Missing imported requests: {result.missing_requests:,}")
            print(f"  Malformed lines: {result.malformed_lines:,}")
        return 0 if result.passed else 2
    except Exception as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

