"""Idempotent Apache access-log importer for LionsPath analytics."""

from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from analytics.config import load_config
    from analytics.database import (
        begin_import_run,
        connect_database,
        finish_import_run,
        get_checkpoint,
        initialize_database,
        insert_request,
        save_checkpoint,
    )
    from analytics.parser import LogParseError, build_request_record, parse_combined_log_line
    from analytics.privacy import line_fingerprint
else:
    from .config import load_config
    from .database import (
        begin_import_run,
        connect_database,
        finish_import_run,
        get_checkpoint,
        initialize_database,
        insert_request,
        save_checkpoint,
    )
    from .parser import LogParseError, build_request_record, parse_combined_log_line
    from .privacy import line_fingerprint


@dataclass
class ImportResult:
    source_count: int = 0
    lines_seen: int = 0
    rows_inserted: int = 0
    duplicates_skipped: int = 0
    malformed_skipped: int = 0
    deferred_partial_lines: int = 0

    def add(self, other: "ImportResult") -> None:
        self.source_count += other.source_count
        self.lines_seen += other.lines_seen
        self.rows_inserted += other.rows_inserted
        self.duplicates_skipped += other.duplicates_skipped
        self.malformed_skipped += other.malformed_skipped
        self.deferred_partial_lines += other.deferred_partial_lines


def source_identity(path: Path) -> str:
    stat = path.stat()
    return f"{stat.st_dev}:{stat.st_ino}"


def open_log_stream(path: Path) -> BinaryIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rb")
    return path.open("rb")


def discover_log_files(pattern: str) -> list[Path]:
    files = [Path(value) for value in glob.glob(pattern) if Path(value).is_file()]
    return sorted(files, key=lambda path: (path.stat().st_mtime_ns, path.name))


def recent_log_files(pattern: str) -> list[Path]:
    files = discover_log_files(pattern)
    if not files:
        return []
    current = [path for path in files if path.name.endswith("_ssl_access.log")]
    previous = [path for path in files if path.name.endswith("_ssl_access.log.1")]
    selected = previous + current
    return selected or files[-1:]


class LogImporter:
    def __init__(
        self,
        database_path: Path,
        secret: bytes,
        timezone_name: str = "America/New_York",
        commit_interval: int = 2000,
    ) -> None:
        self.database_path = Path(database_path)
        self.secret = secret
        self.timezone_name = timezone_name
        self.commit_interval = max(1, commit_interval)

    def import_paths(
        self,
        paths: Iterable[Path],
        dry_run: bool = False,
    ) -> ImportResult:
        selected = [Path(path) for path in paths]
        for path in selected:
            if not path.is_file():
                raise FileNotFoundError(path)

        total = ImportResult()
        connection: sqlite3.Connection | None = None
        run_id: int | None = None
        try:
            if not dry_run:
                connection = connect_database(self.database_path)
                initialize_database(connection)
                run_id = begin_import_run(connection, len(selected))

            for path in selected:
                total.add(self._import_path(path, connection, dry_run))

            if connection is not None and run_id is not None:
                finish_import_run(
                    connection,
                    run_id,
                    "success",
                    total.lines_seen,
                    total.rows_inserted,
                    total.duplicates_skipped,
                    total.malformed_skipped,
                )
            return total
        except Exception as exc:
            if connection is not None:
                connection.rollback()
                if run_id is not None:
                    finish_import_run(
                        connection,
                        run_id,
                        "failed",
                        total.lines_seen,
                        total.rows_inserted,
                        total.duplicates_skipped,
                        total.malformed_skipped,
                        str(exc),
                    )
            raise
        finally:
            if connection is not None:
                connection.close()

    def _import_path(
        self,
        path: Path,
        connection: sqlite3.Connection | None,
        dry_run: bool,
    ) -> ImportResult:
        result = ImportResult(source_count=1)
        compressed = path.suffix.lower() == ".gz"
        stat = path.stat()
        identity = source_identity(path)
        start_offset = 0

        if connection is not None and not compressed:
            checkpoint = get_checkpoint(connection, identity)
            if checkpoint and stat.st_size >= checkpoint["byte_offset"]:
                start_offset = int(checkpoint["byte_offset"])

        checkpoint_offset = start_offset
        with open_log_stream(path) as stream:
            if start_offset:
                stream.seek(start_offset)

            writes_since_commit = 0
            while True:
                line_offset = int(stream.tell())
                raw_line = stream.readline()
                if not raw_line:
                    checkpoint_offset = int(stream.tell())
                    break

                if not compressed and not raw_line.endswith(b"\n"):
                    result.deferred_partial_lines += 1
                    checkpoint_offset = line_offset
                    break

                checkpoint_offset = int(stream.tell())
                result.lines_seen += 1
                fingerprint = line_fingerprint(raw_line, line_offset)

                try:
                    text = raw_line.decode("utf-8", "replace")
                    entry = parse_combined_log_line(text)
                    record = build_request_record(entry, self.secret, self.timezone_name)
                except (LogParseError, UnicodeError, ValueError):
                    result.malformed_skipped += 1
                    continue

                if dry_run or connection is None:
                    result.rows_inserted += 1
                    continue

                inserted = insert_request(
                    connection,
                    record,
                    path.name[:255],
                    line_offset,
                    fingerprint,
                )
                if inserted:
                    result.rows_inserted += 1
                else:
                    result.duplicates_skipped += 1
                writes_since_commit += 1

                if writes_since_commit >= self.commit_interval:
                    connection.commit()
                    writes_since_commit = 0

        if connection is not None:
            connection.commit()
            if not compressed:
                save_checkpoint(
                    connection,
                    identity,
                    str(path),
                    checkpoint_offset,
                    stat.st_size,
                    stat.st_mtime_ns,
                    "success",
                )
                connection.commit()
        return result


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import LionsPath Apache HTTPS access logs into SQLite."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--all", action="store_true", help="Import every matching log")
    source.add_argument(
        "--current", action="store_true", help="Import only the current access log"
    )
    source.add_argument(
        "--file", action="append", type=Path, help="Import a specific file (repeatable)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse without writing SQLite")
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    parser.add_argument("--db", type=Path, help="Override the SQLite database path")
    parser.add_argument("--log-pattern", help="Override the Apache log glob")
    parser.add_argument("--secret-file", type=Path, help="Read the HMAC secret from this file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        config = load_config(args.db, args.log_pattern, args.secret_file)
        if args.file:
            paths = args.file
        elif args.all:
            paths = discover_log_files(config.log_pattern)
        elif args.current:
            paths = [
                path
                for path in discover_log_files(config.log_pattern)
                if path.name.endswith("_ssl_access.log")
            ]
        else:
            paths = recent_log_files(config.log_pattern)

        if not paths:
            raise RuntimeError("No matching Apache access logs were found")

        result = LogImporter(
            config.database_path,
            config.secret,
            config.timezone_name,
        ).import_paths(paths, dry_run=args.dry_run)

        payload = asdict(result)
        payload["database"] = str(config.database_path)
        payload["dry_run"] = bool(args.dry_run)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(
                "Imported {rows_inserted} rows from {source_count} file(s); "
                "{duplicates_skipped} duplicates and {malformed_skipped} malformed "
                "lines skipped.".format(**payload)
            )
        return 0
    except Exception as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
