#!/usr/bin/env bash
# Integration test for full_pipeline_api via pixi (.env loaded automatically).
set -euo pipefail

PIPELINE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../config/paths.sh
source "${PIPELINE_ROOT}/config/paths.sh"

API_HOST="${FULL_PIPELINE_API_HOST:-127.0.0.1}"
API_PORT="${FULL_PIPELINE_API_PORT:-18901}"
API_BASE="http://${API_HOST}:${API_PORT}"
SOURCE_VCF="${OPENRARE_API_TEST_VCF:-${OPENRARE_TEST_VCF_P001}}"
CHROMOSOMES="${OPENRARE_API_TEST_CHROMOSOMES:-1}"
FORK="${OPENRARE_API_TEST_FORK:-4}"
POLL_SEC="${OPENRARE_API_TEST_POLL_SEC:-5}"
POLL_MAX="${OPENRARE_API_TEST_POLL_MAX:-120}"
TEST_TMP="${OPENRARE_API_TEST_TMP:-/tmp/openrare_api_integration_$(id -un)}"
API_PID=""
STARTED_API=no
PIPELINE_INPUT_VCF=""
SAMPLE_ID=""

cleanup() {
  if [[ "$STARTED_API" == yes && -n "$API_PID" ]]; then
    kill "$API_PID" 2>/dev/null || true
    wait "$API_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

log() {
  printf '[api-test] %s\n' "$*"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "ERROR: missing command: $1" >&2; exit 1; }
}

prepare_pipeline_input() {
  local chrom_line sample_name
  chrom_line="$(grep -m1 '^#CHROM' "$SOURCE_VCF" || true)"
  if [[ -z "$chrom_line" ]]; then
    echo "ERROR: no #CHROM header in $SOURCE_VCF" >&2
    exit 1
  fi
  if [[ "$chrom_line" == *$'\t'FORMAT$'\t'* ]]; then
    sample_name="${chrom_line##*$'\t'}"
    PIPELINE_INPUT_VCF="$SOURCE_VCF"
    SAMPLE_ID="$sample_name"
    if [[ -n "${OPENRARE_API_TEST_SAMPLE:-}" && "${OPENRARE_API_TEST_SAMPLE}" != "$sample_name" ]]; then
      log "Ignoring OPENRARE_API_TEST_SAMPLE=${OPENRARE_API_TEST_SAMPLE}; VCF sample column is ${sample_name}"
    fi
    log "Using VCF with existing sample: ${SAMPLE_ID}"
    return 0
  fi
  SAMPLE_ID="${OPENRARE_API_TEST_SAMPLE:-SAMPLE}"
  mkdir -p "$TEST_TMP"
  PIPELINE_INPUT_VCF="${TEST_TMP}/${SAMPLE_ID}.with_sample.vcf"
  bash "$PIPELINE_ROOT/test/prepare_sites_vcf_with_sample.sh" \
    "$SOURCE_VCF" "$PIPELINE_INPUT_VCF" "$SAMPLE_ID"
  log "Prepared sites-only VCF with sample ${SAMPLE_ID}"
}

wait_for_health() {
  local i=0
  while (( i < 30 )); do
    if curl -fsS "${API_BASE}/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

start_api_if_needed() {
  if curl -fsS "${API_BASE}/health" >/dev/null 2>&1; then
    log "API already healthy at ${API_BASE}"
    return 0
  fi
  log "Starting API at ${API_BASE} via pixi..."
  (
    cd "$PIPELINE_ROOT"
    FULL_PIPELINE_API_HOST="$API_HOST" FULL_PIPELINE_API_PORT="$API_PORT" \
      pixi run api
  ) &
  API_PID=$!
  STARTED_API=yes
  if ! wait_for_health; then
    echo "ERROR: API failed to become healthy at ${API_BASE}" >&2
    exit 1
  fi
  log "API started (pid=${API_PID})"
}

poll_job() {
  local job_id="$1"
  local i=0
  local status=""
  while (( i < POLL_MAX )); do
    status="$(curl -fsS "${API_BASE}/jobs/${job_id}" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("status",""))')"
    log "job ${job_id} status=${status}"
    case "$status" in
      succeeded) return 0 ;;
      failed)
        curl -fsS "${API_BASE}/jobs/${job_id}/log" | tail -30 >&2 || true
        echo "ERROR: job failed" >&2
        return 1
        ;;
    esac
    sleep "$POLL_SEC"
    i=$((i + 1))
  done
  echo "ERROR: job timed out after $((POLL_MAX * POLL_SEC))s" >&2
  return 1
}

verify_output() {
  local output_dir="$1"
  local sorted="${output_dir}/06_genos_evee_annotation/vep_output.with_genos_evee.csv"
  [[ -s "$sorted" ]] || { echo "ERROR: missing output: $sorted" >&2; return 1; }
  local rows
  rows="$(wc -l < "$sorted")"
  log "OK: ${sorted} (${rows} lines)"
}

run_json_path_test() {
  log "=== POST /run (JSON path) ==="
  local resp job_id output_dir
  resp="$(curl -fsS -X POST "${API_BASE}/run" \
    -H 'Content-Type: application/json' \
    -d "$(python3 - <<EOF
import json
print(json.dumps({
  "input_vcf": "${PIPELINE_INPUT_VCF}",
  "fork": int("${FORK}"),
  "hpo_id": "",
  "sample_id": "${SAMPLE_ID}",
  "chromosomes": "${CHROMOSOMES}",
  "keep_raw_vep": True,
}))
EOF
)")"
  job_id="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["job_id"])' <<<"$resp")"
  output_dir="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["output_dir"])' <<<"$resp")"
  log "submitted job_id=${job_id} output_dir=${output_dir}"
  poll_job "$job_id"
  verify_output "$output_dir"
}

run_upload_test() {
  log "=== POST /run-upload (multipart) ==="
  local resp job_id output_dir
  resp="$(curl -fsS -X POST "${API_BASE}/run-upload" \
    -F "input_vcf=@${PIPELINE_INPUT_VCF}" \
    -F "fork=${FORK}" \
    -F "sample_id=${SAMPLE_ID}" \
    -F "chromosomes=${CHROMOSOMES}" \
    -F "keep_raw_vep=true")"
  job_id="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["job_id"])' <<<"$resp")"
  output_dir="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["output_dir"])' <<<"$resp")"
  log "submitted job_id=${job_id} output_dir=${output_dir}"
  poll_job "$job_id"
  verify_output "$output_dir"
}

main() {
  require_cmd curl
  require_cmd python3
  require_cmd pixi
  [[ -s "$SOURCE_VCF" ]] || { echo "ERROR: source VCF not found: $SOURCE_VCF" >&2; exit 1; }

  prepare_pipeline_input
  start_api_if_needed
  curl -fsS "${API_BASE}/health" | python3 -m json.tool | head -15
  run_json_path_test
  run_upload_test
  log "All API integration checks passed."
}

main "$@"
