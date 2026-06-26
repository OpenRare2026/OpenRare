#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

HLA_CHROM = "6"
HLA_START = 28477797
HLA_END = 33448354


def normalize_chrom(value: str) -> str:
    value = (value or "").strip()
    if value.lower().startswith("chr"):
        value = value[3:]
    return "MT" if value.upper() in {"M", "MT"} else value


def in_hla(row: dict[str, str]) -> bool:
    chrom = normalize_chrom(row.get("chrom", row.get("#CHROM", "")))
    pos = row.get("pos", row.get("POS", "")).strip()
    if chrom != HLA_CHROM or not pos.isdigit():
        return False
    value = int(pos)
    return HLA_START <= value <= HLA_END


def main() -> None:
    ap = argparse.ArgumentParser(description="Remove rows in the GRCh38 HLA/MHC region from a V3 wide CSV.")
    ap.add_argument("--input-csv", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--log-json")
    args = ap.parse_args()
    input_csv = Path(args.input_csv)
    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    total = removed = kept = 0
    with input_csv.open("r", newline="", encoding="utf-8-sig") as src, output_csv.open(
        "w", newline="", encoding="utf-8"
    ) as dst:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header not found: {input_csv}")
        writer = csv.DictWriter(dst, fieldnames=reader.fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            total += 1
            if in_hla(row):
                removed += 1
                continue
            writer.writerow(row)
            kept += 1
    stats = {
        "input_csv": str(input_csv),
        "output_csv": str(output_csv),
        "hla_region": f"GRCh38 chr6:{HLA_START}-{HLA_END}",
        "input_rows": total,
        "removed_hla_rows": removed,
        "kept_rows": kept,
    }
    if args.log_json:
        Path(args.log_json).write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
