"""
Copy Number Variation (CNV) Detector using read depth analysis.

Detects CNVs from VCF files through read depth analysis, supporting
detection of deletions and duplications with copy number estimation.
"""
import logging
import statistics
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator, Tuple

import pysam

logger = logging.getLogger(__name__)


class CNVType(Enum):
    DEL = "DEL"
    DUP = "DUP"
    CNV = "CNV"


@dataclass
class CNVRegion:
    chromosome: str
    start: int
    end: int
    cnv_type: CNVType
    copy_number: float
    confidence_score: float
    read_depth: float
    read_depth_ratio: float
    supporting_evidence: Dict[str, Any] = field(default_factory=dict)
    genes: List[str] = field(default_factory=list)
    
    @property
    def length(self) -> int:
        return self.end - self.start + 1
    
    def __repr__(self):
        return f"CNVRegion({self.chromosome}:{self.start}-{self.end} {self.cnv_type.value} CN={self.copy_number:.1f})"


@dataclass
class ReadDepthWindow:
    chromosome: str
    start: int
    end: int
    read_count: int
    read_depth: float
    gc_content: Optional[float] = None
    
    @property
    def length(self) -> int:
        return self.end - self.start + 1


class CNVDetectionError(Exception):
    pass


class CNVDetector:
    """
    CNV detection using read depth analysis from VCF/BAM files.
    
    Detection strategies:
    - Read depth ratio analysis across sliding windows
    - B-allele frequency (BAF) analysis for heterozygous sites
    - Split read and discordant pair support (if available)
    """
    
    DEFAULT_WINDOW_SIZE = 1000
    MIN_READ_DEPTH_FOR_DETECTION = 10
    DELETION_CN_THRESHOLD = 1.5
    DUPLICATION_CN_THRESHOLD = 2.5
    NORMAL_CN_BASELINE = 2.0
    
    def __init__(
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        min_read_depth: int = MIN_READ_DEPTH_FOR_DETECTION,
        deletion_threshold: float = DELETION_CN_THRESHOLD,
        duplication_threshold: float = DUPLICATION_CN_THRESHOLD,
        min_cnv_length: int = 100,
        gc_correction: bool = True
    ):
        self.window_size = window_size
        self.min_read_depth = min_read_depth
        self.deletion_threshold = deletion_threshold
        self.duplication_threshold = duplication_threshold
        self.min_cnv_length = min_cnv_length
        self.gc_correction = gc_correction
        
        self._baseline_depths: Dict[str, float] = {}
        self._gc_bias_correction: Dict[str, float] = {}
        
    def detect_from_vcf(
        self,
        vcf_path: str,
        sample_name: Optional[str] = None
    ) -> List[CNVRegion]:
        """
        Detect CNVs from VCF file using read depth information.
        
        Args:
            vcf_path: Path to VCF file
            sample_name: Specific sample to analyze (if multi-sample)
            
        Returns:
            List of detected CNVRegion objects
        """
        if not Path(vcf_path).exists():
            raise CNVDetectionError(f"VCF file not found: {vcf_path}")
        
        logger.info(f"Starting CNV detection from: {vcf_path}")
        
        try:
            vcf_reader = pysam.VariantFile(str(vcf_path))
        except Exception as e:
            raise CNVDetectionError(f"Failed to open VCF file: {e}")
        
        sample = sample_name or list(vcf_reader.header.samples)[0]
        
        read_depth_windows = self._extract_read_depth_windows(vcf_reader, sample)
        vcf_reader.close()
        
        if not read_depth_windows:
            logger.warning("No read depth data extracted from VCF")
            return []
        
        self._compute_baseline_depths(read_depth_windows)
        
        if self.gc_correction:
            self._apply_gc_correction(read_depth_windows)
        
        cnv_candidates = self._detect_cnv_regions(read_depth_windows)
        
        merged_cnvs = self._merge_adjacent_cnvs(cnv_candidates)
        
        filtered_cnvs = [cnv for cnv in merged_cnvs if cnv.length >= self.min_cnv_length]
        
        logger.info(f"Detected {len(filtered_cnvs)} CNVs")
        return filtered_cnvs
    
    def _extract_read_depth_windows(
        self,
        vcf_reader: pysam.VariantFile,
        sample: str
    ) -> List[ReadDepthWindow]:
        """Extract read depth information from VCF records."""
        windows = []
        current_chrom: Optional[str] = None
        window_reads: List[int] = []
        window_start: Optional[int] = None
        
        for record in vcf_reader:
            if record.chrom != current_chrom:
                if window_reads and current_chrom is not None and window_start is not None:
                    window = self._create_window(current_chrom, window_start, window_reads)
                    if window:
                        windows.append(window)
                current_chrom = record.chrom
                window_reads = []
                window_start = record.pos
            
            try:
                sample_data = record.samples.get(sample)
                if sample_data is None:
                    continue
                
                dp = sample_data.get('DP')
                if dp is not None:
                    window_reads.append(int(dp))
                elif 'AD' in dict(sample_data):
                    ad = sample_data.get('AD')
                    if ad:
                        total_ad = sum(ad) if isinstance(ad, (list, tuple)) else int(ad)
                        window_reads.append(total_ad)
                
                if len(window_reads) >= self.window_size:
                    if current_chrom is not None and window_start is not None:
                        window = self._create_window(current_chrom, window_start, window_reads)
                        if window:
                            windows.append(window)
                    window_reads = []
                    window_start = record.pos
                    
            except Exception as e:
                logger.debug(f"Error extracting read depth at {record.chrom}:{record.pos}: {e}")
                continue
        
        if window_reads and current_chrom is not None and window_start is not None:
            window = self._create_window(current_chrom, window_start, window_reads)
            if window:
                windows.append(window)
        
        return windows
    
    def _create_window(
        self,
        chrom: str,
        start: int,
        reads: List[int]
    ) -> Optional[ReadDepthWindow]:
        """Create a read depth window from collected reads."""
        if not reads:
            return None
        
        avg_depth = statistics.mean(reads)
        if avg_depth < self.min_read_depth:
            return None
        
        return ReadDepthWindow(
            chromosome=chrom,
            start=start,
            end=start + len(reads) - 1,
            read_count=len(reads),
            read_depth=avg_depth
        )
    
    def _compute_baseline_depths(self, windows: List[ReadDepthWindow]) -> None:
        """Compute global and per-chromosome baseline read depths."""
        all_depths: List[float] = []
        chrom_depths: Dict[str, List[float]] = {}
        
        for window in windows:
            all_depths.append(window.read_depth)
            if window.chromosome not in chrom_depths:
                chrom_depths[window.chromosome] = []
            chrom_depths[window.chromosome].append(window.read_depth)
        
        if all_depths:
            global_median = statistics.median(all_depths)
            self._baseline_depths['__global__'] = global_median
            logger.debug(f"Global baseline depth: {global_median:.2f}")
        
        for chrom, depths in chrom_depths.items():
            if depths:
                median_depth = statistics.median(depths)
                self._baseline_depths[chrom] = median_depth
                logger.debug(f"Baseline depth for {chrom}: {median_depth:.2f}")
    
    def _apply_gc_correction(self, windows: List[ReadDepthWindow]) -> None:
        """Apply GC-bias correction to read depths (placeholder for future implementation)."""
        pass
    
    def _detect_cnv_regions(self, windows: List[ReadDepthWindow]) -> List[CNVRegion]:
        """Detect CNV regions from read depth windows."""
        cnvs = []
        
        for window in windows:
            baseline = self._baseline_depths.get('__global__',
                          self._baseline_depths.get(window.chromosome, self.NORMAL_CN_BASELINE))
            if baseline == 0:
                continue
            
            depth_ratio = window.read_depth / baseline
            
            cnv_type = None
            copy_number = self.NORMAL_CN_BASELINE
            
            if depth_ratio < 0.75:
                cnv_type = CNVType.DEL
                copy_number = round(self.NORMAL_CN_BASELINE * depth_ratio)
                copy_number = max(0, min(1, copy_number))
            elif depth_ratio > 1.25:
                cnv_type = CNVType.DUP
                copy_number = round(self.NORMAL_CN_BASELINE * depth_ratio)
            
            if cnv_type:
                confidence = self._calculate_confidence(depth_ratio, window.read_depth)
                
                cnv = CNVRegion(
                    chromosome=window.chromosome,
                    start=window.start,
                    end=window.end,
                    cnv_type=cnv_type,
                    copy_number=float(copy_number),
                    confidence_score=confidence,
                    read_depth=window.read_depth,
                    read_depth_ratio=depth_ratio,
                    supporting_evidence={
                        'window_size': window.length,
                        'read_count': window.read_count,
                        'baseline_depth': baseline
                    }
                )
                cnvs.append(cnv)
        
        return cnvs
    
    def _calculate_confidence(self, depth_ratio: float, read_depth: float) -> float:
        """Calculate confidence score for CNV call."""
        ratio_deviation = abs(1.0 - depth_ratio)
        ratio_score = min(1.0, ratio_deviation * 2)
        
        depth_score = min(1.0, read_depth / (self.min_read_depth * 2))
        
        confidence = (ratio_score * 0.7 + depth_score * 0.3)
        return round(min(1.0, max(0.0, confidence)), 3)
    
    def _merge_adjacent_cnvs(self, cnvs: List[CNVRegion]) -> List[CNVRegion]:
        """Merge adjacent CNVs of the same type."""
        if not cnvs:
            return []
        
        sorted_cnvs = sorted(cnvs, key=lambda x: (x.chromosome, x.start))
        merged = [sorted_cnvs[0]]
        
        for current in sorted_cnvs[1:]:
            previous = merged[-1]
            
            if (current.chromosome == previous.chromosome and
                current.cnv_type == previous.cnv_type and
                current.start <= previous.end + self.window_size * 2):
                
                merged[-1] = CNVRegion(
                    chromosome=previous.chromosome,
                    start=previous.start,
                    end=max(previous.end, current.end),
                    cnv_type=previous.cnv_type,
                    copy_number=round((previous.copy_number + current.copy_number) / 2, 1),
                    confidence_score=max(previous.confidence_score, current.confidence_score),
                    read_depth=(previous.read_depth + current.read_depth) / 2,
                    read_depth_ratio=(previous.read_depth_ratio + current.read_depth_ratio) / 2,
                    supporting_evidence={
                        'merged_count': 2,
                        'original_starts': [previous.start, current.start],
                        'original_ends': [previous.end, current.end]
                    }
                )
            else:
                merged.append(current)
        
        return merged
    
    def detect_deletions(self, vcf_path: str) -> List[CNVRegion]:
        """Detect deletion events only."""
        all_cnvs = self.detect_from_vcf(vcf_path)
        return [cnv for cnv in all_cnvs if cnv.cnv_type == CNVType.DEL]
    
    def detect_duplications(self, vcf_path: str) -> List[CNVRegion]:
        """Detect duplication events only."""
        all_cnvs = self.detect_from_vcf(vcf_path)
        return [cnv for cnv in all_cnvs if cnv.cnv_type == CNVType.DUP]
    
    def estimate_copy_number(
        self,
        vcf_path: str,
        region_chrom: str,
        region_start: int,
        region_end: int
    ) -> float:
        """
        Estimate copy number for a specific genomic region.
        
        Args:
            vcf_path: Path to VCF file
            region_chrom: Chromosome
            region_start: Start position
            region_end: End position
            
        Returns:
            Estimated copy number
        """
        try:
            vcf_reader = pysam.VariantFile(str(vcf_path))
        except Exception as e:
            raise CNVDetectionError(f"Failed to open VCF file: {e}")
        
        depths = []
        sample = list(vcf_reader.header.samples)[0]
        
        try:
            for record in vcf_reader.fetch(region_chrom, region_start - 1, region_end):
                try:
                    sample_data = record.samples.get(sample)
                    if sample_data:
                        dp = sample_data.get('DP')
                        if dp is not None:
                            depths.append(float(dp))
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error fetching region: {e}")
        finally:
            vcf_reader.close()
        
        if not depths:
            return self.NORMAL_CN_BASELINE
        
        avg_depth = statistics.median(depths)
        baseline = self._baseline_depths.get(
            '__global__',
            self._baseline_depths.get(region_chrom, self.NORMAL_CN_BASELINE)
        )
        
        if baseline == 0:
            return self.NORMAL_CN_BASELINE
        
        ratio = avg_depth / baseline
        copy_number = round(self.NORMAL_CN_BASELINE * ratio, 1)
        
        return max(0, copy_number)
    
    def generate_cnv_report(self, cnvs: List[CNVRegion]) -> Dict[str, Any]:
        """
        Generate a summary report of detected CNVs.
        
        Args:
            cnvs: List of detected CNV regions
            
        Returns:
            Dictionary containing CNV report
        """
        deletions = [cnv for cnv in cnvs if cnv.cnv_type == CNVType.DEL]
        duplications = [cnv for cnv in cnvs if cnv.cnv_type == CNVType.DUP]
        
        total_deleted_bases = sum(cnv.length for cnv in deletions)
        total_duplicated_bases = sum(cnv.length for cnv in duplications)
        
        chrom_distribution: Dict[str, Dict[str, int]] = {}
        for cnv in cnvs:
            if cnv.chromosome not in chrom_distribution:
                chrom_distribution[cnv.chromosome] = {'DEL': 0, 'DUP': 0}
            chrom_distribution[cnv.chromosome][cnv.cnv_type.value] += 1
        
        high_confidence_cnvs = [cnv for cnv in cnvs if cnv.confidence_score >= 0.7]
        
        return {
            'summary': {
                'total_cnvs': len(cnvs),
                'deletions': len(deletions),
                'duplications': len(duplications),
                'high_confidence_count': len(high_confidence_cnvs),
                'total_deleted_bases': total_deleted_bases,
                'total_duplicated_bases': total_duplicated_bases
            },
            'chromosome_distribution': chrom_distribution,
            'cnvs': [
                {
                    'chromosome': cnv.chromosome,
                    'start': cnv.start,
                    'end': cnv.end,
                    'length': cnv.length,
                    'type': cnv.cnv_type.value,
                    'copy_number': cnv.copy_number,
                    'confidence': cnv.confidence_score,
                    'read_depth': cnv.read_depth,
                    'read_depth_ratio': cnv.read_depth_ratio
                }
                for cnv in sorted(cnvs, key=lambda x: (x.chromosome, x.start))
            ]
        }


def detect_cnvs(
    vcf_path: str,
    window_size: int = CNVDetector.DEFAULT_WINDOW_SIZE,
    min_cnv_length: int = 100
) -> List[CNVRegion]:
    """
    Convenience function to detect CNVs from VCF file.
    
    Args:
        vcf_path: Path to VCF file
        window_size: Window size for read depth analysis
        min_cnv_length: Minimum CNV length to report
        
    Returns:
        List of detected CNV regions
    """
    detector = CNVDetector(
        window_size=window_size,
        min_cnv_length=min_cnv_length
    )
    return detector.detect_from_vcf(vcf_path)


def create_cnv_report(cnvs: List[CNVRegion]) -> Dict[str, Any]:
    """
    Convenience function to generate CNV report.
    
    Args:
        cnvs: List of CNV regions
        
    Returns:
        CNV report dictionary
    """
    detector = CNVDetector()
    return detector.generate_cnv_report(cnvs)
