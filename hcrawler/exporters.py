"""Report exporters."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

from .inventory import build_attack_surface_inventory
from .metrics import executive_summary
from .models import CrawlResult


def export_json(result: CrawlResult, output: Path) -> None:
    output.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def export_summary_json(result: CrawlResult, output: Path) -> None:
    output.write_text(json.dumps(executive_summary(result), indent=2, ensure_ascii=False), encoding="utf-8")


def export_inventory_json(result: CrawlResult, output: Path) -> None:
    output.write_text(json.dumps(build_attack_surface_inventory(result), indent=2, ensure_ascii=False), encoding="utf-8")


def export_txt(result: CrawlResult, output: Path) -> None:
    data = result.to_dict()
    with output.open("w", encoding="utf-8") as file:
        file.write("HCrawler Sentinel Report\n")
        file.write("=" * 80 + "\n\n")
        file.write(f"Start URL: {result.start_url}\n")
        file.write(f"Duration: {data.get('metadata', {}).get('duration_seconds')}s\n\n")
        file.write("Summary\n-------\n")
        for label, key in [
            ("Pages", "pages"), ("Links", "links"), ("External links", "external_links"),
            ("Technologies", "technologies"), ("Emails", "emails"), ("Phones", "phones"),
            ("IPv4s", "ipv4s"), ("Secret hints", "secret_hints"), ("Errors", "errors"),
        ]:
            file.write(f"{label}: {len(data[key])}\n")
        file.write("\nPages\n-----\n")
        for page in data["pages"]:
            file.write(f"{page['status_code']} | risk={page['risk_score']} | depth={page['depth']} | {page['url']}\n")
            if page.get("title"):
                file.write(f"  title: {page['title']}\n")
            for finding in page.get("findings", []):
                file.write(f"  [{finding['severity']}] {finding['title']} - {finding.get('evidence') or ''}\n")
            file.write("\n")


def export_csv(result: CrawlResult, output: Path) -> None:
    data = result.to_dict()
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["category", "value"])
        for page in data["pages"]:
            writer.writerow(["page", json.dumps(page, ensure_ascii=False)])
        for category in (
            "links", "external_links", "sitemap_urls", "robots_disallowed_seen",
            "emails", "phones", "cpfs", "cnpjs", "ipv4s", "secret_hints", "technologies"
        ):
            for value in data[category]:
                writer.writerow([category, value])
        for error in data["errors"]:
            writer.writerow(["error", json.dumps(error, ensure_ascii=False)])


def export_markdown(result: CrawlResult, output: Path) -> None:
    data = result.to_dict()
    lines = [
        "# HCrawler Sentinel Report",
        "",
        f"Start URL: `{result.start_url}`",
        "",
        "## Summary",
        "",
        f"- Pages crawled: {len(data['pages'])}",
        f"- Links found: {len(data['links'])}",
        f"- External links: {len(data['external_links'])}",
        f"- Technologies: {len(data['technologies'])}",
        f"- Emails: {len(data['emails'])}",
        f"- Phones: {len(data['phones'])}",
        f"- IPv4s: {len(data['ipv4s'])}",
        f"- Secret hints: {len(data['secret_hints'])}",
        f"- Errors: {len(data['errors'])}",
        "",
        "## Pages",
        "",
        "| Status | Risk | Depth | URL | Title | Findings |",
        "|---:|---:|---:|---|---|---|",
    ]
    for page in data["pages"]:
        findings = "<br>".join(f"{f['severity']}: {f['title']}" for f in page.get("findings", []))
        title = (page.get("title") or "").replace("|", "\\|")
        lines.append(f"| {page['status_code']} | {page['risk_score']} | {page['depth']} | `{page['url']}` | {title} | {findings} |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_graphviz(result: CrawlResult, output: Path) -> None:
    data = result.to_dict()
    lines = ["digraph HCrawler {", '  rankdir="LR";', '  node [shape=box, style=rounded];']
    for edge in data["edges"]:
        color = "gray" if edge["external"] else "black"
        lines.append(f'  "{edge["source"]}" -> "{edge["target"]}" [color="{color}"];')
    lines.append("}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_sarif(result: CrawlResult, output: Path) -> None:
    rules = {}
    results = []
    for page in result.pages:
        for finding in page.findings:
            rules[finding.id] = {
                "id": finding.id,
                "name": finding.title,
                "shortDescription": {"text": finding.title},
                "fullDescription": {"text": finding.description},
                "help": {"text": finding.recommendation or ""},
            }
            level = {"info": "note", "low": "warning", "medium": "warning", "high": "error", "critical": "error"}.get(finding.severity, "note")
            results.append({
                "ruleId": finding.id,
                "level": level,
                "message": {"text": f"{finding.title}: {finding.evidence or ''}"},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": finding.url or page.url}}}],
            })

    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {"driver": {"name": "HCrawler Sentinel", "rules": list(rules.values())}},
            "results": results,
        }],
    }
    output.write_text(json.dumps(sarif, indent=2, ensure_ascii=False), encoding="utf-8")


def export_sqlite(result: CrawlResult, output: Path) -> None:
    data = result.to_dict()
    conn = sqlite3.connect(output)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS pages")
    cur.execute("DROP TABLE IF EXISTS findings")
    cur.execute("DROP TABLE IF EXISTS links")
    cur.execute("CREATE TABLE pages (url TEXT PRIMARY KEY, status_code INTEGER, depth INTEGER, title TEXT, risk_score INTEGER, content_hash TEXT)")
    cur.execute("CREATE TABLE findings (url TEXT, id TEXT, title TEXT, severity TEXT, evidence TEXT, recommendation TEXT)")
    cur.execute("CREATE TABLE links (source TEXT, target TEXT, external INTEGER)")
    for page in data["pages"]:
        cur.execute("INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?, ?, ?)", (
            page["url"], page["status_code"], page["depth"], page.get("title"), page["risk_score"], page.get("content_hash")
        ))
        for finding in page.get("findings", []):
            cur.execute("INSERT INTO findings VALUES (?, ?, ?, ?, ?, ?)", (
                page["url"], finding["id"], finding["title"], finding["severity"], finding.get("evidence"), finding.get("recommendation")
            ))
    for edge in data["edges"]:
        cur.execute("INSERT INTO links VALUES (?, ?, ?)", (edge["source"], edge["target"], int(edge["external"])))
    conn.commit()
    conn.close()


def export_junit(result: CrawlResult, output: Path) -> None:
    failures = []
    tests = 0
    for page in result.pages:
        for finding in page.findings:
            tests += 1
            if finding.severity in {"critical", "high", "medium"}:
                failures.append((page, finding))

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<testsuite name="HCrawler" tests="{tests}" failures="{len(failures)}">',
    ]
    for page in result.pages:
        for finding in page.findings:
            classname = finding.id.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            name = page.url.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            xml.append(f'  <testcase classname="{classname}" name="{name}">')
            if finding.severity in {"critical", "high", "medium"}:
                message = (finding.title + ": " + (finding.evidence or "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                xml.append(f'    <failure message="{message}">{message}</failure>')
            xml.append("  </testcase>")
    xml.append("</testsuite>")
    output.write_text("\n".join(xml) + "\n", encoding="utf-8")


def export_html(result: CrawlResult, output: Path) -> None:
    data = result.to_dict()

    def esc(value: object) -> str:
        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    page_cards = ""
    for page in data["pages"]:
        finding_items = "".join(
            f"<li><b>{esc(f['severity'])}</b>: {esc(f['title'])}<br><small>{esc(f.get('evidence') or '')}</small></li>"
            for f in page.get("findings", [])
        ) or "<li>No findings</li>"
        page_cards += f"""
        <section class="card">
          <div class="row">
            <span class="badge">HTTP {esc(page['status_code'])}</span>
            <span class="badge risk">Risk {esc(page['risk_score'])}</span>
            <span class="badge">Depth {esc(page['depth'])}</span>
          </div>
          <h3>{esc(page.get('title') or 'Untitled')}</h3>
          <p><code>{esc(page['url'])}</code></p>
          <p>{esc(page.get('meta_description') or '')}</p>
          <ul>{finding_items}</ul>
        </section>
        """

    tech_items = "".join(f"<li>{esc(item)}</li>" for item in data["technologies"]) or "<li>None</li>"

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>HCrawler Sentinel Report</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: #0d1117; color: #e6edf3; }}
    header {{ padding: 2rem; background: linear-gradient(135deg, #111827, #0d1117); border-bottom: 1px solid #30363d; }}
    main {{ max-width: 1180px; margin: auto; padding: 2rem; }}
    h1, h2 {{ color: #7ee787; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; }}
    .metric, .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 1rem; box-shadow: 0 10px 30px rgba(0,0,0,.25); }}
    .metric strong {{ display: block; font-size: 2rem; color: #7ee787; }}
    .card {{ margin: 1rem 0; }}
    .row {{ display: flex; gap: .5rem; flex-wrap: wrap; }}
    .badge {{ background: #21262d; border: 1px solid #30363d; border-radius: 999px; padding: .25rem .65rem; font-size: .85rem; }}
    .risk {{ color: #ffd33d; }}
    code {{ color: #ffa657; overflow-wrap: anywhere; }}
    small {{ color: #8b949e; }}
  </style>
</head>
<body>
<header>
  <h1>HCrawler Sentinel Report</h1>
  <p>Authorized discovery report for <code>{esc(result.start_url)}</code></p>
</header>
<main>
  <section class="grid">
    <div class="metric"><strong>{len(data["pages"])}</strong>Pages</div>
    <div class="metric"><strong>{len(data["links"])}</strong>Links</div>
    <div class="metric"><strong>{len(data["external_links"])}</strong>External</div>
    <div class="metric"><strong>{len(data["technologies"])}</strong>Tech</div>
    <div class="metric"><strong>{len(data["emails"])}</strong>Emails</div>
    <div class="metric"><strong>{len(data["errors"])}</strong>Errors</div>
  </section>
  <h2>Technologies</h2>
  <section class="card"><ul>{tech_items}</ul></section>
  <h2>Pages</h2>
  {page_cards}
</main>
</body>
</html>
"""
    output.write_text(html, encoding="utf-8")


def export_result(result: CrawlResult, output: Path, output_format: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    dispatch = {
        "json": export_json,
        "csv": export_csv,
        "txt": export_txt,
        "md": export_markdown,
        "html": export_html,
        "sarif": export_sarif,
        "sqlite": export_sqlite,
        "dot": export_graphviz,
        "summary": export_summary_json,
        "junit": export_junit,
        "inventory": export_inventory_json,
    }
    if output_format not in dispatch:
        raise ValueError(f"Unsupported output format: {output_format}")
    dispatch[output_format](result, output)
