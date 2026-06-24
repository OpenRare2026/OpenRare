"""
VEP Job Status API endpoints.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, VEPJob, Variant
from services.vep_service import VEPService
from services.vep_csv_parser import VEPCSVParser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vep", tags=["vep"])


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
    vep_annotated_count: Optional[int] = None

    class Config:
        from_attributes = True


def apply_vep_results_to_variants(vep_rows: list, vcf_file_id: int, db: Session) -> int:
    vep_lookup = {}
    for vv in vep_rows:
        chrom = vv.get("chrom", "")
        if chrom and chrom.lower().startswith("chr"):
            chrom = chrom[3:]
        if not chrom:
            location = vv.get("Location", "")
            if ":" in location:
                chrom = location.split(":")[0]
                if chrom.lower().startswith("chr"):
                    chrom = chrom[3:]

        pos = vv.get("pos", "")
        if not pos:
            location = vv.get("Location", "")
            if ":" in location:
                pos = location.split(":")[1]

        ref = vv.get("ref", "")
        alt = vv.get("alt", "")

        if not ref or not alt:
            uploaded_var = vv.get("Uploaded_variation", vv.get("#Uploaded_variation", vv.get("Uploaded variation", "")))
            parts = uploaded_var.split("_")
            if not chrom and len(parts) > 0:
                chrom = parts[0]
                if chrom.lower().startswith("chr"):
                    chrom = chrom[3:]
            if not pos and len(parts) > 1:
                pos = parts[1]
            if not ref and len(parts) > 2:
                ref = parts[2]
            if not alt and len(parts) > 3:
                alt = parts[3]

        key = f"{chrom}:{pos}:{ref}:{alt}"
        vep_lookup[key] = vv

    logger.info(f"VEP lookup built with {len(vep_lookup)} entries")

    def get_float(d, key, default=None):
        val = d.get(key, "")
        if val == "" or val == "-" or val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def get_int(d, key, default=None):
        val = d.get(key, "")
        if val == "" or val == "-" or val is None:
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    updated_count = 0
    for variant in db.query(Variant).filter(Variant.vcf_file_id == vcf_file_id).all():
        v_chrom = variant.chromosome
        if v_chrom.lower().startswith("chr"):
            v_chrom = v_chrom[3:]

        key = f"{v_chrom}:{variant.position}:{variant.ref}:{variant.alt}"
        vep_data = vep_lookup.get(key)
        if vep_data:
            variant.hgvs_c = vep_data.get("hgvsc", "")
            variant.hgvs_p = vep_data.get("hgvsp", "")
            variant.consequence = vep_data.get("consequence", "")
            variant.impact = vep_data.get("impact", "")
            variant.transcript = vep_data.get("transcript_id", "")
            gene_symbol = vep_data.get("gene_symbol", "")
            if gene_symbol:
                variant.all_genes = gene_symbol
                if not variant.gene:
                    variant.gene = gene_symbol
            variant.cdna_position = vep_data.get("cdna_position", "")
            variant.cds_position = vep_data.get("cds_position", "")
            variant.protein_position = vep_data.get("protein_position", "")
            variant.amino_acids = vep_data.get("amino_acids", "")
            variant.codons = vep_data.get("codons", "")
            variant.exon = vep_data.get("exon", "")
            variant.intron = vep_data.get("intron", "")
            variant.strand = vep_data.get("strand", "")
            variant.protein_domains = vep_data.get("protein_domains", "")
            variant.revel_score = get_float(vep_data, "revel_score")
            variant.cadd = get_float(vep_data, "cadd_phred")
            variant.gnomad_popmax_af = get_float(vep_data, "gnomAD_popmax_AF")
            variant.gnomad_eas_af = get_float(vep_data, "gnomAD_eas_AF")
            variant.gnomad_nhomalt = get_int(vep_data, "gnomAD_nhomalt")
            variant.spliceai_ds_max = get_float(vep_data, "spliceAI_ds_max")
            variant.spliceai_type = vep_data.get("spliceAI_type", "")
            variant.loftee_lof_flag = vep_data.get("loftee_lof_flag", "")
            variant.loftee_lof_filter = vep_data.get("loftee_lof_filter", "")
            variant.clinvar_significance = vep_data.get("clinvar_significance", "")
            variant.clinvar_review_status = vep_data.get("clinvar_review_status", "")
            variant.clinvar_star_rating = get_int(vep_data, "clinvar_star_rating")
            variant.pathogenic_rank = get_int(vep_data, "pathogenic_rank")
            variant.evidence_summary = vep_data.get("evidence_summary", "")
            variant.sift = vep_data.get("sift", "")
            variant.polyphen = vep_data.get("polyphen", "")
            variant.vep_annotated = True
            updated_count += 1

    db.commit()
    return updated_count


@router.get("/jobs/{job_id}/status", response_model=VEPJobResponse)
async def get_vep_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VEPJob).filter(VEPJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"VEP job {job_id} not found")

    vep_annotated_count = db.query(Variant).filter(
        Variant.vcf_file_id == job.vcf_file_id,
        Variant.vep_annotated == True
    ).count()

    if vep_annotated_count > 0:
        job.status = "completed"
        if job.rows is None or job.rows == 0:
            job.rows = vep_annotated_count
        db.commit()
        logger.info(f"Job {job_id}: already annotated ({vep_annotated_count} variants), returning completed")
        return VEPJobResponse(
            job_id=job.job_id,
            status="completed",
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
            vep_annotated_count=vep_annotated_count,
        )

    if job.status in ("failed", "timeout", "error"):
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
            vep_annotated_count=0,
        )

    vep_service = VEPService()
    try:
        remote_status = await vep_service.get_status(job_id)
        logger.info(f"Job {job_id}: remote status = {remote_status.status}, result_url = {remote_status.result_url}")
        job.status = remote_status.status
        if remote_status.result_url:
            job.result_url = remote_status.result_url
        if remote_status.rows is not None:
            job.rows = remote_status.rows
        if remote_status.error:
            job.error = remote_status.error
        db.commit()
    except Exception as e:
        logger.error(f"Failed to fetch VEP remote status for {job_id}: {e}")
        return VEPJobResponse(
            job_id=job.job_id,
            status=job.status or "queued",
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
            vep_annotated_count=0,
        )

    completed_statuses = ("completed", "completion", "success", "finished", "done")
    if job.status in completed_statuses and job.result_url:
        import time
        time.sleep(3)
        try:
            csv_content = await vep_service.get_result(job.result_url)
            if csv_content:
                parser = VEPCSVParser()
                vep_result = parser.parse(csv_content)
                logger.info(f"VEP returned {len(vep_result.rows)} annotated variants for job {job_id}")

                if len(vep_result.rows) > 0:
                    updated_count = apply_vep_results_to_variants(vep_result.rows, job.vcf_file_id, db)
                    job.rows = len(vep_result.rows)
                    job.status = "completed"
                    db.commit()
                    vep_annotated_count = updated_count
                    logger.info(f"VEP annotation completed: {updated_count} variants updated for job {job_id}")
                else:
                    job.rows = 0
                    job.status = "completed"
                    db.commit()
                    logger.info(f"VEP returned 0 variants for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to fetch VEP results for {job_id}: {e}")

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
        vep_annotated_count=vep_annotated_count,
    )


@router.get("/jobs/{job_id}", response_model=VEPJobResponse)
async def get_vep_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VEPJob).filter(VEPJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"VEP job {job_id} not found")

    vep_annotated_count = db.query(Variant).filter(
        Variant.vcf_file_id == job.vcf_file_id,
        Variant.vep_annotated == True
    ).count()

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
        vep_annotated_count=vep_annotated_count,
    )


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

    vep_annotated_count = db.query(Variant).filter(
        Variant.vcf_file_id == job.vcf_file_id,
        Variant.vep_annotated == True
    ).count()

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
        vep_annotated_count=vep_annotated_count,
    )


@router.get("/jobs/{job_id}/log")
async def get_vep_job_log(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VEPJob).filter(VEPJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"VEP job {job_id} not found")
    if not job.log_url:
        return {"log": None, "message": "No log URL available for this job"}
    try:
        vep_service = VEPService()
        log_content = await vep_service.get_log(job.log_url)
        return {"log": log_content}
    except Exception as e:
        logger.error(f"Failed to fetch VEP job log: {e}")
        return {"log": None, "error": str(e)}
