#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage: scripts/curl_clean_case_upload.sh phenotype_gene.csv vep_output.csv [hpo_ids.txt] [case_name]

Examples:
  scripts/curl_clean_case_upload.sh input/gene_phenotype_score.csv input/case.vep.csv input/hpo_ids.txt case5
  HPO_IDS="HP:0002352,HP:0002500" scripts/curl_clean_case_upload.sh input/gene_phenotype_score.csv input/case.vep.csv

Environment overrides:
  RARE_PPI_BASE_URL       default: http://127.0.0.1:9000
  RARE_PPI_DATA_DIR       default: ../../data
  CANDIDATE_TOP_N         default: 30000
  VEP_CHUNKSIZE           default: 250000
  OUTPUT_ALL_PPI_FIELDS   default: false
  INCLUDE_NEIGHBORS       default: false
  INCLUDE_EVIDENCE_JSON   default: false
EOF
  exit 2
}

if [ "$#" -lt 2 ]; then
  usage
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

PHENOTYPE_CSV="$1"
VEP_CSV="$2"
HPO_FILE="${3:-}"
CASE_NAME="${4:-upload_case}"

if [ ! -f "$PHENOTYPE_CSV" ]; then
  echo "Phenotype-gene CSV not found: $PHENOTYPE_CSV" >&2
  exit 1
fi

if [ ! -f "$VEP_CSV" ]; then
  echo "VEP CSV not found: $VEP_CSV" >&2
  exit 1
fi

if [ -n "$HPO_FILE" ] && [ ! -f "$HPO_FILE" ]; then
  echo "HPO file not found: $HPO_FILE" >&2
  exit 1
fi

if [ -z "$HPO_FILE" ] && [ -z "${HPO_IDS:-}" ]; then
  echo "Provide an HPO file as the third argument or set HPO_IDS." >&2
  usage
fi

PORT="${RARE_PPI_PORT:-9000}"
BASE_URL="${RARE_PPI_BASE_URL:-http://127.0.0.1:${PORT}}"
DATA_DIR="${RARE_PPI_DATA_DIR:-../../data}"
RESPONSE_DIR="tests/outputs/upload_cases/${CASE_NAME}"
RESPONSE_JSON_DIR="tests/outputs/upload_responses"
RESPONSE_JSON="${RESPONSE_JSON_DIR}/${CASE_NAME}_response.json"
mkdir -p "$RESPONSE_DIR" "$RESPONSE_JSON_DIR"

curl_args=(
  -fsS
  -X POST
  "${BASE_URL}/score/clean-case/upload"
  -F "phenotype_gene_csv=@${PHENOTYPE_CSV}"
  -F "vep_output_csv=@${VEP_CSV}"
  -F "data_dir=${DATA_DIR}"
  -F "output_csv=${RESPONSE_DIR}/${CASE_NAME}_final_score.csv"
  -F "ppi_output_csv=${RESPONSE_DIR}/${CASE_NAME}_ppi_score.csv"
  -F "clean_output_dir=true"
  -F "candidate_top_n=${CANDIDATE_TOP_N:-30000}"
  -F "vep_chunksize=${VEP_CHUNKSIZE:-250000}"
  -F "output_all_ppi_fields=${OUTPUT_ALL_PPI_FIELDS:-false}"
  -F "include_neighbors=${INCLUDE_NEIGHBORS:-false}"
  -F "include_evidence_json=${INCLUDE_EVIDENCE_JSON:-false}"
)

if [ -n "$HPO_FILE" ]; then
  curl_args+=(-F "hpo_file=@${HPO_FILE}")
else
  curl_args+=(-F "hpo_ids=${HPO_IDS}")
fi

curl "${curl_args[@]}" | tee "$RESPONSE_JSON"

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  fi
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "python/python3 not found; skipped local response validation." >&2
  exit 0
fi

"$PYTHON_BIN" - "$RESPONSE_JSON" <<'PY'
import json
import sys
from pathlib import Path

payload = json.load(open(sys.argv[1], encoding="utf-8"))
assert payload["status"] == "completion", payload
for key in ("csv_path", "ppi_csv_path"):
    path = Path(payload[key])
    assert not path.is_absolute(), payload
    assert path.exists(), f"{key} not found: {path}"
print(f"upload clean-case ok: {payload['csv_path']}")
PY
