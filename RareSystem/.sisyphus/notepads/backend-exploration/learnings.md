# Backend Exploration Learnings

## Date: 2026-05-20

## Backend Architecture Overview

### Framework & Stack
- **Web Framework**: FastAPI 0.109.0
- **Server**: Uvicorn 0.27.0
- **Database**: SQLite (development) / PostgreSQL (production) via SQLAlchemy 2.0.25
- **Async**: Native async/await support
- **Validation**: Pydantic 2.5.3

### Directory Structure
```
backend/
├── main.py                 # FastAPI app entry point, router registration
├── run.py                  # Development server runner
├── api/                    # API endpoints (FastAPI routers)
│   ├── health.py          # GET /api/health
│   ├── chat.py            # Chat Q&A endpoints (WebSocket + REST)
│   ├── skills.py          # Skill management & execution
│   ├── variants.py        # VCF upload & variant management
│   ├── acmg.py            # ACMG classification endpoints
│   ├── cases.py           # Case listing & browsing
│   ├── settings.py        # LLM configuration management
│   └── ws_manager.py      # WebSocket connection manager
├── services/               # Business logic layer
│   ├── rag_service.py     # RAG (Retrieval-Augmented Generation) service
│   ├── skill_base.py      # Skill ABC, context, result, registry
│   ├── skills/            # Skill implementations (auto-discovered)
│   │   ├── literature_skill.py  # Local document search
│   │   ├── acmg_skill.py
│   │   ├── variant_skill.py
│   │   ├── phenotype_skill.py
│   │   └── pedigree_skill.py
│   ├── llm_client.py      # Multi-provider LLM client (OpenAI, Anthropic, Ollama)
│   ├── embedding_service.py  # FAISS + sentence-transformers
│   ├── settings_service.py   # LLM settings CRUD
│   ├── gene_lookup.py     # GFF3-based gene annotation
│   ├── variant_detector.py   # SNV/INDEL/STR/CNV detection
│   ├── acmg_classifier.py    # ACMG/AMP classification
│   └── vcf_parser.py         # VCF file parsing
├── database/               # Database layer
│   ├── models.py          # Core models (Patient, Variant, ACMG, Reports)
│   ├── case_models.py     # Q&A models (Documents, Embeddings, Chat, LLMSettings)
│   ├── session.py         # DB session management
│   └── base.py            # SQLAlchemy base
└── models/                 # Pydantic models (minimal, mostly using SQLAlchemy models)
```

## API Endpoint Map

### Health
- `GET /api/health` - Health check

### Cases
- `GET /api/cases` - List all cases with variant counts
- `GET /api/cases/{patient_id}` - Get specific case details

### Variants
- `POST /api/variants/upload` - Upload VCF file (multipart form)
- `GET /api/variants/{vcf_file_id}` - List variants with pagination
- `GET /api/variants/detail/{variant_id}` - Get variant detail

### ACMG Classification
- `GET /api/acmg/{variant_id}` - Get ACMG classification
- `POST /api/acmg/{variant_id}/analyze` - Analyze variant with ACMG

### Chat/Q&A (RAG-based)
- `POST /api/chat/{patient_id}` - Send chat message
- `GET /api/chat/{session_token}` - Get chat history
- `POST /api/chat/qa` - Ask question (REST endpoint)
- `POST /api/chat/index/document` - Index a document
- `POST /api/chat/index/patient/{patient_id}` - Index patient variants
- `DELETE /api/chat/session/{session_token}` - End session
- `GET /api/chat/session/{session_token}/history` - Get session history
- `WebSocket /api/chat/ws/{patient_id}` - Real-time chat streaming

### Skills
- `GET /api/skills` - List all registered skills
- `GET /api/skills/config` - Get skill configurations
- `PUT /api/skills/config/{skill_name}` - Update skill config
- `POST /api/skills/{skill_name}/execute` - Execute a skill

### Settings (LLM Configuration)
- `GET /api/settings/patient/{patient_id}` - Get active LLM settings
- `GET /api/settings/patient/{patient_id}/all` - Get all LLM settings
- `POST /api/settings/patient/{patient_id}` - Create LLM settings
- `PUT /api/settings/{settings_id}` - Update LLM settings
- `DELETE /api/settings/{settings_id}` - Delete LLM settings
- `POST /api/settings/{settings_id}/activate` - Activate settings
- `GET /api/settings/providers` - List all LLM providers
- `GET /api/settings/providers/{provider}/models` - Get provider models

## Service Registration Patterns

### 1. Router Registration (main.py)
```python
from api.health import router as health_router
from api.chat import router as chat_router
from api.skills import router as skills_router

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(skills_router, prefix="/api", tags=["skills"])
```

### 2. Service Dependency Injection
```python
def get_rag_service(db: Session = Depends(get_db)) -> RAGService:
    return create_rag_service(db)

@router.post("/endpoint")
async def endpoint(rag_service: RAGService = Depends(get_rag_service)):
    ...
```

### 3. Factory Pattern for Services
```python
# services/rag_service.py
def create_rag_service(
    db: Session,
    embedding_service: Optional[EmbeddingService] = None,
    llm_client: Optional[LLMClient] = None,
    settings_service: Optional[SettingsService] = None
) -> RAGService:
    return RAGService(...)
```

### 4. Skill Auto-Discovery (services/skill_base.py)
```python
def create_skill_registry() -> SkillRegistry:
    registry = SkillRegistry()
    import services.skills as skills_package
    for importer, modname, ispkg in pkgutil.iter_modules(skills_package.__path__):
        module = importlib.import_module(f"services.skills.{modname}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Skill) and attr is not Skill:
                registry.register(attr())
    return registry
```

## External API Call Patterns

### 1. requests Library (Synchronous)
Used in `services/llm_client.py` for LLM provider APIs:
```python
import requests

response = requests.post(url, headers=self._headers, json=payload, timeout=60)
if response.status_code != 200:
    raise LLMClientError(f"API error: {response.status_code} - {response.text}")
data = response.json()
```

### 2. Streaming Support
```python
response = requests.post(url, json=payload, stream=True, timeout=60)
for line in response.iter_lines():
    if line.startswith("data: "):
        chunk = json.loads(line[6:])
        yield chunk.get("content", "")
```

### 3. Available HTTP Clients (from requirements.txt)
- `requests==2.31.0` - Synchronous HTTP client (used in llm_client.py)
- `httpx==0.26.0` - Async HTTP client (available, not currently used)
- `aiohttp==3.9.1` - Async HTTP client (available, not currently used)

## Configuration & Environment Variables

### Environment File Pattern
- Location: `backend/.env.example` (template), `backend/.env` (actual)
- Loaded via: `python-dotenv==1.0.0`

### Configuration Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rare_disease_db

# API
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
LOG_LEVEL=INFO

# External Services (commented examples)
# GNOMAD_API_URL=https://gnomad.broadinstitute.org/api
# CLINVAR_API_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
```

### LLM Settings (Database-stored)
Stored in `llm_settings` table per patient:
- provider: "openai", "anthropic", "ollama", "custom"
- api_key: Encrypted API key
- model: Model name
- base_url: Custom endpoint URL
- temperature: 0.0-2.0
- max_tokens: 1-32768

## Existing Literature Search Implementation

### Current State (services/skills/literature_skill.py)
- **Name**: `literature_search`
- **Type**: `tool_call`
- **Functionality**: Searches LOCAL documents only
  - Queries `CaseDocument` table in database
  - Uses FAISS vector search for similarity
  - NO external API calls (PubMed, PMC, etc.)

### Gap Identified
**No PubMed/external literature retrieval exists**. The current implementation:
- Only searches indexed local case documents
- No integration with PubMed API, PMC, or other external databases
- No real-time literature fetching

## Key Dependencies for External APIs

### Already Available
```
requests==2.31.0      # Sync HTTP client
httpx==0.26.0         # Async HTTP client  
aiohttp==3.9.1        # Async HTTP client
```

### Not Yet Used
- No PubMed API integration
- No NCBI eutils calls
- No external database queries (gnomAD, ClinVar commented out in .env.example)

## Patterns to Follow for New PubMed Service

### 1. Service Layer (services/pubmed_service.py)
```python
import requests
from typing import List, Optional

class PubMedServiceError(Exception):
    pass

class PubMedService:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def search(self, query: str, max_results: int = 20) -> List[dict]:
        # Use requests library (consistent with llm_client.py)
        response = requests.get(url, params=params, timeout=60)
        ...
```

### 2. Skill Integration (services/skills/pubmed_skill.py)
```python
from services.skill_base import Skill, SkillContext, SkillResult

class PubMedSearchSkill(Skill):
    name = "pubmed_search"
    description = "Search PubMed literature for genetic variants and diseases"
    skill_type = "tool_call"
    icon = "book-open"
    
    def execute(self, context: SkillContext) -> SkillResult:
        # Call PubMedService
        # Format results
        # Return SkillResult with references
```

### 3. API Endpoint (api/literature.py) - Optional
```python
from fastapi import APIRouter

router = APIRouter(prefix="/literature", tags=["literature"])

@router.get("/pubmed/search")
async def search_pubmed(query: str, max_results: int = 20):
    service = PubMedService()
    results = service.search(query, max_results)
    return results
```

### 4. Environment Configuration (.env)
```bash
# External Literature APIs
NCBI_API_KEY=your_ncbi_api_key  # Optional, increases rate limits
PUBMED_BASE_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils
```

## WebSocket Pattern (for Real-time Features)

### Connection Manager (api/ws_manager.py)
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, patient_id: int):
        await websocket.accept()
        self.active_connections[patient_id] = websocket
    
    async def send_to_client(self, patient_id: int, message: dict):
        websocket = self.active_connections.get(patient_id)
        if websocket:
            await websocket.send_json(message)
```

### WebSocket Endpoint (main.py)
```python
@app.websocket("/api/chat/ws/{patient_id}")
async def websocket_chat(websocket: WebSocket, patient_id: int):
    await manager.connect(websocket, patient_id)
    while True:
        data = await websocket.receive_json()
        # Process and stream response
```

## Database Session Pattern

### Dependency (database/session.py)
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Usage in Endpoints
```python
@router.get("/endpoint")
async def endpoint(db: Session = Depends(get_db)):
    results = db.query(Model).filter(...).all()
    return results
```

## Error Handling Pattern

### Custom Exception (api/middleware.py)
```python
class APIException(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 500):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": exc.message}
    )
```

## Summary

This backend is well-structured for adding a PubMed literature retrieval service:

1. **Clear service layer pattern** - Business logic in `services/`, endpoints in `api/`
2. **Dependency injection** - Clean separation of concerns
3. **Existing HTTP clients** - `requests`, `httpx`, `aiohttp` already available
4. **Skill system** - Easy to add new `PubMedSearchSkill`
5. **LLM client pattern** - Good reference for external API integration
6. **Environment config** - Standard pattern for API keys and URLs
7. **Error handling** - Custom exceptions with consistent responses

**Key Gap**: No external literature API integration exists. Current `literature_skill` only searches local documents.
