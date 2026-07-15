#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  restore_unphased_variants.sh --original-vcf FILE --phased-vcf FILE \
    --output-vcf FILE --ensure-headers-script FILE [--stats FILE]

Merge records phased on selected chromosomes with every original record that was
not phased. Passthrough records keep their original GT and receive explicit
phasing/ref-support INFO values.
EOF
}

ORIGINAL_VCF=""
PHASED_VCF=""
OUTPUT_VCF=""
ENSURE_HEADERS_SCRIPT=""
STATS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --original-vcf) ORIGINAL_VCF="${2:?}"; shift 2 ;;
    --phased-vcf) PHASED_VCF="${2:?}"; shift 2 ;;
    --output-vcf) OUTPUT_VCF="${2:?}"; shift 2 ;;
    --ensure-headers-script) ENSURE_HEADERS_SCRIPT="${2:?}"; shift 2 ;;
    --stats) STATS="${2:?}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for value in ORIGINAL_VCF PHASED_VCF OUTPUT_VCF ENSURE_HEADERS_SCRIPT; do
  [[ -n "${!value}" ]] || { echo "ERROR: --${value,,} is required" >&2; exit 2; }
done
[[ -s "$ORIGINAL_VCF" ]] || { echo "ERROR: original VCF not found: $ORIGINAL_VCF" >&2; exit 1; }
[[ -s "$PHASED_VCF" ]] || { echo "ERROR: phased VCF not found: $PHASED_VCF" >&2; exit 1; }
[[ -s "$ENSURE_HEADERS_SCRIPT" ]] || { echo "ERROR: header helper not found: $ENSURE_HEADERS_SCRIPT" >&2; exit 1; }
command -v bcftools >/dev/null 2>&1 || { echo "ERROR: bcftools is required" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 is required" >&2; exit 1; }

mkdir -p "$(dirname "$OUTPUT_VCF")"
workdir=$(mktemp -d "$(dirname "$OUTPUT_VCF")/.restore_unphased.XXXXXX")
trap 'rm -rf "$workdir"' EXIT

index_vcf() {
  local vcf="$1"
  if [[ ! -s "${vcf}.tbi" && ! -s "${vcf}.csi" ]]; then
    bcftools index -f -t "$vcf" || bcftools index -f -c "$vcf"
  fi
}

index_vcf "$ORIGINAL_VCF"
index_vcf "$PHASED_VCF"

passthrough_raw="$workdir/passthrough.raw.vcf.gz"
passthrough_vcf="$workdir/passthrough.tagged.vcf.gz"
merged_unsorted="$workdir/merged.unsorted.vcf.gz"
original_keys="$workdir/original.keys"
merged_keys="$workdir/merged.keys"

# Exact allele matching is intentional: the phasing module guarantees that
# selected records retain the original CHROM/POS/REF/ALT representation.
bcftools isec -c none -C -w1 -Oz -o "$passthrough_raw" "$ORIGINAL_VCF" "$PHASED_VCF"
bcftools index -f -t "$passthrough_raw" || bcftools index -f -c "$passthrough_raw"

python3 "$ENSURE_HEADERS_SCRIPT" \
  --input-vcf "$passthrough_raw" \
  --output-vcf "$passthrough_vcf" \
  --groups phasing \
  --phasing-passthrough \
  --index

original_count=$(bcftools view -H "$ORIGINAL_VCF" | wc -l)
phased_count=$(bcftools view -H "$PHASED_VCF" | wc -l)
passthrough_count=$(bcftools view -H "$passthrough_vcf" | wc -l)

rm -f "$OUTPUT_VCF" "${OUTPUT_VCF}.tbi" "${OUTPUT_VCF}.csi"
if [[ "$passthrough_count" -eq 0 ]]; then
  bcftools view -Oz -o "$OUTPUT_VCF" "$PHASED_VCF"
else
  bcftools concat -a -Oz -o "$merged_unsorted" "$PHASED_VCF" "$passthrough_vcf"
  bcftools sort -T "$workdir/sort" -Oz -o "$OUTPUT_VCF" "$merged_unsorted"
fi
bcftools index -f -t "$OUTPUT_VCF" || bcftools index -f -c "$OUTPUT_VCF"
merged_count=$(bcftools view -H "$OUTPUT_VCF" | wc -l)

[[ $((phased_count + passthrough_count)) -eq "$original_count" ]] || {
  echo "ERROR: phased + passthrough record count does not equal original: ${phased_count} + ${passthrough_count} != ${original_count}" >&2
  exit 1
}
[[ "$merged_count" -eq "$original_count" ]] || {
  echo "ERROR: merged record count differs from original: ${merged_count} != ${original_count}" >&2
  exit 1
}

bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\n' "$ORIGINAL_VCF" | LC_ALL=C sort > "$original_keys"
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\n' "$OUTPUT_VCF" | LC_ALL=C sort > "$merged_keys"
cmp -s "$original_keys" "$merged_keys" || {
  echo "ERROR: merged CPRA multiset differs from original VCF" >&2
  exit 1
}

if [[ -z "$STATS" ]]; then
  STATS="${OUTPUT_VCF%.vcf.gz}.preservation.tsv"
fi
mkdir -p "$(dirname "$STATS")"
{
  printf 'metric\tvalue\n'
  printf 'original_records\t%s\n' "$original_count"
  printf 'phased_records\t%s\n' "$phased_count"
  printf 'passthrough_records\t%s\n' "$passthrough_count"
  printf 'merged_records\t%s\n' "$merged_count"
  printf 'cpra_multiset_match\tyes\n'
} > "$STATS"

echo "RESTORE_OK original=${original_count} phased=${phased_count} passthrough=${passthrough_count} merged=${merged_count}"
echo "output_vcf=$OUTPUT_VCF"
echo "stats=$STATS"
