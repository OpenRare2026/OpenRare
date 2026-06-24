#!/usr/bin/env bash
# Pixi activation: load per-module .env files (repo root = PIXI_PROJECT_ROOT).
set -euo pipefail

_root="${PIXI_PROJECT_ROOT:-.}"

# modules/pipeline — variant annotation pipeline
if [[ -f "${_root}/modules/pipeline/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${_root}/modules/pipeline/.env"
  set +a
fi

# Future modules: add similar blocks, e.g.
# if [[ -f "${_root}/modules/other/.env" ]]; then source ...
