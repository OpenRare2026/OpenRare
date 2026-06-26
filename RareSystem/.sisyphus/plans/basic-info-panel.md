# Basic Information Panel on AnalysisPage

## TL;DR

> **Quick Summary**: Add a resizable "Basic Information" panel above the Variants section on AnalysisPage, displaying patient ID, clinical phenotypes, medical history, and related case metadata.
> 
> **Deliverables**:
> - New `BasicInfoPanel` React component with patient info display
> - `getCase(patientId)` API method in frontend api.ts
> - Integration into AnalysisPage with vertical resize handle
> - Responsive, collapsible layout
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 → Task 3 → Task 4

---

## Context

### Original Request
在Variants的上面部分应该还有一个panel，来展示一些患者的相关信息，包括前面提交的比如患者id，临床表型等相关的内容，这个部分可以叫做 basic information。前端方面，大小可自行调节。

### Interview Summary
**Key Discussions**:
- Panel displays patient info submitted during upload (ID, name, age, sex, ethnicity, diagnosis, medical history)
- Panel should be resizable (user can adjust height)
- Named "Basic Information"
- Read-only display (no editing capability needed)

**Research Findings**:
- Backend API `GET /api/cases/{patient_id}` already exists, returns CaseSummary with all needed fields
- AnalysisPage already has horizontal resize (left/right drag divider) - need to add vertical resize
- Patient type already defined in `frontend/src/types.ts`
- Frontend `api.ts` only has `getCases()`, needs `getCase(patientId)` added

### Metis Review
Metis/Oracle agents unavailable due to model region restrictions. Self-review performed.
**Identified Gaps** (addressed):
- Patient ID on AnalysisPage is currently ignored (`void _patientId`) - need to actually use it
- Need to handle loading/error states for patient data fetch
- Need to handle collapsed state for the panel to maximize variant viewing space

---

## Work Objectives

### Core Objective
Add a resizable Basic Information panel above the Variants tabs on the AnalysisPage left panel, displaying patient demographics, clinical phenotype, and medical history.

### Concrete Deliverables
- `frontend/src/components/BasicInfoPanel.tsx` - New component
- Updated `frontend/src/services/api.ts` - Add getCase() method
- Updated `frontend/src/pages/AnalysisPage.tsx` - Integrate panel with vertical resize

### Definition of Done
- [ ] BasicInfoPanel renders patient info (ID, name, age, sex, ethnicity, diagnosis, medical history)
- [ ] Panel height is resizable via drag handle
- [ ] Panel can be collapsed/expanded
- [ ] Frontend builds without errors

### Must Have
- Patient ID, name, age, sex display
- Clinical phenotype (diagnosis_description) display
- Medical history display
- Resizable panel height (drag handle)
- Collapsible panel (toggle collapse)
- Loading state while fetching patient data

### Must NOT Have (Guardrails)
- NO editing capability for patient info (read-only)
- NO backend changes (API already exists)
- NO modification to existing VariantList or ChatInterface components
- NO patient data persistence on the frontend (fetch on mount)
- NO personally identifiable information display beyond what's already de-identified

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (Vite + React + TypeScript)
- **Automated tests**: None (UI component, visual verification)
- **Framework**: None for this task

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright (playwright skill) - Navigate, interact, assert DOM, screenshot
- **Build verification**: Use Bash (npm run build)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - API + component):
├── Task 1: Add getCase() API method [quick]
└── Task 2: Create BasicInfoPanel component [visual-engineering]

Wave 2 (After Wave 1 - integration + verification):
├── Task 3: Integrate BasicInfoPanel into AnalysisPage [visual-engineering]
└── Task 4: Build verification + visual QA [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 3 → Task 4
Parallel Speedup: Task 1 + Task 2 can run in parallel
Max Concurrent: 2
```

### Dependency Matrix

- **1**: - Task 3
- **2**: - Task 3
- **3**: 1, 2 - Task 4
- **4**: 3 - F1-F4

### Agent Dispatch Summary

- **1**: **1** - T1 → `quick`
- **1**: **1** - T2 → `visual-engineering`
- **2**: **2** - T3 → `visual-engineering`, T4 → `quick`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Add getCase(patientId) API method to frontend

  **What to do**:
  - Add `getCase(patientId: number)` method to `frontend/src/services/api.ts`
  - Method should call `GET /api/cases/{patientId}`
  - Return type should match CaseSummary structure from backend
  - Add CaseSummary type definition to `frontend/src/types.ts`

  **Must NOT do**:
  - Do NOT modify backend API
  - Do NOT change existing getCases() method

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single method addition, straightforward
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `frontend/src/services/api.ts:495-500` - Existing getCases() method pattern to follow

  **API/Type References**:
  - `backend/api/cases.py:31-43` - CaseSummary Pydantic model with field definitions
  - `backend/api/cases.py:106-156` - GET /cases/{patient_id} endpoint returning CaseSummary
  - `frontend/src/types.ts:1-9` - Patient interface (existing, for reference)

  **WHY Each Reference Matters**:
  - `api.ts:getCases()` shows the pattern for API methods (this.request, method, url)
  - `cases.py:CaseSummary` shows the exact response shape to type against
  - `types.ts:Patient` shows existing type patterns to match style

  **Acceptance Criteria**:

  - [ ] `getCase(patientId: number)` method exists in api.ts
  - [ ] CaseSummary type defined in types.ts with: patient_id, patient_name, age, sex, ethnicity, diagnosis_description, medical_history, vcf_files, total_variants, total_classified
  - [ ] Frontend `npm run build` succeeds

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: API method exists and returns correct type
    Tool: Bash
    Preconditions: Frontend project is set up
    Steps:
      1. grep -c "getCase" frontend/src/services/api.ts
      2. Assert count >= 1
      3. grep "async getCase" frontend/src/services/api.ts
      4. Assert method signature includes patientId parameter
    Expected Result: getCase method found with correct signature
    Failure Indicators: Method not found or signature mismatch
    Evidence: .sisyphus/evidence/task-1-api-method.txt

  Scenario: Frontend build passes
    Tool: Bash
    Preconditions: All changes saved
    Steps:
      1. cd frontend && npm run build
      2. Assert exit code 0
      3. Assert no TypeScript errors
    Expected Result: Build completes successfully
    Failure Indicators: TypeScript errors or build failure
    Evidence: .sisyphus/evidence/task-1-build.txt
  ```

  **Commit**: YES (groups with Task 2)
  - Message: `feat(frontend): add getCase API method and CaseSummary type`
  - Files: `frontend/src/services/api.ts`, `frontend/src/types.ts`
  - Pre-commit: `cd frontend && npm run build`

---

- [x] 2. Create BasicInfoPanel component

  **What to do**:
  - Create `frontend/src/components/BasicInfoPanel.tsx`
  - Component props: `patientId: number`, `onCollapse?: (collapsed: boolean) => void`
  - On mount, fetch patient data via `api.getCase(patientId)`
  - Display patient info in a clean card layout:
    - Header row: Patient ID (name), Age, Sex, Ethnicity (compact badges)
    - Expandable section: Clinical Phenotype (diagnosis_description)
    - Expandable section: Medical History (medical_history)
    - Footer row: VCF files count, Total variants, Classified variants (small stats)
  - Loading state: Skeleton/spin while fetching
  - Error state: Alert if fetch fails
  - Collapsible: Toggle button to collapse/expand
  - Use Ant Design components: Card, Descriptions, Tag, Collapse, Spin, Alert, Badge

  **Must NOT do**:
  - Do NOT add editing capability (read-only display)
  - Do NOT store patient data in global state (local component state only)
  - Do NOT modify existing components

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Frontend UI component with layout and styling concerns
  - **Skills**: [`/frontend-ui-ux`]
    - `/frontend-ui-ux`: UI/UX component design, styling, layout
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not needed for component creation, only for testing later

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `frontend/src/components/Settings.tsx:1-30` - Component import pattern (Ant Design, types)
  - `frontend/src/components/ACMGDisplay.tsx` - Existing component pattern for displaying structured data
  - `frontend/src/components/DualTrackReport.tsx` - Report display pattern

  **API/Type References**:
  - `backend/api/cases.py:31-43` - CaseSummary fields to display
  - `frontend/src/types.ts:1-9` - Patient interface (for field names)
  - `frontend/src/services/api.ts:495-500` - getCases() pattern (getCase() will be similar)

  **WHY Each Reference Matters**:
  - `Settings.tsx` shows import conventions and Ant Design component usage patterns
  - `CaseSummary` defines exactly what data fields are available and their types
  - `Patient` interface shows the existing type structure to maintain consistency

  **Acceptance Criteria**:

  - [ ] BasicInfoPanel.tsx exists in frontend/src/components/
  - [ ] Component fetches patient data on mount using api.getCase()
  - [ ] Displays: Patient ID/name, age, sex, ethnicity
  - [ ] Displays: Clinical phenotype (diagnosis_description)
  - [ ] Displays: Medical history (medical_history)
  - [ ] Displays: VCF stats (total_variants, total_classified)
  - [ ] Has loading state (Spin/Skeleton)
  - [ ] Has error state (Alert)
  - [ ] Has collapse/expand toggle
  - [ ] Frontend `npm run build` succeeds

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Component renders with patient data
    Tool: Playwright
    Preconditions: Backend running, patient data exists
    Steps:
      1. Navigate to analysis page
      2. Assert BasicInfoPanel is visible
      3. Assert patient name/ID is displayed
      4. Assert clinical phenotype section exists
      5. Assert medical history section exists
    Expected Result: All patient info fields visible
    Failure Indicators: Missing sections or empty data
    Evidence: .sisyphus/evidence/task-2-patient-data-render.png

  Scenario: Component shows loading state
    Tool: Playwright
    Preconditions: Backend slow to respond (or no data)
    Steps:
      1. Navigate to analysis page
      2. Assert loading spinner/skeleton is visible before data loads
    Expected Result: Loading indicator shown while fetching
    Failure Indicators: No loading state visible
    Evidence: .sisyphus/evidence/task-2-loading-state.png

  Scenario: Component handles missing patient data
    Tool: Playwright
    Preconditions: Backend returns 404 for patient
    Steps:
      1. Navigate to analysis page with non-existent patient
      2. Assert error Alert is shown
      3. Assert Alert message is user-friendly
    Expected Result: Error message displayed gracefully
    Failure Indicators: Blank screen or uncaught error
    Evidence: .sisyphus/evidence/task-2-error-state.png

  Scenario: Collapse toggle works
    Tool: Playwright
    Preconditions: Patient data loaded
    Steps:
      1. Click collapse toggle button
      2. Assert panel content is hidden/collapsed
      3. Click toggle again
      4. Assert panel content is visible/expanded
    Expected Result: Panel toggles between collapsed and expanded
    Failure Indicators: Toggle has no effect
    Evidence: .sisyphus/evidence/task-2-collapse-toggle.png
  ```

  **Commit**: YES (groups with Task 1)
  - Message: `feat(frontend): add BasicInfoPanel component`
  - Files: `frontend/src/components/BasicInfoPanel.tsx`
  - Pre-commit: `cd frontend && npm run build`

---

- [x] 3. Integrate BasicInfoPanel into AnalysisPage with vertical resize

  **What to do**:
  - Modify `frontend/src/pages/AnalysisPage.tsx`
  - Add state for: `patientData` (from API), `basicInfoHeight` (panel height, default ~200px), `basicInfoCollapsed` (collapsed state)
  - Replace `void _patientId` with actual patient ID usage (convert to number)
  - Add `useEffect` to fetch patient data on mount via `api.getCase(NUMERIC_PATIENT_ID)`
  - Insert BasicInfoPanel above the Tabs in the left panel
  - Add a vertical drag resize handle between BasicInfoPanel and Tabs
  - Implement mouse down/move/up handlers for vertical resize (similar to existing horizontal resize)
  - When collapsed, BasicInfoPanel shows only header row (compact)
  - Pass height via style prop to BasicInfoPanel for resizing

  **Must NOT do**:
  - Do NOT change the existing horizontal left/right split
  - Do NOT modify VariantList, ChatInterface, or other existing components
  - Do NOT break the existing Tab navigation

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Layout integration with resize handling, CSS adjustments
  - **Skills**: [`/frontend-ui-ux`]
    - `/frontend-ui-ux`: Layout, resize behavior, integration
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not needed for integration work, only for final testing

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential after Wave 1)
  - **Blocks**: Task 4
  - **Blocked By**: Task 1, Task 2

  **References**:

  **Pattern References**:
  - `frontend/src/pages/AnalysisPage.tsx:27-120` - Current page structure, resize handler pattern, state management
  - `frontend/src/pages/AnalysisPage.tsx:90-120` - Existing horizontal resize (mousedown/mousemove/mouseup) - copy this pattern for vertical resize
  - `frontend/src/pages/AnalysisPage.tsx:172-214` - Left panel layout where BasicInfoPanel goes above Tabs

  **API/Type References**:
  - `frontend/src/components/BasicInfoPanel.tsx` - Component just created (Task 2) - its props interface
  - `frontend/src/services/api.ts` - getCase() method just added (Task 1)

  **WHY Each Reference Matters**:
  - `AnalysisPage.tsx` is the exact file being modified - shows current layout structure
  - The existing horizontal resize pattern at lines 90-120 should be adapted for vertical resize
  - The left panel at lines 172-214 is where the panel needs to be inserted

  **Acceptance Criteria**:

  - [ ] BasicInfoPanel rendered above Tabs in left panel
  - [ ] Vertical drag handle between BasicInfoPanel and Tabs
  - [ ] Drag handle changes BasicInfoPanel height dynamically
  - [ ] Min height constraint prevents panel from being too small
  - [ ] BasicInfoPanel can be collapsed to show only header
  - [ ] Patient data fetched on mount
  - [ ] Existing horizontal resize still works
  - [ ] All existing Tabs (Variants, Visualization, Reports) still work
  - [ ] Frontend `npm run build` succeeds

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: BasicInfoPanel appears above Variants tab
    Tool: Playwright
    Preconditions: App running, patient data available
    Steps:
      1. Navigate to analysis page
      2. Assert BasicInfoPanel is visible
      3. Assert "Variants" tab is below BasicInfoPanel
      4. Assert patient info is displayed
    Expected Result: BasicInfoPanel visible above Variants, data shown
    Failure Indicators: Panel not visible or Variants tab missing
    Evidence: .sisyphus/evidence/task-3-basic-info-above-variants.png

  Scenario: Vertical resize works
    Tool: Playwright
    Preconditions: On analysis page
    Steps:
      1. Locate the vertical resize handle between BasicInfoPanel and Tabs
      2. Drag handle down by 100px
      3. Assert BasicInfoPanel height increased
      4. Drag handle up by 50px
      5. Assert BasicInfoPanel height decreased
    Expected Result: Panel height changes when drag handle is moved
    Failure Indicators: Height doesn't change or handle doesn't work
    Evidence: .sisyphus/evidence/task-3-vertical-resize.png

  Scenario: Existing horizontal resize still works
    Tool: Playwright
    Preconditions: On analysis page
    Steps:
      1. Locate the horizontal resize divider between left and right panels
      2. Drag divider to the right
      3. Assert left panel width increased
      4. Drag divider to the left
      5. Assert left panel width decreased
    Expected Result: Original left/right resize still works
    Failure Indicators: Horizontal resize broken
    Evidence: .sisyphus/evidence/task-3-horizontal-resize-still-works.png

  Scenario: Collapse toggle reduces panel height
    Tool: Playwright
    Preconditions: On analysis page, BasicInfoPanel expanded
    Steps:
      1. Click collapse toggle on BasicInfoPanel
      2. Assert panel shows only compact header
      3. Assert remaining height given to Variants tab area
    Expected Result: Panel collapses, Variants area gets more space
    Failure Indicators: Panel doesn't collapse or layout breaks
    Evidence: .sisyphus/evidence/task-3-collapse-works.png
  ```

  **Commit**: YES
  - Message: `feat(frontend): integrate BasicInfoPanel into AnalysisPage with vertical resize`
  - Files: `frontend/src/pages/AnalysisPage.tsx`
  - Pre-commit: `cd frontend && npm run build`

---

- [x] 4. Build verification + visual QA

  **What to do**:
  - Run `npm run build` to verify no TypeScript errors
  - Start dev server and take screenshot of the analysis page
  - Verify BasicInfoPanel renders correctly
  - Verify resize handles work (both horizontal and vertical)
  - Verify collapse/expand toggle works

  **Must NOT do**:
  - Do NOT modify any code
  - Do NOT add new features

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification-only task
  - **Skills**: [`/playwright`]
    - `/playwright`: Browser automation for visual QA

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (after Task 3)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 3

  **References**:

  **Pattern References**:
  - `frontend/src/pages/AnalysisPage.tsx` - The page being verified

  **WHY Each Reference Matters**:
  - AnalysisPage is where the integration was done, need to verify it

  **Acceptance Criteria**:

  - [ ] `npm run build` succeeds with no errors
  - [ ] Screenshots captured showing BasicInfoPanel in place
  - [ ] No TypeScript errors

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Frontend build succeeds
    Tool: Bash
    Preconditions: All code changes complete
    Steps:
      1. cd frontend && npm run build
      2. Assert exit code 0
      3. Assert "built in" appears in output
    Expected Result: Build succeeds
    Failure Indicators: TypeScript errors or build failure
    Evidence: .sisyphus/evidence/task-4-build-output.txt

  Scenario: Visual QA - BasicInfoPanel visible
    Tool: Playwright
    Preconditions: Dev server running
    Steps:
      1. Navigate to analysis page
      2. Take screenshot
      3. Assert BasicInfoPanel is visible in screenshot
      4. Assert "Basic Information" header visible
    Expected Result: Panel visible with correct layout
    Failure Indicators: Panel missing or layout broken
    Evidence: .sisyphus/evidence/task-4-visual-qa.png
  ```

  **Commit**: NO (verification only)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + `npm run build`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration. Test edge cases: empty patient data, very long text. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1+2**: `feat(frontend): add getCase API, CaseSummary type, and BasicInfoPanel component` - api.ts, types.ts, BasicInfoPanel.tsx
- **3**: `feat(frontend): integrate BasicInfoPanel into AnalysisPage with vertical resize` - AnalysisPage.tsx

---

## Success Criteria

### Verification Commands
```bash
cd frontend && npm run build  # Expected: build succeeds
cd frontend && npx tsc --noEmit  # Expected: no errors
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Frontend builds without errors
- [ ] BasicInfoPanel visible on AnalysisPage
- [ ] Vertical resize works
- [ ] Collapse toggle works
