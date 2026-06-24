"""
SNV/INDEL Variant Detector for Rare Disease Genetic Diagnosis System.

Detects single nucleotide variants (SNVs) and insertions/deletions (INDELs)
from VCF files with quality filtering and annotation support.
"""
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Iterator
from dataclasses import dataclass, field
from datetime import datetime

from .vcf_parser import VCFParser, VCFVariant, VCFHeader, VCFParseError

logger = logging.getLogger(__name__)

DEFAULT_QUAL_THRESHOLD = 30.0
DEFAULT_MIN_DEPTH = 10
DEFAULT_MAX_DEPTH = 10000


@dataclass
class DetectionConfig:
    """Configuration for variant detection."""
    qual_threshold: float = DEFAULT_QUAL_THRESHOLD
    min_depth: int = DEFAULT_MIN_DEPTH
    max_depth: int = DEFAULT_MAX_DEPTH
    filter_failed: bool = True
    include_snv: bool = True
    include_indel: bool = True
    min_allele_frequency: Optional[float] = None
    max_allele_frequency: Optional[float] = None


@dataclass
class DetectedVariant:
    """Represents a detected variant with annotation data."""
    chromosome: str
    position: int
    variant_id: str
    reference: str
    alternate: str
    variant_type: str
    quality: float
    filter_status: str
    info: Dict[str, Any]
    depth: Optional[int] = None
    allele_frequency: Optional[float] = None
    rs_id: Optional[str] = None
    gene: Optional[str] = None
    consequence: Optional[str] = None
    genotype: Optional[Dict[str, Any]] = None
    
    def to_vcf_line(self) -> str:
        """Convert variant to VCF format line."""
        info_parts = []
        for key, value in self.info.items():
            if value is True:
                info_parts.append(key)
            elif value is not None and value is not False:
                info_parts.append(f"{key}={value}")
        
        info_str = ";".join(info_parts) if info_parts else "."
        variant_id = self.rs_id if self.rs_id else self.variant_id
        
        return f"{self.chromosome}\t{self.position}\t{variant_id}\t{self.reference}\t{self.alternate}\t{self.quality:.2f}\t{self.filter_status}\t{info_str}"
    
    def __repr__(self):
        return f"DetectedVariant({self.chromosome}:{self.position} {self.reference}>{self.alternate} [{self.variant_type}])"


class VariantDetectionError(Exception):
    """Raised when variant detection fails."""
    pass


class VariantDetector:
    """
    SNV/INDEL variant detector.
    
    Features:
    - SNV detection (single nucleotide variants)
    - INDEL detection (insertions and deletions)
    - Quality-based filtering (QUAL threshold)
    - Depth-based filtering
    - Allele frequency filtering
    - VCF output generation
    - Batch processing support
    - Integration with VCFParser
    """
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        """
        Initialize variant detector.
        
        Args:
            config: Detection configuration (uses defaults if None)
        """
        self.config = config or DetectionConfig()
        self._stats = {
            "total_variants": 0,
            "snv_count": 0,
            "indel_count": 0,
            "filtered_count": 0,
            "pass_count": 0
        }
    
    def detect(self, vcf_path: str) -> List[DetectedVariant]:
        """
        Detect SNV/INDEL variants from VCF file.
        
        Args:
            vcf_path: Path to input VCF file
            
        Returns:
            List of DetectedVariant objects passing filters
        """
        self._reset_stats()
        
        variants = []
        
        try:
            with VCFParser(vcf_path) as parser:
                parser.parse_header()
                
                for vcf_variant in parser.iter_variants():
                    self._stats["total_variants"] += 1
                    
                    detected = self._process_variant(vcf_variant)
                    if detected:
                        variants.append(detected)
                        
        except VCFParseError as e:
            raise VariantDetectionError(f"Failed to parse VCF file: {e}")
        
        logger.info(f"Detection complete: {len(variants)} variants passed filters "
                   f"(SNV: {self._stats['snv_count']}, INDEL: {self._stats['indel_count']})")
        
        return variants
    
    def detect_iter(self, vcf_path: str) -> Iterator[DetectedVariant]:
        """
        Detect variants using generator pattern for memory efficiency.
        
        Args:
            vcf_path: Path to input VCF file
            
        Yields:
            DetectedVariant objects passing filters
        """
        self._reset_stats()
        
        try:
            with VCFParser(vcf_path) as parser:
                parser.parse_header()
                
                for vcf_variant in parser.iter_variants():
                    self._stats["total_variants"] += 1
                    
                    detected = self._process_variant(vcf_variant)
                    if detected:
                        yield detected
                        
        except VCFParseError as e:
            raise VariantDetectionError(f"Failed to parse VCF file: {e}")
    
    def detect_batch(self, vcf_paths: List[str]) -> Dict[str, List[DetectedVariant]]:
        """
        Detect variants from multiple VCF files.
        
        Args:
            vcf_paths: List of VCF file paths
            
        Returns:
            Dictionary mapping file paths to detected variants
        """
        results = {}
        
        for vcf_path in vcf_paths:
            try:
                logger.info(f"Processing batch file: {vcf_path}")
                variants = self.detect(vcf_path)
                results[vcf_path] = variants
            except VariantDetectionError as e:
                logger.error(f"Failed to process {vcf_path}: {e}")
                results[vcf_path] = []
        
        return results
    
    def _process_variant(self, vcf_variant: VCFVariant) -> Optional[DetectedVariant]:
        """
        Process a single VCF variant and apply filters.
        
        Args:
            vcf_variant: Parsed VCF variant
            
        Returns:
            DetectedVariant if passes filters, None otherwise
        """
        variant_type = vcf_variant.variant_type
        
        if variant_type == "SNV" and not self.config.include_snv:
            return None
        if variant_type == "INDEL" and not self.config.include_indel:
            return None
        if variant_type not in ("SNV", "INDEL"):
            return None
        
        if not self._passes_quality_filter(vcf_variant):
            self._stats["filtered_count"] += 1
            return None
        
        if not self._passes_depth_filter(vcf_variant):
            self._stats["filtered_count"] += 1
            return None
        
        if not self._passes_frequency_filter(vcf_variant):
            self._stats["filtered_count"] += 1
            return None
        
        if self.config.filter_failed and vcf_variant.filter_status != "PASS":
            self._stats["filtered_count"] += 1
            return None
        
        detected = DetectedVariant(
            chromosome=vcf_variant.chromosome,
            position=vcf_variant.position,
            variant_id=vcf_variant.variant_id,
            reference=vcf_variant.reference,
            alternate=vcf_variant.alternate,
            variant_type=variant_type,
            quality=vcf_variant.quality if vcf_variant.quality else 0.0,
            filter_status=vcf_variant.filter_status,
            info=vcf_variant.info,
            genotype=vcf_variant.genotype,
            rs_id=self._extract_rs_id(vcf_variant),
            depth=self._extract_depth(vcf_variant),
            allele_frequency=self._extract_allele_frequency(vcf_variant)
        )
        
        self._update_stats(variant_type)
        
        return detected
    
    def _passes_quality_filter(self, variant: VCFVariant) -> bool:
        """Check if variant passes quality threshold."""
        if variant.quality is None:
            return True
        return variant.quality >= self.config.qual_threshold
    
    def _passes_depth_filter(self, variant: VCFVariant) -> bool:
        """Check if variant passes depth filters."""
        depth = self._extract_depth(variant)
        if depth is None:
            return True
        return self.config.min_depth <= depth <= self.config.max_depth
    
    def _passes_frequency_filter(self, variant: VCFVariant) -> bool:
        """Check if variant passes allele frequency filters."""
        af = self._extract_allele_frequency(variant)
        if af is None:
            return True
        
        if self.config.min_allele_frequency is not None:
            if af < self.config.min_allele_frequency:
                return False
        
        if self.config.max_allele_frequency is not None:
            if af > self.config.max_allele_frequency:
                return False
        
        return True
    
    def _extract_depth(self, variant: VCFVariant) -> Optional[int]:
        """Extract read depth from variant info or genotype."""
        if "DP" in variant.info:
            dp = variant.info["DP"]
            if isinstance(dp, (list, tuple)):
                return int(dp[0]) if dp else None
            return int(dp)
        
        if variant.genotype:
            for key, value in variant.genotype.items():
                if key.endswith("_DP"):
                    if isinstance(value, (list, tuple)):
                        return int(value[0]) if value else None
                    return int(value) if value else None
        
        return None
    
    def _extract_allele_frequency(self, variant: VCFVariant) -> Optional[float]:
        """Extract allele frequency from variant info."""
        for key in ["AF", "VAF", "MAF"]:
            if key in variant.info:
                af = variant.info[key]
                if isinstance(af, (list, tuple)):
                    return float(af[0]) if af else None
                return float(af)
        return None
    
    def _extract_rs_id(self, variant: VCFVariant) -> Optional[str]:
        """Extract dbSNP rs ID from variant."""
        if variant.variant_id and variant.variant_id.startswith("rs"):
            return variant.variant_id
        
        if "RSID" in variant.info:
            rsid = variant.info["RSID"]
            if isinstance(rsid, (list, tuple)):
                return str(rsid[0]) if rsid else None
            return str(rsid)
        
        return None
    
    def _reset_stats(self) -> None:
        """Reset detection statistics."""
        self._stats = {
            "total_variants": 0,
            "snv_count": 0,
            "indel_count": 0,
            "filtered_count": 0,
            "pass_count": 0
        }
    
    def _update_stats(self, variant_type: str) -> None:
        """Update statistics for passed variant."""
        self._stats["pass_count"] += 1
        if variant_type == "SNV":
            self._stats["snv_count"] += 1
        elif variant_type == "INDEL":
            self._stats["indel_count"] += 1
    
    def get_stats(self) -> Dict[str, int]:
        """Get detection statistics."""
        return self._stats.copy()
    
    def write_vcf(self, variants: List[DetectedVariant], output_path: str,
                  header: Optional[VCFHeader] = None) -> None:
        """
        Write detected variants to VCF file.
        
        Args:
            variants: List of detected variants
            output_path: Output file path
            header: Optional VCF header (creates default if None)
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w') as f:
            if header:
                for line in header.raw_header_lines:
                    f.write(line + '\n')
            else:
                f.write(self._generate_default_header())
            
            for variant in variants:
                f.write(variant.to_vcf_line() + '\n')
        
        logger.info(f"Wrote {len(variants)} variants to {output_path}")
    
    def _generate_default_header(self) -> str:
        """Generate default VCF header."""
        header_lines = [
            "##fileformat=VCFv4.2",
            f"##fileDate={datetime.now().strftime('%Y%m%d')}",
            "##source=RareDiseaseGeneticDiagnosis_VariantDetector_v1.0",
            '##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">',
            '##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">',
            '##FILTER=<ID=PASS,Description="All filters passed">',
            '##FILTER=<ID=LowQual,Description="Quality below threshold">',
            '##FILTER=<ID=LowDepth,Description="Read depth below minimum">',
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
        ]
        return '\n'.join(header_lines) + '\n'


def detect_snv_indel(vcf_path: str,
                     qual_threshold: float = DEFAULT_QUAL_THRESHOLD,
                     output_path: Optional[str] = None) -> List[DetectedVariant]:
    """
    Convenience function to detect SNV/INDEL variants.
    
    Args:
        vcf_path: Path to input VCF file
        qual_threshold: Minimum quality score threshold
        output_path: Optional output VCF path
        
    Returns:
        List of detected variants
    """
    config = DetectionConfig(qual_threshold=qual_threshold)
    detector = VariantDetector(config)
    variants = detector.detect(vcf_path)
    
    if output_path:
        detector.write_vcf(variants, output_path)
    
    return variants


def filter_by_quality(variants: List[DetectedVariant],
                      min_qual: float = DEFAULT_QUAL_THRESHOLD) -> List[DetectedVariant]:
    """
    Filter variants by quality score.
    
    Args:
        variants: List of detected variants
        min_qual: Minimum quality threshold
        
    Returns:
        Filtered list of variants
    """
    return [v for v in variants if v.quality >= min_qual]


def filter_by_type(variants: List[DetectedVariant],
                   variant_types: List[str]) -> List[DetectedVariant]:
    """
    Filter variants by type.
    
    Args:
        variants: List of detected variants
        variant_types: List of types to include (e.g., ["SNV", "INDEL"])
        
    Returns:
        Filtered list of variants
    """
    return [v for v in variants if v.variant_type in variant_types]


def get_snv_variants(variants: List[DetectedVariant]) -> List[DetectedVariant]:
    """Extract only SNV variants."""
    return filter_by_type(variants, ["SNV"])


def get_indel_variants(variants: List[DetectedVariant]) -> List[DetectedVariant]:
    """Extract only INDEL variants."""
    return filter_by_type(variants, ["INDEL"])


def annotate_with_bcftools(vcf_path: str, reference_db: str,
                          output_path: Optional[str] = None) -> str:
    """
    Annotate VCF using bcftools.
    
    Args:
        vcf_path: Path to input VCF
        reference_db: Path to reference database (VCF/BCF)
        output_path: Optional output path
        
    Returns:
        Path to annotated VCF
    """
    if output_path is None:
        output_path = str(vcf_path).replace('.vcf', '.annotated.vcf')
    
    try:
        cmd = [
            'bcftools', 'annotate',
            '-a', reference_db,
            '-c', 'INFO',
            '-o', output_path,
            str(vcf_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Annotated VCF written to {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"bcftools annotation failed: {e.stderr}")
        raise VariantDetectionError(f"bcftools annotation failed: {e.stderr}")
    except FileNotFoundError:
        logger.error("bcftools not found in PATH")
        raise VariantDetectionError("bcftools not found. Please install bcftools.")
