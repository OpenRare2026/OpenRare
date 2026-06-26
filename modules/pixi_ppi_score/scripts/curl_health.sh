#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

PORT="${RARE_PPI_PORT:-9000}"
BASE_URL="${RARE_PPI_BASE_URL:-http://127.0.0.1:${PORT}}"
mkdir -p tests/outputs

curl -fsS "${BASE_URL}/health" | tee tests/outputs/health_response.json
python - <<'PY'
import json

payload = json.load(open("tests/outputs/health_response.json", encoding="utf-8"))
assert payload["status"] == "completion", payload
assert payload["missing_file_count"] == 0, payload
print("health ok")
PY
