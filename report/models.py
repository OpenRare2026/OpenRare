from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class SampleMeta(BaseModel):
    family_type: str = ""
    pedigree_role: str = ""
    sample_id: str
    clinical_info: str = ""
    hpo_raw: str = ""
    hpo_terms: list[str] = Field(default_factory=list)
    raghpo_returns: dict[str, Any] | None = None
    liftover_path: str = ""
    vcf_path: str = ""
    wide_table_path: str = ""
    gene_disease_path: str = ""
    ppi_path: str = ""
    report_path: str = ""
    report_date: str = Field(default_factory=lambda: date.today().isoformat())


class VariantRecord(BaseModel):
    chrom: str
    pos: str
    ref: str
    alt: str
    gene_symbol: str
    transcript_id: str = ""
    refseq_id: str = ""
    mane_select: str = ""
    consequence: str = ""
    impact: str = ""
    hgvsc: str = ""
    hgvsp: str = ""
    exon: str = ""
    protein_domains: str = ""
    revel_score: str = ""
    cadd_phred: str = ""
    gnomad_popmax_af: str = ""
    gnomad_eas_af: str = ""
    gnomad_nhomalt: str = ""
    spliceai_ds_max: str = ""
    spliceai_type: str = ""
    loftee_lof_flag: str = ""
    clinvar_significance: str = ""
    clinvar_review_status: str = ""
    clinvar_star_rating: str = ""
    vcf_info_af: str = ""
    vcf_info_dp: str = ""
    clinical_best_tissue: str = ""
    clinical_transcript_tpm: str = ""
    gtex_transcript_top5_tissues: str = ""
    pathogenic_rank: int | None = None
    evidence_summary: str = ""

    @property
    def coordinate(self) -> str:
        return f"{self.chrom}:{self.pos} {self.ref}>{self.alt}"

    @property
    def variant_label(self) -> str:
        if self.hgvsp and self.hgvsp != "-":
            return f"{self.gene_symbol} {self.hgvsp}"
        return f"{self.gene_symbol} {self.coordinate}"


class LiteratureHit(BaseModel):
    pmid: str = ""
    title: str = ""
    authors_journal_year: str = ""
    summary: str = ""
    evidence_level: str = ""


class StrictDrugRecommendation(BaseModel):
    drug_name: str
    chembl_id: str = ""
    indication: str = ""
    clinical_stage: str = ""
    evidence_level: str = ""
    match_basis: str = ""
    caution: str = ""


class TrialTeamRow(BaseModel):
    drug_name: str
    source: str = ""
    registration_number: str = ""
    title: str = ""
    sponsor: str = ""
    principal_investigator: str = ""
    institution: str = ""


class GeneNarrative(BaseModel):
    gene_function: str = ""
    inheritance_mode: str = ""
    phenotype_association: str = ""
    pathway_summary: str = ""
    literature: list[LiteratureHit] = Field(default_factory=list)
    clinical_note: str = ""
    therapeutic_implication: str = ""


class GeneCard(BaseModel):
    rank: int
    gene_symbol: str
    best_pathogenic_rank: int
    variant_count: int
    top_clinvar: str = ""
    main_consequence: str = ""
    main_pathway: str = "-"
    main_associated_phenotype: str = "-"
    main_phenotype_hint: str = ""
    ncbi_gene_id: str = ""
    ncbi_gene_name: str = ""
    ncbi_gene_summary: str = "-"
    ncbi_gene_url: str = ""
    script_gene_function: str = "-"
    script_gene_function_source: str = "-"
    omim_gene_function: str = "-"
    omim_inheritance_mode: str = "-"
    evidence_summary: str = ""
    variants: list[VariantRecord] = Field(default_factory=list)
    drug_recommendations: list[StrictDrugRecommendation] = Field(default_factory=list)
    trial_teams: list[TrialTeamRow] = Field(default_factory=list)
    drug_recommendation_summary: str = ""
    narrative: GeneNarrative | None = None


class TopGeneSummary(BaseModel):
    rank: int
    gene: str
    variant_count: int
    best_pathogenic_rank: int
    top_clinvar: str = ""
    main_consequence: str = ""
    main_pathway: str = "-"
    main_associated_phenotype: str = "-"
    evidence_summary: str = ""


class ReportSummary(BaseModel):
    top_genes: list[TopGeneSummary] = Field(default_factory=list)
    total_variants: int = 0
    total_genes: int = 0
    genes_outside_top_n: int = 0


class ClinicalAdvice(BaseModel):
    immediate_recommendations: list[str] = Field(default_factory=list)
    monitoring: list[str] = Field(default_factory=list)
    communication_points: list[str] = Field(default_factory=list)
    key_findings: list[str] = Field(default_factory=list)


class ReportNarrative(BaseModel):
    gene_narratives: dict[str, GeneNarrative] = Field(default_factory=dict)
    clinical_advice: ClinicalAdvice | None = None


class ReportContext(BaseModel):
    meta: SampleMeta
    summary: ReportSummary
    gene_cards: list[GeneCard] = Field(default_factory=list)
    narrative: ReportNarrative = Field(default_factory=ReportNarrative)
    report_version: str = "v1.1"
    top_n: int = 5
