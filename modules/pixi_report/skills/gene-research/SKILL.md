---
name: gene-research
description: >-
  Investigate genes, drug targets, treatments, disease associations,
  pharmacogenomics, and literature. Use when the user asks about gene symbols,
  ENSG IDs, targets, drug targets, drugs, therapies, disease links, PGx, or
  Open Targets.
---

# Gene Research

## Overview

Every gene query must use **all three data sources**:

| Source | Tools | What it provides |
| ------ | ----- | ---------------- |
| Open Targets | `lookup_gene`, `get_gene_disease_associations`, `search_gene_drugs`, `get_gene_drug_details`, `get_drug_details` | Ensembl ID, disease links, related drugs with full profiles |
| ClinPGx local | `get_gene_pgx_profile` | PGx guidelines, allele effects, evidence levels |
| Literature | `paper_search_search_pubmed` (+ optional arXiv) | Paper metadata + abstracts |

Do **not** call raw GraphQL MCP tools (`query_open_targets_graphql` is not
available).

## Mandatory workflow

Run all steps for every query. Do not pick a subset based on the question type.

### 1. Resolve gene identifiers (Open Targets)

Call `lookup_gene` with the gene symbol (e.g. `BRCA2`).

Returns `ensembl_id` (e.g. `ENSG00000139618`).

### 2. Query target-disease associations (Open Targets)

Call `get_gene_disease_associations` with the Ensembl ID from step 1.

Use `limit=5` by default.

### 3. Query related drugs / treatments (Open Targets)

Call `get_gene_drug_details` with the gene symbol (`limit=5` by default).

This returns clinical stage, indications, mechanisms of action, adverse events,
gene-filtered pharmacogenomics, and PubMed references (title + DOI).

Use `search_gene_drugs` only when you need a lightweight drug name list.
Use `get_drug_details` when you already have a specific ChEMBL ID.

Optional `drug_hint` for narrowing (e.g. `"PARP inhibitor"` for BRCA2).

### 4. Query pharmacogenomics profile (ClinPGx)

Call `get_gene_pgx_profile` with the gene symbol.

If the gene has no ClinPGx entry, note that and continue.

### 5. Literature evidence (PubMed)

Always call `paper_search_search_pubmed` (`max_results=3`).

Add `paper_search_search_arxiv` when the topic has computational or preprint
angles.

Build the query from the gene symbol plus top disease/drug terms from steps
2–4 (e.g. `"TPMT" AND (pharmacogenomics OR azathioprine)`).

### 6. Summarize results

1. **Gene**: symbol, Ensembl ID
2. **Disease associations**: top diseases with scores
3. **Drugs / treatments**: names, ChEMBL IDs, clinical stage, indications, MOA,
   adverse events, Open Targets PGx, references
4. **Pharmacogenomics**: key drugs, guidelines, allele effects
5. **Literature**: titles, authors, year, URLs, brief abstract summary

## Entity ID reference

| Entity   | ID format       | Example                         |
| -------- | --------------- | ------------------------------- |
| Target   | ENSEMBL gene ID | `ENSG00000139618` (BRCA2)       |
| Disease  | EFO / MONDO ID  | `MONDO_0007254` (breast cancer) |
| Drug     | ChEMBL ID       | `CHEMBL521686` (olaparib)       |
