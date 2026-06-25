"""CLI entry for the OpenRare full pipeline.

Usage:
    pixi run pipeline-full --vcf sample.vcf --text "症状描述"
    python -m pipeline.main --vcf sample.vcf --text "症状描述"
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from pipeline.runner import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="OpenRare Rare Disease Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pipeline.main -v sample.vcf -t "肌无力、运动发育迟缓"
  pixi run pipeline-full --vcf sample.vcf --text "AML with FLT3-ITD"
        """,
    )
    parser.add_argument("-v", "--vcf", required=True, dest="vcf_path", help="Input VCF file path")
    parser.add_argument("-t", "--text", required=True, dest="symptom_text", help="Patient symptom description")
    parser.add_argument("-o", "--output", dest="output_dir", default=None, help="Output directory")
    args = parser.parse_args()

    if not Path(args.vcf_path).exists():
        print(f"ERROR: VCF file not found: {args.vcf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        asyncio.run(run_pipeline(
            vcf_path=args.vcf_path,
            symptom_text=args.symptom_text,
            output_dir=args.output_dir,
        ))
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"\nPipeline failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
