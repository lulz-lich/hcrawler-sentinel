"""Console rendering helpers."""

from __future__ import annotations

from colorama import Fore, Style

from .metrics import severity_counts, top_risk_pages
from .models import CrawlResult
from .theme import NEON_CYAN, NEON_GREEN, NEON_MAGENTA, NEON_RED, NEON_YELLOW, RESET


def _bar(value: int, *, width: int = 18, cap: int = 100) -> str:
    filled = max(0, min(width, int(round((value / cap) * width)))) if cap else 0
    return "█" * filled + "░" * (width - filled)


def print_sentinel_summary(result: CrawlResult) -> None:
    counts = severity_counts(result)
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

    print(NEON_CYAN + "╔" + "═" * 78 + "╗" + RESET)
    print(NEON_CYAN + "║" + RESET + NEON_GREEN + " SENTINEL SUMMARY ".center(78) + RESET + NEON_CYAN + "║" + RESET)
    print(NEON_CYAN + "╠" + "═" * 78 + "╣" + RESET)
    for key, value in rows:
        content = f" {key:<15} :: {value}"
        print(NEON_CYAN + "║" + RESET + content.ljust(78) + NEON_CYAN + "║" + RESET)
    print(NEON_CYAN + "╚" + "═" * 78 + "╝" + RESET)
    print()

    print(NEON_MAGENTA + "findings heatmap" + RESET)
    for severity in ["critical", "high", "medium", "low", "info"]:
        color = {
            "critical": NEON_RED,
            "high": Fore.LIGHTRED_EX,
            "medium": NEON_YELLOW,
            "low": Fore.CYAN,
            "info": Fore.WHITE,
        }[severity]
        print(f"  {color}{severity:8s}{RESET} {counts[severity]:3d}  {_bar(counts[severity], cap=max(max(counts.values()) or 1, 6))}")
    print()

    print(NEON_MAGENTA + "top risk pages" + RESET)
    pages = top_risk_pages(result, limit=5)
    if not pages:
        print("  no page data available")
        return
    for idx, page in enumerate(pages, start=1):
        risk_bar = _bar(page["risk_score"], cap=100)
        print(f"  {idx:02d}. risk={page['risk_score']:3d} {risk_bar}  {page['url']}")
