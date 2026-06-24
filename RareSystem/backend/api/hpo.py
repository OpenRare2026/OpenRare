"""
HPO API endpoints - extract phenotypes from clinical notes.
"""
import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from database.models import HPOJob
from services.hpo_service import HPOService, HPOTerm, generate_hpo_job_id, run_hpo_extraction_background

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hpo", tags=["hpo"])


class HPOTermLookupResponse(BaseModel):
    hpo_id: str
    name: str
    definition: Optional[str] = None
    synonyms: Optional[List[str]] = None
    category: Optional[str] = None


class ExtractRequest(BaseModel):
    patient_id: str
    clinical_note: str


class HPOTermResponse(BaseModel):
    phrase: str
    category: str
    hpo_id: str


class ExtractResponse(BaseModel):
    patient_id: str
    status: str
    terms: List[HPOTermResponse] = []


class ExtractAsyncResponse(BaseModel):
    job_id: str
    patient_id: str
    status: str


class HPOJobStatusResponse(BaseModel):
    job_id: str
    patient_id: Optional[int] = None
    status: str
    results: Optional[List[dict]] = None
    error: Optional[str] = None


@router.get("/lookup/{hpo_id}", response_model=HPOTermLookupResponse)
async def lookup_hpo_term(hpo_id: str):
    """
    Look up HPO term information by HPO ID.
    
    Returns the term's name, definition, and synonyms.
    """
    try:
        service = HPOService()
        result = await service.lookup_hpo_term(hpo_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"HPO term {hpo_id} not found")
        
        return HPOTermLookupResponse(
            hpo_id=result.get("hpo_id", hpo_id),
            name=result.get("name", ""),
            definition=result.get("definition"),
            synonyms=result.get("synonyms"),
            category=result.get("category")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HPO lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract", response_model=ExtractResponse)
async def extract_phenotypes(request: ExtractRequest):
    """
    Extract HPO phenotypes from clinical notes (synchronous).
    
    This endpoint:
    1. Submits clinical note to HPO service
    2. Polls for results (up to 120 seconds)
    3. Returns extracted HPO terms
    """
    try:
        service = HPOService()
        results = await service.extract_phenotypes(request.patient_id, request.clinical_note)
        
        if results is None:
            return ExtractResponse(
                patient_id=request.patient_id,
                status="failed"
            )
        
        terms = [
            HPOTermResponse(
                phrase=t.phrase,
                category=t.category,
                hpo_id=t.hpo_id
            )
            for t in results
        ]
        
        return ExtractResponse(
            patient_id=request.patient_id,
            status="completed",
            terms=terms
        )
        
    except Exception as e:
        logger.error(f"HPO extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-async", response_model=ExtractAsyncResponse)
async def extract_phenotypes_async(
    request: ExtractRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start async HPO extraction from clinical notes.
    
    This endpoint:
    1. Creates an HPOJob record with 'queued' status
    2. Schedules background task to extract HPO terms
    3. Returns immediately with job_id
    
    Client should poll /hpo/status/{job_id} to check progress.
    """
    try:
        job_id = generate_hpo_job_id()
        
        patient_id_int = int(request.patient_id) if request.patient_id.isdigit() else None
        
        hpo_job = HPOJob(
            job_id=job_id,
            patient_id=patient_id_int,
            clinical_note=request.clinical_note,
            status="queued"
        )
        db.add(hpo_job)
        db.commit()
        
        background_tasks.add_task(
            run_hpo_extraction_background,
            job_id,
            request.patient_id,
            request.clinical_note
        )
        
        logger.info(f"Started async HPO extraction job {job_id} for patient {request.patient_id}")
        
        return ExtractAsyncResponse(
            job_id=job_id,
            patient_id=request.patient_id,
            status="queued"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start HPO extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=HPOJobStatusResponse)
async def get_hpo_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of an HPO extraction job.
    
    Returns:
    - status: 'queued', 'processing', 'completed', or 'failed'
    - results: extracted HPO terms (when completed)
    - error: error message (when failed)
    """
    hpo_job = db.query(HPOJob).filter(HPOJob.job_id == job_id).first()
    
    if not hpo_job:
        raise HTTPException(status_code=404, detail="HPO job not found")
    
    return HPOJobStatusResponse(
        job_id=hpo_job.job_id,
        patient_id=hpo_job.patient_id,
        status=hpo_job.status,
        results=hpo_job.results,
        error=hpo_job.error
    )
