#!/usr/bin/env python3
"""
Add VAF-related fields to a VCF INFO column from sample FORMAT/AD.

The script keeps the input VCF structure intact and appends/replaces:
  - INFO/VAF: Variant allele frequency for each ALT allele, Number=A
  - INFO/REF_DP: Reference read depth from AD, Number=1
  - INFO/ALT_DP: Alternate read depth for each ALT allele, Number=A

Usage:
  python3 step2_add_vaf_to_vcf_info.py input.vcf.gz output.vaf.vcf.gz
  python3 step2_add_vaf_to_vcf_info.py input.vcf.gz output.vaf.vcf.gz --sample P001
"""

from __future__ import annotations

import argparse
import gzip
import io
import shutil
import subprocess
import sys
from pathlib import Path


INFO_HEADERS = [
    '##INFO=<ID=VAF,Number=A,Type=Float,Description="Variant allele frequency calculated from sample FORMAT/AD as ALT_DEPTH/(REF_DEPTH+sum(ALT_DEPTHS)); one value per ALT allele">',
    '##INFO=<ID=REF_DP,Number=1,Type=Integer,Description="Reference allele depth calculated from sample FORMAT/AD">',
    '##INFO=<ID=ALT_DP,Number=A,Type=Integer,Description="Alternate allele depth calculated from sample FORMAT/AD; one value per ALT allele">',
]

INFO_IDS = {"VAF", "REF_DP", "ALT_DP"}


def open_vcf_reader(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open("r")


def open_vcf_writer(path: Path):
    if str(path).endswith(".gz"):
        if shutil.which("bgzip"):
            raw_out = path.open("wb")
            proc = subprocess.Popen(["bgzip", "-c"], stdin=subprocess.PIPE, stdout=raw_out)
            assert proc.stdin is not None
            text_out = io.TextIOWrapper(proc.stdin, encoding="utf-8", newline="")
            return text_out, proc, raw_out
        return gzip.open(path, "wt"), None, None
    return path.open("w"), None, None


def close_vcf_writer(handle, proc, raw_out) -> None:
    handle.close()
    if proc is not None:
        return_code = proc.wait()
        if raw_out is not None:
            raw_out.close()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, ["bgzip", "-c"])


def parse_info(info: str) -> list[tuple[str, str | None]]:
    if not info or info == ".":
        return []
    parsed: list[tuple[str, str | None]] = []
    for item in info.split(";"):
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
            parsed.append((key, value))
        else:
            parsed.append((item, None))
    return parsed


def format_info(items: list[tuple[str, str | None]]) -> str:
    if not items:
        return "."
    out = []
    for key, value in items:
        if value is None:
            out.append(key)
        else:
            out.append(f"{key}={value}")
    return ";".join(out)


def parse_ad(ad_value: str) -> tuple[int, list[int]] | None:
    if not ad_value or ad_value == ".":
        return None
    try:
        depths = [int(x) for x in ad_value.split(",")]
    except ValueError:
        return None
    if len(depths) < 2:
        return None
    return depths[0], depths[1:]


def calc_vaf_values(ad_value: str, alt_count: int) -> tuple[str, str, str] | None:
    parsed = parse_ad(ad_value)
    if parsed is None:
        return None

    ref_depth, alt_depths = parsed
    if len(alt_depths) < alt_count:
        alt_depths = alt_depths + [0] * (alt_count - len(alt_depths))
    else:
        alt_depths = alt_depths[:alt_count]

    total_depth = ref_depth + sum(alt_depths)
    if total_depth <= 0:
        return None

    vafs = [f"{alt_depth / total_depth:.6f}" for alt_depth in alt_depths]
    return ",".join(vafs), str(ref_depth), ",".join(str(x) for x in alt_depths)


def add_or_replace_info(info: str, values: tuple[str, str, str] | None) -> str:
    items = [(key, value) for key, value in parse_info(info) if key not in INFO_IDS]
    if values is None:
        return format_info(items)

    vaf, ref_dp, alt_dp = values
    items.extend([("VAF", vaf), ("REF_DP", ref_dp), ("ALT_DP", alt_dp)])
    return format_info(items)


def add_vaf_to_vcf(input_vcf: Path, output_vcf: Path, sample_name: str | None = None) -> dict[str, int | str]:
    stats = {
        "records_total": 0,
        "records_with_vaf": 0,
        "records_missing_ad": 0,
        "sample": sample_name or "",
    }

    header_inserted = False
    sample_index = None

    reader = open_vcf_reader(input_vcf)
    writer, proc, raw_out = open_vcf_writer(output_vcf)
    try:
        with reader, writer:
            for line in reader:
                if line.startswith("##INFO=<ID="):
                    info_id = line.split("ID=", 1)[1].split(",", 1)[0].split(">", 1)[0]
                    if info_id in INFO_IDS:
                        continue

                if line.startswith("#CHROM"):
                    if not header_inserted:
                        for header in INFO_HEADERS:
                            writer.write(header + "\n")
                        header_inserted = True

                    cols = line.rstrip("\n").split("\t")
                    samples = cols[9:]
                    if not samples:
                        raise SystemExit("ERROR: VCF has no sample columns")

                    if sample_name:
                        if sample_name not in samples:
                            raise SystemExit(f"ERROR: sample '{sample_name}' not found. Available: {samples}")
                        sample_index = samples.index(sample_name)
                    else:
                        sample_index = 0
                        sample_name = samples[0]
                    stats["sample"] = sample_name
                    writer.write(line)
                    continue

                if line.startswith("#"):
                    writer.write(line)
                    continue

                parts = line.rstrip("\n").split("\t")
                if len(parts) < 10:
                    writer.write(line)
                    continue
                if sample_index is None:
                    raise SystemExit("ERROR: #CHROM header was not found before records")

                stats["records_total"] += 1
                alt_count = len(parts[4].split(","))
                format_keys = parts[8].split(":")
                sample_values = parts[9 + sample_index].split(":")

                values = None
                if "AD" in format_keys:
                    ad_idx = format_keys.index("AD")
                    if ad_idx < len(sample_values):
                        values = calc_vaf_values(sample_values[ad_idx], alt_count)

                if values is None:
                    stats["records_missing_ad"] += 1
                else:
                    stats["records_with_vaf"] += 1

                parts[7] = add_or_replace_info(parts[7], values)
                writer.write("\t".join(parts) + "\n")
    finally:
        if not writer.closed:
            close_vcf_writer(writer, proc, raw_out)
        elif proc is not None:
            return_code = proc.wait()
            if raw_out is not None:
                raw_out.close()
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, ["bgzip", "-c"])

    if str(output_vcf).endswith(".gz") and shutil.which("tabix"):
        subprocess.run(["tabix", "-f", "-p", "vcf", str(output_vcf)], check=True)

    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add VAF/REF_DP/ALT_DP to VCF INFO from FORMAT/AD")
    parser.add_argument("input_vcf", type=Path)
    parser.add_argument("output_vcf", type=Path)
    parser.add_argument("--sample", help="Sample name to use. Default: first sample column.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = add_vaf_to_vcf(args.input_vcf, args.output_vcf, args.sample)
    print(f"Done. Output: {args.output_vcf}")
    print(f"Sample: {stats['sample']}")
    print(f"Total records: {stats['records_total']}")
    print(f"Records with VAF: {stats['records_with_vaf']}")
    print(f"Records missing AD/VAF: {stats['records_missing_ad']}")


if __name__ == "__main__":
    main()
