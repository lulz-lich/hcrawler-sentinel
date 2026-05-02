"""CI-friendly policy gates."""

from __future__ import annotations

from .metrics import severity_counts
from .models import CrawlResult


def evaluate_policy(
    result: CrawlResult,
    *,
    fail_on: str = "high",
    max_errors: int | None = None,
    max_pages: int | None = None,
) -> tuple[bool, list[str]]:
    severity_rank = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    threshold = severity_rank[fail_on]
    counts = severity_counts(result)
    messages: list[str] = []

    for severity, rank in severity_rank.items():
        if rank >= threshold and counts.get(severity, 0) > 0:
            messages.append(f"{counts[severity]} {severity} finding(s) found")

    if max_errors is not None and len(result.errors) > max_errors:
        messages.append(f"Too many crawl errors: {len(result.errors)} > {max_errors}")

    if max_pages is not None and len(result.pages) > max_pages:
        messages.append(f"Too many pages crawled: {len(result.pages)} > {max_pages}")

    return not messages, messages
