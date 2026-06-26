"""
Phenotype-HPO Scoring API endpoints.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, Variant
from services.phenotype_hpo_service import (
    PhenotypeHpoService,
    PhenotypeHpoJobInfo,
    GenePhenotypeScore,
    PhenotypeHpoServiceError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/phenotype-hpo", tags=["phenotype-hpo"])


class SubmitRequest(BaseModel):
    vcf_file_id: int
    hpo_terms: List[str] = Field(default_factory=list)


class SubmitResponse(BaseModel):
    uid: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    uid: str
    status: str
    phase: str = ""
    message: str = ""


class GeneScoreResponse(BaseModel):
    gene_symbol: str
    hgnc_id: str = ""
    gene_score: float = 0.0
    conclusion_code: str = ""
    best_disease_score: float = 0.0
    best_disease_name: str = ""
    best_omim_id: str = ""
    best_orpha_id: str = ""
    best_mondo_id: str = ""
    best_disease_source_dbs: str = ""
    best_disease_match_status: str = ""
    mapping_basis: str = ""
    second_best_disease_score: float = 0.0
    score_gap_to_second_best: float = 0.0
    disease_profile_count: int = 0
    input_hpo_count: int = 0
    scoring_hpo_count: int = 0
    matched_hpo_count: int = 0
    unmatched_hpo_count: int = 0
    mean_input_hpo_ic: float = 0.0
    candidate_variant_count_in_gene: int = 0
    gene_sources: str = ""
    best_term_evidence_summary: str = ""
    db_versions: str = ""
    warning: str = ""
    sample_id: str = ""
    gene_rank: int = 0


class GeneScoresResponse(BaseModel):
    scores: List[GeneScoreResponse]
    total: int


_job_store: dict = {}


@router.post("/submit", response_model=SubmitResponse)
async def submit_phenotype_hpo_job(
    request: SubmitRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit a Phenotype-HPO scoring job.
    
    Takes VCF file ID and HPO terms, builds VEP CSV from variants,
    submits to external scoring service.
    """
    try:
        variants = db.query(Variant).filter(
            Variant.vcf_file_id == request.vcf_file_id,
            Variant.vep_annotated == True
        ).all()
        
        if not variants:
            raise HTTPException(
                status_code=400, 
                detail="No VEP-annotated variants found for this VCF file"
            )
        
        service = PhenotypeHpoService()
        vep_csv = service.build_vep_csv_from_variants(variants)
        
        hpo_terms = request.hpo_terms if request.hpo_terms else []
        
        job_info = await service.submit_job(vep_csv, hpo_terms)
        
        _job_store[job_info.uid] = {
            "vcf_file_id": request.vcf_file_id,
            "hpo_terms": hpo_terms,
        }
        
        background_tasks.add_task(
            _poll_and_store_results,
            job_info.uid,
            request.vcf_file_id
        )
        
        logger.info(f"Submitted Phenotype-HPO job {job_info.uid} for VCF {request.vcf_file_id}")
        
        return SubmitResponse(
            uid=job_info.uid,
            status=job_info.status,
            message=job_info.message
        )
        
    except PhenotypeHpoServiceError as e:
        logger.error(f"Phenotype-HPO service error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit Phenotype-HPO job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{uid}", response_model=JobStatusResponse)
async def get_job_status(uid: str):
    """
    Get the status of a Phenotype-HPO scoring job.
    """
    try:
        service = PhenotypeHpoService()
        status_data = await service.get_job_status(uid)
        
        return JobStatusResponse(
            uid=uid,
            status=status_data.get("status", "unknown"),
            phase=status_data.get("phase", ""),
            message=status_data.get("message", "")
        )
        
    except PhenotypeHpoServiceError as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{uid}", response_model=GeneScoresResponse)
async def get_gene_scores(uid: str):
    """
    Get gene phenotype scores for a completed job.
    """
    try:
        service = PhenotypeHpoService()
        scores = await service.get_gene_scores(uid)
        
        response_scores = []
        for s in scores:
            response_scores.append(GeneScoreResponse(
                gene_symbol=s.gene_symbol,
                hgnc_id=s.hgnc_id,
                gene_score=s.gene_score,
                conclusion_code=s.conclusion_code,
                best_disease_score=s.best_disease_score,
                best_disease_name=s.best_disease_name,
                best_omim_id=s.best_omim_id,
                best_orpha_id=s.best_orpha_id,
                best_mondo_id=s.best_mondo_id,
                best_disease_source_dbs=s.best_disease_source_dbs,
                best_disease_match_status=s.best_disease_match_status,
                mapping_basis=s.mapping_basis,
                second_best_disease_score=s.second_best_disease_score,
                score_gap_to_second_best=s.score_gap_to_second_best,
                disease_profile_count=s.disease_profile_count,
                input_hpo_count=s.input_hpo_count,
                scoring_hpo_count=s.scoring_hpo_count,
                matched_hpo_count=s.matched_hpo_count,
                unmatched_hpo_count=s.unmatched_hpo_count,
                mean_input_hpo_ic=s.mean_input_hpo_ic,
                candidate_variant_count_in_gene=s.candidate_variant_count_in_gene,
                gene_sources=s.gene_sources,
                best_term_evidence_summary=s.best_term_evidence_summary,
                db_versions=s.db_versions,
                warning=s.warning,
                sample_id=s.sample_id,
                gene_rank=s.gene_rank,
            ))
        
        return GeneScoresResponse(scores=response_scores, total=len(response_scores))
        
    except PhenotypeHpoServiceError as e:
        logger.error(f"Failed to get gene scores: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Get results error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _poll_and_store_results(uid: str, vcf_file_id: int):
    """
    Background task to poll for job completion and cache results.
    """
    try:
        service = PhenotypeHpoService()
        await service.poll_until_completion(uid)
        scores = await service.get_gene_scores(uid)
        
        _job_store[uid]["status"] = "completed"
        _job_store[uid]["scores"] = scores
        
        logger.info(f"Job {uid} completed with {len(scores)} gene scores")
        
    except Exception as e:
        logger.error(f"Background polling failed for {uid}: {e}")
        _job_store[uid]["status"] = "failed"
        _job_store[uid]["error"] = str(e)
