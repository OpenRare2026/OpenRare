"""LangChain tools backed by local ClinPGx/PharmGKB data."""

from __future__ import annotations

import json

from langchain_core.tools import tool

from tools.clinpgx_local import get_clinpgx_store


@tool
def get_gene_pgx_profile(
    gene_symbol: str,
    include_low_evidence: bool = False,
    include_pathways: bool = True,
) -> str:
    """Query local ClinPGx data for pharmacogenomic effects of a gene on drugs.

    Returns a drug-centric summary: guideline recommendations, evidence levels,
    effect types (dosage/efficacy/toxicity/metabolism), allele-specific effects,
    and related metabolic pathways.

    Args:
        gene_symbol: HGNC gene symbol, e.g. CYP2D6, TPMT, CYP2C19.
        include_low_evidence: If False (default), only return drugs with clinical
            guidelines or high evidence (1A/1B). If True, include all curated drugs.
        include_pathways: Include PK/PD pathway names where the gene participates.
    """
    store = get_clinpgx_store()
    profile = store.build_gene_pgx_profile(
        gene_symbol,
        include_low_evidence=include_low_evidence,
        include_pathways=include_pathways,
    )
    return json.dumps(profile, ensure_ascii=False, indent=2)


def get_clinpgx_tools() -> list:
    return [get_gene_pgx_profile]
