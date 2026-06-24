# LLM Prompt Templates

This directory contains all LLM prompts used in the rare disease genetic diagnosis system.

## Directory Structure

```
backend/prompts/
├── __init__.py           # Main exports
├── rag_prompts.py        # Case Q&A prompts
├── skill_prompts.py      # Skill-specific prompts
├── pubmed_prompts.py     # PubMed literature prompts
└── README.md             # This file
```

## Prompt Categories

### 1. RAG Prompts (`rag_prompts.py`)

**Usage Context:**
- **Used by:** `backend/services/rag_service.py`
- **Purpose:** Generate answers for case-related questions using retrieved context
- **When:** User asks a question in Case Q&A interface

**Prompts:**
| Prompt Name | Description |
|-------------|-------------|
| `RAG_SYSTEM_PROMPT` | System prompt for clinical genetics assistant |
| `RAG_CONTEXT_TEMPLATE` | Template for formatting retrieved context |
| `build_rag_prompt()` | Function to build complete RAG prompt |

**Flow:**
```
User Question → RAGService._build_rag_prompt() → LLM → Answer with Citations
```

---

### 2. Skill Prompts (`skill_prompts.py`)

**Usage Context:**
- **Used by:** `backend/services/skills/*.py`
- **Purpose:** Provide specialized prompts for different analysis skills
- **When:** User invokes a specific skill via "/" command in ChatInterface

**Prompts:**
| Prompt Name | Skill | Description |
|-------------|-------|-------------|
| `ACMG_CLASSIFICATION_PROMPT` | `/acmg_classification` | Apply ACMG/AMP criteria for variant classification |
| `PHENOTYPE_MATCHING_PROMPT` | `/phenotype_matching` | Analyze phenotype-genotype correlations |
| `PEDIGREE_ANALYSIS_PROMPT` | `/pedigree_analysis` | Analyze family history and inheritance patterns |

**Skills Overview:**

#### ACMG Classification Skill
- **File:** `backend/services/skills/acmg_skill.py`
- **Trigger:** User asks about variant pathogenicity
- **Output:** Systematic ACMG classification with criteria evaluation

#### Phenotype Matching Skill
- **File:** `backend/services/skills/phenotype_skill.py`
- **Trigger:** User asks about gene-phenotype associations
- **Output:** Ranked list of candidate genes with evidence

#### Pedigree Analysis Skill
- **File:** `backend/services/skills/pedigree_skill.py`
- **Trigger:** User asks about family history
- **Output:** Inheritance pattern determination and recurrence risks

---

### 3. PubMed Prompts (`pubmed_prompts.py`)

**Usage Context:**
- **Used by:** `backend/services/skills/pubmed_search_skill.py`
- **Purpose:** Literature search and answer synthesis
- **When:** User searches PubMed or asks literature-related questions

**Prompts:**
| Prompt Name | Description |
|-------------|-------------|
| `QUERY_DECOMPOSITION_PROMPT` | Convert user questions to PubMed search queries |
| `ANSWER_SYNTHESIS_PROMPT` | Generate citation-based answers from abstracts |

**Flow:**
```
User Question (Chinese)
    ↓
QUERY_DECOMPOSITION_PROMPT → PubMed Query (English + MeSH)
    ↓
NCBI E-utilities API → Abstracts
    ↓
ANSWER_SYNTHESIS_PROMPT → Answer with PMID Citations
```

---

## How to Modify Prompts

### Option 1: Direct File Edit
Edit the prompt strings in the corresponding `.py` files.

### Option 2: Runtime Configuration (for skills)
Use the Settings API to customize prompts per skill:
```bash
PUT /api/skills/config/{skill_name}
{
  "config": {
    "query_decomposition_prompt": "your custom prompt...",
    "answer_synthesis_prompt": "your custom prompt..."
  }
}
```

---

## Prompt Variables

Most prompts support variable substitution:

| Variable | Description | Example |
|----------|-------------|---------|
| `{query}` | User's question | "What genes are associated with BRCA1?" |
| `{case_context}` | Patient/case information | "Patient: 35yo female, diagnosis: breast cancer" |
| `{context}` | Retrieved context | "[Patient Info]: ... [Variants]: ..." |
| `{history}` | Conversation history | "Q: ... A: ..." |

---

## Adding New Prompts

1. Create prompt constant in appropriate file:
```python
NEW_PROMPT = """Your prompt here with {variables}."""
```

2. Export in `__init__.py`:
```python
from .your_file import NEW_PROMPT

__all__ = [..., "NEW_PROMPT"]
```

3. Use in service:
```python
from prompts import NEW_PROMPT

prompt = NEW_PROMPT.format(variable=value)
```

---

## Best Practices

1. **Keep prompts focused** - Each prompt should have a single clear purpose
2. **Use variables** - Make prompts reusable with variable substitution
3. **Document usage** - Add comments explaining when/where each prompt is used
4. **Version control** - Track prompt changes in git for reproducibility
5. **Test changes** - Verify prompt modifications don't break existing functionality

---

## Related Files

| File | Purpose |
|------|---------|
| `backend/services/rag_service.py` | RAG service using RAG prompts |
| `backend/services/skills/acmg_skill.py` | ACMG classification skill |
| `backend/services/skills/phenotype_skill.py` | Phenotype matching skill |
| `backend/services/skills/pedigree_skill.py` | Pedigree analysis skill |
| `backend/services/skills/pubmed_search_skill.py` | PubMed search skill |
| `backend/services/llm_client.py` | LLM API client |
