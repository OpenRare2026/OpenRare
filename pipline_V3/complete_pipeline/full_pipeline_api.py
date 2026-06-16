#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = ROOT / "complete_pipeline" / "run_full_pipeline.sh"
JOBS_DIR = Path(os.getenv("FULL_PIPELINE_API_JOBS_DIR", ROOT / "complete_pipeline" / "api_jobs"))
DEFAULT_REF_DIR = Path(os.getenv("FULL_PIPELINE_REF_DIR", "/mnt/workspace/changan/1kgp/beagle_pipeline_param/packages/CHN_ref"))
DEFAULT_BEAGLE_JAR = Path(os.getenv("FULL_PIPELINE_BEAGLE_JAR", "/mnt/workspace/changan/1kgp/beagle.27Feb25.75f.jar"))
DEFAULT_CCRE_BED = ROOT / "modules" / "vcf_preprocessing" / "resources" / "regulatory" / "hg38" / "encode_screen_v4_grch38_ccre.slim.bed.gz"
DEFAULT_NCRNA_BED = ROOT / "modules" / "vcf_preprocessing" / "resources" / "ncrna" / "hg38" / "gencode.v49.ncrna_gene.slim.bed.gz"
DEFAULT_PSEUDOGENE_SCRIPT = ROOT / "modules" / "pseudogene_annotation" / "scripts" / "annotate_pseudogene.py"

JOBS_DIR.mkdir(parents=True, exist_ok=True)
_LOCK = threading.Lock()

app = FastAPI(title="OpenRare V3 Simplified Pipeline API", version="0.1.0")


class RunRequest(BaseModel):
    input_vcf: str = Field(..., description="Input VCF/VCF.GZ absolute path or path relative to current API cwd")
    output_dir: Optional[str] = Field(None, description="Output directory; default is api_jobs/<job_id>/output")
    fork: int = Field(1, description="VEP fork count, default: 1")
    hpo_id: str = Field("", description="Optional patient HPO ID(s), e.g. HP:0001250 or comma-separated IDs")

    # Advanced overrides. Leave unset for the curated V3 defaults in run_full_pipeline.sh.
    sample_id: Optional[str] = Field(None, description="Advanced override: Sample ID, or auto")
    chromosomes: Optional[str] = Field(None, description="Advanced override: Chromosome spec, e.g. 22, 1-22, 1,3,5")
    ref_dir: Optional[str] = Field(None, description="Advanced override: CHN reference panel directory")
    beagle_jar: Optional[str] = Field(None, description="Advanced override: Beagle jar path")
    ccre_bed: Optional[str] = Field(None, description="Advanced override: cCRE BED.GZ")
    ncrna_bed: Optional[str] = Field(None, description="Advanced override: ncRNA BED.GZ")
    chr_jobs: Optional[int] = Field(None, description="Advanced override: concurrent chromosomes for phasing")
    beagle_threads: Optional[int] = Field(None, description="Advanced override: threads per Beagle process")
    java_heap_gb: Optional[int] = Field(None, description="Advanced override: Java heap per Beagle process")
    java_bin: Optional[str] = Field(None, description="Advanced override: Java executable for Beagle")
    top_k_transcripts: Optional[int] = Field(None, description="Advanced override: transcript selection count")
    clinical_tissue: str = Field("", description="Advanced override: GTEx tissue name for phenotype-aware transcript expression")
    keep_raw_vep: Optional[bool] = Field(None, description="Advanced override: keep raw VEP TSV")
    dry_run: bool = False


class RunResponse(BaseModel):
    job_id: str
    status: str
    status_url: str
    output_dir: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def status_path(job_id: str) -> Path:
    return JOBS_DIR / job_id / "status.json"


def read_status(job_id: str) -> dict:
    path = status_path(job_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="job_id not found")
    return json.loads(path.read_text(encoding="utf-8"))


def write_status(job_id: str, **updates) -> dict:
    with _LOCK:
        path = status_path(job_id)
        data = {}
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("job_id", job_id)
        data.update(updates)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
        return data


def safe_upload_name(filename: str | None) -> str:
    name = Path(filename or "input.vcf").name
    name = name.replace("/", "_").replace("\\", "_")
    if not name or name in {".", ".."}:
        name = "input.vcf"
    return name


def normalize_hpo_ids(raw: str) -> str:
    tokens = re.split(r"[\s,;]+", raw.strip())
    return ",".join(token for token in tokens if token)


def read_hpo_upload(upload: UploadFile | None) -> str:
    if upload is None:
        return ""
    data = upload.file.read()
    return normalize_hpo_ids(data.decode("utf-8", errors="replace"))


def save_upload(upload: UploadFile, upload_dir: Path) -> Path:
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / safe_upload_name(upload.filename)
    if target.exists():
        stem = target.stem
        suffix = ''.join(target.suffixes) or target.suffix
        if suffix and stem.endswith(suffix):
            stem = stem[: -len(suffix)]
        target = upload_dir / f"{stem}.{uuid.uuid4().hex[:8]}{suffix}"
    with target.open("wb") as dst:
        shutil.copyfileobj(upload.file, dst)
    return target.resolve()


def build_command(req: RunRequest, output_dir: Path) -> list[str]:
    input_vcf = resolve_path(req.input_vcf)
    cmd = [
        "bash",
        str(RUN_SCRIPT),
        "--input-vcf",
        str(input_vcf),
        "--out-dir",
        str(output_dir),
        "--fork",
        str(req.fork),
    ]

    def add_option(name: str, value) -> None:
        if value is None or value == "":
            return
        cmd.extend([name, str(value)])

    add_option("--hpo-id", req.hpo_id)
    add_option("--sample-id", req.sample_id)
    add_option("--chromosomes", req.chromosomes)
    add_option("--ref-dir", resolve_path(req.ref_dir) if req.ref_dir else None)
    add_option("--beagle-jar", resolve_path(req.beagle_jar) if req.beagle_jar else None)
    add_option("--ccre-bed", resolve_path(req.ccre_bed) if req.ccre_bed else None)
    add_option("--ncrna-bed", resolve_path(req.ncrna_bed) if req.ncrna_bed else None)
    add_option("--chr-jobs", req.chr_jobs)
    add_option("--beagle-threads", req.beagle_threads)
    add_option("--java-heap-gb", req.java_heap_gb)
    add_option("--java-bin", resolve_path(req.java_bin) if req.java_bin else None)
    add_option("--top-k-transcripts", req.top_k_transcripts)
    add_option("--clinical-tissue", req.clinical_tissue)
    if req.keep_raw_vep is not None:
        cmd.extend(["--keep-raw-vep", "yes" if req.keep_raw_vep else "no"])
    if req.dry_run:
        cmd.append("--dry-run")
    return cmd


def run_job(job_id: str, cmd: list[str], output_dir: Path) -> None:
    log_path = JOBS_DIR / job_id / "api_run.log"
    write_status(job_id, status="running", started_at=now_iso(), command=cmd, log=str(log_path))
    try:
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.run(cmd, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT, text=True)
        summary_path = output_dir / "full_pipeline.outputs.tsv"
        summary = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else ""
        if proc.returncode != 0:
            raise RuntimeError(f"pipeline failed with exit code {proc.returncode}")
        write_status(
            job_id,
            status="succeeded",
            finished_at=now_iso(),
            returncode=proc.returncode,
            output_dir=str(output_dir),
            summary_path=str(summary_path),
            summary=summary,
        )
    except Exception as exc:
        write_status(job_id, status="failed", finished_at=now_iso(), error=str(exc), output_dir=str(output_dir))


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "root": str(ROOT),
        "run_script": str(RUN_SCRIPT),
        "run_script_exists": RUN_SCRIPT.is_file(),
        "minimal_required_request_fields": ["input_vcf"],
        "common_optional_request_fields": ["output_dir", "fork", "hpo_id"],
        "endpoints": {"json_path_request": "/run", "multipart_file_upload": "/run-upload"},
        "script_defaults": {
            "sample_id": "auto",
            "chromosomes": "1-22",
            "ref_dir": str(DEFAULT_REF_DIR),
            "beagle_jar": str(DEFAULT_BEAGLE_JAR),
            "java_bin": "/mnt/workspace/pangjiangshuan/vep_runner/envs/vep/lib/jvm/bin/java",
            "chr_jobs": 1,
            "beagle_threads": 4,
            "java_heap_gb": 12,
            "top_k_transcripts": 5,
            "keep_raw_vep": "yes",
        },
        "default_ref_dir_exists": DEFAULT_REF_DIR.is_dir(),
        "default_beagle_jar_exists": DEFAULT_BEAGLE_JAR.is_file(),
        "default_ccre_bed_exists": DEFAULT_CCRE_BED.is_file(),
        "default_ncrna_bed_exists": DEFAULT_NCRNA_BED.is_file(),
        "pseudogene_script_exists": DEFAULT_PSEUDOGENE_SCRIPT.is_file(),
        "jobs_dir": str(JOBS_DIR),
    }


def enqueue_run(
    req: RunRequest,
    background_tasks: BackgroundTasks,
    *,
    job_id: str | None = None,
    extra_status: dict | None = None,
) -> RunResponse:
    if not RUN_SCRIPT.is_file():
        raise HTTPException(status_code=500, detail=f"run script not found: {RUN_SCRIPT}")
    job_id = job_id or uuid.uuid4().hex
    job_dir = JOBS_DIR / job_id
    output_dir = resolve_path(req.output_dir) if req.output_dir else job_dir / "output"
    job_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = build_command(req, output_dir)
    status_payload = {
        "status": "queued",
        "created_at": now_iso(),
        "request": req.dict(),
        "command": cmd,
        "output_dir": str(output_dir),
    }
    if extra_status:
        status_payload.update(extra_status)
    write_status(job_id, **status_payload)
    background_tasks.add_task(run_job, job_id, cmd, output_dir)
    return RunResponse(job_id=job_id, status="queued", status_url=f"/jobs/{job_id}", output_dir=str(output_dir))


@app.post("/run", response_model=RunResponse, status_code=202)
def submit(req: RunRequest, background_tasks: BackgroundTasks) -> RunResponse:
    return enqueue_run(req, background_tasks)


@app.post("/run-upload", response_model=RunResponse, status_code=202)
def submit_upload(
    background_tasks: BackgroundTasks,
    input_vcf: UploadFile = File(..., description="Upload input VCF/VCF.GZ file"),
    output_dir: Optional[str] = Form(None),
    fork: int = Form(1),
    hpo_id: str = Form(""),
    hpo_file: UploadFile | None = File(None, description="Optional TXT file containing HPO IDs; one per line or separated by comma/space/semicolon"),
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
) -> RunResponse:
    job_id = uuid.uuid4().hex
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=False)
    uploaded_path = save_upload(input_vcf, job_dir / "input")
    hpo_from_file = read_hpo_upload(hpo_file)
    merged_hpo_id = normalize_hpo_ids(",".join(x for x in [hpo_id, hpo_from_file] if x))
    req = RunRequest(
        input_vcf=str(uploaded_path),
        output_dir=output_dir,
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
    return enqueue_run(
        req,
        background_tasks,
        job_id=job_id,
        extra_status={
            "request_type": "multipart_upload",
            "uploaded_input_vcf": str(uploaded_path),
            "original_filename": input_vcf.filename or "",
            "content_type": input_vcf.content_type or "",
            "hpo_file_filename": hpo_file.filename if hpo_file else "",
            "hpo_id_merged": merged_hpo_id,
        },
    )


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    return read_status(job_id)


@app.get("/jobs/{job_id}/log")
def get_job_log(job_id: str) -> str:
    status = read_status(job_id)
    log_path = Path(status.get("log", JOBS_DIR / job_id / "api_run.log"))
    if not log_path.is_file():
        raise HTTPException(status_code=404, detail="log not found")
    return log_path.read_text(encoding="utf-8", errors="replace")
