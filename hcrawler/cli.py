"""Command-line interface."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from colorama import  init as colorama_init

from .async_core import AsyncHCrawler
from .config import load_config_file
from .console import print_sentinel_summary
from .core import HCrawler
from .diff import compare_reports
from .doctor import run_doctor
from .exporters import export_result
from .metrics import compare_baseline, write_baseline
from .models import CrawlConfig
from .policy import evaluate_policy
from .profiles import profile_defaults
from .scope import load_scope_file
from .theme import (
    boot_sequence,
    contextual_art,
    event,
    mini_matrix,
    phase,
    print_kv_block,
    rule,
    splash,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hcrawler",
        description="Authorized web discovery, inventory, and lightweight audit CLI.",
    )
    sub = parser.add_subparsers(dest="command")

    crawl = sub.add_parser("crawl", help="Run a crawl")
    crawl.add_argument("url", nargs="?", help="Target URL or domain")
    crawl.add_argument("--scope-file", help="File with one target URL/domain per line. Uses the first target in this release.")
    crawl.add_argument("--config", help="Load options from JSON/YAML config")
    crawl.add_argument("-o", "--output", help="Output file path")
    crawl.add_argument(
        "-f",
        "--format",
        choices=["txt", "json", "csv", "html", "md", "sarif", "sqlite", "dot", "summary", "junit", "inventory"],
        default="txt",
    )
    crawl.add_argument("--profile", choices=["safe", "balanced", "fast", "deep", "portfolio"], default="balanced")
    crawl.add_argument("--async-engine", action="store_true", help="Use optional aiohttp async engine")
    crawl.add_argument("-A", "--user-agent", default=None)
    crawl.add_argument("--cookies")
    crawl.add_argument("--timeout", type=float)
    crawl.add_argument("--delay", type=float)
    crawl.add_argument("--max-pages", type=int)
    crawl.add_argument("--max-depth", type=int)
    crawl.add_argument("--concurrency", type=int)
    crawl.add_argument("--retries", type=int, default=2)
    crawl.add_argument("--backoff", type=float, default=0.5)
    crawl.add_argument("--external", action="store_true")
    crawl.add_argument("--ignore-robots", action="store_true")
    crawl.add_argument("--sitemap", action="store_true")
    crawl.add_argument("--no-robots-sitemaps", action="store_true")
    crawl.add_argument("--include-query-strings", action="store_true")
    crawl.add_argument("--allow", action="append", default=[])
    crawl.add_argument("--deny", action="append", default=[])
    crawl.add_argument("--no-links", action="store_true")
    crawl.add_argument("--emails", action="store_true")
    crawl.add_argument("--phones", action="store_true")
    crawl.add_argument("--cpfs", action="store_true")
    crawl.add_argument("--cnpjs", action="store_true")
    crawl.add_argument("--ipv4s", action="store_true")
    crawl.add_argument("--no-document-validation", action="store_true")
    crawl.add_argument("--audit", action="store_true")
    crawl.add_argument("--sensitive-path-checks", action="store_true")
    crawl.add_argument("--plugin", action="append", default=[])
    crawl.add_argument("--tag")
    crawl.add_argument("--write-baseline", help="Write a normalized baseline JSON file")
    crawl.add_argument("--compare-baseline", help="Compare current result against a baseline JSON file")
    crawl.add_argument(
        "--fail-on",
        choices=["info", "low", "medium", "high", "critical"],
        help="Exit with code 2 if findings at this severity or higher exist",
    )
    crawl.add_argument("--max-errors-policy", type=int, help="Exit with code 2 if crawl errors exceed this number")
    crawl.add_argument("--sentinel-summary", action="store_true", help="Print richer summary table")
    crawl.add_argument("--no-effects", action="store_true", help="Disable ASCII art, animations, and hacker-style effects")
    crawl.add_argument("-q", "--quiet", action="store_true")
    crawl.add_argument("--debug", action="store_true")

    diff = sub.add_parser("diff", help="Compare two JSON reports")
    diff.add_argument("old_report")
    diff.add_argument("new_report")
    diff.add_argument("-o", "--output")

    demo = sub.add_parser("demo-command", help="Print a strong portfolio demo command")
    demo.add_argument("url", nargs="?", default="http://localhost:8000")

    sub.add_parser("doctor", help="Check local installation and optional dependencies")

    return parser


def configure_logging(*, quiet: bool = False, debug: bool = False) -> None:
    level = logging.WARNING if quiet else logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")


def print_banner(*, effects: bool = True, command: str | None = None) -> None:
    splash(enabled=effects, command=command)
    mini_matrix(enabled=effects, rows=3)
    boot_sequence(enabled=effects)


def print_summary(result) -> None:
    event("crawl completed", "info")
    print_kv_block(
        "operation summary",
        [
            ("pages crawled", len(result.pages)),
            ("links found", len(result.links)),
            ("external links", len(result.external_links)),
            ("sitemap urls", len(result.sitemap_urls)),
            ("technologies", len(result.technologies)),
            ("emails found", len(result.emails)),
            ("phones found", len(result.phones)),
            ("cpfs found", len(result.cpfs)),
            ("cnpjs found", len(result.cnpjs)),
            ("ipv4s found", len(result.ipv4s)),
            ("secret hints", len(result.secret_hints)),
            ("sensitive path hits", len(result.checked_sensitive_paths)),
            ("robots blocked", len(result.robots_disallowed_seen)),
            ("errors", len(result.errors)),
        ],
    )


def apply_config_file(args) -> dict:
    if not args.config:
        return {}
    return load_config_file(Path(args.config))


def value(cli_value, config: dict, key: str, default=None):
    return cli_value if cli_value is not None else config.get(key, default)


def run_crawl(args) -> int:
    config_file = apply_config_file(args)
    configure_logging(quiet=args.quiet, debug=args.debug)

    effects = not args.no_effects and not args.quiet

    if not args.quiet:
        print_banner(effects=effects, command="crawl")

    scope_targets = load_scope_file(Path(args.scope_file)) if args.scope_file else []
    url = args.url or config_file.get("url") or config_file.get("start_url") or (scope_targets[0] if scope_targets else None)
    if not url:
        raise SystemExit("Target URL required.")

    profile = config_file.get("profile", args.profile)
    defaults = profile_defaults(profile)

    if not args.quiet:
        rule("target acquisition")
        print_kv_block(
            "mission profile",
            [
                ("target", url),
                ("profile", profile),
                ("output format", args.format or config_file.get("format", "txt")),
                ("audit", config_file.get("audit", args.audit)),
                ("async engine", bool(args.async_engine or config_file.get("async_engine"))),
                ("plugins", ", ".join(config_file.get("plugins", args.plugin)) or "none"),
            ],
        )
        phase("assembling crawler configuration", enabled=effects)

        contextual_art("scope", enabled=effects, chance=1.0)

        if config_file.get("sitemap", args.sitemap):
            contextual_art("sitemap", enabled=effects, chance=1.0)

        if not config_file.get("ignore_robots", args.ignore_robots):
            contextual_art("robots", enabled=effects, chance=1.0)

    config = CrawlConfig(
        start_url=url,
        user_agent=args.user_agent or config_file.get("user_agent") or "HCrawler/7.0 (+authorized-security-research)",
        cookies=args.cookies or config_file.get("cookies"),
        timeout=value(args.timeout, config_file, "timeout", defaults["timeout"]),
        delay=value(args.delay, config_file, "delay", defaults["delay"]),
        max_pages=value(args.max_pages, config_file, "max_pages", defaults["max_pages"]),
        max_depth=value(args.max_depth, config_file, "max_depth", defaults["max_depth"]),
        concurrency=value(args.concurrency, config_file, "concurrency", defaults["concurrency"]),
        retries=value(args.retries, config_file, "retries", 2),
        backoff=value(args.backoff, config_file, "backoff", 0.5),
        same_domain=not config_file.get("external", args.external),
        respect_robots=not config_file.get("ignore_robots", args.ignore_robots),
        collect_links=not config_file.get("no_links", args.no_links),
        collect_emails=config_file.get("emails", args.emails),
        collect_phones=config_file.get("phones", args.phones),
        collect_cpfs=config_file.get("cpfs", args.cpfs),
        collect_cnpjs=config_file.get("cnpjs", args.cnpjs),
        collect_ipv4s=config_file.get("ipv4s", args.ipv4s),
        validate_documents=not config_file.get("no_document_validation", args.no_document_validation),
        include_query_strings=config_file.get("include_query_strings", args.include_query_strings),
        audit_mode=config_file.get("audit", args.audit),
        use_sitemap=config_file.get("sitemap", args.sitemap),
        use_robots_sitemaps=not config_file.get("no_robots_sitemaps", args.no_robots_sitemaps),
        allow_patterns=config_file.get("allow", args.allow),
        deny_patterns=config_file.get("deny", args.deny),
        sensitive_path_checks=config_file.get("sensitive_path_checks", args.sensitive_path_checks),
        tag=args.tag or config_file.get("tag"),
    )

    plugins = config_file.get("plugins", args.plugin)

    if not args.quiet:
        contextual_art("crawl", enabled=effects, chance=1.0)

        if config.collect_emails or config.collect_phones or config.collect_cpfs or config.collect_cnpjs or config.collect_ipv4s:
            contextual_art("leaks", enabled=effects, chance=1.0)

        if config.audit_mode:
            contextual_art("headers", enabled=effects, chance=0.65)
            contextual_art("fingerprint", enabled=effects, chance=0.65)

    if args.async_engine or config_file.get("async_engine"):
        event("async engine selected", "accent")
        phase("spawning asynchronous crawler workers", enabled=effects)
        crawler = AsyncHCrawler(config, plugins=plugins)
        result = asyncio.run(crawler.crawl_async())
    else:
        event("sync engine selected", "accent")
        phase("arming synchronous crawler", enabled=effects)
        crawler = HCrawler(config, plugins=plugins)
        result = crawler.crawl()

    rule("mission report")
    if args.sentinel_summary:
        print_sentinel_summary(result, effects=effects)
    else:
        print_summary(result)

    if args.write_baseline:
        write_baseline(result, Path(args.write_baseline))
        event(f"saved baseline: {args.write_baseline}", "info")

    if args.compare_baseline:
        baseline_diff = compare_baseline(result, Path(args.compare_baseline))
        rule("baseline diff")
        print(json.dumps(baseline_diff, indent=2, ensure_ascii=False))

    output = args.output or config_file.get("output")
    output_format = args.format or config_file.get("format", "txt")

    if args.fail_on or args.max_errors_policy is not None:
        ok, messages = evaluate_policy(
            result,
            fail_on=args.fail_on or "high",
            max_errors=args.max_errors_policy,
        )
        if not ok:
            contextual_art("policy", enabled=effects, chance=1.0)
            event("policy failed", "error")
            for message in messages:
                print(f"- {message}")
            if output:
                export_result(result, Path(output), output_format)
            return 2

    if output:
        contextual_art("report", enabled=effects, chance=1.0)
        export_result(result, Path(output), output_format)
        event(f"saved output: {output}", "info")

    return 0


def run_diff(args) -> int:
    print_banner(effects=True, command="diff")
    contextual_art("diff", enabled=True, chance=1.0)
    rule("report diff")
    result = compare_reports(Path(args.old_report), Path(args.new_report))
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        event(f"saved diff: {args.output}", "info")
    else:
        print(text)
    return 0


def run_demo(args) -> int:
    print(
        f"hcrawler crawl {args.url} "
        "--profile portfolio "
        "--audit "
        "--emails "
        "--phones "
        "--ipv4s "
        "--sitemap "
        "--plugin seo "
        "--plugin privacy "
        "--plugin accessibility "
        "--sentinel-summary "
        "-o report.html "
        "-f html"
    )
    return 0


def run_doctor_cmd() -> int:
    print_banner(effects=True, command="doctor")
    contextual_art("doctor", enabled=True, chance=1.0)
    rule("environment diagnostics")
    ok, checks = run_doctor()
    for check in checks:
        print(check)
    return 0 if ok else 2


def main(argv: list[str] | None = None) -> int:
    colorama_init(autoreset=True)
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "crawl":
        return run_crawl(args)
    if args.command == "diff":
        return run_diff(args)
    if args.command == "demo-command":
        return run_demo(args)
    if args.command == "doctor":
        return run_doctor_cmd()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
