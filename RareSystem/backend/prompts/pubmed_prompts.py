"""
PubMed RAG Skill Prompt Templates.

Contains prompt templates for:
1. Query decomposition: Converting user questions to PubMed search queries
2. Answer synthesis: Generating citation-based answers from PubMed abstracts
"""
import json
import re
import logging
from typing import List, Dict, Any, Optional

from services.pubmed_service import PubMedArticle


logger = logging.getLogger(__name__)


# =============================================================================
# QUERY DECOMPOSITION PROMPT
# =============================================================================

QUERY_DECOMPOSITION_PROMPT = """You are a medical literature search expert specializing in rare disease genetics. Your task is to decompose a user's question into an optimized PubMed search query.

## INPUT
User's question (may be in Chinese or English)

## OUTPUT FORMAT
Return ONLY a valid JSON object with the following structure (no markdown code blocks):
{
  "mesh_terms": ["MeSH term 1", "MeSH term 2"],
  "keywords": ["keyword1", "keyword2"],
  "pubmed_query": "combined search string with field tags",
  "search_strategy": "brief explanation of search strategy"
}

## RULES FOR QUERY CONSTRUCTION

1. **Translation**: Translate Chinese medical terms to standard English MeSH terms
   - Example: "癌症" → "Neoplasms"[mesh], "遗传病" → "Genetic Diseases, Inborn"[mesh]

2. **MeSH Vocabulary**: Use MeSH controlled vocabulary when available
   - Check https://meshb.nlm.nih.gov/ for standard terms
   - Prefer specific terms over broad ones (e.g., "Thrombospondin-2" over "proteins")

3. **Dual Coverage**: Include BOTH MeSH terms AND keywords
   - MeSH terms with [mesh] or [majr] tag
   - Keywords with [tiab] tag for title/abstract search
   - This covers ~5M PubMed records without MeSH indexing

4. **Boolean Operators**:
   - OR: For synonyms and related terms (e.g., "cancer[tiab] OR neoplasm[mesh]")
   - AND: For combining different concepts
   - NOT: Use sparingly, only to exclude clearly irrelevant results

5. **Field Tags**:
   - [mesh]: MeSH term (explodes to include narrower terms)
   - [majr]: Major MeSH topic (main focus of article)
   - [tiab]: Title or abstract
   - [au]: Author name
   - [jour]: Journal name

6. **Query Structure**:
   - Group synonyms with OR within a concept
   - Combine concepts with AND
   - Use parentheses for complex queries

## EXAMPLES

**Example 1 - Gene function in disease:**
User question: "THBS2基因在肿瘤免疫中的作用"
Output:
{
  "mesh_terms": ["Thrombospondin-2", "Neoplasms", "Immunotherapy"],
  "keywords": ["THBS2", "tumor immunity", "cancer immunology"],
  "pubmed_query": "(Thrombospondin-2[mesh] OR THBS2[tiab]) AND (Neoplasms[mesh] OR tumor[tiab] OR cancer[tiab]) AND (Immunotherapy[mesh] OR immun*[tiab])",
  "search_strategy": "Combined gene name with disease context and mechanism"
}

**Example 2 - Rare disease diagnosis:**
User question: "脊髓性肌萎缩症的基因诊断方法"
Output:
{
  "mesh_terms": ["Spinal Muscular Atrophies", "Genetic Testing", "Diagnosis"],
  "keywords": ["SMA", "spinal muscular atrophy", "gene diagnosis", "SMN1"],
  "pubmed_query": "(Spinal Muscular Atrophies[mesh] OR SMA[tiab] OR spinal muscular atrophy[tiab]) AND (Genetic Testing[mesh] OR gene diagnosis[tiab] OR molecular diagnosis[tiab])",
  "search_strategy": "Combined disease entity with diagnostic methodology"
}

**Example 3 - Variant interpretation:**
User question: "BRCA1变异的临床意义和致病性评估"
Output:
{
  "mesh_terms": ["BRCA1 Protein", "Mutation", "Pathogenicity", "Clinical Significance"],
  "keywords": ["BRCA1", "variant", "pathogenic", "clinical interpretation"],
  "pubmed_query": "(BRCA1 Protein[mesh] OR BRCA1[tiab]) AND (Mutation[mesh] OR variant[tiab] OR mutation[tiab]) AND (Pathogenicity[mesh] OR pathogenic[tiab])",
  "search_strategy": "Gene-variant-phenotype triad search"
}

## NOW PROCESS THE USER'S QUESTION
Return ONLY the JSON object, no additional text."""


# =============================================================================
# ANSWER SYNTHESIS PROMPT
# =============================================================================

ANSWER_SYNTHESIS_PROMPT = """You are a medical research assistant specializing in rare disease genetics and clinical genetics. Your task is to synthesize evidence-based answers from PubMed abstracts.

## INPUT
1. User's original question (in Chinese)
2. Multiple PubMed abstracts with PMID references

## OUTPUT
A comprehensive Chinese answer with proper PMID citations.

## CORE REQUIREMENTS

1. **Citation Requirement**: Every factual statement MUST include a citation
   - Format: [PMID: 12345678]
   - Place citation immediately after the statement it supports
   - Multiple citations allowed: [PMID: 12345678, PMID: 87654321]

2. **Evidence Quality Indicators**:
   - Prioritize: Systematic reviews, Meta-analyses, RCTs, Large cohort studies
   - Note study types when relevant: "一项纳入500例患者的研究[PMID: xxx]显示..."
   - Highlight high-quality evidence

3. **Uncertainty Disclosure**:
   - Explicitly state areas with insufficient evidence
   - Note conflicting findings between studies
   - Distinguish consensus from ongoing research

4. **Language**:
   - Write in Chinese
   - Keep PMIDs and technical terms (gene names, protein names) in English
   - Use professional medical terminology

5. **If No Direct Evidence**:
   - Clearly state "未找到直接针对该问题的研究"
   - Provide related or tangential findings if available
   - Suggest broader search terms if appropriate

## ANSWER STRUCTURE

### 主要发现 (Main Findings)
- Key findings with citations
- Group by theme or concept
- Use bullet points for clarity

### 证据强度 (Evidence Strength)
- 强证据领域: Areas with strong consensus
- 证据不足领域: Areas needing more research
- 存在争议的领域: Conflicting findings

### 临床意义 (Clinical Implications - if applicable)
- Practical takeaways
- Limitations

### 参考文献 (References)
List all cited references:
1. [PMID: xxx] Title. Authors. Journal, Year.

## EXAMPLE OUTPUT

### 主要发现

- THBS2（凝血酶敏感蛋白-2）是一种细胞外基质蛋白，在肿瘤微环境中发挥重要作用[PMID: 28534230]
- 研究表明THBS2在多种肿瘤中表达异常，包括结直肠癌、胃癌和胰腺癌[PMID: 29323456, PMID: 30123456]
- THBS2可能通过调节血管生成和免疫细胞浸润影响肿瘤进展[PMID: 28534230]

### 证据强度

- **强证据领域**: THBS2在多种肿瘤中的表达改变已有多项研究证实
- **证据不足领域**: THBS2作为免疫治疗靶点的临床研究较少
- **存在争议**: THBS2对预后的影响在不同癌种中结论不一致

### 参考文献
1. [PMID: 28534230] Thrombospondin-2 in tumor microenvironment. Smith J, et al. Cancer Res, 2018.
2. [PMID: 29323456] THBS2 expression in colorectal cancer. Lee K, et al. Oncogene, 2019.

## NOW SYNTHESIZE THE ANSWER
Based on the user's question and provided abstracts, generate a comprehensive answer following the structure above."""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_decomposition_response(llm_response: str) -> Dict[str, Any]:
    """
    Parse LLM response for query decomposition.
    
    Handles:
    - JSON extraction from markdown code blocks
    - Direct JSON strings
    - Fallback to default query structure if parsing fails
    
    Args:
        llm_response: Raw LLM response string
        
    Returns:
        Dict with keys: mesh_terms, keywords, pubmed_query, search_strategy
    """
    if not llm_response:
        return _default_decomposition("")
    
    # Try to extract JSON from code blocks first
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', llm_response)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # Try direct JSON
        json_str = llm_response.strip()
    
    # Try to find JSON object in the string
    json_obj_match = re.search(r'\{[\s\S]*\}', json_str)
    if json_obj_match:
        json_str = json_obj_match.group(0)
    
    try:
        result = json.loads(json_str)
        
        # Validate required keys
        if 'pubmed_query' not in result:
            # Try to construct from mesh_terms and keywords
            result = _construct_query_from_parts(result)
        
        # Ensure all required keys exist
        result.setdefault('mesh_terms', [])
        result.setdefault('keywords', [])
        result.setdefault('search_strategy', 'LLM-generated query')
        
        return result
        
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse LLM response as JSON: {e}")
        return _default_decomposition(llm_response)


def _default_decomposition(original_input: str) -> Dict[str, Any]:
    """
    Create default decomposition when JSON parsing fails.
    Uses the original input as the query.
    """
    # Clean up the input for PubMed
    query = original_input.strip()
    if query.startswith('{') or query.startswith('```'):
        # It's likely failed JSON, use a generic search
        query = "rare disease genetics"
    
    return {
        'mesh_terms': [],
        'keywords': query.split()[:5],  # Use first 5 words as keywords
        'pubmed_query': query,
        'search_strategy': 'Direct query (LLM response parsing failed)'
    }


def _construct_query_from_parts(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construct pubmed_query from mesh_terms and keywords if not provided.
    """
    mesh_terms = result.get('mesh_terms', [])
    keywords = result.get('keywords', [])
    
    parts = []
    
    if mesh_terms:
        mesh_parts = [f'{term}[mesh]' for term in mesh_terms[:3]]
        parts.append('(' + ' OR '.join(mesh_parts) + ')')
    
    if keywords:
        kw_parts = [f'{kw}[tiab]' for kw in keywords[:5]]
        parts.append('(' + ' OR '.join(kw_parts) + ')')
    
    if parts:
        result['pubmed_query'] = ' AND '.join(parts)
    else:
        result['pubmed_query'] = 'rare disease genetics'
    
    return result


def build_abstract_context(articles: List[PubMedArticle]) -> str:
    """
    Format PubMed articles into LLM-readable context.
    
    Each article includes:
    - PMID (required)
    - Title
    - Authors (first 5)
    - Journal
    - Year
    - Abstract (truncated to 1500 chars if longer)
    
    Args:
        articles: List of PubMedArticle objects
        
    Returns:
        Formatted string for LLM context
    """
    if not articles:
        return "未找到相关文献。No relevant articles found."
    
    parts = [f"共检索到 {len(articles)} 篇相关文献:\n"]
    parts.append("=" * 60)
    
    for i, article in enumerate(articles, 1):
        parts.append(f"\n### 文献 {i} [PMID: {article.pmid}]")
        parts.append("-" * 40)
        
        if article.title:
            parts.append(f"**标题**: {article.title}")
        
        if article.authors:
            author_str = ', '.join(article.authors[:5])
            if len(article.authors) > 5:
                author_str += f' 等 {len(article.authors)} 位作者'
            parts.append(f"**作者**: {author_str}")
        
        if article.journal:
            parts.append(f"**期刊**: {article.journal}")
        
        if article.year:
            parts.append(f"**年份**: {article.year}")
        
        if article.abstract:
            # Truncate very long abstracts
            abstract = article.abstract
            if len(abstract) > 1500:
                abstract = abstract[:1500] + '...'
            parts.append(f"**摘要**: {abstract}")
        
        parts.append(f"**链接**: {article.url}")
        
        if article.doi:
            parts.append(f"**DOI**: {article.doi}")
    
    return '\n'.join(parts)


def format_user_query_with_context(
    user_query: str,
    articles_context: str
) -> str:
    """
    Combine user query with formatted abstracts for LLM input.
    
    Args:
        user_query: Original user question
        articles_context: Formatted abstracts from build_abstract_context()
        
    Returns:
        Complete prompt for answer synthesis
    """
    return f"""## 用户问题
{user_query}

## 检索到的文献
{articles_context}

请基于以上文献回答用户问题，每条事实声明必须附带 PMID 引用。"""
