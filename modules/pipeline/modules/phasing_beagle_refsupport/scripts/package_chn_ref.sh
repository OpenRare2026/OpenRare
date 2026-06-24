#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-/mnt/zzb/peixunban/changan/1kgp/CHN_ref}"
OUTPUT_DIR="${2:-/mnt/zzb/peixunban/changan/1kgp/beagle_pipeline_param/packages}"
BCFTOOLS_BIN="${BCFTOOLS_BIN:-bcftools}"
PACKAGE="${OUTPUT_DIR}/CHN_ref_1000G_CHN_359_GRCh38_phased.tar.gz"
MD5_FILE="${OUTPUT_DIR}/CHN_ref.md5"
README_FILE="${OUTPUT_DIR}/README_CHN_ref.txt"
LOG="${OUTPUT_DIR}/package_chn_ref.log"
STAGE="${OUTPUT_DIR}/.package_stage"

mkdir -p "${OUTPUT_DIR}"
exec > >(tee "${LOG}") 2>&1
[[ -d "${SOURCE_DIR}" ]] || { echo "ERROR: source directory missing" >&2; exit 1; }
command -v "${BCFTOOLS_BIN}" >/dev/null

files=()
for chr in $(seq 1 22); do
    vcf="${SOURCE_DIR}/1000G.CHN.chr${chr}.phased.vcf.gz"
    [[ -s "${vcf}" ]] || { echo "ERROR: missing ${vcf}" >&2; exit 1; }
    if [[ -s "${vcf}.tbi" ]]; then
        index="${vcf}.tbi"
    elif [[ -s "${vcf}.csi" ]]; then
        index="${vcf}.csi"
    else
        echo "ERROR: missing index for ${vcf}" >&2
        exit 1
    fi
    "${BCFTOOLS_BIN}" view -h "${vcf}" >/dev/null
    samples=$("${BCFTOOLS_BIN}" query -l "${vcf}" | wc -l)
    [[ "${samples}" -eq 359 ]] || {
        echo "ERROR: chr${chr} has ${samples} samples, expected 359" >&2
        exit 1
    }
    echo "CHECK_OK chr${chr} samples=${samples}"
    files+=("$(basename "${vcf}")" "$(basename "${index}")")
done

(
    cd "${SOURCE_DIR}"
    md5sum "${files[@]}"
) >"${MD5_FILE}"

cat >"${README_FILE}" <<'EOF'
CHN reference panel
===================
Source: 1000 Genomes 30x GRCh38 phased panel
Subset: CHB + CHS + CDX, 359 samples
Purpose: Beagle phasing reference panel
Coordinates: GRCh38
Chromosome naming: chr1-chr22
Naming: 1000G.CHN.chrN.phased.vcf.gz plus .tbi or .csi index

Extract:
  tar -xzf CHN_ref_1000G_CHN_359_GRCh38_phased.tar.gz

Verify:
  cd CHN_ref
  md5sum -c CHN_ref.md5
EOF

rm -f "${PACKAGE}"
rm -rf "${STAGE}"
mkdir -p "${STAGE}/CHN_ref"
for file in "${files[@]}"; do
    ln "${SOURCE_DIR}/${file}" "${STAGE}/CHN_ref/${file}"
done
cp "${MD5_FILE}" "${STAGE}/CHN_ref/CHN_ref.md5"
cp "${README_FILE}" "${STAGE}/CHN_ref/README_CHN_ref.txt"
tar -C "${STAGE}" -I 'gzip -1' -cf "${PACKAGE}" CHN_ref
rm -rf "${STAGE}"

echo "PACKAGE=${PACKAGE}"
echo "SIZE_BYTES=$(stat -c %s "${PACKAGE}")"
echo "MD5_FILE=${MD5_FILE}"
