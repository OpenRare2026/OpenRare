"""
Report Generation API endpoints.
SSE-based streaming for clinical gene prioritization reports.
"""
import logging
import json
from typing import List, Optional, Generator

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, Variant
from services.report_service import (
    ReportService,
    ReportServiceError,
)
from services.phenotype_hpo_service import PhenotypeHpoService
from services.ppi_score_service import PpiScoreService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/report", tags=["report"])


class ReportRequest(BaseModel):
    vcf_file_id: int
    hpo_job_uid: Optional[str] = None
    ppi_job_id: Optional[str] = None
    hpo_terms: List[str] = Field(default_factory=list)
    symptom_text: Optional[str] = None
    genes: Optional[List[str]] = None
    top_n: int = 10
    k: int = 5


class ReportStatusResponse(BaseModel):
    status: str
    message: str = ""


@router.post("/submit")
async def submit_report(
    request: ReportRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a report generation job.
    
    Requires:
    - vcf_file_id: The VCF file ID (to build wide.csv from VEP-annotated variants)
    - hpo_job_uid: HPO scoring job UID (to get phenotype.csv)
    - ppi_job_id: PPI scoring job ID (to get ppi.csv)
    - hpo_terms: List of primary HPO IDs
    - symptom_text: Clinical phenotype description
    - genes: Selected genes (overrides top_n)
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
        
        service = ReportService()
        
        ppi_service = PpiScoreService()
        wide_csv_path = ppi_service._write_temp_file(
            ppi_service.build_vep_csv_from_variants(variants),
            suffix="_wide.csv"
        )
        
        phenotype_csv_path = None
        if request.hpo_job_uid:
            hpo_service = PhenotypeHpoService()
            phenotype_csv_content = await hpo_service.get_gene_scores_csv(request.hpo_job_uid)
            phenotype_csv_path = service._write_temp_file(phenotype_csv_content, suffix="_phenotype.csv")
        
        ppi_csv_path = None
        if request.ppi_job_id:
            ppi_service = PpiScoreService()
            ppi_csv_content = await ppi_service.get_gene_scores_csv(request.ppi_job_id)
            ppi_csv_path = service._write_temp_file(ppi_csv_content, suffix="_ppi.csv")
        
        return {
            "wide_csv_path": wide_csv_path,
            "phenotype_csv_path": phenotype_csv_path,
            "ppi_csv_path": ppi_csv_path,
            "hpo_terms": request.hpo_terms,
            "symptom_text": request.symptom_text,
            "genes": request.genes,
            "top_n": request.top_n,
            "k": request.k,
        }
        
    except ReportServiceError as e:
        logger.error(f"Report service error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit report job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_report(request: ReportRequest, db: Session = Depends(get_db)):
    """
    Stream report generation via SSE.
    
    Returns Server-Sent Events with:
    - meta: run_id, genes, pheno_coverage, ppi_coverage
    - md: markdown content chunks
    - done: pdf_url for download
    """
    try:
        variants = db.query(Variant).filter(
            Variant.vcf_file_id == request.vcf_file_id,
            Variant.vep_annotated == True
        ).all()
        
        if not variants:
            raise HTTPException(
                status_code=400,
                detail="No VEP-annotated variants found"
            )
        
        logger.info(f"Starting report generation for VCF {request.vcf_file_id} with {len(variants)} variants")
        
        service = ReportService()
        
        ppi_service = PpiScoreService()
        wide_csv_content = ppi_service.build_vep_csv_from_variants(variants)
        logger.info(f"Built wide CSV: {len(wide_csv_content)} bytes, {len(wide_csv_content.split(chr(10)))} lines")
        logger.debug(f"Wide CSV preview: {wide_csv_content[:500]}")
        
        phenotype_csv_content = None
        if request.hpo_job_uid:
            try:
                hpo_service = PhenotypeHpoService()
                phenotype_csv_content = await hpo_service.get_gene_scores_csv(request.hpo_job_uid)
                logger.info(f"Got phenotype CSV: {len(phenotype_csv_content)} bytes")
            except Exception as e:
                logger.warning(f"Failed to get phenotype CSV: {e}")
        
        ppi_csv_content = None
        if request.ppi_job_id:
            try:
                ppi_csv_content = await ppi_service.get_gene_scores_csv(request.ppi_job_id)
                logger.info(f"Got PPI CSV: {len(ppi_csv_content)} bytes")
            except Exception as e:
                logger.warning(f"Failed to get PPI CSV: {e}")
        
        def event_generator() -> Generator[str, None, None]:
            try:
                for event in service.stream_report(
                    wide_csv_content=wide_csv_content,
                    phenotype_csv_content=phenotype_csv_content,
                    ppi_csv_content=ppi_csv_content,
                    hpo_ids=request.hpo_terms,
                    symptom_text=request.symptom_text,
                    genes=request.genes,
                    top_n=request.top_n,
                    k=request.k,
                ):
                    yield f"data: {json.dumps(event)}\n\n"
                    
            except ReportServiceError as e:
                logger.error(f"Report service error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            except Exception as e:
                logger.error(f"Unexpected error in event generator: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stream report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{run_id}/pdf")
async def download_report_pdf(run_id: str):
    """
    Download the generated PDF report.
    """
    try:
        service = ReportService()
        pdf_content = await service.get_pdf(run_id)
        
        from fastapi.responses import Response
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{run_id}.pdf"
            }
        )
        
    except ReportServiceError as e:
        logger.error(f"Failed to download PDF: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"PDF download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def report_service_health():
    """
    Check report API health.
    """
    try:
        service = ReportService()
        is_healthy = await service.health_check()
        service.cleanup()
        
        return {"status": "ok" if is_healthy else "unhealthy"}
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "message": str(e)}
