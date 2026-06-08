#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${VEP_API_HOST:-0.0.0.0}"
PORT="${VEP_API_PORT:-8000}"

exec python3 -m uvicorn api.main:app --app-dir "$ROOT" --host "$HOST" --port "$PORT"
