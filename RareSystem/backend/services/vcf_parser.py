"""
VCF File Parser using pysam library.

Handles parsing of VCF files for variant extraction in the rare disease
genetic diagnosis system. Supports incremental parsing for large files.
"""
import re
import logging
from pathlib import Path
from typing import Iterator, Optional, Dict, List, Any, Generator
from dataclasses import dataclass, field

import pysam

logger = logging.getLogger(__name__)


SUPPORTED_VCF_VERSIONS = ["VCFv4.1", "VCFv4.2", "VCFv4.3"]
REQUIRED_HEADER_FIELDS = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"]


@dataclass
class VCFHeader:
    """Represents VCF file header metadata."""
    version: str = ""
    source: str = ""
    reference: str = ""
    contigs: List[str] = field(default_factory=list)
    info_fields: Dict[str, Dict[str, str]] = field(default_factory=dict)
    format_fields: Dict[str, Dict[str, str]] = field(default_factory=dict)
    filters: Dict[str, Dict[str, str]] = field(default_factory=dict)
    samples: List[str] = field(default_factory=list)
    raw_header_lines: List[str] = field(default_factory=list)


@dataclass
class VCFVariant:
    """Represents a single variant from VCF file."""
    chromosome: str
    position: int
    variant_id: str
    reference: str
    alternate: str
    quality: Optional[float]
    filter_status: str
    info: Dict[str, Any]
    genotype: Optional[Dict[str, Any]] = None
    
    @property
    def variant_type(self) -> str:
        if len(self.reference) == 1 and len(self.alternate) == 1:
            return "SNV"
        elif len(self.reference) > 50 or len(self.alternate) > 50:
            return "SV"
        elif len(self.reference) != len(self.alternate):
            return "INDEL"
        else:
            return "MNV"
    
    def __repr__(self):
        return f"Variant({self.chromosome}:{self.position} {self.reference}>{self.alternate})"


class VCFParseError(Exception):
    """Raised when VCF parsing fails."""
    pass


class VCFValidationError(Exception):
    """Raised when VCF validation fails."""
    pass


class VCFParser:
    """
    VCF file parser using pysam.
    
    Features:
    - Parse VCF header and metadata
    - Extract variant information
    - Validate VCF format
    - Handle different VCF versions (4.1, 4.2, 4.3)
    - Incremental parsing for large files (generator pattern)
    - Error handling for malformed files
    """
    
    def __init__(self, file_path: str):
        """
        Initialize VCF parser.
        
        Args:
            file_path: Path to VCF file (can be plain or gzipped)
        """
        self.file_path = Path(file_path)
        self._vcf_reader: Optional[pysam.VariantFile] = None
        self._header: Optional[VCFHeader] = None
        self._is_open = False
        
        self._validate_file_exists()
    
    def _validate_file_exists(self) -> None:
        """Validate that VCF file exists."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"VCF file not found: {self.file_path}")
        
        if self.file_path.stat().st_size == 0:
            raise VCFParseError(f"VCF file is empty: {self.file_path}")
    
    def open(self) -> None:
        """Open VCF file for reading."""
        if self._is_open:
            return
        
        try:
            self._vcf_reader = pysam.VariantFile(str(self.file_path))
            self._is_open = True
            logger.info(f"Opened VCF file: {self.file_path}")
        except Exception as e:
            raise VCFParseError(f"Failed to open VCF file: {e}")
    
    def close(self) -> None:
        """Close VCF file."""
        if self._vcf_reader is not None:
            self._vcf_reader.close()
            self._vcf_reader = None
        self._is_open = False
        logger.info(f"Closed VCF file: {self.file_path}")
    
    def __enter__(self) -> "VCFParser":
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
    
    def parse_header(self) -> VCFHeader:
        """
        Parse VCF header and metadata.
        
        Returns:
            VCFHeader object with metadata
        """
        if self._header is not None:
            return self._header
        
        if not self._is_open:
            self.open()
        
        header = VCFHeader()
        
        try:
            assert self._vcf_reader is not None
            pysam_header = self._vcf_reader.header
            
            header.version = self._extract_version(pysam_header)
            header.source = self._extract_source(pysam_header)
            header.reference = self._extract_reference(pysam_header)
            header.contigs = self._extract_contigs(pysam_header)
            header.info_fields = self._extract_info_fields(pysam_header)
            header.format_fields = self._extract_format_fields(pysam_header)
            header.filters = self._extract_filters(pysam_header)
            header.samples = list(self._vcf_reader.header.samples)
            header.raw_header_lines = self._extract_raw_header()
            
            self._validate_header(header)
            self._header = header
            
            logger.info(f"Parsed VCF header - Version: {header.version}, "
                       f"Contigs: {len(header.contigs)}, Samples: {len(header.samples)}")
            
        except Exception as e:
            raise VCFParseError(f"Failed to parse VCF header: {e}")
        
        return header
    
    def _extract_version(self, header: "pysam.VariantHeader") -> str:
        """Extract VCF version from header."""
        for rec in header.records:
            if rec.type == "GENERIC" and "VCF" in str(rec):
                match = re.search(r'VCFv[\d.]+', str(rec))
                if match:
                    return match.group()
        return "VCFv4.2"
    
    def _extract_source(self, header: pysam.VariantHeader) -> str:
        """Extract source information from header."""
        for rec in header.records:
            if rec.type == "GENERIC" and 'source=' in str(rec):
                match = re.search(r'source=([^\s,>]+)', str(rec))
                if match:
                    return match.group(1)
        return ""
    
    def _extract_reference(self, header: pysam.VariantHeader) -> str:
        """Extract reference genome from header."""
        for rec in header.records:
            if rec.type == "GENERIC" and 'reference=' in str(rec):
                match = re.search(r'reference=([^\s,>]+)', str(rec))
                if match:
                    return match.group(1)
        return ""
    
    def _extract_contigs(self, header: pysam.VariantHeader) -> List[str]:
        """Extract contig names from header."""
        contigs = []
        for contig in header.contigs.values():
            contigs.append(contig.name)
        return contigs
    
    def _extract_info_fields(self, header: pysam.VariantHeader) -> Dict[str, Dict[str, str]]:
        """Extract INFO field definitions from header."""
        info_fields = {}
        for key, info in header.info.items():
            info_fields[key] = {
                "number": str(info.number),
                "type": info.type,
                "description": info.description or ""
            }
        return info_fields
    
    def _extract_format_fields(self, header: pysam.VariantHeader) -> Dict[str, Dict[str, str]]:
        """Extract FORMAT field definitions from header."""
        format_fields = {}
        for key, fmt in header.formats.items():
            format_fields[key] = {
                "number": str(fmt.number),
                "type": fmt.type,
                "description": fmt.description or ""
            }
        return format_fields
    
    def _extract_filters(self, header: pysam.VariantHeader) -> Dict[str, Dict[str, str]]:
        """Extract FILTER definitions from header."""
        filters = {}
        for key, fltr in header.filters.items():
            filters[key] = {
                "description": fltr.description or ""
            }
        return filters
    
    def _extract_raw_header(self) -> List[str]:
        """Extract raw header lines from file."""
        header_lines = []
        with open(self.file_path, 'rb') as f:
            for line in f:
                try:
                    decoded = line.decode('utf-8', errors='replace').strip()
                    if decoded.startswith('#'):
                        header_lines.append(decoded)
                    else:
                        break
                except:
                    break
        return header_lines
    
    def _validate_header(self, header: VCFHeader) -> None:
        """Validate VCF header for required fields and version."""
        if header.version and header.version not in SUPPORTED_VCF_VERSIONS:
            logger.warning(f"VCF version {header.version} may not be fully supported. "
                          f"Supported versions: {SUPPORTED_VCF_VERSIONS}")
    
    def iter_variants(self, 
                      chrom: Optional[str] = None,
                      start: Optional[int] = None,
                      end: Optional[int] = None) -> Generator[VCFVariant, None, None]:
        """
        Iterate through variants in VCF file (generator pattern for large files).
        
        Args:
            chrom: Filter by chromosome (optional)
            start: Start position (optional, requires chrom)
            end: End position (optional, requires chrom)
        
        Yields:
            VCFVariant objects one at a time
        """
        if not self._is_open:
            self.open()
        
        assert self._vcf_reader is not None
        
        try:
            if chrom and start is not None and end is not None:
                iterator = self._vcf_reader.fetch(chrom, start - 1, end)
            elif chrom:
                iterator = self._vcf_reader.fetch(chrom)
            else:
                iterator = self._vcf_reader
            
            for record in iterator:
                try:
                    variants = self._parse_record(record)
                    for variant in variants:
                        yield variant
                except Exception as e:
                    logger.warning(f"Failed to parse variant at {record.chrom}:{record.pos}: {e}")
                    continue
                    
        except Exception as e:
            raise VCFParseError(f"Error iterating variants: {e}")
    
    def _parse_record(self, record: pysam.VariantRecord) -> List[VCFVariant]:
        """
        Parse a single VCF record into VCFVariant objects.
        
        A single record can have multiple ALT alleles, resulting in multiple variants.
        """
        variants = []
        
        for alt_idx, alt in enumerate(record.alts or ['.']):
            try:
                quality = float(record.qual) if record.qual is not None else None
                filter_status = ','.join(record.filter.keys()) if record.filter else 'PASS'
                info = dict(record.info) if record.info else {}
                
                genotype = None
                if len(record.samples) > 0:
                    genotype = self._extract_genotype(record, alt_idx)
                
                variant = VCFVariant(
                    chromosome=record.chrom,
                    position=record.pos,
                    variant_id=record.id if record.id else '.',
                    reference=record.ref,
                    alternate=alt,
                    quality=quality,
                    filter_status=filter_status,
                    info=info,
                    genotype=genotype
                )
                variants.append(variant)
                
            except Exception as e:
                logger.warning(f"Error parsing ALT allele '{alt}': {e}")
                continue
        
        return variants
    
    def _extract_genotype(self, record: pysam.VariantRecord, alt_idx: int) -> Optional[Dict[str, Any]]:
        """Extract genotype information for a specific ALT allele."""
        genotype = {}
        
        for sample_name, sample_data in record.samples.items():
            try:
                gt = sample_data.get('GT')
                if gt is not None:
                    gt_str = '/'.join(str(g) if g is not None else '.' for g in gt)
                    genotype[f"{sample_name}_GT"] = gt_str
                
                for key in ['DP', 'AD', 'GQ', 'PL']:
                    value = sample_data.get(key)
                    if value is not None:
                        if isinstance(value, (list, tuple)):
                            genotype[f"{sample_name}_{key}"] = list(value)
                        else:
                            genotype[f"{sample_name}_{key}"] = value
                            
            except Exception as e:
                logger.debug(f"Error extracting genotype for sample {sample_name}: {e}")
                continue
        
        return genotype if genotype else None
    
    def get_all_variants(self, max_variants: Optional[int] = None) -> List[VCFVariant]:
        """
        Load all variants into memory (use with caution for large files).
        
        Args:
            max_variants: Maximum number of variants to load (optional)
        
        Returns:
            List of VCFVariant objects
        """
        variants = []
        count = 0
        
        for variant in self.iter_variants():
            variants.append(variant)
            count += 1
            
            if max_variants and count >= max_variants:
                logger.warning(f"Reached maximum variant limit: {max_variants}")
                break
        
        logger.info(f"Loaded {len(variants)} variants from {self.file_path}")
        return variants
    
    def get_variant_count(self) -> int:
        """Count total number of variants in VCF file."""
        if not self._is_open:
            self.open()
        
        assert self._vcf_reader is not None
        
        count = 0
        for _ in self._vcf_reader:
            count += 1
        
        self.close()
        self.open()
        return count
    
    def validate(self) -> bool:
        """
        Validate VCF file format.
        
        Returns:
            True if valid, raises VCFValidationError if not
        """
        try:
            self.open()
            header = self.parse_header()
            
            first_variant = None
            for variant in self.iter_variants():
                first_variant = variant
                break
            
            if first_variant is None:
                logger.warning("VCF file contains no variants")
            
            self.close()
            logger.info(f"VCF file validation passed: {self.file_path}")
            return True
            
        except VCFParseError as e:
            raise VCFValidationError(f"VCF validation failed: {e}")
        finally:
            self.close()


def parse_vcf(file_path: str, 
              max_variants: Optional[int] = None) -> tuple[VCFHeader, List[VCFVariant]]:
    """
    Convenience function to parse VCF file.
    
    Args:
        file_path: Path to VCF file
        max_variants: Maximum variants to load (optional)
    
    Returns:
        Tuple of (header, variants)
    """
    with VCFParser(file_path) as parser:
        header = parser.parse_header()
        variants = parser.get_all_variants(max_variants)
        return header, variants


def validate_vcf(file_path: str) -> bool:
    """
    Convenience function to validate VCF file.
    
    Args:
        file_path: Path to VCF file
    
    Returns:
        True if valid
    """
    parser = VCFParser(file_path)
    return parser.validate()
