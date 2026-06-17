from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

from .config import load_settings, validate_required_keys
from .utils import ensure_dir, setup_logging, today_str, write_json

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI/RPA/업무자동화 뉴스 카드뉴스 자동 생성 파이프라인")
    parser.add_argument("--limit", type=int, default=10, help="검색 후보 최대 개수")
    parser.add_argument("--output", type=str, default=None, help="출력 루트 폴더")
    parser.add_argument(
        "--format",
        type=str,
        default="markdown,ppt,image,json",
        help="저장 형식: json,markdown,ppt,image 조합",
    )
    return parser.parse_args()


def run_pipeline(limit: int, output: str | None, formats: set[str]) -> Path:
    from .card_generator import generate_card_news
    from .export_markdown import export_markdown
    from .extract import extract_article_text
    from .relevance import judge_relevance
    from .search import search_news

    settings = load_settings(output)
    validate_required_keys(settings)

    run_dir = ensure_dir(settings.output_dir / today_str())
    logger.info("출력 폴더: %s", run_dir)

    articles = search_news(settings, limit=limit)
    write_json(run_dir / "articles.json", articles)
    logger.info("검색 후보 %d건 저장", len(articles))

    selected_articles: list[dict[str, Any]] = []
    held_articles: list[dict[str, Any]] = []
    for article in articles:
        extracted = extract_article_text(article, timeout=settings.request_timeout)
        if not extracted:
            continue
        relevance = judge_relevance(extracted, settings)
        extracted["relevance"] = relevance
        score = relevance.get("score", 0.0)
        if relevance.get("is_relevant") and score >= settings.relevance_collect_threshold:
            selected_articles.append(extracted)
        elif score >= settings.relevance_hold_threshold:
            held_articles.append(extracted)

    write_json(run_dir / "selected_articles.json", selected_articles)
    write_json(run_dir / "held_articles.json", held_articles)
    logger.info("수집 %d건, 보류 %d건", len(selected_articles), len(held_articles))

    card_news_items: list[dict[str, Any]] = []
    for article in selected_articles:
        try:
            card_news_items.append(generate_card_news(article, settings))
        except Exception as exc:
            logger.warning("카드뉴스 생성 실패: url=%s error=%s", article.get("url"), exc)

    write_json(run_dir / "card_news.json", card_news_items)

    if "markdown" in formats or "ppt" in formats or "image" in formats:
        export_markdown(card_news_items, run_dir / "card_news.md")

    if "ppt" in formats:
        try:
            from .export_ppt import export_ppt

            export_ppt(card_news_items, run_dir / "ppt" / "card_news.pptx")
        except Exception as exc:
            logger.warning("PPT 생성 실패, JSON/Markdown 결과는 유지됩니다: %s", exc)

    if "image" in formats:
        try:
            from .export_image import export_images

            export_images(card_news_items, run_dir / "images", font_path=settings.font_path)
        except Exception as exc:
            logger.warning("PNG 이미지 생성 실패, JSON/Markdown 결과는 유지됩니다: %s", exc)

    logger.info("완료")
    return run_dir


def main() -> None:
    setup_logging()
    args = parse_args()
    formats = {item.strip().lower() for item in args.format.split(",") if item.strip()}
    run_pipeline(limit=args.limit, output=args.output, formats=formats)


if __name__ == "__main__":
    main()
