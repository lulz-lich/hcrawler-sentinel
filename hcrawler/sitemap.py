"""Sitemap parser."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import requests


def fetch_sitemap_urls(url: str, *, user_agent: str, timeout: float, nested_limit: int = 20) -> tuple[set[str], str | None]:
    try:
        response = requests.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
        if response.status_code >= 400:
            return set(), f"HTTP {response.status_code}"
    except requests.RequestException as exc:
        return set(), str(exc)

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as exc:
        return set(), f"Invalid XML: {exc}"

    urls: set[str] = set()
    nested_sitemaps: set[str] = set()

    for elem in root.iter():
        if elem.tag.endswith("loc") and elem.text:
            value = elem.text.strip()
            if value.endswith(".xml"):
                nested_sitemaps.add(value)
            else:
                urls.add(value)

    for nested in sorted(nested_sitemaps)[:nested_limit]:
        child_urls, _error = fetch_sitemap_urls(nested, user_agent=user_agent, timeout=timeout, nested_limit=0)
        urls.update(child_urls)

    return urls, None
