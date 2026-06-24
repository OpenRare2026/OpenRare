"""
Gene Lookup Service - Maps genomic coordinates to gene names using GFF3 annotation.

Uses GRCh38 reference genome (GENCODE v48 annotation).
Implements efficient binary search for coordinate lookup.
"""
import logging
import os
import bisect
from typing import Optional, List, Tuple, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class GeneLookupService:
    """
    Singleton service for looking up genes by genomic coordinates.
    
    Parses GFF3 file on first use and caches gene intervals in memory.
    Uses binary search for efficient coordinate lookup.
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if GeneLookupService._initialized:
            return
        
        self._genes_by_chr: Dict[str, List[Tuple[int, int, str]]] = {}
        self._gff3_path = self._find_gff3_path()
        
        if self._gff3_path:
            self._load_gff3()
            GeneLookupService._initialized = True
        else:
            logger.warning("GFF3 file not found. Gene lookup will return None.")
    
    def _find_gff3_path(self) -> Optional[str]:
        """Find GFF3 annotation file."""
        possible_paths = [
            # Relative to backend directory
            os.path.join(os.path.dirname(__file__), '..', 'reference', 'gencode.v48.annotation.gff3'),
            # Via environment variable
            os.environ.get('GFF3_ANNOTATION_PATH', ''),
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                logger.info(f"Found GFF3 file at: {abs_path}")
                return abs_path
        
        return None
    
    def _load_gff3(self):
        """Load gene entries from GFF3 file."""
        if not self._gff3_path:
            return
            
        logger.info(f"Loading GFF3 annotation from {self._gff3_path}")
        gene_count = 0
        
        try:
            with open(self._gff3_path, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    
                    parts = line.strip().split('\t')
                    if len(parts) < 9:
                        continue
                    
                    if parts[2] != 'gene':
                        continue
                    
                    chrom = parts[0]
                    try:
                        start = int(parts[3])
                        end = int(parts[4])
                    except ValueError:
                        continue
                    
                    gene_name = self._parse_gene_name(parts[8])
                    if not gene_name:
                        continue
                    
                    if chrom not in self._genes_by_chr:
                        self._genes_by_chr[chrom] = []
                    
                    self._genes_by_chr[chrom].append((start, end, gene_name))
                    gene_count += 1
            
            # Sort by start position for binary search
            for chrom in self._genes_by_chr:
                self._genes_by_chr[chrom].sort(key=lambda x: x[0])
            
            logger.info(f"Loaded {gene_count} genes from {len(self._genes_by_chr)} chromosomes")
            
        except Exception as e:
            logger.error(f"Failed to load GFF3 file: {e}")
    
    def _parse_gene_name(self, attributes: str) -> Optional[str]:
        """Parse gene_name from GFF3 attributes column."""
        for attr in attributes.split(';'):
            attr = attr.strip()
            if attr.startswith('gene_name='):
                return attr.split('=', 1)[1]
        return None
    
    def _normalize_chromosome(self, chromosome: str) -> str:
        """Normalize chromosome name to match GFF3 format (chr prefix)."""
        chromosome = str(chromosome)
        if chromosome.startswith('chr'):
            return chromosome
        return f'chr{chromosome}'
    
    def lookup_gene(self, chromosome: str, position: int) -> Optional[str]:
        """
        Look up gene name by genomic coordinates.
        
        Args:
            chromosome: Chromosome name (e.g., "1", "chr1", "X", "chrX")
            position: 1-based genomic position
            
        Returns:
            Gene symbol if found, None otherwise
        """
        if not self._genes_by_chr:
            return None
        
        chrom = self._normalize_chromosome(chromosome)
        
        if chrom not in self._genes_by_chr:
            # Try without chr prefix
            alt_chrom = chrom[3:] if chrom.startswith('chr') else f'chr{chrom}'
            if alt_chrom in self._genes_by_chr:
                chrom = alt_chrom
            else:
                return None
        
        genes = self._genes_by_chr[chrom]
        if not genes:
            return None
        
        # Binary search to find genes that might contain this position
        # genes are sorted by start position
        idx = bisect.bisect_left(genes, (position, 0, ''))
        
        # Check genes around the found index
        candidates = []
        if idx > 0:
            candidates.append(idx - 1)
        if idx < len(genes):
            candidates.append(idx)
        if idx > 1:
            candidates.append(idx - 2)
        
        for i in candidates:
            start, end, gene_name = genes[i]
            if start <= position <= end:
                return gene_name
        
        return None
    
    def lookup_genes_batch(
        self, 
        variants: List[Tuple[str, int]]
    ) -> Dict[Tuple[str, int], Optional[str]]:
        """
        Batch lookup genes for multiple variants.
        
        Args:
            variants: List of (chromosome, position) tuples
            
        Returns:
            Dictionary mapping (chromosome, position) to gene name
        """
        results = {}
        for chrom, pos in variants:
            results[(chrom, pos)] = self.lookup_gene(chrom, pos)
        return results
    
    def get_gene_count(self) -> int:
        """Get total number of loaded genes."""
        return sum(len(genes) for genes in self._genes_by_chr.values())
    
    def get_chromosomes(self) -> List[str]:
        """Get list of chromosomes with gene annotations."""
        return sorted(self._genes_by_chr.keys())


# Singleton instance
_gene_lookup_service: Optional[GeneLookupService] = None


def get_gene_lookup_service() -> GeneLookupService:
    """Get or create the singleton GeneLookupService instance."""
    global _gene_lookup_service
    if _gene_lookup_service is None:
        _gene_lookup_service = GeneLookupService()
    return _gene_lookup_service
