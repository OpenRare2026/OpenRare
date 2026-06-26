"""LangChain tools for searching local ChinaDrug and ChiCTR trial registries."""

from __future__ import annotations

import json

from langchain_core.tools import tool

from tools.china_trials_local import get_trial_registry_store


@tool
def search_chinadrug_trials(
    drug_names: str = "",
    gene_symbol: str = "",
    limit: int = 20,
) -> str:
    """Search the ChinaDrug Trials registry for teams running related studies.

    Use after Open Targets drug discovery or when the user provides a gene symbol.
    Matches drug names (Chinese or English) against drug_name, and matches gene
    symbols or disease terms against indication/title/objective.

    Returns matching trial rows with sponsor, principal investigator, institution,
    and ethics committee (team fields).

    Args:
        drug_names: One or more drug names, comma/semicolon separated. Pass names
            from Open Targets (e.g. "伊马替尼, imatinib").
        gene_symbol: HGNC gene symbol from the user query (e.g. CFTR, CYP2D6).
        limit: Maximum number of trial rows to return (default 20).
    """
    store = get_trial_registry_store()
    result = store.search_chinadrug(
        drug_names=drug_names or None,
        gene_symbol=gene_symbol or None,
        limit=limit,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def search_chictr_trials(
    drug_names: str = "",
    gene_symbol: str = "",
    limit: int = 20,
) -> str:
    """Search the ChiCTR registry for teams running related clinical studies.

    Use after Open Targets drug discovery or when the user provides a gene symbol.
    Matches drug names and gene-related terms against public/scientific titles,
    intervention, and ailment fields.

    Returns matching trial rows with applicant, study leader, institution, and
    primary sponsor (team fields).

    Args:
        drug_names: One or more drug names, comma/semicolon separated. Pass names
            from Open Targets (e.g. "伊马替尼, imatinib").
        gene_symbol: HGNC gene symbol from the user query (e.g. CFTR, CYP2D6).
        limit: Maximum number of trial rows to return (default 20).
    """
    store = get_trial_registry_store()
    result = store.search_chictr(
        drug_names=drug_names or None,
        gene_symbol=gene_symbol or None,
        limit=limit,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


def get_china_trials_tools() -> list:
    return [search_chinadrug_trials, search_chictr_trials]
