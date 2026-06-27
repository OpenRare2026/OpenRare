#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

OUTPUT_COLUMN = "GENOS-VarRisk"


def normalize_chrom(value: str) -> str:
    chrom = value.strip()
    if chrom.lower().startswith("chr"):
        chrom = chrom[3:]
    return "MT" if chrom.upper() in {"M", "MT"} else chrom


def row_key_groups(row: dict[str, str]) -> list[list[tuple[str, int, str, str]]]:
    chrom = normalize_chrom(row.get("chrom", ""))
    pos_raw = row.get("pos", "").strip()
    ref = row.get("ref", "").strip().upper()
    alt_raw = row.get("alt", "").strip().upper()
    if not chrom or not pos_raw.isdigit() or not ref or not alt_raw:
        return []
    exact: list[tuple[str, int, str, str]] = []
    shifted: list[tuple[str, int, str, str]] = []
    for alt in [item for item in alt_raw.replace("/", ",").split(",") if item]:
        pos = int(pos_raw)
        exact.append((chrom, pos, ref, alt))
        if len(ref) != len(alt):
            shifted.append((chrom, pos - 1, ref, alt))
            shifted.append((chrom, pos + 1, ref, alt))
    groups: list[list[tuple[str, int, str, str]]] = []
    for raw_group in (exact, shifted):
        group: list[tuple[str, int, str, str]] = []
        seen: set[tuple[str, int, str, str]] = set()
        for key in raw_group:
            if key[1] > 0 and key not in seen:
                seen.add(key)
                group.append(key)
        if group:
            groups.append(group)
    return groups


def row_keys(row: dict[str, str]) -> list[tuple[str, int, str, str]]:
    return [key for group in row_key_groups(row) for key in group]


def add_column(fieldnames: list[str]) -> list[str]:
    if OUTPUT_COLUMN in fieldnames:
        return fieldnames
    fields: list[str] = []
    inserted = False
    for field in fieldnames:
        fields.append(field)
        if field == "alt":
            fields.append(OUTPUT_COLUMN)
            inserted = True
    if not inserted:
        fields.append(OUTPUT_COLUMN)
    return fields


def annotate(input_csv: Path, database: Path | None, output_csv: Path, log_json: Path | None) -> dict:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    database_available = database is not None and database.is_file() and Path(f"{database}.tbi").is_file()
    if database is not None and database.exists() and not database_available:
        raise FileNotFoundError(f"GENOS-VarRisk database index not found: {database}.tbi")
    if database_available and shutil.which("tabix") is None:
        raise RuntimeError("tabix command not found")

    with input_csv.open("r", newline="", encoding="utf-8-sig") as src:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header not found: {input_csv}")
        candidate_keys: set[tuple[str, int, str, str]] = set()
        input_rows = 0
        for row in reader:
            input_rows += 1
            candidate_keys.update(row_keys(row))

    lookup: dict[tuple[str, int, str, str], str] = {}
    database_hits = 0
    if database_available and candidate_keys:
        with tempfile.TemporaryDirectory(prefix="genos_evee_query_", dir=str(output_csv.parent)) as tmp_name:
            region_file = Path(tmp_name) / "regions.tsv"
            with region_file.open("w", encoding="utf-8") as handle:
                positions = sorted({(chrom, pos) for chrom, pos, _ref, _alt in candidate_keys}, key=lambda x: (x[0], x[1]))
                for chrom, pos in positions:
                    handle.write(f"{chrom}\t{pos}\t{pos}\n")
            proc = subprocess.run(
                ["tabix", "-R", str(region_file), str(database)],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            for line in proc.stdout.splitlines():
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 5:
                    continue
                key = (normalize_chrom(parts[0]), int(parts[1]), parts[2].upper(), parts[3].upper())
                old = lookup.get(key)
                score = parts[4]
                if old is None or float(score) > float(old):
                    lookup[key] = score
            database_hits = len(lookup)

    matched_rows = 0
    with input_csv.open("r", newline="", encoding="utf-8-sig") as src, output_csv.open(
        "w", newline="", encoding="utf-8"
    ) as dst:
        reader = csv.DictReader(src)
        assert reader.fieldnames is not None
        fieldnames = add_column(list(reader.fieldnames))
        writer = csv.DictWriter(dst, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            scores: list[str] = []
            for group in row_key_groups(row):
                scores = [lookup[key] for key in group if key in lookup]
                if scores:
                    break
            if scores:
                row[OUTPUT_COLUMN] = str(max(float(score) for score in scores))
                matched_rows += 1
            else:
                row[OUTPUT_COLUMN] = "-"
            writer.writerow({field: row.get(field, "-") for field in fieldnames})

    stats = {
        "input_csv": str(input_csv),
        "database": str(database) if database else "",
        "database_available": database_available,
        "output_csv": str(output_csv),
        "input_rows": input_rows,
        "candidate_cpra_keys": len(candidate_keys),
        "queried_database_cpra": database_hits,
        "matched_rows": matched_rows,
        "unmatched_rows": input_rows - matched_rows,
        "output_column": OUTPUT_COLUMN,
    }
    if log_json:
        log_json.parent.mkdir(parents=True, exist_ok=True)
        log_json.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Add GENOS-VarRisk p_fusion scores to a V3 wide CSV before sorting.")
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--database", help="Indexed GENOS-VarRisk .tsv.gz; missing/empty means fill '-'")
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--log-json")
    args = parser.parse_args()
    database = Path(args.database).resolve() if args.database else None
    stats = annotate(
        Path(args.input_csv).resolve(),
        database,
        Path(args.output_csv).resolve(),
        Path(args.log_json).resolve() if args.log_json else None,
    )
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
