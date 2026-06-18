#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from backend.utils.scoring import add_pathogenic_fields, clean_output_value, row_score

HIDDEN_SCORE_FIELDS = [
    "_clinvar_score",
    "_consequence_score",
    "_splice_lof_score",
    "_prediction_score",
    "_frequency_score",
    "_domain_score",
    "_raw_pathogenic_score",
]


def sort_csv(input_csv: Path, output_csv: Path, log_json: Path | None = None) -> dict[str, object]:
    with input_csv.open("r", newline="") as src:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header not found: {input_csv}")
        fieldnames = list(reader.fieldnames)
        for column in ("pathogenic_rank", "evidence_summary"):
            if column not in fieldnames:
                fieldnames.append(column)
        rows = list(reader)

    for seq, row in enumerate(rows):
        row["_original_seq"] = str(seq)
        add_pathogenic_fields(row)

    rows.sort(key=lambda row: (row_score(row, "_raw_pathogenic_score"), -int(row.get("_original_seq", "0"))), reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["pathogenic_rank"] = str(rank)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            for hidden in HIDDEN_SCORE_FIELDS + ["_original_seq"]:
                row.pop(hidden, None)
            writer.writerow({field: clean_output_value(row.get(field, "-")) for field in fieldnames})

    stats = {"input_csv": str(input_csv), "output_csv": str(output_csv), "rows": len(rows), "sort_key": "_raw_pathogenic_score desc, original_order asc"}
    if log_json:
        log_json.parent.mkdir(parents=True, exist_ok=True)
        log_json.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Sort VEP CSV by the OpenRare pathogenic ranking score.")
    parser.add_argument("--input-csv", required=True, help="CSV before final ranking")
    parser.add_argument("--output-csv", required=True, help="Final sorted CSV")
    parser.add_argument("--log-json", help="Optional JSON statistics path")
    args = parser.parse_args()
    stats = sort_csv(Path(args.input_csv), Path(args.output_csv), Path(args.log_json) if args.log_json else None)
    print(f"Sorted {stats['rows']} CSV row(s): {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
