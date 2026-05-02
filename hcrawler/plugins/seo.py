"""SEO quality plugin."""

from __future__ import annotations

from hcrawler.models import Finding


def analyze(*, url, response, soup, html):
    findings = []

    if not soup.title or not soup.title.string:
        findings.append(Finding(
            "seo.missing_title",
            "Missing page title",
            "low",
            "The page has no HTML title.",
            url,
            "Add a descriptive title tag.",
            url,
        ))

    if not soup.find("meta", attrs={"name": "description"}):
        findings.append(Finding(
            "seo.missing_meta_description",
            "Missing meta description",
            "info",
            "The page has no meta description.",
            url,
            "Add a concise meta description.",
            url,
        ))

    h1_count = len(soup.find_all("h1"))
    if h1_count == 0:
        findings.append(Finding(
            "seo.missing_h1",
            "Missing H1",
            "info",
            "The page has no H1 heading.",
            url,
            "Add one clear H1 heading.",
            url,
        ))
    elif h1_count > 1:
        findings.append(Finding(
            "seo.multiple_h1",
            "Multiple H1 headings",
            "info",
            "The page has multiple H1 headings.",
            str(h1_count),
            "Use a single main H1 where appropriate.",
            url,
        ))

    return findings
