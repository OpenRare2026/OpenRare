from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = ROOT / "modules"
COMPLETE_PIPELINE_DIR = ROOT / "complete_pipeline"


class PhasingConfig:
    script: Path = MODULES_DIR / "phasing_beagle_refsupport" / "scripts" / "run_beagle_refsupport_pipeline.sh"
    ref_dir: Path = Path(os.getenv("PHASING_REF_DIR", "/mnt/workspace/changan/1kgp/beagle_pipeline_param/packages/CHN_ref"))
    beagle_jar: Path = Path(os.getenv("PHASING_BEAGLE_JAR", "/mnt/workspace/changan/1kgp/beagle.27Feb25.75f.jar"))
    java_bin: str = os.getenv("PHASING_JAVA_BIN", "/mnt/workspace/pangjiangshuan/vep_runner/envs/vep/lib/jvm/bin/java")
    chr_jobs: int = int(os.getenv("PHASING_CHR_JOBS", "1"))
    beagle_threads: int = int(os.getenv("PHASING_BEAGLE_THREADS", "4"))
    java_heap_gb: int = int(os.getenv("PHASING_JAVA_HEAP_GB", "12"))


class PreprocessingConfig:
    script: Path = MODULES_DIR / "vcf_preprocessing" / "run_vcf_preprocessing.sh"
    ccre_bed: Path = MODULES_DIR / "vcf_preprocessing" / "resources" / "regulatory" / "hg38" / "encode_screen_v4_grch38_ccre.slim.bed.gz"
    ncrna_bed: Path = MODULES_DIR / "vcf_preprocessing" / "resources" / "ncrna" / "hg38" / "gencode.v49.ncrna_gene.slim.bed.gz"


class PseudogeneConfig:
    script: Path = MODULES_DIR / "pseudogene_annotation" / "scripts" / "annotate_pseudogene.py"
    gencode_gtf: Path = Path(os.getenv(
        "PSEUDOGENE_GENCODE_GTF",
        "/mnt/workspace/xiongliwen/00.PublicData/Pseudogene/GENCODE/release_49/gencode.v49.2wayconspseudos.gtf.gz",
    ))
    pseudogene_org: Path = Path(os.getenv(
        "PSEUDOGENE_ORG",
        "/mnt/workspace/xiongliwen/00.PublicData/Pseudogene/Pseudogene.org/Human90/Human90.txt",
    ))
    hgnc: Path = Path(os.getenv(
        "PSEUDOGENE_HGNC",
        "/mnt/workspace/xiongliwen/00.PublicData/phenotype_hpo_v1/hgnc_complete_set.txt",
    ))


class VepConfig:
    script: Path = MODULES_DIR / "vep_runner" / "scripts" / "run_vep_to_csv.py"
    config_file: Path = MODULES_DIR / "vep_runner" / "config" / "vep_runner_config.json"
    fork: int = int(os.getenv("VEP_FORK", "1"))
    top_k_transcripts: int = int(os.getenv("VEP_TOP_K_TRANSCRIPTS", "5"))
    keep_raw_vep: bool = os.getenv("VEP_KEEP_RAW", "yes").lower() in ("yes", "true", "1")


class InfoToCsvConfig:
    script: Path = MODULES_DIR / "vcf_info_to_csv" / "scripts" / "add_vcf_info_to_vep_csv.py"


class SortingConfig:
    script: Path = MODULES_DIR / "result_sorting" / "scripts" / "sort_vep_csv.py"


class ApiConfig:
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "18081"))
    jobs_dir: Path = Path(os.getenv("API_JOBS_DIR", str(ROOT / "complete_pipeline" / "api_jobs")))
    title: str = "OpenRare V3 Pipeline API"
    version: str = "0.2.0"
