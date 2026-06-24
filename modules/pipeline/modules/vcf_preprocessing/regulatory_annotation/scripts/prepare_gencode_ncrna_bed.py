#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import re
import sys
from collections import Counter


ATTR_RE = re.compile(r'([A-Za-z0-9_]+) "([^"]*)"')


def open_text(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "rt")


def parse_attrs(text: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(text))


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert GENCODE GTF gene records to ncRNA gene BED.")
    ap.add_argument("input_gtf")
    ap.add_argument("output_bed")
    ap.add_argument("--exclude-gene-type", action="append", default=["protein_coding"])
    args = ap.parse_args()

    excluded = set(args.exclude_gene_type)
    n_gene = 0
    n_out = 0
    counts: Counter[str] = Counter()

    with open_text(args.input_gtf) as inp, open(args.output_bed, "w") as out:
        for line in inp:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9 or fields[2] != "gene":
                continue
            n_gene += 1
            attrs = parse_attrs(fields[8])
            gene_type = attrs.get("gene_type") or attrs.get("gene_biotype") or "NA"
            if gene_type in excluded:
                continue

            chrom = fields[0]
            start = int(fields[3]) - 1
            end = int(fields[4])
            gene_id = attrs.get("gene_id", ".")
            gene_name = attrs.get("gene_name", gene_id)
            out.write(f"{chrom}\t{start}\t{end}\t{gene_id}\t{gene_name}\t{gene_type}\n")
            counts[gene_type] += 1
            n_out += 1

    sys.stderr.write(f"gene_records\t{n_gene}\n")
    sys.stderr.write(f"ncrna_gene_records\t{n_out}\n")
    for gene_type, count in counts.most_common():
        sys.stderr.write(f"gene_type\t{gene_type}\t{count}\n")


if __name__ == "__main__":
    main()
