"""
Reactome Pathway Service - pathway enrichment analysis and gene mapping.
"""
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

REACTOME_ANALYSIS_URL = "https://reactome.org/AnalysisService"
REACTOME_CONTENT_URL = "https://reactome.org/ContentService"


@dataclass
class PathwayResult:
    st_id: str
    name: str
    p_value: float
    fdr: float
    entities_count: int
    entities_found: int
    entities_ratio: float
    species: str
    mapped_genes: List[str] = field(default_factory=list)
    pathway_type: str = "Pathway"
    compartments: List[str] = field(default_factory=list)


@dataclass
class PathwayAnalysisResult:
    token: str
    pathways: List[PathwayResult]
    genes_not_found: int
    summary: Dict[str, Any]


class ReactomeService:
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def map_gene_to_pathways_batch(
        self, 
        genes: List[str], 
        batch_size: int = 10
    ) -> Dict[str, List[str]]:
        """
        Batch map gene symbols to Reactome pathways using concurrent requests.
        
        Args:
            genes: List of gene symbols
            batch_size: Number of concurrent requests
        
        Returns:
            Dict mapping pathway stId to list of genes
        """
        client = await self._get_client()
        pathway_to_genes: Dict[str, List[str]] = {}
        
        async def fetch_pathways_for_gene(gene: str) -> List[tuple]:
            try:
                response = await client.get(
                    f"{REACTOME_CONTENT_URL}/data/mapping/HGNC/{gene}/pathways",
                    headers={"Accept": "application/json"}
                )
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                pathways = response.json()
                return [(pw.get("stId", ""), gene) for pw in pathways if pw.get("stId")]
            except Exception as e:
                logger.debug(f"Gene mapping failed for {gene}: {e}")
                return []

        semaphore = asyncio.Semaphore(batch_size)
        
        async def fetch_with_semaphore(gene: str):
            async with semaphore:
                return await fetch_pathways_for_gene(gene)

        tasks = [fetch_with_semaphore(gene) for gene in genes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                continue
            for st_id, gene in result:
                if st_id not in pathway_to_genes:
                    pathway_to_genes[st_id] = []
                if gene not in pathway_to_genes[st_id]:
                    pathway_to_genes[st_id].append(gene)
        
        return pathway_to_genes

    async def get_pathway_type_and_compartments(self, st_id: str) -> tuple[str, List[str]]:
        """
        Get pathway type and compartments for a pathway.
        
        Args:
            st_id: Reactome stable identifier
        
        Returns:
            Tuple of (type, compartments list)
        """
        client = await self._get_client()
        try:
            response = await client.get(
                f"{REACTOME_CONTENT_URL}/data/query/{st_id}",
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 404:
                return ("Pathway", [])
                
            response.raise_for_status()
            data = response.json()
            
            # Handle case where Reactome API returns a list instead of a dict
            if isinstance(data, list):
                if len(data) == 0:
                    return ("Pathway", [])
                data = data[0]
            
            pathway_type = data.get("schemaClass", "Pathway")
            
            compartments = []
            if data.get("compartment"):
                compartments = [c.get("displayName", "") for c in data["compartment"] if c.get("displayName")]
            
            return (pathway_type, compartments)
            
        except Exception as e:
            logger.debug(f"Failed to get pathway details for {st_id}: {e}")
            return ("Pathway", [])

    async def analyze_genes(self, genes: List[str]) -> Optional[PathwayAnalysisResult]:
        """
        Perform pathway enrichment analysis on a list of genes.
        
        Args:
            genes: List of gene symbols
        
        Returns:
            PathwayAnalysisResult or None if analysis fails
        """
        if not genes:
            return None
        
        gene_list = "#Genes\n" + "\n".join(genes)
        client = await self._get_client()
        
        try:
            response = await client.post(
                f"{REACTOME_ANALYSIS_URL}/identifiers/projection/",
                data=gene_list,
                headers={"Content-Type": "text/plain"},
                params={"pageSize": 100, "page": 1}
            )
            response.raise_for_status()
            result = response.json()
            
            token = result.get("summary", {}).get("token", "")
            
            logger.info(f"Reactome analysis token: {token}, mapping {len(genes)} genes to pathways...")
            
            pathway_to_genes = await self.map_gene_to_pathways_batch(genes, batch_size=20)
            
            logger.info(f"Mapped {len(pathway_to_genes)} pathways to genes")
            
            pathway_st_ids = [p.get("stId", "") for p in result.get("pathways", [])]
            
            semaphore = asyncio.Semaphore(10)
            
            async def fetch_details(st_id: str):
                async with semaphore:
                    return await self.get_pathway_type_and_compartments(st_id)
            
            details_tasks = [fetch_details(st_id) for st_id in pathway_st_ids if st_id]
            details_results = await asyncio.gather(*details_tasks, return_exceptions=True)
            
            pathway_details_map = {}
            for i, st_id in enumerate(pathway_st_ids):
                if st_id and i < len(details_results):
                    result_item = details_results[i]
                    if not isinstance(result_item, Exception):
                        pathway_details_map[st_id] = result_item
            
            pathways = []
            for pathway_data in result.get("pathways", []):
                st_id = pathway_data.get("stId", "")
                mapped = pathway_to_genes.get(st_id, [])
                
                pathway_type, compartments = pathway_details_map.get(st_id, ("Pathway", []))
                
                pathways.append(PathwayResult(
                    st_id=st_id,
                    name=pathway_data.get("name", ""),
                    p_value=pathway_data.get("entities", {}).get("pValue", 1.0),
                    fdr=pathway_data.get("entities", {}).get("fdr", 1.0),
                    entities_count=pathway_data.get("entities", {}).get("count", 0),
                    entities_found=pathway_data.get("entities", {}).get("found", 0),
                    entities_ratio=pathway_data.get("entities", {}).get("ratio", 0.0),
                    species=pathway_data.get("species", {}).get("displayName", "Homo sapiens"),
                    mapped_genes=mapped,
                    pathway_type= pathway_type,
                    compartments=compartments
                ))
            
            genes_not_found = result.get("identifiersNotFound", 0)
            
            pathways_with_genes = [p for p in pathways if p.mapped_genes]
            logger.info(f"Pathways with mapped genes: {len(pathways_with_genes)}/{len(pathways)}")
            
            return PathwayAnalysisResult(
                token=token,
                pathways=pathways,
                genes_not_found=genes_not_found,
                summary=result.get("summary", {})
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Reactome analysis HTTP error: {e.response.status_code}")
            return None
        except httpx.ConnectError as e:
            logger.error(f"Reactome connection failed: {e}")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"Reactome analysis timeout: {e}")
            return None
        except Exception as e:
            logger.error(f"Reactome analysis unexpected error: {type(e).__name__}: {e}")
            return None

    async def get_pathway_details(self, st_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a pathway.
        
        Args:
            st_id: Reactome stable identifier (e.g., "R-HSA-123456")
        
        Returns:
            Pathway details dictionary or None
        """
        client = await self._get_client()
        try:
            response = await client.get(
                f"{REACTOME_CONTENT_URL}/data/query/{st_id}",
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            data = response.json()
            
            # Handle case where Reactome API returns a list instead of a dict
            # The /data/query endpoint can return either:
            # - A single entity (dict) - expected for unique identifiers
            # - A list of entities - when multiple matches exist
            if isinstance(data, list):
                if len(data) == 0:
                    return None
                # Return the first (and typically only) matching result
                # Log if multiple results found for awareness
                if len(data) > 1:
                    logger.warning(f"Reactome returned {len(data)} results for {st_id}, using first result")
                return data[0]
            
            return data
            
        except Exception as e:
            logger.error(f"Reactome pathway query error: {type(e).__name__}: {e}")
            return None

    async def get_pathway_participants(self, st_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get participating molecules in a pathway.
        
        Args:
            st_id: Reactome stable identifier
        
        Returns:
            List of participating entities
        """
        client = await self._get_client()
        try:
            response = await client.get(
                f"{REACTOME_CONTENT_URL}/data/event/{st_id}/participatingPhysicalEntities",
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 404:
                return []
                
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Reactome participants query error: {type(e).__name__}: {e}")
            return []

    async def get_analysis_result(self, token: str, page: int = 1, page_size: int = 50) -> Optional[Dict[str, Any]]:
        """
        Retrieve previous analysis result by token.
        
        Args:
            token: Analysis token from previous analysis
            page: Page number
            page_size: Results per page
        
        Returns:
            Analysis result dictionary
        """
        client = await self._get_client()
        try:
            response = await client.get(
                f"{REACTOME_ANALYSIS_URL}/token/{token}",
                params={"page": page, "pageSize": page_size}
            )
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Reactome token query error: {type(e).__name__}: {e}")
            return None


reactome_service = ReactomeService()
