# VEP API Integration Plan

## TL;DR

> **Quick Summary**: Integrate external VEP API for variant annotation — upload VCF to VEP, poll async job, parse CSV results, populate variant table with VEP-annotated data. Fallback to current pysam+GFF3 parsing when VEP unavailable.
> 
> **Deliverables**:
> - VEP API service client (submit job, poll status, parse CSV)
> - VEPJob database model for job persistence
> - Extended Variant model with VEP fields (hgvs, consequence, impact)
> - Modified upload flow: VEP-first with pysam fallback
> - Frontend: VEP options in upload form + loading state
> - Configurable VEP API base URL via .env
> - Pytest tests for VEP service and CSV parsing
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 1 (config) → Task 2 (DB schema) → Task 4 (VEP service) → Task 5 (upload integration) → Task 7 (frontend) → Task 9 (tests) → F1-F4

---

## Context

### Original Request
上传VCF之后，需要把VCF发送给一个VEP API（`POST /runs`），得到job_id后轮询结果，从result_url获取CSV，替代目前的variants表格。

### Interview Summary
**Key Discussions**:
- VEP API on separate server (port 8000): No conflict with our backend
- Configurable base URL via .env
- VEP options: hgvs, no_pick, format, fork (user selectable)
- Async polling: simple loading spinner in frontend
- Fallback: keep current pysam+GFF3 parsing as degradation path
- Timeout: 10 minutes
- VEP job info persisted to database

**Research Findings**:
- Frontend VariantList already has empty `consequence` and `hgvs_p` columns — VEP fills them
- Backend upload at variants.py:56-158, integration point at lines 83-86
- Current gene annotation (gene_lookup.py) is minimal: only gene symbol from GFF3
- Database Variant model missing: hgvs_c, hgvs_p, consequence, impact columns

### Gap Analysis (self-conducted, Metis unavailable)
**Identified Gaps** (addressed):
- VEP CSV format unknown → Runtime CSV parsing with header detection
- VEP API may not require auth → Default no auth, but config allows API key
- Polling interval not specified → Default 5 seconds, configurable
- Concurrent VEP jobs → Allow one active job per VCF file, reject duplicates
- VEP returns empty results → Treat as success with 0 variants, show message

---

## Work Objectives

### Core Objective
After VCF upload, send the file to a configurable VEP API, poll for completion, parse the CSV result, and update the variant table with VEP-annotated data. Fall back to current pysam+GFF3 annotation if VEP is unavailable or times out.

### Concrete Deliverables
- `backend/services/vep_service.py` — VEP API client
- `backend/database/models.py` — Extended Variant + new VEPJob model
- `backend/api/variants.py` — Modified upload flow with VEP integration
- `backend/config.py` or `.env` — VEP_API_BASE_URL, VEP_TIMEOUT, VEP_POLL_INTERVAL
- `frontend/src/components/VCFUpload.tsx` — VEP options UI
- `frontend/src/services/api.ts` — VEP status polling endpoint
- `backend/tests/test_vep_service.py` — Unit tests for VEP service
- `backend/tests/test_vep_csv_parser.py` — Unit tests for CSV parsing

### Definition of Done
- [ ] VCF upload submits file to VEP API and receives job_id
- [ ] Backend polls VEP job status until complete (max 10 min)
- [ ] VEP CSV parsed and variant records updated in database
- [ ] Frontend shows loading spinner during VEP processing
- [ ] When VEP unavailable, upload falls back to current pysam+GFF3 path
- [ ] VEP options (hgvs, no_pick, format, fork) configurable in upload form
- [ ] VEP job info persisted to database
- [ ] VEP_API_BASE_URL configurable via .env
- [ ] All pytest tests pass

### Must Have
- VEP API integration (submit, poll, parse, update)
- Fallback to current parsing on VEP failure/timeout
- Configurable VEP API base URL
- VEP job persistence (job_id, status, log_url)
- VEP options in upload form
- Loading indicator during VEP processing
- Variant table populated with VEP-annotated data

### Must NOT Have (Guardrails)
- NO changes to ACMG classification logic
- NO changes to WebSocket chat interface
- NO changes to patient management
- NO local VEP installation
- NO Redis/caching layer (keep simple)
- NO VEP batch optimization beyond what the API supports
- NO modification of Docker deployment configuration
- NO AI slop: over-abstraction, excessive comments, generic utility classes

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: YES (tests-after)
- **Framework**: pytest
- **Test files**: `backend/tests/test_vep_service.py`, `backend/tests/test_vep_csv_parser.py`

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Backend API**: Use Bash (curl) — Send requests, assert status + response fields
- **Frontend/UI**: Use Playwright — Navigate, interact, assert DOM, screenshot
- **Service logic**: Use Bash (pytest) — Run tests, check pass/fail

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation):
├── Task 1: VEP config + .env setup [quick]
├── Task 2: VEPJob DB model + migration [quick]
├── Task 3: Extend Variant DB model with VEP fields [quick]
├── Task 4: VEP service client — submit + poll + parse [deep]
└── Task 5: CSV parser for VEP output (unknown format) [deep]

Wave 2 (After Wave 1 — core integration):
├── Task 6: Modify upload endpoint — VEP-first with fallback [deep]
├── Task 7: VEP options UI in upload form [visual-engineering]
├── Task 8: VEP job status API endpoint [quick]
└── Task 9: Frontend loading state + VEP polling [visual-engineering]

Wave 3 (After Wave 2 — validation + polish):
├── Task 10: Pytest tests for VEP service [unspecified-high]
├── Task 11: Pytest tests for CSV parser [unspecified-high]
└── Task 12: Integration test — full VEP upload flow [deep]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
→ Present results → Get explicit user okay

Critical Path: Task 1 → Task 2 → Task 4 → Task 6 → Task 9 → Task 12 → F1-F4
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 5 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | - | 4, 6, 8 | 1 |
| 2 | 1 | 4, 6, 8 | 1 |
| 3 | 1 | 4, 6 | 1 |
| 4 | 1, 2, 3 | 6, 8, 10 | 1 |
| 5 | 1 | 4, 6, 11 | 1 |
| 6 | 2, 3, 4, 5 | 12 | 2 |
| 7 | - | 9 | 2 |
| 8 | 2, 4 | 9 | 2 |
| 9 | 7, 8 | 12 | 2 |
| 10 | 4 | F2 | 3 |
| 11 | 5 | F2 | 3 |
| 12 | 6, 9 | F3 | 3 |

### Agent Dispatch Summary

- **Wave 1**: 5 tasks — T1 → `quick`, T2 → `quick`, T3 → `quick`, T4 → `deep`, T5 → `deep`
- **Wave 2**: 4 tasks — T6 → `deep`, T7 → `visual-engineering`, T8 → `quick`, T9 → `visual-engineering`
- **Wave 3**: 3 tasks — T10 → `unspecified-high`, T11 → `unspecified-high`, T12 → `deep`
- **FINAL**: 4 tasks — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. VEP Configuration + Environment Setup

  **What to do**:
  - Add VEP config fields to `backend/config.py` or equivalent config module:
    - `VEP_API_BASE_URL` (default: `http://127.0.0.1:8000`)
    - `VEP_TIMEOUT_SECONDS` (default: `600` = 10 minutes)
    - `VEP_POLL_INTERVAL_SECONDS` (default: `5`)
    - `VEP_ENABLED` (default: `True`)
    - `VEP_API_KEY` (optional, default: empty)
  - Add these to `backend/.env.example` with comments
  - Add Pydantic Settings class for VEP config if project uses pydantic-settings

  **Must NOT do**:
  - Don't modify existing config fields
  - Don't add Redis or caching config

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small config addition, well-defined scope
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - `customize-opencode`: Not opencode config

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4, 6, 8
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `backend/config.py` — Existing config pattern (how settings are loaded, what framework is used)
  - `backend/.env.example` — Existing .env format and variable naming convention

  **API/Type References**:
  - `backend/main.py:1-20` — How config is imported and used in app startup

  **WHY Each Reference Matters**:
  - `backend/config.py`: Must match existing config loading pattern (dotenv, pydantic-settings, or os.environ)
  - `backend/.env.example`: Must follow existing variable naming and comment style

  **Acceptance Criteria**:
  - [ ] VEP config fields defined in config module
  - [ ] `.env.example` updated with VEP variables and comments
  - [ ] Backend starts without errors with new config

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: VEP config loaded from .env
    Tool: Bash (curl)
    Preconditions: Backend running with VEP_API_BASE_URL set in .env
    Steps:
      1. Start backend with VEP_API_BASE_URL=http://test-vep:8000 in .env
      2. curl -s http://localhost:8000/api/health
      3. Verify response is {"status":"healthy"}
    Expected Result: Backend starts successfully, VEP config available
    Failure Indicators: Backend fails to start, import error
    Evidence: .sisyphus/evidence/task-1-config-loaded.txt

  Scenario: Missing VEP config uses defaults
    Tool: Bash (curl)
    Preconditions: Backend running WITHOUT VEP_API_BASE_URL in .env
    Steps:
      1. Remove VEP_API_BASE_URL from .env (or use clean env)
      2. Start backend
      3. curl -s http://localhost:8000/api/health
    Expected Result: Backend starts, uses default VEP_API_BASE_URL=http://127.0.0.1:8000
    Failure Indicators: Backend fails to start due to missing required config
    Evidence: .sisyphus/evidence/task-1-config-defaults.txt
  ```

  **Commit**: YES (groups with 2, 3)
  - Message: `feat(vep): add VEP configuration and database schema`
  - Files: `backend/config.py`, `backend/.env.example`
  - Pre-commit: `cd backend && python -c "from config import settings; print(settings.vep_api_base_url)"`

- [x] 2. VEPJob Database Model + Migration

  **What to do**:
  - Add `VEPJob` model to `backend/database/models.py`:
    - `id` (Integer, primary key)
    - `job_id` (String, unique, VEP job identifier)
    - `vcf_file_id` (Integer, FK to vcf_files)
    - `status` (String: queued/running/completed/failed/timeout)
    - `input_filename` (String)
    - `input_bytes` (Integer)
    - `options` (JSON: {hgvs, no_pick, format, fork, etc.})
    - `status_url` (String)
    - `result_url` (String)
    - `log_url` (String)
    - `rows` (Integer, nullable)
    - `error` (String, nullable)
    - `created_at` (DateTime)
    - `updated_at` (DateTime)
  - Create Alembic migration for VEPJob table
  - Add `vep_job_id` column to `VCFFile` model (optional link to latest VEP job)

  **Must NOT do**:
  - Don't modify existing Variant or Patient tables (that's Task 3)
  - Don't add Redis or caching tables

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single model addition, follows existing DB patterns
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 3)
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Tasks 4, 6, 8
  - **Blocked By**: Task 1 (needs config for field naming consistency)

  **References**:

  **Pattern References**:
  - `backend/database/models.py:37-55` — VCFFile model pattern (column types, nullable, ForeignKey)
  - `backend/database/models.py:57-88` — Variant model pattern (index, Column definitions)

  **API/Type References**:
  - VEP API response JSON: `{"job_id": "...", "status": "queued", "status_url": "/runs/{id}", "result_url": "/runs/{id}/result", "log_url": "/runs/{id}/log", "rows": null, "error": null}`

  **WHY Each Reference Matters**:
  - `models.py:37-55`: Must match existing column definition style (String lengths, nullable patterns, DateTime defaults)
  - VEP response JSON: Fields map 1:1 to model columns

  **Acceptance Criteria**:
  - [ ] VEPJob model defined in models.py with all fields
  - [ ] Alembic migration created and applies cleanly
  - [ ] `from database.models import VEPJob` works without error

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: VEPJob model creation
    Tool: Bash
    Preconditions: Database accessible
    Steps:
      1. cd backend && alembic upgrade head
      2. python -c "from database.models import VEPJob; print(VEPJob.__tablename__)"
    Expected Result: Output: "vep_jobs"
    Failure Indicators: Import error, migration failure
    Evidence: .sisyphus/evidence/task-2-vepjob-model.txt

  Scenario: Migration idempotency
    Tool: Bash
    Preconditions: Database at current head
    Steps:
      1. cd backend && alembic downgrade -1
      2. alembic upgrade head
    Expected Result: Both commands succeed without error
    Failure Indicators: Migration conflict, table already exists
    Evidence: .sisyphus/evidence/task-2-migration-idempotent.txt
  ```

  **Commit**: YES (groups with 1, 3)
  - Message: `feat(vep): add VEP configuration and database schema`
  - Files: `backend/database/models.py`, `backend/alembic/versions/`

- [x] 3. Extend Variant Database Model with VEP Fields

  **What to do**:
  - Add columns to `Variant` model in `backend/database/models.py`:
    - `hgvs_c` (String(255), nullable=True) — c.DNA HGVS notation
    - `hgvs_p` (String(255), nullable=True) — p.Protein HGVS notation
    - `consequence` (String(200), nullable=True) — VEP consequence term (e.g., "missense_variant")
    - `impact` (String(50), nullable=True) — VEP impact (HIGH/MODERATE/LOW/MODIFIER)
    - `canonical_transcript` (String(50), nullable=True) — Ensembl transcript ID
    - `sift` (String(50), nullable=True) — SIFT prediction + score
    - `polyphen` (String(50), nullable=True) — PolyPhen prediction + score
    - `cadd` (Float, nullable=True) — CADD score
    - `vep_annotated` (Boolean, default=False) — Flag: was this annotated by VEP?
  - Create Alembic migration for new columns (ALTER TABLE ADD COLUMN)
  - Update `VariantResponse` schema in `backend/api/variants.py` to include new fields
  - Update frontend `Variant` interface in `frontend/src/types/index.ts` to include new fields

  **Must NOT do**:
  - Don't drop or rename existing columns
  - Don't change existing data (new columns are all nullable)
  - Don't modify the VariantList component logic (that's Task 9)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding nullable columns, straightforward migration
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 4, 6
  - **Blocked By**: Task 1 (needs config for consistency)

  **References**:

  **Pattern References**:
  - `backend/database/models.py:57-88` — Current Variant model (column pattern to follow)
  - `backend/api/variants.py:31-46` — VariantResponse schema (Pydantic model pattern)

  **API/Type References**:
  - `frontend/src/types/index.ts:21-45` — Frontend Variant interface (must match)

  **WHY Each Reference Matters**:
  - `models.py:57-88`: New columns must follow existing nullable/String length conventions
  - `variants.py:31-46`: Response schema must expose new fields to frontend
  - `types/index.ts:21-45`: Frontend interface must match backend response shape

  **Acceptance Criteria**:
  - [ ] New columns added to Variant model
  - [ ] Alembic migration applies cleanly (ALTER TABLE)
  - [ ] VariantResponse includes new fields
  - [ ] Frontend Variant interface updated
  - [ ] Existing variants still load (backward compatible)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: New columns in Variant model
    Tool: Bash
    Preconditions: Database migrated
    Steps:
      1. cd backend && python -c "from database.models import Variant; cols = [c.name for c in Variant.__table__.columns]; assert 'hgvs_c' in cols; assert 'consequence' in cols; assert 'vep_annotated' in cols; print('OK')"
    Expected Result: "OK"
    Failure Indicators: Column not found, import error
    Evidence: .sisyphus/evidence/task-3-variant-columns.txt

  Scenario: Backward compatibility — existing variants still load
    Tool: Bash (curl)
    Preconditions: At least one variant exists in DB from previous upload
    Steps:
      1. curl -s http://localhost:8000/api/variants/{existing_vcf_file_id}?page=1&page_size=5
      2. Parse JSON, check items[0] has hgvs_c=null but other fields populated
    Expected Result: Response returns existing variants with new fields as null
    Failure Indicators: 500 error, missing old fields
    Evidence: .sisyphus/evidence/task-3-backward-compat.txt
  ```

  **Commit**: YES (groups with 1, 2)
  - Message: `feat(vep): add VEP configuration and database schema`
  - Files: `backend/database/models.py`, `backend/api/variants.py`, `frontend/src/types/index.ts`, `backend/alembic/versions/`

- [x] 4. VEP Service Client — Submit + Poll + Parse

  **What to do**:
  - Create `backend/services/vep_service.py` with `VEPService` class:
    - `__init__(self, base_url, timeout, poll_interval)` — load from config
    - `async submit_job(self, vcf_path, options: dict) -> VEPJobInfo` — POST /runs with multipart form
      - Send file as `file=@/path/to/file.vcf`
      - Send options as form fields: `hgvs=true`, `no_pick=false`, etc.
      - Return parsed job info (job_id, status, status_url, result_url, log_url)
    - `async poll_job(self, job_id, max_wait_seconds) -> VEPJobStatus` — GET /runs/{job_id}
      - Poll every `poll_interval` seconds until status is "completed" or "failed"
      - Timeout after `max_wait_seconds` (default 600 = 10 min)
      - Return final status
    - `async get_result(self, result_url) -> str` — GET /runs/{job_id}/result
      - Return raw CSV string
    - `async get_log(self, log_url) -> str` — GET /runs/{job_id}/log
      - Return log content for debugging
    - `async process_vcf(self, vcf_path, options, db_session) -> List[VEPAnnotatedVariant]`
      - Orchestrate: submit → poll → get_result → parse CSV → return variants
      - On failure/timeout: return None (caller falls back)
    - Handle all HTTP errors with proper logging
    - Use `httpx` for async HTTP client (or `aiohttp` if already in project)

  **Must NOT do**:
  - Don't implement CSV parsing logic here (that's Task 5)
  - Don't import or modify variant_service.py
  - Don't add Redis caching

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Complex async service with error handling, needs careful design
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 6, 8, 10
  - **Blocked By**: Tasks 1 (config), 2 (VEPJob model), 3 (Variant model)

  **References**:

  **Pattern References**:
  - `backend/services/variant_detector.py:1-50` — Service class pattern (how services are structured, error handling, logging)
  - `backend/services/gene_lookup.py:1-50` — Service initialization pattern

  **API/Type References**:
  - VEP API POST `/runs`: `curl -s -X POST http://127.0.0.1:8000/runs -F file=@/path/to/file.vcf -F hgvs=true`
  - VEP API GET `/runs/{job_id}`: Returns `{"job_id": "...", "status": "queued|running|completed|failed", ...}`
  - VEP API GET `/runs/{job_id}/result`: Returns CSV content
  - VEP API GET `/runs/{job_id}/log`: Returns log text
  - `backend/database/models.py` VEPJob model (from Task 2) — for persisting job info

  **External References**:
  - httpx docs: https://www.python-httpx.org/async/ — async HTTP client

  **WHY Each Reference Matters**:
  - `variant_detector.py`: Must follow same service class structure (init, public methods, private helpers, logging)
  - VEP API spec: Defines exact HTTP calls, response shapes, and status values
  - VEPJob model: submit_job needs to persist job info to DB

  **Acceptance Criteria**:
  - [ ] VEPService class created with submit_job, poll_job, get_result, get_log, process_vcf methods
  - [ ] All HTTP errors handled with proper logging
  - [ ] Timeout logic works (10 min default)
  - [ ] Uses config for base_url, timeout, poll_interval
  - [ ] httpx (or aiohttp) used for async HTTP

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: VEP service submit job
    Tool: Bash (curl + python)
    Preconditions: VEP API running at configured URL, or mock server
    Steps:
      1. python -c "from services.vep_service import VEPService; print('import OK')"
      2. If VEP API available: python -c "
         import asyncio
         from services.vep_service import VEPService
         svc = VEPService('http://127.0.0.1:8000')
         result = asyncio.run(svc.submit_job('backend/tests/data/test.vcf', {'hgvs': 'true'}))
         print(f'job_id={result.job_id}, status={result.status}')
         "
    Expected Result: Import succeeds; if VEP API available, job submitted with job_id returned
    Failure Indicators: Import error, connection refused (if VEP not available, that's OK for this check)
    Evidence: .sisyphus/evidence/task-4-vep-submit.txt

  Scenario: VEP service handles connection failure gracefully
    Tool: Bash (python)
    Preconditions: VEP API NOT running (or wrong URL)
    Steps:
      1. python -c "
         import asyncio
         from services.vep_service import VEPService
         svc = VEPService('http://127.0.0.1:19999')  # non-existent
         try:
             result = asyncio.run(svc.submit_job('/tmp/nonexistent.vcf', {}))
             print('ERROR: should have raised')
         except Exception as e:
             print(f'OK: caught {type(e).__name__}')
         "
    Expected Result: Exception caught gracefully, not unhandled crash
    Failure Indicators: Unhandled exception, process exit
    Evidence: .sisyphus/evidence/task-4-vep-failure.txt
  ```

  **Commit**: YES (groups with 5)
  - Message: `feat(vep): implement VEP API client and CSV parser`
  - Files: `backend/services/vep_service.py`
  - Pre-commit: `cd backend && python -c "from services.vep_service import VEPService; print('OK')"`

- [x] 5. CSV Parser for VEP Output (Unknown Format)

  **What to do**:
  - Create `backend/services/vep_csv_parser.py` with `VEPCSVParser` class:
    - `parse(self, csv_content: str) -> List[VEPAnnotatedVariant]`
    - Since exact VEP CSV format is unknown, implement dynamic header detection:
      1. Read first line as headers
      2. Map headers to known VEP fields using flexible matching:
         - `#Uploaded_variation` or `Uploaded variation` → variant identifier
         - `Location` → chromosome:position
         - `Allele` → alt allele
         - `Gene` → gene symbol
         - `Feature` → transcript ID
         - `Consequence` → consequence term
         - `cDNA_position` / `HGVSc` → hgvs_c
         - `Protein_position` / `HGVSp` → hgvs_p
         - `Amino_acids` → amino acid change
         - `SIFT` → sift prediction
         - `PolyPhen` → polyphen prediction
         - `IMPACT` → impact level
         - `gnomADe_AF` / `AF` → allele frequency
         - `CLIN_SIG` / `ClinVar` → clinvar classification
         - `CADD_PHRED` / `CADD` → cadd score
      3. Parse each row into `VEPAnnotatedVariant` dataclass
    - `VEPAnnotatedVariant` dataclass:
      - chromosome, position, ref, alt, gene, consequence, impact, hgvs_c, hgvs_p, transcript, sift, polyphen, cadd, gnomad_af, clinvar_classification
    - Handle: missing columns, empty values, multi-value fields (comma-separated consequences)
    - Log warnings for unrecognized columns

  **Must NOT do**:
  - Don't hardcode column indices (VEP output format may vary)
  - Don't make HTTP calls (this is pure parsing)
  - Don't modify VEPService

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Unknown format requires robust dynamic parsing with flexible header mapping
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 4)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 6, 11
  - **Blocked By**: Task 1 (config for field naming)

  **References**:

  **Pattern References**:
  - `backend/services/vcf_parser.py:268-340` — Existing parsing pattern (how records are iterated and mapped to dataclasses)

  **API/Type References**:
  - VEP default output format docs: https://www.ensembl.org/info/docs/tools/vep/vep_formats.html
  - Typical VEP output headers: `#Uploaded_variation Location Allele Gene Feature Consequence cDNA_position CDS_position Protein_position Amino_acids Codons Existing_variation IMPACT DISTANCE STRAND FLAG SIFT PolyPhen gnomADe_AF CLIN_SIG SOMATIC PHENO`

  **External References**:
  - Python csv module: https://docs.python.org/3/library/csv.html

  **WHY Each Reference Matters**:
  - `vcf_parser.py`: Must follow same dataclass pattern for parsed results
  - VEP docs: Defines possible column names for header mapping
  - csv module: Standard library for CSV parsing

  **Acceptance Criteria**:
  - [ ] VEPCSVParser class created with `parse()` method
  - [ ] VEPAnnotatedVariant dataclass defined
  - [ ] Dynamic header detection works with VEP default format
  - [ ] Missing columns handled gracefully (null/None values)
  - [ ] Multi-value consequences parsed correctly

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Parse VEP default CSV format
    Tool: Bash (python)
    Preconditions: None
    Steps:
      1. Create a test CSV string with VEP-style headers:
         "#Uploaded_variation,Location,Allele,Gene,Feature,Consequence,HGVSc,HGVSp,IMPACT,SIFT,PolyPhen\n"
         "1_12345_A_T,1:12345,T,BRCA1,ENST000123,coding_sequence_variant,c.1A>T,p.Lys1Asn,MODERATE,deleterious(0.01),probably_damaging(0.99)"
      2. python -c "from services.vep_csv_parser import VEPCSVParser; p = VEPCSVParser(); result = p.parse(test_csv); print(len(result), result[0].gene, result[0].consequence)"
    Expected Result: 1 variant parsed, gene="BRCA1", consequence="coding_sequence_variant"
    Failure Indicators: Parse error, 0 variants, wrong field mapping
    Evidence: .sisyphus/evidence/task-5-csv-parse.txt

  Scenario: Handle missing columns gracefully
    Tool: Bash (python)
    Preconditions: None
    Steps:
      1. Create CSV with minimal headers:
         "Location,Gene,Consequence\n1:12345,BRCA1,missense_variant"
      2. Parse with VEPCSVParser
      3. Check that missing fields (hgvs_c, hgvs_p, sift, etc.) are None
    Expected Result: Variant parsed with only available fields, missing fields are None, no exception
    Failure Indicators: KeyError, crash on missing column
    Evidence: .sisyphus/evidence/task-5-csv-missing-cols.txt

  Scenario: Handle empty CSV
    Tool: Bash (python)
    Preconditions: None
    Steps:
      1. Parse empty string or header-only CSV
      2. Verify returns empty list, no crash
    Expected Result: Returns []
    Failure Indicators: Exception, IndexError
    Evidence: .sisyphus/evidence/task-5-csv-empty.txt
  ```

  **Commit**: YES (groups with 4)
  - Message: `feat(vep): implement VEP API client and CSV parser`
  - Files: `backend/services/vep_csv_parser.py`
  - Pre-commit: `cd backend && python -c "from services.vep_csv_parser import VEPCSVParser; print('OK')"`

- [x] 6. Modify Upload Endpoint — VEP-First with Fallback

  **What to do**:
  - Modify `POST /api/variants/upload` in `backend/api/variants.py` (lines 56-158):
    1. After current pysam VCF parsing (VariantDetector.detect()), always parse and store initial variants (keeps current behavior as fallback base)
    2. Then attempt VEP API annotation:
       - Call `VEPService.process_vcf(vcf_path, vep_options, db_session)`
       - If VEP succeeds: parse CSV → update variant records in DB with VEP fields → mark `vep_annotated=True`
       - If VEP fails/timeout: keep current pysam+GFF3 annotation (fallback) → mark `vep_annotated=False`
       - Log the VEP outcome
    3. Persist VEP job info to VEPJob table
    4. Add VEP options to upload form parameters:
       - `vep_hgvs: bool = True`
       - `vep_no_pick: bool = False`
       - `vep_format: str = "vcf"`
       - `vep_fork: int = 1`
    5. Update UploadResponse to include VEP status:
       - `vep_status: str` — "completed", "failed", "timeout", "skipped"
       - `vep_job_id: Optional[str]`
  - The upload should be synchronous from the client's perspective:
    - Frontend sends VCF → backend handles VEP internally → returns when done (or timeout)
    - Use `asyncio.wait_for()` with timeout

  **Must NOT do**:
  - Don't remove the current pysam+GFF3 parsing path
  - Don't make VEP blocking prevent returning upload response (timeout after 10 min)
  - Don't modify ACMG classification logic
  - Don't change the WebSocket chat

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Core integration point, modifies critical upload flow, needs careful error handling
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 2, 3, 4, 5)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 12
  - **Blocked By**: Tasks 2, 3, 4, 5

  **References**:

  **Pattern References**:
  - `backend/api/variants.py:56-158` — Current upload endpoint (MUST read this carefully — the exact flow to modify)
  - `backend/api/variants.py:79-80` — Where VariantDetector.detect() is called
  - `backend/api/variants.py:83-86` — Where gene_lookup happens (integration point for VEP enhancement)
  - `backend/api/variants.py:122-140` — Where variants are batch-inserted to DB

  **API/Type References**:
  - `backend/services/vep_service.py` (from Task 4) — VEPService.process_vcf() API
  - `backend/services/vep_csv_parser.py` (from Task 5) — VEPCSVParser.parse() API
  - `backend/database/models.py` VEPJob model (from Task 2) — For persisting job info
  - `backend/database/models.py` Variant model (from Task 3) — Updated with VEP fields

  **WHY Each Reference Matters**:
  - `variants.py:56-158`: The exact code to modify — must understand every step
  - VEPService + VEPCSVParser: New dependencies to integrate
  - Models: Must persist VEP job and update variant records

  **Acceptance Criteria**:
  - [ ] Upload endpoint accepts VEP options (vep_hgvs, vep_no_pick, vep_format, vep_fork)
  - [ ] VEP API called after pysam parsing
  - [ ] On VEP success: variants updated with VEP fields, vep_annotated=True
  - [ ] On VEP failure/timeout: current annotation preserved, vep_annotated=False
  - [ ] VEPJob record persisted with job_id, status, URLs
  - [ ] UploadResponse includes vep_status and vep_job_id
  - [ ] Upload returns within timeout (10 min max)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Upload with VEP API available
    Tool: Bash (curl)
    Preconditions: VEP API running, test VCF file available
    Steps:
      1. curl -s -X POST http://localhost:8000/api/variants/upload \
           -F "file=@backend/tests/data/test.vcf" \
           -F "patient_id=test-vep-001" \
           -F "vep_hgvs=true"
      2. Parse JSON response, check vep_status="completed" and vep_job_id is set
    Expected Result: Upload succeeds, VEP annotated, response includes VEP status
    Failure Indicators: 500 error, vep_status="failed", timeout
    Evidence: .sisyphus/evidence/task-6-upload-vep-success.json

  Scenario: Upload with VEP API unavailable (fallback)
    Tool: Bash (curl)
    Preconditions: VEP API NOT running (or wrong URL configured)
    Steps:
      1. Set VEP_API_BASE_URL=http://127.0.0.1:19999 in .env
      2. Restart backend
      3. curl -s -X POST http://localhost:8000/api/variants/upload \
           -F "file=@backend/tests/data/test.vcf" \
           -F "patient_id=test-vep-002"
      4. Parse JSON response, check vep_status="failed" or "skipped"
    Expected Result: Upload succeeds using pysam fallback, VEP status shows failure
    Failure Indicators: 500 error, upload blocked by VEP failure
    Evidence: .sisyphus/evidence/task-6-upload-vep-fallback.json

  Scenario: Upload with VEP options
    Tool: Bash (curl)
    Preconditions: VEP API running
    Steps:
      1. curl -s -X POST http://localhost:8000/api/variants/upload \
           -F "file=@backend/tests/data/test.vcf" \
           -F "patient_id=test-vep-003" \
           -F "vep_hgvs=true" \
           -F "vep_no_pick=true" \
           -F "vep_fork=2"
      2. Check VEPJob.options matches submitted options
    Expected Result: Options passed through to VEP API correctly
    Failure Indicators: Options not in VEPJob record
    Evidence: .sisyphus/evidence/task-6-upload-vep-options.json
  ```

  **Commit**: YES
  - Message: `feat(vep): integrate VEP into upload flow with fallback`
  - Files: `backend/api/variants.py`, `backend/services/variant_service.py`
  - Pre-commit: `cd backend && python -c "from api.variants import router; print('OK')"`

- [x] 7. VEP Options UI in Upload Form

  **What to do**:
  - Modify `frontend/src/components/VCFUpload.tsx` to add VEP options section:
    - Add a collapsible "VEP Options" panel (default expanded) below the file upload
    - Options to add:
      - `HGVS notation` — Switch (default: ON)
      - `No pick` — Switch (default: OFF)
      - `Format` — Select (vcf/json, default: vcf)
      - `Fork` — InputNumber (1-8, default: 1)
    - When VEP is disabled (VEP_ENABLED=false), show a notice instead of options
    - Pass VEP options as additional form fields in the upload request
  - Ensure the upload form still works without VEP (options are optional)

  **Must NOT do**:
  - Don't modify the VariantList component
  - Don't add VEP status display (that's Task 9)
  - Don't change the patient info form fields

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Frontend UI component changes with Ant Design
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not needed for implementation, only QA

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 9
  - **Blocked By**: None (independent of backend tasks, just adds form fields)

  **References**:

  **Pattern References**:
  - `frontend/src/components/VCFUpload.tsx:1-176` — Current upload form (exact component to modify)
  - `frontend/src/components/VCFUpload.tsx:61-79` — Current upload API call (where to add VEP fields)

  **API/Type References**:
  - `frontend/src/services/api.ts:223-250` — uploadVCF method (where form data is constructed)

  **WHY Each Reference Matters**:
  - `VCFUpload.tsx`: Exact file to modify, must match existing form layout and Ant Design patterns
  - `api.ts`: Must add VEP fields to the FormData before sending

  **Acceptance Criteria**:
  - [ ] VEP options panel visible in upload form
  - [ ] HGVS switch defaults to ON, No pick to OFF
  - [ ] Options passed as form fields (vep_hgvs, vep_no_pick, vep_format, vep_fork)
  - [ ] Upload works without VEP options (backward compatible)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: VEP options visible in upload form
    Tool: Playwright
    Preconditions: Frontend running at http://localhost:8888
    Steps:
      1. Navigate to http://localhost:8888
      2. Click "Upload VCF" button or navigate to upload page
      3. Wait for upload form to render
      4. Assert element with text "HGVS" or "VEP" is visible
    Expected Result: VEP options section is visible with HGVS switch
    Failure Indicators: No VEP options visible, form not rendering
    Evidence: .sisyphus/evidence/task-7-vep-options-ui.png

  Scenario: VEP options submitted with upload
    Tool: Playwright + Browser DevTools Network
    Preconditions: Frontend + backend running
    Steps:
      1. Open upload form
      2. Select a test VCF file
      3. Toggle HGVS ON, set Fork to 2
      4. Click Upload
      5. Check network request contains vep_hgvs=true and vep_fork=2
    Expected Result: Form data includes VEP options
    Failure Indicators: VEP options missing from request
    Evidence: .sisyphus/evidence/task-7-vep-submit.png
  ```

  **Commit**: YES (groups with 8, 9)
  - Message: `feat(vep): add frontend VEP options and loading state`
  - Files: `frontend/src/components/VCFUpload.tsx`, `frontend/src/services/api.ts`

- [x] 8. VEP Job Status API Endpoint

  **What to do**:
  - Add new API endpoints in `backend/api/variants.py` (or a new `backend/api/vep.py`):
    - `GET /api/vep/jobs/{job_id}` — Get VEP job status
      - Returns: VEPJob record (job_id, status, created_at, updated_at, error, rows)
    - `GET /api/vep/jobs/vcf/{vcf_file_id}` — Get VEP job by VCF file
      - Returns: Latest VEPJob for the given VCF file
    - `GET /api/vep/jobs/{job_id}/log` — Get VEP job log
      - Proxies to VEP API's log endpoint, returns text
  - Include VEPJob in API router registration in main.py

  **Must NOT do**:
  - Don't add write endpoints (jobs are created by upload flow only)
  - Don't add WebSocket for job status (using simple polling)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple read-only CRUD endpoints
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 7)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 9
  - **Blocked By**: Tasks 2 (VEPJob model), 4 (VEPService for log proxy)

  **References**:

  **Pattern References**:
  - `backend/api/variants.py:160-199` — Existing GET endpoint pattern (how to define response models, pagination)

  **API/Type References**:
  - `backend/database/models.py` VEPJob (from Task 2) — Model to query

  **WHY Each Reference Matters**:
  - `variants.py:160-199`: Must follow same endpoint definition pattern

  **Acceptance Criteria**:
  - [ ] GET /api/vep/jobs/{job_id} returns job info
  - [ ] GET /api/vep/jobs/vcf/{vcf_file_id} returns latest job for VCF
  - [ ] GET /api/vep/jobs/{job_id}/log returns log content
  - [ ] 404 for non-existent job_id

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Get VEP job status
    Tool: Bash (curl)
    Preconditions: At least one VEP job exists (from upload)
    Steps:
      1. curl -s http://localhost:8000/api/vep/jobs/{existing_job_id}
      2. Parse JSON, check job_id and status fields exist
    Expected Result: JSON with job_id, status, created_at
    Failure Indicators: 404, missing fields
    Evidence: .sisyphus/evidence/task-8-vep-job-status.json

  Scenario: VEP job not found
    Tool: Bash (curl)
    Preconditions: None
    Steps:
      1. curl -s -w "\n%{http_code}" http://localhost:8000/api/vep/jobs/nonexistent-id
    Expected Result: 404 status code
    Failure Indicators: 200 with null, 500 error
    Evidence: .sisyphus/evidence/task-8-vep-job-404.txt
  ```

  **Commit**: YES (groups with 7, 9)
  - Message: `feat(vep): add frontend VEP options and loading state`
  - Files: `backend/api/vep.py`, `backend/main.py` (router registration)

- [x] 9. Frontend Loading State + VEP Status Display

  **What to do**:
  - Modify `frontend/src/components/VCFUpload.tsx` and `frontend/src/pages/AnalysisPage.tsx`:
    - After upload, show "VEP annotation in progress..." loading state
    - Since upload is synchronous (backend handles VEP + timeout internally), the loading is:
      - Show spinner during upload API call (which now takes longer due to VEP)
      - After upload returns, show VEP status in upload result:
        - "VEP annotation completed (N variants annotated)"
        - "VEP annotation failed, using local annotation"
        - "VEP annotation timed out (10 min), using local annotation"
    - Modify `frontend/src/components/VariantList.tsx`:
      - Display VEP-annotated fields (consequence, hgvs_p) — these columns already exist but are empty
      - Add `impact` badge column (HIGH=red, MODERATE=orange, LOW=blue, MODIFIER=grey) — only if `vep_annotated=True`
      - Show "VEP" tag on variants that were VEP-annotated (distinguish from fallback variants)

  **Must NOT do**:
  - Don't add real-time WebSocket progress (keep simple)
  - Don't add polling for job status (backend handles sync)
  - Don't change the chat interface

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Frontend UI state management and display
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - `playwright`: Only for QA, not implementation

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 7, 8)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 12
  - **Blocked By**: Tasks 7 (form), 8 (API endpoints)

  **References**:

  **Pattern References**:
  - `frontend/src/components/VCFUpload.tsx:61-79` — Current upload and loading logic
  - `frontend/src/components/VariantList.tsx:106-230` — Current table columns (add impact column)
  - `frontend/src/pages/AnalysisPage.tsx:284-302` — Where VariantList is rendered

  **API/Type References**:
  - `frontend/src/types/index.ts:21-45` — Variant interface (already has consequence, hgvs_p)
  - Backend UploadResponse (from Task 6) — Now includes vep_status, vep_job_id

  **WHY Each Reference Matters**:
  - `VCFUpload.tsx`: Must extend loading state logic
  - `VariantList.tsx`: Must add impact column and VEP indicator
  - `AnalysisPage.tsx`: May need to pass VEP status to VariantList

  **Acceptance Criteria**:
  - [ ] Upload shows loading state during VEP processing
  - [ ] After upload, VEP status message shown (completed/failed/timeout)
  - [ ] VariantList shows consequence and hgvs_p columns populated (from VEP)
  - [ ] Impact badge shown for VEP-annotated variants
  - [ ] "VEP" tag distinguishes VEP-annotated from fallback variants

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Upload shows loading during VEP processing
    Tool: Playwright
    Preconditions: Frontend + backend running, VEP API available
    Steps:
      1. Navigate to upload page
      2. Select VCF file, set VEP options
      3. Click Upload
      4. Assert spinner or "processing" text is visible during upload
      5. Wait for upload to complete
      6. Assert VEP status message is visible
    Expected Result: Loading indicator shown, then VEP status
    Failure Indicators: No loading state, instant result (no VEP time)
    Evidence: .sisyphus/evidence/task-9-loading-state.png

  Scenario: Variant table shows VEP-annotated data
    Tool: Playwright
    Preconditions: VCF uploaded with VEP annotation
    Steps:
      1. Navigate to analysis page for the uploaded VCF
      2. Assert VariantList table is visible
      3. Check first row has populated Consequence column
      4. Check first row has populated HGVS.p column
      5. Check impact badge is visible (red/orange/blue/grey)
    Expected Result: VEP fields populated in table
    Failure Indicators: Consequence and HGVS.p columns still empty
    Evidence: .sisyphus/evidence/task-9-variant-vep-data.png

  Scenario: Fallback variants show without VEP tag
    Tool: Playwright
    Preconditions: VCF uploaded with VEP failure (fallback)
    Steps:
      1. Navigate to analysis page for the uploaded VCF
      2. Check variants exist but no VEP tag/badge
    Expected Result: Variants display with basic data, no VEP indicators
    Failure Indicators: VEP tag shown on non-VEP variants
    Evidence: .sisyphus/evidence/task-9-fallback-variants.png
  ```

  **Commit**: YES (groups with 7, 8)
  - Message: `feat(vep): add frontend VEP options and loading state`
  - Files: `frontend/src/components/VCFUpload.tsx`, `frontend/src/components/VariantList.tsx`, `frontend/src/pages/AnalysisPage.tsx`

- [x] 10. Pytest Tests for VEP Service

  **What to do**:
  - Create `backend/tests/test_vep_service.py`:
    - Test `submit_job`:
      - Success case: mock httpx response with VEP job JSON
      - Connection error: VEP API unreachable
      - Timeout: request takes too long
      - Invalid response: malformed JSON
    - Test `poll_job`:
      - Completes on first poll (status=completed)
      - Polls multiple times before completion (queued→running→completed)
      - Timeout after max_wait_seconds
      - Job fails (status=failed)
    - Test `get_result`:
      - Returns CSV content
      - 404 error (job not found)
    - Test `process_vcf`:
      - Full orchestration success
      - VEP failure → returns None (fallback)
    - Use `pytest` + `pytest-asyncio` + `unittest.mock` / `respx` for httpx mocking

  **Must NOT do**:
  - Don't make real HTTP calls to VEP API in tests (mock everything)
  - Don't test CSV parsing here (that's Task 11)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Test writing requires careful mocking and multiple scenarios
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 11)
  - **Parallel Group**: Wave 3
  - **Blocks**: F2 (code quality review)
  - **Blocked By**: Task 4 (VEPService must exist)

  **References**:

  **Pattern References**:
  - `backend/tests/` — Existing test directory structure and naming convention

  **API/Type References**:
  - `backend/services/vep_service.py` (from Task 4) — VEPService class to test

  **WHY Each Reference Matters**:
  - Tests directory: Must follow existing test file naming and structure
  - VEPService: The class under test

  **Acceptance Criteria**:
  - [ ] test_vep_service.py created
  - [ ] All mock-based tests pass
  - [ ] `cd backend && pytest tests/test_vep_service.py -v` → all green

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All VEP service tests pass
    Tool: Bash (pytest)
    Preconditions: VEPService implemented
    Steps:
      1. cd backend && pytest tests/test_vep_service.py -v
      2. Check all tests pass, 0 failures
    Expected Result: N passed, 0 failed, 0 errors
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-10-vep-tests.txt
  ```

  **Commit**: YES (groups with 11, 12)
  - Message: `test(vep): add pytest tests for VEP service and integration`
  - Files: `backend/tests/test_vep_service.py`

- [x] 11. Pytest Tests for CSV Parser

  **What to do**:
  - Create `backend/tests/test_vep_csv_parser.py`:
    - Test with VEP default output format (full headers)
    - Test with minimal headers (only Gene, Location, Consequence)
    - Test with empty CSV
    - Test with malformed CSV (inconsistent columns)
    - Test multi-value consequences (comma-separated)
    - Test field mapping for each known header variant:
      - `HGVSc` / `cDNA_position`
      - `HGVSp` / `Protein_position`
      - `SIFT` / `PolyPhen` / `CADD_PHRED`
    - Test gnomAD AF parsing
    - Test ClinVar classification parsing
  - Create fixture files: `backend/tests/data/vep_output_sample.csv`

  **Must NOT do**:
  - Don't make HTTP calls (pure parsing tests)
  - Don't test VEPService here (that's Task 10)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Many edge cases to cover for unknown format parsing
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 10)
  - **Parallel Group**: Wave 3
  - **Blocks**: F2
  - **Blocked By**: Task 5 (VEPCSVParser must exist)

  **References**:

  **Pattern References**:
  - `backend/tests/` — Existing test structure

  **API/Type References**:
  - `backend/services/vep_csv_parser.py` (from Task 5) — VEPCSVParser to test
  - VEP output format: https://www.ensembl.org/info/docs/tools/vep/vep_formats.html

  **WHY Each Reference Matters**:
  - Tests: Must follow project test conventions
  - VEPCSVParser: Class under test
  - VEP docs: Reference for expected CSV column names

  **Acceptance Criteria**:
  - [ ] test_vep_csv_parser.py created
  - [ ] Fixture CSV files created
  - [ ] `cd backend && pytest tests/test_vep_csv_parser.py -v` → all green
  - [ ] Coverage includes: full headers, minimal headers, empty, malformed

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All CSV parser tests pass
    Tool: Bash (pytest)
    Preconditions: VEPCSVParser implemented
    Steps:
      1. cd backend && pytest tests/test_vep_csv_parser.py -v
      2. Check all tests pass
    Expected Result: N passed, 0 failed
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-11-csv-tests.txt
  ```

  **Commit**: YES (groups with 10, 12)
  - Message: `test(vep): add pytest tests for VEP service and integration`
  - Files: `backend/tests/test_vep_csv_parser.py`, `backend/tests/data/vep_output_sample.csv`

- [x] 12. Integration Test — Full VEP Upload Flow

  **What to do**:
  - Create `backend/tests/test_vep_integration.py`:
    - Test full upload flow with VEP:
      1. Upload VCF via POST /api/variants/upload with vep_hgvs=true
      2. Verify response includes vep_status and vep_job_id
      3. Verify VEPJob record in database
      4. Verify variants in database have VEP fields populated (if VEP succeeded)
    - Test fallback flow:
      1. Configure VEP_API_BASE_URL to non-existent server
      2. Upload VCF
      3. Verify response vep_status="failed" or "skipped"
      4. Verify variants still exist (from pysam parsing)
    - Use mock VEP server or test fixtures
  - This is the end-to-end test that ties everything together

  **Must NOT do**:
  - Don't require real VEP API for CI (mock it)
  - Don't test individual service methods (those are Task 10, 11)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Integration across multiple components, needs careful setup
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 6, 9)
  - **Parallel Group**: Wave 3
  - **Blocks**: F3
  - **Blocked By**: Tasks 6 (upload endpoint), 9 (frontend)

  **References**:

  **Pattern References**:
  - `backend/tests/` — Existing integration test patterns

  **API/Type References**:
  - All backend services from Tasks 2-6
  - `backend/tests/data/test.vcf` — Test VCF file

  **WHY Each Reference Matters**:
  - Tests: Must follow project integration test conventions
  - All services: This test validates they work together

  **Acceptance Criteria**:
  - [ ] Integration test created
  - [ ] VEP success path tested
  - [ ] VEP fallback path tested
  - [ ] `cd backend && pytest tests/test_vep_integration.py -v` → all green

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Full integration test passes
    Tool: Bash (pytest)
    Preconditions: All VEP components implemented
    Steps:
      1. cd backend && pytest tests/test_vep_integration.py -v
      2. Check all tests pass
    Expected Result: N passed, 0 failed
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-12-integration-tests.txt
  ```

  **Commit**: YES (groups with 10, 11)
  - Message: `test(vep): add pytest tests for VEP service and integration`
  - Files: `backend/tests/test_vep_integration.py`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run linter + `pytest`. Review all changed files for: `as any`/type ignores, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration. Test edge cases: VEP timeout, VEP error, empty results, re-upload. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Task 1+2+3**: `feat(vep): add VEP configuration and database schema` — config files, models.py, .env.example
- **Task 4+5**: `feat(vep): implement VEP API client and CSV parser` — vep_service.py, vep_csv_parser.py
- **Task 6**: `feat(vep): integrate VEP into upload flow with fallback` — variants.py, variant_service.py
- **Task 7+8+9**: `feat(vep): add frontend VEP options and loading state` — VCFUpload.tsx, api.ts, AnalysisPage.tsx
- **Task 10+11+12**: `test(vep): add pytest tests for VEP service and integration` — test files

---

## Success Criteria

### Verification Commands
```bash
# Backend starts without errors
curl -s http://localhost:8000/api/health | python3 -c "import sys,json; assert json.load(sys.stdin)['status']=='healthy'"

# VEP config loaded
curl -s http://localhost:8000/api/config | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'vep_api_base_url' in d"

# VEP job status endpoint exists
curl -s -w "%{http_code}" http://localhost:8000/api/vep/jobs/nonexistent | grep -q "404"

# Pytest passes
cd backend && pytest tests/test_vep_service.py tests/test_vep_csv_parser.py -v

# Upload with VEP (mock mode or real VEP)
curl -s -X POST http://localhost:8000/api/variants/upload \
  -F "file=@backend/tests/data/test.vcf" \
  -F "patient_id=1" \
  -F "vep_hgvs=true"

# Frontend shows VEP options in upload form
# (Playwright verification)
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] All tests pass
- [x] VEP API integration works end-to-end
- [x] Fallback to pysam works when VEP unavailable
