import json
from pathlib import Path

from hcrawler.diff import compare_reports
from hcrawler.metrics import severity_counts
from hcrawler.models import CrawlResult, Finding, PageRecord
from hcrawler.policy import evaluate_policy


def test_compare_reports(tmp_path: Path):
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text(json.dumps({
        "pages": [{"url": "https://a.test", "content_hash": "1", "findings": []}],
        "technologies": ["A"],
        "emails": [],
    }), encoding="utf-8")
    new.write_text(json.dumps({
        "pages": [{"url": "https://a.test", "content_hash": "2", "findings": [{"id": "x", "evidence": "e"}]}],
        "technologies": ["A", "B"],
        "emails": ["b@example.com"],
    }), encoding="utf-8")
    diff = compare_reports(old, new)
    assert diff["changed_pages"] == ["https://a.test"]
    assert diff["added_technologies"] == ["B"]
    assert diff["added_emails"] == ["b@example.com"]


def test_policy_fail_on_high():
    result = CrawlResult(start_url="https://example.com")
    result.pages.append(PageRecord(
        url="https://example.com",
        status_code=200,
        depth=0,
        findings=[Finding("x", "X", "high", "desc")]
    ))
    counts = severity_counts(result)
    ok, messages = evaluate_policy(result, fail_on="high")
    assert counts["high"] == 1
    assert not ok
    assert messages
