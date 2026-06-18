#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-18081}"

echo "[$(date '+%F %T')] Starting OpenRare V3 Pipeline API on ${HOST}:${PORT}"
exec python3 -m uvicorn backend.main:app --host "$HOST" --port "$PORT" --reload
