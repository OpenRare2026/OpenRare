"""
Short Tandem Repeat (STR) Detection Module

Detects and analyzes STR expansions from VCF files for rare disease diagnosis.
Supports common disease-causing STR loci and calculates repeat expansion status.

Key features:
- Common pathogenic STR loci database
- Repeat count calculation from VCF INFO fields
- Expansion status assessment (normal, intermediate, pathogenic)
- Integration with VCFParser
"""
import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from .vcf_parser import VCFParser, VCFVariant, VCFParseError

logger = logging.getLogger(__name__)


class STRRepeatType(Enum):
    """STR repeat motif types."""
    CAG = "CAG"
    CGG = "CGG"
    GAA = "GAA"
    CTG = "CTG"
    ATTCT = "ATTCT"
    TGGAA = "TGGAA"
    CCCCG = "CCCCG"
    OTHER = "OTHER"


class ExpansionStatus(Enum):
    """STR expansion status categories."""
    NORMAL = "Normal"
    INTERMEDIATE = "Intermediate"
    PREMUTATION = "Premutation"
    FULL_MUTATION = "Full Mutation"
    UNKNOWN = "Unknown"


@dataclass
class STRDefinition:
    """Definition of a disease-causing STR locus."""
    gene: str
    chromosome: str
    position: int
    repeat_motif: str
    repeat_type: STRRepeatType
    disease: str
    inheritance: str
    normal_range: Tuple[int, int]
    intermediate_range: Optional[Tuple[int, int]]
    pathogenic_range: Tuple[int, int]
    premutation_range: Optional[Tuple[int, int]] = None
    
    def get_status(self, repeat_count: int) -> ExpansionStatus:
        """Determine expansion status based on repeat count."""
        if self.normal_range[0] <= repeat_count <= self.normal_range[1]:
            return ExpansionStatus.NORMAL
        
        if self.intermediate_range:
            if self.intermediate_range[0] <= repeat_count <= self.intermediate_range[1]:
                return ExpansionStatus.INTERMEDIATE
        
        if self.premutation_range:
            if self.premutation_range[0] <= repeat_count <= self.premutation_range[1]:
                return ExpansionStatus.PREMUTATION
        
        if repeat_count >= self.pathogenic_range[0]:
            return ExpansionStatus.FULL_MUTATION
        
        if repeat_count < self.normal_range[0]:
            return ExpansionStatus.NORMAL
        
        return ExpansionStatus.UNKNOWN


@dataclass
class STRVariant:
    """Detected STR variant with analysis results."""
    locus_id: str
    gene: str
    chromosome: str
    position: int
    repeat_motif: str
    repeat_count: int
    repeat_length_bp: int
    expansion_status: ExpansionStatus
    disease: str
    inheritance: str
    confidence: float
    raw_variant: Optional[VCFVariant] = None
    info_data: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "locus_id": self.locus_id,
            "gene": self.gene,
            "chromosome": self.chromosome,
            "position": self.position,
            "repeat_motif": self.repeat_motif,
            "repeat_count": self.repeat_count,
            "repeat_length_bp": self.repeat_length_bp,
            "expansion_status": self.expansion_status.value,
            "disease": self.disease,
            "inheritance": self.inheritance,
            "confidence": self.confidence,
            "warnings": self.warnings,
        }


@dataclass
class STRReport:
    """Complete STR analysis report."""
    sample_id: str
    analysis_date: str
    total_loci_analyzed: int
    pathogenic_count: int
    intermediate_count: int
    normal_count: int
    unknown_count: int
    str_variants: List[STRVariant]
    summary: str
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "analysis_date": self.analysis_date,
            "total_loci_analyzed": self.total_loci_analyzed,
            "pathogenic_count": self.pathogenic_count,
            "intermediate_count": self.intermediate_count,
            "normal_count": self.normal_count,
            "unknown_count": self.unknown_count,
            "str_variants": [v.to_dict() for v in self.str_variants],
            "summary": self.summary,
            "warnings": self.warnings,
        }


PATHOGENIC_STR_LOCI: Dict[str, STRDefinition] = {
    "HTT": STRDefinition(
        gene="HTT",
        chromosome="chr4",
        position=3076604,
        repeat_motif="CAG",
        repeat_type=STRRepeatType.CAG,
        disease="Huntington Disease",
        inheritance="Autosomal Dominant",
        normal_range=(10, 35),
        intermediate_range=(36, 39),
        pathogenic_range=(40, 250),
    ),
    "FMR1_CGG": STRDefinition(
        gene="FMR1",
        chromosome="chrX",
        position=147912880,
        repeat_motif="CGG",
        repeat_type=STRRepeatType.CGG,
        disease="Fragile X Syndrome",
        inheritance="X-linked",
        normal_range=(5, 44),
        intermediate_range=(45, 54),
        premutation_range=(55, 200),
        pathogenic_range=(200, 1000),
    ),
    "FMR1_GCC": STRDefinition(
        gene="FMR1",
        chromosome="chrX",
        position=147912850,
        repeat_motif="GCC",
        repeat_type=STRRepeatType.OTHER,
        disease="FXTAS (FMR1-related tremor/ataxia)",
        inheritance="X-linked",
        normal_range=(5, 40),
        intermediate_range=None,
        premutation_range=(55, 200),
        pathogenic_range=(200, 900),
    ),
    "ATXN1": STRDefinition(
        gene="ATXN1",
        chromosome="chr6",
        position=16327864,
        repeat_motif="CAG",
        repeat_type=STRRepeatType.CAG,
        disease="Spinocerebellar Ataxia Type 1",
        inheritance="Autosomal Dominant",
        normal_range=(6, 38),
        intermediate_range=(39, 44),
        pathogenic_range=(45, 83),
    ),
    "ATXN2": STRDefinition(
        gene="ATXN2",
        chromosome="chr12",
        position=111660717,
        repeat_motif="CAG",
        repeat_type=STRRepeatType.CAG,
        disease="Spinocerebellar Ataxia Type 2",
        inheritance="Autosomal Dominant",
        normal_range=(14, 31),
        intermediate_range=(32, 34),
        pathogenic_range=(35, 500),
    ),
    "ATXN3": STRDefinition(
        gene="ATXN3",
        chromosome="chr14",
        position=92073109,
        repeat_motif="CAG",
        repeat_type=STRRepeatType.CAG,
        disease="Spinocerebellar Ataxia Type 3 (Machado-Joseph)",
        inheritance="Autosomal Dominant",
        normal_range=(12, 44),
        intermediate_range=(45, 51),
        pathogenic_range=(52, 86),
    ),
    "ATXN7": STRDefinition(
        gene="ATXN7",
        chromosome="chr3",
        position=63898309,
        repeat_motif="CAG",
        repeat_type=STRRepeatType.CAG,
        disease="Spinocerebellar Ataxia Type 7",
        inheritance="Autosomal Dominant",
        normal_range=(4, 19),
        intermediate_range=(20, 28),
        pathogenic_range=(35, 460),
    ),
    "FXN": STRDefinition(
        gene="FXN",
        chromosome="chr9",
        position=71652202,
        repeat_motif="GAA",
        repeat_type=STRRepeatType.GAA,
        disease="Friedreich Ataxia",
        inheritance="Autosomal Recessive",
        normal_range=(5, 33),
        intermediate_range=None,
        pathogenic_range=(66, 1700),
    ),
    "DM1": STRDefinition(
        gene="DMPK",
        chromosome="chr19",
        position=46273462,
        repeat_motif="CTG",
        repeat_type=STRRepeatType.CTG,
        disease="Myotonic Dystrophy Type 1",
        inheritance="Autosomal Dominant",
        normal_range=(5, 34),
        intermediate_range=(35, 49),
        premutation_range=(50, 149),
        pathogenic_range=(50, 3000),
    ),
    "DM2": STRDefinition(
        gene="CNBP",
        chromosome="chr3",
        position=129172500,
        repeat_motif="CCTG",
        repeat_type=STRRepeatType.OTHER,
        disease="Myotonic Dystrophy Type 2",
        inheritance="Autosomal Dominant",
        normal_range=(11, 26),
        intermediate_range=None,
        pathogenic_range=(75, 11000),
    ),
    "AR": STRDefinition(
        gene="AR",
        chromosome="chrX",
        position=67546404,
        repeat_motif="CAG",
        repeat_type=STRRepeatType.CAG,
        disease="Spinal and Bulbar Muscular Atrophy (Kennedy Disease)",
        inheritance="X-linked",
        normal_range=(9, 35),
        intermediate_range=(36, 38),
        pathogenic_range=(38, 70),
    ),
    "C9ORF72": STRDefinition(
        gene="C9ORF72",
        chromosome="chr9",
        position=27573544,
        repeat_motif="GGGGCC",
        repeat_type=STRRepeatType.OTHER,
        disease="ALS/FTD (C9ORF72)",
        inheritance="Autosomal Dominant",
        normal_range=(2, 24),
        intermediate_range=(25, 30),
        pathogenic_range=(30, 5000),
    ),
}


class STRDetector:
    """
    Short Tandem Repeat Detection and Analysis.
    
    Analyzes VCF files for STR expansions at known disease-causing loci.
    Supports multiple INFO field formats for repeat count extraction.
    
    Usage:
        detector = STRDetector()
        report = detector.analyze_vcf("sample.vcf")
        for variant in report.str_variants:
            print(f"{variant.gene}: {variant.repeat_count} repeats - {variant.expansion_status}")
    """
    
    VERSION = "1.0.0"
    
    REPEAT_COUNT_FIELDS = [
        "REPCN", "REPEATS", "RPT", "RN", "NBR", "REPEAT_COUNT",
        "STR_LEN", "STRLEN", "MOTIFS", "NUM_MOTIFS"
    ]
    
    MOTIF_FIELDS = ["MOTIF", "STR_MOTIF", "RU", "REPEAT_UNIT"]
    
    def __init__(self, custom_loci: Optional[Dict[str, STRDefinition]] = None):
        """
        Initialize STR detector.
        
        Args:
            custom_loci: Additional custom STR loci to analyze
        """
        self.loci = PATHOGENIC_STR_LOCI.copy()
        if custom_loci:
            self.loci.update(custom_loci)
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"STRDetector v{self.VERSION} initialized with {len(self.loci)} loci")
    
    def analyze_vcf(
        self,
        vcf_path: str,
        sample_id: Optional[str] = None,
        locus_filter: Optional[List[str]] = None
    ) -> STRReport:
        """
        Analyze VCF file for STR expansions.
        
        Args:
            vcf_path: Path to VCF file
            sample_id: Optional sample identifier
            locus_filter: Optional list of gene names to filter analysis
        
        Returns:
            STRReport with analysis results
        """
        from datetime import datetime
        
        vcf_path_obj = Path(vcf_path)
        if not vcf_path_obj.exists():
            raise FileNotFoundError(f"VCF file not found: {vcf_path}")
        
        sample_id = sample_id or vcf_path_obj.stem
        self.logger.info(f"Analyzing STRs in {vcf_path} for sample {sample_id}")
        
        str_variants: List[STRVariant] = []
        warnings: List[str] = []
        
        loci_to_analyze = self._filter_loci(locus_filter)
        
        with VCFParser(str(vcf_path)) as parser:
            header = parser.parse_header()
            
            for locus_id, str_def in loci_to_analyze.items():
                try:
                    variant = self._analyze_locus(parser, str_def, locus_id)
                    if variant:
                        str_variants.append(variant)
                except Exception as e:
                    warnings.append(f"Error analyzing {str_def.gene}: {str(e)}")
                    self.logger.error(f"Error analyzing locus {locus_id}: {e}")
        
        pathogenic = [v for v in str_variants if v.expansion_status in 
                      (ExpansionStatus.FULL_MUTATION, ExpansionStatus.PREMUTATION)]
        intermediate = [v for v in str_variants if v.expansion_status == ExpansionStatus.INTERMEDIATE]
        normal = [v for v in str_variants if v.expansion_status == ExpansionStatus.NORMAL]
        unknown = [v for v in str_variants if v.expansion_status == ExpansionStatus.UNKNOWN]
        
        summary = self._generate_summary(str_variants, pathogenic, intermediate)
        
        report = STRReport(
            sample_id=sample_id,
            analysis_date=datetime.now().isoformat(),
            total_loci_analyzed=len(loci_to_analyze),
            pathogenic_count=len(pathogenic),
            intermediate_count=len(intermediate),
            normal_count=len(normal),
            unknown_count=len(unknown),
            str_variants=str_variants,
            summary=summary,
            warnings=warnings,
        )
        
        self.logger.info(f"STR analysis complete: {len(pathogenic)} pathogenic, "
                        f"{len(intermediate)} intermediate, {len(normal)} normal")
        
        return report
    
    def _filter_loci(self, locus_filter: Optional[List[str]] = None) -> Dict[str, STRDefinition]:
        """Filter loci by gene name if specified."""
        if not locus_filter:
            return self.loci
        
        return {
            k: v for k, v in self.loci.items()
            if v.gene in locus_filter or k in locus_filter
        }
    
    def _analyze_locus(
        self,
        parser: VCFParser,
        str_def: STRDefinition,
        locus_id: str
    ) -> Optional[STRVariant]:
        """Analyze a single STR locus."""
        chrom = self._normalize_chromosome(str_def.chromosome)
        start = max(1, str_def.position - 100)
        end = str_def.position + 100
        
        variants = list(parser.iter_variants(chrom, start, end))
        
        if not variants:
            self.logger.debug(f"No variants found at {str_def.gene} locus")
            return self._create_normal_variant(str_def, locus_id)
        
        best_variant = None
        best_repeat_count = None
        best_confidence = 0.0
        
        for variant in variants:
            repeat_count, confidence = self._extract_repeat_count(variant, str_def)
            
            if repeat_count is not None:
                if best_repeat_count is None or confidence > best_confidence:
                    best_variant = variant
                    best_repeat_count = repeat_count
                    best_confidence = confidence
        
        if best_repeat_count is not None:
            status = str_def.get_status(best_repeat_count)
            repeat_length = best_repeat_count * len(str_def.repeat_motif)
            
            return STRVariant(
                locus_id=locus_id,
                gene=str_def.gene,
                chromosome=str_def.chromosome,
                position=str_def.position,
                repeat_motif=str_def.repeat_motif,
                repeat_count=best_repeat_count,
                repeat_length_bp=repeat_length,
                expansion_status=status,
                disease=str_def.disease,
                inheritance=str_def.inheritance,
                confidence=best_confidence,
                raw_variant=best_variant,
                info_data=dict(best_variant.info) if best_variant else {},
            )
        
        return self._create_normal_variant(str_def, locus_id)
    
    def _extract_repeat_count(
        self,
        variant: VCFVariant,
        str_def: STRDefinition
    ) -> Tuple[Optional[int], float]:
        """Extract repeat count from VCF INFO field."""
        info = variant.info or {}
        confidence = 0.5
        
        for field in self.REPEAT_COUNT_FIELDS:
            if field in info:
                value = info[field]
                repeat_count = self._parse_repeat_value(value)
                if repeat_count is not None:
                    confidence = 0.9
                    self.logger.debug(f"Found repeat count {repeat_count} in field {field}")
                    return repeat_count, confidence
        
        repeat_count = self._estimate_from_ref_alt(variant, str_def)
        if repeat_count is not None:
            confidence = 0.6
            return repeat_count, confidence
        
        if "STR" in info or "VAR_TYPE" in info:
            repeat_count = self._extract_from_str_annotation(info)
            if repeat_count is not None:
                confidence = 0.7
                return repeat_count, confidence
        
        return None, 0.0
    
    def _parse_repeat_value(self, value: Any) -> Optional[int]:
        """Parse repeat count value from various formats."""
        if isinstance(value, int):
            return value
        
        if isinstance(value, str):
            if ',' in value:
                try:
                    values = [int(x.strip()) for x in value.split(',') if x.strip().isdigit()]
                    return max(values) if values else None
                except ValueError:
                    pass
            
            try:
                return int(float(value))
            except (ValueError, TypeError):
                pass
            
            match = re.search(r'(\d+)', value)
            if match:
                return int(match.group(1))
        
        if isinstance(value, (list, tuple)) and len(value) > 0:
            return self._parse_repeat_value(value[0])
        
        return None
    
    def _estimate_from_ref_alt(
        self,
        variant: VCFVariant,
        str_def: STRDefinition
    ) -> Optional[int]:
        """Estimate repeat count from REF/ALT sequences."""
        motif = str_def.repeat_motif
        
        alt = variant.alternate.upper()
        
        motif_pattern = re.compile(f'({motif})+', re.IGNORECASE)
        match = motif_pattern.search(alt)
        if match:
            matched_seq = match.group(0)
            return len(matched_seq) // len(motif)
        
        ref = variant.reference.upper()
        match = motif_pattern.search(ref)
        if match:
            matched_seq = match.group(0)
            return len(matched_seq) // len(motif)
        
        return None
    
    def _extract_from_str_annotation(self, info: Dict[str, Any]) -> Optional[int]:
        """Extract repeat count from STR-specific annotations."""
        for key, value in info.items():
            if 'REPEAT' in key.upper() or 'STR' in key.upper():
                count = self._parse_repeat_value(value)
                if count is not None:
                    return count
        
        return None
    
    def _normalize_chromosome(self, chrom: str) -> str:
        """Normalize chromosome name for VCF lookup."""
        if chrom.startswith('chr'):
            return chrom
        return f'chr{chrom}'
    
    def _create_normal_variant(
        self,
        str_def: STRDefinition,
        locus_id: str
    ) -> STRVariant:
        """Create a normal-range variant entry when no expansion detected."""
        default_count = str_def.normal_range[0]
        
        return STRVariant(
            locus_id=locus_id,
            gene=str_def.gene,
            chromosome=str_def.chromosome,
            position=str_def.position,
            repeat_motif=str_def.repeat_motif,
            repeat_count=default_count,
            repeat_length_bp=default_count * len(str_def.repeat_motif),
            expansion_status=ExpansionStatus.NORMAL,
            disease=str_def.disease,
            inheritance=str_def.inheritance,
            confidence=0.3,
            warnings=["No variant data found, assuming normal range"],
        )
    
    def _generate_summary(
        self,
        all_variants: List[STRVariant],
        pathogenic: List[STRVariant],
        intermediate: List[STRVariant]
    ) -> str:
        """Generate human-readable summary of STR analysis."""
        if not pathogenic and not intermediate:
            return "No pathogenic STR expansions detected."
        
        lines = []
        
        if pathogenic:
            lines.append("Pathogenic STR expansions detected:")
            for v in pathogenic:
                lines.append(f"  - {v.gene}: {v.repeat_count} repeats ({v.expansion_status.value})")
                lines.append(f"    Disease: {v.disease}")
                lines.append(f"    Inheritance: {v.inheritance}")
        
        if intermediate:
            if lines:
                lines.append("")
            lines.append("Intermediate/uncertain STR expansions:")
            for v in intermediate:
                lines.append(f"  - {v.gene}: {v.repeat_count} repeats (Intermediate range)")
                lines.append(f"    Disease: {v.disease}")
        
        return "\n".join(lines)
    
    def get_locus_info(self, gene: str) -> Optional[STRDefinition]:
        """Get STR locus definition for a gene."""
        for locus_id, str_def in self.loci.items():
            if str_def.gene == gene or locus_id == gene:
                return str_def
        return None
    
    def add_custom_locus(self, locus_id: str, definition: STRDefinition) -> None:
        """Add a custom STR locus for analysis."""
        self.loci[locus_id] = definition
        self.logger.info(f"Added custom STR locus: {locus_id}")


def analyze_str_expansions(
    vcf_path: str,
    sample_id: Optional[str] = None,
    genes: Optional[List[str]] = None
) -> STRReport:
    """
    Convenience function for STR analysis.
    
    Args:
        vcf_path: Path to VCF file
        sample_id: Optional sample identifier
        genes: Optional list of genes to analyze
    
    Returns:
        STRReport with analysis results
    """
    detector = STRDetector()
    return detector.analyze_vcf(vcf_path, sample_id, genes)


def get_supported_str_genes() -> List[str]:
    """Get list of supported disease-causing STR genes."""
    return sorted(set(str_def.gene for str_def in PATHOGENIC_STR_LOCI.values()))
