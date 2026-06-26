"""
Variant API endpoints for VCF upload and variant management.
"""
import logging
import os
import tempfile
import time
import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, Variant, VCFFile, Patient, ACMGClassification, VEPJob
from database.session import verify_tables, init_db
from services.vcf_parser import VCFParser, VCFParseError
from services.variant_detector import VariantDetector, DetectionConfig
from services.gene_lookup import get_gene_lookup_service
from services.vep_service import VEPService
from config import VEP_ENABLED

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/variants", tags=["variants"])


class UploadResponse(BaseModel):
    vcf_file_id: str
    patient_id: str
    total_variants: int
    message: str
    vep_status: str = "skipped"
    vep_job_id: Optional[str] = None
    vep_job_db_id: Optional[int] = None


class VariantResponse(BaseModel):
    id: str
    chromosome: str
    position: int
    ref: str
    alt: str
    variant_type: str
    quality: Optional[float]
    filter_status: Optional[str]
    info_field: Optional[dict]
    gene: Optional[str]
    vcf_file_id: str
    hgvs_c: Optional[str] = None
    hgvs_p: Optional[str] = None
    consequence: Optional[str] = None
    impact: Optional[str] = None
    transcript: Optional[str] = None
    all_genes: Optional[str] = None
    cdna_position: Optional[str] = None
    cds_position: Optional[str] = None
    protein_position: Optional[str] = None
    amino_acids: Optional[str] = None
    codons: Optional[str] = None
    exon: Optional[str] = None
    intron: Optional[str] = None
    strand: Optional[str] = None
    protein_domains: Optional[str] = None
    revel_score: Optional[float] = None
    cadd: Optional[float] = None
    gnomad_popmax_af: Optional[float] = None
    gnomad_eas_af: Optional[float] = None
    gnomad_nhomalt: Optional[int] = None
    spliceai_ds_max: Optional[float] = None
    spliceai_type: Optional[str] = None
    loftee_lof_flag: Optional[str] = None
    loftee_lof_filter: Optional[str] = None
    clinvar_significance: Optional[str] = None
    clinvar_review_status: Optional[str] = None
    clinvar_star_rating: Optional[int] = None
    pathogenic_rank: Optional[int] = None
    evidence_summary: Optional[str] = None
    sift: Optional[str] = None
    polyphen: Optional[str] = None
    vep_annotated: Optional[bool] = None

    class Config:
        from_attributes = True


class VariantListResponse(BaseModel):
    items: List[VariantResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


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
    vep_hgvs: str = Form("true"),
    vep_no_pick: str = Form("false"),
    vep_format: str = Form("vcf"),
    vep_fork: str = Form("1"),
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

        detector = VariantDetector(DetectionConfig())
        detected_variants = detector.detect(tmp_path)

        # Annotate genes for variants
        gene_lookup = get_gene_lookup_service()
        for detected in detected_variants:
            gene_name = gene_lookup.lookup_gene(detected.chromosome, detected.position)
            detected.gene = gene_name

        parsed_hpo_terms = None
        if hpo_terms:
            try:
                parsed_hpo_terms = json.loads(hpo_terms)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse hpo_terms JSON: {hpo_terms[:100]}")

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
                        age=age,
                        sex=sex,
                        ethnicity=ethnicity,
                        diagnosis_description=diagnosis_description,
                        medical_history=medical_history,
                        hpo_terms=parsed_hpo_terms
                    )
                else:
                    patient = Patient(
                        id=pid,
                        name=patient_name or f"Patient_{pid}",
                        age=age,
                        sex=sex,
                        ethnicity=ethnicity,
                        diagnosis_description=diagnosis_description,
                        medical_history=medical_history,
                        hpo_terms=parsed_hpo_terms
                    )
            else:
                patient = Patient(
                    name=patient_name or f"Patient_{int(time.time())}",
                    age=age,
                    sex=sex,
                    ethnicity=ethnicity,
                    diagnosis_description=diagnosis_description,
                    medical_history=medical_history,
                    hpo_terms=parsed_hpo_terms
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

        vcf_file = VCFFile(
            file_name=filename,
            file_path=tmp_path,
            patient_id=patient.id
        )
        db.add(vcf_file)
        db.flush()

        vcf_file_id = vcf_file.id

        existing_keys = set()
        for v in db.query(Variant).filter(Variant.vcf_file_id == vcf_file_id).all():
            key = f"{v.chromosome}:{v.position}:{v.ref}:{v.alt}"
            existing_keys.add(key)

        new_count = 0
        for detected in detected_variants:
            key = f"{detected.chromosome}:{detected.position}:{detected.reference}:{detected.alternate}"
            if key in existing_keys:
                continue
            variant = Variant(
                chromosome=detected.chromosome,
                position=detected.position,
                ref=detected.reference,
                alt=detected.alternate,
                variant_type=detected.variant_type,
                quality=detected.quality,
                filter_status=detected.filter_status,
                info_field=detected.info,
                gene=detected.gene,
                vcf_file_id=vcf_file_id
            )
            db.add(variant)
            new_count += 1

        db.commit()

        logger.info(f"Uploaded VCF file {filename} with {new_count} new variants (total detected: {len(detected_variants)})")

        vep_status = "skipped"
        vep_job_id = None
        vep_job_db_id = None

        if VEP_ENABLED:
            vep_options = {
                "hgvs": vep_hgvs.lower() in ("true", "1", "yes"),
                "no_pick": vep_no_pick.lower() in ("true", "1", "yes"),
                "format": vep_format,
                "fork": int(vep_fork),
            }
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
                    result_url=job_info.result_url,
                    log_url=job_info.log_url,
                    rows=job_info.rows,
                    error=job_info.error,
                )
                db.add(vep_job_record)
                db.commit()
                db.refresh(vep_job_record)
                vep_job_db_id = vep_job_record.id
                vep_status = "queued"

                logger.info(f"VEP job submitted asynchronously: {vep_job_id}, db_id={vep_job_db_id}")

            except Exception as e:
                logger.error(f"Failed to submit VEP job: {e}")
                vep_status = "failed"

        return UploadResponse(
            vcf_file_id=str(vcf_file_id),
            patient_id=str(patient.id),
            total_variants=len(detected_variants),
            message=f"Successfully uploaded {filename}",
            vep_status=vep_status,
            vep_job_id=vep_job_id,
            vep_job_db_id=vep_job_db_id,
        )

    except HTTPException:
        raise
    except VCFParseError as e:
        raise HTTPException(status_code=400, detail=f"VCF parsing error: {str(e)}")
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{vcf_file_id}", response_model=VariantListResponse)
async def get_variants(
    vcf_file_id: str,
    page: int = 1,
    page_size: int = 50,
    gene: Optional[str] = None,
    chromosome: Optional[str] = None,
    variant_type: Optional[str] = None,
    impact: Optional[str] = None,
    consequence: Optional[str] = None,
    clinvar_significance: Optional[str] = None,
    loftee_lof_flag: Optional[str] = None,
    pathogenic_rank: Optional[int] = None,
    vep_annotated: Optional[str] = None,
    position_min: Optional[int] = None,
    position_max: Optional[int] = None,
    revel_score_min: Optional[float] = None,
    cadd_min: Optional[float] = None,
    spliceai_ds_max_min: Optional[float] = None,
    gnomad_popmax_af_max: Optional[float] = None,
    gnomad_eas_af_max: Optional[float] = None,
    clinvar_star_rating_min: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Variant).filter(Variant.vcf_file_id == vcf_file_id)
    
    if gene:
        query = query.filter(Variant.gene.ilike(f"%{gene}%"))
    if chromosome:
        query = query.filter(Variant.chromosome == chromosome)
    if variant_type:
        query = query.filter(Variant.variant_type == variant_type)
    if impact:
        query = query.filter(Variant.impact == impact)
    if consequence:
        query = query.filter(Variant.consequence.ilike(f"%{consequence}%"))
    if clinvar_significance:
        query = query.filter(Variant.clinvar_significance.ilike(f"%{clinvar_significance}%"))
    if loftee_lof_flag:
        query = query.filter(Variant.loftee_lof_flag == loftee_lof_flag)
    if pathogenic_rank is not None:
        query = query.filter(Variant.pathogenic_rank == pathogenic_rank)
    if vep_annotated:
        query = query.filter(Variant.vep_annotated == (vep_annotated.lower() == "true"))
    if position_min:
        query = query.filter(Variant.position >= position_min)
    if position_max:
        query = query.filter(Variant.position <= position_max)
    if revel_score_min is not None:
        query = query.filter(Variant.revel_score >= revel_score_min)
    if cadd_min is not None:
        query = query.filter(Variant.cadd >= cadd_min)
    if spliceai_ds_max_min is not None:
        query = query.filter(Variant.spliceai_ds_max >= spliceai_ds_max_min)
    if gnomad_popmax_af_max is not None:
        query = query.filter((Variant.gnomad_popmax_af == None) | (Variant.gnomad_popmax_af <= gnomad_popmax_af_max))
    if gnomad_eas_af_max is not None:
        query = query.filter((Variant.gnomad_eas_af == None) | (Variant.gnomad_eas_af <= gnomad_eas_af_max))
    if clinvar_star_rating_min is not None:
        query = query.filter(Variant.clinvar_star_rating >= clinvar_star_rating_min)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    variants = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return VariantListResponse(
        items=[VariantResponse(
            id=str(v.id),
            chromosome=str(v.chromosome),
            position=int(v.position),
            ref=str(v.ref),
            alt=str(v.alt),
            variant_type=str(v.variant_type),
            quality=float(v.quality) if v.quality else None,
            filter_status=str(v.filter_status) if v.filter_status else None,
            info_field=dict(v.info_field) if v.info_field else None,
            gene=str(v.gene) if v.gene else None,
            vcf_file_id=str(v.vcf_file_id),
            hgvs_c=str(v.hgvs_c) if v.hgvs_c else None,
            hgvs_p=str(v.hgvs_p) if v.hgvs_p else None,
            consequence=str(v.consequence) if v.consequence else None,
            impact=str(v.impact) if v.impact else None,
            transcript=str(v.transcript) if v.transcript else None,
            all_genes=str(v.all_genes) if v.all_genes else None,
            cdna_position=str(v.cdna_position) if v.cdna_position else None,
            cds_position=str(v.cds_position) if v.cds_position else None,
            protein_position=str(v.protein_position) if v.protein_position else None,
            amino_acids=str(v.amino_acids) if v.amino_acids else None,
            codons=str(v.codons) if v.codons else None,
            exon=str(v.exon) if v.exon else None,
            intron=str(v.intron) if v.intron else None,
            strand=str(v.strand) if v.strand else None,
            protein_domains=str(v.protein_domains) if v.protein_domains else None,
            revel_score=float(v.revel_score) if v.revel_score else None,
            cadd=float(v.cadd) if v.cadd else None,
            gnomad_popmax_af=float(v.gnomad_popmax_af) if v.gnomad_popmax_af else None,
            gnomad_eas_af=float(v.gnomad_eas_af) if v.gnomad_eas_af else None,
            gnomad_nhomalt=int(v.gnomad_nhomalt) if v.gnomad_nhomalt else None,
            spliceai_ds_max=float(v.spliceai_ds_max) if v.spliceai_ds_max else None,
            spliceai_type=str(v.spliceai_type) if v.spliceai_type else None,
            loftee_lof_flag=str(v.loftee_lof_flag) if v.loftee_lof_flag else None,
            loftee_lof_filter=str(v.loftee_lof_filter) if v.loftee_lof_filter else None,
            clinvar_significance=str(v.clinvar_significance) if v.clinvar_significance else None,
            clinvar_review_status=str(v.clinvar_review_status) if v.clinvar_review_status else None,
            clinvar_star_rating=int(v.clinvar_star_rating) if v.clinvar_star_rating else None,
            pathogenic_rank=v.pathogenic_rank,
            evidence_summary=str(v.evidence_summary) if v.evidence_summary else None,
            sift=str(v.sift) if v.sift else None,
            polyphen=str(v.polyphen) if v.polyphen else None,
            vep_annotated=bool(v.vep_annotated) if v.vep_annotated is not None else None,
        ) for v in variants],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/detail/{variant_id}", response_model=VariantResponse)
async def get_variant_detail(
    variant_id: str,
    db: Session = Depends(get_db)
):
    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    return VariantResponse(
        id=str(variant.id),
        chromosome=str(variant.chromosome),
        position=int(variant.position),
        ref=str(variant.ref),
        alt=str(variant.alt),
        variant_type=str(variant.variant_type),
        quality=float(variant.quality) if variant.quality else None,
        filter_status=str(variant.filter_status) if variant.filter_status else None,
        info_field=dict(variant.info_field) if variant.info_field else None,
        gene=str(variant.gene) if variant.gene else None,
        vcf_file_id=str(variant.vcf_file_id),
        hgvs_c=str(variant.hgvs_c) if variant.hgvs_c else None,
        hgvs_p=str(variant.hgvs_p) if variant.hgvs_p else None,
        consequence=str(variant.consequence) if variant.consequence else None,
        impact=str(variant.impact) if variant.impact else None,
        transcript=str(variant.transcript) if variant.transcript else None,
        all_genes=str(variant.all_genes) if variant.all_genes else None,
        cdna_position=str(variant.cdna_position) if variant.cdna_position else None,
        cds_position=str(variant.cds_position) if variant.cds_position else None,
        protein_position=str(variant.protein_position) if variant.protein_position else None,
        amino_acids=str(variant.amino_acids) if variant.amino_acids else None,
        codons=str(variant.codons) if variant.codons else None,
        exon=str(variant.exon) if variant.exon else None,
        intron=str(variant.intron) if variant.intron else None,
        strand=str(variant.strand) if variant.strand else None,
        protein_domains=str(variant.protein_domains) if variant.protein_domains else None,
        revel_score=float(variant.revel_score) if variant.revel_score else None,
        cadd=float(variant.cadd) if variant.cadd else None,
        gnomad_popmax_af=float(variant.gnomad_popmax_af) if variant.gnomad_popmax_af else None,
        gnomad_eas_af=float(variant.gnomad_eas_af) if variant.gnomad_eas_af else None,
        gnomad_nhomalt=int(variant.gnomad_nhomalt) if variant.gnomad_nhomalt else None,
        spliceai_ds_max=float(variant.spliceai_ds_max) if variant.spliceai_ds_max else None,
        spliceai_type=str(variant.spliceai_type) if variant.spliceai_type else None,
        loftee_lof_flag=str(variant.loftee_lof_flag) if variant.loftee_lof_flag else None,
        loftee_lof_filter=str(variant.loftee_lof_filter) if variant.loftee_lof_filter else None,
        clinvar_significance=str(variant.clinvar_significance) if variant.clinvar_significance else None,
        clinvar_review_status=str(variant.clinvar_review_status) if variant.clinvar_review_status else None,
        clinvar_star_rating=int(variant.clinvar_star_rating) if variant.clinvar_star_rating else None,
        pathogenic_rank=variant.pathogenic_rank,
        evidence_summary=str(variant.evidence_summary) if variant.evidence_summary else None,
        sift=str(variant.sift) if variant.sift else None,
        polyphen=str(variant.polyphen) if variant.polyphen else None,
        vep_annotated=bool(variant.vep_annotated) if variant.vep_annotated is not None else None,
    )
