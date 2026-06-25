from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


def _optional_int(value: str) -> int | None:
    text = (value or "").strip()
    if not text or text == "-":
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _optional_float(value: str) -> float | None:
    text = (value or "").strip()
    if not text or text == "-":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _is_present(value: str) -> bool:
    return (value or "").strip() not in ("", "-", ".")


_CRE_CLASS_ZH = {
    "PLS": "启动子样元件 (PLS)",
    "pELS": "近端增强子样元件 (pELS)",
    "dELS": "远端增强子样元件 (dELS)",
    "CA-CTCF": "CTCF 相关元件 (CA-CTCF)",
    "CA-TF": "转录因子结合相关元件 (CA-TF)",
    "TF": "转录因子相关元件 (TF)",
}

_CRE_RELEVANT_CONSEQUENCES = frozenset(
    {
        "intron_variant",
        "upstream_gene_variant",
        "downstream_gene_variant",
        "intergenic_variant",
        "regulatory_region_variant",
        "5_prime_UTR_variant",
        "3_prime_UTR_variant",
        "non_coding_transcript_exon_variant",
        "non_coding_transcript_variant",
        "NMD_transcript_variant",
        "mature_miRNA_variant",
    }
)

_SINGLETON_FAMILY_TYPES = frozenset({"单人", "single", "singleton"})


def _cre_context_relevant(consequence: str) -> bool:
    if not _is_present(consequence):
        return False
    terms = {part.strip() for part in consequence.split("&") if part.strip()}
    if terms & _CRE_RELEVANT_CONSEQUENCES:
        return True
    lowered = consequence.lower()
    return any(token in lowered for token in ("utr", "intron", "intergenic", "regulatory"))


def _phasing_context_relevant(*, gene_variant_count: int, family_type: str) -> bool:
    if gene_variant_count >= 2:
        return True
    normalized = (family_type or "").strip().lower()
    if not normalized:
        return False
    return normalized not in {item.lower() for item in _SINGLETON_FAMILY_TYPES}


def build_genomic_context_items(
    variant: VariantRecord,
    *,
    gene_variant_count: int = 1,
    family_type: str = "",
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []

    confidence = (variant.vcf_info_phasing_confidence or "").strip().upper()
    phased = (variant.vcf_info_beagle_phased or "").strip()
    if (
        confidence == "HIGH"
        and phased in {"1", "YES", "True", "true"}
        and _phasing_context_relevant(
            gene_variant_count=gene_variant_count,
            family_type=family_type,
        )
    ):
        items.append(
            {
                "label": "变异相位",
                "value": "已完成相位推断，置信度高",
                "note": "可用于复合杂合/顺反式判断，建议结合家系样本确认",
            }
        )

    carrier_count = _optional_int(variant.vcf_info_chn_alt_carrier_count)
    alt_ac = _optional_int(variant.vcf_info_chn_alt_ac)
    if (carrier_count or 0) > 0 or (alt_ac or 0) > 0:
        items.append(
            {
                "label": "中国参考人群",
                "value": f"携带该 ALT 约 {carrier_count or '-'} 例，ALT 等位基因计数 {alt_ac or '-'}",
                "note": "补充 gnomAD 之外的本国参考人群携带信息",
            }
        )

    if _is_present(variant.vcf_info_reg_ccre_class) and _cre_context_relevant(variant.consequence):
        classes = [
            _CRE_CLASS_ZH.get(part.strip(), part.strip())
            for part in variant.vcf_info_reg_ccre_class.split(",")
            if part.strip()
        ]
        count = (
            variant.vcf_info_reg_ccre_count
            if _is_present(variant.vcf_info_reg_ccre_class)
            else "-"
        )
        items.append(
            {
                "label": "调控元件",
                "value": f"{'、'.join(classes)}（重叠 {count} 个 cCRE）",
                "note": "提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估",
            }
        )

    if _is_present(variant.vcf_info_ncrna_gene_name):
        gene_type = (
            variant.vcf_info_ncrna_gene_type
            if _is_present(variant.vcf_info_ncrna_gene_type)
            else "ncRNA"
        )
        items.append(
            {
                "label": "非编码 RNA",
                "value": f"{variant.vcf_info_ncrna_gene_name}（{gene_type}）",
                "note": "变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读",
            }
        )

    if (variant.vcf_info_is_pseudogene or "").strip().lower() in {"yes", "1", "true"}:
        pseudo_name = (
            variant.vcf_info_pseudogene_name
            if _is_present(variant.vcf_info_pseudogene_name)
            else "-"
        )
        pseudo_source = (
            variant.vcf_info_pseudogene_source
            if _is_present(variant.vcf_info_pseudogene_source)
            else "-"
        )
        items.append(
            {
                "label": "假基因区域",
                "value": f"命中假基因相关区域（{pseudo_name}，来源 {pseudo_source}）",
                "note": "假基因区变异致病权重通常较低，避免误判为功能基因致病变异",
            }
        )

    return items


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
    vcf_info_vaf: str = ""
    vcf_info_ref_dp: str = ""
    vcf_info_alt_dp: str = ""
    vcf_info_qd: str = ""
    vcf_info_fs: str = ""
    vcf_info_mq: str = ""
    vcf_info_beagle_phased: str = ""
    vcf_info_chn_ref_support: str = ""
    vcf_info_chn_alt_carrier_count: str = ""
    vcf_info_chn_alt_ac: str = ""
    vcf_info_phasing_confidence: str = ""
    vcf_info_reg_ccre_id: str = ""
    vcf_info_reg_ccre_class: str = ""
    vcf_info_reg_ccre_count: str = ""
    vcf_info_ncrna_gene_name: str = ""
    vcf_info_ncrna_gene_type: str = ""
    vcf_info_is_pseudogene: str = ""
    vcf_info_pseudogene_name: str = ""
    vcf_info_pseudogene_source: str = ""
    clinical_best_tissue: str = ""
    clinical_transcript_tpm: str = ""
    gtex_transcript_top5_tissues: str = ""
    pathogenic_rank: int | None = None
    evidence_summary: str = ""
    genos_evee: str = ""

    @property
    def coordinate(self) -> str:
        return f"{self.chrom}:{self.pos} {self.ref}>{self.alt}"

    @property
    def primary_vaf(self) -> str:
        if self.vcf_info_vaf not in ("", "-"):
            return self.vcf_info_vaf
        return self.vcf_info_af

    @property
    def has_read_level_vaf(self) -> bool:
        return _is_present(self.vcf_info_vaf)

    @property
    def has_read_support(self) -> bool:
        return self.read_support_summary != "-"

    @property
    def read_support_summary(self) -> str:
        if self.vcf_info_ref_dp == "-" or self.vcf_info_alt_dp == "-":
            return "-"
        try:
            ref_reads = int(float(self.vcf_info_ref_dp))
            alt_reads = int(float(self.vcf_info_alt_dp))
            return f"参考序列 {ref_reads} 条 / 变异序列 {alt_reads} 条（合计 {ref_reads + alt_reads} 条 reads）"
        except ValueError:
            return "-"

    @property
    def show_gatk_af_row(self) -> bool:
        if not self.has_read_level_vaf or not _is_present(self.vcf_info_af):
            return False
        try:
            return abs(float(self.vcf_info_vaf) - float(self.vcf_info_af)) >= 0.05
        except ValueError:
            return True

    @property
    def sequencing_metrics_text(self) -> str:
        parts: list[str] = []
        if _is_present(self.vcf_info_qd):
            parts.append(f"QD（质量/深度）={self.vcf_info_qd}")
        if _is_present(self.vcf_info_fs):
            parts.append(f"FS（链偏倚）={self.vcf_info_fs}")
        if _is_present(self.vcf_info_mq):
            parts.append(f"MQ（比对质量）={self.vcf_info_mq}")
        return "；".join(parts) if parts else "-"

    @property
    def sequencing_quality_note(self) -> str:
        notes: list[str] = []
        alt_reads = _optional_int(self.vcf_info_alt_dp)
        total_depth = _optional_int(self.vcf_info_dp)
        if alt_reads is not None and alt_reads < 3:
            notes.append("支持变异的 reads 偏少，建议 Sanger 验证")
        if total_depth is not None and total_depth < 10:
            notes.append("测序深度偏低，等位基因比例可信度有限")
        if self.show_gatk_af_row and self.has_read_level_vaf:
            notes.append("测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持")
        qd = _optional_float(self.vcf_info_qd)
        if qd is not None and qd < 2:
            notes.append("位点质量指标 QD 偏低")
        return "；".join(notes) if notes else "-"

    @property
    def genomic_context_items(self) -> list[dict[str, str]]:
        return build_genomic_context_items(self)

    @property
    def has_genomic_context(self) -> bool:
        return bool(self.genomic_context_items)

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
    genos_evee: str = "-"
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
