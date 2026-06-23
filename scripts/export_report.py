#!/usr/bin/env python3
"""Export Final Report Markdown to HTML (web) and PDF."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = PROJECT_ROOT / "scripts" / "export"
DEFAULT_CSS = EXPORT_DIR / "report.css"
TYPST_PREAMBLE = EXPORT_DIR / "typst_preamble.typ"
TOOLS_BIN = PROJECT_ROOT / "tools" / "bin"
BUNDLED_FONTS_DIR = PROJECT_ROOT / "tools" / "fonts"
BUNDLED_CJK_FONT = BUNDLED_FONTS_DIR / "NotoSansSC-Regular.otf"
BUNDLED_CJK_FONT_URL = (
    "https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/SubsetOTF/SC/NotoSansSC-Regular.otf"
)
CJK_MAIN_FONT = "Noto Sans SC"
CJK_MONO_FONT = "Noto Sans SC"

_VARIANT_LIST_HEADER_COMPACT = (
    "| 变异 | 转录本 / 后果 | GENOS-EVEE | 评分 | ClinVar（VAF） |\n"
    "|------|---------------|------------|------|----------------|"
)


def _is_variant_list_header(cells: list[str]) -> bool:
    if len(cells) < 6:
        return False
    if cells[0] != "变异":
        return False
    if len(cells) >= 9:
        return "坐标" in cells[1] and cells[2] == "转录本"
    return cells[1] in ("转录本", "转录本 / 后果") and cells[2] in (
        "后果",
        "评分",
        "GENOS-EVEE",
    )


def _pdf_display(value: str) -> str:
    text = value.strip().strip("*")
    return "无" if text in ("-", "") else text


def _compact_variant_row(cells: list[str]) -> list[str] | None:
    if len(cells) >= 9:
        label, transcript, consequence, cadd, clinvar, vaf = (
            cells[0],
            cells[2],
            cells[3],
            cells[4],
            cells[7],
            cells[8],
        )
        genos = "-"
    elif len(cells) == 6:
        label, transcript, consequence, cadd, clinvar, vaf = cells[:6]
        genos = "-"
    elif len(cells) == 5 and cells[2] not in ("GENOS-EVEE",):
        label, transcript, consequence, cadd, clinvar, vaf = (
            cells[0],
            cells[1],
            cells[2],
            cells[3],
            cells[4],
            "",
        )
        genos = "-"
    elif len(cells) == 5 and cells[2] == "GENOS-EVEE":
        return None
    elif len(cells) == 4 and (" · " in cells[1] or "<br>" in cells[1]):
        return None
    else:
        return None

    if "<br>" in transcript or " · " in transcript:
        annot = transcript.replace("<br>", " · ")
    else:
        annot = f"{transcript} · {consequence}"
    vaf_clean = vaf.strip().strip("*")
    clin_text = _pdf_display(clinvar)
    vaf_text = _pdf_display(vaf_clean)
    cadd_text = _pdf_display(cadd)
    return [
        label,
        annot,
        _pdf_display(genos),
        f"CADD {cadd_text}",
        f"{clin_text}（VAF {vaf_text}）",
    ]


def _is_attribute_table_header(cells: list[str]) -> bool:
    return len(cells) == 2 and cells[0] == "属性" and cells[1] == "内容"


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [part.strip() for part in stripped.strip("|").split("|")]


def _join_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _extract_evidence_block(content: str) -> tuple[str, list[str]]:
    """Move long 证据摘要 out of 2-column tables into a fenced code block."""
    from report.render import _parse_evidence_tree

    extra: list[str] = []
    if content in ("-", "", "见下方评分分解"):
        return content, extra
    if len(content) < 60:
        return content, extra

    extra.extend(["", "**证据摘要**", "", "```", _parse_evidence_tree(content), "```", ""])
    return "见下方评分分解", extra


def preprocess_markdown_for_pdf(markdown: str) -> str:
    """Normalize wide tables for PDF export (column overlap fixes)."""
    lines = markdown.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        header_cells = _split_table_row(line)

        if _is_variant_list_header(header_cells):
            output.append(_VARIANT_LIST_HEADER_COMPACT)
            index += 1
            if index < len(lines) and lines[index].strip().startswith("|------"):
                index += 1
            while index < len(lines):
                row = lines[index]
                if not row.strip().startswith("|") or row.strip().startswith("|------"):
                    break
                cells = _split_table_row(row)
                compact = _compact_variant_row(cells)
                if compact:
                    output.append(_join_table_row(compact))
                else:
                    output.append(row)
                index += 1
            continue

        if _is_attribute_table_header(header_cells):
            table_lines = [line]
            index += 1
            if index < len(lines) and lines[index].strip().startswith("|------"):
                table_lines.append(lines[index])
                index += 1
            pending_evidence: list[str] = []
            while index < len(lines):
                row = lines[index]
                if not row.strip().startswith("|") or row.strip().startswith("|------"):
                    break
                cells = _split_table_row(row)
                if len(cells) == 2 and cells[0] == "证据摘要":
                    short, extra = _extract_evidence_block(cells[1])
                    table_lines.append(_join_table_row([cells[0], short]))
                    pending_evidence.extend(extra)
                else:
                    table_lines.append(row)
                index += 1
            output.extend(table_lines)
            output.extend(pending_evidence)
            continue

        output.append(line)
        index += 1

    return "\n".join(output) + ("\n" if markdown.endswith("\n") else "")


def _resolve_path(path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = PROJECT_ROOT / resolved
    return resolved.resolve()


def _find_typst() -> str | None:
    for candidate in (
        TOOLS_BIN / "typst",
        Path(os.environ.get("TYPST_BIN", "")),
    ):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return shutil.which("typst")


def _ensure_cjk_font() -> Path | None:
    """Ensure bundled Noto Sans SC exists for Typst PDF export."""
    if BUNDLED_CJK_FONT.is_file() and BUNDLED_CJK_FONT.stat().st_size > 0:
        return BUNDLED_CJK_FONT

    BUNDLED_FONTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import urllib.request

        print(f"  Downloading CJK font -> {BUNDLED_CJK_FONT}")
        urllib.request.urlretrieve(BUNDLED_CJK_FONT_URL, BUNDLED_CJK_FONT)
    except OSError as exc:
        print(f"  Warning: failed to download CJK font ({exc})", file=sys.stderr)
        return None

    if BUNDLED_CJK_FONT.is_file() and BUNDLED_CJK_FONT.stat().st_size > 0:
        return BUNDLED_CJK_FONT
    return None


def _pick_cjk_font() -> tuple[str, str, Path | None]:
    """Return (mainfont, monofont, font_dir) for Pandoc/Typst."""
    candidates = [
        (CJK_MAIN_FONT, CJK_MONO_FONT),
        ("Noto Sans CJK SC", "Noto Sans Mono CJK SC"),
        ("Source Han Sans SC", "Source Han Sans SC"),
        ("WenQuanYi Micro Hei", "WenQuanYi Micro Hei Mono"),
        ("DejaVu Sans", "DejaVu Sans Mono"),
    ]

    bundled = _ensure_cjk_font()
    if bundled:
        return CJK_MAIN_FONT, CJK_MONO_FONT, BUNDLED_FONTS_DIR

    try:
        output = subprocess.check_output(["fc-list", ":lang=zh", "family"], text=True)
        families = {line.split(",")[0].strip() for line in output.splitlines() if line.strip()}
        for main, mono in candidates:
            if main in families:
                return main, mono if mono in families else main, None
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return candidates[-1][0], candidates[-1][1], None


def export_html(md_path: Path, html_path: Path, *, title: str | None = None) -> None:
    import pypandoc

    doc_title = title or md_path.stem
    css_path = DEFAULT_CSS.resolve()
    extra_args = [
        "--standalone",
        "--embed-resources",
        f"--css={css_path}",
        "--metadata",
        f"title={doc_title}",
        "--toc",
        "--toc-depth=3",
        "--from=markdown+pipe_tables+table_captions+yaml_metadata_block",
    ]

    html = pypandoc.convert_file(str(md_path), "html5", format="md", extra_args=extra_args)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    # Keep a sibling stylesheet for browsers that prefer external CSS.
    bundled_css = html_path.with_name("report.css")
    if bundled_css.resolve() != css_path.resolve():
        shutil.copy2(css_path, bundled_css)


def export_pdf_typst(md_path: Path, pdf_path: Path, *, title: str | None = None) -> None:
    import pypandoc

    typst_bin = _find_typst()
    if not typst_bin:
        raise RuntimeError(
            "Typst CLI not found. Install typst or place binary at tools/bin/typst"
        )

    mainfont, monofont, font_dir = _pick_cjk_font()
    doc_title = title or md_path.stem
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    md_text = preprocess_markdown_for_pdf(md_path.read_text(encoding="utf-8"))
    pdf_source = md_path.with_name(f"{md_path.stem}.export.pdf.md")
    pdf_source.write_text(md_text, encoding="utf-8")

    extra_args = [
        "--pdf-engine=typst",
        "--from=markdown+pipe_tables+table_captions+yaml_metadata_block",
        "-V",
        f"title={doc_title}",
        "-V",
        "lang=zh",
        "-V",
        "region=CN",
        "-V",
        f"mainfont={mainfont}",
        "-V",
        f"monofont={monofont}",
        "-V",
        "papersize=a4",
        "-V",
        "margin-top=2cm",
        "-V",
        "margin-bottom=2cm",
        "-V",
        "margin-left=2.2cm",
        "-V",
        "margin-right=2.2cm",
        "-V",
        "fontsize=11pt",
    ]

    if TYPST_PREAMBLE.is_file():
        extra_args.extend(["--include-in-header", str(TYPST_PREAMBLE.resolve())])

    env = os.environ.copy()
    env["PATH"] = f"{Path(typst_bin).parent}:{env.get('PATH', '')}"
    if font_dir:
        env["TYPST_FONT_PATHS"] = str(font_dir.resolve())

    old_path = os.environ.get("PATH")
    old_font_paths = os.environ.get("TYPST_FONT_PATHS")
    os.environ["PATH"] = env["PATH"]
    if font_dir:
        os.environ["TYPST_FONT_PATHS"] = env["TYPST_FONT_PATHS"]
    try:
        pypandoc.convert_file(
            str(pdf_source),
            "pdf",
            format="md",
            outputfile=str(pdf_path),
            extra_args=extra_args,
        )
    finally:
        if old_path is None:
            os.environ.pop("PATH", None)
        else:
            os.environ["PATH"] = old_path
        if old_font_paths is None:
            os.environ.pop("TYPST_FONT_PATHS", None)
        else:
            os.environ["TYPST_FONT_PATHS"] = old_font_paths
        if pdf_source.is_file():
            pdf_source.unlink()


def export_pdf_chrome(md_path: Path, pdf_path: Path) -> None:
    """Fallback: md-to-pdf (Puppeteer) when Typst is unavailable."""
    css_path = DEFAULT_CSS.resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "npx",
        "--yes",
        "md-to-pdf",
        str(md_path),
        "--stylesheet",
        str(css_path),
        "--pdf-options",
        '{"format":"A4","printBackground":true,"margin":{"top":"18mm","bottom":"18mm","left":"16mm","right":"16mm"}}',
    ]
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)
    generated = md_path.with_suffix(".pdf")
    if generated != pdf_path and generated.exists():
        generated.replace(pdf_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export report.md to HTML and/or PDF.")
    parser.add_argument(
        "markdown",
        nargs="?",
        default="test_data/output/25B06715455_v1/report.md",
        help="Input Markdown report path.",
    )
    parser.add_argument(
        "--html",
        nargs="?",
        const="auto",
        default=None,
        help="Output HTML path (default: same dir as input, report.html).",
    )
    parser.add_argument(
        "--pdf",
        nargs="?",
        const="auto",
        default=None,
        help="Output PDF path (default: same dir as input, report.pdf).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Document title metadata.",
    )
    parser.add_argument(
        "--pdf-engine",
        choices=("typst", "chrome", "auto"),
        default="auto",
        help="PDF backend: typst (recommended), chrome (md-to-pdf), or auto.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export both HTML and PDF next to the input file.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    md_path = _resolve_path(args.markdown)
    if not md_path.exists():
        print(f"Markdown not found: {md_path}", file=sys.stderr)
        return 1

    out_dir = md_path.parent
    title = args.title

    want_html = args.all or args.html is not None
    want_pdf = args.all or args.pdf is not None

    if not want_html and not want_pdf:
        want_html = want_pdf = True

    if want_html:
        html_path = out_dir / "report.html" if args.html in (None, "auto") else _resolve_path(args.html)
        print(f"Exporting HTML -> {html_path}")
        export_html(md_path, html_path, title=title)
        print("  OK")

    if want_pdf:
        pdf_path = out_dir / "report.pdf" if args.pdf in (None, "auto") else _resolve_path(args.pdf)
        engine = args.pdf_engine
        if engine == "auto":
            engine = "typst" if _find_typst() else "chrome"

        print(f"Exporting PDF ({engine}) -> {pdf_path}")
        try:
            if engine == "typst":
                export_pdf_typst(md_path, pdf_path, title=title)
            else:
                export_pdf_chrome(md_path, pdf_path)
        except Exception as exc:
            if engine == "typst" and args.pdf_engine == "auto":
                print(f"  Typst failed ({exc}); falling back to md-to-pdf...")
                export_pdf_chrome(md_path, pdf_path)
            else:
                raise
        print("  OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
