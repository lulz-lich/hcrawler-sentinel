# Plugin Development

A plugin is a Python module with an `analyze` function.

```python
from hcrawler.models import Finding

def analyze(*, url, response, soup, html):
    findings = []
    if "example" in html.lower():
        findings.append(Finding(
            id="custom.example",
            title="Example marker found",
            severity="info",
            description="The marker appeared in HTML.",
            evidence=url,
            recommendation="Review manually.",
            url=url,
        ))
    return findings
```

Run it:

```bash
hcrawler crawl https://example.com --audit --plugin my_plugin
```

Built-in plugins can be loaded by short name:

```bash
hcrawler crawl https://example.com --audit --plugin seo --plugin privacy --plugin accessibility
```
