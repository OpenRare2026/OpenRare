from __future__ import annotations

from pathlib import Path

from report.drug_recommendations import attach_drug_recommendations
from report.enrich import enrich_report_context
from report.manifest import load_manifest
from report.merge import write_report_outputs
from report.models import ReportContext
from report.output import ReportOutputPaths, resolve_output_paths
from report.gene_function_enrich import attach_gene_function_info
from report.omim_enrich import attach_omim_inheritance_info
from report.pathways import attach_reactome_pathways
from report.phenotypes import attach_open_targets_phenotypes
from report.wide_table import build_report_context


async def generate_report(
    manifest_path: str | Path,
    *,
    row_index: int = 0,
    top_n: int = 5,
    with_agent: bool = True,
    output_dir: str | Path | None = None,
    report_md: str | Path | None = None,
    context_json: str | Path | None = None,
) -> tuple[ReportContext, ReportOutputPaths]:
    meta = load_manifest(manifest_path, row_index=row_index)
    paths = resolve_output_paths(
        meta.sample_id,
        output_dir=output_dir,
        report_md=report_md,
        context_json=context_json,
        with_agent=with_agent,
    )

    context = build_report_context(meta, top_n=top_n)
    context = attach_reactome_pathways(context)
    context = await attach_open_targets_phenotypes(context)
    context = attach_gene_function_info(context)
    context = attach_omim_inheritance_info(context)
    context = await attach_drug_recommendations(context)
    pre_agent_context = context.model_copy(deep=True) if with_agent else None

    if with_agent:
        context = await enrich_report_context(context)

    write_report_outputs(
        context,
        paths,
        meta=meta,
        pre_agent_context=pre_agent_context,
    )
    return context, paths
