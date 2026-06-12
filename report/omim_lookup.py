from __future__ import annotations

import json
import os
import re
import sqlite3
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OMIM_DB = PROJECT_ROOT / "data" / "omim" / "omim_20250411.sqlite3"
GENE_FUNCTION_MAX_LEN = 2000

INHERITANCE_LABELS = {
    "AD": "Autosomal dominant",
    "AR": "Autosomal recessive",
    "XL": "X-linked",
    "XLD": "X-linked dominant",
    "XLR": "X-linked recessive",
    "YL": "Y-linked",
    "MT": "Mitochondrial",
    "IC": "Isolated cases",
    "Mi": "Microdeletion",
    "Mu": "Multifactorial",
    "PD": "Pseudoautosomal dominant",
    "PR": "Pseudoautosomal recessive",
    "SMU": "Somatic mutation",
    "SMo": "Somatic mosaicism",
    "DD": "Digenic dominant",
    "DR": "Digenic recessive",
    "?": "Unknown",
}


def omim_enabled() -> bool:
    return os.getenv("OMIM_ENABLED", "1").lower() in ("1", "true", "yes")


def get_omim_db_path() -> Path:
    configured = os.getenv("OMIM_DB_PATH", "").strip()
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path
    return DEFAULT_OMIM_DB


def _truncate_text(text: str, *, max_len: int = GENE_FUNCTION_MAX_LEN) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."


def _inheritance_label(code: str) -> str:
    code = (code or "").strip()
    if not code:
        return ""
    return INHERITANCE_LABELS.get(code, code)


def _parse_json_field(raw: str | None) -> list[dict]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def _clean_phenotype_name(name: str) -> str:
    cleaned = name.strip()
    if cleaned.startswith("?"):
        cleaned = cleaned[1:].strip()
    return cleaned


def _format_inheritance_mode(gene_map_raw: str | None, phenotype_map_raw: str | None) -> str:
    rows = _parse_json_field(gene_map_raw) or _parse_json_field(phenotype_map_raw)
    if not rows:
        return "-"

    parts: list[str] = []
    seen: set[str] = set()
    for row in rows:
        phenotype = _clean_phenotype_name(
            str(
                row.get("Phenotype View")
                or row.get("Phenotype")
                or row.get("Phenotype MIM number")
                or ""
            )
        )
        inheritance = _inheritance_label(str(row.get("Inheritance") or ""))
        if phenotype and inheritance:
            item = f"{phenotype} ({inheritance})"
        elif inheritance:
            item = inheritance
        elif phenotype:
            item = phenotype
        else:
            continue
        if item not in seen:
            seen.add(item)
            parts.append(item)
    return "; ".join(parts) if parts else "-"


def _select_gene_function(gene_function: str | None, description: str | None) -> str:
    if gene_function and gene_function.strip():
        return _truncate_text(gene_function)
    if description and description.strip():
        return _truncate_text(description)
    return "-"


@lru_cache(maxsize=1)
def _get_connection() -> sqlite3.Connection:
    db_path = get_omim_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"OMIM database not found: {db_path}")
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def query_omim_gene(gene_symbol: str) -> dict | None:
    symbol = gene_symbol.strip().upper()
    if not symbol:
        return None

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT mim_number, prefix, title, mim_type, hgnc_gene_symbol,
               description, geneFunction, inheritance, geneMap, phenotypeMap
        FROM omim
        WHERE mim_type = 'gene'
          AND (
            UPPER(TRIM(hgnc_gene_symbol)) = ?
            OR UPPER(TRIM(hgnc_approved_gene_symbol)) = ?
          )
        ORDER BY CASE WHEN prefix = '*' THEN 0 ELSE 1 END, mim_number
        LIMIT 1
        """,
        (symbol, symbol),
    )
    row = cursor.fetchone()
    if row is None:
        return None

    record = dict(row)
    linked_phenotypes = _parse_json_field(record.get("geneMap")) or _parse_json_field(
        record.get("phenotypeMap")
    )
    return {
        "gene_symbol": gene_symbol.strip(),
        "mim_number": record.get("mim_number") or "",
        "title": (record.get("title") or "").strip(),
        "gene_function": _select_gene_function(
            record.get("geneFunction"),
            record.get("description"),
        ),
        "inheritance_mode": _format_inheritance_mode(
            record.get("geneMap"),
            record.get("phenotypeMap"),
        ),
        "linked_phenotypes": [
            {
                "phenotype": _clean_phenotype_name(
                    str(
                        item.get("Phenotype View")
                        or item.get("Phenotype")
                        or ""
                    )
                ),
                "phenotype_mim_number": str(item.get("Phenotype MIM number") or ""),
                "inheritance": _inheritance_label(str(item.get("Inheritance") or "")),
            }
            for item in linked_phenotypes
        ],
    }


def lookup_omim_gene_function(gene_symbol: str) -> str:
    if not omim_enabled():
        return "-"
    try:
        result = query_omim_gene(gene_symbol)
        return result["gene_function"] if result else "-"
    except Exception:
        return "-"


def lookup_omim_inheritance_mode(gene_symbol: str) -> str:
    if not omim_enabled():
        return "-"
    try:
        result = query_omim_gene(gene_symbol)
        return result["inheritance_mode"] if result else "-"
    except Exception:
        return "-"
