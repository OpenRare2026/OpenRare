#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 INPUT.vcf[.gz] OUTPUT_PREFIX [SAMPLE] [CCRE_BED_GZ] [NCRNA_BED_GZ] [--vaf yes|no] [--regulatory-annotation yes|no] [--ncrna-annotation yes|no]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
input_vcf="$1"; shift
out_prefix="$1"; shift
sample="${1:-}"
if [[ $# -gt 0 ]]; then shift; fi
ccre_bed="${1:-$script_dir/regulatory_annotation/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz}"
if [[ $# -gt 0 ]]; then shift; fi
ncrna_bed="${1:-$script_dir/regulatory_annotation/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz}"
if [[ $# -gt 0 ]]; then shift; fi

VAF=yes
REGULATORY_ANNOTATION=yes
NCRNA_ANNOTATION=yes
while [[ $# -gt 0 ]]; do
  case "$1" in
    --vaf) VAF="${2:?}"; shift 2 ;;
    --regulatory-annotation) REGULATORY_ANNOTATION="${2:?}"; shift 2 ;;
    --ncrna-annotation) NCRNA_ANNOTATION="${2:?}"; shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done
norm_bool() {
  case "$1" in
    yes|YES|true|TRUE|1|on|ON) echo yes ;;
    no|NO|false|FALSE|0|off|OFF) echo no ;;
    *) echo "ERROR: expected yes/no, got: $1" >&2; exit 2 ;;
  esac
}
VAF="$(norm_bool "$VAF")"
REGULATORY_ANNOTATION="$(norm_bool "$REGULATORY_ANNOTATION")"
NCRNA_ANNOTATION="$(norm_bool "$NCRNA_ANNOTATION")"

mkdir -p "$(dirname "$out_prefix")"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

ensure_headers=(python3 "$script_dir/scripts/ensure_vcf_info_headers.py")
vaf_vcf="${out_prefix}.vaf.vcf.gz"
vaf_summary="${out_prefix}.vaf.summary.txt"

if [[ "$VAF" == yes ]]; then
  vaf_cmd=(python3 "$script_dir/add_vaf_to_vcf_info/step2_add_vaf_to_vcf_info.py" "$input_vcf" "$vaf_vcf")
  if [[ -n "$sample" ]]; then vaf_cmd+=(--sample "$sample"); fi
  "${vaf_cmd[@]}" > "$vaf_summary"
else
  "${ensure_headers[@]}" --input-vcf "$input_vcf" --output-vcf "$vaf_vcf" --groups vaf --index
  printf 'step\tstatus\nVAF\tskipped\n' > "$vaf_summary"
fi

current_vcf="$vaf_vcf"
reg_vcf="${tmp_dir}/regulatory.vcf.gz"
reg_summary="${out_prefix}.regulatory.summary.tsv"
if [[ "$REGULATORY_ANNOTATION" == yes ]]; then
  python3 "$script_dir/regulatory_annotation/scripts/annotate_vcf_regulatory.py" \
    --vcf "$current_vcf" \
    --bed "$ccre_bed" \
    --source ENCODE_SCREEN_v4_GRCh38 \
    --stats "$reg_summary" \
    | bgzip -c > "$reg_vcf"
  tabix -f -p vcf "$reg_vcf"
else
  "${ensure_headers[@]}" --input-vcf "$current_vcf" --output-vcf "$reg_vcf" --groups regulatory --index
  printf 'metric\tvalue\ntotal_variants\t0\nannotated_variants\t0\nstatus\tskipped\n' > "$reg_summary"
fi
current_vcf="$reg_vcf"

final_vcf="${out_prefix}.regulatory.vcf.gz"
ncrna_summary="${out_prefix}.ncrna.summary.tsv"
if [[ "$NCRNA_ANNOTATION" == yes ]]; then
  python3 "$script_dir/regulatory_annotation/scripts/annotate_vcf_ncrna.py" \
    --vcf "$current_vcf" \
    --bed "$ncrna_bed" \
    --source GENCODE_v49_GRCh38_ncRNA_gene \
    --stats "$ncrna_summary" \
    | bgzip -c > "$final_vcf"
  tabix -f -p vcf "$final_vcf"
else
  "${ensure_headers[@]}" --input-vcf "$current_vcf" --output-vcf "$final_vcf" --groups ncrna --index
  printf 'metric\tvalue\ntotal_variants\t0\nannotated_variants\t0\nstatus\tskipped\n' > "$ncrna_summary"
fi

printf 'vaf\t%s\n' "$VAF"
printf 'regulatory_annotation\t%s\n' "$REGULATORY_ANNOTATION"
printf 'ncrna_annotation\t%s\n' "$NCRNA_ANNOTATION"
printf 'vaf_vcf\t%s\n' "$vaf_vcf"
printf 'vaf_index\t%s\n' "${vaf_vcf}.tbi"
printf 'vaf_summary\t%s\n' "$vaf_summary"
printf 'final_vcf\t%s\n' "$final_vcf"
printf 'final_index\t%s\n' "${final_vcf}.tbi"
printf 'regulatory_summary\t%s\n' "$reg_summary"
printf 'ncrna_summary\t%s\n' "$ncrna_summary"
