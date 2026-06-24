from __future__ import annotations

from report.models import ReportContext
from report.open_targets_lookup import lookup_main_associated_phenotype, open_targets_enabled


async def attach_open_targets_phenotypes(context: ReportContext) -> ReportContext:
    if not open_targets_enabled():
        return context

    phenotype_by_gene: dict[str, str] = {}
    for card in context.gene_cards:
        phenotype = await lookup_main_associated_phenotype(card.gene_symbol)
        phenotype_by_gene[card.gene_symbol] = phenotype
        card.main_associated_phenotype = phenotype

    for item in context.summary.top_genes:
        item.main_associated_phenotype = phenotype_by_gene.get(item.gene, "-")

    return context
