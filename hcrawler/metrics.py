"""Metrics and baseline helpers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .models import CrawlResult

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]


def severity_counts(result: CrawlResult) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for page in result.pages:
        for finding in page.findings:
            counter[finding.severity] += 1
    return {severity: counter.get(severity, 0) for severity in SEVERITY_ORDER}


def top_risk_pages(result: CrawlResult, *, limit: int = 10) -> list[dict]:
    pages = sorted(result.pages, key=lambda page: page.risk_score, reverse=True)
    return [
        {
            "url": page.url,
            "risk_score": page.risk_score,
            "status_code": page.status_code,
            "title": page.title,
            "findings": len(page.findings),
        }
        for page in pages[:limit]
    ]


def executive_summary(result: CrawlResult) -> dict:
    return {
        "start_url": result.start_url,
        "pages_crawled": len(result.pages),
        "links_found": len(result.links),
        "external_links_found": len(result.external_links),
        "technologies_found": len(result.technologies),
        "emails_found": len(result.emails),
        "phones_found": len(result.phones),
        "ipv4s_found": len(result.ipv4s),
        "secret_hints_found": len(result.secret_hints),
        "errors": len(result.errors),
        "severity_counts": severity_counts(result),
        "top_risk_pages": top_risk_pages(result),
        "duration_seconds": result.metadata.get("duration_seconds"),
        "engine": result.metadata.get("engine"),
    }


def write_baseline(result: CrawlResult, path: Path) -> None:
    baseline = {
        "start_url": result.start_url,
        "pages": sorted(page.url for page in result.pages),
        "technologies": sorted(result.technologies),
        "emails": sorted(result.emails),
        "findings": sorted(
            {
                "url": page.url,
                "id": finding.id,
                "severity": finding.severity,
                "evidence": finding.evidence,
            }
            for page in result.pages
            for finding in page.findings
        ),
    }
    path.write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding="utf-8")


def compare_baseline(result: CrawlResult, path: Path) -> dict:
    baseline = json.loads(path.read_text(encoding="utf-8"))
    current_pages = {page.url for page in result.pages}
    baseline_pages = set(baseline.get("pages", []))

    current_tech = set(result.technologies)
    baseline_tech = set(baseline.get("technologies", []))

    current_findings = {
        (page.url, finding.id, finding.severity, finding.evidence)
        for page in result.pages
        for finding in page.findings
    }
    baseline_findings = {
        (item.get("url"), item.get("id"), item.get("severity"), item.get("evidence"))
        for item in baseline.get("findings", [])
    }

    return {
        "added_pages": sorted(current_pages - baseline_pages),
        "removed_pages": sorted(baseline_pages - current_pages),
        "added_technologies": sorted(current_tech - baseline_tech),
        "removed_technologies": sorted(baseline_tech - current_tech),
        "new_findings": sorted([list(item) for item in current_findings - baseline_findings]),
        "resolved_findings": sorted([list(item) for item in baseline_findings - current_findings]),
    }
