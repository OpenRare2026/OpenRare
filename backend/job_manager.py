from __future__ import annotations

import json
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from fastapi import HTTPException

from backend.config import ApiConfig


_LOCK = threading.Lock()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def status_path(job_id: str) -> Path:
    return ApiConfig.jobs_dir / job_id / "status.json"


def read_status(job_id: str) -> dict:
    path = status_path(job_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"job_id not found: {job_id}")
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


def run_command(
    job_id: str,
    cmd: list[str],
    output_dir: Path,
    step: str,
    log_name: str = "run.log",
    cwd: Optional[Path] = None,
) -> None:
    from backend.config import ApiConfig

    log_path = ApiConfig.jobs_dir / job_id / log_name
    write_status(
        job_id,
        status="running",
        step=step,
        started_at=now_iso(),
        command=cmd,
        log=str(log_path),
    )
    try:
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd or Path.cwd()),
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
        if proc.returncode != 0:
            raise RuntimeError(f"{step} failed with exit code {proc.returncode}")
        write_status(
            job_id,
            status="succeeded",
            finished_at=now_iso(),
            returncode=proc.returncode,
            output_dir=str(output_dir),
        )
    except Exception as exc:
        write_status(
            job_id,
            status="failed",
            finished_at=now_iso(),
            error=str(exc),
            output_dir=str(output_dir),
        )


def create_job_dir(job_id: str) -> Path:
    job_dir = ApiConfig.jobs_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir
