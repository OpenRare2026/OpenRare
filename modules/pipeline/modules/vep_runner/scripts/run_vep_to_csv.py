#!/usr/bin/env python3
import argparse
import csv
import gzip
import json
import math
import os
import re
import sqlite3
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote


BASE_COLUMNS = [
    "Uploaded_variation",
    "Location",
    "Allele",
    "Gene",
    "Feature",
    "Feature_type",
    "Consequence",
    "cDNA_position",
    "CDS_position",
    "Protein_position",
    "Amino_acids",
    "Codons",
    "Existing_variation",
]

REQUESTED_COLUMNS = [
    "chrom",
    "pos",
    "ref",
    "alt",
    "gene_symbol",
    "all_genes",
    "transcript_id",
    "refseq_id",
    "biotype",
    "canonical",
    "mane",
    "mane_select",
    "mane_plus_clinical",
    "appris",
    "tsl",
    "ccds",
    "vep_pick",
    "transcript_flags",
    "consequence",
    "impact",
    "hgvsc",
    "hgvsp",
    "cdna_position",
    "cds_position",
    "protein_position",
    "amino_acids",
    "codons",
    "exon",
    "intron",
    "strand",
    "protein_domains",
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
    "clinical_gtex_tissue_whitelist",
    "clinical_best_tissue",
    "clinical_transcript_tpm",
    "gtex_transcript_max_tissue",
    "gtex_transcript_max_tpm",
    "gtex_transcript_top5_tissues",
    "gtex_max_tissue_in_clinical_whitelist",
    "clinical_vs_global_tpm_ratio",
    "gtex_lookup_status",
    "tx_consequence_score",
    "tx_confidence_score",
    "clinical_expression_score",
    "tx_tie_breaker_score",
    "tx_selection_score",
    "tx_rank_within_variant",
    "tx_eligibility",
    "tx_exclusion_reason",
    "tx_rescue_reason",
    "tx_selected_reason",
    "pathogenic_rank",
    "evidence_summary",
]

VCF_INFO_COLUMN_PREFIX = "vcf_info_"
VCF_INFO_INSERT_AFTER = "alt"
VCF_INFO_HEADER_RE = re.compile(r"^##INFO=<ID=([^,>]+),Number=([^,>]+)")

SPLICEAI_TYPES = [
    ("DS_AG", "acceptor_gain"),
    ("DS_AL", "acceptor_loss"),
    ("DS_DG", "donor_gain"),
    ("DS_DL", "donor_loss"),
]

GNOMAD_NATIVE_POP_AF_FIELDS = [
    "gnomADe_AFR_AF",
    "gnomADe_AMR_AF",
    "gnomADe_ASJ_AF",
    "gnomADe_EAS_AF",
    "gnomADe_FIN_AF",
    "gnomADe_MID_AF",
    "gnomADe_NFE_AF",
    "gnomADe_REMAINING_AF",
    "gnomADe_SAS_AF",
    "gnomADg_AFR_AF",
    "gnomADg_AMI_AF",
    "gnomADg_AMR_AF",
    "gnomADg_ASJ_AF",
    "gnomADg_EAS_AF",
    "gnomADg_FIN_AF",
    "gnomADg_MID_AF",
    "gnomADg_NFE_AF",
    "gnomADg_REMAINING_AF",
    "gnomADg_SAS_AF",
]

GNOMAD_NATIVE_EAS_AF_FIELDS = [
    "gnomADe_EAS_AF",
    "gnomADg_EAS_AF",
]

GNOMAD_NATIVE_OVERALL_AF_FIELDS = [
    "gnomADe_AF",
    "gnomADg_AF",
]

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

TX_CONSEQUENCE_SCORES = {
    "transcript_ablation": 40,
    "splice_acceptor_variant": 40,
    "splice_donor_variant": 40,
    "stop_gained": 40,
    "frameshift_variant": 40,
    "stop_lost": 34,
    "start_lost": 34,
    "missense_variant": 22,
    "protein_altering_variant": 22,
    "inframe_insertion": 18,
    "inframe_deletion": 18,
    "splice_region_variant": 14,
    "synonymous_variant": 5,
    "5_prime_UTR_variant": 3,
    "3_prime_UTR_variant": 3,
    "intron_variant": 0,
    "upstream_gene_variant": 0,
    "downstream_gene_variant": 0,
    "intergenic_variant": 0,
}

TX_EXCLUDED_BIOTYPES = {
    "nonsense_mediated_decay",
    "retained_intron",
    "processed_transcript",
    "processed_pseudogene",
    "transcribed_processed_pseudogene",
    "transcribed_unprocessed_pseudogene",
    "unprocessed_pseudogene",
    "pseudogene",
    "tec",
    "protein_coding_cds_not_defined",
}

TX_BAD_FLAGS = {"cds_start_nf", "cds_end_nf"}
GTEX_TRANSCRIPT_TPM_DEFAULT = (
    "__VEP_RUNNER__/vep_data/GTEx/v11/expression/gtex_v11_transcript_tpm.parquet"
)
HPO_TPM_DATA_DIR_DEFAULT = "__VEP_RUNNER__/vep_data/hpo_tpm"
PSEUDOGENE_LOG_SUFFIX = ".pseudogene_annotation.log.json"
REGULATORY_LOG_SUFFIX = ".regulatory_annotation.log.json"
REGULATORY_CCRE_BED_DEFAULT = "__VEP_RUNNER__/vep_data/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz"
VEP_TMP_DIR_ENV = "VEP_RUNNER_TMPDIR"
VEP_TMP_DIR_DEFAULT = "__VEP_RUNNER__/tmp"
OPENRARE_DATA_ROOT_ENV = "OPENRARE_DATA_ROOT"
PIPELINE_ROOT = Path(__file__).resolve().parents[3]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))
from config.path_utils import openrare_data_root as resolve_openrare_data_root

SQLITE_INSERT_BATCH_SIZE = 20000
SQLITE_FETCH_BATCH_SIZE = 10000


def openrare_data_root() -> str:
    return str(resolve_openrare_data_root())


def load_config(path: Path) -> dict:
    with path.open() as handle:
        config = json.load(handle)
    runner_dir = Path(__file__).resolve().parents[1]
    config = resolve_runner_tokens(config, str(runner_dir))
    return finalize_vep_config(config)


def resolve_runner_tokens(value, runner_dir: str):
    data_root = openrare_data_root()
    if isinstance(value, str):
        resolved = value.replace("__VEP_RUNNER__", runner_dir)
        resolved = resolved.replace("${OPENRARE_DATA_ROOT}", data_root)
        if resolved.startswith("$OPENRARE_DATA_ROOT"):
            resolved = resolved.replace("$OPENRARE_DATA_ROOT", data_root, 1)
        return resolved
    if isinstance(value, list):
        return [resolve_runner_tokens(item, runner_dir) for item in value]
    if isinstance(value, dict):
        return {key: resolve_runner_tokens(item, runner_dir) for key, item in value.items()}
    return value


def finalize_vep_config(config: dict) -> dict:
    vep_bin = (config.get("vep") or "").strip()
    if not vep_bin or vep_bin == "vep":
        resolved = shutil.which("vep")
        if not resolved:
            raise FileNotFoundError(
                "VEP executable not found on PATH. Install ensembl-vep (e.g. pixi) or set an absolute path in config['vep']."
            )
        config["vep"] = resolved
    elif not Path(vep_bin).is_file():
        raise FileNotFoundError(f"VEP executable not found: {vep_bin}")
    return config


def configured_tmp_dir(config: dict | None = None) -> Path:
    runner_dir = str(Path(__file__).resolve().parents[1])
    raw = os.environ.get(VEP_TMP_DIR_ENV)
    if not raw and config:
        raw = config.get("tmp_dir")
    if not raw:
        raw = os.environ.get("TMPDIR")
    if not raw:
        raw = VEP_TMP_DIR_DEFAULT
    path = Path(resolve_runner_tokens(raw, runner_dir)).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def readable_file(path: str) -> bool:
    return bool(path) and Path(path).is_file()


def require_file(path: str, label: str) -> None:
    if not readable_file(path):
        raise FileNotFoundError(f"{label} not found: {path}")


def existing_index(path: str) -> bool:
    return Path(path + ".tbi").is_file() or Path(path + ".csi").is_file()


def clean_clinvar_value(value: str) -> str:
    value = (value or "").strip()
    if value in {"", "-", "."}:
        return "-"
    return value.replace("_", " ")


def clinvar_star_rating(review_status: str) -> int:
    raw = (review_status or "").lower()
    if not raw or raw in {"-", "."}:
        return 0
    if "practice_guideline" in raw:
        return 4
    if "reviewed_by_expert_panel" in raw:
        return 3
    if "criteria_provided,_multiple_submitters,_no_conflicts" in raw:
        return 2
    if "criteria_provided,_single_submitter" in raw:
        return 1
    if "criteria_provided,_conflicting_interpretations" in raw:
        return 1
    if "criteria_provided,_conflicting_classifications" in raw:
        return 1
    return 0


def score_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def score_is_missing(value) -> bool:
    return score_text(value).lower() in MISSING_VALUES


def safe_score_float(value):
    if score_is_missing(value):
        return None
    try:
        number = float(score_text(value))
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def normalize_words(value) -> str:
    if score_is_missing(value):
        return ""
    normalized = score_text(value).lower()
    normalized = re.sub(r"[^\w/]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")


def normalize_clinvar(value) -> str:
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
    return max(((term, CONSEQUENCE_SCORES.get(term, 0)) for term in terms), key=lambda item: item[1])


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


def nhomalt_part(value) -> int:
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


def display_value(value) -> str:
    return "unknown" if score_is_missing(value) else score_text(value)


def row_score(row: dict[str, str], key: str) -> int:
    try:
        return int(row.get(key, "0") or 0)
    except ValueError:
        return 0


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


def add_pathogenic_ranks(rows: list[dict[str, str]]) -> None:
    for row in rows:
        row["_clinvar_score"] = str(score_clinvar(row))
        row["_consequence_score"] = str(score_consequence(row))
        row["_splice_lof_score"] = str(score_splice_lof(row))
        row["_prediction_score"] = str(score_prediction(row))
        row["_frequency_score"] = str(score_frequency(row))
        row["_domain_score"] = str(score_domain(row))
        row["_raw_pathogenic_score"] = str(raw_pathogenic_score(row))

    rows.sort(key=lambda row: row_score(row, "_raw_pathogenic_score"), reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["pathogenic_rank"] = str(rank)
        row["evidence_summary"] = build_evidence_summary(row)


def build_plugin_args(config: dict, disabled: set[str]) -> list[str]:
    plugins = config.get("plugins", {})
    args: list[str] = []

    cadd = plugins.get("cadd", {})
    if cadd.get("enabled") and "cadd" not in disabled:
        require_file(cadd["snv"], "CADD SNV file")
        require_file(cadd["indels"], "CADD indel file")
        if not existing_index(cadd["snv"]):
            raise FileNotFoundError(f"CADD SNV index not found: {cadd['snv']}.tbi/.csi")
        if not existing_index(cadd["indels"]):
            raise FileNotFoundError(f"CADD indel index not found: {cadd['indels']}.tbi/.csi")
        args += [
            "--plugin",
            f"CADD,snv={cadd['snv']},indels={cadd['indels']}",
        ]

    spliceai = plugins.get("spliceai", {})
    if spliceai.get("enabled") and "spliceai" not in disabled:
        require_file(spliceai["snv"], "SpliceAI SNV file")
        require_file(spliceai["indel"], "SpliceAI indel file")
        if not existing_index(spliceai["snv"]):
            raise FileNotFoundError(f"SpliceAI SNV index not found: {spliceai['snv']}.tbi/.csi")
        if not existing_index(spliceai["indel"]):
            raise FileNotFoundError(f"SpliceAI indel index not found: {spliceai['indel']}.tbi/.csi")
        args += [
            "--plugin",
            f"SpliceAI,snv={spliceai['snv']},indel={spliceai['indel']}",
        ]

    am = plugins.get("alphamissense", {})
    if am.get("enabled") and "alphamissense" not in disabled:
        require_file(am["file"], "AlphaMissense file")
        if not existing_index(am["file"]):
            raise FileNotFoundError(f"AlphaMissense index not found: {am['file']}.tbi/.csi")
        args += ["--plugin", f"AlphaMissense,file={am['file']}"]

    dbnsfp = plugins.get("dbnsfp", {})
    if dbnsfp.get("enabled") and "dbnsfp" not in disabled:
        require_file(dbnsfp["file"], "dbNSFP file")
        if not existing_index(dbnsfp["file"]):
            raise FileNotFoundError(f"dbNSFP index not found: {dbnsfp['file']}.tbi/.csi")
        params = ",".join(dbnsfp.get("params", []))
        suffix = f",{params}" if params else ""
        args += ["--plugin", f"dbNSFP,{dbnsfp['file']}{suffix}"]

    loftee = plugins.get("loftee", {})
    if loftee.get("enabled") and "loftee" not in disabled:
        loftee_path = loftee["loftee_path"]
        require_file(str(Path(loftee_path) / "LoF.pm"), "LOFTEE LoF.pm")
        plugin_dir = Path(loftee_path)
        human_ancestor = loftee.get("human_ancestor_fa", "false")
        if human_ancestor and human_ancestor != "false":
            require_file(human_ancestor, "LOFTEE human ancestor FASTA")
        args += [
            "--dir_plugins",
            str(plugin_dir),
            "--plugin",
            ",".join(
                [
                    "LoF",
                    f"loftee_path:{loftee_path}",
                    f"human_ancestor_fa:{human_ancestor}",
                    f"gerp_file:{loftee.get('gerp_file', 'false')}",
                    f"conservation_file:{loftee.get('conservation_file', 'false')}",
                ]
            ),
        ]

    clinvar = plugins.get("clinvar", {})
    if clinvar.get("enabled") and "clinvar" not in disabled:
        require_file(clinvar["file"], "ClinVar VCF")
        if not existing_index(clinvar["file"]):
            raise FileNotFoundError(f"ClinVar index not found: {clinvar['file']}.tbi/.csi")
        custom_parts = [
            clinvar["file"],
            clinvar.get("name", "ClinVar"),
            clinvar.get("format", "vcf"),
            clinvar.get("match", "exact"),
            str(clinvar.get("overlap", "0")),
        ]
        custom_parts.extend(clinvar.get("fields", []))
        args += ["--custom", ",".join(custom_parts)]

    return args


def parse_extra(extra: str) -> dict[str, str]:
    values: dict[str, str] = {}
    if not extra or extra == "-":
        return values
    for item in extra.split(";"):
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
        else:
            key, value = item, "1"
        values[key] = value
    return values


def parse_uploaded_variation(value: str) -> dict[str, str]:
    # VEP VCF IDs commonly look like "7_140753336_A/T".
    parsed = {"chrom": "", "pos": "", "ref": "", "alt": ""}
    if not value:
        return parsed
    chrom, sep, rest = value.partition("_")
    if not sep:
        return parsed
    pos, sep, alleles = rest.partition("_")
    if not sep:
        return parsed
    ref, sep, alt = alleles.partition("/")
    parsed.update({"chrom": chrom, "pos": pos, "ref": ref, "alt": alt})
    return parsed


def vep_uploaded_variation_keys(chrom: str, pos: str, ref: str, alt: str) -> list[str]:
    keys = [f"{chrom}_{pos}_{ref}/{alt}"]
    if len(ref) == len(alt):
        return keys
    try:
        shifted_pos = str(int(pos) + 1)
    except ValueError:
        return keys

    # For VCF indels, VEP reports the normalized event coordinate one base after
    # the left padding base. Keep both forms so final output can map back to VCF.
    keys.append(f"{chrom}_{shifted_pos}_{ref}/{alt}")
    if len(ref) < len(alt) and alt.startswith(ref):
        keys.append(f"{chrom}_{shifted_pos}_-/{alt[len(ref):] or '-'}")
    elif len(ref) > len(alt) and ref.startswith(alt):
        keys.append(f"{chrom}_{shifted_pos}_{ref[len(alt):] or '-'}/-")
    return keys


def original_variant_lookup_keys(
    chrom: str,
    pos: str,
    ref: str,
    alt: str,
    variant_id: str,
) -> list[str]:
    """Build lookup keys for VEP Uploaded_variation values.

    VEP uses the VCF ID column when present (e.g. rs28428499); otherwise it falls
    back to the coordinate form chr1_14833_G/C. Index both so either can be mapped
    back to the original VCF allele.
    """
    keys = vep_uploaded_variation_keys(chrom, pos, ref, alt)
    if variant_id and variant_id not in {".", "-"}:
        keys.append(variant_id)
    return keys


def vcf_info_column_name(info_id: str) -> str:
    return f"{VCF_INFO_COLUMN_PREFIX}{info_id}"


def build_output_columns(vcf_info_ids: list[str] | None = None) -> list[str]:
    fieldnames: list[str] = []
    seen: set[str] = set()

    def append_column(column: str) -> None:
        if column and column not in seen:
            seen.add(column)
            fieldnames.append(column)

    for column in REQUESTED_COLUMNS:
        append_column(column)
        if column == VCF_INFO_INSERT_AFTER:
            for info_id in vcf_info_ids or []:
                append_column(vcf_info_column_name(info_id))
    return fieldnames


def annotate_pseudogene_csv(csv_path: Path, log_json_path: Path | None = None) -> dict[str, object]:
    from annotate_pseudogene import (  # type: ignore
        DEFAULT_GENCODE_GTF,
        DEFAULT_HGNC,
        DEFAULT_PSEUDOGENE_ORG,
        IntervalIndex,
        annotate_csv,
        load_gencode_intervals,
        load_hgnc_pseudogene_map,
        load_pseudogene_org_intervals,
    )

    require_file(str(DEFAULT_GENCODE_GTF), "Pseudogene GENCODE GTF")
    require_file(str(DEFAULT_PSEUDOGENE_ORG), "Pseudogene.org Human90 file")
    require_file(str(DEFAULT_HGNC), "HGNC pseudogene mapping file")

    pgohum_to_symbols, hgnc_stats = load_hgnc_pseudogene_map(DEFAULT_HGNC)
    gencode_intervals, gencode_stats = load_gencode_intervals(
        DEFAULT_GENCODE_GTF,
        pgohum_to_symbols,
    )
    pseudogene_org_intervals, pseudogene_org_stats = load_pseudogene_org_intervals(
        DEFAULT_PSEUDOGENE_ORG,
        pgohum_to_symbols,
    )
    index = IntervalIndex(gencode_intervals + pseudogene_org_intervals)

    tmp_handle = tempfile.NamedTemporaryFile(
        prefix=f"{csv_path.name}.",
        suffix=".pseudogene.tmp",
        dir=str(csv_path.parent),
        delete=False,
    )
    tmp_path = Path(tmp_handle.name)
    tmp_handle.close()
    try:
        annotate_stats = annotate_csv(csv_path, tmp_path, index)
        tmp_path.replace(csv_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    log = {
        "input": str(csv_path),
        "output": str(csv_path),
        "databases": {
            "gencode_gtf": str(DEFAULT_GENCODE_GTF),
            "pseudogene_org": str(DEFAULT_PSEUDOGENE_ORG),
            "hgnc": str(DEFAULT_HGNC),
        },
        "hgnc": hgnc_stats,
        "database_interval_filtering": {
            **gencode_stats,
            **pseudogene_org_stats,
        },
        "annotation": annotate_stats,
    }
    if log_json_path:
        log_json_path.parent.mkdir(parents=True, exist_ok=True)
        log_json_path.write_text(json.dumps(log, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return log


def annotate_regulatory_vcf(
    input_vcf: Path,
    output_vcf: Path,
    log_json_path: Path | None = None,
    summary_tsv_path: Path | None = None,
    ccre_bed: Path | None = None,
) -> dict[str, object]:
    from annotate_regulatory import (  # type: ignore
        DEFAULT_CCRE_BED,
        DEFAULT_SOURCE,
        annotate_vcf,
        write_summary_tsv,
    )

    bed_path = ccre_bed or DEFAULT_CCRE_BED
    require_file(str(bed_path), "Regulatory ENCODE SCREEN cCRE BED")

    stats = annotate_vcf(input_vcf, output_vcf, bed_path, DEFAULT_SOURCE)
    if summary_tsv_path:
        write_summary_tsv(summary_tsv_path, stats)
    if log_json_path:
        log_json_path.parent.mkdir(parents=True, exist_ok=True)
        log_json_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return stats


def parse_vcf_info_header(line: str) -> tuple[str, str] | None:
    match = VCF_INFO_HEADER_RE.match(line)
    if not match:
        return None
    return match.group(1), match.group(2)


def parse_vcf_info_values(
    info: str,
    alt_index: int,
    info_numbers: dict[str, str],
) -> dict[str, str]:
    values: dict[str, str] = {}
    if not info or info in {".", "-"}:
        return values
    for item in info.split(";"):
        if not item:
            continue
        key, sep, raw_value = item.partition("=")
        if not key:
            continue
        value = raw_value if sep else "1"
        number = info_numbers.get(key)
        if number == "A":
            parts = value.split(",")
            if alt_index < len(parts):
                value = parts[alt_index]
        elif number == "R":
            parts = value.split(",")
            if alt_index + 1 < len(parts):
                value = parts[alt_index + 1]
        values[vcf_info_column_name(key)] = "-" if value in {"", "."} else value
    return values


def load_original_vcf_coordinates(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    coordinates: dict[str, dict[str, str]] = {}
    info_numbers: dict[str, str] = {}
    info_field_ids: list[str] = []
    seen_info_ids: set[str] = set()

    def remember_info_id(info_id: str) -> None:
        if info_id and info_id not in seen_info_ids:
            seen_info_ids.add(info_id)
            info_field_ids.append(info_id)

    with open_text(path) as handle:
        for line in handle:
            if line.startswith("##INFO="):
                parsed = parse_vcf_info_header(line)
                if parsed:
                    info_id, number = parsed
                    info_numbers[info_id] = number
                    remember_info_id(info_id)
                continue
            if not line or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            chrom, pos, variant_id, ref, alts = parts[:5]
            info = parts[7] if len(parts) > 7 else ""
            for alt_index, alt in enumerate(alts.split(",")):
                original = {"chrom": chrom, "pos": pos, "ref": ref, "alt": alt}
                info_values = parse_vcf_info_values(info, alt_index, info_numbers)
                for column in info_values:
                    remember_info_id(column.removeprefix(VCF_INFO_COLUMN_PREFIX))
                original.update(info_values)
                for key in original_variant_lookup_keys(chrom, pos, ref, alt, variant_id):
                    coordinates.setdefault(key, original)
    return coordinates, info_field_ids


class SQLiteOriginalVariantLookup:
    def __init__(self, con: sqlite3.Connection):
        self.con = con
        self.cache_key: str | None = None
        self.cache_value: dict[str, str] | None = None

    def get(self, key: str, default=None):
        if key == self.cache_key:
            return self.cache_value if self.cache_value is not None else default
        self.cache_key = key
        row = self.con.execute(
            "select payload from original_variants where key = ?",
            (key,),
        ).fetchone()
        self.cache_value = json.loads(row[0]) if row else None
        return self.cache_value if self.cache_value is not None else default


def flush_original_variant_batch(con: sqlite3.Connection, batch: list[tuple[str, str]]) -> None:
    if not batch:
        return
    con.executemany(
        "insert or ignore into original_variants(key, payload) values (?, ?)",
        batch,
    )
    con.commit()
    batch.clear()


def load_original_vcf_coordinates_sqlite(
    path: Path,
    con: sqlite3.Connection,
) -> tuple[SQLiteOriginalVariantLookup, list[str]]:
    con.execute(
        "create table if not exists original_variants "
        "(key text primary key, payload text not null) without rowid"
    )
    con.execute("delete from original_variants")
    con.commit()

    info_numbers: dict[str, str] = {}
    info_field_ids: list[str] = []
    seen_info_ids: set[str] = set()
    batch: list[tuple[str, str]] = []

    def remember_info_id(info_id: str) -> None:
        if info_id and info_id not in seen_info_ids:
            seen_info_ids.add(info_id)
            info_field_ids.append(info_id)

    with open_text(path) as handle:
        for line in handle:
            if line.startswith("##INFO="):
                parsed = parse_vcf_info_header(line)
                if parsed:
                    info_id, number = parsed
                    info_numbers[info_id] = number
                    remember_info_id(info_id)
                continue
            if not line or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            chrom, pos, variant_id, ref, alts = parts[:5]
            info = parts[7] if len(parts) > 7 else ""
            for alt_index, alt in enumerate(alts.split(",")):
                original = {"chrom": chrom, "pos": pos, "ref": ref, "alt": alt}
                info_values = parse_vcf_info_values(info, alt_index, info_numbers)
                for column in info_values:
                    remember_info_id(column.removeprefix(VCF_INFO_COLUMN_PREFIX))
                original.update(info_values)
                payload = json.dumps(original, ensure_ascii=False, separators=(",", ":"))
                for key in original_variant_lookup_keys(chrom, pos, ref, alt, variant_id):
                    batch.append((key, payload))
                if len(batch) >= SQLITE_INSERT_BATCH_SIZE:
                    flush_original_variant_batch(con, batch)

    flush_original_variant_batch(con, batch)
    return SQLiteOriginalVariantLookup(con), info_field_ids


def strip_hgvs_prefix(value: str) -> str:
    if not value or value == "-":
        return value
    value = unquote(value)
    if ":" in value:
        return value.split(":", 1)[1]
    return value


def first_nonempty(*values: str) -> str:
    for value in values:
        if value not in (None, "", "-"):
            return value
    return "-"


def parse_float(value: str):
    try:
        if value in ("", "-", None):
            return None
        return float(value)
    except ValueError:
        return None


def max_float_string(row: dict[str, str], fields: list[str]) -> str:
    best = None
    for field in fields:
        value = parse_float(row.get(field, ""))
        if value is None:
            continue
        if best is None or value > best:
            best = value
    return f"{best:g}" if best is not None else "-"


def parse_spliceai(value: str) -> tuple[str, str]:
    if not value or value == "-":
        return "-", "-"
    best_score = None
    best_type = "-"
    # SpliceAI format: SYMBOL|DS_AG|DS_AL|DS_DG|DS_DL|DP_AG|DP_AL|DP_DG|DP_DL
    for record in value.split("&"):
        parts = record.split("|")
        if len(parts) < 5:
            continue
        scores = [parse_float(parts[i]) for i in range(1, 5)]
        for (label, effect), score in zip(SPLICEAI_TYPES, scores):
            if score is None:
                continue
            if best_score is None or score > best_score:
                best_score = score
                best_type = effect
    if best_score is None:
        return "-", "-"
    if best_score <= 0:
        return f"{best_score:g}", "-"
    return f"{best_score:g}", best_type


def clean_output_value(value) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def split_multi_value(value: str) -> list[str]:
    if score_is_missing(value):
        return []
    return [part.strip() for part in re.split(r"[,;&|]+", score_text(value)) if part.strip()]


def strip_transcript_version(value: str) -> str:
    return re.sub(r"\.\d+$", "", score_text(value))


def is_yes(value: str) -> bool:
    return score_text(value).upper() in {"YES", "1", "TRUE"}


def normalize_tissue_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", score_text(value).lower())


def parse_tissue_values(values: list[str]) -> list[str]:
    tissues: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        for item in re.split(r"[,;]+", value or ""):
            item = item.strip()
            if not item:
                continue
            key = normalize_tissue_name(item)
            if key and key not in seen:
                seen.add(key)
                tissues.append(item)
    return tissues


def read_tissues_file(path: str | None) -> list[str]:
    if not path:
        return []
    with open(path) as handle:
        text = handle.read()
    return parse_tissue_values([text])


def dedupe_preserve_order(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = normalize_tissue_name(value)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def gtex_v11_tissue_column_map(parquet_path: str | None) -> dict[str, str]:
    if not parquet_path or not Path(parquet_path).is_file():
        return {}
    try:
        import duckdb  # type: ignore
    except Exception as exc:
        print(f"[WARN] Cannot read GTEx v11 tissue columns because duckdb is unavailable: {exc}", file=sys.stderr)
        return {}
    con = duckdb.connect(database=":memory:")
    try:
        rows = con.execute("describe select * from read_parquet(?)", [parquet_path]).fetchall()
    finally:
        con.close()
    return {
        normalize_tissue_name(row[0]): row[0]
        for row in rows
        if row[0] != "transcript_id"
    }


def canonicalize_gtex_v11_tissues(
    tissues: list[str],
    parquet_path: str | None,
    label: str,
) -> list[str]:
    if not tissues:
        return []
    by_normalized = gtex_v11_tissue_column_map(parquet_path)
    if not by_normalized:
        print(f"[WARN] No GTEx v11 tissue columns available for {label}; tissue whitelist is empty", file=sys.stderr)
        return []
    canonical: list[str] = []
    missing: list[str] = []
    for tissue in tissues:
        column = by_normalized.get(normalize_tissue_name(tissue))
        if column:
            canonical.append(column)
        else:
            missing.append(tissue)
    canonical = dedupe_preserve_order(canonical)
    if missing:
        print(
            f"[WARN] {label} tissue(s) not present in GTEx v11 transcript TPM: "
            + ",".join(dedupe_preserve_order(missing)),
            file=sys.stderr,
        )
    return canonical


def resolve_hpo_tissues(
    raw_hpo_ids: list[str],
    hpo_file: str | None,
    data_dir: str,
    top_n: int,
    gtex_transcript_tpm: str | None,
) -> list[str]:
    if not raw_hpo_ids and not hpo_file:
        return []
    try:
        from export_hpo_tissue_tpm import (  # type: ignore
            ExpressionExporter,
            HPOMapper,
            normalize_hpo_ids,
            read_items_file,
        )
    except Exception as exc:
        print(f"[WARN] HPO tissue mapping unavailable: {exc}", file=sys.stderr)
        return []

    raw_items = list(raw_hpo_ids or []) + read_items_file(hpo_file)
    hpo_ids = normalize_hpo_ids(raw_items)
    if not hpo_ids:
        print("[WARN] No valid HPO IDs were provided for tissue mapping", file=sys.stderr)
        return []

    data_path = Path(data_dir)
    mapper = HPOMapper(
        str(data_path / "phenotype_to_anatomy.txt"),
        str(data_path / "uberon.obo"),
        str(data_path / "hp.obo"),
        hp_full_owl=str(data_path / "hp-full.owl"),
        top_n=top_n,
    )
    mapper.load()
    coarse_tissues = mapper.map(hpo_ids)
    expanded: list[str] = []
    for tissue in coarse_tissues:
        aliases = ExpressionExporter.TISSUE_TO_GTEX.get(tissue, [])
        expanded.extend(aliases or [tissue])
    v11_tissues = canonicalize_gtex_v11_tissues(expanded, gtex_transcript_tpm, "HPO-derived")
    if v11_tissues:
        print("[HPO] GTEx v11 tissue whitelist: " + ",".join(v11_tissues), file=sys.stderr)
    return v11_tissues


def sql_quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def format_float(value, digits: int = 4) -> str:
    if value is None:
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "-"
    if not math.isfinite(number):
        return "-"
    return f"{number:.{digits}g}"


class GTExTranscriptLookup:
    def __init__(self, parquet_path: str | None, clinical_tissues: list[str]):
        self.available = False
        self.status = "disabled"
        self.records: dict[str, dict[str, float]] = {}
        self.tissue_columns: list[str] = []
        self.clinical_columns: list[str] = []
        self.parquet_path = parquet_path
        self.clinical_tissues = clinical_tissues
        self.duckdb = None
        if not parquet_path:
            return
        if not Path(parquet_path).is_file():
            self.status = "gtex_file_missing"
            return
        try:
            import duckdb  # type: ignore
        except Exception:
            self.status = "duckdb_unavailable"
            return
        self.duckdb = duckdb
        self.available = True
        self.status = "ready"
        self._load_columns()

    def _load_columns(self) -> None:
        con = self.duckdb.connect(database=":memory:")
        try:
            rows = con.execute(
                "describe select * from read_parquet(?)",
                [self.parquet_path],
            ).fetchall()
        finally:
            con.close()
        all_columns = [row[0] for row in rows]
        self.tissue_columns = [col for col in all_columns if col != "transcript_id"]
        by_normalized = {normalize_tissue_name(col): col for col in self.tissue_columns}
        clinical_columns: list[str] = []
        seen: set[str] = set()
        for tissue in self.clinical_tissues:
            column = by_normalized.get(normalize_tissue_name(tissue))
            if column and column not in seen:
                seen.add(column)
                clinical_columns.append(column)
        self.clinical_columns = clinical_columns

    def load(self, transcript_ids: list[str]) -> None:
        if not self.available:
            return
        base_ids = sorted({strip_transcript_version(tx) for tx in transcript_ids if tx})
        if not base_ids:
            return
        values_sql = ",".join(f"({sql_literal(tx)})" for tx in base_ids)
        select_columns = ["transcript_id"] + [sql_quote_identifier(col) for col in self.tissue_columns]
        sql = f"""
            WITH query_ids(base_id) AS (VALUES {values_sql})
            SELECT {", ".join(select_columns)}
            FROM read_parquet({sql_literal(self.parquet_path)}) p
            JOIN query_ids q
              ON regexp_replace(p.transcript_id, '\\.[0-9]+$', '') = q.base_id
        """
        con = self.duckdb.connect(database=":memory:")
        try:
            cursor = con.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            for values in cursor.fetchall():
                record = dict(zip(columns, values))
                transcript_id = score_text(record.pop("transcript_id"))
                if not transcript_id:
                    continue
                clean_record = {}
                for tissue, value in record.items():
                    try:
                        number = float(value or 0)
                    except (TypeError, ValueError):
                        number = 0.0
                    clean_record[tissue] = number if math.isfinite(number) else 0.0
                self.records[transcript_id] = clean_record
                self.records.setdefault(strip_transcript_version(transcript_id), clean_record)
        finally:
            con.close()

    def expression_for(self, transcript_id: str) -> tuple[dict[str, float] | None, str]:
        if not self.available:
            return None, self.status
        record = self.records.get(transcript_id) or self.records.get(strip_transcript_version(transcript_id))
        if record is None:
            return None, "not_found"
        return record, "ok"


class FullGTExTranscriptLookup:
    def __init__(self, parquet_path: str | None, clinical_tissues: list[str]):
        self.available = False
        self.status = "disabled"
        self.records: dict[str, dict[str, float]] = {}
        self.tissue_columns: list[str] = []
        self.clinical_columns: list[str] = []
        self.parquet_path = parquet_path
        self.clinical_tissues = clinical_tissues
        self.duckdb = None
        if not parquet_path:
            return
        if not Path(parquet_path).is_file():
            self.status = "gtex_file_missing"
            return
        try:
            import duckdb  # type: ignore
        except Exception:
            self.status = "duckdb_unavailable"
            return
        self.duckdb = duckdb
        self.available = True
        self.status = "ready"
        self._load_all_records()

    def _load_all_records(self) -> None:
        con = self.duckdb.connect(database=":memory:")
        try:
            described = con.execute(
                "describe select * from read_parquet(?)",
                [self.parquet_path],
            ).fetchall()
            all_columns = [row[0] for row in described]
            self.tissue_columns = [col for col in all_columns if col != "transcript_id"]
            by_normalized = {normalize_tissue_name(col): col for col in self.tissue_columns}
            seen: set[str] = set()
            for tissue in self.clinical_tissues:
                column = by_normalized.get(normalize_tissue_name(tissue))
                if column and column not in seen:
                    seen.add(column)
                    self.clinical_columns.append(column)

            select_columns = ["transcript_id"] + [
                sql_quote_identifier(col) for col in self.tissue_columns
            ]
            cursor = con.execute(
                f"select {', '.join(select_columns)} from read_parquet(?)",
                [self.parquet_path],
            )
            while True:
                batch = cursor.fetchmany(10000)
                if not batch:
                    break
                for values in batch:
                    transcript_id = score_text(values[0])
                    if not transcript_id:
                        continue
                    record: dict[str, float] = {}
                    for tissue, value in zip(self.tissue_columns, values[1:]):
                        try:
                            number = float(value or 0)
                        except (TypeError, ValueError):
                            number = 0.0
                        record[tissue] = number if math.isfinite(number) else 0.0
                    self.records[transcript_id] = record
                    self.records.setdefault(strip_transcript_version(transcript_id), record)
        finally:
            con.close()

    def load(self, transcript_ids: list[str]) -> None:
        return None

    def expression_for(self, transcript_id: str) -> tuple[dict[str, float] | None, str]:
        if not self.available:
            return None, self.status
        record = self.records.get(transcript_id) or self.records.get(strip_transcript_version(transcript_id))
        if record is None:
            return None, "not_found"
        return record, "ok"


def top_tissues(record: dict[str, float], limit: int = 5) -> list[tuple[str, float]]:
    return sorted(record.items(), key=lambda item: item[1], reverse=True)[:limit]


def expression_score_from_tpm(tpm: float, full_weight: bool) -> int:
    if tpm >= 10:
        return 20 if full_weight else 10
    if tpm >= 5:
        return 16 if full_weight else 8
    if tpm >= 1:
        return 10 if full_weight else 5
    if tpm >= 0.1:
        return 4 if full_weight else 2
    return 0


def transcript_refseq_ids(row: dict[str, str]) -> list[str]:
    ids = split_multi_value(first_nonempty(row.get("refseq_id", ""), row.get("RefSeq", "")))
    transcript_id = row.get("transcript_id", "")
    if transcript_id.startswith(("NM_", "NR_", "XM_", "XR_")):
        ids.append(transcript_id)
    seen: set[str] = set()
    unique: list[str] = []
    for item in ids:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def has_curated_refseq(row: dict[str, str]) -> bool:
    return any(item.startswith(("NM_", "NR_")) for item in transcript_refseq_ids(row))


def has_only_predicted_refseq(row: dict[str, str]) -> bool:
    ids = transcript_refseq_ids(row)
    return bool(ids) and all(item.startswith(("XM_", "XR_")) for item in ids)


def tx_consequence_score(row: dict[str, str]) -> int:
    terms = consequence_terms(row)
    if not terms:
        return 0
    return max(TX_CONSEQUENCE_SCORES.get(term, 0) for term in terms)


def tx_has_mane_select(row: dict[str, str]) -> bool:
    return not score_is_missing(row.get("mane_select", "")) or normalize_words(row.get("mane", "")) == "mane_select"


def tx_has_mane_plus(row: dict[str, str]) -> bool:
    return not score_is_missing(row.get("mane_plus_clinical", "")) or normalize_words(row.get("mane", "")) == "mane_plus_clinical"


def tx_confidence_score(row: dict[str, str]) -> int:
    score = 0
    if tx_has_mane_select(row):
        score += 35
    elif tx_has_mane_plus(row):
        score += 32
    appris = normalize_words(row.get("appris", ""))
    if appris.startswith("p"):
        score += 18
    elif appris.startswith("a"):
        score += 8
    if not score_is_missing(row.get("ccds", "")):
        score += 12
    if is_yes(row.get("canonical", "")):
        score += 10
    tsl = normalize_words(row.get("tsl", ""))
    if tsl == "1":
        score += 8
    elif tsl == "2":
        score += 5
    elif tsl == "3":
        score += 2
    if has_curated_refseq(row):
        score += 8
    if is_yes(row.get("vep_pick", "")):
        score += 3
    return min(score, 35)


def tx_tie_breaker_score(row: dict[str, str]) -> int:
    score = 0
    if is_yes(row.get("vep_pick", "")):
        score += 2
    if not score_is_missing(row.get("hgvsc", "")):
        score += 1
    if not score_is_missing(row.get("hgvsp", "")):
        score += 1
    if not score_is_missing(row.get("protein_position", "")):
        score += 1
    if not score_is_missing(row.get("protein_domains", "")):
        score += 1
    return min(score, 5)


def tx_has_support(row: dict[str, str]) -> bool:
    return any(
        [
            tx_has_mane_select(row),
            tx_has_mane_plus(row),
            not score_is_missing(row.get("ccds", "")),
            is_yes(row.get("canonical", "")),
            normalize_words(row.get("appris", "")).startswith(("p", "a")),
            normalize_words(row.get("tsl", "")) in {"1", "2", "3"},
            has_curated_refseq(row),
        ]
    )


def tx_exclusion_reasons(row: dict[str, str]) -> list[str]:
    reasons: list[str] = []
    transcript_id = row.get("transcript_id", "")
    biotype = normalize_words(row.get("biotype", ""))
    flags = {normalize_words(flag) for flag in split_multi_value(row.get("transcript_flags", ""))}
    if transcript_id.startswith(("XM_", "XR_")) or has_only_predicted_refseq(row):
        reasons.append("predicted_refseq")
    if biotype in TX_EXCLUDED_BIOTYPES:
        reasons.append(f"biotype:{biotype}")
    elif biotype and biotype != "protein_coding":
        reasons.append(f"non_protein_coding:{biotype}")
    if TX_BAD_FLAGS.intersection(flags):
        reasons.append("incomplete_cds")
    if normalize_words(row.get("tsl", "")) == "5" and not tx_has_support(row):
        reasons.append("tsl5_no_support")
    return reasons


def annotate_gtex_for_rows(rows: list[dict[str, str]], lookup: GTExTranscriptLookup) -> None:
    lookup.load([row.get("transcript_id", "") for row in rows])
    clinical_label = ",".join(lookup.clinical_columns) if lookup.clinical_columns else "-"
    for row in rows:
        row["clinical_gtex_tissue_whitelist"] = clinical_label
        record, status = lookup.expression_for(row.get("transcript_id", ""))
        row["gtex_lookup_status"] = status
        row["clinical_best_tissue"] = "-"
        row["clinical_transcript_tpm"] = "-"
        row["gtex_transcript_max_tissue"] = "-"
        row["gtex_transcript_max_tpm"] = "-"
        row["gtex_transcript_top5_tissues"] = "-"
        row["gtex_max_tissue_in_clinical_whitelist"] = "-"
        row["clinical_vs_global_tpm_ratio"] = "-"
        if not record:
            row["clinical_expression_score"] = "0"
            continue

        ranked = top_tissues(record, 5)
        if ranked:
            max_tissue, max_tpm = ranked[0]
            row["gtex_transcript_max_tissue"] = max_tissue
            row["gtex_transcript_max_tpm"] = format_float(max_tpm)
            row["gtex_transcript_top5_tissues"] = ";".join(f"{t}:{format_float(v)}" for t, v in ranked)
        else:
            max_tissue, max_tpm = "-", 0.0

        clinical_values = [(tissue, record.get(tissue, 0.0)) for tissue in lookup.clinical_columns]
        clinical_values = [(tissue, value) for tissue, value in clinical_values if value is not None]
        if clinical_values:
            best_tissue, best_tpm = max(clinical_values, key=lambda item: item[1])
            row["clinical_best_tissue"] = best_tissue
            row["clinical_transcript_tpm"] = format_float(best_tpm)
            row["gtex_max_tissue_in_clinical_whitelist"] = "YES" if max_tissue in lookup.clinical_columns else "NO"
            if max_tpm > 0:
                row["clinical_vs_global_tpm_ratio"] = format_float(best_tpm / max_tpm)
            row["clinical_expression_score"] = str(expression_score_from_tpm(best_tpm, full_weight=True))
        else:
            row["clinical_expression_score"] = str(expression_score_from_tpm(max_tpm, full_weight=False))


def score_transcript_rows(rows: list[dict[str, str]]) -> None:
    for row in rows:
        reasons = tx_exclusion_reasons(row)
        row["tx_exclusion_reason"] = ";".join(reasons) if reasons else "-"
        row["tx_rescue_reason"] = "-"
        row["tx_eligibility"] = "excluded" if reasons else "primary"
        consequence = tx_consequence_score(row)
        confidence = tx_confidence_score(row)
        expression = row_score(row, "clinical_expression_score")
        tie = tx_tie_breaker_score(row)
        row["tx_consequence_score"] = str(consequence)
        row["tx_confidence_score"] = str(confidence)
        row["tx_tie_breaker_score"] = str(tie)
        row["tx_selection_score"] = str(consequence + confidence + expression + tie)
        row["tx_rank_within_variant"] = "-"
        row["tx_selected_reason"] = "-"


def transcript_group_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return (
        row.get("chrom", ""),
        row.get("pos", ""),
        row.get("ref", ""),
        row.get("alt", ""),
        row.get("gene_symbol", ""),
    )


def transcript_sort_key(row: dict[str, str]) -> tuple[int, int, int, int, int, str]:
    return (
        row_score(row, "tx_selection_score"),
        row_score(row, "tx_consequence_score"),
        row_score(row, "tx_confidence_score"),
        row_score(row, "clinical_expression_score"),
        row_score(row, "tx_tie_breaker_score"),
        row.get("transcript_id", ""),
    )


def select_transcripts(rows: list[dict[str, str]], top_k: int) -> list[dict[str, str]]:
    if top_k <= 0:
        for row in rows:
            row["tx_eligibility"] = "selected"
            row["tx_selected_reason"] = "selection_disabled"
        return rows

    grouped: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(transcript_group_key(row), []).append(row)

    selected_rows: list[dict[str, str]] = []
    for group_rows in grouped.values():
        primary = [row for row in group_rows if row.get("tx_eligibility") == "primary"]
        primary_max_consequence = max((row_score(row, "tx_consequence_score") for row in primary), default=-1)
        for row in group_rows:
            if row.get("tx_eligibility") != "excluded":
                continue
            consequence = row_score(row, "tx_consequence_score")
            expression = row_score(row, "clinical_expression_score")
            if consequence >= 40 and primary_max_consequence < 40:
                row["tx_eligibility"] = "rescued"
                row["tx_rescue_reason"] = "unique_high_impact_consequence"
            elif consequence >= 14 and expression >= 16:
                row["tx_eligibility"] = "rescued"
                row["tx_rescue_reason"] = "high_expression_with_possible_effect"

        rankable = [row for row in group_rows if row.get("tx_eligibility") in {"primary", "rescued"}]
        if not rankable:
            rankable = sorted(group_rows, key=transcript_sort_key, reverse=True)[:1]
            for row in rankable:
                row["tx_eligibility"] = "rescued"
                row["tx_rescue_reason"] = "no_primary_transcript_available"

        ranked = sorted(rankable, key=transcript_sort_key, reverse=True)
        for rank, row in enumerate(ranked, start=1):
            row["tx_rank_within_variant"] = str(rank)

        selected = ranked[:top_k]
        selected_ids = {id(row) for row in selected}
        for row in selected:
            row["tx_selected_reason"] = "top_k"
            if row.get("tx_eligibility") == "primary":
                row["tx_eligibility"] = "selected"

        force_reasons = [
            ("mane_select", lambda row: tx_has_mane_select(row)),
            ("mane_plus_clinical", lambda row: tx_has_mane_plus(row)),
            ("vep_pick", lambda row: is_yes(row.get("vep_pick", ""))),
        ]
        max_consequence = max(row_score(row, "tx_consequence_score") for row in group_rows)
        max_consequence_row = sorted(
            [row for row in group_rows if row_score(row, "tx_consequence_score") == max_consequence],
            key=transcript_sort_key,
            reverse=True,
        )[0]
        for row in group_rows:
            reasons = [name for name, predicate in force_reasons if predicate(row)]
            if row is max_consequence_row and max_consequence > 0:
                reasons.append("max_consequence")
            if not reasons or id(row) in selected_ids:
                continue
            if row.get("tx_eligibility") == "excluded" and row_score(row, "tx_consequence_score") < 40:
                continue
            row["tx_selected_reason"] = "force:" + ",".join(reasons)
            if row.get("tx_eligibility") == "primary":
                row["tx_eligibility"] = "forced"
            selected.append(row)
            selected_ids.add(id(row))

        selected_rows.extend(selected)

    return selected_rows


def add_requested_columns(
    row: dict[str, str],
    extra: dict[str, str],
    original_variant: dict[str, str] | None = None,
) -> None:
    parsed = original_variant or parse_uploaded_variation(row.get("Uploaded_variation", ""))
    for key, value in parsed.items():
        row[key] = value

    row["gene_symbol"] = first_nonempty(row.get("SYMBOL", ""), extra.get("SYMBOL", ""), row.get("Gene", ""))
    row["transcript_id"] = first_nonempty(row.get("Feature", ""))
    row["refseq_id"] = first_nonempty(row.get("RefSeq", ""), extra.get("RefSeq", ""))
    row["biotype"] = first_nonempty(row.get("BIOTYPE", ""), extra.get("BIOTYPE", ""))
    row["canonical"] = first_nonempty(row.get("CANONICAL", ""), extra.get("CANONICAL", ""))
    row["mane"] = first_nonempty(row.get("MANE", ""), extra.get("MANE", ""))
    row["mane_select"] = first_nonempty(row.get("MANE_SELECT", ""), extra.get("MANE_SELECT", ""))
    row["mane_plus_clinical"] = first_nonempty(
        row.get("MANE_PLUS_CLINICAL", ""),
        extra.get("MANE_PLUS_CLINICAL", ""),
    )
    row["appris"] = first_nonempty(row.get("APPRIS", ""), extra.get("APPRIS", ""))
    row["tsl"] = first_nonempty(row.get("TSL", ""), extra.get("TSL", ""))
    row["ccds"] = first_nonempty(row.get("CCDS", ""), extra.get("CCDS", ""))
    row["vep_pick"] = first_nonempty(row.get("PICK", ""), extra.get("PICK", ""))
    row["transcript_flags"] = first_nonempty(row.get("FLAGS", ""), extra.get("FLAGS", ""))
    row["consequence"] = first_nonempty(row.get("Consequence", ""))
    row["impact"] = first_nonempty(row.get("IMPACT", ""), extra.get("IMPACT", ""))
    row["hgvsc"] = strip_hgvs_prefix(first_nonempty(row.get("HGVSc", ""), extra.get("HGVSc", "")))
    row["hgvsp"] = strip_hgvs_prefix(first_nonempty(row.get("HGVSp", ""), extra.get("HGVSp", "")))
    row["cdna_position"] = first_nonempty(row.get("cDNA_position", ""))
    row["cds_position"] = first_nonempty(row.get("CDS_position", ""))
    row["protein_position"] = first_nonempty(row.get("Protein_position", ""))
    row["amino_acids"] = first_nonempty(row.get("Amino_acids", ""))
    row["codons"] = first_nonempty(row.get("Codons", ""))
    row["exon"] = first_nonempty(row.get("EXON", ""), extra.get("EXON", ""))
    row["intron"] = first_nonempty(row.get("INTRON", ""), extra.get("INTRON", ""))
    row["strand"] = first_nonempty(row.get("STRAND", ""), extra.get("STRAND", ""))
    row["protein_domains"] = first_nonempty(row.get("DOMAINS", ""), extra.get("DOMAINS", ""))
    row["revel_score"] = first_nonempty(row.get("REVEL_score", ""), extra.get("REVEL_score", ""))
    row["cadd_phred"] = first_nonempty(
        row.get("CADD_phred", ""),
        extra.get("CADD_phred", ""),
        row.get("CADD_PHRED", ""),
        extra.get("CADD_PHRED", ""),
    )
    native_popmax_af = first_nonempty(
        max_float_string(row, GNOMAD_NATIVE_POP_AF_FIELDS),
        max_float_string(row, GNOMAD_NATIVE_OVERALL_AF_FIELDS),
    )
    native_eas_af = max_float_string(row, GNOMAD_NATIVE_EAS_AF_FIELDS)
    row["gnomAD_popmax_AF"] = first_nonempty(row.get("gnomAD4.1_joint_POPMAX_AF", ""), native_popmax_af)
    row["gnomAD_eas_AF"] = first_nonempty(row.get("gnomAD4.1_joint_EAS_AF", ""), native_eas_af)
    row["gnomAD_nhomalt"] = first_nonempty(
        row.get("gnomAD4.1_joint_nhomalt", ""),
        extra.get("gnomAD4.1_joint_nhomalt", ""),
    )
    splice_score, splice_type = parse_spliceai(first_nonempty(row.get("SpliceAI_pred", ""), extra.get("SpliceAI_pred", "")))
    row["spliceAI_ds_max"] = splice_score
    row["spliceAI_type"] = splice_type
    row["loftee_lof_flag"] = first_nonempty(row.get("LoF", ""), extra.get("LoF", ""))
    row["loftee_lof_filter"] = first_nonempty(row.get("LoF_filter", ""), extra.get("LoF_filter", ""))
    clinvar_significance = clean_clinvar_value(
        first_nonempty(row.get("ClinVar_CLNSIG", ""), extra.get("ClinVar_CLNSIG", ""), "")
    )
    clinvar_review_status_raw = first_nonempty(
        row.get("ClinVar_CLNREVSTAT", ""), extra.get("ClinVar_CLNREVSTAT", ""), ""
    )
    row["clinvar_significance"] = clinvar_significance
    row["clinvar_review_status"] = clean_clinvar_value(clinvar_review_status_raw)
    row["clinvar_star_rating"] = str(clinvar_star_rating(clinvar_review_status_raw))
    row.setdefault("all_genes", row["gene_symbol"])


def open_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open()


def convert_vep_table_to_csv(
    vep_path: Path,
    csv_path: Path,
    original_variants: dict[str, dict[str, str]] | None = None,
    vcf_info_ids: list[str] | None = None,
    top_k_transcripts: int = 5,
    clinical_tissues: list[str] | None = None,
    gtex_transcript_tpm: str | None = None,
    disable_gtex_expression: bool = False,
    disable_transcript_selection: bool = False,
    include_vcf_info: bool = True,
    rank_pathogenic: bool = True,
) -> int:
    rows: list[dict[str, str]] = []
    extra_keys: set[str] = set()
    genes_by_variant: dict[str, set[str]] = {}
    header: list[str] | None = None
    original_variants = original_variants or {}

    with open_text(vep_path) as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            if line.startswith("##"):
                continue
            if line.startswith("#"):
                header = line.lstrip("#").split("\t")
                continue
            if header is None:
                raise ValueError("VEP output header was not found")
            parts = line.split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            row = dict(zip(header, parts))
            extra = parse_extra(row.pop("Extra", ""))
            row.update(extra)
            original_variant = original_variants.get(row.get("Uploaded_variation", ""))
            add_requested_columns(row, extra, original_variant)
            extra_keys.update(extra)
            variant_id = row.get("Uploaded_variation", "")
            gene_symbol = row.get("gene_symbol", "")
            if variant_id and gene_symbol and gene_symbol != "-":
                genes_by_variant.setdefault(variant_id, set()).add(gene_symbol)
            rows.append(row)

    for row in rows:
        variant_id = row.get("Uploaded_variation", "")
        genes = sorted(genes_by_variant.get(variant_id, set()))
        row["all_genes"] = ",".join(genes) if genes else row.get("gene_symbol", "-")

    clinical_tissues = clinical_tissues or []
    gtex_lookup = GTExTranscriptLookup(
        None if disable_gtex_expression else gtex_transcript_tpm,
        clinical_tissues,
    )
    annotate_gtex_for_rows(rows, gtex_lookup)
    score_transcript_rows(rows)
    if not disable_transcript_selection:
        rows = select_transcripts(rows, top_k_transcripts)

    if rank_pathogenic:
        add_pathogenic_ranks(rows)
    else:
        for row in rows:
            add_pathogenic_fields(row)
            row["pathogenic_rank"] = "-"
    fieldnames = build_output_columns(vcf_info_ids if include_vcf_info else [])

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            for field in fieldnames:
                row[field] = clean_output_value(row.get(field, "-"))
        writer.writerows(rows)
    return len(rows)


def sqlite_temp_path(csv_path: Path, explicit_path: str | None = None) -> Path:
    if explicit_path:
        path = Path(explicit_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_handle = tempfile.NamedTemporaryFile(
        prefix=f"{csv_path.name}.",
        suffix=".sqlite",
        dir=str(csv_path.parent),
        delete=False,
    )
    path = Path(tmp_handle.name)
    tmp_handle.close()
    return path


def open_selected_rows_db(path: Path, force: bool = True) -> sqlite3.Connection:
    if force:
        cleanup_sqlite_db(path)
    con = sqlite3.connect(str(path))
    con.execute("pragma journal_mode=wal")
    con.execute("pragma synchronous=normal")
    con.execute("pragma temp_store=file")
    con.execute("pragma cache_size=-200000")
    con.execute(
        "create table if not exists selected_rows "
        "(score integer not null, seq integer not null, payload text not null)"
    )
    if force:
        con.execute("delete from selected_rows")
        con.commit()
    return con


def cleanup_sqlite_db(path: Path) -> None:
    path.unlink(missing_ok=True)
    for suffix in ("-wal", "-shm"):
        Path(str(path) + suffix).unlink(missing_ok=True)


def parse_vep_table_groups(
    vep_path: Path,
    original_variants: dict[str, dict[str, str]],
):
    header: list[str] | None = None
    current_key: str | None = None
    current_rows: list[dict[str, str]] = []

    with open_text(vep_path) as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            if line.startswith("##"):
                continue
            if line.startswith("#"):
                header = line.lstrip("#").split("\t")
                continue
            if header is None:
                raise ValueError("VEP output header was not found")
            parts = line.split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            row = dict(zip(header, parts))
            extra = parse_extra(row.pop("Extra", ""))
            row.update(extra)
            variant_id = row.get("Uploaded_variation", "")
            original_variant = original_variants.get(variant_id)
            add_requested_columns(row, extra, original_variant)
            if current_key is not None and variant_id != current_key:
                yield current_key, current_rows
                current_rows = []
            current_key = variant_id
            current_rows.append(row)

    if current_rows:
        yield current_key or "", current_rows


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


def flush_selected_row_batch(con: sqlite3.Connection, batch: list[tuple[int, int, str]]) -> None:
    if not batch:
        return
    con.executemany(
        "insert into selected_rows(score, seq, payload) values (?, ?, ?)",
        batch,
    )
    con.commit()
    batch.clear()


def stage_selected_rows_to_sqlite(
    vep_path: Path,
    original_variants: dict[str, dict[str, str]],
    fieldnames: list[str],
    clinical_tissues: list[str],
    gtex_transcript_tpm: str | None,
    disable_gtex_expression: bool,
    disable_transcript_selection: bool,
    top_k_transcripts: int,
    con: sqlite3.Connection,
) -> int:
    lookup = FullGTExTranscriptLookup(
        None if disable_gtex_expression else gtex_transcript_tpm,
        clinical_tissues,
    )
    rows_written = 0
    seq = 0
    batch: list[tuple[int, int, str]] = []

    for _variant_id, group_rows in parse_vep_table_groups(vep_path, original_variants):
        genes = sorted(
            {
                row.get("gene_symbol", "")
                for row in group_rows
                if row.get("gene_symbol") and row.get("gene_symbol") != "-"
            }
        )
        all_genes = ",".join(genes) if genes else "-"
        for row in group_rows:
            row["all_genes"] = all_genes if all_genes != "-" else row.get("gene_symbol", "-")

        annotate_gtex_for_rows(group_rows, lookup)
        score_transcript_rows(group_rows)
        selected_rows = (
            group_rows
            if disable_transcript_selection
            else select_transcripts(group_rows, top_k_transcripts)
        )

        for row in selected_rows:
            score = add_pathogenic_fields(row)
            payload = {
                field: clean_output_value(row.get(field, "-"))
                for field in fieldnames
            }
            batch.append(
                (
                    score,
                    seq,
                    json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                )
            )
            seq += 1
            rows_written += 1

        if len(batch) >= SQLITE_INSERT_BATCH_SIZE:
            flush_selected_row_batch(con, batch)

    flush_selected_row_batch(con, batch)
    return rows_written


def write_ranked_sqlite_csv(
    con: sqlite3.Connection,
    csv_path: Path,
    fieldnames: list[str],
    rank_pathogenic: bool = True,
) -> int:
    partial_path = csv_path.with_suffix(csv_path.suffix + ".partial")
    partial_path.unlink(missing_ok=True)
    con.execute("create index if not exists selected_rows_score_seq on selected_rows(score desc, seq asc)")
    con.commit()

    rows = 0
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with partial_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        order_sql = "select payload from selected_rows order by score desc, seq asc" if rank_pathogenic else "select payload from selected_rows order by seq asc"
        cursor = con.execute(order_sql)
        while True:
            batch = cursor.fetchmany(SQLITE_FETCH_BATCH_SIZE)
            if not batch:
                break
            for (payload,) in batch:
                rows += 1
                row = json.loads(payload)
                row["pathogenic_rank"] = str(rows) if rank_pathogenic else "-"
                writer.writerow(row)
    partial_path.replace(csv_path)
    return rows


def convert_vep_table_to_csv_sqlite(
    vep_path: Path,
    csv_path: Path,
    original_variants: dict[str, dict[str, str]] | None = None,
    original_vcf_path: Path | None = None,
    vcf_info_ids: list[str] | None = None,
    top_k_transcripts: int = 5,
    clinical_tissues: list[str] | None = None,
    gtex_transcript_tpm: str | None = None,
    disable_gtex_expression: bool = False,
    disable_transcript_selection: bool = False,
    sqlite_db: str | None = None,
    keep_sqlite_db: bool = False,
    include_vcf_info: bool = True,
    rank_pathogenic: bool = True,
) -> int:
    db_path = sqlite_temp_path(csv_path, sqlite_db)
    explicit_db = sqlite_db is not None
    clinical_tissues = clinical_tissues or []

    con = open_selected_rows_db(db_path, force=True)
    try:
        if original_vcf_path is not None:
            original_variants, vcf_info_ids = load_original_vcf_coordinates_sqlite(
                original_vcf_path,
                con,
            )
        else:
            original_variants = original_variants or {}
        fieldnames = build_output_columns(vcf_info_ids if include_vcf_info else [])
        stage_selected_rows_to_sqlite(
            vep_path,
            original_variants,
            fieldnames,
            clinical_tissues,
            gtex_transcript_tpm,
            disable_gtex_expression,
            disable_transcript_selection,
            top_k_transcripts,
            con,
        )
        return write_ranked_sqlite_csv(con, csv_path, fieldnames, rank_pathogenic=rank_pathogenic)
    finally:
        con.close()
        if not keep_sqlite_db and not explicit_db:
            cleanup_sqlite_db(db_path)


def run_command(cmd: list[str], env: dict[str, str], log_path: Path | None) -> None:
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w") as log:
            log.write("COMMAND:\n")
            log.write(" ".join(cmd) + "\n\n")
            log.flush()
            result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, text=True)
    else:
        result = subprocess.run(cmd, env=env, text=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run local VEP with configured plugins and convert VEP tab output to CSV."
    )
    parser.add_argument("-i", "--input", required=True, help="Input VCF or VEP-supported variant file")
    parser.add_argument("-o", "--output", required=True, help="Output CSV path")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "config" / "vep_runner_config.json"),
        help="Path to JSON config",
    )
    parser.add_argument("--format", default="vcf", help="Input format passed to VEP, default: vcf")
    parser.add_argument("--hgvs", action="store_true", help="Add HGVS annotations. Requires configured FASTA and .fai")
    parser.add_argument("--fasta", help="Override FASTA path for --hgvs")
    parser.add_argument("--keep-vep", help="Keep raw VEP tab output at this path")
    parser.add_argument("--log", help="Write VEP command and log to this file")
    parser.add_argument("--no-pick", action="store_true", help="Legacy option; transcript selection already keeps all VEP consequences before selecting top-k")
    parser.add_argument("--top-k-transcripts", type=int, default=5, help="Select this many primary transcripts per variant-gene, default: 5")
    parser.add_argument("--no-transcript-selection", action="store_true", help="Output all transcript consequences after annotation")
    parser.add_argument(
        "--clinical-tissue",
        action="append",
        default=[],
        help="GTEx tissue name for phenotype-aware transcript expression; can be repeated or comma-separated",
    )
    parser.add_argument("--clinical-tissues-file", help="File containing comma/semicolon/newline-separated GTEx tissue names")
    parser.add_argument(
        "--hpo-id",
        action="append",
        default=[],
        help="HPO ID for automatic tissue mapping; can be repeated or comma-separated, e.g. HP:0001250",
    )
    parser.add_argument("--hpo-file", help="File containing HPO IDs separated by whitespace/comma/semicolon")
    parser.add_argument("--top-n-hpo-tissues", type=int, default=3, help="Number of HPO-derived tissue groups to keep, default: 3")
    parser.add_argument("--hpo-data-dir", help="Override HPO tissue mapping data directory")
    parser.add_argument("--gtex-transcript-tpm", help="Override GTEx transcript TPM parquet path")
    parser.add_argument("--disable-gtex-expression", action="store_true", help="Disable GTEx transcript expression lookup")
    parser.add_argument(
        "--no-vcf-info-to-csv",
        action="store_true",
        help="Do not append VCF INFO fields during VEP TSV to CSV conversion; V3 uses module 05 for this step.",
    )
    parser.add_argument(
        "--no-pathogenic-ranking",
        action="store_true",
        help="Do not sort/rank final CSV by pathogenic score; V3 uses module 06 for this step.",
    )
    parser.add_argument(
        "--conversion-mode",
        choices=["sqlite", "memory"],
        default="sqlite",
        help="Raw VEP conversion backend. sqlite is disk-backed and memory-light; memory is the legacy in-memory converter.",
    )
    parser.add_argument(
        "--sqlite-db",
        help="SQLite staging database path for --conversion-mode sqlite. Defaults to a temporary file next to the output CSV.",
    )
    parser.add_argument(
        "--keep-sqlite-db",
        action="store_true",
        help="Keep the SQLite staging database when using the default temporary --sqlite-db path.",
    )
    parser.add_argument(
        "--pseudogene-annotation",
        action="store_true",
        help="Enable bundled pseudogene overlap annotation columns after CSV conversion.",
    )
    parser.add_argument(
        "--no-pseudogene-annotation",
        action="store_true",
        help="Legacy compatibility flag; pseudogene annotation is disabled unless --pseudogene-annotation is set",
    )
    parser.add_argument(
        "--pseudogene-log-json",
        help="Write pseudogene annotation JSON statistics to this path",
    )
    parser.add_argument(
        "--regulatory-annotation",
        action="store_true",
        help="Enable bundled ENCODE SCREEN cCRE regulatory INFO annotation before VEP",
    )
    parser.add_argument(
        "--no-regulatory-annotation",
        action="store_true",
        help="Legacy compatibility flag; regulatory annotation is disabled unless --regulatory-annotation is set",
    )
    parser.add_argument(
        "--regulatory-log-json",
        help="Write regulatory annotation JSON statistics to this path",
    )
    parser.add_argument(
        "--regulatory-summary-tsv",
        help="Write regulatory annotation TSV statistics to this path",
    )
    parser.add_argument(
        "--regulatory-ccre-bed",
        help="Override bundled ENCODE SCREEN cCRE BED path",
    )
    parser.add_argument(
        "--disable-plugin",
        action="append",
        default=[],
        choices=["cadd", "spliceai", "alphamissense", "dbnsfp", "loftee", "clinvar"],
        help="Disable one plugin/custom annotation; can be used multiple times",
    )
    parser.add_argument("--fork", type=int, default=1, help="VEP fork count, default: 1")
    parser.add_argument("--dry-run", action="store_true", help="Print VEP command without running")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    input_path = Path(args.input)
    output_path = Path(args.output)
    require_file(str(input_path), "Input file")
    require_file(config["vep"], "VEP executable")
    runner_dir = str(Path(__file__).resolve().parents[1])

    default_options = list(config.get("default_options", []))
    if not args.no_transcript_selection or args.no_pick:
        for pick_option in ("--pick", "--pick_allele", "--pick_allele_gene", "--per_gene", "--most_severe", "--summary"):
            while pick_option in default_options:
                default_options.remove(pick_option)
    if not args.no_transcript_selection and "--flag_pick" not in default_options:
        default_options.append("--flag_pick")
    for required_option in (
        "--mane",
        "--appris",
        "--tsl",
        "--ccds",
        "--biotype",
        "--transcript_version",
        "--xref_refseq",
    ):
        if required_option not in default_options:
            default_options.append(required_option)

    vep_input_path = input_path
    regulatory_temp_path: Path | None = None
    should_annotate_regulatory = (
        args.format.lower() == "vcf"
        and args.regulatory_annotation
        and not args.no_regulatory_annotation
    )

    cmd = [
        config["vep"],
        "--species",
        config.get("species", "homo_sapiens"),
        "--assembly",
        config.get("assembly", "GRCh38"),
        "--dir_cache",
        config["cache_dir"],
        "--dir_plugins",
        config["plugin_dir"],
        "--format",
        args.format,
        "--input_file",
        str(vep_input_path),
        "--output_file",
    ]

    temp_handle = None
    if args.keep_vep:
        vep_output = Path(args.keep_vep)
        vep_output.parent.mkdir(parents=True, exist_ok=True)
    else:
        temp_handle = tempfile.NamedTemporaryFile(
            prefix="vep_",
            suffix=".txt",
            dir=str(configured_tmp_dir(config)),
            delete=False,
        )
        vep_output = Path(temp_handle.name)
        temp_handle.close()

    cmd.append(str(vep_output))
    cmd += ["--force_overwrite", "--tab"]
    cmd += default_options
    if args.fork and args.fork > 1:
        cmd += ["--fork", str(args.fork)]

    if args.hgvs:
        fasta = args.fasta or config.get("fasta")
        require_file(fasta, "FASTA for --hgvs")
        require_file(fasta + ".fai", "FASTA index for --hgvs")
        cmd += ["--hgvs", "--fasta", fasta]

    cmd += build_plugin_args(config, set(args.disable_plugin))

    env = os.environ.copy()
    env_bin = config.get("env_bin")
    if env_bin:
        env["PATH"] = env_bin + os.pathsep + env.get("PATH", "")

    if args.dry_run:
        if should_annotate_regulatory:
            print("# Regulatory cCRE annotation will run before VEP and provide REG_CCRE_* INFO fields.")
        print(" ".join(cmd))
        if temp_handle is not None:
            vep_output.unlink(missing_ok=True)
        return 0

    try:
        if should_annotate_regulatory:
            regulatory_temp_handle = tempfile.NamedTemporaryFile(
                prefix=f"{input_path.name}.",
                suffix=".regulatory.vcf",
                dir=str(configured_tmp_dir(config)),
                delete=False,
            )
            regulatory_temp_path = Path(regulatory_temp_handle.name)
            regulatory_temp_handle.close()
            regulatory_log_json = (
                Path(args.regulatory_log_json)
                if args.regulatory_log_json
                else output_path.with_suffix(output_path.suffix + REGULATORY_LOG_SUFFIX)
            )
            regulatory_summary_tsv = Path(args.regulatory_summary_tsv) if args.regulatory_summary_tsv else None
            regulatory_ccre_bed = (
                Path(resolve_runner_tokens(args.regulatory_ccre_bed, runner_dir))
                if args.regulatory_ccre_bed
                else Path(resolve_runner_tokens(config.get("regulatory_ccre_bed", REGULATORY_CCRE_BED_DEFAULT), runner_dir))
            )
            annotate_regulatory_vcf(
                input_path,
                regulatory_temp_path,
                log_json_path=regulatory_log_json,
                summary_tsv_path=regulatory_summary_tsv,
                ccre_bed=regulatory_ccre_bed,
            )
            vep_input_path = regulatory_temp_path
            cmd[cmd.index("--input_file") + 1] = str(vep_input_path)

        original_variants = {}
        vcf_info_ids = []
        should_load_original_vcf_in_memory = (
            args.format.lower() == "vcf"
            and args.conversion_mode == "memory"
        )
        if should_load_original_vcf_in_memory:
            original_variants, vcf_info_ids = load_original_vcf_coordinates(vep_input_path)
        run_command(cmd, env, Path(args.log) if args.log else None)
        gtex_transcript_tpm = args.gtex_transcript_tpm or config.get("gtex_transcript_tpm")
        if not gtex_transcript_tpm:
            gtex_transcript_tpm = resolve_runner_tokens(GTEX_TRANSCRIPT_TPM_DEFAULT, runner_dir)
        hpo_data_dir = args.hpo_data_dir or config.get("hpo_data_dir")
        if not hpo_data_dir:
            hpo_data_dir = resolve_runner_tokens(HPO_TPM_DATA_DIR_DEFAULT, runner_dir)
        manual_tissues = parse_tissue_values(args.clinical_tissue) + read_tissues_file(args.clinical_tissues_file)
        hpo_tissues = resolve_hpo_tissues(
            parse_tissue_values(args.hpo_id),
            args.hpo_file,
            hpo_data_dir,
            args.top_n_hpo_tissues,
            gtex_transcript_tpm,
        )
        clinical_tissues = canonicalize_gtex_v11_tissues(
            manual_tissues + hpo_tissues,
            None if args.disable_gtex_expression else gtex_transcript_tpm,
            "clinical",
        )
        if args.conversion_mode == "memory":
            count = convert_vep_table_to_csv(
                vep_output,
                output_path,
                original_variants,
                vcf_info_ids=vcf_info_ids,
                top_k_transcripts=args.top_k_transcripts,
                clinical_tissues=clinical_tissues,
                gtex_transcript_tpm=gtex_transcript_tpm,
                disable_gtex_expression=args.disable_gtex_expression,
                disable_transcript_selection=args.no_transcript_selection,
                include_vcf_info=not args.no_vcf_info_to_csv,
                rank_pathogenic=not args.no_pathogenic_ranking,
            )
        else:
            count = convert_vep_table_to_csv_sqlite(
                vep_output,
                output_path,
                original_variants,
                original_vcf_path=vep_input_path if args.format.lower() == "vcf" else None,
                vcf_info_ids=vcf_info_ids,
                top_k_transcripts=args.top_k_transcripts,
                clinical_tissues=clinical_tissues,
                gtex_transcript_tpm=gtex_transcript_tpm,
                disable_gtex_expression=args.disable_gtex_expression,
                disable_transcript_selection=args.no_transcript_selection,
                sqlite_db=args.sqlite_db,
                keep_sqlite_db=args.keep_sqlite_db,
                include_vcf_info=not args.no_vcf_info_to_csv,
                rank_pathogenic=not args.no_pathogenic_ranking,
            )
        should_annotate_pseudogene = args.pseudogene_annotation and not args.no_pseudogene_annotation
        if should_annotate_pseudogene:
            log_json_path = (
                Path(args.pseudogene_log_json)
                if args.pseudogene_log_json
                else output_path.with_suffix(output_path.suffix + PSEUDOGENE_LOG_SUFFIX)
            )
            annotate_pseudogene_csv(output_path, log_json_path)
    finally:
        if temp_handle is not None:
            try:
                vep_output.unlink()
            except FileNotFoundError:
                pass
        if regulatory_temp_path is not None:
            regulatory_temp_path.unlink(missing_ok=True)

    regulatory_note = "" if not should_annotate_regulatory else " with regulatory cCRE annotation"
    pseudogene_note = " with pseudogene annotation" if should_annotate_pseudogene else ""
    print(f"Wrote {count} VEP consequence row(s){regulatory_note}{pseudogene_note} to {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
