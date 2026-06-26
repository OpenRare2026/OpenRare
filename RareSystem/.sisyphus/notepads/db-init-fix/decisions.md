# Decisions - db-init-fix

## 2026-05-27
- Fix approach: Import `database.models` and `database.case_models` inside `init_db()` before `create_all()`
- Rationale: Explicit, obvious, doesn't rely on `__init__.py` being correctly configured
- Alternative rejected: `from database import *` — too broad, implicit
- Test strategy: TDD (RED → GREEN → REFACTOR)
