"""
Tests for VEPCSVParser — raw pandas read with no preset field assumptions.
"""
import pytest
from services.vep_csv_parser import VEPCSVParser


@pytest.fixture
def parser():
    return VEPCSVParser()


VEP_DEFAULT_CSV = """## VEP output
#Uploaded_variation,Location,Allele,Gene,Feature,Consequence,HGVSc,HGVSp,Impact,SIFT,PolyPhen,CADD_PHRED,gnomADe_AF,CLIN_SIG
1_12345_A_G,1:12345,G,GENE1,ENST0001,missense_variant,c.123A>G,p.Lys41Arg,MODERATE,deleterious(0.01),probably_damaging(0.95),25.3,0.00001,Uncertain_significance
2_67890_C_T,2:67890,T,GENE2,ENST0002,stop_gained,c.678C>T,p.Tyr226*,HIGH,tolerated(0.5),benign(0.1),35.1,0.00005,Pathogenic
"""

VEP_MINIMAL_CSV = """Uploaded variation,Location,Consequence,Impact
1_12345_A_G,1:12345,missense_variant,MODERATE
"""

VEP_EMPTY_CSV = ""

VEP_TAB_DELIMITED_CSV = """Uploaded_variation\tLocation\tConsequence\tImpact
1_12345_A_G\t1:12345\tmissense_variant\tMODERATE
"""

VEP_EXTRA_COLUMNS_CSV = """#Uploaded variation,Location,Allele,Gene,Consequence,Impact,Custom_Field1,Custom_Field2
1_12345_A_G,1:12345,G,BRCA1,missense_variant,MODERATE,value1,value2
"""


class TestVEPCSVParser:
    def test_parse_default_format(self, parser):
        """Parse standard VEP CSV with common columns."""
        variants = parser.parse(VEP_DEFAULT_CSV)
        assert len(variants) == 2

        v1 = variants[0]
        # Raw column names from CSV header (stripped of leading #)
        assert v1["Uploaded_variation"] == "1_12345_A_G"
        assert v1["Location"] == "1:12345"
        assert v1["Allele"] == "G"
        assert v1["Gene"] == "GENE1"
        assert v1["Consequence"] == "missense_variant"
        assert v1["Impact"] == "MODERATE"
        assert v1["HGVSc"] == "c.123A>G"
        assert v1["HGVSp"] == "p.Lys41Arg"
        assert v1["SIFT"] == "deleterious(0.01)"
        assert v1["PolyPhen"] == "probably_damaging(0.95)"
        assert v1["CADD_PHRED"] == "25.3"
        assert v1["gnomADe_AF"] == "0.00001"
        assert v1["CLIN_SIG"] == "Uncertain_significance"

        v2 = variants[1]
        assert v2["Gene"] == "GENE2"
        assert v2["Impact"] == "HIGH"
        assert v2["CLIN_SIG"] == "Pathogenic"

    def test_parse_minimal_headers(self, parser):
        """Parse CSV with only minimal columns."""
        variants = parser.parse(VEP_MINIMAL_CSV)
        assert len(variants) == 1
        v = variants[0]
        assert v["Uploaded variation"] == "1_12345_A_G"
        assert v["Location"] == "1:12345"
        assert v["Consequence"] == "missense_variant"
        assert v["Impact"] == "MODERATE"

    def test_parse_empty_csv(self, parser):
        """Empty CSV returns empty list."""
        variants = parser.parse(VEP_EMPTY_CSV)
        assert variants == []

    def test_parse_whitespace_only(self, parser):
        """Whitespace-only content returns empty list."""
        variants = parser.parse("   \n  \n")
        assert variants == []

    def test_parse_tab_delimited(self, parser):
        """Tab-delimited CSV is correctly parsed."""
        variants = parser.parse(VEP_TAB_DELIMITED_CSV)
        assert len(variants) == 1
        v = variants[0]
        assert v["Uploaded_variation"] == "1_12345_A_G"
        assert v["Location"] == "1:12345"
        assert v["Consequence"] == "missense_variant"

    def test_parse_extra_columns_preserved(self, parser):
        """Extra/unknown columns are preserved as-is."""
        variants = parser.parse(VEP_EXTRA_COLUMNS_CSV)
        assert len(variants) == 1
        v = variants[0]
        # All columns should be present with original names
        assert "Custom_Field1" in v
        assert "Custom_Field2" in v
        assert v["Custom_Field1"] == "value1"
        assert v["Custom_Field2"] == "value2"

    def test_parse_returns_raw_dicts(self, parser):
        """Parser returns plain dicts, not typed objects."""
        variants = parser.parse(VEP_MINIMAL_CSV)
        assert len(variants) == 1
        v = variants[0]
        # Should be a plain dict
        assert isinstance(v, dict)
        # Values are strings (pandas dtype=str)
        assert all(isinstance(val, str) for val in v.values())

    def test_parse_comment_lines_stripped(self, parser):
        """VEP comment lines (##) are removed, header (#) line cleaned."""
        csv_with_comments = """##VEP version 108
##Colocate annotation
#Uploaded_variation,Location,Consequence
1_12345_A_G,1:12345,missense_variant
"""
        variants = parser.parse(csv_with_comments)
        assert len(variants) == 1
        assert "Uploaded_variation" in variants[0]

    def test_parse_no_header_only_comments(self, parser):
        """Only comment lines returns empty list."""
        csv_only_comments = """##VEP version 108
##Colocate annotation
"""
        variants = parser.parse(csv_only_comments)
        assert variants == []

    def test_parse_preserves_column_order(self, parser):
        """Column order from CSV header is preserved."""
        variants = parser.parse(VEP_DEFAULT_CSV)
        assert len(variants) == 2
        # Check first row has expected column order
        v1 = variants[0]
        expected_cols = [
            "Uploaded_variation",
            "Location",
            "Allele",
            "Gene",
            "Feature",
            "Consequence",
            "HGVSc",
            "HGVSp",
            "Impact",
            "SIFT",
            "PolyPhen",
            "CADD_PHRED",
            "gnomADe_AF",
            "CLIN_SIG",
        ]
        assert list(v1.keys()) == expected_cols
