#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from pathlib import Path

VCF_INFO_COLUMN_PREFIX = "vcf_info_"
VCF_FORMAT_COLUMN_PREFIX = "vcf_format_"
INFO_HEADER_RE = re.compile(r"^##INFO=<ID=([^,>]+),Number=([^,>]+)")
FORMAT_HEADER_RE = re.compile(r"^##FORMAT=<ID=([^,>]+),Number=([^,>]+)")


def open_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open("r", encoding="utf-8", errors="replace")


def info_column(info_id: str) -> str:
    return f"{VCF_INFO_COLUMN_PREFIX}{info_id}"


def format_column(format_id: str) -> str:
    return f"{VCF_FORMAT_COLUMN_PREFIX}{format_id}"


def remember(value: str, ordered: list[str], seen: set[str]) -> None:
    if value and value not in seen:
        seen.add(value)
        ordered.append(value)


def vep_keys(chrom: str, pos: str, ref: str, alt: str) -> list[str]:
    keys = [f"{chrom}_{pos}_{ref}/{alt}"]
    if len(ref) == len(alt):
        return keys
    try:
        shifted = str(int(pos) + 1)
    except ValueError:
        return keys
    keys.append(f"{chrom}_{shifted}_{ref}/{alt}")
    if len(ref) < len(alt) and alt.startswith(ref):
        keys.append(f"{chrom}_{shifted}_-/{alt[len(ref):] or '-'}")
    elif len(ref) > len(alt) and ref.startswith(alt):
        keys.append(f"{chrom}_{shifted}_{ref[len(alt):] or '-'}/-")
    return keys


def csv_candidate_key_groups(row: dict[str, str]) -> list[list[str]]:
    groups: list[list[str]] = []
    uploaded = row.get("Uploaded_variation", "")
    if uploaded:
        groups.append([uploaded])
    chrom = row.get("chrom", "")
    pos = row.get("pos", "")
    ref = row.get("ref", "")
    alt = row.get("alt", "")
    if chrom and pos and ref and alt:
        alt_values = [part for part in alt.split("/") if part] if "/" in alt else [alt]
        for alt_value in alt_values:
            keys = [f"{chrom}_{pos}_{ref}/{alt_value}"]
            if len(ref) != len(alt_value):
                try:
                    keys.append(f"{chrom}_{int(pos) - 1}_{ref}/{alt_value}")
                except ValueError:
                    pass
            groups.append(keys)
    deduped_groups: list[list[str]] = []
    seen: set[str] = set()
    for group in groups:
        deduped: list[str] = []
        for key in group:
            if key and key not in seen:
                seen.add(key)
                deduped.append(key)
        if deduped:
            deduped_groups.append(deduped)
    return deduped_groups


def csv_candidate_keys(row: dict[str, str]) -> list[str]:
    return [key for group in csv_candidate_key_groups(row) for key in group]


def merge_info_value(old: str | None, new: str | None) -> str:
    if not old or old == "-":
        return new or "-"
    if not new or new == "-":
        return old
    values: list[str] = []
    seen: set[str] = set()
    for item in (old, new):
        for part in item.split(","):
            if part not in seen:
                seen.add(part)
                values.append(part)
    return ",".join(values) if values else "-"


def lookup_csv_info(row: dict[str, str], lookup: dict[str, dict[str, str]]) -> dict[str, str] | None:
    merged: dict[str, str] = {}
    found = False
    for group in csv_candidate_key_groups(row):
        values = None
        for key in group:
            values = lookup.get(key)
            if values is not None:
                break
        if values is None:
            continue
        found = True
        for column, value in values.items():
            merged[column] = merge_info_value(merged.get(column), value)
    return merged if found else None


def parse_info_values(info: str, alt_index: int, info_numbers: dict[str, str]) -> dict[str, str]:
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
        values[info_column(key)] = "-" if value in {"", "."} else value
    return values


def parse_format_values(format_text: str, sample_text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    if not format_text or format_text in {".", "-"}:
        return values
    format_ids = format_text.split(":")
    sample_values = sample_text.split(":") if sample_text else []
    for index, format_id in enumerate(format_ids):
        if not format_id:
            continue
        value = sample_values[index] if index < len(sample_values) else "-"
        values[format_column(format_id)] = "-" if value in {"", "."} else value
    return values


def load_vcf_annotations(
    vcf_path: Path,
    requested_sample: str | None = None,
) -> tuple[dict[str, dict[str, str]], list[str], list[str], dict[str, object]]:
    lookup: dict[str, dict[str, str]] = {}
    info_numbers: dict[str, str] = {}
    info_ids: list[str] = []
    seen_info_ids: set[str] = set()
    format_ids: list[str] = []
    seen_format_ids: set[str] = set()
    sample_names: list[str] = []
    selected_sample = ""
    selected_sample_column: int | None = None
    stats: dict[str, object] = {
        "vcf_records": 0,
        "vcf_alleles": 0,
        "lookup_keys": 0,
        "sample_count": 0,
        "selected_sample": "",
    }

    with open_text(vcf_path) as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line.startswith("##INFO="):
                match = INFO_HEADER_RE.match(line)
                if match:
                    info_id, number = match.groups()
                    info_numbers[info_id] = number
                    remember(info_id, info_ids, seen_info_ids)
                continue
            if line.startswith("##FORMAT="):
                match = FORMAT_HEADER_RE.match(line)
                if match:
                    format_id, _number = match.groups()
                    remember(format_id, format_ids, seen_format_ids)
                continue
            if line.startswith("#CHROM"):
                header_parts = line.split("\t")
                sample_names = header_parts[9:] if len(header_parts) > 9 else []
                stats["sample_count"] = len(sample_names)
                if requested_sample:
                    if requested_sample not in sample_names:
                        raise ValueError(
                            f"sample not found in VCF: {requested_sample}; available samples: {sample_names}"
                        )
                    selected_sample = requested_sample
                elif sample_names:
                    selected_sample = sample_names[0]
                if selected_sample:
                    selected_sample_column = 9 + sample_names.index(selected_sample)
                stats["selected_sample"] = selected_sample
                continue
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 8:
                continue
            stats["vcf_records"] += 1
            chrom, pos, _var_id, ref, alts = parts[:5]
            info = parts[7]
            format_text = parts[8] if len(parts) > 8 else ""
            sample_text = (
                parts[selected_sample_column]
                if selected_sample_column is not None and selected_sample_column < len(parts)
                else ""
            )
            for alt_index, alt in enumerate(alts.split(",")):
                stats["vcf_alleles"] += 1
                values = parse_info_values(info, alt_index, info_numbers)
                values.update(parse_format_values(format_text, sample_text))
                for column in values:
                    if column.startswith(VCF_INFO_COLUMN_PREFIX):
                        remember(column.removeprefix(VCF_INFO_COLUMN_PREFIX), info_ids, seen_info_ids)
                    elif column.startswith(VCF_FORMAT_COLUMN_PREFIX):
                        remember(column.removeprefix(VCF_FORMAT_COLUMN_PREFIX), format_ids, seen_format_ids)
                for key in vep_keys(chrom, pos, ref, alt):
                    if key not in lookup:
                        lookup[key] = values
    stats["lookup_keys"] = len(lookup)
    return lookup, info_ids, format_ids, stats


def output_fieldnames(
    input_fields: list[str],
    info_ids: list[str],
    format_ids: list[str],
    insert_after: str = "alt",
) -> list[str]:
    fields: list[str] = []
    seen: set[str] = set()

    def add(field: str) -> None:
        if field and field not in seen:
            seen.add(field)
            fields.append(field)

    inserted = False
    for field in input_fields:
        add(field)
        if field == insert_after:
            for info_id in info_ids:
                add(info_column(info_id))
            for format_id in format_ids:
                add(format_column(format_id))
            inserted = True
    if not inserted:
        for info_id in info_ids:
            add(info_column(info_id))
        for format_id in format_ids:
            add(format_column(format_id))
    return fields


def annotate_csv(
    input_csv: Path,
    input_vcf: Path,
    output_csv: Path,
    log_json: Path | None = None,
    sample_name: str | None = None,
) -> dict[str, object]:
    lookup, info_ids, format_ids, vcf_stats = load_vcf_annotations(input_vcf, sample_name)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    matched = 0

    with input_csv.open("r", newline="") as src:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header not found: {input_csv}")
        fieldnames = output_fieldnames(list(reader.fieldnames), info_ids, format_ids)
        with output_csv.open("w", newline="") as dst:
            writer = csv.DictWriter(dst, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in reader:
                rows += 1
                values = lookup_csv_info(row, lookup)
                if values is not None:
                    matched += 1
                for info_id in info_ids:
                    column = info_column(info_id)
                    row[column] = (values or {}).get(column, "-")
                for format_id in format_ids:
                    column = format_column(format_id)
                    row[column] = (values or {}).get(column, "-")
                writer.writerow({field: row.get(field, "-") for field in fieldnames})

    stats = {
        "input_csv": str(input_csv),
        "input_vcf": str(input_vcf),
        "output_csv": str(output_csv),
        "rows": rows,
        "matched_rows": matched,
        "info_fields": len(info_ids),
        "format_fields": len(format_ids),
        "format_field_ids": format_ids,
        **vcf_stats,
    }
    if log_json:
        log_json.parent.mkdir(parents=True, exist_ok=True)
        log_json.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Append VCF INFO and sample FORMAT fields to a VEP CSV.")
    parser.add_argument("--input-csv", required=True, help="VEP CSV from module 04")
    parser.add_argument("--input-vcf", required=True, help="VCF used as module 04 VEP input")
    parser.add_argument("--output-csv", required=True, help="CSV with vcf_info_* and vcf_format_* columns")
    parser.add_argument(
        "--sample-name",
        help="VCF sample to parse; default is the first sample in the VCF header",
    )
    parser.add_argument("--log-json", help="Optional JSON statistics path")
    args = parser.parse_args()

    stats = annotate_csv(
        Path(args.input_csv),
        Path(args.input_vcf),
        Path(args.output_csv),
        Path(args.log_json) if args.log_json else None,
        args.sample_name,
    )
    print(
        f"Annotated {stats['matched_rows']}/{stats['rows']} CSV row(s) with "
        f"{stats['info_fields']} INFO and {stats['format_fields']} FORMAT field(s) "
        f"from sample {stats['selected_sample'] or '-'}: {args.output_csv}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
