from __future__ import annotations

import os

from report.models import ReportContext
from report.ncbi_gene_lookup import lookup_ncbi_genes, ncbi_gene_enabled
from report.omim_lookup import lookup_omim_gene_function, omim_enabled


def _omim_fallback_enabled() -> bool:
    return os.getenv("GENE_FUNCTION_FALLBACK_OMIM", "1").lower() in ("1", "true", "yes")


def attach_gene_function_info(context: ReportContext) -> ReportContext:
    """Attach gene function text for §3.x.1.

    Primary source: NCBI Gene via Entrez E-utilities (GeneCards 无公开批量 API，
    NCBI Gene summary 为 Entrez 标准基因功能描述).
    Fallback: local OMIM SQLite when NCBI returns empty.
    """
    symbols = [card.gene_symbol for card in context.gene_cards]
    ncbi_records = lookup_ncbi_genes(symbols) if ncbi_gene_enabled() else {}

    for card in context.gene_cards:
        symbol = card.gene_symbol.strip().upper()
        ncbi = ncbi_records.get(symbol)

        if ncbi:
            card.ncbi_gene_id = ncbi.ncbi_gene_id
            card.ncbi_gene_name = ncbi.official_name
            card.ncbi_gene_summary = ncbi.summary
            card.ncbi_gene_url = ncbi.url
            card.script_gene_function = ncbi.summary
            card.script_gene_function_source = "NCBI Gene (Entrez)"
            continue

        card.ncbi_gene_summary = "-"
        if _omim_fallback_enabled() and omim_enabled():
            omim_text = lookup_omim_gene_function(card.gene_symbol)
            card.omim_gene_function = omim_text
            if omim_text not in ("", "-"):
                card.script_gene_function = omim_text
                card.script_gene_function_source = "OMIM"
                continue

        card.script_gene_function = "-"
        card.script_gene_function_source = "-"

    return context
