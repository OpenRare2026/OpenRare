"""
VEP API Service Client — submit VCF files, poll job status, fetch results.

Adapted to the OpenRare V3 Queued Pipeline API:
  POST /run-upload   — submit VCF file (multipart, field: input_vcf)
  GET  /jobs/{id}    — poll job status
  GET  /jobs/{id}/files        — list output files
  GET  /jobs/{id}/files/{path} — download a file
  GET  /jobs/{id}/log         — fetch run log

Output files (from a successful run):
  - 06_genos_evee_annotation/vep_output.with_genos_evee.csv  (GENOS-EVEE wide table)
  - vep_output.with_info.ranked_large.csv                    (ranked variant table)
  - gene_phenotype_score.csv                                (gene-level HPO scoring)
  - variant_phenotype_score.csv                              (variant-level HPO scoring)
  - phenotype.csv                                            (phenotype mapping)
"""
import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import httpx

from config import (
    VEP_API_BASE_URL,
    VEP_POLL_MAX_RETRIES,
    VEP_POLL_INTERVAL_SECONDS,
    VEP_ENABLED,
    VEP_API_KEY,
    VEP_ASYNC_POLL_INTERVAL,
    VEP_ASYNC_MAX_DURATION,
)

logger = logging.getLogger(__name__)

RESULT_CSV_PRIORITIES = [
    "vep_output.with_info.ranked_large.csv",
    "vep_output.with_genos_evee.csv",
    "vep_output.with_info.csv",
]

GENE_PHENOTYPE_SCORE_CSV = "gene_phenotype_score.csv"
VARIANT_PHENOTYPE_SCORE_CSV = "variant_phenotype_score.csv"
PHENOTYPE_CSV = "phenotype.csv"


@dataclass
class VEPJobInfo:
    job_id: str
    status: str
    created_at: str = ""
    updated_at: str = ""
    input_filename: str = ""
    input_bytes: int = 0
    options: Optional[Dict] = None
    status_url: str = ""
    result_url: str = ""
    files_url: str = ""
    log_url: str = ""
    rows: Optional[int] = None
    error: Optional[str] = None
    output_dir: str = ""
    queue_position: Optional[int] = None


class VEPServiceError(Exception):
    pass


class VEPService:
    def __init__(
        self,
        base_url: str = VEP_API_BASE_URL,
        max_retries: int = VEP_POLL_MAX_RETRIES,
        poll_interval: int = VEP_POLL_INTERVAL_SECONDS,
        api_key: str = VEP_API_KEY,
    ):
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.poll_interval = poll_interval
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        h = {}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def submit_job(self, vcf_path: str, options: Optional[Dict] = None) -> VEPJobInfo:
        url = f"{self.base_url}/run-upload"
        files = {
            "input_vcf": (Path(vcf_path).name, open(vcf_path, "rb"), "application/octet-stream"),
        }
        data = {
            "hgvs": "true",
            "top_n_hpo_tissues": "3",
        }
        if options:
            for k, v in options.items():
                if v is not None:
                    data[k] = str(v).lower() if isinstance(v, bool) else str(v)

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, files=files, data=data, headers=self._headers())
            resp.raise_for_status()
            result = resp.json()

        return VEPJobInfo(
            job_id=result.get("job_id", ""),
            status=result.get("status", "unknown"),
            status_url=result.get("status_url", ""),
            files_url=result.get("files_url", ""),
            output_dir=result.get("output_dir", ""),
            queue_position=result.get("queue_position"),
        )

    async def poll_job(self, job_id: str) -> VEPJobInfo:
        url = f"{self.base_url}/jobs/{job_id}"
        last_status = "unknown"

        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(1, self.max_retries + 1):
                resp = await client.get(url, headers=self._headers())
                resp.raise_for_status()
                result = resp.json()

                last_status = result.get("status", "unknown")
                job_info = VEPJobInfo(
                    job_id=job_id,
                    status=last_status,
                    created_at=result.get("created_at", ""),
                    input_filename=result.get("original_filename", ""),
                    status_url=result.get("status_url", ""),
                    files_url=result.get("files_url", ""),
                    log_url=result.get("api_log_download_url", ""),
                    output_dir=result.get("output_dir", ""),
                    error=result.get("error"),
                )

                if last_status in ("completed", "completion", "success", "succeeded", "finished", "done", "failed"):
                    return job_info

                if attempt < self.max_retries:
                    logger.info(f"VEP job {job_id}: status={last_status}, retry {attempt}/{self.max_retries}, waiting {self.poll_interval}s...")
                    await asyncio.sleep(self.poll_interval)

        logger.error(f"VEP job {job_id}: still {last_status} after {self.max_retries} retries")
        return VEPJobInfo(job_id=job_id, status="timeout")

    async def get_status(self, job_id: str) -> VEPJobInfo:
        url = f"{self.base_url}/jobs/{job_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            result = resp.json()
            return VEPJobInfo(
                job_id=job_id,
                status=result.get("status", "unknown"),
                created_at=result.get("created_at", ""),
                input_filename=result.get("original_filename", ""),
                status_url=result.get("status_url", ""),
                files_url=result.get("files_url", ""),
                log_url=result.get("api_log_download_url", ""),
                output_dir=result.get("output_dir", ""),
                error=result.get("error"),
            )

    async def list_files(self, job_id: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/jobs/{job_id}/files"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json().get("files", [])

    async def download_file(self, job_id: str, file_path: str) -> bytes:
        url = f"{self.base_url}/jobs/{job_id}/files/{file_path}"
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.content

    def _find_file_by_relative_path(self, files: List[Dict], target_name: str) -> Optional[Dict]:
        for f in files:
            rp = f.get("relative_path", "")
            if rp.endswith(target_name) or os.path.basename(rp) == target_name:
                return f
        return None

    async def get_result_csv(self, job_id: str) -> Optional[str]:
        files = await self.list_files(job_id)

        for candidate_name in RESULT_CSV_PRIORITIES:
            match = self._find_file_by_relative_path(files, candidate_name)
            if match:
                relative_path = match.get("relative_path", "")
                logger.info(f"VEP job {job_id}: downloading result CSV {relative_path}")
                content = await self.download_file(job_id, relative_path)
                return content.decode("utf-8", errors="replace")

        return None

    async def download_key_files(self, job_id: str, save_dir: str) -> Dict[str, Optional[str]]:
        """
        Download the key output files from a completed VEP job.
        Returns a dict mapping file_key -> local_path (or None if not found).
        """
        files = await self.list_files(job_id)
        os.makedirs(save_dir, exist_ok=True)

        result = {
            "result_csv": None,
            "gene_phenotype_score_csv": None,
            "variant_phenotype_score_csv": None,
            "phenotype_csv": None,
        }

        file_targets = {
            "result_csv": RESULT_CSV_PRIORITIES,
            "gene_phenotype_score_csv": [GENE_PHENOTYPE_SCORE_CSV],
            "variant_phenotype_score_csv": [VARIANT_PHENOTYPE_SCORE_CSV],
            "phenotype_csv": [PHENOTYPE_CSV],
        }

        for key, names in file_targets.items():
            for name in names:
                match = self._find_file_by_relative_path(files, name)
                if match:
                    relative_path = match.get("relative_path", "")
                    local_name = f"{job_id}_{os.path.basename(relative_path)}"
                    local_path = os.path.join(save_dir, local_name)
                    logger.info(f"VEP job {job_id}: downloading {relative_path} -> {local_path}")
                    content = await self.download_file(job_id, relative_path)
                    with open(local_path, "wb") as f:
                        f.write(content)
                    result[key] = local_path
                    break

        return result

    async def get_result(self, result_url: str) -> str:
        url = f"{self.base_url}{result_url}" if result_url.startswith("/") else result_url
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.text

    async def get_log(self, job_id: str) -> str:
        url = f"{self.base_url}/jobs/{job_id}/log"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.text

    async def submit_vcf_async(
        self, vcf_path: str, options: Optional[Dict] = None
    ) -> VEPJobInfo:
        if not VEP_ENABLED:
            return VEPJobInfo(job_id="", status="disabled")

        logger.info(f"Submitting VCF to VEP API (async): {vcf_path}")
        job_info = await self.submit_job(vcf_path, options)
        logger.info(f"VEP job submitted (async): {job_info.job_id}, status={job_info.status}")
        return job_info
