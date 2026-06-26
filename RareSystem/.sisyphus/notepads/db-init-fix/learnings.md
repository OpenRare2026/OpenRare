# Learnings - db-init-fix

## 2026-05-27 Initial Analysis
- Root cause: `init_db()` in `database/session.py` calls `Base.metadata.create_all()` without importing model classes first
- `database/session.py` only imports `from .base import Base` — no models
- `database/__init__.py` imports all models but isn't loaded before `init_db()` is called
- Three startup paths affected: main.py:startup_event, docker/start.sh, run.py (indirect)
- Alembic env.py correctly imports models — migrations work fine
- Two database files exist locally: root `rare_disease_diagnosis.db` and `backend/rare_disease_diagnosis.db`
- 13 expected tables: patients, vcf_files, variants, acmg_evidence, acmg_classifications, clinical_reports, research_reports, case_documents, case_embeddings, chat_sessions, chat_messages, llm_settings, skill_configs
