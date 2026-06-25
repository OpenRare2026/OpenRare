#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from config.path_utils import (
    full_pipeline_beagle_jar,
    full_pipeline_genos_evee_db,
    full_pipeline_ref_dir,
)

RUN_SCRIPT = ROOT / "scripts" / "run_full_pipeline.sh"
JOBS_DIR = Path(os.getenv("FULL_PIPELINE_API_JOBS_DIR", ROOT / "complete_pipeline" / "api_jobs"))
DEFAULT_REF_DIR = full_pipeline_ref_dir()
DEFAULT_BEAGLE_JAR = full_pipeline_beagle_jar()
DEFAULT_GENOS_EVEE_DB = full_pipeline_genos_evee_db()
DEFAULT_CCRE_BED = ROOT / "modules" / "vcf_preprocessing" / "resources" / "regulatory" / "hg38" / "encode_screen_v4_grch38_ccre.slim.bed.gz"
DEFAULT_NCRNA_BED = ROOT / "modules" / "vcf_preprocessing" / "resources" / "ncrna" / "hg38" / "gencode.v49.ncrna_gene.slim.bed.gz"
DEFAULT_PSEUDOGENE_SCRIPT = ROOT / "modules" / "pseudogene_annotation" / "scripts" / "annotate_pseudogene.py"
DEFAULT_JAVA_BIN = os.getenv("JAVA_BIN", "java")

JOBS_DIR.mkdir(parents=True, exist_ok=True)
_LOCK = threading.Lock()
_QUEUE_CONDITION = threading.Condition()
_PENDING_JOBS: deque[dict] = deque()
_CURRENT_JOB_ID: str | None = None
_WORKER_THREAD: threading.Thread | None = None


class RunRequest(BaseModel):
    input_vcf: str = Field(..., description="Input VCF/VCF.GZ absolute path or path relative to current API cwd")
    output_dir: Optional[str] = Field(None, description="Output directory; default is api_jobs/<job_id>/output")
    fork: int = Field(1, description="VEP fork count, default: 1")
    hpo_id: str = Field("", description="Optional patient HPO ID(s), e.g. HP:0001250 or comma-separated IDs")
    input_assembly: Optional[str] = Field(
        None,
        description="Input VCF assembly: auto, GRCh37, or GRCh38; GRCh37 triggers liftover before phasing",
    )

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
    genos_evee_db: Optional[str] = Field(None, description="Advanced override: indexed GENOS-EVEE CPRA TSV.GZ")
    keep_raw_vep: Optional[bool] = Field(None, description="Advanced override: keep raw VEP TSV")
    dry_run: bool = False


class RunResponse(BaseModel):
    job_id: str
    status: str
    status_url: str
    files_url: str
    output_dir: str
    queue_position: int


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


def queue_snapshot() -> dict:
    with _QUEUE_CONDITION:
        pending_ids = [task["job_id"] for task in _PENDING_JOBS]
        return {
            "running_job_id": _CURRENT_JOB_ID,
            "queued_job_ids": pending_ids,
            "queued_count": len(pending_ids),
        }


def queue_position(job_id: str) -> int | None:
    with _QUEUE_CONDITION:
        if job_id == _CURRENT_JOB_ID:
            return 0
        for index, task in enumerate(_PENDING_JOBS, start=1):
            if task["job_id"] == job_id:
                return index
    return None


def refresh_pending_statuses() -> None:
    with _QUEUE_CONDITION:
        pending_ids = [task["job_id"] for task in _PENDING_JOBS]
    for position, job_id in enumerate(pending_ids, start=1):
        write_status(job_id, status="queued", queue_position=position)


def enqueue_task(job_id: str, cmd: list[str], output_dir: Path) -> int:
    with _QUEUE_CONDITION:
        _PENDING_JOBS.append(
            {"job_id": job_id, "cmd": cmd, "output_dir": str(output_dir)}
        )
        position = len(_PENDING_JOBS)
        _QUEUE_CONDITION.notify()
    refresh_pending_statuses()
    return position


def recover_queue() -> None:
    recoverable: list[tuple[str, dict]] = []
    for path in JOBS_DIR.glob("*/status.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        job_id = data.get("job_id") or path.parent.name
        if data.get("status") == "running":
            write_status(
                job_id,
                status="failed",
                finished_at=now_iso(),
                error="API service restarted while this job was running; automatic process resume is not safe.",
            )
        elif data.get("status") == "queued" and data.get("command") and data.get("output_dir"):
            recoverable.append((data.get("created_at", ""), data))
    for _created_at, data in sorted(recoverable, key=lambda item: item[0]):
        enqueue_task(
            data["job_id"],
            list(data["command"]),
            Path(data["output_dir"]),
        )


def queue_worker() -> None:
    global _CURRENT_JOB_ID
    while True:
        with _QUEUE_CONDITION:
            while not _PENDING_JOBS:
                _QUEUE_CONDITION.wait()
            task = _PENDING_JOBS.popleft()
            _CURRENT_JOB_ID = task["job_id"]
        refresh_pending_statuses()
        try:
            run_job(task["job_id"], list(task["cmd"]), Path(task["output_dir"]))
        finally:
            with _QUEUE_CONDITION:
                _CURRENT_JOB_ID = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global _WORKER_THREAD
    if not (_WORKER_THREAD and _WORKER_THREAD.is_alive()):
        recover_queue()
        _WORKER_THREAD = threading.Thread(
            target=queue_worker,
            name="openrare-v3-single-worker",
            daemon=True,
        )
        _WORKER_THREAD.start()
    yield


app = FastAPI(
    title="OpenRare V3 Queued Pipeline API",
    version="0.2.0",
    lifespan=lifespan,
)


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
        suffix = "".join(target.suffixes) or target.suffix
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
    add_option("--input-assembly", req.input_assembly)
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
    add_option("--genos-evee-db", resolve_path(req.genos_evee_db) if req.genos_evee_db else None)
    if req.keep_raw_vep is not None:
        cmd.extend(["--keep-raw-vep", "yes" if req.keep_raw_vep else "no"])
    if req.dry_run:
        cmd.append("--dry-run")
    return cmd


def run_job(job_id: str, cmd: list[str], output_dir: Path) -> None:
    log_path = JOBS_DIR / job_id / "api_run.log"
    write_status(
        job_id,
        status="running",
        queue_position=0,
        started_at=now_iso(),
        command=cmd,
        log=str(log_path),
    )
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
            queue_position=None,
        )
    except Exception as exc:
        write_status(
            job_id,
            status="failed",
            queue_position=None,
            finished_at=now_iso(),
            error=str(exc),
            output_dir=str(output_dir),
        )


@app.get("/health")
def health() -> dict:
    queue = queue_snapshot()
    return {
        "status": "ok",
        "root": str(ROOT),
        "run_script": str(RUN_SCRIPT),
        "run_script_exists": RUN_SCRIPT.is_file(),
        "minimal_required_request_fields": ["input_vcf"],
        "common_optional_request_fields": ["output_dir", "fork", "hpo_id"],
        "execution": {
            "mode": "single_worker_fifo_queue",
            **queue,
        },
        "endpoints": {
            "json_path_request": "/run",
            "multipart_file_upload": "/run-upload",
            "queue": "/queue",
            "job_status": "/jobs/{job_id}",
            "job_files": "/jobs/{job_id}/files",
            "job_file_download": "/jobs/{job_id}/files/{relative_path}",
        },
        "script_defaults": {
            "sample_id": "auto",
            "chromosomes": "1-22",
            "ref_dir": str(DEFAULT_REF_DIR),
            "beagle_jar": str(DEFAULT_BEAGLE_JAR),
            "java_bin": DEFAULT_JAVA_BIN,
            "chr_jobs": 1,
            "beagle_threads": 4,
            "java_heap_gb": 12,
            "top_k_transcripts": 5,
            "keep_raw_vep": "yes",
            "genos_evee_db": str(DEFAULT_GENOS_EVEE_DB),
        },
        "default_ref_dir_exists": DEFAULT_REF_DIR.is_dir(),
        "default_beagle_jar_exists": DEFAULT_BEAGLE_JAR.is_file(),
        "default_ccre_bed_exists": DEFAULT_CCRE_BED.is_file(),
        "default_ncrna_bed_exists": DEFAULT_NCRNA_BED.is_file(),
        "pseudogene_script_exists": DEFAULT_PSEUDOGENE_SCRIPT.is_file(),
        "default_genos_evee_db_exists": DEFAULT_GENOS_EVEE_DB.is_file(),
        "default_genos_evee_db_index_exists": Path(f"{DEFAULT_GENOS_EVEE_DB}.tbi").is_file(),
        "jobs_dir": str(JOBS_DIR),
    }


def enqueue_run(
    req: RunRequest,
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
    position = enqueue_task(job_id, cmd, output_dir)
    return RunResponse(
        job_id=job_id,
        status="queued",
        status_url=f"/jobs/{job_id}",
        files_url=f"/jobs/{job_id}/files",
        output_dir=str(output_dir),
        queue_position=position,
    )


@app.post("/run", response_model=RunResponse, status_code=202)
def submit(req: RunRequest) -> RunResponse:
    return enqueue_run(req)


@app.post("/run-upload", response_model=RunResponse, status_code=202)
def submit_upload(
    input_vcf: UploadFile = File(..., description="Upload input VCF/VCF.GZ file"),
    output_dir: Optional[str] = Form(None),
    fork: int = Form(1),
    hpo_id: str = Form(""),
    input_assembly: Optional[str] = Form(None),
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
    genos_evee_db: Optional[str] = Form(None),
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
        input_assembly=input_assembly,
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
        genos_evee_db=genos_evee_db,
        keep_raw_vep=keep_raw_vep,
        dry_run=dry_run,
    )
    return enqueue_run(
        req,
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


def public_job_status(job_id: str, request: Request) -> dict:
    data = read_status(job_id)
    position = queue_position(job_id)
    if position is not None:
        data["queue_position"] = position
    data["status_url"] = str(request.url_for("get_job", job_id=job_id))
    data["files_url"] = str(request.url_for("list_job_files", job_id=job_id))
    data["api_log_download_url"] = str(
        request.url_for("download_api_log", job_id=job_id)
    )
    return data


def output_root_for_job(job_id: str) -> Path:
    status = read_status(job_id)
    output_dir = status.get("output_dir")
    if not output_dir:
        raise HTTPException(status_code=404, detail="job output directory is not available")
    root = Path(output_dir).expanduser().resolve()
    if not root.is_dir():
        raise HTTPException(status_code=404, detail="job output directory does not exist yet")
    return root


def safe_job_file(job_id: str, file_path: str) -> Path:
    root = output_root_for_job(job_id)
    candidate = (root / file_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid file path") from exc
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    return candidate


@app.get("/queue", name="get_queue")
def get_queue(request: Request) -> dict:
    snapshot = queue_snapshot()
    jobs = []
    for job_id in ([snapshot["running_job_id"]] if snapshot["running_job_id"] else []) + snapshot[
        "queued_job_ids"
    ]:
        status = read_status(job_id)
        jobs.append(
            {
                "job_id": job_id,
                "status": status.get("status"),
                "queue_position": queue_position(job_id),
                "created_at": status.get("created_at"),
                "output_dir": status.get("output_dir"),
                "status_url": str(request.url_for("get_job", job_id=job_id)),
            }
        )
    return {**snapshot, "jobs": jobs}


@app.get("/jobs/{job_id}", name="get_job")
def get_job(job_id: str, request: Request) -> dict:
    return public_job_status(job_id, request)


@app.get("/jobs/{job_id}/files", name="list_job_files")
def list_job_files(job_id: str, request: Request) -> dict:
    root = output_root_for_job(job_id)
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        stat = path.stat()
        base = str(request.base_url).rstrip("/")
        files.append(
            {
                "relative_path": relative,
                "stage": relative.split("/", 1)[0],
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(
                    stat.st_mtime, timezone.utc
                ).isoformat(),
                "download_url": f"{base}/jobs/{job_id}/files/{quote(relative, safe='/')}",
            }
        )
    return {
        "job_id": job_id,
        "status": read_status(job_id).get("status"),
        "output_dir": str(root),
        "file_count": len(files),
        "files": files,
    }


@app.get("/jobs/{job_id}/files/{file_path:path}", name="download_job_file")
def download_job_file(job_id: str, file_path: str) -> FileResponse:
    path = safe_job_file(job_id, file_path)
    return FileResponse(path, filename=path.name)


@app.get("/jobs/{job_id}/log")
def get_job_log(job_id: str) -> str:
    status = read_status(job_id)
    log_path = Path(status.get("log", JOBS_DIR / job_id / "api_run.log"))
    if not log_path.is_file():
        raise HTTPException(status_code=404, detail="log not found")
    return log_path.read_text(encoding="utf-8", errors="replace")


@app.get("/jobs/{job_id}/api-log/download", name="download_api_log")
def download_api_log(job_id: str) -> FileResponse:
    status = read_status(job_id)
    log_path = Path(status.get("log", JOBS_DIR / job_id / "api_run.log"))
    if not log_path.is_file():
        raise HTTPException(status_code=404, detail="log not found")
    return FileResponse(log_path, filename=f"{job_id}.api_run.log")
