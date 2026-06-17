from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from backend.config import PhasingConfig, ROOT
from backend.job_manager import create_job_dir, run_command, read_status
from backend.models import PhasingRequest, JobResponse
from backend.utils.file_utils import resolve_path

router = APIRouter(prefix="/api/v1/phasing", tags=["phasing"])


def _build_cmd(req: PhasingRequest, output_dir: Path) -> list[str]:
    script = PhasingConfig.script
    if not script.is_file():
        raise HTTPException(status_code=500, detail=f"phasing script not found: {script}")

    cmd = [
        "bash", str(script),
        "--patient-vcf", resolve_path(req.input_vcf),
        "--out-dir", str(output_dir),
        "--beagle-jar", str(resolve_path(req.beagle_jar) if req.beagle_jar else PhasingConfig.beagle_jar),
        "--chromosomes", req.chromosomes,
        "--ref-dir", str(resolve_path(req.ref_dir) if req.ref_dir else PhasingConfig.ref_dir),
    ]

    def add(name: str, value):
        if value is not None:
            cmd.extend([name, str(value)])

    add("--sample-id", req.sample_id)
    add("--chr-jobs", req.chr_jobs or PhasingConfig.chr_jobs)
    add("--beagle-threads", req.beagle_threads or PhasingConfig.beagle_threads)
    add("--java-heap-gb", req.java_heap_gb or PhasingConfig.java_heap_gb)
    add("--java-bin", resolve_path(req.java_bin) if req.java_bin else PhasingConfig.java_bin)

    if req.dry_run:
        cmd.append("--dry-run")
    return cmd


@router.post("", response_model=JobResponse, status_code=202)
def submit_phasing(req: PhasingRequest, background_tasks: BackgroundTasks) -> JobResponse:
    job_id = uuid.uuid4().hex
    job_dir = create_job_dir(job_id)
    output_dir = resolve_path(req.output_dir) if req.output_dir else job_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = _build_cmd(req, output_dir)

    from backend.job_manager import write_status, now_iso

    write_status(
        job_id,
        status="queued",
        step="phasing",
        created_at=now_iso(),
        request=req.model_dump(),
        command=cmd,
        output_dir=str(output_dir),
    )
    background_tasks.add_task(run_command, job_id, cmd, output_dir, step="phasing")
    return JobResponse(job_id=job_id, status="queued", status_url=f"/api/v1/jobs/{job_id}", output_dir=str(output_dir))


@router.get("/{job_id}")
def get_phasing_job(job_id: str) -> dict:
    return read_status(job_id)
