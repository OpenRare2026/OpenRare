#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

export PYTHONPATH="${PROJECT_DIR}/app${PYTHONPATH:+:${PYTHONPATH}}"
export RARE_PPI_DATA_DIR="${RARE_PPI_DATA_DIR:-../../data}"
export RARE_PPI_CACHE_DIR="${RARE_PPI_CACHE_DIR:-${RARE_PPI_DATA_DIR}/cache}"
export RARE_PPI_OUTPUT_DIR="${RARE_PPI_OUTPUT_DIR:-output}"
export RARE_PPI_UPLOAD_DIR="${RARE_PPI_UPLOAD_DIR:-uploads}"
export RARE_PPI_RESPONSE_PATH_BASE="${RARE_PPI_RESPONSE_PATH_BASE:-$PROJECT_DIR}"

mkdir -p "$RARE_PPI_OUTPUT_DIR" "$RARE_PPI_UPLOAD_DIR"

exec python -m uvicorn app.api:app \
  --host "${RARE_PPI_HOST:-0.0.0.0}" \
  --port "${RARE_PPI_PORT:-9000}"
