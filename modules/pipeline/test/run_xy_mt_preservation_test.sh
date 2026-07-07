#!/usr/bin/env bash
# Unit tests: restore_unphased_variants.sh must preserve chrX/chrY when not in --chromosomes.
set -euo pipefail

PIPELINE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESTORE_SCRIPT="${PIPELINE_ROOT}/modules/phasing_beagle_refsupport/scripts/restore_unphased_variants.sh"
ENSURE_HEADERS="${PIPELINE_ROOT}/modules/vcf_preprocessing/scripts/ensure_vcf_info_headers.py"
OUT_DIR="${OPENRARE_XY_MT_TEST_OUT:-${PIPELINE_ROOT}/tmp/xy_mt_preservation_test}"
mkdir -p "$OUT_DIR"

chmod +x "$RESTORE_SCRIPT"

PHASING_INFO='##INFO=<ID=BEAGLE_PHASED,Number=1,Type=Integer,Description="Beagle phased">
##INFO=<ID=CHN_REF_SUPPORT,Number=1,Type=String,Description="Ref support">
##INFO=<ID=CHN_ALT_CARRIER_COUNT,Number=1,Type=Integer,Description="Carrier count">
##INFO=<ID=CHN_ALT_AC,Number=1,Type=Integer,Description="AC">
##INFO=<ID=PHASING_CONFIDENCE,Number=1,Type=String,Description="Confidence">'

run_case() {
  local name="$1"
  local original_vcf="$2"
  local phased_vcf="$3"
  local merged_vcf="$4"
  local stats="$5"
  local expected_original="$6"
  local expected_phased="$7"
  local expected_passthrough="$8"

  printf '\n[case:%s] running restore...\n' "$name"
  bgzip -f -c "$original_vcf" > "${original_vcf}.gz"
  bcftools index -f -t "${original_vcf}.gz"
  bgzip -f -c "$phased_vcf" > "${phased_vcf}.gz"
  bcftools index -f -t "${phased_vcf}.gz"

  bash "$RESTORE_SCRIPT" \
    --original-vcf "${original_vcf}.gz" \
    --phased-vcf "${phased_vcf}.gz" \
    --output-vcf "$merged_vcf" \
    --ensure-headers-script "$ENSURE_HEADERS" \
    --stats "$stats"

  grep -q $'original_records\t'"${expected_original}" "$stats" || {
    echo "ERROR [$name]: expected original_records=${expected_original}" >&2; exit 1; }
  grep -q $'phased_records\t'"${expected_phased}" "$stats" || {
    echo "ERROR [$name]: expected phased_records=${expected_phased}" >&2; exit 1; }
  grep -q $'passthrough_records\t'"${expected_passthrough}" "$stats" || {
    echo "ERROR [$name]: expected passthrough_records=${expected_passthrough}" >&2; exit 1; }
  grep -q $'merged_records\t'"${expected_original}" "$stats" || {
    echo "ERROR [$name]: expected merged_records=${expected_original}" >&2; exit 1; }
  grep -q $'cpra_multiset_match\tyes' "$stats" || {
    echo "ERROR [$name]: expected cpra_multiset_match=yes" >&2; exit 1; }

  printf '[case:%s] stats:\n' "$name"
  cat "$stats"
}

assert_passthrough() {
  local name="$1"
  local merged_vcf="$2"
  local chrom="$3"
  local pos="$4"
  local expected_gt="$5"

  local line
  line="$(bcftools view -H "$merged_vcf" "${chrom}:${pos}-${pos}")"
  [[ -n "$line" ]] || { echo "ERROR [$name]: ${chrom}:${pos} missing" >&2; exit 1; }
  echo "$line" | grep -q 'CHN_REF_SUPPORT=NOT_EVALUATED' || {
    echo "ERROR [$name]: ${chrom}:${pos} should have CHN_REF_SUPPORT=NOT_EVALUATED" >&2; exit 1; }
  echo "$line" | grep -q 'BEAGLE_PHASED=0' || {
    echo "ERROR [$name]: ${chrom}:${pos} should have BEAGLE_PHASED=0" >&2; exit 1; }
  echo "$line" | grep -q "GT[[:space:]]${expected_gt}" || {
    echo "ERROR [$name]: ${chrom}:${pos} GT should remain ${expected_gt}, got: $line" >&2; exit 1; }
}

assert_phased() {
  local name="$1"
  local merged_vcf="$2"
  local chrom="$3"
  local pos="$4"
  local expected_gt="$5"

  local line
  line="$(bcftools view -H "$merged_vcf" "${chrom}:${pos}-${pos}")"
  [[ -n "$line" ]] || { echo "ERROR [$name]: ${chrom}:${pos} missing" >&2; exit 1; }
  echo "$line" | grep -q 'BEAGLE_PHASED=1' || {
    echo "ERROR [$name]: ${chrom}:${pos} should have BEAGLE_PHASED=1" >&2; exit 1; }
  echo "$line" | grep -q "GT[[:space:]]${expected_gt}" || {
    echo "ERROR [$name]: ${chrom}:${pos} phased GT should be ${expected_gt}, got: $line" >&2; exit 1; }
}

# ---------------------------------------------------------------------------
# Case 1: --chromosomes 1  (default 1-22 behaviour) — chrX/chrY are passthrough
# ---------------------------------------------------------------------------
CASE1_DIR="${OUT_DIR}/case1_chr1_phased"
mkdir -p "$CASE1_DIR"

cat >"${CASE1_DIR}/original.vcf" <<'EOF'
##fileformat=VCFv4.2
##contig=<ID=chr1,length=248956422>
##contig=<ID=chrX,length=156040895>
##contig=<ID=chrY,length=57227415>
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chr1	100	.	A	G	50	PASS	.	GT	0/1
chrX	2786989	.	C	T	50	PASS	.	GT	0/1
chrX	154931044	.	G	A	50	PASS	.	GT	1/1
chrY	2667398	.	A	G	50	PASS	.	GT	0/1
chrY	2781479	.	T	C	50	PASS	.	GT	1
EOF

cat >"${CASE1_DIR}/phased.vcf" <<EOF
##fileformat=VCFv4.2
##contig=<ID=chr1,length=248956422>
${PHASING_INFO}
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chr1	100	.	A	G	50	PASS	BEAGLE_PHASED=1;CHN_REF_SUPPORT=POLYMORPHIC;CHN_ALT_CARRIER_COUNT=10;CHN_ALT_AC=12;PHASING_CONFIDENCE=HIGH	GT	0|1
EOF

run_case "chr1_phased_xy_passthrough" \
  "${CASE1_DIR}/original.vcf" \
  "${CASE1_DIR}/phased.vcf" \
  "${CASE1_DIR}/merged.vcf.gz" \
  "${CASE1_DIR}/preservation.tsv" \
  5 1 4

assert_phased "chr1_phased_xy_passthrough" "${CASE1_DIR}/merged.vcf.gz" chr1 100 "0|1"
assert_passthrough "chr1_phased_xy_passthrough" "${CASE1_DIR}/merged.vcf.gz" chrX 2786989 "0/1"
assert_passthrough "chr1_phased_xy_passthrough" "${CASE1_DIR}/merged.vcf.gz" chrX 154931044 "1/1"
assert_passthrough "chr1_phased_xy_passthrough" "${CASE1_DIR}/merged.vcf.gz" chrY 2781479 "1"
assert_passthrough "chr1_phased_xy_passthrough" "${CASE1_DIR}/merged.vcf.gz" chrY 2667398 "0/1"

xy_count=$(bcftools view -H "${CASE1_DIR}/merged.vcf.gz" chrX | wc -l)
yy_count=$(bcftools view -H "${CASE1_DIR}/merged.vcf.gz" chrY | wc -l)
[[ "$xy_count" -eq 2 ]] || { echo "ERROR: expected 2 chrX records, got $xy_count" >&2; exit 1; }
[[ "$yy_count" -eq 2 ]] || { echo "ERROR: expected 2 chrY records, got $yy_count" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Case 2: --chromosomes X — only chrX phased, chrY passthrough
# ---------------------------------------------------------------------------
CASE2_DIR="${OUT_DIR}/case2_chrx_phased"
mkdir -p "$CASE2_DIR"

cat >"${CASE2_DIR}/original.vcf" <<'EOF'
##fileformat=VCFv4.2
##contig=<ID=chrX,length=156040895>
##contig=<ID=chrY,length=57227415>
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chrX	2786989	.	C	T	50	PASS	.	GT	0/1
chrX	154931044	.	G	A	50	PASS	.	GT	0/0
chrY	2667398	.	A	G	50	PASS	.	GT	0/1
chrY	2781479	.	T	C	50	PASS	.	GT	1
EOF

cat >"${CASE2_DIR}/phased.vcf" <<EOF
##fileformat=VCFv4.2
##contig=<ID=chrX,length=156040895>
${PHASING_INFO}
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chrX	2786989	.	C	T	50	PASS	BEAGLE_PHASED=1;CHN_REF_SUPPORT=POLYMORPHIC;CHN_ALT_CARRIER_COUNT=5;CHN_ALT_AC=6;PHASING_CONFIDENCE=HIGH	GT	0|1
chrX	154931044	.	G	A	50	PASS	BEAGLE_PHASED=1;CHN_REF_SUPPORT=MONOMORPHIC_REF;CHN_ALT_CARRIER_COUNT=0;CHN_ALT_AC=0;PHASING_CONFIDENCE=LOW	GT	0|0
EOF

run_case "chrx_phased_y_passthrough" \
  "${CASE2_DIR}/original.vcf" \
  "${CASE2_DIR}/phased.vcf" \
  "${CASE2_DIR}/merged.vcf.gz" \
  "${CASE2_DIR}/preservation.tsv" \
  4 2 2

assert_phased "chrx_phased_y_passthrough" "${CASE2_DIR}/merged.vcf.gz" chrX 2786989 "0|1"
assert_phased "chrx_phased_y_passthrough" "${CASE2_DIR}/merged.vcf.gz" chrX 154931044 "0|0"
assert_passthrough "chrx_phased_y_passthrough" "${CASE2_DIR}/merged.vcf.gz" chrY 2781479 "1"
assert_passthrough "chrx_phased_y_passthrough" "${CASE2_DIR}/merged.vcf.gz" chrY 2667398 "0/1"

# ---------------------------------------------------------------------------
# Case 3: --chromosomes Y — only chrY phased, chrX passthrough
# ---------------------------------------------------------------------------
CASE3_DIR="${OUT_DIR}/case3_chry_phased"
mkdir -p "$CASE3_DIR"

cat >"${CASE3_DIR}/original.vcf" <<'EOF'
##fileformat=VCFv4.2
##contig=<ID=chrX,length=156040895>
##contig=<ID=chrY,length=57227415>
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chrX	2786989	.	C	T	50	PASS	.	GT	0/1
chrY	2667398	.	A	G	50	PASS	.	GT	0/1
chrY	2781479	.	T	C	50	PASS	.	GT	1
EOF

cat >"${CASE3_DIR}/phased.vcf" <<EOF
##fileformat=VCFv4.2
##contig=<ID=chrY,length=57227415>
${PHASING_INFO}
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chrY	2667398	.	A	G	50	PASS	BEAGLE_PHASED=1;CHN_REF_SUPPORT=POLYMORPHIC;CHN_ALT_CARRIER_COUNT=2;CHN_ALT_AC=2;PHASING_CONFIDENCE=HIGH	GT	0|1
chrY	2781479	.	T	C	50	PASS	BEAGLE_PHASED=1;CHN_REF_SUPPORT=POLYMORPHIC;CHN_ALT_CARRIER_COUNT=3;CHN_ALT_AC=4;PHASING_CONFIDENCE=HIGH	GT	1
EOF

run_case "chry_phased_x_passthrough" \
  "${CASE3_DIR}/original.vcf" \
  "${CASE3_DIR}/phased.vcf" \
  "${CASE3_DIR}/merged.vcf.gz" \
  "${CASE3_DIR}/preservation.tsv" \
  3 2 1

assert_passthrough "chry_phased_x_passthrough" "${CASE3_DIR}/merged.vcf.gz" chrX 2786989 "0/1"
assert_phased "chry_phased_x_passthrough" "${CASE3_DIR}/merged.vcf.gz" chrY 2781479 "1"
assert_phased "chry_phased_x_passthrough" "${CASE3_DIR}/merged.vcf.gz" chrY 2667398 "0|1"

# ---------------------------------------------------------------------------
# Case 4: contig naming without "chr" prefix (X/Y) — passthrough when phasing 1-22
# ---------------------------------------------------------------------------
CASE4_DIR="${OUT_DIR}/case4_no_chr_prefix"
mkdir -p "$CASE4_DIR"

cat >"${CASE4_DIR}/original.vcf" <<'EOF'
##fileformat=VCFv4.2
##contig=<ID=1,length=248956422>
##contig=<ID=X,length=156040895>
##contig=<ID=Y,length=57227415>
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
1	100	.	A	G	50	PASS	.	GT	0/1
X	200	.	C	T	50	PASS	.	GT	0/1
Y	300	.	G	A	50	PASS	.	GT	1
EOF

cat >"${CASE4_DIR}/phased.vcf" <<EOF
##fileformat=VCFv4.2
##contig=<ID=1,length=248956422>
${PHASING_INFO}
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
1	100	.	A	G	50	PASS	BEAGLE_PHASED=1;CHN_REF_SUPPORT=POLYMORPHIC;CHN_ALT_CARRIER_COUNT=10;CHN_ALT_AC=12;PHASING_CONFIDENCE=HIGH	GT	0|1
EOF

run_case "no_chr_prefix_xy_passthrough" \
  "${CASE4_DIR}/original.vcf" \
  "${CASE4_DIR}/phased.vcf" \
  "${CASE4_DIR}/merged.vcf.gz" \
  "${CASE4_DIR}/preservation.tsv" \
  3 1 2

assert_passthrough "no_chr_prefix_xy_passthrough" "${CASE4_DIR}/merged.vcf.gz" X 200 "0/1"
assert_passthrough "no_chr_prefix_xy_passthrough" "${CASE4_DIR}/merged.vcf.gz" Y 300 "1"

printf '\n[xy-mt-preservation-test] ALL CASES OK\n'
printf '  case1 (chr1 phased, chrX/chrY passthrough): %s\n' "${CASE1_DIR}/merged.vcf.gz"
printf '  case2 (chrX phased, chrY passthrough):       %s\n' "${CASE2_DIR}/merged.vcf.gz"
printf '  case3 (chrY phased, chrX passthrough):       %s\n' "${CASE3_DIR}/merged.vcf.gz"
printf '  case4 (X/Y without chr prefix, passthrough):  %s\n' "${CASE4_DIR}/merged.vcf.gz"
