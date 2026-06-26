"""
Integration tests for PubMed RAG components.

Tests:
- PubMedCache: read/write/expiration/clear
- PubMed Prompts: template loading, parsing, context formatting
"""
import os
import sys
import json
import time
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from services.pubmed_cache import PubMedCache, create_pubmed_cache
from services.pubmed_service import PubMedArticle, PubMedSearchResult
from services.skills.prompts.pubmed_prompts import (
    QUERY_DECOMPOSITION_PROMPT,
    ANSWER_SYNTHESIS_PROMPT,
    parse_decomposition_response,
    build_abstract_context,
)


class TestPubMedCache:
    """Integration tests for PubMed cache layer."""
    
    def test_cache_roundtrip(self, tmp_path):
        """Test cache write and read roundtrip."""
        cache = PubMedCache(cache_dir=str(tmp_path), cache_ttl=86400)
        
        result = PubMedSearchResult(
            articles=[
                PubMedArticle(
                    pmid='12345',
                    title='Test Article',
                    authors=['Smith J', 'Lee K'],
                    journal='Nature',
                    year='2024',
                    abstract='This is a test abstract.',
                    doi='10.1234/test'
                )
            ],
            total_count=1,
            query_used='test query'
        )
        
        cache.set('test query', 100, 'relevance', result)
        cached = cache.get('test query', 100, 'relevance')
        
        assert cached is not None
        assert cached.total_count == 1
        assert len(cached.articles) == 1
        assert cached.articles[0].pmid == '12345'
        assert cached.articles[0].title == 'Test Article'
        assert cached.articles[0].journal == 'Nature'
    
    def test_cache_expiration(self, tmp_path):
        """Test cache TTL expiration."""
        cache = PubMedCache(cache_dir=str(tmp_path), cache_ttl=0)
        
        result = PubMedSearchResult(
            articles=[PubMedArticle(pmid='12345', title='Test')],
            total_count=1,
            query_used='test'
        )
        
        cache.set('test', 100, 'relevance', result)
        cached = cache.get('test', 100, 'relevance')
        
        assert cached is None
    
    def test_cache_clear(self, tmp_path):
        """Test cache clearing."""
        cache = PubMedCache(cache_dir=str(tmp_path), cache_ttl=86400)
        
        result = PubMedSearchResult(
            articles=[PubMedArticle(pmid='12345', title='Test')],
            total_count=1,
            query_used='test'
        )
        
        cache.set('query1', 100, 'relevance', result)
        cache.set('query2', 100, 'relevance', result)
        
        cache.clear()
        
        assert cache.get('query1', 100, 'relevance') is None
        assert cache.get('query2', 100, 'relevance') is None
    
    def test_cache_different_queries(self, tmp_path):
        """Test that different queries create different cache entries."""
        cache = PubMedCache(cache_dir=str(tmp_path), cache_ttl=86400)
        
        result1 = PubMedSearchResult(
            articles=[PubMedArticle(pmid='11111', title='Article 1')],
            total_count=1,
            query_used='query1'
        )
        result2 = PubMedSearchResult(
            articles=[PubMedArticle(pmid='22222', title='Article 2')],
            total_count=1,
            query_used='query2'
        )
        
        cache.set('query1', 100, 'relevance', result1)
        cache.set('query2', 100, 'relevance', result2)
        
        cached1 = cache.get('query1', 100, 'relevance')
        cached2 = cache.get('query2', 100, 'relevance')
        
        assert cached1.articles[0].pmid == '11111'
        assert cached2.articles[0].pmid == '22222'


class TestPubMedPrompts:
    """Integration tests for PubMed prompt templates."""
    
    def test_query_decomposition_prompt_exists(self):
        """Test query decomposition prompt is defined."""
        assert QUERY_DECOMPOSITION_PROMPT is not None
        assert len(QUERY_DECOMPOSITION_PROMPT) > 100
        assert 'MeSH' in QUERY_DECOMPOSITION_PROMPT or 'mesh' in QUERY_DECOMPOSITION_PROMPT.lower()
        assert 'JSON' in QUERY_DECOMPOSITION_PROMPT
    
    def test_answer_synthesis_prompt_exists(self):
        """Test answer synthesis prompt is defined."""
        assert ANSWER_SYNTHESIS_PROMPT is not None
        assert len(ANSWER_SYNTHESIS_PROMPT) > 100
        assert 'PMID' in ANSWER_SYNTHESIS_PROMPT
        assert 'Citation' in ANSWER_SYNTHESIS_PROMPT or '引用' in ANSWER_SYNTHESIS_PROMPT
    
    def test_parse_decomposition_valid_json(self):
        """Test parsing valid JSON response."""
        response = json.dumps({
            "mesh_terms": ["Neoplasms", "Genetic Predisposition"],
            "keywords": ["cancer", "genetic"],
            "pubmed_query": "Neoplasms[mesh] AND genetic[tiab]",
            "search_strategy": "Combined disease and mechanism"
        })
        
        result = parse_decomposition_response(response)
        
        assert result['pubmed_query'] == "Neoplasms[mesh] AND genetic[tiab]"
        assert len(result['mesh_terms']) == 2
        assert len(result['keywords']) == 2
    
    def test_parse_decomposition_markdown_json(self):
        """Test parsing JSON in markdown code block."""
        response = '''```json
{
  "mesh_terms": ["Diabetes Mellitus"],
  "keywords": ["diabetes"],
  "pubmed_query": "Diabetes Mellitus[mesh]",
  "search_strategy": "Direct MeSH search"
}
```'''
        
        result = parse_decomposition_response(response)
        
        assert result['pubmed_query'] == "Diabetes Mellitus[mesh]"
    
    def test_parse_decomposition_fallback(self):
        """Test fallback for invalid JSON."""
        response = "This is not valid JSON at all"
        
        result = parse_decomposition_response(response)
        
        assert 'pubmed_query' in result
        assert result['pubmed_query'] == response
    
    def test_build_abstract_context_empty(self):
        """Test building context from empty article list."""
        context = build_abstract_context([])
        
        assert '未找到' in context or 'No' in context
    
    def test_build_abstract_context_single(self):
        """Test building context from single article."""
        articles = [
            PubMedArticle(
                pmid='12345',
                title='Test Article Title',
                authors=['Smith J', 'Lee K', 'Wang Z'],
                journal='Nature',
                year='2024',
                abstract='This is a test abstract for the article.',
                doi='10.1234/test'
            )
        ]
        
        context = build_abstract_context(articles)
        
        assert '12345' in context
        assert 'Test Article Title' in context
        assert 'Nature' in context
        assert '2024' in context
        assert 'PMID' in context
    
    def test_build_abstract_context_multiple(self):
        """Test building context from multiple articles."""
        articles = [
            PubMedArticle(pmid='11111', title='Article 1', journal='Journal A'),
            PubMedArticle(pmid='22222', title='Article 2', journal='Journal B'),
            PubMedArticle(pmid='33333', title='Article 3', journal='Journal C'),
        ]
        
        context = build_abstract_context(articles)
        
        assert '11111' in context
        assert '22222' in context
        assert '33333' in context
        assert '3' in context
    
    def test_build_abstract_context_truncation(self):
        """Test that long abstracts are truncated."""
        long_abstract = 'A' * 2000
        articles = [
            PubMedArticle(
                pmid='12345',
                title='Test',
                abstract=long_abstract
            )
        ]
        
        context = build_abstract_context(articles)
        
        assert len(context) < len(long_abstract) + 500


class TestPubMedCacheFactory:
    """Test factory function."""
    
    def test_create_pubmed_cache(self, tmp_path):
        """Test cache factory function."""
        cache = create_pubmed_cache(cache_dir=str(tmp_path), cache_ttl=3600)
        
        assert isinstance(cache, PubMedCache)
        assert cache._cache_ttl == 3600


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
