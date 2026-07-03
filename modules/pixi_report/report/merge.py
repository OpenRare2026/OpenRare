from __future__ import annotations

from pathlib import Path

from report.models import ReportContext, SampleMeta
from report.output import ReportOutputPaths, _write_json
from report.paths import assert_no_absolute_paths_in_text
from report.render import render_report


def _export_model(model: SampleMeta | ReportContext) -> SampleMeta | ReportContext:
    """Re-validate before JSON export so path fields stay module-relative."""
    return type(model).model_validate(model.model_dump())


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
        _write_json(paths.meta_json, _export_model(meta))

    if pre_agent_context is not None and paths.context_pre_agent_json is not None:
        _write_json(paths.context_pre_agent_json, _export_model(pre_agent_context))

    _write_json(paths.context_json, _export_model(context))

    markdown = render_report(context, output_path=paths.report_md.name)
    assert_no_absolute_paths_in_text(markdown)
    paths.report_md.write_text(markdown, encoding="utf-8")

    return paths
