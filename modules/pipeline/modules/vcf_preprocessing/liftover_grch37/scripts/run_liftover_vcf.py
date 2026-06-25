#!/usr/bin/env python3
"""Run GRCh37/hg19 → GRCh38/hg38 VCF liftover via liftover-runner.jar."""

from __future__ import annotations

import argparse
import json
import gzip
import os
import shutil
import subprocess
import sys
from pathlib import Path

_PIPELINE_ROOT = Path(__file__).resolve().parents[4]
if str(_PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_ROOT))
from config.path_utils import liftover_config_path, liftover_jar_path


def read_vcf_header_lines(vcf_path: Path, limit: int = 500) -> list[str]:
    path = Path(vcf_path)
    opener = gzip.open if str(path).endswith(".gz") else open
    lines: list[str] = []
    with opener(path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("#"):
                lines.append(line.rstrip("\n"))
                if len(lines) >= limit:
                    break
            else:
                break
    return lines


def detect_vcf_assembly(vcf_path: Path) -> str:
    """Return GRCh37, GRCh38, or unknown based on VCF header."""
    header = read_vcf_header_lines(vcf_path)
    reference_tokens: list[str] = []
    for line in header:
        if line.startswith("##reference="):
            reference_tokens.append(line.split("=", 1)[1].strip().lower())
        if line.startswith("##contig=<ID="):
            # Picard liftover cares about contig naming; assembly hint only here.
            continue
    for token in reference_tokens:
        if "grch37" in token or "hg19" in token or "ncbi37" in token:
            return "GRCh37"
        if "grch38" in token or "hg38" in token:
            return "GRCh38"
    return "unknown"


def resolve_java_bin(explicit: str | None) -> str:
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            return str(path.resolve())
        found = shutil.which(explicit)
        if found:
            return found
        raise FileNotFoundError(f"Java executable not found: {explicit}")
    java_bin = os.environ.get("JAVA_BIN", "java")
    found = shutil.which(java_bin)
    if not found and Path(java_bin).is_file():
        return str(Path(java_bin).resolve())
    if not found:
        raise FileNotFoundError("Java executable not found on PATH (set JAVA_BIN)")
    return found


def build_command(
    java_bin: str,
    jar: Path,
    config: Path,
    input_vcf: Path,
    out_dir: Path,
    run_id: str,
    normalize: bool,
    force: bool,
) -> list[str]:
    return [
        java_bin,
        "-jar",
        str(jar),
        "--config",
        str(config),
        "--input",
        str(input_vcf),
        "--out-dir",
        str(out_dir),
        "--run-id",
        run_id,
        "--normalize",
        "true" if normalize else "false",
        "--force",
        "true" if force else "false",
    ]


def final_output_vcf(out_dir: Path, normalize: bool) -> Path:
    if normalize:
        return out_dir / "output" / "output.grch38.norm.vcf.gz"
    return out_dir / "output" / "output.grch38.vcf.gz"


def write_manifest(
    manifest_path: Path,
    *,
    input_vcf: Path,
    out_dir: Path,
    output_vcf: Path,
    summary: dict,
    assembly_detected: str,
) -> None:
    payload = {
        "input_vcf": str(input_vcf),
        "out_dir": str(out_dir),
        "output_vcf": str(output_vcf),
        "assembly_detected": assembly_detected,
        "summary": summary,
        "summary_json": str(out_dir / "summary" / "summary.json"),
        "rejected_vcf": str(out_dir / "rejected" / "rejected.vcf.gz"),
        "liftover_log": str(out_dir / "logs" / "liftover.log"),
        "qc_log": str(out_dir / "logs" / "qc.log"),
    }
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GRCh37/hg19 → GRCh38 VCF liftover (liftover-runner.jar)")
    parser.add_argument("--input", required=True, help="Input GRCh37 VCF/VCF.GZ")
    parser.add_argument("--out-dir", default="", help="Liftover run directory (00_liftover)")
    parser.add_argument("--run-id", default="", help="Run id for jar logs (default: basename of out-dir)")
    parser.add_argument("--config", default="", help="liftover_config.toml (default: LIFTOVER_CONFIG / .env)")
    parser.add_argument("--jar", default="", help="liftover-runner.jar (default: LIFTOVER_JAR / .env)")
    parser.add_argument("--java-bin", default="", help="Java executable (default: JAVA_BIN)")
    parser.add_argument("--normalize", choices=("true", "false"), default="true")
    parser.add_argument("--force", choices=("true", "false"), default="true")
    parser.add_argument("--detect-only", action="store_true", help="Only print detected assembly and exit")
    parser.add_argument("--log-json", default="", help="Write manifest JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_vcf = Path(args.input).expanduser().resolve()
    if not input_vcf.is_file():
        print(f"ERROR: input VCF not found: {input_vcf}", file=sys.stderr)
        return 1

    assembly = detect_vcf_assembly(input_vcf)
    if args.detect_only:
        print(assembly)
        return 0

    if not args.out_dir:
        print("ERROR: --out-dir is required unless --detect-only", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir).expanduser().resolve()

    jar = Path(args.jar).expanduser() if args.jar else liftover_jar_path()
    config = Path(args.config).expanduser() if args.config else liftover_config_path()
    if not jar.is_file():
        print(f"ERROR: liftover jar not found: {jar}", file=sys.stderr)
        return 1
    if not config.is_file():
        print(f"ERROR: liftover config not found: {config}", file=sys.stderr)
        return 1

    normalize = args.normalize == "true"
    force = args.force == "true"
    run_id = args.run_id or out_dir.name
    java_bin = resolve_java_bin(args.java_bin or None)

    out_dir.parent.mkdir(parents=True, exist_ok=True)
    cmd = build_command(java_bin, jar, config, input_vcf, out_dir, run_id, normalize, force)
    print("CMD:", " ".join(cmd))
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        print(f"ERROR: liftover jar failed with returncode={result.returncode}", file=sys.stderr)
        return result.returncode

    output_vcf = final_output_vcf(out_dir, normalize)
    if not output_vcf.is_file():
        print(f"ERROR: expected output VCF missing: {output_vcf}", file=sys.stderr)
        return 1

    summary_path = out_dir / "summary" / "summary.json"
    summary: dict = {}
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

    manifest_path = Path(args.log_json) if args.log_json else out_dir / "liftover.manifest.json"
    write_manifest(
        manifest_path,
        input_vcf=input_vcf,
        out_dir=out_dir,
        output_vcf=output_vcf,
        summary=summary,
        assembly_detected=assembly,
    )
    print(output_vcf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
