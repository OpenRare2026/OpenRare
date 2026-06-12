---
name: paper-search
description: >-
  Search and retrieve academic papers about genes, targets, and diseases using
  paper-search-mcp tools. Use when the user asks for literature, papers,
  publications, PubMed, arXiv, citations, or evidence from scientific articles.
---

# Paper Search

## Overview

This skill uses `paper-search-mcp` tools to find and read academic papers
relevant to gene and target research.

**Search tools return metadata + abstract, not full text.** Each hit includes
`paper_id`, `title`, `authors`, `abstract`, `doi`, `published_date`, `url`,
and optionally `pdf_url`. PubMed abstracts come from NCBI E-utilities; arXiv /
bioRxiv / medRxiv include preprint abstracts. Full text requires a separate
download/read step (PubMed does not support direct PDF read).

## Preferred tools

| Tool                    | When to use                                      |
| ----------------------- | ------------------------------------------------ |
| `search_papers`         | Broad multi-source search with deduplication     |
| `search_pubmed`         | Biomedical and clinical literature               |
| `search_arxiv`          | Preprints and computational biology              |
| `search_semantic_scholar` | Citation-aware metadata and open-access links  |
| `download_with_fallback`| Retrieve PDF when full text is needed          |
| `read_paper`            | Extract text from a downloaded paper             |

## Search strategy

Literature search is **required** for every gene/target research run as step 5
of the unified workflow (after Open Targets and ClinPGx). Run PubMed even when
the user does not explicitly ask for papers.

1. Build queries from resolved gene symbols and disease/context terms:
   - `"{gene_symbol}" AND (disease OR target OR association)`
   - Example: `"BRCA2" AND ("breast cancer" OR "DNA repair")`

2. For biomedical topics, prioritize PubMed and Europe PMC sources.

3. Start with `search_papers` for a broad sweep; use source-specific tools
   when you need finer control.

4. Use `max_results=3` by default for PubMed; add arXiv when relevant.

## Full-text workflow

When the user needs paper content or detailed evidence:

1. Pick the most relevant result with a DOI or open-access link.
2. Call `download_with_fallback` with the paper metadata.
3. Call `read_paper` on the downloaded file to extract text.
4. Quote or summarize only the sections relevant to the user's question.

## Configuration notes

- `PAPER_SEARCH_MCP_UNPAYWALL_EMAIL` is required for Unpaywall DOI lookups.
- `PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY` is optional but improves rate limits.

## Output format

For each paper, include:

- Title
- Authors (first author et al. is fine)
- Year (from `published_date`)
- Source / journal (`source` field: pubmed, arxiv, etc.)
- DOI or URL
- Brief summary from the returned **abstract** (do not claim full-text access
  unless you ran `read_*_paper`)
- One-line relevance note

End with a brief synthesis of how the papers support or contradict the
gene/target findings from Open Targets data.
