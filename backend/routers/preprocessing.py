from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks

from backend.config import PreprocessingConfig
from backend.job_manager import create_job_dir, now_iso, run_command, read_status, write_status
from backend.models import PreprocessingRequest, JobResponse
from backend.utils.file_utils import resolve_path

router = APIRouter(prefix="/api/v1/preprocessing", tags=["preprocessing"])


def _build_cmd(req: PreprocessingRequest) -> list[str]:
    script = PreprocessingConfig.script
    cmd = [
        "bash", str(script),
        str(resolve_path(req.input_vcf)),
        str(resolve_path(req.output_prefix)),
    ]
    if req.sample_id:
        cmd.append(req.sample_id)
    cmd.append(str(resolve_path(req.ccre_bed) if req.ccre_bed else PreprocessingConfig.ccre_bed))
    cmd.append(str(resolve_path(req.ncrna_bed) if req.ncrna_bed else PreprocessingConfig.ncrna_bed))
    return cmd


@router.post("", response_model=JobResponse, status_code=202)
def submit_preprocessing(req: PreprocessingRequest, background_tasks: BackgroundTasks) -> JobResponse:
    job_id = uuid.uuid4().hex
    job_dir = create_job_dir(job_id)
    output_prefix = resolve_path(req.output_prefix)
    output_dir = output_prefix.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = _build_cmd(req)

    write_status(
        job_id,
        status="queued",
        step="preprocessing",
        created_at=now_iso(),
        request=req.model_dump(),
        command=cmd,
        output_dir=str(output_dir),
    )
    background_tasks.add_task(run_command, job_id, cmd, output_dir, step="preprocessing", log_name="preprocessing.log")
    return JobResponse(job_id=job_id, status="queued", status_url=f"/api/v1/jobs/{job_id}", output_dir=str(output_dir))


@router.get("/{job_id}")
def get_preprocessing_job(job_id: str) -> dict:
    return read_status(job_id)
