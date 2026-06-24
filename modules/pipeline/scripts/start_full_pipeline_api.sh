#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${FULL_PIPELINE_API_HOST:-0.0.0.0}"
PORT="${FULL_PIPELINE_API_PORT:-18901}"
cd "$ROOT"
exec python3 -m uvicorn complete_pipeline.full_pipeline_api:app --host "$HOST" --port "$PORT"
