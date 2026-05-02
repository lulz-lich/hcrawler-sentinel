"""Attack surface inventory builder."""

from __future__ import annotations

from urllib.parse import urlparse

from .models import CrawlResult


def build_attack_surface_inventory(result: CrawlResult) -> dict:
    endpoints = []
    forms = []
    pages_by_status: dict[str, int] = {}

    for page in result.pages:
        parsed = urlparse(page.url)
        pages_by_status[str(page.status_code)] = pages_by_status.get(str(page.status_code), 0) + 1
        endpoints.append({
            "url": page.url,
            "path": parsed.path or "/",
            "status_code": page.status_code,
            "risk_score": page.risk_score,
            "content_type": page.content_type,
            "title": page.title,
            "forms_count": page.forms_count,
            "technologies": page.technologies,
        })
        if page.forms_count:
            forms.append({
                "url": page.url,
                "forms_count": page.forms_count,
                "risk_score": page.risk_score,
            })

    return {
        "target": result.start_url,
        "summary": {
            "pages": len(result.pages),
            "links": len(result.links),
            "external_links": len(result.external_links),
            "technologies": len(result.technologies),
            "forms_pages": len(forms),
            "errors": len(result.errors),
        },
        "pages_by_status": pages_by_status,
        "technologies": sorted(result.technologies),
        "endpoints": endpoints,
        "forms": forms,
    }
