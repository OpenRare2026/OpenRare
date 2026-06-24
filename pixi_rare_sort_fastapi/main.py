"""ponytail: FastAPI wrapper — file upload + async job queue (in-memory dict)."""
from __future__ import annotations

import os, uuid, threading, time, tempfile
from pathlib import Path

from fastapi import FastAPI, Query, UploadFile, File, HTTPException
import uvicorn

from pipeline import run

app = FastAPI(title="rare_sort")

# ponytail: in-memory dict, lost on restart. Replace with sqlite/redis if persistence matters.
jobs: dict[str, dict] = {}


def _run_job(job_id: str, input_path: str, gene_score_csv: str | None = None,
             ppi_score_csv: str | None = None):
    jobs[job_id]["status"] = "running"
    jobs[job_id]["started_at"] = time.time()
    try:
        output = Path(tempfile.mkdtemp()) / "ranked.csv"
        result_path = run(input_path, str(output),
                          gene_score_csv=gene_score_csv,
                          ppi_score_csv=ppi_score_csv)
        jobs[job_id]["status"] = "done"
        jobs[job_id]["output"] = result_path
        jobs[job_id]["elapsed"] = time.time() - jobs[job_id]["started_at"]
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/score")
def score_path(input_path: str = Query(..., description="CSV/Parquet path on server"),
               gene_score_path: str | None = Query(None, description="gene_phenotype_score.csv path (optional)"),
               ppi_score_path: str | None = Query(None, description="ppi_score.csv path (optional)")):
    if not os.path.exists(input_path):
        raise HTTPException(404, f"input not found: {input_path}")
    if gene_score_path and not os.path.exists(gene_score_path):
        raise HTTPException(404, f"gene_score file not found: {gene_score_path}")
    if ppi_score_path and not os.path.exists(ppi_score_path):
        raise HTTPException(404, f"ppi_score file not found: {ppi_score_path}")
    job_id = uuid.uuid4().hex[:8]
    jobs[job_id] = {"status": "queued", "input": input_path, "created_at": time.time(),
                    "gene_score_path": gene_score_path, "ppi_score_path": ppi_score_path}
    threading.Thread(target=_run_job, args=(job_id, input_path, gene_score_path, ppi_score_path), daemon=True).start()
    return {"job_id": job_id, "status": "queued"}


@app.post("/score/upload")
async def score_upload(file: UploadFile = File(...),
                       gene_score_file: UploadFile | None = None,
                       ppi_score_file: UploadFile | None = None):
    tmpdir = tempfile.mkdtemp()
    input_path = os.path.join(tmpdir, file.filename or "upload.csv")
    with open(input_path, "wb") as f:
        while chunk := await file.read(8 * 1024 * 1024):
            f.write(chunk)

    gene_score_path = None
    if gene_score_file:
        gene_score_path = os.path.join(tmpdir, gene_score_file.filename or "gene_score.csv")
        with open(gene_score_path, "wb") as f:
            while chunk := await gene_score_file.read(8 * 1024 * 1024):
                f.write(chunk)

    ppi_score_path = None
    if ppi_score_file:
        ppi_score_path = os.path.join(tmpdir, ppi_score_file.filename or "ppi_score.csv")
        with open(ppi_score_path, "wb") as f:
            while chunk := await ppi_score_file.read(8 * 1024 * 1024):
                f.write(chunk)

    job_id = uuid.uuid4().hex[:8]
    jobs[job_id] = {"status": "queued", "input": input_path, "filename": file.filename, "created_at": time.time()}
    threading.Thread(target=_run_job, args=(job_id, input_path, gene_score_path, ppi_score_path), daemon=True).start()
    return {"job_id": job_id, "status": "queued", "filename": file.filename}


@app.get("/status/{job_id}")
def job_status(job_id: str):
    j = jobs.get(job_id)
    if not j:
        raise HTTPException(404, f"job not found: {job_id}")
    return j


@app.get("/jobs")
def list_jobs():
    return {k: {"status": v["status"], "input": v.get("input"), "filename": v.get("filename")} for k, v in jobs.items()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
