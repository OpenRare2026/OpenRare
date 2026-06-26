from __future__ import annotations

import csv
from pathlib import Path


def format_ppi_score(value: str | None) -> str:
    text = (value or "").strip()
    if not text or text == "-":
        return "-"
    try:
        return f"{float(text):.4f}"
    except ValueError:
        return "-"


def load_ppi_lookup(path: str | Path) -> dict[str, str]:
    """Load gene -> PPI score from a CSV with ``gene`` and ``ppi_final`` columns."""
    ppi_path = Path(path)
    lookup: dict[str, str] = {}
    with ppi_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            gene = (row.get("gene") or "").strip()
            if not gene:
                continue
            formatted = format_ppi_score(row.get("ppi_final"))
            if formatted != "-":
                lookup[gene] = formatted
    return lookup


def resolve_gene_ppi_score(
    gene_symbol: str,
    variants: list,
    *,
    ppi_lookup: dict[str, str] | None = None,
) -> str:
    if ppi_lookup:
        score = ppi_lookup.get(gene_symbol)
        if score:
            return score

    best: float | None = None
    for variant in variants:
        text = getattr(variant, "ppi_final", "-")
        if not text or text == "-":
            continue
        try:
            value = float(text)
        except ValueError:
            continue
        if best is None or value > best:
            best = value

    if best is None:
        return "-"
    return f"{best:.4f}"
