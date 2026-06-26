"""
VEP Job Status API endpoints.

When VEP completes, downloads all key output files via VEP API,
converts main CSV to Parquet, updates VEPJob record.
"""
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, VEPJob
from services.vep_service import VEPService
from services.parquet_service import ParquetService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vep", tags=["vep"])

DATA_DIR = os.environ.get("VEP_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vep_results"))


class VEPJobResponse(BaseModel):
    job_id: str
    status: str
    input_filename: Optional[str]
    input_bytes: Optional[int]
    options: Optional[dict]
    status_url: Optional[str]
    result_url: Optional[str]
    log_url: Optional[str]
    rows: Optional[int]
    error: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    csv_path: Optional[str] = None
    parquet_path: Optional[str] = None
    gene_phenotype_score_path: Optional[str] = None
    variant_phenotype_score_path: Optional[str] = None
    ppi_score_path: Optional[str] = None
    phenotype_path: Optional[str] = None
    parquet_available: bool = False


async def _fetch_and_save_vep_results(job: VEPJob, db: Session) -> int:
    """
    Download all key files from VEP service, convert main CSV to Parquet,
    update VEPJob record. Returns number of rows in the result.
    """
    vep_service = VEPService()
    save_dir = os.path.join(DATA_DIR, job.job_id)

    downloaded = await vep_service.download_key_files(job.job_id, save_dir)

    result_csv_path = downloaded.get("result_csv")
    gene_score_path = downloaded.get("gene_phenotype_score_csv")
    variant_score_path = downloaded.get("variant_phenotype_score_csv")
    phenotype_path = downloaded.get("phenotype_csv")

    row_count = 0
    parquet_path = None

    if result_csv_path and os.path.exists(result_csv_path):
        service = ParquetService()
        csv_content = open(result_csv_path, "r", encoding="utf-8").read()
        csv_saved, parquet_path = service.csv_to_parquet(csv_content, job.job_id)
        row_count = service.row_count(parquet_path)
        job.csv_path = csv_saved
        job.parquet_path = parquet_path
        job.rows = row_count

    job.gene_phenotype_score_path = gene_score_path
    job.variant_phenotype_score_path = variant_score_path
    job.phenotype_path = phenotype_path
    job.status = "completed"
    db.commit()

    logger.info(
        f"VEP job {job.job_id}: saved results "
        f"(rows={row_count}, gene_score={gene_score_path is not None}, "
        f"variant_score={variant_score_path is not None})"
    )
    return row_count


def _build_job_response(job: VEPJob, parquet_available: bool = False) -> VEPJobResponse:
    return VEPJobResponse(
        job_id=job.job_id,
        status=job.status,
        input_filename=job.input_filename,
        input_bytes=job.input_bytes,
        options=job.options,
        status_url=job.status_url,
        result_url=job.result_url,
        log_url=job.log_url,
        rows=job.rows,
        error=job.error,
        created_at=str(job.created_at) if job.created_at else None,
        updated_at=str(job.updated_at) if job.updated_at else None,
        csv_path=job.csv_path,
        parquet_path=job.parquet_path,
        gene_phenotype_score_path=job.gene_phenotype_score_path,
        variant_phenotype_score_path=job.variant_phenotype_score_path,
        ppi_score_path=job.ppi_score_path,
        phenotype_path=job.phenotype_path,
        parquet_available=parquet_available,
    )


@router.get("/jobs/{job_id}/status", response_model=VEPJobResponse)
async def get_vep_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VEPJob).filter(VEPJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"VEP job {job_id} not found")

    completed_statuses = ("completed", "completion", "success", "succeeded", "finished", "done")
    parquet_available = bool(job.parquet_path) and job.status in completed_statuses

    if parquet_available:
        return _build_job_response(job, parquet_available=True)

    if job.status in ("failed", "timeout", "error"):
        return _build_job_response(job, parquet_available=False)

    # Still in progress — poll remote VEP service
    vep_service = VEPService()
    try:
        remote_status = await vep_service.get_status(job_id)
        logger.info(f"Job {job_id}: remote={remote_status.status}")

        job.status = remote_status.status
        if remote_status.files_url:
            job.result_url = remote_status.files_url
        if remote_status.error:
            job.error = remote_status.error
        db.commit()
    except Exception as e:
        logger.error(f"Failed to fetch VEP remote status for {job_id}: {e}")
        return _build_job_response(job, parquet_available=False)

    if job.status in completed_statuses:
        try:
            row_count = await _fetch_and_save_vep_results(job, db)
            parquet_available = row_count > 0
            logger.info(f"VEP annotation completed for job {job_id}: {row_count} rows")
        except Exception as e:
            logger.error(f"Failed to fetch/save VEP results for {job_id}: {e}")

    return _build_job_response(job, parquet_available=parquet_available)


@router.get("/jobs/{job_id}", response_model=VEPJobResponse)
async def get_vep_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VEPJob).filter(VEPJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"VEP job {job_id} not found")

    completed_statuses = ("completed", "completion", "success", "succeeded", "finished", "done")
    parquet_available = bool(job.parquet_path) and job.status in completed_statuses

    return _build_job_response(job, parquet_available=parquet_available)


@router.get("/jobs/vcf/{vcf_file_id}", response_model=VEPJobResponse)
async def get_vep_job_by_vcf(vcf_file_id: int, db: Session = Depends(get_db)):
    job = (
        db.query(VEPJob)
        .filter(VEPJob.vcf_file_id == vcf_file_id)
        .order_by(VEPJob.created_at.desc())
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail=f"No VEP job found for VCF file {vcf_file_id}")

    completed_statuses = ("completed", "completion", "success", "succeeded", "finished", "done")
    parquet_available = bool(job.parquet_path) and job.status in completed_statuses

    return _build_job_response(job, parquet_available=parquet_available)


@router.get("/jobs/{job_id}/log")
async def get_vep_job_log(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VEPJob).filter(VEPJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"VEP job {job_id} not found")
    try:
        vep_service = VEPService()
        log_content = await vep_service.get_log(job_id)
        return {"log": log_content}
    except Exception as e:
        logger.error(f"Failed to fetch VEP job log: {e}")
        return {"log": None, "error": str(e)}
