from __future__ import annotations

import argparse
import os
from dataclasses import replace
from pathlib import Path

from dotenv import load_dotenv

from news_card_pipeline.config import load_settings
from news_card_pipeline.export_html import render_magazine_html
from news_card_pipeline.internal_ai_usage import generate_internal_ai_usage_content
from news_card_pipeline.search import search_news
from news_card_pipeline.utils import ensure_dir, today_str, write_json


DEFAULT_TEMPLATE = r"c:\Users\user0530\AppData\Local\Microsoft\Windows\INetCache\IE\Y3SA03R2\template_1_magazine[1].html"


def main() -> None:
    parser = argparse.ArgumentParser(description="Search articles, summarize with OpenAI, and render magazine HTML")
    parser.add_argument("--template", type=str, default=DEFAULT_TEMPLATE, help="HTML template path")
    parser.add_argument("--output", type=str, default="output", help="Output root directory")
    parser.add_argument(
        "--query",
        type=str,
        default="기업 사내 AI 활용 업무 자동화 사례 최신 뉴스",
        help="Tavily search query",
    )
    parser.add_argument("--limit", type=int, default=5, help="Tavily search result limit")
    parser.add_argument("--article-count", type=int, default=3, help="Number of articles to pass to OpenAI")
    args = parser.parse_args()

    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_api_key or openai_api_key.startswith("your_"):
        raise RuntimeError("OPENAI_API_KEY must be set to a real API key in .env")
    tavily_api_key = os.getenv("TAVILY_API_KEY", "")
    if not tavily_api_key or tavily_api_key.startswith("your_"):
        raise RuntimeError("TAVILY_API_KEY must be set to a real API key in .env")

    run_dir = ensure_dir(Path(args.output) / today_str())
    settings = load_settings(args.output)
    settings = replace(settings, search_queries=[args.query], max_search_results_per_query=args.limit)

    searched_articles = search_news(settings, limit=args.limit)
    write_json(run_dir / "internal_ai_usage_search_results.json", searched_articles)

    source_articles = []
    for article in searched_articles:
        try:
            from news_card_pipeline.extract import extract_article_text

            extracted = extract_article_text(article, timeout=settings.request_timeout)
        except ModuleNotFoundError:
            extracted = None
        source_articles.append(extracted or article)
        if len(source_articles) >= args.article_count:
            break

    if not source_articles:
        raise RuntimeError("No articles were found for OpenAI summarization.")

    write_json(run_dir / "internal_ai_usage_source_articles.json", source_articles)
    content = generate_internal_ai_usage_content(source_articles)
    write_json(run_dir / "internal_ai_usage.json", content)
    render_magazine_html(
        content=content,
        template_path=Path(args.template),
        output_path=run_dir / "internal_ai_usage.html",
    )
    print(f"articles used: {len(source_articles)}")
    for index, article in enumerate(source_articles, start=1):
        print(f"{index}. {article.get('title', '')} | {article.get('url', '')}")
    print(f"saved: {run_dir / 'internal_ai_usage_search_results.json'}")
    print(f"saved: {run_dir / 'internal_ai_usage_source_articles.json'}")
    print(f"saved: {run_dir / 'internal_ai_usage.json'}")
    print(f"saved: {run_dir / 'internal_ai_usage.html'}")


if __name__ == "__main__":
    main()
