#!/usr/bin/env bash
# Verify VEP plugin data files and indexes expected by vep_runner_config.json.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENRARE_REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
# shellcheck source=../../config/paths.sh
source "${OPENRARE_REPO_ROOT}/pipline_V3/config/paths.sh"

CONFIG="${OPENRARE_VEP_CONFIG:-${OPENRARE_PIPELINE_V3_ROOT}/modules/vep_runner/config/vep_runner_config.json}"
export OPENRARE_DATA_ROOT

python3 - <<'PY' "$CONFIG" "$OPENRARE_REPO_ROOT" "$OPENRARE_DATA_ROOT"
import json
import os
import shutil
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
repo_root = Path(sys.argv[2])
data_root = Path(sys.argv[3])

def expand(value: str) -> str:
    return value.replace("${OPENRARE_DATA_ROOT}", str(data_root)).replace(
        "$OPENRARE_DATA_ROOT", str(data_root), 1
    )

def check_file(path: str, label: str) -> list[str]:
    issues = []
    p = Path(path)
    if not p.is_file():
        issues.append(f"MISSING file: {label} -> {p}")
        return issues
    if p.stat().st_size == 0:
        issues.append(f"EMPTY file: {label} -> {p}")
    return issues

def check_dir(path: str, label: str) -> list[str]:
    p = Path(path)
    if not p.is_dir():
        issues.append(f"MISSING dir: {label} -> {p}")
    return []

def check_index(path: str, label: str) -> list[str]:
    p = Path(path)
    if not (Path(str(p) + ".tbi").is_file() or Path(str(p) + ".csi").is_file()):
        issues.append(f"MISSING index (.tbi/.csi): {label} -> {p}")
    return []

with config_path.open() as handle:
    config = json.load(handle)

issues: list[str] = []

vep_bin = shutil.which("vep")
if not vep_bin:
    issues.append("MISSING: vep not found on PATH (run pixi install)")

issues += check_dir(expand(config["cache_dir"]), "cache_dir")
issues += check_file(expand(config.get("fasta", "")), "reference FASTA")
fasta = expand(config.get("fasta", ""))
if fasta:
    issues += check_file(fasta + ".fai", "reference FASTA index")

plugin_dir = expand(config["plugin_dir"])
for pm in ("CADD.pm", "SpliceAI.pm", "AlphaMissense.pm", "dbNSFP.pm"):
    issues += check_file(str(Path(plugin_dir) / pm), f"plugin {pm}")

loftee = config.get("plugins", {}).get("loftee", {})
if loftee.get("enabled"):
    loftee_path = expand(loftee["loftee_path"])
    issues += check_file(str(Path(loftee_path) / "LoF.pm"), "LoFTEE LoF.pm")
    ancestor = loftee.get("human_ancestor_fa", "")
    if ancestor and ancestor != "false":
        issues += check_file(expand(ancestor), "LoFTEE human_ancestor_fa")

plugins = config.get("plugins", {})
for name, key_paths in [
    ("cadd", ["snv", "indels"]),
    ("spliceai", ["snv", "indel"]),
    ("alphamissense", ["file"]),
    ("dbnsfp", ["file"]),
    ("clinvar", ["file"]),
]:
    section = plugins.get(name, {})
    if not section.get("enabled"):
        continue
    for key in key_paths:
        path = expand(section[key])
        issues += check_file(path, f"{name}.{key}")
        if name in {"cadd", "spliceai", "alphamissense", "dbnsfp", "clinvar"}:
            issues += check_index(path, f"{name}.{key}")

if issues:
    print("VEP plugin verification FAILED:\n")
    for item in issues:
        print(f"  - {item}")
    sys.exit(1)

print("VEP plugin verification OK.")
print(f"  repo_root={repo_root}")
print(f"  data_root={data_root}")
print(f"  vep={vep_bin}")
PY
