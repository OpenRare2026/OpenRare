#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 INPUT.vcf[.gz] OUTPUT_PREFIX [CCRE_BED_GZ] [NCRNA_BED_GZ]" >&2
  echo "Example: $0 P013.genotyper.rm_clinvar_20250729.vcf.gz results/regulatory/P013.genotyper.rm_clinvar_20250729" >&2
  exit 2
fi

input_vcf="$1"
out_prefix="$2"
ccre_bed="${3:-resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz}"
ncrna_bed="${4:-resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz}"

mkdir -p "$(dirname "$out_prefix")"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

python3 scripts/annotate_vcf_regulatory.py \
  --vcf "$input_vcf" \
  --bed "$ccre_bed" \
  --source ENCODE_SCREEN_v4_GRCh38 \
  --stats "${out_prefix}.regulatory.summary.tsv" \
  | bgzip -c > "${tmp_dir}/regulatory.vcf.gz"

python3 scripts/annotate_vcf_ncrna.py \
  --vcf "${tmp_dir}/regulatory.vcf.gz" \
  --bed "$ncrna_bed" \
  --source GENCODE_v49_GRCh38_ncRNA_gene \
  --stats "${out_prefix}.ncrna.summary.tsv" \
  | bgzip -c > "${out_prefix}.regulatory.vcf.gz"

tabix -f -p vcf "${out_prefix}.regulatory.vcf.gz"

printf 'output_vcf\t%s\n' "${out_prefix}.regulatory.vcf.gz"
printf 'output_index\t%s\n' "${out_prefix}.regulatory.vcf.gz.tbi"
printf 'regulatory_summary\t%s\n' "${out_prefix}.regulatory.summary.tsv"
printf 'ncrna_summary\t%s\n' "${out_prefix}.ncrna.summary.tsv"
