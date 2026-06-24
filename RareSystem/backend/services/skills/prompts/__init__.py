"""
PubMed RAG skill prompt templates.

This module contains prompt templates for:
- Query decomposition: Converting user questions to PubMed search queries
- Answer synthesis: Generating citation-based answers from PubMed abstracts
"""

from .pubmed_prompts import (
    QUERY_DECOMPOSITION_PROMPT,
    ANSWER_SYNTHESIS_PROMPT,
    parse_decomposition_response,
    build_abstract_context,
)

__all__ = [
    "QUERY_DECOMPOSITION_PROMPT",
    "ANSWER_SYNTHESIS_PROMPT",
    "parse_decomposition_response",
    "build_abstract_context",
]
