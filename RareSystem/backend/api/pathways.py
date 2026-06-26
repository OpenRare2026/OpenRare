"""
Pathway API endpoints - Reactome pathway enrichment analysis.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from database.models import VEPJob
from services.pathway_service import reactome_service, PathwayResult
from services.parquet_service import ParquetService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pathways", tags=["pathways"])


class PathwayAnalysisRequest(BaseModel):
    genes: List[str]


class PathwayResponse(BaseModel):
    st_id: str
    name: str
    p_value: float
    fdr: float
    entities_count: int
    entities_found: int
    entities_ratio: float
    species: str
    mapped_genes: List[str] = []
    pathway_type: str = "Pathway"
    compartments: List[str] = []


class PathwayAnalysisResponse(BaseModel):
    token: str
    pathways: List[PathwayResponse]
    genes_analyzed: int
    genes_not_found: int


class GOBiologicalProcess(BaseModel):
    db_id: int
    display_name: str
    accession: str
    database_name: str
    definition: Optional[str] = None
    name: str
    url: str
    schema_class: str


class LiteratureReference(BaseModel):
    db_id: int
    display_name: str
    title: Optional[str] = None
    journal: Optional[str] = None
    pages: Optional[str] = None
    pub_med_identifier: Optional[int] = None
    volume: Optional[int] = None
    year: Optional[int] = None
    url: Optional[str] = None


class Summation(BaseModel):
    db_id: int
    display_name: str
    text: Optional[str] = None


class OrthologousEvent(BaseModel):
    db_id: int
    display_name: str
    st_id: str
    st_id_version: str
    species_name: str
    schema_class: str
    is_in_disease: bool = False
    is_inferred: bool = False
    max_depth: int = 0
    release_date: Optional[str] = None
    has_diagram: bool = False
    has_ehld: bool = False


class HasEvent(BaseModel):
    db_id: int
    display_name: str
    st_id: str
    st_id_version: str
    name: List[str] = []
    schema_class: str
    is_in_disease: bool = False
    is_inferred: bool = False
    max_depth: int = 0
    release_date: Optional[str] = None
    species_name: Optional[str] = None
    category: Optional[str] = None
    has_diagram: bool = False
    has_ehld: bool = False


class Compartment(BaseModel):
    db_id: int
    display_name: str
    name: str = ""
    schema_class: str
    accession: Optional[str] = None


class Species(BaseModel):
    db_id: int
    display_name: str
    name: List[str] = []
    tax_id: Optional[str] = None
    abbreviation: Optional[str] = None
    schema_class: str = "Species"


class ReviewStatus(BaseModel):
    db_id: int
    display_name: str
    definition: Optional[str] = None
    name: List[str] = []
    schema_class: str = "ReviewStatus"


class PathwayDetailResponse(BaseModel):
    db_id: int
    st_id: str
    st_id_version: str
    display_name: str
    name: List[str] = []
    schema_class: str
    class_name: Optional[str] = None
    
    species_name: str
    species: Optional[Species] = None
    
    is_in_disease: bool = False
    is_inferred: bool = False
    has_diagram: bool = False
    has_ehld: bool = False
    
    release_date: Optional[str] = None
    release_status: Optional[str] = None
    last_updated_date: Optional[str] = None
    review_status: Optional[ReviewStatus] = None
    previous_review_status: Optional[ReviewStatus] = None
    
    max_depth: int = 0
    
    go_biological_process: Optional[GOBiologicalProcess] = None
    summation: List[Summation] = []
    literature_reference: List[LiteratureReference] = []
    compartment: List[Compartment] = []
    has_event: List[HasEvent] = []
    orthologous_event: List[OrthologousEvent] = []
    
    url: str


@router.post("/analyze", response_model=PathwayAnalysisResponse)
async def analyze_pathways(request: PathwayAnalysisRequest):
    """
    Perform pathway enrichment analysis on a list of genes.
    
    Uses Reactome's over-representation analysis to find pathways
    enriched for the provided genes.
    """
    try:
        result = await reactome_service.analyze_genes(request.genes)
        
        if result is None:
            raise HTTPException(
                status_code=500, 
                detail="Pathway analysis failed"
            )
        
        pathways = [
            PathwayResponse(
                st_id=p.st_id,
                name=p.name,
                p_value=p.p_value,
                fdr=p.fdr,
                entities_count=p.entities_count,
                entities_found=p.entities_found,
                entities_ratio=p.entities_ratio,
                species=p.species,
                mapped_genes=p.mapped_genes,
                pathway_type=p.pathway_type,
                compartments=p.compartments
            )
            for p in result.pathways
        ]
        
        return PathwayAnalysisResponse(
            token=result.token,
            pathways=pathways,
            genes_analyzed=len(request.genes),
            genes_not_found=result.genes_not_found
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pathway analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/vcf/{vcf_file_id}", response_model=PathwayAnalysisResponse)
async def analyze_vcf_pathways(
    vcf_file_id: str,
    db: Session = Depends(get_db)
):
    """
    Perform pathway enrichment analysis using genes from VEP Parquet results.
    
    Extracts all unique gene symbols from the VEP Parquet file
    and performs pathway enrichment analysis.
    """
    from pathlib import Path as FilePath
    
    try:
        vcf_id = int(vcf_file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid VCF file ID")

    vep_job = db.query(VEPJob).filter(
        VEPJob.vcf_file_id == vcf_id,
        VEPJob.parquet_path.isnot(None)
    ).order_by(VEPJob.created_at.desc()).first()

    if not vep_job or not vep_job.parquet_path:
        raise HTTPException(
            status_code=400,
            detail="No VEP results available for this VCF file"
        )

    parquet_path = FilePath(vep_job.parquet_path)
    if not parquet_path.exists():
        raise HTTPException(
            status_code=400,
            detail="VEP Parquet file not found"
        )

    service = ParquetService()
    result = service.read_parquet(str(parquet_path), page=1, page_size=100000)

    # Extract gene symbols from whatever VEP column provides them
    gene_cols = [c for c in result.columns if c in ("Gene", "gene_symbol", "SYMBOL", "Gene_symbol")]
    
    genes = set()
    for row in result.items:
        for col in gene_cols:
            val = row.get(col, "")
            if val:
                # Some VEP outputs have comma-separated gene lists
                for g in val.split(","):
                    g = g.strip()
                    if g:
                        genes.add(g)

    if not genes:
        raise HTTPException(
            status_code=400,
            detail="No genes found in VEP results"
        )

    try:
        result = await reactome_service.analyze_genes(list(genes))

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Pathway analysis failed"
            )

        pathways = [
            PathwayResponse(
                st_id=p.st_id,
                name=p.name,
                p_value=p.p_value,
                fdr=p.fdr,
                entities_count=p.entities_count,
                entities_found=p.entities_found,
                entities_ratio=p.entities_ratio,
                species=p.species,
                mapped_genes=p.mapped_genes,
                pathway_type=p.pathway_type,
                compartments=p.compartments
            )
            for p in result.pathways
        ]

        return PathwayAnalysisResponse(
            token=result.token,
            pathways=pathways,
            genes_analyzed=len(genes),
            genes_not_found=result.genes_not_found
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"VCF pathway analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{st_id}", response_model=PathwayDetailResponse)
async def get_pathway_detail(st_id: str):
    """
    Get detailed information about a specific pathway.
    
    Args:
        st_id: Reactome stable identifier (e.g., R-HSA-123456)
    """
    try:
        result = await reactome_service.get_pathway_details(st_id)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Pathway {st_id} not found"
            )
        
        go_bp_data = result.get("goBiologicalProcess")
        go_biological_process = None
        if go_bp_data:
            go_biological_process = GOBiologicalProcess(
                db_id=go_bp_data.get("dbId", 0),
                display_name=go_bp_data.get("displayName", ""),
                accession=go_bp_data.get("accession", ""),
                database_name=go_bp_data.get("databaseName", ""),
                definition=go_bp_data.get("definition"),
                name=go_bp_data.get("name", ""),
                url=go_bp_data.get("url", ""),
                schema_class=go_bp_data.get("schemaClass", "")
            )
        
        literature_references = []
        for ref in result.get("literatureReference", []):
            literature_references.append(LiteratureReference(
                db_id=ref.get("dbId", 0),
                display_name=ref.get("displayName", ""),
                title=ref.get("title"),
                journal=ref.get("journal"),
                pages=ref.get("pages"),
                pub_med_identifier=ref.get("pubMedIdentifier"),
                volume=ref.get("volume"),
                year=ref.get("year"),
                url=ref.get("url")
            ))
        
        summations = []
        for s in result.get("summation", []):
            summations.append(Summation(
                db_id=s.get("dbId", 0),
                display_name=s.get("displayName", ""),
                text=s.get("text")
            ))
        
        compartments = []
        for c in result.get("compartment", []):
            compartments.append(Compartment(
                db_id=c.get("dbId", 0),
                display_name=c.get("displayName", ""),
                name=c.get("name", ""),
                schema_class=c.get("schemaClass", ""),
                accession=c.get("accession")
            ))
        
        has_events = []
        for e in result.get("hasEvent", []):
            has_events.append(HasEvent(
                db_id=e.get("dbId", 0),
                display_name=e.get("displayName", ""),
                st_id=e.get("stId", ""),
                st_id_version=e.get("stIdVersion", ""),
                name=e.get("name", []),
                schema_class=e.get("schemaClass", ""),
                is_in_disease=e.get("isInDisease", False),
                is_inferred=e.get("isInferred", False),
                max_depth=e.get("maxDepth", 0),
                release_date=e.get("releaseDate"),
                species_name=e.get("speciesName"),
                category=e.get("category"),
                has_diagram=e.get("hasDiagram", False),
                has_ehld=e.get("hasEHLD", False)
            ))
        
        orthologous_events = []
        for o in result.get("orthologousEvent", []):
            orthologous_events.append(OrthologousEvent(
                db_id=o.get("dbId", 0),
                display_name=o.get("displayName", ""),
                st_id=o.get("stId", ""),
                st_id_version=o.get("stIdVersion", ""),
                species_name=o.get("speciesName", ""),
                schema_class=o.get("schemaClass", ""),
                is_in_disease=o.get("isInDisease", False),
                is_inferred=o.get("isInferred", False),
                max_depth=o.get("maxDepth", 0),
                release_date=o.get("releaseDate"),
                has_diagram=o.get("hasDiagram", False),
                has_ehld=o.get("hasEHLD", False)
            ))
        
        species_data = result.get("species")
        species_obj = None
        if species_data and isinstance(species_data, list) and len(species_data) > 0:
            s = species_data[0]
            species_obj = Species(
                db_id=s.get("dbId", 0),
                display_name=s.get("displayName", ""),
                name=s.get("name", []),
                tax_id=s.get("taxId"),
                abbreviation=s.get("abbreviation"),
                schema_class=s.get("schemaClass", "Species")
            )
        
        review_status_data = result.get("reviewStatus")
        review_status_obj = None
        if review_status_data:
            review_status_obj = ReviewStatus(
                db_id=review_status_data.get("dbId", 0),
                display_name=review_status_data.get("displayName", ""),
                definition=review_status_data.get("definition"),
                name=review_status_data.get("name", []),
                schema_class=review_status_data.get("schemaClass", "ReviewStatus")
            )
        
        previous_review_status_data = result.get("previousReviewStatus")
        previous_review_status_obj = None
        if previous_review_status_data:
            previous_review_status_obj = ReviewStatus(
                db_id=previous_review_status_data.get("dbId", 0),
                display_name=previous_review_status_data.get("displayName", ""),
                definition=previous_review_status_data.get("definition"),
                name=previous_review_status_data.get("name", []),
                schema_class=previous_review_status_data.get("schemaClass", "ReviewStatus")
            )
        
        return PathwayDetailResponse(
            db_id=result.get("dbId", 0),
            st_id=result.get("stId", st_id),
            st_id_version=result.get("stIdVersion", ""),
            display_name=result.get("displayName", ""),
            name=result.get("name", []),
            schema_class=result.get("schemaClass", ""),
            class_name=result.get("className"),
            species_name=result.get("speciesName", ""),
            species=species_obj,
            is_in_disease=result.get("isInDisease", False),
            is_inferred=result.get("isInferred", False),
            has_diagram=result.get("hasDiagram", False),
            has_ehld=result.get("hasEHLD", False),
            release_date=result.get("releaseDate"),
            release_status=result.get("releaseStatus"),
            last_updated_date=result.get("lastUpdatedDate"),
            review_status=review_status_obj,
            previous_review_status=previous_review_status_obj,
            max_depth=result.get("maxDepth", 0),
            go_biological_process=go_biological_process,
            summation=summations,
            literature_reference=literature_references,
            compartment=compartments,
            has_event=has_events,
            orthologous_event=orthologous_events,
            url=f"https://reactome.org/PathwayBrowser/#/{st_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pathway detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/token/{token}")
async def get_analysis_by_token(
    token: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)
):
    """
    Retrieve previous pathway analysis results by token.
    
    Args:
        token: Analysis token from a previous analysis
        page: Page number for paginated results
        page_size: Number of results per page
    """
    try:
        result = await reactome_service.get_analysis_result(token, page, page_size)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Analysis token not found or expired"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gene/{gene}")
async def get_pathways_for_gene(gene: str):
    """
    Get all pathways associated with a gene.
    
    Args:
        gene: Gene symbol (e.g., TP53)
    """
    try:
        pathways = await reactome_service.map_gene_to_pathways(gene)
        
        return {
            "gene": gene,
            "pathways": pathways or [],
            "count": len(pathways) if pathways else 0
        }
        
    except Exception as e:
        logger.error(f"Gene pathway mapping error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
