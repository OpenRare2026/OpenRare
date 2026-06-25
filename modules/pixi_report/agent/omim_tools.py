from __future__ import annotations

import json

from langchain_core.tools import tool

from report.omim_lookup import omim_enabled, query_omim_gene


@tool
def lookup_omim_gene(gene_symbol: str) -> str:
    """Look up a gene in local OMIM SQLite for gene function and inheritance mode.

    Returns JSON with fields:
    - mim_number, title
    - gene_function (from OMIM geneFunction, fallback description)
    - inheritance_mode (from OMIM geneMap / phenotypeMap Inheritance codes)
    - linked_phenotypes (structured phenotype list)
    """
    if not omim_enabled():
        return "OMIM lookup is disabled (OMIM_ENABLED=0)."

    symbol = gene_symbol.strip()
    if not symbol:
        return "Gene symbol is required."

    try:
        result = query_omim_gene(symbol)
    except FileNotFoundError as exc:
        return str(exc)
    except Exception as exc:
        return f"OMIM lookup failed for '{symbol}': {exc}"

    if result is None:
        return f"No OMIM gene entry found for '{symbol}'."

    return json.dumps(result, ensure_ascii=False, indent=2)
