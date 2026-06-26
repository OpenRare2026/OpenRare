# PubMed Literature Retrieval Research Summary

**Research Date:** May 20, 2026  
**Researcher:** The Librarian  
**Plan:** pubmed-literature-research

## Executive Summary

Comprehensive research completed on PubMed APIs, medical NLP approaches, and literature retrieval best practices for rare disease genetic diagnosis Q&A system.

### Key Findings

#### 1. NCBI E-utilities API (Well-Documented, Stable)
- **9 endpoints**: ESearch, EFetch, ESummary, ELink, EPost, EInfo, ESpell, ECitMatch, EGQuery
- **Rate limits**: 3 req/sec (no API key), 10 req/sec (with API key)
- **Best practice**: Always use `email` + `api_key` parameters, implement exponential backoff
- **History Server**: Essential for batch processing >1000 records

#### 2. BioPython Entrez (Recommended Library)
- **Most mature**: 3319 code snippets, active maintenance
- **Production use**: RAGflow, Biomni, SRAgent
- **Pattern**: `Entrez.esearch()` → `Entrez.efetch()` → `Medline.parse()`
- **Batch processing**: Use `usehistory=y` + WebEnv/QueryKey pattern

#### 3. Medical NER (Multiple Options Available)
- **OpenMed** (Best for production): 12+ specialized models, HIPAA-compliant
  - Disease detection, pharma detection, gene detection, PII detection
  - One-line API: `analyze_text(query, model_name="disease_detection_superclinical")`
- **Med7** (Lightweight): spaCy-based, 7 categories (DRUG, STRENGTH, FORM, etc.)
- **GLiNER-BioMed** (Zero-shot): Flexible labels, no training needed

#### 4. Chinese Medical Query Translation (Key Challenge)
- **Problem**: Direct translation loses medical context
- **Solution**: Medical glossary + MeSH mapping + entity-aware translation
- **Existing tools**: Suppr (超能文献), MedCite - can use as reference or API
- **Research**: Cross-lingual UMLS mapping shows promise (string + semantic similarity)

#### 5. RAG + PubMed (State-of-the-Art, 2026 Research)
- **Best retrieval**: Cross-Encoder Reranking (composite score: 0.827)
- **Best QA agent**: PubMed Reasoner (78.32% accuracy, surpasses human experts)
- **Hallucination detection**: NLI verification reduces 12.7% → 3.2%
- **Iterative refinement**: Self-MedRAG improves accuracy by 10% on PubMedQA

#### 6. MeSH Terms (Critical for Precision)
- **Automatic mapping**: PubMed maps queries to MeSH automatically
- **Manual control**: Use `[MeSH Terms]` tag for precision
- **Explosion**: MeSH searches include narrower terms automatically
- **Coverage gap**: New articles not yet indexed (combine with free-text `[tiab]`)

## Notepad Files Created

1. **learnings.md** - Comprehensive technical documentation
   - E-utilities API reference
   - BioPython usage patterns
   - Medical NER tools comparison
   - RAG architectures
   - Code examples

2. **issues.md** - Challenges and limitations
   - Chinese translation accuracy
   - Rate limiting constraints
   - MeSH coverage gaps
   - Hallucination risks
   - Rare disease specific challenges

3. **decisions.md** - Architectural decisions
   - 10 key decisions with rationale
   - Implementation patterns
   - Trade-offs and consequences
   - Open questions for future resolution

## Recommended Architecture

```
Chinese Query → Medical NER → Translation + MeSH Mapping → 
Hybrid Retrieval (BM25+Dense) → Cross-Encoder Reranking → 
Iterative Refinement → Hallucination Detection → 
Dual-Track Output (Clinical + Research)
```

## Next Steps

1. **Implement BioPython wrapper** with rate limiting and caching
2. **Build medical glossary** for Chinese→English translation
3. **Integrate OpenMed** for entity extraction
4. **Implement hybrid retrieval** with reranking
5. **Add hallucination detection** with NLI verification
6. **Design dual-track UI** with clear visual distinction

## Key Resources

### Documentation
- [NCBI E-utilities Guide](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [BioPython Entrez Tutorial](https://biopython.org/docs/latest/Tutorial/chapter_entrez.html)
- [MeSH Database](https://www.ncbi.nlm.nih.gov/mesh/)

### Libraries
- [BioPython](https://biopython.org/) - `pip install biopython`
- [OpenMed](https://github.com/maziyarpanahi/openmed) - `pip install openmed`
- [Med7](https://github.com/kormilitzin/med7) - `pip install med7`

### Research Papers (2026)
- arXiv:2605.02520 - Benchmarking Retrieval Strategies for Biomedical RAG
- arXiv:2603.27335 - PubMed Reasoner: Dynamic Reasoning-based Retrieval
- arXiv:2601.04531 - Self-MedRAG: Iterative Medical QA

### Chinese Tools
- [Suppr 超能文献](https://suppr.wilddata.cn/) - Chinese PubMed search
- [MedCite](https://ai-bio.cn/medcite/) - AI-powered semantic retrieval

## Compliance Notes

- **NCBI Requirements**: Email identification mandatory, API key recommended
- **Rate Limits**: 3 req/sec (no key), 10 req/sec (with key)
- **Patient Data**: No storage (per project requirements)
- **Clinical Use**: Clear warnings for research track findings

---

**Research Status:** ✅ COMPLETE  
**All Required Avenues:** ✅ Covered
- [x] NCBI E-utilities API (esearch, efetch, elink)
- [x] BioPython Entrez module
- [x] GitHub PubMed integration examples
- [x] Medical NER for keyword extraction
- [x] Chinese medical query translation
- [x] RAG + PubMed patterns
- [x] Rate limits, authentication, terms of use
- [x] Existing Python libraries comparison
