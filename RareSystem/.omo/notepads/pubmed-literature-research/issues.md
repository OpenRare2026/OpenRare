# Issues and Challenges Encountered

## 1. Chinese Medical Query Translation

### Problem
Direct translation of Chinese medical queries to English often loses semantic meaning or uses incorrect terminology.

**Example:**
- "心肌梗死" should translate to "Myocardial Infarction[MeSH Terms]" not "Heart Attack"
- "糖尿病并发症" should expand to include "diabetic nephropathy", "diabetic retinopathy", etc.

### Current Limitations
- General translation APIs (Google Translate, DeepL) don't understand medical context
- MeSH term mapping requires domain knowledge
- No comprehensive Chinese-English medical terminology dictionary available

### Potential Solutions
1. Build medical glossary with MeSH mappings
2. Use medical NER before translation (OpenMed, Med7)
3. Leverage existing Chinese PubMed tools (Suppr, MedCite) as reference

## 2. Rate Limiting and API Quotas

### Problem
NCBI E-utilities has strict rate limits:
- 3 requests/second without API key
- 10 requests/second with API key
- Large queries (>10,000 records) require special handling

### Impact
- Batch processing of large result sets requires careful pagination
- Real-time Q&A may experience delays
- Need for intelligent caching strategies

### Mitigation Strategies
1. Always use API key (register at https://www.ncbi.nlm.nih.gov/account/)
2. Implement exponential backoff for retries
3. Use History Server pattern for large result sets
4. Cache frequently accessed queries
5. Consider LocalBioRAG approach for offline access

## 3. MeSH Term Coverage Gap

### Problem
- New articles take time to be indexed with MeSH terms (days to weeks)
- Emerging diseases/treatments may not have established MeSH terms
- Rare diseases may have limited MeSH coverage

### Impact
- Recent publications may be missed in MeSH-only searches
- Novel therapeutic approaches may not be captured

### Solution
Always combine MeSH terms with free-text search:
```python
query = "(Diabetes Mellitus[MeSH Terms] OR diabetes[tiab])"
```

## 4. Evidence Quality in RAG

### Problem
Standard RAG approaches may retrieve irrelevant or low-quality evidence for medical QA.

**Research Findings (2026):**
- Multi-Query Expansion introduces retrieval noise (contextual precision: 0.671)
- Dense-only retrieval misses structural context in full-text articles
- Single-shot retrieval fails for complex multi-step queries

### Solutions
1. **Cross-Encoder Reranking** - Best composite score (0.827)
2. **Iterative Query Refinement** - PubMed Reasoner approach
3. **Self-Reflection** - Self-MedRAG pattern (improves accuracy by 10%)
4. **Hybrid Retrieval** - BM25 + Dense with RRF

## 5. Hallucination in Medical LLM Responses

### Problem
LLMs generate plausible but unsupported medical claims - unacceptable in clinical settings.

**Baseline hallucination rate:** 12.7% (general RAG)

### Solution
Implement hallucination detection pipeline:
```python
# ClinicalRAG approach:
# 1. Extract claims from generated answer
# 2. Verify each claim against retrieved evidence (NLI model)
# 3. Calculate faithfulness score
# 4. Flag or filter unsupported claims
```

**Result:** Hallucination rate reduced to 3.2%

## 6. Full-Text vs. Abstract Retrieval

### Problem
- PubMed provides free abstracts, but full-text requires PMC or subscriptions
- Many questions require full-text evidence (methods, results, tables)
- Abstracts may not contain sufficient detail for complex queries

### Trade-offs
| Approach | Pros | Cons |
|----------|------|------|
| Abstracts only | Free, fast, complete coverage | Limited detail, may miss key evidence |
| PMC full-text | Complete evidence, figures/tables | Only ~7M articles (vs. 36M+ PubMed), parsing complexity |
| Publisher APIs | Access to latest articles | Subscription required, heterogeneous APIs |

### Recommended Strategy
1. Start with abstracts for broad coverage
2. Use PMC full-text when available (filter: `pmc[filter]`)
3. For critical evidence, provide links to publisher versions

## 7. Chinese-Language Medical Literature

### Problem
- Many relevant clinical studies published in Chinese journals
- Not indexed in PubMed/MEDLINE
- Language barrier for international researchers

### Current State
- PubMed includes some Chinese journals (e.g., Chinese Medical Journal)
- CNKI, Wanfang Data are major Chinese databases (separate from PubMed)
- Translation tools needed for cross-language retrieval

### Potential Approach
1. Search PubMed for English abstracts of Chinese studies
2. Integrate with Chinese databases (CNKI via API)
3. Use translation for Chinese full-text when needed

## 8. Rare Disease Specific Challenges

### Problem
Rare diseases have unique characteristics:
- Limited literature (sometimes <100 papers)
- Inconsistent terminology (orphan diseases have multiple names)
- Genetic heterogeneity (same phenotype, different genes)
- Phenotype variability (same gene, different phenotypes)

### Search Strategy Adjustments
1. **Include synonyms**: Use OR for all known disease names
2. **Gene-centric search**: Search by gene symbol + phenotype
3. **Broader terms**: Include parent diseases in MeSH hierarchy
4. **Case reports**: Include publication type "Case Reports"
5. **Preprints**: Consider bioRxiv/medRxiv for latest findings

Example query:
```python
query = """
    (
        "Progeria"[MeSH Terms] OR 
        progeria[tiab] OR 
        "Hutchinson-Gilford syndrome"[tiab] OR
        LMNA[Gene Name]
    )
    AND
    (
        case reports[pt] OR
        clinical trial[pt] OR
        review[pt]
    )
"""
```

## 9. Unresolved Questions

### For Implementation
1. **Which NER model best for Chinese medical text?**
   - OpenMed supports English only
   - Need to evaluate Chinese medical NER tools (MedCAT, custom models)

2. **Optimal chunking strategy for biomedical RAG?**
   - GraLC-RAG shows structure-aware chunking improves breadth
   - But MRR (standard metric) favors content-similarity
   - Trade-off between precision and coverage

3. **How to handle multi-modal evidence?**
   - Tables, figures often contain critical data
   - MedVRAG shows page-image retrieval improves accuracy (+1.0 point)
   - But adds complexity and latency

4. **Best embedding model for Chinese→English medical retrieval?**
   - PubMedBERT trained on English only
   - Need cross-lingual biomedical embeddings

### For Evaluation
1. **How to measure retrieval quality for rare diseases?**
   - Standard benchmarks (BioASQ, PubMedQA) focus on common conditions
   - Need rare disease-specific evaluation set

2. **Clinical relevance vs. retrieval metrics?**
   - High MRR doesn't guarantee clinically useful evidence
   - Need clinician-in-the-loop evaluation

## 10. Technical Debt Considerations

### If Building Production System
1. **Caching layer**: Redis/Memcached for frequent queries
2. **Query logging**: Track usage patterns for optimization
3. **A/B testing**: Compare retrieval strategies on real queries
4. **Monitoring**: Track API errors, latency, hallucination rates
5. **Fallback strategies**: What if NCBI API is down?
6. **Data versioning**: PubMed updates daily - how to handle reproducibility?

### Compliance and Ethics
1. **No patient data storage**: As per project requirements
2. **HIPAA compliance**: If processing any clinical text
3. **Terms of use**: NCBI requires email identification, rate limit compliance
4. **Citation requirements**: Some datasets require citation (BioASQ, etc.)
