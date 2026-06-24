"""rare_sort scoring pipeline — CSV/Parquet → ranked CSV.

Usage:
    python pipeline.py input.csv [--output ranked.csv]
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

import dataio
from dataio import available_engines, iter_chunks

from rare_sort import default_registry, needed_columns, theta_keys, FeatureBundle, apply_theta
from rare_sort._util import variant_key, to_int
from rare_sort.scorer import rank_units


# ponytail: tuned theta from P12 v2 (LLMProposer, 2026-06-18)
P12_V2_THETA = {
    "clinvar_score": 1.291,
    "consequence_score": 1.101,
    "splice_lof_score": 2.027,
    "prediction_score": 0.497,
    "frequency_score": 0.210,
    "domain_score": 3.661,
}


def run(input_path: str, output_csv: str | None = None, chunksize: int = 250_000,
        gene_score_csv: str | None = None, ppi_score_csv: str | None = None):
    t0 = time.time()
    reg = default_registry()
    theta = P12_V2_THETA
    proj_cols = needed_columns(reg)

    eng = available_engines()[0]
    fmt = "parquet" if input_path.lower().endswith((".parquet", ".pq")) else "csv"
    print(f"[pipeline] engine: {eng}  format: {fmt}")
    print(f"[pipeline] input : {input_path}")
    print(f"[pipeline] registry: {theta_keys(reg)}")

    # ── PASS 1: project + score → vkey→(score,rank) lookup ──────────
    print("[pass 1] scoring with column projection + selected_tx_only ...", flush=True)
    F_parts, idx_parts = [], []
    total, kept = 0, 0

    pass1_engine = "pandas" if fmt == "csv" else eng
    for chunk in iter_chunks(input_path, proj_cols, engine=pass1_engine, fmt=fmt,
                             selected_tx_only=True, chunk_rows=chunksize):
        total += len(chunk)
        chunk = chunk.fillna("-")
        recs = chunk.to_dict("records")
        n, m = len(recs), len(reg)
        F = np.zeros((n, m), dtype=float)
        for j, c in enumerate(reg):
            cal = c.calibrate
            F[:, j] = [cal(r) for r in recs]
        idx = pd.DataFrame({
            "_order": np.arange(kept, kept + n),
            "_vkey": [variant_key(r.get("chrom"), r.get("pos"), r.get("ref"), r.get("alt"))
                      for r in recs],
            "gene_symbol": [r.get("gene_symbol") for r in recs],
        })
        if "tx_rank_within_variant" in chunk.columns:
            idx["tx_rank"] = [to_int(r.get("tx_rank_within_variant")) for r in recs]
        F_parts.append(F)
        idx_parts.append(idx)
        kept += n
        if kept % 2_000_000 < chunksize:
            print(f"  [{time.strftime('%H:%M:%S')}] {kept:,} rows scored "
                  f"({time.time()-t0:.0f}s)", flush=True)

    print(f"[pass 1] {kept:,} rows → assembling features ({time.time()-t0:.0f}s)", flush=True)
    F = np.vstack(F_parts) if len(F_parts) > 1 else F_parts[0]
    idx_all = pd.concat(idx_parts, ignore_index=True)

    bundle = FeatureBundle(F=F, keys=theta_keys(reg),
                           kinds=[c.kind for c in reg],
                           groups=[c.group for c in reg], index=idx_all)
    scores = apply_theta(bundle, theta)
    ranked = rank_units(bundle, scores, level="variant", collapse="auto")
    print(f"[pass 1] ranked {len(ranked):,} variants ({time.time()-t0:.0f}s)", flush=True)

    lookup_rows = []
    for _, r in ranked.iterrows():
        vk = r["_unit"]
        lookup_rows.append({
            "_vkey": f"{vk[0]}:{vk[1]}:{vk[2]}:{vk[3]}",
            "evolve_score": float(r["score"]),
            "evolve_rank": int(r["rank"]),
        })
    lookup_df = pd.DataFrame(lookup_rows)
    tmpdir = tempfile.mkdtemp()
    lookup_path = f"{tmpdir}/scores.parquet"
    lookup_df.to_parquet(lookup_path, index=False)
    print(f"[pass 1] score lookup: {len(lookup_df):,} entries → {lookup_path} "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ── PASS 2: duckdb SQL — filter, join, sort, export ──────────
    if output_csv is None:
        stem = Path(input_path).stem
        output_csv = str(Path(input_path).parent / f"{stem}.ranked.csv")
    else:
        output_csv = str(output_csv)

    print(f"[pass 2] duckdb sort+join → {output_csv}", flush=True)
    import duckdb
    con = duckdb.connect()

    vk_expr = ("regexp_replace(CAST(chrom AS VARCHAR), '^[Cc][Hh][Rr]', '') || ':' || "
               "CAST(pos AS VARCHAR) || ':' || "
               "upper(CAST(ref AS VARCHAR)) || ':' || "
               "upper(CAST(alt AS VARCHAR))")

    if fmt == "csv":
        src = (f"read_csv_auto('{input_path.replace(chr(39), chr(39)+chr(39))}', "
               f"all_varchar=true, null_padding=true, ignore_errors=true, sample_size=-1)")
    else:
        src = f"read_parquet('{input_path.replace(chr(39), chr(39)+chr(39))}')"

    schema_rows = con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()
    schema_cols = [r[0] for r in schema_rows]
    has_tx = "tx_rank_within_variant" in schema_cols

    all_cols = [f'"{c}"' for c in schema_cols]
    proj = ", ".join(all_cols)
    proj_with_key = f"{proj}, {vk_expr} AS _vkey"

    where = ""
    if has_tx:
        where = "WHERE (CAST(tx_rank_within_variant AS VARCHAR) = '1' OR tx_rank_within_variant IS NULL)"

    con.execute(f"CREATE OR REPLACE TABLE scores AS SELECT * FROM read_parquet('{lookup_path}')")

    # ── optional gene-level score tables ──
    pathogenic_expr = "s.evolve_score"
    extra_joins = ""
    extra_cols = ""

    if gene_score_csv and os.path.exists(gene_score_csv):
        gs_src = f"read_csv_auto('{gene_score_csv.replace(chr(39), chr(39)+chr(39))}', all_varchar=true)"
        con.execute(f"CREATE OR REPLACE TABLE gene_scores AS SELECT gene_symbol, CAST(gene_score AS DOUBLE) AS gene_score FROM {gs_src}")
        extra_joins += "\n        LEFT JOIN gene_scores gs ON src.gene_symbol = gs.gene_symbol"
        pathogenic_expr = f"s.evolve_score * SQRT(COALESCE(gs.gene_score, 0))"
        extra_cols += ", gs.gene_score"
        print("[pass 2] gene_score table loaded", flush=True)

    if ppi_score_csv and os.path.exists(ppi_score_csv):
        ppi_src = f"read_csv_auto('{ppi_score_csv.replace(chr(39), chr(39)+chr(39))}', all_varchar=true)"
        con.execute(f"CREATE OR REPLACE TABLE ppi_scores AS SELECT gene, CAST(ppi_final AS DOUBLE) AS ppi_final FROM {ppi_src}")
        extra_joins += "\n        LEFT JOIN ppi_scores ppi ON src.gene_symbol = ppi.gene"
        pathogenic_expr = f"({pathogenic_expr}) * SQRT(COALESCE(ppi.ppi_final, 0))"
        extra_cols += ", ppi.ppi_final"
        print("[pass 2] ppi_score table loaded", flush=True)

    has_pathogenic = bool(gene_score_csv or ppi_score_csv)

    q = f"""
    COPY (
        SELECT src.*, s.evolve_score, s.evolve_rank{extra_cols},
               {pathogenic_expr} AS pathogenic_score,
               ROW_NUMBER() OVER (ORDER BY {pathogenic_expr} DESC NULLS LAST) AS pathogenic_rank
        FROM (SELECT {proj_with_key} FROM {src} {where}) src
        LEFT JOIN scores s ON src._vkey = s._vkey{extra_joins}
        ORDER BY pathogenic_score DESC NULLS LAST
    ) TO '{output_csv}' (HEADER, DELIMITER ',');
    """
    print(f"[pass 2] executing SQL sort+join+export ...", flush=True)
    con.execute(q)
    con.close()

    total_time = time.time() - t0
    print(f"[pipeline] done: {output_csv} ({total_time:.0f}s = {total_time/60:.1f} min)", flush=True)

    verify_cols = ["evolve_score", "evolve_rank"]
    if has_pathogenic:
        verify_cols += ["pathogenic_score", "pathogenic_rank"]
    if gene_score_csv and os.path.exists(gene_score_csv):
        verify_cols.append("gene_score")
    verify = pd.read_csv(output_csv, nrows=5, usecols=verify_cols)
    for c in verify_cols:
        print(f"  top {c}: {list(verify[c])}", flush=True)

    return output_csv


def main():
    ap = argparse.ArgumentParser(description="rare_sort scoring pipeline (optimized)")
    ap.add_argument("input_path", help="VEP CSV or Parquet file")
    ap.add_argument("--output", "-o", default=None, help="output CSV path")
    ap.add_argument("--chunksize", type=int, default=250_000,
                    help="rows per chunk (default 250k)")
    ap.add_argument("--gene-score", default=None, help="gene_phenotype_score.csv path")
    ap.add_argument("--ppi-score", default=None, help="ppi_score.csv path")
    args = ap.parse_args()
    run(args.input_path, args.output, args.chunksize, args.gene_score, args.ppi_score)


if __name__ == "__main__":
    main()
