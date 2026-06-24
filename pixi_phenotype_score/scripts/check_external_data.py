#!/usr/bin/env python3
"""Check external runtime data without downloading or modifying it."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from path_config import display_path, load_paths  # noqa: E402


def main() -> int:
    paths = load_paths()
    checks = {
        "HPO ontology": paths.hpo_ontology,
        "HPO annotations": paths.hpo_annotations,
        "gene-disease associations": paths.gene_disease_associations,
        "HGNC symbols": paths.hgnc_symbols,
        "MONDO ontology": paths.mondo_ontology,
        "OMIM database": paths.omim_database,
        "Orphanet packets": paths.orphanet_packets,
        "Orphanet index": paths.orphanet_index,
    }
    missing = 0
    for name, path in checks.items():
        exists = path.exists()
        print(f"{'OK' if exists else 'MISSING':7} {name:28} {display_path(path)}")
        missing += int(not exists)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
