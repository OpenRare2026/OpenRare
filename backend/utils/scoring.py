from __future__ import annotations

import math
import re
from typing import Any


MISSING_VALUES = {"", "-", ".", "na", "nan", "none", "null", "unknown"}

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

PATHOGENIC_CLINVAR = {"pathogenic", "likely_pathogenic", "pathogenic/likely_pathogenic"}
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


def score_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def score_is_missing(value: Any) -> bool:
    return score_text(value).lower() in MISSING_VALUES


def safe_score_float(value: Any) -> float | None:
    if score_is_missing(value):
        return None
    try:
        number = float(score_text(value))
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def normalize_words(value: Any) -> str:
    if score_is_missing(value):
        return ""
    normalized = score_text(value).lower()
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


def consequence_terms(row: dict[str, str]) -> list[str]:
    value = row.get("consequence", "")
    if score_is_missing(value):
        return []
    return [
        normalize_words(term)
        for term in re.split(r"[&,|;/]+", score_text(value))
        if normalize_words(term)
    ]


def best_consequence(row: dict[str, str]) -> tuple[str, int]:
    terms = consequence_terms(row)
    if not terms:
        return "", 0
    return max(
        ((term, CONSEQUENCE_SCORES.get(term, 0)) for term in terms),
        key=lambda item: item[1],
    )


def score_clinvar(row: dict[str, str]) -> int:
    return clinvar_components(row)["score"]


def clinvar_components(row: dict[str, str]) -> dict[str, object]:
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
    star = safe_score_float(row.get("clinvar_star_rating", ""))
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


def score_consequence(row: dict[str, str]) -> int:
    _consequence, base_score = best_consequence(row)
    impact_score = IMPACT_SCORES.get(normalize_words(row.get("impact", "")), 0)
    return base_score + impact_score


def score_loftee(row: dict[str, str]) -> int:
    if not LOF_CONSEQUENCES.intersection(consequence_terms(row)):
        return 0
    if not score_is_missing(row.get("loftee_lof_filter", "")):
        return -8

    flag = normalize_words(row.get("loftee_lof_flag", ""))
    if flag == "hc":
        return 15
    if flag == "lc":
        return 5
    if flag:
        return -3
    return 0


def score_splice_lof(row: dict[str, str]) -> int:
    ds_max = safe_score_float(row.get("spliceAI_ds_max", ""))
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
        if ds_max >= 0.2 and not score_is_missing(row.get("spliceAI_type", "")):
            score += 2

    return score + score_loftee(row)


def revel_part(row: dict[str, str]) -> int:
    if not PREDICTION_ELIGIBLE.intersection(consequence_terms(row)):
        return 0
    revel = safe_score_float(row.get("revel_score", ""))
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


def cadd_part(row: dict[str, str]) -> int:
    cadd = safe_score_float(row.get("cadd_phred", ""))
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


def score_prediction(row: dict[str, str]) -> int:
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
    nhomalt = safe_score_float(value)
    if nhomalt is None or nhomalt <= 0:
        return 0
    if nhomalt <= 5:
        return -3
    if nhomalt <= 20:
        return -8
    return -15


def score_frequency(row: dict[str, str]) -> int:
    eas_af = safe_score_float(row.get("gnomAD_eas_AF", ""))
    popmax_af = safe_score_float(row.get("gnomAD_popmax_AF", ""))
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


def score_domain(row: dict[str, str]) -> int:
    return 0 if score_is_missing(row.get("protein_domains", "")) else 3


def display_value(value: Any) -> str:
    return "unknown" if score_is_missing(value) else score_text(value)


def row_score(row: dict[str, str], key: str) -> int:
    try:
        return int(row.get(key, "0") or 0)
    except ValueError:
        return 0


def clean_output_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def build_evidence_summary(row: dict[str, str]) -> str:
    parts: list[str] = []
    clinvar = clinvar_components(row)
    clinvar_score = row_score(row, "_clinvar_score")
    if clinvar_score != 0:
        parts.append(
            "ClinVar="
            f"{clinvar['significance'] or 'unknown'}"
            f"(base={clinvar['base_score']},"
            f"star_factor={clinvar['star_factor']:.2f},"
            f"review_factor={clinvar['review_factor']:.2f},"
            f"benign_adjust_factor={clinvar['benign_adjust_factor']:.2f},"
            f"score={clinvar['score']})"
        )

    consequence, _base_score = best_consequence(row)
    consequence_score = row_score(row, "_consequence_score")
    if consequence_score != 0:
        parts.append(f"consequence={consequence or 'unknown'}({consequence_score:+d})")

    splice_lof_score = row_score(row, "_splice_lof_score")
    if splice_lof_score != 0:
        label = display_value(row.get("spliceAI_ds_max", ""))
        parts.append(f"splice_lof=SpliceAI:{label}({splice_lof_score:+d})")

    revel = safe_score_float(row.get("revel_score", ""))
    revel_score = revel_part(row)
    if revel_score != 0 and revel is not None:
        parts.append(f"REVEL={revel:g}({revel_score:+d})")

    cadd = safe_score_float(row.get("cadd_phred", ""))
    cadd_score = cadd_part(row)
    if cadd_score != 0 and cadd is not None:
        parts.append(f"CADD={cadd:g}({cadd_score:+d})")

    eas_af = row.get("gnomAD_eas_AF", "")
    popmax_af = row.get("gnomAD_popmax_AF", "")
    if not score_is_missing(eas_af):
        parts.append(f"EAS_AF={score_text(eas_af)}")
    elif not score_is_missing(popmax_af):
        parts.append(f"popmax_AF={score_text(popmax_af)}")

    frequency_score = row_score(row, "_frequency_score")
    if frequency_score != 0:
        parts.append(f"frequency({frequency_score:+d})")

    domain_score = row_score(row, "_domain_score")
    if domain_score != 0:
        parts.append(f"domain({domain_score:+d})")

    parts.append(f"total={row_score(row, '_raw_pathogenic_score'):+d}")
    return "; ".join(parts)


def raw_pathogenic_score(row: dict[str, str]) -> int:
    return sum(
        [
            score_clinvar(row),
            score_consequence(row),
            score_splice_lof(row),
            score_prediction(row),
            score_frequency(row),
            score_domain(row),
        ]
    )


def add_pathogenic_fields(row: dict[str, str]) -> int:
    row["_clinvar_score"] = str(score_clinvar(row))
    row["_consequence_score"] = str(score_consequence(row))
    row["_splice_lof_score"] = str(score_splice_lof(row))
    row["_prediction_score"] = str(score_prediction(row))
    row["_frequency_score"] = str(score_frequency(row))
    row["_domain_score"] = str(score_domain(row))
    score = raw_pathogenic_score(row)
    row["_raw_pathogenic_score"] = str(score)
    row["evidence_summary"] = build_evidence_summary(row)
    row["pathogenic_rank"] = "-"
    return score
