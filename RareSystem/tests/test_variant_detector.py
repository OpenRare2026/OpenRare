"""
Tests for SNV/INDEL Variant Detector.
"""
import pytest
from pathlib import Path

from backend.services.variant_detector import (
    VariantDetector,
    DetectionConfig,
    DetectedVariant,
    detect_snv_indel,
    filter_by_quality,
    filter_by_type,
    get_snv_variants,
    get_indel_variants,
    VariantDetectionError
)


TEST_DATA_DIR = Path(__file__).parent / "data"
SAMPLE_VCF = TEST_DATA_DIR / "sample.vcf"
EMPTY_VCF = TEST_DATA_DIR / "empty.vcf"


class TestDetectionConfig:
    def test_default_config(self):
        config = DetectionConfig()
        assert config.qual_threshold == 30.0
        assert config.min_depth == 10
        assert config.max_depth == 10000
        assert config.filter_failed is True
        assert config.include_snv is True
        assert config.include_indel is True
    
    def test_custom_config(self):
        config = DetectionConfig(
            qual_threshold=50.0,
            min_depth=20,
            include_indel=False
        )
        assert config.qual_threshold == 50.0
        assert config.min_depth == 20
        assert config.include_indel is False


class TestDetectedVariant:
    def test_snv_detection(self):
        variant = DetectedVariant(
            chromosome="chr1",
            position=1000,
            variant_id="rs123",
            reference="A",
            alternate="G",
            variant_type="SNV",
            quality=50.0,
            filter_status="PASS",
            info={}
        )
        assert variant.variant_type == "SNV"
    
    def test_indel_detection(self):
        variant = DetectedVariant(
            chromosome="chr2",
            position=500,
            variant_id=".",
            reference="AG",
            alternate="AGCT",
            variant_type="INDEL",
            quality=60.0,
            filter_status="PASS",
            info={}
        )
        assert variant.variant_type == "INDEL"
    
    def test_to_vcf_line(self):
        variant = DetectedVariant(
            chromosome="chr1",
            position=1000,
            variant_id="rs123",
            reference="A",
            alternate="G",
            variant_type="SNV",
            quality=50.0,
            filter_status="PASS",
            info={"DP": 100, "AF": 0.5}
        )
        line = variant.to_vcf_line()
        assert "chr1" in line
        assert "1000" in line
        assert "rs123" in line
        assert "A" in line
        assert "G" in line
        assert "PASS" in line


class TestVariantDetector:
    def test_detect_snv_indel(self):
        detector = VariantDetector()
        variants = detector.detect(str(SAMPLE_VCF))
        
        assert len(variants) >= 1
        
        stats = detector.get_stats()
        assert stats["total_variants"] > 0
    
    def test_quality_filter(self):
        config = DetectionConfig(qual_threshold=50.0)
        detector = VariantDetector(config)
        variants = detector.detect(str(SAMPLE_VCF))
        
        for v in variants:
            assert v.quality >= 50.0
    
    def test_filter_failed_variants(self):
        config = DetectionConfig(filter_failed=True)
        detector = VariantDetector(config)
        variants = detector.detect(str(SAMPLE_VCF))
        
        for v in variants:
            assert v.filter_status == "PASS"
    
    def test_include_only_snv(self):
        config = DetectionConfig(include_snv=True, include_indel=False)
        detector = VariantDetector(config)
        variants = detector.detect(str(SAMPLE_VCF))
        
        for v in variants:
            assert v.variant_type == "SNV"
    
    def test_include_only_indel(self):
        config = DetectionConfig(include_snv=False, include_indel=True)
        detector = VariantDetector(config)
        variants = detector.detect(str(SAMPLE_VCF))
        
        for v in variants:
            assert v.variant_type == "INDEL"
    
    def test_detect_iter_generator(self):
        detector = VariantDetector()
        count = 0
        for variant in detector.detect_iter(str(SAMPLE_VCF)):
            count += 1
            assert isinstance(variant, DetectedVariant)
        
        assert count >= 1
    
    def test_stats_tracking(self):
        detector = VariantDetector()
        detector.detect(str(SAMPLE_VCF))
        
        stats = detector.get_stats()
        assert stats["total_variants"] > 0
        assert stats["pass_count"] > 0
        assert stats["snv_count"] + stats["indel_count"] == stats["pass_count"]
    
    def test_rs_id_extraction(self):
        detector = VariantDetector()
        variants = detector.detect(str(SAMPLE_VCF))
        
        rs_variants = [v for v in variants if v.rs_id]
        assert len(rs_variants) >= 1
    
    def test_depth_extraction(self):
        detector = VariantDetector()
        variants = detector.detect(str(SAMPLE_VCF))
        
        for v in variants:
            if v.depth:
                assert v.depth >= detector.config.min_depth
    
    def test_empty_vcf_handling(self):
        detector = VariantDetector()
        variants = detector.detect(str(EMPTY_VCF))
        
        assert len(variants) == 0
        stats = detector.get_stats()
        assert stats["total_variants"] == 0


class TestConvenienceFunctions:
    def test_detect_snv_indel_function(self):
        variants = detect_snv_indel(str(SAMPLE_VCF), qual_threshold=30.0)
        
        assert len(variants) >= 1
        for v in variants:
            assert v.quality >= 30.0
    
    def test_filter_by_quality(self):
        detector = VariantDetector()
        all_variants = detector.detect(str(SAMPLE_VCF))
        
        filtered = filter_by_quality(all_variants, min_qual=40.0)
        
        for v in filtered:
            assert v.quality >= 40.0
    
    def test_filter_by_type(self):
        detector = VariantDetector()
        all_variants = detector.detect(str(SAMPLE_VCF))
        
        snvs = filter_by_type(all_variants, ["SNV"])
        for v in snvs:
            assert v.variant_type == "SNV"
    
    def test_get_snv_variants(self):
        detector = VariantDetector()
        all_variants = detector.detect(str(SAMPLE_VCF))
        
        snvs = get_snv_variants(all_variants)
        for v in snvs:
            assert v.variant_type == "SNV"
    
    def test_get_indel_variants(self):
        detector = VariantDetector()
        all_variants = detector.detect(str(SAMPLE_VCF))
        
        indels = get_indel_variants(all_variants)
        for v in indels:
            assert v.variant_type == "INDEL"


class TestVCFOutput:
    def test_write_vcf(self, tmp_path):
        detector = VariantDetector()
        variants = detector.detect(str(SAMPLE_VCF))
        
        output_file = tmp_path / "output.vcf"
        detector.write_vcf(variants, str(output_file))
        
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "##fileformat=VCFv4.2" in content or "#CHROM" in content
    
    def test_write_vcf_with_custom_header(self, tmp_path):
        from backend.services.vcf_parser import VCFHeader
        
        detector = VariantDetector()
        variants = detector.detect(str(SAMPLE_VCF))
        
        header = VCFHeader(raw_header_lines=["##fileformat=VCFv4.2"])
        
        output_file = tmp_path / "output_header.vcf"
        detector.write_vcf(variants, str(output_file), header=header)
        
        assert output_file.exists()


class TestBatchProcessing:
    def test_detect_batch(self):
        detector = VariantDetector()
        
        vcf_paths = [str(SAMPLE_VCF)]
        results = detector.detect_batch(vcf_paths)
        
        assert str(SAMPLE_VCF) in results
        assert len(results[str(SAMPLE_VCF)]) >= 1
