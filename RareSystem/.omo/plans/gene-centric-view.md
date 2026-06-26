# Gene-Centric Variants View

## TL;DR

> **Quick Summary**: Add a gene-centric view to the variants display, complementing the existing variant-centric view. Users can toggle between views, see gene-level summaries with annotations, and expand/filter to see variants per gene.
> 
> **Deliverables**:
> - Backend: Gene aggregation API endpoint, gene info annotation service
> - Frontend: GeneView component with expandable rows, tab toggle between variant/gene view
> - Gene annotations: Description, disease associations, inheritance patterns from external APIs
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 → Task 3-4 → Task 5-6

---

## Context

### Original Request
现在在variants里面，都是按照一个变异为一个维度来做展示的，这个继续保留。还希望可以按照一个基因，一行来展示，相关的信息也可以保存进来。

### User Decisions
- **View mode**: Both - expandable rows inline AND filter variant list when clicking gene
- **Gene info**: With annotations - include gene description, disease associations, inheritance patterns from external APIs

### Current Architecture

**Existing:**
- `Variant.gene` field (String, indexed) stores gene symbol
- `GeneLookupService` maps coordinates → gene names via GFF3
- `VariantList.tsx` shows one row per variant
- Gene filtering exists (search by gene name)
- No gene grouping or gene-centric view

**Missing:**
- No gene aggregation API
- No gene metadata storage
- No gene-centric UI component
- No external gene annotation integration

---

## Work Objectives

### Core Objective
Enable users to view variants grouped by gene, with gene-level annotations and summaries, while preserving the existing variant-centric view.

### Concrete Deliverables

**Backend:**
1. `backend/api/genes.py` - New gene endpoints
2. `backend/services/gene_info_service.py` - Gene annotation service (OMIM, HGNC, etc.)
3. `backend/database/models.py` - Optional: GeneInfo cache table

**Frontend:**
1. `frontend/src/components/GeneView.tsx` - Gene-centric variant list with expandable rows
2. `frontend/src/components/GeneView/GeneExpandableRow.tsx` - Expanded row showing variants
3. `frontend/src/components/VariantList.tsx` - Add tab toggle
4. `frontend/src/types.ts` - GeneView, GeneInfo types
5. `frontend/src/services/api.ts` - Gene API methods

### Definition of Done
- [ ] Users can toggle between "Variant View" and "Gene View" tabs
- [ ] Gene View shows one row per gene with variant count, types, classifications
- [ ] Gene rows are expandable to show all variants inline
- [ ] Clicking gene name filters the variant list to that gene
- [ ] Gene annotations (description, diseases, inheritance) are displayed
- [ ] Gene info is fetched from external APIs and cached

---

## TODOs

- [ ] 1. Backend: Gene Aggregation API

  **What to do**:
  - Create `backend/api/genes.py` with router (prefix="/genes"):
    - `GET /api/genes/{vcf_file_id}` - List genes with variant summaries
      - Group variants by gene
      - Return: gene name, variant count, variant types distribution, ACMG classifications, max gnomAD AF
    - `GET /api/genes/{vcf_file_id}/{gene_name}` - Get all variants for a gene
    - `GET /api/genes/info/{gene_name}` - Get gene info (with external annotation)
  - Query pattern:
    ```python
    from sqlalchemy import func
    genes = db.query(
        Variant.gene,
        func.count(Variant.id).label('variant_count')
    ).filter(
        Variant.vcf_file_id == vcf_file_id,
        Variant.gene.isnot(None)
    ).group_by(Variant.gene).all()
    ```

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Tasks 3, 5

  **References**:
  - `backend/services/variant_service.py:546-570` - Count by chromosome/type patterns
  - `backend/api/variants.py:160-199` - Variant list endpoint pattern

  **Acceptance Criteria**:
  - [ ] `GET /api/genes/{vcf_file_id}` returns gene summaries
  - [ ] `GET /api/genes/{vcf_file_id}/{gene_name}` returns variants for gene
  - [ ] Endpoint works with existing variant data

  **QA Scenarios**:
  ```
  Scenario: Gene aggregation endpoint returns correct counts
    Tool: Bash
    Steps:
      1. Run: curl -s http://localhost:8080/api/genes/1 | python3 -c "
         import sys, json
         data = json.load(sys.stdin)
         print(f'Gene count: {len(data[\"genes\"])}')
         for g in data['genes'][:3]:
             print(f'  {g[\"gene\"]}: {g[\"variant_count\"]} variants')
         print('PASS')
         "
    Expected: Gene list with counts
  ```

  **Commit**: YES (Wave 1)
  - Message: `feat(genes): add gene aggregation API endpoints`

- [ ] 2. Backend: Gene Info Annotation Service

  **What to do**:
  - Create `backend/services/gene_info_service.py`:
    - `GeneInfoService` class with methods:
      - `get_gene_info(gene_name: str) -> GeneInfo` - Fetch gene annotation
      - `_fetch_from_hgnc(gene_name)` - Query HGNC API for gene info
      - `_fetch_from_omim(gene_name)` - Query OMIM API (if key available)
      - `_fetch_from_ncbi(gene_name)` - Query NCBI Gene database
    - `GeneInfo` dataclass:
      - symbol, name, description, chromosome, location
      - omim_id, hgnc_id, ensembl_id
      - diseases: List[str] - Associated diseases
      - inheritance: List[str] - Inheritance patterns (AD, AR, XL, etc.)
    - Caching: Store in memory with TTL (24h), optionally in DB
  - Optional: Add `GeneInfoCache` table for persistence
  - Use free APIs (HGNC, NCBI) - OMIM requires license

  **External APIs**:
  - HGNC REST API: `https://rest.genename.org/fetch/symbol/{symbol}`
  - NCBI Gene: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
  - MyGene.info: `https://mygene.info/v3/gene/{gene_id}` (aggregates multiple sources)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Tasks 3, 5

  **References**:
  - `backend/services/gene_lookup.py` - Singleton pattern to follow
  - `backend/services/llm_client.py` - External API patterns

  **Acceptance Criteria**:
  - [ ] GeneInfoService fetches gene info from external APIs
  - [ ] Handles missing genes gracefully
  - [ ] Caches results

  **QA Scenarios**:
  ```
  Scenario: Gene info service fetches BRCA1 info
    Tool: Bash
    Steps:
      1. Run: cd backend && python -c "
         from services.gene_info_service import GeneInfoService
         svc = GeneInfoService()
         info = svc.get_gene_info('BRCA1')
         print(f'Symbol: {info.symbol}')
         print(f'Name: {info.name}')
         print(f'Inheritance: {info.inheritance}')
         print('PASS')
         "
    Expected: Gene info returned
  ```

  **Commit**: YES (Wave 1)
  - Message: `feat(genes): add gene info annotation service with external APIs`

- [ ] 3. Frontend: Gene Types and API Methods

  **What to do**:
  - Add to `frontend/src/types.ts`:
    ```typescript
    export interface GeneSummary {
      gene: string
      variant_count: number
      variant_types: { type: string; count: number }[]
      classifications: { classification: string; count: number }[]
      max_gnomad_af: number | null
      chromosomes: string[]
    }

    export interface GeneInfo {
      symbol: string
      name: string
      description: string
      chromosome: string
      location: string
      omim_id: string | null
      hgnc_id: string | null
      diseases: string[]
      inheritance: string[]
    }
    ```
  - Add to `frontend/src/services/api.ts`:
    - `getGenes(vcfFileId: string)` - Get gene summaries
    - `getGeneVariants(vcfFileId: string, geneName: string)` - Get variants for gene
    - `getGeneInfo(geneName: string)` - Get gene annotation info

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Tasks 5, 6
  - **Blocked By**: Tasks 1, 2

  **Commit**: YES (Wave 2)
  - Message: `feat(types): add gene view types and API methods`

- [ ] 4. Frontend: GeneExpandableRow Component

  **What to do**:
  - Create `frontend/src/components/GeneView/GeneExpandableRow.tsx`:
    - Props: `{ gene: GeneSummary; geneInfo?: GeneInfo; variants: Variant[]; onVariantSelect: (v: Variant) => void }`
    - Shows collapsed gene row with summary
    - Expandable section shows:
      - Gene info panel (if loaded): description, diseases, inheritance
      - Mini variant table (Position, Change, Type, Classification, gnomAD AF)
      - Click variant → trigger onVariantSelect
    - Loading state for gene info
    - Ant Design Collapse/Table for layout

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 3)
  - **Blocks**: Task 5
  - **Blocked By**: Tasks 1, 2

  **References**:
  - `frontend/src/components/VariantList.tsx:97-229` - Column definitions to reuse
  - `frontend/src/components/SkillCard.tsx` - Card styling pattern

  **Commit**: YES (Wave 2)
  - Message: `feat(ui): add GeneExpandableRow component`

- [ ] 5. Frontend: GeneView Component

  **What to do**:
  - Create `frontend/src/components/GeneView.tsx`:
    - Props: `{ vcfFileId: string; onVariantSelect: (v: Variant) => void; onGeneFilter: (gene: string) => void }`
    - Main gene table with columns:
      - Gene (clickable → filter variant list)
      - Variant Count
      - Types (Tags)
      - Classifications (Tags)
      - Max gnomAD AF
      - Action (expand)
    - Expandable rows using GeneExpandableRow
    - Search/filter by gene name
    - Pagination
    - Sort by variant count

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 6)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 3, 4

  **References**:
  - `frontend/src/components/VariantList.tsx` - Same structure to follow
  - Ant Design Table expandable rows: https://ant.design/components/table#components-table-demo-expand

  **Commit**: YES (Wave 3)
  - Message: `feat(ui): add GeneView component with expandable rows`

- [ ] 6. Frontend: Integrate Gene View into AnalysisPage

  **What to do**:
  - Modify `frontend/src/pages/AnalysisPage.tsx`:
    - Change "Variants" tab to have sub-tabs or toggle: "By Variant" | "By Gene"
    - Or add new "Gene View" tab
    - Wire up GeneView component
    - Implement `onGeneFilter` → switch to Variant tab with gene filter applied
  - Modify `frontend/src/components/VariantList.tsx`:
    - Accept `initialGeneFilter` prop
    - Pre-fill gene filter when switching from Gene View

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (after Task 5)
  - **Blocked By**: Task 5

  **References**:
  - `frontend/src/pages/AnalysisPage.tsx:248-277` - Tab structure

  **Commit**: YES (Wave 3)
  - Message: `feat(ui): integrate gene view with toggle in analysis page`

---

## UI Mockup

```
┌─────────────────────────────────────────────────────────────────────┐
│ Variants │ Visualization │ Reports │                               │
│         ┌─────────────────────────────────────────┐                │
│         │ [Variant View] [Gene View]              │  ← Toggle      │
│         ├─────────────────────────────────────────┤                │
│         │ Search: [________] [Clear]              │                │
│         ├─────────────────────────────────────────┤                │
│         │ Gene     │ # │ Types      │ Class. │ AF │ Action       │
│         ├──────────┼───┼────────────┼────────┼────┼───────────────┤
│         │ BRCA1    │ 3 │ SNV INDEL  │ Path   │ 0% │ [▼ Expand]   │
│         ├──────────┴───┴────────────┴────────┴────┴───────────────┤
│         │ ▼ BRCA1 Details                                           │
│         │ ┌─────────────────────────────────────────────────────┐ │
│         │ │ BRCA1 - BRCA1 DNA repair associated                  │ │
│         │ │ Inheritance: AD | OMIM: 113705                       │ │
│         │ │ Diseases: Hereditary breast and ovarian cancer       │ │
│         │ ├─────────────────────────────────────────────────────┤ │
│         │ │ Pos        │ Change   │ Type │ Class. │ gnomAD    │ │
│         │ │ chr17:1234 │ A>G      │ SNV  │ Path   │ 0.001%    │ │
│         │ │ chr17:5678 │ del5     │ INDEL│ VUS    │ -         │ │
│         │ │ chr17:9012 │ C>T      │ SNV  │ VUS    │ 0.0001%   │ │
│         │ └─────────────────────────────────────────────────────┘ │
│         ├──────────┬───┬────────────┬────────┬────┬───────────────┤
│         │ TP53     │ 1 │ SNV        │ VUS    │ 0% │ [▶ Expand]   │
│         ├──────────┼───┼────────────┼────────┼────┼───────────────┤
│         │ CFTR     │ 2 │ SNV        │ Likely │ 2% │ [▶ Expand]   │
│         └──────────┴───┴────────────┴────────┴────┴───────────────┘
└─────────────────────────────────────────────────────────────────────┘
```

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - Backend):
├── Task 1: Gene aggregation API [quick]
└── Task 2: Gene info annotation service [unspecified-high]

Wave 2 (Frontend Scaffolding):
├── Task 3: Gene types and API methods [quick]
└── Task 4: GeneExpandableRow component [visual-engineering]

Wave 3 (Integration):
├── Task 5: GeneView component [visual-engineering]
└── Task 6: AnalysisPage integration [visual-engineering]

Critical Path: Task 1-2 → Task 3-4 → Task 5 → Task 6
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | - | 3, 5 | 1 |
| 2 | - | 3, 4, 5 | 1 |
| 3 | 1, 2 | 5, 6 | 2 |
| 4 | 2 | 5 | 2 |
| 5 | 3, 4 | 6 | 3 |
| 6 | 5 | - | 3 |

---

## Success Criteria

### Verification Commands
```bash
# Backend API test
curl http://localhost:8080/api/genes/1 | python3 -m json.tool

# Gene info test
curl http://localhost:8080/api/genes/info/BRCA1 | python3 -m json.tool

# Frontend build
cd frontend && npm run build
```

### Final Checklist
- [ ] Gene aggregation API returns correct summaries
- [ ] Gene info service fetches from external APIs
- [ ] Gene View shows genes with expandable rows
- [ ] Clicking gene filters variant list
- [ ] Gene info (description, diseases, inheritance) displays correctly
- [ ] Toggle between Variant/Gene views works
- [ ] Frontend build succeeds
