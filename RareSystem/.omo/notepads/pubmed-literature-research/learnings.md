# PubMed Literature Retrieval Research Findings

## 1. NCBI E-utilities API Documentation and Usage

### Base URL and Structure
All E-utilities URLs begin with: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

### Nine E-utilities Endpoints
1. **ESearch** - Search a text query in a single Entrez database, returns UIDs (PMIDs for PubMed)
2. **ESummary** - Retrieve document summaries for each UID
3. **EFetch** - Retrieve full records for each UID
4. **EPost** - Upload a list of UIDs for later use
5. **ELink** - Retrieve UIDs for related or linked records, or LinkOut URLs
6. **EInfo** - Retrieve information and statistics about a single database
7. **ESpell** - Retrieve spelling suggestions for a text query
8. **ECitMatch** - Search PubMed for a series of citation strings
9. **EGQuery** - Search a text query in all databases and return the number of results for each database

### Rate Limits and API Key Requirements
- **Without API Key**: Maximum 3 requests per second
- **With API Key**: Maximum 10 requests per second (default), higher rates available by request
- **Large Jobs**: Limit to weekends or 9:00 PM - 5:00 AM Eastern time on weekdays
- **Retmax Limits**: 
  - ESearch: Up to 100,000 UIDs (use retstart/retmax for pagination)
  - PMC ESearch (updated Feb 2026): Only first 10,000 records accessible
  - EPost: Up to 10,000 PMCIDs per request

### Required Parameters for All Requests
- `email` - Always identify yourself to NCBI
- `tool` - Software name for identification
- `api_key` - Optional but recommended for higher rate limits

### ESearch Parameters (PubMed Search)
```
Base: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
Required: db=pubmed&term={query}
Optional:
  - retmax: Number of results (default=20, max=100,000)
  - retmode: Output format (xml, json)
  - sort: Sort order (relevance, date, etc.)
  - usehistory=y: Save results for batch retrieval
  - mindate/maxdate: Date range (YYYY/MM/DD)
  - reldate: Days relative to current date
```

### EFetch Parameters (Full Record Retrieval)
```
Base: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
Required: db=pubmed&id={pmid1,pmid2,...}
Optional:
  - rettype: medline, xml, abstract, etc.
  - retmode: text, xml, json
```

### History Server Pattern (for Large Datasets)
```python
# Step 1: Search with usehistory=y
esearch.fcgi?db=pubmed&term=query&usehistory=y

# Returns: WebEnv and QueryKey

# Step 2: Fetch using WebEnv and QueryKey
efetch.fcgi?db=pubmed&query_key={key}&WebEnv={webenv}&rettype=medline
```

## 2. BioPython Entrez Module - Best Practices

### Installation and Setup
```bash
pip install biopython
```

### Basic Usage Pattern
```python
from Bio import Entrez

# ALWAYS set email (required by NCBI)
Entrez.email = "your.email@example.com"

# Optional: Set API key for higher rate limits
Entrez.api_key = "your_api_key_here"

# Search PubMed
handle = Entrez.esearch(
    db="pubmed",
    term="diabetes[MeSH Terms]",
    retmax=20,
    retmode="json"
)
record = Entrez.read(handle)
pmids = record["IdList"]

# Fetch full records
fetch_handle = Entrez.efetch(
    db="pubmed",
    id=pmids,
    rettype="medline",
    retmode="text"
)

# Parse Medline format
from Bio import Medline
records = Medline.parse(fetch_handle)
for record in records:
    print(record.get("TI", "No title"))  # Title
    print(record.get("AB", "No abstract"))  # Abstract
```

### Batch Processing Pattern (for Large Result Sets)
```python
from Bio import Entrez
import time

Entrez.email = "your.email@example.com"

# Search with history
search_results = Entrez.read(
    Entrez.esearch(
        db="pubmed",
        term="cancer[MeSH Terms]",
        usehistory="y",
        retmax=10000
    )
)

count = int(search_results["Count"])
webenv = search_results["WebEnv"]
query_key = search_results["QueryKey"]

# Fetch in batches
batch_size = 100
for start in range(0, count, batch_size):
    end = min(count, start + batch_size)
    fetch_handle = Entrez.efetch(
        db="pubmed",
        rettype="medline",
        retmode="text",
        retstart=start,
        retmax=batch_size,
        webenv=webenv,
        query_key=query_key
    )
    # Process batch...
    fetch_handle.close()
    time.sleep(0.34)  # Respect rate limit (3 req/sec without API key)
```

### Error Handling Best Practices
```python
from Bio import Entrez
from urllib.error import URLError, HTTPError
import time

def safe_entrez_search(db, term, max_retries=3):
    Entrez.email = "your.email@example.com"
    
    for attempt in range(max_retries):
        try:
            handle = Entrez.esearch(db=db, term=term, retmax=100)
            record = Entrez.read(handle)
            handle.close()
            return record
        except HTTPError as e:
            if e.code == 429:  # Rate limit exceeded
                time.sleep(10)  # Wait longer
                continue
            raise
        except URLError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(5)
    
    raise Exception("Max retries exceeded")
```

## 3. Medical Keyword Extraction Approaches

### Named Entity Recognition (NER) Tools

#### OpenMed (Production-Ready, 2026)
```python
from openmed import analyze_text

result = analyze_text(
    "Patient started on imatinib for chronic myeloid leukemia.",
    model_name="disease_detection_superclinical"
)

for entity in result.entities:
    print(f"{entity.label:<12} {entity.text:<35} {entity.confidence:.2f}")
```

**Available Models:**
- `disease_detection_superclinical` - Disease & Conditions (434M params)
- `pharma_detection_superclinical` - Drugs & Medications (434M params)
- `pii_detection_superclinical` - PII & De-identification (434M params)
- `anatomy_detection_electramed` - Anatomy & Body Parts (109M params)
- `gene_detection_genecorpus` - Genes & Proteins (109M params)

**Installation:**
```bash
pip install openmed
```

#### Med7 (spaCy-based, Lightweight)
```python
import spacy

med7 = spacy.load("en_core_med7_lg")

text = "Patient was prescribed Magnesium hydroxide 400mg/5ml suspension PO"
doc = med7(text)

for ent in doc.ents:
    print(ent.text, "=>", ent.label_)
# Output: Magnesium hydroxide => DRUG
#         400mg/5ml => STRENGTH
#         suspension => FORM
#         PO => ROUTE
```

**7 Entity Categories:**
- DRUG, STRENGTH, FORM, ROUTE, DOSAGE, FREQUENCY, DURATION

**Installation:**
```bash
pip install med7
python -m med7 download
```

#### GLiNER-BioMed (Zero-Shot, Flexible)
```python
from gliner import GLiNER

model = GLiNER.from_pretrained("Ihor/gliner-biomed-large-v1.0")

text = "Patient diagnosed with type 2 diabetes mellitus and hypertension."
labels = ["Disease", "Drug", "Lab test", "Demographic information"]

entities = model.predict_entities(text, labels, threshold=0.5)
```

**Installation:**
```bash
pip install gliner
```

#### Clinical NER Pipeline (Production-Grade)
```python
from src.ner import ClinicalNERPipeline

pipeline = ClinicalNERPipeline()

text = "Patient presents with Type 2 diabetes mellitus, controlled on metformin 500mg twice daily."
entities = pipeline.extract(text)

for ent in entities:
    print(f"{ent.text} | {ent.label} | {ent.umls_cui}")
# Output: Type 2 diabetes mellitus | CONDITION | C0011860
#         metformin | MEDICATION | C0025598
```

**Features:**
- UMLS concept linking
- SNOMED CT, ICD-10, RxNorm mapping
- HIPAA de-identification
- FHIR output format

### Chinese Medical Query Translation

#### Challenge
Chinese medical queries need translation to English for PubMed search. Key issues:
- Professional terminology (e.g., "心肌梗死" → "Myocardial Infarction" not "Heart Attack")
- Semantic understanding (e.g., "糖尿病并发症" includes "diabetic nephropathy", "diabetic retinopathy")
- MeSH term mapping

#### Solutions

**1. Medical Translation with Glossary**
```python
class MedicalTranslator:
    def __init__(self):
        self.term_dict = self.load_medical_terms()  # Load medical dictionary
        self.translator = DeepLAPI()  # Or other translation API
        
    def translate_with_glossary(self, text):
        terms = self.extract_medical_entities(text)
        result = self.translator.translate(
            text, 
            glossary=self.term_dict  # Use medical glossary
        )
        return result
```

**2. Cross-Lingual UMLS Mapping**
Research shows strategies for mapping Chinese medical entities to UMLS:
- String-based: Translate → MetaMap/Elasticsearch → UMLS
- Semantic-based: Cross-lingual BERT → semantic similarity
- Combined: String + semantic similarity integration

**3. Existing Chinese PubMed Search Tools**
- **Suppr (超能文献)**: Chinese natural language PubMed search
  - API: https://openapi.suppr.wilddata.cn
  - Features: Smart semantic understanding, multi-dimensional filters
- **MedCite (MedCite 学术引擎)**: AI-powered semantic retrieval
  - Supports Chinese queries with MeSH term expansion
  - Multi-round Q&A with evidence citations

## 4. PubMed Search Query Building

### PubMed Field Tags
```
[ti] - Title
[ab] - Abstract
[tiab] - Title/Abstract
[MeSH Terms] - MeSH terms (explodes to include narrower terms)
[MeSH Major Topic] - Major MeSH terms only
[au] - Author
[journal] - Journal name
[dp] - Publication date
[pt] - Publication type
```

### MeSH Term Search Strategy
```python
# Basic MeSH search
term = "Diabetes Mellitus, Type 2[MeSH Terms]"

# MeSH with subheadings (qualifiers)
term = "Diabetes Mellitus, Type 2/drug therapy[MeSH Terms]"

# MeSH without explosion (don't include narrower terms)
term = "Diabetes Mellitus, Type 2[MeSH Terms:noexp]"

# Major MeSH topic only
term = "Diabetes Mellitus, Type 2[MeSH Major Topic]"

# Combine MeSH with free text
term = "(Diabetes Mellitus, Type 2[MeSH Terms] OR type 2 diabetes[tiab])"
```

### Common Search Patterns
```python
# Date range
term = "cancer[MeSH Terms] AND 2020:2024[dp]"

# Article type filter
term = "COVID-19[MeSH Terms] AND Clinical Trial[pt]"

# Author search
term = "Smith J[au] AND 2023[dp]"

# Journal filter
term = "immunotherapy[tiab] AND Nature[journal]"

# Complex Boolean query
term = """
    (Diabetes Mellitus[MeSH Terms] OR diabetes[tiab]) 
    AND 
    (Complications[Subheading] OR complication[tiab])
    AND 
    (2020:2024[dp])
    AND 
    (English[la])
"""
```

### LLM-Assisted Query Building
```python
# Pattern from cxy15/PubMed-literature-search
# Natural language → PubMed query
prompt = """
Convert this natural language query to a PubMed search query:
"{user_query}"

Return ONLY the PubMed query string using MeSH terms and field tags.
Example: "recent diabetes drug trials" → "Diabetes Mellitus/drug therapy[MeSH] AND Clinical Trial[pt] AND 2023:2024[dp]"
"""
```

## 5. RAG + PubMed Integration Patterns

### State-of-the-Art Approaches (2026)

#### 1. PubMed Reasoner (Iterative Query Refinement)
**Key Innovation:** Self-critic query refinement BEFORE full retrieval
```python
# Three-stage process:
# 1. Search with Self-Critic Query Refinement
#    - Evaluate MeSH terms for coverage, alignment, redundancy
#    - Refine based on partial (metadata) retrieval
# 2. Reflective Article Retrieval with Early Stopping
#    - Process articles in batches
#    - Stop when sufficient evidence gathered
# 3. Evidence-Grounded Response Generation
#    - Produce answers with explicit citations
```

**Performance:** 78.32% accuracy on PubMedQA (surpasses human experts)

#### 2. Self-MedRAG (Hybrid Retrieval + Self-Reflection)
```python
# Hybrid retrieval: BM25 (lexical) + Contriever (semantic) via RRF
# Self-reflection loop:
#   1. Generate answer with rationale
#   2. Verify rationale against evidence (NLI or LLM-based)
#   3. If insufficient support → reformulate query → iterate
```

**Performance:** 
- MedQA: 80.00% → 83.33% (with self-reflection)
- PubMedQA: 69.10% → 79.82% (with self-reflection)

#### 3. Agentic RAG (Dual-Domain Retrieval)
```python
# Retrieve from both PubMed (literature) and MIMIC-IV (clinical notes)
# Domain-specific encoders:
#   - PubMedBERT for literature
#   - ClinicalBERT for clinical notes
# Agentic loop: assess evidence quality → refine query → re-query
```

**Performance:** 82.09% on PubMedQA

#### 4. LocalBioRAG (Fully Local, Privacy-Preserving)
```python
# Complete local pipeline (no external API calls)
# Hybrid retrieval:
#   1. BM25 sparse search → top 100 candidates
#   2. BGE-M3 dense re-ranking → top 10 documents
#   3. Llama 3.1 8B LoRA for snippet extraction
#   4. Second LoRA for evidence-grounded answer generation
```

**Index:** Full PubMed (~38M abstracts) in Qdrant

### RAG Architecture Components

#### Retrieval Strategies (Comparative Study 2026)
| Strategy | Composite Score | Contextual Precision | Best For |
|----------|----------------|---------------------|----------|
| Cross-Encoder Reranking | 0.827 | 0.852 | Highest precision |
| Dense Vector Search | 0.822 | 0.831 | General purpose |
| Hybrid BM25 + Dense | 0.825 | 0.843 | Balanced recall/precision |
| Multi-Query Expansion | 0.789 | 0.671 | Broad recall (but noisy) |
| MMR (Maximal Marginal Relevance) | 0.801 | 0.798 | Diversity |

**Key Finding:** Cross-Encoder Reranking achieves best composite score; Multi-Query Expansion introduces retrieval noise.

#### Embedding Models for Biomedical Text
- **PubMedBERT** - Domain-specific, trained on 21M PubMed abstracts
- **BiomedBERT** - Contrastive fine-tuning for biomedical retrieval
- **MedCPT** - Contrastive pre-trained for medical information retrieval
- **text-embedding-3-small** (OpenAI) - General purpose, works well with reranking

#### Chunking Strategies for Full-Text Articles
**Problem:** Standard metrics (MRR) reward precision but ignore retrieval breadth.

**GraLC-RAG (Graph-Aware Late Chunking):**
- Structure-aware chunk boundary detection
- UMLS knowledge graph infusion
- Graph-guided hybrid retrieval
- Retrieves from 15.6× more sections vs. content-similarity methods

**Finding:** Content-similarity methods achieve highest MRR (0.517) but retrieve from single section; structure-aware methods retrieve from up to 15.6× more sections.

### Hallucination Detection in Medical RAG
```python
# Claim extraction → NLI entailment → FactScore-style faithfulness
# ClinicalRAG approach:
#   1. Extract claims from generated answer
#   2. Verify each claim against retrieved evidence (NLI model)
#   3. Calculate faithfulness score
#   4. Flag or filter unsupported claims
```

**Results:** Hallucination rate reduced from 12.7% → 3.2%

## 6. Existing Python Libraries for PubMed Search

### Primary Libraries

#### BioPython (Most Mature)
```bash
pip install biopython
```
**Pros:**
- Comprehensive Entrez API wrapper
- Built-in XML/Medline parsers
- History server support for batch processing
- Rate limit handling
- Extensive documentation

**Cons:**
- Low-level API (requires manual query building)
- No built-in NLP/NER

#### metapub
```bash
pip install metapub
```
**Features:**
- Higher-level PubMed API wrapper
- Built-in PMID conversion tools
- Article metadata extraction

#### pubmed-parser
```bash
pip install pubmed-parser
```
**Features:**
- Parse PubMed XML/MEDLINE files
- Convert to structured formats (JSON, DataFrame)

### Integrated Solutions

#### RAGflow (Enterprise RAG Platform)
**Location:** `infiniflow/ragflow/agent/tools/pubmed.py`
```python
from Bio import Entrez
import xml.etree.ElementTree as ET

# Integrated PubMed tool in RAG pipeline
```

#### Biomni (Biomedical MCP Tools)
**Location:** `snap-stanford/Biomni/biomni/tool/example_mcp_tools/pubmed_mcp.py`
```python
from Bio import Entrez
from mcp.server.fastmcp import FastMCP

Entrez.email = os.getenv("NCBI_EMAIL")
mcp = FastMCP("pubmed-live")
```

#### PubMed Reporter (Natural Language → PubMed Query)
**Location:** `cxy15/PubMed-literature-search`
```bash
python -m pubmed_reporter -n 80 -o report.txt review "CRISPR gene editing recent advances"
```
**Features:**
- Natural language query → PubMed search string (LLM-powered)
- Authoritative journal filtering
- Relevance scoring
- Chinese language support

## 7. Best Practices Summary

### For Chinese Medical Query → PubMed Search Pipeline

```python
"""
Recommended architecture for rare disease genetic diagnosis Q&A:
"""

from openmed import analyze_text  # Medical NER
from Bio import Entrez  # PubMed search
from transformers import pipeline  # Translation

# Step 1: Extract medical entities from Chinese query
chinese_query = "罕见糖尿病并发症的最新治疗方法"
entities = analyze_text(chinese_query, model_name="disease_detection_superclinical")
# Extracts: 糖尿病 (diabetes), 并发症 (complications)

# Step 2: Translate entities with medical glossary
medical_glossary = {
    "糖尿病": "Diabetes Mellitus",
    "并发症": "Complications",
    "治疗": "Therapy"
}
english_query = translate_with_glossary(chinese_query, medical_glossary)
# Result: "Diabetes Mellitus Complications Therapy"

# Step 3: Build PubMed query with MeSH terms
pubmed_query = """
    (Diabetes Mellitus[MeSH Terms] OR diabetes[tiab]) 
    AND 
    (Complications[Subheading] OR complication[tiab])
    AND 
    (Therapeutics[MeSH Terms] OR treatment[tiab])
    AND 
    (2020:2026[dp])
"""

# Step 4: Search PubMed with rate limiting
Entrez.email = "your.email@example.com"
Entrez.api_key = "your_api_key"  # For 10 req/sec

handle = Entrez.esearch(
    db="pubmed",
    term=pubmed_query,
    retmax=50,
    sort="relevance"
)
record = Entrez.read(handle)
pmids = record["IdList"]

# Step 5: Fetch full records
fetch_handle = Entrez.efetch(
    db="pubmed",
    id=pmids[:20],  # Top 20
    rettype="medline",
    retmode="text"
)

# Step 6: Parse and process
from Bio import Medline
records = Medline.parse(fetch_handle)
for record in records:
    title = record.get("TI", "")
    abstract = record.get("AB", "")
    # Process for RAG...
```

### Rate Limiting and Error Handling
```python
import time
from functools import wraps
from urllib.error import HTTPError

def rate_limit(max_per_second=3):
    """Decorator for NCBI rate limiting"""
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
def safe_entrez_call(func, **kwargs):
    """Safe Entrez call with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(**kwargs)
        except HTTPError as e:
            if e.code == 429:
                time.sleep(10 * (attempt + 1))
            elif e.code >= 500:
                time.sleep(5 * (attempt + 1))
            else:
                raise
    raise Exception("Max retries exceeded")
```

### ACMG/Genomics-Specific Considerations
For rare disease genetic diagnosis:
1. **Gene names**: Use HGNC symbols (e.g., "BRCA1", "CFTR")
2. **Variant types**: Include terms like "mutation", "variant", "polymorphism"
3. **Inheritance patterns**: "autosomal dominant", "X-linked", etc.
4. **Phenotype terms**: Use HPO (Human Phenotype Ontology) terms
5. **Combine with clinical features**: Patient symptoms + gene name

Example query for rare disease:
```python
query = """
    (CFTR[Gene Name] OR "Cystic Fibrosis Transmembrane Conductance Regulator"[Gene Name])
    AND
    (mutation[tiab] OR variant[tiab] OR polymorphism[tiab])
    AND
    ("Cystic Fibrosis"[MeSH Terms] OR "cystic fibrosis"[tiab])
    AND
    (2020:2026[dp])
    AND
    (Clinical Trial[pt] OR Review[pt])
"""
```

## 8. Key Resources and Links

### Official Documentation
- NCBI E-utilities Guide: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- E-utilities Parameters: https://www.ncbi.nlm.nih.gov/books/NBK25499/
- MeSH Database: https://www.ncbi.nlm.nih.gov/mesh/
- PubMed Advanced Search: https://pubmed.ncbi.nlm.nih.gov/advanced/

### Python Libraries
- BioPython: https://biopython.org/
- OpenMed: https://github.com/maziyarpanahi/openmed
- Med7: https://github.com/kormilitzin/med7
- GLiNER-BioMed: https://github.com/ds4dh/GLiNER-biomed

### Research Papers (2026)
- "Benchmarking Retrieval Strategies for Biomedical RAG" (arXiv:2605.02520)
- "PubMed Reasoner: Dynamic Reasoning-based Retrieval" (arXiv:2603.27335)
- "Graph-Aware Late Chunking for Biomedical RAG" (arXiv:2603.22633)
- "Self-MedRAG: Iterative Medical QA" (arXiv:2601.04531)

### Chinese PubMed Tools
- Suppr (超能文献): https://suppr.wilddata.cn/
- MedCite: https://ai-bio.cn/medcite/
- EasyPubMed (Chrome Extension): https://github.com/naivenaive/EasyPubMed
