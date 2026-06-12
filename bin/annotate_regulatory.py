#!/usr/bin/env python3
"""Annotate VCF records with bundled ENCODE SCREEN cCRE overlaps."""

from __future__ import annotations

import argparse
import bisect
import gzip
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path


RUNNER_DIR = Path(__file__).resolve().parents[1]
REGULATORY_DATA_DIR = RUNNER_DIR / "vep_data" / "regulatory" / "hg38"
DEFAULT_CCRE_BED = REGULATORY_DATA_DIR / "encode_screen_v4_grch38_ccre.slim.bed.gz"
DEFAULT_SOURCE = "ENCODE_SCREEN_v4_GRCh38"
REG_INFO_IDS = {"REG_CCRE_ID", "REG_CCRE_CLASS", "REG_CCRE_COUNT", "REG_CCRE_SOURCE"}
INFO_HEADERS = [
    '##INFO=<ID=REG_CCRE_ID,Number=.,Type=String,Description="ENCODE SCREEN cCRE identifiers overlapping this variant interval">',
    '##INFO=<ID=REG_CCRE_CLASS,Number=.,Type=String,Description="ENCODE SCREEN cCRE classes overlapping this variant interval">',
    '##INFO=<ID=REG_CCRE_COUNT,Number=1,Type=Integer,Description="Number of ENCODE SCREEN cCRE intervals overlapping this variant interval">',
    '##INFO=<ID=REG_CCRE_SOURCE,Number=1,Type=String,Description="Regulatory annotation source version">',
]


def open_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open()


def write_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "wt")
    return path.open("w")


def chrom_aliases(chrom: str) -> list[str]:
    aliases = [chrom]
    if chrom.startswith("chr"):
        aliases.append(chrom[3:])
    else:
        aliases.append(f"chr{chrom}")
    if chrom == "MT":
        aliases.append("chrM")
    elif chrom == "chrM":
        aliases.append("MT")

    seen: set[str] = set()
    out: list[str] = []
    for alias in aliases:
        if alias and alias not in seen:
            seen.add(alias)
            out.append(alias)
    return out


def load_bed(path: Path) -> dict[str, tuple[list[tuple[int, int, str, str]], list[int], int]]:
    by_chrom: dict[str, list[tuple[int, int, str, str]]] = defaultdict(list)
    with open_text(path) as handle:
        for line in handle:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 5:
                raise ValueError(f"BED requires at least 5 columns: {line[:120]}")
            chrom, start, end, ccre_id, ccre_class = fields[:5]
            start_i = int(start)
            end_i = int(end)
            if end_i <= start_i:
                continue
            by_chrom[chrom].append((start_i, end_i, ccre_id, ccre_class))

    index = {}
    for chrom, rows in by_chrom.items():
        rows.sort(key=lambda item: (item[0], item[1], item[2]))
        starts = [item[0] for item in rows]
        max_len = max(item[1] - item[0] for item in rows)
        index[chrom] = (rows, starts, max_len)
    return index


def uniq(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def overlap_one_chrom(
    index: dict[str, tuple[list[tuple[int, int, str, str]], list[int], int]],
    chrom: str,
    start: int,
    end: int,
) -> list[tuple[int, int, str, str]]:
    if chrom not in index:
        return []
    rows, starts, max_len = index[chrom]
    i = bisect.bisect_left(starts, end) - 1
    lower_start = start - max_len
    hits: list[tuple[int, int, str, str]] = []
    while i >= 0 and rows[i][0] >= lower_start:
        reg_start, reg_end, ccre_id, ccre_class = rows[i]
        if reg_start < end and reg_end > start:
            hits.append((reg_start, reg_end, ccre_id, ccre_class))
        i -= 1
    hits.sort(key=lambda item: (item[0], item[1], item[2]))
    return hits


def overlap(
    index: dict[str, tuple[list[tuple[int, int, str, str]], list[int], int]],
    chrom: str,
    start: int,
    end: int,
) -> list[tuple[int, int, str, str]]:
    for alias in chrom_aliases(chrom):
        hits = overlap_one_chrom(index, alias, start, end)
        if hits:
            return hits
    return []


def add_info(info: str, key: str, value: str) -> str:
    if info in {"", "."}:
        return f"{key}={value}"
    return f"{info};{key}={value}"


def strip_regulatory_info(info: str) -> str:
    if info in {"", "."}:
        return info
    kept = []
    for item in info.split(";"):
        key = item.split("=", 1)[0]
        if key not in REG_INFO_IDS:
            kept.append(item)
    return ";".join(kept) if kept else "."


def variant_interval(pos: str, ref: str) -> tuple[int, int]:
    start = int(pos) - 1
    return start, start + max(1, len(ref))


def annotate_vcf(input_vcf: Path, output_vcf: Path, ccre_bed: Path, source: str) -> dict[str, object]:
    index = load_bed(ccre_bed)
    total = 0
    annotated = 0
    class_counts: dict[str, int] = defaultdict(int)
    existing_info: set[str] = set()
    pending_headers: list[str] = []

    output_vcf.parent.mkdir(parents=True, exist_ok=True)
    with open_text(input_vcf) as inp, write_text(output_vcf) as out:
        for line in inp:
            if line.startswith("##INFO=<ID="):
                existing_info.add(line.split("ID=", 1)[1].split(",", 1)[0])
                pending_headers.append(line)
                continue
            if line.startswith("##"):
                pending_headers.append(line)
                continue
            if line.startswith("#CHROM"):
                for header in pending_headers:
                    out.write(header)
                for header in INFO_HEADERS:
                    info_id = header.split("ID=", 1)[1].split(",", 1)[0]
                    if info_id not in existing_info:
                        out.write(header + "\n")
                out.write(line)
                break
        else:
            raise ValueError("Input does not look like a VCF: missing #CHROM header")

        for line in inp:
            if not line.strip() or line.startswith("#"):
                out.write(line)
                continue
            total += 1
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                out.write(line)
                continue
            chrom, pos, _variant_id, ref = fields[:4]
            start, end = variant_interval(pos, ref)
            hits = overlap(index, chrom, start, end)
            fields[7] = strip_regulatory_info(fields[7])
            if not hits:
                out.write("\t".join(fields) + "\n")
                continue

            annotated += 1
            ids = uniq([hit[2] for hit in hits])
            classes = uniq([hit[3] for hit in hits])
            for ccre_class in classes:
                class_counts[ccre_class] += 1

            info = fields[7]
            info = add_info(info, "REG_CCRE_ID", ",".join(ids))
            info = add_info(info, "REG_CCRE_CLASS", ",".join(classes))
            info = add_info(info, "REG_CCRE_COUNT", str(len(hits)))
            info = add_info(info, "REG_CCRE_SOURCE", source)
            fields[7] = info
            out.write("\t".join(fields) + "\n")

    return {
        "source": source,
        "run_date": date.today().isoformat(),
        "input_vcf": str(input_vcf),
        "output_vcf": str(output_vcf),
        "ccre_bed": str(ccre_bed),
        "total_variants": total,
        "variants_with_ccre_overlap": annotated,
        "variants_without_ccre_overlap": total - annotated,
        "class_counts": dict(sorted(class_counts.items(), key=lambda item: (-item[1], item[0]))),
    }


def write_summary_tsv(path: Path, stats: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as out:
        out.write("metric\tvalue\n")
        for key in (
            "source",
            "run_date",
            "input_vcf",
            "output_vcf",
            "ccre_bed",
            "total_variants",
            "variants_with_ccre_overlap",
            "variants_without_ccre_overlap",
        ):
            out.write(f"{key}\t{stats[key]}\n")
        for ccre_class, count in stats["class_counts"].items():  # type: ignore[union-attr]
            out.write(f"class:{ccre_class}\t{count}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Annotate VCF variants with bundled ENCODE SCREEN cCRE overlaps.")
    parser.add_argument("--input", "-i", required=True, type=Path, help="Input VCF, optionally .gz")
    parser.add_argument("--output", "-o", required=True, type=Path, help="Output annotated VCF")
    parser.add_argument("--ccre-bed", type=Path, default=DEFAULT_CCRE_BED, help="Normalized 5-column cCRE BED.gz")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source label written to REG_CCRE_SOURCE")
    parser.add_argument("--summary-tsv", type=Path, help="Write tabular annotation statistics")
    parser.add_argument("--log-json", type=Path, help="Write JSON annotation statistics")
    args = parser.parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(f"Input VCF not found: {args.input}")
    if not args.ccre_bed.is_file():
        raise FileNotFoundError(f"cCRE BED not found: {args.ccre_bed}")

    stats = annotate_vcf(args.input, args.output, args.ccre_bed, args.source)
    if args.summary_tsv:
        write_summary_tsv(args.summary_tsv, stats)
    if args.log_json:
        args.log_json.parent.mkdir(parents=True, exist_ok=True)
        args.log_json.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(
        "Annotated "
        f"{stats['variants_with_ccre_overlap']} / {stats['total_variants']} variant(s) "
        f"with regulatory cCRE overlap to {args.output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
