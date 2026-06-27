#!/usr/bin/env bash
# Dry-run smoke test: all VEP-prep toggles off + mock annotation DBs (no Beagle / no VEP execution).
set -euo pipefail

PIPELINE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${OPENRARE_MOCK_SMOKE_OUT:-/tmp/openrare_mock_smoke_$(id -un)}"
INPUT_VCF="${OPENRARE_MOCK_SMOKE_VCF:-${PIPELINE_ROOT}/test/input/P001.genotyper10000.vcf}"
MOCK_ROOT="${PIPELINE_ROOT}/resource_mock"

log() {
  printf '[mock-smoke] %s\n' "$*"
}

[[ -s "$INPUT_VCF" ]] || { echo "ERROR: input VCF not found: $INPUT_VCF" >&2; exit 1; }
[[ -s "${MOCK_ROOT}/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.mock.bed.gz" ]] || {
  echo "ERROR: mock cCRE BED missing under ${MOCK_ROOT}" >&2
  exit 1
}

log "dry-run with mock DBs -> ${OUT_DIR}"
bash "${PIPELINE_ROOT}/scripts/run_full_pipeline.sh" \
  --input-vcf "$INPUT_VCF" \
  --out-dir "$OUT_DIR" \
  --chromosomes 1 \
  --sample-id P001 \
  --phasing no \
  --vaf no \
  --regulatory-annotation no \
  --ncrna-annotation no \
  --pseudogene-annotation no \
  --hla-filter yes \
  --ccre-bed "${MOCK_ROOT}/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.mock.bed.gz" \
  --ncrna-bed "${MOCK_ROOT}/ncrna/hg38/gencode.v49.ncrna_gene.slim.mock.bed.gz" \
  --GENOS-VarRisk-db "${MOCK_ROOT}/genos_evee/genos_evee.cpra.mock.tsv.gz" \
  --dry-run

log "OK: mock smoke dry-run completed"
