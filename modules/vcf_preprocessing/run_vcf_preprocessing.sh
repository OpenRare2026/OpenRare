#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 INPUT.vcf[.gz] OUTPUT_PREFIX [SAMPLE] [CCRE_BED_GZ] [NCRNA_BED_GZ]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
input_vcf="$1"
out_prefix="$2"
sample="${3:-}"
ccre_bed="${4:-$script_dir/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz}"
ncrna_bed="${5:-$script_dir/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz}"

mkdir -p "$(dirname "$out_prefix")"

vaf_vcf="${out_prefix}.vaf.vcf.gz"
vaf_summary="${out_prefix}.vaf.summary.txt"

vaf_cmd=(python3 "$script_dir/add_vaf_to_vcf_info/step2_add_vaf_to_vcf_info.py" "$input_vcf" "$vaf_vcf")
if [[ -n "$sample" ]]; then
  vaf_cmd+=(--sample "$sample")
fi

"${vaf_cmd[@]}" > "$vaf_summary"

"$script_dir/regulatory_annotation/scripts/run_regulatory_annotation.sh" \
  "$vaf_vcf" \
  "$out_prefix" \
  "$ccre_bed" \
  "$ncrna_bed"

printf 'vaf_vcf\t%s\n' "$vaf_vcf"
printf 'vaf_index\t%s\n' "${vaf_vcf}.tbi"
printf 'vaf_summary\t%s\n' "$vaf_summary"
printf 'final_vcf\t%s\n' "${out_prefix}.regulatory.vcf.gz"
printf 'final_index\t%s\n' "${out_prefix}.regulatory.vcf.gz.tbi"
printf 'regulatory_summary\t%s\n' "${out_prefix}.regulatory.summary.tsv"
printf 'ncrna_summary\t%s\n' "${out_prefix}.ncrna.summary.tsv"
