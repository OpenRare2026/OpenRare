"""
RAG Prompts - Case Q&A and Document Retrieval

Usage Context:
- Used by: backend/services/rag_service.py
- Purpose: Generate answers for case-related questions using retrieved context
- When: User asks a question in Case Q&A interface

Flow:
1. User asks question in ChatInterface
2. RAGService._build_rag_prompt() uses these prompts
3. LLM generates answer with citations
"""

from typing import List, Tuple, Optional

# =============================================================================
# RAG SYSTEM PROMPT
# =============================================================================
# Used when: Building the main prompt for case Q&A
# Location: RAGService._build_rag_prompt()

RAG_SYSTEM_PROMPT = """You are a clinical genetics assistant helping analyze rare disease cases.
Use the provided context to answer questions accurately.
Always cite your sources and indicate confidence level.
If uncertain, clearly state limitations."""


# =============================================================================
# RAG CONTEXT TEMPLATE
# =============================================================================
# Used when: Formatting retrieved context for the LLM
# Location: RAGService._format_context_for_prompt()

RAG_CONTEXT_TEMPLATE = """
[Patient Information]: {patient_info}

[Variants]:
{variant_info}

[Relevant Context]:
{relevant_docs}

[Clinical Notes]:
{clinical_notes}
"""


# =============================================================================
# RAG QUESTION TEMPLATE
# =============================================================================
# Used when: Building the final prompt with question

RAG_QUESTION_TEMPLATE = """
Previous conversation:
{history}

Question: {query}

Answer (with citations):
"""


def build_rag_prompt(
    query: str,
    context: str,
    history: Optional[List[Tuple[str, str]]] = None
) -> str:
    """
    Build the complete RAG prompt for LLM.
    
    Args:
        query: User's question
        context: Formatted context string
        history: Optional conversation history [(user_msg, assistant_msg), ...]
    
    Returns:
        Complete prompt string for LLM
    """
    prompt_parts = [
        RAG_SYSTEM_PROMPT,
        "",
        f"Context: {context}",
        ""
    ]
    
    if history:
        prompt_parts.append("Previous conversation:")
        for user_msg, assistant_msg in history[-3:]:
            prompt_parts.append(f"  Q: {user_msg}")
            prompt_parts.append(f"  A: {assistant_msg}")
        prompt_parts.append("")
    
    prompt_parts.append(f"Question: {query}")
    prompt_parts.append("")
    prompt_parts.append("Answer (with citations):")
    
    return " | ".join(prompt_parts)
