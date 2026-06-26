#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

PORT="${RARE_PPI_PORT:-9000}"
BASE_URL="${RARE_PPI_BASE_URL:-http://127.0.0.1:${PORT}}"
REQUEST_JSON="${1:?usage: scripts/curl_score.sh score_request.json}"
mkdir -p tests/outputs

curl -fsS -X POST "${BASE_URL}/score" \
  -H "Content-Type: application/json" \
  --data-binary @"${REQUEST_JSON}" \
  | tee tests/outputs/score_response.json

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

"$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path

payload = json.load(open("tests/outputs/score_response.json", encoding="utf-8"))
assert payload["status"] == "completion", payload
assert payload["count"] == 3, payload
csv_path = Path(payload["csv_path"])
assert not csv_path.is_absolute(), payload
assert csv_path.exists(), f"CSV not found: {csv_path}"
print(f"score ok: {csv_path}")
PY
