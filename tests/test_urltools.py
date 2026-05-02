from hcrawler.urltools import looks_like_binary, normalize_start_url, normalize_url


def test_normalize_start_url():
    assert normalize_start_url("example.com") == "https://example.com"


def test_normalize_without_query():
    assert normalize_url("HTTPS://Example.com/a?z=1#x") == "https://example.com/a"


def test_normalize_with_query_sorted():
    assert normalize_url("https://example.com/a?z=1&a=2#x", include_query_strings=True) == "https://example.com/a?a=2&z=1"


def test_binary_detection():
    assert looks_like_binary("https://example.com/file.pdf")
