#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${RARE_PPI_PYTHON:-${PROJECT_DIR}/ppi_env/bin/python}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "[ERROR] Python environment not found: $PYTHON_BIN" >&2
  echo "[ERROR] Run ${SCRIPT_DIR}/setup_env.sh first, or set RARE_PPI_PYTHON." >&2
  exit 1
fi

cd "$SCRIPT_DIR"
exec "$PYTHON_BIN" -m uvicorn api:app --host "${RARE_PPI_HOST:-0.0.0.0}" --port "${RARE_PPI_PORT:-8000}"
