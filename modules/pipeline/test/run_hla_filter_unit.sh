#!/usr/bin/env bash
set -euo pipefail

PIPELINE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FILTER_PY="${PIPELINE_ROOT}/modules/hla_filter/scripts/filter_hla_region_csv.py"
OUT_DIR="${OPENRARE_HLA_FILTER_TEST_OUT:-/tmp/openrare_hla_filter_unit_$(id -un)}"
mkdir -p "$OUT_DIR"

INPUT_CSV="${OUT_DIR}/sample.csv"
OUTPUT_CSV="${OUT_DIR}/filtered.csv"
LOG_JSON="${OUT_DIR}/log.json"

cat >"$INPUT_CSV" <<'EOF'
#CHROM,POS,REF,ALT
6,28477798,G,A
6,33448354,C,T
6,33448355,G,A
1,1000,G,A
EOF

python3 "$FILTER_PY" \
  --input-csv "$INPUT_CSV" \
  --output-csv "$OUTPUT_CSV" \
  --log-json "$LOG_JSON"

rows="$(wc -l < "$OUTPUT_CSV")"
[[ "$rows" -eq 3 ]] || { echo "ERROR: expected 3 lines (header + 2 kept rows), got $rows" >&2; exit 1; }
grep -q '^1,1000' "$OUTPUT_CSV" || { echo "ERROR: non-HLA row missing" >&2; exit 1; }
grep -q '^6,33448355' "$OUTPUT_CSV" || { echo "ERROR: borderline non-HLA chr6 row missing" >&2; exit 1; }
grep -q '^6,28477798' "$OUTPUT_CSV" && { echo "ERROR: HLA rows should be removed" >&2; exit 1; }

printf '[hla-filter-test] OK: %s\n' "$OUTPUT_CSV"
