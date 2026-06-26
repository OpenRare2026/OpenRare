"""
ACMG/AMP Criteria Definitions and Base Interfaces

This module defines the interfaces for all ACMG/AMP criteria for variant classification.
Criteria are organized by evidence strength:
- Pathogenic Very Strong: PVS1
- Pathogenic Strong: PS1-PS4
- Pathogenic Moderate: PM1-PM6
- Pathogenic Supporting: PP1-PP5
- Benign Standalone: BA1
- Benign Strong: BS1-BS4
- Benign Supporting: BP1-BP7

Reference: Richards et al. 2015. Standards and guidelines for the interpretation of
sequence variants. Genet Med. 17(5):405-424.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EvidenceStrength(Enum):
    """Evidence strength levels for ACMG criteria."""
    PATHOGENIC_VERY_STRONG = "pathogenic_very_strong"
    PATHOGENIC_STRONG = "pathogenic_strong"
    PATHOGENIC_MODERATE = "pathogenic_moderate"
    PATHOGENIC_SUPPORTING = "pathogenic_supporting"
    BENIGN_STANDALONE = "benign_standalone"
    BENIGN_STRONG = "benign_strong"
    BENIGN_SUPPORTING = "benign_supporting"


class EvidenceDirection(Enum):
    """Direction of evidence (pathogenic vs benign)."""
    PATHOGENIC = "pathogenic"
    BENIGN = "benign"


@dataclass
class CriterionResult:
    """Result of evaluating a single ACMG criterion."""
    criterion_code: str
    criterion_name: str
    is_met: bool
    evidence_strength: EvidenceStrength
    direction: EvidenceDirection
    score: float
    description: str = ""
    evidence_sources: List[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "criterion_code": self.criterion_code,
            "criterion_name": self.criterion_name,
            "is_met": self.is_met,
            "evidence_strength": self.evidence_strength.value,
            "direction": self.direction.value,
            "score": self.score,
            "description": self.description,
            "evidence_sources": self.evidence_sources,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


LOF_CONSEQUENCES = {
    "transcript_ablation", "splice_acceptor_variant", "splice_donor_variant",
    "stop_gained", "frameshift_variant", "stop_lost", "start_lost",
    "transcript_amplification", "feature_elongation", "feature_truncation"
}

SPLICE_CONSEQUENCES = {"splice_acceptor_variant", "splice_donor_variant"}
FRAMESHIFT_CONSEQUENCES = {"frameshift_variant"}
STOP_GAIN_CONSEQUENCES = {"stop_gained"}
START_LOST_CONSEQUENCES = {"start_lost"}
EXON_DELETION_CONSEQUENCES = {"exon_loss_variant"}

NULL_VARIANT_CONSEQUENCES = (
    SPLICE_CONSEQUENCES | FRAMESHIFT_CONSEQUENCES | 
    STOP_GAIN_CONSEQUENCES | START_LOST_CONSEQUENCES | EXON_DELETION_CONSEQUENCES
)

MISSENSE_CONSEQUENCES = {"missense_variant"}
SYNONYMOUS_CONSEQUENCES = {"synonymous_variant"}
INFRAME_INDEL_CONSEQUENCES = {"inframe_insertion", "inframe_deletion"}


class BaseCriterion(ABC):
    """Abstract base class for ACMG criteria."""
    
    code: str = ""
    name: str = ""
    description: str = ""
    evidence_strength: EvidenceStrength = EvidenceStrength.PATHOGENIC_SUPPORTING
    direction: EvidenceDirection = EvidenceDirection.PATHOGENIC
    default_score: float = 0.0
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.code}")
    
    @abstractmethod
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        pass
    
    def get_score(self) -> float:
        return self.config.get("score", self.default_score)
    
    def is_enabled(self) -> bool:
        return self.config.get("enabled", True)
    
    def _get_consequence(self, variant: Dict[str, Any]) -> str:
        consequences = variant.get("consequence", variant.get("consequences", []))
        if isinstance(consequences, list) and consequences:
            return consequences[0]
        return variant.get("consequence", "")
    
    def _get_af_gnomad(self, variant: Dict[str, Any]) -> float:
        return float(variant.get("gnomad_af", variant.get("gnomad_af_global", 0.0)) or 0.0)
    
    def _get_gene(self, variant: Dict[str, Any]) -> str:
        return variant.get("gene", variant.get("gene_symbol", ""))
    
    def _get_hgvs_p(self, variant: Dict[str, Any]) -> str:
        return variant.get("hgvs_p", variant.get("protein_change", ""))
    
    def _get_hgvs_c(self, variant: Dict[str, Any]) -> str:
        return variant.get("hgvs_c", variant.get("coding_change", ""))


class PVS1(BaseCriterion):
    """
    PVS1 - Null variant (nonsense, frameshift, canonical +/- 1 or 2 splice sites,
    initiation codon, single or multi-exon deletion) in a gene where LOF is a
    known mechanism of disease.
    
    Strength can be modified based on:
    - NMD prediction (escape vs trigger)
    - Location in gene (last exon vs other)
    - Alternative transcripts
    - Gene LOF mechanism validity
    """
    code = "PVS1"
    name = "Null variant in gene where LOF is known disease mechanism"
    evidence_strength = EvidenceStrength.PATHOGENIC_VERY_STRONG
    direction = EvidenceDirection.PATHOGENIC
    default_score = 8.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PVS1 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        gene = self._get_gene(variant)
        
        if not consequence or consequence not in NULL_VARIANT_CONSEQUENCES:
            return self._not_met("Variant is not a null variant (not LOF consequence)")
        
        lof_genes = context.get("lof_disease_genes", set())
        if isinstance(lof_genes, list):
            lof_genes = set(lof_genes)
        
        gene_info = variant.get("gene_info", {})
        gene_lof_mechanism = gene_info.get("lof_mechanism", context.get("gene_lof_mechanism", False))
        
        if gene not in lof_genes and not gene_lof_mechanism:
            return self._not_met(f"Gene {gene} is not known to have LOF as disease mechanism")
        
        strength_modifier, warnings = self._assess_strength_modifier(variant, context)
        
        is_met = True
        final_strength = self.evidence_strength
        confidence = 0.9
        
        if strength_modifier == "very_strong":
            final_strength = EvidenceStrength.PATHOGENIC_VERY_STRONG
            confidence = 0.95
        elif strength_modifier == "strong":
            final_strength = EvidenceStrength.PATHOGENIC_STRONG
            confidence = 0.85
        elif strength_modifier == "moderate":
            final_strength = EvidenceStrength.PATHOGENIC_MODERATE
            confidence = 0.75
        elif strength_modifier == "supporting":
            final_strength = EvidenceStrength.PATHOGENIC_SUPPORTING
            confidence = 0.65
        
        description = f"Null variant ({consequence}) in {gene}, a gene where LOF is a known disease mechanism"
        if warnings:
            description += f". Considerations: {'; '.join(warnings)}"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=is_met,
            evidence_strength=final_strength,
            direction=self.direction,
            score=self._get_adjusted_score(final_strength),
            description=description,
            evidence_sources=["gene_constraint", "lof_mechanism_database"],
            confidence=confidence,
            metadata={"warnings": warnings, "strength_modifier": strength_modifier}
        )
    
    def _assess_strength_modifier(self, variant: Dict[str, Any], context: Dict[str, Any]) -> tuple:
        warnings = []
        modifier = "very_strong"
        
        consequence = self._get_consequence(variant)
        gene_info = variant.get("gene_info", {})
        exon_info = variant.get("exon_info", {})
        
        if consequence in SPLICE_CONSEQUENCES:
            splice_impact = self._assess_splice_impact(variant)
            if splice_impact == "uncertain":
                modifier = self._downgrade_modifier(modifier)
                warnings.append("Splice variant impact prediction uncertain")
        
        nmd_escape = exon_info.get("nmd_escape", False)
        is_last_exon = exon_info.get("is_last_exon", False)
        is_last_50bp = exon_info.get("is_last_50bp", False)
        
        if nmd_escape or is_last_exon or is_last_50bp:
            modifier = self._downgrade_modifier(modifier)
            warnings.append("Variant may escape NMD (last exon or within 50bp of last exon)")
        
        other_transcripts = gene_info.get("other_transcripts", [])
        rescue_possible = any(
            t.get("has_alternative_start", False) or t.get("escapes_nmd", False)
            for t in other_transcripts
        )
        if rescue_possible:
            modifier = self._downgrade_modifier(modifier)
            warnings.append("Alternative transcript rescue possible")
        
        exon_number = exon_info.get("exon_number", 1)
        total_exons = gene_info.get("total_exons", 1)
        if exon_number <= 1 and total_exons > 1:
            pass
        
        return modifier, warnings
    
    def _assess_splice_impact(self, variant: Dict[str, Any]) -> str:
        spliceai_score = variant.get("spliceai_score", 0)
        maxent_score = variant.get("maxent_score", 0)
        
        if spliceai_score >= 0.8 or maxent_score >= 3:
            return "high_confidence"
        elif spliceai_score >= 0.5 or maxent_score >= 1:
            return "moderate_confidence"
        else:
            return "uncertain"
    
    def _downgrade_modifier(self, current: str) -> str:
        levels = ["very_strong", "strong", "moderate", "supporting"]
        try:
            idx = levels.index(current)
            return levels[min(idx + 1, len(levels) - 1)]
        except ValueError:
            return "moderate"
    
    def _get_adjusted_score(self, strength: EvidenceStrength) -> float:
        scores = {
            EvidenceStrength.PATHOGENIC_VERY_STRONG: 8.0,
            EvidenceStrength.PATHOGENIC_STRONG: 4.0,
            EvidenceStrength.PATHOGENIC_MODERATE: 2.0,
            EvidenceStrength.PATHOGENIC_SUPPORTING: 1.0,
        }
        return scores.get(strength, 0.0)
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PS1(BaseCriterion):
    """
    PS1 - Same amino acid change as a previously established pathogenic variant
    regardless of nucleotide change.
    
    Caveats:
    - Need to confirm the reference variant is truly pathogenic
    - Consider if different nucleotide change could affect splicing
    """
    code = "PS1"
    name = "Same amino acid change as established pathogenic variant"
    evidence_strength = EvidenceStrength.PATHOGENIC_STRONG
    direction = EvidenceDirection.PATHOGENIC
    default_score = 4.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PS1 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        if consequence not in MISSENSE_CONSEQUENCES:
            return self._not_met("Variant is not a missense variant")
        
        hgvs_p = self._get_hgvs_p(variant)
        gene = self._get_gene(variant)
        
        if not hgvs_p:
            return self._not_met("No protein change (HGVS.p) available")
        
        clinvar_variants = variant.get("clinvar_variants", [])
        pathogenic_same_aa = []
        
        for cv in clinvar_variants:
            if cv.get("hgvs_p") == hgvs_p and cv.get("gene") == gene:
                significance = cv.get("clinical_significance", "").lower()
                if significance in ("pathogenic", "likely pathogenic"):
                    if cv.get("hgvs_c") != variant.get("hgvs_c"):
                        pathogenic_same_aa.append(cv)
        
        if not pathogenic_same_aa:
            known_pathogenic = context.get("known_pathogenic_variants", {})
            if hgvs_p in known_pathogenic.get(gene, {}):
                path_var = known_pathogenic[gene][hgvs_p]
                if path_var.get("review_status") in ("reviewed_by_expert", "practice_guideline"):
                    pathogenic_same_aa.append(path_var)
        
        if not pathogenic_same_aa:
            return self._not_met(f"No established pathogenic variant with same amino acid change found for {hgvs_p}")
        
        splice_effect = self._check_splice_effect(variant)
        
        description = f"Same amino acid change ({hgvs_p}) as established pathogenic variant(s)"
        if splice_effect:
            description += f". Warning: This nucleotide change may affect splicing"
        
        confidence = 0.95 if not splice_effect else 0.8
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["ClinVar", "literature"],
            confidence=confidence,
            metadata={"matching_variants": len(pathogenic_same_aa), "splice_warning": splice_effect}
        )
    
    def _check_splice_effect(self, variant: Dict[str, Any]) -> bool:
        spliceai_score = variant.get("spliceai_score", 0)
        return spliceai_score >= 0.2
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PS2(BaseCriterion):
    """
    PS2 - De novo (both maternity and paternity confirmed) variant in a patient
    with the disease and no family history.
    
    Requires:
    - Confirmed parentage (both parents tested)
    - Confirmed de novo status
    - Affected proband with disease consistent with gene
    - No family history of the condition
    """
    code = "PS2"
    name = "De novo variant with confirmed parentage"
    evidence_strength = EvidenceStrength.PATHOGENIC_STRONG
    direction = EvidenceDirection.PATHOGENIC
    default_score = 4.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PS2 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        inheritance_info = context.get("inheritance", {})
        
        is_de_novo = variant.get("de_novo", inheritance_info.get("de_novo", False))
        
        if not is_de_novo:
            return self._not_met("Variant is not confirmed as de novo")
        
        parentage_confirmed = inheritance_info.get("parentage_confirmed", False)
        maternity_confirmed = inheritance_info.get("maternity_confirmed", False)
        paternity_confirmed = inheritance_info.get("paternity_confirmed", False)
        
        if not parentage_confirmed and not (maternity_confirmed and paternity_confirmed):
            return self._not_met("De novo status not confirmed - parentage testing required")
        
        family_history = context.get("family_history", {})
        has_family_history = family_history.get("affected_relatives", False)
        
        if has_family_history:
            return self._not_met("Family history of condition present - not compatible with de novo")
        
        gene = self._get_gene(variant)
        disease_match = self._check_disease_gene_match(variant, context)
        
        if not disease_match:
            return self._not_met(f"Patient phenotype not consistent with gene {gene}")
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description="Confirmed de novo variant in affected individual with no family history",
            evidence_sources=["family_segregation", "parentage_testing"],
            confidence=0.95,
            metadata={
                "maternity_confirmed": maternity_confirmed,
                "paternity_confirmed": paternity_confirmed,
            }
        )
    
    def _check_disease_gene_match(self, variant: Dict[str, Any], context: Dict[str, Any]) -> bool:
        gene = self._get_gene(variant)
        phenotype_genes = context.get("phenotype_associated_genes", [])
        return gene in phenotype_genes or context.get("gene_phenotype_match", True)
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PS3(BaseCriterion):
    """
    PS3 - Well-established in vitro or in vivo functional studies supportive of
    a damaging effect on the gene or gene product.
    
    Criteria for "well-established":
    - Assay is validated and reproducible
    - Controls are appropriate
    - Published in peer-reviewed journal
    - Multiple studies confirm findings
    """
    code = "PS3"
    name = "Well-established functional studies show damaging effect"
    evidence_strength = EvidenceStrength.PATHOGENIC_STRONG
    direction = EvidenceDirection.PATHOGENIC
    default_score = 4.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PS3 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        functional_studies = variant.get("functional_studies", [])
        
        if not functional_studies:
            return self._not_met("No functional studies available")
        
        damaging_studies = []
        evidence_level = "supporting"
        
        for study in functional_studies:
            if self._is_study_damaging(study):
                quality = self._assess_study_quality(study)
                if quality == "well_established":
                    damaging_studies.append(study)
                    evidence_level = "strong"
                elif quality == "moderate" and evidence_level != "strong":
                    evidence_level = "moderate"
        
        if not damaging_studies:
            return self._not_met("No well-established functional studies showing damaging effect")
        
        study_types = set(s.get("study_type", "unknown") for s in damaging_studies)
        description = f"Functional studies ({len(damaging_studies)}) show damaging effect"
        
        if len(damaging_studies) > 1:
            description += " with multiple confirmatory studies"
        
        confidence = 0.9 if len(damaging_studies) >= 2 else 0.85
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=[s.get("reference", "functional_study") for s in damaging_studies],
            confidence=confidence,
            metadata={"study_types": list(study_types), "study_count": len(damaging_studies)}
        )
    
    def _is_study_damaging(self, study: Dict[str, Any]) -> bool:
        result = study.get("result", "").lower()
        if "damaging" in result or "pathogenic" in result or "loss of function" in result:
            return True
        if study.get("is_damaging", False):
            return True
        effect_size = study.get("effect_size")
        if effect_size is not None and effect_size > 2.0:
            return True
        return False
    
    def _assess_study_quality(self, study: Dict[str, Any]) -> str:
        quality_score = study.get("quality_score", 0)
        validation = study.get("validated", False)
        reproducible = study.get("reproducible", False)
        peer_reviewed = study.get("peer_reviewed", True)
        
        if quality_score >= 4 and validation and reproducible and peer_reviewed:
            return "well_established"
        elif quality_score >= 3 and validation:
            return "moderate"
        else:
            return "limited"
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PS4(BaseCriterion):
    """
    PS4 - The prevalence of the variant in affected individuals is significantly
    increased compared with the prevalence in controls.
    
    Statistical criteria:
    - OR > 5 with CI not including 1, and p < 0.05
    - OR for recessive conditions may be lower
    - Need to consider population stratification
    """
    code = "PS4"
    name = "Significantly increased prevalence in affected vs controls"
    evidence_strength = EvidenceStrength.PATHOGENIC_STRONG
    direction = EvidenceDirection.PATHOGENIC
    default_score = 4.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PS4 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        case_control_data = variant.get("case_control_data", context.get("case_control_data", []))
        
        if not case_control_data:
            return self._not_met("No case-control data available")
        
        significant_studies = []
        best_evidence = {"or": 0, "ci_lower": 0, "p_value": 1}
        
        for study in case_control_data:
            result = self._analyze_case_control(study)
            if result["significant"]:
                significant_studies.append(study)
                if result["or"] > best_evidence["or"]:
                    best_evidence = result
        
        if not significant_studies:
            return self._not_met("No significant case-control association found")
        
        inheritance = context.get("inheritance_mode", "dominant")
        or_threshold = 5.0 if inheritance != "recessive" else 2.0
        
        description = f"Significant case-control association (OR={best_evidence['or']:.1f}, p={best_evidence['p_value']:.2e})"
        
        confidence = 0.9 if len(significant_studies) >= 2 else 0.85
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=[s.get("study_name", "case_control_study") for s in significant_studies],
            confidence=confidence,
            metadata={
                "odds_ratio": best_evidence["or"],
                "ci_lower": best_evidence["ci_lower"],
                "p_value": best_evidence["p_value"],
            }
        )
    
    def _analyze_case_control(self, study: Dict[str, Any]) -> Dict[str, Any]:
        cases_with = study.get("cases_with_variant", 0)
        cases_total = study.get("cases_total", 1)
        controls_with = study.get("controls_with_variant", 0)
        controls_total = study.get("controls_total", 1)
        
        if cases_with == 0:
            return {"significant": False, "or": 0, "ci_lower": 0, "p_value": 1}
        
        if controls_with == 0:
            controls_with = 0.5
        
        odds_ratio = (cases_with / cases_total) / (controls_with / controls_total)
        p_value = study.get("p_value", 0.001)
        ci_lower = study.get("ci_lower", odds_ratio * 0.5)
        
        or_threshold = study.get("or_threshold", 5.0)
        
        significant = odds_ratio >= or_threshold and ci_lower > 1.0 and p_value < 0.05
        
        return {
            "significant": significant,
            "or": odds_ratio,
            "ci_lower": ci_lower,
            "p_value": p_value,
        }
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PM1(BaseCriterion):
    """
    PM1 - Located in a mutational hot spot and/or critical and well-established
    functional domain (e.g. active site of an enzyme) without benign variation.
    """
    code = "PM1"
    name = "Located in mutational hot spot or critical functional domain"
    evidence_strength = EvidenceStrength.PATHOGENIC_MODERATE
    direction = EvidenceDirection.PATHOGENIC
    default_score = 2.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PM1 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        if consequence not in MISSENSE_CONSEQUENCES and consequence not in INFRAME_INDEL_CONSEQUENCES:
            return self._not_met("Variant is not a missense or in-frame indel")
        
        protein_domain_info = variant.get("protein_domain", {})
        hotspot_info = variant.get("hotspot", {})
        
        in_hotspot = hotspot_info.get("is_hotspot", False)
        hotspot_benign_count = hotspot_info.get("benign_count", 0)
        
        in_critical_domain = protein_domain_info.get("is_critical_domain", False)
        domain_benign_count = protein_domain_info.get("benign_count", 0)
        
        domain_name = protein_domain_info.get("name", "")
        
        if not in_hotspot and not in_critical_domain:
            return self._not_met("Variant not in mutational hotspot or critical functional domain")
        
        total_benign = hotspot_benign_count + domain_benign_count
        if total_benign > 2:
            return self._not_met(f"Benign variation present in domain/hotspot ({total_benign} benign variants)")
        
        description_parts = []
        if in_hotspot:
            description_parts.append("mutational hotspot")
        if in_critical_domain and domain_name:
            description_parts.append(f"critical domain {domain_name}")
        
        description = f"Located in {' and '.join(description_parts)} without benign variation"
        
        confidence = 0.85 if total_benign == 0 else 0.75
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["domain_database", "hotspot_analysis"],
            confidence=confidence,
            metadata={
                "in_hotspot": in_hotspot,
                "in_critical_domain": in_critical_domain,
                "domain_name": domain_name,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PM2(BaseCriterion):
    """
    PM2 - Absent from controls (or at extremely low frequency if recessive)
    in Exome Sequencing Project, 1000 Genomes Project, or ExAC.
    
    Now uses gnomAD as primary population database.
    Thresholds:
    - Dominant: < 0.001% (1 in 100,000)
    - Recessive: < 0.01% (1 in 10,000)
    """
    code = "PM2"
    name = "Absent from population databases"
    evidence_strength = EvidenceStrength.PATHOGENIC_MODERATE
    direction = EvidenceDirection.PATHOGENIC
    default_score = 2.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PM2 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        af_gnomad = self._get_af_gnomad(variant)
        af_1000g = float(variant.get("af_1000g", 0) or 0)
        af_exac = float(variant.get("exac_af", 0) or 0)
        
        max_af = max(af_gnomad, af_1000g, af_exac)
        
        inheritance = context.get("inheritance_mode", "dominant")
        
        if inheritance == "recessive":
            threshold = 0.0001
        else:
            threshold = 0.00001
        
        if max_af > threshold:
            databases_found = []
            if af_gnomad > 0:
                databases_found.append(f"gnomAD={af_gnomad:.6f}")
            if af_1000g > 0:
                databases_found.append(f"1000G={af_1000g:.6f}")
            if af_exac > 0:
                databases_found.append(f"ExAC={af_exac:.6f}")
            return self._not_met(f"Present in population databases ({', '.join(databases_found)})")
        
        if max_af == 0:
            description = "Absent from all population databases (gnomAD, 1000 Genomes, ExAC)"
        else:
            description = f"Extremely low frequency (max AF={max_af:.6f})"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["gnomAD", "1000Genomes", "ExAC"],
            confidence=0.9,
            metadata={
                "gnomad_af": af_gnomad,
                "1000g_af": af_1000g,
                "exac_af": af_exac,
                "inheritance_mode": inheritance,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PM3(BaseCriterion):
    """
    PM3 - For recessive disorders, detected in trans with a pathogenic variant.
    
    Requires:
    - Confirmed compound heterozygosity (different alleles)
    - Phase confirmed by parental testing or phasing analysis
    - Other variant is pathogenic/likely pathogenic
    """
    code = "PM3"
    name = "Detected in trans with pathogenic variant (recessive)"
    evidence_strength = EvidenceStrength.PATHOGENIC_MODERATE
    direction = EvidenceDirection.PATHOGENIC
    default_score = 2.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PM3 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        inheritance = context.get("inheritance_mode", "")
        if inheritance != "recessive":
            return self._not_met("Not applicable - gene not associated with recessive inheritance")
        
        compound_het_info = context.get("compound_heterozygous", variant.get("compound_het", {}))
        
        other_variant = compound_het_info.get("other_variant", {})
        phase_confirmed = compound_het_info.get("phase_confirmed", False)
        
        if not other_variant:
            return self._not_met("No other variant identified in compound heterozygosity analysis")
        
        other_classification = other_variant.get("classification", "").lower()
        if other_classification not in ("pathogenic", "likely pathogenic"):
            return self._not_met(f"Other variant is not pathogenic (classification: {other_classification})")
        
        if not phase_confirmed:
            return self._not_met("Phase not confirmed - parental testing or phasing analysis required")
        
        trans_confirmed = compound_het_info.get("in_trans", True)
        if not trans_confirmed:
            return self._not_met("Variants are in cis (same allele), not in trans")
        
        other_variant_id = other_variant.get("id", f"{other_variant.get('chromosome')}:{other_variant.get('position')}")
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=f"Detected in trans with pathogenic variant {other_variant_id}",
            evidence_sources=["segregation_analysis", "phasing_analysis"],
            confidence=0.9,
            metadata={
                "other_variant": other_variant_id,
                "other_classification": other_classification,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PM4(BaseCriterion):
    """
    PM4 - Protein length changes as a result of in-frame deletions/insertions
    in a nonrepeat region or stop-loss variants.
    """
    code = "PM4"
    name = "Protein length change in non-repeat region"
    evidence_strength = EvidenceStrength.PATHOGENIC_MODERATE
    direction = EvidenceDirection.PATHOGENIC
    default_score = 2.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PM4 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        
        is_inframe_indel = consequence in INFRAME_INDEL_CONSEQUENCES
        is_stop_loss = consequence == "stop_lost"
        
        if not is_inframe_indel and not is_stop_loss:
            return self._not_met("Variant is not an in-frame indel or stop-loss")
        
        if is_inframe_indel:
            repeat_info = variant.get("repeat_region", {})
            in_repeat = repeat_info.get("in_repeat", False)
            
            if in_repeat:
                return self._not_met("In-frame indel is in a repetitive region")
            
            indel_length = abs(len(variant.get("ref", "")) - len(variant.get("alt", "")))
            description = f"In-frame {'deletion' if 'deletion' in consequence else 'insertion'} of {indel_length} bp in non-repeat region"
        else:
            description = "Stop-loss variant predicted to extend protein"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["repeat_masker", "protein_annotation"],
            confidence=0.85,
            metadata={"consequence": consequence}
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PM5(BaseCriterion):
    """
    PM5 - Novel missense change at an amino acid residue where a different
    missense change determined to be pathogenic has been seen before.
    
    Example: Known pathogenic p.Arg500Trp, evaluating p.Arg500Gln
    """
    code = "PM5"
    name = "Novel missense at residue with known pathogenic missense"
    evidence_strength = EvidenceStrength.PATHOGENIC_MODERATE
    direction = EvidenceDirection.PATHOGENIC
    default_score = 2.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PM5 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        if consequence not in MISSENSE_CONSEQUENCES:
            return self._not_met("Variant is not a missense variant")
        
        hgvs_p = self._get_hgvs_p(variant)
        gene = self._get_gene(variant)
        
        if not hgvs_p:
            return self._not_met("No protein change annotation available")
        
        import re
        match = re.match(r"p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})", hgvs_p)
        if not match:
            return self._not_met(f"Cannot parse protein change: {hgvs_p}")
        
        ref_aa, position, alt_aa = match.groups()
        residue = position
        
        residue_variants = variant.get("residue_variants", [])
        pathogenic_at_residue = []
        
        for rv in residue_variants:
            if str(rv.get("position")) == residue and rv.get("gene") == gene:
                significance = rv.get("classification", "").lower()
                if significance in ("pathogenic", "likely pathogenic"):
                    if rv.get("hgvs_p") != hgvs_p:
                        pathogenic_at_residue.append(rv)
        
        if not pathogenic_at_residue:
            return self._not_met(f"No pathogenic missense variants at residue {residue}")
        
        other_changes = [rv.get("hgvs_p") for rv in pathogenic_at_residue[:3]]
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=f"Novel missense at residue {residue} where pathogenic missense variants exist ({', '.join(other_changes)})",
            evidence_sources=["ClinVar", "literature"],
            confidence=0.8,
            metadata={
                "residue": residue,
                "known_pathogenic": other_changes,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PM6(BaseCriterion):
    """
    PM6 - Assumed de novo, but without confirmation of paternity and maternity.
    
    Weaker evidence than PS2 due to lack of parentage confirmation.
    """
    code = "PM6"
    name = "Assumed de novo without parentage confirmation"
    evidence_strength = EvidenceStrength.PATHOGENIC_MODERATE
    direction = EvidenceDirection.PATHOGENIC
    default_score = 2.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PM6 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        inheritance_info = context.get("inheritance", {})
        
        assumed_de_novo = variant.get("assumed_de_novo", inheritance_info.get("assumed_de_novo", False))
        
        if not assumed_de_novo:
            is_de_novo = variant.get("de_novo", False)
            parentage_confirmed = inheritance_info.get("parentage_confirmed", False)
            
            if is_de_novo and parentage_confirmed:
                return self._not_met("De novo with confirmed parentage - use PS2 instead")
            
            if not is_de_novo:
                return self._not_met("Variant is not assumed to be de novo")
        
        parents_tested = inheritance_info.get("parents_tested", True)
        if not parents_tested:
            return self._not_met("Parents not tested")
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description="Assumed de novo variant (parentage not confirmed)",
            evidence_sources=["family_history", "segregation_analysis"],
            confidence=0.7,
            metadata={"parentage_confirmed": False}
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PP1(BaseCriterion):
    """
    PP1 - Co-segregation with disease in multiple affected family members
    in a gene definitively known to cause the disease.
    
    Note: Can be upgraded to Strong (PS1_moderate) with sufficient segregation.
    """
    code = "PP1"
    name = "Co-segregation with disease in multiple family members"
    evidence_strength = EvidenceStrength.PATHOGENIC_SUPPORTING
    direction = EvidenceDirection.PATHOGENIC
    default_score = 1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PP1 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        segregation_info = context.get("segregation", variant.get("segregation", {}))
        
        if not segregation_info:
            return self._not_met("No segregation data available")
        
        affected_with = segregation_info.get("affected_with_variant", 0)
        affected_without = segregation_info.get("affected_without_variant", 0)
        unaffected_with = segregation_info.get("unaffected_with_variant", 0)
        unaffected_without = segregation_info.get("unaffected_without_variant", 0)
        total_meioses = segregation_info.get("meioses_count", 0)
        
        if affected_without > 0:
            return self._not_met(f"Incomplete segregation: {affected_without} affected individuals without variant")
        
        if affected_with < 2:
            return self._not_met(f"Insufficient segregation: only {affected_with} affected individuals with variant")
        
        if unaffected_with > 0:
            penetrance_issue = True
        
        gene = self._get_gene(variant)
        gene_definitive = context.get("gene_definitive", True)
        
        if not gene_definitive:
            return self._not_met(f"Gene {gene} not definitively associated with disease")
        
        if affected_with >= 4 and total_meioses >= 3:
            strength = EvidenceStrength.PATHOGENIC_STRONG
            score = 4.0
            description = f"Strong co-segregation: {affected_with} affected members across {total_meioses} meioses"
        elif affected_with >= 3 and total_meioses >= 2:
            strength = EvidenceStrength.PATHOGENIC_MODERATE
            score = 2.0
            description = f"Moderate co-segregation: {affected_with} affected members across {total_meioses} meioses"
        else:
            strength = EvidenceStrength.PATHOGENIC_SUPPORTING
            score = 1.0
            description = f"Co-segregation with disease in {affected_with} affected family members"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=strength,
            direction=self.direction,
            score=score,
            description=description,
            evidence_sources=["family_segregation"],
            confidence=0.85,
            metadata={
                "affected_with_variant": affected_with,
                "meioses_count": total_meioses,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PP2(BaseCriterion):
    """
    PP2 - Missense variant in a gene that has a low rate of benign missense
    variation and in which missense variants are a common mechanism of disease.
    """
    code = "PP2"
    name = "Missense in gene with low benign missense rate"
    evidence_strength = EvidenceStrength.PATHOGENIC_SUPPORTING
    direction = EvidenceDirection.PATHOGENIC
    default_score = 1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PP2 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        if consequence not in MISSENSE_CONSEQUENCES:
            return self._not_met("Variant is not a missense variant")
        
        gene = self._get_gene(variant)
        gene_info = variant.get("gene_info", context.get("gene_info", {}))
        
        missense_as_mechanism = gene_info.get("missense_mechanism", False)
        if not missense_as_mechanism:
            return self._not_met(f"Missense variants not established as disease mechanism for {gene}")
        
        constraint = gene_info.get("constraint", {})
        missense_z = constraint.get("missense_z", 0)
        oeo_ratio = constraint.get("oeo_ratio", 0)
        
        if missense_z < 2.0 and oeo_ratio > 0.5:
            return self._not_met(f"Gene {gene} has high benign missense variation (Z={missense_z:.2f})")
        
        bening_missense_rate = gene_info.get("benign_missense_rate", 0.1)
        if bening_missense_rate > 0.3:
            return self._not_met(f"High benign missense rate ({bening_missense_rate:.2%})")
        
        description = f"Missense in gene {gene} with low benign missense rate"
        if missense_z >= 3.0:
            description += f" (Z={missense_z:.2f})"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["gnomAD_constraint", "gene_mechanism"],
            confidence=0.8,
            metadata={
                "missense_z": missense_z,
                "gene": gene,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PP3(BaseCriterion):
    """
    PP3 - Multiple lines of computational evidence support a deleterious
    effect on the gene or gene product.
    
    Requires concordant predictions from multiple algorithms.
    """
    code = "PP3"
    name = "Multiple computational evidence lines support deleterious effect"
    evidence_strength = EvidenceStrength.PATHOGENIC_SUPPORTING
    direction = EvidenceDirection.PATHOGENIC
    default_score = 1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PP3 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        predictions = variant.get("predictions", {})
        if not predictions:
            predictions = {
                "sift": variant.get("sift"),
                "polyphen": variant.get("polyphen"),
                "cadd": variant.get("cadd"),
                "revel": variant.get("revel"),
                "mutationtaster": variant.get("mutationtaster"),
                "spliceai": variant.get("spliceai"),
            }
        
        deleterious_count = 0
        total_count = 0
        prediction_details = []
        
        sift = predictions.get("sift")
        if sift is not None:
            total_count += 1
            if float(sift) <= 0.05:
                deleterious_count += 1
                prediction_details.append(f"SIFT={sift:.3f}(D)")
        
        polyphen = predictions.get("polyphen")
        if polyphen is not None:
            total_count += 1
            if float(polyphen) >= 0.85:
                deleterious_count += 1
                prediction_details.append(f"PolyPhen={polyphen:.2f}(D)")
        
        cadd = predictions.get("cadd")
        if cadd is not None:
            total_count += 1
            if float(cadd) >= 20:
                deleterious_count += 1
                prediction_details.append(f"CADD={cadd:.1f}(D)")
        
        revel = predictions.get("revel")
        if revel is not None:
            total_count += 1
            if float(revel) >= 0.5:
                deleterious_count += 1
                prediction_details.append(f"REVEL={revel:.2f}(D)")
        
        mutationtaster = predictions.get("mutationtaster")
        if mutationtaster is not None:
            total_count += 1
            if str(mutationtaster).lower() in ("d", "disease", "pathogenic"):
                deleterious_count += 1
                prediction_details.append(f"MT=D")
        
        spliceai = predictions.get("spliceai")
        if spliceai is not None:
            total_count += 1
            if float(spliceai) >= 0.5:
                deleterious_count += 1
                prediction_details.append(f"SpliceAI={spliceai:.2f}(D)")
        
        if total_count < 3:
            return self._not_met("Insufficient computational predictions available")
        
        deleterious_ratio = deleterious_count / total_count
        
        if deleterious_ratio < 0.6 or deleterious_count < 3:
            return self._not_met(f"Computational evidence not concordant ({deleterious_count}/{total_count} deleterious)")
        
        description = f"Multiple computational tools predict deleterious ({deleterious_count}/{total_count})"
        if prediction_details:
            description += f": {', '.join(prediction_details[:3])}"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["SIFT", "PolyPhen", "CADD", "REVEL"],
            confidence=min(0.9, deleterious_ratio),
            metadata={
                "deleterious_count": deleterious_count,
                "total_predictions": total_count,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PP4(BaseCriterion):
    """
    PP4 - Patient's phenotype or family history is highly specific for a
    disease with a single genetic etiology.
    """
    code = "PP4"
    name = "Phenotype highly specific for single genetic etiology"
    evidence_strength = EvidenceStrength.PATHOGENIC_SUPPORTING
    direction = EvidenceDirection.PATHOGENIC
    default_score = 1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PP4 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        phenotype_match = context.get("phenotype_match", {})
        
        if not phenotype_match:
            return self._not_met("No phenotype matching data available")
        
        specificity_score = phenotype_match.get("specificity_score", 0)
        gene_match_score = phenotype_match.get("gene_match_score", 0)
        single_gene = phenotype_match.get("single_gene_match", False)
        
        if not single_gene:
            gene = self._get_gene(variant)
            candidate_genes = phenotype_match.get("candidate_genes", [])
            if len(candidate_genes) > 1:
                return self._not_met(f"Multiple genes ({len(candidate_genes)}) could explain phenotype")
        
        if specificity_score < 0.7:
            return self._not_met(f"Phenotype not highly specific (specificity={specificity_score:.2f})")
        
        if gene_match_score < 0.8:
            return self._not_met(f"Gene-phenotype match not strong (match_score={gene_match_score:.2f})")
        
        description = "Patient phenotype highly specific for disease associated with this gene"
        if single_gene:
            description += " (single gene match)"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["phenotype_matching", "HPO"],
            confidence=min(specificity_score, gene_match_score),
            metadata={
                "specificity_score": specificity_score,
                "gene_match_score": gene_match_score,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class PP5(BaseCriterion):
    """
    PP5 - Reputable source recently reports variant as pathogenic, but the
    evidence is not available to the laboratory to perform independent evaluation.
    
    Note: This criterion is often used sparingly as it relies on trust in
    the reporting source without verification.
    """
    code = "PP5"
    name = "Reputable source reports as pathogenic"
    evidence_strength = EvidenceStrength.PATHOGENIC_SUPPORTING
    direction = EvidenceDirection.PATHOGENIC
    default_score = 1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating PP5 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        external_classifications = variant.get("external_classifications", [])
        
        if not external_classifications:
            clinvar_status = variant.get("clinvar_status", "")
            if clinvar_status:
                external_classifications = [{
                    "source": "ClinVar",
                    "classification": variant.get("clinvar_significance", ""),
                    "review_status": variant.get("clinvar_review_status", ""),
                }]
        
        pathogenic_reports = []
        for ec in external_classifications:
            classification = ec.get("classification", "").lower()
            if classification in ("pathogenic", "likely pathogenic"):
                source = ec.get("source", "unknown")
                review_status = ec.get("review_status", "")
                
                if review_status in ("reviewed_by_expert", "practice_guideline", "no_assertion"):
                    pathogenic_reports.append({
                        "source": source,
                        "classification": ec.get("classification"),
                        "review_status": review_status,
                    })
        
        if not pathogenic_reports:
            return self._not_met("No reputable source reports this variant as pathogenic")
        
        sources = [r["source"] for r in pathogenic_reports]
        description = f"Reported as pathogenic by reputable source(s): {', '.join(sources)}"
        
        confidence = 0.7
        for r in pathogenic_reports:
            if r["review_status"] == "practice_guideline":
                confidence = 0.9
                break
            elif r["review_status"] == "reviewed_by_expert":
                confidence = max(confidence, 0.8)
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=sources,
            confidence=confidence,
            metadata={"reports": pathogenic_reports}
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BA1(BaseCriterion):
    """
    BA1 - Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes,
    or ExAC. (Stand-alone benign criterion)
    
    Note: Threshold can be adjusted based on disease prevalence.
    """
    code = "BA1"
    name = "Allele frequency >5% in population databases"
    evidence_strength = EvidenceStrength.BENIGN_STANDALONE
    direction = EvidenceDirection.BENIGN
    default_score = -8.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BA1 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        af_gnomad = self._get_af_gnomad(variant)
        af_1000g = float(variant.get("af_1000g", 0) or 0)
        af_exac = float(variant.get("exac_af", 0) or 0)
        
        max_af = max(af_gnomad, af_1000g, af_exac)
        
        threshold = context.get("ba1_threshold", 0.05)
        
        if max_af < threshold:
            return self._not_met(f"Allele frequency ({max_af:.4f}) below {threshold:.2%} threshold")
        
        sources = []
        if af_gnomad >= threshold:
            sources.append(f"gnomAD={af_gnomad:.4f}")
        if af_1000g >= threshold:
            sources.append(f"1000G={af_1000g:.4f}")
        if af_exac >= threshold:
            sources.append(f"ExAC={af_exac:.4f}")
        
        description = f"High allele frequency ({max_af:.2%}) exceeds BA1 threshold"
        if sources:
            description += f": {', '.join(sources)}"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["gnomAD", "1000Genomes", "ExAC"],
            confidence=1.0,
            metadata={
                "max_af": max_af,
                "threshold": threshold,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BS1(BaseCriterion):
    """
    BS1 - Allele frequency is greater than expected for disorder.
    
    Takes into account disease prevalence and genetic heterogeneity.
    """
    code = "BS1"
    name = "Allele frequency greater than expected for disorder"
    evidence_strength = EvidenceStrength.BENIGN_STRONG
    direction = EvidenceDirection.BENIGN
    default_score = -4.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BS1 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        af_gnomad = self._get_af_gnomad(variant)
        
        prevalence = context.get("disease_prevalence", 0.0001)
        genetic_heterogeneity = context.get("genetic_heterogeneity", 0.1)
        penetrance = context.get("penetrance", 1.0)
        
        expected_max_af = (prevalence * genetic_heterogeneity) / penetrance
        
        inheritance = context.get("inheritance_mode", "dominant")
        if inheritance == "recessive":
            expected_max_af = (prevalence * genetic_heterogeneity) ** 0.5 / penetrance
        
        safety_factor = context.get("bs1_safety_factor", 2.0)
        threshold = expected_max_af * safety_factor
        
        if af_gnomad < threshold:
            return self._not_met(f"Allele frequency ({af_gnomad:.6f}) not greater than expected ({threshold:.6f})")
        
        description = f"Allele frequency ({af_gnomad:.4%}) exceeds expected for disease prevalence"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["gnomAD", "disease_prevalence"],
            confidence=0.9,
            metadata={
                "observed_af": af_gnomad,
                "expected_max_af": expected_max_af,
                "threshold": threshold,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BS2(BaseCriterion):
    """
    BS2 - Observed in a healthy adult individual for a recessive (homozygous),
    dominant (heterozygous), or X-linked (hemizygous) disorder, with full
    penetrance expected at an early age.
    """
    code = "BS2"
    name = "Observed in healthy adult (opposite inheritance pattern)"
    evidence_strength = EvidenceStrength.BENIGN_STRONG
    direction = EvidenceDirection.BENIGN
    default_score = -4.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BS2 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        healthy_carriers = variant.get("healthy_carriers", context.get("healthy_carriers", []))
        
        if not healthy_carriers:
            return self._not_met("No healthy carrier data available")
        
        inheritance = context.get("inheritance_mode", "dominant")
        age_of_onset = context.get("typical_age_of_onset", "adult")
        penetrance = context.get("penetrance", 1.0)
        
        if age_of_onset in ("childhood", "infantile", "neonatal") and penetrance >= 0.95:
            min_age = 50
        else:
            min_age = 60
        
        qualifying_carriers = []
        for carrier in healthy_carriers:
            carrier_age = carrier.get("age", 0)
            carrier_genotype = carrier.get("genotype", "")
            
            if inheritance == "dominant":
                if carrier_genotype in ("heterozygous", "het") and carrier_age >= min_age:
                    qualifying_carriers.append(carrier)
            elif inheritance == "recessive":
                if carrier_genotype in ("homozygous", "hom") and carrier_age >= min_age:
                    qualifying_carriers.append(carrier)
            elif inheritance == "x_linked":
                if carrier_genotype in ("hemizygous", "hem") and carrier_age >= min_age:
                    qualifying_carriers.append(carrier)
        
        if not qualifying_carriers:
            return self._not_met(f"No healthy carriers meeting age/genotype criteria for {inheritance} inheritance")
        
        description = f"Observed in {len(qualifying_carriers)} healthy adult(s) inconsistent with {inheritance} inheritance"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["population_databases", "healthy_cohorts"],
            confidence=0.9,
            metadata={
                "carrier_count": len(qualifying_carriers),
                "inheritance_mode": inheritance,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BS3(BaseCriterion):
    """
    BS3 - Well-established in vitro or in vivo functional studies show no
    damaging effect on protein function or splicing.
    """
    code = "BS3"
    name = "Functional studies show no damaging effect"
    evidence_strength = EvidenceStrength.BENIGN_STRONG
    direction = EvidenceDirection.BENIGN
    default_score = -4.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BS3 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        functional_studies = variant.get("functional_studies", [])
        
        if not functional_studies:
            return self._not_met("No functional studies available")
        
        benign_studies = []
        for study in functional_studies:
            result = study.get("result", "").lower()
            if self._is_study_benign(study):
                quality = self._assess_study_quality(study)
                if quality in ("well_established", "moderate"):
                    benign_studies.append(study)
        
        if not benign_studies:
            return self._not_met("No functional studies showing benign effect")
        
        description = f"Functional studies ({len(benign_studies)}) show no damaging effect"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=[s.get("reference", "functional_study") for s in benign_studies],
            confidence=0.9,
            metadata={"study_count": len(benign_studies)}
        )
    
    def _is_study_benign(self, study: Dict[str, Any]) -> bool:
        result = study.get("result", "").lower()
        if "benign" in result or "normal" in result or "wild-type" in result:
            return True
        if "neutral" in result or "no effect" in result:
            return True
        if study.get("is_benign", False):
            return True
        return False
    
    def _assess_study_quality(self, study: Dict[str, Any]) -> str:
        quality_score = study.get("quality_score", 0)
        validation = study.get("validated", False)
        
        if quality_score >= 4 and validation:
            return "well_established"
        elif quality_score >= 3:
            return "moderate"
        else:
            return "limited"
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BS4(BaseCriterion):
    """
    BS4 - Lack of segregation in affected members of a family.
    """
    code = "BS4"
    name = "Lack of segregation in affected family members"
    evidence_strength = EvidenceStrength.BENIGN_STRONG
    direction = EvidenceDirection.BENIGN
    default_score = -4.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BS4 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        segregation_info = context.get("segregation", variant.get("segregation", {}))
        
        if not segregation_info:
            return self._not_met("No segregation data available")
        
        affected_without_variant = segregation_info.get("affected_without_variant", 0)
        affected_with_variant = segregation_info.get("affected_with_variant", 0)
        
        if affected_without_variant == 0:
            return self._not_met("No affected individuals without the variant")
        
        penetrance = context.get("penetrance", 1.0)
        if penetrance < 0.5:
            return self._not_met(f"Reduced penetrance ({penetrance:.0%}) complicates segregation interpretation")
        
        description = f"Variant does not segregate with disease ({affected_without_variant} affected without variant)"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["family_segregation"],
            confidence=0.9,
            metadata={
                "affected_without_variant": affected_without_variant,
                "affected_with_variant": affected_with_variant,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BP1(BaseCriterion):
    """
    BP1 - Missense variant in a gene for which primarily truncating variants
    are known to cause disease.
    """
    code = "BP1"
    name = "Missense in gene where truncating variants cause disease"
    evidence_strength = EvidenceStrength.BENIGN_SUPPORTING
    direction = EvidenceDirection.BENIGN
    default_score = -1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BP1 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        if consequence not in MISSENSE_CONSEQUENCES:
            return self._not_met("Variant is not a missense variant")
        
        gene = self._get_gene(variant)
        gene_info = variant.get("gene_info", context.get("gene_info", {}))
        
        lof_primary_mechanism = gene_info.get("lof_primary_mechanism", False)
        missense_pathogenic_count = gene_info.get("pathogenic_missense_count", 0)
        
        if not lof_primary_mechanism:
            return self._not_met(f"LOF not primary mechanism for {gene}")
        
        if missense_pathogenic_count > 5:
            return self._not_met(f"Multiple pathogenic missense variants exist for {gene}")
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=f"Missense in gene {gene} where truncating variants are primary disease mechanism",
            evidence_sources=["gene_mechanism_database"],
            confidence=0.8,
            metadata={"gene": gene}
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BP2(BaseCriterion):
    """
    BP2 - Observed in trans with a pathogenic variant for a recessive disorder,
    or observed in cis with a pathogenic variant in any inheritance pattern.
    """
    code = "BP2"
    name = "Observed in trans/cis with pathogenic variant"
    evidence_strength = EvidenceStrength.BENIGN_SUPPORTING
    direction = EvidenceDirection.BENIGN
    default_score = -1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BP2 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        phase_info = context.get("phase_info", variant.get("phase_info", {}))
        
        in_cis_with_pathogenic = phase_info.get("in_cis_with_pathogenic", False)
        in_trans_with_pathogenic = phase_info.get("in_trans_with_pathogenic", False)
        
        if not in_cis_with_pathogenic and not in_trans_with_pathogenic:
            return self._not_met("Not observed in cis or trans with a pathogenic variant")
        
        if in_cis_with_pathogenic:
            other_variant = phase_info.get("cis_variant", {})
            description = f"Observed in cis with pathogenic variant {other_variant.get('id', 'unknown')}"
        else:
            other_variant = phase_info.get("trans_variant", {})
            inheritance = context.get("inheritance_mode", "")
            if inheritance != "recessive":
                return self._not_met("In trans with pathogenic variant only applicable for recessive disorders")
            description = f"Observed in trans with pathogenic variant {other_variant.get('id', 'unknown')} (recessive)"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["phasing_analysis"],
            confidence=0.85,
            metadata=phase_info
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BP3(BaseCriterion):
    """
    BP3 - In-frame deletions/insertions in a repetitive region without a
    known function.
    """
    code = "BP3"
    name = "In-frame indel in repetitive region without known function"
    evidence_strength = EvidenceStrength.BENIGN_SUPPORTING
    direction = EvidenceDirection.BENIGN
    default_score = -1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BP3 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        if consequence not in INFRAME_INDEL_CONSEQUENCES:
            return self._not_met("Variant is not an in-frame insertion or deletion")
        
        repeat_info = variant.get("repeat_region", {})
        in_repeat = repeat_info.get("in_repeat", False)
        repeat_type = repeat_info.get("repeat_type", "")
        has_known_function = repeat_info.get("has_known_function", False)
        
        if not in_repeat:
            return self._not_met("Not in a repetitive region")
        
        if has_known_function:
            return self._not_met("Repetitive region has known functional significance")
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=f"In-frame indel in repetitive {repeat_type or 'region'} without known function",
            evidence_sources=["repeat_masker", "functional_annotation"],
            confidence=0.85,
            metadata={"repeat_type": repeat_type}
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BP4(BaseCriterion):
    """
    BP4 - Multiple lines of computational evidence suggest no impact on
    gene or gene product.
    """
    code = "BP4"
    name = "Computational evidence suggests no impact"
    evidence_strength = EvidenceStrength.BENIGN_SUPPORTING
    direction = EvidenceDirection.BENIGN
    default_score = -1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BP4 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        predictions = variant.get("predictions", {})
        if not predictions:
            predictions = {
                "sift": variant.get("sift"),
                "polyphen": variant.get("polyphen"),
                "cadd": variant.get("cadd"),
                "revel": variant.get("revel"),
            }
        
        benign_count = 0
        total_count = 0
        prediction_details = []
        
        sift = predictions.get("sift")
        if sift is not None:
            total_count += 1
            if float(sift) > 0.05:
                benign_count += 1
                prediction_details.append(f"SIFT={sift:.3f}(T)")
        
        polyphen = predictions.get("polyphen")
        if polyphen is not None:
            total_count += 1
            if float(polyphen) <= 0.15:
                benign_count += 1
                prediction_details.append(f"PolyPhen={polyphen:.2f}(B)")
        
        cadd = predictions.get("cadd")
        if cadd is not None:
            total_count += 1
            if float(cadd) < 15:
                benign_count += 1
                prediction_details.append(f"CADD={cadd:.1f}(B)")
        
        revel = predictions.get("revel")
        if revel is not None:
            total_count += 1
            if float(revel) < 0.3:
                benign_count += 1
                prediction_details.append(f"REVEL={revel:.2f}(B)")
        
        if total_count < 3:
            return self._not_met("Insufficient computational predictions available")
        
        benign_ratio = benign_count / total_count
        
        if benign_ratio < 0.6 or benign_count < 3:
            return self._not_met(f"Computational evidence not concordant for benign ({benign_count}/{total_count})")
        
        description = f"Multiple computational tools predict benign ({benign_count}/{total_count})"
        if prediction_details:
            description += f": {', '.join(prediction_details[:3])}"
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=["SIFT", "PolyPhen", "CADD", "REVEL"],
            confidence=min(0.9, benign_ratio),
            metadata={
                "benign_count": benign_count,
                "total_predictions": total_count,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BP5(BaseCriterion):
    """
    BP5 - Variant found in a case with an alternate molecular basis for disease.
    """
    code = "BP5"
    name = "Variant found in case with alternate molecular basis"
    evidence_strength = EvidenceStrength.BENIGN_SUPPORTING
    direction = EvidenceDirection.BENIGN
    default_score = -1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BP5 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        case_info = context.get("case_info", {})
        
        has_alternate_diagnosis = case_info.get("alternate_molecular_diagnosis", False)
        primary_cause = case_info.get("primary_genetic_cause", {})
        
        if not has_alternate_diagnosis:
            return self._not_met("No alternate molecular basis for disease identified")
        
        primary_gene = primary_cause.get("gene", "")
        current_gene = self._get_gene(variant)
        
        if current_gene == primary_gene:
            return self._not_met("Cannot exclude as alternative cause in same gene")
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=f"Variant found in case with alternate diagnosis ({primary_gene})",
            evidence_sources=["case_notes", "diagnostic_workup"],
            confidence=0.8,
            metadata={"alternate_gene": primary_gene}
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BP6(BaseCriterion):
    """
    BP6 - Reputable source recently reports variant as benign, but the
    evidence is not available to the laboratory to perform independent evaluation.
    """
    code = "BP6"
    name = "Reputable source reports as benign"
    evidence_strength = EvidenceStrength.BENIGN_SUPPORTING
    direction = EvidenceDirection.BENIGN
    default_score = -1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BP6 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        external_classifications = variant.get("external_classifications", [])
        
        if not external_classifications:
            clinvar_status = variant.get("clinvar_status", "")
            if clinvar_status:
                external_classifications = [{
                    "source": "ClinVar",
                    "classification": variant.get("clinvar_significance", ""),
                    "review_status": variant.get("clinvar_review_status", ""),
                }]
        
        benign_reports = []
        for ec in external_classifications:
            classification = ec.get("classification", "").lower()
            if classification in ("benign", "likely benign"):
                source = ec.get("source", "unknown")
                review_status = ec.get("review_status", "")
                benign_reports.append({
                    "source": source,
                    "classification": ec.get("classification"),
                    "review_status": review_status,
                })
        
        if not benign_reports:
            return self._not_met("No reputable source reports this variant as benign")
        
        sources = [r["source"] for r in benign_reports]
        description = f"Reported as benign by reputable source(s): {', '.join(sources)}"
        
        confidence = 0.7
        for r in benign_reports:
            if r["review_status"] == "practice_guideline":
                confidence = 0.9
                break
            elif r["review_status"] == "reviewed_by_expert":
                confidence = max(confidence, 0.8)
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description=description,
            evidence_sources=sources,
            confidence=confidence,
            metadata={"reports": benign_reports}
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


class BP7(BaseCriterion):
    """
    BP7 - A synonymous (silent) variant for which splicing prediction algorithms
    predict no impact to the splice consensus sequence nor the creation of a
    new splice site, and the nucleotide is not highly conserved.
    """
    code = "BP7"
    name = "Synonymous variant with no predicted splicing impact"
    evidence_strength = EvidenceStrength.BENIGN_SUPPORTING
    direction = EvidenceDirection.BENIGN
    default_score = -1.0
    
    def evaluate(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> CriterionResult:
        self.logger.debug(f"Evaluating BP7 for variant {variant.get('chromosome')}:{variant.get('position')}")
        context = context or {}
        
        consequence = self._get_consequence(variant)
        if consequence not in SYNONYMOUS_CONSEQUENCES:
            return self._not_met("Variant is not synonymous")
        
        spliceai_score = variant.get("spliceai_score", 0)
        maxent_diff = abs(variant.get("maxent_diff", 0))
        
        if spliceai_score >= 0.5:
            return self._not_met(f"SpliceAI predicts splice impact (score={spliceai_score:.2f})")
        
        if maxent_diff >= 3:
            return self._not_met(f"MaxEntScan suggests splice impact (diff={maxent_diff:.1f})")
        
        conservation = variant.get("phylop", 0)
        gerp = variant.get("gerp", 0)
        
        if conservation > 4.0 or gerp > 3.0:
            return self._not_met("Nucleotide is highly conserved")
        
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=True,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=self.get_score(),
            description="Synonymous variant with no predicted splice impact and low conservation",
            evidence_sources=["SpliceAI", "MaxEntScan", "phyloP"],
            confidence=0.85,
            metadata={
                "spliceai_score": spliceai_score,
                "maxent_diff": maxent_diff,
                "phylop": conservation,
            }
        )
    
    def _not_met(self, reason: str) -> CriterionResult:
        return CriterionResult(
            criterion_code=self.code,
            criterion_name=self.name,
            is_met=False,
            evidence_strength=self.evidence_strength,
            direction=self.direction,
            score=0.0,
            description=reason,
            confidence=1.0,
        )


CRITERIA_REGISTRY: Dict[str, type] = {
    "PVS1": PVS1,
    "PS1": PS1,
    "PS2": PS2,
    "PS3": PS3,
    "PS4": PS4,
    "PM1": PM1,
    "PM2": PM2,
    "PM3": PM3,
    "PM4": PM4,
    "PM5": PM5,
    "PM6": PM6,
    "PP1": PP1,
    "PP2": PP2,
    "PP3": PP3,
    "PP4": PP4,
    "PP5": PP5,
    "BA1": BA1,
    "BS1": BS1,
    "BS2": BS2,
    "BS3": BS3,
    "BS4": BS4,
    "BP1": BP1,
    "BP2": BP2,
    "BP3": BP3,
    "BP4": BP4,
    "BP5": BP5,
    "BP6": BP6,
    "BP7": BP7,
}


def get_criterion_class(code: str) -> Optional[type]:
    return CRITERIA_REGISTRY.get(code.upper())


def get_all_criteria_codes() -> List[str]:
    return list(CRITERIA_REGISTRY.keys())


def register_criterion(criterion_class: type) -> None:
    if hasattr(criterion_class, 'code') and criterion_class.code:
        CRITERIA_REGISTRY[criterion_class.code] = criterion_class
        logger.info(f"Registered ACMG criterion: {criterion_class.code}")
    else:
        raise ValueError("Criterion class must have a 'code' attribute")
