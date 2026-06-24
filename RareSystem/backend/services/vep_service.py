"""
VEP API Service Client — submit VCF files, poll job status, fetch results.

Uses httpx for async HTTP. Falls back gracefully on any failure.
"""
import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import time
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
from services.vep_csv_parser import VEPCSVParser, VEPParseResult

logger = logging.getLogger(__name__)


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
    log_url: str = ""
    rows: Optional[int] = None
    error: Optional[str] = None


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
        self.parser = VEPCSVParser()

    def _headers(self) -> Dict[str, str]:
        h = {}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def submit_job(self, vcf_path: str, options: Optional[Dict] = None) -> VEPJobInfo:
        url = f"{self.base_url}/runs"
        files = {"file": (Path(vcf_path).name, open(vcf_path, "rb"), "application/octet-stream")}
        data = {}
        if options:
            for k, v in options.items():
                data[k] = str(v).lower() if isinstance(v, bool) else str(v)

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, files=files, data=data, headers=self._headers())
            resp.raise_for_status()
            result = resp.json()

        return VEPJobInfo(
            job_id=result.get("job_id", ""),
            status=result.get("status", "unknown"),
            created_at=result.get("created_at", ""),
            updated_at=result.get("updated_at", ""),
            input_filename=result.get("input_filename", ""),
            input_bytes=result.get("input_bytes", 0),
            options=result.get("options"),
            status_url=result.get("status_url", ""),
            result_url=result.get("result_url", ""),
            log_url=result.get("log_url", ""),
            rows=result.get("rows"),
            error=result.get("error"),
        )

    async def poll_job(self, job_id: str) -> VEPJobInfo:
        url = f"{self.base_url}/runs/{job_id}"
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
                    updated_at=result.get("updated_at", ""),
                    input_filename=result.get("input_filename", ""),
                    input_bytes=result.get("input_bytes", 0),
                    options=result.get("options"),
                    status_url=result.get("status_url", ""),
                    result_url=result.get("result_url", ""),
                    log_url=result.get("log_url", ""),
                    rows=result.get("rows"),
                    error=result.get("error"),
                )

                if last_status in ("completed", "failed"):
                    return job_info
                
                if await self.get_result(job_info.result_url):
                    logger.info(f"VEP job {job_id}: result available before completion, status={last_status}")
                    return job_info

                if attempt < self.max_retries:
                    logger.info(f"VEP job {job_id}: status={last_status}, retry {attempt}/{self.max_retries}, waiting {self.poll_interval}s...")
                    await asyncio.sleep(self.poll_interval)

        logger.error(f"VEP job {job_id}: still {last_status} after {self.max_retries} retries")
        return VEPJobInfo(job_id=job_id, status="timeout")

    async def get_status(self, job_id: str) -> VEPJobInfo:
        url = f"{self.base_url}/runs/{job_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            result = resp.json()
            return VEPJobInfo(
                job_id=job_id,
                status=result.get("status", "unknown"),
                created_at=result.get("created_at", ""),
                updated_at=result.get("updated_at", ""),
                input_filename=result.get("input_filename", ""),
                input_bytes=result.get("input_bytes", 0),
                options=result.get("options"),
                status_url=result.get("status_url", ""),
                result_url=result.get("result_url", ""),
                log_url=result.get("log_url", ""),
                rows=result.get("rows"),
                error=result.get("error"),
            )

    async def get_result(self, result_url: str) -> str:
        url = f"{self.base_url}{result_url}" if result_url.startswith("/") else result_url
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.text

    async def get_log(self, log_url: str) -> str:
        url = f"{self.base_url}{log_url}" if log_url.startswith("/") else log_url
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.text

    async def process_vcf(
        self, vcf_path: str, options: Optional[Dict] = None
    ) -> Optional[VEPParseResult]:
        if not VEP_ENABLED:
            logger.info("VEP annotation disabled, skipping")
            return None

        try:
            logger.info(f"Submitting VCF to VEP API: {vcf_path}")
            job_info = await self.submit_job(vcf_path, options)
            logger.info(f"VEP job submitted: {job_info.job_id}, status={job_info.status}")

            job_info = await self.poll_job(job_info.job_id)
            logger.info(f"VEP job completed: {job_info.job_id}, status={job_info.status}")

            if job_info.status == "failed":
                logger.error(f"VEP job failed: {job_info.error}")
                return None

            if job_info.status == "timeout":
                logger.error(f"VEP job timed out after {self.max_retries} retries")
                return None

            if not job_info.result_url:
                logger.warning("VEP job completed but no result_url")
                return None
            time.sleep(5)
            csv_content = await self.get_result(job_info.result_url)
            logger.info(f"VEP raw CSV (first 500 chars): {csv_content[:500]}")
            logger.info(f"VEP raw CSV (lines): {csv_content[:1000].count(chr(10))} lines")
            variants = self.parser.parse(csv_content)
            logger.info(f"VEP returned {len(variants.rows)} annotated variants")
            logger.info(f"VEP columns: {variants.columns}")
            if len(variants.rows) > 0:
                logger.info(f"VEP first row: {variants.rows[0]}")
            return variants

        except httpx.ConnectError as e:
            logger.error(f"VEP API connection failed: {e}")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"VEP API timeout: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"VEP API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"VEP API unexpected error: {type(e).__name__}: {e}")
            return None

    async def submit_vcf_async(
        self, vcf_path: str, options: Optional[Dict] = None
    ) -> VEPJobInfo:
        if not VEP_ENABLED:
            return VEPJobInfo(job_id="", status="disabled")

        logger.info(f"Submitting VCF to VEP API (async): {vcf_path}")
        job_info = await self.submit_job(vcf_path, options)
        logger.info(f"VEP job submitted (async): {job_info.job_id}, status={job_info.status}")
        return job_info

    async def poll_until_complete(
        self, job_id: str, poll_interval: int = VEP_ASYNC_POLL_INTERVAL, max_duration: int = VEP_ASYNC_MAX_DURATION
    ) -> Optional[VEPParseResult]:
        start_time = time.time()
        url = f"{self.base_url}/runs/{job_id}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                elapsed = time.time() - start_time
                if elapsed > max_duration:
                    logger.error(f"VEP job {job_id}: exceeded max duration {max_duration}s")
                    return None

                try:
                    resp = await client.get(url, headers=self._headers())
                    resp.raise_for_status()
                    result = resp.json()
                    status = result.get("status", "unknown")
                    logger.info(f"VEP job {job_id}: status={status}, elapsed={int(elapsed)}s")

                    if status == "failed":
                        logger.error(f"VEP job {job_id} failed: {result.get('error')}")
                        return None

                    if status == "completed":
                        result_url = result.get("result_url", "")
                        if not result_url:
                            logger.warning(f"VEP job {job_id} completed but no result_url")
                            return None
                        time.sleep(5)
                        csv_content = await self.get_result(result_url)
                        logger.info(f"VEP raw CSV (first 500 chars): {csv_content[:500]}")
                        variants = self.parser.parse(csv_content)
                        logger.info(f"VEP returned {len(variants.rows)} annotated variants")
                        return variants

                    if status == "queuing" or status == "queued" or status == "processing" or status == "running":
                        logger.info(f"VEP job {job_id}: {status}, waiting {poll_interval}s...")
                        await asyncio.sleep(poll_interval)
                        continue

                    logger.warning(f"VEP job {job_id}: unknown status {status}")
                    await asyncio.sleep(poll_interval)

                except httpx.HTTPStatusError as e:
                    logger.error(f"VEP job {job_id} HTTP error: {e.response.status_code}")
                    return None
                except Exception as e:
                    logger.error(f"VEP job {job_id} error: {type(e).__name__}: {e}")
                    await asyncio.sleep(poll_interval)
