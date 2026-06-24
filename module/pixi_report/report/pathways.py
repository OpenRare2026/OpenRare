from __future__ import annotations

from report.models import ReportContext
from report.reactome import lookup_main_pathway, reactome_enabled


def attach_reactome_pathways(context: ReportContext) -> ReportContext:
    if not reactome_enabled():
        return context

    pathway_by_gene: dict[str, str] = {}
    for card in context.gene_cards:
        pathway = lookup_main_pathway(card.gene_symbol)
        pathway_by_gene[card.gene_symbol] = pathway
        card.main_pathway = pathway

    for item in context.summary.top_genes:
        item.main_pathway = pathway_by_gene.get(item.gene, "-")

    return context
