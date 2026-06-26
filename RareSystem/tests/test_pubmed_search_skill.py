"""
Unit tests for PubMed Search Skill.

Tests:
- Skill metadata
- NCBI config missing handling
- LLM fallback behavior
- No results handling
- Cache integration
- Reference building
"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from services.skill_base import SkillContext, SkillResult
from services.skills.pubmed_search_skill import PubMedSearchSkill
from services.pubmed_service import PubMedArticle, PubMedSearchResult
from services.rag_service import ChatReference


class TestPubMedSearchSkillMetadata:
    """Test skill metadata is correctly defined."""
    
    def test_skill_name(self):
        skill = PubMedSearchSkill()
        assert skill.name == "pubmed_search"
    
    def test_skill_type(self):
        skill = PubMedSearchSkill()
        assert skill.skill_type == "tool_call"
    
    def test_skill_icon(self):
        skill = PubMedSearchSkill()
        assert skill.icon == "search"
    
    def test_skill_description(self):
        skill = PubMedSearchSkill()
        assert "PubMed" in skill.description
        assert "MEDLINE" in skill.description
    
    def test_skill_input_schema(self):
        skill = PubMedSearchSkill()
        assert "query" in skill.input_schema
        assert "max_results" in skill.input_schema


class TestPubMedSearchSkillMissingConfig:
    """Test handling of missing NCBI configuration."""
    
    def test_missing_ncbi_email(self):
        """Should return error message when NCBI_EMAIL is not set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('NCBI_EMAIL', None)
            os.environ.pop('NCBI_API_KEY', None)
            
            skill = PubMedSearchSkill()
            context = SkillContext(
                query='罕见病遗传诊断',
                patient_id=1,
                db_session=None,
                llm_client=None
            )
            result = skill.execute(context)
            
            assert result.confidence == 0.0
            assert 'NCBI' in result.content or '配置' in result.content
            assert result.metadata.get('error') == 'missing_ncbi_config'


class TestPubMedSearchSkillLLMFallback:
    """Test LLM fallback behavior."""
    
    def test_no_llm_client_for_query_decomposition(self):
        """Should use original query when LLM client is not available."""
        skill = PubMedSearchSkill()
        
        # Mock the internal methods to avoid actual PubMed calls
        with patch.object(skill, '_missing_config_result') as mock_missing:
            mock_missing.return_value = SkillResult(
                content="test",
                references=[],
                confidence=0.5
            )
            
            # This will hit the missing config check first
            with patch.dict(os.environ, {'NCBI_EMAIL': 'test@example.com'}):
                # Create mock PubMed service that returns empty results
                with patch('services.skills.pubmed_search_skill.create_pubmed_service') as mock_service:
                    mock_pubmed = Mock()
                    mock_pubmed.search_and_fetch.return_value = PubMedSearchResult(
                        articles=[],
                        total_count=0,
                        query_used='test'
                    )
                    mock_service.return_value = mock_pubmed
                    
                    context = SkillContext(
                        query='test query',
                        patient_id=1,
                        db_session=None,
                        llm_client=None
                    )
                    result = skill.execute(context)
                    
                    # Should use original query since LLM is not available
                    assert result.metadata.get('query_used') == 'test query'


class TestPubMedSearchSkillNoResults:
    """Test handling of no search results."""
    
    def test_no_results_message(self):
        """Should return appropriate message when no results found."""
        skill = PubMedSearchSkill()
        
        with patch.dict(os.environ, {'NCBI_EMAIL': 'test@example.com'}):
            with patch('services.skills.pubmed_search_skill.create_pubmed_service') as mock_service:
                mock_pubmed = Mock()
                mock_pubmed.search_and_fetch.return_value = PubMedSearchResult(
                    articles=[],
                    total_count=0,
                    query_used='nonexistent query xyz'
                )
                mock_service.return_value = mock_pubmed
                
                with patch('services.skills.pubmed_search_skill.create_pubmed_cache') as mock_cache:
                    mock_cache_obj = Mock()
                    mock_cache_obj.get.return_value = None
                    mock_cache.return_value = mock_cache_obj
                    
                    context = SkillContext(
                        query='nonexistent query xyz',
                        patient_id=1,
                        db_session=None,
                        llm_client=None
                    )
                    result = skill.execute(context)
                    
                    assert '未找到' in result.content or 'No' in result.content
                    assert result.confidence < 0.5


class TestPubMedSearchSkillCacheHit:
    """Test cache hit behavior."""
    
    def test_cache_hit_skips_api_call(self):
        """Should skip PubMed API call when cache hit."""
        skill = PubMedSearchSkill()
        
        cached_result = PubMedSearchResult(
            articles=[
                PubMedArticle(pmid='12345', title='Test Article', abstract='Test abstract')
            ],
            total_count=1,
            query_used='test query'
        )
        
        with patch.dict(os.environ, {'NCBI_EMAIL': 'test@example.com'}):
            with patch('services.skills.pubmed_search_skill.create_pubmed_service') as mock_service:
                mock_pubmed = Mock()
                mock_service.return_value = mock_pubmed
                
                with patch('services.skills.pubmed_search_skill.create_pubmed_cache') as mock_cache:
                    mock_cache_obj = Mock()
                    mock_cache_obj.get.return_value = cached_result
                    mock_cache.return_value = mock_cache_obj
                    
                    context = SkillContext(
                        query='test query',
                        patient_id=1,
                        db_session=None,
                        llm_client=None
                    )
                    result = skill.execute(context)
                    
                    # Should use cached result, not call API
                    mock_pubmed.search_and_fetch.assert_not_called()
                    assert result.metadata.get('from_cache') == True
                    assert '12345' in result.content


class TestPubMedSearchSkillBuildReferences:
    """Test reference building."""
    
    def test_build_references(self):
        """Should build ChatReference list from articles."""
        skill = PubMedSearchSkill()
        
        articles = [
            PubMedArticle(
                pmid='12345',
                title='Test Article 1',
                authors=['Smith J'],
                journal='Nature',
                year='2024',
                abstract='Abstract 1'
            ),
            PubMedArticle(
                pmid='67890',
                title='Test Article 2',
                authors=['Lee K'],
                journal='Science',
                year='2023',
                abstract='Abstract 2'
            ),
        ]
        
        refs = skill._build_references(articles)
        
        assert len(refs) == 2
        assert refs[0].reference_id == '12345'
        assert refs[0].reference_type == 'pubmed'
        assert refs[1].reference_id == '67890'
    
    def test_build_references_limit(self):
        """Should limit references to 10."""
        skill = PubMedSearchSkill()
        
        articles = [
            PubMedArticle(pmid=str(i), title=f'Article {i}')
            for i in range(20)
        ]
        
        refs = skill._build_references(articles)
        
        assert len(refs) == 10


class TestPubMedSearchSkillConfidence:
    """Test confidence calculation."""
    
    def test_confidence_no_results(self):
        skill = PubMedSearchSkill()
        assert skill._calculate_confidence(0, 0) == 0.1
    
    def test_confidence_few_results(self):
        skill = PubMedSearchSkill()
        assert skill._calculate_confidence(3, 3) == 0.4
    
    def test_confidence_moderate_results(self):
        skill = PubMedSearchSkill()
        assert skill._calculate_confidence(15, 15) == 0.6
    
    def test_confidence_many_results(self):
        skill = PubMedSearchSkill()
        assert skill._calculate_confidence(40, 40) == 0.75
    
    def test_confidence_very_many_results(self):
        skill = PubMedSearchSkill()
        assert skill._calculate_confidence(100, 500) == 0.85


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
