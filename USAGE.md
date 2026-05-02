# HCrawler Sentinel Usage Guide

## Basic crawl

```bash
hcrawler crawl https://example.com
```

## Portfolio-grade report

```bash
hcrawler crawl http://localhost:8000 --profile portfolio --audit --emails --phones --ipv4s --sitemap --plugin seo --plugin privacy --plugin accessibility --sentinel-summary -o report.html -f html
```

## Config file

```bash
hcrawler crawl --config examples/portfolio-config.yaml
```

## Scope file

```bash
hcrawler crawl --scope-file examples/scope.txt --audit
```

## Async crawl

```bash
hcrawler crawl https://example.com --async-engine --concurrency 10 --profile fast --audit -o report.json -f json
```

## Export formats

```bash
hcrawler crawl https://example.com --audit -o report.txt -f txt
hcrawler crawl https://example.com --audit -o report.json -f json
hcrawler crawl https://example.com --audit -o report.csv -f csv
hcrawler crawl https://example.com --audit -o report.html -f html
hcrawler crawl https://example.com --audit -o report.md -f md
hcrawler crawl https://example.com --audit -o report.sarif -f sarif
hcrawler crawl https://example.com --audit -o report.sqlite -f sqlite
hcrawler crawl https://example.com --audit -o junit.xml -f junit
hcrawler crawl https://example.com --audit -o graph.dot -f dot
hcrawler crawl https://example.com --audit -o summary.json -f summary
hcrawler crawl https://example.com --audit -o inventory.json -f inventory
```

## Plugins

```bash
hcrawler crawl https://example.com --audit --plugin seo
hcrawler crawl https://example.com --audit --plugin privacy
hcrawler crawl https://example.com --audit --plugin accessibility
```

## Baseline

```bash
hcrawler crawl https://example.com --audit --write-baseline baseline.json -o report.json -f json
hcrawler crawl https://example.com --audit --compare-baseline baseline.json
```

## CI policy

```bash
hcrawler crawl https://example.com --audit --fail-on medium -o report.sarif -f sarif
```

## Doctor

```bash
hcrawler doctor
```
