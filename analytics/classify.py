"""Request normalization and coarse, non-identifying client classification."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import urlsplit


ASSET_EXTENSIONS = {
    ".css", ".js", ".mjs", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".webp", ".avif", ".ico", ".woff", ".woff2", ".ttf", ".otf",
    ".map", ".json", ".xml", ".txt", ".webmanifest", ".mp3", ".mp4",
    ".webm", ".pdf", ".zip",
}

BOT_PATTERNS = re.compile(
    r"bot|crawler|spider|slurp|bingpreview|headless|lighthouse|pagespeed|"
    r"python-requests|python-urllib|curl/|wget/|go-http-client|httpclient|"
    r"nikto|nmap|masscan|sqlmap|zgrab|securityheaders|uptimerobot|statuscake|"
    r"monitoring|probe|scanner",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ClientClassification:
    browser: str
    operating_system: str
    device_type: str
    is_bot: bool


def extract_path(request_target: str) -> str:
    """Return only a path, intentionally discarding all query and fragment data."""

    target = (request_target or "/").strip()
    if target == "*":
        return "*"
    try:
        parsed = urlsplit(target)
        path = parsed.path or "/"
    except ValueError:
        path = "/"
    path = "".join(char for char in path if ord(char) >= 32)
    if not path.startswith("/"):
        path = "/" + path
    return path[:2048]


def normalize_path(request_target: str) -> str:
    path = extract_path(request_target)
    if path == "*":
        return path
    path = re.sub(r"/{2,}", "/", path)
    if path.lower() in {"/index.html", "/index.htm"}:
        return "/"
    if len(path) > 1:
        path = path.rstrip("/")
    return path or "/"


def is_asset_path(path: str) -> bool:
    normalized = normalize_path(path)
    if normalized.startswith("/assets/") or normalized in {
        "/favicon.ico", "/robots.txt", "/sitemap.xml",
    }:
        return True
    return PurePosixPath(normalized).suffix.lower() in ASSET_EXTENSIONS


def is_api_path(path: str) -> bool:
    normalized = normalize_path(path)
    return normalized.startswith("/api/") or normalized.startswith("/admin/analytics/api/")


def classify_user_agent(user_agent: str) -> ClientClassification:
    ua = user_agent or ""
    is_bot = not ua or ua == "-" or bool(BOT_PATTERNS.search(ua))

    if is_bot:
        browser = "Bot / Automated"
    elif "Edg/" in ua or "EdgiOS/" in ua or "EdgA/" in ua:
        browser = "Edge"
    elif "CriOS/" in ua or ("Chrome/" in ua and "Chromium/" not in ua):
        browser = "Chrome"
    elif "Firefox/" in ua or "FxiOS/" in ua:
        browser = "Firefox"
    elif "Safari/" in ua and "Chrome/" not in ua and "Chromium/" not in ua:
        browser = "Safari"
    else:
        browser = "Other"

    if "CrOS" in ua:
        operating_system = "ChromeOS"
    elif "Windows" in ua:
        operating_system = "Windows"
    elif "Android" in ua:
        operating_system = "Android"
    elif any(token in ua for token in ("iPhone", "iPad", "iPod")):
        operating_system = "iOS"
    elif "Mac OS X" in ua or "Macintosh" in ua:
        operating_system = "macOS"
    elif "Linux" in ua:
        operating_system = "Linux"
    else:
        operating_system = "Other"

    if is_bot:
        device_type = "Other"
    elif "iPad" in ua or "Tablet" in ua or ("Android" in ua and "Mobile" not in ua):
        device_type = "Tablet"
    elif any(token in ua for token in ("Mobile", "iPhone", "iPod")):
        device_type = "Mobile"
    elif operating_system == "ChromeOS":
        device_type = "Desktop / Chromebook"
    elif operating_system in {"Windows", "macOS", "Linux"}:
        device_type = "Desktop / Chromebook"
    else:
        device_type = "Other"

    return ClientClassification(browser, operating_system, device_type, is_bot)


def classify_referrer(referrer: str) -> str:
    value = (referrer or "").strip()
    if not value or value == "-":
        return "Direct"
    if value.startswith("/"):
        return "Internal"
    try:
        hostname = (urlsplit(value).hostname or "").lower().rstrip(".")
    except ValueError:
        return "Other"
    if not hostname:
        return "Other"
    if hostname == "lionspath.lcps.k12.va.us":
        return "Internal"
    if hostname == "classroom.google.com":
        return "Google Classroom"
    if hostname == "google.com" or hostname.endswith(".google.com"):
        return "Google Search"
    if hostname == "lcps.k12.va.us" or hostname.endswith(".lcps.k12.va.us"):
        return "LCPS Website"
    return hostname[:255]


def classify_request(
    method: str,
    path: str,
    status_code: int,
    user_agent: str,
) -> tuple[str, bool, bool, ClientClassification]:
    client = classify_user_agent(user_agent)
    asset = is_asset_path(path)
    api = is_api_path(path)
    successful_get = method.upper() == "GET" and 200 <= status_code < 400
    pageview = successful_get and not asset and not api and not client.is_bot

    if client.is_bot:
        request_class = "bot"
    elif asset:
        request_class = "asset"
    elif api:
        request_class = "api"
    elif pageview:
        request_class = "pageview"
    else:
        request_class = "other"
    return request_class, pageview, asset, client

