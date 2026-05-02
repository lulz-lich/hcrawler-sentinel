# HCrawler Sentinel

HCrawler Sentinel is a Python CLI for authorized web discovery, attack-surface inventory, baseline comparison, graphing, and lightweight security auditing.

It is built as a portfolio-grade security tool: scoped crawling, robots.txt and sitemap support, optional async crawling, metadata extraction, technology fingerprinting, weak-signal checks, plugins, report diffing, policy gates, and professional exports.

## Ethical scope

Use only on systems you own, manage, or have explicit permission to test.

Do not use it for spam, harassment, credential theft, stalking, access-control bypass, or unauthorized crawling. The internet is already messy enough without another script pretending ethics are optional.

## Features

### Crawling

- same-domain crawling by default
- optional external-domain crawling
- depth and page limits
- safe, balanced, fast, deep, and portfolio profiles
- retries with exponential backoff
- configurable delay and timeout
- optional async engine with `aiohttp`
- custom User-Agent
- Cookie header for authorized authenticated crawls
- binary/static asset skipping
- max URL length protection

### Scope and discovery

- `robots.txt` support
- sitemap discovery from `/sitemap.xml`
- sitemap discovery from `robots.txt`
- nested sitemap parsing
- URL normalization
- optional query string preservation
- allow and deny regex filters
- scope file support
- link graph tracking

### Audit mode

- page title extraction
- meta description extraction
- canonical URL extraction
- heading counts
- forms, scripts, images, internal links, and external links counting
- response timing
- content length
- SHA-256 content hashing
- technology fingerprinting
- browser security-header checks
- mixed-content weak signal
- password-over-HTTP detection
- weak secret-keyword detection
- optional sensitive-path checks
- risk score per page

### Extraction

- emails
- phone numbers
- IPv4 addresses
- CPF values with check-digit validation
- CNPJ values with check-digit validation

### Plugins

Built-in plugins:

- `seo`
- `privacy`
- `accessibility`

### Reporting

- TXT
- JSON
- CSV
- Markdown
- HTML
- SARIF
- SQLite
- JUnit
- Graphviz DOT
- executive summary JSON
- attack-surface inventory JSON

### Workflow features

- report diffing
- baseline writing
- baseline comparison
- CI policy gates with `--fail-on`
- `doctor` command
- YAML/JSON config
- Dockerfile
- Makefile
- pre-commit config
- GitHub Actions CI and release workflow

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/hcrawler.git
cd hcrawler
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,async]"
```

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev,async]"
```

## Quick demo

```bash
hcrawler crawl http://localhost:8000 --profile portfolio --audit --emails --phones --ipv4s --sitemap --plugin seo --plugin privacy --plugin accessibility --sentinel-summary -o report.html -f html
```

## Async mode

```bash
hcrawler crawl https://example.com --async-engine --concurrency 10 --profile fast --audit -o report.json -f json
```

## Inventory export

```bash
hcrawler crawl https://example.com --audit -o inventory.json -f inventory
```

## SARIF export

```bash
hcrawler crawl https://example.com --audit -o report.sarif -f sarif
```

## SQLite export

```bash
hcrawler crawl https://example.com --audit -o report.sqlite -f sqlite
```

## Link graph export

```bash
hcrawler crawl https://example.com --audit -o graph.dot -f dot
dot -Tpng graph.dot -o graph.png
```

## Baseline

```bash
hcrawler crawl https://example.com --audit --write-baseline baseline.json -o report.json -f json
```

Compare later:

```bash
hcrawler crawl https://example.com --audit --compare-baseline baseline.json
```

## Diff reports

```bash
hcrawler diff old.json new.json
```

## CI policy gate

```bash
hcrawler crawl https://example.com --audit --fail-on medium -o report.sarif -f sarif
```

## Doctor

```bash
hcrawler doctor
```

## Resume bullet

Developed HCrawler Sentinel, a Python CLI for authorized web discovery, attack-surface inventory and lightweight security auditing, featuring scoped crawling, robots.txt/sitemap support, optional async mode, retries with backoff, URL normalization, technology fingerprinting, security-header analysis, CPF/CNPJ validation, plugin-based findings, weak-signal detection, SARIF/SQLite/JUnit/HTML/JSON reporting, baseline comparison, CI policy gates and link graph export.
