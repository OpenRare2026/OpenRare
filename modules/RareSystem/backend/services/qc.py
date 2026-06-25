"""
VCF Quality Control Pipeline.

Handles quality control checks for VCF files in the rare disease genetic
diagnosis system. Supports configurable thresholds for quality filtering.
"""
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from .vcf_parser import VCFParser, VCFVariant, VCFHeader, VCFParseError

logger = logging.getLogger(__name__)


class QCStatus(Enum):
    """Quality control status levels."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass
class QCParameters:
    """Configurable QC threshold parameters."""
    min_quality_score: float = 20.0
    min_depth: int = 10
    min_genotype_quality: int = 20
    min_call_rate: float = 0.95
    max_missing_rate: float = 0.05
    min_variant_quality_by_depth: float = 2.0
    min_allele_balance: float = 0.2
    max_allele_balance: float = 0.8
    require_pass_filter: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_quality_score": self.min_quality_score,
            "min_depth": self.min_depth,
            "min_genotype_quality": self.min_genotype_quality,
            "min_call_rate": self.min_call_rate,
            "max_missing_rate": self.max_missing_rate,
            "min_variant_quality_by_depth": self.min_variant_quality_by_depth,
            "min_allele_balance": self.min_allele_balance,
            "max_allele_balance": self.max_allele_balance,
            "require_pass_filter": self.require_pass_filter,
        }


@dataclass
class SampleQCStats:
    """QC statistics for a single sample."""
    sample_name: str
    total_variants: int = 0
    passed_variants: int = 0
    missing_genotypes: int = 0
    low_depth_variants: int = 0
    low_gq_variants: int = 0
    mean_depth: float = 0.0
    mean_quality: float = 0.0
    mean_genotype_quality: float = 0.0
    call_rate: float = 0.0
    heterozygous_count: int = 0
    homozygous_ref_count: int = 0
    homozygous_alt_count: int = 0
    _depth_sum: float = 0.0
    _gq_sum: float = 0.0
    _depth_count: int = 0
    _gq_count: int = 0
    
    def calculate_call_rate(self) -> None:
        if self.total_variants > 0:
            self.call_rate = 1.0 - (self.missing_genotypes / self.total_variants)
    
    def calculate_mean_depth(self) -> None:
        if self._depth_count > 0:
            self.mean_depth = self._depth_sum / self._depth_count
    
    def calculate_mean_gq(self) -> None:
        if self._gq_count > 0:
            self.mean_genotype_quality = self._gq_sum / self._gq_count
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_name": self.sample_name,
            "total_variants": self.total_variants,
            "passed_variants": self.passed_variants,
            "missing_genotypes": self.missing_genotypes,
            "low_depth_variants": self.low_depth_variants,
            "low_gq_variants": self.low_gq_variants,
            "mean_depth": self.mean_depth,
            "mean_quality": self.mean_quality,
            "mean_genotype_quality": self.mean_genotype_quality,
            "call_rate": self.call_rate,
            "heterozygous_count": self.heterozygous_count,
            "homozygous_ref_count": self.homozygous_ref_count,
            "homozygous_alt_count": self.homozygous_alt_count,
        }


@dataclass
class VariantQCStats:
    """QC statistics for variant-level metrics."""
    total_variants: int = 0
    passed_variants: int = 0
    failed_variants: int = 0
    low_quality_variants: int = 0
    low_depth_variants: int = 0
    filtered_variants: int = 0
    snv_count: int = 0
    indel_count: int = 0
    sv_count: int = 0
    mnv_count: int = 0
    pass_filter_count: int = 0
    fail_filter_count: int = 0
    mean_quality: float = 0.0
    mean_depth: float = 0.0
    quality_distribution: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_variants": self.total_variants,
            "passed_variants": self.passed_variants,
            "failed_variants": self.failed_variants,
            "low_quality_variants": self.low_quality_variants,
            "low_depth_variants": self.low_depth_variants,
            "filtered_variants": self.filtered_variants,
            "snv_count": self.snv_count,
            "indel_count": self.indel_count,
            "sv_count": self.sv_count,
            "mnv_count": self.mnv_count,
            "pass_filter_count": self.pass_filter_count,
            "fail_filter_count": self.fail_filter_count,
            "mean_quality": self.mean_quality,
            "mean_depth": self.mean_depth,
            "quality_distribution": self.quality_distribution,
        }


@dataclass
class QCReport:
    """Complete QC report with all statistics and recommendations."""
    file_path: str
    overall_status: QCStatus
    variant_stats: VariantQCStats
    sample_stats: Dict[str, SampleQCStats]
    parameters: QCParameters
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "overall_status": self.overall_status.value,
            "variant_stats": self.variant_stats.to_dict(),
            "sample_stats": {k: v.to_dict() for k, v in self.sample_stats.items()},
            "parameters": self.parameters.to_dict(),
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }
    
    def get_summary(self) -> str:
        lines = [
            "=" * 60,
            "VCF Quality Control Report",
            "=" * 60,
            f"File: {self.file_path}",
            f"Overall Status: {self.overall_status.value}",
            "",
            "Variant Statistics:",
            f"  Total variants: {self.variant_stats.total_variants}",
            f"  Passed variants: {self.variant_stats.passed_variants}",
            f"  Failed variants: {self.variant_stats.failed_variants}",
            f"  Mean quality: {self.variant_stats.mean_quality:.1f}",
            f"  Mean depth: {self.variant_stats.mean_depth:.1f}",
            "",
            "Variant Types:",
            f"  SNV: {self.variant_stats.snv_count}",
            f"  INDEL: {self.variant_stats.indel_count}",
            f"  SV: {self.variant_stats.sv_count}",
            f"  MNV: {self.variant_stats.mnv_count}",
            "",
        ]
        
        for sample_name, stats in self.sample_stats.items():
            lines.extend([
                f"Sample: {sample_name}",
                f"  Call rate: {stats.call_rate:.2%}",
                f"  Mean depth: {stats.mean_depth:.1f}",
                f"  Mean GQ: {stats.mean_genotype_quality:.1f}",
                f"  Heterozygous: {stats.heterozygous_count}",
                f"  Homozygous ALT: {stats.homozygous_alt_count}",
                "",
            ])
        
        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
            lines.append("")
        
        if self.recommendations:
            lines.append("Recommendations:")
            for r in self.recommendations:
                lines.append(f"  * {r}")
        
        return "\n".join(lines)


class VCFQualityChecker:
    """
    VCF Quality Control Pipeline.
    
    Performs comprehensive quality control checks on VCF files:
    - Variant quality score filtering
    - Sample call rate calculation
    - Depth of coverage validation
    - Genotype quality assessment
    - Filter status verification
    
    Usage:
        checker = VCFQualityChecker(params)
        report = checker.run_qc("sample.vcf")
        passed_variants = checker.filter_variants("sample.vcf")
    """
    
    def __init__(self, params: Optional[QCParameters] = None):
        self.params = params or QCParameters()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def run_qc(self, vcf_path: str) -> QCReport:
        """
        Run complete QC pipeline on VCF file.
        
        Args:
            vcf_path: Path to VCF file
            
        Returns:
            QCReport with all QC statistics
        """
        self.logger.info(f"Starting QC for: {vcf_path}")
        
        parser = VCFParser(vcf_path)
        
        try:
            parser.open()
            header = parser.parse_header()
            
            variant_stats = VariantQCStats()
            sample_stats = self._init_sample_stats(header)
            
            quality_sum = 0.0
            depth_sum = 0.0
            quality_scores = []
            
            for variant in parser.iter_variants():
                self._update_variant_stats(variant, variant_stats, quality_scores)
                self._update_sample_stats(variant, sample_stats, header)
                
                if variant.quality is not None:
                    quality_sum += variant.quality
                    quality_scores.append(variant.quality)
                
                dp = variant.info.get("DP")
                if dp is not None:
                    depth_sum += float(dp)
            
            self._finalize_stats(variant_stats, sample_stats, quality_sum, depth_sum)
            self._calculate_quality_distribution(variant_stats, quality_scores)
            
            warnings, recommendations = self._generate_warnings_and_recommendations(
                variant_stats, sample_stats
            )
            
            overall_status = self._determine_overall_status(
                variant_stats, sample_stats, warnings
            )
            
            report = QCReport(
                file_path=vcf_path,
                overall_status=overall_status,
                variant_stats=variant_stats,
                sample_stats=sample_stats,
                parameters=self.params,
                warnings=warnings,
                recommendations=recommendations,
            )
            
            self.logger.info(f"QC completed. Status: {overall_status.value}")
            return report
            
        finally:
            parser.close()
    
    def _init_sample_stats(self, header: VCFHeader) -> Dict[str, SampleQCStats]:
        stats = {}
        for sample in header.samples:
            stats[sample] = SampleQCStats(sample_name=sample)
        return stats
    
    def _update_variant_stats(
        self,
        variant: VCFVariant,
        stats: VariantQCStats,
        quality_scores: List[float],
    ) -> None:
        stats.total_variants += 1
        
        if variant.variant_type == "SNV":
            stats.snv_count += 1
        elif variant.variant_type == "INDEL":
            stats.indel_count += 1
        elif variant.variant_type == "SV":
            stats.sv_count += 1
        elif variant.variant_type == "MNV":
            stats.mnv_count += 1
        
        if variant.filter_status == "PASS":
            stats.pass_filter_count += 1
        else:
            stats.fail_filter_count += 1
        
        if variant.quality is not None:
            if variant.quality < self.params.min_quality_score:
                stats.low_quality_variants += 1
        
        dp = variant.info.get("DP")
        if dp is not None and float(dp) < self.params.min_depth:
            stats.low_depth_variants += 1
    
    def _update_sample_stats(
        self,
        variant: VCFVariant,
        sample_stats: Dict[str, SampleQCStats],
        header: VCFHeader,
    ) -> None:
        if not variant.genotype:
            return
        
        for sample_name in header.samples:
            stats = sample_stats[sample_name]
            stats.total_variants += 1
            
            gt_key = f"{sample_name}_GT"
            gt = variant.genotype.get(gt_key, "")
            
            if gt in ("./.", ".|.", "."):
                stats.missing_genotypes += 1
            elif "/" in gt:
                alleles = gt.split("/")
                if alleles[0] == alleles[1]:
                    if alleles[0] == "0":
                        stats.homozygous_ref_count += 1
                    else:
                        stats.homozygous_alt_count += 1
                else:
                    stats.heterozygous_count += 1
            elif "|" in gt:
                alleles = gt.split("|")
                if alleles[0] == alleles[1]:
                    if alleles[0] == "0":
                        stats.homozygous_ref_count += 1
                    else:
                        stats.homozygous_alt_count += 1
                else:
                    stats.heterozygous_count += 1
            
            dp_key = f"{sample_name}_DP"
            dp = variant.genotype.get(dp_key)
            if dp is not None:
                dp_val = float(dp)
                stats._depth_sum += dp_val
                stats._depth_count += 1
                if int(dp) < self.params.min_depth:
                    stats.low_depth_variants += 1
            
            gq_key = f"{sample_name}_GQ"
            gq = variant.genotype.get(gq_key)
            if gq is not None:
                gq_val = float(gq)
                stats._gq_sum += gq_val
                stats._gq_count += 1
                if int(gq) < self.params.min_genotype_quality:
                    stats.low_gq_variants += 1
    
    def _finalize_stats(
        self,
        variant_stats: VariantQCStats,
        sample_stats: Dict[str, SampleQCStats],
        quality_sum: float,
        depth_sum: float,
    ) -> None:
        if variant_stats.total_variants > 0:
            variant_stats.mean_quality = quality_sum / variant_stats.total_variants
            variant_stats.mean_depth = depth_sum / variant_stats.total_variants
        
        variant_stats.passed_variants = (
            variant_stats.total_variants - 
            variant_stats.low_quality_variants - 
            variant_stats.low_depth_variants -
            variant_stats.fail_filter_count
        )
        variant_stats.failed_variants = variant_stats.total_variants - variant_stats.passed_variants
        variant_stats.filtered_variants = variant_stats.failed_variants
        
        for stats in sample_stats.values():
            stats.calculate_call_rate()
            stats.calculate_mean_depth()
            stats.calculate_mean_gq()
    
    def _calculate_quality_distribution(
        self,
        stats: VariantQCStats,
        quality_scores: List[float],
    ) -> None:
        if not quality_scores:
            return
        
        bins = {
            "0-10": 0,
            "10-20": 0,
            "20-30": 0,
            "30-50": 0,
            "50-100": 0,
            "100+": 0,
        }
        
        for q in quality_scores:
            if q < 10:
                bins["0-10"] += 1
            elif q < 20:
                bins["10-20"] += 1
            elif q < 30:
                bins["20-30"] += 1
            elif q < 50:
                bins["30-50"] += 1
            elif q < 100:
                bins["50-100"] += 1
            else:
                bins["100+"] += 1
        
        stats.quality_distribution = bins
    
    def _generate_warnings_and_recommendations(
        self,
        variant_stats: VariantQCStats,
        sample_stats: Dict[str, SampleQCStats],
    ) -> Tuple[List[str], List[str]]:
        warnings = []
        recommendations = []
        
        if variant_stats.total_variants == 0:
            warnings.append("No variants found in VCF file")
            recommendations.append("Verify VCF file contains variant data")
            return warnings, recommendations
        
        low_quality_rate = variant_stats.low_quality_variants / variant_stats.total_variants
        if low_quality_rate > 0.1:
            warnings.append(f"High rate of low quality variants: {low_quality_rate:.1%}")
            recommendations.append(
                f"Consider adjusting quality threshold (current: {self.params.min_quality_score})"
            )
        
        low_depth_rate = variant_stats.low_depth_variants / variant_stats.total_variants
        if low_depth_rate > 0.05:
            warnings.append(f"High rate of low depth variants: {low_depth_rate:.1%}")
            recommendations.append(
                f"Consider adjusting depth threshold (current: {self.params.min_depth})"
            )
        
        for sample_name, stats in sample_stats.items():
            if stats.call_rate < self.params.min_call_rate:
                warnings.append(
                    f"Sample {sample_name} has low call rate: {stats.call_rate:.1%}"
                )
                recommendations.append(
                    f"Review sample {sample_name} for potential quality issues"
                )
            
            if stats.mean_depth < self.params.min_depth:
                warnings.append(
                    f"Sample {sample_name} has low mean depth: {stats.mean_depth:.1f}"
                )
                recommendations.append(
                    f"Consider additional sequencing for sample {sample_name}"
                )
        
        return warnings, recommendations
    
    def _determine_overall_status(
        self,
        variant_stats: VariantQCStats,
        sample_stats: Dict[str, SampleQCStats],
        warnings: List[str],
    ) -> QCStatus:
        if variant_stats.total_variants == 0:
            return QCStatus.FAIL
        
        for stats in sample_stats.values():
            if stats.call_rate < self.params.min_call_rate * 0.9:
                return QCStatus.FAIL
        
        critical_warnings = sum(
            1 for w in warnings 
            if "No variants" in w or "low call rate" in w
        )
        
        if critical_warnings > 0:
            return QCStatus.FAIL
        
        if len(warnings) > 0:
            return QCStatus.WARNING
        
        return QCStatus.PASS
    
    def filter_variants(
        self,
        vcf_path: str,
        output_path: Optional[str] = None,
    ) -> Generator[VCFVariant, None, None]:
        """
        Filter variants based on QC thresholds.
        
        Args:
            vcf_path: Path to input VCF file
            output_path: Optional path for filtered output
            
        Yields:
            VCFVariant objects passing QC filters
        """
        self.logger.info(f"Filtering variants from: {vcf_path}")
        
        parser = VCFParser(vcf_path)
        passed_count = 0
        failed_count = 0
        
        try:
            parser.open()
            header = parser.parse_header()
            
            for variant in parser.iter_variants():
                if self._variant_passes_qc(variant):
                    passed_count += 1
                    yield variant
                else:
                    failed_count += 1
            
            self.logger.info(
                f"Filtering complete. Passed: {passed_count}, Failed: {failed_count}"
            )
            
        finally:
            parser.close()
    
    def _variant_passes_qc(self, variant: VCFVariant) -> bool:
        if self.params.require_pass_filter and variant.filter_status != "PASS":
            return False
        
        if variant.quality is not None and variant.quality < self.params.min_quality_score:
            return False
        
        dp = variant.info.get("DP")
        if dp is not None and float(dp) < self.params.min_depth:
            return False
        
        if variant.genotype:
            for key, value in variant.genotype.items():
                if key.endswith("_GQ") and value is not None:
                    if int(value) < self.params.min_genotype_quality:
                        return False
        
        return True
    
    def get_filtered_variants(self, vcf_path: str) -> List[VCFVariant]:
        """
        Get all variants passing QC as a list.
        
        Args:
            vcf_path: Path to VCF file
            
        Returns:
            List of VCFVariant objects passing QC
        """
        return list(self.filter_variants(vcf_path))
    
    def validate_vcf_integrity(self, vcf_path: str) -> Tuple[bool, List[str]]:
        """
        Validate VCF file integrity.
        
        Args:
            vcf_path: Path to VCF file
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            parser = VCFParser(vcf_path)
            parser.open()
            header = parser.parse_header()
            
            if not header.samples:
                errors.append("No samples found in VCF file")
            
            if not header.contigs:
                errors.append("No contigs defined in VCF header")
            
            variant_count = 0
            prev_pos = 0
            prev_chrom = ""
            
            for variant in parser.iter_variants():
                variant_count += 1
                
                if variant.position <= 0:
                    errors.append(
                        f"Invalid position at {variant.chromosome}:{variant.position}"
                    )
                
                if not variant.reference:
                    errors.append(
                        f"Missing reference at {variant.chromosome}:{variant.position}"
                    )
                
                if not variant.alternate or variant.alternate == ".":
                    continue
                
                if (variant.chromosome == prev_chrom and 
                    variant.position < prev_pos):
                    errors.append(
                        f"Variants not sorted at {variant.chromosome}:{variant.position}"
                    )
                
                prev_chrom = variant.chromosome
                prev_pos = variant.position
            
            if variant_count == 0:
                errors.append("No variants found in VCF file")
            
            parser.close()
            
            is_valid = len(errors) == 0
            self.logger.info(
                f"VCF validation {'passed' if is_valid else 'failed'}: {vcf_path}"
            )
            return is_valid, errors
            
        except VCFParseError as e:
            errors.append(f"Parse error: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            return False, errors


def run_qc_pipeline(
    vcf_path: str,
    params: Optional[QCParameters] = None,
) -> QCReport:
    """
    Convenience function to run QC pipeline.
    
    Args:
        vcf_path: Path to VCF file
        params: Optional QC parameters
        
    Returns:
        QCReport with results
    """
    checker = VCFQualityChecker(params)
    return checker.run_qc(vcf_path)


def filter_vcf(
    vcf_path: str,
    params: Optional[QCParameters] = None,
) -> List[VCFVariant]:
    """
    Convenience function to filter VCF variants.
    
    Args:
        vcf_path: Path to VCF file
        params: Optional QC parameters
        
    Returns:
        List of variants passing QC
    """
    checker = VCFQualityChecker(params)
    return checker.get_filtered_variants(vcf_path)
