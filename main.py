import argparse
import asyncio
import json
import sys
from pathlib import Path

from agent.factory import build_agent
from agent.report import build_report
from agent.schemas import GeneDiseaseResearchInput
from agent.workflow import run_workflow

DEFAULT_QUERY = "BRCA2 与乳腺癌的靶点关联和相关文献"


async def run_query(query: str, output_format: str, json_path: Path | None) -> None:
    agent = await build_agent()
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]},
    )

    report = build_report(query, result)
    report_json = report.model_dump(mode="json")

    if output_format in ("text", "both"):
        print(report.summary or result["messages"][-1].content)

    if output_format in ("json", "both"):
        serialized = json.dumps(report_json, ensure_ascii=False, indent=2)
        if json_path:
            json_path.write_text(serialized + "\n", encoding="utf-8")
            if output_format == "json":
                print(f"Wrote structured report to {json_path}", file=sys.stderr)
        elif output_format == "json":
            print(serialized)
        else:
            print("\n--- structured report (JSON) ---")
            print(serialized)


async def run_structured(
    gene: str,
    mondo_ids: list[str],
    output_format: str,
    json_path: Path | None,
) -> None:
    workflow_input = GeneDiseaseResearchInput(
        gene_symbol=gene,
        mondo_ids=mondo_ids,
    )
    report = await run_workflow(workflow_input)
    report_json = report.model_dump(mode="json")

    if output_format in ("text", "both"):
        print(report.summary)

    if output_format in ("json", "both"):
        serialized = json.dumps(report_json, ensure_ascii=False, indent=2)
        if json_path:
            json_path.write_text(serialized + "\n", encoding="utf-8")
            if output_format == "json":
                print(f"Wrote structured report to {json_path}", file=sys.stderr)
        elif output_format == "json":
            print(serialized)
        else:
            print("\n--- structured report (JSON) ---")
            print(serialized)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gene search agent")
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Research question (free-text mode)",
    )
    parser.add_argument(
        "--gene",
        help="Gene symbol for structured workflow mode (e.g. CFTR)",
    )
    parser.add_argument(
        "--mondo-ids",
        nargs="+",
        default=[],
        help="MONDO disease IDs for structured workflow (e.g. MONDO_0009061)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "both"],
        default="both",
        help="Output format: text summary, sourced JSON, or both (default: both)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write JSON report to file",
    )
    args = parser.parse_args()

    output_format = args.format
    if args.output and args.format == "both":
        output_format = "both"

    try:
        if args.gene:
            asyncio.run(
                run_structured(args.gene, args.mondo_ids, output_format, args.output)
            )
        else:
            query = args.query or DEFAULT_QUERY
            asyncio.run(run_query(query, output_format, args.output))
    except KeyError as exc:
        missing = exc.args[0]
        print(
            f"Missing required environment variable: {missing}\n"
            "Copy .env.example to .env and fill in LLM_BASE_URL, "
            "LLM_API_KEY, and LLM_MODEL.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
