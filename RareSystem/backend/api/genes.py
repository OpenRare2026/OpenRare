"""
Gene API endpoints - Gene-centric variant view.

Reads gene data from VEP Parquet results.
Column names match the OpenRare V3 pipeline output:
  chrom, pos, ref, alt, gene_symbol, all_genes, consequence, impact,
  hgvsc, hgvsp, gnomAD_eas_AF, clinvar_significance, ...
"""
import logging
from typing import List, Optional, Dict
from collections import defaultdict
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, VEPJob
from services.parquet_service import ParquetService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/genes", tags=["genes"])


class GeneSummary(BaseModel):
    gene: str
    variant_count: int
    variant_types: Dict[str, int] = Field(default_factory=dict)
    classifications: Dict[str, int] = Field(default_factory=dict)
    max_gnomad_af: Optional[float] = None
    chromosomes: List[str] = Field(default_factory=list)


class GeneListResponse(BaseModel):
    genes: List[GeneSummary]
    total: int


class GeneVariant(BaseModel):
    id: str
    chromosome: str
    position: int
    ref: str
    alt: str
    variant_type: str
    quality: Optional[float] = None
    gnomad_af: Optional[float] = None
    clinvar_significance: Optional[str] = None
    acmg_classification: Optional[str] = None

    class Config:
        from_attributes = True


class GeneVariantsResponse(BaseModel):
    gene: str
    variants: List[GeneVariant]
    total: int


class GeneInfo(BaseModel):
    symbol: str
    name: str = ""
    description: str = ""
    chromosome: str = ""
    location: str = ""
    omim_id: Optional[str] = None
    hgnc_id: Optional[str] = None
    ensembl_id: Optional[str] = None
    diseases: List[str] = Field(default_factory=list)
    inheritance: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)


GENE_SYMBOL_COLS = ("gene_symbol", "SYMBOL", "Gene_symbol", "Gene")
ALL_GENES_COLS = ("all_genes",)
CHROM_COL_NAMES = ("chrom", "Chromosome", "chr", "#CHROM")
POS_COL_NAMES = ("pos", "Position", "POS")
REF_COL_NAMES = ("ref", "Reference", "REF")
ALT_COL_NAMES = ("alt", "Alternate", "Allele", "ALT")
AF_COL_PATTERNS = ("gnomAD_eas_AF", "gnomAD_popmax_AF", "gnomAD_AF", "AF")
CLINVAR_COL_NAMES = ("clinvar_significance", "ClinVar", "CLINVAR_clnsig", "CLNSIG")


def _find_vep_parquet(vcf_file_id: int, db: Session):
    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == vcf_file_id,
        VEPJob.parquet_path.isnot(None)
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.parquet_path:
        return None, None

    parquet_path = Path(vep_job.parquet_path)
    if not parquet_path.exists():
        return None, None

    return vep_job, parquet_path


def _pick_col(columns: List[str], candidates: tuple) -> Optional[str]:
    for c in candidates:
        if c in columns:
            return c
    return None


def _pick_af_col(columns: List[str]) -> Optional[str]:
    for pattern in AF_COL_PATTERNS:
        if pattern in columns:
            return pattern
    for c in columns:
        low = c.lower()
        if "gnomad" in low and "af" in low:
            return c
        if "af" in low and "popmax" in low:
            return c
    return None


def _derive_variant_type(ref: str, alt: str) -> str:
    if not ref or not alt:
        return "SNV"
    if len(ref) == 1 and len(alt) == 1:
        return "SNV"
    elif len(ref) != len(alt):
        return "INDEL"
    else:
        return "MNV"


@router.get("/info/{gene_name}", response_model=Optional[GeneInfo])
async def get_gene_info(gene_name: str):
    from services.gene_info_service import get_gene_info_service

    service = get_gene_info_service()
    info = service.get_gene_info(gene_name)

    if info:
        return GeneInfo(
            symbol=info.symbol,
            name=info.name,
            description=info.description,
            chromosome=info.chromosome,
            location=info.location,
            omim_id=info.omim_id,
            hgnc_id=info.hgnc_id,
            ensembl_id=info.ensembl_id,
            diseases=info.diseases,
            inheritance=info.inheritance,
            aliases=info.aliases
        )

    return None


@router.get("/{vcf_file_id}", response_model=GeneListResponse)
async def get_genes(
    vcf_file_id: str,
    db: Session = Depends(get_db)
):
    try:
        vcf_id = int(vcf_file_id)
    except ValueError:
        return GeneListResponse(genes=[], total=0)

    vep_job, parquet_path = _find_vep_parquet(vcf_id, db)
    if not parquet_path:
        return GeneListResponse(genes=[], total=0)

    service = ParquetService()
    result = service.read_parquet(str(parquet_path), page=1, page_size=100000)

    gene_col = _pick_col(result.columns, GENE_SYMBOL_COLS)
    if not gene_col:
        return GeneListResponse(genes=[], total=0)

    chrom_col = _pick_col(result.columns, CHROM_COL_NAMES)
    af_col = _pick_af_col(result.columns)
    clinvar_col = _pick_col(result.columns, CLINVAR_COL_NAMES)
    ref_col = _pick_col(result.columns, REF_COL_NAMES)
    alt_col = _pick_col(result.columns, ALT_COL_NAMES)

    gene_data = defaultdict(lambda: {
        'variants': [],
        'types': defaultdict(int),
        'classifications': defaultdict(int),
        'chromosomes': set(),
        'max_af': 0.0
    })

    for row in result.items:
        gene = row.get(gene_col, "")
        if not gene or gene == "-":
            continue

        gene_data[gene]['variants'].append(row)

        ref_val = row.get(ref_col, "") if ref_col else ""
        alt_val = row.get(alt_col, "") if alt_col else ""
        vtype = _derive_variant_type(ref_val, alt_val)
        gene_data[gene]['types'][vtype] += 1

        if chrom_col:
            chrom = row.get(chrom_col, "")
            if chrom:
                gene_data[gene]['chromosomes'].add(chrom)

        if af_col:
            af_val = row.get(af_col, "")
            if af_val:
                try:
                    af = float(af_val)
                    if af > gene_data[gene]['max_af']:
                        gene_data[gene]['max_af'] = af
                except (ValueError, TypeError):
                    pass

        if clinvar_col:
            cv = row.get(clinvar_col, "")
            if cv and cv != "-":
                gene_data[gene]['classifications'][cv] += 1

    genes = []
    for gene, data in sorted(gene_data.items(), key=lambda x: -len(x[1]['variants'])):
        genes.append(GeneSummary(
            gene=gene,
            variant_count=len(data['variants']),
            variant_types=dict(data['types']),
            classifications=dict(data['classifications']),
            max_gnomad_af=data['max_af'] if data['max_af'] > 0 else None,
            chromosomes=sorted(list(data['chromosomes']))
        ))

    return GeneListResponse(genes=genes, total=len(genes))


@router.get("/{vcf_file_id}/{gene_name}", response_model=GeneVariantsResponse)
async def get_gene_variants(
    vcf_file_id: str,
    gene_name: str,
    db: Session = Depends(get_db)
):
    try:
        vcf_id = int(vcf_file_id)
    except ValueError:
        return GeneVariantsResponse(gene=gene_name, variants=[], total=0)

    vep_job, parquet_path = _find_vep_parquet(vcf_id, db)
    if not parquet_path:
        return GeneVariantsResponse(gene=gene_name, variants=[], total=0)

    service = ParquetService()
    result = service.read_parquet(str(parquet_path), page=1, page_size=100000)

    gene_col = _pick_col(result.columns, GENE_SYMBOL_COLS)
    if not gene_col:
        return GeneVariantsResponse(gene=gene_name, variants=[], total=0)

    chrom_col = _pick_col(result.columns, CHROM_COL_NAMES)
    pos_col = _pick_col(result.columns, POS_COL_NAMES)
    ref_col = _pick_col(result.columns, REF_COL_NAMES)
    alt_col = _pick_col(result.columns, ALT_COL_NAMES)
    af_col = _pick_af_col(result.columns)
    clinvar_col = _pick_col(result.columns, CLINVAR_COL_NAMES)

    matching_rows = [
        row for row in result.items
        if row.get(gene_col, "") == gene_name
    ]

    gene_variants = []
    for idx, row in enumerate(matching_rows):
        chromosome = row.get(chrom_col, "") if chrom_col else ""
        position = 0
        if pos_col:
            try:
                position = int(row.get(pos_col, 0))
            except (ValueError, TypeError):
                pass

        ref = row.get(ref_col, "") if ref_col else ""
        alt = row.get(alt_col, "") if alt_col else ""

        gnomad_af = None
        if af_col:
            af_val = row.get(af_col, "")
            if af_val:
                try:
                    gnomad_af = float(af_val)
                except (ValueError, TypeError):
                    gnomad_af = None

        clinvar_cls = row.get(clinvar_col, "") if clinvar_col else None

        gene_variants.append(GeneVariant(
            id=f"{chromosome}-{position}-{ref}-{alt}",
            chromosome=chromosome,
            position=position,
            ref=ref,
            alt=alt,
            variant_type=_derive_variant_type(ref, alt),
            quality=None,
            gnomad_af=gnomad_af,
            clinvar_significance=clinvar_cls,
            acmg_classification=None
        ))

    return GeneVariantsResponse(
        gene=gene_name,
        variants=gene_variants,
        total=len(gene_variants)
    )
