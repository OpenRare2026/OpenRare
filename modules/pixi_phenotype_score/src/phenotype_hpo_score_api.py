#!/usr/bin/env python3
"""FastAPI wrapper for phenotype-HPO scoring v3."""

from __future__ import annotations

import collections
import json
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from path_config import PROJECT_ROOT, display_path, load_paths

PATHS = load_paths()
WORK_DIR = PROJECT_ROOT
RUN_ROOT = PATHS.runtime_root / "api_runs"
DEFAULT_HPO_FILE = PATHS.default_hpo_file
SCORING_SCRIPT = PROJECT_ROOT / "src" / "phenotype_hpo_score.py"
MODULE_README = PROJECT_ROOT / "README.md"
ALLOWED_OUTPUTS = {
    "README.md",
    "gene_phenotype_score.csv",
    "variant_phenotype_score.csv",
}

app = FastAPI(title="Phenotype-HPO Score Pixi API", version="3.0-pixi")


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


class JobManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._ready = threading.Condition(self._lock)
        self._queue: collections.deque[dict[str, Any]] = collections.deque()
        self._running_uid = ""
        self._worker = threading.Thread(target=self._worker_loop, name="phenotype-score-worker", daemon=True)
        self._worker.start()

    def enqueue(self, job: dict[str, Any]) -> dict[str, Any]:
        with self._ready:
            self._queue.append(job)
            self._refresh_queued_locked()
            self._ready.notify()
            return self._snapshot_for_uid_locked(job["uid"])

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "running_uid": self._running_uid,
                "queued_count": len(self._queue),
                "queued_uids": [job["uid"] for job in self._queue],
            }

    def augment_status(self, status: dict[str, Any]) -> dict[str, Any]:
        uid = str(status.get("uid", ""))
        with self._lock:
            status.update(self._snapshot_for_uid_locked(uid))
        return status

    def _snapshot_for_uid_locked(self, uid: str) -> dict[str, Any]:
        queued_uids = [job["uid"] for job in self._queue]
        position = queued_uids.index(uid) + 1 if uid in queued_uids else 0
        return {
            "running_uid": self._running_uid,
            "queued_count": len(self._queue),
            "queue_position": position,
            "is_running": uid == self._running_uid,
        }

    def _refresh_queued_locked(self) -> None:
        for idx, job in enumerate(self._queue, 1):
            uid = job["uid"]
            update_status(
                uid,
                status="queued",
                phase="queued",
                message=f"Job queued at position {idx}",
                queue_position=idx,
                queued_count=len(self._queue),
                running_uid=self._running_uid,
            )

    def _worker_loop(self) -> None:
        while True:
            with self._ready:
                while not self._queue:
                    self._ready.wait()
                job = self._queue.popleft()
                self._running_uid = job["uid"]
                self._refresh_queued_locked()
            try:
                run_scoring_job(**job)
            finally:
                with self._ready:
                    if self._running_uid == job["uid"]:
                        self._running_uid = ""
                    self._refresh_queued_locked()


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
    input_format: str,
    chunksize: int,
    rebuild_orpha_index: bool,
) -> None:
    update_status(
        uid,
        status="running",
        phase="running",
        message="Scoring job started",
        queue_position=0,
        started_at=utc_now(),
    )
    outdir = outputs_dir(uid)
    outdir.mkdir(parents=True, exist_ok=True)
    if MODULE_README.exists():
        shutil.copy2(MODULE_README, outdir / MODULE_README.name)

    cmd = [
        sys.executable,
        display_path(SCORING_SCRIPT),
        "--input-csv",
        display_path(input_csv),
        "--hpo-file",
        display_path(hpo_file),
        "--config",
        display_path(PATHS.config_file),
        "--outdir",
        display_path(outdir),
        "--min-similarity",
        str(min_similarity),
        "--input-format",
        input_format,
        "--chunksize",
        str(chunksize),
    ]
    if max_orpha_files:
        cmd.extend(["--max-orpha-files", str(max_orpha_files)])
    if rebuild_orpha_index:
        cmd.append("--rebuild-orpha-index")

    write_log(uid, f"[api] uid={uid}")
    write_log(uid, f"[api] input_csv={display_path(input_csv)}")
    write_log(uid, f"[api] hpo_file={display_path(hpo_file)}")
    write_log(uid, f"[api] hgvs={hgvs}")
    write_log(uid, f"[api] input_format={input_format}")
    write_log(uid, f"[api] chunksize={chunksize}")
    write_log(uid, f"[api] path_config={display_path(PATHS.config_file)}")
    display_cmd = ["python", *cmd[1:]]
    write_log(uid, "[api] command=" + " ".join(display_cmd))

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
                update_status(uid, status="running", phase="running", message=clean)
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
    return {"status": "ok", "version": "v3-pixi"}


@app.get("/queue")
def queue_status() -> dict[str, Any]:
    return manager.snapshot()


@app.post("/runs")
async def create_run(
    file: UploadFile = File(..., description="Annotated variant CSV. Must contain all_genes and gene_symbol."),
    hpo_file: UploadFile | None = File(None, description="Optional HPO list file. One HPO ID per line."),
    hpo_list: str | None = Form(None, description="Optional HPO list text. One HPO ID per line or comma separated."),
    hgvs: bool = Form(False, description="Reserved flag. Accepted for compatibility; not used by v2 scoring."),
    min_similarity: float = Form(0.20),
    max_orpha_files: int = Form(0),
    input_format: str = Form("auto"),
    chunksize: int = Form(100000),
    rebuild_orpha_index: bool = Form(False),
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
        "status": "queued",
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
        "queue_position": 0,
        "queued_count": 0,
    }
    atomic_write_json(status_path(uid), initial)
    write_log(uid, "[api] Job queued")
    initial.update(
        manager.enqueue(
            {
                "uid": uid,
                "input_csv": input_path,
                "hpo_file": hpo_path,
                "min_similarity": min_similarity,
                "max_orpha_files": max_orpha_files,
                "hgvs": hgvs,
                "input_format": input_format,
                "chunksize": chunksize,
                "rebuild_orpha_index": rebuild_orpha_index,
            }
        )
    )
    return initial


@app.get("/runs/{uid}")
def get_run(uid: str) -> dict[str, Any]:
    return manager.augment_status(read_json(status_path(uid)))


@app.get("/runs/{uid}/files")
def list_files(uid: str) -> dict[str, Any]:
    status = manager.augment_status(read_json(status_path(uid)))
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


manager = JobManager()
