"""Report diffing."""

from __future__ import annotations

import json
from pathlib import Path


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_reports(old_path: Path, new_path: Path) -> dict:
    old = load_report(old_path)
    new = load_report(new_path)

    old_pages = {page["url"]: page for page in old.get("pages", [])}
    new_pages = {page["url"]: page for page in new.get("pages", [])}

    old_urls = set(old_pages)
    new_urls = set(new_pages)

    changed = sorted(
        url for url in old_urls & new_urls
        if old_pages[url].get("content_hash") and new_pages[url].get("content_hash")
        and old_pages[url].get("content_hash") != new_pages[url].get("content_hash")
    )

    old_findings = {(p["url"], f["id"], f.get("evidence")) for p in old.get("pages", []) for f in p.get("findings", [])}
    new_findings = {(p["url"], f["id"], f.get("evidence")) for p in new.get("pages", []) for f in p.get("findings", [])}

    return {
        "added_pages": sorted(new_urls - old_urls),
        "removed_pages": sorted(old_urls - new_urls),
        "changed_pages": changed,
        "added_technologies": sorted(set(new.get("technologies", [])) - set(old.get("technologies", []))),
        "removed_technologies": sorted(set(old.get("technologies", [])) - set(new.get("technologies", []))),
        "added_emails": sorted(set(new.get("emails", [])) - set(old.get("emails", []))),
        "removed_emails": sorted(set(old.get("emails", [])) - set(new.get("emails", []))),
        "added_findings": sorted([list(item) for item in new_findings - old_findings]),
        "removed_findings": sorted([list(item) for item in old_findings - new_findings]),
    }
