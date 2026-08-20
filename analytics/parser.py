"""Apache Combined Log Format parsing for LionsPath analytics."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .classify import (
    classify_referrer,
    classify_request,
    extract_path,
    normalize_path,
)
from .privacy import daily_visitor_hash, monthly_visitor_hash


COMBINED_LOG_RE = re.compile(
    r'^(?P<remote_addr>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<request>(?:[^"\\]|\\.)*)" '
    r'(?P<status>\d{3}|-) (?P<size>\d+|-) '
    r'"(?P<referrer>(?:[^"\\]|\\.)*)" '
    r'"(?P<user_agent>(?:[^"\\]|\\.)*)"(?: .*)?$'
)


class LogParseError(ValueError):
    """Raised when a log line cannot be safely interpreted."""


@dataclass(frozen=True)
class ApacheLogEntry:
    remote_addr: str
    timestamp: datetime
    method: str
    request_target: str
    protocol: str
    status_code: int
    bytes_sent: int | None
    referrer: str
    user_agent: str


@dataclass(frozen=True)
class RequestRecord:
    occurred_at_utc: int
    timestamp_utc: str
    timestamp_local: str
    local_date: str
    local_hour: int
    local_weekday: int
    visitor_day_hash: str
    visitor_month_hash: str
    method: str
    path: str
    normalized_path: str
    status_code: int
    bytes_sent: int | None
    referrer_source: str
    browser: str
    operating_system: str
    device_type: str
    request_class: str
    is_pageview: int
    is_asset: int
    is_bot: int


def parse_apache_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%d/%b/%Y:%H:%M:%S %z")
    except ValueError as exc:
        raise LogParseError("Invalid Apache timestamp") from exc
    return parsed


def parse_combined_log_line(line: str) -> ApacheLogEntry:
    match = COMBINED_LOG_RE.match(line.rstrip("\r\n"))
    if not match:
        raise LogParseError("Line does not match Apache Combined Log Format")

    request = match.group("request")
    parts = request.split()
    if len(parts) < 2:
        raise LogParseError("Request field is incomplete")
    method = parts[0].upper()[:16]
    request_target = parts[1]
    protocol = parts[2][:32] if len(parts) > 2 else ""

    status_text = match.group("status")
    if status_text == "-":
        raise LogParseError("Status code is missing")
    size_text = match.group("size")

    return ApacheLogEntry(
        remote_addr=match.group("remote_addr"),
        timestamp=parse_apache_timestamp(match.group("timestamp")),
        method=method,
        request_target=request_target,
        protocol=protocol,
        status_code=int(status_text),
        bytes_sent=None if size_text == "-" else int(size_text),
        referrer=match.group("referrer"),
        user_agent=match.group("user_agent"),
    )


def build_request_record(
    entry: ApacheLogEntry,
    secret: bytes,
    timezone_name: str = "America/New_York",
) -> RequestRecord:
    local_timezone = ZoneInfo(timezone_name)
    utc_time = entry.timestamp.astimezone(timezone.utc)
    local_time = entry.timestamp.astimezone(local_timezone)
    path = extract_path(entry.request_target)
    normalized = normalize_path(path)
    request_class, pageview, asset, client = classify_request(
        entry.method,
        normalized,
        entry.status_code,
        entry.user_agent,
    )

    return RequestRecord(
        occurred_at_utc=int(utc_time.timestamp()),
        timestamp_utc=utc_time.isoformat().replace("+00:00", "Z"),
        timestamp_local=local_time.isoformat(),
        local_date=local_time.date().isoformat(),
        local_hour=local_time.hour,
        local_weekday=local_time.weekday(),
        visitor_day_hash=daily_visitor_hash(
            secret, local_time.date(), entry.remote_addr, entry.user_agent
        ),
        visitor_month_hash=monthly_visitor_hash(
            secret, local_time.date(), entry.remote_addr, entry.user_agent
        ),
        method=entry.method,
        path=path,
        normalized_path=normalized,
        status_code=entry.status_code,
        bytes_sent=entry.bytes_sent,
        referrer_source=classify_referrer(entry.referrer),
        browser=client.browser,
        operating_system=client.operating_system,
        device_type=client.device_type,
        request_class=request_class,
        is_pageview=int(pageview),
        is_asset=int(asset),
        is_bot=int(client.is_bot),
    )

