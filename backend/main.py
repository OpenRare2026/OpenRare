from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from backend.config import ApiConfig, ROOT
from backend.job_manager import read_status

app = FastAPI(title=ApiConfig.title, version=ApiConfig.version)

# Register routers
from backend.routers import phasing, preprocessing, pseudogene, vep, vcf_info_to_csv, sorting, pipeline

app.include_router(phasing.router)
app.include_router(preprocessing.router)
app.include_router(pseudogene.router)
app.include_router(vep.router)
app.include_router(vcf_info_to_csv.router)
app.include_router(sorting.router)
app.include_router(pipeline.router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": ApiConfig.version,
        "root": str(ROOT),
        "endpoints": {
            "phasing": "/api/v1/phasing",
            "preprocessing": "/api/v1/preprocessing",
            "pseudogene": "/api/v1/pseudogene",
            "vep": "/api/v1/vep",
            "vcf_info_to_csv": "/api/v1/vcf-info-to-csv",
            "sort": "/api/v1/sort",
            "pipeline": "/api/v1/pipeline",
            "pipeline_upload": "/api/v1/pipeline/upload",
        },
        "jobs_dir": str(ApiConfig.jobs_dir),
    }


@app.get("/api/v1/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    return read_status(job_id)


@app.get("/api/v1/jobs/{job_id}/log")
def get_job_log(job_id: str) -> PlainTextResponse:
    import json
    from pathlib import Path

    status = read_status(job_id)
    log_path = Path(status.get("log", str(ApiConfig.jobs_dir / job_id / "run.log")))
    if not log_path.is_file():
        raise HTTPException(status_code=404, detail="log not found")
    return PlainTextResponse(log_path.read_text(encoding="utf-8", errors="replace"))
