"""URL helpers."""

from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urldefrag, urljoin, urlparse, urlunparse

from .constants import BINARY_EXTENSIONS


def normalize_start_url(url: str) -> str:
    parsed = urlparse(url)
    return url if parsed.scheme else "https://" + url


def normalize_url(url: str, *, include_query_strings: bool = False) -> str:
    clean, _fragment = urldefrag(url.strip())
    parsed = urlparse(clean)

    if parsed.scheme not in {"http", "https"}:
        return clean

    parsed = parsed._replace(scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower())

    if include_query_strings:
        query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))
        parsed = parsed._replace(query=query)
    else:
        parsed = parsed._replace(query="")

    return urlunparse(parsed).rstrip("/")


def absolute_url(base: str, href: str, *, include_query_strings: bool = False) -> str:
    return normalize_url(urljoin(base, href), include_query_strings=include_query_strings)


def same_domain(url: str, domain: str) -> bool:
    return urlparse(url).netloc.lower() == domain.lower()


def is_http_url(url: str) -> bool:
    return urlparse(url).scheme in {"http", "https"}


def pattern_match(url: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, url) for pattern in patterns)


def looks_like_binary(url: str) -> bool:
    ext_pattern = "|".join(re.escape(ext) for ext in BINARY_EXTENSIONS)
    return bool(re.search(rf"\.({ext_pattern})(?:$|\?)", url, re.I))
