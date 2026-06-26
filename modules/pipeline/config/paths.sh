#!/usr/bin/env bash
# Shared path defaults for OpenRare pipeline module. External data via environment variables.
# Source from shell scripts: source "${PIPELINE_ROOT}/config/paths.sh"
set -euo pipefail

if [[ -z "${OPENRARE_PIPELINE_ROOT:-}" ]]; then
  _paths_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  OPENRARE_PIPELINE_ROOT="$(cd "${_paths_dir}/.." && pwd)"
fi

# Backward-compatible alias
OPENRARE_PIPELINE_V3_ROOT="${OPENRARE_PIPELINE_ROOT}"

_env_file="${OPENRARE_PIPELINE_ROOT}/.env"
if [[ -f "$_env_file" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$_env_file"
  set +a
fi

openrare_resolve_path() {
  local value="${1:?}"
  if [[ "$value" == /* ]]; then
    printf '%s' "$value"
  else
    printf '%s' "${OPENRARE_PIPELINE_ROOT}/${value}"
  fi
}

: "${OPENRARE_DATA_ROOT:=/path/to/vep_runner}"
: "${OPENRARE_PUBLIC_DATA_ROOT:=/path/to/public_data}"
: "${FULL_PIPELINE_REF_DIR:=/path/to/phasing/CHN_ref}"
: "${FULL_PIPELINE_BEAGLE_JAR:=/path/to/phasing/beagle.27Feb25.75f.jar}"

OPENRARE_DATA_ROOT="$(openrare_resolve_path "$OPENRARE_DATA_ROOT")"
OPENRARE_PUBLIC_DATA_ROOT="$(openrare_resolve_path "$OPENRARE_PUBLIC_DATA_ROOT")"
FULL_PIPELINE_REF_DIR="$(openrare_resolve_path "$FULL_PIPELINE_REF_DIR")"
FULL_PIPELINE_BEAGLE_JAR="$(openrare_resolve_path "$FULL_PIPELINE_BEAGLE_JAR")"
: "${FULL_PIPELINE_GENOS_EVEE_DB:=resource/genos_evee/genos_evee.cpra.tsv.gz}"
FULL_PIPELINE_GENOS_EVEE_DB="$(openrare_resolve_path "$FULL_PIPELINE_GENOS_EVEE_DB")"

: "${LIFTOVER_JAR:=/path/to/grch37_to_grch38_liftover/liftover_runner/target/liftover-runner.jar}"
: "${LIFTOVER_CONFIG:=/path/to/grch37_to_grch38_liftover/config/liftover_config.toml}"
LIFTOVER_JAR="$(openrare_resolve_path "$LIFTOVER_JAR")"
LIFTOVER_CONFIG="$(openrare_resolve_path "$LIFTOVER_CONFIG")"

OPENRARE_VEP_CONFIG="${OPENRARE_PIPELINE_ROOT}/modules/vep_runner/config/vep_runner_config.json"
OPENRARE_LIFTOVER_SCRIPT="${OPENRARE_PIPELINE_ROOT}/modules/vcf_preprocessing/liftover_grch37/scripts/run_liftover_vcf.py"
OPENRARE_CCRE_BED="${OPENRARE_PIPELINE_ROOT}/modules/vcf_preprocessing/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz"
OPENRARE_NCRNA_BED="${OPENRARE_PIPELINE_ROOT}/modules/vcf_preprocessing/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz"
OPENRARE_TEST_VCF_P001="${OPENRARE_PIPELINE_ROOT}/test/input/P001.genotyper10000.vcf"
