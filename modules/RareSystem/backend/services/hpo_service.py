"""
HPO API Service Client — submit clinical notes, poll job status, fetch results.

Uses httpx for async HTTP. Falls back gracefully on any failure.
"""
import asyncio
import logging
import re
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

from config import (
    HPO_API_BASE_URL,
    HPO_POLL_INTERVAL_SECONDS,
    HPO_POLL_MAX_ATTEMPTS,
)

logger = logging.getLogger(__name__)


def _extract_numeric_patient_id(patient_id: str) -> str:
    """Extract numeric part from patient_id string (e.g., 'patient_1780309362623' -> '1780309362623')."""
    match = re.search(r'\d+', patient_id)
    if match:
        return match.group()
    return patient_id


def generate_hpo_job_id() -> str:
    """Generate a unique HPO job ID."""
    return f"hpo_{uuid.uuid4().hex[:12]}"


@dataclass
class HPOTerm:
    phrase: str
    category: str
    hpo_id: str


@dataclass
class HPOJobInfo:
    job_id: str
    status: str
    created_at: str = ""
    updated_at: str = ""
    status_url: str = ""
    result_url: str = ""
    log_url: str = ""
    error: Optional[str] = None
    results: Optional[List[HPOTerm]] = None


class HPOServiceError(Exception):
    pass


class HPOService:
    def __init__(
        self,
        base_url: str = HPO_API_BASE_URL,
        poll_interval: int = HPO_POLL_INTERVAL_SECONDS,
        max_attempts: int = HPO_POLL_MAX_ATTEMPTS,
    ):
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.max_attempts = max_attempts

    async def submit_job(self, patient_id: str, clinical_note: str) -> HPOJobInfo:
        url = f"{self.base_url}/api/v1/extract"
        numeric_id = _extract_numeric_patient_id(patient_id)
        payload = {
            "notes": [
                {
                    "patient_id": numeric_id,
                    "clinical_note": clinical_note
                }
            ]
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            result = resp.json()

        return HPOJobInfo(
            job_id=result.get("job_id", ""),
            status=result.get("status", "unknown"),
            created_at=result.get("created_at", ""),
            updated_at=result.get("updated_at", ""),
            status_url=result.get("status_url", ""),
            result_url=result.get("result_url", ""),
            log_url=result.get("log_url", ""),
        )

    async def poll_and_fetch_result(self, job_id: str) -> HPOJobInfo:
        status_url = f"{self.base_url}/runs/{job_id}"
        result_url = f"{self.base_url}/runs/{job_id}/result"

        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(1, self.max_attempts + 1):
                try:
                    resp = await client.get(result_url)
                    
                    # Handle 425 (Too Early) - job still queued
                    if resp.status_code == 425:
                        logger.info(f"HPO job {job_id}: still queued (425), attempt {attempt}/{self.max_attempts}")
                        if attempt < self.max_attempts:
                            await asyncio.sleep(self.poll_interval)
                        continue
                    
                    # Handle 404 - result not ready
                    if resp.status_code == 404:
                        logger.info(f"HPO job {job_id}: result not ready (404), attempt {attempt}/{self.max_attempts}")
                        if attempt < self.max_attempts:
                            await asyncio.sleep(self.poll_interval)
                        continue
                    
                    resp.raise_for_status()
                    result = resp.json()

                    # Check for queued status in response body
                    if "detail" in result and "queued" in result["detail"].lower():
                        logger.info(f"HPO job {job_id}: still queued (detail), attempt {attempt}/{self.max_attempts}")
                        if attempt < self.max_attempts:
                            await asyncio.sleep(self.poll_interval)
                        continue

                    if "results" in result:
                        terms = []
                        for item in result.get("results", []):
                            terms.append(HPOTerm(
                                phrase=item.get("phrase", ""),
                                category=item.get("category", ""),
                                hpo_id=item.get("hpo_id", "")
                            ))
                        return HPOJobInfo(
                            job_id=job_id,
                            status="completed",
                            results=terms
                        )

                except httpx.HTTPStatusError as e:
                    logger.warning(f"HPO job {job_id}: HTTP error {e.response.status_code}, attempt {attempt}/{self.max_attempts}")
                    if attempt < self.max_attempts:
                        await asyncio.sleep(self.poll_interval)
                    continue

        logger.error(f"HPO job {job_id}: timed out after {self.max_attempts} attempts")
        return HPOJobInfo(job_id=job_id, status="timeout")

    async def lookup_hpo_term(self, hpo_id: str) -> Optional[Dict[str, Any]]:
        if not hpo_id.upper().startswith("HP:"):
            hpo_id = f"HP:{hpo_id}"
        
        hpo_iri = hpo_id.replace(":", "_")
        url = f"https://www.ebi.ac.uk/ols4/api/terms?iri=http://purl.obolibrary.org/obo/{hpo_iri}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url)
                
                if resp.status_code == 404:
                    logger.warning(f"HPO term {hpo_id} not found")
                    return None
                    
                resp.raise_for_status()
                result = resp.json()
                
                terms = result.get("_embedded", {}).get("terms", [])
                if not terms:
                    logger.warning(f"HPO term {hpo_id} not found in response")
                    return None
                
                term = terms[0]
                descriptions = term.get("description", [])
                synonyms = term.get("synonyms", [])
                
                return {
                    "hpo_id": term.get("obo_id", hpo_id),
                    "name": term.get("label", ""),
                    "definition": descriptions[0] if descriptions else "",
                    "synonyms": synonyms,
                    "category": "phenotype",
                    "display_category": "primary"  # Default to primary phenotype
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HPO lookup HTTP error: {e.response.status_code}")
            return None
        except httpx.ConnectError as e:
            logger.error(f"HPO lookup connection failed: {e}")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"HPO lookup timeout: {e}")
            return None
        except Exception as e:
            logger.error(f"HPO lookup unexpected error: {type(e).__name__}: {e}")
            return None

    async def extract_phenotypes(self, patient_id: str, clinical_note: str) -> Optional[List[HPOTerm]]:
        try:
            logger.info(f"Submitting clinical note to HPO API for patient {patient_id}")
            job_info = await self.submit_job(patient_id, clinical_note)
            logger.info(f"HPO job submitted: {job_info.job_id}, status={job_info.status}")

            job_info = await self.poll_and_fetch_result(job_info.job_id)
            logger.info(f"HPO job completed: {job_info.job_id}, status={job_info.status}")

            if job_info.status == "completed" and job_info.results:
                logger.info(f"HPO extracted {len(job_info.results)} phenotypes")
                return job_info.results

            return None

        except httpx.ConnectError as e:
            logger.error(f"HPO API connection failed: {e}")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"HPO API timeout: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HPO API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"HPO API unexpected error: {type(e).__name__}: {e}")
            return None


async def run_hpo_extraction_background(
    job_id: str,
    patient_id: str,
    clinical_note: str,
    db_session_factory=None
) -> None:
    """
    Background task to extract HPO terms and update the database.
    
    Args:
        job_id: Unique job identifier
        patient_id: Patient ID for HPO extraction (temp ID, real ID will be set by VCF upload)
        clinical_note: Clinical text to extract phenotypes from
        db_session_factory: Optional database session factory for testing
    """
    from database import get_db
    from database.models import HPOJob, Patient
    
    logger.info(f"Starting background HPO extraction for job {job_id}")
    
    if db_session_factory:
        db = next(db_session_factory())
    else:
        db = next(get_db())
    
    try:
        hpo_job = db.query(HPOJob).filter(HPOJob.job_id == job_id).first()
        if hpo_job:
            hpo_job.status = "processing"
            db.commit()
        
        service = HPOService()
        results = await service.extract_phenotypes(patient_id, clinical_note)
        
        if results:
            hpo_terms = [
                {
                    "phrase": t.phrase,
                    "category": t.category,
                    "hpo_id": t.hpo_id,
                    "display_category": "primary"  # Default to primary phenotype
                }
                for t in results
            ]
            
            if hpo_job:
                hpo_job.status = "completed"
                hpo_job.results = hpo_terms
                db.commit()
            
            db.refresh(hpo_job)
            actual_patient_id = hpo_job.patient_id
            for _ in range(30):
                if actual_patient_id:
                    break
                await asyncio.sleep(1)
                db.refresh(hpo_job)
                actual_patient_id = hpo_job.patient_id
            
            if actual_patient_id:
                patient = db.query(Patient).filter(Patient.id == actual_patient_id).first()
                if patient:
                    patient.hpo_terms = hpo_terms
                    db.commit()
                    logger.info(f"Updated patient {actual_patient_id} with {len(hpo_terms)} HPO terms")
            
            logger.info(f"HPO extraction completed for job {job_id}: {len(hpo_terms)} terms extracted")
        else:
            if hpo_job:
                hpo_job.status = "completed"
                hpo_job.results = []
                db.commit()
            
            db.refresh(hpo_job)
            actual_patient_id = hpo_job.patient_id
            for _ in range(30):
                if actual_patient_id:
                    break
                await asyncio.sleep(1)
                db.refresh(hpo_job)
                actual_patient_id = hpo_job.patient_id
            
            if actual_patient_id:
                patient = db.query(Patient).filter(Patient.id == actual_patient_id).first()
                if patient:
                    patient.hpo_terms = []
                    db.commit()
            
            logger.info(f"HPO extraction completed for job {job_id}: no terms extracted")
    
    except Exception as e:
        logger.error(f"HPO extraction failed for job {job_id}: {e}")
        
        try:
            hpo_job = db.query(HPOJob).filter(HPOJob.job_id == job_id).first()
            if hpo_job:
                hpo_job.status = "failed"
                hpo_job.error = str(e)
                db.commit()
        except Exception as update_error:
            logger.error(f"Failed to update job status: {update_error}")
    
    finally:
        try:
            db.close()
        except:
            pass
