from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import ensure_dir


def export_markdown(card_news_items: list[dict[str, Any]], output_path: Path) -> None:
    ensure_dir(output_path.parent)
    lines = ["# AI 업무 자동화 카드뉴스", ""]

    for article_idx, item in enumerate(card_news_items, start=1):
        title = item.get("article_title", "제목 없음")
        url = item.get("url", "")
        lines.extend(
            [
                f"## 기사 {article_idx}. {title}",
                "",
                f"원문: [{title}]({url})  ",
                f"출처: {item.get('source', '')}  ",
                f"발행일: {item.get('published_date', '')}",
                "",
            ]
        )
        for card in item.get("cards", []):
            lines.extend(
                [
                    f"### 카드 {card.get('card_no')}. {card.get('title', '')}",
                    str(card.get("body", "")),
                    "",
                ]
            )

    output_path.write_text("\n".join(lines), encoding="utf-8")
