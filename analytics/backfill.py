"""Historical LionsPath analytics import and aggregate rebuilding."""

from __future__ import annotations

import argparse
import json
import sys
from contextlib import closing
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from analytics.config import AnalyticsConfig, load_config
    from analytics.database import connect_database, initialize_database
    from analytics.import_logs import ImportResult, LogImporter, discover_log_files
    from analytics.rollups import RollupResult, refresh_rollups
    from analytics.validate import ValidationResult, validate_log_import
else:
    from .config import AnalyticsConfig, load_config
    from .database import connect_database, initialize_database
    from .import_logs import ImportResult, LogImporter, discover_log_files
    from .rollups import RollupResult, refresh_rollups
    from .validate import ValidationResult, validate_log_import


@dataclass(frozen=True)
class BackfillResult:
    files_discovered: int
    import_result: ImportResult
    rollup_result: RollupResult | None
    validation_result: ValidationResult | None
    dry_run: bool


def run_backfill(
    config: AnalyticsConfig,
    dry_run: bool = False,
    validate_file: Path | None = None,
    expected_total: int | None = None,
    expected_home_gets: int | None = None,
    expected_malformed_lines: int | None = None,
) -> BackfillResult:
    paths = discover_log_files(config.log_pattern)
    if not paths:
        raise RuntimeError(f"No logs matched {config.log_pattern}")

    import_result = LogImporter(
        config.database_path,
        config.secret,
        config.timezone_name,
    ).import_paths(paths, dry_run=dry_run)

    rollup_result: RollupResult | None = None
    validation_result: ValidationResult | None = None
    if not dry_run:
        with closing(connect_database(config.database_path)) as connection:
            initialize_database(connection)
            rollup_result = refresh_rollups(connection)
        if validate_file is not None:
            validation_result = validate_log_import(
                validate_file,
                config.database_path,
                expected_total,
                expected_home_gets,
                expected_malformed_lines,
            )

    return BackfillResult(
        files_discovered=len(paths),
        import_result=import_result,
        rollup_result=rollup_result,
        validation_result=validation_result,
        dry_run=dry_run,
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import all available LionsPath logs and rebuild aggregate tables."
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse without writing SQLite")
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    parser.add_argument("--db", type=Path, help="Override the SQLite database path")
    parser.add_argument("--log-pattern", help="Override the Apache log glob")
    parser.add_argument("--secret-file", type=Path, help="Read the HMAC secret from this file")
    parser.add_argument("--validate-file", type=Path, help="Reconcile this log after import")
    parser.add_argument("--expected-total", type=int, help="Expected raw lines in validation log")
    parser.add_argument("--expected-home", type=int, help="Expected exact GET / requests")
    parser.add_argument(
        "--expected-malformed",
        type=int,
        help="Expected non-request lines in the validation log",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        config = load_config(args.db, args.log_pattern, args.secret_file)
        result = run_backfill(
            config,
            dry_run=args.dry_run,
            validate_file=args.validate_file,
            expected_total=args.expected_total,
            expected_home_gets=args.expected_home,
            expected_malformed_lines=args.expected_malformed,
        )
        payload = asdict(result)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            imported = result.import_result
            print(
                f"Backfill {'dry run' if result.dry_run else 'complete'}: "
                f"{result.files_discovered} file(s), {imported.lines_seen:,} lines, "
                f"{imported.rows_inserted:,} rows inserted, "
                f"{imported.duplicates_skipped:,} duplicates skipped."
            )
            if result.rollup_result:
                rollups = result.rollup_result
                print(
                    f"Rollups refreshed for {rollups.start_date} through {rollups.end_date}: "
                    f"{rollups.daily_rows} daily, {rollups.hourly_rows} hourly, "
                    f"{rollups.page_rows} page rows."
                )
            if result.validation_result:
                validation = result.validation_result
                print(
                    f"Validation {'PASSED' if validation.passed else 'FAILED'}: "
                    f"{validation.file}; {validation.raw_lines:,} raw lines, "
                    f"{validation.direct_home_gets:,} exact GET / requests, "
                    f"{validation.missing_requests:,} missing from SQLite."
                )
        if result.validation_result and not result.validation_result.passed:
            return 2
        return 0
    except Exception as exc:
        print(f"Backfill failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

