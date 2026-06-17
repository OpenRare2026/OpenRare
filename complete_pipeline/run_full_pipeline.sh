#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PHASING_SCRIPT="${ROOT}/modules/phasing_beagle_refsupport/scripts/run_beagle_refsupport_pipeline.sh"
PREPROCESS_SCRIPT="${ROOT}/modules/vcf_preprocessing/run_vcf_preprocessing.sh"
PSEUDOGENE_PY="${ROOT}/modules/pseudogene_annotation/scripts/annotate_pseudogene.py"
VEP_SCRIPT="${ROOT}/modules/vep_runner/scripts/run_vep_to_csv.py"
INFO_TO_CSV_SCRIPT="${ROOT}/modules/vcf_info_to_csv/scripts/add_vcf_info_to_vep_csv.py"
SORT_CSV_SCRIPT="${ROOT}/modules/result_sorting/scripts/sort_vep_csv.py"
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
  --keep-raw-vep yes|no     Keep raw VEP TSV, default: yes
  --dry-run                 Print commands only
EOF
}

INPUT_VCF=""
OUT_DIR=""
SAMPLE_ID="auto"
REF_DIR="/mnt/workspace/changan/1kgp/beagle_pipeline_param/packages/CHN_ref"
BEAGLE_JAR="/mnt/workspace/changan/1kgp/beagle.27Feb25.75f.jar"
CHROMOSOMES="1-22"
JAVA_BIN="/mnt/workspace/pangjiangshuan/vep_runner/envs/vep/lib/jvm/bin/java"
CCRE_BED="${ROOT}/modules/vcf_preprocessing/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz"
NCRNA_BED="${ROOT}/modules/vcf_preprocessing/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz"
FORK=1
CHR_JOBS=1
BEAGLE_THREADS=4
JAVA_HEAP_GB=12
TOP_K_TRANSCRIPTS=5
HPO_ID=""
CLINICAL_TISSUE=""
KEEP_RAW_VEP=yes
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
    --clinical-tissue) CLINICAL_TISSUE="${2:?}"; shift 2 ;;
    --keep-raw-vep) KEEP_RAW_VEP="${2:?}"; shift 2 ;;
    --dry-run) DRY_RUN=yes; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for name in INPUT_VCF OUT_DIR; do
  [[ -n "${!name}" ]] || { echo "ERROR: --${name,,} is required" >&2; usage >&2; exit 2; }
done
[[ -s "$INPUT_VCF" ]] || { echo "ERROR: input VCF not found: $INPUT_VCF" >&2; exit 1; }
[[ -d "$REF_DIR" ]] || { echo "ERROR: ref dir not found: $REF_DIR" >&2; exit 1; }
[[ -s "$BEAGLE_JAR" ]] || { echo "ERROR: Beagle jar not found: $BEAGLE_JAR" >&2; exit 1; }
[[ -x "$JAVA_BIN" ]] || { echo "ERROR: Java executable not found: $JAVA_BIN" >&2; exit 1; }
[[ -s "$CCRE_BED" ]] || { echo "ERROR: cCRE BED not found: $CCRE_BED" >&2; exit 1; }
[[ -s "$NCRNA_BED" ]] || { echo "ERROR: ncRNA BED not found: $NCRNA_BED" >&2; exit 1; }
[[ -s "$VEP_CONFIG" ]] || { echo "ERROR: VEP config not found: $VEP_CONFIG" >&2; exit 1; }
[[ -s "$PSEUDOGENE_PY" ]] || { echo "ERROR: pseudogene script not found: $PSEUDOGENE_PY" >&2; exit 1; }
[[ -s "$INFO_TO_CSV_SCRIPT" ]] || { echo "ERROR: INFO-to-CSV script not found: $INFO_TO_CSV_SCRIPT" >&2; exit 1; }
[[ -s "$SORT_CSV_SCRIPT" ]] || { echo "ERROR: result sorting script not found: $SORT_CSV_SCRIPT" >&2; exit 1; }

mkdir -p "$OUT_DIR"/{00_input,01_phasing,02_vcf_preprocessing,03_pseudogene_annotation,04_vep,05_vcf_info_to_csv,06_result_sorting,logs}
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

sample_arg=()
if [[ "$SAMPLE_ID" != auto ]]; then
  sample_arg=(--sample-id "$SAMPLE_ID")
fi

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

phased_vcf=""
if [[ "$DRY_RUN" == yes ]]; then
  phased_vcf="${OUT_DIR}/01_phasing/<sample>.chr<chromosomes>.original_sites.beagle_phase_merged.refsupport.vcf.gz"
else
  mapfile -t phased_candidates < <(find "${OUT_DIR}/01_phasing" -maxdepth 1 -type f -name '*.original_sites.beagle_phase_merged.refsupport.vcf.gz' | sort)
  [[ "${#phased_candidates[@]}" -eq 1 ]] || { echo "ERROR: expected one phased VCF, found ${#phased_candidates[@]}" >&2; exit 1; }
  phased_vcf="${phased_candidates[0]}"
fi

pre_prefix="${OUT_DIR}/02_vcf_preprocessing/preprocessed"
pre_sample=""
[[ "$SAMPLE_ID" != auto ]] && pre_sample="$SAMPLE_ID"
run_cmd bash "$PREPROCESS_SCRIPT" "$phased_vcf" "$pre_prefix" "$pre_sample" "$CCRE_BED" "$NCRNA_BED"
preprocessed_vcf="${pre_prefix}.regulatory.vcf.gz"

pseudo_input_vcf="${OUT_DIR}/03_pseudogene_annotation/preprocessed.regulatory.for_pseudogene.vcf"
pseudo_vcf="${OUT_DIR}/03_pseudogene_annotation/preprocessed.pseudogene_annotated.vcf.gz"
pseudo_plain_vcf="${OUT_DIR}/03_pseudogene_annotation/preprocessed.pseudogene_annotated.vcf"
pseudo_log_json="${OUT_DIR}/03_pseudogene_annotation/pseudogene_annotation.log.json"
pseudo_sample=""
[[ "$SAMPLE_ID" != auto ]] && pseudo_sample="$SAMPLE_ID"
rm -f "$pseudo_input_vcf" "$pseudo_plain_vcf" "$pseudo_vcf" "${pseudo_vcf}.tbi" "${pseudo_vcf}.csi"
if [[ "$DRY_RUN" == yes ]]; then
  run_cmd bcftools view -Ov -o "$pseudo_input_vcf" "$preprocessed_vcf"
else
  run_cmd bcftools view -Ov -o "$pseudo_input_vcf" "$preprocessed_vcf"
fi
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
  printf ' > %q
' "$pseudo_vcf"
  bgzip -f -c "$pseudo_plain_vcf" > "$pseudo_vcf"
  rm -f "$pseudo_plain_vcf" "$pseudo_input_vcf"
  if command -v bcftools >/dev/null 2>&1; then
    run_cmd bcftools index -f -t "$pseudo_vcf"
  else
    run_cmd tabix -f -p vcf "$pseudo_vcf"
  fi
fi

vep_base_csv="${OUT_DIR}/04_vep/vep_output.base.csv"
vep_log="${OUT_DIR}/04_vep/vep.log"
raw_vep="${OUT_DIR}/04_vep/raw_vep.tsv"
vep_info_csv="${OUT_DIR}/05_vcf_info_to_csv/vep_output.with_info.csv"
vep_info_log="${OUT_DIR}/05_vcf_info_to_csv/vcf_info_to_csv.log.json"
vep_csv="${OUT_DIR}/06_result_sorting/vep_output.sorted.csv"
vep_sort_log="${OUT_DIR}/06_result_sorting/result_sorting.log.json"
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

run_cmd python3 "$INFO_TO_CSV_SCRIPT" \
  --input-csv "$vep_base_csv" \
  --input-vcf "$pseudo_vcf" \
  --output-csv "$vep_info_csv" \
  --log-json "$vep_info_log"

run_cmd python3 "$SORT_CSV_SCRIPT" \
  --input-csv "$vep_info_csv" \
  --output-csv "$vep_csv" \
  --log-json "$vep_sort_log"

{
  printf 'step\tpath\n'
  printf 'original_input_vcf\t%s\n' "$INPUT_VCF"
  printf 'input_vcf_gz\t%s\n' "$PIPELINE_INPUT_VCF"
  printf 'phased_vcf\t%s\n' "$phased_vcf"
  printf 'preprocessed_vcf\t%s\n' "$preprocessed_vcf"
  printf 'pseudogene_annotated_vcf\t%s\n' "$pseudo_vcf"
  printf 'vep_base_csv\t%s\n' "$vep_base_csv"
  printf 'vep_info_csv\t%s\n' "$vep_info_csv"
  printf 'vep_csv\t%s\n' "$vep_csv"
  printf 'vep_log\t%s\n' "$vep_log"
  printf 'vcf_info_to_csv_log\t%s\n' "$vep_info_log"
  printf 'result_sorting_log\t%s\n' "$vep_sort_log"
  printf 'full_log\t%s\n' "$LOG"
} > "$SUMMARY"
cat "$SUMMARY"
