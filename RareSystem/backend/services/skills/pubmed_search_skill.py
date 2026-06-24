"""
PubMed Search Skill - PubMed literature retrieval with LLM-based query decomposition.

This skill provides:
1. LLM-driven query decomposition (Chinese → English + MeSH terms)
2. PubMed search via E-utilities API
3. LLM-based answer synthesis with PMID citations
4. File-based caching to reduce API calls

Configuration:
- ncbi_email: NCBI account email (required by NCBI for identification)
- ncbi_api_key: NCBI API key (optional, enables 10 req/sec vs 3 req/sec)

Config can be set via:
1. Settings API: PUT /api/skills/config/pubmed_search
2. Environment variables: NCBI_EMAIL, NCBI_API_KEY (fallback)
"""
import os
import logging
from typing import List, Optional, Any, Dict

from services.skill_base import Skill, SkillContext, SkillResult
from services.rag_service import ChatReference
from services.pubmed_service import (
    PubMedService,
    PubMedSearchResult,
    PubMedArticle,
    PubMedServiceError,
    PubMedSearchError,
    PubMedRateLimitError,
    create_pubmed_service,
)
from services.pubmed_cache import PubMedCache, create_pubmed_cache
from services.skills.prompts.pubmed_prompts import (
    QUERY_DECOMPOSITION_PROMPT,
    ANSWER_SYNTHESIS_PROMPT,
    parse_decomposition_response,
    build_abstract_context,
    format_user_query_with_context,
)


logger = logging.getLogger(__name__)

DEFAULT_MAX_RESULTS = 100
DEFAULT_CACHE_TTL_HOURS = 24
DEFAULT_LLM_TEMPERATURE = 0.3
DEFAULT_LLM_MAX_TOKENS = 2000


class PubMedSearchSkill(Skill):
    """
    PubMed literature search skill with LLM-based query processing.
    
    Features:
    - Translates Chinese queries to English PubMed queries with MeSH terms
    - Retrieves up to 100 abstracts from PubMed
    - Generates citation-based answers in Chinese
    - Caches results to reduce API calls
    
    All parameters configurable via Settings API.
    """
    
    name = "pubmed_search"
    description = "PubMed 文献检索 - 搜索 MEDLINE 数据库获取罕见病遗传诊断相关文献摘要，生成循证回答"
    skill_type = "tool_call"
    icon = "search"
    input_schema = {
        "query": "str - 搜索关键词或医学问题（支持中文）",
        "max_results": "int - 最大检索数量（默认100）"
    }
    config_schema = {
        "ncbi_email": {
            "type": "string",
            "label": "NCBI 邮箱",
            "description": "NCBI 账户邮箱，用于 PubMed API 身份标识",
            "placeholder": "your-email@example.com",
            "required": True,
            "group": "credentials",
            "group_label": "NCBI 凭证"
        },
        "ncbi_api_key": {
            "type": "string",
            "label": "NCBI API Key",
            "description": "NCBI API 密钥，启用后访问频率从 3次/秒 提升到 10次/秒",
            "placeholder": "从 https://www.ncbi.nlm.nih.gov/account/settings/ 获取",
            "required": False,
            "group": "credentials",
            "group_label": "NCBI 凭证"
        },
        "max_results": {
            "type": "integer",
            "label": "最大检索数量",
            "description": "每次搜索返回的最大文献数量",
            "default": 100,
            "min": 10,
            "max": 500,
            "group": "search",
            "group_label": "搜索参数"
        },
        "sort_order": {
            "type": "select",
            "label": "排序方式",
            "description": "PubMed 搜索结果的排序方式",
            "default": "relevance",
            "options": [
                {"value": "relevance", "label": "相关度"},
                {"value": "pub_date", "label": "发表日期"}
            ],
            "group": "search",
            "group_label": "搜索参数"
        },
        "cache_ttl_hours": {
            "type": "integer",
            "label": "缓存有效期（小时）",
            "description": "搜索结果的本地缓存时间",
            "default": 24,
            "min": 1,
            "max": 168,
            "group": "cache",
            "group_label": "缓存设置"
        },
        "query_decomposition_prompt": {
            "type": "textarea",
            "label": "查询分解 Prompt",
            "description": "用于将用户问题分解为 PubMed 搜索词的 Prompt 模板",
            "default": "default",
            "rows": 8,
            "group": "prompts",
            "group_label": "Prompt 模板"
        },
        "answer_synthesis_prompt": {
            "type": "textarea",
            "label": "回答合成 Prompt",
            "description": "用于根据文献摘要生成回答的 Prompt 模板",
            "default": "default",
            "rows": 8,
            "group": "prompts",
            "group_label": "Prompt 模板"
        },
        "llm_temperature": {
            "type": "float",
            "label": "LLM 温度",
            "description": "控制回答的随机性，值越低越确定",
            "default": 0.3,
            "min": 0.0,
            "max": 1.0,
            "step": 0.1,
            "group": "llm",
            "group_label": "LLM 参数"
        },
        "llm_max_tokens": {
            "type": "integer",
            "label": "LLM 最大 Token 数",
            "description": "LLM 生成的最大 token 数量",
            "default": 2000,
            "min": 500,
            "max": 8000,
            "group": "llm",
            "group_label": "LLM 参数"
        }
    }
    
    def execute(self, context: SkillContext) -> SkillResult:
        config = self._get_config(context)
        
        if not config["ncbi_email"]:
            return self._missing_config_result()
        
        pubmed_service = create_pubmed_service(
            email=config["ncbi_email"],
            api_key=config["ncbi_api_key"]
        )
        cache = create_pubmed_cache()
        
        max_results = config["max_results"]
        sort_order = config["sort_order"]
        
        pubmed_query = self._decompose_query(
            context.query,
            context.llm_client,
            config["query_decomposition_prompt"],
            config["llm_temperature"],
            config["llm_max_tokens"]
        )
        
        cached_result = cache.get(pubmed_query, max_results, sort_order)
        if cached_result:
            logger.info(f"Using cached PubMed result for query: {pubmed_query[:50]}")
            articles = cached_result.articles
            total_count = cached_result.total_count
            from_cache = True
        else:
            try:
                search_result = pubmed_service.search_and_fetch(
                    query=pubmed_query,
                    max_results=max_results,
                    sort=sort_order,
                    include_abstracts=True
                )
                articles = search_result.articles
                total_count = search_result.total_count
                
                cache.set(pubmed_query, max_results, sort_order, search_result)
                from_cache = False
                
            except PubMedRateLimitError as e:
                return self._rate_limit_result(str(e))
            except PubMedSearchError as e:
                return self._search_error_result(str(e))
            except PubMedServiceError as e:
                return self._service_error_result(str(e))
        
        if not articles:
            return self._no_results_result(context.query, pubmed_query)
        
        content = self._synthesize_answer(
            context.query,
            articles,
            context.llm_client,
            config["answer_synthesis_prompt"],
            config["llm_temperature"],
            config["llm_max_tokens"]
        )
        
        references = self._build_references(articles)
        confidence = self._calculate_confidence(len(articles), total_count)
        
        return SkillResult(
            content=content,
            references=references,
            confidence=confidence,
            metadata={
                "skill": self.name,
                "query_used": pubmed_query,
                "total_results": total_count,
                "articles_fetched": len(articles),
                "from_cache": from_cache,
            }
        )
    
    def _get_config(self, context: SkillContext) -> Dict[str, Any]:
        db_config = {}
        
        if context.db_session:
            try:
                from database.case_models import SkillConfig
                config_record = context.db_session.query(SkillConfig).filter(
                    SkillConfig.skill_name == self.name
                ).first()
                
                if config_record is not None and config_record.config is not None:
                    db_config = config_record.config
                    logger.debug(f"Loaded config from SkillConfig")
            except Exception as e:
                logger.warning(f"Failed to load SkillConfig: {e}")
        
        return {
            "ncbi_email": db_config.get("ncbi_email") or os.getenv("NCBI_EMAIL", ""),
            "ncbi_api_key": db_config.get("ncbi_api_key") or os.getenv("NCBI_API_KEY", ""),
            "max_results": db_config.get("max_results", DEFAULT_MAX_RESULTS),
            "sort_order": db_config.get("sort_order", "relevance"),
            "cache_ttl_hours": db_config.get("cache_ttl_hours", DEFAULT_CACHE_TTL_HOURS),
            "query_decomposition_prompt": db_config.get("query_decomposition_prompt") or QUERY_DECOMPOSITION_PROMPT,
            "answer_synthesis_prompt": db_config.get("answer_synthesis_prompt") or ANSWER_SYNTHESIS_PROMPT,
            "llm_temperature": db_config.get("llm_temperature", DEFAULT_LLM_TEMPERATURE),
            "llm_max_tokens": db_config.get("llm_max_tokens", DEFAULT_LLM_MAX_TOKENS),
        }
    
    def _decompose_query(
        self,
        user_query: str,
        llm_client: Optional[Any],
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        if not llm_client:
            logger.info("No LLM client available, using direct query")
            return user_query
        
        try:
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_query}
            ]
            
            response = llm_client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            parsed = parse_decomposition_response(response.content)
            pubmed_query = parsed.get("pubmed_query", user_query)
            
            logger.info(f"Query decomposed: '{user_query[:30]}...' -> '{pubmed_query[:50]}...'")
            return pubmed_query
            
        except Exception as e:
            logger.warning(f"LLM query decomposition failed: {e}, using original query")
            return user_query
    
    def _synthesize_answer(
        self,
        user_query: str,
        articles: List[PubMedArticle],
        llm_client: Optional[Any],
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        abstracts_context = build_abstract_context(articles)
        
        if not llm_client:
            logger.info("No LLM client available, returning formatted abstracts")
            return self._format_abstracts_fallback(user_query, articles)
        
        try:
            user_message = format_user_query_with_context(user_query, abstracts_context)
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = llm_client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.content
            
        except Exception as e:
            logger.warning(f"LLM answer synthesis failed: {e}, returning formatted abstracts")
            return self._format_abstracts_fallback(user_query, articles)
    
    def _format_abstracts_fallback(
        self,
        user_query: str,
        articles: List[PubMedArticle]
    ) -> str:
        """
        Format articles as a fallback when LLM is not available.
        """
        parts = [
            f"**PubMed 检索结果** (查询: {user_query})",
            f"共找到 {len(articles)} 篇相关文献\n",
            "=" * 50
        ]
        
        for i, article in enumerate(articles[:20], 1):  # Limit to 20 in fallback
            parts.append(f"\n### {i}. {article.title}")
            parts.append(f"**PMID**: {article.pmid}")
            if article.authors:
                parts.append(f"**作者**: {', '.join(article.authors[:3])}")
            if article.journal:
                parts.append(f"**期刊**: {article.journal}")
            if article.year:
                parts.append(f"**年份**: {article.year}")
            if article.abstract:
                parts.append(f"**摘要**: {article.abstract[:300]}...")
            parts.append(f"**链接**: {article.url}")
        
        if len(articles) > 20:
            parts.append(f"\n... 还有 {len(articles) - 20} 篇文献未显示")
        
        return '\n'.join(parts)
    
    def _build_references(self, articles: List[PubMedArticle]) -> List[ChatReference]:
        """
        Build ChatReference list from articles.
        """
        refs = []
        for article in articles[:10]:  # Limit to 10 references
            refs.append(ChatReference(
                reference_id=article.pmid,
                reference_type="pubmed",
                label=article.title[:50] if article.title else f"Article {article.pmid}",
                url=article.url
            ))
        return refs
    
    def _calculate_confidence(self, articles_count: int, total_count: int) -> float:
        """
        Calculate confidence score based on result count.
        
        Higher count = higher confidence (more evidence available)
        """
        if articles_count == 0:
            return 0.1
        elif articles_count < 5:
            return 0.4
        elif articles_count < 20:
            return 0.6
        elif articles_count < 50:
            return 0.75
        else:
            return 0.85
    
    # -------------------------------------------------------------------------
    # Error handling methods
    # -------------------------------------------------------------------------
    
    def _missing_config_result(self) -> SkillResult:
        """Return result for missing NCBI configuration."""
        return SkillResult(
            content=(
                "⚠️ **PubMed 检索需要配置 NCBI 凭证**\n\n"
                "请配置以下环境变量：\n"
                "1. `NCBI_EMAIL`: 您的邮箱地址（NCBI 要求标识）\n"
                "2. `NCBI_API_KEY`: API 密钥（可选，启用 10 次/秒访问）\n\n"
                "获取 API 密钥：https://www.ncbi.nlm.nih.gov/account/settings/\n\n"
                "配置后请重启服务。"
            ),
            references=[],
            confidence=0.0,
            metadata={"error": "missing_ncbi_config", "skill": self.name}
        )
    
    def _rate_limit_result(self, error_msg: str) -> SkillResult:
        """Return result for rate limit error."""
        return SkillResult(
            content=(
                "⚠️ **PubMed API 访问频率限制**\n\n"
                f"错误信息: {error_msg}\n\n"
                "建议：\n"
                "1. 配置 `NCBI_API_KEY` 可将访问频率从 3次/秒 提升到 10次/秒\n"
                "2. 稍后重试\n\n"
                "获取 API 密钥：https://www.ncbi.nlm.nih.gov/account/settings/"
            ),
            references=[],
            confidence=0.0,
            metadata={"error": "rate_limit", "skill": self.name}
        )
    
    def _search_error_result(self, error_msg: str) -> SkillResult:
        """Return result for search error."""
        return SkillResult(
            content=(
                "⚠️ **PubMed 检索错误**\n\n"
                f"错误信息: {error_msg}\n\n"
                "建议：\n"
                "1. 检查网络连接\n"
                "2. 简化搜索词后重试\n"
                "3. 如问题持续，请联系管理员"
            ),
            references=[],
            confidence=0.0,
            metadata={"error": "search_error", "skill": self.name}
        )
    
    def _service_error_result(self, error_msg: str) -> SkillResult:
        """Return result for general service error."""
        return SkillResult(
            content=(
                "⚠️ **PubMed 服务暂时不可用**\n\n"
                f"错误信息: {error_msg}\n\n"
                "请稍后重试。如问题持续，请联系管理员。"
            ),
            references=[],
            confidence=0.0,
            metadata={"error": "service_error", "skill": self.name}
        )
    
    def _no_results_result(self, user_query: str, pubmed_query: str) -> SkillResult:
        """Return result for no search results."""
        return SkillResult(
            content=(
                f"**未找到相关文献**\n\n"
                f"您的查询: {user_query}\n"
                f"PuBMed 查询: {pubmed_query}\n\n"
                "建议：\n"
                "1. 使用更通用的关键词\n"
                "2. 减少搜索词数量\n"
                "3. 尝试英文关键词\n"
                "4. 检查拼写是否正确"
            ),
            references=[],
            confidence=0.2,
            metadata={"error": "no_results", "skill": self.name, "query_used": pubmed_query}
        )
