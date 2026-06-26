"""
Report Generation API endpoints.
SSE-based streaming for clinical gene prioritization reports.
"""
import csv
import logging
import json
import os
import tempfile
from typing import List, Optional, Generator
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, VEPJob, Patient, VCFFile
from services.report_service import (
    ReportService,
    ReportServiceError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/report", tags=["report"])


class ReportRequest(BaseModel):
    vcf_file_id: int
    hpo_terms: List[str] = Field(default_factory=list)
    top_n: int = 10
    diagnosis_description: Optional[str] = None
    medical_history: Optional[str] = None


class ReportStatusResponse(BaseModel):
    status: str
    message: str = ""


def _validate_file_path(path: Optional[str], field_name: str, required: bool = False) -> Optional[str]:
    if not path:
        if required:
            raise HTTPException(status_code=400, detail=f"No {field_name} available")
        return None

    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=400, detail=f"{field_name} file not found: {path}")

    return str(file_path.resolve())


def _generate_phenotype_csv(
    patient_id: int,
    hpo_terms: List[str],
    diagnosis_description: Optional[str] = None,
    medical_history: Optional[str] = None,
) -> Optional[str]:
    """Generate phenotype.csv (ID + Phenotype columns).

    Composes phenotype text from explicit clinical inputs (highest priority),
    then Patient DB record as fallback.
    """
    from database import SessionLocal
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return None

        parts = []

        if diagnosis_description:
            parts.append(diagnosis_description)
        elif patient.diagnosis_description:
            parts.append(patient.diagnosis_description)

        if medical_history:
            parts.append(medical_history)
        elif patient.medical_history:
            parts.append(patient.medical_history)

        if hpo_terms:
            parts.append("HPO: " + ", ".join(hpo_terms))
        elif patient.hpo_terms:
            hpo_ids = [t.get("hpo_id", "") for t in patient.hpo_terms if t.get("hpo_id")]
            if hpo_ids:
                parts.append("HPO: " + ", ".join(hpo_ids))

        phenotype_text = "; ".join(parts) if parts else "无描述"

        fd, path = tempfile.mkstemp(suffix=".csv", prefix="rdr_phenotype_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["ID", "Phenotype"])
            writer.writerow([str(patient_id), phenotype_text])

        os.chmod(path, 0o644)
        return path
    except Exception as e:
        logger.error(f"Failed to generate phenotype.csv: {e}")
        return None
    finally:
        db.close()


@router.post("/stream")
async def stream_report(request: ReportRequest, db: Session = Depends(get_db)):
    """
    Stream report generation via SSE.
    """
    try:
        vep_job = db.query(VEPJob).filter(
            VEPJob.vcf_file_id == request.vcf_file_id,
            VEPJob.csv_path.isnot(None)
        ).order_by(VEPJob.created_at.desc()).first()

        if not vep_job or not vep_job.csv_path:
            raise HTTPException(
                status_code=400,
                detail="No VEP results available"
            )

        wide_csv_path = _validate_file_path(
            vep_job.ranked_csv_path or vep_job.csv_path,
            "Ranked/VEP CSV",
            required=True,
        )

        phenotype_csv_path = None
        if vep_job.phenotype_path:
            phenotype_csv_path = _validate_file_path(vep_job.phenotype_path, "Phenotype CSV")
        if not phenotype_csv_path:
            vcf_file = db.query(VCFFile).filter(VCFFile.id == request.vcf_file_id).first()
            if vcf_file and vcf_file.patient_id:
                phenotype_csv_path = _generate_phenotype_csv(
                    patient_id=vcf_file.patient_id,
                    hpo_terms=request.hpo_terms,
                    diagnosis_description=request.diagnosis_description,
                    medical_history=request.medical_history,
                )

        ppi_csv_path = _validate_file_path(vep_job.ppi_score_path, "PPI score CSV")

        wide_source = "ranked" if vep_job.ranked_csv_path else "vep"
        logger.info(
            f"Report paths - wide({wide_source}): {wide_csv_path}, "
            f"phenotype: {phenotype_csv_path}, ppi: {ppi_csv_path}"
        )

        file_paths = {
            "wide_csv": wide_csv_path,
            "phenotype_csv": phenotype_csv_path,
            "ppi_csv": ppi_csv_path,
        }
        for label, fpath in file_paths.items():
            if not fpath:
                logger.warning(f"Report input file [{label}]: NOT PROVIDED")
                continue
            p = Path(fpath)
            if p.exists():
                size = p.stat().st_size
                logger.info(f"Report input file [{label}]: EXISTS, size={size} bytes, path={fpath}")
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        header = f.readline().strip()
                        logger.info(f"Report input file [{label}] header: {header[:200]}")
                except Exception as e:
                    logger.warning(f"Report input file [{label}] read error: {e}")
            else:
                logger.error(f"Report input file [{label}]: MISSING ON DISK, path={fpath}")

        service = ReportService()
        _generated_temp: List[str] = []

        def event_generator() -> Generator[str, None, None]:
            try:
                for event in service.stream_report(
                    wide_csv_path=wide_csv_path,
                    phenotype_csv_path=phenotype_csv_path,
                    ppi_csv_path=ppi_csv_path,
                    hpo_ids=request.hpo_terms,
                    top_n=request.top_n,
                ):
                    yield f"data: {json.dumps(event)}\n\n"

            except ReportServiceError as e:
                logger.error(f"Report service error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            except Exception as e:
                logger.error(f"Unexpected error in event generator: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            finally:
                service.cleanup()
                for p in _generated_temp:
                    try:
                        if os.path.exists(p):
                            os.remove(p)
                    except OSError:
                        pass

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


@router.get("/{run_id}/md")
async def download_report_md(run_id: str):
    try:
        service = ReportService()
        content = await service.get_markdown(run_id)

        from fastapi.responses import Response
        return Response(
            content=content,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=report_{run_id}.md"
            }
        )

    except ReportServiceError as e:
        logger.error(f"Failed to download markdown: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Markdown download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def report_service_health():
    try:
        service = ReportService()
        is_healthy = await service.health_check()
        service.cleanup()

        return {"status": "ok" if is_healthy else "unhealthy"}

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "message": str(e)}
