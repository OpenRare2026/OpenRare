#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FastAPI wrapper for the rare disease PPI scorer."""

import json
import os
import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import Config, DEFAULT_DATA_DIR, PROJECT_DIR, RunParameters, config_from_run_parameters, validate_run_parameters
from Network import RareDiseasePPIScorer, _read_items_file, _unique_preserve_order, normalize_hpo_ids
from run_clean_case import (
    build_final_table,
    build_phenotype_gene_summary,
    build_vep_gene_summary,
    clean_output_dir,
    select_candidate_gene_union,
)


app = FastAPI(
    title="Rare Disease Dual-Anchor PPI Scoring API",
    version="1.0.0",
    description="FastAPI service for scoring candidate genes against disease and tissue PPI anchors.",
)

_scorer_cache: Dict[str, RareDiseasePPIScorer] = {}
_cache_lock = threading.RLock()
_score_lock = threading.RLock()
_job_lock = threading.RLock()
_jobs: Dict[str, Dict[str, Any]] = {}
_job_executor = ThreadPoolExecutor(max_workers=int(os.environ.get("RARE_PPI_API_WORKERS", "1")))
DEFAULT_OUTPUT_DIR = os.environ.get("RARE_PPI_OUTPUT_DIR", os.path.join(PROJECT_DIR, "output"))
DEFAULT_UPLOAD_DIR = os.environ.get("RARE_PPI_UPLOAD_DIR", os.path.join(PROJECT_DIR, "uploads"))

STATUS_COMPLETION = "completion"
STATUS_FAILURE = "failure"
STATUS_QUEUING = "queuing"


class CleanCaseParameters(BaseModel):
    """Request model for clean final CSV case scoring."""

    model_config = ConfigDict(extra="ignore")

    data_dir: str = Field(default_factory=lambda: DEFAULT_DATA_DIR)
    phenotype_gene_csv: str
    vep_output_csv: str
    hpo_file: Optional[str] = None
    hpo_ids: List[str] = Field(default_factory=list)
    output_csv: Optional[str] = None
    clean_output_dir: bool = True
    include_audit: bool = False
    include_neighbors: bool = False
    include_evidence_json: bool = False
    output_all_ppi_fields: bool = False
    assume_hgnc_standardized: bool = True
    vep_chunksize: int = 250_000
    candidate_top_n: int = 30_000
    timeout: Optional[float] = None


def _model_dump(model: Any) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return dict(model.__dict__)


def _completion(**payload) -> Dict[str, Any]:
    return {"status": STATUS_COMPLETION, **payload}


def _failure(message: str, **payload) -> Dict[str, Any]:
    return {"status": STATUS_FAILURE, "message": message, **payload}


def _set_job_progress(job_id: str, stage: str, message: str, progress: float, **payload):
    with _job_lock:
        job = _jobs.setdefault(job_id, {"job_id": job_id, "status": STATUS_QUEUING})
        job.update({
            "stage": stage,
            "message": message,
            "progress": round(float(progress), 4),
            **payload,
        })


def _jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def _cache_key(cfg: Config) -> str:
    return json.dumps(cfg.to_dict(include_paths=False), sort_keys=True, default=str)


def _get_scorer(cfg: Config) -> RareDiseasePPIScorer:
    key = _cache_key(cfg)
    with _cache_lock:
        scorer = _scorer_cache.get(key)
        if scorer is None:
            scorer = RareDiseasePPIScorer(cfg)
            scorer.initialize()
            _scorer_cache[key] = scorer
        return scorer


def _prepare_params(params: RunParameters) -> RunParameters:
    params.candidate_genes = _unique_preserve_order(
        list(params.candidate_genes) + _read_items_file(params.candidate_gene_file)
    )
    params.hpo_ids = normalize_hpo_ids(list(params.hpo_ids) + _read_items_file(params.hpo_file), deduplicate=False)
    validate_run_parameters(params)
    return params


def _dataframe_records(df: pd.DataFrame):
    return df.where(pd.notnull(df), None).to_dict(orient="records")


def _default_csv_path() -> str:
    return os.path.join(DEFAULT_OUTPUT_DIR, f"ppi_score_{uuid.uuid4().hex}.csv")


def _default_clean_case_csv_path() -> str:
    return os.path.join(DEFAULT_OUTPUT_DIR, f"clean_case_{uuid.uuid4().hex}", "final_score.csv")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _split_form_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item for item in re.split(r"[\s,;]+", value.strip()) if item]


def _safe_upload_name(filename: Optional[str], fallback: str) -> str:
    name = os.path.basename(filename or fallback).strip() or fallback
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name or fallback


async def _save_upload(upload: UploadFile, run_dir: Path, fallback_name: str) -> str:
    upload_path = run_dir / _safe_upload_name(upload.filename, fallback_name)
    index = 1
    while upload_path.exists():
        stem = Path(upload_path.name).stem
        suffix = Path(upload_path.name).suffix
        upload_path = run_dir / f"{stem}_{index}{suffix}"
        index += 1

    with open(upload_path, "wb") as handle:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return str(upload_path)


async def _clean_case_params_from_uploads(
    *,
    phenotype_gene_csv: UploadFile,
    vep_output_csv: UploadFile,
    hpo_file: Optional[UploadFile],
    hpo_ids: Optional[str],
    data_dir: str,
    output_csv: Optional[str],
    clean_output_dir: bool,
    include_audit: bool,
    include_neighbors: bool,
    include_evidence_json: bool,
    output_all_ppi_fields: bool,
    assume_hgnc_standardized: bool,
    vep_chunksize: int,
    candidate_top_n: int,
) -> tuple[CleanCaseParameters, str]:
    run_dir = Path(DEFAULT_UPLOAD_DIR) / f"clean_case_{uuid.uuid4().hex}"
    input_dir = run_dir / "inputs"
    output_dir = run_dir / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    phenotype_path = await _save_upload(phenotype_gene_csv, input_dir, "phenotype_gene.csv")
    vep_path = await _save_upload(vep_output_csv, input_dir, "vep_output.csv")
    hpo_path = await _save_upload(hpo_file, input_dir, "hpo_ids.txt") if hpo_file is not None else None
    csv_path = output_csv or str(output_dir / "final_score.csv")
    params = CleanCaseParameters(
        data_dir=data_dir,
        phenotype_gene_csv=phenotype_path,
        vep_output_csv=vep_path,
        hpo_file=hpo_path,
        hpo_ids=_split_form_list(hpo_ids),
        output_csv=csv_path,
        clean_output_dir=clean_output_dir,
        include_audit=include_audit,
        include_neighbors=include_neighbors,
        include_evidence_json=include_evidence_json,
        output_all_ppi_fields=output_all_ppi_fields,
        assume_hgnc_standardized=assume_hgnc_standardized,
        vep_chunksize=vep_chunksize,
        candidate_top_n=candidate_top_n,
    )
    return params, str(run_dir)


async def _score_params_from_uploads(
    *,
    candidate_gene_file: UploadFile,
    hpo_file: Optional[UploadFile],
    candidate_genes: Optional[str],
    hpo_ids: Optional[str],
    data_dir: str,
    output_csv: Optional[str],
    audit_json: Optional[str],
    include_audit: bool,
    assume_hgnc_standardized: bool,
    d_min_evidence: float,
    d_fallback_evidence: float,
    d_broaden_hpo_level: int,
    t_gtex_tpm_cutoff: float,
    t_tau_cutoff: float,
    t_top_n_expr: int,
    t_pathway_top_pct: int,
    t_pathway_top_n: int,
    depmap_effect_cutoff: float,
    string_score_cutoff: int,
    k_neighbor_cap: int,
    top_n_neighbors: int,
    string_chunksize: int,
    betweenness_sample_k: int,
    sssp_cutoff: int,
    w_disease: float,
    w_tissue: float,
    w_topology: float,
    load_clinvar: bool,
) -> tuple[RunParameters, str]:
    run_dir = Path(DEFAULT_UPLOAD_DIR) / f"score_{uuid.uuid4().hex}"
    run_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = await _save_upload(candidate_gene_file, run_dir, "candidate_genes.txt")
    hpo_path = await _save_upload(hpo_file, run_dir, "hpo_ids.txt") if hpo_file is not None else None
    csv_path = output_csv or str(run_dir / "ppi_score.csv")
    audit_path = audit_json
    if include_audit and audit_path is None:
        audit_path = str(run_dir / "audit.json")
    params = RunParameters(
        data_dir=data_dir,
        candidate_genes=_split_form_list(candidate_genes),
        candidate_gene_file=candidate_path,
        hpo_ids=_split_form_list(hpo_ids),
        hpo_file=hpo_path,
        output_csv=csv_path,
        audit_json=audit_path,
        include_audit=include_audit,
        assume_hgnc_standardized=assume_hgnc_standardized,
        d_min_evidence=d_min_evidence,
        d_fallback_evidence=d_fallback_evidence,
        d_broaden_hpo_level=d_broaden_hpo_level,
        t_gtex_tpm_cutoff=t_gtex_tpm_cutoff,
        t_tau_cutoff=t_tau_cutoff,
        t_top_n_expr=t_top_n_expr,
        t_pathway_top_pct=t_pathway_top_pct,
        t_pathway_top_n=t_pathway_top_n,
        depmap_effect_cutoff=depmap_effect_cutoff,
        string_score_cutoff=string_score_cutoff,
        k_neighbor_cap=k_neighbor_cap,
        top_n_neighbors=top_n_neighbors,
        string_chunksize=string_chunksize,
        betweenness_sample_k=betweenness_sample_k,
        sssp_cutoff=sssp_cutoff,
        w_disease=w_disease,
        w_tissue=w_tissue,
        w_topology=w_topology,
        load_clinvar=load_clinvar,
    )
    return params, str(run_dir)


def _run_score(params: RunParameters) -> Dict[str, Any]:
    params = _prepare_params(params)
    if not params.candidate_genes:
        raise ValueError("candidate_genes 不能为空")

    csv_path = os.path.abspath(params.output_csv or _default_csv_path())
    cfg = config_from_run_parameters(params)
    scorer = _get_scorer(cfg)
    with _score_lock:
        df = scorer.run(
            candidate_genes=params.candidate_genes,
            hpo_ids=params.hpo_ids,
            assume_hgnc_standardized=params.assume_hgnc_standardized,
        )
        audit = json.loads(json.dumps(scorer.last_audit, ensure_ascii=False, default=str))

    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    df.to_csv(csv_path, index=False)
    if params.audit_json:
        os.makedirs(os.path.dirname(os.path.abspath(params.audit_json)), exist_ok=True)
        with open(params.audit_json, "w", encoding="utf-8") as handle:
            json.dump(audit, handle, ensure_ascii=False, indent=2)

    payload = {
        "count": int(len(df)),
        "output_format": "csv",
        "csv_path": csv_path,
        "columns": list(df.columns),
    }
    if params.include_audit:
        payload["audit"] = audit
    if params.audit_json:
        payload["audit_json"] = os.path.abspath(params.audit_json)
    return payload


def _run_score_job(job_id: str, params: RunParameters, input_dir: Optional[str] = None):
    try:
        result = _run_score(params)
        if input_dir:
            result["input_dir"] = input_dir
        with _job_lock:
            _jobs[job_id] = {"job_id": job_id, "status": STATUS_COMPLETION, **result}
    except Exception as exc:
        with _job_lock:
            _jobs[job_id] = _failure(str(exc), job_id=job_id)


def _run_clean_case(params: CleanCaseParameters, job_id: Optional[str] = None) -> Dict[str, Any]:
    if job_id:
        _set_job_progress(job_id, "prepare", "Preparing output paths", 0.02)
    output_csv = Path(params.output_csv or _default_clean_case_csv_path()).expanduser().resolve()
    if params.clean_output_dir:
        clean_output_dir(output_csv)

    if job_id:
        _set_job_progress(job_id, "read_hpo", "Reading HPO input", 0.05)
    hpo_ids = normalize_hpo_ids(list(params.hpo_ids) + _read_items_file(params.hpo_file), deduplicate=False)
    if not hpo_ids:
        raise ValueError("hpo_ids/hpo_file 不能为空")

    if job_id:
        _set_job_progress(job_id, "read_vep", "Streaming VEP CSV and aggregating genes", 0.10)
    vep_summary = build_vep_gene_summary(params.vep_output_csv, chunksize=params.vep_chunksize)
    if job_id:
        _set_job_progress(job_id, "read_phenotype", "Reading phenotype-gene CSV", 0.25, vep_gene_count=int(len(vep_summary)))
    phenotype_summary = build_phenotype_gene_summary(params.phenotype_gene_csv)
    if job_id:
        _set_job_progress(
            job_id,
            "select_candidates",
            "Selecting top candidate gene union",
            0.30,
            vep_gene_count=int(len(vep_summary)),
            phenotype_gene_count=int(len(phenotype_summary)),
        )
    candidate_genes = select_candidate_gene_union(
        vep_summary,
        phenotype_summary,
        top_n=params.candidate_top_n,
    )
    if not candidate_genes:
        raise ValueError("VEP/phenotype 输入中没有可用 gene_symbol")

    include_neighbors = params.include_neighbors or params.output_all_ppi_fields
    include_evidence_json = params.include_evidence_json or params.output_all_ppi_fields

    cfg = Config(
        data_dir=params.data_dir,
        TOP_N_NEIGHBORS=Config.TOP_N_NEIGHBORS if include_neighbors else 0,
    )
    if job_id:
        _set_job_progress(
            job_id,
            "initialize_scorer",
            "Loading cached databases and STRING graph",
            0.35,
            candidate_gene_count=int(len(candidate_genes)),
        )
    scorer = _get_scorer(cfg)
    with _score_lock:
        if job_id:
            _set_job_progress(job_id, "score_ppi", "Scoring candidate genes with PPI anchors", 0.55)
        ppi = scorer.run(
            candidate_genes=candidate_genes,
            hpo_ids=hpo_ids,
            assume_hgnc_standardized=params.assume_hgnc_standardized,
        )
        audit = scorer.last_audit

    if job_id:
        _set_job_progress(job_id, "merge_outputs", "Merging PPI, phenotype, and VEP summaries", 0.85)
    final = build_final_table(
        ppi=ppi,
        phenotype_csv=params.phenotype_gene_csv,
        vep_summary=vep_summary,
        audit=audit,
        include_neighbors=include_neighbors,
        include_evidence_json=include_evidence_json,
    )
    if job_id:
        _set_job_progress(job_id, "write_csv", "Writing final CSV", 0.95, output_rows=int(len(final)))
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(output_csv, index=False)

    payload = {
        "mode": "clean_case",
        "count": int(len(final)),
        "output_format": "csv",
        "csv_path": str(output_csv),
        "columns": list(final.columns),
        "candidate_gene_count": int(len(candidate_genes)),
        "candidate_top_n": int(params.candidate_top_n),
        "vep_top_gene_count": int(min(len(vep_summary), params.candidate_top_n) if params.candidate_top_n else len(vep_summary)),
        "phenotype_top_gene_count": int(min(len(phenotype_summary), params.candidate_top_n) if params.candidate_top_n else len(phenotype_summary)),
        "vep_chunksize": int(params.vep_chunksize),
        "include_neighbors": bool(include_neighbors),
        "include_evidence_json": bool(include_evidence_json),
        "output_all_ppi_fields": bool(params.output_all_ppi_fields),
        "hpo_count": int(len(hpo_ids)),
        "ranked_gene_count": int(final["final_rank"].notna().sum()) if "final_rank" in final else 0,
        "in_network": int(ppi["in_network"].sum()) if "in_network" in ppi else 0,
        "not_in_string": int((~ppi["in_network"]).sum()) if "in_network" in ppi else 0,
        "mapped_tissues": audit.get("mapped_tissues", []),
        "mapped_tissue_counts": audit.get("mapped_tissue_counts", {}),
    }
    if params.include_audit:
        payload["audit"] = json.loads(json.dumps(audit, ensure_ascii=False, default=str))
    return payload


def _run_clean_case_job(job_id: str, params: CleanCaseParameters, input_dir: Optional[str] = None):
    try:
        result = _run_clean_case(params, job_id=job_id)
        if input_dir:
            result["input_dir"] = input_dir
        with _job_lock:
            _jobs[job_id] = {
                **_jobs.get(job_id, {}),
                "job_id": job_id,
                "status": STATUS_COMPLETION,
                "stage": "complete",
                "message": "Job completed",
                "progress": 1.0,
                **result,
            }
    except Exception as exc:
        with _job_lock:
            _jobs[job_id] = {
                **_jobs.get(job_id, {}),
                **_failure(str(exc), job_id=job_id),
                "stage": "failure",
                "progress": _jobs.get(job_id, {}).get("progress", 0.0),
            }


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content=_failure(str(exc.detail)))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=_failure("request validation failed", errors=_jsonable(exc.errors())),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=_failure(str(exc)))


@app.get("/version")
def version():
    commit = os.environ.get("RARE_PPI_GIT_COMMIT", "")
    try:
        import subprocess

        commit = commit or subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT_DIR,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        commit = commit or "unknown"
    return _completion(
        api_version=app.version,
        git_commit=commit,
        supports_clean_case_upload=True,
        supports_progress=True,
        supports_parameters=[
            "candidate_top_n",
            "output_all_ppi_fields",
            "vep_chunksize",
            "timeout",
        ],
    )


@app.get("/health")
def health():
    cfg = Config()
    missing_files = cfg.missing_files()
    return _completion(
        data_dir=cfg.DATA_DIR,
        missing_file_count=len(missing_files),
        cached_scorer_count=len(_scorer_cache),
    )


@app.get("/config")
def get_config(include_paths: bool = True, include_missing_files: bool = False):
    cfg = Config()
    payload = cfg.to_dict(include_paths=include_paths)
    if include_missing_files:
        payload["missing_files"] = cfg.missing_files()
    return _completion(config=payload)


@app.post("/initialize")
async def initialize(params: RunParameters | None = None):
    params = params or RunParameters()
    try:
        cfg = config_from_run_parameters(params)
        await run_in_threadpool(_get_scorer, cfg)
        return _completion(data_dir=cfg.DATA_DIR)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/score")
async def score(params: RunParameters):
    try:
        result = await run_in_threadpool(_run_score, params)
        return _completion(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/score/upload")
async def score_upload(
    candidate_gene_file: UploadFile = File(...),
    hpo_file: Optional[UploadFile] = File(None),
    candidate_genes: Optional[str] = Form(None),
    hpo_ids: Optional[str] = Form(None),
    data_dir: str = Form(DEFAULT_DATA_DIR),
    output_csv: Optional[str] = Form(None),
    audit_json: Optional[str] = Form(None),
    include_audit: bool = Form(False),
    assume_hgnc_standardized: bool = Form(True),
    d_min_evidence: float = Form(Config.D_MIN_EVIDENCE),
    d_fallback_evidence: float = Form(Config.D_FALLBACK_EVIDENCE),
    d_broaden_hpo_level: int = Form(Config.D_BROADEN_HPO_LEVEL),
    t_gtex_tpm_cutoff: float = Form(Config.T_GTEX_TPM_CUTOFF),
    t_tau_cutoff: float = Form(Config.T_TAU_CUTOFF),
    t_top_n_expr: int = Form(Config.T_TOP_N_EXPR),
    t_pathway_top_pct: int = Form(Config.T_PATHWAY_TOP_PCT),
    t_pathway_top_n: int = Form(Config.T_PATHWAY_TOP_N),
    depmap_effect_cutoff: float = Form(Config.DEPMAP_EFFECT_CUTOFF),
    string_score_cutoff: int = Form(Config.STRING_SCORE_CUTOFF),
    k_neighbor_cap: int = Form(Config.K_NEIGHBOR_CAP),
    top_n_neighbors: int = Form(Config.TOP_N_NEIGHBORS),
    string_chunksize: int = Form(Config.STRING_CHUNKSIZE),
    betweenness_sample_k: int = Form(Config.BETWEENNESS_SAMPLE_K),
    sssp_cutoff: int = Form(Config.SSSP_CUTOFF),
    w_disease: float = Form(Config.W_DISEASE),
    w_tissue: float = Form(Config.W_TISSUE),
    w_topology: float = Form(Config.W_TOPOLOGY),
    load_clinvar: bool = Form(Config.LOAD_CLINVAR),
):
    try:
        params, input_dir = await _score_params_from_uploads(
            candidate_gene_file=candidate_gene_file,
            hpo_file=hpo_file,
            candidate_genes=candidate_genes,
            hpo_ids=hpo_ids,
            data_dir=data_dir,
            output_csv=output_csv,
            audit_json=audit_json,
            include_audit=include_audit,
            assume_hgnc_standardized=assume_hgnc_standardized,
            d_min_evidence=d_min_evidence,
            d_fallback_evidence=d_fallback_evidence,
            d_broaden_hpo_level=d_broaden_hpo_level,
            t_gtex_tpm_cutoff=t_gtex_tpm_cutoff,
            t_tau_cutoff=t_tau_cutoff,
            t_top_n_expr=t_top_n_expr,
            t_pathway_top_pct=t_pathway_top_pct,
            t_pathway_top_n=t_pathway_top_n,
            depmap_effect_cutoff=depmap_effect_cutoff,
            string_score_cutoff=string_score_cutoff,
            k_neighbor_cap=k_neighbor_cap,
            top_n_neighbors=top_n_neighbors,
            string_chunksize=string_chunksize,
            betweenness_sample_k=betweenness_sample_k,
            sssp_cutoff=sssp_cutoff,
            w_disease=w_disease,
            w_tissue=w_tissue,
            w_topology=w_topology,
            load_clinvar=load_clinvar,
        )
        result = await run_in_threadpool(_run_score, params)
        return _completion(input_dir=input_dir, **result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/score/clean-case")
async def score_clean_case(params: CleanCaseParameters):
    try:
        result = await run_in_threadpool(_run_clean_case, params)
        return _completion(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/score/clean-case/upload")
async def score_clean_case_upload(
    phenotype_gene_csv: UploadFile = File(...),
    vep_output_csv: UploadFile = File(...),
    hpo_file: Optional[UploadFile] = File(None),
    hpo_ids: Optional[str] = Form(None),
    data_dir: str = Form(DEFAULT_DATA_DIR),
    output_csv: Optional[str] = Form(None),
    clean_output_dir: bool = Form(True),
    include_audit: bool = Form(False),
    include_neighbors: bool = Form(False),
    include_evidence_json: bool = Form(False),
    output_all_ppi_fields: bool = Form(False),
    assume_hgnc_standardized: bool = Form(True),
    vep_chunksize: int = Form(250_000),
    candidate_top_n: int = Form(30_000),
):
    try:
        params, input_dir = await _clean_case_params_from_uploads(
            phenotype_gene_csv=phenotype_gene_csv,
            vep_output_csv=vep_output_csv,
            hpo_file=hpo_file,
            hpo_ids=hpo_ids,
            data_dir=data_dir,
            output_csv=output_csv,
            clean_output_dir=clean_output_dir,
            include_audit=include_audit,
            include_neighbors=include_neighbors,
            include_evidence_json=include_evidence_json,
            output_all_ppi_fields=output_all_ppi_fields,
            assume_hgnc_standardized=assume_hgnc_standardized,
            vep_chunksize=vep_chunksize,
            candidate_top_n=candidate_top_n,
        )
        result = await run_in_threadpool(_run_clean_case, params)
        return _completion(input_dir=input_dir, **result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/score/async")
def score_async(params: RunParameters):
    job_id = str(uuid.uuid4())
    with _job_lock:
        _jobs[job_id] = {"job_id": job_id, "status": STATUS_QUEUING}
    _job_executor.submit(_run_score_job, job_id, params)
    return {"job_id": job_id, "status": STATUS_QUEUING}


@app.post("/score/upload/async")
async def score_upload_async(
    candidate_gene_file: UploadFile = File(...),
    hpo_file: Optional[UploadFile] = File(None),
    candidate_genes: Optional[str] = Form(None),
    hpo_ids: Optional[str] = Form(None),
    data_dir: str = Form(DEFAULT_DATA_DIR),
    output_csv: Optional[str] = Form(None),
    audit_json: Optional[str] = Form(None),
    include_audit: bool = Form(False),
    assume_hgnc_standardized: bool = Form(True),
    d_min_evidence: float = Form(Config.D_MIN_EVIDENCE),
    d_fallback_evidence: float = Form(Config.D_FALLBACK_EVIDENCE),
    d_broaden_hpo_level: int = Form(Config.D_BROADEN_HPO_LEVEL),
    t_gtex_tpm_cutoff: float = Form(Config.T_GTEX_TPM_CUTOFF),
    t_tau_cutoff: float = Form(Config.T_TAU_CUTOFF),
    t_top_n_expr: int = Form(Config.T_TOP_N_EXPR),
    t_pathway_top_pct: int = Form(Config.T_PATHWAY_TOP_PCT),
    t_pathway_top_n: int = Form(Config.T_PATHWAY_TOP_N),
    depmap_effect_cutoff: float = Form(Config.DEPMAP_EFFECT_CUTOFF),
    string_score_cutoff: int = Form(Config.STRING_SCORE_CUTOFF),
    k_neighbor_cap: int = Form(Config.K_NEIGHBOR_CAP),
    top_n_neighbors: int = Form(Config.TOP_N_NEIGHBORS),
    string_chunksize: int = Form(Config.STRING_CHUNKSIZE),
    betweenness_sample_k: int = Form(Config.BETWEENNESS_SAMPLE_K),
    sssp_cutoff: int = Form(Config.SSSP_CUTOFF),
    w_disease: float = Form(Config.W_DISEASE),
    w_tissue: float = Form(Config.W_TISSUE),
    w_topology: float = Form(Config.W_TOPOLOGY),
    load_clinvar: bool = Form(Config.LOAD_CLINVAR),
):
    try:
        params, input_dir = await _score_params_from_uploads(
            candidate_gene_file=candidate_gene_file,
            hpo_file=hpo_file,
            candidate_genes=candidate_genes,
            hpo_ids=hpo_ids,
            data_dir=data_dir,
            output_csv=output_csv,
            audit_json=audit_json,
            include_audit=include_audit,
            assume_hgnc_standardized=assume_hgnc_standardized,
            d_min_evidence=d_min_evidence,
            d_fallback_evidence=d_fallback_evidence,
            d_broaden_hpo_level=d_broaden_hpo_level,
            t_gtex_tpm_cutoff=t_gtex_tpm_cutoff,
            t_tau_cutoff=t_tau_cutoff,
            t_top_n_expr=t_top_n_expr,
            t_pathway_top_pct=t_pathway_top_pct,
            t_pathway_top_n=t_pathway_top_n,
            depmap_effect_cutoff=depmap_effect_cutoff,
            string_score_cutoff=string_score_cutoff,
            k_neighbor_cap=k_neighbor_cap,
            top_n_neighbors=top_n_neighbors,
            string_chunksize=string_chunksize,
            betweenness_sample_k=betweenness_sample_k,
            sssp_cutoff=sssp_cutoff,
            w_disease=w_disease,
            w_tissue=w_tissue,
            w_topology=w_topology,
            load_clinvar=load_clinvar,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    job_id = str(uuid.uuid4())
    with _job_lock:
        _jobs[job_id] = {"job_id": job_id, "status": STATUS_QUEUING, "input_dir": input_dir}
    _job_executor.submit(_run_score_job, job_id, params, input_dir)
    return {"job_id": job_id, "status": STATUS_QUEUING, "input_dir": input_dir}


@app.post("/score/clean-case/async")
def score_clean_case_async(params: CleanCaseParameters):
    job_id = str(uuid.uuid4())
    with _job_lock:
        _jobs[job_id] = {"job_id": job_id, "status": STATUS_QUEUING, "mode": "clean_case"}
    _job_executor.submit(_run_clean_case_job, job_id, params)
    return {"job_id": job_id, "status": STATUS_QUEUING, "mode": "clean_case"}


@app.post("/score/clean-case/upload/async")
async def score_clean_case_upload_async(
    phenotype_gene_csv: UploadFile = File(...),
    vep_output_csv: UploadFile = File(...),
    hpo_file: Optional[UploadFile] = File(None),
    hpo_ids: Optional[str] = Form(None),
    data_dir: str = Form(DEFAULT_DATA_DIR),
    output_csv: Optional[str] = Form(None),
    clean_output_dir: bool = Form(True),
    include_audit: bool = Form(False),
    include_neighbors: bool = Form(False),
    include_evidence_json: bool = Form(False),
    output_all_ppi_fields: bool = Form(False),
    assume_hgnc_standardized: bool = Form(True),
    vep_chunksize: int = Form(250_000),
    candidate_top_n: int = Form(30_000),
):
    try:
        params, input_dir = await _clean_case_params_from_uploads(
            phenotype_gene_csv=phenotype_gene_csv,
            vep_output_csv=vep_output_csv,
            hpo_file=hpo_file,
            hpo_ids=hpo_ids,
            data_dir=data_dir,
            output_csv=output_csv,
            clean_output_dir=clean_output_dir,
            include_audit=include_audit,
            include_neighbors=include_neighbors,
            include_evidence_json=include_evidence_json,
            output_all_ppi_fields=output_all_ppi_fields,
            assume_hgnc_standardized=assume_hgnc_standardized,
            vep_chunksize=vep_chunksize,
            candidate_top_n=candidate_top_n,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    job_id = str(uuid.uuid4())
    with _job_lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": STATUS_QUEUING,
            "mode": "clean_case",
            "input_dir": input_dir,
        }
    _job_executor.submit(_run_clean_case_job, job_id, params, input_dir)
    return {"job_id": job_id, "status": STATUS_QUEUING, "mode": "clean_case", "input_dir": input_dir}


@app.get("/score/{job_id}")
def get_score_job(job_id: str):
    with _job_lock:
        job = _jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"job_id 不存在: {job_id}")
        return dict(job)


@app.get("/score/{job_id}/csv")
def download_score_csv(job_id: str):
    with _job_lock:
        job = _jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"job_id 不存在: {job_id}")
        if job.get("status") == STATUS_QUEUING:
            raise HTTPException(status_code=202, detail="任务仍在等待或运行")
        if job.get("status") == STATUS_FAILURE:
            raise HTTPException(status_code=400, detail=job.get("message", "任务失败"))
        csv_path = job.get("csv_path")
    if not csv_path or not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="CSV 文件不存在")
    return FileResponse(csv_path, media_type="text/csv", filename=os.path.basename(csv_path))
