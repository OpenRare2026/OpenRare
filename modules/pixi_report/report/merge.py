from __future__ import annotations

from pathlib import Path

from report.models import ReportContext, SampleMeta
from report.output import ReportOutputPaths, _write_json
from report.render import render_report


def write_report_outputs(
    context: ReportContext,
    paths: ReportOutputPaths,
    *,
    meta: SampleMeta | None = None,
    pre_agent_context: ReportContext | None = None,
) -> ReportOutputPaths:
    """Write intermediate JSON snapshots and final Markdown report."""
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    if meta is not None:
        _write_json(paths.meta_json, meta)

    if pre_agent_context is not None and paths.context_pre_agent_json is not None:
        _write_json(paths.context_pre_agent_json, pre_agent_context)

    _write_json(paths.context_json, context)

    markdown = render_report(context, output_path=str(paths.report_md.resolve()))
    paths.report_md.write_text(markdown, encoding="utf-8")

    return paths
