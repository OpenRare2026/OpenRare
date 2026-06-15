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


def build_vep_gene_summary(vep_csv: str) -> pd.DataFrame:
    vep = pd.read_csv(vep_csv, low_memory=False)
    if "gene_symbol" not in vep.columns:
        raise ValueError(f"VEP CSV missing gene_symbol column: {vep_csv}")

    vep["gene_symbol"] = vep["gene_symbol"].map(_clean_str)
    vep = vep[(vep["gene_symbol"] != "") & (vep["gene_symbol"] != "-")]
    if vep.empty:
        raise ValueError("VEP CSV has no usable gene_symbol values")

    if "pathogenic_rank" in vep.columns:
        vep["pathogenic_rank_num"] = pd.to_numeric(vep["pathogenic_rank"], errors="coerce")
    else:
        vep["pathogenic_rank_num"] = pd.NA

    cadd_col = "cadd_phred" if "cadd_phred" in vep.columns else None
    agg: Dict[str, Any] = {
        "best_pathogenic_rank": ("pathogenic_rank_num", "min"),
        "variant_row_count": ("gene_symbol", "size"),
    }
    if cadd_col:
        agg["max_cadd_phred"] = (cadd_col, lambda s: pd.to_numeric(s, errors="coerce").max())

    summary = vep.groupby("gene_symbol", as_index=False).agg(**agg)
    if "max_cadd_phred" not in summary.columns:
        summary["max_cadd_phred"] = pd.NA
    summary["_rank_sort"] = pd.to_numeric(summary["best_pathogenic_rank"], errors="coerce").fillna(10**9)
    summary = summary.sort_values(
        ["_rank_sort", "variant_row_count", "gene_symbol"],
        ascending=[True, False, True],
    ).drop(columns=["_rank_sort"])
    return summary.reset_index(drop=True)


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
    phenotype = pd.read_csv(phenotype_csv)
    if "gene_symbol" not in phenotype.columns:
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
    phenotype_columns = [col for col in phenotype_columns if col in phenotype.columns]

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
        "gene_rank",
        "ppi_rank",
        "best_pathogenic_rank",
        "variant_row_count",
        "max_cadd_phred",
        "in_network",
        "score_mode",
        "note",
        "disease_score",
        "tissue_score",
        "topology_score",
        "gene_in_d",
        "gene_d_evidence_score",
        "gene_in_t",
        "gene_t_weight",
        "d_gene_count",
        "t_gene_count",
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
    if include_evidence_json:
        columns.extend(["gene_d_sources_json", "gene_t_layers_json", "gene_t_tissues_json"])
    if include_neighbors:
        columns.append("top_neighbors_json")
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
    parser.add_argument("--no-assume-hgnc-standardized", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_csv = Path(args.output_csv).resolve()
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if args.clean_output_dir:
        clean_output_dir(output_csv)

    vep_summary = build_vep_gene_summary(args.vep_output_csv)
    candidate_genes = _unique_preserve_order(vep_summary["gene_symbol"].astype(str).tolist())
    hpo_ids = normalize_hpo_ids(_read_items_file(args.hpo_file), deduplicate=False)
    if not hpo_ids:
        raise SystemExit("HPO list is empty")

    cfg = Config(data_dir=args.data_dir)
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
