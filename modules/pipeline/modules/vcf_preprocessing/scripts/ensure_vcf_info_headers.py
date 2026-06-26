#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import io
import shutil
import subprocess
from pathlib import Path

HEADERS: dict[str, list[str]] = {
    "phasing": [
        '##INFO=<ID=BEAGLE_PHASED,Number=1,Type=Integer,Description="1 if GT was replaced by Beagle noimpute phased GT; 0 if original GT was retained">',
        '##INFO=<ID=CHN_REF_SUPPORT,Number=1,Type=String,Description="Support category in the supplied reference panel: POLYMORPHIC, MONOMORPHIC_REF, ALLELE_MISMATCH, NOT_IN_REF">',
        '##INFO=<ID=CHN_ALT_CARRIER_COUNT,Number=1,Type=Integer,Description="Number of reference samples carrying allele 1 at an exactly matched CHROM/POS/REF/ALT marker">',
        '##INFO=<ID=CHN_ALT_AC,Number=1,Type=Integer,Description="Allele 1 count in reference samples at an exactly matched CHROM/POS/REF/ALT marker">',
        '##INFO=<ID=PHASING_CONFIDENCE,Number=1,Type=String,Description="Confidence label based on Beagle output and reference ALT support: HIGH, LOW, UNPHASED">',
    ],
    "vaf": [
        '##INFO=<ID=VAF,Number=A,Type=Float,Description="Variant allele frequency calculated from sample FORMAT/AD as ALT_DEPTH/(REF_DEPTH+sum(ALT_DEPTHS)); one value per ALT allele">',
        '##INFO=<ID=REF_DP,Number=1,Type=Integer,Description="Reference allele depth calculated from sample FORMAT/AD">',
        '##INFO=<ID=ALT_DP,Number=A,Type=Integer,Description="Alternate allele depth calculated from sample FORMAT/AD; one value per ALT allele">',
    ],
    "regulatory": [
        '##INFO=<ID=REG_CCRE_ID,Number=.,Type=String,Description="ENCODE SCREEN cCRE identifiers overlapping this variant interval">',
        '##INFO=<ID=REG_CCRE_CLASS,Number=.,Type=String,Description="ENCODE SCREEN cCRE classes overlapping this variant interval">',
        '##INFO=<ID=REG_CCRE_COUNT,Number=1,Type=Integer,Description="Number of ENCODE SCREEN cCRE intervals overlapping this variant interval">',
        '##INFO=<ID=REG_CCRE_SOURCE,Number=1,Type=String,Description="Regulatory annotation source version">',
    ],
    "ncrna": [
        '##INFO=<ID=NCRNA_GENE_ID,Number=.,Type=String,Description="GENCODE non-coding RNA gene identifiers overlapping this variant interval">',
        '##INFO=<ID=NCRNA_GENE_NAME,Number=.,Type=String,Description="GENCODE non-coding RNA gene names overlapping this variant interval">',
        '##INFO=<ID=NCRNA_GENE_TYPE,Number=.,Type=String,Description="GENCODE non-coding RNA gene types overlapping this variant interval">',
        '##INFO=<ID=NCRNA_GENE_COUNT,Number=1,Type=Integer,Description="Number of GENCODE non-coding RNA gene intervals overlapping this variant interval">',
        '##INFO=<ID=NCRNA_SOURCE,Number=1,Type=String,Description="Non-coding RNA annotation source version">',
    ],
    "pseudogene": [
        '##INFO=<ID=is_pseudogene,Number=1,Type=String,Description="Pseudogene annotation result: Yes or No">',
        '##INFO=<ID=pseudogene_name,Number=.,Type=String,Description="HGNC pseudogene symbol list; VCF-escaped %3B separates multiple names; - means reads-level evidence only; . means missing">',
        '##INFO=<ID=pseudogene_source,Number=1,Type=String,Description="Pseudogene annotation source: GENCODE.v49, Pseudogene.org, Pseudogene.org&GENCODE.v49, Reads_mapped, or .">',
    ],
}


def open_reader(path: Path):
    return gzip.open(path, "rt") if str(path).endswith(".gz") else path.open("r", encoding="utf-8", errors="replace")


def open_writer(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if str(path).endswith(".gz"):
        if shutil.which("bgzip"):
            raw = path.open("wb")
            proc = subprocess.Popen(["bgzip", "-c"], stdin=subprocess.PIPE, stdout=raw)
            assert proc.stdin is not None
            return io.TextIOWrapper(proc.stdin, encoding="utf-8", newline=""), proc, raw
        return gzip.open(path, "wt"), None, None
    return path.open("w", encoding="utf-8"), None, None


def close_writer(handle, proc, raw) -> None:
    handle.close()
    if proc is not None:
        code = proc.wait()
        if raw is not None:
            raw.close()
        if code != 0:
            raise subprocess.CalledProcessError(code, ["bgzip", "-c"])


def main() -> None:
    ap = argparse.ArgumentParser(description="Add expected V3 INFO headers to a VCF without changing variant records.")
    ap.add_argument("--input-vcf", required=True)
    ap.add_argument("--output-vcf", required=True)
    ap.add_argument("--groups", required=True, help="Comma-separated groups: phasing,vaf,regulatory,ncrna,pseudogene")
    ap.add_argument("--index", action="store_true", help="Create tabix index for .gz output")
    args = ap.parse_args()
    groups = [x.strip() for x in args.groups.split(",") if x.strip()]
    wanted: list[str] = []
    for group in groups:
        if group not in HEADERS:
            raise SystemExit(f"unknown group: {group}")
        wanted.extend(HEADERS[group])

    input_vcf = Path(args.input_vcf)
    output_vcf = Path(args.output_vcf)
    existing: set[str] = set()
    inserted = False
    reader = open_reader(input_vcf)
    writer, proc, raw = open_writer(output_vcf)
    try:
        with reader, writer:
            for line in reader:
                if line.startswith("##INFO=<ID="):
                    existing.add(line.split("ID=", 1)[1].split(",", 1)[0].split(">", 1)[0])
                if line.startswith("#CHROM") and not inserted:
                    for header in wanted:
                        info_id = header.split("ID=", 1)[1].split(",", 1)[0]
                        if info_id not in existing:
                            writer.write(header + "\n")
                    inserted = True
                writer.write(line)
    finally:
        close_writer(writer, proc, raw)
    if args.index and str(output_vcf).endswith(".gz"):
        if shutil.which("bcftools"):
            subprocess.run(["bcftools", "index", "-f", "-t", str(output_vcf)], check=True)
        elif shutil.which("tabix"):
            subprocess.run(["tabix", "-f", "-p", "vcf", str(output_vcf)], check=True)


if __name__ == "__main__":
    main()
