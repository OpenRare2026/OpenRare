"""
PubMed API endpoints for literature search.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.pubmed_service import (
    PubMedService,
    PubMedArticle,
    PubMedServiceError,
    create_pubmed_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pubmed", tags=["pubmed"])


class PubMedArticleResponse(BaseModel):
    pmid: str
    title: str
    authors: List[str] = []
    journal: str = ""
    year: str = ""
    abstract: str = ""
    url: str = ""
    doi: str = ""


class PubMedSearchResponse(BaseModel):
    articles: List[PubMedArticleResponse]
    total_count: int
    query: str


@router.get("/search", response_model=PubMedSearchResponse)
async def search_pubmed(
    query: str = Query(..., min_length=1, description="PubMed search query"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    include_abstracts: bool = Query(True, description="Include article abstracts"),
):
    """
    Search PubMed for articles related to a query.
    
    Returns article details including:
    - PMID
    - Title
    - Authors
    - Journal
    - Year
    - Abstract (if include_abstracts=true)
    - URL to PubMed
    - DOI (if available)
    """
    try:
        service = create_pubmed_service()
        result = service.search_and_fetch(
            query=query,
            max_results=max_results,
            include_abstracts=include_abstracts,
        )
        
        articles = [
            PubMedArticleResponse(
                pmid=article.pmid,
                title=article.title,
                authors=article.authors,
                journal=article.journal,
                year=article.year,
                abstract=article.abstract,
                url=article.url,
                doi=article.doi,
            )
            for article in result.articles
        ]
        
        return PubMedSearchResponse(
            articles=articles,
            total_count=result.total_count,
            query=result.query_used,
        )
        
    except PubMedServiceError as e:
        logger.error(f"PubMed search error: {e}")
        raise HTTPException(status_code=503, detail=f"PubMed service error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during PubMed search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
