"""robots.txt helpers."""

from __future__ import annotations

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests


def load_robots(start_url: str, user_agent: str, timeout: float) -> tuple[RobotFileParser | None, set[str], str | None]:
    parsed = urlparse(start_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)
    sitemaps: set[str] = set()

    try:
        response = requests.get(robots_url, headers={"User-Agent": user_agent}, timeout=timeout)
        if response.status_code >= 400:
            return None, sitemaps, f"robots.txt HTTP {response.status_code}"

        parser.parse(response.text.splitlines())
        for line in response.text.splitlines():
            if line.lower().startswith("sitemap:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    sitemaps.add(value)
        return parser, sitemaps, None
    except requests.RequestException as exc:
        return None, sitemaps, str(exc)
