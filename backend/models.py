from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ===== Step-specific request models =====

class PhasingRequest(BaseModel):
    input_vcf: str = Field(..., description="Input VCF/VCF.GZ path")
    output_dir: Optional[str] = Field(None, description="Output directory")
    ref_dir: Optional[str] = Field(None, description="CHN reference panel directory")
    beagle_jar: Optional[str] = Field(None, description="Beagle jar path")
    chromosomes: str = Field("1-22", description="Chromosome spec, e.g. 1-22, 1,3,5")
    sample_id: Optional[str] = Field(None, description="Sample ID (auto-detect if empty)")
    chr_jobs: Optional[int] = Field(None, description="Concurrent chromosomes")
    beagle_threads: Optional[int] = Field(None, description="Threads per Beagle process")
    java_heap_gb: Optional[int] = Field(None, description="Java heap per Beagle process (GB)")
    java_bin: Optional[str] = Field(None, description="Java executable path")
    dry_run: bool = False


class PreprocessingRequest(BaseModel):
    input_vcf: str = Field(..., description="Input phased VCF/VCF.GZ path")
    output_prefix: str = Field(..., description="Output file prefix (path without extension)")
    sample_id: Optional[str] = Field(None, description="Sample name for output")
    ccre_bed: Optional[str] = Field(None, description="cCRE BED.GZ path")
    ncrna_bed: Optional[str] = Field(None, description="ncRNA BED.GZ path")


class PseudogeneRequest(BaseModel):
    input_vcf: str = Field(..., description="Input preprocessed VCF path")
    output_dir: str = Field(..., description="Output directory")
    sample_name: Optional[str] = Field(None, description="Sample name")
    gencode_gtf: Optional[str] = Field(None, description="GENCODE pseudogene GTF path")
    pseudogene_org: Optional[str] = Field(None, description="Pseudogene.org data path")
    hgnc: Optional[str] = Field(None, description="HGNC complete set path")
    dry_run: bool = False


class VepRequest(BaseModel):
    input_vcf: str = Field(..., description="Input VCF/VCF.GZ path")
    output_csv: str = Field(..., description="Output CSV path")
    config: Optional[str] = Field(None, description="VEP runner config JSON path")
    fork: int = Field(1, description="VEP fork count")
    hpo_id: str = Field("", description="HPO ID(s) for phenotype-aware selection")
    clinical_tissue: str = Field("", description="GTEx tissue name")
    top_k_transcripts: int = Field(5, description="Top K transcript selection count")
    keep_raw_vep: bool = True
    dry_run: bool = False


class InfoToCsvRequest(BaseModel):
    input_csv: str = Field(..., description="Input VEP CSV path")
    input_vcf: str = Field(..., description="Input annotated VCF path")
    output_csv: str = Field(..., description="Output CSV with INFO fields")


class SortingRequest(BaseModel):
    input_csv: str = Field(..., description="Input CSV with INFO fields path")
    output_csv: str = Field(..., description="Final sorted CSV path")


# ===== Full pipeline request =====

class PipelineRequest(BaseModel):
    input_vcf: str = Field(..., description="Input VCF/VCF.GZ path")
    output_dir: Optional[str] = Field(None, description="Output directory")
    fork: int = Field(1, description="VEP fork count")
    hpo_id: str = Field("", description="Patient HPO ID(s)")
    sample_id: Optional[str] = Field(None, description="Sample ID")
    chromosomes: Optional[str] = Field(None, description="Chromosome spec")
    ref_dir: Optional[str] = Field(None, description="CHN reference panel directory")
    beagle_jar: Optional[str] = Field(None, description="Beagle jar path")
    ccre_bed: Optional[str] = Field(None, description="cCRE BED.GZ")
    ncrna_bed: Optional[str] = Field(None, description="ncRNA BED.GZ")
    chr_jobs: Optional[int] = Field(None, description="Concurrent chromosomes for phasing")
    beagle_threads: Optional[int] = Field(None, description="Threads per Beagle process")
    java_heap_gb: Optional[int] = Field(None, description="Java heap per Beagle process")
    java_bin: Optional[str] = Field(None, description="Java executable")
    top_k_transcripts: Optional[int] = Field(None, description="Transcript selection count")
    clinical_tissue: str = Field("", description="GTEx tissue for phenotype-aware expression")
    keep_raw_vep: Optional[bool] = Field(None, description="Keep raw VEP TSV")
    dry_run: bool = False


# ===== Upload request (multipart) =====

class PipelineUploadRequest(BaseModel):
    fork: int = Field(1, ge=1)
    hpo_id: str = ""
    sample_id: Optional[str] = None
    chromosomes: Optional[str] = None
    dry_run: bool = False


# ===== Response models =====

class JobResponse(BaseModel):
    job_id: str
    status: str
    status_url: str
    output_dir: str


class StepResponse(BaseModel):
    job_id: str
    status: str
    status_url: str
    step: str
