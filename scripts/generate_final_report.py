#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from report.pipeline import generate_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate final genome variant analysis report from test manifest and wide table.",
    )
    parser.add_argument(
        "--manifest",
        default="test_data/test_case/test1.csv",
        help="Test case manifest CSV (test1.csv format).",
    )
    parser.add_argument(
        "--row-index",
        type=int,
        default=0,
        help="Zero-based row index in manifest CSV.",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--output-dir",
        help=(
            "Output directory for all artifacts: meta.json, context.json, "
            "context.pre_agent.json, report.md."
        ),
    )
    parser.add_argument(
        "--output",
        help="Final report Markdown path (default: test_data/output/<sample_id>_final_report.md).",
    )
    parser.add_argument(
        "--json-snapshot",
        help="ReportContext JSON path (default: sibling of --output as *.context.json).",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top genes to include.",
    )
    return parser


def _resolve_path(path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = PROJECT_ROOT / resolved
    return resolved


async def _main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    manifest_path = _resolve_path(args.manifest)

    output_dir = _resolve_path(args.output_dir) if args.output_dir else None
    report_md = _resolve_path(args.output) if args.output else None
    context_json = _resolve_path(args.json_snapshot) if args.json_snapshot else None

    if output_dir is None and report_md is None:
        from report.manifest import load_manifest

        meta = load_manifest(manifest_path, row_index=args.row_index)
        report_md = PROJECT_ROOT / "test_data" / "output" / f"{meta.sample_id}_final_report.md"

    context, paths = await generate_report(
        manifest_path,
        row_index=args.row_index,
        top_n=args.top_n,
        with_agent=True,
        output_dir=output_dir,
        report_md=report_md,
        context_json=context_json,
    )

    print("Wrote outputs:")
    for path in paths.all_written_paths():
        print(f"  - {path}")

    print(
        f"Top genes: {', '.join(card.gene_symbol for card in context.gene_cards)} "
        f"({context.summary.total_variants} variants, {context.summary.total_genes} genes)"
    )
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
