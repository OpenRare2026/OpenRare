"""
Gene API endpoints - Gene-centric variant view.
"""
import logging
from typing import List, Optional, Dict
from collections import defaultdict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, Variant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/genes", tags=["genes"])


# Pydantic models
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


@router.get("/info/{gene_name}", response_model=Optional[GeneInfo])
async def get_gene_info(gene_name: str):
    """
    Get gene annotation info from external APIs.
    """
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
    """
    Get genes with variant summaries for a VCF file.
    """
    try:
        vcf_id = int(vcf_file_id)
    except ValueError:
        return GeneListResponse(genes=[], total=0)
    
    variants = db.query(Variant).filter(
        Variant.vcf_file_id == vcf_id,
        Variant.gene.isnot(None),
        Variant.gene != ""
    ).all()
    
    if not variants:
        return GeneListResponse(genes=[], total=0)
    
    gene_data = defaultdict(lambda: {
        'variants': [],
        'types': defaultdict(int),
        'classifications': defaultdict(int),
        'chromosomes': set(),
        'max_af': 0.0
    })
    
    for v in variants:
        gene = v.gene
        if not gene:
            continue
            
        gene_data[gene]['variants'].append(v)
        gene_data[gene]['types'][v.variant_type] += 1
        gene_data[gene]['chromosomes'].add(v.chromosome)
        
        if hasattr(v, 'acmg_classification') and v.acmg_classification:
            cls = v.acmg_classification.classification
            gene_data[gene]['classifications'][cls] += 1
        
        if v.info_field and isinstance(v.info_field, dict):
            gnomad_af = v.info_field.get('gnomad_af') or v.info_field.get('AF')
            if gnomad_af is not None:
                try:
                    af = float(gnomad_af)
                    if af > gene_data[gene]['max_af']:
                        gene_data[gene]['max_af'] = af
                except (ValueError, TypeError):
                    pass
    
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
    """
    Get all variants for a specific gene.
    """
    try:
        vcf_id = int(vcf_file_id)
    except ValueError:
        return GeneVariantsResponse(gene=gene_name, variants=[], total=0)
    
    variants = db.query(Variant).filter(
        Variant.vcf_file_id == vcf_id,
        Variant.gene == gene_name
    ).all()
    
    gene_variants = []
    for v in variants:
        gnomad_af = None
        if v.info_field and isinstance(v.info_field, dict):
            gnomad_af = v.info_field.get('gnomad_af') or v.info_field.get('AF')
            if gnomad_af is not None:
                try:
                    gnomad_af = float(gnomad_af)
                except (ValueError, TypeError):
                    gnomad_af = None
        
        acmg_cls = None
        if hasattr(v, 'acmg_classification') and v.acmg_classification:
            acmg_cls = v.acmg_classification.classification
        
        clinvar_cls = None
        if hasattr(v, 'clinvar_significance') and v.clinvar_significance:
            clinvar_cls = v.clinvar_significance
        elif v.info_field and isinstance(v.info_field, dict):
            clinvar_cls = v.info_field.get('clinvar_significance') or v.info_field.get('CLNSIG')
        
        gene_variants.append(GeneVariant(
            id=str(v.id),
            chromosome=str(v.chromosome),
            position=int(v.position),
            ref=str(v.ref),
            alt=str(v.alt),
            variant_type=str(v.variant_type),
            quality=float(v.quality) if v.quality else None,
            gnomad_af=gnomad_af,
            clinvar_significance=clinvar_cls,
            acmg_classification=acmg_cls
        ))
    
    return GeneVariantsResponse(
        gene=gene_name,
        variants=gene_variants,
        total=len(gene_variants)
    )
