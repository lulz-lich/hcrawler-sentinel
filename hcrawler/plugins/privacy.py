"""Privacy weak-signal plugin."""

from __future__ import annotations

from hcrawler.models import Finding

TRACKING_HINTS = {
    "google-analytics.com": "Google Analytics",
    "googletagmanager.com": "Google Tag Manager",
    "facebook.net": "Meta/Facebook",
    "hotjar.com": "Hotjar",
    "clarity.ms": "Microsoft Clarity",
}


def analyze(*, url, response, soup, html):
    lower = html.lower()
    detected = [name for marker, name in TRACKING_HINTS.items() if marker in lower]

    if not detected:
        return []

    return [Finding(
        "privacy.third_party_tracking",
        "Third-party tracking scripts detected",
        "info",
        "Common third-party analytics or tracking scripts were found.",
        ", ".join(sorted(set(detected))),
        "Review privacy policy, consent flow, and necessity of third-party tracking.",
        url,
    )]
