"""OpenRare full pipeline runner — orchestrates all 6 modules end-to-end.

Pattern: submit async job → poll status → download result → pass to next step.
All module URLs resolved from the project's unified MODULES config.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

import httpx

# ── Module URL config (mirrors gateway/src/gateway/main.py MODULES) ──

# ── Local config ──────────────────────────────────────────────────────

_LOCAL = {
    "RAG-HPO":          ("127.0.0.1", 8010),
    "pipeline":         ("127.0.0.1", 18901),
    "phenotype_score":  ("127.0.0.1", 7773),
    "ppi_score":        ("127.0.0.1", 9000),
    "rare_sort":        ("127.0.0.1", 5010),
    "report":           ("127.0.0.1", 8800),
}

# ponytail: remote targets. Switch back to _LOCAL after testing.
_REMOTE = {
    "RAG-HPO":          ("172.27.206.112", 9003),
    "pipeline":         ("172.27.206.113", 18901),
    "phenotype_score":  ("172.27.206.112", 7003),
    "ppi_score":        ("172.27.206.113", 9000),
    "rare_sort":        ("172.27.206.113", 5002),
    "report":           ("172.27.206.112", 8800),
}

_active_targets = _LOCAL

GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 8100
_use_gateway: bool | None = None


_remote_mode: bool = False


def set_remote(enabled: bool = True) -> None:
    global _active_targets, _remote_mode
    _active_targets = _REMOTE if enabled else _LOCAL
    _remote_mode = enabled


async def _check_gateway() -> bool:
    global _use_gateway
    if _remote_mode:  # ponytail: no local gateway in remote mode
        return False
    if _use_gateway is None:
        try:
            async with httpx.AsyncClient(trust_env=False) as c:
                r = await c.get(f"http://{GATEWAY_HOST}:{GATEWAY_PORT}/health", timeout=2.0)
                _use_gateway = r.status_code == 200
        except Exception:
            _use_gateway = False
    return _use_gateway


def module_url(name: str, path: str = "") -> str:
    host, port = _active_targets[name]
    return f"http://{host}:{port}{path}"


async def module_request(
    name: str,
    method: str,
    path: str,
    timeout: float = 120.0,
    **kwargs,
) -> httpx.Response:
    """Send a request to a module, optionally through the gateway."""
    if await _check_gateway():
        url = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}/m/{name}{path}"
    else:
        url = module_url(name, path)
    async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
        return await client.request(method, url, **kwargs)


# ── Helpers ───────────────────────────────────────────────────────────


def _json_get(data: dict | str, key: str, default: Any = "") -> Any:
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return default
    keys = key.split(".")
    for k in keys:
        if isinstance(data, dict):
            data = data.get(k)
        else:
            return default
    return data if data is not None else default


async def _poll_job(
    name: str,
    poll_url_path: str,
    status_field: str = "status",
    ready_statuses: tuple = ("completed", "completion", "done", "succeeded"),
    fail_statuses: tuple = ("failure", "failed"),
    poll_interval: float = 30.0,
    max_wait: float = 21600.0,
) -> dict:
    """Poll an async job until completion or failure. Returns the final response JSON."""
    elapsed = 0.0
    while elapsed < max_wait:
        try:
            resp = await module_request(name, "GET", poll_url_path, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            print(f"  [poll] {name} request failed: {exc}, retrying...", flush=True)
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            continue

        status = str(_json_get(data, status_field, "")).lower()
        print(f"  [poll] {name} [{elapsed:.0f}s] status={status}", flush=True)

        if status in ready_statuses:
            return data
        if status in fail_statuses:
            err = _json_get(data, "message", _json_get(data, "error", "unknown"))
            raise RuntimeError(f"{name} job failed: {err}")

        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    raise TimeoutError(f"{name} job timed out after {max_wait}s")


# ── Step 1: HPO RAG ──────────────────────────────────────────────────


async def step_hpo_rag(artifacts: dict) -> dict:
    """Extract HPO terms from symptom text. Returns {hpo_file: path, hpo_ids: [...]}."""
    symptom_text = artifacts["symptom_text"]
    output_dir = artifacts["output_dir"]

    print("\n── Step 1/6: HPO RAG ──", flush=True)
    hpo_file = os.path.join(output_dir, "hpo_terms.txt")

    payload = {
        "notes": [{"patient_id": "1", "clinical_note": symptom_text}],
    }
    resp = await module_request("RAG-HPO", "POST", "/api/v1/extract", json=payload)
    if resp.status_code >= 500:
        print(f"  WARN: HPO RAG service unavailable, creating empty HPO file", flush=True)
        Path(hpo_file).touch()
        return {"hpo_file": hpo_file, "hpo_ids": []}

    resp.raise_for_status()
    job_id = _json_get(resp.json(), "job_id")
    if not job_id:
        print(f"  WARN: no job_id from HPO RAG, creating empty HPO file", flush=True)
        Path(hpo_file).touch()
        return {"hpo_file": hpo_file, "hpo_ids": []}

    print(f"  job_id={job_id}", flush=True)

    data = await _poll_job("RAG-HPO", f"/runs/{job_id}", poll_interval=30.0)

    results = data.get("results", [])
    hpo_ids = [
        r.get("hpo_id") for r in (results or [])
        if isinstance(r, dict) and r.get("hpo_id") and r.get("hpo_id") != "No Candidate Fit"
    ]

    with open(hpo_file, "w") as f:
        f.write("\n".join(hpo_ids) + "\n" if hpo_ids else "")

    count = len(hpo_ids)
    print(f"  done: {count} HPO terms → {hpo_file}", flush=True)
    return {"hpo_file": hpo_file, "hpo_ids": hpo_ids}


# ── Step 2: VEP ──────────────────────────────────────────────────────


def _split_vcf(vcf_path: str, output_dir: str, max_variants: int = 1_000_000) -> list[str]:
    """Split a large VCF into chunks of max_variants each. Returns list of part VCF paths."""
    split_dir = os.path.join(output_dir, "vep_split_temp")
    os.makedirs(split_dir, exist_ok=True)

    header_lines = []
    variant_lines = []
    with open(vcf_path) as f:
        for line in f:
            if line.startswith("#"):
                header_lines.append(line)
            else:
                variant_lines.append(line)

    total = len(variant_lines)
    num_parts = max(1, (total + max_variants - 1) // max_variants)
    print(f"  total variants={total}, splitting into {num_parts} part(s)", flush=True)

    header = "".join(header_lines)
    part_files = []
    for i in range(num_parts):
        chunk = variant_lines[i * max_variants : (i + 1) * max_variants]
        part_path = os.path.join(split_dir, f"part_{i + 1}.vcf")
        with open(part_path, "w") as f:
            f.write(header)
            f.writelines(chunk)
        part_files.append(part_path)
        print(f"  part_{i + 1}.vcf: {len(chunk)} variants", flush=True)

    return part_files


async def step_vep(artifacts: dict) -> dict:
    """Annotate VCF with VEP + optional HPO tissue specificity. Returns {vep_csv: path}."""
    vcf_path = artifacts["vcf_path"]
    hpo_ids = artifacts.get("hpo_ids", [])
    output_dir = artifacts["output_dir"]

    print("\n── Step 2/6: VEP annotation ──", flush=True)

    part_files = _split_vcf(vcf_path, output_dir)
    all_csv_files = []

    for idx, part_vcf in enumerate(part_files, 1):
        print(f"  submitting part {idx}/{len(part_files)}: {os.path.basename(part_vcf)}", flush=True)

        # Build multipart form
        files = {"input_vcf": open(part_vcf, "rb")}
        form_data = {"hgvs": "true", "fork": "16" if hpo_ids else "8"}
        if hpo_ids:
            form_data["hpo_id"] = ",".join(hpo_ids)
            form_data["top_n_hpo_tissues"] = "3"

        resp = await module_request("pipeline", "POST", "/run-upload", files=files, data=form_data, timeout=120.0)
        files["input_vcf"].close()

        if resp.status_code >= 500:
            raise RuntimeError(f"VEP service unavailable (HTTP {resp.status_code})")

        resp.raise_for_status()
        job_id = _json_get(resp.json(), "job_id")
        if not job_id:
            raise RuntimeError(f"VEP returned no job_id: {resp.text[:500]}")

        print(f"  part {idx} job_id={job_id}", flush=True)

        await _poll_job("pipeline", f"/jobs/{job_id}", poll_interval=180.0)

        # Download result CSV
        files_resp = await module_request("pipeline", "GET", f"/jobs/{job_id}/files", timeout=30.0)
        files_data = files_resp.json()
        file_list = files_data if isinstance(files_data, list) else files_data.get("files", [])

        # Find the best CSV: prefer with_genos_evee > with_info > sorted
        csv_url = None
        for keyword in ["vep_output.with_genos_evee.csv", "vep_output.with_info.csv", "vep_output.sorted.csv"]:
            for fobj in file_list:
                rp = fobj.get("relative_path", "")
                if keyword in rp:
                    csv_url = fobj.get("download_url", "")
                    break
            if csv_url:
                break

        if not csv_url:
            raise RuntimeError(f"No VEP CSV found in job files: {files_data}")

        part_csv = os.path.join(output_dir, f"vep_output_part_{idx}.csv")
        dl_resp = await module_request("pipeline", "GET", csv_url, timeout=600.0)
        with open(part_csv, "wb") as f:
            f.write(dl_resp.content)
        print(f"  part {idx} downloaded: {os.path.getsize(part_csv)} bytes", flush=True)
        all_csv_files.append(part_csv)

    # Merge all parts
    final_csv = os.path.join(output_dir, "vep_output.csv")
    with open(final_csv, "w") as out:
        for i, csv_file in enumerate(all_csv_files):
            with open(csv_file) as f:
                if i == 0:
                    out.write(f.read())
                else:
                    f.readline()  # skip header
                    out.write(f.read())

    # Clean up
    for f in all_csv_files:
        os.remove(f)
    split_dir = os.path.join(output_dir, "vep_split_temp")
    import shutil
    shutil.rmtree(split_dir, ignore_errors=True)

    lines = sum(1 for _ in open(final_csv))
    print(f"  done: {final_csv} ({lines} lines)", flush=True)
    return {"vep_csv": final_csv}


# ── Step 3: Phenotype-HPO Score ──────────────────────────────────────


async def step_phenotype(artifacts: dict) -> dict:
    """Score genes/variants by phenotype similarity. Returns {gene_csv: path, variant_csv: path}."""
    vep_csv = artifacts.get("vep_csv")
    hpo_file = artifacts.get("hpo_file")
    output_dir = artifacts["output_dir"]

    print("\n── Step 3/6: Phenotype-HPO scoring ──", flush=True)

    if not vep_csv or not os.path.exists(vep_csv):
        print("  WARN: no VEP CSV, skipping", flush=True)
        return {"gene_csv": "", "variant_csv": ""}

    files = {}
    if os.path.exists(vep_csv):
        files["file"] = open(vep_csv, "rb")
    if hpo_file and os.path.exists(hpo_file):
        files["hpo_file"] = open(hpo_file, "rb")

    resp = await module_request("phenotype_score", "POST", "/runs", files=files, data={"hgvs": "true"}, timeout=120.0)
    for f in files.values():
        f.close()

    if resp.status_code >= 500:
        print("  WARN: Phenotype service unavailable, skipping", flush=True)
        return {"gene_csv": "", "variant_csv": ""}

    resp.raise_for_status()
    job_id = _json_get(resp.json(), "uid", _json_get(resp.json(), "job_id"))
    if not job_id:
        print("  WARN: no job_id from phenotype, skipping", flush=True)
        return {"gene_csv": "", "variant_csv": ""}

    print(f"  job_id={job_id}", flush=True)
    await _poll_job("phenotype_score", f"/runs/{job_id}", poll_interval=30.0)

    gene_csv = os.path.join(output_dir, "gene_phenotype_score.csv")
    variant_csv = os.path.join(output_dir, "variant_phenotype_score.csv")

    for name, path in [("gene_phenotype_score.csv", gene_csv), ("variant_phenotype_score.csv", variant_csv)]:
        try:
            dl = await module_request("phenotype_score", "GET", f"/runs/{job_id}/files/{name}", timeout=300.0)
            with open(path, "wb") as f:
                f.write(dl.content)
        except Exception as exc:
            print(f"  WARN: could not download {name}: {exc}", flush=True)

    print(f"  done: {gene_csv}, {variant_csv}", flush=True)
    return {"gene_csv": gene_csv, "variant_csv": variant_csv}


# ── Step 4: PPI Score ────────────────────────────────────────────────


async def step_ppi(artifacts: dict) -> dict:
    """Score with protein-protein interaction network. Returns {ppi_csv: path}."""
    gene_csv = artifacts.get("gene_csv", "")
    vep_csv = artifacts.get("vep_csv", "")
    hpo_ids = artifacts.get("hpo_ids", [])
    output_dir = artifacts["output_dir"]

    print("\n── Step 4/6: PPI network scoring ──", flush=True)

    if not gene_csv or not os.path.exists(gene_csv):
        print("  WARN: no gene phenotype CSV, skipping PPI", flush=True)
        return {"ppi_csv": ""}

    files = {}
    if os.path.exists(gene_csv):
        files["phenotype_gene_csv"] = open(gene_csv, "rb")
    if os.path.exists(vep_csv):
        files["vep_output_csv"] = open(vep_csv, "rb")

    data = {}
    if hpo_ids:
        data["hpo_ids"] = ",".join(hpo_ids)

    resp = await module_request(
        "ppi_score", "POST", "/score/clean-case/upload/async",
        files=files, data=data, timeout=120.0,
    )
    for f in files.values():
        f.close()

    if resp.status_code >= 500:
        print("  WARN: PPI service unavailable, skipping", flush=True)
        return {"ppi_csv": ""}

    resp.raise_for_status()
    job_id = _json_get(resp.json(), "job_id")
    if not job_id:
        print("  WARN: no job_id from PPI, skipping", flush=True)
        return {"ppi_csv": ""}

    print(f"  job_id={job_id}", flush=True)
    await _poll_job("ppi_score", f"/score/{job_id}", poll_interval=30.0)

    ppi_csv = os.path.join(output_dir, "ppi_score.csv")
    try:
        dl = await module_request("ppi_score", "GET", f"/score/{job_id}/csv", timeout=300.0)
        with open(ppi_csv, "wb") as f:
            f.write(dl.content)
        print(f"  done: {ppi_csv} ({os.path.getsize(ppi_csv)} bytes)", flush=True)
    except Exception as exc:
        print(f"  WARN: PPI download failed: {exc}", flush=True)
        ppi_csv = ""

    return {"ppi_csv": ppi_csv}


# ── Step 5: Ranking (rare_sort) ──────────────────────────────────────


async def step_rank(artifacts: dict) -> dict:
    """Rank variants with evolve_score + pathogenic_score. Returns {ranked_csv: path}."""
    vep_csv = artifacts.get("vep_csv", "")
    gene_csv = artifacts.get("gene_csv", "")
    ppi_csv = artifacts.get("ppi_csv", "")
    output_dir = artifacts["output_dir"]

    print("\n── Step 5/6: Variant ranking ──", flush=True)

    if not vep_csv or not os.path.exists(vep_csv):
        print("  WARN: no VEP CSV, skipping ranking", flush=True)
        return {"ranked_csv": ""}

    files = {"file": open(vep_csv, "rb")}
    if gene_csv and os.path.exists(gene_csv):
        files["gene_score_file"] = open(gene_csv, "rb")
        print(f"  with gene_score: {gene_csv}", flush=True)
    if ppi_csv and os.path.exists(ppi_csv):
        files["ppi_score_file"] = open(ppi_csv, "rb")
        print(f"  with ppi_score: {ppi_csv}", flush=True)

    resp = await module_request("rare_sort", "POST", "/score/upload", files=files, timeout=120.0)
    for f in files.values():
        f.close()

    if resp.status_code >= 500:
        print("  WARN: Ranking service unavailable, skipping", flush=True)
        return {"ranked_csv": ""}

    resp.raise_for_status()
    job_id = _json_get(resp.json(), "job_id")
    if not job_id:
        print("  WARN: no job_id from ranking, skipping", flush=True)
        return {"ranked_csv": ""}

    print(f"  job_id={job_id}", flush=True)
    await _poll_job("rare_sort", f"/status/{job_id}", poll_interval=30.0)

    ranked_csv = os.path.join(output_dir, "ranked_output.csv")
    try:
        dl = await module_request("rare_sort", "GET", f"/output/{job_id}", timeout=600.0)
        with open(ranked_csv, "wb") as f:
            f.write(dl.content)
        lines = sum(1 for _ in open(ranked_csv))
        print(f"  done: {ranked_csv} ({lines} lines)", flush=True)
    except Exception as exc:
        print(f"  WARN: ranking download failed: {exc}", flush=True)
        ranked_csv = ""

    return {"ranked_csv": ranked_csv}


# ── Step 6: Report ───────────────────────────────────────────────────


async def step_report(artifacts: dict) -> dict:
    """Generate clinical report via SSE streaming. Returns {report_md: path, report_pdf: path}."""
    ranked_csv = artifacts.get("ranked_csv", "")
    vep_csv = artifacts.get("vep_csv", "")
    gene_csv = artifacts.get("gene_csv", "")
    ppi_csv = artifacts.get("ppi_csv", "")
    hpo_file = artifacts.get("hpo_file", "")
    symptom_text = artifacts.get("symptom_text", "")
    output_dir = artifacts["output_dir"]

    print("\n── Step 6/6: Report generation ──", flush=True)

    wide_csv = ranked_csv if ranked_csv and os.path.exists(ranked_csv) else vep_csv
    print(f"  using wide table: {wide_csv}", flush=True)

    def _read(path, top_n=None):
        if not path or not os.path.exists(path):
            return None
        with open(path) as f:
            if top_n:
                header = f.readline()
                lines = [f.readline() for _ in range(top_n - 1) if f.readline()]
                return header + "".join(lines)
            return f.read()

    payload = {
        "wide": _read(wide_csv, 1000) or "",
        "hpo_file": _read(hpo_file) or "",
        "symptom_text": symptom_text,
        "top_n": 10,
        "k": 5,
    }
    phenotype_content = _read(gene_csv, 1000)
    if phenotype_content:
        payload["phenotype"] = phenotype_content
    ppi_content = _read(ppi_csv, 1000)
    if ppi_content:
        payload["ppi"] = ppi_content

    report_md = os.path.join(output_dir, "report.md")
    report_pdf = os.path.join(output_dir, "report.pdf")

    try:
        async with httpx.AsyncClient(timeout=600.0, trust_env=False) as client:
            if await _check_gateway():
                url = f"{GATEWAY_URL}/m/report/report/stream"
            else:
                url = module_url("report", "/report/stream")

            report_lines = []
            pdf_url = ""
            run_id = ""

            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            d = json.loads(line[5:].strip())
                            event_type = d.get("type", "")

                            if event_type == "meta":
                                run_id = d.get("run_id", "")
                                genes = d.get("genes", [])
                                print(f"  run_id={run_id}, genes={genes}", flush=True)
                            elif event_type == "md":
                                text = d.get("text", "")
                                if text:
                                    report_lines.append(text)
                            elif event_type == "done":
                                pdf_url = d.get("pdf_url", "")
                                if pdf_url:
                                    print(f"  PDF available: {pdf_url}", flush=True)
                        except json.JSONDecodeError:
                            pass

            if report_lines:
                with open(report_md, "w") as f:
                    f.write("".join(report_lines))
                print(f"  done: {report_md} ({len(report_lines)} chunks)", flush=True)

            if pdf_url:
                dl_resp = await client.get(
                    f"{module_url('report', pdf_url)}" if not await _check_gateway() else f"{GATEWAY_URL}/m/report{pdf_url}",
                    timeout=300.0,
                )
                with open(report_pdf, "wb") as f:
                    f.write(dl_resp.content)
                print(f"  done: {report_pdf} ({os.path.getsize(report_pdf)} bytes)", flush=True)

    except Exception as exc:
        print(f"  ERROR: report generation failed: {exc}", flush=True)

    return {"report_md": report_md, "report_pdf": report_pdf}


# ── Orchestrator ─────────────────────────────────────────────────────


PIPELINE_STEPS = [
    ("HPO_RAG", step_hpo_rag, False),        # optional: creates empty hpo file on failure
    ("VEP", step_vep, True),                  # required
    ("Phenotype", step_phenotype, False),     # optional: can skip
    ("PPI", step_ppi, False),                 # optional: can skip
    ("Rank", step_rank, False),               # optional: report falls back to VEP
    ("Report", step_report, True),            # required
]


async def run_pipeline(
    vcf_path: str,
    symptom_text: str,
    output_dir: str | None = None,
) -> dict:
    """Run the full 6-step pipeline. Returns the artifacts dict with all outputs."""
    if output_dir is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = f"./rare_disease_output_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"OpenRare Full Pipeline")
    print(f"  VCF:   {vcf_path}")
    print(f"  Text:  {symptom_text[:80]}{'...' if len(symptom_text) > 80 else ''}")
    print(f"  Out:   {output_dir}")
    print(f"{'='*60}", flush=True)

    artifacts = {
        "vcf_path": vcf_path,
        "symptom_text": symptom_text,
        "output_dir": output_dir,
    }

    for step_name, step_fn, required in PIPELINE_STEPS:
        try:
            result = await step_fn(artifacts)
            artifacts.update(result)
        except Exception as exc:
            if required:
                print(f"\nFATAL: required step '{step_name}' failed: {exc}", flush=True)
                raise
            else:
                print(f"\nWARN: optional step '{step_name}' failed: {exc}, continuing...", flush=True)
                # Set empty defaults so downstream steps don't crash
                artifacts.update({k: "" for k in _step_defaults(step_name)})

    print(f"\n{'='*60}")
    print(f"Pipeline complete.")
    print(f"  Output directory: {output_dir}")
    for key in ["hpo_file", "vep_csv", "gene_csv", "variant_csv", "ppi_csv", "ranked_csv", "report_md", "report_pdf"]:
        val = artifacts.get(key, "")
        if val and os.path.exists(val):
            size = os.path.getsize(val)
            print(f"  {key}: {val} ({size} bytes)")
    print(f"{'='*60}\n", flush=True)

    return artifacts


def _step_defaults(step_name: str) -> dict:
    """Return empty artifact defaults when an optional step is skipped."""
    defaults = {
        "HPO_RAG": {"hpo_file": "", "hpo_ids": []},
        "VEP": {"vep_csv": ""},
        "Phenotype": {"gene_csv": "", "variant_csv": ""},
        "PPI": {"ppi_csv": ""},
        "Rank": {"ranked_csv": ""},
        "Report": {"report_md": "", "report_pdf": ""},
    }
    return defaults.get(step_name, {})
