## Learnings

## 2026-05-19 Session Start
- Project: Rare Disease Genetic Diagnosis System
- Frontend: React 18 + TypeScript + Ant Design 5 + Zustand + Vite
- Backend: FastAPI + SQLAlchemy + RAG (FAISS + sentence-transformers) + Multi-provider LLM
- No existing skill/streaming/slash-command system
- ChatInterface.tsx uses batch rendering (await full response)
- llm_client.py has ABC pattern with 4 providers (OpenAI, Anthropic, Ollama, Custom)
- rag_service.py has ask() -> build context -> retrieve -> generate -> return complete
- Settings.tsx only has LLM config (provider/key/model/temperature/max_tokens)

## Q&A System Architecture - Codebase Exploration (May 20, 2026)

### Overview
The Q&A system is a RAG-based (Retrieval-Augmented Generation) system with a skills/plugins architecture for extending functionality.

### Key Architecture Patterns

#### 1. Skill System Architecture
- **Base Class**: `Skill` (ABC) in `backend/services/skill_base.py`
  - Abstract methods: `execute(context: SkillContext) -> SkillResult`
  - Properties: `name`, `description`, `skill_type`, `icon`, `input_schema`
  - Two skill types: `prompt_injection` (LLM-powered) and `tool_call` (data query)

- **Registry Pattern**: `SkillRegistry` with auto-discovery
  - Location: `backend/services/skill_base.py::create_skill_registry()`
  - Auto-discovers skills from `backend/services/skills/` package
  - Uses `pkgutil.iter_modules()` for dynamic loading

- **Skill Context/Result**: Dataclasses for type-safe communication
  - `SkillContext`: query, patient_id, db_session, llm_client, case_context
  - `SkillResult`: content, references, confidence, metadata

#### 2. RAG Service Core
- **Main Service**: `RAGService` in `backend/services/rag_service.py`
  - Document retrieval via `EmbeddingService` (FAISS + sentence-transformers)
  - LLM integration via `LLMClient` (multi-provider: OpenAI, Anthropic, Ollama)
  - Session management with `ChatSession` and `ChatMessageRecord`
  - Streaming support via `ask_stream()` generator

- **Key Methods**:
  - `ask()`: Standard Q&A with context retrieval
  - `ask_stream()`: Streaming responses with skill support
  - `index_case_document()`: Document indexing for RAG
  - `index_patient_variants()`: Auto-index patient data

#### 3. API Layer Structure
- **Chat API**: `backend/api/chat.py`
  - REST endpoints: `/api/chat/{patient_id}`, `/api/chat/qa`
  - WebSocket endpoint: `/api/chat/ws/{patient_id}` in `main.py`
  - Integration with `RAGService` and `ConnectionManager`

- **Skills API**: `backend/api/skills.py`
  - `GET /api/skills`: List all skills
  - `GET /api/skills/config`: Get skill configurations
  - `PUT /api/skills/config/{skill_name}`: Update skill config
  - `POST /api/skills/{skill_name}/execute`: Execute skill (REST fallback)

#### 4. Frontend Integration
- **Components**:
  - `ChatInterface.tsx`: Main Q&A UI with WebSocket support
  - `SkillDropdown.tsx`: Skill selection with search (triggered by `/`)
  - `StreamingMessage.tsx`: Render streaming responses with references
  - `SkillCard.tsx`: Display skill information

- **WebSocket Protocol**:
  - Message types: `chat`, `skill`, `cancel`
  - Response types: `chunk`, `skill_result`, `done`, `error`, `session_info`
  - Streaming via chunked responses

#### 5. Database Models
- **Core Tables** (`backend/database/case_models.py`):
  - `CaseDocument`: Indexed documents for RAG
  - `CaseEmbedding`: Vector embeddings (pickled)
  - `ChatSession`: Q&A session tracking
  - `ChatMessageRecord`: Message history with references
  - `LLMSettings`: Per-patient LLM configuration
  - `SkillConfig`: Skill enable/disable + custom config

### Existing Skills (6 total)

| Skill Name | Type | Icon | Purpose |
|------------|------|------|---------|
| `acmg_classification` | prompt_injection | experiment | ACMG variant classification with PVS1-PS4, PM1-PM6, PP1-PP5 criteria |
| `phenotype_matching` | prompt_injection | medicine-box | Phenotype-gene association analysis |
| `pedigree_analysis` | prompt_injection | apartment | Inheritance pattern inference from family history |
| `variant_annotation` | tool_call | search | Query local database for variant annotations |
| `literature_search` | tool_call | book | Search local documents and RAG知识库 |
| *(PubMed skill - to be added)* | tool_call | book | PubMed/MEDLINE literature retrieval |

### Extension Points for New Skills

#### To Add a New Skill:
1. Create file: `backend/services/skills/{skill_name}_skill.py`
2. Inherit from `Skill` base class
3. Implement required properties and `execute()` method
4. Skill auto-registers on next server restart (no manual registration)
5. Frontend automatically picks up via `/api/skills` endpoint

#### Skill Implementation Pattern:
```python
from services.skill_base import Skill, SkillContext, SkillResult
from services.rag_service import ChatReference

class MyNewSkill(Skill):
    name = "my_skill_name"
    description = "Description in Chinese"
    skill_type = "tool_call"  # or "prompt_injection"
    icon = "book"  # matches Ant Design icon key
    input_schema = {"param": "type - description"}
    
    def execute(self, context: SkillContext) -> SkillResult:
        # Access context.db_session, context.llm_client, context.patient_id
        # Return SkillResult with content, references, confidence, metadata
```

### Data Flow

```
User Input (Frontend)
    ↓
WebSocket: /api/chat/ws/{patient_id}
    ↓
ConnectionManager → RAGService.ask_stream()
    ↓
[If skill selected] → SkillRegistry.get(skill_name) → Skill.execute()
    ↓
[If no skill] → RAG retrieval → LLM generation
    ↓
Streaming chunks → WebSocket → Frontend
    ↓
ChatInterface renders with StreamingMessage component
```

### Key Configuration Files
- `backend/.env.example`: Environment variables (API_PORT, CORS_ORIGINS, LLM keys)
- `backend/database/base.py`: SQLAlchemy base
- `backend/alembic/versions/`: Database migrations (including skill_configs table)

### Testing Patterns
- Skills are tested indirectly via integration tests
- No dedicated unit tests for individual skills yet
- Mock responses provided when LLM not configured

### Important Notes
1. **No PubMed skill exists yet** - `literature_skill.py` only searches local documents
2. **Skill configs stored in DB** - `SkillConfig` table controls enable/disable
3. **Frontend triggers skills with `/`** - Type `/` in chat to open skill dropdown
4. **Two execution modes**: 
   - `prompt_injection`: Builds prompt, sends to LLM
   - `tool_call`: Direct data query, returns structured results
5. **References system**: Skills can attach `ChatReference` objects for citations


## Q&A System Architecture - Codebase Exploration (May 20, 2026)

### Overview
The Q&A system is a RAG-based (Retrieval-Augmented Generation) system with a skills/plugins architecture for extending functionality.

### Key Architecture Patterns

#### 1. Skill System Architecture
- **Base Class**: `Skill` (ABC) in `backend/services/skill_base.py`
  - Abstract methods: `execute(context: SkillContext) -> SkillResult`
  - Properties: `name`, `description`, `skill_type`, `icon`, `input_schema`
  - Two skill types: `prompt_injection` (LLM-powered) and `tool_call` (data query)

- **Registry Pattern**: `SkillRegistry` with auto-discovery
  - Location: `backend/services/skill_base.py::create_skill_registry()`
  - Auto-discovers skills from `backend/services/skills/` package
  - Uses `pkgutil.iter_modules()` for dynamic loading

- **Skill Context/Result**: Dataclasses for type-safe communication
  - `SkillContext`: query, patient_id, db_session, llm_client, case_context
  - `SkillResult`: content, references, confidence, metadata

#### 2. RAG Service Core
- **Main Service**: `RAGService` in `backend/services/rag_service.py`
  - Document retrieval via `EmbeddingService` (FAISS + sentence-transformers)
  - LLM integration via `LLMClient` (multi-provider: OpenAI, Anthropic, Ollama)
  - Session management with `ChatSession` and `ChatMessageRecord`
  - Streaming support via `ask_stream()` generator

- **Key Methods**:
  - `ask()`: Standard Q&A with context retrieval
  - `ask_stream()`: Streaming responses with skill support
  - `index_case_document()`: Document indexing for RAG
  - `index_patient_variants()`: Auto-index patient data

#### 3. API Layer Structure
- **Chat API**: `backend/api/chat.py`
  - REST endpoints: `/api/chat/{patient_id}`, `/api/chat/qa`
  - WebSocket endpoint: `/api/chat/ws/{patient_id}` in `main.py`
  - Integration with `RAGService` and `ConnectionManager`

- **Skills API**: `backend/api/skills.py`
  - `GET /api/skills`: List all skills
  - `GET /api/skills/config`: Get skill configurations
  - `PUT /api/skills/config/{skill_name}`: Update skill config
  - `POST /api/skills/{skill_name}/execute`: Execute skill (REST fallback)

#### 4. Frontend Integration
- **Components**:
  - `ChatInterface.tsx`: Main Q&A UI with WebSocket support
  - `SkillDropdown.tsx`: Skill selection with search (triggered by `/`)
  - `StreamingMessage.tsx`: Render streaming responses with references
  - `SkillCard.tsx`: Display skill information

- **WebSocket Protocol**:
  - Message types: `chat`, `skill`, `cancel`
  - Response types: `chunk`, `skill_result`, `done`, `error`, `session_info`
  - Streaming via chunked responses

#### 5. Database Models
- **Core Tables** (`backend/database/case_models.py`):
  - `CaseDocument`: Indexed documents for RAG
  - `CaseEmbedding`: Vector embeddings (pickled)
  - `ChatSession`: Q&A session tracking
  - `ChatMessageRecord`: Message history with references
  - `LLMSettings`: Per-patient LLM configuration
  - `SkillConfig`: Skill enable/disable + custom config

### Existing Skills (6 total)

| Skill Name | Type | Icon | Purpose |
|------------|------|------|---------|
| `acmg_classification` | prompt_injection | experiment | ACMG variant classification with PVS1-PS4, PM1-PM6, PP1-PP5 criteria |
| `phenotype_matching` | prompt_injection | medicine-box | Phenotype-gene association analysis |
| `pedigree_analysis` | prompt_injection | apartment | Inheritance pattern inference from family history |
| `variant_annotation` | tool_call | search | Query local database for variant annotations |
| `literature_search` | tool_call | book | Search local documents and RAG知识库 |
| *(PubMed skill - to be added)* | tool_call | book | PubMed/MEDLINE literature retrieval |

### Extension Points for New Skills

#### To Add a New Skill:
1. Create file: `backend/services/skills/{skill_name}_skill.py`
2. Inherit from `Skill` base class
3. Implement required properties and `execute()` method
4. Skill auto-registers on next server restart (no manual registration)
5. Frontend automatically picks up via `/api/skills` endpoint

#### Skill Implementation Pattern:
```python
from services.skill_base import Skill, SkillContext, SkillResult
from services.rag_service import ChatReference

class MyNewSkill(Skill):
    name = "my_skill_name"
    description = "Description in Chinese"
    skill_type = "tool_call"  # or "prompt_injection"
    icon = "book"  # matches Ant Design icon key
    input_schema = {"param": "type - description"}
    
    def execute(self, context: SkillContext) -> SkillResult:
        # Access context.db_session, context.llm_client, context.patient_id
        # Return SkillResult with content, references, confidence, metadata
```

### Data Flow

```
User Input (Frontend)
    ↓
WebSocket: /api/chat/ws/{patient_id}
    ↓
ConnectionManager → RAGService.ask_stream()
    ↓
[If skill selected] → SkillRegistry.get(skill_name) → Skill.execute()
    ↓
[If no skill] → RAG retrieval → LLM generation
    ↓
Streaming chunks → WebSocket → Frontend
    ↓
ChatInterface renders with StreamingMessage component
```

### Key Configuration Files
- `backend/.env.example`: Environment variables (API_PORT, CORS_ORIGINS, LLM keys)
- `backend/database/base.py`: SQLAlchemy base
- `backend/alembic/versions/`: Database migrations (including skill_configs table)

### Testing Patterns
- Skills are tested indirectly via integration tests
- No dedicated unit tests for individual skills yet
- Mock responses provided when LLM not configured

### Important Notes
1. **No PubMed skill exists yet** - `literature_skill.py` only searches local documents
2. **Skill configs stored in DB** - `SkillConfig` table controls enable/disable
3. **Frontend triggers skills with `/`** - Type `/` in chat to open skill dropdown
4. **Two execution modes**: 
   - `prompt_injection`: Builds prompt, sends to LLM
   - `tool_call`: Direct data query, returns structured results
5. **References system**: Skills can attach `ChatReference` objects for citations

