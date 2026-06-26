"""
PPI Score Service Client.
Submits HPO gene scores and VEP output to PPI scoring API for network-based gene prioritization.
"""
import asyncio
import logging
import csv
import io
import os
import tempfile
from dataclasses import dataclass
from typing import List, Optional
import httpx

from config import (
    PPI_SCORE_API_BASE_URL,
    PPI_SCORE_POLL_INTERVAL,
    PPI_SCORE_MAX_DURATION,
)

logger = logging.getLogger(__name__)

PPI_SHARED_DIR = "/tmp"


@dataclass
class PpiJobInfo:
    job_id: str
    status: str
    message: str = ""


@dataclass
class PpiGeneScore:
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


class PpiScoreServiceError(Exception):
    pass


class PpiScoreService:
    def __init__(
        self,
        base_url: str = PPI_SCORE_API_BASE_URL,
        poll_interval: int = PPI_SCORE_POLL_INTERVAL,
        max_duration: int = PPI_SCORE_MAX_DURATION,
    ):
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.max_duration = max_duration
        os.makedirs(PPI_SHARED_DIR, exist_ok=True)
        self.temp_dir = tempfile.mkdtemp(prefix="ppi_score_", dir=PPI_SHARED_DIR)

    def _write_temp_file(self, content: str, suffix: str = ".csv") -> str:
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.temp_dir)
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.chmod(path, 0o644)
        return path

    def cleanup(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp dir {self.temp_dir}: {e}")

    async def submit_job(
        self,
        phenotype_gene_csv_content: str,
        vep_csv_content: str,
        hpo_ids: List[str],
    ) -> PpiJobInfo:
        url = f"{self.base_url}/score/clean-case/async"
        
        hpo_file_path = self._write_temp_file("\n".join(hpo_ids), suffix=".txt")
        phenotype_csv_path = self._write_temp_file(phenotype_gene_csv_content, suffix="_gene.csv")
        vep_csv_path = self._write_temp_file(vep_csv_content, suffix="_vep.csv")
        
        payload = {
            "phenotype_gene_csv": phenotype_csv_path,
            "vep_output_csv": vep_csv_path,
            "hpo_file": hpo_file_path,
            "hpo_ids": hpo_ids,
            "clean_output_dir": True,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            result = resp.json()
            
        return PpiJobInfo(
            job_id=result.get("job_id", ""),
            status=result.get("status", "queued"),
            message=result.get("message", ""),
        )

    async def get_job_status(self, job_id: str) -> dict:
        url = f"{self.base_url}/score/{job_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def check_csv_ready(self, job_id: str) -> bool:
        url = f"{self.base_url}/score/{job_id}/csv"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return True
            return False

    async def poll_until_completion(self, job_id: str) -> dict:
        elapsed = 0
        while elapsed < self.max_duration:
            status_data = await self.get_job_status(job_id)
            status = status_data.get("status", "")
            
            if status in ("completed", "done", "success"):
                return status_data
            elif status == "failed":
                raise PpiScoreServiceError(
                    f"Job {job_id} failed: {status_data.get('message', 'Unknown error')}"
                )
            
            csv_ready = await self.check_csv_ready(job_id)
            if csv_ready:
                return {"status": "completed", "job_id": job_id}
            
            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval
            
        raise PpiScoreServiceError(f"Job {job_id} timed out after {self.max_duration}s")

    async def get_gene_scores(self, job_id: str) -> List[PpiGeneScore]:
        url = f"{self.base_url}/score/{job_id}/csv"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
        return self._parse_gene_scores_csv(resp.text)

    async def get_gene_scores_csv(self, job_id: str) -> str:
        url = f"{self.base_url}/score/{job_id}/csv"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
        return resp.text

    def _parse_gene_scores_csv(self, csv_content: str) -> List[PpiGeneScore]:
        scores = []
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row in reader:
            try:
                score = PpiGeneScore(
                    gene=row.get("gene", row.get("gene_symbol", "")),
                    disease_score=self._parse_float(row.get("disease_score")),
                    tissue_score=self._parse_float(row.get("tissue_score")),
                    topology_score=self._parse_float(row.get("topology_score")),
                    final_score=self._parse_float(row.get("final_score", row.get("combined_score"))),
                    rank=self._parse_int(row.get("rank")),
                    disease_evidence=row.get("disease_evidence", ""),
                    tissue_evidence=row.get("tissue_evidence", ""),
                    topology_evidence=row.get("topology_evidence", ""),
                    neighbor_genes=row.get("neighbor_genes", ""),
                    hpo_match_count=self._parse_int(row.get("hpo_match_count")),
                )
                scores.append(score)
            except Exception as e:
                logger.warning(f"Failed to parse PPI gene score row: {e}")
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

    def build_vep_csv_from_variants(self, variants: List) -> str:
        from database import Variant
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
