"""Dataclasses used by HCrawler Sentinel."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .constants import DEFAULT_USER_AGENT


class CrawlProfile(str, Enum):
    SAFE = "safe"
    BALANCED = "balanced"
    FAST = "fast"
    DEEP = "deep"
    PORTFOLIO = "portfolio"


@dataclass(slots=True)
class CrawlConfig:
    start_url: str
    user_agent: str = DEFAULT_USER_AGENT
    cookies: str | None = None
    timeout: float = 10.0
    delay: float = 0.3
    max_pages: int = 150
    max_depth: int = 2
    concurrency: int = 5
    retries: int = 2
    backoff: float = 0.5
    same_domain: bool = True
    respect_robots: bool = True
    collect_links: bool = True
    collect_emails: bool = False
    collect_phones: bool = False
    collect_cpfs: bool = False
    collect_cnpjs: bool = False
    collect_ipv4s: bool = False
    validate_documents: bool = True
    include_query_strings: bool = False
    audit_mode: bool = False
    use_sitemap: bool = False
    use_robots_sitemaps: bool = True
    allow_patterns: list[str] = field(default_factory=list)
    deny_patterns: list[str] = field(default_factory=list)
    sensitive_path_checks: bool = False
    max_url_length: int = 2048
    tag: str | None = None


@dataclass(slots=True)
class Finding:
    id: str
    title: str
    severity: str
    description: str
    evidence: str | None = None
    recommendation: str | None = None
    url: str | None = None


@dataclass(slots=True)
class PageRecord:
    url: str
    status_code: int
    depth: int
    method: str = "GET"
    title: str | None = None
    meta_description: str | None = None
    canonical_url: str | None = None
    content_type: str | None = None
    response_time_ms: float | None = None
    content_length: int | None = None
    content_hash: str | None = None
    robots_allowed: bool = True
    technologies: list[str] = field(default_factory=list)
    forms_count: int = 0
    scripts_count: int = 0
    images_count: int = 0
    internal_links_count: int = 0
    external_links_count: int = 0
    headings: dict[str, int] = field(default_factory=dict)
    security_headers: dict[str, bool] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    risk_score: int = 0


@dataclass(slots=True)
class LinkEdge:
    source: str
    target: str
    external: bool = False


@dataclass(slots=True)
class CrawlError:
    url: str
    error: str


@dataclass
class CrawlResult:
    start_url: str
    pages: list[PageRecord] = field(default_factory=list)
    links: set[str] = field(default_factory=set)
    external_links: set[str] = field(default_factory=set)
    edges: list[LinkEdge] = field(default_factory=list)
    sitemap_urls: set[str] = field(default_factory=set)
    robots_disallowed_seen: set[str] = field(default_factory=set)
    emails: set[str] = field(default_factory=set)
    phones: set[str] = field(default_factory=set)
    cpfs: set[str] = field(default_factory=set)
    cnpjs: set[str] = field(default_factory=set)
    ipv4s: set[str] = field(default_factory=set)
    secret_hints: set[str] = field(default_factory=set)
    technologies: set[str] = field(default_factory=set)
    checked_sensitive_paths: list[PageRecord] = field(default_factory=list)
    errors: list[CrawlError] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def all_findings(self) -> list[Finding]:
        findings: list[Finding] = []
        for page in self.pages:
            findings.extend(page.findings)
        return findings

    def to_dict(self) -> dict:
        data = asdict(self)
        for key in (
            "links",
            "external_links",
            "sitemap_urls",
            "robots_disallowed_seen",
            "emails",
            "phones",
            "cpfs",
            "cnpjs",
            "ipv4s",
            "secret_hints",
            "technologies",
        ):
            data[key] = sorted(data[key])
        return data
