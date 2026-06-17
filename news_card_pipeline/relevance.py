from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from .config import Settings, TOPICS
from .utils import read_json_from_llm, truncate_text

logger = logging.getLogger(__name__)


def judge_relevance(article: dict[str, Any], settings: Settings) -> dict[str, Any]:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY가 없습니다.")

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""
아래 기사가 다음 수집 대상 주제 중 하나 이상에 명확히 관련되는지 판단하라.

수집 대상 주제:
{", ".join(TOPICS)}

제외 기준:
- 관련성이 약한 일반 AI 뉴스
- 소비자용 챗봇, 반도체, 투자, 모델 성능 뉴스처럼 업무 자동화와 직접 관련 없는 기사
- 명확한 근거가 없는 기사

반드시 JSON만 반환하라.
형식:
{{
  "is_relevant": true,
  "score": 0.0,
  "matched_topics": ["RPA", "AI Agent"],
  "reason": "이 기사가 수집 대상인 이유"
}}

기사 제목: {article.get("title", "")}
출처: {article.get("source", "")}
발행일: {article.get("published_date", "")}
요약/본문:
{truncate_text(article.get("text") or article.get("snippet", ""), 6000)}
""".strip()

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "너는 기업 업무 자동화 뉴스 큐레이터다. 엄격하게 관련성을 판단한다."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content or "{}"
    try:
        result = read_json_from_llm(content)
    except Exception as exc:
        logger.warning("관련성 JSON 파싱 실패: url=%s error=%s", article.get("url"), exc)
        result = {"is_relevant": False, "score": 0.0, "matched_topics": [], "reason": "LLM JSON 파싱 실패"}

    result["score"] = float(result.get("score", 0.0))
    result["is_relevant"] = bool(result.get("is_relevant")) and result["score"] >= settings.relevance_collect_threshold
    return result
