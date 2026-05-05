"""Console rendering helpers."""

from __future__ import annotations

from colorama import Fore

from .metrics import severity_counts, top_risk_pages
from .models import CrawlResult
from .theme import (
    NEON_CYAN,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_RED,
    NEON_YELLOW,
    RESET,
    contextual_art,
    contextual_result_art,
)


def _bar(value: int, *, width: int = 22, cap: int = 100) -> str:
    if cap <= 0:
        return "░" * width
    filled = max(0, min(width, int(round((value / cap) * width))))
    return "█" * filled + "░" * (width - filled)


def print_sentinel_summary(result: CrawlResult, *, effects: bool = True) -> None:
    counts = severity_counts(result)

    contextual_result_art(result, enabled=effects)

    rows = [
        ("Target", result.start_url),
        ("Pages", len(result.pages)),
        ("Links", len(result.links)),
        ("External links", len(result.external_links)),
        ("Technologies", len(result.technologies)),
        ("Errors", len(result.errors)),
        ("Engine", result.metadata.get("engine", "unknown")),
        ("Duration", f"{result.metadata.get('duration_seconds', '?')}s"),
    ]

    print(NEON_CYAN + "╔" + "═" * 86 + "╗" + RESET)
    print(NEON_CYAN + "║" + RESET + NEON_GREEN + " SENTINEL CRAWL SUMMARY ".center(86) + RESET + NEON_CYAN + "║" + RESET)
    print(NEON_CYAN + "╠" + "═" * 86 + "╣" + RESET)
    for key, value in rows:
        content = f" {key:<18} :: {value}"
        print(NEON_CYAN + "║" + RESET + content.ljust(86) + NEON_CYAN + "║" + RESET)
    print(NEON_CYAN + "╚" + "═" * 86 + "╝" + RESET)
    print()

    print(NEON_MAGENTA + "finding severity heatmap" + RESET)
    max_count = max(max(counts.values()) if counts else 1, 6)
    for severity in ["critical", "high", "medium", "low", "info"]:
        color = {
            "critical": NEON_RED,
            "high": Fore.LIGHTRED_EX,
            "medium": NEON_YELLOW,
            "low": Fore.CYAN,
            "info": Fore.WHITE,
        }[severity]
        print(f"  {color}{severity:8s}{RESET} {counts[severity]:3d}  {_bar(counts[severity], cap=max_count)}")
    print()

    print(NEON_MAGENTA + "top risk pages" + RESET)
    pages = top_risk_pages(result, limit=7)
    if not pages:
        print("  no page data available")
        return

    for idx, page in enumerate(pages, start=1):
        risk_bar = _bar(page["risk_score"], cap=100)
        print(f"  {idx:02d}. risk={page['risk_score']:3d} {risk_bar}  {page['url']}")

    if result.checked_sensitive_paths:
        print()
        contextual_art("http", enabled=effects, chance=1.0)
        print(NEON_YELLOW + f"sensitive path hits: {len(result.checked_sensitive_paths)}" + RESET)