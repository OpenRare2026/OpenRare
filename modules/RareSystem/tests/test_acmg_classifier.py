"""
Tests for how ACMGClassifier combines met criteria into a classification.

Expected classes follow the combining rules in Richards et al. 2015, Table 5.
"""
import pytest
from backend.services.acmg_classifier import ACMGClassifier, ClassificationCategory
from backend.services.acmg_criteria import (
    BaseCriterion,
    CriterionResult,
    EvidenceDirection,
    EvidenceStrength,
)

STRENGTHS = {
    "PVS": (EvidenceStrength.PATHOGENIC_VERY_STRONG, 8.0),
    "PS": (EvidenceStrength.PATHOGENIC_STRONG, 4.0),
    "PM": (EvidenceStrength.PATHOGENIC_MODERATE, 2.0),
    "PP": (EvidenceStrength.PATHOGENIC_SUPPORTING, 1.0),
    "BA": (EvidenceStrength.BENIGN_STANDALONE, -8.0),
    "BS": (EvidenceStrength.BENIGN_STRONG, -4.0),
    "BP": (EvidenceStrength.BENIGN_SUPPORTING, -1.0),
}


class AlwaysMet(BaseCriterion):
    """A criterion that is met for any variant, with the default score for its strength."""

    def __init__(self, code):
        self.code = code
        super().__init__()

    def evaluate(self, variant, context=None):
        strength, score = STRENGTHS[self.code.rstrip("0123456789")]
        direction = EvidenceDirection.BENIGN if self.code.startswith("B") else EvidenceDirection.PATHOGENIC
        return CriterionResult(self.code, self.code, True, strength, direction, score)


def classify(*codes):
    classifier = ACMGClassifier(config={"enabled_criteria": []})
    for code in codes:
        classifier.register_custom_criterion(AlwaysMet(code))
    return classifier.classify({}).classification


@pytest.mark.parametrize("codes", [("PS3",), ("PS2",), ("PS3", "PP3")])
def test_one_strong_alone_or_with_one_supporting_is_vus(codes):
    assert classify(*codes) == ClassificationCategory.UNCERTAIN_SIGNIFICANCE


@pytest.mark.parametrize("codes", [("PS3", "PM1"), ("PS3", "PP3", "PP4")])
def test_one_strong_with_one_moderate_or_two_supporting_is_likely_pathogenic(codes):
    assert classify(*codes) == ClassificationCategory.LIKELY_PATHOGENIC


def test_two_strong_benign_is_benign():
    assert classify("BS1", "BS2") == ClassificationCategory.BENIGN


LAST_EXON = {"exon_info": {"is_last_exon": True}}
NMD_RESCUE = {"gene_info": {"other_transcripts": [{"escapes_nmd": True}]}}


@pytest.mark.parametrize(
    "extra, expected",
    [
        ({}, ClassificationCategory.PATHOGENIC),  # PVS1 + PM2 + PP4
        (LAST_EXON, ClassificationCategory.LIKELY_PATHOGENIC),  # PVS1_Strong + PM2 + PP4
        ({**LAST_EXON, **NMD_RESCUE}, ClassificationCategory.UNCERTAIN_SIGNIFICANCE),  # PVS1_Moderate + PM2 + PP4
    ],
)
def test_pvs1_counts_at_its_applied_strength(extra, expected):
    classifier = ACMGClassifier(config={"enabled_criteria": ["PVS1", "PM2", "PP4"]})
    variant = {"gene": "GENE1", "consequence": "stop_gained", "gnomad_af": 0.0, **extra}
    context = {
        "lof_disease_genes": ["GENE1"],
        "phenotype_match": {"specificity_score": 0.9, "gene_match_score": 0.9, "single_gene_match": True},
    }
    assert classifier.classify(variant, context).classification == expected
