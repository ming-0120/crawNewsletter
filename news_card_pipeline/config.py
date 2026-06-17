from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


SEARCH_QUERIES = [
    "국내 기업 AI 업무 자동화 최신 뉴스",
    "국내 기업 생성형 AI 업무 자동화 도입 사례",
    "AI 에이전트 업무 자동화 국내 기업 뉴스",
    "RPA AI 자동화 국내 사례 최신 기사",
    "엑셀 자동화 AI 국내 기업 사례",
    "스프레드시트 자동화 AI 업무 생산성 사례",
    "사내 업무 생산성 향상 AI 도구 국내 기사",
]


TOPICS = [
    "업무 자동화",
    "RPA",
    "AI Agent",
    "MCP",
    "Excel 자동화",
    "스프레드시트 자동화",
    "데이터 처리 자동화",
    "AI 기반 사무 자동화",
    "기업용 AI 도구",
    "사내 업무 생산성 향상 도구",
]


@dataclass(frozen=True)
class Settings:
    tavily_api_key: str | None
    openai_api_key: str | None
    openai_model: str = "gpt-4.1-mini"
    search_queries: list[str] = field(default_factory=lambda: SEARCH_QUERIES.copy())
    max_search_results_per_query: int = 8
    relevance_collect_threshold: float = 0.8
    relevance_hold_threshold: float = 0.5
    request_timeout: int = 30
    output_dir: Path = Path("output")
    font_path: str | None = None


def load_settings(output_dir: str | None = None) -> Settings:
    load_dotenv()
    return Settings(
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        max_search_results_per_query=int(os.getenv("MAX_SEARCH_RESULTS_PER_QUERY", "8")),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        output_dir=Path(output_dir or os.getenv("OUTPUT_DIR", "output")),
        font_path=os.getenv("CARD_FONT_PATH"),
    )


def validate_required_keys(settings: Settings) -> None:
    missing = []
    if not settings.tavily_api_key:
        missing.append("TAVILY_API_KEY")
    if not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if missing:
        raise RuntimeError(f"필수 환경변수가 없습니다: {', '.join(missing)}")
