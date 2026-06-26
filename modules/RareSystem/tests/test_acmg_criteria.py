"""
Unit tests for ACMG/AMP criteria evaluation.

Tests all 28 ACMG criteria with various variant scenarios.
"""
import pytest
from backend.services.acmg_criteria import (
    PVS1, PS1, PS2, PS3, PS4,
    PM1, PM2, PM3, PM4, PM5, PM6,
    PP1, PP2, PP3, PP4, PP5,
    BA1, BS1, BS2, BS3, BS4,
    BP1, BP2, BP3, BP4, BP5, BP6, BP7,
    EvidenceStrength, EvidenceDirection, CriterionResult,
)


class TestPVS1:
    """Tests for PVS1 criterion - Null variant in LOF gene."""
    
    def test_pvs1_frameshift_in_lof_gene(self):
        criterion = PVS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "AT",
            "consequence": "frameshift_variant",
            "gene": "BRCA1",
            "gene_info": {"lof_mechanism": True},
        }
        context = {"lof_disease_genes": {"BRCA1", "TP53", "CFTR"}}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_VERY_STRONG
        assert result.score > 0
        assert "frameshift_variant" in result.description.lower() or "null variant" in result.description.lower()
    
    def test_pvs1_nonsense_in_lof_gene(self):
        criterion = PVS1()
        variant = {
            "chromosome": "chr17",
            "position": 7577559,
            "ref": "C",
            "alt": "T",
            "consequence": "stop_gained",
            "gene": "TP53",
        }
        context = {"gene_lof_mechanism": True}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_VERY_STRONG
    
    def test_pvs1_splice_donor_in_lof_gene(self):
        criterion = PVS1()
        variant = {
            "chromosome": "chr7",
            "position": 117199646,
            "ref": "G",
            "alt": "A",
            "consequence": "splice_donor_variant",
            "gene": "CFTR",
            "spliceai_score": 0.95,
        }
        context = {"lof_disease_genes": {"CFTR"}}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
    
    def test_pvs1_not_met_missense(self):
        criterion = PVS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "BRCA1",
        }
        context = {"lof_disease_genes": {"BRCA1"}}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False
        assert "not a null variant" in result.description.lower()
    
    def test_pvs1_not_met_gene_not_lof(self):
        criterion = PVS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "AT",
            "consequence": "frameshift_variant",
            "gene": "GENEX",
        }
        context = {"lof_disease_genes": {"BRCA1", "TP53"}}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False
        assert "not known" in result.description.lower() or "lof" in result.description.lower()
    
    def test_pvs1_strength_modifier_last_exon(self):
        criterion = PVS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "AT",
            "consequence": "frameshift_variant",
            "gene": "BRCA1",
            "gene_info": {"lof_mechanism": True},
            "exon_info": {"is_last_exon": True},
        }
        context = {"lof_disease_genes": {"BRCA1"}}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength != EvidenceStrength.PATHOGENIC_VERY_STRONG
        assert any("nmd" in w.lower() or "last exon" in w.lower() for w in result.metadata.get("warnings", []))


class TestPS1:
    """Tests for PS1 criterion - Same amino acid change as pathogenic variant."""
    
    def test_ps1_same_aa_different_nt(self):
        criterion = PS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "TP53",
            "hgvs_p": "p.Arg175His",
            "hgvs_c": "c.524G>A",
            "clinvar_variants": [
                {
                    "hgvs_p": "p.Arg175His",
                    "hgvs_c": "c.524G>T",
                    "gene": "TP53",
                    "clinical_significance": "Pathogenic",
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_STRONG
        assert "same amino acid" in result.description.lower()
    
    def test_ps1_not_met_different_aa(self):
        criterion = PS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "TP53",
            "hgvs_p": "p.Arg175His",
            "hgvs_c": "c.524G>A",
            "clinvar_variants": [
                {
                    "hgvs_p": "p.Arg175Cys",
                    "gene": "TP53",
                    "clinical_significance": "Pathogenic",
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False
    
    def test_ps1_not_met_not_missense(self):
        criterion = PS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "AT",
            "consequence": "frameshift_variant",
            "gene": "TP53",
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestPS2:
    """Tests for PS2 criterion - Confirmed de novo variant."""
    
    def test_ps2_confirmed_de_novo(self):
        criterion = PS2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "de_novo": True,
            "gene": "DNMT3A",
        }
        context = {
            "inheritance": {
                "parentage_confirmed": True,
                "maternity_confirmed": True,
                "paternity_confirmed": True,
            },
            "family_history": {"affected_relatives": False},
            "phenotype_associated_genes": ["DNMT3A"],
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_STRONG
        assert result.confidence >= 0.9
    
    def test_ps2_not_met_no_parentage(self):
        criterion = PS2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "de_novo": True,
        }
        context = {
            "inheritance": {"parentage_confirmed": False},
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False
        assert "parentage" in result.description.lower()
    
    def test_ps2_not_met_family_history(self):
        criterion = PS2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "de_novo": True,
        }
        context = {
            "inheritance": {"parentage_confirmed": True},
            "family_history": {"affected_relatives": True},
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestPS3:
    """Tests for PS3 criterion - Functional studies."""
    
    def test_ps3_well_established_functional(self):
        criterion = PS3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "functional_studies": [
                {
                    "study_type": "in_vitro",
                    "result": "loss of function",
                    "quality_score": 5,
                    "validated": True,
                    "reproducible": True,
                    "peer_reviewed": True,
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_STRONG
    
    def test_ps3_multiple_studies(self):
        criterion = PS3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "functional_studies": [
                {
                    "study_type": "in_vitro",
                    "result": "damaging",
                    "quality_score": 4,
                    "validated": True,
                    "reproducible": True,
                    "peer_reviewed": True,
                },
                {
                    "study_type": "in_vivo",
                    "result": "pathogenic",
                    "quality_score": 4,
                    "validated": True,
                    "reproducible": True,
                    "peer_reviewed": True,
                },
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.confidence >= 0.9
    
    def test_ps3_not_met_no_studies(self):
        criterion = PS3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False
        assert "no functional studies" in result.description.lower()


class TestPS4:
    """Tests for PS4 criterion - Case-control studies."""
    
    def test_ps4_significant_case_control(self):
        criterion = PS4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "case_control_data": [
                {
                    "cases_with_variant": 50,
                    "cases_total": 500,
                    "controls_with_variant": 5,
                    "controls_total": 5000,
                    "or_threshold": 5.0,
                    "p_value": 0.001,
                    "ci_lower": 2.5,
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_STRONG
        assert result.metadata["odds_ratio"] >= 5.0
    
    def test_ps4_not_met_low_or(self):
        criterion = PS4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "case_control_data": [
                {
                    "cases_with_variant": 10,
                    "cases_total": 500,
                    "controls_with_variant": 50,
                    "controls_total": 5000,
                    "or_threshold": 5.0,
                    "p_value": 0.1,
                    "ci_lower": 0.5,
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestPM1:
    """Tests for PM1 criterion - Mutational hotspot/critical domain."""
    
    def test_pm1_in_hotspot(self):
        criterion = PM1()
        variant = {
            "chromosome": "chr17",
            "position": 7577559,
            "ref": "C",
            "alt": "T",
            "consequence": "missense_variant",
            "gene": "TP53",
            "hotspot": {
                "is_hotspot": True,
                "benign_count": 0,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_MODERATE
    
    def test_pm1_in_critical_domain(self):
        criterion = PM1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "BRCA1",
            "protein_domain": {
                "is_critical_domain": True,
                "name": "RING finger",
                "benign_count": 0,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert "critical domain" in result.description.lower()
    
    def test_pm1_not_met_benign_in_domain(self):
        criterion = PM1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "BRCA1",
            "protein_domain": {
                "is_critical_domain": True,
                "benign_count": 5,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestPM2:
    """Tests for PM2 criterion - Absent from population databases."""
    
    def test_pm2_absent_from_all(self):
        criterion = PM2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gnomad_af": 0.0,
            "af_1000g": 0.0,
            "exac_af": 0.0,
        }
        context = {"inheritance_mode": "dominant"}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_MODERATE
    
    def test_pm2_very_low_frequency_recessive(self):
        criterion = PM2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gnomad_af": 0.00005,
        }
        context = {"inheritance_mode": "recessive"}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
    
    def test_pm2_not_met_high_frequency(self):
        criterion = PM2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gnomad_af": 0.001,
        }
        context = {"inheritance_mode": "dominant"}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestPM3:
    """Tests for PM3 criterion - In trans with pathogenic variant."""
    
    def test_pm3_compound_het_confirmed(self):
        criterion = PM3()
        variant = {
            "chromosome": "chr7",
            "position": 117199646,
            "ref": "G",
            "alt": "A",
            "gene": "CFTR",
        }
        context = {
            "inheritance_mode": "recessive",
            "compound_heterozygous": {
                "other_variant": {
                    "chromosome": "chr7",
                    "position": 117199647,
                    "classification": "Pathogenic",
                },
                "phase_confirmed": True,
                "in_trans": True,
            },
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_MODERATE
    
    def test_pm3_not_met_no_other_variant(self):
        criterion = PM3()
        variant = {
            "chromosome": "chr7",
            "position": 117199646,
            "ref": "G",
            "alt": "A",
        }
        context = {
            "inheritance_mode": "recessive",
            "compound_heterozygous": {},
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False
    
    def test_pm3_not_met_in_cis(self):
        criterion = PM3()
        variant = {
            "chromosome": "chr7",
            "position": 117199646,
            "ref": "G",
            "alt": "A",
        }
        context = {
            "inheritance_mode": "recessive",
            "compound_heterozygous": {
                "other_variant": {"classification": "Pathogenic"},
                "phase_confirmed": True,
                "in_trans": False,
            },
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestPM4:
    """Tests for PM4 criterion - Protein length change."""
    
    def test_pm4_inframe_deletion(self):
        criterion = PM4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "AAA",
            "alt": "A",
            "consequence": "inframe_deletion",
            "repeat_region": {"in_repeat": False},
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_MODERATE
    
    def test_pm4_stop_loss(self):
        criterion = PM4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "T",
            "alt": "C",
            "consequence": "stop_lost",
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
    
    def test_pm4_not_met_in_repeat(self):
        criterion = PM4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "AAA",
            "alt": "A",
            "consequence": "inframe_deletion",
            "repeat_region": {"in_repeat": True},
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestPM5:
    """Tests for PM5 criterion - Different missense at same residue."""
    
    def test_pm5_different_missense_same_residue(self):
        criterion = PM5()
        variant = {
            "chromosome": "chr17",
            "position": 7577559,
            "ref": "C",
            "alt": "T",
            "consequence": "missense_variant",
            "gene": "TP53",
            "hgvs_p": "p.Arg175His",
            "residue_variants": [
                {
                    "position": "175",
                    "gene": "TP53",
                    "hgvs_p": "p.Arg175Cys",
                    "classification": "Pathogenic",
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_MODERATE
        assert "175" in result.description
    
    def test_pm5_not_met_no_pathogenic_at_residue(self):
        criterion = PM5()
        variant = {
            "chromosome": "chr17",
            "position": 7577559,
            "ref": "C",
            "alt": "T",
            "consequence": "missense_variant",
            "gene": "TP53",
            "hgvs_p": "p.Arg175His",
            "residue_variants": [],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestPM6:
    """Tests for PM6 criterion - Assumed de novo."""
    
    def test_pm6_assumed_de_novo(self):
        criterion = PM6()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "assumed_de_novo": True,
        }
        context = {
            "inheritance": {"parents_tested": True},
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_MODERATE
    
    def test_pm6_not_met_confirmed_de_novo(self):
        criterion = PM6()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "de_novo": True,
        }
        context = {
            "inheritance": {"parentage_confirmed": True},
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False
        assert "ps2" in result.description.lower()


class TestPP1:
    """Tests for PP1 criterion - Co-segregation."""
    
    def test_pp1_cosegregation(self):
        criterion = PP1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gene": "BRCA1",
        }
        context = {
            "segregation": {
                "affected_with_variant": 3,
                "affected_without_variant": 0,
                "meioses_count": 2,
            },
            "gene_definitive": True,
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_MODERATE
    
    def test_pp1_strong_segregation(self):
        criterion = PP1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        context = {
            "segregation": {
                "affected_with_variant": 5,
                "affected_without_variant": 0,
                "meioses_count": 4,
            },
            "gene_definitive": True,
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_STRONG
    
    def test_pp1_not_met_incomplete_segregation(self):
        criterion = PP1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        context = {
            "segregation": {
                "affected_with_variant": 2,
                "affected_without_variant": 1,
            },
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestPP2:
    """Tests for PP2 criterion - Low benign missense rate."""
    
    def test_pp2_constrained_gene(self):
        criterion = PP2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "TP53",
            "gene_info": {
                "missense_mechanism": True,
                "constraint": {"missense_z": 3.5, "oeo_ratio": 0.2},
                "benign_missense_rate": 0.05,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_SUPPORTING
    
    def test_pp2_not_met_high_benign_rate(self):
        criterion = PP2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "GENEX",
            "gene_info": {
                "missense_mechanism": True,
                "constraint": {"missense_z": 1.0, "oeo_ratio": 0.8},
                "benign_missense_rate": 0.5,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestPP3:
    """Tests for PP3 criterion - Computational evidence."""
    
    def test_pp3_concordant_deleterious(self):
        criterion = PP3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "predictions": {
                "sift": 0.01,
                "polyphen": 0.95,
                "cadd": 28.0,
                "revel": 0.7,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_SUPPORTING
        assert result.metadata["deleterious_count"] >= 3
    
    def test_pp3_not_met_conflicting_predictions(self):
        criterion = PP3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "predictions": {
                "sift": 0.8,
                "polyphen": 0.1,
                "cadd": 5.0,
                "revel": 0.2,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestPP4:
    """Tests for PP4 criterion - Specific phenotype."""
    
    def test_pp4_specific_phenotype(self):
        criterion = PP4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gene": "CFTR",
        }
        context = {
            "phenotype_match": {
                "specificity_score": 0.9,
                "gene_match_score": 0.95,
                "single_gene_match": True,
            },
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_SUPPORTING
    
    def test_pp4_not_met_multiple_genes(self):
        criterion = PP4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        context = {
            "phenotype_match": {
                "specificity_score": 0.5,
                "gene_match_score": 0.6,
                "candidate_genes": ["GENE1", "GENE2", "GENE3"],
            },
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestPP5:
    """Tests for PP5 criterion - Reputable source reports pathogenic."""
    
    def test_pp5_clinvar_pathogenic(self):
        criterion = PP5()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "external_classifications": [
                {
                    "source": "ClinVar",
                    "classification": "Pathogenic",
                    "review_status": "reviewed_by_expert",
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.PATHOGENIC_SUPPORTING
    
    def test_pp5_not_met_benign_report(self):
        criterion = PP5()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "external_classifications": [
                {
                    "source": "ClinVar",
                    "classification": "Benign",
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestBA1:
    """Tests for BA1 criterion - High allele frequency."""
    
    def test_ba1_high_frequency(self):
        criterion = BA1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gnomad_af": 0.08,
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_STANDALONE
        assert result.score < 0
    
    def test_ba1_not_met_low_frequency(self):
        criterion = BA1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gnomad_af": 0.01,
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestBS1:
    """Tests for BS1 criterion - Frequency greater than expected."""
    
    def test_bs1_frequency_exceeds_prevalence(self):
        criterion = BS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gnomad_af": 0.001,
        }
        context = {
            "disease_prevalence": 0.00001,
            "genetic_heterogeneity": 0.5,
            "penetrance": 1.0,
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_STRONG
    
    def test_bs1_not_met_frequency_ok(self):
        criterion = BS1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gnomad_af": 0.000001,
        }
        context = {
            "disease_prevalence": 0.001,
            "genetic_heterogeneity": 0.5,
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestBS2:
    """Tests for BS2 criterion - Healthy carriers."""
    
    def test_bs2_healthy_dominant_carrier(self):
        criterion = BS2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "healthy_carriers": [
                {"age": 65, "genotype": "heterozygous"},
            ],
        }
        context = {
            "inheritance_mode": "dominant",
            "typical_age_of_onset": "childhood",
            "penetrance": 1.0,
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_STRONG
    
    def test_bs2_not_met_carrier_too_young(self):
        criterion = BS2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "healthy_carriers": [
                {"age": 25, "genotype": "heterozygous"},
            ],
        }
        context = {
            "inheritance_mode": "dominant",
            "typical_age_of_onset": "childhood",
            "penetrance": 1.0,
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestBS3:
    """Tests for BS3 criterion - Functional studies benign."""
    
    def test_bs3_functional_benign(self):
        criterion = BS3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "functional_studies": [
                {
                    "result": "benign",
                    "quality_score": 5,
                    "validated": True,
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_STRONG
    
    def test_bs3_not_met_damaging_result(self):
        criterion = BS3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "functional_studies": [
                {"result": "damaging"},
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestBS4:
    """Tests for BS4 criterion - Lack of segregation."""
    
    def test_bs4_no_segregation(self):
        criterion = BS4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        context = {
            "segregation": {
                "affected_without_variant": 2,
                "affected_with_variant": 3,
            },
            "penetrance": 1.0,
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_STRONG
    
    def test_bs4_not_met_reduced_penetrance(self):
        criterion = BS4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        context = {
            "segregation": {
                "affected_without_variant": 1,
            },
            "penetrance": 0.3,
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestBP1:
    """Tests for BP1 criterion - Missense in LOF gene."""
    
    def test_bp1_missense_in_lof_gene(self):
        criterion = BP1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "DMD",
            "gene_info": {
                "lof_primary_mechanism": True,
                "pathogenic_missense_count": 1,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_SUPPORTING
    
    def test_bp1_not_met_mixed_mechanism(self):
        criterion = BP1()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "missense_variant",
            "gene": "TP53",
            "gene_info": {
                "lof_primary_mechanism": False,
                "pathogenic_missense_count": 10,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestBP2:
    """Tests for BP2 criterion - In cis/trans with pathogenic."""
    
    def test_bp2_in_cis_with_pathogenic(self):
        criterion = BP2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        context = {
            "phase_info": {
                "in_cis_with_pathogenic": True,
                "cis_variant": {"id": "chr1:100050"},
            },
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_SUPPORTING
    
    def test_bp2_not_met_no_phase_info(self):
        criterion = BP2()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        context = {"phase_info": {}}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestBP3:
    """Tests for BP3 criterion - In-frame indel in repeat."""
    
    def test_bp3_inframe_in_repeat(self):
        criterion = BP3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "AAA",
            "alt": "A",
            "consequence": "inframe_deletion",
            "repeat_region": {
                "in_repeat": True,
                "repeat_type": "tandem",
                "has_known_function": False,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_SUPPORTING
    
    def test_bp3_not_met_functional_repeat(self):
        criterion = BP3()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "AAA",
            "alt": "A",
            "consequence": "inframe_deletion",
            "repeat_region": {
                "in_repeat": True,
                "has_known_function": True,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestBP4:
    """Tests for BP4 criterion - Computational benign predictions."""
    
    def test_bp4_concordant_benign(self):
        criterion = BP4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "predictions": {
                "sift": 0.9,
                "polyphen": 0.05,
                "cadd": 8.0,
                "revel": 0.1,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_SUPPORTING
    
    def test_bp4_not_met_deleterious_predictions(self):
        criterion = BP4()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "predictions": {
                "sift": 0.01,
                "polyphen": 0.9,
                "cadd": 25.0,
            },
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False


class TestBP5:
    """Tests for BP5 criterion - Alternate molecular diagnosis."""
    
    def test_bp5_alternate_diagnosis(self):
        criterion = BP5()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "gene": "GENE1",
        }
        context = {
            "case_info": {
                "alternate_molecular_diagnosis": True,
                "primary_genetic_cause": {"gene": "GENE2"},
            },
        }
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_SUPPORTING
    
    def test_bp5_not_met_no_alternate(self):
        criterion = BP5()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
        }
        context = {"case_info": {}}
        
        result = criterion.evaluate(variant, context)
        
        assert result.is_met is False


class TestBP6:
    """Tests for BP6 criterion - Reputable source benign."""
    
    def test_bp6_clinvar_benign(self):
        criterion = BP6()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "external_classifications": [
                {
                    "source": "ClinVar",
                    "classification": "Benign",
                    "review_status": "reviewed_by_expert",
                }
            ],
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_SUPPORTING


class TestBP7:
    """Tests for BP7 criterion - Synonymous no splice impact."""
    
    def test_bp7_synonymous_no_splice_impact(self):
        criterion = BP7()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "synonymous_variant",
            "spliceai_score": 0.05,
            "maxent_diff": 0.5,
            "phylop": 1.0,
            "gerp": 0.5,
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is True
        assert result.evidence_strength == EvidenceStrength.BENIGN_SUPPORTING
    
    def test_bp7_not_met_splice_impact(self):
        criterion = BP7()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "synonymous_variant",
            "spliceai_score": 0.8,
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False
    
    def test_bp7_not_met_conserved(self):
        criterion = BP7()
        variant = {
            "chromosome": "chr1",
            "position": 100000,
            "ref": "A",
            "alt": "G",
            "consequence": "synonymous_variant",
            "spliceai_score": 0.1,
            "phylop": 5.0,
        }
        
        result = criterion.evaluate(variant)
        
        assert result.is_met is False
