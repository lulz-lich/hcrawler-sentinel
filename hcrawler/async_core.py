"""Optional asynchronous crawler engine."""

from __future__ import annotations

import asyncio
import time

try:
    import aiohttp
except Exception:  # pragma: no cover
    aiohttp = None

import requests

from .core import HCrawler
from .models import CrawlError, CrawlResult
from .urltools import normalize_url


class AsyncHCrawler(HCrawler):
    """Async version using aiohttp when available."""

    async def _fetch_text(self, session, url: str):
        if self.config.respect_robots and not self._robots_allowed(url):
            self.result.errors.append(CrawlError(url, "Blocked by robots.txt policy"))
            return None

        last_error = None
        for attempt in range(self.config.retries + 1):
            started = time.perf_counter()
            try:
                async with session.get(url, timeout=self.config.timeout, allow_redirects=True) as response:
                    body = await response.read()
                    elapsed = round((time.perf_counter() - started) * 1000, 2)
                    text = body.decode(response.charset or "utf-8", errors="ignore")
                    return response.status, dict(response.headers), text, body, elapsed
            except Exception as exc:
                last_error = exc
                if attempt < self.config.retries:
                    await asyncio.sleep(self.config.backoff * (2 ** attempt))

        self.result.errors.append(CrawlError(url, str(last_error)))
        return None

    async def crawl_async(self) -> CrawlResult:
        if aiohttp is None:
            raise RuntimeError("Async mode requires aiohttp. Install with: pip install aiohttp")

        queue: asyncio.Queue[tuple[str, int]] = asyncio.Queue()
        await queue.put((self.start_url, 0))
        for url in sorted(self._seed_sitemaps()):
            await queue.put((url, 0))

        seen: set[str] = set()
        lock = asyncio.Lock()
        connector = aiohttp.TCPConnector(limit=self.config.concurrency)
        headers = {"User-Agent": self.config.user_agent}
        if self.config.cookies:
            headers["Cookie"] = self.config.cookies

        started = time.time()

        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            async def worker():
                while True:
                    async with lock:
                        if len(self.result.pages) >= self.config.max_pages:
                            return
                    try:
                        url, depth = await asyncio.wait_for(queue.get(), timeout=0.5)
                    except asyncio.TimeoutError:
                        return

                    url = normalize_url(url, include_query_strings=self.config.include_query_strings)
                    async with lock:
                        if url in seen or not self._allowed_url(url):
                            queue.task_done()
                            continue
                        seen.add(url)

                    fetched = await self._fetch_text(session, url)
                    if fetched is None:
                        queue.task_done()
                        continue

                    status, headers_dict, text, body, elapsed = fetched
                    content_type = headers_dict.get("content-type", headers_dict.get("Content-Type", "")).lower()
                    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                        self.result.errors.append(CrawlError(url, f"Skipped non-HTML content: {content_type or 'unknown'}"))
                        queue.task_done()
                        continue

                    response = requests.Response()
                    response.status_code = status
                    response._content = body
                    response.headers.update(headers_dict)
                    response.url = url
                    response.encoding = "utf-8"

                    page, internal_links = self._analyze_page(url=url, depth=depth, response=response, html=text)
                    page.response_time_ms = elapsed

                    async with lock:
                        self.result.pages.append(page)
                        if self.config.collect_links and depth < self.config.max_depth:
                            for link in sorted(internal_links):
                                if link not in seen:
                                    await queue.put((link, depth + 1))

                    if self.config.delay > 0:
                        await asyncio.sleep(self.config.delay)
                    queue.task_done()

            workers = [asyncio.create_task(worker()) for _ in range(max(1, self.config.concurrency))]
            await asyncio.gather(*workers)

        self._check_sensitive_paths()
        self.result.metadata = {
            "duration_seconds": round(time.time() - started, 2),
            "page_budget": self.config.max_pages,
            "max_depth": self.config.max_depth,
            "tag": self.config.tag,
            "engine": "async",
        }
        return self.result
