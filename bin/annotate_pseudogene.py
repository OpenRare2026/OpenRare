#!/usr/bin/env python3
"""Annotate VCF-like CSV rows with HGNC-backed pseudogene overlap."""

from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


RUNNER_DIR = Path(__file__).resolve().parents[1]
PSEUDOGENE_DATA_DIR = RUNNER_DIR / "vep_data" / "pseudogene"
DEFAULT_GENCODE_GTF = (
    PSEUDOGENE_DATA_DIR
    / "GENCODE"
    / "release_49"
    / "gencode.v49.2wayconspseudos.gtf.gz"
)
DEFAULT_PSEUDOGENE_ORG = (
    PSEUDOGENE_DATA_DIR / "Pseudogene.org" / "Human90" / "Human90.txt"
)
DEFAULT_HGNC = PSEUDOGENE_DATA_DIR / "HGNC" / "hgnc_complete_set.txt"


@dataclass(frozen=True)
class Interval:
    chrom: str
    start: int
    end: int
    symbol: str
    source: str
    raw_id: str


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
        chrom_intervals = self.by_chrom.get(chrom)
        if not chrom_intervals:
            return []
        starts = self.starts[chrom]
        stop = bisect.bisect_right(starts, pos)
        matches: list[Interval] = []
        for interval in reversed(chrom_intervals[:stop]):
            if interval.end < pos:
                # Intervals are short enough here that this reverse scan is fine.
                continue
            if interval.start <= pos <= interval.end:
                matches.append(interval)
        return matches


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


def annotate_csv(input_csv: Path, output_csv: Path, index: IntervalIndex) -> dict[str, object]:
    total_rows = 0
    annotated_rows = 0
    source_counts: Counter[str] = Counter()
    unique_symbols: set[str] = set()

    with input_csv.open(newline="") as in_handle, output_csv.open(
        "w", newline=""
    ) as out_handle:
        reader = csv.DictReader(in_handle)
        required = {"chrom", "pos"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"input CSV missing required columns: {sorted(missing)}")

        new_fields = [
            "is_pseudogene",
            "pseudogene_name",
            "pseudogene_source",
        ]
        fieldnames = list(reader.fieldnames or [])
        for field in new_fields:
            if field not in fieldnames:
                fieldnames.append(field)
        writer = csv.DictWriter(out_handle, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            total_rows += 1
            chrom = normalize_chrom(row["chrom"])
            try:
                pos = int(row["pos"])
            except ValueError as exc:
                raise ValueError(f"invalid pos at input row {total_rows + 1}: {row['pos']}") from exc

            matches = index.query(chrom, pos)
            symbols = sorted({match.symbol for match in matches})
            sources = {match.source for match in matches}
            if symbols:
                annotated_rows += 1
                unique_symbols.update(symbols)
                label = source_label(sources)
                source_counts[label] += 1
                row["is_pseudogene"] = "Yes"
                row["pseudogene_name"] = ";".join(symbols)
                row["pseudogene_source"] = label
            else:
                source_counts["Not_pseudogene"] += 1
                row["is_pseudogene"] = "No"
                row["pseudogene_name"] = ""
                row["pseudogene_source"] = ""
            writer.writerow(row)

    return {
        "input_rows": total_rows,
        "annotated_as_pseudogene": annotated_rows,
        "not_pseudogene": total_rows - annotated_rows,
        "unique_annotated_pseudogene_names": len(unique_symbols),
        "source_counts": dict(source_counts),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Annotate CSV variant positions with HGNC-backed pseudogene overlaps "
            "from GENCODE v49 and Pseudogene.org."
        )
    )
    parser.add_argument("--input", required=True, type=Path, help="Input VEP-style CSV.")
    parser.add_argument("--output", type=Path, help="Output annotated CSV.")
    parser.add_argument("--gencode-gtf", default=DEFAULT_GENCODE_GTF, type=Path)
    parser.add_argument("--pseudogene-org", default=DEFAULT_PSEUDOGENE_ORG, type=Path)
    parser.add_argument("--hgnc", default=DEFAULT_HGNC, type=Path)
    parser.add_argument("--log-json", type=Path, help="Optional JSON log output path.")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    output = args.output
    if output is None:
        output = args.input.with_name(f"{args.input.stem}.pseudogene_annotated.csv")

    pgohum_to_symbols, hgnc_stats = load_hgnc_pseudogene_map(args.hgnc)
    gencode_intervals, gencode_stats = load_gencode_intervals(
        args.gencode_gtf, pgohum_to_symbols
    )
    pseudogene_org_intervals, pseudogene_org_stats = load_pseudogene_org_intervals(
        args.pseudogene_org, pgohum_to_symbols
    )
    index = IntervalIndex(gencode_intervals + pseudogene_org_intervals)
    annotate_stats = annotate_csv(args.input, output, index)

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
