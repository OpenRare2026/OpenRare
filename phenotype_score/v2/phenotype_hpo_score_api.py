#!/usr/bin/env python3
"""FastAPI wrapper for phenotype-HPO scoring v2."""

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
DATA_DIR = Path("/mnt/workspace/xiongliwen/00.PublicData")
RUN_ROOT = WORK_DIR / "api_runs"
DEFAULT_HPO_FILE = WORK_DIR / "hpo_test.txt"
SCORING_SCRIPT = WORK_DIR / "phenotype_hpo_score_v2.py"
MODULE_README = WORK_DIR / "README_phenotype_hpo_score_v2.md"
ALLOWED_OUTPUTS = {
    "README_phenotype_hpo_score_v2.md",
    "gene_phenotype_score.csv",
    "variant_phenotype_score.csv",
}

app = FastAPI(title="Phenotype-HPO Score v2 API", version="2.0")
executor = ThreadPoolExecutor(max_workers=1)


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def run_dir(uid: str) -> Path:
    return RUN_ROOT / uid


def status_path(uid: str) -> Path:
    return run_dir(uid) / "status.json"


def log_path(uid: str) -> Path:
    return run_dir(uid) / "run.log"


def outputs_dir(uid: str) -> Path:
    return run_dir(uid) / "outputs"


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    tmp.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HTTPException(status_code=404, detail="uid not found")
    return json.loads(path.read_text())


def tail_log(uid: str, limit: int = 80) -> list[str]:
    path = log_path(uid)
    if not path.exists():
        return []
    lines = path.read_text(errors="replace").splitlines()
    return lines[-limit:]


def output_file_urls(uid: str) -> list[dict[str, str]]:
    return [
        {"name": name, "url": f"/runs/{uid}/files/{name}"}
        for name in sorted(ALLOWED_OUTPUTS)
        if (outputs_dir(uid) / name).exists()
    ]


def update_status(uid: str, **fields: Any) -> dict[str, Any]:
    path = status_path(uid)
    current = json.loads(path.read_text()) if path.exists() else {"uid": uid}
    current.update(fields)
    current["updated_at"] = utc_now()
    current["log_tail"] = tail_log(uid)
    current["files"] = output_file_urls(uid) if current.get("status") == "completion" else []
    atomic_write_json(path, current)
    return current


def safe_filename(filename: str, fallback: str) -> str:
    name = Path(filename or fallback).name.strip()
    return name or fallback


def save_upload(upload: UploadFile, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as out:
        shutil.copyfileobj(upload.file, out)


def write_log(uid: str, line: str) -> None:
    with log_path(uid).open("a") as f:
        f.write(line.rstrip("\n") + "\n")


def run_scoring_job(
    uid: str,
    input_csv: Path,
    hpo_file: Path,
    min_similarity: float,
    max_orpha_files: int,
    hgvs: bool,
) -> None:
    update_status(
        uid,
        status="queuing",
        phase="running",
        message="Scoring job started",
        started_at=utc_now(),
    )
    outdir = outputs_dir(uid)
    outdir.mkdir(parents=True, exist_ok=True)
    if MODULE_README.exists():
        shutil.copy2(MODULE_README, outdir / MODULE_README.name)

    cmd = [
        sys.executable,
        str(SCORING_SCRIPT),
        "--input-csv",
        str(input_csv),
        "--hpo-file",
        str(hpo_file),
        "--data-dir",
        str(DATA_DIR),
        "--outdir",
        str(outdir),
        "--min-similarity",
        str(min_similarity),
    ]
    if max_orpha_files:
        cmd.extend(["--max-orpha-files", str(max_orpha_files)])

    write_log(uid, f"[api] uid={uid}")
    write_log(uid, f"[api] input_csv={input_csv}")
    write_log(uid, f"[api] hpo_file={hpo_file}")
    write_log(uid, f"[api] hgvs={hgvs}")
    write_log(uid, "[api] command=" + " ".join(cmd))

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=WORK_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            write_log(uid, line)
            clean = line.strip()
            if clean:
                update_status(uid, status="queuing", phase="running", message=clean)
        return_code = proc.wait()
        if return_code != 0:
            update_status(
                uid,
                status="failure",
                phase="failed",
                message=f"Scoring job failed with exit code {return_code}",
                exit_code=return_code,
                finished_at=utc_now(),
            )
            return

        summary_file = outdir / "run_summary.json"
        summary: dict[str, Any] = {}
        if summary_file.exists():
            summary = json.loads(summary_file.read_text())
            summary_file.unlink()

        missing = sorted(name for name in ALLOWED_OUTPUTS if not (outdir / name).exists())
        if missing:
            update_status(
                uid,
                status="failure",
                phase="failed",
                message="Missing expected output files: " + ",".join(missing),
                summary=summary,
                finished_at=utc_now(),
            )
            return

        update_status(
            uid,
            status="completion",
            phase="completed",
            message="Scoring job completed",
            exit_code=return_code,
            summary=summary,
            finished_at=utc_now(),
        )
    except Exception as exc:
        write_log(uid, f"[api] exception={exc!r}")
        update_status(
            uid,
            status="failure",
            phase="failed",
            message=str(exc),
            finished_at=utc_now(),
        )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs")
async def create_run(
    file: UploadFile = File(..., description="Annotated variant CSV. Must contain all_genes and gene_symbol."),
    hpo_file: UploadFile | None = File(None, description="Optional HPO list file. One HPO ID per line."),
    hpo_list: str | None = Form(None, description="Optional HPO list text. One HPO ID per line or comma separated."),
    hgvs: bool = Form(False, description="Reserved flag. Accepted for compatibility; not used by v2 scoring."),
    min_similarity: float = Form(0.20),
    max_orpha_files: int = Form(0),
) -> dict[str, Any]:
    uid = uuid.uuid4().hex
    base = run_dir(uid)
    input_dir = base / "inputs"
    input_dir.mkdir(parents=True, exist_ok=True)

    input_name = safe_filename(file.filename, "input.csv")
    input_path = input_dir / input_name
    save_upload(file, input_path)

    if hpo_file is not None:
        hpo_name = safe_filename(hpo_file.filename, "hpo.txt")
        hpo_path = input_dir / hpo_name
        save_upload(hpo_file, hpo_path)
    elif hpo_list:
        hpo_path = input_dir / "hpo_list.txt"
        normalized = hpo_list.replace(",", "\n").replace(";", "\n")
        hpo_path.write_text(normalized.strip() + "\n")
    else:
        hpo_path = input_dir / DEFAULT_HPO_FILE.name
        shutil.copy2(DEFAULT_HPO_FILE, hpo_path)

    initial = {
        "uid": uid,
        "status": "queuing",
        "phase": "queued",
        "message": "Job queued",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "input_filename": input_name,
        "hpo_filename": hpo_path.name,
        "status_url": f"/runs/{uid}",
        "files_url": f"/runs/{uid}/files",
        "files": [],
        "log_tail": [],
    }
    atomic_write_json(status_path(uid), initial)
    write_log(uid, "[api] Job queued")
    executor.submit(run_scoring_job, uid, input_path, hpo_path, min_similarity, max_orpha_files, hgvs)
    return initial


@app.get("/runs/{uid}")
def get_run(uid: str) -> dict[str, Any]:
    return read_json(status_path(uid))


@app.get("/runs/{uid}/files")
def list_files(uid: str) -> dict[str, Any]:
    status = read_json(status_path(uid))
    return {
        "uid": uid,
        "status": status.get("status"),
        "files": output_file_urls(uid) if status.get("status") == "completion" else [],
    }


@app.get("/runs/{uid}/files/{filename}")
def download_file(uid: str, filename: str) -> FileResponse:
    if filename not in ALLOWED_OUTPUTS:
        raise HTTPException(status_code=404, detail="file not found")
    status = read_json(status_path(uid))
    if status.get("status") != "completion":
        raise HTTPException(status_code=409, detail="run is not complete")
    path = outputs_dir(uid) / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path, filename=filename)
