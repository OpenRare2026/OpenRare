from __future__ import annotations

import json
import os
import re
import hashlib
import shutil
import subprocess
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from queue import Empty, Queue
from pathlib import Path
from typing import Any

import fcntl
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel


RUNNER_DIR = Path(__file__).resolve().parents[1]
RUNNER_SCRIPT = RUNNER_DIR / "bin" / "run_vep_to_csv.py"
PSEUDOGENE_SCRIPT = RUNNER_DIR / "bin" / "annotate_pseudogene.py"
REGULATORY_SCRIPT = RUNNER_DIR / "bin" / "annotate_regulatory.py"
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
QUEUE_SCAN_SECONDS = float(os.environ.get("VEP_API_QUEUE_SCAN_SECONDS", "10"))
PROGRESS_UPDATE_SECONDS = float(os.environ.get("VEP_API_PROGRESS_UPDATE_SECONDS", "5"))
PROGRESS_RUNNING_MAX = 95
SCHEDULER_LOCK_PATH = JOB_DIR / ".vep_scheduler.lock"
CACHE_LOCK_PATH = JOB_DIR / ".vep_result_cache.lock"
CACHE_KEY_VERSION = 2
ADOPT_LEGACY_QUEUED_JOBS = os.environ.get("VEP_API_ADOPT_LEGACY_QUEUED_JOBS", "").lower() in {
    "1",
    "true",
    "yes",
}
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
_STOP_JOB_ID = "__stop__"
_SCHEDULER_QUEUE: Queue[str] = Queue()
_SCHEDULER_LOCK = threading.Lock()
_SCHEDULED_JOB_IDS: set[str] = set()
_SCHEDULER_STOP = threading.Event()
_SCHEDULER_THREAD: threading.Thread | None = None
_ACTIVE_JOB_ID: str | None = None
_LAST_SCHEDULER_ERROR: str | None = None
_SKIPPED_UNWRITABLE_JOB_IDS: set[str] = set()
_IGNORED_LEGACY_JOB_IDS: set[str] = set()

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
    input_sha256: str | None = None
    reused_from_job_id: str | None = None
    deduplicated_to_job_id: str | None = None
    waiting_for_job_id: str | None = None
    message: str | None = None
    progress_percent: int = 0
    progress_stage: str | None = None
    progress_message: str | None = None


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
    with tmp.open("w") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)
    try:
        directory_fd = os.open(str(path.parent), os.O_DIRECTORY)
    except OSError:
        return
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


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


def parse_iso_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def clamp_progress(value: Any, minimum: int = 0, maximum: int = 100) -> int:
    try:
        integer = int(value)
    except (TypeError, ValueError):
        integer = minimum
    return max(minimum, min(maximum, integer))


def running_progress_percent(status: dict[str, Any]) -> int:
    current = clamp_progress(status.get("progress_percent"), minimum=10, maximum=PROGRESS_RUNNING_MAX)
    started_at = parse_iso_timestamp(status.get("started_at"))
    if not started_at:
        return current
    elapsed = max(0.0, (datetime.now(timezone.utc) - started_at).total_seconds())
    if RUN_TIMEOUT_SECONDS:
        estimated = 10 + int((PROGRESS_RUNNING_MAX - 10) * min(0.98, elapsed / RUN_TIMEOUT_SECONDS))
    else:
        estimated = 10 + int(85 * (1 - pow(0.5, elapsed / 600)))
    return max(current, clamp_progress(estimated, minimum=10, maximum=PROGRESS_RUNNING_MAX))


def progress_defaults(status: dict[str, Any]) -> dict[str, Any]:
    status_name = status.get("status")
    if status_name == "succeeded":
        return {
            "progress_percent": 100,
            "progress_stage": status.get("progress_stage") or "completed",
            "progress_message": status.get("progress_message") or "VEP result is ready.",
        }
    if status_name == "failed":
        return {
            "progress_percent": clamp_progress(status.get("progress_percent"), maximum=99),
            "progress_stage": status.get("progress_stage") or "failed",
            "progress_message": status.get("progress_message") or "VEP job failed.",
        }
    if status.get("waiting_for_job_id"):
        return {
            "progress_percent": clamp_progress(status.get("progress_percent"), maximum=5),
            "progress_stage": status.get("progress_stage") or "waiting_for_duplicate",
            "progress_message": status.get("progress_message")
            or "Waiting for an identical VCF run to finish.",
        }
    if status_name == "running":
        return {
            "progress_percent": running_progress_percent(status),
            "progress_stage": status.get("progress_stage") or "running_vep",
            "progress_message": status.get("progress_message") or "Running VEP annotation.",
        }
    return {
        "progress_percent": clamp_progress(status.get("progress_percent"), maximum=5),
        "progress_stage": status.get("progress_stage") or "queued",
        "progress_message": status.get("progress_message") or "Waiting in the API queue.",
    }


def with_progress_defaults(status: dict[str, Any]) -> dict[str, Any]:
    status = dict(status)
    for key, value in progress_defaults(status).items():
        status.setdefault(key, value)
        if key == "progress_percent":
            status[key] = value if status.get("status") == "running" else clamp_progress(status[key])
    return status


def update_progress(
    job_id: str,
    percent: int,
    stage: str,
    message: str,
    **changes: Any,
) -> dict[str, Any]:
    return update_status(
        job_id,
        progress_percent=clamp_progress(percent),
        progress_stage=stage,
        progress_message=message,
        **changes,
    )


@contextmanager
def exclusive_file_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = path.open("a+")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield lock_file
    finally:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()


def normalize_list_text(value: str, *, lowercase: bool = False, uppercase: bool = False) -> str:
    items: list[str] = []
    seen: set[str] = set()
    for item in re.split(r"[,;]+", value or ""):
        item = item.strip()
        if not item:
            continue
        key = re.sub(r"\s+", " ", item)
        if lowercase:
            key = key.lower()
        if uppercase:
            key = key.upper()
        if key not in seen:
            seen.add(key)
            items.append(key)
    return ",".join(items)


def result_cache_options(options: dict[str, Any]) -> dict[str, Any]:
    hpo_id = normalize_list_text(str(options.get("hpo_id", "")), uppercase=True)
    effective_regulatory_annotation = bool(options.get("regulatory_annotation")) and not bool(
        options.get("no_regulatory_annotation")
    )
    return {
        "format": str(options.get("format", "vcf")).lower(),
        "hgvs": bool(options.get("hgvs", True)),
        "no_pick": bool(options.get("no_pick", False)),
        "no_transcript_selection": bool(options.get("no_transcript_selection", False)),
        "pseudogene_annotation": bool(options.get("pseudogene_annotation", False))
        and not bool(options.get("no_pseudogene_annotation", False)),
        "regulatory_annotation": effective_regulatory_annotation,
        "top_k_transcripts": int(options.get("top_k_transcripts", 5)),
        "clinical_tissue": normalize_list_text(
            str(options.get("clinical_tissue", "")),
            lowercase=True,
        ),
        "hpo_id": hpo_id,
        "top_n_hpo_tissues": int(options.get("top_n_hpo_tissues", 3)) if hpo_id else 0,
        "disable_plugins": sorted(
            {
                str(plugin).strip().lower()
                for plugin in options.get("disable_plugins", [])
                if str(plugin).strip()
            }
        ),
    }


def build_cache_key(input_sha256: str, options: dict[str, Any]) -> str:
    payload = {
        "cache_key_version": CACHE_KEY_VERSION,
        "input_sha256": input_sha256,
        "options": result_cache_options(options),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def result_output_path(job_id: str) -> Path:
    return job_path(job_id) / "output.csv"


def completed_output_rows(directory: Path) -> int | None:
    output_path = directory / "output.csv"
    wrapper_log_path = directory / "wrapper.log"
    if not output_path.is_file() or not wrapper_log_path.is_file():
        return None
    try:
        if "Wrote " not in wrapper_log_path.read_text():
            return None
        return count_csv_rows(output_path)
    except OSError:
        return None


def reusable_status(status: dict[str, Any]) -> bool:
    if status.get("status") in {"queued", "running"}:
        return not status.get("waiting_for_job_id") and (
            bool(status.get("scheduler_owned")) or ADOPT_LEGACY_QUEUED_JOBS
        )
    if status.get("status") == "succeeded":
        try:
            return result_output_path(status["job_id"]).is_file()
        except (KeyError, HTTPException):
            return False
    return False


def status_matches_cache_key(status: dict[str, Any], cache_key: str) -> bool:
    if status.get("cache_key") == cache_key:
        return True
    if not status.get("input_sha256"):
        return False
    try:
        return build_cache_key(str(status["input_sha256"]), status.get("options", {})) == cache_key
    except (TypeError, ValueError):
        return False


def ensure_status_cache_fields(directory: Path, status: dict[str, Any]) -> dict[str, Any]:
    if status.get("cache_key") and status.get("input_sha256"):
        return status
    input_filename = status.get("input_filename")
    options = status.get("options")
    if not input_filename or not isinstance(options, dict):
        return status
    input_path = directory / safe_filename(str(input_filename))
    if not input_path.is_file():
        input_path = directory / str(input_filename)
    if not input_path.is_file():
        return status
    try:
        input_sha256 = str(status.get("input_sha256") or file_sha256(input_path))
        cache_key = str(status.get("cache_key") or build_cache_key(input_sha256, options))
    except (OSError, TypeError, ValueError):
        return status
    changes: dict[str, Any] = {}
    if not status.get("input_sha256"):
        changes["input_sha256"] = input_sha256
    if not status.get("cache_key"):
        changes["cache_key"] = cache_key
        changes["cache_key_version"] = CACHE_KEY_VERSION
        changes["cache_options"] = result_cache_options(options)
    if not changes:
        return status
    try:
        status.update(changes)
        write_json(directory / "status.json", status)
    except OSError:
        pass
    return status


def find_reusable_job(
    cache_key: str,
    *,
    exclude_job_id: str | None = None,
    allowed_statuses: set[str] | None = None,
) -> str | None:
    if not JOB_DIR.is_dir():
        return None
    candidates: list[tuple[int, str, str]] = []
    priority = {"succeeded": 0, "running": 1, "queued": 2}
    for directory in JOB_DIR.iterdir():
        if not directory.is_dir() or not JOB_ID_RE.fullmatch(directory.name):
            continue
        if directory.name == exclude_job_id:
            continue
        path = directory / "status.json"
        if not path.is_file():
            continue
        try:
            status = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        status = ensure_status_cache_fields(directory, status)
        status_name = str(status.get("status", ""))
        if allowed_statuses is not None and status_name not in allowed_statuses:
            continue
        if not reusable_status(status):
            continue
        if not status_matches_cache_key(status, cache_key):
            continue
        candidates.append((priority.get(status_name, 99), str(status.get("created_at", "")), directory.name))
    if not candidates:
        return None
    return sorted(candidates)[0][2]


def link_or_copy_file(source: Path, target: Path) -> None:
    if not source.is_file():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)
    try:
        os.link(source, target)
    except OSError:
        shutil.copy2(source, target)


def copy_reused_artifacts(source_job_id: str, target_job_id: str) -> None:
    source_directory = job_path(source_job_id)
    target_directory = job_path(target_job_id)
    for filename in [
        "output.csv",
        "output.csv.sqlite",
        "output.csv.sqlite-wal",
        "output.csv.sqlite-shm",
        "wrapper.log",
        "vep.log",
        "raw_vep.txt",
        "pseudogene_annotation.log.json",
        "regulatory_annotation.log.json",
        "output.csv.pseudogene_annotation.log.json",
        "output.csv.regulatory_annotation.log.json",
    ]:
        link_or_copy_file(source_directory / filename, target_directory / filename)


def mark_job_reused(job_id: str, source_job_id: str) -> dict[str, Any]:
    source_status = read_status(source_job_id)
    copy_reused_artifacts(source_job_id, job_id)
    rows = source_status.get("rows")
    if rows is None:
        rows = count_csv_rows(result_output_path(source_job_id))
    return finish_job_success(
        job_id,
        rows=rows,
        completed_at=source_status.get("completed_at") or now_iso(),
        reused_from_job_id=source_job_id,
        deduplicated_to_job_id=source_job_id,
        waiting_for_job_id=None,
        reused_at=now_iso(),
        progress_percent=100,
        progress_stage="reused",
        progress_message=f"Reused cached result from job {source_job_id}.",
    )


def resolve_waiting_duplicate(job_id: str, status: dict[str, Any]) -> bool | None:
    source_job_id = status.get("waiting_for_job_id")
    if not source_job_id or source_job_id == job_id or not JOB_ID_RE.fullmatch(str(source_job_id)):
        return None
    try:
        source_status = read_status(str(source_job_id))
    except HTTPException:
        update_status(job_id, waiting_for_job_id=None, error=None)
        return None

    source_status_name = source_status.get("status")
    if source_status_name == "succeeded" and result_output_path(str(source_job_id)).is_file():
        mark_job_reused(job_id, str(source_job_id))
        return True
    if source_status_name in {"queued", "running"}:
        if source_status_name == "queued":
            enqueue_job(str(source_job_id))
        update_status(
            job_id,
            status="queued",
            message="Duplicate input is already queued or running; waiting for cached result.",
            progress_percent=5,
            progress_stage="waiting_for_duplicate",
            progress_message="Waiting for an identical VCF run to finish.",
            error=None,
        )
        return False

    update_status(
        job_id,
        waiting_for_job_id=None,
        message=None,
        progress_stage="queued",
        progress_message="Waiting in the API queue.",
        error=None,
    )
    return None


def enqueue_waiting_duplicates(source_job_id: str, cache_key: str | None) -> int:
    if not cache_key or not JOB_DIR.is_dir():
        return 0
    count = 0
    for directory in JOB_DIR.iterdir():
        if not directory.is_dir() or not JOB_ID_RE.fullmatch(directory.name):
            continue
        if directory.name == source_job_id:
            continue
        path = directory / "status.json"
        if not path.is_file():
            continue
        try:
            status = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if status.get("status") != "queued":
            continue
        if status.get("waiting_for_job_id") != source_job_id:
            continue
        if not status_matches_cache_key(status, cache_key):
            continue
        if enqueue_job(directory.name):
            count += 1
    return count


def finish_job_success(job_id: str, **changes: Any) -> dict[str, Any]:
    changes.setdefault("progress_percent", 100)
    changes.setdefault("progress_stage", "completed")
    changes.setdefault("progress_message", "VEP result is ready.")
    status = update_status(job_id, status="succeeded", error=None, **changes)
    enqueue_waiting_duplicates(job_id, status.get("cache_key"))
    return status


def can_manage_job_dir(directory: Path) -> bool:
    return os.access(directory, os.W_OK | os.X_OK)


def waiting_source_is_unfinished(status: dict[str, Any]) -> bool:
    source_job_id = status.get("waiting_for_job_id")
    if not source_job_id or not JOB_ID_RE.fullmatch(str(source_job_id)):
        return False
    try:
        source_status = read_status(str(source_job_id))
    except HTTPException:
        return False
    return source_status.get("status") in {"queued", "running"}


def scan_queued_jobs() -> tuple[list[str], list[str], list[str]]:
    if not JOB_DIR.is_dir():
        return [], [], []
    queued_jobs: list[tuple[str, str]] = []
    unwritable_jobs: list[tuple[str, str]] = []
    legacy_jobs: list[tuple[str, str]] = []
    for directory in JOB_DIR.iterdir():
        if not directory.is_dir() or not JOB_ID_RE.fullmatch(directory.name):
            continue
        path = directory / "status.json"
        if not path.is_file():
            continue
        try:
            status = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if status.get("status") == "queued":
            if waiting_source_is_unfinished(status):
                continue
            if not status.get("scheduler_owned") and not ADOPT_LEGACY_QUEUED_JOBS:
                legacy_jobs.append((str(status.get("created_at", "")), directory.name))
                continue
            queue = queued_jobs if can_manage_job_dir(directory) else unwritable_jobs
            queue.append((str(status.get("created_at", "")), directory.name))
    return [job_id for _, job_id in sorted(queued_jobs)], [
        job_id for _, job_id in sorted(unwritable_jobs)
    ], [
        job_id for _, job_id in sorted(legacy_jobs)
    ]


def list_queued_job_ids() -> list[str]:
    queued_job_ids, _, _ = scan_queued_jobs()
    return queued_job_ids


def enqueue_job(job_id: str) -> bool:
    with _SCHEDULER_LOCK:
        if job_id in _SCHEDULED_JOB_IDS:
            return False
        _SCHEDULED_JOB_IDS.add(job_id)
    _SCHEDULER_QUEUE.put(job_id)
    return True


def enqueue_queued_jobs() -> int:
    queued_job_ids, unwritable_job_ids, legacy_job_ids = scan_queued_jobs()
    with _SCHEDULER_LOCK:
        _SKIPPED_UNWRITABLE_JOB_IDS.clear()
        _SKIPPED_UNWRITABLE_JOB_IDS.update(unwritable_job_ids)
        _IGNORED_LEGACY_JOB_IDS.clear()
        _IGNORED_LEGACY_JOB_IDS.update(legacy_job_ids)
    count = 0
    for job_id in queued_job_ids:
        if enqueue_job(job_id):
            count += 1
    return count


def recover_interrupted_jobs() -> int:
    global _LAST_SCHEDULER_ERROR

    SCHEDULER_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock_file = SCHEDULER_LOCK_PATH.open("a+")
    try:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0

        recovered = 0
        if JOB_DIR.is_dir():
            for directory in JOB_DIR.iterdir():
                if not directory.is_dir() or not JOB_ID_RE.fullmatch(directory.name):
                    continue
                path = directory / "status.json"
                if not path.is_file():
                    continue
                try:
                    status = json.loads(path.read_text())
                except (OSError, json.JSONDecodeError):
                    continue
                if status.get("status") != "running":
                    continue
                if not status.get("scheduler_owned"):
                    continue
                if not can_manage_job_dir(directory):
                    with _SCHEDULER_LOCK:
                        _SKIPPED_UNWRITABLE_JOB_IDS.add(directory.name)
                    continue
                try:
                    rows = completed_output_rows(directory)
                    if rows is not None:
                        finish_job_success(
                            directory.name,
                            rows=rows,
                            completed_at=status.get("completed_at") or now_iso(),
                            recovered_at=now_iso(),
                        )
                        recovered += 1
                        continue
                    update_status(
                        directory.name,
                        status="queued",
                        error="Recovered after API restart while job was marked running.",
                        recovered_at=now_iso(),
                        progress_percent=0,
                        progress_stage="queued",
                        progress_message="Recovered after API restart; waiting in the queue.",
                    )
                except OSError as exc:
                    with _SCHEDULER_LOCK:
                        _LAST_SCHEDULER_ERROR = f"{directory.name}: {exc}"
                        _SKIPPED_UNWRITABLE_JOB_IDS.add(directory.name)
                    continue
                recovered += 1
        return recovered
    finally:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()


def scheduler_snapshot() -> dict[str, Any]:
    with _SCHEDULER_LOCK:
        active_job_id = _ACTIVE_JOB_ID
        scheduled_job_ids = sorted(_SCHEDULED_JOB_IDS)
        last_error = _LAST_SCHEDULER_ERROR
        skipped_unwritable_job_ids = sorted(_SKIPPED_UNWRITABLE_JOB_IDS)
        ignored_legacy_job_ids = sorted(_IGNORED_LEGACY_JOB_IDS)
        thread_alive = bool(_SCHEDULER_THREAD and _SCHEDULER_THREAD.is_alive())
    return {
        "running": thread_alive,
        "active_job_id": active_job_id,
        "queue_depth": _SCHEDULER_QUEUE.qsize(),
        "scheduled_job_ids": scheduled_job_ids,
        "queued_job_ids": list_queued_job_ids(),
        "skipped_unwritable_job_ids": skipped_unwritable_job_ids,
        "skipped_unwritable_count": len(skipped_unwritable_job_ids),
        "ignored_legacy_job_ids": ignored_legacy_job_ids,
        "ignored_legacy_count": len(ignored_legacy_job_ids),
        "adopt_legacy_queued_jobs": ADOPT_LEGACY_QUEUED_JOBS,
        "lock_path": str(SCHEDULER_LOCK_PATH),
        "result_cache_lock_path": str(CACHE_LOCK_PATH),
        "result_cache_key_version": CACHE_KEY_VERSION,
        "last_error": last_error,
    }


def run_scheduled_job(job_id: str) -> bool:
    global _ACTIVE_JOB_ID, _LAST_SCHEDULER_ERROR

    SCHEDULER_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock_file = SCHEDULER_LOCK_PATH.open("a+")
    try:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False

        try:
            status = read_status(job_id)
        except HTTPException:
            return True
        if status.get("status") != "queued":
            return True

        waiting_resolution = resolve_waiting_duplicate(job_id, status)
        if waiting_resolution is not None:
            return True

        rows = completed_output_rows(job_path(job_id))
        if rows is not None:
            finish_job_success(
                job_id,
                rows=rows,
                completed_at=status.get("completed_at") or now_iso(),
                recovered_at=now_iso(),
            )
            return True

        cache_key = status.get("cache_key")
        if cache_key:
            with exclusive_file_lock(CACHE_LOCK_PATH):
                reusable_job_id = find_reusable_job(
                    str(cache_key),
                    exclude_job_id=job_id,
                    allowed_statuses={"succeeded"},
                )
                if reusable_job_id:
                    mark_job_reused(job_id, reusable_job_id)
                    return True

        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(
            json.dumps(
                {
                    "pid": os.getpid(),
                    "job_id": job_id,
                    "locked_at": now_iso(),
                },
                sort_keys=True,
            )
            + "\n"
        )
        lock_file.flush()

        with _SCHEDULER_LOCK:
            _ACTIVE_JOB_ID = job_id
        update_status(
            job_id,
            scheduler_owned=True,
            scheduler_pid=os.getpid(),
            scheduler_claimed_at=now_iso(),
            scheduler_lock_path=str(SCHEDULER_LOCK_PATH),
        )
        run_vep_job(job_id)
        with _SCHEDULER_LOCK:
            _LAST_SCHEDULER_ERROR = None
        return True
    except Exception as exc:
        with _SCHEDULER_LOCK:
            _LAST_SCHEDULER_ERROR = f"{job_id}: {exc}"
        try:
            if read_status(job_id).get("status") == "queued":
                update_status(job_id, status="failed", error=str(exc))
        except Exception:
            pass
        return True
    finally:
        with _SCHEDULER_LOCK:
            if _ACTIVE_JOB_ID == job_id:
                _ACTIVE_JOB_ID = None
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        finally:
            lock_file.close()


def scheduler_loop() -> None:
    next_scan_at = 0.0
    while not _SCHEDULER_STOP.is_set():
        if time.monotonic() >= next_scan_at:
            enqueue_queued_jobs()
            next_scan_at = time.monotonic() + QUEUE_SCAN_SECONDS
        try:
            job_id = _SCHEDULER_QUEUE.get(timeout=1)
        except Empty:
            continue
        if job_id == _STOP_JOB_ID:
            return
        with _SCHEDULER_LOCK:
            _SCHEDULED_JOB_IDS.discard(job_id)
        if not run_scheduled_job(job_id) and not _SCHEDULER_STOP.is_set():
            enqueue_job(job_id)
            time.sleep(min(1.0, QUEUE_SCAN_SECONDS))


def start_scheduler() -> None:
    global _SCHEDULER_THREAD
    recover_interrupted_jobs()
    with _SCHEDULER_LOCK:
        if _SCHEDULER_THREAD and _SCHEDULER_THREAD.is_alive():
            return
        _SCHEDULER_STOP.clear()
        _SCHEDULER_THREAD = threading.Thread(
            target=scheduler_loop,
            name="vep-job-scheduler",
            daemon=True,
        )
        _SCHEDULER_THREAD.start()
    enqueue_queued_jobs()


def stop_scheduler() -> None:
    _SCHEDULER_STOP.set()
    _SCHEDULER_QUEUE.put(_STOP_JOB_ID)
    thread = _SCHEDULER_THREAD
    if thread:
        thread.join(timeout=5)


def public_status(status: dict[str, Any], base_url: str | None = None) -> dict[str, Any]:
    job_id = status["job_id"]
    prefix = base_url.rstrip("/") if base_url else ""
    status = with_progress_defaults(status)
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


async def save_upload(upload: UploadFile, path: Path) -> tuple[int, str]:
    total = 0
    digest = hashlib.sha256()
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
            digest.update(chunk)
            handle.write(chunk)
        handle.flush()
        os.fsync(handle.fileno())
    if total == 0:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    return total, digest.hexdigest()


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
    sqlite_db_path = directory / "output.csv.sqlite"
    pseudogene_log_path = directory / "pseudogene_annotation.log.json"
    regulatory_log_path = directory / "regulatory_annotation.log.json"
    options = status["options"]

    waiting_resolution = resolve_waiting_duplicate(job_id, status)
    if waiting_resolution is not None:
        return

    rows = completed_output_rows(directory)
    if rows is not None:
        finish_job_success(
            job_id,
            rows=rows,
            completed_at=status.get("completed_at") or now_iso(),
            recovered_at=now_iso(),
        )
        return

    cache_key = status.get("cache_key")
    if cache_key:
        with exclusive_file_lock(CACHE_LOCK_PATH):
            reusable_job_id = find_reusable_job(
                str(cache_key),
                exclude_job_id=job_id,
                allowed_statuses={"succeeded"},
            )
            if reusable_job_id:
                mark_job_reused(job_id, reusable_job_id)
                return

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
        "--conversion-mode",
        "sqlite",
        "--sqlite-db",
        str(sqlite_db_path),
        "--keep-sqlite-db",
    ]
    if options["hgvs"]:
        cmd.append("--hgvs")
    if options["no_pick"]:
        cmd.append("--no-pick")
    if options.get("no_transcript_selection"):
        cmd.append("--no-transcript-selection")
    if options.get("pseudogene_annotation") and not options.get("no_pseudogene_annotation"):
        cmd.append("--pseudogene-annotation")
        cmd += ["--pseudogene-log-json", str(pseudogene_log_path)]
    elif options.get("no_pseudogene_annotation"):
        cmd.append("--no-pseudogene-annotation")
    if options.get("regulatory_annotation") and not options.get("no_regulatory_annotation"):
        cmd.append("--regulatory-annotation")
        cmd += ["--regulatory-log-json", str(regulatory_log_path)]
    elif options.get("no_regulatory_annotation"):
        cmd.append("--no-regulatory-annotation")
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

    update_progress(
        job_id,
        10,
        "running_vep",
        "Running VEP annotation.",
        status="running",
        command=cmd,
        started_at=now_iso(),
        error=None,
    )
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(RUNNER_DIR),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output_parts: list[str] = []
        started_at = time.monotonic()
        next_progress_at = started_at
        while True:
            try:
                stdout, _ = process.communicate(timeout=PROGRESS_UPDATE_SECONDS)
                if stdout:
                    output_parts.append(stdout)
                break
            except subprocess.TimeoutExpired:
                if RUN_TIMEOUT_SECONDS and time.monotonic() - started_at > RUN_TIMEOUT_SECONDS:
                    process.kill()
                    stdout, _ = process.communicate()
                    if stdout:
                        output_parts.append(stdout)
                    raise subprocess.TimeoutExpired(cmd, RUN_TIMEOUT_SECONDS)
                if time.monotonic() >= next_progress_at:
                    latest_status = read_status(job_id)
                    update_progress(
                        job_id,
                        running_progress_percent(latest_status),
                        "running_vep",
                        "Running VEP annotation.",
                        status="running",
                    )
                    next_progress_at = time.monotonic() + PROGRESS_UPDATE_SECONDS
        wrapper_log_path.write_text("".join(output_parts))
        if process.returncode != 0:
            message = tail_text(wrapper_log_path.read_text())
            update_progress(
                job_id,
                clamp_progress(read_status(job_id).get("progress_percent"), maximum=99),
                "failed",
                "VEP job failed.",
                status="failed",
                error=message or f"VEP exited with {process.returncode}",
            )
            return
        rows = count_csv_rows(output_path)
        finish_job_success(job_id, rows=rows, completed_at=now_iso())
    except subprocess.TimeoutExpired as exc:
        update_progress(
            job_id,
            clamp_progress(read_status(job_id).get("progress_percent"), maximum=99),
            "failed",
            "VEP job timed out.",
            status="failed",
            error=f"VEP timed out after {exc.timeout} seconds",
        )
    except Exception as exc:
        update_progress(
            job_id,
            clamp_progress(read_status(job_id).get("progress_percent"), maximum=99),
            "failed",
            "VEP job failed.",
            status="failed",
            error=str(exc),
        )


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
    start_scheduler()


@app.on_event("shutdown")
def shutdown() -> None:
    stop_scheduler()


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
        "pseudogene_script": str(PSEUDOGENE_SCRIPT),
        "pseudogene_script_exists": PSEUDOGENE_SCRIPT.is_file(),
        "regulatory_script": str(REGULATORY_SCRIPT),
        "regulatory_script_exists": REGULATORY_SCRIPT.is_file(),
        "config": str(CONFIG_PATH),
        "config_exists": CONFIG_PATH.is_file(),
        "job_dir": str(JOB_DIR),
        "scheduler": scheduler_snapshot(),
    }


@app.get("/scheduler")
def scheduler() -> dict[str, Any]:
    return scheduler_snapshot()


@app.post("/runs", response_model=RunResponse, status_code=202)
async def submit_run(
    request: Request,
    file: UploadFile = File(...),
    hgvs: bool = Form(True),
    no_pick: bool = Form(False),
    no_transcript_selection: bool = Form(False),
    pseudogene_annotation: bool = Form(False),
    no_pseudogene_annotation: bool = Form(False),
    regulatory_annotation: bool = Form(False),
    no_regulatory_annotation: bool = Form(False),
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
    input_bytes, input_sha256 = await save_upload(file, input_path)

    created_at = now_iso()
    options = {
        "hgvs": hgvs,
        "no_pick": no_pick,
        "no_transcript_selection": no_transcript_selection,
        "pseudogene_annotation": pseudogene_annotation,
        "no_pseudogene_annotation": no_pseudogene_annotation,
        "regulatory_annotation": regulatory_annotation,
        "no_regulatory_annotation": no_regulatory_annotation,
        "top_k_transcripts": top_k_transcripts,
        "clinical_tissue": clinical_tissue,
        "hpo_id": hpo_id,
        "top_n_hpo_tissues": top_n_hpo_tissues,
        "format": input_format,
        "fork": fork,
        "disable_plugins": disabled_plugins,
        "keep_raw_vep": keep_raw_vep,
    }
    cache_key = build_cache_key(input_sha256, options)
    status = {
        "job_id": job_id,
        "status": "queued",
        "created_at": created_at,
        "updated_at": created_at,
        "input_filename": input_filename,
        "input_bytes": input_bytes,
        "input_sha256": input_sha256,
        "cache_key": cache_key,
        "cache_key_version": CACHE_KEY_VERSION,
        "cache_options": result_cache_options(options),
        "options": options,
        "rows": None,
        "error": None,
        "message": None,
        "progress_percent": 0,
        "progress_stage": "queued",
        "progress_message": "Waiting in the API queue.",
        "scheduler_owned": True,
    }
    with exclusive_file_lock(CACHE_LOCK_PATH):
        reusable_job_id = find_reusable_job(cache_key, exclude_job_id=job_id)
        if reusable_job_id:
            source_status = read_status(reusable_job_id)
            status.update(
                {
                    "status": "succeeded" if source_status.get("status") == "succeeded" else "queued",
                    "deduplicated_to_job_id": reusable_job_id,
                    "reused_from_job_id": reusable_job_id
                    if source_status.get("status") == "succeeded"
                    else None,
                    "rows": source_status.get("rows") if source_status.get("status") == "succeeded" else None,
                }
            )
            if source_status.get("status") == "succeeded":
                write_json(status_path(job_id), status)
                status = mark_job_reused(job_id, reusable_job_id)
            else:
                status["status"] = "queued"
                status["waiting_for_job_id"] = reusable_job_id
                status["message"] = (
                    "Duplicate input is already queued or running; waiting for cached result."
                )
                status["progress_percent"] = 5
                status["progress_stage"] = "waiting_for_duplicate"
                status["progress_message"] = "Waiting for an identical VCF run to finish."
                status["error"] = None
                write_json(status_path(job_id), status)
                enqueue_job(job_id)
        else:
            write_json(status_path(job_id), status)
            enqueue_job(job_id)
    return public_status(status, base_url=str(request.base_url))


@app.get("/runs/{job_id}", response_model=RunResponse)
def get_run(request: Request, job_id: str) -> dict[str, Any]:
    return public_status(read_status(job_id), base_url=str(request.base_url))


@app.get("/runs/{job_id}/progress")
def get_run_progress(request: Request, job_id: str) -> dict[str, Any]:
    status = public_status(read_status(job_id), base_url=str(request.base_url))
    return {
        "job_id": status["job_id"],
        "status": status["status"],
        "progress_percent": status["progress_percent"],
        "progress_stage": status["progress_stage"],
        "progress_message": status["progress_message"],
        "message": status.get("message"),
        "error": status.get("error"),
        "status_url": status["status_url"],
        "result_url": status["result_url"],
    }


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
    for path in [
        directory / "wrapper.log",
        directory / "vep.log",
        directory / "regulatory_annotation.log.json",
        directory / "pseudogene_annotation.log.json",
    ]:
        if path.is_file():
            parts.append(f"### {path.name}\n{path.read_text()}")
    return PlainTextResponse("\n\n".join(parts) if parts else "No log yet.\n")
