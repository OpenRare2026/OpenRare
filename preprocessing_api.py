#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


BASE_WORKDIR = Path(os.environ.get("PREPROCESS_API_BASE_WORKDIR", "/mnt/workspace/wangzilu1")).resolve()
PROJECT_DIR = Path(os.environ.get("PREPROCESS_API_PROJECT_DIR", str(BASE_WORKDIR / "OpenRare"))).resolve()
RUN_SCRIPT = PROJECT_DIR / "前置VCF处理.sh"
DEFAULT_OUT_DIR = PROJECT_DIR / "results/preprocess/api"
DEFAULT_CCRE_BED = PROJECT_DIR / "regulatory_annotation/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz"
DEFAULT_NCRNA_BED = PROJECT_DIR / "regulatory_annotation/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz"
SAFE_PREFIX_RE = re.compile(r"^[A-Za-z0-9._/\-]+$")


class PreprocessRequest(BaseModel):
    input_vcf: str = Field(..., description="VCF path, absolute or relative to base workdir")
    output_prefix: str | None = Field(None, description="Output prefix, absolute or relative to base workdir")
    sample: str | None = Field(None, description="Optional sample name for FORMAT/AD VAF calculation")
    ccre_bed: str | None = Field(None, description="Optional cCRE BED.gz path")
    ncrna_bed: str | None = Field(None, description="Optional GENCODE ncRNA BED.gz path")


class PreprocessResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    input_vcf: str
    output_prefix: str
    sample: str | None = None
    vaf_vcf: str
    vaf_index: str
    vaf_summary: str
    output_vcf: str
    output_index: str
    regulatory_summary: str
    ncrna_summary: str


class JobStatus(PreprocessResponse):
    created_at: str
    updated_at: str
    command: list[str]
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""


app = FastAPI(
    title="OpenRare VCF Preprocessing API",
    version="1.0.0",
    description="Run VAF INFO annotation followed by CRE and ncRNA annotation for hg38 VCF files.",
)

jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def resolve_path(value: str, *, must_exist: bool = False) -> Path:
    if not value or "\x00" in value:
        raise HTTPException(status_code=400, detail="Invalid path")
    if not SAFE_PREFIX_RE.match(value):
        raise HTTPException(status_code=400, detail="Path contains unsupported characters")
    raw = Path(value)
    if any(part == ".." for part in raw.parts):
        raise HTTPException(status_code=400, detail="Path traversal using .. is not allowed")
    path = raw if raw.is_absolute() else BASE_WORKDIR / raw
    path = path.resolve()
    if must_exist and not path.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    return path


def input_stem(path: Path) -> str:
    name = path.name
    for suffix in (".vcf.gz", ".vcf"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return path.stem


def tail(text: str, limit: int = 6000) -> str:
    return text[-limit:]


def set_job(job_id: str, **updates) -> None:
    with jobs_lock:
        jobs[job_id].update(updates)
        jobs[job_id]["updated_at"] = now()


def run_job(job_id: str) -> None:
    with jobs_lock:
        job = dict(jobs[job_id])
    set_job(job_id, status="running")
    try:
        proc = subprocess.run(
            job["command"],
            cwd=str(PROJECT_DIR),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        set_job(
            job_id,
            status="succeeded" if proc.returncode == 0 else "failed",
            returncode=proc.returncode,
            stdout_tail=tail(proc.stdout),
            stderr_tail=tail(proc.stderr),
        )
    except Exception as exc:
        set_job(job_id, status="failed", returncode=None, stderr_tail=repr(exc))


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "base_workdir": str(BASE_WORKDIR),
        "project_dir": str(PROJECT_DIR),
        "run_script_exists": RUN_SCRIPT.exists(),
        "default_ccre_bed_exists": DEFAULT_CCRE_BED.exists(),
        "default_ncrna_bed_exists": DEFAULT_NCRNA_BED.exists(),
    }


@app.post("/preprocess", response_model=PreprocessResponse)
def preprocess(req: PreprocessRequest) -> PreprocessResponse:
    input_vcf = resolve_path(req.input_vcf, must_exist=True)
    ccre_bed = resolve_path(req.ccre_bed, must_exist=True) if req.ccre_bed else DEFAULT_CCRE_BED
    ncrna_bed = resolve_path(req.ncrna_bed, must_exist=True) if req.ncrna_bed else DEFAULT_NCRNA_BED

    if not RUN_SCRIPT.exists():
        raise HTTPException(status_code=500, detail=f"Missing runner script: {RUN_SCRIPT}")
    if not ccre_bed.exists():
        raise HTTPException(status_code=500, detail=f"Missing cCRE BED: {ccre_bed}")
    if not ncrna_bed.exists():
        raise HTTPException(status_code=500, detail=f"Missing ncRNA BED: {ncrna_bed}")

    job_id = uuid.uuid4().hex[:12]
    if req.output_prefix:
        output_prefix = resolve_path(req.output_prefix, must_exist=False)
    else:
        DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
        output_prefix = DEFAULT_OUT_DIR / f"{input_stem(input_vcf)}.{job_id}"
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    sample = req.sample or ""
    command = [str(RUN_SCRIPT), str(input_vcf), str(output_prefix), sample, str(ccre_bed), str(ncrna_bed)]
    job = {
        "job_id": job_id,
        "status": "queued",
        "created_at": now(),
        "updated_at": now(),
        "input_vcf": str(input_vcf),
        "output_prefix": str(output_prefix),
        "sample": req.sample,
        "vaf_vcf": f"{output_prefix}.vaf.vcf.gz",
        "vaf_index": f"{output_prefix}.vaf.vcf.gz.tbi",
        "vaf_summary": f"{output_prefix}.vaf.summary.txt",
        "output_vcf": f"{output_prefix}.regulatory.vcf.gz",
        "output_index": f"{output_prefix}.regulatory.vcf.gz.tbi",
        "regulatory_summary": f"{output_prefix}.regulatory.summary.tsv",
        "ncrna_summary": f"{output_prefix}.ncrna.summary.tsv",
        "command": command,
        "returncode": None,
        "stdout_tail": "",
        "stderr_tail": "",
    }
    with jobs_lock:
        jobs[job_id] = job
    thread = threading.Thread(target=run_job, args=(job_id,), daemon=True)
    thread.start()
    return PreprocessResponse(**job)


@app.get("/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str) -> JobStatus:
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**job)
