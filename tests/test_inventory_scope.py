from pathlib import Path

from hcrawler.inventory import build_attack_surface_inventory
from hcrawler.models import CrawlResult, PageRecord
from hcrawler.scope import load_scope_file


def test_scope_file(tmp_path: Path):
    scope = tmp_path / "scope.txt"
    scope.write_text("# comment\nexample.com\nhttps://example.org\n", encoding="utf-8")
    assert load_scope_file(scope) == ["https://example.com", "https://example.org"]


def test_inventory():
    result = CrawlResult(start_url="https://example.com")
    result.pages.append(PageRecord(url="https://example.com/login", status_code=200, depth=0, forms_count=1))
    inventory = build_attack_surface_inventory(result)
    assert inventory["summary"]["forms_pages"] == 1
    assert inventory["endpoints"][0]["path"] == "/login"
