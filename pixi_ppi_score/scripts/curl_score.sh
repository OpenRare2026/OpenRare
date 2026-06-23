#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

PORT="${RARE_PPI_PORT:-9000}"
BASE_URL="${RARE_PPI_BASE_URL:-http://127.0.0.1:${PORT}}"
mkdir -p tests/outputs

curl -fsS -X POST "${BASE_URL}/score" \
  -H "Content-Type: application/json" \
  --data-binary @tests/inputs/score_request.json \
  | tee tests/outputs/score_response.json

python - <<'PY'
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
