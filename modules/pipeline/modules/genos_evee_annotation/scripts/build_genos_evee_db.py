#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

CHROM_ALIASES = ("chrom", "chr", "chromosome", "#chrom")
POS_ALIASES = ("pos", "position", "start")
REF_ALIASES = ("ref", "reference", "reference_allele")
ALT_ALIASES = ("alt", "alternate", "alternate_allele")
CPRA_ALIASES = ("cpra", "variant", "variant_id", "variant_key")
SCORE_ALIASES = ("p_fusion", "p-fusion", "pfusion")


def open_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("r", encoding="utf-8", errors="replace")


def find_field(fields: list[str], aliases: tuple[str, ...]) -> str | None:
    by_lower = {field.strip().lower(): field for field in fields}
    for alias in aliases:
        if alias in by_lower:
            return by_lower[alias]
    return None


def normalize_chrom(value: str) -> str:
    chrom = value.strip()
    if chrom.lower().startswith("chr"):
        chrom = chrom[3:]
    return "MT" if chrom.upper() in {"M", "MT"} else chrom


def parse_cpra(value: str) -> tuple[str, str, str, str] | None:
    parts = [part for part in re.split(r"[:_\-/|]+", value.strip()) if part]
    if len(parts) < 4:
        return None
    chrom, pos, ref, alt = parts[:4]
    if not pos.isdigit():
        return None
    return normalize_chrom(chrom), pos, ref.upper(), alt.upper()


def resolve_inputs(values: list[str]) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        path = Path(value).expanduser()
        if path.is_dir():
            paths.extend(sorted(path.glob("predictions.shard*.tsv*")))
            continue
        if any(char in value for char in "*?[]"):
            paths.extend(sorted(path.parent.glob(path.name)))
            continue
        paths.append(path)
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(resolved)
    return deduped


def extract_rows(path: Path, handle) -> tuple[int, int]:
    rows = 0
    valid = 0
    with open_text(path) as src:
        sample = src.read(65536)
        src.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters="\t,")
        reader = csv.DictReader(src, dialect=dialect)
        if reader.fieldnames is None:
            raise ValueError(f"header not found: {path}")
        fields = list(reader.fieldnames)
        score_field = find_field(fields, SCORE_ALIASES)
        if score_field is None:
            raise ValueError(f"p_fusion column not found in {path}; columns={fields}")
        cpra_field = find_field(fields, CPRA_ALIASES)
        chrom_field = find_field(fields, CHROM_ALIASES)
        pos_field = find_field(fields, POS_ALIASES)
        ref_field = find_field(fields, REF_ALIASES)
        alt_field = find_field(fields, ALT_ALIASES)
        if cpra_field is None and not all((chrom_field, pos_field, ref_field, alt_field)):
            raise ValueError(
                f"CPRA columns not found in {path}; expected CPRA/variant_id or chrom,pos,ref,alt; columns={fields}"
            )
        for row in reader:
            rows += 1
            if cpra_field:
                parsed = parse_cpra(row.get(cpra_field, ""))
                if parsed is None:
                    continue
                chrom, pos, ref, alt = parsed
            else:
                chrom = normalize_chrom(row.get(chrom_field or "", ""))
                pos = row.get(pos_field or "", "").strip()
                ref = row.get(ref_field or "", "").strip().upper()
                alt = row.get(alt_field or "", "").strip().upper()
            score = row.get(score_field, "").strip()
            if not chrom or not pos.isdigit() or not ref or not alt or score in {"", ".", "-"}:
                continue
            try:
                float(score)
            except ValueError:
                continue
            handle.write(f"{chrom}\t{pos}\t{ref}\t{alt}\t{score}\n")
            valid += 1
    return rows, valid


def run(cmd: list[str], **kwargs) -> None:
    subprocess.run(cmd, check=True, **kwargs)


def build_database(inputs: list[Path], output: Path, threads: int, log_json: Path | None) -> dict:
    for path in inputs:
        if not path.is_file():
            raise FileNotFoundError(path)
    if not inputs:
        raise ValueError("no prediction TSV files found")
    for command in ("sort", "bgzip", "tabix"):
        if shutil.which(command) is None:
            raise RuntimeError(f"required command not found: {command}")

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    stats: dict[str, object] = {"inputs": [], "output": str(output)}
    with tempfile.TemporaryDirectory(prefix="genos_evee_", dir=str(output.parent)) as tmp_name:
        tmp = Path(tmp_name)
        extracted = tmp / "extracted.tsv"
        sorted_path = tmp / "sorted.tsv"
        merged = tmp / "genos_evee.cpra.tsv"
        total_rows = 0
        total_valid = 0
        with extracted.open("w", encoding="utf-8") as dst:
            for path in inputs:
                rows, valid = extract_rows(path, dst)
                total_rows += rows
                total_valid += valid
                stats["inputs"].append({"path": str(path), "rows": rows, "valid_rows": valid})
        run(
            [
                "sort",
                "-T",
                str(tmp),
                "-k1,1V",
                "-k2,2n",
                "-k3,3",
                "-k4,4",
                "-k5,5gr",
                str(extracted),
                "-o",
                str(sorted_path),
            ]
        )
        unique = 0
        with sorted_path.open("r", encoding="utf-8") as src, merged.open("w", encoding="utf-8") as dst:
            dst.write("#CHROM\tPOS\tREF\tALT\tGENOS-EVEE\n")
            previous: tuple[str, str, str, str] | None = None
            for line in src:
                parts = line.rstrip("\n").split("\t")
                key = tuple(parts[:4])
                if key == previous:
                    continue
                dst.write(line)
                previous = key
                unique += 1
        uncompressed = output.with_suffix("") if output.suffix == ".gz" else output
        shutil.copyfile(merged, uncompressed)
        run(["bgzip", "-@", str(threads), "-f", str(uncompressed)])
        generated = Path(f"{uncompressed}.gz")
        if generated != output:
            generated.replace(output)
        run(["tabix", "-f", "-s", "1", "-b", "2", "-e", "2", str(output)])
        stats.update({"input_rows": total_rows, "valid_rows": total_valid, "unique_cpra": unique})
    if log_json:
        log_json.parent.mkdir(parents=True, exist_ok=True)
        log_json.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Build indexed GENOS-EVEE CPRA database from prediction TSV shards.")
    parser.add_argument("--input", action="append", required=True, help="TSV file, directory, or glob; repeatable")
    parser.add_argument("--output", required=True, help="Output .tsv.gz database")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--log-json")
    args = parser.parse_args()
    inputs = resolve_inputs(args.input)
    stats = build_database(
        inputs,
        Path(args.output),
        max(1, args.threads),
        Path(args.log_json) if args.log_json else None,
    )
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
