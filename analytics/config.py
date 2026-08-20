"""Configuration loading for the LionsPath analytics backend."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path

from .privacy import validate_secret


DEFAULT_DATABASE_PATH = Path("/var/lib/lionspath/analytics.db")
DEFAULT_LOG_PATTERN = "/var/log/apache2/lionspath_ssl_access.log*"
DEFAULT_SECRET_FILE = Path("/etc/lionspath/analytics.secret")
DEFAULT_TIMEZONE = "America/New_York"


@dataclass(frozen=True)
class AnalyticsConfig:
    database_path: Path
    log_pattern: str
    secret: bytes
    timezone_name: str = DEFAULT_TIMEZONE


def load_secret(secret_file: Path | None = None) -> bytes:
    path = secret_file or Path(
        os.environ.get("LIONPATH_ANALYTICS_SECRET_FILE", DEFAULT_SECRET_FILE)
    )
    try:
        metadata = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError("Analytics secret must be a regular, non-symlink file")
        if os.name == "posix" and stat.S_IMODE(metadata.st_mode) & 0o077:
            raise RuntimeError("Analytics secret permissions must be 0600 or stricter")
        secret = path.read_bytes().strip()
    except OSError as exc:
        raise RuntimeError(
            f"Analytics secret is unavailable at {path}. Create it with restricted permissions."
        ) from exc
    return validate_secret(secret)


def load_config(
    database_path: Path | None = None,
    log_pattern: str | None = None,
    secret_file: Path | None = None,
) -> AnalyticsConfig:
    configured_database = database_path or Path(
        os.environ.get("LIONPATH_ANALYTICS_DB", DEFAULT_DATABASE_PATH)
    )
    configured_pattern = log_pattern or os.environ.get(
        "LIONPATH_ANALYTICS_LOG_PATTERN", DEFAULT_LOG_PATTERN
    )
    configured_timezone = os.environ.get(
        "LIONPATH_ANALYTICS_TIMEZONE", DEFAULT_TIMEZONE
    )
    return AnalyticsConfig(
        database_path=configured_database,
        log_pattern=configured_pattern,
        secret=load_secret(secret_file),
        timezone_name=configured_timezone,
    )
