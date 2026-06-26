"""
Ranking Service Client.

Calls the external Ranking API at RANK_API_BASE_URL.

API flow:
  POST /score/upload          — submit VEP output CSV + gene score CSV + PPI score CSV
  GET  /status/{job_id}       — poll job status
  GET  /output/{job_id}       — download ranked_output.csv

The ranking service combines VEP variant annotation, gene-phenotype scores,
and PPI network scores to produce a final ranked gene list.
"""
import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import httpx

from config import (
    RANK_API_BASE_URL,
    RANK_POLL_INTERVAL,
    RANK_MAX_DURATION,
)

logger = logging.getLogger(__name__)


@dataclass
class RankingJobInfo:
    job_id: str
    status: str
    error: Optional[str] = None


class RankingServiceError(Exception):
    pass


class RankingService:
    def __init__(
        self,
        base_url: str = RANK_API_BASE_URL,
        poll_interval: int = RANK_POLL_INTERVAL,
        max_duration: int = RANK_MAX_DURATION,
    ):
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.max_duration = max_duration

    async def submit(
        self,
        vep_csv_path: str,
        gene_score_csv_path: str,
        ppi_score_csv_path: str,
    ) -> RankingJobInfo:
        """
        Submit a ranking job to the Ranking service (async).

        Args:
            vep_csv_path: Local path to VEP annotated variant CSV.
            gene_score_csv_path: Local path to gene_phenotype_score CSV.
            ppi_score_csv_path: Local path to PPI score CSV.

        Returns:
            RankingJobInfo with job_id and initial status.
        """
        url = f"{self.base_url}/score/upload"

        f_vep = open(vep_csv_path, "rb")
        f_gene = open(gene_score_csv_path, "rb")
        f_ppi = open(ppi_score_csv_path, "rb")

        files = {
            "file": (
                Path(vep_csv_path).name,
                f_vep,
                "application/octet-stream",
            ),
            "gene_score_file": (
                Path(gene_score_csv_path).name,
                f_gene,
                "application/octet-stream",
            ),
            "ppi_score_file": (
                Path(ppi_score_csv_path).name,
                f_ppi,
                "application/octet-stream",
            ),
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, files=files)
                resp.raise_for_status()
                result = resp.json()
        finally:
            f_vep.close()
            f_gene.close()
            f_ppi.close()

        job_id = result.get("job_id", "")
        status = result.get("status", "queued")

        logger.info(f"Ranking job submitted: job_id={job_id}, status={status}")
        return RankingJobInfo(job_id=job_id, status=status)

    async def get_status(self, job_id: str) -> RankingJobInfo:
        """Poll the status of a ranking job."""
        url = f"{self.base_url}/status/{job_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            result = resp.json()

        return RankingJobInfo(
            job_id=job_id,
            status=result.get("status", "unknown"),
            error=result.get("error"),
        )

    async def poll_until_complete(self, job_id: str) -> RankingJobInfo:
        """
        Poll the ranking job until it reaches a terminal status
        or exceeds max_duration.

        Terminal statuses: completed, success, succeeded, failed, error.
        """
        elapsed = 0
        while elapsed < self.max_duration:
            info = await self.get_status(job_id)
            logger.info(
                f"Ranking job {job_id}: status={info.status}, elapsed={elapsed}s"
            )

            terminal = ("completed", "completion", "success", "succeeded", "finished", "done", "failed", "error")
            if info.status in terminal:
                return info

            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

        logger.error(
            f"Ranking job {job_id}: timed out after {elapsed}s (max={self.max_duration}s)"
        )
        return RankingJobInfo(job_id=job_id, status="timeout")

    async def download_ranked_csv(self, job_id: str) -> bytes:
        """Download the ranked_output.csv for a completed ranking job."""
        url = f"{self.base_url}/output/{job_id}"
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content

    async def download_and_save(
        self, job_id: str, save_dir: str
    ) -> Dict[str, Optional[str]]:
        """
        Download the ranked output CSV from a completed ranking job.

        Returns dict mapping file_key -> local_path (or None if not found).
        Keys: ranked_csv
        """
        os.makedirs(save_dir, exist_ok=True)

        result: Dict[str, Optional[str]] = {
            "ranked_csv": None,
        }

        try:
            logger.info(f"Ranking job {job_id}: downloading ranked CSV")
            content = await self.download_ranked_csv(job_id)
            local_path = os.path.join(save_dir, f"{job_id}_ranked.csv")
            with open(local_path, "wb") as f:
                f.write(content)
            result["ranked_csv"] = local_path
            logger.info(f"Ranking job {job_id}: saved ranked CSV -> {local_path}")
        except Exception as e:
            logger.warning(f"Ranking job {job_id}: failed to download ranked CSV: {e}")

        return result

    async def health_check(self) -> bool:
        """Try GET {base_url}/ with a short timeout to check service availability."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/")
                return resp.status_code == 200
        except Exception:
            return False
