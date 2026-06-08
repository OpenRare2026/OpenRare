from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel


RUNNER_DIR = Path(__file__).resolve().parents[1]
RUNNER_SCRIPT = RUNNER_DIR / "bin" / "run_vep_to_csv.py"
CONFIG_PATH = RUNNER_DIR / "config" / "vep_runner_config.json"
GTEX_QUERY_PYTHON = RUNNER_DIR / "envs" / "gtex_query" / "bin" / "python"


def configured_job_dir() -> Path:
    raw = Path(os.environ.get("VEP_API_JOB_DIR", "api_jobs"))
    if not raw.is_absolute():
        raw = RUNNER_DIR / raw
    return raw.resolve()


JOB_DIR = configured_job_dir()
MAX_UPLOAD_BYTES = int(os.environ.get("VEP_API_MAX_UPLOAD_BYTES", str(1024 * 1024 * 1024)))
RUN_TIMEOUT_SECONDS = int(os.environ.get("VEP_API_RUN_TIMEOUT_SECONDS", "0"))
ALLOWED_PLUGINS = {"cadd", "spliceai", "alphamissense", "dbnsfp", "loftee", "clinvar"}
JOB_ID_RE = re.compile(r"^[0-9a-f]{32}$")
FORMAT_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
PUBLIC_STATUS_BY_INTERNAL_STATUS = {
    "queued": "queuing",
    "running": "queuing",
    "succeeded": "completion",
    "failed": "failure",
    "queuing": "queuing",
    "completion": "completion",
    "failure": "failure",
}

app = FastAPI(
    title="VEP Runner API",
    description="HTTP wrapper around the bundled offline VEP runner.",
    version="1.0.0",
)


class RunResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    updated_at: str
    input_filename: str
    input_bytes: int
    options: dict[str, Any]
    status_url: str
    result_url: str
    log_url: str
    result_path: str
    rows: int | None = None
    error: str | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def job_path(job_id: str) -> Path:
    if not JOB_ID_RE.fullmatch(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return JOB_DIR / job_id


def status_path(job_id: str) -> Path:
    return job_path(job_id) / "status.json"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def read_status(job_id: str) -> dict[str, Any]:
    path = status_path(job_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(path.read_text())


def update_status(job_id: str, **changes: Any) -> dict[str, Any]:
    status = read_status(job_id)
    status.update(changes)
    status["updated_at"] = now_iso()
    write_json(status_path(job_id), status)
    return status


def public_status(status: dict[str, Any], base_url: str | None = None) -> dict[str, Any]:
    job_id = status["job_id"]
    prefix = base_url.rstrip("/") if base_url else ""
    status = dict(status)
    status["status"] = PUBLIC_STATUS_BY_INTERNAL_STATUS.get(status.get("status"), status.get("status"))
    status["status_url"] = f"{prefix}/runs/{job_id}"
    status["result_url"] = f"{prefix}/runs/{job_id}/result"
    status["log_url"] = f"{prefix}/runs/{job_id}/log"
    status["result_path"] = str(job_path(job_id) / "output.csv")
    return status


def safe_filename(filename: str | None) -> str:
    name = Path(filename or "input.vcf").name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or "input.vcf"


def parse_disabled_plugins(value: str) -> list[str]:
    plugins = [item.strip().lower() for item in value.split(",") if item.strip()]
    invalid = sorted(set(plugins) - ALLOWED_PLUGINS)
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported plugin(s): {', '.join(invalid)}",
        )
    return plugins


def validate_input_format(value: str) -> str:
    if not value or not FORMAT_RE.fullmatch(value):
        raise HTTPException(status_code=400, detail="Invalid VEP input format")
    return value


async def save_upload(upload: UploadFile, path: Path) -> int:
    total = 0
    with path.open("wb") as handle:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                handle.close()
                path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Uploaded file is too large")
            handle.write(chunk)
    if total == 0:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    return total


def count_csv_rows(path: Path) -> int:
    with path.open() as handle:
        return max(0, sum(1 for _ in handle) - 1)


def tail_text(value: str, limit: int = 4000) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[-limit:]


def run_vep_job(job_id: str) -> None:
    status = read_status(job_id)
    directory = job_path(job_id)
    input_path = directory / status["input_filename"]
    output_path = directory / "output.csv"
    vep_log_path = directory / "vep.log"
    wrapper_log_path = directory / "wrapper.log"
    raw_vep_path = directory / "raw_vep.txt"
    options = status["options"]

    cmd = [
        str(GTEX_QUERY_PYTHON if GTEX_QUERY_PYTHON.is_file() else sys.executable),
        str(RUNNER_SCRIPT),
        "-i",
        str(input_path),
        "-o",
        str(output_path),
        "--format",
        options["format"],
        "--fork",
        str(options["fork"]),
        "--log",
        str(vep_log_path),
    ]
    if options["hgvs"]:
        cmd.append("--hgvs")
    if options["no_pick"]:
        cmd.append("--no-pick")
    if options.get("no_transcript_selection"):
        cmd.append("--no-transcript-selection")
    cmd += ["--top-k-transcripts", str(options.get("top_k_transcripts", 5))]
    if options.get("clinical_tissue"):
        cmd += ["--clinical-tissue", options["clinical_tissue"]]
    if options.get("hpo_id"):
        cmd += ["--hpo-id", options["hpo_id"]]
    if options.get("top_n_hpo_tissues"):
        cmd += ["--top-n-hpo-tissues", str(options["top_n_hpo_tissues"])]
    if options["keep_raw_vep"]:
        cmd += ["--keep-vep", str(raw_vep_path)]
    for plugin in options["disable_plugins"]:
        cmd += ["--disable-plugin", plugin]

    update_status(job_id, status="running", command=cmd, started_at=now_iso())
    try:
        result = subprocess.run(
            cmd,
            cwd=str(RUNNER_DIR),
            text=True,
            capture_output=True,
            timeout=RUN_TIMEOUT_SECONDS or None,
        )
        wrapper_log_path.write_text((result.stdout or "") + (result.stderr or ""))
        if result.returncode != 0:
            message = tail_text(wrapper_log_path.read_text())
            update_status(job_id, status="failed", error=message or f"VEP exited with {result.returncode}")
            return
        rows = count_csv_rows(output_path)
        update_status(job_id, status="succeeded", rows=rows, completed_at=now_iso())
    except subprocess.TimeoutExpired as exc:
        update_status(job_id, status="failed", error=f"VEP timed out after {exc.timeout} seconds")
    except Exception as exc:
        update_status(job_id, status="failed", error=str(exc))


def result_response(job_id: str) -> FileResponse:
    path = job_path(job_id) / "output.csv"
    return FileResponse(path, media_type="text/csv", filename=f"{job_id}.vep.csv")


def result_not_ready_response(job_id: str, request: Request, status_code: int = 202) -> JSONResponse:
    status = public_status(read_status(job_id), base_url=str(request.base_url))
    status["message"] = (
        "VEP result is not ready yet. Poll this same result_url later; when the job "
        "succeeds this endpoint returns the CSV file directly."
    )
    status["retry_after_seconds"] = 10
    return JSONResponse(status, status_code=status_code, headers={"Retry-After": "10"})


@app.on_event("startup")
def startup() -> None:
    JOB_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "vep-runner-api",
        "docs": "/docs",
        "submit": "/runs",
        "jobs": str(JOB_DIR),
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "runner_script": str(RUNNER_SCRIPT),
        "runner_script_exists": RUNNER_SCRIPT.is_file(),
        "config": str(CONFIG_PATH),
        "config_exists": CONFIG_PATH.is_file(),
        "job_dir": str(JOB_DIR),
    }


@app.post("/runs", response_model=RunResponse, status_code=202)
async def submit_run(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    hgvs: bool = Form(True),
    no_pick: bool = Form(False),
    no_transcript_selection: bool = Form(False),
    top_k_transcripts: int = Form(5),
    clinical_tissue: str = Form(""),
    hpo_id: str = Form(""),
    top_n_hpo_tissues: int = Form(3),
    format: str = Form("vcf"),
    fork: int = Form(1),
    disable_plugins: str = Form(""),
    keep_raw_vep: bool = Form(False),
) -> dict[str, Any]:
    if not RUNNER_SCRIPT.is_file():
        raise HTTPException(status_code=500, detail=f"Runner script not found: {RUNNER_SCRIPT}")
    if fork < 1:
        raise HTTPException(status_code=400, detail="fork must be >= 1")
    if top_k_transcripts < 1:
        raise HTTPException(status_code=400, detail="top_k_transcripts must be >= 1")
    if top_n_hpo_tissues < 1:
        raise HTTPException(status_code=400, detail="top_n_hpo_tissues must be >= 1")
    input_format = validate_input_format(format)
    disabled_plugins = parse_disabled_plugins(disable_plugins)

    job_id = uuid.uuid4().hex
    directory = job_path(job_id)
    directory.mkdir(parents=True, exist_ok=False)
    input_filename = safe_filename(file.filename)
    input_path = directory / input_filename
    input_bytes = await save_upload(file, input_path)

    created_at = now_iso()
    status = {
        "job_id": job_id,
        "status": "queued",
        "created_at": created_at,
        "updated_at": created_at,
        "input_filename": input_filename,
        "input_bytes": input_bytes,
        "options": {
            "hgvs": hgvs,
            "no_pick": no_pick,
            "no_transcript_selection": no_transcript_selection,
            "top_k_transcripts": top_k_transcripts,
            "clinical_tissue": clinical_tissue,
            "hpo_id": hpo_id,
            "top_n_hpo_tissues": top_n_hpo_tissues,
            "format": input_format,
            "fork": fork,
            "disable_plugins": disabled_plugins,
            "keep_raw_vep": keep_raw_vep,
        },
        "rows": None,
        "error": None,
    }
    write_json(status_path(job_id), status)
    background_tasks.add_task(run_vep_job, job_id)
    return public_status(status, base_url=str(request.base_url))


@app.get("/runs/{job_id}", response_model=RunResponse)
def get_run(request: Request, job_id: str) -> dict[str, Any]:
    return public_status(read_status(job_id), base_url=str(request.base_url))


@app.get("/runs/{job_id}/result", response_model=None)
def download_result(request: Request, job_id: str) -> FileResponse | JSONResponse:
    status = read_status(job_id)
    if status["status"] == "failed":
        payload = public_status(status, base_url=str(request.base_url))
        payload["message"] = "VEP failed. Check log_url for details."
        return JSONResponse(payload, status_code=500)
    if status["status"] != "succeeded":
        return result_not_ready_response(job_id, request)
    if not (job_path(job_id) / "output.csv").is_file():
        raise HTTPException(status_code=404, detail="Result CSV not found")
    return result_response(job_id)


@app.get("/runs/{job_id}/log")
def get_log(job_id: str) -> PlainTextResponse:
    read_status(job_id)
    directory = job_path(job_id)
    parts = []
    for path in [directory / "wrapper.log", directory / "vep.log"]:
        if path.is_file():
            parts.append(f"### {path.name}\n{path.read_text()}")
    return PlainTextResponse("\n\n".join(parts) if parts else "No log yet.\n")
