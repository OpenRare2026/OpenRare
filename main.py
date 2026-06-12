import argparse
import asyncio
import json
import sys
from pathlib import Path

from agent.factory import build_agent
from agent.report import build_report

DEFAULT_QUERY = "BRCA2 与乳腺癌的靶点关联和相关文献"


async def run(query: str, output_format: str, json_path: Path | None) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Gene search agent")
    parser.add_argument(
        "query",
        nargs="?",
        default=DEFAULT_QUERY,
        help="Research question (default: BRCA2 example query)",
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
        help="Write JSON report to file (implies --format json if only -o is given)",
    )
    args = parser.parse_args()

    output_format = args.format
    if args.output and args.format == "both":
        output_format = "both"

    try:
        asyncio.run(run(args.query, output_format, args.output))
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
