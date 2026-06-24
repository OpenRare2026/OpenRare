#!/usr/bin/env python3
"""FastAPI server for RAG-HPO pipeline.

Start with:
    uvicorn dev.server:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import os
import json
import uuid
import time
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

try:
    from config import settings
    from schemas import (
        ExtractRequest,
        RunResponse,
        JobStatus,
        HealthResponse,
        ResultItem,
        utcnow,
    )
except ImportError:
    from dev.config import settings
    from dev.schemas import (
        ExtractRequest,
        RunResponse,
        JobStatus,
        HealthResponse,
        ResultItem,
        utcnow,
    )

# ── Globals ────────────────────────────────────────────────────────

_JOBS_DIR = settings.jobs_dir

_pipeline = None
_jobs: dict[str, dict] = {}
_lock = threading.Lock()


def _job_dir(job_id: str) -> str:
    return os.path.join(_JOBS_DIR, job_id)


def _job_path(job_id: str) -> str:
    return os.path.join(_job_dir(job_id), "job.json")


def _save_job(job_id: str):
    """Persist a single job to disk. Call while holding _lock."""
    job = _jobs.get(job_id)
    if job is None:
        return
    try:
        os.makedirs(_job_dir(job_id), exist_ok=True)
        with open(_job_path(job_id), "w", encoding="utf-8") as f:
            json.dump(job, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"[WARN] Could not save job {job_id}: {exc}")


def _load_jobs():
    """Restore _jobs from disk. Call before accepting requests."""
    if not os.path.isdir(_JOBS_DIR):
        return
    count = 0
    for entry in os.listdir(_JOBS_DIR):
        jp = os.path.join(_JOBS_DIR, entry, "job.json")
        if not os.path.isfile(jp):
            continue
        try:
            with open(jp, "r", encoding="utf-8") as f:
                job = json.load(f)
            if isinstance(job, dict) and "job_id" in job:
                _jobs[job["job_id"]] = job
                count += 1
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[WARN] Could not load {jp}: {exc}")
    if count:
        print(f"[INFO] Restored {count} job(s) from {_JOBS_DIR}")

# ── Lifespan ───────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pipeline

    try:
        from rag_hpo import LLMClient
        from pipeline import Pipeline
    except ImportError:
        from dev.rag_hpo import LLMClient
        from dev.pipeline import Pipeline

    llm = LLMClient(
        api_key=settings.api_key,
        base_url=settings.base_url,
        model_name=settings.model,
        max_tokens_per_day=settings.max_tokens_per_day,
        max_queries_per_minute=settings.max_queries_per_minute,
        temperature=settings.temperature,
    )
    print(f"LLM client initialized: {settings.model} via {settings.base_url}")

    _pipeline = Pipeline()
    _pipeline.initialize(llm)
    _load_jobs()
    print("Pipeline ready — models loaded, FAISS index built.")

    yield

    print("Shutting down.")


# ── App ────────────────────────────────────────────────────────────

app = FastAPI(
    title="RAG-HPO",
    description="HPO term extraction from clinical notes via LLM + RAG",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ────────────────────────────────────────────────────────


def _base_url(req: Request) -> str:
    """Reconstruct the base URL from the incoming request."""
    return str(req.base_url).rstrip("/")


def _build_job_urls(job_id: str, base: str) -> dict:
    return {
        "status_url": f"{base}/runs/{job_id}",
        "result_url": f"{base}/runs/{job_id}/result",
        "log_url": f"{base}/runs/{job_id}/log",
    }


def _queued_jobs() -> int:
    return sum(1 for j in _jobs.values() if j["status"] == "queued")


# ── Endpoints ──────────────────────────────────────────────────────


@app.get("/api/v1/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", model_loaded=_pipeline is not None and _pipeline.is_ready, queue_size=_queued_jobs())


# ── Submit ─────────────────────────────────────────────────────────


@app.post("/runs", response_model=RunResponse, status_code=202)
@app.post("/api/v1/extract", response_model=RunResponse, status_code=202)
async def create_run(req: ExtractRequest, request: Request):
    """Submit clinical notes for HPO extraction. Returns a job descriptor."""
    if _pipeline is None or not _pipeline.is_ready:
        raise HTTPException(503, "Pipeline not initialized yet.")

    job_id = str(uuid.uuid4())
    notes = [n.model_dump() for n in req.notes]
    now = utcnow()
    base = _base_url(request)
    input_bytes = sum(len(n["clinical_note"].encode("utf-8")) for n in notes)

    job_meta = {
        "job_id": job_id,
        "status": "queued",
        "created_at": now,
        "updated_at": now,
        "input_filename": req.input_filename,
        "input_bytes": input_bytes,
        "options": {},
        "notes_count": len(notes),
        "rows": None,
        "results": None,
        "elapsed_seconds": None,
        "error": None,
        **_build_job_urls(job_id, base),
    }

    with _lock:
        _jobs[job_id] = job_meta
        _save_job(job_id)

    thread = threading.Thread(target=_run_job, args=(job_id, notes), daemon=True)
    thread.start()

    return RunResponse(**job_meta)


# ── Status ──────────────────────────────────────────────────────────


@app.get("/runs/{job_id}", response_model=JobStatus)
@app.get("/api/v1/jobs/{job_id}", response_model=JobStatus)
async def get_run(job_id: str, request: Request):
    """Get the status (and, when finished, results) of a job."""
    with _lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(404, f"Job '{job_id}' not found.")

    base = _base_url(request)
    urls = _build_job_urls(job_id, base)
    return JobStatus(**{**job, **urls})


# ── Result ──────────────────────────────────────────────────────────


@app.get("/runs/{job_id}/result")
@app.get("/api/v1/jobs/{job_id}/result")
async def get_run_result(job_id: str):
    """Get only the results of a completed job."""
    with _lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(404, f"Job '{job_id}' not found.")
    if job["status"] == "queued":
        raise HTTPException(425, "Job still queued. Try again later.")
    if job["status"] == "failure":
        raise HTTPException(422, job.get("error", "Job failed."))
    return {"job_id": job_id, "status": job["status"], "results": job.get("results", [])}


# ── Log ─────────────────────────────────────────────────────────────


@app.get("/runs/{job_id}/log")
@app.get("/api/v1/jobs/{job_id}/log")
async def get_run_log(job_id: str):
    """Get a minimal execution log for a job."""
    with _lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(404, f"Job '{job_id}' not found.")
    return {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
        "elapsed_seconds": job.get("elapsed_seconds"),
        "error": job.get("error"),
    }


# ── Download ────────────────────────────────────────────────────────

from fastapi.responses import FileResponse


@app.get("/runs/{job_id}/download/{filename}")
@app.get("/api/v1/jobs/{job_id}/download/{filename}")
async def download_file(job_id: str, filename: str):
    """Download an export file (hpo_ids.txt or phenotypes.tsv)."""
    path = os.path.join(_job_dir(job_id), filename)
    if not os.path.isfile(path):
        raise HTTPException(404, f"File '{filename}' not found for job '{job_id}'.")
    return FileResponse(path, filename=filename, media_type="application/octet-stream")


# ── Background runner ───────────────────────────────────────────────


def _run_job(job_id: str, notes: list[dict]):
    t0 = time.time()
    try:
        results = _pipeline.run(notes)
        items = [ResultItem(**r) for r in results]
    except Exception as exc:
        with _lock:
            _jobs[job_id]["status"] = "failure"
            _jobs[job_id]["error"] = str(exc)
            _jobs[job_id]["updated_at"] = utcnow()
            _save_job(job_id)
        return

    elapsed = time.time() - t0
    with _lock:
        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["results"] = [i.model_dump() for i in items]
        _jobs[job_id]["rows"] = len(items)
        _jobs[job_id]["elapsed_seconds"] = round(elapsed, 1)
        _jobs[job_id]["updated_at"] = utcnow()
        _save_job(job_id)

    # Write export files alongside job.json
    note_map = {n["patient_id"]: n["clinical_note"] for n in notes}
    _write_export_files(job_id, items, note_map)


def _write_export_files(job_id: str, items: list[ResultItem], note_map: dict[str, str]):
    """Write hpo_ids.txt and phenotypes.tsv to the job directory."""
    import csv
    jd = _job_dir(job_id)
    os.makedirs(jd, exist_ok=True)

    hpo_ids = [i.hpo_id for i in items if i.hpo_id and i.hpo_id != "No Candidate Fit"]
    with open(os.path.join(jd, "hpo_ids.txt"), "w") as f:
        f.write("\n".join(hpo_ids) + "\n")

    with open(os.path.join(jd, "phenotypes.tsv"), "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["ID", "Phenotype"])
        seen_pid = set()
        for i in items:
            if i.patient_id not in seen_pid:
                w.writerow([i.patient_id, note_map.get(i.patient_id, "")])
                seen_pid.add(i.patient_id)
