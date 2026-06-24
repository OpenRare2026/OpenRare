"""
Phenotype-HPO Scoring Service Client.
Submits VEP CSV and HPO terms to external scoring API, polls for completion.
"""
import asyncio
import logging
import tempfile
import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from config import (
    PHENOTYPE_HPO_API_BASE_URL,
    PHENOTYPE_HPO_POLL_INTERVAL,
    PHENOTYPE_HPO_MAX_DURATION,
)
from database import Variant

logger = logging.getLogger(__name__)


@dataclass
class PhenotypeHpoJobInfo:
    uid: str
    status: str
    phase: str = ""
    message: str = ""
    status_url: str = ""
    files_url: str = ""


@dataclass
class GenePhenotypeScore:
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


class PhenotypeHpoServiceError(Exception):
    pass


class PhenotypeHpoService:
    def __init__(
        self,
        base_url: str = PHENOTYPE_HPO_API_BASE_URL,
        poll_interval: int = PHENOTYPE_HPO_POLL_INTERVAL,
        max_duration: int = PHENOTYPE_HPO_MAX_DURATION,
    ):
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.max_duration = max_duration

    async def submit_job(
        self,
        vep_csv_content: str,
        hpo_terms: List[str],
        hgvs: bool = True,
    ) -> PhenotypeHpoJobInfo:
        url = f"{self.base_url}/runs"
        
        vep_file = ("vep.csv", vep_csv_content, "text/csv")
        hpo_content = ",".join(hpo_terms)
        
        files = {"file": vep_file}
        data = {"hpo_list": hpo_content, "hgvs": str(hgvs).lower()}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, files=files, data=data)
            resp.raise_for_status()
            result = resp.json()
            
        return PhenotypeHpoJobInfo(
            uid=result.get("uid", ""),
            status=result.get("status", "queuing"),
            phase=result.get("phase", ""),
            message=result.get("message", ""),
            status_url=result.get("status_url", ""),
            files_url=result.get("files_url", ""),
        )

    async def get_job_status(self, uid: str) -> Dict[str, Any]:
        url = f"{self.base_url}/runs/{uid}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def poll_until_completion(self, uid: str) -> Dict[str, Any]:
        elapsed = 0
        while elapsed < self.max_duration:
            status_data = await self.get_job_status(uid)
            status = status_data.get("status", "")
            
            if status == "completion":
                return status_data
            elif status == "failure":
                raise PhenotypeHpoServiceError(
                    f"Job {uid} failed: {status_data.get('message', 'Unknown error')}"
                )
            
            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval
            
        raise PhenotypeHpoServiceError(f"Job {uid} timed out after {self.max_duration}s")

    async def get_gene_scores(self, uid: str) -> List[GenePhenotypeScore]:
        url = f"{self.base_url}/runs/{uid}/files/gene_phenotype_score.csv"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
        return self._parse_gene_scores_csv(resp.text)

    async def get_gene_scores_csv(self, uid: str) -> str:
        url = f"{self.base_url}/runs/{uid}/files/gene_phenotype_score.csv"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
        return resp.text

    def _parse_gene_scores_csv(self, csv_content: str) -> List[GenePhenotypeScore]:
        scores = []
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row in reader:
            try:
                score = GenePhenotypeScore(
                    gene_symbol=row.get("gene_symbol", ""),
                    hgnc_id=row.get("hgnc_id", ""),
                    gene_score=self._parse_float(row.get("gene_score")),
                    conclusion_code=row.get("conclusion_code", ""),
                    best_disease_score=self._parse_float(row.get("best_disease_score")),
                    best_disease_name=row.get("best_disease_name", ""),
                    best_omim_id=row.get("best_omim_id", ""),
                    best_orpha_id=row.get("best_orpha_id", ""),
                    best_mondo_id=row.get("best_mondo_id", ""),
                    best_disease_source_dbs=row.get("best_disease_source_dbs", ""),
                    best_disease_match_status=row.get("best_disease_match_status", ""),
                    mapping_basis=row.get("mapping_basis", ""),
                    second_best_disease_score=self._parse_float(row.get("second_best_disease_score")),
                    score_gap_to_second_best=self._parse_float(row.get("score_gap_to_second_best")),
                    disease_profile_count=self._parse_int(row.get("disease_profile_count")),
                    input_hpo_count=self._parse_int(row.get("input_hpo_count")),
                    scoring_hpo_count=self._parse_int(row.get("scoring_hpo_count")),
                    matched_hpo_count=self._parse_int(row.get("matched_hpo_count")),
                    unmatched_hpo_count=self._parse_int(row.get("unmatched_hpo_count")),
                    mean_input_hpo_ic=self._parse_float(row.get("mean_input_hpo_ic")),
                    candidate_variant_count_in_gene=self._parse_int(row.get("candidate_variant_count_in_gene")),
                    gene_sources=row.get("gene_sources", ""),
                    best_term_evidence_summary=row.get("best_term_evidence_summary", ""),
                    db_versions=row.get("db_versions", ""),
                    warning=row.get("warning", ""),
                    sample_id=row.get("sample_id", ""),
                    gene_rank=self._parse_int(row.get("gene_rank")),
                )
                scores.append(score)
            except Exception as e:
                logger.warning(f"Failed to parse gene score row: {e}")
                continue
                
        return scores

    def _parse_float(self, value: Optional[str]) -> float:
        if value is None or value == "":
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _parse_int(self, value: Optional[str]) -> int:
        if value is None or value == "":
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def build_vep_csv_from_variants(self, variants: List[Variant]) -> str:
        output = io.StringIO()
        fieldnames = [
            "chrom", "pos", "ref", "alt", "gene_symbol", "all_genes", "transcript_id",
            "consequence", "impact", "hgvsc", "hgvsp", "cdna_position", "cds_position",
            "protein_position", "amino_acids", "codons", "exon", "intron", "strand",
            "protein_domains", "revel_score", "cadd_phred", "gnomAD_popmax_AF",
            "gnomAD_eas_AF", "gnomAD_nhomalt", "spliceAI_ds_max", "spliceAI_type",
            "loftee_lof_flag", "loftee_lof_filter", "clinvar_significance",
            "clinvar_review_status", "clinvar_star_rating", "pathogenic_rank",
            "evidence_summary"
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for v in variants:
            chrom = v.chromosome
            if chrom.lower().startswith("chr"):
                chrom = chrom[3:]
            
            gene = v.gene or ""
            all_genes = v.all_genes or gene
            
            row = {
                "chrom": chrom,
                "pos": str(v.position),
                "ref": v.ref,
                "alt": v.alt,
                "gene_symbol": gene,
                "all_genes": all_genes,
                "transcript_id": v.transcript or "",
                "consequence": v.consequence or "",
                "impact": v.impact or "",
                "hgvsc": v.hgvs_c or "",
                "hgvsp": v.hgvs_p or "",
                "cdna_position": v.cdna_position or "",
                "cds_position": v.cds_position or "",
                "protein_position": v.protein_position or "",
                "amino_acids": v.amino_acids or "",
                "codons": v.codons or "",
                "exon": v.exon or "",
                "intron": v.intron or "",
                "strand": v.strand or "",
                "protein_domains": v.protein_domains or "",
                "revel_score": str(v.revel_score) if v.revel_score else "",
                "cadd_phred": str(v.cadd) if v.cadd else "",
                "gnomAD_popmax_AF": str(v.gnomad_popmax_af) if v.gnomad_popmax_af else "",
                "gnomAD_eas_AF": str(v.gnomad_eas_af) if v.gnomad_eas_af else "",
                "gnomAD_nhomalt": str(v.gnomad_nhomalt) if v.gnomad_nhomalt else "",
                "spliceAI_ds_max": str(v.spliceai_ds_max) if v.spliceai_ds_max else "",
                "spliceAI_type": v.spliceai_type or "",
                "loftee_lof_flag": v.loftee_lof_flag or "",
                "loftee_lof_filter": v.loftee_lof_filter or "",
                "clinvar_significance": v.clinvar_significance or "",
                "clinvar_review_status": v.clinvar_review_status or "",
                "clinvar_star_rating": str(v.clinvar_star_rating) if v.clinvar_star_rating else "",
                "pathogenic_rank": str(v.pathogenic_rank) if v.pathogenic_rank else "",
                "evidence_summary": v.evidence_summary or "",
            }
            writer.writerow(row)
        
        return output.getvalue()
