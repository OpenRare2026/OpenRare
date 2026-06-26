"""
Variant API endpoints for VCF upload and variant display.

Upload flow: save VCF temp file → decompress .vcf.gz if needed → create Patient/VCFFile → submit VEP async.
Variant display: read from Parquet (whatever VEP columns are present).
"""
import gzip
import logging
import os
import shutil
import tempfile
import time
import json
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, VCFFile, Patient, VEPJob
from database.session import verify_tables, init_db
from services.vep_service import VEPService
from services.parquet_service import ParquetService
from config import VEP_ENABLED

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/variants", tags=["variants"])


def decompress_vcf_gz(gz_path: str) -> str:
    """
    Decompress a .vcf.gz file to a plain .vcf file in the same directory.

    Returns the path to the decompressed .vcf file.
    Removes the original .gz file after successful decompression.
    """
    vcf_path = gz_path[:-3] if gz_path.endswith(".gz") else gz_path + ".decompressed.vcf"
    logger.info(f"Decompressing {gz_path} -> {vcf_path}")

    with gzip.open(gz_path, "rb") as f_in:
        with open(vcf_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    try:
        os.remove(gz_path)
        logger.info(f"Removed compressed file: {gz_path}")
    except OSError:
        logger.warning(f"Failed to remove compressed file: {gz_path}")

    logger.info(f"Decompression complete: {vcf_path} ({os.path.getsize(vcf_path)} bytes)")
    return vcf_path


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    vcf_file_id: str
    patient_id: str
    message: str
    vep_status: str = "skipped"
    vep_job_id: Optional[str] = None
    vep_job_db_id: Optional[int] = None


class SubmitVEPRequest(BaseModel):
    hpo_terms: List[str] = []
    vep_fork: int = 1
    vep_chromosomes: Optional[str] = None


class SubmitVEPResponse(BaseModel):
    vep_job_id: Optional[str] = None
    vep_status: str = "skipped"
    vep_job_db_id: Optional[int] = None


class DynamicVariantListResponse(BaseModel):
    columns: List[str]
    items: List[Dict[str, str]]
    total: int
    page: int
    page_size: int
    total_pages: int
    vep_job_id: Optional[str] = None
    message: str = ""


class DynamicVariantDetailResponse(BaseModel):
    row_index: int
    columns: List[str]
    row: Dict[str, str]


# ---------------------------------------------------------------------------
# Upload VCF — no Phase 1 parsing, direct VEP submission
# ---------------------------------------------------------------------------

@router.post("/upload", response_model=UploadResponse)
async def upload_vcf(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    patient_name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    sex: Optional[str] = Form(None),
    ethnicity: Optional[str] = Form(None),
    diagnosis_description: Optional[str] = Form(None),
    medical_history: Optional[str] = Form(None),
    hpo_terms: Optional[str] = Form(None),
    vep_fork: str = Form("16"),
    vep_chromosomes: Optional[str] = Form(None),
    hpo_job_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        if not verify_tables():
            logger.warning("Database tables missing, re-initializing...")
            init_db()

        filename = file.filename or "unknown.vcf"
        if not filename.endswith(('.vcf', '.vcf.gz')):
            raise HTTPException(status_code=400, detail="File must be a VCF file (.vcf or .vcf.gz)")

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        if tmp_path.endswith(".gz"):
            try:
                tmp_path = decompress_vcf_gz(tmp_path)
            except Exception as e:
                logger.error(f"Failed to decompress .vcf.gz file: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to decompress .vcf.gz file: {str(e)}")

        parsed_hpo_terms = None
        if hpo_terms:
            try:
                parsed_hpo_terms = json.loads(hpo_terms)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse hpo_terms JSON: {hpo_terms[:100]}")

        # --- Patient record (same logic as before) ---
        patient = None
        if patient_name:
            patient = db.query(Patient).filter(Patient.name == patient_name).first()

        if not patient:
            pid = int(patient_id) if patient_id.isdigit() else None
            if pid:
                existing_by_id = db.query(Patient).filter(Patient.id == pid).first()
                if existing_by_id:
                    patient = Patient(
                        name=patient_name or f"Patient_{pid}",
                        age=age, sex=sex, ethnicity=ethnicity,
                        diagnosis_description=diagnosis_description,
                        medical_history=medical_history,
                        hpo_terms=parsed_hpo_terms,
                    )
                else:
                    patient = Patient(
                        id=pid,
                        name=patient_name or f"Patient_{pid}",
                        age=age, sex=sex, ethnicity=ethnicity,
                        diagnosis_description=diagnosis_description,
                        medical_history=medical_history,
                        hpo_terms=parsed_hpo_terms,
                    )
            else:
                patient = Patient(
                    name=patient_name or f"Patient_{int(time.time())}",
                    age=age, sex=sex, ethnicity=ethnicity,
                    diagnosis_description=diagnosis_description,
                    medical_history=medical_history,
                    hpo_terms=parsed_hpo_terms,
                )
            db.add(patient)
            db.flush()
        else:
            if age is not None:
                patient.age = age
            if sex:
                patient.sex = sex
            if ethnicity:
                patient.ethnicity = ethnicity
            if diagnosis_description:
                patient.diagnosis_description = diagnosis_description
            if medical_history:
                patient.medical_history = medical_history
            if parsed_hpo_terms:
                patient.hpo_terms = parsed_hpo_terms
            db.flush()

        if hpo_job_id:
            from database.models import HPOJob
            hpo_job = db.query(HPOJob).filter(HPOJob.job_id == hpo_job_id).first()
            if hpo_job:
                hpo_job.patient_id = patient.id
                db.flush()
                logger.info(f"Updated HPOJob {hpo_job_id} with patient_id {patient.id}")

        # --- VCFFile record ---
        vcf_file = VCFFile(
            file_name=filename,
            file_path=tmp_path,
            patient_id=patient.id,
        )
        db.add(vcf_file)
        db.flush()
        vcf_file_id = vcf_file.id

        db.commit()

        logger.info(f"Uploaded VCF {filename}, vcf_file_id={vcf_file_id}, patient_id={patient.id}")

        # --- Submit to VEP (async) ---
        vep_status = "skipped"
        vep_job_id = None
        vep_job_db_id = None

        if VEP_ENABLED:
            vep_options = {
                "fork": int(vep_fork),
                "hpo_id": ",".join(
                    t["hpo_id"] for t in (parsed_hpo_terms or []) if t.get("hpo_id")
                ),
            }
            if vep_chromosomes:
                vep_options["chromosomes"] = vep_chromosomes
            vep_service = VEPService()
            try:
                job_info = await vep_service.submit_vcf_async(tmp_path, vep_options)
                vep_job_id = job_info.job_id
                vep_status = job_info.status

                vep_job_record = VEPJob(
                    job_id=job_info.job_id,
                    vcf_file_id=vcf_file_id,
                    status=job_info.status,
                    input_filename=job_info.input_filename,
                    input_bytes=job_info.input_bytes,
                    options=vep_options,
                    status_url=job_info.status_url,
                    result_url=job_info.files_url,
                    log_url=job_info.log_url,
                    rows=job_info.rows,
                    error=job_info.error,
                )
                db.add(vep_job_record)
                db.commit()
                db.refresh(vep_job_record)
                vep_job_db_id = vep_job_record.id
                vep_status = "queued"

                logger.info(f"VEP job submitted: {vep_job_id}, db_id={vep_job_db_id}")

            except Exception as e:
                logger.error(f"Failed to submit VEP job: {e}")
                vep_status = "failed"

        return UploadResponse(
            vcf_file_id=str(vcf_file_id),
            patient_id=str(patient.id),
            message=f"VCF submitted for VEP annotation",
            vep_status=vep_status,
            vep_job_id=vep_job_id,
            vep_job_db_id=vep_job_db_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Submit VEP for an existing VCF file (deferred after HPO extraction)
# ---------------------------------------------------------------------------

@router.post("/{vcf_file_id}/submit-vep", response_model=SubmitVEPResponse)
async def submit_vep_for_vcf(
    vcf_file_id: int,
    request: SubmitVEPRequest,
    db: Session = Depends(get_db),
):
    vcf_file = db.query(VCFFile).filter(VCFFile.id == vcf_file_id).first()
    if not vcf_file:
        raise HTTPException(status_code=404, detail="VCF file not found")

    if not os.path.exists(vcf_file.file_path):
        raise HTTPException(status_code=400, detail="VCF file not found on disk")

    vcf_path = vcf_file.file_path
    if vcf_path.endswith(".gz"):
        try:
            vcf_path = decompress_vcf_gz(vcf_path)
            vcf_file.file_path = vcf_path
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to decompress .vcf.gz file: {str(e)}")

    vep_status = "skipped"
    vep_job_id = None
    vep_job_db_id = None

    if VEP_ENABLED:
        vep_options = {
            "fork": request.vep_fork,
            "hpo_id": ",".join(request.hpo_terms),
        }
        if request.vep_chromosomes:
            vep_options["chromosomes"] = request.vep_chromosomes

        vep_service = VEPService()
        try:
            job_info = await vep_service.submit_vcf_async(vcf_path, vep_options)
            vep_job_id = job_info.job_id
            vep_status = job_info.status

            vep_job_record = VEPJob(
                job_id=job_info.job_id,
                vcf_file_id=vcf_file_id,
                status=job_info.status,
                input_filename=job_info.input_filename,
                input_bytes=job_info.input_bytes,
                options=vep_options,
                status_url=job_info.status_url,
                result_url=job_info.files_url,
                log_url=job_info.log_url,
                rows=job_info.rows,
                error=job_info.error,
            )
            db.add(vep_job_record)
            db.commit()
            db.refresh(vep_job_record)
            vep_job_db_id = vep_job_record.id
            vep_status = "queued"

            logger.info(f"Deferred VEP job submitted: {vep_job_id}, db_id={vep_job_db_id}")

        except Exception as e:
            logger.error(f"Failed to submit deferred VEP job: {e}")
            vep_status = "failed"

    return SubmitVEPResponse(
        vep_job_id=vep_job_id,
        vep_status=vep_status,
        vep_job_db_id=vep_job_db_id,
    )


# ---------------------------------------------------------------------------
# Variant listing — read from Parquet (dynamic columns from VEP)
# ---------------------------------------------------------------------------

@router.get("/{vcf_file_id}", response_model=DynamicVariantListResponse)
async def get_variants(
    vcf_file_id: str,
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    vcf_file = db.query(VCFFile).filter(VCFFile.id == int(vcf_file_id)).first()
    if not vcf_file:
        raise HTTPException(status_code=404, detail="VCF file not found")

    vep_job = (
        db.query(VEPJob)
        .filter(VEPJob.vcf_file_id == int(vcf_file_id), VEPJob.parquet_path.isnot(None))
        .order_by(VEPJob.created_at.desc())
        .first()
    )

    if not vep_job or not vep_job.parquet_path:
        return DynamicVariantListResponse(
            columns=[], items=[], total=0,
            page=page, page_size=page_size, total_pages=0,
            vep_job_id=None,
            message="VEP annotation pending or not yet available",
        )

    if not os.path.exists(vep_job.parquet_path):
        return DynamicVariantListResponse(
            columns=[], items=[], total=0,
            page=page, page_size=page_size, total_pages=0,
            vep_job_id=vep_job.job_id,
            message="Parquet file not found, VEP may still be processing",
        )

    service = ParquetService()
    result = service.read_parquet(
        vep_job.parquet_path,
        page=page,
        page_size=page_size,
        search=search,
    )

    return DynamicVariantListResponse(
        columns=result.columns,
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        vep_job_id=vep_job.job_id,
        message="",
    )


# ---------------------------------------------------------------------------
# Variant detail — single row from Parquet
# ---------------------------------------------------------------------------

@router.get("/detail/{vcf_file_id}/{row_index}", response_model=DynamicVariantDetailResponse)
async def get_variant_detail(
    vcf_file_id: str,
    row_index: int,
    db: Session = Depends(get_db),
):
    vep_job = (
        db.query(VEPJob)
        .filter(VEPJob.vcf_file_id == int(vcf_file_id), VEPJob.parquet_path.isnot(None))
        .order_by(VEPJob.created_at.desc())
        .first()
    )

    if not vep_job or not vep_job.parquet_path:
        raise HTTPException(status_code=404, detail="VEP annotation not yet available")

    service = ParquetService()
    columns = service.get_schema(vep_job.parquet_path)
    row = service.read_row(vep_job.parquet_path, row_index)

    if row is None:
        raise HTTPException(status_code=404, detail=f"Row {row_index} not found")

    return DynamicVariantDetailResponse(
        row_index=row_index,
        columns=columns,
        row=row,
    )
