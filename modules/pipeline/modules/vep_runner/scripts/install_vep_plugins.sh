#!/usr/bin/env bash
# Install VEP cache (optional) and plugin Perl modules for OpenRare pipeline module.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
# shellcheck source=../../../config/paths.sh
source "${PIPELINE_ROOT}/config/paths.sh"

VEP_RELEASE="${OPENRARE_VEP_RELEASE:-115}"
DATA_ROOT="${OPENRARE_DATA_ROOT}"
INSTALL_CACHE="${OPENRARE_VEP_INSTALL_CACHE:-no}"
ASSEMBLY="${OPENRARE_VEP_ASSEMBLY:-GRCh38}"
SPECIES="${OPENRARE_VEP_SPECIES:-homo_sapiens}"

CACHE_DIR="${DATA_ROOT}/vep_cache"
PLUGIN_DIR="${CACHE_DIR}/Plugins"
LOFTEE_DIR="${PLUGIN_DIR}/loftee"
VEP_PLUGINS_BASE="https://raw.githubusercontent.com/Ensembl/VEP_plugins/release/${VEP_RELEASE}"

PLUGIN_PMS=(
  CADD.pm
  SpliceAI.pm
  AlphaMissense.pm
  dbNSFP.pm
)

log() { printf '[vep-setup] %s\n' "$*"; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "ERROR: missing command: $1 (use pixi shell?)" >&2; exit 1; }
}

mkdir -p "${DATA_ROOT}/tmp" "${DATA_ROOT}/vep_data" "${PLUGIN_DIR}"

if [[ "$INSTALL_CACHE" == yes ]]; then
  require_cmd vep_install
  log "Installing VEP cache to ${CACHE_DIR} (this may take a while)..."
  vep_install -a cf -s "$SPECIES" -y "$ASSEMBLY" -c "$CACHE_DIR" --CONVERT
else
  log "Skipping cache install (set OPENRARE_VEP_INSTALL_CACHE=yes to enable vep_install)."
fi

log "Downloading VEP plugin modules (release/${VEP_RELEASE}) into ${PLUGIN_DIR}"
for pm in "${PLUGIN_PMS[@]}"; do
  target="${PLUGIN_DIR}/${pm}"
  curl -fsSL --connect-timeout 30 --max-time 120 "${VEP_PLUGINS_BASE}/${pm}" -o "$target"
  log "  ${pm}"
done

if [[ ! -f "${LOFTEE_DIR}/LoF.pm" ]]; then
  log "Cloning LoFTEE into ${LOFTEE_DIR}"
  if command -v git >/dev/null 2>&1; then
    git clone --depth 1 https://github.com/konradjk/loftee.git "$LOFTEE_DIR"
  else
    log "WARN: git not found; clone LoFTEE manually into ${LOFTEE_DIR}"
  fi
else
  log "LoFTEE already present at ${LOFTEE_DIR}"
fi

if [[ ! -s "${LOFTEE_DIR}/human_ancestor.fa.gz" ]]; then
  log "WARN: missing ${LOFTEE_DIR}/human_ancestor.fa.gz"
  log "      Download from LoFTEE documentation or copy from an existing installation."
fi

log "Plugin module setup finished."
log "Next: download annotation databases and build tabix indexes — see modules/vep_runner/README.md"
log "Verify: pixi run vep-verify-plugins"
