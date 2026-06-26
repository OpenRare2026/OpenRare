"""
Phenotype-HPO Scoring API endpoints.

POST /submit — submits VEP output CSV to the phenotype-HPO scoring service
               at PHENOTYPE_HPO_API_BASE_URL, polls until completion, downloads
               gene_phenotype_score.csv, saves to VEPJob record, returns parsed results.

GET /results/{vcf_file_id} — returns cached gene phenotype scores from the saved CSV.
"""
import csv
import logging
import os
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, VEPJob
from services.phenotype_hpo_service import PhenotypeHpoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/phenotype-hpo", tags=["phenotype-hpo"])

DATA_DIR = os.environ.get(
    "VEP_DATA_DIR",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "phenotype_hpo_results"
    ),
)


class SubmitRequest(BaseModel):
    vcf_file_id: int
    hpo_terms: List[str] = Field(default_factory=list)


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


def _parse_gene_phenotype_score_csv(path: str) -> List[GeneScoreResponse]:
    """Parse gene_phenotype_score.csv into response models."""
    results = []
    col_map = {
        "gene_symbol": "gene_symbol",
        "hgnc_id": "hgnc_id",
        "gene_score": "gene_score",
        "conclusion_code": "conclusion_code",
        "best_disease_score": "best_disease_score",
        "best_disease_name": "best_disease_name",
        "best_omim_id": "best_omim_id",
        "best_orpha_id": "best_orpha_id",
        "best_mondo_id": "best_mondo_id",
        "best_disease_source_dbs": "best_disease_source_dbs",
        "best_disease_match_status": "best_disease_match_status",
        "mapping_basis": "mapping_basis",
        "second_best_disease_score": "second_best_disease_score",
        "score_gap_to_second_best": "score_gap_to_second_best",
        "disease_profile_count": "disease_profile_count",
        "input_hpo_count": "input_hpo_count",
        "scoring_hpo_count": "scoring_hpo_count",
        "matched_hpo_count": "matched_hpo_count",
        "unmatched_hpo_count": "unmatched_hpo_count",
        "mean_input_hpo_ic": "mean_input_hpo_ic",
        "candidate_variant_count_in_gene": "candidate_variant_count_in_gene",
        "gene_sources": "gene_sources",
        "best_term_evidence_summary": "best_term_evidence_summary",
        "db_versions": "db_versions",
        "warning": "warning",
        "sample_id": "sample_id",
        "gene_rank": "gene_rank",
    }

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = {}
            for csv_col, model_field in col_map.items():
                val = row.get(csv_col, "")
                field_info = GeneScoreResponse.model_fields.get(model_field)
                if field_info:
                    ann = field_info.annotation
                    if ann is float:
                        try:
                            item[model_field] = float(val) if val and val != "-" else 0.0
                        except ValueError:
                            item[model_field] = 0.0
                    elif ann is int:
                        try:
                            item[model_field] = int(val) if val and val != "-" else 0
                        except ValueError:
                            item[model_field] = 0
                    else:
                        item[model_field] = val
            results.append(GeneScoreResponse(**item))

    return results


@router.post("/submit", response_model=GeneScoresResponse)
async def submit_phenotype_hpo_job(
    request: SubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit VEP output to phenotype-HPO scoring service, poll until complete,
    download gene_phenotype_score.csv, save to VEPJob, and return parsed results.
    """
    # 1. Find the VEPJob with a saved CSV for this vcf_file_id
    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == request.vcf_file_id,
        VEPJob.csv_path.isnot(None),
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.csv_path:
        raise HTTPException(
            status_code=400,
            detail="No VEP results available for this VCF file. "
                   "VEP annotation must complete before phenotype-HPO scoring.",
        )

    vep_csv_path = Path(vep_job.csv_path)
    if not vep_csv_path.exists():
        raise HTTPException(
            status_code=400,
            detail="VEP CSV file not found on disk.",
        )

    # 2. Check if gene_phenotype_score.csv already exists for this VEPJob
    if vep_job.gene_phenotype_score_path:
        existing_path = Path(vep_job.gene_phenotype_score_path)
        if existing_path.exists():
            logger.info(
                f"Gene phenotype score already available for vcf_file_id={request.vcf_file_id}, "
                f"returning cached results from {existing_path}"
            )
            try:
                scores = _parse_gene_phenotype_score_csv(str(existing_path))
                return GeneScoresResponse(scores=scores, total=len(scores))
            except Exception as e:
                logger.warning(f"Failed to parse cached gene phenotype scores: {e}")

    # 3. Submit to phenotype-HPO service
    service = PhenotypeHpoService()
    try:
        job_info = await service.submit_run(
            csv_path=str(vep_csv_path),
            hpo_terms=request.hpo_terms if request.hpo_terms else None,
        )
    except Exception as e:
        logger.error(f"Failed to submit to phenotype-HPO service: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Phenotype-HPO service submission failed: {e}",
        )

    if not job_info.uid:
        raise HTTPException(
            status_code=502,
            detail="Phenotype-HPO service returned empty job uid.",
        )

    # 4. Poll until completion
    try:
        final_info = await service.poll_until_complete(job_info.uid)
    except Exception as e:
        logger.error(f"Failed to poll phenotype-HPO job {job_info.uid}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Phenotype-HPO service polling failed: {e}",
        )

    if final_info.status in ("failed", "error", "timeout"):
        error_msg = final_info.error or f"Job ended with status: {final_info.status}"
        logger.error(f"Phenotype-HPO job {job_info.uid} failed: {error_msg}")
        raise HTTPException(status_code=502, detail=error_msg)

    completed_statuses = ("completed", "completion", "success", "succeeded", "finished", "done")
    if final_info.status not in completed_statuses:
        logger.warning(f"Phenotype-HPO job {job_info.uid}: unexpected status {final_info.status}, treating as error")
        raise HTTPException(status_code=502, detail=f"Job ended with unexpected status: {final_info.status}")

    # 5. Download results
    save_dir = os.path.join(DATA_DIR, job_info.uid)
    try:
        downloaded = await service.download_key_results(job_info.uid, save_dir)
    except Exception as e:
        logger.error(f"Failed to download phenotype-HPO results for {job_info.uid}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Phenotype-HPO result download failed: {e}",
        )

    gene_score_path = downloaded.get("gene_phenotype_score_csv")
    variant_score_path = downloaded.get("variant_phenotype_score_csv")
    phenotype_path = downloaded.get("phenotype_csv")

    # 6. Save paths to VEPJob
    vep_job.gene_phenotype_score_path = gene_score_path
    vep_job.variant_phenotype_score_path = variant_score_path
    vep_job.phenotype_path = phenotype_path
    db.commit()

    logger.info(
        f"Phenotype-HPO scoring complete for vcf_file_id={request.vcf_file_id}: "
        f"gene_score={gene_score_path is not None}, "
        f"variant_score={variant_score_path is not None}"
    )

    # 7. Parse and return results
    if gene_score_path and Path(gene_score_path).exists():
        try:
            scores = _parse_gene_phenotype_score_csv(gene_score_path)
            return GeneScoresResponse(scores=scores, total=len(scores))
        except Exception as e:
            logger.error(f"Failed to parse gene phenotype scores: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        logger.warning(
            f"gene_phenotype_score.csv not found in phenotype-HPO output for {job_info.uid}"
        )
        return GeneScoresResponse(scores=[], total=0)


@router.get("/results/{vcf_file_id}", response_model=GeneScoresResponse)
async def get_gene_scores(
    vcf_file_id: int,
    db: Session = Depends(get_db),
):
    """Get cached gene phenotype scores for a VCF file."""
    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == vcf_file_id,
        VEPJob.gene_phenotype_score_path.isnot(None),
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.gene_phenotype_score_path:
        raise HTTPException(
            status_code=404,
            detail="No gene phenotype scores available. "
                   "Submit via POST /phenotype-hpo/submit first.",
        )

    score_path = Path(vep_job.gene_phenotype_score_path)
    if not score_path.exists():
        raise HTTPException(status_code=404, detail="Gene phenotype score file not found")

    try:
        scores = _parse_gene_phenotype_score_csv(str(score_path))
        return GeneScoresResponse(scores=scores, total=len(scores))
    except Exception as e:
        logger.error(f"Failed to parse gene phenotype scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))
