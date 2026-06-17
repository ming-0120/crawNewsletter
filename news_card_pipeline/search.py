from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from tavily import TavilyClient

from .config import Settings
from .utils import normalize_url

logger = logging.getLogger(__name__)

KOREAN_NEWS_DOMAINS = [
    "zdnet.co.kr",
    "aitimes.com",
    "itworld.co.kr",
    "cio.co.kr",
    "bloter.net",
    "etnews.com",
    "ddaily.co.kr",
    "digitaltoday.co.kr",
    "inews24.com",
    "it.chosun.com",
    "newsis.com",
    "yna.co.kr",
    "hankyung.com",
    "mk.co.kr",
    "sedaily.com",
    "biz.chosun.com",
]


def search_news(settings: Settings, limit: int) -> list[dict[str, Any]]:
    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY가 없습니다.")

    client = TavilyClient(api_key=settings.tavily_api_key)
    results: list[dict[str, Any]] = []

    for query in settings.search_queries:
        try:
            try:
                response = client.search(
                    query=query,
                    search_depth="advanced",
                    topic="news",
                    max_results=settings.max_search_results_per_query,
                    include_answer=False,
                    include_raw_content=False,
                    include_domains=KOREAN_NEWS_DOMAINS,
                )
            except TypeError:
                response = client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=settings.max_search_results_per_query,
                    include_answer=False,
                    include_raw_content=False,
                    include_domains=KOREAN_NEWS_DOMAINS,
                )
        except Exception as exc:
            logger.warning("Tavily 검색 실패: query=%s error=%s", query, exc)
            continue

        for item in response.get("results", []):
            url = item.get("url")
            if not url:
                continue
            url = normalize_url(url)
            if not _is_korean_site(url):
                continue
            results.append(
                {
                    "query": query,
                    "title": item.get("title") or "",
                    "url": url,
                    "source": item.get("source") or _source_from_url(url),
                    "published_date": item.get("published_date") or item.get("publishedDate") or "",
                    "snippet": item.get("content") or "",
                    "score": item.get("score"),
                }
            )

    return dedupe_by_url(results)[:limit]


def _source_from_url(url: str) -> str:
    parts = url.split("/")
    return parts[2] if len(parts) > 2 else ""


def _is_korean_site(url: str) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname.endswith(".kr") or hostname in KOREAN_NEWS_DOMAINS


def dedupe_by_url(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for article in articles:
        url = normalize_url(article.get("url", ""))
        if not url or url in seen:
            continue
        seen.add(url)
        article["url"] = url
        unique.append(article)
    return unique
