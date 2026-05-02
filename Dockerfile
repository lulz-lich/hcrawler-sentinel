FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY hcrawler /app/hcrawler

RUN pip install --no-cache-dir ".[async]"

ENTRYPOINT ["hcrawler"]
