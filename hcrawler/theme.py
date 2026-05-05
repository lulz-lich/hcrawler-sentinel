"""Context-aware terminal theme, ASCII art, pixel art and animations for HCrawler Sentinel.

The goal is not to dump random ASCII art. Each visual appears only when it
matches the current action: scope loading, robots, sitemap, crawling, fingerprint,
data extraction, graphing, reporting, diffing or diagnostics.
"""

from __future__ import annotations

import random
import sys
import time
from typing import Iterable

from colorama import Fore, Style

NEON_GREEN = Fore.LIGHTGREEN_EX
NEON_CYAN = Fore.CYAN
NEON_RED = Fore.LIGHTRED_EX
NEON_YELLOW = Fore.YELLOW
NEON_MAGENTA = Fore.LIGHTMAGENTA_EX
MUTED = Fore.GREEN
DIM = Fore.LIGHTBLACK_EX
WHITE = Fore.WHITE
RESET = Style.RESET_ALL


BANNERS = [
    r"""
██╗  ██╗ ██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗
██║  ██║██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗
███████║██║     ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝
██╔══██║██║     ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗
██║  ██║╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝
             authorized crawling // inventory // lightweight audit
""",
    r"""
┌──────────────────────────────────────────────────────────────────────────────┐
│   HCrawler Sentinel                                                          │
│                                                                              │
│   [scope] ──► [crawl queue] ──► [HTTP fetch] ──► [parse] ──► [report]         │
│      │              │                 │              │           │           │
│      ▼              ▼                 ▼              ▼           ▼           │
│   robots         sitemap           headers        links       findings       │
└──────────────────────────────────────────────────────────────────────────────┘
""",
    r"""
        __      __        ___.       _________                    .__
       /  \    /  \ ____  \_ |__    /   _____/ ____ _____    ____ |  |__
       \   \/\/   // __ \  | __ \   \_____  \_/ ___\\__  \  /    \|  |  \
        \        /\  ___/  | \_\ \  /        \  \___ / __ \|   |  \   Y  \
         \__/\  /  \___  > |___  / /_______  /\___  >____  /___|  /___|  /
              \/       \/      \/          \/     \/     \/     \/     \/
              crawling the web graph, not pretending curl is a product
""",
]


PHASE_ART = {
    "scope": [
        r"""
        ┌──────────── SCOPE LOCK ────────────┐
        │ target domain accepted             │
        │ external traversal: controlled      │
        │ query strategy: normalized          │
        └────────────────────────────────────┘
""",
        r"""
             .----------------.
            / authorized zone /|
           /_________________/ |
           |   crawl scope   | |
           |   locked        | /
           |_________________|/
""",
    ],
    "robots": [
        r"""
        robots.txt
        ┌───────────────┐
        │ Allow: /docs  │
        │ Deny: /admin  │
        │ Sitemap: ...  │
        └───────┬───────┘
                ▼
          policy respected
""",
        r"""
          ┌───────────────────────┐
          │ robots policy parser  │
          ├───────────────────────┤
          │ can_fetch(url) -> yes │
          └───────────────────────┘
""",
    ],
    "sitemap": [
        r"""
              sitemap.xml
        ┌─────────┬─────────┬─────────┐
        │ /       │ /docs   │ /blog   │
        └────┬────┴────┬────┴────┬────┘
             ▼         ▼         ▼
          queue     queue     queue
""",
        r"""
        sitemap discovery
        root.xml ──► nested.xml ──► urlset
             │             │
             └──── URLs ───┘
""",
    ],
    "crawl": [
        r"""
                    .-.
                   (   )
                    '-'
                  __/|\__
             .---'  / \  '---.
          .-'      /   \      '-.
        .'        /_____\        '.
       /        _/       \_        \
      |       .' WEB GRAPH '.       |
       \     /   traversal  \     /
        '._ /_______________\ _.'
           '-----------------'
""",
        r"""
        URL FRONTIER
   ┌──────────────────┐
   │ /                │
   │ /about           │
   │ /contact         │
   │ /docs            │
   │ binary skipped   │
   └────────┬─────────┘
            ▼
       normalized queue
""",
        r"""
              .     .
              \\   //
               \\_//
             .-     -.
            /  .---.  \
           |  /     \  |
           | | () () | |
            \ \  ^  / /
             `-.___.-'

        crawler spider online
""",
    ],
    "http": [
        r"""
        ┌─────────────────────────┐
        │ GET /                   │
        │ GET /robots.txt         │
        │ GET /sitemap.xml        │
        │ GET /contact            │
        └───────────┬─────────────┘
                    ▼
              response parser
""",
        r"""
          HTTP TRACE
        ┌──────────────┐
        │ 200 text/html│──► parse
        │ 301 redirect │──► follow
        │ 403 blocked  │──► log
        │ 404 missing  │──► report
        └──────────────┘
""",
    ],
    "fingerprint": [
        r"""
        FINGERPRINT ENGINE
        ┌────────────┬──────────────┐
        │ headers    │ Server       │
        │ html       │ React/Next   │
        │ scripts    │ Analytics    │
        │ meta       │ Generator    │
        └────────────┴──────────────┘
""",
        r"""
          .-------------------------.
          | technology signatures   |
          | wp-content  -> WordPress|
          | _next/      -> Next.js  |
          | cf-ray      -> CF edge  |
          '-------------------------'
""",
    ],
    "headers": [
        r"""
        SECURITY HEADERS
        ┌────────────────────────────┐
        │ CSP                  [?]   │
        │ HSTS                 [?]   │
        │ X-Frame-Options      [?]   │
        │ Referrer-Policy      [?]   │
        └────────────────────────────┘
""",
        r"""
        header audit
        response ──► browser controls ──► finding score
""",
    ],
    "leaks": [
        r"""
        PATTERN EXTRACTION
        ┌────────┬────────┬────────┬────────┐
        │ emails │ phones │ cpf    │ cnpj   │
        └────┬───┴────┬───┴────┬───┴────┬───┘
             ▼        ▼        ▼        ▼
          evidence candidates, not magic
""",
        r"""
             .-------------------.
             | data pattern hit  |
             | email / phone / id|
             '---------+---------'
                       ▼
                 report evidence
""",
    ],
    "graph": [
        r"""
        LINK GRAPH
             /docs
              ▲
              │
        / ◄───┼───► /contact
              │
              ▼
            /blog
""",
        r"""
        graph export
        page A ─────► page B
          │             │
          ▼             ▼
        page C ─────► page D
""",
    ],
    "report": [
        r"""
        REPORT PIPELINE
        ┌────────┬────────┬────────┬────────┐
        │ JSON   │ HTML   │ SARIF  │ SQLITE │
        ├────────┼────────┼────────┼────────┤
        │ MD     │ CSV    │ JUNIT  │ DOT    │
        └────────┴────────┴────────┴────────┘
""",
        r"""
        ┌────────────────────────────────────┐
        │ SENTINEL REPORT                    │
        ├────────────────────────────────────┤
        │ pages        █████████░░░          │
        │ links        ████████████░         │
        │ findings     █████░░░░░░░          │
        │ technologies ███████░░░░░          │
        └────────────────────────────────────┘
""",
    ],
    "policy": [
        r"""
        CI POLICY GATE
        ┌──────────────┐
        │ severity >= ?│── fail/pass
        │ errors <= ?  │── fail/pass
        └──────────────┘
""",
    ],
    "diff": [
        r"""
        REPORT DIFF
        old.json ──► hashes/pages/findings ◄── new.json
             │                                  │
             └──────────── delta.json ──────────┘
""",
    ],
    "doctor": [
        r"""
        ENVIRONMENT DOCTOR
        ┌────────────┬──────────┐
        │ python     │ check    │
        │ requests   │ check    │
        │ bs4        │ check    │
        │ aiohttp    │ optional │
        └────────────┴──────────┘
""",
    ],
}


BOOT_LINES = [
    "loading authorized scope rules",
    "checking robots and sitemap handlers",
    "arming HTTP retry/backoff engine",
    "warming HTML parser",
    "loading fingerprint signatures",
    "binding extraction patterns",
    "mounting report exporters",
    "initializing contextual terminal layer",
]


QUOTES = [
    "authorized recon only",
    "scope first, scan second",
    "web graph acquisition ready",
    "headers, links, metadata, findings",
    "green text does not make it legal, permission does",
]


def _out(text: str) -> None:
    sys.stdout.write(text)
    sys.stdout.flush()


def typewrite(
    text: str,
    *,
    delay: float = 0.002,
    enabled: bool = True,
    newline: bool = True,
    color: str = "",
) -> None:
    if not enabled:
        _out(color + text + RESET + ("\n" if newline else ""))
        return

    _out(color)
    for char in text:
        _out(char)
        time.sleep(delay)
    if color:
        _out(RESET)
    if newline:
        _out("\n")


def splash(*, enabled: bool = True, command: str | None = None) -> None:
    banner = random.choice(BANNERS)
    color = random.choice([NEON_GREEN, NEON_CYAN, NEON_MAGENTA])

    if enabled:
        for line in banner.splitlines():
            if line.strip():
                typewrite(line, delay=0.00045, enabled=True, color=color)
            else:
                print()
    else:
        print(color + banner + RESET)

    print(NEON_GREEN + "[ HCrawler Sentinel // contextual web reconnaissance interface ]" + RESET)
    print(MUTED + f"[ {random.choice(QUOTES)} ]" + RESET)
    print()


def boot_sequence(*, enabled: bool = True) -> None:
    for idx, line in enumerate(BOOT_LINES, start=1):
        prefix = f"[{idx:02d}/{len(BOOT_LINES):02d}] "
        typewrite(prefix + line + " ... ok", delay=0.0012, enabled=enabled, color=MUTED)
    print()


def rule(label: str = "") -> None:
    bar = "═" * 78
    if label:
        print(NEON_CYAN + f"╔{bar}╗" + RESET)
        centered = f" {label} ".center(78, "═")
        print(NEON_CYAN + f"║{centered}║" + RESET)
        print(NEON_CYAN + f"╚{bar}╝" + RESET)
    else:
        print(NEON_CYAN + "═" * 80 + RESET)


def print_kv_block(title: str, rows: Iterable[tuple[str, object]]) -> None:
    width = 88
    print(NEON_CYAN + "┌" + "─" * (width - 2) + "┐" + RESET)
    heading = f" {title} ".center(width - 2, "─")
    print(NEON_CYAN + "│" + RESET + NEON_GREEN + heading + RESET + NEON_CYAN + "│" + RESET)
    print(NEON_CYAN + "├" + "─" * (width - 2) + "┤" + RESET)
    for key, value in rows:
        key_text = f" {key:<24}"
        value_text = f" {value}"
        content = (key_text + "│" + value_text)[: width - 2]
        print(NEON_CYAN + "│" + RESET + content.ljust(width - 2) + NEON_CYAN + "│" + RESET)
    print(NEON_CYAN + "└" + "─" * (width - 2) + "┘" + RESET)


def phase(label: str, *, enabled: bool = True, loops: int = 14) -> None:
    frames = ["[    ]", "[=   ]", "[==  ]", "[=== ]", "[ ===]", "[  ==]", "[   =]", "[====]"]
    if not enabled:
        print(MUTED + f"{label} ... done" + RESET)
        return

    for idx in range(loops):
        _out("\r" + NEON_GREEN + frames[idx % len(frames)] + RESET + f" {label}")
        time.sleep(0.025)
    _out("\r" + NEON_GREEN + "[done]" + RESET + f" {label}" + " " * 12 + "\n")


def event(message: str, level: str = "info") -> None:
    color = {
        "info": NEON_GREEN,
        "warn": NEON_YELLOW,
        "error": NEON_RED,
        "accent": NEON_MAGENTA,
    }.get(level, NEON_GREEN)
    icon = {
        "info": "[+]",
        "warn": "[!]",
        "error": "[x]",
        "accent": "[*]",
    }.get(level, "[+]")
    print(color + f"{icon} {message}" + RESET)


def mini_matrix(*, enabled: bool = True, rows: int = 4, width: int = 88) -> None:
    if not enabled:
        return

    alphabet = "01ABCDEF<>[]{}:/\\.-_#@%+"
    for _ in range(rows):
        line = "".join(random.choice(alphabet) for _ in range(width))
        print(DIM + line + RESET)
        time.sleep(0.005)
    print()


def contextual_art(context: str, *, enabled: bool = True, chance: float = 1.0) -> None:
    """Print one context-relevant art piece."""
    if not enabled:
        return
    if random.random() > chance:
        return

    arts = PHASE_ART.get(context)
    if not arts:
        return

    color = {
        "scope": NEON_CYAN,
        "robots": NEON_YELLOW,
        "sitemap": NEON_CYAN,
        "crawl": NEON_GREEN,
        "http": NEON_CYAN,
        "fingerprint": NEON_MAGENTA,
        "headers": NEON_YELLOW,
        "leaks": NEON_RED,
        "graph": NEON_GREEN,
        "report": NEON_CYAN,
        "policy": NEON_YELLOW,
        "diff": NEON_MAGENTA,
        "doctor": NEON_CYAN,
    }.get(context, NEON_GREEN)

    print(color + random.choice(arts) + RESET)


def contextual_result_art(result, *, enabled: bool = True) -> None:
    """Print result-based art only when it matches the actual crawl outcome."""
    if not enabled:
        return

    if result.links or result.external_links:
        contextual_art("graph", enabled=True, chance=1.0)

    if result.technologies:
        contextual_art("fingerprint", enabled=True, chance=1.0)

    if result.emails or result.phones or result.cpfs or result.cnpjs or result.ipv4s or result.secret_hints:
        contextual_art("leaks", enabled=True, chance=1.0)

    has_header_findings = any(
        finding.id.startswith("headers.") or finding.id.startswith("transport.")
        for page in result.pages
        for finding in page.findings
    )
    if has_header_findings:
        contextual_art("headers", enabled=True, chance=1.0)