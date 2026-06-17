from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from .config import Settings
from .utils import read_json_from_llm, truncate_text

logger = logging.getLogger(__name__)


CARD_PROMPT_TEMPLATE = """
다음 기사를 사내 공유용 카드뉴스로 만들어라.

조건:
- 카드 수: 5장
- 대상: 비개발자 포함 전사 직원
- 출력 언어: 한국어
- 영어 기사도 한국어로 자연스럽게 번역·요약할 것
- 전문 용어는 필요한 경우 원문 용어를 괄호로 함께 표기할 것
- 톤: 쉽고 명확하게
- 과장 금지
- 원문에 없는 내용은 사실처럼 쓰지 말 것
- 각 카드 제목은 짧게 작성
- 각 카드 본문은 2~3문장
- 마지막 카드에는 출처와 주의점을 포함
- 결과는 반드시 JSON으로 반환

JSON 형식:
{{
  "article_title": "",
  "source": "",
  "published_date": "",
  "url": "",
  "cards": [
    {{
      "card_no": 1,
      "title": "",
      "body": ""
    }}
  ]
}}

기사 메타데이터:
- 제목: {title}
- 출처: {source}
- 발행일: {published_date}
- URL: {url}

기사 내용:
{article_text}
""".strip()


def generate_card_news(article: dict[str, Any], settings: Settings) -> dict[str, Any]:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY가 없습니다.")

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = CARD_PROMPT_TEMPLATE.format(
        title=article.get("title", ""),
        source=article.get("source", ""),
        published_date=article.get("published_date", ""),
        url=article.get("url", ""),
        article_text=truncate_text(article.get("text", ""), 10000),
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "너는 사내 커뮤니케이션용 카드뉴스 편집자다."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content or "{}"
    result = read_json_from_llm(content)
    result.setdefault("article_title", article.get("title", ""))
    result.setdefault("source", article.get("source", ""))
    result.setdefault("published_date", article.get("published_date", ""))
    result.setdefault("url", article.get("url", ""))
    cards = result.get("cards", [])
    if not isinstance(cards, list) or len(cards) != 5:
        raise ValueError("카드뉴스 JSON은 cards 5개를 포함해야 합니다.")
    return result
