"""
Phenotype-HPO Scoring Service Client.

Calls the external phenotype-HPO scoring API at PHENOTYPE_HPO_API_BASE_URL.

API flow:
  POST /runs                    — submit annotated variant CSV + optional HPO terms
  GET  /runs/{uid}              — poll job status
  GET  /runs/{uid}/files        — list output files
  GET  /runs/{uid}/files/{name} — download a specific output file

Output files include gene_phenotype_score.csv (the gene-level HPO scoring result).
"""
import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from config import (
    PHENOTYPE_HPO_API_BASE_URL,
    PHENOTYPE_HPO_POLL_INTERVAL,
    PHENOTYPE_HPO_MAX_DURATION,
)

logger = logging.getLogger(__name__)

GENE_PHENOTYPE_SCORE_CSV = "gene_phenotype_score.csv"
VARIANT_PHENOTYPE_SCORE_CSV = "variant_phenotype_score.csv"
PHENOTYPE_CSV = "phenotype.csv"


@dataclass
class PhenotypeHpoJobInfo:
    uid: str
    status: str
    error: Optional[str] = None


class PhenotypeHpoServiceError(Exception):
    pass


class PhenotypeHpoService:
    def __init__(
        self,
        base_url: str = PHENOTYPE_HPO_API_BASE_URL,
        poll_interval: int = PHENOTYPE_HPO_POLL_INTERVAL,
        max_duration: int = PHENOTYPE_HPO_MAX_DURATION,
    ):
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.max_duration = max_duration

    async def submit_run(
        self,
        csv_path: str,
        hpo_terms: Optional[List[str]] = None,
        min_similarity: float = 0.2,
    ) -> PhenotypeHpoJobInfo:
        """
        Submit an annotated variant CSV to the phenotype-HPO scoring service.

        Args:
            csv_path: Local path to the VEP output CSV (must contain gene_symbol / all_genes).
            hpo_terms: Optional list of HPO IDs (e.g. ["HP:0001250", "HP:0001263"]).
            min_similarity: Minimum phenotype similarity threshold.

        Returns:
            PhenotypeHpoJobInfo with uid and initial status.
        """
        url = f"{self.base_url}/runs"

        files = {
            "file": (
                Path(csv_path).name,
                open(csv_path, "rb"),
                "application/octet-stream",
            ),
        }
        data: Dict[str, Any] = {
            "min_similarity": str(min_similarity),
            "input_format": "auto",
        }
        if hpo_terms:
            data["hpo_list"] = ",".join(hpo_terms)

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, files=files, data=data)
            resp.raise_for_status()
            result = resp.json()

        uid = result.get("uid", "")
        status = result.get("status", "queued")

        logger.info(f"Phenotype-HPO job submitted: uid={uid}, status={status}")
        return PhenotypeHpoJobInfo(uid=uid, status=status)

    async def get_status(self, uid: str) -> PhenotypeHpoJobInfo:
        """Poll the status of a phenotype-HPO scoring job."""
        url = f"{self.base_url}/runs/{uid}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            result = resp.json()

        return PhenotypeHpoJobInfo(
            uid=uid,
            status=result.get("status", "unknown"),
            error=result.get("error"),
        )

    async def poll_until_complete(self, uid: str) -> PhenotypeHpoJobInfo:
        """
        Poll the phenotype-HPO job until it reaches a terminal status
        or exceeds max_duration.

        Terminal statuses: completed, success, succeeded, failed, error.
        """
        elapsed = 0
        while elapsed < self.max_duration:
            info = await self.get_status(uid)
            logger.info(
                f"Phenotype-HPO job {uid}: status={info.status}, elapsed={elapsed}s"
            )

            terminal = ("completed", "completion", "success", "succeeded", "finished", "done", "failed", "error")
            if info.status in terminal:
                return info

            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

        logger.error(
            f"Phenotype-HPO job {uid}: timed out after {elapsed}s (max={self.max_duration}s)"
        )
        return PhenotypeHpoJobInfo(uid=uid, status="timeout")

    async def list_files(self, uid: str) -> List[Dict[str, Any]]:
        """List output files for a completed phenotype-HPO job."""
        url = f"{self.base_url}/runs/{uid}/files"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json().get("files", [])

    async def download_file(self, uid: str, filename: str) -> bytes:
        """Download a specific output file from a completed job."""
        url = f"{self.base_url}/runs/{uid}/files/{filename}"
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content

    def _find_file(self, files_list: List[Dict], target_name: str) -> Optional[Dict]:
        """Find a file entry by name in the output files list."""
        for f in files_list:
            name = f.get("name", f.get("filename", f.get("relative_path", "")))
            if os.path.basename(name) == target_name or name.endswith(target_name):
                return f
        return None

    async def download_key_results(
        self, uid: str, save_dir: str
    ) -> Dict[str, Optional[str]]:
        """
        Download the key output files from a completed phenotype-HPO job.

        Returns dict mapping file_key -> local_path (or None if not found).
        Keys: gene_phenotype_score_csv, variant_phenotype_score_csv, phenotype_csv
        """
        files_list = await self.list_files(uid)
        os.makedirs(save_dir, exist_ok=True)

        result = {
            "gene_phenotype_score_csv": None,
            "variant_phenotype_score_csv": None,
            "phenotype_csv": None,
        }

        targets = {
            "gene_phenotype_score_csv": GENE_PHENOTYPE_SCORE_CSV,
            "variant_phenotype_score_csv": VARIANT_PHENOTYPE_SCORE_CSV,
            "phenotype_csv": PHENOTYPE_CSV,
        }

        for key, target_name in targets.items():
            match = self._find_file(files_list, target_name)
            if match:
                filename = match.get(
                    "name", match.get("filename", match.get("relative_path", ""))
                )
                logger.info(
                    f"Phenotype-HPO job {uid}: downloading {filename}"
                )
                content = await self.download_file(uid, filename)
                local_path = os.path.join(save_dir, f"{uid}_{target_name}")
                with open(local_path, "wb") as f:
                    f.write(content)
                result[key] = local_path
                logger.info(
                    f"Phenotype-HPO job {uid}: saved {target_name} -> {local_path}"
                )
            else:
                logger.warning(
                    f"Phenotype-HPO job {uid}: {target_name} not found in output files"
                )

        return result
