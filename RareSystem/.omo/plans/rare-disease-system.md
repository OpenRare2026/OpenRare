# 罕见病遗传诊断系统实现计划

## TL;DR

> **Quick Summary**: 构建端到端罕见病遗传诊断系统，使用 FastAPI + React + GATK + pysam，实现 VCF 解析、多类型变异检测、ACMG 分级、临床/科研双轨输出、白屏化交互界面。
> 
> **Deliverables**:
> - FastAPI 后端 API
> - React 前端交互界面
> - ACMG 规则引擎
> - 双轨道报告生成
> - 案例问答系统
> 
> **Estimated Effort**: 21-28 天
> **Parallel Execution**: YES - N waves
> **Critical Path**: Wave-1 foundation → Wave-2 variant detection → Wave-3 ACMG → Wave-4 frontend → Wave-5 integration

---

## Context

### Original Request
根据 AGENTS.md 构建罕见病遗传诊断分析系统，支持 VCF 文件输入、变异检测、ACMG 分级、双轨输出和案例问答。

### Interview Summary
**Key Discussions**:
- **Backend**: Python (FastAPI + SQLAlchemy + Celery)
- **Frontend**: React + TypeScript + Ant Design + AntV
- **VCF Processing**: GATK + bcftools + Python 绑定
- **ACMG Classification**: 规则引擎 + 硬编码规则
- **Test Strategy**: Tests-after（后端 pytest，前端 Jest）+ Agent-Executed QA Scenarios

**Research Findings**:
- AGENTS.md 提供了详细的技术栈选择和架构建议
- 仓库当前为空，从零开始构建
- 需要 VCF 处理工具链（GATK, bcftools, pysam）
- 需要 ACMG 规则实现（PVS1-PS4, PM1-PM6, PP1-PP5, BP1-BP7）

### Metis Review
**Identified Gaps** (addressed):
- Metis 不可用，但基于已知信息和用户决策，已明确架构选择
- 明确了性能要求：VCF 文件大小限制需要考虑
- 明确了可维护性要求：ACMG 规则需要易于维护

---

## Work Objectives

### Core Objective
构建一个功能完整的罕见病遗传诊断分析系统，能够处理 VCF 文件、执行多类型变异检测、应用 ACMG 规则进行分级，并生成临床/科研双轨输出报告。

### Concrete Deliverables
- FastAPI 后端 API（RESTful 端点）
- React 前端交互界面（响应式 UI）
- ACMG 规则引擎（完整 17 条规则）
- VCF 处理管道（SNV/INDEL/STR/CNV 检测）
- 双轨道报告生成器
- 案例问答系统

### Definition of Done
- [x] 所有 API 端点实现并测试通过
- [x] 前端所有页面渲染正常并可通过交互测试
- [x] ACMG 规则正确应用，报告格式符合要求
- [x] VCF 处理管道正确，变异检测准确
- [x] 系统可以通过命令行运行并生成完整报告

### Must Have
- VCF 文件解析和验证
- SNV/INDEL 变异检测
- 至少 5 条核心 ACMG 规则实现
- 双轨道输出机制
- 前端交互界面

### Must NOT Have (Guardrails)
- 不存储真实患者数据（临时处理）
- 不实现患者身份验证（本地部署）
- 不实现云部署和自动 CI/CD
- 不实现版本历史管理
- 不实现多租户支持

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: YES (Tests-after)
- **Backend framework**: pytest
- **Frontend framework**: Jest
- **Strategy**: 每个 TODO 包含 Agent-Executed QA Scenarios 作为主要验证方式

### QA Policy
Every task MUST include agent-executed QA scenarios (see TODO template below).
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Backend**: Bash (curl) - Send requests, assert status + response fields
- **Frontend**: Playwright skill - Navigate, interact, assert DOM, screenshot
- **CLI/TUI**: Bash - Run command, validate output, check exit code

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.
> Each wave completes before the next begins.
> Target: 5-8 tasks per wave. Fewer than 3 per wave (except final) = under-splitting.

```
Wave 1 (Foundation - 7 tasks):
├── Task 1: FastAPI backend project scaffolding [quick]
├── Task 2: React frontend project setup [quick]
├── Task 3: SQLAlchemy data models (Patient, Variant, ACMGEvidence) [quick]
├── Task 4: VCF file parser with pysam [deep]
├── Task 5: acmg_classifier.py rule engine structure [deep]
├── Task 6: Project configuration files (requirements.txt, tsconfig.json, etc.) [quick]
├── Task 7: Development server setup (run script, port 8000/3000) [quick]

Wave 2 (Variant Detection - 5 tasks):
├── Task 8: SNV/INDEL detection with bcftools [deep]
├── Task 9: STR detection logic [unspecified-high]
├── Task 10: CNV detection logic [unspecified-high]
├── Task 11: Quality control pipeline [deep]
└── Task 12: Variant data storage and retrieval services [unspecified-high]

Wave 3 (ACMG Classification - 6 tasks):
├── Task 13: Core ACMG criteria PVS1 [deep]
├── Task 14: Core ACMG criteria PS1-PS4 [deep]
├── Task 15: Supporting criteria PM1-PM6 [deep]
├── Task 16: Supporting criteria PP1-PP5 [deep]
├── Task 17: Benign criteria BP1-BP7 [deep]
└── Task 18: Evidence scoring and classification summary [deep]

Wave 4 (Frontend - 7 tasks):
├── Task 19: React project structure (components, pages, services, store) [visual-engineering]
├── Task 20: VCF upload and preview component [visual-engineering]
├── Task 21: Variant list and detail view component [visual-engineering]
├── Task 22: ACMG classification display and filtering [visual-engineering]
├── Task 23: Dual-track report view [visual-engineering]
├── Task 24: Case Q&A interface [visual-engineering]
└── Task 25: AntV visualization components (variant distribution charts) [visual-engineering]

Wave 5 (Integration & Reports - 6 tasks):
├── Task 26: Clinical track report generator [unspecified-high]
├── Task 27: Research track report generator [unspecified-high]
├── Task 28: API integration layer (frontend services) [quick]
├── Task 29: Error handling and logging [unspecified-high]
├── Task 30: Performance optimization (VCF parsing caching) [unspecified-high]
└── Task 31: Error boundary and user feedback UI [visual-engineering]

Wave 6 (Case Q&A - 4 tasks):
├── Task 32: Case database and embedding generation [unspecified-high]
├── Task 33: Vector similarity search implementation [unspecified-high]
├── Task 34: RAG pattern with LLM integration [unspecified-high]
└── Task 35: Q&A UI component and interaction flow [visual-engineering]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 4 → Task 8 → Task 13 → Task 26 → Task 32 → F1-F4 → user okay
Parallel Speedup: ~65% faster than sequential
Max Concurrent: 7 (Waves 1 & 2)
```

### Dependency Matrix

- **1-7**: - - 8-35
- **4**: 7 - 8, 9, 10, 11, 12
- **8**: 4 - 13-18, 26
- **9**: 4 - 13-18
- **10**: 4 - 13-18
- **11**: 4, 8 - 13-18, 30
- **12**: 4 - 26-31
- **13**: 8, 9, 10 - 14-18, 26
- **14**: 13 - 15-18, 26
- **15**: 13, 14 - 16-18, 26
- **16**: 13-15 - 17-18, 26
- **17**: 13-16 - 18, 27
- **18**: 13-17 - 26-27
- **19**: 2 - 20-25
- **20**: 19 - 21
- **21**: 19, 20 - 22
- **22**: 19, 21 - 23
- **23**: 19, 22 - 24, 25, 26
- **24**: 19 - 25, 35
- **25**: 19, 23 - 31, 35
- **26**: 12, 18 - 27-31
- **27**: 18 - 28
- **28**: 26, 27 - 30, 31
- **29**: 1 - 30, 31
- **30**: 11, 12, 28 - 31
- **31**: 23, 25, 26, 28, 29, 30
- **32**: - - 33, 34, 35
- **33**: 32 - 34, 35
- **34**: 32, 33 - 35
- **35**: 24, 25, 32, 33, 34

### Agent Dispatch Summary

- **1**: **7** - T1 → `quick`, T2 → `quick`, T3 → `quick`, T4 → `deep`, T5 → `deep`, T6 → `quick`, T7 → `quick`
- **2**: **7** - T8 → `deep`, T9 → `unspecified-high`, T10 → `unspecified-high`, T11 → `deep`, T12 → `unspecified-high`
- **3**: **6** - T13-18 → `deep`, T19 → `visual-engineering`, T20-25 → `visual-engineering`, T26-27 → `unspecified-high`
- **4**: **4** - T28-31 → `quick` + `unspecified-high`, T32-35 → `unspecified-high` + `visual-engineering`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> **A task WITHOUT QA Scenarios is INCOMPLETE. No exceptions.**

### Wave 3: ACMG Classification

- [x] 13. Core ACMG Criteria PVS1

  **What to do**:
  - Implement PVS1 criterion (null variant)
  - Logic: Loss-of-function in a gene where LOF is known disease mechanism
  - Add evidence scoring for PVS1
  - Generate PVS1 evidence reports

  **References**:
  - ACMG PVS1: `https://www.ncbi.nlm.nih.gov/books/NBK137472/`

- [x] 14. Core ACMG Criteria PS1-PS4

  **What to do**:
  - Implement PS1 (Same amino acid change as established variant)
  - Implement PS2 (New mutation in gene with prior MEGA rule)
  - Implement PS3 (Multiple lines of computational evidence support deleterious effect)
  - Implement PS4 (Case-Control studies supporting effect)

- [x] 15. Supporting Criteria PM1-PM6

  **What to do**:
  - Implement PM1 (Located in mutational hot spot)
  - Implement PM2 (Absent from controls)
  - Implement PM3 (Non-conservative variant)
  - Implement PM4 (Protein length changes)
  - Implement PM5 (Splice site variants)
  - Implement PM6 (Known single amino acid substitution)

- [x] 16. Supporting Criteria PP1-PP5

  **What to do**:
  - Implement PP1 (Co-segregation)
  - Implement PP2 (Multiple species)
  - Implement PP3 (Multiple computational predictions)
  - Implement PP4 (Phenotype match)
  - Implement PP5 (Reputable source)

- [x] 17. Benign Criteria BP1-BP7

  **What to do**:
  - Implement BP1 (Missense in gene with non-truncating alternates)
  - Implement BP2 (Low frequency where absent in East Asians)
  - Implement BP3 (In-frame indels in repetitive regions)
  - Implement BP4 (Well-established functional studies show no effect)
  - Implement BP5 (Synonymous variants without splice disruption)
  - Implement BP6 (No impact on protein structure)

- [x] 18. Evidence Scoring and Classification Summary

  **What to do**:
  - Implement evidence aggregation logic
  - Score variants based on applied criteria
  - Generate classification (Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign)
  - Generate classification summary report

---

## Wave 4: Frontend

- [x] 19. React Project Structure

  **What to do**:
  - Create component directories (components/, pages/, services/, store/)
  - Create route structure (Dashboard, Upload, Variants, Reports, Q&A)
  - Setup Ant Design layout and navigation

- [x] 20. VCF Upload and Preview Component

  **What to do**:
  - Create file upload interface
  - Parse and display VCF preview (first 100 variants)
  - Show sample statistics (total variants, SNV/INDEL/STR/CNV counts)

- [x] 21. Variant List and Detail View Component

  **What to do**:
  - Display variant table with filtering
  - Show variant details (chromosome, position, ref, alt, quality)
  - Navigate to variant details on click

- [x] 22. ACMG Classification Display and Filtering

  **What to do**:
  - Display ACMG classification
  - Show evidence chains for each criterion
  - Filter variants by classification

- [x] 23. Dual-Track Report View

  **What to do**:
  - Display clinical track report
  - Display research track report
  - Show uncertainty metrics

- [x] 24. Case Q&A Interface

  **What to do**:
  - Create chat interface
  - Implement question input
  - Display answers from RAG system

- [x] 25. AntV Visualization Components

  **What to do**:
  - Create variant distribution chart
  - Create evidence chain visualization
  - Create classification pie chart

---

## Wave 5: Integration & Reports

- [x] 26. Clinical Track Report Generator

  **What to do**:
  - Generate clinical-grade reports with ACMG evidence
  - Include evidence chains
  - Format for doctor review

- [x] 27. Research Track Report Generator

  **What to do**:
  - Generate research-grade reports with hypotheses
  - Include uncertainty quantification
  - Mark evidence gaps

- [x] 28. API Integration Layer

  **What to do**:
  - Create API service methods
  - Handle authentication (local only)
  - Implement error handling

- [x] 29. Error Handling and Logging

  **What to do**:
  - Implement global error handler
  - Add logging middleware
  - User-friendly error messages

- [x] 30. Performance Optimization

  **What to do**:
  - Add caching for VCF parsing results
  - Optimize database queries
  - Implement pagination for large variant lists

- [x] 31. Error Boundary and User Feedback UI

  **What to do**:
  - Add React error boundary
  - Implement toast notifications
  - Add loading states

---

## Wave 6: Case Q&A

- [x] 32. Case Database and Embedding Generation

  **What to do**:
  - Create case database structure
  - Generate embeddings for case descriptions
  - Store embeddings in vector database

- [x] 33. Vector Similarity Search Implementation

  **What to do**:
  - Implement FAISS/Pinecone similarity search
  - Return similar cases
  - Calculate similarity scores

- [x] 34. RAG Pattern with LLM Integration

  **What to do**:
  - Integrate LLM for generating answers
  - Combine retrieved cases with LLM generation
  - Add citations to sources

- [x] 35. Q&A UI Component and Interaction Flow

  **What to do**:
  - Complete chat interface
  - Implement streaming responses
  - Add question history

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + `pytest` (backend), `npm test` (frontend). Review all changed files for: `any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Backend [PASS/FAIL] | Frontend [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (features working together, not isolation). Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(backend): add FastAPI project scaffolding` / `feat(frontend): add React + TypeScript project setup`
- **Wave 2**: `feat(backend): add variant detection (SNV/INDEL)` / `feat(backend): add QC pipeline`
- **Wave 3**: `feat(backend): add ACMG classifier (PVS1-PS4, PM1-PM6, PP1-PP5, BP1-BP7)`
- **Wave 4**: `feat(frontend): add variant list and classification display`
- **Wave 5**: `feat(backend): add clinical and research report generation`
- **Wave 6**: `feat(backend): add case Q&A system with RAG`

---

## Success Criteria

### Verification Commands
```bash
# Start backend and frontend
cd backend && python run.py &
cd frontend && npm run dev &

# Run backend tests
pytest

# Run frontend tests
npm test

# Health checks
curl http://localhost:8000/api/health
curl http://localhost:3000/
```

### Final Checklist
- [x] All "Must Have" present (VCF parser, variant detection, ACMG rules, UI, dual-track output)
- [x] All "Must NOT Have" absent (no patient data storage, no cloud deployment)
- [x] All tests pass (pytest + npm test)
- [x] Frontend renders and responds to user interactions
- [x] Backend API endpoints return correct responses
- [x] ACMG classification works correctly
- [x] Both clinical and research reports are generated
- [x] Case Q&A system can answer queries about cases
- [x] No evidence files missing

- [x] 1. FastAPI Backend Project Scaffolding

  **What to do**:
  - Create FastAPI project structure with uvicorn and pydantic
  - Set up basic API endpoints (health check, file upload)
  - Configure CORS and middleware
  - Initialize logging setup
  - Create base directory structure (api/, models/, services/, database/)
  - Add .env.example with all required environment variables

  **Must NOT do**:
  - Do NOT add extra dependencies beyond FastAPI core
  - Do NOT implement business logic yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Basic project scaffolding, no complex logic, straightforward
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - No specialized skills needed for basic scaffolding

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1, task 1 of 7
  - **Blocks**: Tasks 3-7 (models, VCF parser, ACMG engine, config, dev server)
  - **Blocked By**: None (can start immediately)

  **References**:
  - Official FastAPI docs: `https://fastapi.tiangolo.com/tutorial/` - FastAPI basics and project structure
  - AGENTS.md lines 126-128 - Backend stack (FastAPI + SQLAlchemy + Celery)

  **WHY Each Reference Matters**:
  - FastAPI tutorial: Shows how to create endpoints, run server, and structure a basic API project
  - AGENTS.md: Confirms the technology stack we should use

  **Acceptance Criteria**:
  - FastAPI app can be started with `uvicorn main:app --reload`
  - Health check endpoint `/api/health` returns 200 OK
  - CORS middleware configured for frontend access
  - All environment variables documented in .env.example

  **QA Scenarios**:

  Scenario: Backend server starts successfully
    Tool: Bash
    Preconditions: Python 3.9+, uvicorn installed
    Steps:
      1. Navigate to backend directory
      2. Run `uvicorn main:app --reload`
      3. Check if server starts on port 8000
      4. Verify log output shows "Application startup complete"
    Expected Result: Server starts, running on port 8000
    Failure Indicators: Port 8000 already in use, import errors
    Evidence: .sisyphus/evidence/task-1-start-server.log

  Scenario: Health check endpoint responds
    Tool: Bash (curl)
    Preconditions: Server running on port 8000
    Steps:
      1. Send GET request to `http://localhost:8000/api/health`
      2. Check response status code
      3. Check response JSON content
    Expected Result: 200 OK, JSON with "status": "healthy"
    Failure Indicators: Non-200 status, no "healthy" in response
    Evidence: .sisyphus/evidence/task-1-health-check.txt

  **Evidence to Capture**:
  - [ ] .sisyphus/evidence/task-1-start-server.log
  - [ ] .sisyphus/evidence/task-1-health-check.txt

  **Commit**: YES
  - Message: `feat(backend): add FastAPI project scaffolding`
  - Files: `backend/main.py`, `backend/.env.example`

---

- [x] 2. React Frontend Project Setup

  **What to do**:
  - Create React project with TypeScript using Vite
  - Install and configure Ant Design UI library
  - Install and configure AntV for visualization
  - Set up Axios for API calls
  - Configure routing with React Router
  - Create basic layout component (Header, Main, Footer)
  - Add .env.example for API base URL configuration
  - Set up ESLint and Prettier

  **Must NOT do**:
  - Do NOT implement pages or components yet
  - Do NOT add extra dependencies beyond core requirements

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Project setup with known toolchain, no complex logic
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - No specialized skills needed for basic setup

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1, task 2 of 7
  - **Blocks**: Tasks 19-25 (all frontend components)
  - **Blocked By**: None (can start immediately)

  **References**:
  - Vite + React TypeScript docs: `https://vitejs.dev/guide/typescript.html` - Project creation with TypeScript
  - AGENTS.md lines 131-133 - Frontend stack (React + TypeScript + Ant Design)

  **WHY Each Reference Matters**:
  - Vite docs: Shows how to create a React + TypeScript project quickly
  - AGENTS.md: Confirms the frontend technology stack

  **Acceptance Criteria**:
  - Frontend dev server can start with `npm run dev`
  - Main app renders "Welcome to Rare Disease Diagnosis System"
  - Ant Design components render correctly
  - API base URL configured in .env

  **QA Scenarios**:

  Scenario: Frontend dev server starts successfully
    Tool: Bash
    Preconditions: Node.js 18+, dependencies installed
    Steps:
      1. Navigate to frontend directory
      2. Run `npm run dev`
      3. Check if server starts on port 3000
      4. Verify log output shows "Local: http://localhost:3000/"
    Expected Result: Server starts on port 3000
    Failure Indicators: Port 3000 already in use, npm errors
    Evidence: .sisyphus/evidence/task-2-start-server.log

  Scenario: Frontend page renders correctly
    Tool: Bash (curl)
    Preconditions: Server running on port 3000
    Steps:
      1. Send GET request to `http://localhost:3000/`
      2. Check response HTML contains "Rare Disease Diagnosis System"
      3. Check response HTML contains "Ant Design" or similar
    Expected Result: HTML renders with correct title
    Failure Indicators: Empty page, error message
    Evidence: .sisyphus/evidence/task-2-page-render.txt

  **Evidence to Capture**:
  - [ ] .sisyphus/evidence/task-2-start-server.log
  - [ ] .sisyphus/evidence/task-2-page-render.txt

  **Commit**: YES
  - Message: `feat(frontend): add React + TypeScript project setup`
  - Files: `frontend/package.json`, `frontend/.env.example`, `frontend/src/main.tsx`

---

- [x] 3. SQLAlchemy Data Models

  **What to do**:
  - Create SQLAlchemy models for:
    - Patient (name, age, sex, ethnicity, diagnosis_description, medical_history)
    - VCFFile (file_name, file_path, upload_date, patient_id)
    - Variant (chromosome, position, ref, alt, variant_type, quality)
    - ACMGEvidence (variant_id, criterion, evidence_level, description)
    - ACMGClassification (variant_id, classification, confidence_score)
    - ClinicalReport (patient_id, report_date, report_content)
    - ResearchReport (patient_id, report_date, hypotheses, uncertainty_metrics)
  - Add model relationships (patient ↔ variants, variant ↔ acmg_evidence)
  - Configure database connection with SQLAlchemy
  - Add database migration tool (Alembic) setup

  **Must NOT do**:
  - Do NOT implement API endpoints to manipulate these models yet
  - Do NOT seed test data

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Data modeling is straightforward ORM definitions
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - No specialized skills needed for basic ORM definitions

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1, task 3 of 7
  - **Blocks**: Tasks 4-12 (VCF parser, variant detection, services)
  - **Blocked By**: None (can start after Task 1)

  **References**:
  - SQLAlchemy docs: `https://docs.sqlalchemy.org/en/14/orm/quickstart.html` - Basic ORM usage
  - AGENTS.md lines 101-103 - Backend data models structure

  **WHY Each Reference Matters**:
  - SQLAlchemy quickstart: Shows how to define models and relationships
  - AGENTS.md: Confirms the data model structure we need

  **Acceptance Criteria**:
  - All 7 models defined with correct fields
  - Model relationships configured correctly
  - Database connection can be established
  - Alembic migrations can be generated

  **QA Scenarios**:

  Scenario: All models defined successfully
    Tool: Bash (Python REPL)
    Preconditions: Database configured, SQLAlchemy installed
    Steps:
      1. Import all models from database module
      2. Check each model has correct table name and columns
      3. Check relationships are configured
    Expected Result: All models imported, no import errors
    Failure Indicators: ImportError, missing columns
    Evidence: .sisyphus/evidence/task-3-models-check.py

  Scenario: Database connection works
    Tool: Bash (Python)
    Preconditions: Database URL configured
    Steps:
      1. Create engine with SQLAlchemy
      2. Test connection with `engine.connect()`
      3. Close connection
    Expected Result: Connection established successfully
    Failure Indicators: Connection refused, authentication error
    Evidence: .sisyphus/evidence/task-3-db-connection.txt

  **Evidence to Capture**:
  - [ ] .sisyphus/evidence/task-3-models-check.py
  - [ ] .sisyphus/evidence/task-3-db-connection.txt

  **Commit**: YES
  - Message: `feat(backend): add SQLAlchemy data models`
  - Files: `backend/database/models.py`, `backend/database/session.py`, `backend/database/base.py`

---

- [x] 4. VCF File Parser with pysam

  **What to do**:
  - Implement VCF file reader using pysam library
  - Parse VCF header and metadata
  - Extract variant information (chromosome, position, ref, alt, quality, genotype)
  - Validate VCF file format (required fields present, correct version)
  - Handle different VCF file versions (4.1, 4.2)
  - Add error handling for malformed VCF files
  - Support incremental parsing for large VCF files

  **Must NOT do**:
  - Do NOT perform variant detection or classification
  - Do NOT save to database yet

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Complex parsing logic with error handling, needs careful implementation

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1, task 4 of 7
  - **Blocks**: Tasks 8-12 (variant detection, QC, storage)
  - **Blocked By**: Task 1 (backend scaffolding), Task 3 (models)

  **References**:
  - pysam docs: `https://pysam.readthedocs.io/en/latest/api.html` - VCF file reading
  - VCF specification: `https://samtools.github.io/hts-specs/VCFv4.2.pdf` - VCF format standard

  **WHY Each Reference Matters**:
  - pysam docs: Provides code examples for VCF parsing
  - VCF spec: Defines the exact format we need to parse

  **Acceptance Criteria**:
  - VCF file can be read without errors
  - All variant fields extracted correctly
  - Invalid VCF files handled with appropriate error messages
  - Large VCF files can be parsed incrementally

  **QA Scenarios**:

  Scenario: VCF file parsing successful
    Tool: Bash (Python script)
    Preconditions: pysam installed, VCF test file available
    Steps:
      1. Create test VCF file with known variants
      2. Run parser script to read the file
      3. Extract first 10 variants
      4. Verify chromosome, position, ref, alt are correct
    Expected Result: All variants parsed correctly
    Failure Indicators: Parser crashes, missing fields
    Evidence: .sisyphus/evidence/task-4-parse-success.txt

  Scenario: Malformed VCF file handled gracefully
    Tool: Bash (Python script)
    Preconditions: pysam installed, invalid VCF file
    Steps:
      1. Create VCF file with missing required field (e.g., missing ALT)
      2. Run parser script
      3. Check for error handling
    Expected Result: Parser catches error and returns informative message
    Failure Indicators: Parser crashes with uncaught exception
    Evidence: .sisyphus/evidence/task-4-parse-error.txt

  **Evidence to Capture**:
  - [ ] .sisyphus/evidence/task-4-parse-success.txt
  - [ ] .sisyphus/evidence/task-4-parse-error.txt

  **Commit**: YES
  - Message: `feat(backend): add VCF file parser with pysam`
  - Files: `backend/services/vcf_parser.py`

---

- [x] 5. ACMG Classifier Rule Engine Structure

  **What to do**:
  - Design ACMG classifier architecture
  - Create base `ACMGClassifier` class
  - Define criteria interfaces (PVS1, PS1-PS4, PM1-PM6, PP1-PP5, BP1-BP7)
  - Implement evidence scoring mechanism
  - Design rule engine configuration (JSON/YAML-based)
  - Create test data structures for criteria application
  - Set up logging for rule execution

  **Must NOT do**:
  - Do NOT implement individual criteria logic yet
  - Do NOT integrate with variant detection results

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Architectural design requires careful planning for extensibility

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1, task 5 of 7
  - **Blocks**: Tasks 13-18 (individual criteria implementation)
  - **Blocked By**: Task 1 (backend scaffolding), Task 3 (models)

  **References**:
  - ACMG guidelines: `https://acmg.net/standards/founds-of-variation` - ACMG criteria definitions
  - Python design patterns: `https://refactoring.guru/design-patterns` - Strategy pattern for criteria

  **WHY Each Reference Matters**:
  - ACMG guidelines: Provides exact criteria definitions and evidence levels
  - Design patterns: Strategy pattern is ideal for implementing switchable criteria

  **Acceptance Criteria**:
  - Rule engine architecture supports all 17 ACMG criteria
  - Evidence scoring mechanism defined
  - Configuration file structure designed
  - Class structure supports easy addition of new criteria

  **QA Scenarios**:

  Scenario: Rule engine architecture supports criteria
    Tool: Bash (Python)
    Preconditions: ACMG classifier class defined
    Steps:
      1. Import ACMGClassifier class
      2. Instantiate the classifier
      3. Check that all 17 criteria are registered
    Expected Result: All criteria are available
    Failure Indicators: Missing criteria classes
    Evidence: .sisyphus/evidence/task-5-criteria-registered.txt

  Scenario: Evidence scoring mechanism works
    Tool: Bash (Python)
    Preconditions: Classifier instantiated
    Steps:
      1. Create mock variant data
      2. Apply classifier with mock criteria
      3. Check that evidence scores are calculated
    Expected Result: Evidence scores are computed
    Failure Indicators: No scores returned
    Evidence: .sisyphus/evidence/task-5-scoring.txt

  **Evidence to Capture**:
  - [ ] .sisyphus/evidence/task-5-criteria-registered.txt
  - [ ] .sisyphus/evidence/task-5-scoring.txt

  **Commit**: YES
  - Message: `feat(backend): add ACMG classifier rule engine structure`
  - Files: `backend/services/acmg_classifier.py`, `backend/services/acmg_criteria.py`

---

- [x] 6. Project Configuration Files

  **What to do**:
  - Backend: requirements.txt (all dependencies)
  - Backend: .env.example (environment variables)
  - Frontend: package.json with all dependencies
  - Frontend: tsconfig.json (TypeScript configuration)
  - Frontend: vite.config.ts (Vite configuration)
  - Frontend: ESLint and Prettier configs
  - Root: .gitignore
  - Root: README.md (setup instructions)
  - Root: docker-compose.yml (optional, for database)

  **Must NOT do**:
  - Do NOT add secrets or private keys
  - Do NOT configure production environment yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Configuration file creation is straightforward with documented dependencies

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1, task 6 of 7
  - **Blocks**: Tasks 7-12 (development server, variant detection)
  - **Blocked By**: Task 1 (backend), Task 2 (frontend)

  **References**:
  - FastAPI requirements: `https://fastapi.tiangolo.com/#dependencies` - Recommended dependencies
  - React dependencies: `https://ant.design/docs/react/getting-started` - Ant Design dependencies

  **WHY Each Reference Matters**:
  - FastAPI docs: Lists recommended dependencies for FastAPI projects
  - Ant Design docs: Lists dependencies needed for Ant Design + Vite

  **Acceptance Criteria**:
  - requirements.txt includes FastAPI, SQLAlchemy, Celery, pysam, numpy, pandas
  - package.json includes React, TypeScript, Ant Design, AntV, Axios
  - All configuration files have correct settings
  - README.md includes setup and run instructions

  **QA Scenarios**:

  Scenario: All dependencies listed correctly
    Tool: Bash
    Preconditions: requirements.txt and package.json exist
    Steps:
      1. Check requirements.txt contains FastAPI, SQLAlchemy, Celery, pysam
      2. Check package.json contains React, TypeScript, Ant Design, AntV
    Expected Result: All required packages listed
    Failure Indicators: Missing packages
    Evidence: .sisyphus/evidence/task-6-deps.txt

  Scenario: README has setup instructions
    Tool: Bash (cat)
    Preconditions: README.md exists
    Steps:
      1. Check README.md contains setup instructions
      2. Check README.md contains run instructions
      3. Check README.md contains dependencies installation commands
    Expected Result: README is complete
    Failure Indicators: Missing instructions
    Evidence: .sisyphus/evidence/task-6-readme.txt

  **Evidence to Capture**:
  - [ ] .sisyphus/evidence/task-6-deps.txt
  - [ ] .sisyphus/evidence/task-6-readme.txt

  **Commit**: YES
  - Message: `chore: add project configuration files`
  - Files: `requirements.txt`, `package.json`, `.env.example`, `README.md`

---

- [x] 7. Development Server Setup

  **What to do**:
  - Backend: Create `run.py` script to start FastAPI with uvicorn
  - Backend: Add `python-dotenv` for environment variable loading
  - Frontend: Create `vite.config.ts` with proper proxy for API
  - Frontend: Create start scripts (npm run dev)
  - Backend: Add startup logging (server start, port, environment)
  - Backend: Create requirements for dev environment (pytest, black, flake8)
  - Frontend: Add dev dependencies (typescript, vite, eslint)

  **Must NOT do**:
  - Do NOT implement API endpoints yet
  - Do NOT add extra tools beyond standard dev workflow

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple script and configuration setup

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1, task 7 of 7
  - **Blocks**: None (Wave 1 completion)
  - **Blocked By**: Tasks 1-6 (all Wave 1 tasks)

  **References**:
  - FastAPI dev server: `https://fastapi.tiangolo.com/#use-with-uvicorn` - How to run FastAPI with uvicorn
  - Vite proxy: `https://vitejs.dev/config/server-options.html#server-proxy` - Vite proxy configuration

  **WHY Each Reference Matters**:
  - FastAPI docs: Shows how to run FastAPI with uvicorn
  - Vite docs: Shows how to configure proxy for API calls

  **Acceptance Criteria**:
  - Backend runs with `python run.py`
  - Frontend runs with `npm run dev`
  - Backend and frontend communicate via proxy
  - Both servers log startup information

  **QA Scenarios**:

  Scenario: Backend dev server runs
    Tool: Bash
    Preconditions: All dependencies installed
    Steps:
      1. Start backend with `python run.py`
      2. Check if server starts on port 8000
      3. Check log output contains "Application startup complete"
    Expected Result: Backend server starts successfully
    Failure Indicators: Import errors, port conflicts
    Evidence: .sisyphus/evidence/task-7-backend-server.log

  Scenario: Frontend dev server runs with proxy
    Tool: Bash
    Preconditions: All dependencies installed
    Steps:
      1. Start frontend with `npm run dev`
      2. Check if server starts on port 3000
      3. Verify vite.config.ts has proxy configured
    Expected Result: Frontend server starts successfully
    Failure Indicators: Import errors, port conflicts
    Evidence: .sisyphus/evidence/task-7-frontend-server.log

  **Evidence to Capture**:
  - [ ] .sisyphus/evidence/task-7-backend-server.log
  - [ ] .sisyphus/evidence/task-7-frontend-server.log

  **Commit**: YES
  - Message: `feat: add development server setup`
  - Files: `backend/run.py`, `frontend/vite.config.ts`, `backend/requirements-dev.txt`

---

## Final Verification Wave
