"""
Tests for CNV detection module.
"""
import pytest
from pathlib import Path

from backend.services.cnv_detector import (
    CNVDetector,
    CNVType,
    CNVRegion,
    CNVDetectionError,
    detect_cnvs,
    create_cnv_report,
)


TEST_DATA_DIR = Path(__file__).parent / "data"


class TestCNVDetector:
    """Tests for CNVDetector class."""
    
    def test_init_default_params(self):
        """Test detector initialization with default parameters."""
        detector = CNVDetector()
        assert detector.window_size == CNVDetector.DEFAULT_WINDOW_SIZE
        assert detector.min_read_depth == CNVDetector.MIN_READ_DEPTH_FOR_DETECTION
        assert detector.deletion_threshold == CNVDetector.DELETION_CN_THRESHOLD
        assert detector.duplication_threshold == CNVDetector.DUPLICATION_CN_THRESHOLD
    
    def test_init_custom_params(self):
        """Test detector initialization with custom parameters."""
        detector = CNVDetector(
            window_size=500,
            min_read_depth=5,
            deletion_threshold=1.0,
            duplication_threshold=3.0,
            min_cnv_length=200
        )
        assert detector.window_size == 500
        assert detector.min_read_depth == 5
        assert detector.deletion_threshold == 1.0
        assert detector.duplication_threshold == 3.0
        assert detector.min_cnv_length == 200
    
    def test_detect_from_nonexistent_file(self):
        """Test detection raises error for non-existent file."""
        detector = CNVDetector()
        with pytest.raises(CNVDetectionError, match="VCF file not found"):
            detector.detect_from_vcf("/nonexistent/path/file.vcf")
    
    def test_cnv_type_enum(self):
        """Test CNVType enum values."""
        assert CNVType.DEL.value == "DEL"
        assert CNVType.DUP.value == "DUP"
        assert CNVType.CNV.value == "CNV"
    
    def test_cnv_region_properties(self):
        """Test CNVRegion properties."""
        region = CNVRegion(
            chromosome="chr1",
            start=1000,
            end=2000,
            cnv_type=CNVType.DEL,
            copy_number=1.0,
            confidence_score=0.8,
            read_depth=20.0,
            read_depth_ratio=0.5
        )
        assert region.length == 1001
        assert str(region) == "CNVRegion(chr1:1000-2000 DEL CN=1.0)"
    
    def test_detect_from_sample_vcf(self):
        """Test detection from sample VCF file."""
        vcf_path = TEST_DATA_DIR / "sample.vcf"
        if not vcf_path.exists():
            pytest.skip("Sample VCF not available")
        
        detector = CNVDetector(min_cnv_length=1)
        cnvs = detector.detect_from_vcf(str(vcf_path))
        
        assert isinstance(cnvs, list)
        for cnv in cnvs:
            assert isinstance(cnv, CNVRegion)
            assert cnv.cnv_type in [CNVType.DEL, CNVType.DUP]
    
    def test_detect_deletions_only(self):
        """Test deletion-only detection."""
        vcf_path = TEST_DATA_DIR / "sample.vcf"
        if not vcf_path.exists():
            pytest.skip("Sample VCF not available")
        
        detector = CNVDetector(min_cnv_length=1)
        deletions = detector.detect_deletions(str(vcf_path))
        
        assert isinstance(deletions, list)
        for cnv in deletions:
            assert cnv.cnv_type == CNVType.DEL
    
    def test_detect_duplications_only(self):
        """Test duplication-only detection."""
        vcf_path = TEST_DATA_DIR / "sample.vcf"
        if not vcf_path.exists():
            pytest.skip("Sample VCF not available")
        
        detector = CNVDetector(min_cnv_length=1)
        duplications = detector.detect_duplications(str(vcf_path))
        
        assert isinstance(duplications, list)
        for cnv in duplications:
            assert cnv.cnv_type == CNVType.DUP
    
    def test_estimate_copy_number(self):
        """Test copy number estimation for a region."""
        vcf_path = TEST_DATA_DIR / "sample.vcf"
        if not vcf_path.exists():
            pytest.skip("Sample VCF not available")
        
        detector = CNVDetector()
        cn = detector.estimate_copy_number(str(vcf_path), "chr1", 1000, 3000)
        
        assert isinstance(cn, float)
        assert cn >= 0
    
    def test_generate_cnv_report(self):
        """Test CNV report generation."""
        cnvs = [
            CNVRegion(
                chromosome="chr1",
                start=1000,
                end=2000,
                cnv_type=CNVType.DEL,
                copy_number=1.0,
                confidence_score=0.9,
                read_depth=20.0,
                read_depth_ratio=0.5
            ),
            CNVRegion(
                chromosome="chr2",
                start=5000,
                end=6000,
                cnv_type=CNVType.DUP,
                copy_number=3.0,
                confidence_score=0.7,
                read_depth=60.0,
                read_depth_ratio=1.5
            )
        ]
        
        detector = CNVDetector()
        report = detector.generate_cnv_report(cnvs)
        
        assert 'summary' in report
        assert 'cnvs' in report
        assert 'chromosome_distribution' in report
        
        assert report['summary']['total_cnvs'] == 2
        assert report['summary']['deletions'] == 1
        assert report['summary']['duplications'] == 1


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_detect_cnvs_function(self):
        """Test detect_cnvs convenience function."""
        vcf_path = TEST_DATA_DIR / "sample.vcf"
        if not vcf_path.exists():
            pytest.skip("Sample VCF not available")
        
        cnvs = detect_cnvs(str(vcf_path), window_size=100, min_cnv_length=1)
        assert isinstance(cnvs, list)
    
    def test_create_cnv_report_function(self):
        """Test create_cnv_report convenience function."""
        cnvs = [
            CNVRegion(
                chromosome="chr1",
                start=100,
                end=500,
                cnv_type=CNVType.DEL,
                copy_number=1.0,
                confidence_score=0.8,
                read_depth=15.0,
                read_depth_ratio=0.5
            )
        ]
        
        report = create_cnv_report(cnvs)
        assert 'summary' in report
        assert report['summary']['total_cnvs'] == 1


class TestCNVConfidenceScoring:
    """Tests for confidence score calculation."""
    
    def test_confidence_high_deviation(self):
        """Test confidence is higher for greater depth ratio deviation."""
        detector = CNVDetector()
        
        high_dev_score = detector._calculate_confidence(0.3, 30)
        low_dev_score = detector._calculate_confidence(0.9, 30)
        
        assert high_dev_score > low_dev_score
    
    def test_confidence_high_depth(self):
        """Test confidence is higher for higher read depth."""
        detector = CNVDetector()
        
        high_depth_score = detector._calculate_confidence(0.5, 100)
        low_depth_score = detector._calculate_confidence(0.5, 15)
        
        assert high_depth_score >= low_depth_score
    
    def test_confidence_bounds(self):
        """Test confidence score is bounded between 0 and 1."""
        detector = CNVDetector()
        
        for ratio in [0.1, 0.5, 1.0, 2.0, 5.0]:
            for depth in [10, 50, 100, 500]:
                score = detector._calculate_confidence(ratio, float(depth))
                assert 0 <= score <= 1


class TestCNVMerging:
    """Tests for adjacent CNV merging."""
    
    def test_merge_adjacent_same_type(self):
        """Test merging adjacent CNVs of the same type."""
        detector = CNVDetector()
        
        cnvs = [
            CNVRegion(
                chromosome="chr1",
                start=1000,
                end=1100,
                cnv_type=CNVType.DEL,
                copy_number=1.0,
                confidence_score=0.8,
                read_depth=20.0,
                read_depth_ratio=0.5
            ),
            CNVRegion(
                chromosome="chr1",
                start=1150,
                end=1250,
                cnv_type=CNVType.DEL,
                copy_number=1.0,
                confidence_score=0.7,
                read_depth=18.0,
                read_depth_ratio=0.45
            )
        ]
        
        merged = detector._merge_adjacent_cnvs(cnvs)
        
        assert len(merged) == 1
        assert merged[0].start == 1000
        assert merged[0].end == 1250
    
    def test_no_merge_different_types(self):
        """Test CNVs of different types are not merged."""
        detector = CNVDetector()
        
        cnvs = [
            CNVRegion(
                chromosome="chr1",
                start=1000,
                end=1100,
                cnv_type=CNVType.DEL,
                copy_number=1.0,
                confidence_score=0.8,
                read_depth=20.0,
                read_depth_ratio=0.5
            ),
            CNVRegion(
                chromosome="chr1",
                start=1150,
                end=1250,
                cnv_type=CNVType.DUP,
                copy_number=3.0,
                confidence_score=0.7,
                read_depth=60.0,
                read_depth_ratio=1.5
            )
        ]
        
        merged = detector._merge_adjacent_cnvs(cnvs)
        
        assert len(merged) == 2
    
    def test_no_merge_different_chromosomes(self):
        """Test CNVs on different chromosomes are not merged."""
        detector = CNVDetector()
        
        cnvs = [
            CNVRegion(
                chromosome="chr1",
                start=1000,
                end=1100,
                cnv_type=CNVType.DEL,
                copy_number=1.0,
                confidence_score=0.8,
                read_depth=20.0,
                read_depth_ratio=0.5
            ),
            CNVRegion(
                chromosome="chr2",
                start=1000,
                end=1100,
                cnv_type=CNVType.DEL,
                copy_number=1.0,
                confidence_score=0.8,
                read_depth=20.0,
                read_depth_ratio=0.5
            )
        ]
        
        merged = detector._merge_adjacent_cnvs(cnvs)
        
        assert len(merged) == 2
