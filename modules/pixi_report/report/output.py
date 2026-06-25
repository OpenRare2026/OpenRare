from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from report.models import ReportContext, SampleMeta


@dataclass(frozen=True)
class ReportOutputPaths:
    """Standard paths for intermediate JSON and final Markdown."""

    output_dir: Path
    meta_json: Path
    context_json: Path
    report_md: Path
    context_pre_agent_json: Path | None = None

    def all_written_paths(self) -> list[Path]:
        paths = [self.meta_json, self.context_json, self.report_md]
        if self.context_pre_agent_json is not None:
            paths.append(self.context_pre_agent_json)
        return paths


def resolve_output_paths(
    sample_id: str,
    *,
    output_dir: str | Path | None = None,
    report_md: str | Path | None = None,
    context_json: str | Path | None = None,
    with_agent: bool = True,
) -> ReportOutputPaths:
    """Resolve output file paths from --output-dir or explicit file paths."""
    if output_dir is not None:
        base = Path(output_dir)
        return ReportOutputPaths(
            output_dir=base,
            meta_json=base / "meta.json",
            context_json=base / "context.json",
            report_md=base / "report.md",
            context_pre_agent_json=(base / "context.pre_agent.json") if with_agent else None,
        )

    report_path = Path(report_md or f"{sample_id}_final_report.md")
    context_path = Path(context_json) if context_json else report_path.with_suffix(".context.json")

    return ReportOutputPaths(
        output_dir=report_path.parent,
        meta_json=report_path.with_name(f"{sample_id}.meta.json"),
        context_json=context_path,
        report_md=report_path,
        context_pre_agent_json=(
            report_path.with_name(f"{sample_id}.context.pre_agent.json") if with_agent else None
        ),
    )


def _write_json(path: Path, payload: BaseModel | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, BaseModel):
        data = payload.model_dump(mode="json")
    else:
        data = payload
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
