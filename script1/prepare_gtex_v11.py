#!/usr/bin/env python3
"""Build a GTEx v11 gene-level tissue-median TPM GCT for Network.py.

The shared GTEx v11 files are transcript-by-sample TPM plus sample metadata.
Network.py expects the older GTEx gene_median_tpm.gct shape:

    Name  Description  Tissue_1  Tissue_2 ...

This script streams the transcript TPM file, sums transcripts per gene for
each sample, then computes the median TPM for every detailed GTEx tissue.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_SOURCE_DIR = Path(os.environ.get("GTEX_V11_SOURCE_DIR", PROJECT_DIR / "data" / "GTEx" / "v11"))
DEFAULT_DATA_DIR = Path(os.environ.get("RARE_PPI_DATA_DIR", PROJECT_DIR / "data"))
TRANSCRIPT_TPM_NAME = "GTEx_Analysis_2025-08-22_v11_RSEMv1.3.3_transcripts_tpm.txt.gz"
SAMPLE_METADATA_NAME = "GTEx_Analysis_v11_Annotations_SampleAttributesDS.txt"
OUTPUT_NAME = "GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.gct.gz"
MANIFEST_NAME = "GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.manifest.json"


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def stable_gene_id(gene_id: str) -> str:
    return gene_id.split(".", 1)[0]


def read_tsv_header(path: Path) -> List[str]:
    with path.open(encoding="utf-8", errors="replace") as handle:
        return handle.readline().rstrip("\n").split("\t")


def load_gene_symbols(data_dir: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}

    biomart = data_dir / "ensembl_biomart_export.txt"
    if biomart.exists():
        with biomart.open(encoding="utf-8", errors="replace") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            gene_idx = header.index("Gene stable ID")
            symbol_idx = header.index("HGNC symbol") if "HGNC symbol" in header else None
            name_idx = header.index("Gene name") if "Gene name" in header else None
            for line in handle:
                row = line.rstrip("\n").split("\t")
                if len(row) <= gene_idx:
                    continue
                gene = stable_gene_id(row[gene_idx])
                symbol = ""
                if symbol_idx is not None and len(row) > symbol_idx:
                    symbol = row[symbol_idx].strip()
                if not symbol and name_idx is not None and len(row) > name_idx:
                    symbol = row[name_idx].strip()
                if gene and symbol:
                    mapping.setdefault(gene, symbol)

    hgnc = data_dir / "hgnc_complete_set.txt"
    if hgnc.exists():
        with hgnc.open(encoding="utf-8", errors="replace") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            gene_idx = header.index("ensembl_gene_id")
            symbol_idx = header.index("symbol")
            for line in handle:
                row = line.rstrip("\n").split("\t")
                if len(row) <= max(gene_idx, symbol_idx):
                    continue
                gene = stable_gene_id(row[gene_idx].strip())
                symbol = row[symbol_idx].strip()
                if gene and symbol:
                    mapping[gene] = symbol

    return mapping


def read_expression_samples(expression_path: Path) -> List[str]:
    with gzip.open(expression_path, "rt", encoding="utf-8", errors="replace") as handle:
        header = handle.readline().rstrip("\n").split("\t")
    if len(header) < 3 or header[0] != "transcript_id" or header[1] != "gene_id":
        raise ValueError(f"Unexpected GTEx v11 transcript TPM header in {expression_path}")
    return header[2:]


def load_sample_tissues(metadata_path: Path, samples: Iterable[str]) -> Tuple[List[str], Dict[str, np.ndarray]]:
    requested = list(samples)
    requested_set = set(requested)
    sample_to_tissue: Dict[str, str] = {}

    with metadata_path.open(encoding="utf-8", errors="replace") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        sample_idx = header.index("SAMPID")
        tissue_idx = header.index("SMTSD")
        analyte_idx = header.index("ANALYTE_TYPE")
        for line in handle:
            row = line.rstrip("\n").split("\t")
            if len(row) <= max(sample_idx, tissue_idx, analyte_idx):
                continue
            sample = row[sample_idx]
            if sample not in requested_set:
                continue
            if not row[analyte_idx].startswith("RNA"):
                continue
            tissue = row[tissue_idx].strip()
            if tissue:
                sample_to_tissue[sample] = tissue

    missing = [sample for sample in requested if sample not in sample_to_tissue]
    if missing:
        examples = ", ".join(missing[:5])
        raise ValueError(f"{len(missing)} expression samples are missing from metadata, e.g. {examples}")

    tissues = sorted(set(sample_to_tissue.values()))
    groups = {
        tissue: np.array(
            [idx for idx, sample in enumerate(requested) if sample_to_tissue[sample] == tissue],
            dtype=np.int64,
        )
        for tissue in tissues
    }
    return tissues, groups


def format_tpm(value: float) -> str:
    if not np.isfinite(value):
        return "0"
    if abs(value) < 5e-7:
        return "0"
    return f"{value:.6g}"


def iter_transcript_rows(expression_path: Path, sample_count: int):
    with gzip.open(expression_path, "rt", encoding="utf-8", errors="replace") as handle:
        handle.readline()
        for line_number, line in enumerate(handle, start=2):
            try:
                _transcript_id, gene_id, rest = line.split("\t", 2)
            except ValueError as exc:
                raise ValueError(f"Malformed row {line_number} in {expression_path}") from exc
            values = np.fromstring(rest, sep="\t", dtype=np.float32)
            if values.size != sample_count:
                raise ValueError(
                    f"Row {line_number} has {values.size} TPM values, expected {sample_count}"
                )
            yield line_number, gene_id, values


def write_gene_row(
    body_handle,
    name: str,
    gene_stable: str,
    values: np.ndarray,
    tissue_groups: Dict[str, np.ndarray],
    gene_symbols: Dict[str, str],
) -> None:
    symbol = gene_symbols.get(gene_stable) or gene_stable
    medians = [format_tpm(float(np.median(values[indices]))) for indices in tissue_groups.values()]
    body_handle.write(name)
    body_handle.write("\t")
    body_handle.write(symbol)
    body_handle.write("\t")
    body_handle.write("\t".join(medians))
    body_handle.write("\n")


def build_gct(source_dir: Path, data_dir: Path, output_path: Path, force: bool) -> Dict[str, object]:
    expression_path = source_dir / "expression" / TRANSCRIPT_TPM_NAME
    metadata_path = source_dir / "metadata" / SAMPLE_METADATA_NAME
    if not expression_path.exists():
        raise FileNotFoundError(expression_path)
    if not metadata_path.exists():
        raise FileNotFoundError(metadata_path)

    data_dir.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.stat().st_size > 0 and not force:
        log(f"GTEx v11 GCT already exists: {output_path}")
        return {"output": str(output_path), "skipped": True}

    samples = read_expression_samples(expression_path)
    tissues, tissue_groups = load_sample_tissues(metadata_path, samples)
    gene_symbols = load_gene_symbols(data_dir)
    log(f"Loaded {len(samples)} samples across {len(tissues)} tissues")
    log(f"Loaded {len(gene_symbols)} Ensembl gene -> symbol mappings")

    body_path = output_path.with_suffix(output_path.suffix + ".body.tmp")
    tmp_output_path = output_path.with_suffix(output_path.suffix + ".tmp")

    rows = 0
    current_name = ""
    current_stable = ""
    current_values = None
    start = time.time()

    with body_path.open("w", encoding="utf-8") as body_handle:
        for line_number, gene_id, values in iter_transcript_rows(expression_path, len(samples)):
            gene_stable = stable_gene_id(gene_id)
            if current_values is None:
                current_name = gene_id
                current_stable = gene_stable
                current_values = values.copy()
                continue

            if gene_stable == current_stable:
                current_values += values
                continue

            write_gene_row(body_handle, current_name, current_stable, current_values, tissue_groups, gene_symbols)
            rows += 1
            if rows % 1000 == 0:
                elapsed = time.time() - start
                log(f"Processed {rows} genes through input row {line_number} ({elapsed:.1f}s)")

            current_name = gene_id
            current_stable = gene_stable
            current_values = values.copy()

        if current_values is not None:
            write_gene_row(body_handle, current_name, current_stable, current_values, tissue_groups, gene_symbols)
            rows += 1

    with gzip.open(tmp_output_path, "wt", encoding="utf-8") as output_handle:
        output_handle.write("#1.2\n")
        output_handle.write(f"{rows}\t{len(tissues)}\n")
        output_handle.write("Name\tDescription\t")
        output_handle.write("\t".join(tissues))
        output_handle.write("\n")
        with body_path.open(encoding="utf-8") as body_handle:
            shutil.copyfileobj(body_handle, output_handle)

    os.replace(tmp_output_path, output_path)
    body_path.unlink(missing_ok=True)

    metadata_copy_path = data_dir / SAMPLE_METADATA_NAME
    if not metadata_copy_path.exists() or metadata_copy_path.stat().st_size != metadata_path.stat().st_size:
        shutil.copy2(metadata_path, metadata_copy_path)

    manifest = {
        "source_expression": str(expression_path),
        "source_metadata": str(metadata_path),
        "output": str(output_path),
        "sample_count": len(samples),
        "tissue_count": len(tissues),
        "gene_count": rows,
        "tissues": tissues,
        "created_at_epoch": int(time.time()),
    }
    manifest_path = data_dir / MANIFEST_NAME
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=True)

    log(f"Wrote {rows} genes x {len(tissues)} tissues: {output_path}")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = args.output or (args.data_dir / OUTPUT_NAME)
    manifest = build_gct(args.source_dir, args.data_dir, output_path, args.force)
    print(json.dumps(manifest, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
