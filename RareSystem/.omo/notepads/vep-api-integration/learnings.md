# VEP API Integration - Learnings

## 2026-05-28 Session Start
- Backend runs on port 8000, frontend on 8888 (vite proxy)
- VEP API is on a SEPARATE server (also port 8000 but different machine)
- Frontend VariantList already has empty consequence and hgvs_p columns
- Current gene annotation: gene_lookup.py only does GFF3 coordinate lookup → gene symbol
- Database: SQLite at backend/rare_disease_diagnosis.db
- Config pattern: .env file + pydantic-settings or os.environ
- Upload endpoint: POST /api/variants/upload (variants.py:56-158)
- Integration point: variants.py:83-86 (after detection, before DB storage)
