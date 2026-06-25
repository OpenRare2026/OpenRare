from __future__ import annotations

import json
import os

from dotenv import load_dotenv

load_dotenv()


def open_targets_enabled() -> bool:
    return os.getenv("OPEN_TARGETS_ENABLED", "1").lower() in ("1", "true", "yes")


def _format_disease_names(rows: list[dict], *, max_names: int = 2) -> str:
    scored: list[tuple[float, str]] = []
    for row in rows:
        disease = row.get("disease") or {}
        name = (disease.get("name") or "").strip()
        if not name:
            continue
        score = row.get("score")
        try:
            numeric_score = float(score) if score is not None else 0.0
        except (TypeError, ValueError):
            numeric_score = 0.0
        scored.append((numeric_score, name))

    if not scored:
        return "-"

    scored.sort(key=lambda item: item[0], reverse=True)
    names: list[str] = []
    for _, name in scored:
        if name not in names:
            names.append(name)
        if len(names) >= max_names:
            break
    return "; ".join(names)


async def lookup_main_associated_phenotype(gene_symbol: str, *, limit: int = 5) -> str:
    """Resolve top Open Targets disease association(s) for a gene symbol."""
    if not open_targets_enabled():
        return "-"

    from agent.open_targets_tools import get_gene_disease_associations, lookup_gene

    try:
        lookup_raw = await lookup_gene.ainvoke({"gene_symbol": gene_symbol.strip()})
        if lookup_raw.startswith("No target found"):
            return "-"

        lookup_data = json.loads(lookup_raw)
        ensembl_id = lookup_data.get("ensembl_id")
        if not ensembl_id:
            return "-"

        assoc_raw = await get_gene_disease_associations.ainvoke(
            {"ensembl_id": ensembl_id, "limit": limit}
        )
        if assoc_raw.startswith("No target data") or assoc_raw.startswith("Invalid Ensembl"):
            return "-"

        assoc_data = json.loads(assoc_raw)
        rows = (assoc_data.get("associatedDiseases") or {}).get("rows") or []
        return _format_disease_names(rows)
    except Exception:
        return "-"
