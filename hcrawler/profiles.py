"""Profile defaults."""

from __future__ import annotations

from .models import CrawlProfile


def profile_defaults(profile: str) -> dict:
    selected = CrawlProfile(profile)

    if selected == CrawlProfile.SAFE:
        return {"max_pages": 50, "max_depth": 1, "delay": 1.0, "timeout": 10.0, "concurrency": 1}

    if selected == CrawlProfile.BALANCED:
        return {"max_pages": 150, "max_depth": 2, "delay": 0.3, "timeout": 10.0, "concurrency": 5}

    if selected == CrawlProfile.FAST:
        return {"max_pages": 400, "max_depth": 2, "delay": 0.05, "timeout": 6.0, "concurrency": 10}

    if selected == CrawlProfile.DEEP:
        return {"max_pages": 1200, "max_depth": 5, "delay": 0.2, "timeout": 10.0, "concurrency": 8}

    if selected == CrawlProfile.PORTFOLIO:
        return {"max_pages": 120, "max_depth": 2, "delay": 0.15, "timeout": 8.0, "concurrency": 5}

    raise ValueError(f"Unknown profile: {profile}")
