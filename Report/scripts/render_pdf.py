#!/usr/bin/env python3
"""
Render a finished report markdown file to PDF.

markdown -> HTML -> PDF via xhtml2pdf (pisa). xhtml2pdf is built on reportlab and
is pure-pip: NO system libraries (no pango/cairo, no fontconfig). To show Chinese
it needs a CJK TrueType font, which travels WITH this skill at
``assets/fonts/NotoSansSC-Regular.ttf`` and is registered through the CSS
``@font-face`` + a ``link_callback`` that resolves the relative url to that file.

"Zero system deps" does not mean "zero font file" — the .ttf is bundled on purpose
so the skill renders Chinese on a bare server. Swap the font by dropping another
.ttf into assets/fonts/ and pointing report.css / --font at it.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import markdown
from xhtml2pdf import pisa

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
CSS_PATH = ASSETS / "report.css"

FOOTER = ('<div id="footerContent" class="footer">'
          '罕见病候选基因分析报告 · 探索性结果，非临床诊断 &nbsp;·&nbsp; '
          '<pdf:pagenumber> / <pdf:pagecount></div>')


def _link_callback(uri, rel):
    """Resolve relative urls in CSS/HTML (e.g. fonts/...) to absolute file paths."""
    p = (ASSETS / uri)
    if p.exists():
        return str(p.resolve())
    p2 = (SKILL_DIR / uri)
    return str(p2.resolve()) if p2.exists() else uri


def md_to_pdf(md_text: str, pdf_path: str, css_path: str | Path = None) -> str:
    html_body = markdown.markdown(
        md_text, extensions=["tables", "fenced_code", "sane_lists"]
    )
    css = Path(css_path or CSS_PATH).read_text(encoding="utf-8")
    html = (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{css}</style></head><body>{FOOTER}{html_body}</body></html>")
    with open(pdf_path, "wb") as f:
        result = pisa.CreatePDF(html, dest=f, link_callback=_link_callback,
                                encoding="utf-8")
    if result.err:
        raise RuntimeError(f"xhtml2pdf reported {result.err} error(s)")
    return pdf_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True, help="filled report markdown")
    ap.add_argument("--pdf", required=True, help="output pdf path")
    ap.add_argument("--css", default=None)
    a = ap.parse_args()
    md_to_pdf(Path(a.md).read_text(encoding="utf-8"), a.pdf, a.css)
    print(f"wrote {a.pdf}")


if __name__ == "__main__":
    main()
