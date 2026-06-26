"""
PPI Score Service Client.

Calls the external PPI (Protein-Protein Interaction) scoring API at PPI_SCORE_API_BASE_URL.

API flow:
  POST /score/clean-case/upload/async  — submit phenotype_gene_csv + vep_output_csv + optional HPO
  GET  /score/{job_id}                  — poll job status
  GET  /score/{job_id}/csv              — download scored variant CSV
  GET  /score/{job_id}/ppi-csv          — download PPI network CSV

The clean-case endpoint combines phenotype gene scoring with VEP variant annotation
and PPI network topology to produce final prioritized gene/variant scores.
"""
import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from config import (
    PPI_SCORE_API_BASE_URL,
    PPI_SCORE_POLL_INTERVAL,
    PPI_SCORE_MAX_DURATION,
)

logger = logging.getLogger(__name__)


@dataclass
class PpiScoreJobInfo:
    job_id: str
    status: str
    error: Optional[str] = None


class PpiScoreServiceError(Exception):
    pass


class PpiScoreService:
    def __init__(
        self,
        base_url: str = PPI_SCORE_API_BASE_URL,
        poll_interval: int = PPI_SCORE_POLL_INTERVAL,
        max_duration: int = PPI_SCORE_MAX_DURATION,
    ):
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.max_duration = max_duration

    async def submit_clean_case_async(
        self,
        phenotype_gene_csv_path: str,
        vep_output_csv_path: str,
        hpo_ids: Optional[List[str]] = None,
    ) -> PpiScoreJobInfo:
        """
        Submit a clean-case scoring job to the PPI service (async).

        Args:
            phenotype_gene_csv_path: Local path to gene_phenotype_score.csv
                                     (output from phenotype-HPO service).
            vep_output_csv_path: Local path to VEP annotated variant CSV.
            hpo_ids: Optional list of HPO IDs.

        Returns:
            PpiScoreJobInfo with job_id and initial status.
        """
        url = f"{self.base_url}/score/clean-case/upload/async"

        files = {
            "phenotype_gene_csv": (
                Path(phenotype_gene_csv_path).name,
                open(phenotype_gene_csv_path, "rb"),
                "application/octet-stream",
            ),
            "vep_output_csv": (
                Path(vep_output_csv_path).name,
                open(vep_output_csv_path, "rb"),
                "application/octet-stream",
            ),
        }
        data: Dict[str, Any] = {}
        if hpo_ids:
            data["hpo_ids"] = ",".join(hpo_ids)

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, files=files, data=data)
            resp.raise_for_status()
            result = resp.json()

        job_id = result.get("job_id", "")
        status = result.get("status", "queued")

        logger.info(f"PPI score job submitted: job_id={job_id}, status={status}")
        return PpiScoreJobInfo(job_id=job_id, status=status)

    async def get_status(self, job_id: str) -> PpiScoreJobInfo:
        """Poll the status of a PPI score job."""
        url = f"{self.base_url}/score/{job_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            result = resp.json()

        return PpiScoreJobInfo(
            job_id=job_id,
            status=result.get("status", "unknown"),
            error=result.get("error"),
        )

    async def poll_until_complete(self, job_id: str) -> PpiScoreJobInfo:
        """
        Poll the PPI score job until it reaches a terminal status
        or exceeds max_duration.

        Terminal statuses: completed, success, succeeded, failed, error.
        """
        elapsed = 0
        while elapsed < self.max_duration:
            info = await self.get_status(job_id)
            logger.info(
                f"PPI score job {job_id}: status={info.status}, elapsed={elapsed}s"
            )

            terminal = ("completed", "completion", "success", "succeeded", "finished", "done", "failed", "error")
            if info.status in terminal:
                return info

            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

        logger.error(
            f"PPI score job {job_id}: timed out after {elapsed}s (max={self.max_duration}s)"
        )
        return PpiScoreJobInfo(job_id=job_id, status="timeout")

    async def download_score_csv(self, job_id: str) -> bytes:
        """Download the scored variant CSV for a completed PPI job."""
        url = f"{self.base_url}/score/{job_id}/csv"
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content

    async def download_ppi_csv(self, job_id: str) -> bytes:
        """Download the PPI network CSV for a completed PPI job."""
        url = f"{self.base_url}/score/{job_id}/ppi-csv"
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content

    async def download_key_results(
        self, job_id: str, save_dir: str
    ) -> Dict[str, Optional[str]]:
        """
        Download the key output files from a completed PPI score job.

        Returns dict mapping file_key -> local_path (or None if not found).
        Keys: score_csv, ppi_csv
        """
        os.makedirs(save_dir, exist_ok=True)

        result = {
            "score_csv": None,
            "ppi_csv": None,
        }

        # Download score CSV
        try:
            logger.info(f"PPI score job {job_id}: downloading score CSV")
            content = await self.download_score_csv(job_id)
            local_path = os.path.join(save_dir, f"{job_id}_ppi_score.csv")
            with open(local_path, "wb") as f:
                f.write(content)
            result["score_csv"] = local_path
            logger.info(f"PPI score job {job_id}: saved score CSV -> {local_path}")
        except Exception as e:
            logger.warning(f"PPI score job {job_id}: failed to download score CSV: {e}")

        # Download PPI CSV
        try:
            logger.info(f"PPI score job {job_id}: downloading PPI CSV")
            content = await self.download_ppi_csv(job_id)
            local_path = os.path.join(save_dir, f"{job_id}_ppi_network.csv")
            with open(local_path, "wb") as f:
                f.write(content)
            result["ppi_csv"] = local_path
            logger.info(f"PPI score job {job_id}: saved PPI CSV -> {local_path}")
        except Exception as e:
            logger.warning(f"PPI score job {job_id}: failed to download PPI CSV: {e}")

        return result
