from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from .utils import ensure_dir


def _read_template(template_path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return template_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return template_path.read_text(encoding="utf-8", errors="replace")


def _style_from_template(template_html: str) -> str:
    match = re.search(r"<style>(.*?)</style>", template_html, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _br(text: str) -> str:
    return "<br />".join(html.escape(line.strip()) for line in text.splitlines() if line.strip())


def _after_quote(text: str) -> str:
    escaped = _br(text)
    return f"<br />{escaped}" if escaped else ""


def render_magazine_html(content: dict[str, Any], template_path: Path, output_path: Path) -> None:
    template_html = _read_template(template_path)
    style = _style_from_template(template_html)
    ensure_dir(output_path.parent)

    cover = content.get("cover", {})
    data_view = content.get("data_view", {})
    key_message = content.get("key_message", {})
    cta = content.get("cta", {})

    page_title = html.escape(content.get("page_title", "AI usage insight"))
    rendered = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  <style>
{style}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="card">
      <div class="full-image"></div>
      <div class="cover-gradient"></div>
      <div class="cover-title">
        <div class="eyebrow">{html.escape(cover.get("eyebrow", ""))}</div>
        <h1>{_br(cover.get("title", ""))}</h1>
      </div>
    </section>

    <section class="card">
      <div class="page-label">{html.escape(data_view.get("label", ""))}</div>
      <div class="content-top">
        <h2>{_br(data_view.get("title", ""))}</h2>
        <p class="subtitle">{html.escape(data_view.get("subtitle", ""))}</p>
      </div>
      <div class="media-frame">
        <div class="mock-window">
          <div class="window-bar"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
          <div class="dashboard">
            <div class="chart"></div>
            <div class="panel">
              <div class="line short"></div>
              <div class="line"></div>
              <div class="line"></div>
              <div class="line" style="width:72%"></div>
              <div class="line" style="width:88%"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="card">
      <div class="text-card">
        <div class="page-label" style="top:64px;left:86px;">{html.escape(key_message.get("label", ""))}</div>
        <div class="quote-box">
          <p>{_br(key_message.get("quote_before", ""))}<br /><strong>{html.escape(key_message.get("strong_text", ""))}</strong>{_after_quote(key_message.get("quote_after", ""))}</p>
        </div>
        <div class="summary-pill">{html.escape(key_message.get("summary", ""))}</div>
      </div>
    </section>

    <section class="card">
      <div class="cta">
        <div>
          <h2>{_br(cta.get("title", ""))}</h2>
          <p>{html.escape(cta.get("body", ""))}</p>
        </div>
      </div>
      <div class="brand"><span>{html.escape(cta.get("brand_left", ""))}</span><span>{html.escape(cta.get("brand_right", ""))}</span></div>
    </section>
  </main>
</body>
</html>
"""
    output_path.write_text(rendered, encoding="utf-8")
