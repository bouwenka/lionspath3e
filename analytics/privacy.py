"""Privacy-preserving identifiers used by the analytics importer."""

from __future__ import annotations

import hashlib
import hmac
from datetime import date


MINIMUM_SECRET_BYTES = 32


def validate_secret(secret: bytes) -> bytes:
    if not isinstance(secret, bytes):
        raise TypeError("Analytics secret must be bytes")
    if len(secret) < MINIMUM_SECRET_BYTES:
        raise ValueError("Analytics secret must contain at least 32 bytes")
    return secret


def _visitor_hash(secret: bytes, scope: str, ip_address: str, user_agent: str) -> str:
    validate_secret(secret)
    message = "\x1f".join((scope, ip_address, user_agent)).encode("utf-8", "replace")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def daily_visitor_hash(
    secret: bytes,
    local_date: date,
    ip_address: str,
    user_agent: str,
) -> str:
    """Return an identifier that intentionally rotates every local calendar day."""

    return _visitor_hash(secret, f"day:{local_date.isoformat()}", ip_address, user_agent)


def monthly_visitor_hash(
    secret: bytes,
    local_date: date,
    ip_address: str,
    user_agent: str,
) -> str:
    """Return a month-scoped estimate without creating a long-term device ID."""

    return _visitor_hash(
        secret,
        f"month:{local_date.year:04d}-{local_date.month:02d}",
        ip_address,
        user_agent,
    )


def line_fingerprint(raw_line: bytes, logical_offset: int) -> str:
    """Fingerprint a decompressed log line independently of its rotated filename."""

    if logical_offset < 0:
        raise ValueError("Log offset cannot be negative")
    content = raw_line.rstrip(b"\r\n")
    digest = hashlib.sha256()
    digest.update(str(logical_offset).encode("ascii"))
    digest.update(b"\x00")
    digest.update(content)
    return digest.hexdigest()

