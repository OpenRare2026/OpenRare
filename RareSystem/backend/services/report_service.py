"""
Rare Disease Report Generation Service.
Generates clinical-grade gene prioritization reports via SSE streaming.

The external Report microservice expects file PATHS (not CSV content)
because it uses pd.read_csv(path) internally. This service passes file
paths directly and writes HPO terms to a temporary file for the
hpo_path parameter.
"""
import logging
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Generator, Dict, Any
import requests
import httpx

from config import (
    REPORT_API_BASE_URL,
    REPORT_POLL_INTERVAL,
    REPORT_MAX_DURATION,
)

logger = logging.getLogger(__name__)


@dataclass
class ReportMeta:
    run_id: str = ""
    genes: List[str] = field(default_factory=list)
    pheno_coverage: float = 0.0
    ppi_coverage: float = 0.0


@dataclass
class ReportChunk:
    chunk_type: str
    slot: str = ""
    text: str = ""


@dataclass
class ReportResult:
    run_id: str
    pdf_url: str
    markdown: str = ""
    meta: Optional[ReportMeta] = None


class ReportServiceError(Exception):
    pass


class ReportService:
    def __init__(
        self,
        base_url: str = REPORT_API_BASE_URL,
        poll_interval: int = REPORT_POLL_INTERVAL,
        max_duration: int = REPORT_MAX_DURATION,
    ):
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.max_duration = max_duration
        self._temp_files: List[str] = []

    def _write_hpo_temp_file(self, hpo_ids: List[str]) -> str:
        """Write HPO IDs to a temporary file and return its path."""
        content = "\n".join(hpo_ids)
        fd, path = tempfile.mkstemp(suffix=".hpo", prefix="rdr_hpo_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(path, 0o644)
        self._temp_files.append(path)
        logger.info(f"Wrote {len(hpo_ids)} HPO terms to temp file: {path}")
        return path

    def cleanup(self):
        """Remove temporary files created during report generation."""
        for path in self._temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"Cleaned up temp file: {path}")
            except OSError:
                pass
        self._temp_files.clear()

    def stream_report(
        self,
        wide_csv_path: str,
        phenotype_csv_path: Optional[str] = None,
        ppi_csv_path: Optional[str] = None,
        hpo_ids: Optional[List[str]] = None,
        top_n: int = 10,
    ) -> Generator[Dict[str, Any], None, None]:
        """Stream report generation via SSE.

        Args:
            wide_csv_path: File path to the wide (VEP/ranked result) CSV.
            phenotype_csv_path: File path to the gene-phenotype score CSV (optional).
            ppi_csv_path: File path to the PPI score CSV (optional).
            hpo_ids: List of HPO term IDs (e.g. ["HP:0001250"]).
            top_n: Number of top genes to include.
        """
        url = f"{self.base_url}/report/stream"

        data: Dict[str, Any] = {
            "wide_path": wide_csv_path,
            "top_n": top_n,
        }

        if phenotype_csv_path:
            data["phenotype_path"] = phenotype_csv_path
            logger.info(f"Included phenotype CSV path: {phenotype_csv_path}")

        if ppi_csv_path:
            data["ppi_path"] = ppi_csv_path
            logger.info(f"Included PPI CSV path: {ppi_csv_path}")

        if hpo_ids:
            hpo_temp_path = self._write_hpo_temp_file(hpo_ids)
            data["hpo_path"] = hpo_temp_path
            logger.info(f"Included HPO file: {len(hpo_ids)} terms via temp file {hpo_temp_path}")

        logger.info(f"Report API request: {url}, payload keys: {list(data.keys())}")

        path_keys = {"wide_path", "phenotype_path", "ppi_path", "hpo_path"}
        for key, val in data.items():
            if key not in path_keys:
                continue
            p = Path(val)
            if p.exists():
                size = p.stat().st_size
                logger.info(f"Report payload [{key}]: EXISTS, size={size} bytes, path={val}")
            else:
                logger.error(f"Report payload [{key}]: MISSING ON DISK, path={val}")

        try:
            response = requests.post(
                url,
                json=data,
                stream=True,
                timeout=(120, 600)
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                line_str = line.decode('utf-8').strip()
                if not line_str or line_str.startswith(":"):
                    continue

                if line_str.startswith("data:"):
                    data_str = line_str[5:].strip()
                    if data_str:
                        try:
                            event = json.loads(data_str)
                            event_type = event.get("type", "")
                            if event_type == "meta":
                                logger.info(f"Report job started: run_id={event.get('run_id', 'N/A')}")
                            elif event_type == "error":
                                logger.error(f"Report job error: {event.get('message', 'unknown')}")
                            elif event_type == "done":
                                logger.info(f"Report job done: run_id={event.get('run_id', 'N/A')}, pdf_url={event.get('pdf_url', 'N/A')}")
                            yield event
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse SSE data: {e}")
                            continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Report API request failed: {e}")
            raise ReportServiceError(f"Report API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error streaming report: {e}")
            raise ReportServiceError(f"Report streaming failed: {e}")

    def generate_report(
        self,
        wide_csv_path: str,
        phenotype_csv_path: Optional[str] = None,
        ppi_csv_path: Optional[str] = None,
        hpo_ids: Optional[List[str]] = None,
        top_n: int = 10,
    ) -> ReportResult:
        markdown_parts = []
        meta = None
        pdf_url = ""
        run_id = ""

        for event in self.stream_report(
            wide_csv_path=wide_csv_path,
            phenotype_csv_path=phenotype_csv_path,
            ppi_csv_path=ppi_csv_path,
            hpo_ids=hpo_ids,
            top_n=top_n,
        ):
            event_type = event.get("type", "")

            if event_type == "meta":
                meta = ReportMeta(
                    run_id=event.get("run_id", ""),
                    genes=event.get("genes", []),
                    pheno_coverage=event.get("pheno_coverage", 0.0),
                    ppi_coverage=event.get("ppi_coverage", 0.0),
                )
                run_id = meta.run_id

            elif event_type == "md":
                text = event.get("text", "")
                markdown_parts.append(text)

            elif event_type == "done":
                pdf_url = event.get("pdf_url", "")
                md_url = event.get("md_url", "")
                # Some report services return md_url instead of pdf_url
                if not pdf_url and md_url:
                    pdf_url = md_url
                if not run_id:
                    run_id = event.get("run_id", "")

        try:
            return ReportResult(
                run_id=run_id,
                pdf_url=pdf_url,
                markdown="".join(markdown_parts),
                meta=meta,
            )
        finally:
            self.cleanup()

    async def get_markdown(self, run_id: str) -> str:
        """Fetch markdown content for a report run from the external service."""
        md_url = f"{self.base_url}/report/{run_id}/md"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(md_url)
                resp.raise_for_status()
                logger.info(f"Fetched markdown for run_id={run_id}, length={len(resp.text)} chars")
                return resp.text
        except Exception as e:
            logger.error(f"Failed to fetch markdown for run_id={run_id}: {e}")
            raise ReportServiceError(f"Markdown not available for run_id={run_id}: {e}")

    async def get_pdf(self, run_id: str) -> bytes:
        """Fetch PDF content for a report run.

        Tries the /pdf endpoint first; if unavailable (404), falls back
        to the /md endpoint and converts markdown to a simple HTML page.
        """
        # Try PDF endpoint first
        pdf_url = f"{self.base_url}/report/{run_id}/pdf"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(pdf_url)
                if resp.status_code == 200:
                    return resp.content
        except httpx.HTTPStatusError:
            pass
        except Exception:
            pass

        # Fallback: fetch markdown and wrap in HTML for download
        md_url = f"{self.base_url}/report/{run_id}/md"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(md_url)
                resp.raise_for_status()
                md_content = resp.text

            # Convert markdown to a minimal HTML document
            html_content = self._markdown_to_html(md_content, run_id)
            return html_content.encode("utf-8")
        except Exception as e:
            logger.error(f"Failed to fetch report content for run_id={run_id}: {e}")
            raise ReportServiceError(f"Report content not available for run_id={run_id}")

    @staticmethod
    def _markdown_to_html(markdown: str, run_id: str = "") -> str:
        """Convert markdown to a minimal HTML document for download."""
        import re

        # Basic markdown-to-HTML: headers, bold, tables, code blocks, paragraphs
        lines = markdown.split("\n")
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='zh-CN'><head>",
            "<meta charset='UTF-8'>",
            f"<title>Report {run_id}</title>",
            "<style>",
            "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; "
            "max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #333; }",
            "table { border-collapse: collapse; width: 100%; margin: 16px 0; }",
            "th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }",
            "th { background: #f5f5f5; font-weight: 600; }",
            "tr:nth-child(even) { background: #fafafa; }",
            "code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }",
            "pre { background: #f4f4f4; padding: 16px; border-radius: 6px; overflow-x: auto; }",
            "pre code { background: none; padding: 0; }",
            "blockquote { border-left: 4px solid #ddd; margin: 16px 0; padding: 8px 16px; color: #666; }",
            "h1 { border-bottom: 2px solid #1890ff; padding-bottom: 8px; }",
            "h2 { border-bottom: 1px solid #eee; padding-bottom: 6px; }",
            "</style></head><body>",
        ]

        in_code_block = False
        code_buffer = []

        for line in lines:
            # Code block toggle
            if line.strip().startswith("```"):
                if in_code_block:
                    html_parts.append(f"<pre><code>{chr(10).join(code_buffer)}</code></pre>")
                    code_buffer = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            # Headers
            if line.startswith("#### "):
                html_parts.append(f"<h4>{line[5:]}</h4>")
            elif line.startswith("### "):
                html_parts.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("## "):
                html_parts.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("# "):
                html_parts.append(f"<h1>{line[2:]}</h1>")
            # Table rows
            elif line.strip().startswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if all(set(c) <= {"-", ":", " "} for c in cells):
                    continue  # skip separator row
                tag = "th" if not html_parts or html_parts[-1].startswith("<h") else "td"
                row = "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"
                html_parts.append(row)
            # Blockquote
            elif line.startswith("> "):
                html_parts.append(f"<blockquote>{line[2:]}</blockquote>")
            # Horizontal rule
            elif line.strip() == "---":
                html_parts.append("<hr>")
            # Empty line
            elif not line.strip():
                html_parts.append("<br>")
            # Regular paragraph
            else:
                # Bold
                line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
                # Inline code
                line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)
                html_parts.append(f"<p>{line}</p>")

        html_parts.append("</body></html>")
        return "\n".join(html_parts)

    async def health_check(self) -> bool:
        url = f"{self.base_url}/health"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                return resp.status_code == 200
        except Exception:
            return False
