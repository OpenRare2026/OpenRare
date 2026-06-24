"""
PubMed Cache - File-based cache for PubMed query results.

Provides caching for PubMedSearchResult objects to reduce NCBI API calls.
Uses MD5 hash of query parameters as cache key with configurable TTL.
"""
import json
import logging
import os
import time
import hashlib
from pathlib import Path
from typing import Optional, List

from services.pubmed_service import PubMedArticle, PubMedSearchResult


logger = logging.getLogger(__name__)

# Default cache directory relative to this file
DEFAULT_CACHE_DIR = Path(__file__).parent.parent / ".pubmed_cache"
DEFAULT_CACHE_TTL = 86400  # 24 hours in seconds


class PubMedCache:
    """
    File-based cache for PubMed search results.
    
    Stores PubMedSearchResult objects as JSON files with TTL-based expiration.
    Cache key is MD5 hash of (query + max_results + sort) to ensure unique keys.
    
    Attributes:
        cache_dir: Directory for cache files
        cache_ttl: Time-to-live in seconds (default 24 hours)
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        cache_ttl: int = DEFAULT_CACHE_TTL
    ):
        """
        Initialize PubMed cache.
        
        Args:
            cache_dir: Directory for cache files (default: backend/.pubmed_cache/)
            cache_ttl: Cache TTL in seconds (default: 86400 = 24 hours)
        """
        self._cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self._cache_ttl = cache_ttl
        
        # Create cache directory if not exists
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"PubMedCache initialized: dir={self._cache_dir}, ttl={self._cache_ttl}s")
    
    def get(
        self,
        query: str,
        max_results: int,
        sort: str
    ) -> Optional[PubMedSearchResult]:
        """
        Retrieve cached search result.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results
            sort: Sort order ("relevance" or "date")
            
        Returns:
            PubMedSearchResult if cache hit and not expired, None otherwise
        """
        cache_key = self._make_key(query, max_results, sort)
        cache_file = self._cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            logger.debug(f"PubMed cache miss: query='{query[:50]}...'")
            return None
        
        # Check expiration
        if self._is_expired(cache_file):
            logger.debug(f"PubMed cache expired: query='{query[:50]}...'")
            try:
                cache_file.unlink()
            except OSError:
                pass
            return None
        
        # Load from cache
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            result = self._deserialize(data)
            logger.info(f"PubMed cache hit: query='{query[:50]}...', articles={len(result.articles)}")
            return result
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"PubMed cache read error: {e}")
            try:
                cache_file.unlink()
            except OSError:
                pass
            return None
    
    def set(
        self,
        query: str,
        max_results: int,
        sort: str,
        result: PubMedSearchResult
    ) -> None:
        """
        Store search result in cache.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results
            sort: Sort order
            result: PubMedSearchResult to cache
        """
        cache_key = self._make_key(query, max_results, sort)
        cache_file = self._cache_dir / f"{cache_key}.json"
        
        try:
            data = self._serialize(result)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"PubMed cache set: query='{query[:50]}...', articles={len(result.articles)}")
            
        except (IOError, TypeError) as e:
            logger.warning(f"PubMed cache write error: {e}")
    
    def clear(self) -> None:
        """
        Clear all cached results.
        """
        cleared_count = 0
        try:
            for cache_file in self._cache_dir.glob("*.json"):
                cache_file.unlink()
                cleared_count += 1
            logger.info(f"PubMed cache cleared: {cleared_count} files removed")
        except OSError as e:
            logger.warning(f"PubMed cache clear error: {e}")
    
    def _make_key(self, query: str, max_results: int, sort: str) -> str:
        """
        Generate cache key from query parameters.
        
        Uses MD5 hash of normalized parameters.
        """
        key_string = f"{query}|{max_results}|{sort}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def _is_expired(self, cache_file: Path) -> bool:
        """
        Check if cache file has expired based on TTL.
        """
        if self._cache_ttl <= 0:
            return True
        
        try:
            file_mtime = cache_file.stat().st_mtime
            age = time.time() - file_mtime
            return age > self._cache_ttl
        except OSError:
            return True
    
    def _serialize(self, result: PubMedSearchResult) -> dict:
        """
        Serialize PubMedSearchResult to JSON-compatible dict.
        """
        return {
            "articles": [
                {
                    "pmid": article.pmid,
                    "title": article.title,
                    "authors": article.authors,
                    "journal": article.journal,
                    "year": article.year,
                    "abstract": article.abstract,
                    "url": article.url,
                    "doi": article.doi,
                }
                for article in result.articles
            ],
            "total_count": result.total_count,
            "query_used": result.query_used,
        }
    
    def _deserialize(self, data: dict) -> PubMedSearchResult:
        """
        Deserialize dict to PubMedSearchResult.
        """
        articles = [
            PubMedArticle(
                pmid=article_data["pmid"],
                title=article_data["title"],
                authors=article_data.get("authors", []),
                journal=article_data.get("journal", ""),
                year=article_data.get("year", ""),
                abstract=article_data.get("abstract", ""),
                url=article_data.get("url", ""),
                doi=article_data.get("doi", ""),
            )
            for article_data in data["articles"]
        ]
        
        return PubMedSearchResult(
            articles=articles,
            total_count=data.get("total_count", 0),
            query_used=data.get("query_used", ""),
        )


def create_pubmed_cache(
    cache_dir: Optional[str] = None,
    cache_ttl: int = DEFAULT_CACHE_TTL
) -> PubMedCache:
    """
    Factory function to create PubMedCache instance.
    """
    return PubMedCache(cache_dir=cache_dir, cache_ttl=cache_ttl)
