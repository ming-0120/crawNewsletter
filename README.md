# AI/RPA/업무자동화 뉴스 카드뉴스 자동 생성 파이프라인

Tavily로 AI, RPA, AI Agent, MCP, Excel 자동화, 데이터 처리 자동화 관련 최신 기사 후보를 검색하고, OpenAI LLM으로 관련성 판단과 사내 공유용 카드뉴스 생성을 수행합니다.

## 설계 요약

파이프라인은 `검색 -> 중복 제거 -> 본문 추출 -> 관련성 판단 -> 카드뉴스 생성 -> JSON/Markdown/PPTX/PNG 저장` 순서로 동작합니다. 날짜 폴더는 실행 시점의 오늘 날짜를 사용해 `output/YYYY-MM-DD/`에 생성됩니다.

PPTX와 PNG 생성은 선택 출력물입니다. 생성 중 오류가 나도 핵심 결과물인 JSON과 Markdown 저장 흐름은 유지됩니다.

## 설치

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

`.env`에 API Key를 입력합니다.

```bash
TAVILY_API_KEY=...
OPENAI_API_KEY=...
```

## 실행

```bash
python main.py
```

옵션:

```bash
python main.py --limit 10
python main.py --output ./output
python main.py --format markdown,ppt,image
python main.py --format json,markdown
```

## 폴더 구조

```text
news_card_pipeline/
  main.py
  config.py
  search.py
  extract.py
  relevance.py
  card_generator.py
  export_markdown.py
  export_ppt.py
  export_image.py
  utils.py
requirements.txt
.env.example
README.md
main.py
```

## 출력 구조

```text
output/
  YYYY-MM-DD/
    articles.json
    selected_articles.json
    held_articles.json
    card_news.json
    card_news.md
    ppt/
      card_news.pptx
    images/
      article_01_card_01.png
      article_01_card_02.png
```

## 파일별 역할

- `main.py`: CLI 실행 진입점
- `news_card_pipeline/main.py`: 전체 실행 흐름
- `config.py`: API Key, 검색어, 설정값 관리
- `search.py`: Tavily 검색 및 URL 중복 제거
- `extract.py`: 기사 본문 추출
- `relevance.py`: LLM 기반 관련성 판단
- `card_generator.py`: 카드뉴스 JSON 생성
- `export_markdown.py`: Markdown 저장
- `export_ppt.py`: PPTX 저장
- `export_image.py`: PNG 이미지 저장
- `utils.py`: 공통 함수

## 카드뉴스 JSON 예시

```json
{
  "article_title": "기업용 AI 자동화 도구 출시",
  "source": "Example News",
  "published_date": "2026-01-01",
  "url": "https://example.com/article",
  "cards": [
    {
      "card_no": 1,
      "title": "업무 자동화 확대",
      "body": "기업용 AI 도구가 반복 업무를 줄이는 기능을 제공한다고 기사에서 설명합니다."
    },
    {
      "card_no": 2,
      "title": "핵심 내용",
      "body": "문서 작성, 데이터 정리, 업무 흐름 연결 기능이 소개됐습니다. 비개발자도 사용할 수 있는 인터페이스를 강조했습니다."
    },
    {
      "card_no": 3,
      "title": "왜 중요한가",
      "body": "반복적인 사무 작업 시간을 줄일 수 있어 생산성 개선과 관련됩니다. 기사에서 언급한 기능은 팀 단위 업무 흐름 개선에 초점이 있습니다."
    },
    {
      "card_no": 4,
      "title": "적용 아이디어",
      "body": "주간 보고서 초안 작성, 엑셀 데이터 정리, 웹 정보 수집 업무에 우선 적용을 검토할 수 있습니다."
    },
    {
      "card_no": 5,
      "title": "주의와 출처",
      "body": "도입 전 보안, 권한, 데이터 검증 절차를 확인해야 합니다. 출처: Example News, https://example.com/article"
    }
  ]
}
```

## 예외 처리

- API Key가 없으면 실행 초기에 명확한 오류를 냅니다.
- Tavily 검색 실패는 쿼리 단위로 로깅하고 다음 쿼리를 계속 처리합니다.
- 기사 본문 추출 실패, 빈 본문, 너무 짧은 본문은 제외합니다.
- LLM 관련성 응답이 JSON이 아니면 제외 처리합니다.
- URL은 fragment 제거 후 중복 제거합니다.
- PPTX 또는 PNG 생성 실패 시에도 `card_news.json`과 `card_news.md`는 유지됩니다.

## 추후 확장 아이디어

- Slack, Teams, Notion, Confluence 자동 배포
- 보류 기사(`held_articles.json`)를 사람이 검토하는 승인 단계 추가
- RSS, Google News, 사내 구독 매체 API 추가
- 기사 원문 스크린샷 저장
- 카드뉴스 템플릿 테마 다중화
- 주간 리포트 형태의 PDF 생성
- SQLite 또는 PostgreSQL 기반 수집 이력 관리
