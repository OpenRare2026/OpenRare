from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks

from backend.config import InfoToCsvConfig
from backend.job_manager import create_job_dir, now_iso, run_command, read_status, write_status
from backend.models import InfoToCsvRequest, JobResponse
from backend.utils.file_utils import resolve_path

router = APIRouter(prefix="/api/v1/vcf-info-to-csv", tags=["vcf_info_to_csv"])


def _build_cmd(req: InfoToCsvRequest, output_dir: Path) -> list[str]:
    output_csv = resolve_path(req.output_csv)
    output_dir = output_csv.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    return [
        "python3", str(InfoToCsvConfig.script),
        "--input-csv", str(resolve_path(req.input_csv)),
        "--input-vcf", str(resolve_path(req.input_vcf)),
        "--output-csv", str(output_csv),
        "--log-json", str(output_dir / "vcf_info_to_csv.log.json"),
    ]


@router.post("", response_model=JobResponse, status_code=202)
def submit_vcf_info_to_csv(req: InfoToCsvRequest, background_tasks: BackgroundTasks) -> JobResponse:
    job_id = uuid.uuid4().hex
    job_dir = create_job_dir(job_id)
    output_dir = resolve_path(req.output_csv).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = _build_cmd(req, output_dir)

    write_status(
        job_id,
        status="queued",
        step="vcf_info_to_csv",
        created_at=now_iso(),
        request=req.model_dump(),
        command=cmd,
        output_dir=str(output_dir),
    )
    background_tasks.add_task(run_command, job_id, cmd, output_dir, step="vcf_info_to_csv", log_name="vcf_info_to_csv.log")
    return JobResponse(job_id=job_id, status="queued", status_url=f"/api/v1/jobs/{job_id}", output_dir=str(output_dir))


@router.get("/{job_id}")
def get_vcf_info_to_csv_job(job_id: str) -> dict:
    return read_status(job_id)
