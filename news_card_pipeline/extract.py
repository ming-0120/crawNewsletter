from __future__ import annotations

import logging
from typing import Any

import trafilatura

logger = logging.getLogger(__name__)


def extract_article_text(article: dict[str, Any], timeout: int = 30) -> dict[str, Any] | None:
    url = article.get("url", "")
    if not url:
        return None

    try:
        downloaded = trafilatura.fetch_url(url, timeout=timeout)
        if not downloaded:
            raise RuntimeError("본문 다운로드 실패")
        metadata = trafilatura.extract_metadata(downloaded)
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
    except Exception as exc:
        logger.warning("기사 본문 추출 실패: url=%s error=%s", url, exc)
        return None

    if not text or len(text.strip()) < 200:
        logger.info("빈 본문 또는 너무 짧은 본문 제외: url=%s", url)
        return None

    extracted = dict(article)
    extracted["text"] = text.strip()
    if metadata:
        extracted["title"] = extracted.get("title") or metadata.title or ""
        extracted["source"] = extracted.get("source") or metadata.sitename or ""
        extracted["published_date"] = extracted.get("published_date") or metadata.date or ""
        extracted["author"] = metadata.author or ""
    return extracted
