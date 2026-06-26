# Case Q&A Skills System + WebSocket Streaming

## TL;DR

> **Quick Summary**: Add a Skills system (5 genetic-diagnosis-specific skills, configurable in Settings, triggerable via `/` in dialog) and WebSocket streaming output to the Case Q&A dialog.
> 
> **Deliverables**:
> - Backend Skill framework (base class + registry + config storage + API)
> - 5 concrete skill implementations (ACMG, Variant Annotation, Phenotype Matching, Literature Search, Pedigree Analysis)
> - WebSocket streaming chat endpoint replacing batch response
> - Frontend `/` command UI with searchable dropdown
> - Frontend SkillCard component for skill output rendering
> - Frontend Skills tab in Settings page
> - Frontend streaming message renderer
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: Task 1 → Task 8-12 → Task 13 → Task 17 → F1-F4

---

## Context

### Original Request
修改Case Q&A的对话框：1、使其可以安装skills，具体的skills，可以在Settings里面来配置相对应的skills，也可以类似opencode在对话框中通过'/'来使用对应的skills。2、输出需要流式输出，不要等结果都出完了才最终输出。

### Interview Summary
**Key Discussions**:
- Skills system: 类似opencode的skills模式 (confirmed)
- 5 initial genetic-diagnosis skills: ACMG分类解读、变异注释检索、临床表型匹配、文献检索、家系分析
- Mixed skill mode: 提示词注入型 + 工具调用型 (confirmed)
- Skill output: 专属卡片样式 (expandable, icon/title, visually distinct)
- Skills config: 全局配置 (not per-patient)
- Streaming: WebSocket 方案
- Test strategy: tests-after

**Research Findings**:
- Frontend: React 18 + TypeScript + Ant Design 5.22.6 + Zustand 4.5 + Vite 6
- Backend: FastAPI + SQLAlchemy + RAG (FAISS + sentence-transformers) + Multi-provider LLM
- ChatInterface.tsx: Batch rendering (NOT streaming), no slash commands, no skill system
- chat.py: POST /chat/{patient_id} returns complete response synchronously
- llm_client.py: Abstract base with generate() and chat() - NO streaming support
- rag_service.py: ask() → build context → retrieve docs → generate → return complete
- Settings.tsx: Only LLM config per patient (provider/key/model/temperature/max_tokens)
- No existing skill/plugin/slash-command system anywhere in codebase

### Metis Review
**Identified Gaps** (addressed):
- Skill output vs regular message distinction → resolved: dedicated SkillCard component
- Skills scope → resolved: global (not per-patient)
- Streaming cancellation → default: WebSocket close + frontend cancel button
- Multi-skill per message → default: one skill per message for simplicity
- Skill persistence → will use SQLite + JSON config for skill settings

---

## Work Objectives

### Core Objective
Transform the Case Q&A dialog from a simple batch-response chat into an extensible, skill-augmented, streaming conversation system.

### Concrete Deliverables
- `backend/services/skill_base.py` - Skill abstract base class + SkillRegistry
- `backend/database/case_models.py` extension - SkillConfig table
- `backend/services/skills/` - 5 skill implementation files
- `backend/api/skills.py` - Skills CRUD + config API endpoints
- `backend/api/chat.py` extension - WebSocket endpoint for streaming
- `backend/services/llm_client.py` extension - `chat_stream()` method on all providers
- `backend/services/rag_service.py` extension - `ask_stream()` + skill integration
- `frontend/src/types.ts` extension - Skill, SkillConfig, StreamingChatMessage types
- `frontend/src/services/websocket.ts` - WebSocket client service
- `frontend/src/components/SkillCard.tsx` - Skill output card component
- `frontend/src/components/SkillDropdown.tsx` - `/` command searchable dropdown
- `frontend/src/components/StreamingMessage.tsx` - Streaming message renderer
- `frontend/src/components/Settings.tsx` extension - Skills tab
- `frontend/src/components/ChatInterface.tsx` rewrite - Wire everything together

### Definition of Done
- [ ] `/` in chat input shows searchable skill dropdown, selecting a skill prepends it
- [ ] Skill-activated messages render in SkillCard with icon, title, expandable content
- [ ] Messages render incrementally as LLM generates tokens (no waiting for completion)
- [ ] Settings page has Skills tab to enable/disable/configure each skill
- [ ] All 5 skills produce correct output for their domain
- [ ] Existing batch chat endpoint still works (backward compatible)

### Must Have
- Skill base class with `skill_type` field (prompt_injection | tool_call)
- SkillRegistry with `register()`, `get()`, `list()` methods
- Global SkillConfig persistence (SQLite)
- WebSocket streaming with chunk-by-chunk message delivery
- `/` command dropdown with search/filter
- SkillCard with distinct visual styling (Ant Design Card + Collapse)
- Streaming message content updates (character-by-character or chunk-by-chunk)
- Cancel/stop button during streaming
- Backward compatible (existing REST chat endpoint still works)

### Must NOT Have (Guardrails)
- No skill marketplace/store (out of scope)
- No multi-skill chaining per message (one skill per message)
- No per-patient skill configuration (global only)
- No SSE alternative (WebSocket chosen)
- No custom skill authoring UI (skills are code-only, not user-authored)
- No AI slop: excessive comments, over-abstraction, generic names
- No storing patient data in skill configs
- No console.log in production code

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: YES (pytest for backend, vitest for frontend)
- **Automated tests**: Tests-after
- **Framework**: pytest (backend), vitest (frontend)
- **If tests-after**: Implementation first, then test files to verify correctness

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright (playwright skill) - Navigate, interact, assert DOM, screenshot
- **TUI/CLI**: Use interactive_bash (tmux) - Run command, send keystrokes, validate output
- **API/Backend**: Use Bash (curl) - Send requests, assert status + response fields
- **Library/Module**: Use Bash (python REPL) - Import, call functions, compare output

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - foundation + scaffolding):
├── Task 1: Skill base class + SkillRegistry + DB model + migration [quick]
├── Task 2: LLMClient streaming - chat_stream() on all providers [unspecified-high]
├── Task 3: WebSocket connection manager + endpoint skeleton [unspecified-high]
├── Task 4: Frontend type definitions [quick]
├── Task 5: WebSocket client service [quick]
├── Task 6: SkillCard component [visual-engineering]
└── Task 7: Skills API endpoints (list, configure) [quick]

Wave 2 (After Wave 1 - skill implementations):
├── Task 8: ACMG Classification Skill (prompt-injection) [deep]
├── Task 9: Variant Annotation Skill (tool-call) [unspecified-high]
├── Task 10: Phenotype Matching Skill (prompt-injection) [deep]
├── Task 11: Literature Search Skill (tool-call) [unspecified-high]
└── Task 12: Pedigree Analysis Skill (prompt-injection) [deep]

Wave 3 (After Wave 2 - integration + UI):
├── Task 13: RAG service + WebSocket streaming + skill integration [deep]
├── Task 14: / command parser + searchable dropdown [visual-engineering]
├── Task 15: Streaming message renderer [visual-engineering]
└── Task 16: Settings Skills tab [visual-engineering]

Wave 4 (After Wave 3 - full integration):
└── Task 17: ChatInterface full integration [deep]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 8-12 → Task 13 → Task 17 → F1-F4 → user okay
Parallel Speedup: ~65% faster than sequential
Max Concurrent: 7 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | - | 7,8,9,10,11,12,13 | 1 |
| 2 | - | 3,13 | 1 |
| 3 | 2 | 13 | 1 |
| 4 | - | 5,6,14,15,16,17 | 1 |
| 5 | 4 | 14,15,17 | 1 |
| 6 | 4 | 17 | 1 |
| 7 | 1 | 14,16 | 1 |
| 8 | 1 | 13 | 2 |
| 9 | 1 | 13 | 2 |
| 10 | 1 | 13 | 2 |
| 11 | 1 | 13 | 2 |
| 12 | 1 | 13 | 2 |
| 13 | 1,2,3,8-12 | 17 | 3 |
| 14 | 4,5,7 | 17 | 3 |
| 15 | 4,5 | 17 | 3 |
| 16 | 4,7 | 17 | 3 |
| 17 | 6,13,14,15,16 | F1-F4 | 4 |

### Agent Dispatch Summary

- **Wave 1 (7 tasks)**: T1 → `quick`, T2 → `unspecified-high`, T3 → `unspecified-high`, T4 → `quick`, T5 → `quick`, T6 → `visual-engineering`, T7 → `quick`
- **Wave 2 (5 tasks)**: T8 → `deep`, T9 → `unspecified-high`, T10 → `deep`, T11 → `unspecified-high`, T12 → `deep`
- **Wave 3 (4 tasks)**: T13 → `deep`, T14 → `visual-engineering`, T15 → `visual-engineering`, T16 → `visual-engineering`
- **Wave 4 (1 task)**: T17 → `deep`
- **FINAL (4 tasks)**: F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Skill Base Class + SkillRegistry + DB Model + Migration

  **What to do**:
  - Create `backend/services/skill_base.py` with abstract `Skill` class:
    - Fields: `name` (str), `description` (str), `skill_type` (Literal["prompt_injection", "tool_call"]), `icon` (str), `input_schema` (dict)
    - Abstract method: `execute(context: SkillContext) -> SkillResult`
    - `SkillContext` dataclass: `query`, `patient_id`, `db_session`, `llm_client`, `case_context`
    - `SkillResult` dataclass: `content`, `references`, `confidence`, `metadata`
  - Create `SkillRegistry` class with:
    - `_skills: Dict[str, Skill]` internal registry
    - `register(skill: Skill)` - register a skill instance
    - `get(name: str) -> Skill` - lookup by name
    - `list() -> List[Skill]` - return all registered skills
    - `list_by_type(skill_type: str) -> List[Skill]` - filter by type
    - Auto-discovery: scan `backend/services/skills/` directory and import all modules
  - Add `SkillConfig` table to `backend/database/case_models.py`:
    - `id`, `skill_name` (str, unique), `is_enabled` (bool, default True), `config` (JSON), `created_at`, `updated_at`
  - Create Alembic migration for `SkillConfig` table
  - Create `backend/services/skills/__init__.py` with auto-registration of all skills

  **Must NOT do**:
  - Do not implement any specific skill logic (that's Wave 2)
  - Do not add per-patient skill configs
  - Do not create a skill marketplace/store

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single-file abstractions + DB model, well-defined patterns
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - `git-master`: Not needed, no git operations

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2,3,4,5,6,7)
  - **Blocks**: Tasks 7, 8, 9, 10, 11, 12, 13
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL):

  **Pattern References** (existing code to follow):
  - `backend/services/llm_client.py:30-50` - Abstract base class pattern (LLMClient ABC with abstractmethods). Follow this exact pattern for Skill ABC.
  - `backend/services/llm_client.py:290-308` - Factory function pattern (`create_llm_client`). Create analogous `create_skill_registry()`.
  - `backend/database/case_models.py` - Existing SQLAlchemy model definitions. Follow the same column types, naming conventions, and import style for SkillConfig table.
  - `backend/services/rag_service.py:577-588` - Factory function pattern (`create_rag_service`). Follow same style.

  **API/Type References** (contracts to implement against):
  - `backend/services/rag_service.py:31-54` - ChatReference, QAResponse, CaseContext dataclasses. Model SkillContext/SkillResult after these.

  **External References** (libraries and frameworks):
  - Python ABC: https://docs.python.org/3/library/abc.html
  - SQLAlchemy JSON column: https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.JSON

  **WHY Each Reference Matters**:
  - `llm_client.py:30-50` - Must use identical ABC pattern so codebase is consistent
  - `case_models.py` - Must follow existing DB model style for migration compatibility
  - `rag_service.py:31-54` - SkillContext/SkillResult should mirror ChatReference/QAResponse structure for seamless integration

  **Acceptance Criteria**:

  - [ ] `backend/services/skill_base.py` exists with Skill ABC, SkillContext, SkillResult, SkillRegistry
  - [ ] `backend/database/case_models.py` has SkillConfig table
  - [ ] Alembic migration file created and `alembic upgrade head` succeeds
  - [ ] `python -c "from services.skill_base import SkillRegistry; r = SkillRegistry(); print(len(r.list()))"` returns `0` (empty registry before skills registered)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: SkillRegistry register and list works
    Tool: Bash
    Preconditions: Backend virtual environment activated
    Steps:
      1. Run: cd backend && python -c "
         from services.skill_base import SkillRegistry, Skill, SkillContext, SkillResult
         from dataclasses import dataclass
         @dataclass
         class TestSkill(Skill):
             name: str = 'test'
             description: str = 'test skill'
             skill_type: str = 'prompt_injection'
             icon: str = 'test'
             input_schema: dict = {}
             def execute(self, context): return SkillResult(content='ok', references=[], confidence=1.0, metadata={})
         reg = SkillRegistry()
         reg.register(TestSkill())
         skills = reg.list()
         assert len(skills) == 1
         assert skills[0].name == 'test'
         assert reg.get('test').name == 'test'
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: SkillRegistry correctly registers and retrieves skills
    Failure Indicators: ImportError, AssertionError, or any exception
    Evidence: .sisyphus/evidence/task-1-registry-test.txt

  Scenario: SkillConfig table is queryable
    Tool: Bash
    Preconditions: Database migration run
    Steps:
      1. Run: cd backend && python -c "
         from database import get_db
         from database.case_models import SkillConfig
         db = next(get_db())
         count = db.query(SkillConfig).count()
         print(f'SkillConfig rows: {count}')
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: SkillConfig table accessible and queryable
    Failure Indicators: Table not found error
    Evidence: .sisyphus/evidence/task-1-db-model-test.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(skills): add skill framework base class, registry, and DB model`
  - Files: `backend/services/skill_base.py`, `backend/database/case_models.py`, `backend/services/skills/__init__.py`, migration file
  - Pre-commit: `cd backend && python -c "from services.skill_base import SkillRegistry; print('OK')"`

- [x] 2. LLMClient Streaming Support

  **What to do**:
  - Add abstract `chat_stream()` method to `LLMClient` base class in `backend/services/llm_client.py`:
    - Signature: `chat_stream(self, messages, temperature, max_tokens, **kwargs) -> Iterator[str]`
    - Yields content chunks as strings
  - Implement `chat_stream()` for all 4 providers:
    - **OpenAI**: Use `stream=True` in payload, parse `data: {"choices":[{"delta":{"content":"..."}}]}` SSE lines
    - **Anthropic**: Use `stream=True`, parse `event: content_block_delta` SSE events
    - **Ollama**: Use `stream=True` in payload, parse `{"message":{"content":"..."}}` JSON lines
    - **Custom**: Same as OpenAI (OpenAI-compatible APIs)
  - Each implementation should use `requests` with `stream=True` and iterate `response.iter_lines()`
  - Handle connection errors and timeouts in streaming mode
  - Return `Iterator[str]` (generator) yielding content fragments

  **Must NOT do**:
  - Do not modify existing `chat()` or `generate()` methods (backward compatibility)
  - Do not add WebSocket logic here (that's Task 3)
  - Do not add skill-specific logic

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful SSE/streaming parsing for 4 different API formats
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1,3,4,5,6,7)
  - **Blocks**: Tasks 3, 13
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL):

  **Pattern References**:
  - `backend/services/llm_client.py:52-104` - OpenAI `chat()` implementation. `chat_stream()` must follow same URL, headers, payload structure but add `stream=True`.
  - `backend/services/llm_client.py:107-161` - Anthropic `chat()`. Same headers and URL pattern for streaming.
  - `backend/services/llm_client.py:164-232` - Ollama `chat()`. Ollama uses different JSON streaming format.
  - `backend/services/llm_client.py:235-287` - Custom `chat()`. OpenAI-compatible, same as OpenAI streaming.

  **External References**:
  - OpenAI Streaming: https://platform.openai.com/docs/api-reference/chat/create#chat-create-stream
  - Anthropic Streaming: https://docs.anthropic.com/en/api/messages-streaming
  - Ollama Streaming: https://github.com/ollama/ollama/blob/main/docs/api.md

  **WHY Each Reference Matters**:
  - Each provider has a different streaming protocol. Must follow exact SSE/NDJSON parsing for each.

  **Acceptance Criteria**:

  - [ ] `chat_stream()` abstract method exists in LLMClient
  - [ ] All 4 provider classes implement `chat_stream()` returning generator
  - [ ] Existing `chat()` and `generate()` still work (no regressions)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: chat_stream method exists on all LLMClient subclasses
    Tool: Bash
    Preconditions: Backend venv activated
    Steps:
      1. Run: cd backend && python -c "
         from services.llm_client import OpenAIClient, AnthropicClient, OllamaClient, CustomClient
         for cls in [OpenAIClient, AnthropicClient, OllamaClient, CustomClient]:
             assert hasattr(cls, 'chat_stream'), f'{cls.__name__} missing chat_stream'
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: All 4 client classes have chat_stream method
    Failure Indicators: AssertionError or AttributeError
    Evidence: .sisyphus/evidence/task-2-streaming-methods.txt

  Scenario: Existing chat() method still works (backward compat)
    Tool: Bash
    Preconditions: Backend venv activated
    Steps:
      1. Run: cd backend && python -c "
         from services.llm_client import OpenAIClient, AnthropicClient, OllamaClient, CustomClient
         for cls in [OpenAIClient, AnthropicClient, OllamaClient, CustomClient]:
             assert hasattr(cls, 'chat'), f'{cls.__name__} missing chat'
             assert hasattr(cls, 'generate'), f'{cls.__name__} missing generate'
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: No regressions to existing methods
    Failure Indicators: AssertionError
    Evidence: .sisyphus/evidence/task-2-backward-compat.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(llm): add streaming chat support for all providers`
  - Files: `backend/services/llm_client.py`
  - Pre-commit: `cd backend && python -c "from services.llm_client import OpenAIClient; print('OK')"`

- [x] 3. WebSocket Connection Manager + Chat Endpoint

  **What to do**:
  - Create `backend/api/ws_manager.py` with `ConnectionManager` class:
    - `active_connections: Dict[int, List[WebSocket]]` keyed by patient_id
    - `connect(websocket, patient_id)` - accept and store connection
    - `disconnect(websocket, patient_id)` - remove connection
    - `send_to_client(patient_id, message)` - send JSON to specific patient's connections
  - Add WebSocket endpoint to `backend/api/chat.py`:
    - `@router.websocket("/ws/{patient_id}")`
    - Accept connection, register with ConnectionManager
    - Message format: `{"type": "chat"|"skill"|"cancel", "content": str, "skill_name": str|null, "session_token": str|null}`
    - Response format: `{"type": "chunk"|"skill_result"|"done"|"error", "content": str, ...}`
    - Handle disconnect gracefully
    - Placeholder for RAGService streaming (full integration in Task 13)
  - WebSocket route auto-registered via chat_router in main.py

  **Must NOT do**:
  - Do not implement full skill-aware streaming logic (Task 13)
  - Do not modify RAG service yet
  - Do not add authentication

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: WebSocket lifecycle management requires careful error handling
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1,2,4,5,6,7)
  - **Blocks**: Task 13
  - **Blocked By**: Task 2 (needs chat_stream from LLMClient)

  **References** (CRITICAL):

  **Pattern References**:
  - `backend/api/chat.py:77-129` - Existing REST chat endpoint. Follow same dependency injection.
  - `backend/main.py:72-77` - Router registration pattern.
  - FastAPI WebSocket docs: https://fastapi.tiangolo.com/advanced/websockets/

  **Acceptance Criteria**:

  - [ ] `backend/api/ws_manager.py` exists with ConnectionManager class
  - [ ] WebSocket endpoint `/api/chat/ws/{patient_id}` exists
  - [ ] Connection accepts and disconnects cleanly

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: WebSocket endpoint accepts connections
    Tool: Bash
    Preconditions: Backend server running on port 8080
    Steps:
      1. Run: timeout 5 websocat ws://localhost:8080/api/chat/ws/1 2>&1 || true
      2. Assert: No "connection refused" error
    Expected Result: WebSocket handshake succeeds
    Failure Indicators: "connection refused"
    Evidence: .sisyphus/evidence/task-3-ws-connect.txt

  Scenario: ConnectionManager tracks connections
    Tool: Bash
    Preconditions: Backend venv activated
    Steps:
      1. Run: cd backend && python -c "
         from api.ws_manager import ConnectionManager
         mgr = ConnectionManager()
         assert hasattr(mgr, 'active_connections')
         assert hasattr(mgr, 'connect')
         assert hasattr(mgr, 'disconnect')
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: ConnectionManager has all required methods
    Failure Indicators: ImportError or AttributeError
    Evidence: .sisyphus/evidence/task-3-manager-test.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(chat): add WebSocket connection manager and streaming endpoint`
  - Files: `backend/api/ws_manager.py`, `backend/api/chat.py`
  - Pre-commit: `cd backend && python -c "from api.ws_manager import ConnectionManager; print('OK')"`

- [x] 4. Frontend Type Definitions

  **What to do**:
  - Add to `frontend/src/types.ts`:
    ```typescript
    export type SkillType = 'prompt_injection' | 'tool_call'

    export interface Skill {
      name: string
      description: string
      skill_type: SkillType
      icon: string
      input_schema: Record<string, unknown>
    }

    export interface SkillConfig {
      id: number
      skill_name: string
      is_enabled: boolean
      config: Record<string, unknown>
      created_at: string
      updated_at: string
    }

    export interface StreamingChatMessage {
      id: string
      role: 'user' | 'assistant'
      content: string
      timestamp: string
      references?: ChatReference[]
      confidence?: number
      skill_name?: string
      skill_type?: SkillType
      is_streaming?: boolean
    }

    export interface WSMessage {
      type: 'chat' | 'skill' | 'cancel'
      content: string
      skill_name?: string
      session_token?: string
    }

    export interface WSResponse {
      type: 'chunk' | 'skill_result' | 'done' | 'error' | 'session_info'
      content?: string
      message_id?: string
      references?: ChatReference[]
      confidence?: number
      skill_name?: string
      skill_type?: SkillType
      session_token?: string
    }
    ```

  **Must NOT do**:
  - Do not modify existing types (ChatMessage, ChatReference, etc.)
  - Do not add UI component types here

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding type definitions, purely additive
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1,2,3,5,6,7)
  - **Blocks**: Tasks 5, 6, 14, 15, 16, 17
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `frontend/src/types.ts:139-153` - Existing ChatMessage and ChatReference. StreamingChatMessage must be compatible with these fields.

  **Acceptance Criteria**:

  - [ ] Types compile: `cd frontend && npx tsc --noEmit`
  - [ ] All new types are exported

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: New types compile and are importable
    Tool: Bash
    Preconditions: Frontend deps installed
    Steps:
      1. Run: cd frontend && npx tsc --noEmit 2>&1 | tail -5
      2. Assert: Exit code 0
    Expected Result: No TypeScript compilation errors
    Failure Indicators: Type errors
    Evidence: .sisyphus/evidence/task-4-types-compile.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(types): add skill and streaming WebSocket type definitions`
  - Files: `frontend/src/types.ts`
  - Pre-commit: `cd frontend && npx tsc --noEmit`

- [x] 5. WebSocket Client Service

  **What to do**:
  - Create `frontend/src/services/websocket.ts`:
    - `ChatWebSocket` class:
      - Constructor: `new ChatWebSocket(patientId: number)`
      - `connect()`: Establish WebSocket to `ws://host/api/chat/ws/{patientId}`
      - `send(message: WSMessage)`: Send JSON message
      - `onMessage(callback: (data: WSResponse) => void)`: Register message handler
      - `onError(callback: (error: Event) => void)`: Register error handler
      - `onClose(callback: (event: CloseEvent) => void)`: Register close handler
      - `close()`: Close connection
      - `isConnected`: boolean getter
      - Auto-reconnect with exponential backoff (1s, 2s, 4s, max 30s)
      - Message buffer for offline queuing

  **Must NOT do**:
  - Do not add UI components or skill logic
  - Do not use socket.io

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1,2,3,4,6,7)
  - **Blocks**: Tasks 14, 15, 17
  - **Blocked By**: Task 4 (needs type definitions)

  **References**:

  **Pattern References**:
  - `frontend/src/services/api.ts:119-195` - APIService class pattern. Follow same style.

  **Acceptance Criteria**:

  - [ ] File exists with ChatWebSocket class
  - [ ] Type checking passes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: ChatWebSocket class has correct interface
    Tool: Bash
    Preconditions: Frontend deps installed
    Steps:
      1. Run: cd frontend && npx tsc --noEmit 2>&1 | tail -3
      2. Assert: Exit code 0
    Expected Result: No type errors
    Failure Indicators: Type errors
    Evidence: .sisyphus/evidence/task-5-ws-service.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(ws): add WebSocket client service with auto-reconnect`
  - Files: `frontend/src/services/websocket.ts`
  - Pre-commit: `cd frontend && npx tsc --noEmit`

- [x] 6. SkillCard Component

  **What to do**:
  - Create `frontend/src/components/SkillCard.tsx`:
    - Ant Design Card with colored left border (blue=prompt_injection, green=tool_call)
    - Icon, title, skill_type Tag, collapsible content via Collapse
    - References as Tags (same as ChatInterface.renderReference)
    - Confidence badge (same as ChatInterface)
    - Props: `{ skill: Skill; content: string; references?: ChatReference[]; confidence?: number }`

  **Must NOT do**:
  - Do not implement `/` dropdown or streaming rendering

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI component with specific visual design using Ant Design
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1,2,3,4,5,7)
  - **Blocks**: Task 17
  - **Blocked By**: Task 4 (needs Skill type)

  **References**:

  **Pattern References**:
  - `frontend/src/components/ChatInterface.tsx:103-131` - renderReference() - use identical Tag styling
  - `frontend/src/components/ChatInterface.tsx:180-193` - confidence badge - use identical styling

  **External References**:
  - Ant Design Card: https://ant.design/components/card
  - Ant Design Collapse: https://ant.design/components/collapse

  **Acceptance Criteria**:

  - [ ] File exists and renders without errors
  - [ ] Type checking passes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: SkillCard component compiles
    Tool: Bash
    Preconditions: Frontend deps installed
    Steps:
      1. Run: cd frontend && npx tsc --noEmit 2>&1 | tail -3
      2. Assert: Exit code 0
    Expected Result: No type errors
    Failure Indicators: Type errors
    Evidence: .sisyphus/evidence/task-6-skillcard-types.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(ui): add SkillCard component for skill output rendering`
  - Files: `frontend/src/components/SkillCard.tsx`
  - Pre-commit: `cd frontend && npx tsc --noEmit`

- [x] 7. Skills API Endpoints

  **What to do**:
  - Create `backend/api/skills.py` with router (prefix="/skills"):
    - `GET /api/skills` - List all skills with their configs
    - `GET /api/skills/config` - Get all skill configs
    - `PUT /api/skills/config/{skill_name}` - Update skill config (is_enabled, config JSON)
    - `POST /api/skills/{skill_name}/execute` - Execute a tool-call skill
  - Register in `backend/main.py`
  - Add frontend API methods: `getSkills()`, `getSkillConfigs()`, `updateSkillConfig()`, `executeSkill()`

  **Must NOT do**:
  - Do not implement skill execution logic (Wave 2)
  - Do not add WebSocket routes

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1,2,3,4,5,6)
  - **Blocks**: Tasks 14, 16
  - **Blocked By**: Task 1 (needs SkillRegistry + SkillConfig)

  **References**:

  **Pattern References**:
  - `backend/api/settings.py` - CRUD pattern to follow
  - `frontend/src/services/api.ts:466-493` - Settings API method pattern

  **Acceptance Criteria**:

  - [ ] Endpoints exist and return valid JSON
  - [ ] Frontend API methods added
  - [ ] `curl http://localhost:8080/api/skills` works

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Skills API returns valid JSON
    Tool: Bash
    Preconditions: Backend server running
    Steps:
      1. Run: curl -s http://localhost:8080/api/skills | python3 -m json.tool
      2. Assert: Valid JSON returned
    Expected Result: Valid JSON array
    Failure Indicators: 404 or invalid JSON
    Evidence: .sisyphus/evidence/task-7-skills-api.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(skills): add skills API endpoints and frontend API methods`
  - Files: `backend/api/skills.py`, `backend/main.py`, `frontend/src/services/api.ts`
  - Pre-commit: `cd backend && python -c "from api.skills import router; print('OK')"`

- [x] 8. ACMG Classification Skill (prompt_injection)

  **What to do**:
  - Create `backend/services/skills/acmg_skill.py`:
    - Extend `Skill` base class from `skill_base.py`
    - `name = "acmg_classification"`, `description = "ACMG/AMP变异分类解读"`, `skill_type = "prompt_injection"`, `icon = "experiment"`
    - `input_schema`: `{"variant_description": "str - variant to classify (e.g. chr1:12345 A>G)"}`
    - `execute(context)`:
      - Build enhanced prompt with ACMG-specific instructions: apply PVS1-PS4, PM1-PM6, PP1-PP5, BP1-BP7 criteria systematically
      - Inject patient variant data from `context.case_context`
      - Call `context.llm_client.chat()` with enhanced ACMG prompt
      - Return SkillResult with classification, evidence chain, and confidence

  **Must NOT do**:
  - Do not implement actual ACMG rule engine (that exists in `acmg_classifier.py` already)
  - Do not modify existing ACMG classification service
  - Do not add WebSocket or streaming logic

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires domain knowledge of ACMG criteria and careful prompt engineering
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 9,10,11,12)
  - **Blocks**: Task 13
  - **Blocked By**: Task 1 (needs Skill base class + registry)

  **References** (CRITICAL):

  **Pattern References**:
  - `backend/services/skill_base.py` - Skill base class (Task 1). Must extend this exactly.
  - `backend/services/acmg_classifier.py` - Existing ACMG classification service. Reference for ACMG criteria structure and terminology. Do NOT import/call this; it's for reference only.
  - `backend/services/rag_service.py:295-322` - `_build_rag_prompt()` pattern. ACMG skill should build its own specialized prompt using similar structure.

  **External References**:
  - ACMG/AMP Guidelines: https://www.acmg.net/docs/Standards_Guidelines_for_the_Interpretation_of_Sequence_Variants.pdf

  **WHY Each Reference Matters**:
  - `acmg_classifier.py` provides the canonical ACMG criteria names and evidence structure to use in prompts
  - `_build_rag_prompt()` shows the established prompt-building pattern in the codebase

  **Acceptance Criteria**:

  - [ ] File exists extending Skill base class with correct fields
  - [ ] Skill registered in `skills/__init__.py`
  - [ ] `python -c "from services.skills import create_skill_registry; r = create_skill_registry(); s = r.get('acmg_classification'); print(s.name)"` prints "acmg_classification"

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: ACMG skill is registered and returns correct metadata
    Tool: Bash
    Preconditions: Task 1 completed
    Steps:
      1. Run: cd backend && python -c "
         from services.skills import create_skill_registry
         reg = create_skill_registry()
         skill = reg.get('acmg_classification')
         assert skill is not None, 'ACMG skill not found'
         assert skill.skill_type == 'prompt_injection'
         assert skill.name == 'acmg_classification'
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: ACMG skill registered with correct type
    Failure Indicators: KeyError or AttributeError
    Evidence: .sisyphus/evidence/task-8-acmg-registration.txt

  Scenario: ACMG skill execute returns valid SkillResult
    Tool: Bash
    Preconditions: Task 1 and 8 completed
    Steps:
      1. Run: cd backend && python -c "
         from services.skills import create_skill_registry
         from services.skill_base import SkillContext
         reg = create_skill_registry()
         skill = reg.get('acmg_classification')
         ctx = SkillContext(query='Classify BRCA1 variant', patient_id=1, db_session=None, llm_client=None, case_context=None)
         # execute should handle missing llm_client gracefully
         try:
             result = skill.execute(ctx)
             assert result.content is not None
         except Exception as e:
             assert 'llm' in str(e).lower() or 'client' in str(e).lower(), f'Unexpected error: {e}'
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: Skill returns result or raises appropriate error when LLM unavailable
    Failure Indicators: Unexpected exception type
    Evidence: .sisyphus/evidence/task-8-acmg-execute.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(skills): implement ACMG classification skill`
  - Files: `backend/services/skills/acmg_skill.py`, `backend/services/skills/__init__.py`
  - Pre-commit: `cd backend && python -c "from services.skills import create_skill_registry; r=create_skill_registry(); print(len(r.list()))"`

- [x] 9. Variant Annotation Skill (tool_call)

  **What to do**:
  - Create `backend/services/skills/variant_skill.py`:
    - Extend `Skill` base class
    - `name = "variant_annotation"`, `description = "变异注释检索"`, `skill_type = "tool_call"`, `icon = "search"`
    - `input_schema`: `{"variant_description": "str", "databases": "list - gnomad, clinvar, dbsnp"}`
    - `execute(context)`:
      - Parse variant description (chr:pos ref>alt format)
      - Query available databases via `context.db_session`:
        - Look up variant in local Variant table
        - Retrieve ACMG classification if available
        - Get population frequency from gnomad_af field
      - Build structured annotation result
      - Return SkillResult with all gathered annotations as structured content

  **Must NOT do**:
  - Do not make external API calls to gnomad/ClinVar (out of scope, local data only)
  - Do not add new database tables

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Database query orchestration with multiple data sources
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 8,10,11,12)
  - **Blocks**: Task 13
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `backend/database/models.py` - Patient, Variant, VCFFile, ACMGClassification, ACMGEvidence models. These are the data sources for annotation.
  - `backend/services/rag_service.py:122-176` - `_build_variant_context()` pattern for querying variant data. Follow similar query patterns.

  **Acceptance Criteria**:

  - [ ] File exists with correct Skill subclass
  - [ ] Registered in skills/__init__.py
  - [ ] Skill queries local DB for variant annotations

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Variant annotation skill registered
    Tool: Bash
    Preconditions: Task 1 completed
    Steps:
      1. Run: cd backend && python -c "
         from services.skills import create_skill_registry
         reg = create_skill_registry()
         skill = reg.get('variant_annotation')
         assert skill is not None
         assert skill.skill_type == 'tool_call'
         print('PASS')
         "
    Expected Result: Skill registered as tool_call type
    Evidence: .sisyphus/evidence/task-9-variant-registration.txt

  Scenario: Variant skill handles missing variant gracefully
    Tool: Bash
    Preconditions: Backend venv activated, DB available
    Steps:
      1. Run: cd backend && python -c "
         from services.skills import create_skill_registry
         from services.skill_base import SkillContext
         from database import get_db
         reg = create_skill_registry()
         skill = reg.get('variant_annotation')
         db = next(get_db())
         ctx = SkillContext(query='chrZ:999999 A>T', patient_id=9999, db_session=db, llm_client=None, case_context=None)
         result = skill.execute(ctx)
         assert result.content is not None
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: Returns result even for non-existent variant (empty annotation)
    Failure Indicators: Unhandled exception
    Evidence: .sisyphus/evidence/task-9-variant-missing.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(skills): implement variant annotation skill`
  - Files: `backend/services/skills/variant_skill.py`, `backend/services/skills/__init__.py`

- [x] 10. Phenotype Matching Skill (prompt_injection)

  **What to do**:
  - Create `backend/services/skills/phenotype_skill.py`:
    - `name = "phenotype_matching"`, `description = "临床表型与基因关联匹配"`, `skill_type = "prompt_injection"`, `icon = "medicine-box"`
    - `execute(context)`:
      - Extract phenotype terms from query
      - Build specialized prompt for phenotype-gene association analysis
      - Include patient phenotype data from context.case_context
      - Call LLM with phenotype-matching instructions
      - Return result with gene-disease associations and evidence

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 13
  - **Blocked By**: Task 1

  **References**:
  - `backend/services/rag_service.py:103-120` - `_build_patient_context()` for extracting patient phenotype data
  - `backend/services/skill_base.py` - Base class (Task 1)

  **Acceptance Criteria**:
  - [ ] File exists extending Skill base class
  - [ ] Registered in skills/__init__.py
  - [ ] Skill produces phenotype-gene association results

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Phenotype skill registered correctly
    Tool: Bash
    Preconditions: Task 1 completed
    Steps:
      1. Run: cd backend && python -c "
         from services.skills import create_skill_registry
         reg = create_skill_registry()
         skill = reg.get('phenotype_matching')
         assert skill is not None
         assert skill.skill_type == 'prompt_injection'
         print('PASS')
         "
    Expected Result: Skill registered
    Evidence: .sisyphus/evidence/task-10-phenotype-registration.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(skills): implement phenotype matching skill`
  - Files: `backend/services/skills/phenotype_skill.py`, `backend/services/skills/__init__.py`

- [x] 11. Literature Search Skill (tool_call)

  **What to do**:
  - Create `backend/services/skills/literature_skill.py`:
    - `name = "literature_search"`, `description = "遗传学文献检索"`, `skill_type = "tool_call"`, `icon = "book"`
    - `execute(context)`:
      - Search local case documents and indexed RAG knowledge base
      - Use `context.db_session` to query CaseDocument for relevant literature notes
      - Use embedding_service to find semantically similar documents
      - Build structured literature summary
      - Return SkillResult with references and confidence

  **Must NOT do**:
  - Do not call PubMed/external APIs (out of scope)
  - Do not add new embedding logic (use existing EmbeddingService)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 13
  - **Blocked By**: Task 1

  **References**:
  - `backend/services/rag_service.py:198-227` - `_retrieve_relevant_documents()` pattern for searching indexed documents
  - `backend/services/embedding_service.py` - EmbeddingService for semantic search

  **Acceptance Criteria**:
  - [ ] File exists extending Skill base class
  - [ ] Registered in skills/__init__.py

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Literature skill registered
    Tool: Bash
    Preconditions: Task 1 completed
    Steps:
      1. Run: cd backend && python -c "
         from services.skills import create_skill_registry
         reg = create_skill_registry()
         skill = reg.get('literature_search')
         assert skill is not None
         assert skill.skill_type == 'tool_call'
         print('PASS')
         "
    Expected Result: Skill registered as tool_call
    Evidence: .sisyphus/evidence/task-11-literature-registration.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(skills): implement literature search skill`
  - Files: `backend/services/skills/literature_skill.py`, `backend/services/skills/__init__.py`

- [x] 12. Pedigree Analysis Skill (prompt_injection)

  **What to do**:
  - Create `backend/services/skills/pedigree_skill.py`:
    - `name = "pedigree_analysis"`, `description = "家系分析与遗传模式推断"`, `skill_type = "prompt_injection"`, `icon = "apartment"`
    - `execute(context)`:
      - Build specialized prompt for pedigree/inheritance pattern analysis
      - Include family history and variant data from context
      - Instruct LLM to identify inheritance patterns (AD, AR, XL, mitochondrial)
      - Call LLM with pedigree-specific instructions
      - Return result with inheritance pattern analysis and confidence

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 13
  - **Blocked By**: Task 1

  **References**:
  - `backend/services/rag_service.py:103-120` - Patient context for family history data
  - `backend/services/skill_base.py` - Base class (Task 1)

  **Acceptance Criteria**:
  - [ ] File exists extending Skill base class
  - [ ] Registered in skills/__init__.py
  - [ ] All 5 skills registered: `python -c "from services.skills import create_skill_registry; r=create_skill_registry(); print(len(r.list()))"` returns `5`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All 5 skills registered in registry
    Tool: Bash
    Preconditions: All Wave 2 tasks completed
    Steps:
      1. Run: cd backend && python -c "
         from services.skills import create_skill_registry
         reg = create_skill_registry()
         skills = reg.list()
         assert len(skills) == 5, f'Expected 5 skills, got {len(skills)}'
         names = sorted([s.name for s in skills])
         expected = sorted(['acmg_classification', 'variant_annotation', 'phenotype_matching', 'literature_search', 'pedigree_analysis'])
         assert names == expected, f'Got {names}, expected {expected}'
         print('PASS')
         "
      2. Assert: stdout contains "PASS"
    Expected Result: All 5 skills registered with correct names
    Failure Indicators: Wrong count or wrong names
    Evidence: .sisyphus/evidence/task-12-all-skills-registered.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `feat(skills): implement pedigree analysis skill`
  - Files: `backend/services/skills/pedigree_skill.py`, `backend/services/skills/__init__.py`

- [x] 13. RAG Service + WebSocket Streaming + Skill Integration

  **What to do**:
  - Extend `backend/services/rag_service.py`:
    - Add `ask_stream()` method:
      - Same context building as `ask()`
      - Use `llm_client.chat_stream()` instead of `chat()`
      - Yield content chunks as they arrive
      - After streaming completes, yield final metadata (references, confidence)
    - Add skill-aware routing:
      - Check if `skill_name` is provided in the request
      - For `prompt_injection` skills: inject skill prompt into RAG prompt before LLM call
      - For `tool_call` skills: call `skill.execute()`, then stream the result
      - For no skill: default RAG behavior (same as current `ask()`)
  - Update `backend/api/chat.py` WebSocket endpoint (from Task 3):
    - Wire up `rag_service.ask_stream()` to WebSocket
    - For each chunk, send `{"type": "chunk", "content": "..."}`
    - When skill is used, send `{"type": "skill_result", "skill_name": "...", "content": "..."}`
    - On completion, send `{"type": "done", "message_id": "...", "references": [...], "confidence": 0.85}`
    - On error, send `{"type": "error", "content": "..."}`
    - Handle cancel messages: stop streaming and send `{"type": "done"}`
  - Store streamed messages in ChatMessageRecord after completion (same as current behavior)

  **Must NOT do**:
  - Do not remove the existing REST `POST /chat/{patient_id}` endpoint
  - Do not change the database schema for ChatMessageRecord
  - Do not add authentication

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Complex integration of 3 systems (streaming, skills, RAG), requires careful orchestration
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential within this task)
  - **Blocks**: Task 17
  - **Blocked By**: Tasks 1, 2, 3, 8-12

  **References** (CRITICAL):

  **Pattern References**:
  - `backend/services/rag_service.py:454-492` - `ask()` method. `ask_stream()` must mirror this flow but yield chunks instead of returning complete.
  - `backend/services/rag_service.py:257-293` - `_generate_answer()`. The streaming version must use `chat_stream()` instead of `chat()`.
  - `backend/services/rag_service.py:295-322` - `_build_rag_prompt()`. Skill prompts must be injected here for prompt_injection skills.
  - `backend/api/chat.py:81-129` - Existing REST endpoint. WebSocket must produce equivalent output structure.

  **API/Type References**:
  - `backend/services/skill_base.py` - SkillContext, SkillResult, Skill base class (Task 1).
  - `backend/api/ws_manager.py` - ConnectionManager (Task 3).

  **WHY Each Reference Matters**:
  - `ask()` is the canonical implementation; `ask_stream()` must be functionally equivalent but streaming
  - Skill integration modifies the prompt generation, which is the core of RAG

  **Acceptance Criteria**:

  - [ ] `rag_service.ask_stream()` exists and yields chunks
  - [ ] WebSocket endpoint streams responses in real-time
  - [ ] Skill routing works: prompt_injection → enhanced prompt, tool_call → execute()
  - [ ] Existing REST endpoint still works unchanged
  - [ ] Cancel message stops streaming

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: WebSocket streaming delivers chunks
    Tool: Bash
    Preconditions: Backend server running with at least one patient in DB
    Steps:
      1. Run: timeout 15 websocat ws://localhost:8080/api/chat/ws/1 <<< '{"type":"chat","content":"hello","session_token":null}' 2>&1 || true
      2. Assert: Output contains at least one "chunk" type message or "error" type (graceful)
    Expected Result: WebSocket receives streaming chunks
    Failure Indicators: No response or only "connection refused"
    Evidence: .sisyphus/evidence/task-13-ws-streaming.txt

  Scenario: Cancel message stops streaming
    Tool: Bash
    Preconditions: Backend server running
    Steps:
      1. Run: (echo '{"type":"chat","content":"hello"}'; sleep 1; echo '{"type":"cancel"}') | timeout 10 websocat ws://localhost:8080/api/chat/ws/1 2>&1 || true
      2. Assert: Output contains "done" type message
    Expected Result: Streaming stops after cancel, "done" message sent
    Failure Indicators: Streaming continues indefinitely
    Evidence: .sisyphus/evidence/task-13-ws-cancel.txt
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(chat): integrate skills, streaming, and WebSocket into RAG chat flow`
  - Files: `backend/services/rag_service.py`, `backend/api/chat.py`
  - Pre-commit: `cd backend && python -c "from services.rag_service import RAGService; print('OK')"`

- [x] 14. `/` Command Parser + Searchable Dropdown

  **What to do**:
  - Create `frontend/src/components/SkillDropdown.tsx`:
    - Props: `{ skills: Skill[]; visible: boolean; onSelect: (skill: Skill) => void; onClose: () => void; position: { top: number; left: number } }`
    - Render a dropdown (Ant Design `Select` or custom dropdown) showing all enabled skills
    - Search/filter by skill name or description
    - Each item shows: icon, name, description, type badge
    - Keyboard navigation (up/down arrows, Enter to select, Escape to close)
    - Click outside to close
  - Modify `frontend/src/components/ChatInterface.tsx`:
    - Detect `/` at start of input → show SkillDropdown
    - After typing `/`, filter skills as user types more characters (e.g., `/ac` filters to "acmg_classification")
    - On skill select: replace `/...` with skill name in input, show skill indicator
    - On send: include `skill_name` in WebSocket message if skill was selected
    - Show active skill indicator above input (Tag with skill name, X to deselect)

  **Must NOT do**:
  - Do not implement skill execution (backend handles this)
  - Do not modify the actual chat message sending logic yet (Task 17)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Interactive dropdown UI with keyboard support and filtering
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 13, 15, 16)
  - **Blocks**: Task 17
  - **Blocked By**: Tasks 4, 5, 7

  **References**:

  **Pattern References**:
  - `frontend/src/components/ChatInterface.tsx:288-308` - Current input area with TextArea and Send button. SkillDropdown must integrate here.
  - `frontend/src/components/ChatInterface.tsx:96-101` - `handleKeyPress()` pattern. Add `/` detection here.
  - Ant Design Select with search: https://ant.design/components/select#select-with-search

  **Acceptance Criteria**:

  - [ ] SkillDropdown component exists
  - [ ] Typing `/` shows dropdown
  - [ ] Filtering works (type `/ac` → shows ACMG skill)
  - [ ] Skill selection updates input state
  - [ ] Keyboard navigation works

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Slash command shows dropdown
    Tool: Playwright
    Preconditions: Frontend dev server running, at least one patient loaded
    Steps:
      1. Navigate to analysis page with chat
      2. Click on chat input TextArea
      3. Type "/" character
      4. Assert: SkillDropdown is visible
      5. Assert: Shows at least one skill option
      6. Screenshot
    Expected Result: Dropdown appears with skill list
    Failure Indicators: No dropdown appears
    Evidence: .sisyphus/evidence/task-14-slash-dropdown.png

  Scenario: Skill filtering works
    Tool: Playwright
    Preconditions: SkillDropdown visible
    Steps:
      1. Continue typing "/acmg" in the input
      2. Assert: Only ACMG-related skills shown (filtered list)
      3. Press Escape
      4. Assert: Dropdown closes
    Expected Result: Filter narrows to matching skills
    Failure Indicators: All skills still shown regardless of filter
    Evidence: .sisyphus/evidence/task-14-skill-filter.png
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(ui): add slash command skill dropdown with search and keyboard nav`
  - Files: `frontend/src/components/SkillDropdown.tsx`, `frontend/src/components/ChatInterface.tsx`
  - Pre-commit: `cd frontend && npx tsc --noEmit`

- [x] 15. Streaming Message Renderer

  **What to do**:
  - Create `frontend/src/components/StreamingMessage.tsx`:
    - Render assistant messages with incremental content updates
    - Use `useState` + `useEffect` to append chunks to displayed content
    - Show blinking cursor at end of content while streaming
    - When `is_streaming` transitions to false, render final content with references and confidence (same as renderMessage in ChatInterface)
    - Handle empty content gracefully (show loading indicator)
    - If skill_name is present, wrap content in SkillCard component
  - The component receives chunks via props or context (not WebSocket directly)

  **Must NOT do**:
  - Do not handle WebSocket connection here (Task 17 does that)
  - Do not modify existing renderMessage function yet

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 17
  - **Blocked By**: Tasks 4, 5

  **References**:

  **Pattern References**:
  - `frontend/src/components/ChatInterface.tsx:133-198` - `renderMessage()` layout. StreamingMessage must produce identical output when streaming completes.
  - `frontend/src/components/SkillCard.tsx` - Use for skill output rendering (Task 6).

  **Acceptance Criteria**:

  - [ ] StreamingMessage component exists
  - [ ] Content renders incrementally
  - [ ] Blinking cursor shown during streaming
  - [ ] Final render matches renderMessage output

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: StreamingMessage renders content incrementally
    Tool: Playwright
    Preconditions: Component mounted in test story/page
    Steps:
      1. Render StreamingMessage with initial content="Hello"
      2. Append chunk " world" to content
      3. Assert: Text shows "Hello world"
      4. Mark is_streaming=false
      5. Assert: No blinking cursor
      6. Screenshot
    Expected Result: Content updates as chunks arrive
    Failure Indicators: Content does not update, or final render differs
    Evidence: .sisyphus/evidence/task-15-streaming-render.png
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(ui): add streaming message renderer with incremental updates`
  - Files: `frontend/src/components/StreamingMessage.tsx`
  - Pre-commit: `cd frontend && npx tsc --noEmit`

- [x] 16. Settings Skills Tab

  **What to do**:
  - Extend `frontend/src/components/Settings.tsx`:
    - Add Ant Design `Tabs` component with two tabs: "LLM Settings" (existing) + "Skills"
    - Skills tab content:
      - Table (Ant Design `Table`) showing all skills with columns: Icon, Name, Description, Type (Tag), Enabled (Switch)
      - Each row expandable to show config JSON editor (Ant Design `Input.TextArea` for JSON)
      - "Save" button per skill to PUT config changes
      - Load skills on mount via `api.getSkills()` + `api.getSkillConfigs()`
    - Move existing LLM settings form into the first tab

  **Must NOT do**:
  - Do not remove existing LLM settings functionality
  - Do not add skill authoring UI

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 17
  - **Blocked By**: Tasks 4, 7

  **References**:

  **Pattern References**:
  - `frontend/src/components/Settings.tsx:136-262` - Existing settings form. Move into Tab pane.
  - Ant Design Tabs: https://ant.design/components/tabs
  - Ant Design Table: https://ant.design/components/table
  - Ant Design Switch: https://ant.design/components/switch

  **Acceptance Criteria**:

  - [ ] Settings has two tabs: "LLM Settings" and "Skills"
  - [ ] Skills tab shows table of all skills with enable/disable toggle
  - [ ] Config changes persist via API
  - [ ] Existing LLM settings unchanged

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Skills tab shows all 5 skills
    Tool: Playwright
    Preconditions: Frontend and backend running, skills registered
    Steps:
      1. Navigate to Settings page
      2. Click "Skills" tab
      3. Assert: Table shows 5 rows
      4. Assert: Each row has Switch component
      5. Screenshot
    Expected Result: 5 skills listed with toggle switches
    Failure Indicators: Missing skills or missing controls
    Evidence: .sisyphus/evidence/task-16-skills-tab.png

  Scenario: Toggle skill enable/disable
    Tool: Playwright
    Preconditions: Skills tab visible
    Steps:
      1. Click Switch on "ACMG Classification" row to disable
      2. Assert: Switch shows disabled state
      3. Reload page
      4. Click "Skills" tab
      5. Assert: ACMG Classification still disabled (persisted)
    Expected Result: Setting persists after reload
    Failure Indicators: Reverts to previous state after reload
    Evidence: .sisyphus/evidence/task-16-skill-toggle.png
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `feat(settings): add Skills tab for skill configuration management`
  - Files: `frontend/src/components/Settings.tsx`
  - Pre-commit: `cd frontend && npx tsc --noEmit`

- [x] 17. ChatInterface Full Integration

  **What to do**:
  - Rewrite `frontend/src/components/ChatInterface.tsx` to integrate all components:
    - Replace REST-based `handleSend()` with WebSocket-based sending:
      - Use `ChatWebSocket` (Task 5) to connect on mount
      - Send messages via WebSocket
      - Receive streaming chunks, update message content incrementally
    - Use `StreamingMessage` (Task 15) to render assistant messages while streaming
    - Use `SkillCard` (Task 6) when skill_name is present in response
    - Integrate `SkillDropdown` (Task 14) for `/` commands
    - Add "Stop" button (replaces Send button during streaming) to send cancel message
    - Maintain backward compatibility: if WebSocket fails, fall back to REST API
    - Update `Zustand` store with new message types (StreamingChatMessage)
    - Load enabled skills list on mount via `api.getSkills()`
    - Show skill indicator above input when a skill is selected

  **Must NOT do**:
  - Do not remove REST API fallback
  - Do not modify WebSocket service or SkillDropdown component (those are done)
  - Do not add new npm dependencies

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Complex integration of 5+ components, careful state management
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4 (final integration)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 6, 13, 14, 15, 16

  **References** (CRITICAL):

  **Pattern References**:
  - `frontend/src/components/ChatInterface.tsx` - Entire current component. Must preserve message rendering, references, confidence badges while adding streaming + skills.
  - `frontend/src/services/websocket.ts` - ChatWebSocket API (Task 5).
  - `frontend/src/components/StreamingMessage.tsx` - Streaming renderer (Task 15).
  - `frontend/src/components/SkillCard.tsx` - Skill output card (Task 6).
  - `frontend/src/components/SkillDropdown.tsx` - `/` command dropdown (Task 14).
  - `frontend/src/store/index.ts:85-86` - `addChatMessage` and `setChatMessages` actions.

  **WHY Each Reference Matters**:
  - This task is the integration point; must use all preceding components correctly

  **Acceptance Criteria**:

  - [ ] Chat sends via WebSocket and renders streaming responses
  - [ ] `/` shows skill dropdown, selecting skill includes it in message
  - [ ] Skill responses render in SkillCard
  - [ ] Stop button cancels streaming
  - [ ] Falls back to REST if WebSocket unavailable
  - [ ] Existing message rendering (references, confidence) preserved

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Full end-to-end chat with streaming
    Tool: Playwright
    Preconditions: Frontend + backend running, LLM configured
    Steps:
      1. Navigate to analysis page for a patient
      2. Type "What are the most significant variants?" in chat input
      3. Click Send button
      4. Wait up to 30s for response to start appearing
      5. Assert: Content appears incrementally (take 2 screenshots 2s apart, content should differ)
      6. Assert: When complete, references and confidence badge visible
      7. Screenshot final state
    Expected Result: Streaming text appears incrementally, final result shows references
    Failure Indicators: No response, or response appears all at once
    Evidence: .sisyphus/evidence/task-17-e2e-streaming.png

  Scenario: Skill activation via slash command
    Tool: Playwright
    Preconditions: Frontend + backend running, skills registered
    Steps:
      1. Click chat input
      2. Type "/"
      3. Assert: SkillDropdown visible
      4. Click "ACMG Classification" skill
      5. Assert: Skill indicator shown above input
      6. Type "Classify the BRCA1 variant"
      7. Click Send
      8. Wait for response
      9. Assert: Response rendered in SkillCard with blue border
      10. Screenshot
    Expected Result: Skill-activated message renders in SkillCard
    Failure Indicators: No SkillCard, or skill not included in request
    Evidence: .sisyphus/evidence/task-17-skill-activation.png

  Scenario: Stop button cancels streaming
    Tool: Playwright
    Preconditions: Chat is streaming a response
    Steps:
      1. Send a question in chat
      2. While streaming, click Stop button (replaces Send during streaming)
      3. Assert: Streaming stops, partial content preserved
      4. Assert: Send button reappears
    Expected Result: Streaming stops, partial message remains visible
    Failure Indicators: Streaming continues or message disappears
    Evidence: .sisyphus/evidence/task-17-stop-streaming.png

  Scenario: WebSocket fallback to REST
    Tool: Playwright
    Preconditions: Backend REST API working, WebSocket deliberately broken
    Steps:
      1. Temporarily make WebSocket connection fail (or simulate)
      2. Send a chat message
      3. Assert: Response still appears (via REST fallback)
      4. Assert: No error shown to user (graceful degradation)
    Expected Result: Chat works even without WebSocket
    Failure Indicators: No response or error toast
    Evidence: .sisyphus/evidence/task-17-ws-fallback.txt
  ```

  **Commit**: YES
  - Message: `feat(chat): fully integrate skills, streaming, and WebSocket into ChatInterface`
  - Files: `frontend/src/components/ChatInterface.tsx`, `frontend/src/store/index.ts`
  - Pre-commit: `cd frontend && npx tsc --noEmit`

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
  Run `tsc --noEmit` + linter + `bun test`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (features working together, not isolation). Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(skills): add skill framework, streaming, and frontend scaffolding` - multiple files
- **Wave 2**: `feat(skills): implement 5 genetic diagnosis skills` - skills/*.py files
- **Wave 3**: `feat(skills): integrate streaming + skills into chat flow` - rag_service.py, ChatInterface.tsx
- **Wave 4**: `feat(skills): complete ChatInterface integration` - ChatInterface.tsx, Settings.tsx

---

## Success Criteria

### Verification Commands
```bash
# Backend tests
cd backend && pytest tests/ -v  # Expected: all pass

# Frontend build
cd frontend && npm run build    # Expected: success, no errors

# Frontend type check
cd frontend && npx tsc --noEmit  # Expected: no errors

# WebSocket connectivity test
websocat ws://localhost:8080/api/chat/ws/1  # Expected: connection established

# Skills API
curl http://localhost:8080/api/skills        # Expected: JSON with 5 skills
curl http://localhost:8080/api/skills/config # Expected: skill configs
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] `/` command shows skill dropdown in chat
- [ ] Skill output renders in SkillCard
- [ ] Messages stream incrementally
- [ ] Settings has Skills tab
- [ ] Cancel button works during streaming
