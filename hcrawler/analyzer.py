"""Page analysis helpers."""

from __future__ import annotations

import hashlib
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from requests import Response

from .constants import SECURITY_HEADERS
from .models import Finding


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def extract_title(soup: BeautifulSoup) -> str | None:
    return " ".join(soup.title.string.split()) if soup.title and soup.title.string else None


def extract_meta_description(soup: BeautifulSoup) -> str | None:
    tag = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if tag and tag.get("content"):
        return " ".join(tag["content"].split())
    return None


def extract_canonical(soup: BeautifulSoup, base_url: str) -> str | None:
    tag = soup.find("link", rel=lambda rel: rel and "canonical" in rel)
    if tag and tag.get("href"):
        return urljoin(base_url, tag["href"])
    return None


def extract_heading_counts(soup: BeautifulSoup) -> dict[str, int]:
    return {tag: len(soup.find_all(tag)) for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]}


def analyze_security_headers(response: Response) -> dict[str, bool]:
    headers = {key.lower() for key in response.headers}
    return {header: header in headers for header in SECURITY_HEADERS}


def detect_technologies(response: Response, soup: BeautifulSoup, html: str) -> set[str]:
    technologies: set[str] = set()
    headers = {key.lower(): value.lower() for key, value in response.headers.items()}
    lower = html.lower()
    combined = lower + "\n" + "\n".join(f"{k}: {v}" for k, v in headers.items())

    for header_name, label in [
        ("server", "Server"),
        ("x-powered-by", "X-Powered-By"),
        ("via", "Via"),
        ("x-generator", "X-Generator"),
    ]:
        if headers.get(header_name):
            technologies.add(f"{label}: {headers[header_name]}")

    for generator in soup.find_all("meta", attrs={"name": re.compile("^generator$", re.I)}):
        if generator.get("content"):
            technologies.add(f"Generator: {generator['content']}")

    signatures = {
        "WordPress": ["wp-content", "wp-includes"],
        "WooCommerce": ["woocommerce"],
        "Drupal": ["drupal-settings-json", "/sites/default/"],
        "Joomla": ["content=\"joomla", "/media/system/js/"],
        "React": ["__react_devtools_global_hook__", "react-dom", "react.production.min"],
        "Next.js": ["_next/static", "__next_data__"],
        "Vue": ["vue.js", "__vue__", "data-v-"],
        "Nuxt": ["__nuxt__", "/_nuxt/"],
        "Angular": ["ng-version", "angular.js", "ng-app"],
        "Svelte": ["svelte"],
        "Bootstrap": ["bootstrap.min.css", "bootstrap.css", "bootstrap.bundle"],
        "Tailwind": ["tailwind", "tw-"],
        "jQuery": ["jquery.min.js", "jquery.js"],
        "Laravel": ["laravel_session", "x-csrf-token"],
        "Django": ["csrftoken", "django"],
        "Flask": ["werkzeug", "flask"],
        "Express": ["x-powered-by: express"],
        "Nginx": ["server: nginx"],
        "Apache": ["server: apache"],
        "Cloudflare": ["cf-ray", "__cf_bm", "server: cloudflare"],
        "Vercel": ["x-vercel-id", "server: vercel"],
        "Netlify": ["x-nf-request-id", "server: netlify"],
        "Shopify": ["cdn.shopify.com", "x-shopify"],
        "Google Tag Manager": ["googletagmanager.com", "gtm.js"],
        "Google Analytics": ["google-analytics.com", "gtag("],
        "Microsoft Clarity": ["clarity.ms"],
        "Hotjar": ["hotjar.com"],
    }

    for name, markers in signatures.items():
        if any(marker.lower() in combined for marker in markers):
            technologies.add(name)

    return technologies


def count_external_links(soup: BeautifulSoup, page_url: str) -> int:
    domain = urlparse(page_url).netloc.lower()
    count = 0
    for tag in soup.find_all("a", href=True):
        href = urljoin(page_url, tag["href"])
        parsed = urlparse(href)
        if parsed.scheme in {"http", "https"} and parsed.netloc.lower() != domain:
            count += 1
    return count


def count_internal_links(soup: BeautifulSoup, page_url: str) -> int:
    domain = urlparse(page_url).netloc.lower()
    count = 0
    for tag in soup.find_all("a", href=True):
        href = urljoin(page_url, tag["href"])
        parsed = urlparse(href)
        if parsed.scheme in {"http", "https"} and parsed.netloc.lower() == domain:
            count += 1
    return count


def severity_weight(severity: str) -> int:
    return {"info": 1, "low": 5, "medium": 12, "high": 25, "critical": 40}.get(severity, 1)


def build_findings(
    *,
    url: str,
    soup: BeautifulSoup,
    response: Response,
    security_headers: dict[str, bool],
    secret_hints: set[str],
) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    parsed = urlparse(url)

    def add(id_: str, title: str, severity: str, description: str, evidence: str | None, recommendation: str) -> None:
        findings.append(Finding(id_, title, severity, description, evidence, recommendation, url))

    if parsed.scheme != "https":
        add(
            "transport.no_https",
            "Page is not using HTTPS",
            "high",
            "The page was requested over plain HTTP.",
            url,
            "Serve the application over HTTPS and redirect HTTP to HTTPS.",
        )

    missing_headers = [header for header, present in security_headers.items() if not present]
    if missing_headers:
        add(
            "headers.missing_security_headers",
            "Missing security headers",
            "medium",
            "One or more common browser security headers are missing.",
            ", ".join(missing_headers),
            "Configure security headers according to the application context.",
        )

    forms = soup.find_all("form")
    if forms:
        add(
            "surface.forms_detected",
            "Forms detected",
            "info",
            "HTML forms were found on the page.",
            f"{len(forms)} form(s)",
            "Review validation, CSRF protection, authentication, and authorization.",
        )

    password_inputs = soup.find_all("input", attrs={"type": re.compile("^password$", re.I)})
    if password_inputs and parsed.scheme != "https":
        add(
            "forms.password_over_http",
            "Password input over HTTP",
            "critical",
            "A password input was found on a page not using HTTPS.",
            url,
            "Never serve login forms over HTTP.",
        )

    if secret_hints:
        add(
            "exposure.secret_keywords",
            "Potential secret-related keywords found",
            "medium",
            "The page source contains words commonly associated with secrets or credentials.",
            ", ".join(sorted(secret_hints)),
            "Manually verify whether real secrets are exposed and rotate if necessary.",
        )

    if len(soup.find_all("script")) > 20:
        add(
            "surface.high_script_count",
            "High number of script tags",
            "low",
            "The page has many script tags, increasing client-side complexity.",
            str(len(soup.find_all("script"))),
            "Review third-party scripts and reduce unnecessary client-side code.",
        )

    mixed_content = []
    if parsed.scheme == "https":
        for tag in soup.find_all(src=True):
            if str(tag.get("src", "")).startswith("http://"):
                mixed_content.append(tag.get("src"))
        for tag in soup.find_all(href=True):
            if str(tag.get("href", "")).startswith("http://"):
                mixed_content.append(tag.get("href"))
    if mixed_content:
        add(
            "transport.mixed_content",
            "Potential mixed content",
            "medium",
            "HTTPS page references HTTP resources.",
            str(mixed_content[0]),
            "Load subresources over HTTPS.",
        )

    score = min(sum(severity_weight(finding.severity) for finding in findings), 100)
    return findings, score
