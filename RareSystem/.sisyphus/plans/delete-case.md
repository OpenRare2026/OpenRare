# Delete Case Feature - Browse Cases

## TL;DR

> **Quick Summary**: Add a delete button with Popconfirm to each case row in BrowseCases page, with backend DELETE endpoint that cascades all related data and cleans up VCF files on disk.
> 
> **Deliverables**:
> - Backend `DELETE /api/cases/{patient_id}` endpoint with full cascade cleanup
> - Frontend Delete button with Popconfirm in BrowseCases Action column
> - Active case protection (disable delete for currently open case)
> - TDD tests (pytest backend + vitest frontend)
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 → Task 4 → Task 6 → F1-F4

---

## Context

### Original Request
"Browse Cases 针对每一个案例数据，应该是有一个delete的案件，可以将数据进行删除掉"

### Interview Summary
**Key Discussions**:
- Delete confirmation: YES - Ant Design Popconfirm (二次确认气泡)
- File cleanup: YES - Delete VCF files from disk using VCFFile.file_path
- Active case protection: YES - Disable delete button if case is currently open in AnalysisPage
- Test strategy: TDD (pytest backend + vitest frontend)

**Research Findings**:
- Backend has no DELETE endpoint for cases yet (`backend/api/cases.py`)
- Patient model cascades to VCFFile→Variant→ACMG* + ClinicalReport + ResearchReport (automatic)
- Non-cascaded tables: CaseDocument→CaseEmbedding, ChatSession→ChatMessageRecord, LLMSettings (need manual cleanup)
- FAISS index is in-memory; `embedding_service.clear_index()` available to reset stale vectors
- App.tsx tracks `sessionInfo { patientId, vcfFileId }` for the currently active case
- BrowseCases.tsx currently only has "Open" button in Action column
- VCFFile.file_path stores the server-side path to the uploaded VCF file

### Metis Review (Self-Performed)
**Identified Gaps** (addressed):
- FAISS index stale entries after CaseDocument deletion → Plan: call `embedding_service.clear_index()` to reset; index rebuilt on next search
- VCF file may not exist on disk (already manually deleted) → Plan: use `os.path.exists()` check before `os.remove()`, log warning if missing
- SkillConfig is NOT per-patient → Plan: do NOT delete SkillConfig (it's global)
- Error handling if deletion partially fails → Plan: use DB transaction (rollback on failure)

---

## Work Objectives

### Core Objective
Add a delete action to each case row in BrowseCases that deletes the case and ALL associated data (variants, ACMG records, reports, chat sessions, case documents, LLM settings, VCF files on disk).

### Concrete Deliverables
- `backend/api/cases.py`: New `DELETE /cases/{patient_id}` endpoint
- `tests/test_delete_case.py`: pytest test file for the DELETE endpoint
- `frontend/src/services/api.ts`: New `deleteCase(patientId)` method
- `frontend/src/pages/BrowseCases.tsx`: Delete button with Popconfirm + active case disable
- `frontend/src/App.tsx`: Pass `activePatientId` to BrowseCases
- `frontend/src/__tests__/BrowseCases.test.tsx`: vitest test for delete interaction

### Definition of Done
- [ ] `curl -X DELETE http://localhost:8000/api/cases/1` returns 200 and deletes all related data
- [ ] BrowseCases shows Delete button with Popconfirm for each row
- [ ] Delete button is disabled when case is currently open in AnalysisPage
- [ ] After deletion, case list refreshes; if deleted case was active, session clears
- [ ] VCF files on disk are removed
- [ ] All pytest and vitest tests pass

### Must Have
- DELETE /api/cases/{patient_id} endpoint that removes ALL related data
- Popconfirm before deletion with clear warning text
- Disable delete button for currently active case
- Delete VCF files from disk
- Refresh case list after successful deletion
- Clear session and redirect if deleted case was the active one
- TDD tests for both backend and frontend

### Must NOT Have (Guardrails)
- NO bulk delete (single case at a time only)
- NO undo/restore/soft-delete functionality
- NO audit trail or deletion logging beyond standard app logging
- NO permission checks (local deployment, single user)
- NO SkillConfig deletion (global, not per-patient)
- AI slop: Do NOT add excessive error handling, toast notifications, or animation effects

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: TDD
- **Framework**: pytest (backend) + vitest (frontend)
- **TDD Flow**: Each task follows RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **API/Backend**: Use Bash (curl) - Send DELETE request, assert status + response, verify DB state
- **Frontend/UI**: Use Bash (npm run build) - Verify build passes
- **Library/Module**: Use Bash (pytest/vitest) - Run tests, assert pass/fail

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - TDD red + API method):
├── Task 1: Backend TDD red - pytest test for DELETE endpoint [quick]
├── Task 2: Frontend API - Add deleteCase(patientId) to api.ts [quick]
└── Task 3: Frontend TDD red - vitest test for BrowseCases delete [quick]

Wave 2 (After Wave 1 - TDD green implementation):
├── Task 4: Backend TDD green - Implement DELETE endpoint (depends: 1) [unspecified-high]
└── Task 5: Frontend TDD green - Implement delete UI in BrowseCases + App.tsx (depends: 2, 3) [unspecified-high]

Wave 3 (After Wave 2 - integration + verification):
└── Task 6: Build verification + integration QA (depends: 4, 5) [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 4 → Task 6 → F1-F4 → user okay
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | - | 4 | 1 |
| 2 | - | 5 | 1 |
| 3 | - | 5 | 1 |
| 4 | 1 | 6 | 2 |
| 5 | 2, 3 | 6 | 2 |
| 6 | 4, 5 | F1-F4 | 3 |
| F1 | 6 | user okay | FINAL |
| F2 | 6 | user okay | FINAL |
| F3 | 6 | user okay | FINAL |
| F4 | 6 | user okay | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **3** - T1 → `quick`, T2 → `quick`, T3 → `quick`
- **Wave 2**: **2** - T4 → `unspecified-high`, T5 → `unspecified-high`
- **Wave 3**: **1** - T6 → `quick`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Backend TDD Red - Write pytest test for DELETE /cases/{patient_id}

  **What to do**:
  - Create `tests/test_delete_case.py` with pytest test cases
  - Test cases to cover:
    - `test_delete_case_success`: DELETE existing case → 200, verify Patient + all related data deleted
    - `test_delete_case_not_found`: DELETE non-existent patient_id → 404
    - `test_delete_case_cleans_vcf_files`: Verify VCF file_path files are deleted from disk (mock os.remove)
    - `test_delete_case_cleans_non_cascaded`: Verify CaseDocument, ChatSession, ChatMessageRecord, LLMSettings are deleted
    - `test_delete_case_clears_faiss_index`: Verify embedding_service.clear_index() is called after CaseDocument deletion
    - `test_delete_case_file_missing_on_disk`: VCF file_path doesn't exist → no error, just log warning
  - All tests should FAIL at this point (RED phase) since endpoint doesn't exist

  **Must NOT do**:
  - Do NOT implement the endpoint yet (that's Task 4)
  - Do NOT modify any existing code

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Writing a single test file following existing pytest patterns
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not UI testing

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Task 4
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `tests/test_settings_service.py` - Existing pytest test file pattern (imports, setup, assertions)
  - `backend/api/cases.py:52-103` - Existing list_cases endpoint pattern (DB session usage, query patterns)
  - `backend/api/settings.py:181-191` - Existing DELETE endpoint pattern (`delete_settings`)

  **API/Type References** (contracts to implement against):
  - `backend/database/models.py:11-34` - Patient model with cascade relationships
  - `backend/database/models.py:37-54` - VCFFile model with file_path column
  - `backend/database/case_models.py:11-34` - CaseDocument model (patient_id FK, no cascade)
  - `backend/database/case_models.py:59-78` - ChatSession model (patient_id FK, no cascade)
  - `backend/database/case_models.py:104-133` - LLMSettings model (patient_id FK, no cascade)

  **External References**:
  - FastAPI testing: `https://fastapi.tiangolo.com/tutorial/testing/` - TestClient pattern

  **WHY Each Reference Matters**:
  - `test_settings_service.py`: Copy the pytest structure (fixtures, imports, assertion style)
  - `cases.py:52-103`: Understand how existing endpoints query the DB
  - `settings.py:181-191`: See the DELETE endpoint pattern to follow
  - `models.py`: Know which models have cascade and which don't (determines what to manually delete in tests)
  - `case_models.py`: Non-cascaded models that need explicit deletion verification

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file created: `tests/test_delete_case.py`
  - [ ] 6 test functions defined (all expected to FAIL since endpoint doesn't exist)
  - [ ] Tests cover: success, 404, file cleanup, non-cascaded cleanup, FAISS clear, missing file

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: TDD Red - all tests fail as expected
    Tool: Bash (pytest)
    Preconditions: DELETE /cases/{patient_id} endpoint does not exist
    Steps:
      1. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing && python -m pytest tests/test_delete_case.py -v
      2. Assert: All 6 tests show FAILED or ERROR (because endpoint not implemented)
    Expected Result: 6 collected, 6 failed/errored
    Failure Indicators: Tests pass (means endpoint already exists) or 0 tests collected (syntax error)
    Evidence: .sisyphus/evidence/task-1-tdd-red.txt
  ```

  **Commit**: YES (groups with Tasks 2, 3)
  - Message: `test(cases): add TDD tests for delete case endpoint and UI`
  - Files: `tests/test_delete_case.py`
  - Pre-commit: `python -m pytest tests/test_delete_case.py --collect-only`

---

- [x] 2. Frontend API - Add deleteCase(patientId) method to api.ts

  **What to do**:
  - Add `deleteCase(patientId: number)` async method to `frontend/src/services/api.ts`
  - Method sends `DELETE` request to `/cases/${patientId}`
  - Returns `Promise<{message: string, patient_id: number}>`
  - Follow existing API method patterns in the class (e.g., `getCases()`, `getCase()`)

  **Must NOT do**:
  - Do NOT modify any existing API methods
  - Do NOT add error handling beyond what the base `request()` method already provides

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single method addition to existing API class
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 5
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `frontend/src/services/api.ts:495-507` - Existing `getCases()` and `getCase()` methods (pattern to follow)

  **WHY Each Reference Matters**:
  - `api.ts:495-507`: Copy the exact method structure (return type, this.request() call pattern)

  **Acceptance Criteria**:
  - [ ] `deleteCase` method added to ApiService class
  - [ ] Method sends DELETE to `/cases/${patientId}`
  - [ ] TypeScript builds without errors (`npm run build`)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Frontend build passes after adding deleteCase method
    Tool: Bash (npm run build)
    Preconditions: api.ts has the new method
    Steps:
      1. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing/frontend && npm run build
      2. Assert: Exit code 0, no TypeScript errors
    Expected Result: Build successful
    Failure Indicators: TypeScript type errors or build failure
    Evidence: .sisyphus/evidence/task-2-build.txt

  Scenario: deleteCase method signature is correct
    Tool: Bash (grep)
    Preconditions: Method added
    Steps:
      1. Grep for "deleteCase" in api.ts
      2. Assert: Method exists with correct signature (patientId: number, returns Promise)
    Expected Result: `async deleteCase(patientId: number): Promise<{message: string, patient_id: number}>`
    Failure Indicators: Method missing or wrong signature
    Evidence: .sisyphus/evidence/task-2-method-sig.txt
  ```

  **Commit**: YES (groups with Tasks 1, 3)
  - Message: `test(cases): add TDD tests for delete case endpoint and UI`
  - Files: `frontend/src/services/api.ts`
  - Pre-commit: `npm run build`

---

- [x] 3. Frontend TDD Red - Write vitest test for BrowseCases delete interaction

  **What to do**:
  - Create `frontend/src/__tests__/BrowseCases.test.tsx` with vitest + @testing-library/react tests
  - Test cases to cover:
    - `renders delete button for each case row`: Each row shows a Delete button
    - `delete button shows Popconfirm on click`: Clicking Delete shows confirmation popover
    - `delete button is disabled for active case`: Row with patientId matching activePatientId has disabled Delete
    - `calls onDeleteCase when confirmed`: After Popconfirm confirm, `onDeleteCase(patientId)` is called
    - `shows loading state during deletion`: Delete button shows loading spinner while API call in progress
  - All tests should FAIL at this point (RED phase) since delete UI doesn't exist

  **Must NOT do**:
  - Do NOT implement the delete button yet (that's Task 5)
  - Do NOT modify BrowseCases.tsx or App.tsx

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single test file following existing vitest patterns
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 5
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `frontend/src/pages/BrowseCases.tsx:78-188` - Current column definitions and Action column render
  - `frontend/vitest.config.ts` - Vitest configuration

  **API/Type References** (contracts to implement against):
  - `frontend/src/pages/BrowseCases.tsx:44-47` - `CaseListResponse` and `CaseSummary` interfaces (for test data)

  **External References**:
  - Ant Design Popconfirm testing: `https://ant.design/components/popconfirm` - Component API
  - @testing-library/react: `https://testing-library.com/docs/react-testing-library/intro` - Query patterns

  **WHY Each Reference Matters**:
  - `BrowseCases.tsx:78-188`: Understand current column structure to write tests for new Action column
  - `vitest.config.ts`: Ensure tests run with correct configuration
  - `CaseSummary interface`: Create proper test data fixtures

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file created: `frontend/src/__tests__/BrowseCases.test.tsx`
  - [ ] 5 test cases defined (all expected to FAIL since delete UI doesn't exist)
  - [ ] Tests mock `api.deleteCase()` and `api.getCases()`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: TDD Red - all tests fail as expected
    Tool: Bash (vitest)
    Preconditions: Delete button UI not yet implemented in BrowseCases
    Steps:
      1. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing/frontend && npx vitest run src/__tests__/BrowseCases.test.tsx
      2. Assert: Tests show FAILED (because delete UI doesn't exist yet)
    Expected Result: Tests collected and failing
    Failure Indicators: 0 tests collected (syntax error in test file)
    Evidence: .sisyphus/evidence/task-3-tdd-red.txt
  ```

  **Commit**: YES (groups with Tasks 1, 2)
  - Message: `test(cases): add TDD tests for delete case endpoint and UI`
  - Files: `frontend/src/__tests__/BrowseCases.test.tsx`
  - Pre-commit: `npx vitest run --collect-only`

---

- [x] 4. Backend TDD Green - Implement DELETE /cases/{patient_id} endpoint

  **What to do**:
  - Add `DELETE /cases/{patient_id}` endpoint to `backend/api/cases.py`
  - Implementation steps:
    1. Query Patient by patient_id → 404 if not found
    2. Get all VCFFiles for this patient, delete files from disk (os.path.exists + os.remove)
    3. Delete non-cascaded records: CaseDocument→CaseEmbedding (via cascade on CaseDocument), ChatSession→ChatMessageRecord (via cascade on ChatSession), LLMSettings
    4. Call `embedding_service.clear_index()` to reset FAISS in-memory index
    5. Delete the Patient record (SQLAlchemy cascade handles VCFFile→Variant→ACMG* + Reports)
    6. Commit transaction; on any error, rollback
  - Return `{message: "Case deleted", patient_id: patient_id}`
  - Run all pytest tests to verify GREEN

  **Must NOT do**:
  - Do NOT delete SkillConfig (it's global, not per-patient)
  - Do NOT add soft-delete or audit trail
  - Do NOT add permission checks

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Backend endpoint with multiple DB operations and file I/O, needs careful implementation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5)
  - **Parallel Group**: Wave 2 (with Task 5)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1 (need tests to make green)

  **References**:

  **Pattern References** (existing code to follow):
  - `backend/api/cases.py:52-103` - Existing list_cases endpoint (DB query patterns, response format)
  - `backend/api/settings.py:181-191` - Existing DELETE endpoint pattern

  **API/Type References** (contracts to implement against):
  - `backend/database/models.py:11-34` - Patient model with cascade relationships (VCFFile, ClinicalReport, ResearchReport)
  - `backend/database/models.py:37-54` - VCFFile model with `file_path` column
  - `backend/database/case_models.py:11-34` - CaseDocument model (manual deletion needed)
  - `backend/database/case_models.py:59-78` - ChatSession model (manual deletion needed)
  - `backend/database/case_models.py:104-133` - LLMSettings model (manual deletion needed)
  - `backend/services/embedding_service.py:203-215` - `remove_document()` and `clear_index()` methods

  **Test References** (tests that must pass):
  - `tests/test_delete_case.py` - All 6 test cases must PASS after implementation

  **WHY Each Reference Matters**:
  - `cases.py:52-103`: Copy the DB session usage pattern
  - `settings.py:181-191`: Copy the DELETE endpoint structure
  - `models.py`: Know which relationships cascade automatically (just delete Patient) vs need manual cleanup
  - `case_models.py`: These are the non-cascaded models that MUST be explicitly deleted before Patient deletion
  - `embedding_service.py:203-215`: `clear_index()` resets FAISS after CaseDocument deletion

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] `python -m pytest tests/test_delete_case.py -v` → 6 tests PASS
  - [ ] DELETE /cases/{patient_id} returns 200 for existing case
  - [ ] DELETE /cases/{patient_id} returns 404 for non-existent case

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: TDD Green - all tests pass
    Tool: Bash (pytest)
    Preconditions: DELETE endpoint implemented
    Steps:
      1. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing && python -m pytest tests/test_delete_case.py -v
      2. Assert: All 6 tests PASS
    Expected Result: 6 passed, 0 failed
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-4-tdd-green.txt

  Scenario: DELETE non-existent case returns 404
    Tool: Bash (curl with test server)
    Preconditions: Backend server running
    Steps:
      1. Run: curl -s -o /dev/null -w "%{http_code}" -X DELETE http://localhost:8000/api/cases/99999
      2. Assert: HTTP status 404
    Expected Result: 404
    Failure Indicators: 200 (case shouldn't exist), 500 (server error)
    Evidence: .sisyphus/evidence/task-4-404.txt

  Scenario: Delete case with missing VCF file on disk (graceful handling)
    Tool: Bash (pytest)
    Preconditions: Test for missing file scenario
    Steps:
      1. Run: python -m pytest tests/test_delete_case.py::test_delete_case_file_missing_on_disk -v
      2. Assert: Test passes (no error thrown when file missing)
    Expected Result: PASS
    Failure Indicators: FAIL (unhandled FileNotFoundError)
    Evidence: .sisyphus/evidence/task-4-missing-file.txt
  ```

  **Commit**: YES (groups with Task 5)
  - Message: `feat(cases): implement delete case with cascade cleanup and file removal`
  - Files: `backend/api/cases.py`
  - Pre-commit: `python -m pytest tests/test_delete_case.py -v`

---

- [x] 5. Frontend TDD Green - Implement delete button in BrowseCases + update App.tsx

  **What to do**:
  - Update `BrowseCases.tsx`:
    1. Add `activePatientId` and `onDeleteCase` to props
    2. Add Delete button with `Popconfirm` in Action column (next to existing Open button)
    3. Popconfirm title: "Are you sure you want to delete this case? This action cannot be undone."
    4. On confirm: call `api.deleteCase(patientId)`, then call `loadCases()` to refresh list, then call `onDeleteCase(patientId)` to notify parent
    5. Disable Delete button if `record.patient_id === activePatientId` (currently active case)
    6. Show loading state (Spin) on Delete button during API call
    7. Handle error: show `message.error()` on API failure
  - Update `App.tsx`:
    1. Add `handleDeleteCase(patientId: number)` callback
    2. If deleted case is the active one (`sessionInfo?.patientId === String(patientId)`): clear session + redirect to browse
    3. Pass `activePatientId={sessionInfo?.patientId ? Number(sessionInfo.patientId) : null}` and `onDeleteCase={handleDeleteCase}` to BrowseCases
  - Update `BrowseCasesProps` interface with new props
  - Run vitest tests to verify GREEN

  **Must NOT do**:
  - Do NOT add toast/notification beyond basic message.error
  - Do NOT add animation effects on deletion
  - Do NOT modify the Open button behavior
  - Do NOT add bulk delete functionality

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Multi-file changes (BrowseCases + App.tsx), UI interaction logic, state management
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 4)
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 2, 3 (need API method and tests)

  **References**:

  **Pattern References** (existing code to follow):
  - `frontend/src/pages/BrowseCases.tsx:169-188` - Existing Action column render (Open button pattern)
  - `frontend/src/App.tsx:73-76` - `handleOpenCase` callback pattern (for `handleDeleteCase`)

  **API/Type References** (contracts to implement against):
  - `frontend/src/services/api.ts` - `deleteCase(patientId)` method (added in Task 2)
  - `frontend/src/pages/BrowseCases.tsx:49-51` - BrowseCasesProps interface

  **Test References** (tests that must pass):
  - `frontend/src/__tests__/BrowseCases.test.tsx` - All 5 test cases must PASS

  **External References**:
  - Ant Design Popconfirm: `https://ant.design/components/popconfirm` - API, props
  - Ant Design message: `https://ant.design/components/message` - message.error() usage

  **WHY Each Reference Matters**:
  - `BrowseCases.tsx:169-188`: Understand how to add to existing Action column (Space component, Button placement)
  - `App.tsx:73-76`: Copy the callback pattern for `handleDeleteCase`
  - `api.ts`: The `deleteCase` method signature to call
  - `BrowseCasesProps`: Extend the interface with new props

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] `npx vitest run src/__tests__/BrowseCases.test.tsx` → 5 tests PASS
  - [ ] `npm run build` → build success

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: TDD Green - all frontend tests pass
    Tool: Bash (vitest)
    Preconditions: Delete UI implemented in BrowseCases
    Steps:
      1. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing/frontend && npx vitest run src/__tests__/BrowseCases.test.tsx
      2. Assert: All 5 tests PASS
    Expected Result: 5 passed, 0 failed
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-5-tdd-green.txt

  Scenario: Frontend build passes
    Tool: Bash (npm run build)
    Preconditions: All changes applied
    Steps:
      1. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing/frontend && npm run build
      2. Assert: Exit code 0, no TypeScript errors
    Expected Result: Build successful
    Failure Indicators: TypeScript type errors
    Evidence: .sisyphus/evidence/task-5-build.txt

  Scenario: Delete button disabled for active case
    Tool: Bash (grep)
    Preconditions: Component updated
    Steps:
      1. Grep for "disabled" in BrowseCases.tsx Action column
      2. Assert: Condition checks record.patient_id === activePatientId
    Expected Result: Disabled condition found in delete button
    Failure Indicators: No disabled logic found
    Evidence: .sisyphus/evidence/task-5-disabled-logic.txt

  Scenario: Popconfirm exists on delete button
    Tool: Bash (grep)
    Preconditions: Component updated
    Steps:
      1. Grep for "Popconfirm" in BrowseCases.tsx
      2. Assert: Popconfirm component wraps delete button with confirmation text
    Expected Result: Popconfirm found with title text
    Failure Indicators: No Popconfirm found (no confirmation dialog)
    Evidence: .sisyphus/evidence/task-5-popconfirm.txt
  ```

  **Commit**: YES (groups with Task 4)
  - Message: `feat(cases): implement delete case with Popconfirm and cascade cleanup`
  - Files: `frontend/src/pages/BrowseCases.tsx, frontend/src/App.tsx`
  - Pre-commit: `npm run build`

---

- [x] 6. Build Verification + Integration QA

  **What to do**:
  - Run full frontend build: `cd frontend && npm run build`
  - Run backend tests: `cd /mnt/zzb/peixunban/hujie/hanjianbing && python -m pytest tests/test_delete_case.py -v`
  - Run frontend tests: `cd frontend && npx vitest run`
  - Verify no regressions in existing tests
  - Test the complete delete flow via curl (if backend server available)

  **Must NOT do**:
  - Do NOT make code changes (verification only)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Running build and test commands, no code changes
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential after Wave 2)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 4, 5

  **References**:

  **Pattern References**:
  - None (verification only)

  **Acceptance Criteria**:
  - [ ] `npm run build` → PASS
  - [ ] `python -m pytest tests/test_delete_case.py -v` → all PASS
  - [ ] `npx vitest run src/__tests__/BrowseCases.test.tsx` → all PASS

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Full build + test suite passes
    Tool: Bash (npm + pytest)
    Preconditions: All implementation tasks complete
    Steps:
      1. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing/frontend && npm run build
      2. Assert: Build success
      3. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing && python -m pytest tests/test_delete_case.py -v
      4. Assert: All tests pass
      5. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing/frontend && npx vitest run src/__tests__/BrowseCases.test.tsx
      6. Assert: All tests pass
    Expected Result: All 3 commands succeed
    Failure Indicators: Any build failure or test failure
    Evidence: .sisyphus/evidence/task-6-integration.txt

  Scenario: No regressions in existing functionality
    Tool: Bash (npm run build)
    Preconditions: All changes applied
    Steps:
      1. Run: cd /mnt/zzb/peixunban/hujie/hanjianbing/frontend && npm run build
      2. Assert: No new TypeScript errors introduced
    Expected Result: Build success with same warnings as before (only chunk size warning)
    Failure Indicators: New type errors or compilation failures
    Evidence: .sisyphus/evidence/task-6-no-regression.txt
  ```

  **Commit**: NO (verification only, no code changes)

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter + `bun test`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task. Test edge cases. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec. Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(cases): add TDD tests for delete case endpoint and UI` - test files + api.ts
- **Wave 2**: `feat(cases): implement delete case with Popconfirm and cascade cleanup` - implementation files
- **Wave 3**: `test(cases): verify delete case integration` - evidence files

---

## Success Criteria

### Verification Commands
```bash
cd backend && pytest tests/test_delete_case.py -v  # Expected: all tests PASS
cd frontend && npx vitest run src/__tests__/BrowseCases.test.tsx  # Expected: all tests PASS
cd frontend && npm run build  # Expected: build success
curl -X DELETE http://localhost:8000/api/cases/1  # Expected: 200 {"message": "Case deleted", "patient_id": 1}
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
