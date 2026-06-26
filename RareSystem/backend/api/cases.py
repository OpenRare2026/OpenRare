"""
Cases API endpoints - List and browse imported VCF cases.
"""
import logging
import os
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, Patient, VCFFile, ACMGClassification, VEPJob
from database.case_models import CaseDocument, ChatSession, LLMSettings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cases", tags=["cases"])


class UpdateHpoTermsRequest(BaseModel):
    hpo_terms: List[dict]


class UpdateHpoTermCategoryRequest(BaseModel):
    hpo_id: str
    display_category: str  # "primary" or "secondary"


class VCFFileSummary(BaseModel):
    id: int
    file_name: str
    upload_date: str
    variant_count: int
    classified_count: int

    class Config:
        from_attributes = True


class CaseSummary(BaseModel):
    patient_id: int
    patient_name: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    ethnicity: Optional[str]
    diagnosis_description: Optional[str]
    medical_history: Optional[str]
    hpo_terms: Optional[List[dict]] = None
    vcf_files: List[VCFFileSummary]
    total_variants: int
    total_classified: int

    class Config:
        from_attributes = True

    @staticmethod
    def _normalize_hpo_terms(hpo_terms):
        """Normalize HPO terms to list-of-dict format.
        Database may store either List[str] (e.g. ["HP:0001324"]) or
        List[dict] (e.g. [{"hpo_id": "HP:0001324", ...}])."""
        if not hpo_terms:
            return None
        normalized = []
        for term in hpo_terms:
            if isinstance(term, str):
                normalized.append({"hpo_id": term, "display_category": "primary"})
            elif isinstance(term, dict):
                normalized.append(term)
        return normalized


class CaseListResponse(BaseModel):
    cases: List[CaseSummary]
    total: int


@router.get("", response_model=CaseListResponse)
async def list_cases(
    db: Session = Depends(get_db)
):
    patients = db.query(Patient).order_by(Patient.id.desc()).all()

    cases = []
    for patient in patients:
        vcf_files = db.query(VCFFile).filter(
            VCFFile.patient_id == patient.id
        ).all()

        vcf_summaries = []
        total_variants = 0
        total_classified = 0

        for vcf in vcf_files:
            vep_job = db.query(VEPJob).filter(
                VEPJob.vcf_file_id == vcf.id
            ).order_by(VEPJob.created_at.desc()).first()
            variant_count = vep_job.rows if vep_job and vep_job.rows else 0

            classified_count = 0

            total_variants += variant_count
            total_classified += classified_count

            vcf_summaries.append(VCFFileSummary(
                id=vcf.id,
                file_name=vcf.file_name,
                upload_date=vcf.upload_date.isoformat() if vcf.upload_date else "",
                variant_count=variant_count,
                classified_count=classified_count,
            ))

        cases.append(CaseSummary(
            patient_id=patient.id,
            patient_name=patient.name,
            age=patient.age,
            sex=patient.sex,
            ethnicity=patient.ethnicity,
            diagnosis_description=patient.diagnosis_description,
            medical_history=patient.medical_history,
            hpo_terms=CaseSummary._normalize_hpo_terms(patient.hpo_terms),
            vcf_files=vcf_summaries,
            total_variants=total_variants,
            total_classified=total_classified,
        ))

    return CaseListResponse(cases=cases, total=len(cases))


@router.get("/{patient_id}", response_model=CaseSummary)
async def get_case(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Case not found")

    vcf_files = db.query(VCFFile).filter(
        VCFFile.patient_id == patient.id
    ).all()

    vcf_summaries = []
    total_variants = 0
    total_classified = 0

    for vcf in vcf_files:
        vep_job = db.query(VEPJob).filter(
            VEPJob.vcf_file_id == vcf.id
        ).order_by(VEPJob.created_at.desc()).first()
        variant_count = vep_job.rows if vep_job and vep_job.rows else 0

        classified_count = 0

        total_variants += variant_count
        total_classified += classified_count

        vcf_summaries.append(VCFFileSummary(
            id=vcf.id,
            file_name=vcf.file_name,
            upload_date=vcf.upload_date.isoformat() if vcf.upload_date else "",
            variant_count=variant_count,
            classified_count=classified_count,
        ))

    return CaseSummary(
        patient_id=patient.id,
        patient_name=patient.name,
        age=patient.age,
        sex=patient.sex,
        ethnicity=patient.ethnicity,
        diagnosis_description=patient.diagnosis_description,
        medical_history=patient.medical_history,
        hpo_terms=CaseSummary._normalize_hpo_terms(patient.hpo_terms),
        vcf_files=vcf_summaries,
        total_variants=total_variants,
        total_classified=total_classified,
    )


class UpdateHpoTermsResponse(BaseModel):
    message: str
    patient_id: int


@router.put("/{patient_id}/hpo-terms", response_model=UpdateHpoTermsResponse)
async def update_hpo_terms(
    patient_id: int,
    request: UpdateHpoTermsRequest,
    db: Session = Depends(get_db)
):
    """
    Update HPO terms for a patient.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Case not found")
    
    patient.hpo_terms = request.hpo_terms
    db.commit()
    
    logger.info(f"Updated HPO terms for patient {patient_id}: {len(request.hpo_terms)} terms")
    
    return UpdateHpoTermsResponse(
        message="HPO terms updated",
        patient_id=patient_id
    )


class UpdateHpoTermCategoryResponse(BaseModel):
    message: str
    patient_id: int
    hpo_id: str
    display_category: str


@router.patch("/{patient_id}/hpo-terms/category", response_model=UpdateHpoTermCategoryResponse)
async def update_hpo_term_category(
    patient_id: int,
    request: UpdateHpoTermCategoryRequest,
    db: Session = Depends(get_db)
):
    """
    Update the display category (primary/secondary) of a single HPO term.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if not patient.hpo_terms:
        raise HTTPException(status_code=404, detail="No HPO terms found for this patient")
    
    # Find and update the term
    updated = False
    for term in patient.hpo_terms:
        if term.get("hpo_id") == request.hpo_id:
            term["display_category"] = request.display_category
            updated = True
            break
    
    if not updated:
        raise HTTPException(status_code=404, detail=f"HPO term {request.hpo_id} not found")
    
    db.commit()
    
    logger.info(f"Updated HPO term {request.hpo_id} category to {request.display_category} for patient {patient_id}")
    
    return UpdateHpoTermCategoryResponse(
        message="HPO term category updated",
        patient_id=patient_id,
        hpo_id=request.hpo_id,
        display_category=request.display_category
    )


class DeleteCaseResponse(BaseModel):
    message: str
    patient_id: int


@router.delete("/{patient_id}", response_model=DeleteCaseResponse)
async def delete_case(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a case and all associated data.
    
    This endpoint:
    1. Deletes VCF files from disk
    2. Deletes non-cascaded records (CaseDocument, ChatSession, LLMSettings)
    3. Clears the FAISS index
    4. Deletes the Patient record (cascade handles VCFFile, Variant, ACMG records, Reports)
    """
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Case not found")
    
    try:
        # Step 1: Get all VCF files and delete from disk
        vcf_files = db.query(VCFFile).filter(VCFFile.patient_id == patient_id).all()
        for vcf in vcf_files:
            if vcf.file_path and os.path.exists(vcf.file_path):
                try:
                    os.remove(vcf.file_path)
                    logger.info(f"Deleted VCF file from disk: {vcf.file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete VCF file {vcf.file_path}: {e}")
            else:
                logger.warning(f"VCF file not found on disk: {vcf.file_path}")
            
            # Delete VEP jobs for this VCF file (must be deleted before VCFFile)
            db.query(VEPJob).filter(VEPJob.vcf_file_id == vcf.id).delete()
        
        # Step 2: Delete non-cascaded records
        # CaseDocument (cascade to CaseEmbedding)
        db.query(CaseDocument).filter(CaseDocument.patient_id == patient_id).delete()
        
        # ChatSession (cascade to ChatMessageRecord)
        db.query(ChatSession).filter(ChatSession.patient_id == patient_id).delete()
        
        # LLMSettings
        db.query(LLMSettings).filter(LLMSettings.patient_id == patient_id).delete()
        
        # Step 3: Clear FAISS index (reset in-memory index)
        try:
            from services.embedding_service import get_embedding_service
            embedding_service = get_embedding_service()
            embedding_service.clear_index()
            logger.info("Cleared FAISS index after case deletion")
        except Exception as e:
            logger.warning(f"Failed to clear FAISS index: {e}")
        
        # Step 4: Delete the Patient record
        # SQLAlchemy cascade will handle: VCFFile -> Variant -> ACMGEvidence, ACMGClassification
        # And: ClinicalReport, ResearchReport
        db.delete(patient)
        db.commit()
        
        logger.info(f"Successfully deleted case with patient_id={patient_id}")
        
        return DeleteCaseResponse(
            message="Case deleted",
            patient_id=patient_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting case {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete case: {str(e)}")
