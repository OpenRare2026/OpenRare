#!/usr/bin/env python3
"""FastAPI wrapper for HGNC-backed pseudogene annotation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse


WORK_DIR = Path(__file__).resolve().parent
RUN_ROOT = WORK_DIR / "api_runs"
ANNOTATION_SCRIPT = WORK_DIR / "annotate_pseudogene.py"
MODULE_README = WORK_DIR / "README_pseudogene_anno_module.md"

OUTPUT_VCF = "pseudogene_annotated.vcf"
OUTPUT_LOG_JSON = "pseudogene_annotation.log.json"
ALLOWED_OUTPUTS = {
    "README_pseudogene_anno_module.md",
    OUTPUT_VCF,
    OUTPUT_LOG_JSON,
}

app = FastAPI(title="Pseudogene Annotation API", version="1.0")
executor = ThreadPoolExecutor(max_workers=1)


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def run_dir(uid: str) -> Path:
    return RUN_ROOT / uid


def inputs_dir(uid: str) -> Path:
    return run_dir(uid) / "inputs"


def outputs_dir(uid: str) -> Path:
    return run_dir(uid) / "outputs"


def status_path(uid: str) -> Path:
    return run_dir(uid) / "status.json"


def log_path(uid: str) -> Path:
    return run_dir(uid) / "run.log"


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HTTPException(status_code=404, detail="uid not found")
    return json.loads(path.read_text())


def tail_log(uid: str, limit: int = 80) -> list[str]:
    path = log_path(uid)
    if not path.exists():
        return []
    return path.read_text(errors="replace").splitlines()[-limit:]


def output_file_urls(uid: str) -> list[dict[str, str]]:
    outdir = outputs_dir(uid)
    return [
        {"name": name, "url": f"/runs/{uid}/files/{name}"}
        for name in sorted(ALLOWED_OUTPUTS)
        if (outdir / name).exists()
    ]


def update_status(uid: str, **fields: Any) -> dict[str, Any]:
    path = status_path(uid)
    current = json.loads(path.read_text()) if path.exists() else {"uid": uid}
    current.update(fields)
    current["updated_at"] = utc_now()
    current["log_tail"] = tail_log(uid)
    current["files"] = (
        output_file_urls(uid) if current.get("status") == "completion" else []
    )
    atomic_write_json(path, current)
    return current


def safe_filename(filename: str | None, fallback: str) -> str:
    name = Path(filename or fallback).name.strip()
    return name or fallback


def save_upload(upload: UploadFile, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as out:
        shutil.copyfileobj(upload.file, out)


def write_log(uid: str, line: str) -> None:
    path = log_path(uid)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(line.rstrip("\n") + "\n")


def load_annotation_summary(log_json: Path) -> dict[str, Any]:
    if not log_json.exists():
        return {}
    data = json.loads(log_json.read_text())
    return data.get("annotation", {})


def run_annotation_job(uid: str, input_vcf: Path) -> None:
    update_status(
        uid,
        status="queuing",
        phase="running",
        message="Pseudogene annotation job started",
        started_at=utc_now(),
    )
    outdir = outputs_dir(uid)
    outdir.mkdir(parents=True, exist_ok=True)

    if MODULE_README.exists():
        shutil.copy2(MODULE_README, outdir / MODULE_README.name)

    output_vcf = outdir / OUTPUT_VCF
    output_log_json = outdir / OUTPUT_LOG_JSON
    cmd = [
        sys.executable,
        str(ANNOTATION_SCRIPT),
        "--input",
        str(input_vcf),
        "--output",
        str(output_vcf),
        "--log-json",
        str(output_log_json),
    ]
    write_log(uid, "Command: " + " ".join(cmd))
    with log_path(uid).open("a") as log_handle:
        proc = subprocess.run(
            cmd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    if proc.returncode != 0:
        update_status(
            uid,
            status="failure",
            phase="failed",
            message=f"Annotation job failed with exit code {proc.returncode}",
            finished_at=utc_now(),
        )
        return

    summary = load_annotation_summary(output_log_json)
    update_status(
        uid,
        status="completion",
        phase="completed",
        message="Pseudogene annotation job completed",
        finished_at=utc_now(),
        summary=summary,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "pseudogene_annotation"}


@app.post("/runs")
def create_run(
    file: UploadFile | None = File(default=None),
    hpo_file: UploadFile | None = File(default=None),
    input_path: str | None = Form(default=None),
    hpo_list: str | None = Form(default=None),
    hgvs: bool | None = Form(default=None),
) -> dict[str, Any]:
    if file is None and not input_path:
        raise HTTPException(
            status_code=400,
            detail="Provide either multipart file=@... or form field input_path.",
        )

    uid = uuid.uuid4().hex
    in_dir = inputs_dir(uid)
    in_dir.mkdir(parents=True, exist_ok=True)

    if file is not None:
        filename = safe_filename(file.filename, "input.vcf")
        input_vcf = in_dir / filename
        save_upload(file, input_vcf)
        input_mode = "upload"
    else:
        source = Path(str(input_path)).expanduser()
        if not source.exists() or not source.is_file():
            raise HTTPException(status_code=400, detail=f"input_path not found: {source}")
        input_vcf = in_dir / source.name
        shutil.copy2(source, input_vcf)
        input_mode = "server_path"

    compat_options = {
        "hpo_file_received": hpo_file is not None,
        "hpo_list_received": bool(hpo_list),
        "hgvs": hgvs,
        "note": "hpo_file, hpo_list, and hgvs are accepted for curl compatibility but ignored by pseudogene annotation.",
    }

    atomic_write_json(
        status_path(uid),
        {
            "uid": uid,
            "status": "queuing",
            "phase": "queued",
            "message": "Job queued",
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "input_mode": input_mode,
            "input_file": str(input_vcf),
            "compat_options": compat_options,
            "status_url": f"/runs/{uid}",
            "files_url": f"/runs/{uid}/files",
            "files": [],
            "log_tail": [],
        },
    )
    executor.submit(run_annotation_job, uid, input_vcf)
    return read_json(status_path(uid))


@app.get("/runs/{uid}")
def get_run(uid: str) -> dict[str, Any]:
    return read_json(status_path(uid))


@app.get("/runs/{uid}/files")
def list_files(uid: str) -> dict[str, Any]:
    status = read_json(status_path(uid))
    return {
        "uid": uid,
        "status": status.get("status"),
        "files": output_file_urls(uid),
    }


@app.get("/runs/{uid}/files/{filename}")
def download_file(uid: str, filename: str) -> FileResponse:
    name = Path(filename).name
    if name not in ALLOWED_OUTPUTS:
        raise HTTPException(status_code=404, detail="file not allowed")
    path = outputs_dir(uid) / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path, filename=name)
