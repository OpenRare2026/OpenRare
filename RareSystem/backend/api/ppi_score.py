"""
PPI Score API endpoints.

POST /submit — submits phenotype_gene_csv + VEP output CSV to the PPI scoring
               service at PPI_SCORE_API_BASE_URL (clean-case upload async),
               polls until completion, downloads scored CSVs, saves paths to
               VEPJob record, and returns parsed gene-level scores.

GET /results/{vcf_file_id} — returns cached PPI scores from the saved CSV.

The PPI scoring service requires two inputs:
  1. phenotype_gene_csv  — gene_phenotype_score.csv (output of phenotype-HPO service)
  2. vep_output_csv      — VEP annotated variant CSV

Therefore, phenotype-HPO scoring must complete before PPI scoring can be submitted.
"""
import csv
import logging
import os
from collections import defaultdict
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, VEPJob
from services.ppi_score_service import PpiScoreService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ppi-score", tags=["ppi-score"])

DATA_DIR = os.environ.get(
    "VEP_DATA_DIR",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "ppi_score_results"
    ),
)


class SubmitRequest(BaseModel):
    vcf_file_id: int
    hpo_terms: List[str] = Field(default_factory=list)
    force_refresh: bool = False


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


def _parse_variant_phenotype_score_csv(path: str) -> List[GeneScoreResponse]:
    """
    Parse variant_phenotype_score.csv, final_score.csv, or PPI scored CSV
    from service output. Groups by gene and returns per-gene aggregated scores.

    Handles two input formats:
    - gene_phenotype_score style: gene_symbol, gene_score, gene_rank, conclusion_code
    - final_score/PPI style: gene_symbol/gene, gene_score, ppi_final, clinical_best_tissue
    """
    gene_data = defaultdict(lambda: {
        "variants": [],
        "max_gene_score": 0.0,
        "max_ppi_final": 0.0,
        "gene_rank": 0,
        "conclusion_code": "",
        "tissue": "",
        "gene_sources": "",
    })

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gene = row.get(
                "gene_symbol_normalized",
                row.get("gene_symbol", row.get("gene", row.get("all_genes", ""))),
            )
            if not gene or gene == "-":
                continue
            # For all_genes like "ENSG00000286448,ENSG00000292994", take the first
            if "," in gene:
                gene = gene.split(",")[0].strip()

            try:
                gene_score = float(
                    row.get("gene_score", row.get("disease_score", row.get("final_score", 0))) or 0
                )
            except ValueError:
                gene_score = 0.0

            # PPI final score (from final_score.csv)
            try:
                ppi_final = float(row.get("ppi_final", 0) or 0)
            except ValueError:
                ppi_final = 0.0

            try:
                gene_rank = int(row.get("gene_rank", row.get("rank", 0)) or 0)
            except ValueError:
                gene_rank = 0

            tissue = row.get("clinical_best_tissue", row.get("tissue", ""))

            # Track best (highest combined) score per gene
            combined = gene_score + ppi_final
            prev_combined = gene_data[gene]["max_gene_score"] + gene_data[gene]["max_ppi_final"]
            if combined > prev_combined:
                gene_data[gene]["max_gene_score"] = gene_score
                gene_data[gene]["max_ppi_final"] = ppi_final
                gene_data[gene]["gene_rank"] = gene_rank
                gene_data[gene]["conclusion_code"] = row.get("conclusion_code", "")
                gene_data[gene]["tissue"] = tissue
                gene_data[gene]["gene_sources"] = row.get("gene_sources", "")

            gene_data[gene]["variants"].append(row)

    results = []
    for gene, data in sorted(
        gene_data.items(),
        key=lambda x: (
            -(x[1]["max_gene_score"] + x[1]["max_ppi_final"])
        ),
    ):
        # Derive rank from sort order if not explicitly set
        results.append(GeneScoreResponse(
            gene=gene,
            disease_score=data["max_gene_score"],
            tissue_score=data["max_ppi_final"] if data["max_ppi_final"] > 0 else 0.0,
            topology_score=0.0,
            final_score=data["max_ppi_final"],
            rank=data["gene_rank"] if data["gene_rank"] > 0 else len(results) + 1,
            disease_evidence=data["conclusion_code"],
            tissue_evidence=data["tissue"],
            hpo_match_count=len(data["variants"]),
        ))

    return results


@router.post("/submit", response_model=GeneScoresResponse)
async def submit_ppi_job(
    request: SubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit phenotype gene scores + VEP output to PPI scoring service,
    poll until complete, download results, save to VEPJob, return parsed scores.

    Prerequisite: gene_phenotype_score.csv must exist (phenotype-HPO scoring
    must have been run first via POST /phenotype-hpo/submit).
    """
    # 1. Find the VEPJob with saved CSV and gene phenotype score
    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == request.vcf_file_id,
        VEPJob.csv_path.isnot(None),
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.csv_path:
        raise HTTPException(
            status_code=400,
            detail="No VEP results available for this VCF file. "
                   "VEP annotation must complete before PPI scoring.",
        )

    vep_csv_path = Path(vep_job.csv_path)
    if not vep_csv_path.exists():
        raise HTTPException(status_code=400, detail="VEP CSV file not found on disk.")

    # 2. Check if PPI score already exists (cached) — skip if force_refresh
    if not request.force_refresh and vep_job.ppi_score_path:
        existing_path = Path(vep_job.ppi_score_path)
        if existing_path.exists():
            logger.info(
                f"PPI score already available for vcf_file_id={request.vcf_file_id}, "
                f"returning cached results from {existing_path}"
            )
            try:
                scores = _parse_variant_phenotype_score_csv(str(existing_path))
                return GeneScoresResponse(scores=scores, total=len(scores))
            except Exception as e:
                logger.warning(f"Failed to parse cached PPI scores: {e}")

    # 3. Require gene_phenotype_score.csv (from phenotype-HPO service)
    if not vep_job.gene_phenotype_score_path:
        raise HTTPException(
            status_code=400,
            detail="No gene phenotype scores available. "
                   "Run POST /phenotype-hpo/submit first before PPI scoring.",
        )

    gene_score_path = Path(vep_job.gene_phenotype_score_path)
    if not gene_score_path.exists():
        raise HTTPException(
            status_code=400,
            detail="Gene phenotype score file not found on disk. "
                   "Re-run POST /phenotype-hpo/submit.",
        )

    # 4. Submit to PPI scoring service
    service = PpiScoreService()
    try:
        job_info = await service.submit_clean_case_async(
            phenotype_gene_csv_path=str(gene_score_path),
            vep_output_csv_path=str(vep_csv_path),
            hpo_ids=request.hpo_terms if request.hpo_terms else None,
        )
    except Exception as e:
        logger.error(f"Failed to submit to PPI score service: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"PPI score service submission failed: {e}",
        )

    if not job_info.job_id:
        raise HTTPException(
            status_code=502,
            detail="PPI score service returned empty job_id.",
        )

    # 5. Poll until completion
    try:
        final_info = await service.poll_until_complete(job_info.job_id)
    except Exception as e:
        logger.error(f"Failed to poll PPI score job {job_info.job_id}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"PPI score service polling failed: {e}",
        )

    if final_info.status in ("failed", "error", "timeout"):
        error_msg = final_info.error or f"Job ended with status: {final_info.status}"
        logger.error(f"PPI score job {job_info.job_id} failed: {error_msg}")
        raise HTTPException(status_code=502, detail=error_msg)

    completed_statuses = ("completed", "completion", "success", "succeeded", "finished", "done")
    if final_info.status not in completed_statuses:
        logger.warning(f"PPI score job {job_info.job_id}: unexpected status {final_info.status}, treating as error")
        raise HTTPException(status_code=502, detail=f"Job ended with unexpected status: {final_info.status}")

    # 6. Download results
    save_dir = os.path.join(DATA_DIR, job_info.job_id)
    try:
        downloaded = await service.download_key_results(job_info.job_id, save_dir)
    except Exception as e:
        logger.error(f"Failed to download PPI score results for {job_info.job_id}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"PPI score result download failed: {e}",
        )

    score_csv = downloaded.get("score_csv")
    ppi_csv = downloaded.get("ppi_csv")

    # 7. Update VEPJob — save PPI score CSV to dedicated field
    if score_csv:
        vep_job.ppi_score_path = score_csv
    db.commit()

    logger.info(
        f"PPI scoring complete for vcf_file_id={request.vcf_file_id}: "
        f"score_csv={score_csv is not None}, ppi_csv={ppi_csv is not None}"
    )

    # 8. Parse and return results
    if score_csv and Path(score_csv).exists():
        try:
            scores = _parse_variant_phenotype_score_csv(score_csv)
            return GeneScoresResponse(scores=scores, total=len(scores))
        except Exception as e:
            logger.error(f"Failed to parse PPI score CSV: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        logger.warning(
            f"PPI score CSV not found in PPI service output for {job_info.job_id}"
        )
        return GeneScoresResponse(scores=[], total=0)


@router.get("/results/{vcf_file_id}", response_model=GeneScoresResponse)
async def get_gene_scores(
    vcf_file_id: int,
    db: Session = Depends(get_db),
):
    """Get cached PPI gene scores for a VCF file."""
    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == vcf_file_id,
        VEPJob.ppi_score_path.isnot(None),
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.ppi_score_path:
        raise HTTPException(
            status_code=404,
            detail="No PPI scores available. "
                   "Submit via POST /ppi-score/submit first.",
        )

    score_path = Path(vep_job.ppi_score_path)
    if not score_path.exists():
        raise HTTPException(status_code=404, detail="PPI score file not found")

    try:
        scores = _parse_variant_phenotype_score_csv(str(score_path))
        return GeneScoresResponse(scores=scores, total=len(scores))
    except Exception as e:
        logger.error(f"Failed to parse variant phenotype scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))
