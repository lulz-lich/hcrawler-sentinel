"""Basic accessibility plugin."""

from __future__ import annotations

from hcrawler.models import Finding


def analyze(*, url, response, soup, html):
    findings = []
    images = soup.find_all("img")
    missing_alt = [img for img in images if not img.get("alt")]

    if missing_alt:
        findings.append(Finding(
            "a11y.images_missing_alt",
            "Images missing alt text",
            "low",
            "Some images do not include alt text.",
            f"{len(missing_alt)} of {len(images)} image(s)",
            "Add meaningful alt text or empty alt for decorative images.",
            url,
        ))

    html_tag = soup.find("html")
    if html_tag and not html_tag.get("lang"):
        findings.append(Finding(
            "a11y.missing_lang",
            "Missing HTML lang attribute",
            "info",
            "The document root does not declare a language.",
            url,
            "Add a lang attribute to the html tag.",
            url,
        ))

    return findings
