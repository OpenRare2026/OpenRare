from __future__ import annotations

from report.models import ReportContext
from report.omim_lookup import lookup_omim_gene_function, lookup_omim_inheritance_mode, omim_enabled


def attach_omim_gene_info(context: ReportContext) -> ReportContext:
    if not omim_enabled():
        return context

    for card in context.gene_cards:
        card.omim_gene_function = lookup_omim_gene_function(card.gene_symbol)
        card.omim_inheritance_mode = lookup_omim_inheritance_mode(card.gene_symbol)

    return context
