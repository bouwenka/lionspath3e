"""Incremental log import and recent rollup refresh for the systemd timer."""

from __future__ import annotations

import argparse
import json
import sys
from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from analytics.config import AnalyticsConfig, load_config
    from analytics.database import connect_database, initialize_database
    from analytics.import_logs import ImportResult, LogImporter, recent_log_files
    from analytics.rollups import RollupResult, refresh_rollups
else:
    from .config import AnalyticsConfig, load_config
    from .database import connect_database, initialize_database
    from .import_logs import ImportResult, LogImporter, recent_log_files
    from .rollups import RollupResult, refresh_rollups


@dataclass(frozen=True)
class RefreshResult:
    files_selected: tuple[str, ...]
    import_result: ImportResult
    rollup_result: RollupResult


def run_refresh(
    config: AnalyticsConfig,
    rollup_days: int = 3,
) -> RefreshResult:
    if rollup_days < 1 or rollup_days > 31:
        raise ValueError("rollup_days must be between 1 and 31")

    paths = recent_log_files(config.log_pattern)
    if not paths:
        raise RuntimeError(f"No logs matched {config.log_pattern}")

    imported = LogImporter(
        config.database_path,
        config.secret,
        config.timezone_name,
    ).import_paths(paths)

    with closing(connect_database(config.database_path)) as connection:
        initialize_database(connection)
        newest_row = connection.execute("SELECT MAX(local_date) FROM requests").fetchone()
        newest = str(newest_row[0]) if newest_row and newest_row[0] else None
        if newest is None:
            rollups = RollupResult(None, None, 0, 0, 0)
        else:
            newest_date = date.fromisoformat(newest)
            start = (newest_date - timedelta(days=rollup_days - 1)).isoformat()
            rollups = refresh_rollups(connection, start, newest)

    return RefreshResult(
        files_selected=tuple(path.name for path in paths),
        import_result=imported,
        rollup_result=rollups,
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import recent LionsPath logs and refresh recent aggregates."
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    parser.add_argument("--db", type=Path, help="Override the SQLite database path")
    parser.add_argument("--log-pattern", help="Override the Apache log glob")
    parser.add_argument("--secret-file", type=Path, help="Read the HMAC secret from this file")
    parser.add_argument(
        "--rollup-days",
        type=int,
        default=3,
        help="Number of most-recent local dates to rebuild (default: 3)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        result = run_refresh(
            load_config(args.db, args.log_pattern, args.secret_file),
            args.rollup_days,
        )
        payload = asdict(result)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            imported = result.import_result
            rollups = result.rollup_result
            print(
                f"Refresh complete: {imported.rows_inserted:,} rows inserted from "
                f"{imported.source_count} file(s); rollups cover "
                f"{rollups.start_date or 'no data'} through {rollups.end_date or 'no data'}."
            )
        return 0
    except Exception as exc:
        print(f"Refresh failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
