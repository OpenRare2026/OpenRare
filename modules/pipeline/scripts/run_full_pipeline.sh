#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=config/paths.sh
source "${ROOT}/config/paths.sh"

PHASING_SCRIPT="${ROOT}/modules/phasing_beagle_refsupport/scripts/run_beagle_refsupport_pipeline.sh"
PREPROCESS_SCRIPT="${ROOT}/modules/vcf_preprocessing/run_vcf_preprocessing.sh"
LIFTOVER_PY="${OPENRARE_LIFTOVER_SCRIPT}"
PSEUDOGENE_PY="${ROOT}/modules/pseudogene_annotation/scripts/annotate_pseudogene.py"
VEP_SCRIPT="${ROOT}/modules/vep_runner/scripts/run_vep_to_csv.py"
INFO_TO_CSV_SCRIPT="${ROOT}/modules/vcf_info_to_csv/scripts/add_vcf_info_to_vep_csv.py"
ENSURE_HEADERS_SCRIPT="${ROOT}/modules/vcf_preprocessing/scripts/ensure_vcf_info_headers.py"
GENOS_EVEE_SCRIPT="${ROOT}/modules/genos_evee_annotation/scripts/add_genos_evee_to_csv.py"
HLA_FILTER_SCRIPT="${ROOT}/modules/hla_filter/scripts/filter_hla_region_csv.py"
# SORT_CSV_SCRIPT="${ROOT}/modules/result_sorting/scripts/sort_vep_csv.py"
VEP_CONFIG="${ROOT}/modules/vep_runner/config/vep_runner_config.json"

usage() {
  cat <<'EOF'
Usage:
  run_full_pipeline.sh --input-vcf FILE --out-dir DIR [--fork N]

Required:
  --input-vcf FILE          Input patient VCF/VCF.GZ; .vcf is automatically bgzip-compressed and indexed
  --out-dir DIR             Output directory

Common optional:
  --fork N                  VEP fork count, default: 1
  --hpo-id ID               Optional patient HPO ID(s) for phenotype-aware transcript selection; comma-separated is allowed
  --phasing yes|no          Whether to run Beagle phasing before preprocessing; default: yes
  --vaf yes|no              Whether to add VAF/REF_DP/ALT_DP before VEP; default: yes
  --regulatory-annotation yes|no  Whether to add ENCODE cCRE INFO fields before VEP; default: yes
  --ncrna-annotation yes|no       Whether to add GENCODE ncRNA INFO fields before VEP; default: yes
  --pseudogene-annotation yes|no  Whether to run pseudogene annotation before VEP; default: yes
  --hla-filter yes|no       Whether to remove GRCh38 HLA/MHC rows from final wide CSV; default: yes

Advanced optional overrides, usually not needed:
  --sample-id ID            Sample ID used for output prefixes; default: auto
  --chromosomes SPEC        Default: 1-22. Example: 22, 1-22, or 1,3,5
  --ref-dir DIR             CHN reference panel directory for Beagle phasing
  --beagle-jar FILE         Beagle jar path
  --ccre-bed FILE           cCRE slim BED.GZ
  --ncrna-bed FILE          GENCODE ncRNA slim BED.GZ
  --chr-jobs N              Concurrent chromosomes for phasing, default: 1
  --beagle-threads N        Threads per Beagle process, default: 4
  --java-heap-gb N          Java heap per Beagle process, default: 12
  --java-bin PATH           Java executable for Beagle
  --top-k-transcripts N     VEP transcript selection count, default: 5
  --clinical-tissue NAME    Optional clinical tissue for VEP runner
  --genos-evee-db FILE      Indexed GENOS-EVEE CPRA TSV.GZ; default: resource/genos_evee/genos_evee.cpra.tsv.gz
  --keep-raw-vep yes|no     Keep raw VEP TSV, default: yes
  --input-assembly SPEC     Input assembly: auto, GRCh37, or GRCh38 (default: auto)
  --dry-run                 Print commands only
EOF
}

INPUT_VCF=""
OUT_DIR=""
SAMPLE_ID="auto"
REF_DIR="${FULL_PIPELINE_REF_DIR}"
BEAGLE_JAR="${FULL_PIPELINE_BEAGLE_JAR}"
CHROMOSOMES="1-22"
JAVA_BIN="${JAVA_BIN:-java}"
CCRE_BED="${ROOT}/modules/vcf_preprocessing/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz"
NCRNA_BED="${ROOT}/modules/vcf_preprocessing/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz"
FORK=1
CHR_JOBS=1
BEAGLE_THREADS=4
JAVA_HEAP_GB=12
TOP_K_TRANSCRIPTS=5
HPO_ID=""
CLINICAL_TISSUE=""
GENOS_EVEE_DB="${FULL_PIPELINE_GENOS_EVEE_DB}"
KEEP_RAW_VEP=yes
INPUT_ASSEMBLY="auto"
PHASING=yes
VAF=yes
REGULATORY_ANNOTATION=yes
NCRNA_ANNOTATION=yes
PSEUDOGENE_ANNOTATION=yes
HLA_FILTER=yes
DRY_RUN=no

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input-vcf) INPUT_VCF="${2:?}"; shift 2 ;;
    --out-dir) OUT_DIR="${2:?}"; shift 2 ;;
    --sample-id) SAMPLE_ID="${2:?}"; shift 2 ;;
    --ref-dir) REF_DIR="${2:?}"; shift 2 ;;
    --beagle-jar) BEAGLE_JAR="${2:?}"; shift 2 ;;
    --chromosomes) CHROMOSOMES="${2:?}"; shift 2 ;;
    --ccre-bed) CCRE_BED="${2:?}"; shift 2 ;;
    --ncrna-bed) NCRNA_BED="${2:?}"; shift 2 ;;
    --fork) FORK="${2:?}"; shift 2 ;;
    --chr-jobs) CHR_JOBS="${2:?}"; shift 2 ;;
    --beagle-threads) BEAGLE_THREADS="${2:?}"; shift 2 ;;
    --java-heap-gb) JAVA_HEAP_GB="${2:?}"; shift 2 ;;
    --java-bin) JAVA_BIN="${2:?}"; shift 2 ;;
    --top-k-transcripts) TOP_K_TRANSCRIPTS="${2:?}"; shift 2 ;;
    --hpo-id) HPO_ID="${2:?}"; shift 2 ;;
    --phasing) PHASING="${2:?}"; shift 2 ;;
    --vaf) VAF="${2:?}"; shift 2 ;;
    --regulatory-annotation) REGULATORY_ANNOTATION="${2:?}"; shift 2 ;;
    --ncrna-annotation) NCRNA_ANNOTATION="${2:?}"; shift 2 ;;
    --pseudogene-annotation) PSEUDOGENE_ANNOTATION="${2:?}"; shift 2 ;;
    --hla-filter) HLA_FILTER="${2:?}"; shift 2 ;;
    --clinical-tissue) CLINICAL_TISSUE="${2:?}"; shift 2 ;;
    --genos-evee-db) GENOS_EVEE_DB="${2:?}"; shift 2 ;;
    --keep-raw-vep) KEEP_RAW_VEP="${2:?}"; shift 2 ;;
    --input-assembly) INPUT_ASSEMBLY="${2:?}"; shift 2 ;;
    --dry-run) DRY_RUN=yes; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for name in INPUT_VCF OUT_DIR; do
  [[ -n "${!name}" ]] || { echo "ERROR: --${name,,} is required" >&2; usage >&2; exit 2; }
done
[[ -s "$INPUT_VCF" ]] || { echo "ERROR: input VCF not found: $INPUT_VCF" >&2; exit 1; }

norm_bool() {
  case "$1" in
    yes|YES|true|TRUE|1|on|ON) echo yes ;;
    no|NO|false|FALSE|0|off|OFF) echo no ;;
    *) echo "ERROR: $2 must be yes or no, got: $1" >&2; exit 2 ;;
  esac
}
PHASING="$(norm_bool "$PHASING" --phasing)"
VAF="$(norm_bool "$VAF" --vaf)"
REGULATORY_ANNOTATION="$(norm_bool "$REGULATORY_ANNOTATION" --regulatory-annotation)"
NCRNA_ANNOTATION="$(norm_bool "$NCRNA_ANNOTATION" --ncrna-annotation)"
PSEUDOGENE_ANNOTATION="$(norm_bool "$PSEUDOGENE_ANNOTATION" --pseudogene-annotation)"
HLA_FILTER="$(norm_bool "$HLA_FILTER" --hla-filter)"

if [[ "$PHASING" == yes ]]; then
  [[ -d "$REF_DIR" ]] || { echo "ERROR: ref dir not found: $REF_DIR" >&2; exit 1; }
  [[ -s "$BEAGLE_JAR" ]] || { echo "ERROR: Beagle jar not found: $BEAGLE_JAR" >&2; exit 1; }
  if [[ "$JAVA_BIN" != */* ]]; then
    resolved_java="$(command -v "$JAVA_BIN" || true)"
    if [[ -n "$resolved_java" ]]; then
      JAVA_BIN="$resolved_java"
    fi
  fi
  [[ -x "$JAVA_BIN" ]] || { echo "ERROR: Java executable not found: $JAVA_BIN" >&2; exit 1; }
fi
[[ -s "$CCRE_BED" ]] || { echo "ERROR: cCRE BED not found: $CCRE_BED" >&2; exit 1; }
[[ -s "$NCRNA_BED" ]] || { echo "ERROR: ncRNA BED not found: $NCRNA_BED" >&2; exit 1; }
[[ -s "$VEP_CONFIG" ]] || { echo "ERROR: VEP config not found: $VEP_CONFIG" >&2; exit 1; }
[[ -s "$PSEUDOGENE_PY" ]] || { echo "ERROR: pseudogene script not found: $PSEUDOGENE_PY" >&2; exit 1; }
[[ -s "$INFO_TO_CSV_SCRIPT" ]] || { echo "ERROR: INFO-to-CSV script not found: $INFO_TO_CSV_SCRIPT" >&2; exit 1; }
[[ -s "$ENSURE_HEADERS_SCRIPT" ]] || { echo "ERROR: ensure-header script not found: $ENSURE_HEADERS_SCRIPT" >&2; exit 1; }
[[ -s "$GENOS_EVEE_SCRIPT" ]] || { echo "ERROR: GENOS-EVEE annotation script not found: $GENOS_EVEE_SCRIPT" >&2; exit 1; }
[[ -s "$HLA_FILTER_SCRIPT" ]] || { echo "ERROR: HLA filter script not found: $HLA_FILTER_SCRIPT" >&2; exit 1; }
case "$INPUT_ASSEMBLY" in
  auto|GRCh37|GRCh38) ;;
  *)
    echo "ERROR: --input-assembly must be auto, GRCh37, or GRCh38: $INPUT_ASSEMBLY" >&2
    exit 2
    ;;
esac

mkdir -p "$OUT_DIR"/{00_input,00_liftover,01_phasing,02_vcf_preprocessing,03_pseudogene_annotation,04_vep,05_vcf_info_to_csv,06_genos_evee_annotation,07_hla_filter,logs}
LOG="${OUT_DIR}/logs/full_pipeline.log"
SUMMARY="${OUT_DIR}/full_pipeline.outputs.tsv"
exec > >(tee -a "$LOG") 2>&1

run_cmd() {
  printf '[%s] CMD:' "$(date '+%F %T')"
  printf ' %q' "$@"
  printf '\n'
  if [[ "$DRY_RUN" != yes ]]; then
    "$@"
  fi
}

PIPELINE_INPUT_VCF=""
normalize_input_vcf() {
  local source_vcf="$1"
  case "$source_vcf" in
    *.vcf.gz|*.VCF.GZ)
      PIPELINE_INPUT_VCF="$source_vcf"
      if [[ ! -s "${PIPELINE_INPUT_VCF}.tbi" && ! -s "${PIPELINE_INPUT_VCF}.csi" ]]; then
        if command -v bcftools >/dev/null 2>&1; then
          run_cmd bcftools index -f -t "$PIPELINE_INPUT_VCF"
        else
          run_cmd tabix -f -p vcf "$PIPELINE_INPUT_VCF"
        fi
      fi
      ;;
    *.vcf|*.VCF)
      local base
      base="$(basename "$source_vcf")"
      base="${base%.[vV][cC][fF]}"
      PIPELINE_INPUT_VCF="${OUT_DIR}/00_input/${base}.vcf.gz"
      if [[ "$DRY_RUN" == yes ]]; then
        run_cmd bgzip -f -c "$source_vcf" '>' "$PIPELINE_INPUT_VCF"
      else
        printf '[%s] CMD:' "$(date '+%F %T')"
        printf ' %q' bgzip -f -c "$source_vcf"
        printf ' > %q\n' "$PIPELINE_INPUT_VCF"
        bgzip -f -c "$source_vcf" > "$PIPELINE_INPUT_VCF"
      fi
      if command -v bcftools >/dev/null 2>&1; then
        run_cmd bcftools index -f -t "$PIPELINE_INPUT_VCF"
      else
        run_cmd tabix -f -p vcf "$PIPELINE_INPUT_VCF"
      fi
      ;;
    *)
      echo "ERROR: input VCF must end with .vcf or .vcf.gz: $source_vcf" >&2
      exit 2
      ;;
  esac
}

normalize_input_vcf "$INPUT_VCF"

resolved_assembly="$INPUT_ASSEMBLY"
liftover_vcf=""
liftover_manifest=""
if [[ "$resolved_assembly" == auto ]]; then
  if [[ "$DRY_RUN" == yes ]]; then
    resolved_assembly="GRCh38"
    echo "[liftover] dry-run: assuming GRCh38 (auto-detect skipped)"
  else
    resolved_assembly="$(python3 "$LIFTOVER_PY" --input "$PIPELINE_INPUT_VCF" --detect-only)"
    echo "[liftover] auto-detected assembly: ${resolved_assembly}"
  fi
fi

if [[ "$resolved_assembly" == GRCh37 ]]; then
  liftover_dir="${OUT_DIR}/00_liftover"
  liftover_manifest="${liftover_dir}/liftover.manifest.json"
  [[ -s "$LIFTOVER_PY" ]] || { echo "ERROR: liftover script not found: $LIFTOVER_PY" >&2; exit 1; }
  [[ -s "$LIFTOVER_JAR" ]] || { echo "ERROR: LIFTOVER_JAR not found: $LIFTOVER_JAR" >&2; exit 1; }
  [[ -s "$LIFTOVER_CONFIG" ]] || { echo "ERROR: LIFTOVER_CONFIG not found: $LIFTOVER_CONFIG" >&2; exit 1; }
  if [[ "$DRY_RUN" == yes ]]; then
    run_cmd python3 "$LIFTOVER_PY" \
      --input "$PIPELINE_INPUT_VCF" \
      --out-dir "$liftover_dir" \
      --normalize true \
      --force true \
      --log-json "$liftover_manifest"
    liftover_vcf="${liftover_dir}/output/output.grch38.norm.vcf.gz"
  else
    mapfile -t liftover_lines < <(
      python3 "$LIFTOVER_PY" \
        --input "$PIPELINE_INPUT_VCF" \
        --out-dir "$liftover_dir" \
        --normalize true \
        --force true \
        --log-json "$liftover_manifest"
    )
    liftover_vcf="${liftover_lines[-1]}"
    [[ -s "$liftover_vcf" ]] || { echo "ERROR: liftover output missing: $liftover_vcf" >&2; exit 1; }
  fi
  PIPELINE_INPUT_VCF="$liftover_vcf"
  echo "[liftover] using GRCh38 VCF: $PIPELINE_INPUT_VCF"
elif [[ "$resolved_assembly" == GRCh38 ]]; then
  echo "[liftover] skipped (input assembly GRCh38)"
else
  echo "[liftover] skipped (assembly=${resolved_assembly}; expected GRCh37 to liftover)"
fi

sample_arg=()
if [[ "$SAMPLE_ID" != auto ]]; then
  sample_arg=(--sample-id "$SAMPLE_ID")
fi

phased_vcf=""
if [[ "$PHASING" == yes ]]; then
  run_cmd bash "$PHASING_SCRIPT" \
    --patient-vcf "$PIPELINE_INPUT_VCF" \
    --ref-dir "$REF_DIR" \
    --out-dir "${OUT_DIR}/01_phasing" \
    --beagle-jar "$BEAGLE_JAR" \
    --chromosomes "$CHROMOSOMES" \
    "${sample_arg[@]}" \
    --chr-jobs "$CHR_JOBS" \
    --beagle-threads "$BEAGLE_THREADS" \
    --java-heap-gb "$JAVA_HEAP_GB" \
    --java-bin "$JAVA_BIN" \
    --resume yes

  if [[ "$DRY_RUN" == yes ]]; then
    phased_vcf="${OUT_DIR}/01_phasing/<sample>.chr<chromosomes>.original_sites.beagle_phase_merged.refsupport.vcf.gz"
  else
    mapfile -t phased_candidates < <(find "${OUT_DIR}/01_phasing" -maxdepth 1 -type f -name '*.original_sites.beagle_phase_merged.refsupport.vcf.gz' | sort)
    [[ "${#phased_candidates[@]}" -eq 1 ]] || { echo "ERROR: expected one phased VCF, found ${#phased_candidates[@]}" >&2; exit 1; }
    phased_vcf="${phased_candidates[0]}"
  fi
else
  phased_vcf="${OUT_DIR}/01_phasing/input.with_phasing_headers.vcf.gz"
  printf '[%s] SKIP phasing: adding expected phasing INFO headers only: %s\n' "$(date '+%F %T')" "$phased_vcf"
  run_cmd python3 "$ENSURE_HEADERS_SCRIPT" --input-vcf "$PIPELINE_INPUT_VCF" --output-vcf "$phased_vcf" --groups phasing --index
fi

pre_prefix="${OUT_DIR}/02_vcf_preprocessing/preprocessed"
pre_sample=""
[[ "$SAMPLE_ID" != auto ]] && pre_sample="$SAMPLE_ID"
run_cmd bash "$PREPROCESS_SCRIPT" "$phased_vcf" "$pre_prefix" "$pre_sample" "$CCRE_BED" "$NCRNA_BED" \
  --vaf "$VAF" \
  --regulatory-annotation "$REGULATORY_ANNOTATION" \
  --ncrna-annotation "$NCRNA_ANNOTATION"
preprocessed_vcf="${pre_prefix}.regulatory.vcf.gz"

pseudo_input_vcf="${OUT_DIR}/03_pseudogene_annotation/preprocessed.regulatory.for_pseudogene.vcf"
pseudo_vcf="${OUT_DIR}/03_pseudogene_annotation/preprocessed.pseudogene_annotated.vcf.gz"
pseudo_plain_vcf="${OUT_DIR}/03_pseudogene_annotation/preprocessed.pseudogene_annotated.vcf"
pseudo_log_json="${OUT_DIR}/03_pseudogene_annotation/pseudogene_annotation.log.json"
pseudo_sample=""
[[ "$SAMPLE_ID" != auto ]] && pseudo_sample="$SAMPLE_ID"
rm -f "$pseudo_input_vcf" "$pseudo_plain_vcf" "$pseudo_vcf" "${pseudo_vcf}.tbi" "${pseudo_vcf}.csi"
if [[ "$PSEUDOGENE_ANNOTATION" == yes ]]; then
  run_cmd bcftools view -Ov -o "$pseudo_input_vcf" "$preprocessed_vcf"
  pseudo_cmd=(python3 "$PSEUDOGENE_PY" --input "$pseudo_input_vcf" --output "$pseudo_plain_vcf" --log-json "$pseudo_log_json")
  if [[ -n "$pseudo_sample" ]]; then
    pseudo_cmd+=(--sample-name "$pseudo_sample")
  fi
  run_cmd "${pseudo_cmd[@]}"
  if [[ "$DRY_RUN" == yes ]]; then
    run_cmd bgzip -f -c "$pseudo_plain_vcf" '>' "$pseudo_vcf"
  else
    printf '[%s] CMD:' "$(date '+%F %T')"
    printf ' %q' bgzip -f -c "$pseudo_plain_vcf"
    printf ' > %q\n' "$pseudo_vcf"
    bgzip -f -c "$pseudo_plain_vcf" > "$pseudo_vcf"
    rm -f "$pseudo_plain_vcf" "$pseudo_input_vcf"
    if command -v bcftools >/dev/null 2>&1; then
      run_cmd bcftools index -f -t "$pseudo_vcf"
    else
      run_cmd tabix -f -p vcf "$pseudo_vcf"
    fi
  fi
else
  printf '[%s] SKIP pseudogene annotation: adding expected pseudogene INFO headers only: %s\n' "$(date '+%F %T')" "$pseudo_vcf"
  printf '{"status":"skipped","output":"%s"}\n' "$pseudo_vcf" > "$pseudo_log_json"
  run_cmd python3 "$ENSURE_HEADERS_SCRIPT" --input-vcf "$preprocessed_vcf" --output-vcf "$pseudo_vcf" --groups pseudogene --index
fi

vep_base_csv="${OUT_DIR}/04_vep/vep_output.base.csv"
vep_log="${OUT_DIR}/04_vep/vep.log"
raw_vep="${OUT_DIR}/04_vep/raw_vep.tsv"
vep_info_csv="${OUT_DIR}/05_vcf_info_to_csv/vep_output.with_info.csv"
vep_info_log="${OUT_DIR}/05_vcf_info_to_csv/vcf_info_to_csv.log.json"
vep_evee_csv="${OUT_DIR}/06_genos_evee_annotation/vep_output.with_genos_evee.csv"
vep_evee_log="${OUT_DIR}/06_genos_evee_annotation/genos_evee_annotation.log.json"
hla_filtered_csv="${OUT_DIR}/07_hla_filter/vep_output.no_hla.csv"
hla_filter_log="${OUT_DIR}/07_hla_filter/hla_filter.log.json"
# Final sorting is intentionally disabled. The HLA-filtered GENOS-EVEE wide table is the final CSV when HLA_FILTER=yes.
vep_csv="$vep_evee_csv"
vep_cmd=(python3 "$VEP_SCRIPT" -i "$pseudo_vcf" -o "$vep_base_csv" --config "$VEP_CONFIG" --format vcf --hgvs --fork "$FORK" --top-k-transcripts "$TOP_K_TRANSCRIPTS" --no-pseudogene-annotation --no-regulatory-annotation --no-vcf-info-to-csv --no-pathogenic-ranking --log "$vep_log")
if [[ "$KEEP_RAW_VEP" == yes ]]; then
  vep_cmd+=(--keep-vep "$raw_vep")
fi
if [[ -n "$HPO_ID" ]]; then
  vep_cmd+=(--hpo-id "$HPO_ID")
fi
if [[ -n "$CLINICAL_TISSUE" ]]; then
  vep_cmd+=(--clinical-tissue "$CLINICAL_TISSUE")
fi
run_cmd "${vep_cmd[@]}"

info_to_csv_cmd=(python3 "$INFO_TO_CSV_SCRIPT" \
  --input-csv "$vep_base_csv" \
  --input-vcf "$pseudo_vcf" \
  --output-csv "$vep_info_csv" \
  --log-json "$vep_info_log")
if [[ "$SAMPLE_ID" != auto ]]; then
  info_to_csv_cmd+=(--sample-name "$SAMPLE_ID")
fi
run_cmd "${info_to_csv_cmd[@]}"

genos_evee_cmd=(python3 "$GENOS_EVEE_SCRIPT" \
  --input-csv "$vep_info_csv" \
  --output-csv "$vep_evee_csv" \
  --log-json "$vep_evee_log")
if [[ -s "$GENOS_EVEE_DB" ]]; then
  [[ -s "${GENOS_EVEE_DB}.tbi" ]] || { echo "ERROR: GENOS-EVEE database index not found: ${GENOS_EVEE_DB}.tbi" >&2; exit 1; }
  genos_evee_cmd+=(--database "$GENOS_EVEE_DB")
else
  echo "WARNING: GENOS-EVEE database not found; GENOS-EVEE column will be filled with '-': $GENOS_EVEE_DB"
fi
run_cmd "${genos_evee_cmd[@]}"

if [[ "$HLA_FILTER" == yes ]]; then
  run_cmd python3 "$HLA_FILTER_SCRIPT" --input-csv "$vep_evee_csv" --output-csv "$hla_filtered_csv" --log-json "$hla_filter_log"
  vep_csv="$hla_filtered_csv"
else
  printf '[%s] SKIP HLA filter: keeping GENOS-EVEE wide CSV: %s\n' "$(date '+%F %T')" "$vep_csv"
fi

{
  printf 'step\tpath\n'
  printf 'original_input_vcf\t%s\n' "$INPUT_VCF"
  printf 'input_vcf_gz\t%s\n' "$PIPELINE_INPUT_VCF"
  if [[ -n "$liftover_vcf" ]]; then
    printf 'liftover_vcf\t%s\n' "$liftover_vcf"
    printf 'liftover_manifest\t%s\n' "$liftover_manifest"
  fi
  printf 'input_assembly\t%s\n' "$resolved_assembly"
  printf 'phasing\t%s\n' "$PHASING"
  printf 'vaf\t%s\n' "$VAF"
  printf 'regulatory_annotation\t%s\n' "$REGULATORY_ANNOTATION"
  printf 'ncrna_annotation\t%s\n' "$NCRNA_ANNOTATION"
  printf 'pseudogene_annotation\t%s\n' "$PSEUDOGENE_ANNOTATION"
  printf 'hla_filter\t%s\n' "$HLA_FILTER"
  printf 'phased_vcf\t%s\n' "$phased_vcf"
  printf 'preprocessed_vcf\t%s\n' "$preprocessed_vcf"
  printf 'pseudogene_annotated_vcf\t%s\n' "$pseudo_vcf"
  printf 'vep_base_csv\t%s\n' "$vep_base_csv"
  printf 'vep_info_csv\t%s\n' "$vep_info_csv"
  printf 'genos_evee_database\t%s\n' "$GENOS_EVEE_DB"
  printf 'vep_genos_evee_csv\t%s\n' "$vep_evee_csv"
  printf 'hla_filtered_csv\t%s\n' "$hla_filtered_csv"
  printf 'vep_csv\t%s\n' "$vep_csv"
  printf 'vep_log\t%s\n' "$vep_log"
  printf 'vcf_info_to_csv_log\t%s\n' "$vep_info_log"
  printf 'genos_evee_annotation_log\t%s\n' "$vep_evee_log"
  printf 'hla_filter_log\t%s\n' "$hla_filter_log"
  printf 'full_log\t%s\n' "$LOG"
} > "$SUMMARY"
cat "$SUMMARY"
