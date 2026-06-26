# Architectural Decisions for PubMed Literature Retrieval System

## Decision 1: Use BioPython Entrez as Primary PubMed Interface

### Context
Need programmatic access to PubMed for literature search and retrieval.

### Options Considered
1. **BioPython Entrez** - Mature, comprehensive wrapper
2. **Direct HTTP requests** - More control, but more code
3. **metapub** - Higher-level, but less maintained
4. **pubmed-parser** - Good for parsing, not for searching

### Decision
**Use BioPython Entrez** as the primary interface.

### Rationale
- Most mature and well-documented (3319 code snippets in Context7)
- Built-in rate limiting and error handling
- History server support for batch processing
- Integrated XML/Medline parsers
- Active maintenance (latest version 1.88.dev0)
- Used in production systems (RAGflow, Biomni, SRAgent)

### Implementation Pattern
```python
from Bio import Entrez

Entrez.email = "your.email@example.com"
Entrez.api_key = "your_api_key"  # For 10 req/sec

# Search
handle = Entrez.esearch(db="pubmed", term=query, retmax=50)
record = Entrez.read(handle)
pmids = record["IdList"]

# Fetch
fetch_handle = Entrez.efetch(db="pubmed", id=pmids, rettype="medline")
```

### Consequences
- **Positive**: Rapid development, reliable, well-tested
- **Negative**: Low-level API requires manual query building
- **Mitigation**: Build higher-level wrapper for common patterns

---

## Decision 2: Hybrid Retrieval Strategy (BM25 + Dense + Reranking)

### Context
Research shows single retrieval strategy is suboptimal for biomedical QA.

### Options Considered
1. **Dense-only** (vector search) - Good semantic matching
2. **BM25-only** (lexical) - Good for exact term matching
3. **Hybrid BM25 + Dense** - Combines both strengths
4. **Hybrid + Cross-Encoder Reranking** - Best performance (0.827 composite)

### Decision
**Implement Hybrid BM25 + Dense with Cross-Encoder Reranking**

### Rationale
- Cross-Encoder Reranking achieves best composite score (0.827)
- Hybrid approach balances recall and precision
- Dense vectors capture semantic similarity
- BM25 captures exact term matches (important for gene names, variants)
- Research-backed (arXiv:2605.02520)

### Implementation Pattern
```python
# Stage 1: Parallel retrieval
bm25_results = bm25_search(query, top_k=100)
dense_results = dense_search(query, top_k=100)  # PubMedBERT embeddings

# Stage 2: Reciprocal Rank Fusion
combined = reciprocal_rank_fusion(bm25_results, dense_results, k=60)

# Stage 3: Cross-encoder reranking
reranked = cross_encoder.rerank(query, combined[:50], top_k=20)
```

### Consequences
- **Positive**: Best retrieval quality, handles diverse query types
- **Negative**: More complex, higher latency
- **Mitigation**: Cache embeddings, use efficient ANN index (FAISS, Qdrant)

---

## Decision 3: Medical NER with OpenMed for Entity Extraction

### Context
Need to extract medical entities from Chinese clinical queries for targeted search.

### Options Considered
1. **OpenMed** - 12+ specialized models, production-ready
2. **Med7** - Lightweight, spaCy-based, 7 categories
3. **GLiNER-BioMed** - Zero-shot, flexible labels
4. **Clinical NER Pipeline** - Full pipeline with UMLS linking

### Decision
**Use OpenMed for disease/drug extraction, with fallback to GLiNER for zero-shot**

### Rationale
- OpenMed has specialized models (disease, pharma, genes, anatomy)
- High accuracy (trained on clinical text)
- Easy one-line API
- HIPAA-compliant PII detection built-in
- GLiNER as fallback for custom entity types

### Implementation Pattern
```python
from openmed import analyze_text

# Extract diseases
result = analyze_text(
    query,
    model_name="disease_detection_superclinical"
)
diseases = [e.text for e in result.entities if e.label == "DISEASE"]

# Extract drugs
result = analyze_text(
    query,
    model_name="pharma_detection_superclinical"
)
drugs = [e.text for e in result.entities if e.label == "DRUG"]
```

### Consequences
- **Positive**: High accuracy, production-ready, multiple specialized models
- **Negative**: English-only (Chinese queries need translation first)
- **Mitigation**: Translate Chinese → English before NER, or use Chinese NER tools

---

## Decision 4: Iterative Query Refinement (PubMed Reasoner Pattern)

### Context
Single-shot retrieval often fails for complex biomedical queries requiring multi-step inference.

### Options Considered
1. **Single-shot RAG** - Simple, but brittle
2. **Multi-query expansion** - Broad coverage, but noisy (precision: 0.671)
3. **Iterative refinement with self-critic** - PubMed Reasoner approach
4. **Agentic RAG** - Autonomous decision-making in retrieval loop

### Decision
**Implement Iterative Query Refinement with Self-Critic**

### Rationale
- PubMed Reasoner achieves 78.32% accuracy (surpasses human experts)
- Self-critic evaluates MeSH terms BEFORE full retrieval
- Reflective retrieval with early stopping controls token usage
- Evidence-grounded responses with explicit citations

### Implementation Pattern
```python
class PubMedRetriever:
    def retrieve(self, query, max_iterations=3):
        evidence = []
        for iteration in range(max_iterations):
            # Step 1: Generate/refine query with MeSH terms
            refined_query = self.self_critic_refine(query, evidence)
            
            # Step 2: Retrieve batch of articles
            new_evidence = self.search_pubmed(refined_query, top_k=10)
            evidence.extend(new_evidence)
            
            # Step 3: Check if sufficient evidence
            if self.has_sufficient_evidence(evidence):
                break
        
        # Step 4: Generate answer with citations
        return self.generate_answer(query, evidence)
    
    def self_critic_refine(self, query, existing_evidence):
        # Evaluate MeSH term coverage, alignment, redundancy
        # Refine query based on partial retrieval
        pass
```

### Consequences
- **Positive**: Higher accuracy, handles complex queries, efficient
- **Negative**: More complex, higher latency (multiple iterations)
- **Mitigation**: Set max iterations, use early stopping

---

## Decision 5: Hallucination Detection with NLI Verification

### Context
LLMs generate hallucinated medical claims - unacceptable in clinical settings.

### Options Considered
1. **No detection** - Fast, but risky
2. **Citation checking** - Verify citations exist
3. **NLI-based verification** - Check claim entailment
4. **LLM-as-judge** - Use another LLM to verify

### Decision
**Implement NLI-based Hallucination Detection (ClinicalRAG Pattern)**

### Rationale
- Reduces hallucination rate from 12.7% → 3.2%
- Lightweight (NLI model faster than full LLM)
- Claim-level granularity (can flag specific unsupported claims)
- Research-backed approach

### Implementation Pattern
```python
from transformers import pipeline

nli = pipeline("textual-entailment", model="deberta-v3-large-mnli")

def detect_hallucinations(answer, evidence):
    # Extract claims from answer
    claims = extract_claims(answer)
    
    # Verify each claim against evidence
    verified_claims = []
    for claim in claims:
        # Check if evidence entails claim
        result = nli(premise=evidence, hypothesis=claim)
        if result["label"] == "ENTAILMENT" and result["score"] > 0.8:
            verified_claims.append(claim)
        else:
            # Flag as potentially hallucinated
            flagged_claims.append(claim)
    
    return verified_claims, flagged_claims
```

### Consequences
- **Positive**: Significantly reduces hallucinations, claim-level granularity
- **Negative**: Adds latency, may be overly conservative
- **Mitigation**: Use lightweight NLI model, cache results

---

## Decision 6: Chinese Query Translation with Medical Glossary

### Context
Users ask questions in Chinese, but PubMed requires English queries.

### Options Considered
1. **Direct translation** (Google/DeepL) - Fast, but inaccurate for medical terms
2. **Translation + medical glossary** - Better terminology
3. **Chinese PubMed tools** (Suppr, MedCite) - Use their API
4. **Cross-lingual embeddings** - No translation needed

### Decision
**Implement Translation + Medical Glossary + MeSH Mapping**

### Rationale
- Direct translation loses medical context
- Medical glossary ensures correct terminology
- MeSH mapping improves search precision
- More control than relying on external APIs

### Implementation Pattern
```python
class MedicalTranslator:
    def __init__(self):
        self.glossary = self.load_medical_glossary()
        self.mesh_map = self.load_mesh_mapping()
        self.translator = DeepLAPI()  # Or other translation service
    
    def translate_query(self, chinese_query):
        # Step 1: Extract medical entities (using Chinese NER if available)
        entities = self.extract_entities(chinese_query)
        
        # Step 2: Translate with glossary
        translated = self.translator.translate(
            chinese_query,
            glossary=self.glossary
        )
        
        # Step 3: Map to MeSH terms
        mesh_terms = [self.mesh_map.get(e, e) for e in entities]
        
        # Step 4: Build PubMed query
        pubmed_query = self.build_pubmed_query(mesh_terms, translated)
        
        return pubmed_query
```

### Consequences
- **Positive**: Accurate medical terminology, MeSH-aware
- **Negative**: Requires maintaining glossary and MeSH mapping
- **Mitigation**: Start with common rare disease terms, expand over time

---

## Decision 7: Rate Limiting with Exponential Backoff

### Context
NCBI E-utilities has strict rate limits (3-10 req/sec). Need to handle gracefully.

### Options Considered
1. **Simple sleep** - Fixed delay between requests
2. **Rate limiter decorator** - Enforce max requests/second
3. **Exponential backoff** - Increase delay on errors
4. **Queue-based** - Centralized request queue

### Decision
**Implement Rate Limiter Decorator + Exponential Backoff**

### Rationale
- Decorator pattern is reusable and transparent
- Exponential backoff handles transient errors gracefully
- Combines proactive (rate limit) and reactive (backoff) strategies

### Implementation Pattern
```python
import time
from functools import wraps
from urllib.error import HTTPError

def rate_limit(max_per_second=10):
    min_interval = 1.0 / max_per_second
    last_called = [0.0]
    
    @wraps
    def decorator(func):
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            remaining = min_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_per_second=10)  # With API key
def safe_entrez_search(**kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            handle = Entrez.esearch(**kwargs)
            record = Entrez.read(handle)
            handle.close()
            return record
        except HTTPError as e:
            if e.code == 429:  # Rate limit
                time.sleep(10 * (attempt + 1))
            elif e.code >= 500:  # Server error
                time.sleep(5 * (attempt + 1))
            else:
                raise
    raise Exception("Max retries exceeded")
```

### Consequences
- **Positive**: Compliant with NCBI policies, handles errors gracefully
- **Negative**: Adds latency for large batch operations
- **Mitigation**: Use History Server pattern for large result sets

---

## Decision 8: Evidence Grounding with Explicit Citations

### Context
Clinical users need to verify evidence sources for trust and accountability.

### Options Considered
1. **No citations** - Clean output, but unverifiable
2. **PMID list at end** - Simple, but hard to verify
3. **Inline citations** - Each claim linked to source
4. **Evidence tables** - Structured claim-evidence mapping

### Decision
**Implement Inline Citations with Evidence Tables**

### Rationale
- Mirrors academic writing conventions
- Enables quick verification
- Supports dual-track mechanism (clinical vs. research)
- Required for clinical-grade reports

### Implementation Pattern
```python
def generate_answer_with_citations(query, evidence):
    prompt = f"""
    Question: {query}
    
    Evidence:
    {[f"[{i}] {e['title']} (PMID: {e['pmid']})" for i, e in enumerate(evidence, 1)]}
    
    Instructions:
    - Answer the question using ONLY the provided evidence
    - Include inline citations like [1], [2] for each claim
    - If evidence is insufficient, state uncertainty
    - Generate evidence table mapping claims to sources
    """
    
    response = llm.generate(prompt)
    
    # Parse response to extract claims and citations
    answer, evidence_table = parse_citations(response)
    
    return {
        "answer": answer,
        "evidence_table": evidence_table,
        "references": evidence
    }
```

### Consequences
- **Positive**: Transparent, verifiable, clinically appropriate
- **Negative**: More verbose, requires parsing
- **Mitigation**: Provide both short and detailed output modes

---

## Decision 9: Local Caching for Frequently Accessed Queries

### Context
Repeated queries for common rare diseases should be cached for efficiency.

### Options Considered
1. **No caching** - Always fresh, but slow
2. **In-memory cache** - Fast, but lost on restart
3. **Redis cache** - Persistent, shared across instances
4. **File-based cache** - Simple, persistent

### Decision
**Implement Redis Cache with TTL (Time-To-Live)**

### Rationale
- Redis is fast and supports TTL
- Shared cache across multiple instances
- Reduces NCBI API load
- Improves response time for common queries

### Implementation Pattern
```python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379)

def cached_pubmed_search(query, ttl_hours=24):
    cache_key = f"pubmed:search:{hash(query)}"
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Search PubMed
    results = safe_entrez_search(db="pubmed", term=query, retmax=50)
    
    # Cache results
    redis_client.setex(
        cache_key,
        timedelta(hours=ttl_hours),
        json.dumps(results)
    )
    
    return results
```

### Consequences
- **Positive**: Faster responses, reduced API load
- **Negative**: Stale data (PubMed updates daily)
- **Mitigation**: Use appropriate TTL (24h for searches, 1h for fetches)

---

## Decision 10: Dual-Track Output (Clinical vs. Research)

### Context
System serves both clinical diagnosis support and research hypothesis generation.

### Options Considered
1. **Single output** - Simple, but doesn't distinguish confidence levels
2. **Confidence scores** - Numeric, but hard to interpret
3. **Dual-track** - Separate clinical and research outputs
4. **Tiered evidence** - Graded by evidence quality

### Decision
**Implement Dual-Track Output with Clear Visual Distinction**

### Rationale
- Matches project requirements (clinical vs. research tracks)
- Clear visual distinction prevents misuse
- Clinical track: ACMG classification, fully verified
- Research track: Hypotheses with uncertainty quantification

### Implementation Pattern
```python
def generate_dual_track_report(query, evidence):
    # Clinical track: Only high-confidence, verified evidence
    clinical_evidence = filter_by_quality(evidence, min_quality="high")
    clinical_report = generate_clinical_report(query, clinical_evidence)
    
    # Research track: All evidence with uncertainty
    research_report = generate_research_report(query, evidence)
    
    return {
        "clinical_track": {
            "report": clinical_report,
            "warning": "Clinical-grade evidence only. Consult clinician.",
            "acmg_classifications": classify_acmg(clinical_evidence)
        },
        "research_track": {
            "report": research_report,
            "warning": "Exploratory findings. Not for clinical decision-making.",
            "uncertainty_metrics": calculate_uncertainty(evidence)
        }
    }
```

### Consequences
- **Positive**: Clear separation, appropriate for different use cases
- **Negative**: More complex output generation
- **Mitigation**: Use templates, clear UI design

---

## Summary of Key Decisions

| # | Decision | Chosen Approach | Rationale |
|---|----------|-----------------|-----------|
| 1 | PubMed Interface | BioPython Entrez | Mature, comprehensive, well-documented |
| 2 | Retrieval Strategy | Hybrid BM25+Dense+Rerank | Best performance (0.827 composite) |
| 3 | Medical NER | OpenMed + GLiNER | Specialized models, zero-shot fallback |
| 4 | Query Refinement | Iterative with Self-Critic | 78.32% accuracy on PubMedQA |
| 5 | Hallucination Detection | NLI Verification | Reduces hallucination 12.7% → 3.2% |
| 6 | Chinese Translation | Medical Glossary + MeSH | Accurate terminology |
| 7 | Rate Limiting | Decorator + Backoff | Compliant, handles errors |
| 8 | Evidence Grounding | Inline Citations | Transparent, verifiable |
| 9 | Caching | Redis with TTL | Fast, reduces API load |
| 10 | Output Format | Dual-Track | Clinical vs. research separation |

## Open Decisions (To Be Determined)

1. **Chinese NER Tool**: Which tool best for Chinese medical entity extraction?
2. **Embedding Model**: Best cross-lingual biomedical embeddings?
3. **Vector Database**: FAISS vs. Qdrant vs. ChromaDB?
4. **LLM Backend**: GPT-4o vs. local models (Llama 3.1)?
5. **Evaluation Metrics**: How to measure rare disease retrieval quality?
