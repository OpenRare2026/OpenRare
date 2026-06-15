#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean final CSV runner for phenotype + VEP + HPO case inputs.

This wrapper keeps intermediate data in memory and writes only the requested
final CSV. Gene names in the output remain the input VEP gene symbols.
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd

from Network import RareDiseasePPIScorer, normalize_hpo_ids
from config import Config, DEFAULT_DATA_DIR, PROJECT_DIR, SCRIPT_DIR


def _clean_str(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _read_items_file(path: str) -> List[str]:
    items = []
    with open(path, encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            items.extend(x for x in re.split(r"[\s,;]+", line) if x)
    return items


def _unique_preserve_order(values: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def build_vep_gene_summary(vep_csv: str, chunksize: int = 250_000) -> pd.DataFrame:
    header = pd.read_csv(vep_csv, nrows=0)
    if "gene_symbol" not in header.columns:
        raise ValueError(f"VEP CSV missing gene_symbol column: {vep_csv}")

    has_rank = "pathogenic_rank" in header.columns
    has_cadd = "cadd_phred" in header.columns
    usecols = ["gene_symbol"]
    if has_rank:
        usecols.append("pathogenic_rank")
    if has_cadd:
        usecols.append("cadd_phred")

    stats: Dict[str, Dict[str, Any]] = {}
    reader = pd.read_csv(
        vep_csv,
        usecols=usecols,
        chunksize=max(int(chunksize), 1),
        low_memory=True,
    )
    for chunk in reader:
        chunk["gene_symbol"] = chunk["gene_symbol"].map(_clean_str)
        chunk = chunk[(chunk["gene_symbol"] != "") & (chunk["gene_symbol"] != "-")]
        if chunk.empty:
            continue

        if has_rank:
            chunk["pathogenic_rank_num"] = pd.to_numeric(chunk["pathogenic_rank"], errors="coerce")
        else:
            chunk["pathogenic_rank_num"] = pd.NA
        if has_cadd:
            chunk["cadd_phred_num"] = pd.to_numeric(chunk["cadd_phred"], errors="coerce")
        else:
            chunk["cadd_phred_num"] = pd.NA

        grouped = chunk.groupby("gene_symbol", sort=False).agg(
            variant_row_count=("gene_symbol", "size"),
            best_pathogenic_rank=("pathogenic_rank_num", "min"),
            max_cadd_phred=("cadd_phred_num", "max"),
        )
        for gene, row in grouped.iterrows():
            current = stats.setdefault(
                gene,
                {
                    "variant_row_count": 0,
                    "best_pathogenic_rank": pd.NA,
                    "max_cadd_phred": pd.NA,
                },
            )
            current["variant_row_count"] += int(row["variant_row_count"])
            rank = row["best_pathogenic_rank"]
            if pd.notna(rank):
                if pd.isna(current["best_pathogenic_rank"]) or float(rank) < float(current["best_pathogenic_rank"]):
                    current["best_pathogenic_rank"] = float(rank)
            cadd = row["max_cadd_phred"]
            if pd.notna(cadd):
                if pd.isna(current["max_cadd_phred"]) or float(cadd) > float(current["max_cadd_phred"]):
                    current["max_cadd_phred"] = float(cadd)

    if not stats:
        raise ValueError("VEP CSV has no usable gene_symbol values")

    summary = pd.DataFrame(
        {"gene_symbol": gene, **values}
        for gene, values in stats.items()
    )
    summary["_rank_sort"] = pd.to_numeric(summary["best_pathogenic_rank"], errors="coerce").fillna(10**9)
    summary = summary.sort_values(
        ["_rank_sort", "variant_row_count", "gene_symbol"],
        ascending=[True, False, True],
    ).drop(columns=["_rank_sort"])
    return summary.reset_index(drop=True)


def build_phenotype_gene_summary(phenotype_csv: str) -> pd.DataFrame:
    header = pd.read_csv(phenotype_csv, nrows=0)
    if "gene_symbol" not in header.columns:
        raise ValueError(f"phenotype-gene CSV missing gene_symbol column: {phenotype_csv}")
    usecols = ["gene_symbol"]
    for col in ("gene_score", "gene_rank"):
        if col in header.columns:
            usecols.append(col)
    phenotype = pd.read_csv(phenotype_csv, usecols=usecols)
    phenotype["gene_symbol"] = phenotype["gene_symbol"].map(_clean_str)
    phenotype = phenotype[(phenotype["gene_symbol"] != "") & (phenotype["gene_symbol"] != "-")]
    if phenotype.empty:
        return pd.DataFrame(columns=["gene_symbol"])
    if "gene_rank" in phenotype.columns:
        phenotype["gene_rank_num"] = pd.to_numeric(phenotype["gene_rank"], errors="coerce")
    else:
        phenotype["gene_rank_num"] = pd.NA
    if "gene_score" in phenotype.columns:
        phenotype["gene_score_num"] = pd.to_numeric(phenotype["gene_score"], errors="coerce")
    else:
        phenotype["gene_score_num"] = pd.NA
    summary = phenotype.groupby("gene_symbol", as_index=False).agg(
        best_gene_rank=("gene_rank_num", "min"),
        best_gene_score=("gene_score_num", "max"),
    )
    summary["_rank_sort"] = pd.to_numeric(summary["best_gene_rank"], errors="coerce").fillna(10**9)
    summary["_score_sort"] = pd.to_numeric(summary["best_gene_score"], errors="coerce").fillna(-10**9)
    summary = summary.sort_values(
        ["_rank_sort", "_score_sort", "gene_symbol"],
        ascending=[True, False, True],
    ).drop(columns=["_rank_sort", "_score_sort"])
    return summary.reset_index(drop=True)


def select_candidate_gene_union(
    vep_summary: pd.DataFrame,
    phenotype_summary: pd.DataFrame,
    top_n: int = 30_000,
) -> List[str]:
    limit = max(int(top_n), 0)
    if limit == 0:
        vep_genes = vep_summary["gene_symbol"].astype(str).tolist()
        phenotype_genes = phenotype_summary["gene_symbol"].astype(str).tolist()
    else:
        vep_genes = vep_summary.head(limit)["gene_symbol"].astype(str).tolist()
        phenotype_genes = phenotype_summary.head(limit)["gene_symbol"].astype(str).tolist()
    return _unique_preserve_order(vep_genes + phenotype_genes)


def clean_output_dir(output_csv: Path):
    """Remove old output artifacts so the directory contains only final CSV."""
    output_dir = output_csv.parent
    if not output_dir.exists():
        return
    protected = {
        Path("/").resolve(),
        Path(PROJECT_DIR).resolve(),
        Path(SCRIPT_DIR).resolve(),
    }
    if output_dir.resolve() in protected:
        raise ValueError(f"refuse to clean protected output directory: {output_dir}")
    for child in output_dir.iterdir():
        if child.resolve() == output_csv.resolve():
            continue
        if child.is_file():
            child.unlink()


def build_final_table(
    ppi: pd.DataFrame,
    phenotype_csv: str,
    vep_summary: pd.DataFrame,
    audit: Dict[str, Any],
    include_neighbors: bool = False,
    include_evidence_json: bool = False,
) -> pd.DataFrame:
    phenotype_header = pd.read_csv(phenotype_csv, nrows=0)
    if "gene_symbol" not in phenotype_header.columns:
        raise ValueError(f"phenotype-gene CSV missing gene_symbol column: {phenotype_csv}")

    ppi = ppi.sort_values("ppi_final", ascending=False).reset_index(drop=True)
    ppi["ppi_rank"] = ppi.index + 1

    phenotype_columns = [
        "gene_symbol",
        "gene_score",
        "gene_rank",
        "conclusion_code",
        "best_disease_score",
        "best_disease_name",
        "best_omim_id",
        "best_orpha_id",
        "best_mondo_id",
        "best_disease_match_status",
        "mapping_basis",
    ]
    phenotype_columns = [col for col in phenotype_columns if col in phenotype_header.columns]
    phenotype = pd.read_csv(phenotype_csv, usecols=phenotype_columns)

    merged = ppi.merge(phenotype[phenotype_columns], left_on="gene", right_on="gene_symbol", how="left")
    if "gene_symbol" in merged.columns:
        merged = merged.drop(columns=["gene_symbol"])

    merged = merged.merge(
        vep_summary[["gene_symbol", "best_pathogenic_rank", "variant_row_count", "max_cadd_phred"]],
        left_on="gene",
        right_on="gene_symbol",
        how="left",
    ).drop(columns=["gene_symbol"])

    merged["gene_score"] = pd.to_numeric(merged.get("gene_score"), errors="coerce")
    merged["ppi_final"] = pd.to_numeric(merged.get("ppi_final"), errors="coerce")
    merged["has_phenotype_score"] = merged["gene_score"].notna()
    rankable = merged["has_phenotype_score"] & merged["in_network"].astype(bool)

    merged["combined_score"] = pd.NA
    merged.loc[rankable, "combined_score"] = (
        merged.loc[rankable, "gene_score"] + merged.loc[rankable, "ppi_final"]
    ) / 2

    merged["final_rank"] = pd.NA
    ranked_idx = merged[rankable].sort_values(
        ["combined_score", "gene_score", "ppi_final"],
        ascending=False,
    ).index
    merged.loc[ranked_idx, "final_rank"] = range(1, len(ranked_idx) + 1)

    merged["mapped_tissues"] = ",".join(audit.get("mapped_tissues", []))
    merged["mapped_tissue_counts_json"] = json.dumps(audit.get("mapped_tissue_counts", {}), ensure_ascii=False)

    columns = [
        "final_rank",
        "gene",
        "combined_score",
        "gene_score",
        "ppi_final",
        "in_network",
        "disease_score",
        "tissue_score",
        "topology_score",
        "score_mode",
        "score_weight_sum",
        "note",
        "gene_in_d",
        "gene_d_evidence_score",
        "gene_d_sources_json",
        "gene_in_t",
        "gene_t_weight",
        "gene_t_layers_json",
        "gene_t_tissues_json",
        "mapped_tissues_json",
        "d_gene_count",
        "t_gene_count",
        "top_neighbors_json",
        "top_neighbors_count",
        "gene_rank",
        "ppi_rank",
        "best_pathogenic_rank",
        "variant_row_count",
        "max_cadd_phred",
        "mapped_tissues",
        "mapped_tissue_counts_json",
        "conclusion_code",
        "best_disease_score",
        "best_disease_name",
        "best_omim_id",
        "best_orpha_id",
        "best_mondo_id",
        "best_disease_match_status",
        "mapping_basis",
    ]
    if not include_evidence_json:
        columns = [col for col in columns if col not in {"gene_d_sources_json", "gene_t_layers_json", "gene_t_tissues_json"}]
    if not include_neighbors:
        columns = [col for col in columns if col not in {"top_neighbors_json", "top_neighbors_count"}]
    columns = list(dict.fromkeys(columns))
    columns = [col for col in columns if col in merged.columns]

    final = merged.sort_values(
        ["final_rank", "in_network", "ppi_rank", "gene"],
        ascending=[True, False, True, True],
        na_position="last",
    )
    return final[columns].reset_index(drop=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run clean final PPI CSV from phenotype/VEP/HPO inputs.")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--phenotype-gene-csv", required=True, help="phenotype-gene score CSV")
    parser.add_argument("--vep-output-csv", required=True, help="VEP output CSV with gene_symbol column")
    parser.add_argument("--hpo-file", required=True, help="HPO ID list file")
    parser.add_argument("--output-csv", required=True, help="final CSV path")
    parser.add_argument(
        "--clean-output-dir",
        action="store_true",
        help="delete all other files/directories in output directory before writing final CSV",
    )
    parser.add_argument("--include-neighbors", action="store_true", help="keep top_neighbors_json in final CSV")
    parser.add_argument("--include-evidence-json", action="store_true", help="keep D/T evidence JSON columns in final CSV")
    parser.add_argument("--vep-chunksize", type=int, default=250_000, help="rows per chunk when reading large VEP CSV")
    parser.add_argument("--candidate-top-n", type=int, default=30_000, help="use union of top N VEP genes and top N phenotype genes; 0 means all")
    parser.add_argument("--no-assume-hgnc-standardized", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_csv = Path(args.output_csv).resolve()
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if args.clean_output_dir:
        clean_output_dir(output_csv)

    vep_summary = build_vep_gene_summary(args.vep_output_csv, chunksize=args.vep_chunksize)
    phenotype_summary = build_phenotype_gene_summary(args.phenotype_gene_csv)
    candidate_genes = select_candidate_gene_union(vep_summary, phenotype_summary, top_n=args.candidate_top_n)
    hpo_ids = normalize_hpo_ids(_read_items_file(args.hpo_file), deduplicate=False)
    if not hpo_ids:
        raise SystemExit("HPO list is empty")

    cfg = Config(
        data_dir=args.data_dir,
        TOP_N_NEIGHBORS=Config.TOP_N_NEIGHBORS if args.include_neighbors else 0,
    )
    scorer = RareDiseasePPIScorer(cfg)
    scorer.initialize()
    ppi = scorer.run(
        candidate_genes=candidate_genes,
        hpo_ids=hpo_ids,
        assume_hgnc_standardized=not args.no_assume_hgnc_standardized,
    )

    final = build_final_table(
        ppi=ppi,
        phenotype_csv=args.phenotype_gene_csv,
        vep_summary=vep_summary,
        audit=scorer.last_audit,
        include_neighbors=args.include_neighbors,
        include_evidence_json=args.include_evidence_json,
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(output_csv, index=False)

    summary = {
        "output_csv": str(output_csv),
        "candidate_gene_count": int(len(candidate_genes)),
        "candidate_top_n": int(args.candidate_top_n),
        "vep_top_gene_count": int(min(len(vep_summary), args.candidate_top_n) if args.candidate_top_n else len(vep_summary)),
        "phenotype_top_gene_count": int(min(len(phenotype_summary), args.candidate_top_n) if args.candidate_top_n else len(phenotype_summary)),
        "hpo_count": int(len(hpo_ids)),
        "output_rows": int(len(final)),
        "ranked_gene_count": int(final["final_rank"].notna().sum()) if "final_rank" in final else 0,
        "in_network": int(ppi["in_network"].sum()),
        "not_in_string": int((~ppi["in_network"]).sum()),
        "mapped_tissues": scorer.last_audit.get("mapped_tissues", []),
        "mapped_tissue_counts": scorer.last_audit.get("mapped_tissue_counts", {}),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
