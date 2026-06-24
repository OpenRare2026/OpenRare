"""
PPI Score API endpoints.
Network-based gene prioritization using disease and tissue PPI anchors.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, Variant
from services.ppi_score_service import (
    PpiScoreService,
    PpiJobInfo,
    PpiGeneScore,
    PpiScoreServiceError,
)
from services.phenotype_hpo_service import PhenotypeHpoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ppi-score", tags=["ppi-score"])


class SubmitRequest(BaseModel):
    vcf_file_id: int
    hpo_job_uid: str
    hpo_terms: List[str] = Field(default_factory=list)


class SubmitResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: str = ""


class GeneScoreResponse(BaseModel):
    gene: str
    disease_score: float = 0.0
    tissue_score: float = 0.0
    topology_score: float = 0.0
    final_score: float = 0.0
    rank: int = 0
    disease_evidence: str = ""
    tissue_evidence: str = ""
    topology_evidence: str = ""
    neighbor_genes: str = ""
    hpo_match_count: int = 0


class GeneScoresResponse(BaseModel):
    scores: List[GeneScoreResponse]
    total: int


_job_store: dict = {}


@router.post("/submit", response_model=SubmitResponse)
async def submit_ppi_job(
    request: SubmitRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit a PPI scoring job.
    
    Requires:
    - vcf_file_id: The VCF file ID
    - hpo_job_uid: The HPO scoring job UID (to get gene_phenotype_score.csv)
    - hpo_terms: List of HPO IDs
    """
    try:
        hpo_service = PhenotypeHpoService()
        gene_scores_csv = await hpo_service.get_gene_scores_csv(request.hpo_job_uid)
        
        variants = db.query(Variant).filter(
            Variant.vcf_file_id == request.vcf_file_id,
            Variant.vep_annotated == True
        ).all()
        
        if not variants:
            raise HTTPException(
                status_code=400,
                detail="No VEP-annotated variants found for this VCF file"
            )
        
        ppi_service = PpiScoreService()
        vep_csv = ppi_service.build_vep_csv_from_variants(variants)
        
        job_info = await ppi_service.submit_job(
            gene_scores_csv,
            vep_csv,
            request.hpo_terms
        )
        
        _job_store[job_info.job_id] = {
            "vcf_file_id": request.vcf_file_id,
            "hpo_job_uid": request.hpo_job_uid,
        }
        
        background_tasks.add_task(
            _poll_and_store_results,
            job_info.job_id,
            request.vcf_file_id
        )
        
        logger.info(f"Submitted PPI job {job_info.job_id} for VCF {request.vcf_file_id}")
        
        return SubmitResponse(
            job_id=job_info.job_id,
            status=job_info.status,
            message=job_info.message
        )
        
    except PpiScoreServiceError as e:
        logger.error(f"PPI service error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit PPI job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a PPI scoring job.
    """
    try:
        service = PpiScoreService()
        status_data = await service.get_job_status(job_id)
        
        return JobStatusResponse(
            job_id=job_id,
            status=status_data.get("status", "unknown"),
            message=status_data.get("message", "")
        )
        
    except PpiScoreServiceError as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{job_id}", response_model=GeneScoresResponse)
async def get_gene_scores(job_id: str):
    """
    Get gene scores for a completed PPI job.
    """
    try:
        service = PpiScoreService()
        scores = await service.get_gene_scores(job_id)
        
        response_scores = []
        for s in scores:
            response_scores.append(GeneScoreResponse(
                gene=s.gene,
                disease_score=s.disease_score,
                tissue_score=s.tissue_score,
                topology_score=s.topology_score,
                final_score=s.final_score,
                rank=s.rank,
                disease_evidence=s.disease_evidence,
                tissue_evidence=s.tissue_evidence,
                topology_evidence=s.topology_evidence,
                neighbor_genes=s.neighbor_genes,
                hpo_match_count=s.hpo_match_count,
            ))
        
        return GeneScoresResponse(scores=response_scores, total=len(response_scores))
        
    except PpiScoreServiceError as e:
        logger.error(f"Failed to get gene scores: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Get results error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _poll_and_store_results(job_id: str, vcf_file_id: int):
    """
    Background task to poll for job completion and cache results.
    """
    service = PpiScoreService()
    try:
        await service.poll_until_completion(job_id)
        scores = await service.get_gene_scores(job_id)
        
        _job_store[job_id]["status"] = "completed"
        _job_store[job_id]["scores"] = scores
        
        logger.info(f"PPI job {job_id} completed with {len(scores)} gene scores")
    except Exception as e:
        logger.error(f"Background polling failed for {job_id}: {e}")
        _job_store[job_id]["status"] = "failed"
        _job_store[job_id]["error"] = str(e)
    finally:
        service.cleanup()
