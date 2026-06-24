#!/usr/bin/env bash
set -euo pipefail

CHR="${1:?Usage: process_one_chromosome.sh <chromosome>}"
: "${PIPE_PATIENT_VCF:?}"
: "${PIPE_REF_DIR:?}"
: "${PIPE_OUT_DIR:?}"
: "${PIPE_BEAGLE_JAR:?}"
: "${PIPE_SAMPLE_ID:?}"
: "${PIPE_JAVA_BIN:?}"
: "${PIPE_BCFTOOLS_BIN:?}"
: "${PIPE_PYTHON_BIN:?}"
: "${PIPE_REF_PREFIX:?}"
: "${PIPE_REF_SUFFIX:?}"
: "${PIPE_BEAGLE_THREADS:?}"
: "${PIPE_JAVA_HEAP_GB:?}"
: "${PIPE_SEED_BASE:?}"
: "${PIPE_KEEP_INTERMEDIATE:?}"
: "${PIPE_RESUME:?}"
: "${PIPE_MERGER:?}"

BCF="${PIPE_BCFTOOLS_BIN}"
REF="${PIPE_REF_DIR}/${PIPE_REF_PREFIX}.chr${CHR}.${PIPE_REF_SUFFIX}"
PATIENT="${PIPE_OUT_DIR}/patient_by_chr/${PIPE_SAMPLE_ID}.chr${CHR}.vcf.gz"
POSITIONS="${PIPE_OUT_DIR}/reference_subset/${PIPE_SAMPLE_ID}.chr${CHR}.positions.tsv"
REF_SUBSET="${PIPE_OUT_DIR}/reference_subset/${PIPE_REF_PREFIX}.chr${CHR}.patient_positions.vcf.gz"
PREFIX="${PIPE_OUT_DIR}/beagle_noimpute/${PIPE_SAMPLE_ID}.chr${CHR}.beagle_phased.noimpute"
BEAGLE_VCF="${PREFIX}.vcf.gz"
FINAL="${PIPE_OUT_DIR}/final_refsupport/${PIPE_SAMPLE_ID}.chr${CHR}.original_sites.beagle_phase_merged.refsupport.vcf.gz"
RAW="${FINAL%.gz}"
LOG="${PIPE_OUT_DIR}/logs/${PIPE_SAMPLE_ID}.chr${CHR}.worker.log"
STATS="${PIPE_OUT_DIR}/logs/${PIPE_SAMPLE_ID}.chr${CHR}.annotation_stats.tsv"
ROW="${PIPE_OUT_DIR}/logs/${PIPE_SAMPLE_ID}.chr${CHR}.summary_row.tsv"
SEED=$((PIPE_SEED_BASE + CHR))

exec > >(tee "${LOG}") 2>&1
start_epoch=$(date +%s)
echo "[$(date '+%F %T')] START chr${CHR}"
echo "CONFIG chr=${CHR} sample=${PIPE_SAMPLE_ID} threads=${PIPE_BEAGLE_THREADS} heap_gb=${PIPE_JAVA_HEAP_GB} seed=${SEED}"

index_vcf() {
    local vcf="$1"
    "${BCF}" index -f -t "${vcf}" || "${BCF}" index -f -c "${vcf}"
}

count_filter() {
    "${BCF}" view -i "$1" -H "$2" | wc -l
}

extract_patient() {
    local region="chr${CHR}"
    if ! "${BCF}" index -s "${PIPE_PATIENT_VCF}" | cut -f1 | grep -Fxq "${region}"; then
        region="${CHR}"
    fi
    "${BCF}" index -s "${PIPE_PATIENT_VCF}" | cut -f1 | grep -Fxq "${region}" || {
        echo "ERROR: patient VCF has neither chr${CHR} nor ${CHR}" >&2
        return 1
    }
    rm -f "${PATIENT}" "${PATIENT}.tbi" "${PATIENT}.csi"
    "${BCF}" view -s "${PIPE_SAMPLE_ID}" -r "${region}" -Oz -o "${PATIENT}" "${PIPE_PATIENT_VCF}"
    index_vcf "${PATIENT}"
}

validate_final() {
    local original_sites final_sites imp pkeys fkeys
    [[ -s "${PATIENT}" && -s "${FINAL}" ]] || return 1
    "${BCF}" view -h "${FINAL}" >/dev/null || return 1
    original_sites=$("${BCF}" view -H "${PATIENT}" | wc -l)
    final_sites=$("${BCF}" view -H "${FINAL}" | wc -l)
    [[ "${original_sites}" -eq "${final_sites}" ]] || return 1
    imp=$("${BCF}" view -i 'INFO/IMP=1' -H "${FINAL}" 2>/dev/null | wc -l || true)
    [[ "${imp}" -eq 0 ]] || return 1
    pkeys=$(mktemp)
    fkeys=$(mktemp)
    "${BCF}" query -f '%CHROM\t%POS\t%REF\t%ALT\n' "${PATIENT}" >"${pkeys}"
    "${BCF}" query -f '%CHROM\t%POS\t%REF\t%ALT\n' "${FINAL}" >"${fkeys}"
    cmp -s "${pkeys}" "${fkeys}"
    local status=$?
    rm -f "${pkeys}" "${fkeys}"
    return "${status}"
}

if [[ ! -s "${PATIENT}" ]]; then
    extract_patient
fi

if [[ "${PIPE_RESUME}" == yes ]] && validate_final && [[ -s "${ROW}" ]]; then
    echo "[$(date '+%F %T')] RESUME chr${CHR}: validated final output; skipping"
    exit 0
fi

extract_patient
original_sites=$("${BCF}" view -H "${PATIENT}" | wc -l)
read -r original_phased original_unphased < <(
    "${BCF}" query -f '[%GT\n]' "${PATIENT}" |
        awk 'index($0,"|"){p++} index($0,"/"){u++} END{print p+0,u+0}'
)

"${BCF}" query -f '%CHROM\t%POS\n' "${PATIENT}" | sort -u >"${POSITIONS}"
rm -f "${REF_SUBSET}" "${REF_SUBSET}.tbi" "${REF_SUBSET}.csi"
"${BCF}" view -R "${POSITIONS}" -Oz -o "${REF_SUBSET}" "${REF}"
index_vcf "${REF_SUBSET}"

rm -f "${PREFIX}".*
"${PIPE_JAVA_BIN}" "-Xmx${PIPE_JAVA_HEAP_GB}g" -jar "${PIPE_BEAGLE_JAR}" \
    gt="${PATIENT}" ref="${REF}" impute=false out="${PREFIX}" \
    nthreads="${PIPE_BEAGLE_THREADS}" seed="${SEED}"
index_vcf "${BEAGLE_VCF}"

rm -f "${RAW}" "${FINAL}" "${FINAL}.tbi" "${FINAL}.csi"
"${PIPE_PYTHON_BIN}" "${PIPE_MERGER}" \
    --patient-vcf "${PATIENT}" \
    --beagle-vcf "${BEAGLE_VCF}" \
    --ref-vcf "${REF_SUBSET}" \
    --output-vcf "${RAW}" \
    --chrom "chr${CHR}" \
    --sample-id "${PIPE_SAMPLE_ID}" \
    --stats "${STATS}"
bgzip -f -c "${RAW}" >"${FINAL}"
rm -f "${RAW}"
index_vcf "${FINAL}"

final_sites=$("${BCF}" view -H "${FINAL}" | wc -l)
b1=$(count_filter 'INFO/BEAGLE_PHASED=1' "${FINAL}")
b0=$(count_filter 'INFO/BEAGLE_PHASED=0' "${FINAL}")
poly=$(count_filter 'INFO/CHN_REF_SUPPORT="POLYMORPHIC"' "${FINAL}")
mono=$(count_filter 'INFO/CHN_REF_SUPPORT="MONOMORPHIC_REF"' "${FINAL}")
mismatch=$(count_filter 'INFO/CHN_REF_SUPPORT="ALLELE_MISMATCH"' "${FINAL}")
absent=$(count_filter 'INFO/CHN_REF_SUPPORT="NOT_IN_REF"' "${FINAL}")
high=$(count_filter 'INFO/PHASING_CONFIDENCE="HIGH"' "${FINAL}")
low=$(count_filter 'INFO/PHASING_CONFIDENCE="LOW"' "${FINAL}")
conf_unphased=$(count_filter 'INFO/PHASING_CONFIDENCE="UNPHASED"' "${FINAL}")
read -r final_phased final_unphased < <(
    "${BCF}" query -f '[%GT\n]' "${FINAL}" |
        awk 'index($0,"|"){p++} index($0,"/"){u++} END{print p+0,u+0}'
)
imp=$("${BCF}" view -i 'INFO/IMP=1' -H "${FINAL}" 2>/dev/null | wc -l || true)

pkeys=$(mktemp)
fkeys=$(mktemp)
trap 'rm -f "${pkeys}" "${fkeys}"' EXIT
"${BCF}" query -f '%CHROM\t%POS\t%REF\t%ALT\n' "${PATIENT}" >"${pkeys}"
"${BCF}" query -f '%CHROM\t%POS\t%REF\t%ALT\n' "${FINAL}" >"${fkeys}"
cmp -s "${pkeys}" "${fkeys}" && order=yes || order=no

[[ "${final_sites}" -eq "${original_sites}" ]]
[[ "${imp}" -eq 0 && "${order}" == yes ]]
[[ $((b1 + b0)) -eq "${final_sites}" ]]
[[ $((poly + mono + mismatch + absent)) -eq "${final_sites}" ]]
[[ $((high + low + conf_unphased)) -eq "${final_sites}" ]]

elapsed=$(( $(date +%s) - start_epoch ))
printf 'chr%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "${CHR}" "${original_sites}" "${original_phased}" "${original_unphased}" \
    "${final_sites}" "${b1}" "${b0}" "${poly}" "${mono}" "${mismatch}" \
    "${absent}" "${high}" "${low}" "${conf_unphased}" "${final_phased}" \
    "${final_unphased}" "${imp}" "${order}" "${elapsed}" >"${ROW}"

if [[ "${PIPE_KEEP_INTERMEDIATE}" == no ]]; then
    rm -f "${PATIENT}" "${PATIENT}.tbi" "${PATIENT}.csi"
    rm -f "${POSITIONS}" "${REF_SUBSET}" "${REF_SUBSET}.tbi" "${REF_SUBSET}.csi"
    rm -f "${PREFIX}.vcf.gz" "${PREFIX}.vcf.gz.tbi" "${PREFIX}.vcf.gz.csi" "${PREFIX}.log"
fi
echo "[$(date '+%F %T')] DONE chr${CHR}: sites=${final_sites}, elapsed=${elapsed}s"
