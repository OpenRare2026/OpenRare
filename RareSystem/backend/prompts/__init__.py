"""
LLM Prompt Templates - Centralized Configuration

This module provides a unified location for all LLM prompts used in the system.
Each prompt is documented with its purpose and usage context.

Prompt Categories:
1. RAG Prompts - Case Q&A and document retrieval
2. Skill Prompts - Specialized analysis tasks
3. PubMed Prompts - Literature search and synthesis
"""

from .rag_prompts import (
    RAG_SYSTEM_PROMPT,
    RAG_CONTEXT_TEMPLATE,
    build_rag_prompt,
)
from .skill_prompts import (
    ACMG_CLASSIFICATION_PROMPT,
    PHENOTYPE_MATCHING_PROMPT,
    PEDIGREE_ANALYSIS_PROMPT,
)
from .pubmed_prompts import (
    QUERY_DECOMPOSITION_PROMPT,
    ANSWER_SYNTHESIS_PROMPT,
    parse_decomposition_response,
    build_abstract_context,
)

__all__ = [
    # RAG Prompts
    "RAG_SYSTEM_PROMPT",
    "RAG_CONTEXT_TEMPLATE",
    "build_rag_prompt",
    # Skill Prompts
    "ACMG_CLASSIFICATION_PROMPT",
    "PHENOTYPE_MATCHING_PROMPT",
    "PEDIGREE_ANALYSIS_PROMPT",
    # PubMed Prompts
    "QUERY_DECOMPOSITION_PROMPT",
    "ANSWER_SYNTHESIS_PROMPT",
    "parse_decomposition_response",
    "build_abstract_context",
]
