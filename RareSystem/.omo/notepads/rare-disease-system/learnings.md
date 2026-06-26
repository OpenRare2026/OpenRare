# Frontend Setup Learnings

## Date: 2026-05-15

### Successful Patterns

#### Vite + React + TypeScript Setup
- Use Vite 6.x with `@vitejs/plugin-react` for fast development
- TypeScript configuration requires separate `tsconfig.node.json` for vite.config.ts
- Path alias `@/*` -> `src/*` configured in both tsconfig.json and vite.config.ts

#### Ant Design Integration
- Wrap app with `ConfigProvider` in main.tsx for global theme configuration
- Use `Layout` component (Header, Content, Footer) for consistent page structure
- Icons from `@ant-design/icons` work seamlessly with Ant Design components

#### API Proxy Configuration
```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

#### Environment Variables
- Use `.env.example` to document required environment variables
- Vite uses `VITE_` prefix for exposed environment variables
- Example: `VITE_API_BASE_URL=http://localhost:8000/api`

### Directory Structure Convention
```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route pages
│   ├── services/       # API service functions
│   ├── store/          # State management
│   ├── App.tsx         # Main application component
│   └── main.tsx        # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.example
```

### Dependencies Version Notes
- React 18.3.1 - Latest stable with concurrent features
- Ant Design 5.22.6 - Uses CSS-in-JS styling
- React Router DOM 7.1.1 - Latest with improved type safety
- Axios 1.7.9 - HTTP client for API calls

### Gotchas
- Port 3000 may be in use; Vite automatically finds next available port
- All source files must be in `src/` directory for TypeScript to compile
- `tsconfig.node.json` is required for vite.config.ts TypeScript support
# Backend Scaffolding Learnings

## Date: 2026-05-15

### FastAPI Setup Patterns

#### Environment Variable Handling
- Use `python-dotenv` for loading `.env` files
- Always provide defaults for environment variables
- Parse CORS_ORIGINS as comma-separated string: `os.getenv("CORS_ORIGINS", "...").split(",")`

#### Project Structure
```
backend/
├── api/          # FastAPI routers
├── models/       # Pydantic models
├── services/     # Business logic
├── database/     # DB connections and ORM models
├── main.py       # Application entry point
└── .env.example  # Environment template
```

#### CORS Configuration
- Configure CORS middleware before registering routes
- Allow credentials for frontend-backend communication
- Default origins: localhost:3000 for React/Vue dev servers

#### Logging Setup
- Configure logging at application startup
- Use format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Set level via environment variable for flexibility

### Dependencies (Minimal)
- fastapi: Web framework
- uvicorn: ASGI server
- pydantic: Data validation
- python-dotenv: Environment configuration

### Testing Approach
1. Import test: `python -c "from main import app; print('OK')"`
2. Health endpoint: `curl http://localhost:8000/api/health`
3. Server startup: `uvicorn main:app --reload`

## Task 6: Project Configuration Files - Learnings

### Dependencies Decisions

**Backend (requirements.txt)**:
- FastAPI 0.109.0: Modern async framework with automatic OpenAPI docs
- SQLAlchemy 2.0.25: Latest 2.x version with async support
- Celery 5.3.6: For async VCF processing tasks
- pysam 0.22.0: Essential for VCF/BAM file parsing
- numpy/pandas: Data processing for variant analysis
- scikit-allel: Population genetics analysis
- reportlab/weasyprint: Clinical report generation (PDF)

**Frontend (package.json updates)**:
- Added @antv/g2 and @antv/g2plot: Clinical data visualization
- Added echarts: Additional charting capabilities
- Added zustand: Lightweight state management (simpler than Redux)
- Added vitest + testing-library: Modern testing stack

### .gitignore Strategy

Root .gitignore covers both Python and Node patterns:
- Patient data files (*.vcf, *.bam, *.fastq) explicitly excluded
- Secrets and credentials patterns for security
- Build artifacts from both backend and frontend
- IDE settings for team development

### README Structure

Comprehensive documentation includes:
- Clear prerequisites (Python 3.9+, Node.js 18+)
- Step-by-step setup for both backend and frontend
- Multiple run options (uvicorn direct vs python main.py)
- Testing instructions for both stacks
- Security notes emphasizing local-only patient data processing
- Data flow diagram in text form

### Best Practices Applied

1. Version pinning for reproducibility (==) vs semver (^)
2. Grouped dependencies by category with comments
3. No secrets or environment-specific values in config files
4. Clear separation between dev and prod dependencies
5. Testing frameworks included from the start
