"""Synchronous crawler engine."""

from __future__ import annotations

import importlib
import logging
import time
from collections import deque
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser

from .analyzer import (
    analyze_security_headers,
    build_findings,
    count_external_links,
    count_internal_links,
    detect_technologies,
    extract_canonical,
    extract_heading_counts,
    extract_meta_description,
    extract_title,
    severity_weight,
    sha256_text,
)
from .constants import SENSITIVE_PATH_HINTS
from .models import CrawlConfig, CrawlError, CrawlResult, LinkEdge, PageRecord
from .patterns import extract_cnpjs, extract_cpfs, extract_emails, extract_ipv4s, extract_phones, extract_secret_hints
from .robots import load_robots
from .sitemap import fetch_sitemap_urls
from .urltools import absolute_url, is_http_url, looks_like_binary, normalize_start_url, normalize_url, pattern_match, same_domain

logger = logging.getLogger("hcrawler")


class HCrawler:
    """Authorized web crawler with audit and reporting features."""

    def __init__(self, config: CrawlConfig, *, plugins: list[str] | None = None) -> None:
        self.config = config
        self.start_url = normalize_start_url(config.start_url)
        self.start_domain = urlparse(self.start_url).netloc.lower()
        self.result = CrawlResult(start_url=self.start_url)
        self._robots: RobotFileParser | None = None
        self._robots_sitemaps: set[str] = set()
        self.plugins = [self._load_plugin(name) for name in (plugins or [])]

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.user_agent})
        if config.cookies:
            self.session.headers.update({"Cookie": config.cookies})

        if config.respect_robots:
            self._robots, self._robots_sitemaps, error = load_robots(self.start_url, config.user_agent, config.timeout)
            if error:
                self.result.errors.append(CrawlError(f"{urlparse(self.start_url).scheme}://{self.start_domain}/robots.txt", error))

    def _load_plugin(self, name: str):
        module_name = f"hcrawler.plugins.{name}" if "." not in name else name
        return importlib.import_module(module_name)

    def _allowed_url(self, url: str) -> bool:
        if len(url) > self.config.max_url_length:
            return False
        if not is_http_url(url):
            return False
        if looks_like_binary(url):
            return False
        if self.config.same_domain and not same_domain(url, self.start_domain):
            return False
        if self.config.allow_patterns and not pattern_match(url, self.config.allow_patterns):
            return False
        if self.config.deny_patterns and pattern_match(url, self.config.deny_patterns):
            return False
        return True

    def _robots_allowed(self, url: str) -> bool:
        if not self._robots:
            return True
        allowed = self._robots.can_fetch(self.config.user_agent, url)
        if not allowed:
            self.result.robots_disallowed_seen.add(url)
        return allowed

    def _fetch_response(self, url: str) -> requests.Response | None:
        if self.config.respect_robots and not self._robots_allowed(url):
            self.result.errors.append(CrawlError(url, "Blocked by robots.txt policy"))
            return None

        last_error = None
        for attempt in range(self.config.retries + 1):
            try:
                response = self.session.get(url, timeout=self.config.timeout, allow_redirects=True)
                if response.status_code >= 400:
                    self.result.errors.append(CrawlError(url, f"HTTP {response.status_code}"))
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt < self.config.retries:
                    time.sleep(self.config.backoff * (2 ** attempt))
        self.result.errors.append(CrawlError(url, str(last_error)))
        return None

    def _seed_sitemaps(self) -> set[str]:
        sitemap_sources: set[str] = set()
        parsed = urlparse(self.start_url)

        if self.config.use_sitemap:
            sitemap_sources.add(f"{parsed.scheme}://{parsed.netloc}/sitemap.xml")

        if self.config.use_robots_sitemaps:
            sitemap_sources.update(self._robots_sitemaps)

        discovered: set[str] = set()
        for sitemap in sorted(sitemap_sources):
            urls, error = fetch_sitemap_urls(sitemap, user_agent=self.config.user_agent, timeout=self.config.timeout)
            if error:
                self.result.errors.append(CrawlError(sitemap, error))
                continue
            for url in urls:
                normalized = normalize_url(url, include_query_strings=self.config.include_query_strings)
                if self._allowed_url(normalized):
                    discovered.add(normalized)

        self.result.sitemap_urls.update(discovered)
        return discovered

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> tuple[set[str], set[str]]:
        internal: set[str] = set()
        external: set[str] = set()

        for tag in soup.find_all("a", href=True):
            normalized = absolute_url(base_url, tag["href"], include_query_strings=self.config.include_query_strings)

            if not is_http_url(normalized):
                continue

            if same_domain(normalized, self.start_domain):
                if self._allowed_url(normalized):
                    internal.add(normalized)
                self.result.edges.append(LinkEdge(base_url, normalized, False))
            else:
                external.add(normalized)
                self.result.edges.append(LinkEdge(base_url, normalized, True))
                if not self.config.same_domain and self._allowed_url(normalized):
                    internal.add(normalized)

        return internal, external

    def _extract_patterns(self, html: str) -> set[str]:
        secret_hints = extract_secret_hints(html)

        if self.config.collect_emails:
            self.result.emails.update(extract_emails(html))
        if self.config.collect_phones:
            self.result.phones.update(extract_phones(html))
        if self.config.collect_cpfs:
            self.result.cpfs.update(extract_cpfs(html, validate=self.config.validate_documents))
        if self.config.collect_cnpjs:
            self.result.cnpjs.update(extract_cnpjs(html, validate=self.config.validate_documents))
        if self.config.collect_ipv4s:
            self.result.ipv4s.update(extract_ipv4s(html))

        if self.config.audit_mode:
            self.result.secret_hints.update(secret_hints)

        return secret_hints

    def _analyze_page(self, *, url: str, depth: int, response: requests.Response, html: str) -> tuple[PageRecord, set[str]]:
        soup = BeautifulSoup(html, "html.parser")
        secret_hints = self._extract_patterns(html)
        internal_links, external_links = self._extract_links(soup, url) if self.config.collect_links else (set(), set())

        self.result.links.update(internal_links)
        self.result.external_links.update(external_links)

        technologies = detect_technologies(response, soup, html) if self.config.audit_mode else set()
        self.result.technologies.update(technologies)

        security_headers = analyze_security_headers(response) if self.config.audit_mode else {}
        findings, risk_score = build_findings(
            url=url,
            soup=soup,
            response=response,
            security_headers=security_headers,
            secret_hints=secret_hints,
        ) if self.config.audit_mode else ([], 0)

        if self.config.audit_mode:
            for plugin in self.plugins:
                findings.extend(plugin.analyze(url=url, response=response, soup=soup, html=html))

        risk_score = min(risk_score + sum(severity_weight(f.severity) for f in findings if f.id.startswith(("seo.", "a11y.", "privacy."))), 100)

        page = PageRecord(
            url=url,
            status_code=response.status_code,
            depth=depth,
            title=extract_title(soup),
            meta_description=extract_meta_description(soup),
            canonical_url=extract_canonical(soup, url),
            content_type=response.headers.get("content-type", "").lower(),
            response_time_ms=None,
            content_length=len(response.content),
            content_hash=sha256_text(html),
            robots_allowed=True,
            technologies=sorted(technologies),
            forms_count=len(soup.find_all("form")),
            scripts_count=len(soup.find_all("script")),
            images_count=len(soup.find_all("img")),
            internal_links_count=count_internal_links(soup, url),
            external_links_count=count_external_links(soup, url),
            headings=extract_heading_counts(soup),
            security_headers=security_headers,
            findings=findings,
            risk_score=min(risk_score, 100),
        )
        return page, internal_links

    def _check_sensitive_paths(self) -> None:
        if not self.config.sensitive_path_checks or not self.config.audit_mode:
            return

        parsed = urlparse(self.start_url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for hint in SENSITIVE_PATH_HINTS:
            url = f"{base}/{hint}"
            if self.config.respect_robots and not self._robots_allowed(url):
                continue

            try:
                response = self.session.get(url, timeout=self.config.timeout, allow_redirects=False)
            except requests.RequestException as exc:
                self.result.errors.append(CrawlError(url, str(exc)))
                continue

            if response.status_code in {200, 206, 301, 302, 307, 308, 401, 403}:
                self.result.checked_sensitive_paths.append(PageRecord(
                    url=url,
                    status_code=response.status_code,
                    depth=0,
                    content_type=response.headers.get("content-type", "").lower(),
                    content_length=len(response.content),
                    content_hash=sha256_text(response.text[:10000]),
                    risk_score=10 if response.status_code == 200 else 3,
                ))

    def crawl(self) -> CrawlResult:
        started = time.time()
        queue: deque[tuple[str, int]] = deque([(self.start_url, 0)])
        seen: set[str] = set()

        for sitemap_url in sorted(self._seed_sitemaps()):
            queue.append((sitemap_url, 0))

        while queue and len(self.result.pages) < self.config.max_pages:
            url, depth = queue.popleft()
            url = normalize_url(url, include_query_strings=self.config.include_query_strings)

            if url in seen or not self._allowed_url(url):
                continue

            seen.add(url)
            logger.info("Crawling %s", url)
            start = time.perf_counter()
            response = self._fetch_response(url)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

            if response is None:
                continue

            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                self.result.errors.append(CrawlError(url, f"Skipped non-HTML content: {content_type or 'unknown'}"))
                continue

            page, internal_links = self._analyze_page(url=url, depth=depth, response=response, html=response.text)
            page.response_time_ms = elapsed_ms
            self.result.pages.append(page)

            if self.config.collect_links and depth < self.config.max_depth:
                for link in sorted(internal_links):
                    if link not in seen:
                        queue.append((link, depth + 1))

            if self.config.delay > 0:
                time.sleep(self.config.delay)

        self._check_sensitive_paths()
        self.result.metadata = {
            "duration_seconds": round(time.time() - started, 2),
            "page_budget": self.config.max_pages,
            "max_depth": self.config.max_depth,
            "tag": self.config.tag,
            "engine": "sync",
        }
        return self.result
