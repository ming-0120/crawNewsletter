from __future__ import annotations

import json
from typing import Any

from langchain_openai import ChatOpenAI

from .utils import read_json_from_llm, truncate_text


def _article_payload(articles: list[dict[str, Any]]) -> str:
    payload = []
    for index, article in enumerate(articles, start=1):
        payload.append(
            {
                "article_no": index,
                "title": article.get("title", ""),
                "source": article.get("source", ""),
                "published_date": article.get("published_date", ""),
                "url": article.get("url", ""),
                "content": truncate_text(article.get("text") or article.get("snippet", ""), 4000),
            }
        )
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_article_based_prompt(articles: list[dict[str, Any]]) -> str:
    return f"""
당신은 사내 뉴스레터용 카드뉴스 편집자입니다.

주제 질문:
"사내에서 현재 AI를 어떤 업무까지 사용하고 있는지"

아래 기사들만 근거로 사용해 카드뉴스 문안을 작성하세요.
회사의 실제 내부 사용 현황을 알고 있는 것처럼 단정하지 마세요.
기사에서 확인되는 기업 AI 활용 흐름을 바탕으로 "우리 회사에서 점검해볼 업무 범위"처럼 표현하세요.

작성 조건:
- 출력 언어: 한국어
- 대상: 비개발자 포함 전사 직원
- 톤: 쉽고 명확하게
- 과장 금지
- 기사에 없는 사실을 사실처럼 쓰지 말 것
- HTML 카드에 들어가므로 각 문구는 짧게 쓸 것
- 결과는 반드시 JSON만 반환

HTML 템플릿 구조:
1. cover: 첫 표지
2. data_view: 기사 기반 흐름 요약
3. key_message: 핵심 메시지
4. cta: 사내 점검 질문과 출처 표시

JSON 형식:
{{
  "page_title": "",
  "cover": {{
    "eyebrow": "",
    "title": ""
  }},
  "data_view": {{
    "label": "",
    "title": "",
    "subtitle": ""
  }},
  "key_message": {{
    "label": "",
    "quote_before": "",
    "strong_text": "",
    "quote_after": "",
    "summary": ""
  }},
  "cta": {{
    "title": "",
    "body": "",
    "brand_left": "",
    "brand_right": ""
  }},
  "sources": [
    {{
      "title": "",
      "source": "",
      "published_date": "",
      "url": ""
    }}
  ]
}}

기사 목록:
{_article_payload(articles)}
""".strip()


def generate_internal_ai_usage_content(articles: list[dict[str, Any]]) -> dict[str, Any]:
    if not articles:
        raise ValueError("OpenAI에 전달할 기사 목록이 비어 있습니다.")

    llm_light = ChatOpenAI(model="gpt-5.1", temperature=0, max_tokens=25000)
    response = llm_light.invoke(build_article_based_prompt(articles))
    content = response.content
    if isinstance(content, list):
        content = "".join(str(item) for item in content)
    return read_json_from_llm(str(content))
