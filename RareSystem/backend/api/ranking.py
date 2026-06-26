"""
Ranking API endpoints.

POST /submit — submits VEP CSV + gene score CSV + PPI score CSV to the ranking
               service at RANK_API_BASE_URL, polls until completion, downloads
               ranked_output.csv, saves path to VEPJob record, and returns
               parsed ranked gene results.

GET /results/{vcf_file_id} — returns cached ranking results from the saved CSV.

The ranking service requires three inputs:
  1. file             — VEP annotated variant CSV
  2. gene_score_file  — gene_phenotype_score.csv (output of phenotype-HPO service)
  3. ppi_score_file   — PPI score CSV (output of PPI scoring service)

Therefore, both phenotype-HPO scoring and PPI scoring must complete before
ranking can be submitted.
"""
import csv
import logging
import os
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, VEPJob
from services.ranking_service import RankingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ranking", tags=["ranking"])

DATA_DIR = os.environ.get(
    "VEP_DATA_DIR",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "ranking_results"
    ),
)


class RankingSubmitRequest(BaseModel):
    vcf_file_id: int


class RankedGeneResponse(BaseModel):
    gene: str
    combined_score: float = 0.0
    rank: int = 0
    gene_score: float = 0.0
    ppi_final: float = 0.0
    disease_score: float = 0.0
    tissue_score: float = 0.0
    topology_score: float = 0.0
    conclusion_code: str = ""
    best_disease_name: str = ""
    best_disease_score: float = 0.0
    in_network: bool = False
    score_mode: str = ""
    mapped_tissues: str = ""


class RankedGenesResponse(BaseModel):
    scores: List[RankedGeneResponse]
    total: int


def _parse_ranked_csv(path: str) -> List[RankedGeneResponse]:
    """Parse ranked_output.csv, aggregating variant-level rows to gene-level.

    The ranking service output is variant-level (same format as VEP CSV) with
    added columns: gene_score, ppi_final, evolve_score, evolve_rank,
    pathogenic_score, pathogenic_rank_1. We aggregate per gene taking the
    best (lowest) rank and highest scores.
    """
    from collections import defaultdict

    GeneAgg = lambda: {
        "pathogenic_rank": 999999,
        "evolve_rank": 999999,
        "max_pathogenic_score": 0.0,
        "max_evolve_score": 0.0,
        "max_gene_score": 0.0,
        "max_ppi_final": 0.0,
        "variant_count": 0,
    }
    gene_data: dict = defaultdict(GeneAgg)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gene = row.get(
                "gene_symbol",
                row.get("gene", row.get("Gene", "")),
            )
            if not gene or gene == "-":
                continue
            if "," in gene:
                gene = gene.split(",")[0].strip()

            d = gene_data[gene]
            d["variant_count"] += 1

            try:
                ps = float(row.get("pathogenic_score", 0) or 0)
                d["max_pathogenic_score"] = max(d["max_pathogenic_score"], ps)
            except ValueError:
                pass

            try:
                pr = int(float(row.get("pathogenic_rank_1", row.get("pathogenic_rank", 0)) or 0))
                if pr > 0:
                    d["pathogenic_rank"] = min(d["pathogenic_rank"], pr)
            except ValueError:
                pass

            try:
                es = float(row.get("evolve_score", 0) or 0)
                d["max_evolve_score"] = max(d["max_evolve_score"], es)
            except ValueError:
                pass

            try:
                er = int(float(row.get("evolve_rank", 0) or 0))
                if er > 0:
                    d["evolve_rank"] = min(d["evolve_rank"], er)
            except ValueError:
                pass

            try:
                d["max_gene_score"] = max(d["max_gene_score"], float(row.get("gene_score", 0) or 0))
            except ValueError:
                pass

            try:
                d["max_ppi_final"] = max(d["max_ppi_final"], float(row.get("ppi_final", 0) or 0))
            except ValueError:
                pass

    results: List[RankedGeneResponse] = []
    for gene, d in sorted(
        gene_data.items(),
        key=lambda x: x[1]["pathogenic_rank"],
    ):
        pr = d["pathogenic_rank"] if d["pathogenic_rank"] < 999999 else 0
        er = d["evolve_rank"] if d["evolve_rank"] < 999999 else 0
        results.append(RankedGeneResponse(
            gene=gene,
            combined_score=d["max_pathogenic_score"],
            rank=pr if pr > 0 else len(results) + 1,
            gene_score=d["max_gene_score"],
            ppi_final=d["max_ppi_final"],
            disease_score=d["max_gene_score"],
            tissue_score=d["max_ppi_final"],
            topology_score=0.0,
            conclusion_code="",
            best_disease_name="",
            best_disease_score=d["max_gene_score"],
            in_network=d["max_ppi_final"] > 0.5,
            score_mode="",
            mapped_tissues="",
        ))

    return results


@router.post("/submit", response_model=RankedGenesResponse)
async def submit_ranking_job(
    request: RankingSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit VEP CSV + gene score CSV + PPI score CSV to ranking service,
    poll until complete, download results, save to VEPJob, return parsed scores.

    Prerequisites:
      - VEP annotation must be complete (csv_path exists)
      - Gene phenotype scoring must be complete (gene_phenotype_score_path exists)
      - PPI scoring must be complete (ppi_score_path exists)
    """
    # 1. Find the VEPJob with saved CSV, gene score, and PPI score
    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == request.vcf_file_id,
        VEPJob.csv_path.isnot(None),
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.csv_path:
        raise HTTPException(
            status_code=400,
            detail="No VEP results available for this VCF file. "
                   "VEP annotation must complete before ranking.",
        )

    vep_csv_path = Path(vep_job.csv_path)
    if not vep_csv_path.exists():
        raise HTTPException(status_code=400, detail="VEP CSV file not found on disk.")

    # 2. Check if ranking already exists (cached)
    if vep_job.ranked_csv_path:
        existing_path = Path(vep_job.ranked_csv_path)
        if existing_path.exists():
            logger.info(
                f"Ranking results already available for vcf_file_id={request.vcf_file_id}, "
                f"returning cached results from {existing_path}"
            )
            try:
                scores = _parse_ranked_csv(str(existing_path))
                return RankedGenesResponse(scores=scores, total=len(scores))
            except Exception as e:
                logger.warning(f"Failed to parse cached ranking results: {e}")

    # 3. Require gene_phenotype_score.csv (from phenotype-HPO service)
    if not vep_job.gene_phenotype_score_path:
        raise HTTPException(
            status_code=400,
            detail="No gene phenotype scores available. "
                   "Run POST /phenotype-hpo/submit first before ranking.",
        )

    gene_score_path = Path(vep_job.gene_phenotype_score_path)
    if not gene_score_path.exists():
        raise HTTPException(
            status_code=400,
            detail="Gene phenotype score file not found on disk. "
                   "Re-run POST /phenotype-hpo/submit.",
        )

    # 4. Require PPI score CSV (from PPI scoring service)
    if not vep_job.ppi_score_path:
        raise HTTPException(
            status_code=400,
            detail="No PPI scores available. "
                   "Run POST /ppi-score/submit first before ranking.",
        )

    ppi_score_path = Path(vep_job.ppi_score_path)
    if not ppi_score_path.exists():
        raise HTTPException(
            status_code=400,
            detail="PPI score file not found on disk. "
                   "Re-run POST /ppi-score/submit.",
        )

    # 5. Submit to ranking service
    service = RankingService()
    try:
        job_info = await service.submit(
            vep_csv_path=str(vep_csv_path),
            gene_score_csv_path=str(gene_score_path),
            ppi_score_csv_path=str(ppi_score_path),
        )
    except Exception as e:
        logger.error(f"Failed to submit to ranking service: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Ranking service submission failed: {e}",
        )

    if not job_info.job_id:
        raise HTTPException(
            status_code=502,
            detail="Ranking service returned empty job_id.",
        )

    # 6. Poll until completion
    try:
        final_info = await service.poll_until_complete(job_info.job_id)
    except Exception as e:
        logger.error(f"Failed to poll ranking job {job_info.job_id}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Ranking service polling failed: {e}",
        )

    if final_info.status in ("failed", "error", "timeout"):
        error_msg = final_info.error or f"Job ended with status: {final_info.status}"
        logger.error(f"Ranking job {job_info.job_id} failed: {error_msg}")
        raise HTTPException(status_code=502, detail=error_msg)

    completed_statuses = ("completed", "completion", "success", "succeeded", "finished", "done")
    if final_info.status not in completed_statuses:
        logger.warning(f"Ranking job {job_info.job_id}: unexpected status {final_info.status}, treating as error")
        raise HTTPException(status_code=502, detail=f"Job ended with unexpected status: {final_info.status}")

    # 7. Download results
    save_dir = os.path.join(DATA_DIR, job_info.job_id)
    try:
        downloaded = await service.download_and_save(job_info.job_id, save_dir)
    except Exception as e:
        logger.error(f"Failed to download ranking results for {job_info.job_id}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Ranking result download failed: {e}",
        )

    ranked_csv = downloaded.get("ranked_csv")

    # 8. Update VEPJob — save ranked CSV path
    if ranked_csv:
        vep_job.ranked_csv_path = ranked_csv
    db.commit()

    logger.info(
        f"Ranking complete for vcf_file_id={request.vcf_file_id}: "
        f"ranked_csv={ranked_csv is not None}"
    )

    # 9. Parse and return results
    if ranked_csv and Path(ranked_csv).exists():
        try:
            scores = _parse_ranked_csv(ranked_csv)
            return RankedGenesResponse(scores=scores, total=len(scores))
        except Exception as e:
            logger.error(f"Failed to parse ranked CSV: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        logger.warning(
            f"Ranked CSV not found in ranking service output for {job_info.job_id}"
        )
        return RankedGenesResponse(scores=[], total=0)


@router.get("/results/{vcf_file_id}", response_model=RankedGenesResponse)
async def get_ranking_results(
    vcf_file_id: int,
    db: Session = Depends(get_db),
):
    """Get cached ranking results for a VCF file."""
    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == vcf_file_id,
        VEPJob.ranked_csv_path.isnot(None),
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.ranked_csv_path:
        raise HTTPException(
            status_code=404,
            detail="No ranking results available. "
                   "Submit via POST /ranking/submit first.",
        )

    ranked_path = Path(vep_job.ranked_csv_path)
    if not ranked_path.exists():
        raise HTTPException(status_code=404, detail="Ranked CSV file not found")

    try:
        scores = _parse_ranked_csv(str(ranked_path))
        return RankedGenesResponse(scores=scores, total=len(scores))
    except Exception as e:
        logger.error(f"Failed to parse ranked CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))
