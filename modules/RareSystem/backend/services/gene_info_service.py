"""
Gene Info Service - Fetches gene annotations from external APIs.

Uses free APIs:
- MyGene.info (aggregates multiple sources including HGNC, NCBI, Ensembl)

No API keys required.
"""
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


@dataclass
class GeneInfo:
    """Gene annotation information."""
    symbol: str
    name: str = ""
    description: str = ""
    chromosome: str = ""
    location: str = ""
    omim_id: Optional[str] = None
    hgnc_id: Optional[str] = None
    ensembl_id: Optional[str] = None
    diseases: List[str] = field(default_factory=list)
    inheritance: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)


class GeneInfoService:
    """
    Service for fetching gene information from external APIs.
    
    Uses MyGene.info as primary source (aggregates HGNC, NCBI, Ensembl).
    Implements in-memory caching with TTL.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache: Dict[str, tuple] = {}  # {gene: (info, timestamp)}
            cls._instance._cache_ttl = 86400  # 24 hours in seconds
        return cls._instance
    
    def get_gene_info(self, gene_name: str) -> Optional[GeneInfo]:
        """
        Get gene information from external APIs.
        
        Args:
            gene_name: Gene symbol (e.g., "BRCA1")
            
        Returns:
            GeneInfo if found, None otherwise
        """
        if not gene_name:
            return None
        
        gene_name = gene_name.upper().strip()
        
        # Check cache first
        if gene_name in self._cache:
            cached_info, cached_time = self._cache[gene_name]
            if (datetime.now() - cached_time).total_seconds() < self._cache_ttl:
                return cached_info
        
        # Fetch from MyGene.info
        info = self._fetch_from_mygene(gene_name)
        
        if info:
            self._cache[gene_name] = (info, datetime.now())
        
        return info
    
    def _fetch_from_mygene(self, gene_name: str) -> Optional[GeneInfo]:
        """Fetch gene info from MyGene.info API."""
        try:
            # MyGene.info query endpoint
            url = "https://mygene.info/v3/query"
            params = {
                "q": f"symbol:{gene_name}",
                "species": "human",
                "fields": "symbol,name,summary,genomic_pos,OMIM,HGNC,ensembl,disease,alias"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("hits"):
                logger.debug(f"No gene found for: {gene_name}")
                return None
            
            hit = data["hits"][0]
            
            # Parse genomic position
            chrom = ""
            location = ""
            if "genomic_pos" in hit:
                pos = hit["genomic_pos"]
                if isinstance(pos, list):
                    pos = pos[0] if pos else {}
                if isinstance(pos, dict):
                    chrom = str(pos.get("chr", ""))
                    start = pos.get("start", "")
                    end = pos.get("end", "")
                    if start and end:
                        location = f"{start}-{end}"
            
            # Parse OMIM ID
            omim_id = None
            if "OMIM" in hit:
                omim_data = hit["OMIM"]
                if isinstance(omim_data, list):
                    omim_id = str(omim_data[0]) if omim_data else None
                else:
                    omim_id = str(omim_data)
            
            # Parse HGNC ID
            hgnc_id = None
            if "HGNC" in hit:
                hgnc_data = hit["HGNC"]
                if isinstance(hgnc_data, str):
                    hgnc_id = hgnc_data
                elif isinstance(hgnc_data, list) and hgnc_data:
                    hgnc_id = str(hgnc_data[0])
            
            # Parse Ensembl ID
            ensembl_id = None
            if "ensembl" in hit:
                ensembl_data = hit["ensembl"]
                if isinstance(ensembl_data, dict):
                    ensembl_id = ensembl_data.get("gene", "")
                elif isinstance(ensembl_data, list) and ensembl_data:
                    ensembl_id = ensembl_data[0].get("gene", "")
            
            # Parse diseases
            diseases = []
            if "disease" in hit:
                disease_data = hit["disease"]
                if isinstance(disease_data, list):
                    diseases = [
                        d.get("name", "") for d in disease_data 
                        if isinstance(d, dict) and d.get("name")
                    ][:10]  # Limit to 10
                elif isinstance(disease_data, dict):
                    name = disease_data.get("name", "")
                    if name:
                        diseases = [name]
            
            # Parse aliases
            aliases = hit.get("alias", [])
            if isinstance(aliases, str):
                aliases = [aliases]
            aliases = aliases[:5] if isinstance(aliases, list) else []
            
            # Derive inheritance patterns
            inheritance = self._infer_inheritance(gene_name, diseases)
            
            return GeneInfo(
                symbol=hit.get("symbol", gene_name),
                name=hit.get("name", ""),
                description=hit.get("summary", ""),
                chromosome=chrom,
                location=location,
                omim_id=omim_id,
                hgnc_id=hgnc_id,
                ensembl_id=ensembl_id,
                diseases=diseases,
                inheritance=inheritance,
                aliases=aliases
            )
            
        except requests.Timeout:
            logger.warning(f"Timeout fetching gene info for {gene_name}")
            return None
        except requests.RequestException as e:
            logger.warning(f"Request error fetching gene info for {gene_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching gene info for {gene_name}: {e}")
            return None
    
    def _infer_inheritance(self, gene_name: str, diseases: List[str]) -> List[str]:
        """Infer inheritance patterns from gene name or diseases."""
        inheritance = []
        
        # Known inheritance patterns for common disease genes
        known_patterns: Dict[str, List[str]] = {
            "BRCA1": ["AD"],
            "BRCA2": ["AD"],
            "TP53": ["AD"],
            "MLH1": ["AD"],
            "MSH2": ["AD"],
            "MSH6": ["AD"],
            "PMS2": ["AD"],
            "APC": ["AD"],
            "CFTR": ["AR"],
            "PAH": ["AR"],
            "GAA": ["AR"],
            "SMN1": ["AR"],
            "HBB": ["AR"],
            "G6PD": ["XL"],
            "DMD": ["XL"],
            "FMR1": ["XL"],
            "HTT": ["AD"],
            "MYH7": ["AD"],
            "LMNA": ["AD"],
            "TSC1": ["AD"],
            "TSC2": ["AD"],
            "NF1": ["AD"],
            "NF2": ["AD"],
            "VHL": ["AD"],
            "RET": ["AD"],
            "PTEN": ["AD"],
            "STK11": ["AD"],
            "CDH1": ["AD"],
        }
        
        gene_upper = gene_name.upper()
        if gene_upper in known_patterns:
            inheritance = known_patterns[gene_upper]
        else:
            # Try to infer from disease names
            disease_text = " ".join(diseases).lower()
            if "autosomal dominant" in disease_text:
                inheritance.append("AD")
            if "autosomal recessive" in disease_text:
                inheritance.append("AR")
            if "x-linked" in disease_text:
                inheritance.append("XL")
            if "mitochondrial" in disease_text:
                inheritance.append("Mitochondrial")
        
        return inheritance
    
    def get_gene_info_batch(self, gene_names: List[str]) -> Dict[str, Optional[GeneInfo]]:
        """Get gene info for multiple genes."""
        results = {}
        for gene in gene_names:
            results[gene] = self.get_gene_info(gene)
        return results
    
    def clear_cache(self):
        """Clear the gene info cache."""
        self._cache.clear()


# Singleton instance
_gene_info_service: Optional[GeneInfoService] = None


def get_gene_info_service() -> GeneInfoService:
    """Get or create the singleton GeneInfoService instance."""
    global _gene_info_service
    if _gene_info_service is None:
        _gene_info_service = GeneInfoService()
    return _gene_info_service
