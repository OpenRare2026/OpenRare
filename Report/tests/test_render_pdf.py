"""Tests for the Markdown-to-PDF rendering pipeline."""
import tempfile
from pathlib import Path
from scripts.render_pdf import md_to_pdf, CSS_PATH

SAMPLE_MD = """# 罕见病候选基因分析报告

> 探索性报告，非临床诊断结论。

## 临床表型概述

患者为3岁男童，临床主要表现为反复呼吸道感染。

## 候选基因 1：CFTR

### 变异证据（宽表）

| rank | 变异 | consequence | impact | CADD |
| --- | --- | --- | --- | --- |
| 1 | p.Phe508del | frameshift_variant | HIGH | 32 |
"""


class TestRenderPDF:
    def test_basic_pdf_generation(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name

        try:
            result = md_to_pdf(SAMPLE_MD, pdf_path)
            assert result == pdf_path
            assert Path(pdf_path).exists()
            assert Path(pdf_path).stat().st_size > 0
        finally:
            Path(pdf_path).unlink(missing_ok=True)

    def test_pdf_with_chinese_text(self):
        md = "# 测试\n\n这是一段中文测试文本。\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n"
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name

        try:
            result = md_to_pdf(md, pdf_path)
            assert Path(pdf_path).stat().st_size > 0
        finally:
            Path(pdf_path).unlink(missing_ok=True)

    def test_custom_css(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name

        try:
            result = md_to_pdf(SAMPLE_MD, pdf_path, css_path=CSS_PATH)
            assert Path(pdf_path).stat().st_size > 0
        finally:
            Path(pdf_path).unlink(missing_ok=True)

    def test_css_file_exists(self):
        assert CSS_PATH.exists()
        css = CSS_PATH.read_text()
        assert "@font-face" in css
        assert "WenQuanYiZenHei" in css

    def test_empty_md_renders(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name

        try:
            result = md_to_pdf("# Empty\n", pdf_path)
            assert Path(pdf_path).stat().st_size > 0
        finally:
            Path(pdf_path).unlink(missing_ok=True)
