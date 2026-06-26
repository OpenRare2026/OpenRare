#!/usr/bin/env bash
# Add a single sample with missing genotype (./.) to a sites-only VCF for pipeline testing.
set -euo pipefail

INPUT="${1:?input VCF}"
OUTPUT="${2:?output VCF}"
SAMPLE="${3:-SAMPLE}"

chrom_line="$(grep -m1 '^#CHROM' "$INPUT" || true)"
if [[ -z "$chrom_line" ]]; then
  echo "ERROR: no #CHROM header in $INPUT" >&2
  exit 1
fi

{
  grep '^##' "$INPUT" | grep -v '^##FORMAT=<ID=GT' || true
  echo '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">'
  echo "$chrom_line" | awk -v sample="$SAMPLE" 'BEGIN{OFS="\t"} {
    if ($0 ~ /FORMAT/) print $0
    else print $0, "FORMAT", sample
  }'
  awk -v sample="$SAMPLE" 'BEGIN{OFS="\t"} !/^#/ {
    print $1, $2, $3, $4, $5, $6, $7, $8, "GT", "./."
  }' "$INPUT"
} > "$OUTPUT"
