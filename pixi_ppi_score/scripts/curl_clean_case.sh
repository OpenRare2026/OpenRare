#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

REQUEST_JSON="${1:?usage: scripts/curl_clean_case.sh clean_case_request.json}"
PORT="${RARE_PPI_PORT:-9000}"
BASE_URL="${RARE_PPI_BASE_URL:-http://127.0.0.1:${PORT}}"
case_name="$(basename "$REQUEST_JSON" _clean_request.json)"
RESPONSE_DIR="tests/outputs/clean_cases/${case_name}"
RESPONSE_JSON="${RESPONSE_DIR}/${case_name}_response.json"
mkdir -p "$RESPONSE_DIR"

curl -fsS -X POST "${BASE_URL}/score/clean-case" \
  -H "Content-Type: application/json" \
  --data-binary @"${REQUEST_JSON}" \
  | tee "${RESPONSE_JSON}"
