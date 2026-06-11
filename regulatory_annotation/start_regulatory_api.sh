#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

if ! python3 - <<'PY' >/dev/null 2>&1
import fastapi, uvicorn
PY
then
  python3 -m pip install --user -r requirements.txt
fi

export PATH="$HOME/.local/bin:$PATH"
export REG_API_BASE_WORKDIR="${REG_API_BASE_WORKDIR:-$(dirname "$script_dir")}"
export REG_API_PROJECT_DIR="${REG_API_PROJECT_DIR:-$script_dir}"
export REG_API_HOST="${REG_API_HOST:-0.0.0.0}"
export REG_API_PORT="${REG_API_PORT:-10086}"

exec python3 -m uvicorn regulatory_annotation_api:app --host "$REG_API_HOST" --port "$REG_API_PORT"
