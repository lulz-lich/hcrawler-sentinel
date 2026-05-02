# Sentinel Features

## Doctor command

```bash
hcrawler doctor
```

## Inventory export

```bash
hcrawler crawl https://example.com --audit -o inventory.json -f inventory
```

## Policy gates

```bash
hcrawler crawl https://example.com --audit --fail-on medium -o report.sarif -f sarif
```

## Baseline

```bash
hcrawler crawl https://example.com --audit --write-baseline baseline.json
hcrawler crawl https://example.com --audit --compare-baseline baseline.json
```

## Graph

```bash
hcrawler crawl https://example.com --audit -o graph.dot -f dot
dot -Tpng graph.dot -o graph.png
```
