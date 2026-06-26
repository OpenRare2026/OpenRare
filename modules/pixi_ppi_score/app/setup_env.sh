#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_DIR="${RARE_PPI_ENV_DIR:-${PROJECT_DIR}/ppi_env}"
REQUIREMENTS="${SCRIPT_DIR}/requirements.txt"
PYTHON_BIN="${ENV_DIR}/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  python3 -m venv --without-pip "$ENV_DIR"
fi

if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
  tmp_get_pip="$(mktemp)"
  trap 'rm -f "$tmp_get_pip"' EXIT
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o "$tmp_get_pip"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$tmp_get_pip" https://bootstrap.pypa.io/get-pip.py
  else
    echo "[ERROR] pip is missing in ${ENV_DIR}, and neither curl nor wget is available." >&2
    exit 1
  fi
  "$PYTHON_BIN" "$tmp_get_pip"
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r "$REQUIREMENTS"
echo "Use: source ${ENV_DIR}/bin/activate"
