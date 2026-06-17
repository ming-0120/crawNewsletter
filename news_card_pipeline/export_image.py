from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .utils import ensure_dir, truncate_text, wrap_text


def _load_font(font_path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        font_path,
        "C:/Windows/Fonts/malgun.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def export_images(card_news_items: list[dict[str, Any]], output_dir: Path, font_path: str | None = None) -> None:
    ensure_dir(output_dir)
    title_font = _load_font(font_path, 58)
    body_font = _load_font(font_path, 38)
    footer_font = _load_font(font_path, 24)

    for article_idx, item in enumerate(card_news_items, start=1):
        source = item.get("source", "")
        for card in item.get("cards", []):
            card_no = int(card.get("card_no", 0))
            image = Image.new("RGB", (1080, 1080), "#F7F9FC")
            draw = ImageDraw.Draw(image)

            draw.rectangle((0, 0, 1080, 130), fill="#16324F")
            draw.rectangle((70, 185, 1010, 850), fill="#FFFFFF", outline="#D9E2EC", width=2)
            draw.rectangle((70, 890, 1010, 1010), fill="#EEF4F8")

            draw.text((70, 40), f"Card {card_no}", fill="#A7D8FF", font=footer_font)
            draw.text((70, 205), wrap_text(card.get("title", ""), 14), fill="#16324F", font=title_font)

            body = wrap_text(truncate_text(card.get("body", ""), 340), 23)
            draw.multiline_text((95, 380), body, fill="#243B53", font=body_font, spacing=16)

            footer = wrap_text(truncate_text(f"{source} | {item.get('url', '')}", 120), 38)
            draw.multiline_text((95, 925), footer, fill="#52606D", font=footer_font, spacing=8)

            filename = output_dir / f"article_{article_idx:02d}_card_{card_no:02d}.png"
            image.save(filename)
