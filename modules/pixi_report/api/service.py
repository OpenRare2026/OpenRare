from __future__ import annotations

import logging
import re
import uuid
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from api.meta_adapter import build_sample_meta
from api.wide_table_limited import load_wide_table_rows_limited
from report.drug_recommendations import attach_drug_recommendations
from report.enrich import enrich_clinical_advice, enrich_gene_narrative
from report.gene_function_enrich import attach_gene_function_info
from report.merge import write_report_outputs
from report.models import GeneNarrative, ReportContext, ReportNarrative
from report.omim_enrich import attach_omim_inheritance_info
from report.output import resolve_output_paths
from report.pathways import attach_reactome_pathways
from report.phenotypes import attach_open_targets_phenotypes
from report.ppi_lookup import load_ppi_lookup
from report.wide_table import build_gene_cards, select_variants

from agent.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

OUTPUT_ROOT = PROJECT_ROOT / "test_data" / "output"
WIDE_TABLE_MAX_ROWS = 10000
_SECTION_HEADER = re.compile(r"^##\s+")


def split_report_sections(markdown: str) -> list[str]:
    """Split rendered report.md into complete top-level sections."""
    sections: list[str] = []
    current: list[str] = []

    for line in markdown.splitlines(keepends=True):
        if _SECTION_HEADER.match(line) and current:
            text = "".join(current).strip()
            if text:
                sections.append(text)
            current = [line]
            continue
        current.append(line)

    text = "".join(current).strip()
    if text:
        sections.append(text)
    return sections


async def stream_report_events(
    *,
    wide_path: str,
    phenotype_path: str,
    hpo_path: str,
    ppi_path: str = "",
    top_n: int = 5,
) -> AsyncIterator[dict[str, Any]]:
    run_id = uuid.uuid4().hex[:12]
    output_dir = OUTPUT_ROOT / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    meta = build_sample_meta(
        wide_path=wide_path,
        phenotype_path=phenotype_path,
        hpo_path=hpo_path,
        ppi_path=ppi_path,
    )
    paths = resolve_output_paths(
        meta.sample_id,
        output_dir=output_dir,
        with_agent=True,
    )

    rows = load_wide_table_rows_limited(meta.wide_table_path, max_rows=WIDE_TABLE_MAX_ROWS)
    variants = select_variants(rows)
    ppi_lookup = load_ppi_lookup(meta.ppi_path) if meta.ppi_path.strip() else None
    gene_cards, summary = build_gene_cards(variants, top_n=top_n, ppi_lookup=ppi_lookup)
    context = ReportContext(
        meta=meta,
        summary=summary,
        gene_cards=gene_cards,
        top_n=top_n,
    )

    genes = [card.gene_symbol for card in context.gene_cards]
    logger.info(
        "[%s] start sample=%s top_n=%d variants=%d genes=%s",
        run_id,
        meta.sample_id,
        top_n,
        summary.total_variants,
        ", ".join(genes),
    )
    yield {"type": "meta", "run_id": run_id, "genes": genes}
    yield {"type": "md", "text": "等待较长时间\n"}
    logger.info("[%s] SSE meta + waiting hint sent; prefetch + agent starting", run_id)

    logger.info("[%s] prefetch: reactome pathways", run_id)
    context = attach_reactome_pathways(context)
    logger.info("[%s] prefetch: open targets phenotypes (MCP)", run_id)
    context = await attach_open_targets_phenotypes(context)
    logger.info("[%s] prefetch: ncbi gene function", run_id)
    context = attach_gene_function_info(context)
    logger.info("[%s] prefetch: omim inheritance", run_id)
    context = attach_omim_inheritance_info(context)
    logger.info("[%s] prefetch: drug recommendations (MCP)", run_id)
    context = await attach_drug_recommendations(context)
    pre_agent_context = context.model_copy(deep=True)
    logger.info("[%s] prefetch done; agent gene narratives starting", run_id)

    narrative = ReportNarrative()
    gene_total = len(context.gene_cards)
    for index, card in enumerate(context.gene_cards, start=1):
        logger.info(
            "[%s] agent gene narrative %d/%d: %s (MCP + LLM)",
            run_id,
            index,
            gene_total,
            card.gene_symbol,
        )
        try:
            gene_narrative = await enrich_gene_narrative(context.meta, card)
        except Exception:
            logger.warning(
                "[%s] agent gene narrative failed: %s; using fallback",
                run_id,
                card.gene_symbol,
            )
            gene_narrative = GeneNarrative(
                gene_function=card.script_gene_function
                if card.script_gene_function not in ("", "-")
                else "Agent 生成失败",
                inheritance_mode=card.omim_inheritance_mode
                if card.omim_inheritance_mode not in ("", "-")
                else "",
                pathway_summary=card.main_pathway if card.main_pathway != "-" else "",
            )
        narrative.gene_narratives[card.gene_symbol] = gene_narrative
        card.narrative = gene_narrative
        logger.info("[%s] agent gene narrative done: %s", run_id, card.gene_symbol)

    logger.info("[%s] agent clinical advice starting (MCP + LLM)", run_id)
    try:
        narrative.clinical_advice = await enrich_clinical_advice(context)
    except Exception:
        logger.warning("[%s] agent clinical advice failed; skipping", run_id)
        narrative.clinical_advice = None
    else:
        logger.info("[%s] agent clinical advice done", run_id)
    context.narrative = narrative

    logger.info("[%s] writing report to %s", run_id, paths.output_dir)
    write_report_outputs(
        context,
        paths,
        meta=meta,
        pre_agent_context=pre_agent_context,
    )

    report_text = paths.report_md.read_text(encoding="utf-8")
    sections = split_report_sections(report_text)
    logger.info("[%s] streaming %d report sections via SSE", run_id, len(sections))
    for section in sections:
        yield {"type": "md", "text": section}

    logger.info("[%s] done md_url=/report/%s/md", run_id, run_id)
    yield {
        "type": "done",
        "md_url": f"/report/{run_id}/md",
    }
