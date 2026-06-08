#!/usr/bin/env python3
"""Rank annotated variants with an explainable rule-based pathogenicity score."""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd


MISSING_VALUES = {"", "-", ".", "na", "nan", "none", "null", "unknown"}
REQUIRED_COLUMNS = [
    "consequence",
    "impact",
    "revel_score",
    "cadd_phred",
    "gnomAD_popmax_AF",
    "gnomAD_eas_AF",
    "gnomAD_nhomalt",
    "spliceAI_ds_max",
    "spliceAI_type",
    "loftee_lof_flag",
    "loftee_lof_filter",
    "clinvar_significance",
    "clinvar_review_status",
    "clinvar_star_rating",
    "protein_domains",
]
SCORE_COLUMNS = [
    "clinvar_score",
    "consequence_score",
    "splice_lof_score",
    "prediction_score",
    "frequency_score",
    "domain_score",
    "raw_pathogenic_score",
    "pathogenic_rank",
    "evidence_summary",
]

CLINVAR_BASE_SCORES = {
    "pathogenic": 40,
    "likely_pathogenic": 30,
    "pathogenic/likely_pathogenic": 35,
    "uncertain_significance": 3,
    "conflicting_interpretations": 0,
    "likely_benign": -25,
    "benign": -35,
    "benign/likely_benign": -30,
}
PATHOGENIC_CLINVAR = {
    "pathogenic",
    "likely_pathogenic",
    "pathogenic/likely_pathogenic",
}
BENIGN_CLINVAR = {"benign", "likely_benign", "benign/likely_benign"}
REVIEW_STATUS_SCORES = {
    "practice_guideline": 8,
    "reviewed_by_expert_panel": 8,
    "criteria_provided_multiple_submitters_no_conflicts": 5,
    "criteria_provided_single_submitter": 2,
}
STAR_FACTORS = {4: 1.20, 3: 1.15, 2: 1.10, 1: 1.00, 0: 1.00}
REVIEW_FACTORS = {
    "practice_guideline": 1.15,
    "reviewed_by_expert_panel": 1.15,
    "criteria_provided_multiple_submitters_no_conflicts": 1.10,
    "criteria_provided_single_submitter": 1.00,
}
BENIGN_ADJUST_FACTORS = {
    "benign": 0.95,
    "likely_benign": 0.90,
    "benign/likely_benign": 0.925,
}
CONSEQUENCE_SCORES = {
    "transcript_ablation": 30,
    "splice_acceptor_variant": 28,
    "splice_donor_variant": 28,
    "stop_gained": 28,
    "frameshift_variant": 28,
    "stop_lost": 24,
    "start_lost": 22,
    "missense_variant": 12,
    "protein_altering_variant": 12,
    "inframe_insertion": 10,
    "inframe_deletion": 10,
    "splice_region_variant": 6,
    "synonymous_variant": 2,
    "intron_variant": 0,
    "upstream_gene_variant": -3,
    "downstream_gene_variant": -3,
    "intergenic_variant": -5,
}
IMPACT_SCORES = {"high": 5, "moderate": 3, "low": 0, "modifier": -3}
PREDICTION_ELIGIBLE = {"missense_variant", "protein_altering_variant"}
LOF_CONSEQUENCES = {
    "transcript_ablation",
    "splice_acceptor_variant",
    "splice_donor_variant",
    "stop_gained",
    "frameshift_variant",
    "stop_lost",
    "start_lost",
}


def text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def is_missing(value: Any) -> bool:
    return text(value).lower() in MISSING_VALUES


def safe_float(value: Any) -> float | None:
    if is_missing(value):
        return None
    try:
        number = float(text(value))
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def normalize_words(value: Any) -> str:
    if is_missing(value):
        return ""
    normalized = text(value).lower()
    normalized = re.sub(r"[^\w/]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")


def normalize_clinvar(value: Any) -> str:
    normalized = normalize_words(value)
    normalized = re.sub(r"\s*/\s*", "/", normalized)
    aliases = {
        "vus": "uncertain_significance",
        "uncertain_significance": "uncertain_significance",
        "conflicting_interpretations_of_pathogenicity": "conflicting_interpretations",
        "conflicting_interpretations": "conflicting_interpretations",
    }
    return aliases.get(normalized, normalized)


def consequence_terms(row: pd.Series) -> list[str]:
    value = row.get("consequence", "")
    if is_missing(value):
        return []
    return [
        normalize_words(term)
        for term in re.split(r"[&,|;/]+", text(value))
        if normalize_words(term)
    ]


def best_consequence(row: pd.Series) -> tuple[str, int]:
    terms = consequence_terms(row)
    if not terms:
        return "", 0
    return max(((term, CONSEQUENCE_SCORES.get(term, 0)) for term in terms), key=lambda x: x[1])


def score_clinvar(row: pd.Series) -> int:
    return clinvar_components(row)["score"]


def clinvar_components(row: pd.Series) -> dict[str, Any]:
    significance = normalize_clinvar(row.get("clinvar_significance", ""))
    base_score = CLINVAR_BASE_SCORES.get(significance, 0)
    if base_score == 0:
        return {
            "significance": significance,
            "base_score": base_score,
            "star_factor": 1.00,
            "review_factor": 1.00,
            "benign_adjust_factor": 1.00,
            "score": 0,
        }

    star_factor = 1.00
    star = safe_float(row.get("clinvar_star_rating", ""))
    if star is not None:
        star_factor = STAR_FACTORS.get(int(star), 1.00)
    review_status = normalize_words(row.get("clinvar_review_status", ""))
    review_factor = REVIEW_FACTORS.get(review_status, 1.00)
    benign_adjust_factor = BENIGN_ADJUST_FACTORS.get(significance, 1.00)
    score = round(base_score * star_factor * review_factor * benign_adjust_factor)
    return {
        "significance": significance,
        "base_score": base_score,
        "star_factor": star_factor,
        "review_factor": review_factor,
        "benign_adjust_factor": benign_adjust_factor,
        "score": int(score),
    }


def score_consequence(row: pd.Series) -> int:
    _, base_score = best_consequence(row)
    impact_score = IMPACT_SCORES.get(normalize_words(row.get("impact", "")), 0)
    return base_score + impact_score


def score_splice_lof(row: pd.Series) -> int:
    ds_max = safe_float(row.get("spliceAI_ds_max", ""))
    score = 0
    if ds_max is not None:
        if ds_max >= 0.8:
            score += 20
        elif ds_max >= 0.5:
            score += 15
        elif ds_max >= 0.2:
            score += 8
        elif ds_max >= 0.1:
            score += 3
        if ds_max >= 0.2 and not is_missing(row.get("spliceAI_type", "")):
            score += 2

    return score + score_loftee(row)


def score_loftee(row: pd.Series) -> int:
    if not LOF_CONSEQUENCES.intersection(consequence_terms(row)):
        return 0
    if not is_missing(row.get("loftee_lof_filter", "")):
        return -8

    flag = normalize_words(row.get("loftee_lof_flag", ""))
    if flag == "hc":
        return 15
    if flag == "lc":
        return 5
    if flag:
        return -3
    return 0


def revel_part(row: pd.Series) -> int:
    if not PREDICTION_ELIGIBLE.intersection(consequence_terms(row)):
        return 0
    revel = safe_float(row.get("revel_score", ""))
    if revel is None:
        return 0
    if revel >= 0.9:
        return 15
    if revel >= 0.75:
        return 12
    if revel >= 0.5:
        return 8
    if revel >= 0.25:
        return 3
    return 0


def cadd_part(row: pd.Series) -> int:
    cadd = safe_float(row.get("cadd_phred", ""))
    if cadd is None:
        return 0
    if cadd >= 30:
        return 12
    if cadd >= 25:
        return 9
    if cadd >= 20:
        return 6
    if cadd >= 10:
        return 2
    return 0


def score_prediction(row: pd.Series) -> int:
    return revel_part(row) + cadd_part(row)


def eas_af_part(af: float) -> int:
    if af < 0:
        return 0
    if af < 0.0001:
        return 10
    if af < 0.001:
        return 8
    if af < 0.01:
        return 3
    if af <= 0.05:
        return -10
    return -25


def popmax_af_part(af: float) -> int:
    if af < 0:
        return 0
    if af < 0.0001:
        return 8
    if af < 0.001:
        return 6
    if af < 0.01:
        return 2
    if af <= 0.05:
        return -8
    return -20


def nhomalt_part(value: Any) -> int:
    nhomalt = safe_float(value)
    if nhomalt is None or nhomalt <= 0:
        return 0
    if nhomalt <= 5:
        return -3
    if nhomalt <= 20:
        return -8
    return -15


def score_frequency(row: pd.Series) -> int:
    eas_af = safe_float(row.get("gnomAD_eas_AF", ""))
    popmax_af = safe_float(row.get("gnomAD_popmax_AF", ""))
    score = 0
    if eas_af is not None:
        score += eas_af_part(eas_af)
        if popmax_af is not None:
            if popmax_af > 0.05:
                score -= 10
            elif popmax_af > 0.01:
                score -= 5
    elif popmax_af is not None:
        score += popmax_af_part(popmax_af)
    score += nhomalt_part(row.get("gnomAD_nhomalt", ""))
    return score


def score_domain(row: pd.Series) -> int:
    return 0 if is_missing(row.get("protein_domains", "")) else 3


def display_value(value: Any) -> str:
    return "unknown" if is_missing(value) else text(value)


def build_evidence_summary(row: pd.Series) -> str:
    parts: list[str] = []
    clinvar = clinvar_components(row)
    if row["clinvar_score"] != 0:
        parts.append(
            "ClinVar="
            f"{clinvar['significance'] or 'unknown'}"
            f"(base={clinvar['base_score']},"
            f"star_factor={clinvar['star_factor']:.2f},"
            f"review_factor={clinvar['review_factor']:.2f},"
            f"benign_adjust_factor={clinvar['benign_adjust_factor']:.2f},"
            f"score={clinvar['score']})"
        )

    consequence, _ = best_consequence(row)
    if row["consequence_score"] != 0:
        parts.append(f"consequence={consequence or 'unknown'}({row['consequence_score']:+d})")

    if row["splice_lof_score"] != 0:
        label = display_value(row.get("spliceAI_ds_max", ""))
        parts.append(f"splice_lof=SpliceAI:{label}({row['splice_lof_score']:+d})")

    revel = safe_float(row.get("revel_score", ""))
    revel_score = revel_part(row)
    if revel_score != 0 and revel is not None:
        parts.append(f"REVEL={revel:g}({revel_score:+d})")

    cadd = safe_float(row.get("cadd_phred", ""))
    cadd_score = cadd_part(row)
    if cadd_score != 0 and cadd is not None:
        parts.append(f"CADD={cadd:g}({cadd_score:+d})")

    eas_af = row.get("gnomAD_eas_AF", "")
    popmax_af = row.get("gnomAD_popmax_AF", "")
    if not is_missing(eas_af):
        parts.append(f"EAS_AF={text(eas_af)}")
    elif not is_missing(popmax_af):
        parts.append(f"popmax_AF={text(popmax_af)}")
    if row["frequency_score"] != 0:
        parts.append(f"frequency({row['frequency_score']:+d})")

    if row["domain_score"] != 0:
        parts.append(f"domain({row['domain_score']:+d})")
    parts.append(f"total={row['raw_pathogenic_score']:+d}")
    return "; ".join(parts)


def warn_missing_columns(columns: list[str]) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing:
        print(
            "WARNING: missing input columns; their evidence is treated as unknown: "
            + ", ".join(missing),
            file=sys.stderr,
        )


def rank_variants(input_path: Path, output_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(input_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    original_columns = list(frame.columns)
    warn_missing_columns(original_columns)

    frame["clinvar_score"] = frame.apply(score_clinvar, axis=1)
    frame["consequence_score"] = frame.apply(score_consequence, axis=1)
    frame["splice_lof_score"] = frame.apply(score_splice_lof, axis=1)
    frame["prediction_score"] = frame.apply(score_prediction, axis=1)
    frame["frequency_score"] = frame.apply(score_frequency, axis=1)
    frame["domain_score"] = frame.apply(score_domain, axis=1)
    frame["raw_pathogenic_score"] = frame[
        [
            "clinvar_score",
            "consequence_score",
            "splice_lof_score",
            "prediction_score",
            "frequency_score",
            "domain_score",
        ]
    ].sum(axis=1)
    frame = frame.sort_values("raw_pathogenic_score", ascending=False, kind="mergesort").reset_index(drop=True)
    frame["pathogenic_rank"] = frame.index + 1
    frame["evidence_summary"] = frame.apply(build_evidence_summary, axis=1)
    frame = frame[original_columns + SCORE_COLUMNS]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, encoding="utf-8-sig")
    return frame


def print_statistics(frame: pd.DataFrame, input_count: int) -> None:
    scores = frame["raw_pathogenic_score"]
    print(f"Input variants: {input_count}")
    print(f"Output variants: {len(frame)}")
    if len(frame):
        print(f"raw_pathogenic_score max: {scores.max()}")
        print(f"raw_pathogenic_score min: {scores.min()}")
        print(f"raw_pathogenic_score median: {scores.median():g}")
    else:
        print("raw_pathogenic_score max: NA")
        print("raw_pathogenic_score min: NA")
        print("raw_pathogenic_score median: NA")

    preview_columns = [
        "chrom",
        "pos",
        "ref",
        "alt",
        "gene_symbol",
        "consequence",
        "clinvar_significance",
        "gnomAD_eas_AF",
        "raw_pathogenic_score",
    ]
    available = [column for column in preview_columns if column in frame.columns]
    print("\nTop 20 variants:")
    print(frame[available].head(20).to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Input annotated CSV")
    parser.add_argument("--output", required=True, type=Path, help="Output ranked CSV")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = rank_variants(args.input, args.output)
    print_statistics(frame, input_count=len(frame))


if __name__ == "__main__":
    main()
