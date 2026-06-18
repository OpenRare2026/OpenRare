from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from backend.config import ApiConfig, ROOT
from backend.job_manager import create_job_dir, now_iso, run_command, read_status, write_status
from backend.models import PipelineRequest, PipelineUploadRequest, JobResponse
from backend.utils.file_utils import resolve_path, save_upload

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])

RUN_SCRIPT = ROOT / "scripts" / "run_full_pipeline.sh"


def _normalize_hpo_ids(raw: str) -> str:
    tokens = re.split(r"[\s,;]+", raw.strip())
    return ",".join(token for token in tokens if token)


def _read_hpo_upload(upload: UploadFile | None) -> str:
    if upload is None:
        return ""
    data = upload.file.read()
    return _normalize_hpo_ids(data.decode("utf-8", errors="replace"))


def _build_full_cmd(req: PipelineRequest, output_dir: Path) -> list[str]:
    if not RUN_SCRIPT.is_file():
        raise HTTPException(status_code=500, detail=f"pipeline script not found: {RUN_SCRIPT}")

    input_vcf = resolve_path(req.input_vcf)
    cmd = [
        "bash", str(RUN_SCRIPT),
        "--input-vcf", str(input_vcf),
        "--out-dir", str(output_dir),
        "--fork", str(req.fork),
    ]

    def add(name: str, value):
        if value is not None and value != "":
            cmd.extend([name, str(value)])

    add("--hpo-id", req.hpo_id)
    add("--sample-id", req.sample_id)
    add("--chromosomes", req.chromosomes)
    add("--ref-dir", str(resolve_path(req.ref_dir)) if req.ref_dir else None)
    add("--beagle-jar", str(resolve_path(req.beagle_jar)) if req.beagle_jar else None)
    add("--ccre-bed", str(resolve_path(req.ccre_bed)) if req.ccre_bed else None)
    add("--ncrna-bed", str(resolve_path(req.ncrna_bed)) if req.ncrna_bed else None)
    add("--chr-jobs", req.chr_jobs)
    add("--beagle-threads", req.beagle_threads)
    add("--java-heap-gb", req.java_heap_gb)
    add("--java-bin", str(resolve_path(req.java_bin)) if req.java_bin else None)
    add("--top-k-transcripts", req.top_k_transcripts)
    add("--clinical-tissue", req.clinical_tissue)
    if req.keep_raw_vep is not None:
        cmd.extend(["--keep-raw-vep", "yes" if req.keep_raw_vep else "no"])
    if req.dry_run:
        cmd.append("--dry-run")
    return cmd


@router.post("", response_model=JobResponse, status_code=202)
def submit_pipeline(req: PipelineRequest, background_tasks: BackgroundTasks) -> JobResponse:
    job_id = uuid.uuid4().hex
    job_dir = create_job_dir(job_id)
    output_dir = resolve_path(req.output_dir) if req.output_dir else job_dir / "output"
    job_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = _build_full_cmd(req, output_dir)

    write_status(
        job_id,
        status="queued",
        step="full_pipeline",
        created_at=now_iso(),
        request=req.model_dump(),
        command=cmd,
        output_dir=str(output_dir),
    )
    background_tasks.add_task(
        run_command,
        job_id, cmd, output_dir,
        step="full_pipeline",
        log_name="pipeline.log",
        cwd=ROOT,
    )
    return JobResponse(job_id=job_id, status="queued", status_url=f"/api/v1/jobs/{job_id}", output_dir=str(output_dir))


@router.post("/upload", response_model=JobResponse, status_code=202)
def submit_pipeline_upload(
    background_tasks: BackgroundTasks,
    input_vcf: UploadFile = File(..., description="Input VCF/VCF.GZ file"),
    output_dir: Optional[str] = Form(None),
    fork: int = Form(1),
    hpo_id: str = Form(""),
    hpo_file: UploadFile | None = File(None, description="Optional TXT file containing HPO IDs"),
    sample_id: Optional[str] = Form(None),
    chromosomes: Optional[str] = Form(None),
    ref_dir: Optional[str] = Form(None),
    beagle_jar: Optional[str] = Form(None),
    ccre_bed: Optional[str] = Form(None),
    ncrna_bed: Optional[str] = Form(None),
    chr_jobs: Optional[int] = Form(None),
    beagle_threads: Optional[int] = Form(None),
    java_heap_gb: Optional[int] = Form(None),
    java_bin: Optional[str] = Form(None),
    top_k_transcripts: Optional[int] = Form(None),
    clinical_tissue: str = Form(""),
    keep_raw_vep: Optional[bool] = Form(None),
    dry_run: bool = Form(False),
) -> JobResponse:
    job_id = uuid.uuid4().hex
    job_dir = create_job_dir(job_id)
    uploaded_path = save_upload(input_vcf, job_dir / "input")
    hpo_from_file = _read_hpo_upload(hpo_file)
    merged_hpo_id = _normalize_hpo_ids(",".join(x for x in [hpo_id, hpo_from_file] if x))
    output_dir_path = job_dir / "output"

    req = PipelineRequest(
        input_vcf=str(uploaded_path),
        output_dir=str(output_dir_path),
        fork=fork,
        hpo_id=merged_hpo_id,
        sample_id=sample_id,
        chromosomes=chromosomes,
        ref_dir=ref_dir,
        beagle_jar=beagle_jar,
        ccre_bed=ccre_bed,
        ncrna_bed=ncrna_bed,
        chr_jobs=chr_jobs,
        beagle_threads=beagle_threads,
        java_heap_gb=java_heap_gb,
        java_bin=java_bin,
        top_k_transcripts=top_k_transcripts,
        clinical_tissue=clinical_tissue,
        keep_raw_vep=keep_raw_vep,
        dry_run=dry_run,
    )
    cmd = _build_full_cmd(req, output_dir_path)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    write_status(
        job_id,
        status="queued",
        step="full_pipeline",
        created_at=now_iso(),
        request=req.model_dump(),
        command=cmd,
        output_dir=str(output_dir_path),
        original_filename=input_vcf.filename or "",
    )
    background_tasks.add_task(
        run_command,
        job_id, cmd, output_dir_path,
        step="full_pipeline",
        log_name="pipeline.log",
        cwd=ROOT,
    )
    return JobResponse(job_id=job_id, status="queued", status_url=f"/api/v1/jobs/{job_id}", output_dir=str(output_dir_path))
