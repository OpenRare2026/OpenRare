#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

if ! python3 - <<'PY' >/dev/null 2>&1
import fastapi, uvicorn
PY
then
  python3 -m pip install --user -r regulatory_annotation/requirements.txt
fi

export PATH="$HOME/.local/bin:$PATH"
export PREPROCESS_API_BASE_WORKDIR="${PREPROCESS_API_BASE_WORKDIR:-$(dirname "$script_dir")}"
export PREPROCESS_API_PROJECT_DIR="${PREPROCESS_API_PROJECT_DIR:-$script_dir}"
export PREPROCESS_API_HOST="${PREPROCESS_API_HOST:-0.0.0.0}"
export PREPROCESS_API_PORT="${PREPROCESS_API_PORT:-10087}"

exec python3 -m uvicorn preprocessing_api:app --host "$PREPROCESS_API_HOST" --port "$PREPROCESS_API_PORT"
