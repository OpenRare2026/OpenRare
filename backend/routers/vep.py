from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks

from backend.config import VepConfig
from backend.job_manager import create_job_dir, now_iso, run_command, read_status, write_status
from backend.models import VepRequest, JobResponse
from backend.utils.file_utils import resolve_path

router = APIRouter(prefix="/api/v1/vep", tags=["vep"])


def _build_cmd(req: VepRequest) -> list[str]:
    script = VepConfig.script
    config_file = resolve_path(req.config) if req.config else VepConfig.config_file

    cmd = [
        "python3", str(script),
        "-i", str(resolve_path(req.input_vcf)),
        "-o", str(resolve_path(req.output_csv)),
        "--config", str(config_file),
        "--format", "vcf",
        "--hgvs",
        "--fork", str(req.fork or VepConfig.fork),
        "--top-k-transcripts", str(req.top_k_transcripts or VepConfig.top_k_transcripts),
        "--no-pseudogene-annotation",
        "--no-regulatory-annotation",
        "--no-vcf-info-to-csv",
        "--no-pathogenic-ranking",
    ]

    if req.keep_raw_vep if req.keep_raw_vep is not None else VepConfig.keep_raw_vep:
        cmd.extend(["--keep-vep", str(resolve_path(req.output_csv).parent / "raw_vep.tsv")])

    if req.hpo_id:
        cmd.extend(["--hpo-id", req.hpo_id])

    if req.clinical_tissue:
        cmd.extend(["--clinical-tissue", req.clinical_tissue])

    if req.dry_run:
        cmd.append("--dry-run")
    return cmd


@router.post("", response_model=JobResponse, status_code=202)
def submit_vep(req: VepRequest, background_tasks: BackgroundTasks) -> JobResponse:
    job_id = uuid.uuid4().hex
    job_dir = create_job_dir(job_id)
    output_csv = resolve_path(req.output_csv)
    output_dir = output_csv.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = _build_cmd(req)

    write_status(
        job_id,
        status="queued",
        step="vep",
        created_at=now_iso(),
        request=req.model_dump(),
        command=cmd,
        output_dir=str(output_dir),
    )
    background_tasks.add_task(run_command, job_id, cmd, output_dir, step="vep", log_name="vep.log")
    return JobResponse(job_id=job_id, status="queued", status_url=f"/api/v1/jobs/{job_id}", output_dir=str(output_dir))


@router.get("/{job_id}")
def get_vep_job(job_id: str) -> dict:
    return read_status(job_id)
