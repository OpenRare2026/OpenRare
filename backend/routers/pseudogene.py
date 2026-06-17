from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from backend.config import PseudogeneConfig
from backend.job_manager import create_job_dir, now_iso, run_command, read_status, write_status
from backend.models import PseudogeneRequest, JobResponse
from backend.utils.file_utils import resolve_path

router = APIRouter(prefix="/api/v1/pseudogene", tags=["pseudogene"])


def _build_cmd(req: PseudogeneRequest, output_dir: Path) -> list[str]:
    script = PseudogeneConfig.script
    if not script.is_file():
        raise HTTPException(status_code=500, detail=f"pseudogene script not found: {script}")

    cmd = [
        "python3", str(script),
        "--input", str(resolve_path(req.input_vcf)),
        "--output", str(output_dir / "preprocessed.pseudogene_annotated.vcf"),
        "--log-json", str(output_dir / "pseudogene_annotation.log.json"),
    ]

    def add(name: str, value):
        if value is not None:
            cmd.extend([name, str(value)])

    add("--sample-name", req.sample_name)
    add("--gencode-gtf", str(resolve_path(req.gencode_gtf) if req.gencode_gtf else PseudogeneConfig.gencode_gtf))
    add("--pseudogene-org", str(resolve_path(req.pseudogene_org) if req.pseudogene_org else PseudogeneConfig.pseudogene_org))
    add("--hgnc", str(resolve_path(req.hgnc) if req.hgnc else PseudogeneConfig.hgnc))

    if req.dry_run:
        cmd.append("--dry-run")
    return cmd


@router.post("", response_model=JobResponse, status_code=202)
def submit_pseudogene(req: PseudogeneRequest, background_tasks: BackgroundTasks) -> JobResponse:
    job_id = uuid.uuid4().hex
    job_dir = create_job_dir(job_id)
    output_dir = resolve_path(req.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = _build_cmd(req, output_dir)

    write_status(
        job_id,
        status="queued",
        step="pseudogene",
        created_at=now_iso(),
        request=req.model_dump(),
        command=cmd,
        output_dir=str(output_dir),
    )
    background_tasks.add_task(run_command, job_id, cmd, output_dir, step="pseudogene", log_name="pseudogene.log")
    return JobResponse(job_id=job_id, status="queued", status_url=f"/api/v1/jobs/{job_id}", output_dir=str(output_dir))


@router.get("/{job_id}")
def get_pseudogene_job(job_id: str) -> dict:
    return read_status(job_id)
