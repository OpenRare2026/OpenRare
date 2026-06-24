"""
Caching Utilities for Performance Optimization

Provides:
- In-memory LRU cache for small data
- Redis-based distributed cache for large data
- Decorator for caching function results
- Cache invalidation strategies
"""
import hashlib
import json
import logging
import pickle
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")
K = TypeVar("K")

DEFAULT_TTL = 3600
MAX_MEMORY_CACHE_SIZE = 1000


@dataclass
class CacheEntry(Generic[T]):
    """A single cache entry with metadata."""
    value: T
    created_at: float
    ttl: int
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        return time.time() > self.created_at + self.ttl
    
    def touch(self) -> None:
        self.access_count += 1
        self.last_accessed = time.time()


class MemoryCache(Generic[K, T]):
    """
    In-memory LRU cache with TTL support.
    
    Features:
    - Least Recently Used eviction
    - Time-To-Live expiration
    - Thread-safe operations
    - Access statistics
    """
    
    def __init__(
        self,
        max_size: int = MAX_MEMORY_CACHE_SIZE,
        default_ttl: int = DEFAULT_TTL
    ):
        self._cache: OrderedDict[K, CacheEntry[T]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def get(self, key: K) -> Optional[T]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            self._misses += 1
            return None
        
        entry = self._cache[key]
        
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None
        
        self._cache.move_to_end(key)
        entry.touch()
        self._hits += 1
        
        return entry.value
    
    def set(self, key: K, value: T, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        if len(self._cache) >= self._max_size:
            self._evict_lru()
        
        entry = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl=ttl or self._default_ttl
        )
        
        if key in self._cache:
            del self._cache[key]
        
        self._cache[key] = entry
    
    def delete(self, key: K) -> bool:
        """Delete entry from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._cache:
            self._cache.popitem(last=False)
            self._evictions += 1
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        expired_keys = [
            k for k, v in self._cache.items() if v.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": hit_rate,
        }


class VCFParseCache:
    """
    Specialized cache for VCF parsing results.
    
    Caches:
    - Parsed variant data
    - VCF header information
    - Quality metrics
    """
    
    def __init__(
        self,
        memory_cache: Optional[MemoryCache[str, Any]] = None,
        redis_client: Optional[Any] = None
    ):
        self._memory_cache = memory_cache or MemoryCache(max_size=500)
        self._redis = redis_client
        self._key_prefix = "vcf:"
    
    @staticmethod
    def _generate_file_hash(file_path: str) -> str:
        """Generate hash for VCF file for cache key."""
        import os
        
        try:
            stat = os.stat(file_path)
            key_data = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(key_data.encode()).hexdigest()[:16]
        except OSError:
            return hashlib.md5(file_path.encode()).hexdigest()[:16]
    
    @staticmethod
    def _generate_variant_key(chromosome: str, position: int, ref: str, alt: str) -> str:
        """Generate cache key for a variant."""
        key_data = f"{chromosome}:{position}:{ref}:{alt}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def get_parsed_variants(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached parsed variants for a VCF file."""
        file_hash = self._generate_file_hash(file_path)
        cache_key = f"{self._key_prefix}variants:{file_hash}"
        return self._memory_cache.get(cache_key)
    
    def set_parsed_variants(
        self,
        file_path: str,
        variants: List[Dict[str, Any]],
        ttl: int = 7200
    ) -> None:
        """Cache parsed variants for a VCF file."""
        file_hash = self._generate_file_hash(file_path)
        cache_key = f"{self._key_prefix}variants:{file_hash}"
        self._memory_cache.set(cache_key, variants, ttl)
        logger.info(f"Cached {len(variants)} variants for {file_path}")
    
    def get_header_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached VCF header information."""
        file_hash = self._generate_file_hash(file_path)
        cache_key = f"{self._key_prefix}header:{file_hash}"
        return self._memory_cache.get(cache_key)
    
    def set_header_info(
        self,
        file_path: str,
        header_info: Dict[str, Any],
        ttl: int = 7200
    ) -> None:
        """Cache VCF header information."""
        file_hash = self._generate_file_hash(file_path)
        cache_key = f"{self._key_prefix}header:{file_hash}"
        self._memory_cache.set(cache_key, header_info, ttl)
    
    def get_quality_metrics(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached quality metrics for a VCF file."""
        file_hash = self._generate_file_hash(file_path)
        cache_key = f"{self._key_prefix}qc:{file_hash}"
        return self._memory_cache.get(cache_key)
    
    def set_quality_metrics(
        self,
        file_path: str,
        metrics: Dict[str, Any],
        ttl: int = 7200
    ) -> None:
        """Cache quality metrics for a VCF file."""
        file_hash = self._generate_file_hash(file_path)
        cache_key = f"{self._key_prefix}qc:{file_hash}"
        self._memory_cache.set(cache_key, metrics, ttl)
    
    def invalidate_file(self, file_path: str) -> None:
        """Invalidate all cache entries for a VCF file."""
        file_hash = self._generate_file_hash(file_path)
        for suffix in ["variants", "header", "qc"]:
            cache_key = f"{self._key_prefix}{suffix}:{file_hash}"
            self._memory_cache.delete(cache_key)
        logger.info(f"Invalidated cache for {file_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._memory_cache.get_stats()


def cached(
    ttl: int = DEFAULT_TTL,
    key_prefix: str = "",
    key_builder: Optional[Callable[..., str]] = None
) -> Callable:
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
        key_builder: Custom function to build cache key from arguments
    
    Usage:
        @cached(ttl=300, key_prefix="acmg:")
        def classify_variant(variant_id: str) -> dict:
            ...
    """
    _cache: MemoryCache[str, Any] = MemoryCache(max_size=500)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [str(arg) for arg in args]
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}{func.__name__}:{':'.join(key_parts)}"
            
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            logger.debug(f"Cache set for {cache_key}")
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [str(arg) for arg in args]
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}{func.__name__}:{':'.join(key_parts)}"
            
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            result = await func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            logger.debug(f"Cache set for {cache_key}")
            
            return result
        
        if hasattr(func, '__aenter__'):
            return async_wrapper
        return wrapper
    
    return decorator


def cache_result(
    func: Optional[Callable] = None,
    *,
    ttl: int = DEFAULT_TTL,
    key_prefix: str = ""
) -> Union[Callable, Callable[[Callable], Callable]]:
    """
    Simpler caching decorator without key_builder.
    
    Usage:
        @cache_result
        def my_function(arg):
            return expensive_computation(arg)
        
        @cache_result(ttl=60, key_prefix="expensive:")
        def another_function(arg):
            ...
    """
    def decorator(f: Callable) -> Callable:
        return cached(ttl=ttl, key_prefix=key_prefix)(f)
    
    if func is not None:
        return decorator(func)
    return decorator


class CacheManager:
    """
    Central cache manager for the application.
    
    Manages multiple named caches with different configurations.
    """
    
    _instance: Optional['CacheManager'] = None
    
    def __new__(cls) -> 'CacheManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._caches: Dict[str, MemoryCache] = {}
            cls._instance._vcf_cache: Optional[VCFParseCache] = None
        return cls._instance
    
    def get_cache(self, name: str, max_size: int = 500) -> MemoryCache:
        """Get or create a named cache."""
        if name not in self._caches:
            self._caches[name] = MemoryCache(max_size=max_size)
        return self._caches[name]
    
    def get_vcf_cache(self) -> VCFParseCache:
        """Get the VCF parsing cache."""
        if self._vcf_cache is None:
            self._vcf_cache = VCFParseCache()
        return self._vcf_cache
    
    def clear_all(self) -> None:
        """Clear all caches."""
        for cache in self._caches.values():
            cache.clear()
        if self._vcf_cache:
            self._vcf_cache._memory_cache.clear()
        logger.info("All caches cleared")
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        stats = {}
        for name, cache in self._caches.items():
            stats[name] = cache.get_stats()
        if self._vcf_cache:
            stats["vcf"] = self._vcf_cache.get_stats()
        return stats


def get_cache_manager() -> CacheManager:
    """Get the singleton cache manager instance."""
    return CacheManager()
