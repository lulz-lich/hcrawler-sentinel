"""Console rendering helpers."""

from __future__ import annotations

from colorama import Fore, Style

from .metrics import severity_counts, top_risk_pages
from .models import CrawlResult


def print_sentinel_summary(result: CrawlResult) -> None:
    counts = severity_counts(result)
    print(Fore.LIGHTGREEN_EX + "Sentinel Summary" + Style.RESET_ALL)
    print("-" * 64)
    print(f"Target:          {result.start_url}")
    print(f"Pages:           {len(result.pages)}")
    print(f"Links:           {len(result.links)}")
    print(f"External links:  {len(result.external_links)}")
    print(f"Technologies:    {len(result.technologies)}")
    print(f"Errors:          {len(result.errors)}")
    print()
    print("Findings:")
    for severity in ["critical", "high", "medium", "low", "info"]:
        color = {
            "critical": Fore.RED,
            "high": Fore.LIGHTRED_EX,
            "medium": Fore.YELLOW,
            "low": Fore.CYAN,
            "info": Fore.WHITE,
        }[severity]
        print(f"  {color}{severity:8s}{Style.RESET_ALL}: {counts[severity]}")
    print()
    print("Top risk pages:")
    for page in top_risk_pages(result, limit=5):
        print(f"  risk={page['risk_score']:3d} | {page['url']}")
