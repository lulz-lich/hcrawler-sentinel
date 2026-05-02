# Architecture

HCrawler Sentinel is organized as a modular Python package.

## Modules

| Module | Responsibility |
|---|---|
| `cli.py` | CLI and subcommands |
| `core.py` | Synchronous crawler |
| `async_core.py` | Optional async crawler |
| `models.py` | Dataclasses |
| `patterns.py` | Extractors and CPF/CNPJ validation |
| `analyzer.py` | Audit findings and page analysis |
| `robots.py` | robots.txt parsing |
| `sitemap.py` | sitemap parsing |
| `exporters.py` | report exports |
| `diff.py` | report diffing |
| `metrics.py` | severity counts, baseline and summary |
| `policy.py` | CI policy gates |
| `inventory.py` | attack-surface inventory |
| `scope.py` | scope file loading |
| `plugins/` | optional analyzers |

## Pipeline

1. CLI parses arguments or config.
2. Profile defaults are applied.
3. Robots and sitemaps are loaded.
4. URLs are normalized and filtered.
5. Pages are fetched with retries.
6. HTML is parsed with BeautifulSoup.
7. Patterns and links are extracted.
8. Audit mode runs findings and plugins.
9. Results are exported.
