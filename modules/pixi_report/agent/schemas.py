from __future__ import annotations

from pydantic import BaseModel, Field



class DataSource(BaseModel):
    provider: str
    tool: str
    url: str | None = None
    entity_id: str | None = None


class GeneInfo(BaseModel):
    symbol: str
    ensembl_id: str
    source: DataSource


class DiseaseAssociation(BaseModel):
    id: str
    name: str
    score: float
    source: DataSource


class DrugIndication(BaseModel):
    disease_id: str
    disease_name: str
    max_clinical_stage: str


class DrugMechanism(BaseModel):
    mechanism: str
    target_name: str | None = None
    target_genes: list[str] = Field(default_factory=list)


class DrugAdverseEvent(BaseModel):
    name: str
    count: int | None = None
    log_lr: float | None = None
    meddra_code: str | None = None


class DrugPharmacogenomic(BaseModel):
    gene_symbol: str | None = None
    haplotype_id: str | None = None
    variant_rs_id: str | None = None
    phenotype: str | None = None
    category: str | None = None
    evidence_level: str | None = None
    annotation: str | None = None
    literature_pmids: list[str] = Field(default_factory=list)


class DrugReference(BaseModel):
    pmid: str
    title: str | None = None
    doi: str | None = None
    url: str | None = None


class DrugHit(BaseModel):
    chembl_id: str
    name: str
    description: str | None = None
    maximum_clinical_stage: str | None = None
    indications: list[DrugIndication] = Field(default_factory=list)
    mechanisms: list[DrugMechanism] = Field(default_factory=list)
    adverse_events: list[DrugAdverseEvent] = Field(default_factory=list)
    pharmacogenomics: list[DrugPharmacogenomic] = Field(default_factory=list)
    references: list[DrugReference] = Field(default_factory=list)
    source: DataSource


class PgxAlleleEffect(BaseModel):
    allele: str
    effect: str
    allele_function: str | None = None


class PgxDrugProfile(BaseModel):
    drug_name: str
    priority: str
    guideline_sources: list[str] = Field(default_factory=list)
    guideline_summary: str | None = None
    evidence_levels: list[str] = Field(default_factory=list)
    effect_types: list[str] = Field(default_factory=list)
    allele_effects: list[PgxAlleleEffect] = Field(default_factory=list)
    pathways: list[str] = Field(default_factory=list)
    source: DataSource


class PaperHit(BaseModel):
    paper_id: str
    title: str
    authors: str | None = None
    abstract: str | None = None
    published_date: str | None = None
    url: str | None = None
    doi: str | None = None
    pdf_url: str | None = None
    source: DataSource


class GeneResearchReport(BaseModel):
    query: str
    generated_at: str
    summary: str
    gene: GeneInfo | None = None
    drugs: list[DrugHit] = Field(default_factory=list)
    pgx_drugs: list[PgxDrugProfile] = Field(default_factory=list)
    papers: list[PaperHit] = Field(default_factory=list)
    sources: list[DataSource] = Field(default_factory=list)


class GeneDiseaseResearchInput(BaseModel):
    gene_symbol: str
    mondo_ids: list[str] = Field(default_factory=list)


class FilteredDrugHit(DrugHit):
    matched_disease: bool = False
    matched_mondo_ids: list[str] = Field(default_factory=list)


class ChinaTrialHit(BaseModel):
    source: str
    registration_number: str
    drug_name: str | None = None
    title: str | None = None
    team: dict = Field(default_factory=dict)
    match_score: int | None = None


class DrugTeamRecommendation(BaseModel):
    drug_name: str
    chembl_id: str | None = None
    matched_disease: bool
    chinadrug_trials: list[ChinaTrialHit] = Field(default_factory=list)
    chictr_trials: list[ChinaTrialHit] = Field(default_factory=list)
    agent_summary: str | None = None


class GeneDiseaseResearchReport(BaseModel):
    input: GeneDiseaseResearchInput
    query: str
    generated_at: str
    summary: str
    gene: GeneInfo | None = None
    diseases: list[DiseaseAssociation] = Field(default_factory=list)
    drugs: list[FilteredDrugHit] = Field(default_factory=list)
    literature_drugs: list[FilteredDrugHit] = Field(default_factory=list)
    team_recommendations: list[DrugTeamRecommendation] = Field(default_factory=list)
    papers: list[PaperHit] = Field(default_factory=list)
    sources: list[DataSource] = Field(default_factory=list)
    workflow_meta: dict = Field(default_factory=dict)
