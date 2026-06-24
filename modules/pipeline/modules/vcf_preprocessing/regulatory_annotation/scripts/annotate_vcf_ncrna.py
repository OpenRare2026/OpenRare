#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import gzip
import sys
from collections import defaultdict
from datetime import date


INFO_HEADERS = [
    '##INFO=<ID=NCRNA_GENE_ID,Number=.,Type=String,Description="GENCODE non-coding RNA gene identifiers overlapping this variant interval">',
    '##INFO=<ID=NCRNA_GENE_NAME,Number=.,Type=String,Description="GENCODE non-coding RNA gene names overlapping this variant interval">',
    '##INFO=<ID=NCRNA_GENE_TYPE,Number=.,Type=String,Description="GENCODE non-coding RNA gene types overlapping this variant interval">',
    '##INFO=<ID=NCRNA_GENE_COUNT,Number=1,Type=Integer,Description="Number of GENCODE non-coding RNA gene intervals overlapping this variant interval">',
    '##INFO=<ID=NCRNA_SOURCE,Number=1,Type=String,Description="Non-coding RNA annotation source version">',
]


def open_text(path: str):
    if path == "-":
        return sys.stdin
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "rt")


def load_bed(path: str):
    by_chrom = defaultdict(list)
    with open_text(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) < 6:
                raise SystemExit(f"BED requires at least 6 columns: {line[:120]}")
            chrom, start, end, gene_id, gene_name, gene_type = f[:6]
            start_i = int(start)
            end_i = int(end)
            if end_i <= start_i:
                continue
            by_chrom[chrom].append((start_i, end_i, gene_id, gene_name, gene_type))

    index = {}
    for chrom, rows in by_chrom.items():
        rows.sort(key=lambda x: (x[0], x[1], x[2]))
        starts = [r[0] for r in rows]
        max_len = max(r[1] - r[0] for r in rows)
        index[chrom] = (rows, starts, max_len)
    return index


def uniq(values):
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def overlap(index, chrom: str, start: int, end: int):
    if chrom not in index:
        return []
    rows, starts, max_len = index[chrom]
    i = bisect.bisect_left(starts, end) - 1
    lower_start = start - max_len
    hits = []
    while i >= 0 and rows[i][0] >= lower_start:
        r_start, r_end, gene_id, gene_name, gene_type = rows[i]
        if r_start < end and r_end > start:
            hits.append((r_start, r_end, gene_id, gene_name, gene_type))
        i -= 1
    hits.sort(key=lambda x: (x[0], x[1], x[2]))
    return hits


def add_info(info: str, key: str, value: str) -> str:
    if info == "." or info == "":
        return f"{key}={value}"
    return f"{info};{key}={value}"


def main() -> None:
    ap = argparse.ArgumentParser(description="Annotate VCF variants with GENCODE ncRNA gene overlaps.")
    ap.add_argument("--vcf", required=True, help="Input VCF, optionally .gz")
    ap.add_argument("--bed", required=True, help="6-column BED: chrom start end gene_id gene_name gene_type")
    ap.add_argument("--source", default="GENCODE_v49_GRCh38_ncRNA_gene")
    ap.add_argument("--stats", help="Write summary TSV")
    args = ap.parse_args()

    index = load_bed(args.bed)
    total = annotated = 0
    type_counts = defaultdict(int)
    existing_info = set()
    pending_headers = []

    with open_text(args.vcf) as fh:
        for line in fh:
            if line.startswith("##INFO=<ID="):
                existing_info.add(line.split("ID=", 1)[1].split(",", 1)[0])
                pending_headers.append(line)
                continue
            if line.startswith("##"):
                pending_headers.append(line)
                continue
            if line.startswith("#CHROM"):
                for h in pending_headers:
                    sys.stdout.write(h)
                for h in INFO_HEADERS:
                    info_id = h.split("ID=", 1)[1].split(",", 1)[0]
                    if info_id not in existing_info:
                        sys.stdout.write(h + "\n")
                sys.stdout.write(line)
                break
        else:
            raise SystemExit("Input does not look like a VCF: missing #CHROM header")

        for line in fh:
            if not line.strip() or line.startswith("#"):
                sys.stdout.write(line)
                continue
            total += 1
            f = line.rstrip("\n").split("\t")
            if len(f) < 8:
                sys.stdout.write(line)
                continue
            chrom = f[0]
            pos = int(f[1])
            ref = f[3]
            start = pos - 1
            end = start + max(1, len(ref))
            hits = overlap(index, chrom, start, end)
            if hits:
                annotated += 1
                gene_ids = uniq([h[2] for h in hits])
                gene_names = uniq([h[3] for h in hits])
                gene_types = uniq([h[4] for h in hits])
                for gene_type in gene_types:
                    type_counts[gene_type] += 1
                info = f[7]
                info = add_info(info, "NCRNA_GENE_ID", ",".join(gene_ids))
                info = add_info(info, "NCRNA_GENE_NAME", ",".join(gene_names))
                info = add_info(info, "NCRNA_GENE_TYPE", ",".join(gene_types))
                info = add_info(info, "NCRNA_GENE_COUNT", str(len(hits)))
                info = add_info(info, "NCRNA_SOURCE", args.source)
                f[7] = info
                sys.stdout.write("\t".join(f) + "\n")
            else:
                sys.stdout.write(line)

    if args.stats:
        with open(args.stats, "w") as out:
            out.write("metric\tvalue\n")
            out.write(f"source\t{args.source}\n")
            out.write(f"run_date\t{date.today().isoformat()}\n")
            out.write(f"total_variants\t{total}\n")
            out.write(f"variants_with_ncrna_overlap\t{annotated}\n")
            out.write(f"variants_without_ncrna_overlap\t{total - annotated}\n")
            for gene_type, count in sorted(type_counts.items(), key=lambda x: (-x[1], x[0])):
                out.write(f"gene_type:{gene_type}\t{count}\n")


if __name__ == "__main__":
    main()
