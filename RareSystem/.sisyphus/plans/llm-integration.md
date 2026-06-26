# Plan: LLM Integration for Case Q&A

## TL;DR
> 通过API动态配置LLM提供商、API Key、模型等参数
> 支持多提供商：OpenAI、Anthropic、Ollama、国内模型
> 配置存储到数据库，前端设置页面管理

## Context

### Original Request
用户需要在Case Q&A中接入大模型，提供者配置放在整个页面的Settings里做

### User Decision
选择方案B：通过后端API动态配置

### Research Findings
- 当前RAG服务使用mock LLM (`_mock_llm_response`)
- 前端无设置页面，仅Zustand状态管理
- 无LLM配置相关API端点
- 使用Zustand管理状态，需添加settings slice

### Implementation Requirements
1. 数据库存储LLM配置
2. 设置管理服务（CRUD）
3. API端点（GET/POST/PUT /api/settings）
4. RAG服务集成真实LLM
5. 前端设置页面

---

## Work Objectives

### Core Objective
为Case Q&A添加可配置的大模型集成，用户通过前端设置页面管理LLM提供商和参数

### Deliverables
- LLM配置数据库模型
- 设置管理服务
- 设置API端点
- RAG服务集成真实LLM
- 前端设置页面

### Definition of Done
- 后端能读取/更新LLM配置
- RAG服务使用配置的LLM生成回答
- 前端设置页面可配置LLM参数
- API测试通过

---

## Verification Strategy

### Test Decision
- Infrastructure exists: YES
- Automated tests: YES (TDD)
- Framework: pytest

### QA Policy
- 后端测试：使用pytest测试设置API和RAG服务
- 前端测试：使用React Testing Library测试设置页面

---

## Execution Strategy

### Parallel Execution Waves

**Wave 1: Foundation + Database**
- Task 1: Create LLM settings database model
- Task 2: Create settings service for CRUD operations
- Task 3: Add settings route to main.py
- Task 4: Test settings API endpoints

**Wave 2: RAG Integration**
- Task 5: Create LLM client factory
- Task 6: Update RAG service to use real LLM
- Task 7: Mock LLM API calls for testing
- Task 8: Test RAG service with LLM integration

**Wave 3: Frontend Settings**
- Task 9: Add settings slice to Zustand store
- Task 10: Create Settings page component
- Task 11: Add Settings page route
- Task 12: Integrate Settings with AnalysisPage

**Wave 4: Testing + Integration**
- Task 13: Write backend tests
- Task 14: Write frontend tests
- Task 15: E2E test full flow
- Task 16: Final verification

---

## TODOs

### Wave 1 - Foundation + Database

- [ ] 1. Create LLM Settings Database Model
  **What to do**:
  - Create table `llm_settings` in `database/case_models.py`
  - Fields: id, provider (text), api_key (text), model (text), base_url (text), temperature (float), max_tokens (integer), provider_name (text - Chinese display name), is_active (boolean)
  - Set `is_active=1` by default
  - Add relationship to `ChatSession`
  - Import model in `database/__init__.py`

  **Must NOT do**:
  - Don't create separate file - add to `case_models.py`

  **Recommended Agent Profile**:
  - Category: `deep`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: YES (in Wave 1)
  - Parallel Group: Wave 1
  - Blocks: None
  - Blocked By: None

  **References**:
  - `database/case_models.py:59-79` (ChatSession model) - pattern for foreign keys, relationships, indexes
  - `database/base.py` - pattern for Base class import

  **Acceptance Criteria**:
  - [ ] `ChatSession` has `llm_setting` relationship (one-to-one)
  - [ ] Model created: `python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"`

  **QA Scenarios**:
  ```
  Scenario: Create LLM settings table
    Tool: Bash
    Preconditions: Database initialized
    Steps:
      1. Run: python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
      2. Run: python -c "from sqlalchemy import inspect; from database.session import engine; inspector = inspect(engine); tables = inspector.get_table_names(); assert 'llm_settings' in tables"
    Expected Result: llm_settings table created successfully
    Evidence: .sisyphus/evidence/task-1-create-table.{ext}
  ```

- [ ] 2. Create Settings Service
  **What to do**:
  - Create `services/settings_service.py`
  - Import SQLAlchemy, Session from database
  - Create class `SettingsService`
  - Methods:
    - `get_llm_settings(patient_id: int) -> LLMSettings` - Get active settings for patient, default to system settings if not found
    - `create_or_update_llm_settings(patient_id: int, config: dict) -> LLMSettings` - Create or update settings
    - `delete_llm_settings(patient_id: int) -> bool` - Delete settings
  - LLMSettings class using Pydantic BaseModel with validation

  **Must NOT do**:
  - Don't use hardcoded values - use database
  - Don't store API keys in config file

  **Recommended Agent Profile**:
  - Category: `deep`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 1
  - Blocks: Task 3
  - Blocked By: None

  **References**:
  - `services/rag_service.py:65-73` (RAGService __init__) - pattern for service initialization with database
  - `database/case_models.py:19-34` (CaseDocument model) - pattern for SQLAlchemy models with relationships

  **Acceptance Criteria**:
  - [ ] Service imports successfully: `python -c "from services.settings_service import SettingsService; print('OK')"`
  - [ ] SettingsService class exists with all required methods

  **QA Scenarios**:
  ```
  Scenario: Get LLM settings for patient
    Tool: Bash
    Preconditions: Database has llm_settings table
    Steps:
      1. Start backend server
      2. Call: curl http://localhost:8080/api/settings/patient/1
    Expected Result: Returns LLM settings object with all fields
    Evidence: .sisyphus/evidence/task-2-get-settings.{ext}
  ```

- [ ] 3. Add Settings API Routes
  **What to do**:
  - Create `api/settings.py`
  - Import FastAPI, Depends, HTTPException, Session from fastapi and database
  - Create Settings router: `router = APIRouter(prefix="/settings", tags=["settings"])`
  - Endpoint:
    - `GET /settings/patient/{patient_id}` - Get active settings for patient
    - `POST /settings/patient/{patient_id}` - Create/update settings
    - `DELETE /settings/patient/{patient_id}` - Delete settings
  - Add relationship to `ChatSession` in LLMSettings model
  - Import in `main.py` and register router

  **Must NOT do**:
  - Don't use authentication middleware
  - Don't expose API keys in debug output

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: YES (in Wave 1)
  - Parallel Group: Wave 1
  - Blocks: Task 4
  - Blocked By: None

  **References**:
  - `api/chat.py:81-118` (send_chat_message endpoint) - pattern for FastAPI endpoints with dependencies
  - `api/variants.py:1-50` (VCF upload endpoint) - pattern for request/response models with Pydantic

  **Acceptance Criteria**:
  - [ ] Router imported successfully in main.py
  - [ ] All endpoints return correct HTTP status codes (200, 201, 404, 400)
  - [ ] Test with curl: `curl http://localhost:8080/api/settings/patient/1`

  **QA Scenarios**:
  ```
  Scenario: Get settings for non-existent patient
    Tool: Bash
    Preconditions: No settings for patient 999
    Steps:
      1. Call: curl http://localhost:8080/api/settings/patient/999
    Expected Result: 404 Not Found
    Evidence: .sisyphus/evidence/task-3-404-test.{ext}

  Scenario: Create settings
    Tool: Bash
    Preconditions: Database initialized
    Steps:
      1. POST with config: {"provider": "openai", "api_key": "sk-test", "model": "gpt-4"}
      2. GET: http://localhost:8080/api/settings/patient/1
    Expected Result: Settings created and retrieved successfully
    Evidence: .sisyphus/evidence/task-3-create-test.{ext}
  ```

- [ ] 4. Test Settings API
  **What to do**:
  - Start backend server
  - Test all API endpoints with curl
  - Test error cases (404, 400, 500)
  - Verify settings persist to database

  **Must NOT do**:
  - Don't mock responses - test real database
  - Don't use production API keys

  **Recommended Agent Profile**:
  - Category: `deep`
  - Skills: []
  - Run In Background: true

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 1
  - Blocks: Wave 2
  - Blocked By: Task 3

  **References**:
  - No specific references - test real implementation

  **Acceptance Criteria**:
  - [ ] All endpoints return expected responses
  - [ ] Settings saved to database
  - [ ] Error handling works correctly

  **QA Scenarios**:
  - POST /settings/patient/1 (valid config) → 200 OK
  - GET /settings/patient/1 → Settings object
  - DELETE /settings/patient/1 → Success message
  - GET /settings/patient/999 → 404 Not Found
  - POST invalid config → 400 Bad Request

---

### Wave 2 - RAG Integration

- [ ] 5. Create LLM Client Factory
  **What to do**:
  - Create `services/llm_client.py`
  - Support providers: openai, anthropic, ollama, custom
  - Factory function `create_llm_client(provider: str, config: dict)`
  - Methods for different providers:
    - OpenAI: client = OpenAI(api_key=config['api_key'], base_url=config.get('base_url'))
    - Anthropic: client = Anthropic(api_key=config['api_key'])
    - Ollama: requests.post(config['base_url'] + '/api/generate', ...)
  - Fallback: raise exception with clear error message

  **Must NOT do**:
  - Don't hardcode API keys
  - Don't include API key in logs

  **Recommended Agent Profile**:
  - Category: `deep`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 2
  - Blocks: Task 6
  - Blocked By: Wave 1

  **References**:
  - `services/rag_service.py:221-233` (_generate_answer) - pattern for calling external service
  - Official docs: https://platform.openai.com/docs/libraries/python

  **Acceptance Criteria**:
  - [ ] Factory function accepts valid provider and config
  - [ ] Returns appropriate client instance
  - [ ] Invalid provider raises error

  **QA Scenarios**:
  ```
  Scenario: Create OpenAI client
    Tool: Python REPL
    Preconditions: Config with openai provider
    Steps:
      1. from services.llm_client import create_llm_client
      2. client = create_llm_client('openai', {'api_key': 'test'})
      3. Verify client type
    Expected Result: Returns OpenAI client instance
    Evidence: .sisyphus/evidence/task-5-openai-client.{ext}
  ```

- [ ] 6. Update RAG Service to Use Real LLM
  **What to do**:
  - Update `services/rag_service.py`
  - Add parameter: `llm_client=None` to `__init__`
  - Get LLM settings from SettingsService: `settings_service.get_llm_settings(patient_id)`
  - Initialize LLM client: `self._llm_client = create_llm_client(provider, settings)`
  - Replace `_mock_llm_response` with `_call_llm(query, context, history)`
  - Use LLM API to generate answer instead of mock
  - Return actual LLM response

  **Must NOT do**:
  - Don't break existing functionality
  - Don't remove mock fallback for testing

  **Recommended Agent Profile**:
  - Category: `ultrabrain`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 2
  - Blocks: Task 7
  - Blocked By: Task 5

  **References**:
  - `services/rag_service.py:264-293` (_mock_llm_response) - current mock implementation to replace
  - `services/rag_service.py:64-73` (__init__) - pattern for adding parameters

  **Acceptance Criteria**:
  - [ ] RAG service imports successfully
  - [ ] Uses LLM client to generate answers
  - [ ] Falls back to mock if no LLM configured

  **QA Scenarios**:
  ```
  Scenario: RAG service uses LLM
    Tool: Bash
    Preconditions: LLM settings configured
    Steps:
      1. Set backend env: LLM_PROVIDER=openai, LLM_API_KEY=test
      2. POST /api/chat/1
    Expected Result: Response from LLM, not mock
    Evidence: .sisyphus/evidence/task-6-rag-llm.{ext}
  ```

- [ ] 7. Mock LLM API Calls for Testing
  **What to do**:
  - Create mock LLM responses for unit tests
  - Add testing flag in SettingsService
  - Configure mock LLM responses for common queries
  - Ensure tests pass without real API calls

  **Must NOT do**:
  - Don't commit mock configurations to database
  - Don't use real API calls in CI/CD

  **Recommended Agent Profile**:
  - Category: `deep`
  - Skills: []
  - Run In Background: true

  **Parallelization**:
  - Can Run In Parallel: YES (in Wave 2)
  - Parallel Group: Wave 2
  - Blocks: Task 8
  - Blocked By: Task 6

  **References**:
  - `services/rag_service.py:264-293` (_mock_llm_response) - patterns for mock responses

  **Acceptance Criteria**:
  - [ ] Unit tests pass without real LLM
  - [ ] Tests cover all provider types
  - [ ] Tests use fixtures for configuration

  **QA Scenarios**:
  ```
  Scenario: Test RAG with mocked LLM
    Tool: pytest
    Preconditions: Mock LLM configured
    Steps:
      1. pytest tests/test_rag_service.py -v
    Expected Result: All tests pass
    Evidence: .sisyphus/evidence/task-7-mock-tests.{ext}
  ```

- [ ] 8. Test RAG Service with LLM Integration
  **What to do**:
  - Write integration tests for RAG service with LLM
  - Test different LLM providers
  - Test error handling (invalid API key, rate limits)
  - Test context formatting and prompt building
  - Run all tests

  **Must NOT do**:
  - Don't make real API calls in test suite
  - Don't expose test API keys

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: []
  - Run In Background: true

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 2
  - Blocks: Wave 3
  - Blocked By: Task 7

  **References**:
  - Tests already exist in `tests/` directory

  **Acceptance Criteria**:
  - [ ] Integration tests pass
  - [ ] Error handling works correctly
  - [ ] All providers tested

---

### Wave 3 - Frontend Settings

- [ ] 9. Add Settings Slice to Zustand Store
  **What to do**:
  - Update `frontend/src/store/index.ts`
  - Add settings slice with Zustand `create()`
  - State: `settings` (object with provider, api_key, model, base_url, temperature, max_tokens)
  - Actions: `updateSettings`, `clearSettings`
  - Persist to localStorage (optional)

  **Must NOT do**:
  - Don't use external state management libraries
  - Don't expose API keys in Redux dev tools

  **Recommended Agent Profile**:
  - Category: `visual-engineering`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 3
  - Blocks: Task 10
  - Blocked By: Wave 2

  **References**:
  - `frontend/src/store/index.ts` - existing Zustand store pattern
  - `frontend/src/components/ChatInterface.tsx` - pattern for form state management

  **Acceptance Criteria**:
  - [ ] Store imports successfully
  - [ ] Settings state updates correctly
  - [ ] API calls work with store

  **QA Scenarios**:
  ```
  Scenario: Update settings in store
    Tool: React Testing Library
    Preconditions: Store initialized
    Steps:
      1. act(() => store.updateSettings({provider: 'openai'}))
      2. Assert store.getState().settings.provider === 'openai'
    Expected Result: Settings updated correctly
    Evidence: .sisyphus/evidence/task-9-store-update.{ext}
  ```

- [ ] 10. Create Settings Page Component
  **What to do**:
  - Create `frontend/src/components/Settings.tsx`
  - Form with fields:
    - LLM Provider (select: OpenAI, Anthropic, Ollama, Custom)
    - API Key (password input)
    - Model Name (text input)
    - Base URL (text input, optional, for custom/OpenAI enterprise)
    - Temperature (slider 0-2)
    - Max Tokens (number input)
  - Provider-specific fields:
    - OpenAI: show model list dropdown (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
    - Anthropic: show model list (claude-3-haiku, claude-3-sonnet, claude-3-opus)
    - Ollama: show model list (llama3, mistral, qwen)
  - Save button calls API
  - Cancel/Reset button

  **Must NOT do**:
  - Don't hardcode provider-specific data
  - Don't store API keys in localStorage (use backend storage)

  **Recommended Agent Profile**:
  - Category: `visual-engineering`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 3
  - Blocks: Task 11
  - Blocked By: Task 9

  **References**:
  - `frontend/src/components/VCFUpload.tsx` - pattern for form inputs
  - `frontend/src/components/ACMGDisplay.tsx` - pattern for Card layout

  **Acceptance Criteria**:
  - [ ] Component renders without errors
  - [ ] Form validation works
  - [ ] Save button updates settings

  **QA Scenarios**:
  ```
  Scenario: Render settings form
    Tool: React Testing Library
    Preconditions: Store has default settings
    Steps:
      1. render(<Settings />)
      2. Assert provider select has options
      3. Assert temperature slider has range
    Expected Result: Form renders with all fields
    Evidence: .sisyphus/evidence/task-10-render.{ext}

  Scenario: Save settings
    Tool: React Testing Library
    Preconditions: Form has valid data
    Steps:
      1. Fill form with: provider='openai', api_key='sk-test', model='gpt-4o-mini'
      2. Click Save
      3. Assert store.updateSettings called
    Expected Result: Settings saved, API called
    Evidence: .sisyphus/evidence/task-10-save.{ext}
  ```

- [ ] 11. Add Settings Page Route
  **What to do**:
  - Update `frontend/src/App.tsx` or create `frontend/src/pages/SettingsPage.tsx`
  - Add route for `/settings`
  - Add "Settings" link/button in navigation
  - Integrate with AnalysisPage (add Settings button to header)

  **Must NOT do**:
  - Don't create separate route file - add to App.tsx
  - Don't break existing routes

  **Recommended Agent Profile**:
  - Category: `visual-engineering`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: YES (in Wave 3)
  - Parallel Group: Wave 3
  - Blocks: Task 12
  - Blocked By: Task 10

  **References**:
  - `frontend/src/App.tsx` - existing routes
  - `frontend/src/pages/AnalysisPage.tsx` - existing page pattern

  **Acceptance Criteria**:
  - [ ] Route accessible at `/settings`
  - [ ] Navigation link works
  - [ ] Settings page accessible from AnalysisPage

  **QA Scenarios**:
  ```
  Scenario: Navigate to settings
    Tool: Playwright
    Preconditions: App running on localhost:8888
    Steps:
      1. Click "Settings" navigation link
      2. Assert URL is /settings
      3. Assert Settings component renders
    Expected Result: Navigate to settings page
    Evidence: .sisyphus/evidence/task-11-navigate.{ext}
  ```

- [ ] 12. Integrate Settings with AnalysisPage
  **What to do**:
  - Update `frontend/src/pages/AnalysisPage.tsx`
  - Add "Settings" button in header or toolbar
  - Open Settings modal or navigate to settings page
  - Ensure settings persist across session

  **Must NOT do**:
  - Don't duplicate navigation logic
  - Don't break existing AnalysisPage functionality

  **Recommended Agent Profile**:
  - Category: `visual-engineering`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 3
  - Blocks: Wave 4
  - Blocked By: Task 11

  **References**:
  - `frontend/src/pages/AnalysisPage.tsx` - existing layout
  - `frontend/src/components/Settings.tsx` - settings component

  **Acceptance Criteria**:
  - [ ] Settings accessible from AnalysisPage
  - [ ] Settings changes reflect in chat
  - [ ] Session persistence works

  **QA Scenarios**:
  ```
  Scenario: Change LLM settings from AnalysisPage
    Tool: Playwright
    Preconditions: AnalysisPage open, patient data loaded
    Steps:
      1. Click Settings button
      2. Change provider to 'anthropic'
      3. Save
      4. Send chat message
    Expected Result: Chat uses new LLM settings
    Evidence: .sisyphus/evidence/task-12-integrate.{ext}
  ```

---

### Wave 4 - Testing + Integration

- [ ] 13. Write Backend Tests
  **What to do**:
  - Create `tests/test_settings.py`
  - Test SettingsService methods
  - Test settings API endpoints
  - Test error handling
  - Run all tests: `pytest tests/test_settings.py -v`

  **Must NOT do**:
  - Don't use real API keys in tests
  - Don't use database in CI/CD

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: []
  - Run In Background: true

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 4
  - Blocks: Task 15
  - Blocked By: Wave 3

  **References**:
  - `tests/` - existing test structure
  - `services/settings_service.py` - implementation

  **Acceptance Criteria**:
  - [ ] All tests pass
  - [ ] Test coverage > 80%
  - [ ] No flaky tests

  **QA Scenarios**:
  ```
  Scenario: Settings API with valid data
    Tool: pytest
    Preconditions: Test database initialized
    Steps:
      1. POST /settings/patient/1 with valid config
      2. GET /settings/patient/1
    Expected Result: 200 OK, settings returned
    Evidence: .sisyphus/evidence/task-13-api-tests.{ext}
  ```

- [ ] 14. Write Frontend Tests
  **What to do**:
  - Create `frontend/src/components/__tests__/Settings.test.tsx`
  - Test settings form rendering
  - Test form validation
  - Test store interactions
  - Run tests: `npm test -- --coverage`

  **Must NOT do**:
  - Don't test API calls directly
  - Don't use real API endpoints

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: []
  - Run In Background: true

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 4
  - Blocks: Task 15
  - Blocked By: Wave 3

  **References**:
  - `frontend/src/components/VCFUpload.test.tsx` - existing test patterns

  **Acceptance Criteria**:
  - [ ] All tests pass
  - [ ] Test coverage > 70%
  - [ ] UI renders correctly

  **QA Scenarios**:
  ```
  Scenario: Settings form validation
    Tool: React Testing Library
    Preconditions: Settings component mounted
    Steps:
      1. Submit form with empty API key
      2. Assert error message shown
    Expected Result: Validation catches missing field
    Evidence: .sisyphus/evidence/task-14-ui-tests.{ext}
  ```

- [ ] 15. E2E Test Full Flow
  **What to do**:
  - Start backend and frontend servers
  - Test complete workflow:
    1. Login/Access AnalysisPage
    2. Navigate to Settings
    3. Configure LLM (provider, API key, model)
    4. Save settings
    5. Send chat message
    6. Verify response from configured LLM
  - Test error scenarios: invalid API key, missing configuration
  - Capture screenshots and logs

  **Must NOT do**:
  - Don't use production API keys
  - Don't test with sensitive data

  **Recommended Agent Profile**:
  - Category: `visual-engineering`
  - Skills: []
  - Run In Background: true

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 4
  - Blocks: Task 16
  - Blocked By: Wave 3

  **References**:
  - Playwright skill available: `/playwright`

  **Acceptance Criteria**:
  - [ ] Full workflow works
  - [ ] Error scenarios handled
  - [ ] Screenshots captured

  **QA Scenarios**:
  ```
  Scenario: End-to-end LLM configuration and chat
    Tool: Playwright
    Preconditions: Backend and frontend running
    Steps:
      1. Navigate to AnalysisPage
      2. Click Settings → Configure OpenAI
      3. Save settings
      4. Send message: "What are the key variants?"
      5. Verify LLM responds
    Expected Result: Message answered with LLM response
    Evidence: .sisyphus/evidence/task-15-e2e.{ext}
  ```

- [ ] 16. Final Verification
  **What to do**:
  - Run all backend and frontend tests
  - Verify test coverage meets targets
  - Check linting and type checking
  - Deploy to staging environment
  - Perform manual QA testing
  - Document changes

  **Must NOT do**:
  - Don't skip verification
  - Don't merge without passing tests

  **Recommended Agent Profile**:
  - Category: `deep`
  - Skills: []
  - Run In Background: true

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 4
  - Blocked By: Wave 3

  **References**:
  - `backend/.env.example` - check for new environment variables

  **Acceptance Criteria**:
  - [ ] All tests pass
  - [ ] Coverage targets met
  - [ ] Documentation updated
  - [ ] Manual QA approved

  **QA Scenarios**:
  - Backend tests: pytest -v --cov
  - Frontend tests: npm test -- --coverage
  - Lint: npm run lint
  - Type check: npm run type-check

---

## Final Verification Wave (MANDATORY)

- [ ] F1. Plan Compliance Audit — `oracle`
  Read the plan end to end. For each TODO item: verify implementation exists. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check that LLM integration is complete and properly configured. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. Code Quality Review — `unspecified-high`
  Run `tsc --noEmit` + linter + `pytest`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. Real Manual QA — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Navigate to Settings page. Configure LLM (OpenAI with test key). Send chat message. Verify LLM response. Test error handling (invalid API key). Test different providers (Anthropic, Ollama). Save screenshots and logs. Test from AnalysisPage integration.
  Output: `Settings [N/N] | Chat Integration [N/N] | Error Handling [N tested] | VERDICT`

- [ ] F4. Scope Fidelity Check — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 - everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Verdict`

---

## Commit Strategy

- Task 1-4: `feat(settings): add LLM settings database and API`
- Task 5-8: `feat(llm): integrate LLM client factory and RAG service`
- Task 9-12: `feat(frontend): add settings page and store integration`
- Task 13-16: `test: add LLM integration tests and final verification`
- Final: `chore: LLM integration complete`

---

## Success Criteria

### Verification Commands
```bash
# Backend tests
pytest tests/test_settings.py -v --cov

# Frontend tests
npm test -- --coverage

# Lint
npm run lint

# Type check
npm run type-check

# Integration test
curl http://localhost:8080/api/settings/patient/1
```

### Final Checklist
- [ ] All "Must Have" present (LLM configuration API, RAG integration, Settings page)
- [ ] All "Must NOT Have" absent (no hardcoded API keys, no mock-only implementation)
- [ ] All tests pass
- [ ] Test coverage > 70%
- [ ] Manual QA approved
- [ ] Documentation updated
