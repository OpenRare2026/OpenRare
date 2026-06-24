"""
Rare Disease Report Generation Service.
Generates clinical-grade gene prioritization reports via SSE streaming.
"""
import asyncio
import logging
import json
import os
import tempfile
import requests
from dataclasses import dataclass, field
from typing import List, Optional, Generator, Dict, Any
import httpx

from config import (
    REPORT_API_BASE_URL,
    REPORT_POLL_INTERVAL,
    REPORT_MAX_DURATION,
)

logger = logging.getLogger(__name__)

REPORT_SHARED_DIR = "/tmp/rdr_runs"


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
        os.makedirs(REPORT_SHARED_DIR, exist_ok=True)

    def _write_temp_file(self, content: str, suffix: str = ".csv") -> str:
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        filename = f"hujie_{unique_id}{suffix}"
        path = os.path.join(REPORT_SHARED_DIR, filename)
        
        with open(path, 'w') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(path, 0o644)
        
        logger.info(f"Created file {path}: {len(content)} bytes")
        return path

    def cleanup(self):
        pass

    def stream_report(
        self,
        wide_csv_content: str,
        phenotype_csv_content: Optional[str] = None,
        ppi_csv_content: Optional[str] = None,
        hpo_ids: Optional[List[str]] = None,
        symptom_text: Optional[str] = None,
        case_id: Optional[str] = None,
        genes: Optional[List[str]] = None,
        top_n: int = 10,
        k: int = 5,
    ) -> Generator[Dict[str, Any], None, None]:
        url = f"{self.base_url}/report/stream"
        
        wide_path = self._write_temp_file(wide_csv_content, suffix="_wide.csv")
        
        payload = {
            "wide": wide_path,
            "top_n": top_n,
            "k": k,
        }
        
        if phenotype_csv_content:
            phenotype_path = self._write_temp_file(phenotype_csv_content, suffix="_phenotype.csv")
            payload["phenotype"] = phenotype_path
            logger.info(f"Written phenotype CSV to {phenotype_path}")
        
        if ppi_csv_content:
            ppi_path = self._write_temp_file(ppi_csv_content, suffix="_ppi.csv")
            payload["ppi"] = ppi_path
            logger.info(f"Written PPI CSV to {ppi_path}")
        
        if hpo_ids:
            hpo_content = "\n".join(hpo_ids)
            hpo_path = self._write_temp_file(hpo_content, suffix="_hpo.txt")
            payload["hpo_file"] = hpo_path
            logger.info(f"Written HPO file to {hpo_path}: {len(hpo_ids)} terms")
        
        if symptom_text:
            payload["symptom_text"] = symptom_text
        
        if case_id:
            payload["case_id"] = case_id
        
        if genes:
            payload["genes"] = ",".join(genes)
        
        logger.info(f"Report API request: {url}")
        logger.info(f"Payload: wide={wide_path}, phenotype={'yes' if phenotype_csv_content else 'no'}, ppi={'yes' if ppi_csv_content else 'no'}, hpo={'yes' if hpo_ids else 'no'}")
        
        try:
            response = requests.post(
                url,
                json=payload,
                stream=True,
                timeout=(120, 3600)
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
        wide_csv_content: str,
        phenotype_csv_content: Optional[str] = None,
        ppi_csv_content: Optional[str] = None,
        hpo_ids: Optional[List[str]] = None,
        symptom_text: Optional[str] = None,
        case_id: Optional[str] = None,
        genes: Optional[List[str]] = None,
        top_n: int = 10,
        k: int = 5,
    ) -> ReportResult:
        markdown_parts = []
        meta = None
        pdf_url = ""
        run_id = ""
        
        for event in self.stream_report(
            wide_csv_content=wide_csv_content,
            phenotype_csv_content=phenotype_csv_content,
            ppi_csv_content=ppi_csv_content,
            hpo_ids=hpo_ids,
            symptom_text=symptom_text,
            case_id=case_id,
            genes=genes,
            top_n=top_n,
            k=k,
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
                if not run_id:
                    run_id = event.get("run_id", "")
        
        return ReportResult(
            run_id=run_id,
            pdf_url=pdf_url,
            markdown="".join(markdown_parts),
            meta=meta,
        )

    async def get_pdf(self, run_id: str) -> bytes:
        url = f"{self.base_url}/report/{run_id}/pdf"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content

    async def health_check(self) -> bool:
        url = f"{self.base_url}/health"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                return resp.status_code == 200
        except Exception:
            return False
