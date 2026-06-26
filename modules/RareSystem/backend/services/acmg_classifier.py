"""
ACMG/AMP Variant Classifier - Rule Engine Architecture

This module implements the ACMG/AMP variant classification system using a
rule engine architecture. It supports:
- All 28 ACMG criteria evaluation
- Point-based evidence scoring
- Configurable classification thresholds
- Evidence chain traceability
- Classification summary generation

Reference: Richards et al. 2015. Genet Med. 17(5):405-424.
"""
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .acmg_criteria import (
    BaseCriterion,
    CRITERIA_REGISTRY,
    CriterionResult,
    EvidenceDirection,
    EvidenceStrength,
    get_criterion_class,
    get_all_criteria_codes,
)

logger = logging.getLogger(__name__)


class ClassificationCategory(Enum):
    """ACMG classification categories."""
    PATHOGENIC = "Pathogenic"
    LIKELY_PATHOGENIC = "Likely Pathogenic"
    UNCERTAIN_SIGNIFICANCE = "Variant of Uncertain Significance"
    LIKELY_BENIGN = "Likely Benign"
    BENIGN = "Benign"


@dataclass
class ClassificationResult:
    """Complete classification result for a variant."""
    variant_id: str
    classification: ClassificationCategory
    confidence_score: float
    total_pathogenic_score: float
    total_benign_score: float
    pathogenic_criteria: List[CriterionResult] = field(default_factory=list)
    benign_criteria: List[CriterionResult] = field(default_factory=list)
    evidence_chain: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "variant_id": self.variant_id,
            "classification": self.classification.value,
            "confidence_score": self.confidence_score,
            "total_pathogenic_score": self.total_pathogenic_score,
            "total_benign_score": self.total_benign_score,
            "pathogenic_criteria": [c.to_dict() for c in self.pathogenic_criteria],
            "benign_criteria": [c.to_dict() for c in self.benign_criteria],
            "evidence_chain": self.evidence_chain,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


@dataclass
class ScoringThresholds:
    """Threshold values for classification based on point scores."""
    pathogenic_threshold: float = 10.0
    likely_pathogenic_threshold: float = 6.0
    likely_benign_threshold: float = -6.0
    benign_threshold: float = -10.0
    
    pvs1_count_for_pathogenic: int = 1
    ps_count_for_pathogenic: int = 2
    pm_count_for_pathogenic: int = 3
    pp_count_for_pathogenic: int = 4


class ACMGClassifier:
    """
    ACMG/AMP Variant Classification Rule Engine.
    
    This class orchestrates the evaluation of all ACMG criteria for a given variant
    and produces a classification based on the combined evidence.
    
    Usage:
        classifier = ACMGClassifier()
        result = classifier.classify(variant_data)
        print(result.classification)
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ACMG classifier.
        
        Args:
            config: Configuration dictionary containing:
                - criteria: Per-criterion configuration
                - thresholds: Classification thresholds
                - enabled_criteria: List of criteria codes to enable
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        self.criteria_instances: Dict[str, BaseCriterion] = {}
        self.thresholds = self._load_thresholds()
        self._initialize_criteria()
        
        self.logger.info(f"ACMGClassifier v{self.VERSION} initialized with {len(self.criteria_instances)} criteria")
    
    def _load_thresholds(self) -> ScoringThresholds:
        """Load scoring thresholds from configuration."""
        threshold_config = self.config.get("thresholds", {})
        return ScoringThresholds(
            pathogenic_threshold=threshold_config.get("pathogenic", 10.0),
            likely_pathogenic_threshold=threshold_config.get("likely_pathogenic", 6.0),
            likely_benign_threshold=threshold_config.get("likely_benign", -6.0),
            benign_threshold=threshold_config.get("benign", -10.0),
            pvs1_count_for_pathogenic=threshold_config.get("pvs1_count", 1),
            ps_count_for_pathogenic=threshold_config.get("ps_count", 2),
            pm_count_for_pathogenic=threshold_config.get("pm_count", 3),
            pp_count_for_pathogenic=threshold_config.get("pp_count", 4),
        )
    
    def _initialize_criteria(self) -> None:
        """Initialize criterion instances from registry."""
        criteria_config = self.config.get("criteria", {})
        enabled_criteria = self.config.get("enabled_criteria", get_all_criteria_codes())
        
        for code in enabled_criteria:
            criterion_class = get_criterion_class(code)
            if criterion_class:
                criterion_config_for_code = criteria_config.get(code, {})
                self.criteria_instances[code] = criterion_class(config=criterion_config_for_code)
                self.logger.debug(f"Initialized criterion: {code}")
            else:
                self.logger.warning(f"Unknown criterion code: {code}")
    
    def classify(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """
        Classify a variant using all enabled ACMG criteria.
        
        Args:
            variant: Variant data dictionary containing genomic information,
                     annotations, and population frequencies.
            context: Additional context (patient info, family data, etc.)
        
        Returns:
            ClassificationResult with final classification and evidence.
        """
        variant_id = self._get_variant_id(variant)
        self.logger.info(f"Classifying variant: {variant_id}")
        
        pathogenic_results: List[CriterionResult] = []
        benign_results: List[CriterionResult] = []
        evidence_chain: List[Dict[str, Any]] = []
        warnings: List[str] = []
        
        for code, criterion in self.criteria_instances.items():
            if not criterion.is_enabled():
                continue
            
            try:
                self.logger.debug(f"Evaluating criterion: {code}")
                result = criterion.evaluate(variant, context)
                
                if result.is_met:
                    evidence_chain.append({
                        "criterion": code,
                        "description": result.description,
                        "score": result.score,
                        "confidence": result.confidence,
                        "sources": result.evidence_sources,
                    })
                
                if result.direction == EvidenceDirection.PATHOGENIC:
                    pathogenic_results.append(result)
                else:
                    benign_results.append(result)
                    
            except Exception as e:
                self.logger.error(f"Error evaluating {code}: {e}")
                warnings.append(f"Evaluation error for {code}: {str(e)}")
        
        total_pathogenic_score = sum(r.score for r in pathogenic_results if r.is_met)
        total_benign_score = sum(r.score for r in benign_results if r.is_met)
        
        classification = self._determine_classification(
            pathogenic_results, 
            benign_results,
            total_pathogenic_score,
            total_benign_score,
            warnings
        )
        
        confidence = self._calculate_confidence(
            pathogenic_results, 
            benign_results, 
            classification
        )
        
        result = ClassificationResult(
            variant_id=variant_id,
            classification=classification,
            confidence_score=confidence,
            total_pathogenic_score=total_pathogenic_score,
            total_benign_score=total_benign_score,
            pathogenic_criteria=pathogenic_results,
            benign_criteria=benign_results,
            evidence_chain=evidence_chain,
            warnings=warnings,
            metadata={
                "classifier_version": self.VERSION,
                "criteria_count": len(self.criteria_instances),
            }
        )
        
        self.logger.info(
            f"Classification result: {classification.value} "
            f"(P={total_pathogenic_score:.1f}, B={total_benign_score:.1f})"
        )
        
        return result
    
    def get_evidence(self, variant: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, CriterionResult]:
        """
        Get evidence for each criterion without determining classification.
        
        Args:
            variant: Variant data dictionary
            context: Additional context
        
        Returns:
            Dictionary mapping criterion codes to their results.
        """
        evidence: Dict[str, CriterionResult] = {}
        
        for code, criterion in self.criteria_instances.items():
            if criterion.is_enabled():
                try:
                    evidence[code] = criterion.evaluate(variant, context)
                except Exception as e:
                    self.logger.error(f"Error evaluating {code}: {e}")
                    evidence[code] = CriterionResult(
                        criterion_code=code,
                        criterion_name=criterion.name,
                        is_met=False,
                        evidence_strength=criterion.evidence_strength,
                        direction=criterion.direction,
                        score=0.0,
                        description=f"Evaluation error: {str(e)}",
                        confidence=0.0,
                    )
        
        return evidence
    
    def get_classification_summary(self, result: ClassificationResult) -> str:
        """
        Generate a human-readable classification summary.
        
        Args:
            result: ClassificationResult to summarize
        
        Returns:
            Formatted summary string.
        """
        lines = [
            f"ACMG Classification Summary",
            f"=" * 50,
            f"Variant: {result.variant_id}",
            f"Classification: {result.classification.value}",
            f"Confidence: {result.confidence_score:.2%}",
            f"",
            f"Evidence Scores:",
            f"  Pathogenic: {result.total_pathogenic_score:.1f}",
            f"  Benign: {result.total_benign_score:.1f}",
            f"",
        ]
        
        if result.pathogenic_criteria:
            lines.append("Pathogenic Evidence:")
            for c in result.pathogenic_criteria:
                if c.is_met:
                    lines.append(f"  [{c.criterion_code}] {c.description[:80]}")
        
        if result.benign_criteria:
            lines.append("")
            lines.append("Benign Evidence:")
            for c in result.benign_criteria:
                if c.is_met:
                    lines.append(f"  [{c.criterion_code}] {c.description[:80]}")
        
        if result.warnings:
            lines.append("")
            lines.append("Warnings:")
            for w in result.warnings:
                lines.append(f"  - {w}")
        
        return "\n".join(lines)
    
    def _get_variant_id(self, variant: Dict[str, Any]) -> str:
        """Generate a unique variant identifier."""
        chrom = variant.get("chromosome", variant.get("chr", "?"))
        pos = variant.get("position", variant.get("pos", "?"))
        ref = variant.get("ref", "?")
        alt = variant.get("alt", "?")
        return f"{chrom}:{pos}:{ref}:{alt}"
    
    def _determine_classification(
        self,
        pathogenic: List[CriterionResult],
        benign: List[CriterionResult],
        p_score: float,
        b_score: float,
        warnings: List[str]
    ) -> ClassificationCategory:
        """
        Determine final classification based on evidence.
        
        Uses both point-based scoring and ACMG combining rules.
        """
        met_pathogenic = [c for c in pathogenic if c.is_met]
        met_benign = [c for c in benign if c.is_met]
        
        pvs1_met = any(c.criterion_code == "PVS1" for c in met_pathogenic)
        ps_met = sum(1 for c in met_pathogenic if c.criterion_code.startswith("PS"))
        pm_met = sum(1 for c in met_pathogenic if c.criterion_code.startswith("PM"))
        pp_met = sum(1 for c in met_pathogenic if c.criterion_code.startswith("PP"))
        
        ba1_met = any(c.criterion_code == "BA1" for c in met_benign)
        bs_met = sum(1 for c in met_benign if c.criterion_code.startswith("BS"))
        bp_met = sum(1 for c in met_benign if c.criterion_code.startswith("BP"))
        
        if ba1_met:
            return ClassificationCategory.BENIGN
        
        if b_score <= self.thresholds.benign_threshold:
            return ClassificationCategory.BENIGN
        
        if b_score <= self.thresholds.likely_benign_threshold:
            return ClassificationCategory.LIKELY_BENIGN
        
        if ba1_met or bs_met >= 2:
            return ClassificationCategory.LIKELY_BENIGN
        
        if pvs1_met and (ps_met >= 1 or pm_met >= 2 or (pm_met >= 1 and pp_met >= 1) or pp_met >= 2):
            return ClassificationCategory.PATHOGENIC
        
        if ps_met >= 2:
            return ClassificationCategory.PATHOGENIC
        
        if ps_met >= 1 and (pm_met >= 3 or (pm_met >= 2 and pp_met >= 2) or (pm_met >= 1 and pp_met >= 4)):
            return ClassificationCategory.PATHOGENIC
        
        if p_score >= self.thresholds.pathogenic_threshold:
            return ClassificationCategory.PATHOGENIC
        
        if p_score >= self.thresholds.likely_pathogenic_threshold:
            return ClassificationCategory.LIKELY_PATHOGENIC
        
        if ps_met >= 1 or pm_met >= 3 or (pm_met >= 2 and pp_met >= 2) or (pm_met >= 1 and pp_met >= 4):
            return ClassificationCategory.LIKELY_PATHOGENIC
        
        return ClassificationCategory.UNCERTAIN_SIGNIFICANCE
    
    def _calculate_confidence(
        self,
        pathogenic: List[CriterionResult],
        benign: List[CriterionResult],
        classification: ClassificationCategory
    ) -> float:
        """Calculate confidence score for the classification."""
        met_pathogenic = [c for c in pathogenic if c.is_met]
        met_benign = [c for c in benign if c.is_met]
        
        if not met_pathogenic and not met_benign:
            return 0.5
        
        avg_pathogenic_conf = (
            sum(c.confidence for c in met_pathogenic) / len(met_pathogenic)
            if met_pathogenic else 0.0
        )
        avg_benign_conf = (
            sum(c.confidence for c in met_benign) / len(met_benign)
            if met_benign else 0.0
        )
        
        if classification in (ClassificationCategory.PATHOGENIC, ClassificationCategory.LIKELY_PATHOGENIC):
            evidence_strength = avg_pathogenic_conf
            contradicting = avg_benign_conf
        else:
            evidence_strength = avg_benign_conf
            contradicting = avg_pathogenic_conf
        
        evidence_count = len(met_pathogenic) + len(met_benign)
        count_factor = min(1.0, evidence_count / 5.0)
        
        confidence = (evidence_strength * 0.6 + count_factor * 0.2 + (1 - contradicting) * 0.2)
        
        return min(1.0, max(0.0, confidence))
    
    def register_custom_criterion(self, criterion: BaseCriterion) -> None:
        """Register a custom criterion instance."""
        self.criteria_instances[criterion.code] = criterion
        self.logger.info(f"Registered custom criterion: {criterion.code}")
    
    def get_registered_criteria(self) -> List[str]:
        """Get list of all registered criteria codes."""
        return list(self.criteria_instances.keys())


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load classifier configuration from file.
    
    Args:
        config_path: Path to JSON configuration file.
                    Defaults to config/acmg_config.json
    
    Returns:
        Configuration dictionary.
    """
    if config_path is None:
        config_path = str(Path(__file__).parent.parent.parent / "config" / "acmg_config.json")
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Configuration file not found at {config_path}, using defaults")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return {}


def create_classifier(config_path: Optional[str] = None) -> ACMGClassifier:
    """
    Factory function to create an ACMGClassifier instance.
    
    Args:
        config_path: Optional path to configuration file.
    
    Returns:
        Configured ACMGClassifier instance.
    """
    config = load_config(config_path)
    return ACMGClassifier(config=config)
