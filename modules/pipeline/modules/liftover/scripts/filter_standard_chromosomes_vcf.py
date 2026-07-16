#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
from pathlib import Path


AUTOSOMES = {str(i) for i in range(1, 23)}
SEX_CHROMS = {"X", "Y"}
MITO_CHROMS = {"M", "MT"}
STANDARD = AUTOSOMES | SEX_CHROMS | MITO_CHROMS


def open_text(path: Path, mode: str):
    if "r" in mode and path.suffix == ".gz":
        return gzip.open(path, mode + "t", encoding="utf-8")
    return path.open(mode, encoding="utf-8")


def canonical_chrom(chrom: str) -> str:
    value = chrom.strip()
    if value.lower().startswith("chr"):
        value = value[3:]
    value = value.upper()
    if value == "M":
        return "MT"
    return value


def is_standard_chrom(chrom: str) -> bool:
    return canonical_chrom(chrom) in STANDARD


def contig_id_from_header(line: str) -> str | None:
    prefix = "##contig=<ID="
    if not line.startswith(prefix):
        return None
    rest = line[len(prefix) :]
    for sep in (",", ">"):
        idx = rest.find(sep)
        if idx >= 0:
            return rest[:idx]
    return rest.strip()


def filter_vcf(input_vcf: Path, output_vcf: Path, ignored_tsv: Path, stats_tsv: Path) -> None:
    output_vcf.parent.mkdir(parents=True, exist_ok=True)
    ignored_tsv.parent.mkdir(parents=True, exist_ok=True)
    stats_tsv.parent.mkdir(parents=True, exist_ok=True)

    total_records = 0
    kept_records = 0
    ignored_records = 0
    ignored_contigs: dict[str, int] = {}

    with open_text(input_vcf, "r") as src, output_vcf.open("w", encoding="utf-8") as out, ignored_tsv.open(
        "w", encoding="utf-8"
    ) as ignored:
        ignored.write("chrom\tpos\tid\tref\talt\treason\n")
        for line in src:
            if line.startswith("##contig=<ID="):
                contig = contig_id_from_header(line)
                if contig and not is_standard_chrom(contig):
                    continue
                out.write(line)
                continue
            if line.startswith("#"):
                out.write(line)
                continue

            total_records += 1
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 5:
                ignored_records += 1
                ignored.write(".\t.\t.\t.\t.\tmalformed_vcf_record\n")
                continue

            chrom, pos, var_id, ref, alt = fields[:5]
            if is_standard_chrom(chrom):
                kept_records += 1
                out.write(line)
            else:
                ignored_records += 1
                ignored_contigs[chrom] = ignored_contigs.get(chrom, 0) + 1
                ignored.write(f"{chrom}\t{pos}\t{var_id}\t{ref}\t{alt}\tnonstandard_chromosome\n")

    with stats_tsv.open("w", encoding="utf-8") as stats:
        stats.write("metric\tvalue\n")
        stats.write(f"input_records\t{total_records}\n")
        stats.write(f"kept_standard_records\t{kept_records}\n")
        stats.write(f"ignored_nonstandard_records\t{ignored_records}\n")
        stats.write(f"ignored_nonstandard_contig_count\t{len(ignored_contigs)}\n")
        for chrom, count in sorted(ignored_contigs.items()):
            stats.write(f"ignored_contig:{chrom}\t{count}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep only standard human chromosomes in a VCF and log ignored nonstandard records."
    )
    parser.add_argument("--input-vcf", required=True, type=Path)
    parser.add_argument("--output-vcf", required=True, type=Path, help="Uncompressed VCF output path")
    parser.add_argument("--ignored-tsv", required=True, type=Path)
    parser.add_argument("--stats-tsv", required=True, type=Path)
    args = parser.parse_args()

    filter_vcf(args.input_vcf, args.output_vcf, args.ignored_tsv, args.stats_tsv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
