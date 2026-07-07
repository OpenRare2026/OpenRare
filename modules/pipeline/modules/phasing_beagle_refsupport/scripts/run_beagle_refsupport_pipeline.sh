#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WORKER="${SCRIPT_DIR}/process_one_chromosome.sh"
MERGER="${SCRIPT_DIR}/merge_beagle_with_ref_support.py"

usage() {
    cat <<'EOF'
Usage:
  run_beagle_refsupport_pipeline.sh --patient-vcf FILE --ref-dir DIR
    --out-dir DIR --beagle-jar FILE --chromosomes RANGE [options]

Required:
  --patient-vcf FILE       Patient VCF/VCF.GZ
  --ref-dir DIR            Reference VCF directory
  --out-dir DIR            Pipeline output directory
  --beagle-jar FILE        Beagle 5.x jar
  --chromosomes SPEC       auto, all, 1-22, or 1,3,5,22 (auto = every patient contig with a reference panel)

Optional:
  --sample-id ID           Default: automatically detect the single VCF sample
  --chr-jobs N             Concurrent chromosomes (default: 1)
  --beagle-threads N       Threads per Beagle process (default: 4)
  --java-heap-gb N         Java heap per Beagle process (default: 12)
  --seed-base N            Per-chromosome seed is base+chrom (default: 20260608)
  --java-bin PATH          Default: java
  --bcftools-bin PATH      Default: bcftools
  --python-bin PATH        Default: python3
  --ref-prefix TEXT        Default: 1000G.CHN
  --ref-suffix TEXT        Default: phased.vcf.gz
  --keep-intermediate yes|no  Default: yes
  --resume yes|no          Skip validated final chromosomes (default: yes)
  --help
EOF
}

PATIENT_VCF=""
REF_DIR=""
OUT_DIR=""
BEAGLE_JAR=""
CHROMOSOMES=""
SAMPLE_ID=""
CHR_JOBS=1
BEAGLE_THREADS=4
JAVA_HEAP_GB=12
SEED_BASE=20260608
JAVA_BIN=java
BCFTOOLS_BIN=bcftools
PYTHON_BIN=python3
REF_PREFIX=1000G.CHN
REF_SUFFIX=phased.vcf.gz
KEEP_INTERMEDIATE=yes
RESUME=yes

while [[ $# -gt 0 ]]; do
    case "$1" in
        --patient-vcf) PATIENT_VCF="${2:?}"; shift 2 ;;
        --ref-dir) REF_DIR="${2:?}"; shift 2 ;;
        --out-dir) OUT_DIR="${2:?}"; shift 2 ;;
        --beagle-jar) BEAGLE_JAR="${2:?}"; shift 2 ;;
        --chromosomes) CHROMOSOMES="${2:?}"; shift 2 ;;
        --sample-id) SAMPLE_ID="${2:?}"; shift 2 ;;
        --chr-jobs) CHR_JOBS="${2:?}"; shift 2 ;;
        --beagle-threads) BEAGLE_THREADS="${2:?}"; shift 2 ;;
        --java-heap-gb) JAVA_HEAP_GB="${2:?}"; shift 2 ;;
        --seed-base) SEED_BASE="${2:?}"; shift 2 ;;
        --java-bin) JAVA_BIN="${2:?}"; shift 2 ;;
        --bcftools-bin) BCFTOOLS_BIN="${2:?}"; shift 2 ;;
        --python-bin) PYTHON_BIN="${2:?}"; shift 2 ;;
        --ref-prefix) REF_PREFIX="${2:?}"; shift 2 ;;
        --ref-suffix) REF_SUFFIX="${2:?}"; shift 2 ;;
        --keep-intermediate) KEEP_INTERMEDIATE="${2:?}"; shift 2 ;;
        --resume) RESUME="${2:?}"; shift 2 ;;
        --help|-h) usage; exit 0 ;;
        *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
    esac
done

for value in PATIENT_VCF REF_DIR OUT_DIR BEAGLE_JAR CHROMOSOMES; do
    [[ -n "${!value}" ]] || { echo "ERROR: --${value,,} is required" >&2; usage >&2; exit 2; }
done
[[ "${CHR_JOBS}" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: --chr-jobs must be positive" >&2; exit 2; }
[[ "${BEAGLE_THREADS}" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: --beagle-threads must be positive" >&2; exit 2; }
[[ "${JAVA_HEAP_GB}" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: --java-heap-gb must be positive" >&2; exit 2; }
[[ "${SEED_BASE}" =~ ^[0-9]+$ ]] || { echo "ERROR: --seed-base must be an integer" >&2; exit 2; }
[[ "${KEEP_INTERMEDIATE}" =~ ^(yes|no)$ ]] || { echo "ERROR: --keep-intermediate must be yes/no" >&2; exit 2; }
[[ "${RESUME}" =~ ^(yes|no)$ ]] || { echo "ERROR: --resume must be yes/no" >&2; exit 2; }
(( CHR_JOBS * BEAGLE_THREADS <= 64 )) || {
    echo "ERROR: chr-jobs * beagle-threads exceeds safety limit 64" >&2
    exit 2
}

resolve_bin() {
    local value="$1"
    if [[ "${value}" == */* ]]; then
        [[ -x "${value}" ]] || { echo "ERROR: executable unavailable: ${value}" >&2; exit 1; }
        readlink -f "${value}"
    else
        command -v "${value}" || { echo "ERROR: command unavailable: ${value}" >&2; exit 1; }
    fi
}

JAVA_BIN=$(resolve_bin "${JAVA_BIN}")
BCFTOOLS_BIN=$(resolve_bin "${BCFTOOLS_BIN}")
PYTHON_BIN=$(resolve_bin "${PYTHON_BIN}")
[[ -s "${PATIENT_VCF}" ]] || { echo "ERROR: missing patient VCF: ${PATIENT_VCF}" >&2; exit 1; }
[[ -d "${REF_DIR}" ]] || { echo "ERROR: missing reference directory: ${REF_DIR}" >&2; exit 1; }
[[ -s "${BEAGLE_JAR}" ]] || { echo "ERROR: missing Beagle jar: ${BEAGLE_JAR}" >&2; exit 1; }
[[ -x "${WORKER}" && -s "${MERGER}" ]] || { echo "ERROR: pipeline helper scripts missing" >&2; exit 1; }

mkdir -p "${OUT_DIR}"/{patient_by_chr,reference_subset,beagle_noimpute,final_refsupport,logs}
MASTER_LOG="${OUT_DIR}/logs/run_beagle_refsupport_pipeline.log"
exec > >(tee -a "${MASTER_LOG}") 2>&1
pipeline_start=$(date +%s)

echo "[$(date '+%F %T')] Pipeline starting"
"${JAVA_BIN}" -version
"${BCFTOOLS_BIN}" --version | head -1
"${PYTHON_BIN}" --version

index_vcf() {
    local vcf="$1"
    if [[ ! -s "${vcf}.tbi" && ! -s "${vcf}.csi" ]]; then
        "${BCFTOOLS_BIN}" index -f -t "${vcf}" || "${BCFTOOLS_BIN}" index -f -c "${vcf}"
    fi
}

index_vcf "${PATIENT_VCF}"
"${BCFTOOLS_BIN}" view -h "${PATIENT_VCF}" >/dev/null
mapfile -t patient_samples < <("${BCFTOOLS_BIN}" query -l "${PATIENT_VCF}")
if [[ -z "${SAMPLE_ID}" ]]; then
    [[ "${#patient_samples[@]}" -eq 1 ]] || {
        echo "ERROR: patient VCF has ${#patient_samples[@]} samples; use --sample-id" >&2
        exit 1
    }
    SAMPLE_ID="${patient_samples[0]}"
else
    printf '%s\n' "${patient_samples[@]}" | grep -Fxq "${SAMPLE_ID}" || {
        echo "ERROR: sample ${SAMPLE_ID} is absent from patient VCF" >&2
        exit 1
    }
fi

expand_chromosomes() {
    if [[ "$1" =~ ^([0-9]+)-([0-9]+)$ ]]; then
        seq "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    else
        tr ',' '\n' <<<"$1"
    fi
}

contig_to_beagle_chr() {
    local contig="$1"
    contig="${contig#chr}"
    contig="${contig#CHR}"
    if [[ "${contig}" =~ ^[1-9][0-9]*$ ]]; then
        echo "${contig}"
        return 0
    fi
    return 1
}

resolve_chromosome_list() {
    local spec="$1"
    if [[ "${spec}" == auto || "${spec}" == all ]]; then
        declare -A seen=()
        local contig chr ref
        while IFS= read -r contig; do
            [[ -n "${contig}" ]] || continue
            chr=$(contig_to_beagle_chr "${contig}") || continue
            ref="${REF_DIR}/${REF_PREFIX}.chr${chr}.${REF_SUFFIX}"
            [[ -s "${ref}" ]] || continue
            [[ -n "${seen[$chr]:-}" ]] && continue
            seen["${chr}"]=1
            printf '%s\n' "${chr}"
        done < <("${BCFTOOLS_BIN}" query -f '%CHROM\n' "${PATIENT_VCF}" | sort -u) | sort -n
        return 0
    fi
    expand_chromosomes "${spec}"
}

CHROMOSOMES_SPEC="${CHROMOSOMES}"
mapfile -t chroms < <(resolve_chromosome_list "${CHROMOSOMES}")
[[ "${#chroms[@]}" -gt 0 ]] || {
    echo "ERROR: empty chromosome list (spec=${CHROMOSOMES}; no patient contig matched an available reference panel)" >&2
    exit 1
}
if [[ "${CHROMOSOMES_SPEC}" == auto || "${CHROMOSOMES_SPEC}" == all ]]; then
    CHROMOSOMES="$(IFS=,; echo "${chroms[*]}")"
    echo "AUTO_CHROMOSOMES resolved=${CHROMOSOMES}"
fi
for chr in "${chroms[@]}"; do
    [[ "${chr}" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: invalid chromosome: ${chr}" >&2; exit 2; }
done

echo "CONFIG sample=${SAMPLE_ID} chromosomes_spec=${CHROMOSOMES_SPEC} chromosomes=${CHROMOSOMES} chr_jobs=${CHR_JOBS} beagle_threads=${BEAGLE_THREADS} heap_gb=${JAVA_HEAP_GB} seed_base=${SEED_BASE}"
for chr in "${chroms[@]}"; do
    ref="${REF_DIR}/${REF_PREFIX}.chr${chr}.${REF_SUFFIX}"
    [[ -s "${ref}" ]] || { echo "ERROR: missing reference: ${ref}" >&2; exit 1; }
    index_vcf "${ref}"
    "${BCFTOOLS_BIN}" view -h "${ref}" >/dev/null
    sample_count=$("${BCFTOOLS_BIN}" query -l "${ref}" | wc -l)
    if [[ "${sample_count}" -ne 359 ]]; then
        echo "WARNING chr${chr}: reference sample count is ${sample_count}, expected 359"
    fi
    set +o pipefail
    gt_probe=$("${BCFTOOLS_BIN}" query -f '[%GT\n]' "${ref}" 2>/dev/null | head -n 5000 || true)
    set -o pipefail
    read -r phased_probe unphased_probe < <(
        awk '
        $0=="./." || $0==".|." || $0=="." {next}
        index($0,"|"){p++}
        index($0,"/"){u++}
        END{print p+0,u+0}
        ' <<<"${gt_probe}"
    )
    if [[ "${unphased_probe}" -gt 0 ]]; then
        echo "ERROR chr${chr}: unphased reference GT detected" >&2
        exit 1
    fi
    [[ "${phased_probe}" -gt 0 ]] || {
        echo "ERROR chr${chr}: phased reference GT was not detected" >&2
        exit 1
    }
    echo "REFERENCE_OK chr${chr} samples=${sample_count}"
done

export PIPE_PATIENT_VCF="${PATIENT_VCF}"
export PIPE_REF_DIR="${REF_DIR}"
export PIPE_OUT_DIR="${OUT_DIR}"
export PIPE_BEAGLE_JAR="${BEAGLE_JAR}"
export PIPE_SAMPLE_ID="${SAMPLE_ID}"
export PIPE_JAVA_BIN="${JAVA_BIN}"
export PIPE_BCFTOOLS_BIN="${BCFTOOLS_BIN}"
export PIPE_PYTHON_BIN="${PYTHON_BIN}"
export PIPE_REF_PREFIX="${REF_PREFIX}"
export PIPE_REF_SUFFIX="${REF_SUFFIX}"
export PIPE_BEAGLE_THREADS="${BEAGLE_THREADS}"
export PIPE_JAVA_HEAP_GB="${JAVA_HEAP_GB}"
export PIPE_SEED_BASE="${SEED_BASE}"
export PIPE_KEEP_INTERMEDIATE="${KEEP_INTERMEDIATE}"
export PIPE_RESUME="${RESUME}"
export PIPE_MERGER="${MERGER}"

fail=0
running=0
for chr in "${chroms[@]}"; do
    "${WORKER}" "${chr}" &
    running=$((running + 1))
    if (( running >= CHR_JOBS )); then
        wait -n || fail=1
        running=$((running - 1))
    fi
done
while (( running > 0 )); do
    wait -n || fail=1
    running=$((running - 1))
done
[[ "${fail}" -eq 0 ]] || { echo "ERROR: one or more chromosome jobs failed" >&2; exit 1; }

SUMMARY="${OUT_DIR}/logs/allchr_refsupport_summary.tsv"
{
    echo -e 'chrom\toriginal_sites\toriginal_GT_phased\toriginal_GT_unphased\tfinal_sites\tBEAGLE_PHASED_1\tBEAGLE_PHASED_0\tCHN_POLYMORPHIC\tCHN_MONOMORPHIC_REF\tCHN_ALLELE_MISMATCH\tCHN_NOT_IN_REF\tCONF_HIGH\tCONF_LOW\tCONF_UNPHASED\tfinal_GT_phased\tfinal_GT_unphased\tIMP_sites\torder_match\telapsed_seconds'
    for chr in "${chroms[@]}"; do
        cat "${OUT_DIR}/logs/${SAMPLE_ID}.chr${chr}.summary_row.tsv"
    done
} >"${SUMMARY}"

if [[ "${CHROMOSOMES_SPEC}" == auto || "${CHROMOSOMES_SPEC}" == all ]]; then
    merged_label="auto"
elif [[ "${CHROMOSOMES}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
    merged_label="${BASH_REMATCH[1]}_${BASH_REMATCH[2]}"
else
    merged_label=$(tr ',' '_' <<<"${CHROMOSOMES}")
fi
MERGED="${OUT_DIR}/${SAMPLE_ID}.chr${merged_label}.original_sites.beagle_phase_merged.refsupport.vcf.gz"
inputs=()
for chr in "${chroms[@]}"; do
    inputs+=("${OUT_DIR}/final_refsupport/${SAMPLE_ID}.chr${chr}.original_sites.beagle_phase_merged.refsupport.vcf.gz")
done
rm -f "${MERGED}" "${MERGED}.tbi" "${MERGED}.csi"
if [[ "${#inputs[@]}" -eq 1 ]]; then
    "${BCFTOOLS_BIN}" view -Oz -o "${MERGED}" "${inputs[0]}"
else
    "${BCFTOOLS_BIN}" concat -a -Oz -o "${MERGED}" "${inputs[@]}"
fi
"${BCFTOOLS_BIN}" index -f -t "${MERGED}" || "${BCFTOOLS_BIN}" index -f -c "${MERGED}"

total_elapsed=$(( $(date +%s) - pipeline_start ))
FINAL_SUMMARY="${OUT_DIR}/logs/final_merged_summary.txt"
awk -F '\t' -v elapsed="${total_elapsed}" -v merged="${MERGED}" '
NR==1 {next}
{
  n++; orig+=$2; final+=$5; b1+=$6; b0+=$7; poly+=$8; mono+=$9;
  mismatch+=$10; absent+=$11; high+=$12; low+=$13; unpconf+=$14;
  phased+=$15; unphased+=$16; imp+=$17
}
END {
  print "chromosomes_completed=" n
  print "original_sites=" orig
  print "final_sites=" final
  print "BEAGLE_PHASED_1=" b1
  print "BEAGLE_PHASED_0=" b0
  print "CHN_REF_SUPPORT_POLYMORPHIC=" poly
  print "CHN_REF_SUPPORT_MONOMORPHIC_REF=" mono
  print "CHN_REF_SUPPORT_ALLELE_MISMATCH=" mismatch
  print "CHN_REF_SUPPORT_NOT_IN_REF=" absent
  print "PHASING_CONFIDENCE_HIGH=" high
  print "PHASING_CONFIDENCE_LOW=" low
  print "PHASING_CONFIDENCE_UNPHASED=" unpconf
  print "final_GT_phased=" phased
  print "final_GT_unphased=" unphased
  print "IMP_sites=" imp
  print "total_elapsed_seconds=" elapsed
  print "merged_vcf=" merged
}' "${SUMMARY}" >"${FINAL_SUMMARY}"

cat "${FINAL_SUMMARY}"
echo "[$(date '+%F %T')] Pipeline completed"
