#!/usr/bin/env python3
"""Annotate VCF records with HGNC-backed pseudogene and reads-level evidence."""

from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_GENCODE_GTF = Path(
    "/mnt/workspace/xiongliwen/00.PublicData/Pseudogene/"
    "GENCODE/release_49/gencode.v49.2wayconspseudos.gtf.gz"
)
DEFAULT_PSEUDOGENE_ORG = Path(
    "/mnt/workspace/xiongliwen/00.PublicData/Pseudogene/"
    "Pseudogene.org/Human90/Human90.txt"
)
DEFAULT_HGNC = Path(
    "/mnt/workspace/xiongliwen/00.PublicData/phenotype_hpo_v1/hgnc_complete_set.txt"
)

PSEUDOGENE_INFO_HEADERS = [
    '##INFO=<ID=is_pseudogene,Number=1,Type=String,Description="Pseudogene annotation result: Yes or No">',
    '##INFO=<ID=pseudogene_name,Number=.,Type=String,Description="HGNC pseudogene symbol list; VCF-escaped %3B separates multiple names; - means reads-level evidence only; . means missing">',
    '##INFO=<ID=pseudogene_source,Number=1,Type=String,Description="Pseudogene annotation source: GENCODE.v49, Pseudogene.org, Pseudogene.org&GENCODE.v49, Reads_mapped, or .">',
]
PSEUDOGENE_KEYS = {"is_pseudogene", "pseudogene_name", "pseudogene_source"}


@dataclass(frozen=True)
class Interval:
    chrom: str
    start: int
    end: int
    symbol: str
    source: str
    raw_id: str


@dataclass
class ReadMetrics:
    dp: int | None = None
    ref_depth: int | None = None
    alt_depth: int | None = None
    vaf: float | None = None
    mq: float | None = None
    mq_rank_sum: float | None = None
    ref_mq: float | None = None
    alt_mq: float | None = None
    high_dp: bool = False
    low_vaf: bool = False
    vaf_deviates_from_het: bool = False
    low_mq: bool = False
    alt_mq_lower_than_ref: bool = False
    abnormal: bool = False


@dataclass
class VcfRecord:
    line_no: int
    fields: list[str]
    chrom: str
    pos: int
    info: dict[str, str | bool]
    format_keys: list[str]
    sample_values: dict[str, str]
    metrics: ReadMetrics = field(default_factory=ReadMetrics)
    db_symbols: list[str] = field(default_factory=list)
    db_source: str = ""
    chrom_known: bool = True
    is_non_primary: bool = False
    neighbor_abnormal_count: int = 0
    neighbor_vaf_similar_count: int = 0
    reads_rules: list[str] = field(default_factory=list)


class IntervalIndex:
    def __init__(self, intervals: list[Interval]) -> None:
        self.by_chrom: dict[str, list[Interval]] = defaultdict(list)
        self.starts: dict[str, list[int]] = {}
        for interval in intervals:
            self.by_chrom[interval.chrom].append(interval)
        for chrom, chrom_intervals in self.by_chrom.items():
            chrom_intervals.sort(key=lambda item: item.start)
            self.starts[chrom] = [item.start for item in chrom_intervals]

    def query(self, chrom: str, pos: int) -> list[Interval]:
        matches: list[Interval] = []
        seen: set[tuple[str, int, int, str, str, str]] = set()
        for key in chrom_query_keys(chrom):
            chrom_intervals = self.by_chrom.get(key)
            if not chrom_intervals:
                continue
            starts = self.starts[key]
            stop = bisect.bisect_right(starts, pos)
            for interval in reversed(chrom_intervals[:stop]):
                if interval.end < pos:
                    continue
                if interval.start <= pos <= interval.end:
                    dedup_key = (
                        interval.chrom,
                        interval.start,
                        interval.end,
                        interval.symbol,
                        interval.source,
                        interval.raw_id,
                    )
                    if dedup_key not in seen:
                        seen.add(dedup_key)
                        matches.append(interval)
        return matches

    def has_chrom(self, chrom: str) -> bool:
        return any(key in self.by_chrom for key in chrom_query_keys(chrom))


def chrom_query_keys(value: str) -> list[str]:
    """Return exact/alias chromosome keys without projecting alt contigs to primaries."""
    raw = value.strip()
    if not raw:
        return [raw]
    keys = [raw]
    if raw.lower().startswith("chr"):
        no_chr = raw[3:]
        keys.append(no_chr)
    else:
        keys.append(f"chr{raw}")
    normalized = normalize_chrom(raw)
    keys.append(normalized)
    if normalized != raw:
        keys.extend([normalized, f"chr{normalized}"])
    return list(dict.fromkeys(keys))


def is_primary_chrom(value: str) -> bool:
    chrom = normalize_chrom(value)
    return chrom in {str(number) for number in range(1, 23)} | {"X", "Y", "MT"}


def normalize_chrom(value: str) -> str:
    chrom = value.strip()
    if chrom.lower().startswith("chr"):
        chrom = chrom[3:]
    if chrom in {"23", "X"}:
        return "X"
    if chrom in {"24", "Y"}:
        return "Y"
    if chrom in {"25", "M", "MT", "Mt", "m"}:
        return "MT"
    return chrom


def parse_gtf_attrs(attrs: str) -> dict[str, str]:
    return dict(re.findall(r'(\S+)\s+"([^"]*)"', attrs))


def split_hgnc_xrefs(value: str) -> list[str]:
    if not value:
        return []
    return [part for part in re.split(r"[|,;\s]+", value.strip()) if part]


def load_hgnc_pseudogene_map(path: Path) -> tuple[dict[str, set[str]], dict[str, object]]:
    pgohum_to_symbols: dict[str, set[str]] = defaultdict(set)
    locus_type_counts: Counter[str] = Counter()
    pseudogene_rows = 0
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            locus_group = row.get("locus_group", "")
            locus_type = row.get("locus_type", "")
            is_pseudogene = (
                "pseudogene" in locus_group.lower()
                or "pseudogene" in locus_type.lower()
            )
            if not is_pseudogene:
                continue
            pseudogene_rows += 1
            locus_type_counts[locus_type] += 1
            symbol = row.get("symbol", "").strip()
            if not symbol:
                continue
            for xref in split_hgnc_xrefs(row.get("pseudogene.org", "")):
                if xref.startswith("PGOHUM"):
                    pgohum_to_symbols[xref].add(symbol)
    stats = {
        "hgnc_pseudogene_rows": pseudogene_rows,
        "hgnc_locus_type_counts": dict(sorted(locus_type_counts.items())),
        "hgnc_pseudogene_org_xrefs": len(pgohum_to_symbols),
    }
    return pgohum_to_symbols, stats


def load_gencode_intervals(
    path: Path, pgohum_to_symbols: dict[str, set[str]]
) -> tuple[list[Interval], dict[str, int]]:
    intervals: list[Interval] = []
    raw_ids: set[str] = set()
    kept_ids: set[str] = set()
    with gzip.open(path, "rt") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9:
                continue
            attrs = parse_gtf_attrs(fields[8])
            raw_id = attrs.get("gene_id", "").strip()
            if not raw_id:
                continue
            raw_ids.add(raw_id)
            symbols = pgohum_to_symbols.get(raw_id)
            if not symbols:
                continue
            chrom = normalize_chrom(fields[0])
            start = int(fields[3])
            end = int(fields[4])
            for symbol in symbols:
                intervals.append(
                    Interval(chrom, start, end, symbol, "GENCODE.v49", raw_id)
                )
            kept_ids.add(raw_id)
    return intervals, {
        "gencode_raw_unique_ids": len(raw_ids),
        "gencode_hgnc_mapped_ids": len(kept_ids),
        "gencode_hgnc_intervals": len(intervals),
    }


def load_pseudogene_org_intervals(
    path: Path, pgohum_to_symbols: dict[str, set[str]]
) -> tuple[list[Interval], dict[str, int]]:
    intervals: list[Interval] = []
    raw_ids: set[str] = set()
    kept_ids: set[str] = set()
    with path.open() as handle:
        for line in handle:
            if not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 4:
                continue
            raw_id = fields[0].strip()
            raw_ids.add(raw_id)
            symbols = pgohum_to_symbols.get(raw_id)
            if not symbols:
                continue
            chrom = normalize_chrom(fields[1])
            start = int(fields[2])
            end = int(fields[3])
            for symbol in symbols:
                intervals.append(
                    Interval(chrom, start, end, symbol, "Pseudogene.org", raw_id)
                )
            kept_ids.add(raw_id)
    return intervals, {
        "pseudogene_org_raw_unique_ids": len(raw_ids),
        "pseudogene_org_hgnc_mapped_ids": len(kept_ids),
        "pseudogene_org_hgnc_intervals": len(intervals),
    }


def source_label(sources: set[str]) -> str:
    has_gencode = "GENCODE.v49" in sources
    has_pseudogene_org = "Pseudogene.org" in sources
    if has_gencode and has_pseudogene_org:
        return "Pseudogene.org&GENCODE.v49"
    if has_gencode:
        return "GENCODE.v49"
    if has_pseudogene_org:
        return "Pseudogene.org"
    return ""


def parse_number(value: str | bool | None) -> float | None:
    if value is None or value is True:
        return None
    text = str(value).strip()
    if not text or text == ".":
        return None
    try:
        return float(text.split(",")[0])
    except ValueError:
        return None


def parse_int(value: str | bool | None) -> int | None:
    number = parse_number(value)
    return int(number) if number is not None else None


def parse_info(info_text: str) -> dict[str, str | bool]:
    if info_text in {"", "."}:
        return {}
    info: dict[str, str | bool] = {}
    for item in info_text.split(";"):
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
            info[key] = value
        else:
            info[item] = True
    return info


def format_info(info: dict[str, str | bool]) -> str:
    if not info:
        return "."
    parts: list[str] = []
    for key, value in info.items():
        if value is True:
            parts.append(key)
        else:
            parts.append(f"{key}={value}")
    return ";".join(parts) if parts else "."


def parse_format_sample(format_text: str, sample_text: str) -> tuple[list[str], dict[str, str]]:
    if not format_text or format_text == "." or not sample_text or sample_text == ".":
        return [], {}
    keys = format_text.split(":")
    values = sample_text.split(":")
    return keys, {key: values[idx] if idx < len(values) else "" for idx, key in enumerate(keys)}


def split_numeric_list(value: str | None) -> list[float]:
    if not value or value == ".":
        return []
    numbers: list[float] = []
    for part in value.split(","):
        try:
            numbers.append(float(part))
        except ValueError:
            return []
    return numbers


def first_existing(info: dict[str, str | bool], keys: list[str]) -> str | bool | None:
    for key in keys:
        if key in info:
            return info[key]
    return None


def compute_read_metrics(
    record: VcfRecord,
    args: argparse.Namespace,
) -> ReadMetrics:
    info = record.info
    sample = record.sample_values
    metrics = ReadMetrics()

    metrics.dp = parse_int(sample.get("DP"))
    if metrics.dp is None:
        metrics.dp = parse_int(info.get("DP"))

    ad_values = split_numeric_list(sample.get("AD"))
    if len(ad_values) >= 2:
        metrics.ref_depth = int(ad_values[0])
        metrics.alt_depth = int(sum(ad_values[1:]))
        denom = metrics.ref_depth + metrics.alt_depth
        if denom > 0:
            metrics.vaf = metrics.alt_depth / denom

    if metrics.vaf is None:
        af = parse_number(first_existing(info, ["VAF", "AF"]))
        if af is not None:
            metrics.vaf = af

    metrics.mq = parse_number(first_existing(info, ["MQ", "RMSMQ"]))
    metrics.mq_rank_sum = parse_number(info.get("MQRankSum"))
    metrics.ref_mq = parse_number(info.get(args.info_ref_mq_field))
    metrics.alt_mq = parse_number(info.get(args.info_alt_mq_field))

    metrics.high_dp = metrics.dp is not None and metrics.dp >= args.min_high_dp
    metrics.low_vaf = metrics.vaf is not None and metrics.vaf <= args.max_low_vaf
    metrics.vaf_deviates_from_het = (
        metrics.vaf is not None
        and abs(metrics.vaf - 0.5) >= args.min_vaf_deviation_from_het
    )
    metrics.low_mq = metrics.mq is not None and metrics.mq <= args.max_low_mq

    if metrics.ref_mq is not None and metrics.alt_mq is not None:
        metrics.alt_mq_lower_than_ref = (
            metrics.ref_mq - metrics.alt_mq >= args.min_ref_alt_mq_delta
        )
    elif metrics.mq_rank_sum is not None:
        # GATK MQRankSum is Alt vs Ref. A negative value means ALT reads
        # have lower mapping quality than REF reads.
        metrics.alt_mq_lower_than_ref = (
            -metrics.mq_rank_sum >= args.min_ref_alt_mq_delta
        )

    vaf_abnormal = metrics.low_vaf or metrics.vaf_deviates_from_het
    metrics.abnormal = metrics.high_dp and vaf_abnormal
    return metrics


def vcf_escape_info_value(value: str) -> str:
    return (
        value.replace("%", "%25")
        .replace(";", "%3B")
        .replace("=", "%3D")
        .replace(" ", "%20")
        .replace("\t", "%09")
    )


def add_pseudogene_info(info: dict[str, str | bool], is_pg: str, name: str, source: str) -> None:
    for key in PSEUDOGENE_KEYS:
        info.pop(key, None)
    info["is_pseudogene"] = is_pg
    info["pseudogene_name"] = vcf_escape_info_value(name)
    info["pseudogene_source"] = vcf_escape_info_value(source)


def add_info_headers(header_lines: list[str]) -> list[str]:
    existing_ids: set[str] = set()
    for line in header_lines:
        match = re.match(r"##INFO=<ID=([^,>]+)", line)
        if match:
            existing_ids.add(match.group(1))

    new_header: list[str] = []
    inserted = False
    for line in header_lines:
        if line.startswith("#CHROM") and not inserted:
            for info_header in PSEUDOGENE_INFO_HEADERS:
                match = re.match(r"##INFO=<ID=([^,>]+)", info_header)
                if match and match.group(1) not in existing_ids:
                    new_header.append(info_header)
            inserted = True
        new_header.append(line)
    return new_header


def parse_vcf_records(input_vcf: Path, sample_name: str | None) -> tuple[list[str], list[VcfRecord]]:
    header_lines: list[str] = []
    records: list[VcfRecord] = []
    sample_index = 9
    with input_vcf.open() as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\n")
            if line.startswith("#"):
                header_lines.append(line)
                if line.startswith("#CHROM"):
                    columns = line.split("\t")
                    if sample_name:
                        if sample_name not in columns:
                            raise ValueError(f"sample not found in VCF header: {sample_name}")
                        sample_index = columns.index(sample_name)
                    elif len(columns) > 9:
                        sample_index = 9
                continue

            fields = line.split("\t")
            if len(fields) < 8:
                raise ValueError(f"invalid VCF row at line {line_no}: expected >=8 columns")
            try:
                pos = int(fields[1])
            except ValueError as exc:
                raise ValueError(f"invalid POS at line {line_no}: {fields[1]}") from exc

            format_keys: list[str] = []
            sample_values: dict[str, str] = {}
            if len(fields) > sample_index and len(fields) > 8:
                format_keys, sample_values = parse_format_sample(fields[8], fields[sample_index])
            records.append(
                VcfRecord(
                    line_no=line_no,
                    fields=fields,
                    chrom=fields[0].strip(),
                    pos=pos,
                    info=parse_info(fields[7]),
                    format_keys=format_keys,
                    sample_values=sample_values,
                )
            )
    return header_lines, records


def annotate_db(records: list[VcfRecord], index: IntervalIndex) -> dict[str, Any]:
    unique_symbols: set[str] = set()
    unmatched_chrom_counts: Counter[str] = Counter()
    non_primary_contig_counts: Counter[str] = Counter()
    db_annotated = 0
    non_primary_contig_annotated = 0
    non_primary_contig_unannotated = 0

    for record in records:
        record.chrom_known = index.has_chrom(record.chrom)
        if not record.chrom_known:
            unmatched_chrom_counts[record.chrom] += 1

        record.is_non_primary = not is_primary_chrom(record.chrom)
        if record.is_non_primary:
            non_primary_contig_counts[record.chrom] += 1

        matches = index.query(record.chrom, record.pos)
        symbols = sorted({match.symbol for match in matches})
        sources = {match.source for match in matches}
        if symbols:
            record.db_symbols = symbols
            record.db_source = source_label(sources)
            unique_symbols.update(symbols)
            db_annotated += 1
            if record.is_non_primary:
                non_primary_contig_annotated += 1
        elif record.is_non_primary:
            non_primary_contig_unannotated += 1

    return {
        "db_annotated_as_pseudogene": db_annotated,
        "unique_annotated_pseudogene_names": len(unique_symbols),
        "unmatched_chrom_rows": sum(unmatched_chrom_counts.values()),
        "unmatched_chrom_examples": [
            chrom for chrom, _ in unmatched_chrom_counts.most_common(10)
        ],
        "non_primary_contig_rows": sum(non_primary_contig_counts.values()),
        "non_primary_contig_annotated": non_primary_contig_annotated,
        "non_primary_contig_unannotated": non_primary_contig_unannotated,
        "non_primary_contig_examples": [
            chrom for chrom, _ in non_primary_contig_counts.most_common(10)
        ],
    }


def compute_neighbor_evidence(records: list[VcfRecord], args: argparse.Namespace) -> None:
    by_chrom: dict[str, list[VcfRecord]] = defaultdict(list)
    for record in records:
        by_chrom[record.chrom].append(record)

    for chrom_records in by_chrom.values():
        chrom_records.sort(key=lambda record: record.pos)
        positions = [record.pos for record in chrom_records]
        for record in chrom_records:
            left = bisect.bisect_left(positions, record.pos - args.neighbor_window_bp)
            right = bisect.bisect_right(positions, record.pos + args.neighbor_window_bp)
            abnormal_count = 0
            similar_count = 0
            for neighbor in chrom_records[left:right]:
                if not neighbor.metrics.abnormal:
                    continue
                abnormal_count += 1
                if (
                    record.metrics.vaf is not None
                    and neighbor.metrics.vaf is not None
                    and abs(record.metrics.vaf - neighbor.metrics.vaf)
                    <= args.max_neighbor_vaf_delta
                ):
                    similar_count += 1
            record.neighbor_abnormal_count = abnormal_count
            record.neighbor_vaf_similar_count = similar_count


def evaluate_reads_rules(record: VcfRecord, args: argparse.Namespace) -> list[str]:
    metrics = record.metrics
    vaf_abnormal = metrics.low_vaf or metrics.vaf_deviates_from_het
    rules: list[str] = []

    if metrics.high_dp and vaf_abnormal and metrics.low_mq:
        rules.append("high_dp_vaf_abnormal_low_mq")

    if (
        metrics.high_dp
        and vaf_abnormal
        and record.neighbor_abnormal_count >= args.min_neighbor_abnormal_variants
        and record.neighbor_vaf_similar_count >= args.min_neighbor_abnormal_variants
    ):
        rules.append("high_dp_neighbor_abnormal_similar_vaf")

    if metrics.alt_mq_lower_than_ref and vaf_abnormal:
        rules.append("alt_mq_lower_than_ref_vaf_abnormal")

    return rules


def annotate_vcf(
    input_vcf: Path,
    output_vcf: Path,
    index: IntervalIndex,
    args: argparse.Namespace,
) -> dict[str, Any]:
    header_lines, records = parse_vcf_records(input_vcf, args.sample_name)
    db_stats = annotate_db(records, index)

    for record in records:
        record.metrics = compute_read_metrics(record, args)
    compute_neighbor_evidence(records, args)

    source_counts: Counter[str] = Counter()
    reads_rule_counts: Counter[str] = Counter()
    reads_annotated = 0
    reads_evaluated = 0

    output_vcf.parent.mkdir(parents=True, exist_ok=True)
    with output_vcf.open("w") as out_handle:
        for header in add_info_headers(header_lines):
            out_handle.write(header + "\n")

        for record in records:
            if record.db_symbols:
                add_pseudogene_info(
                    record.info,
                    "Yes",
                    ";".join(record.db_symbols),
                    record.db_source,
                )
                source_counts[record.db_source] += 1
            else:
                reads_evaluated += 1
                record.reads_rules = evaluate_reads_rules(record, args)
                for rule in record.reads_rules:
                    reads_rule_counts[rule] += 1
                if record.reads_rules:
                    reads_annotated += 1
                    add_pseudogene_info(record.info, "Yes", "-", "Reads_mapped")
                    source_counts["Reads_mapped"] += 1
                else:
                    add_pseudogene_info(record.info, "No", ".", ".")
                    source_counts["Not_pseudogene"] += 1

            record.fields[7] = format_info(record.info)
            out_handle.write("\t".join(record.fields) + "\n")

    total_annotated = db_stats["db_annotated_as_pseudogene"] + reads_annotated
    return {
        "input_records": len(records),
        **db_stats,
        "reads_evaluated_records": reads_evaluated,
        "reads_annotated_as_pseudogene": reads_annotated,
        "total_annotated_as_pseudogene": total_annotated,
        "not_pseudogene": len(records) - total_annotated,
        "source_counts": dict(source_counts),
        "reads_rule_counts": dict(reads_rule_counts),
        "reads_thresholds": {
            "min_high_dp": args.min_high_dp,
            "max_low_vaf": args.max_low_vaf,
            "min_vaf_deviation_from_het": args.min_vaf_deviation_from_het,
            "max_low_mq": args.max_low_mq,
            "min_ref_alt_mq_delta": args.min_ref_alt_mq_delta,
            "neighbor_window_bp": args.neighbor_window_bp,
            "min_neighbor_abnormal_variants": args.min_neighbor_abnormal_variants,
            "max_neighbor_vaf_delta": args.max_neighbor_vaf_delta,
            "info_ref_mq_field": args.info_ref_mq_field,
            "info_alt_mq_field": args.info_alt_mq_field,
            "sample_name": args.sample_name,
        },
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Annotate VCF records with HGNC-backed pseudogene overlaps from "
            "GENCODE v49/Pseudogene.org, then run configurable reads-level "
            "evidence only for DB-unannotated records."
        )
    )
    parser.add_argument("--input", required=True, type=Path, help="Input VCF.")
    parser.add_argument("--output", type=Path, help="Output annotated VCF.")
    parser.add_argument("--gencode-gtf", default=DEFAULT_GENCODE_GTF, type=Path)
    parser.add_argument("--pseudogene-org", default=DEFAULT_PSEUDOGENE_ORG, type=Path)
    parser.add_argument("--hgnc", default=DEFAULT_HGNC, type=Path)
    parser.add_argument("--log-json", type=Path, help="Optional JSON log output path.")
    parser.add_argument("--sample-name", default=None, help="Sample column for FORMAT metrics. Defaults to the first sample.")
    parser.add_argument("--min-high-dp", type=int, default=50)
    parser.add_argument("--max-low-vaf", type=float, default=0.2)
    parser.add_argument("--min-vaf-deviation-from-het", type=float, default=0.3)
    parser.add_argument("--max-low-mq", type=float, default=40.0)
    parser.add_argument("--min-ref-alt-mq-delta", type=float, default=3.0)
    parser.add_argument("--neighbor-window-bp", type=int, default=200)
    parser.add_argument("--min-neighbor-abnormal-variants", type=int, default=3)
    parser.add_argument("--max-neighbor-vaf-delta", type=float, default=0.1)
    parser.add_argument("--info-ref-mq-field", default="REF_MQ")
    parser.add_argument("--info-alt-mq-field", default="ALT_MQ")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    output = args.output
    if output is None:
        output = args.input.with_name(f"{args.input.stem}.pseudogene_annotated.vcf")

    pgohum_to_symbols, hgnc_stats = load_hgnc_pseudogene_map(args.hgnc)
    gencode_intervals, gencode_stats = load_gencode_intervals(
        args.gencode_gtf, pgohum_to_symbols
    )
    pseudogene_org_intervals, pseudogene_org_stats = load_pseudogene_org_intervals(
        args.pseudogene_org, pgohum_to_symbols
    )
    index = IntervalIndex(gencode_intervals + pseudogene_org_intervals)
    annotate_stats = annotate_vcf(args.input, output, index, args)

    log = {
        "input": str(args.input),
        "output": str(output),
        "databases": {
            "gencode_gtf": str(args.gencode_gtf),
            "pseudogene_org": str(args.pseudogene_org),
            "hgnc": str(args.hgnc),
        },
        "hgnc": hgnc_stats,
        "database_interval_filtering": {
            **gencode_stats,
            **pseudogene_org_stats,
        },
        "annotation": annotate_stats,
    }

    text = json.dumps(log, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.log_json:
        args.log_json.parent.mkdir(parents=True, exist_ok=True)
        args.log_json.write_text(text + "\n")


if __name__ == "__main__":
    main()
