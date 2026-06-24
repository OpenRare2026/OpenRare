# AGENTS.md - 罕见病遗传诊断分析系统

## Project Overview

End-to-end analysis system for rare disease genetic diagnosis processing:
- Input: VCF files + patient characteristics (de-identified) + medical history + disease description
- Processing: Multi-type variant detection (SNV/INDEL, STR, CNV), QC, visualization, confidence evaluation
- Output: Dual-track mechanism
  - Clinical track: ACMG classification, clinical-grade reports (evidence chains, interpretable reasoning)
  - Research track: Hypotheses with explicit uncertainty quantification, evidence gaps
- Deployment: Local only, no patient data storage, secure external data invocation
- Interface: White-screen interactive UI, case-based Q&A

## Key Considerations

### ACMG Classification
- Implement ACMG/AMP guidelines for variant interpretation
- Evidence tables: PVS1, PS1-PS4, PM1-PM6, PP1-PP5, BP1-BP7
- Clinical track only for findings meeting clinical-grade criteria
- Research track for uncertain but potentially valuable findings

### Variant Detection
- SNV/INDEL detection (tools: GATK, bcftools, freebayes)
- STR analysis
- CNV detection
- Integration with population databases (gnomAD, ExAC) and clinical databases (ClinVar, HGMD)

### Clinical vs Research Output
- **Clinical track**: Required standards compliance, fully verified, patient-facing or clinician-facing
- **Research track**: Exploratory, documented uncertainty, hypothesis generation, not for clinical decision-making
- Clear visual distinction and warnings when using research output

### Data Privacy & Security
- No patient data storage on platform
- Local deployment preferred
- Secure external data invocation (encrypted APIs, secure containers)
- De-identified patient characteristics only

### Dual-Interface
- Web UI with white-screen interaction (no templates, dynamic rendering)
- Natural language Q&A over cases (RAG, vector search, or similar)
- Case-based exploration and drill-down

## Development Workflow

### Setup
```bash
# Clone repo (local deployment only)
git clone <repo-url>
cd <project-directory>

# Dependencies (specify based on framework choice)
# Frontend: npm install / yarn install / pnpm install
# Backend: pip install -r requirements.txt / poetry install

# Database setup (if using)
# docker-compose up -d postgresql
```

### Run Development Server
```bash
# Frontend dev server
npm run dev
# or
yarn dev

# Backend API server
python manage.py runserver
# or
python main.py
```

### Run Tests
```bash
# Run all tests
pytest
# or
npm test

# Run specific test file
pytest tests/test_acmg.py
```

### Build for Production
```bash
# Frontend build
npm run build

# Backend build
python setup.py build
# or
poetry build
```

## Directory Structure

```
.
├── src/                          # Source code
│   ├── backend/                  # Backend API
│   │   ├── api/                  # API endpoints
│   │   ├── models/               # Data models (ACMG, variants, patient)
│   │   ├── services/             # Business logic
│   │   │   ├── variant_detection.py
│   │   │   ├── acmg_classifier.py
│   │   │   ├── qc.py
│   │   │   └── visualization.py
│   │   └── database/             # Database models and migrations
│   ├── frontend/                 # Frontend UI
│   │   ├── components/           # Reusable components
│   │   ├── pages/                # Route pages
│   │   ├── services/             # API services
│   │   └── store/                # State management
│   └── shared/                   # Shared utilities
├── tests/                        # Test files
├── docs/                         # Documentation
├── config/                       # Configuration files
└── docker/                       # Docker configurations
```

## Key Technologies (to be decided during development)

Consider these stacks:

### Backend Options
- Python: FastAPI + SQLAlchemy + Celery (async processing)
- Node.js: Express/NestJS + TypeORM
- Go: Gin/gorilla

### Frontend Options
- React + TypeScript + Ant Design + AntV (visualization)
- Vue 3 + TypeScript + Element Plus
- Next.js for SSR capabilities

### VCF Processing
- GATK pipeline
- bcftools CLI + Python bindings
- pysam for VCF parsing

### Visualization
- AntV G2Plot (clinical data)
- ECharts / D3.js
- Interactive reports using PDF/HTML generation

### Q&A Implementation
- Vector embeddings + similarity search (FAISS, Pinecone)
- RAG pattern with LangChain or similar
- Domain-specific LLM (medical context)

## Important Notes

### Data Flow
1. Upload VCF + patient metadata → Parse → Validate
2. Variant detection pipeline → QC → Database storage
3. ACMG classification → Evidence scoring
4. Generate dual-track reports
5. Interactive visualization and Q&A

### Clinical Integration
- Reports must be editable by clinicians
- Evidence chains must be traceable to source data
- Uncertainty metrics must be clearly labeled
- All ACMG criteria must be justifiable

### Performance Considerations
- VCF files can be large (50MB-2GB+ for whole genome)
- Processing requires efficient VCF parsing
- For whole exome/genome: consider batch processing and job queues
- Interactive UI must handle large variant lists efficiently

### Testing Requirements
- Unit tests for ACMG rules (all criteria)
- Integration tests for VCF processing pipeline
- UI component tests for accessibility
- E2E tests for full analysis workflow
- Test data: synthetic VCFs with known ACMG classifications

### No External Patient Data Storage
- All patient data processed locally
- External data services invoked securely via APIs
- No database persistence for real patient data
