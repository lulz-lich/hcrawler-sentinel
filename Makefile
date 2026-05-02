.PHONY: install dev test lint demo build clean

install:
	pip install -e .

dev:
	pip install -e ".[dev,async]"

test:
	pytest

lint:
	ruff check .

demo:
	hcrawler crawl http://localhost:8000 --profile portfolio --audit --emails --phones --ipv4s --plugin seo --plugin privacy --plugin accessibility --sentinel-summary -o report.html -f html

build:
	python -m build

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
