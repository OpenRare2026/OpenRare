# 修复数据库初始化：解决 "no such table: patients" 错误

## TL;DR

> **Quick Summary**: VCF上传时因数据库表未正确初始化导致 `sqlite3.OperationalError: no such table: patients`。需要加固 init_db() 增加验证机制、迁移到 FastAPI lifespan、修复 alembic.ini 路径、清理残留DB文件、添加防御性检查。
> 
> **Deliverables**:
> - 健壮的 `init_db()` 函数，含表存在性验证和详细日志
> - FastAPI lifespan context manager 替代废弃的 `@app.on_event("startup")`
> - 修复后的 `alembic.ini` 使用绝对路径
> - 残留数据库文件清理
> - 关键端点的防御性数据库检查
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 → Task 3 → Task 5 → Task 6 → F1-F4

---

## Context

### Original Request
用户上传 VCF 文件时，`POST /api/variants/upload` 返回 500 错误，日志显示 `sqlite3.OperationalError: no such table: patients`。

### Interview Summary
**Key Discussions**:
- 错误发生点：`api/variants.py` 第89行 `db.query(Patient).filter(Patient.id == pid).first()`
- `init_db()` 存在但缺乏验证，`create_all()` 可能为空操作（metadata为空时）
- `@app.on_event("startup")` 已废弃，reload时可能有时序问题
- alembic.ini 相对路径导致根目录残留DB文件

**Research Findings**:
- 存在两个数据库文件：`backend/rare_disease_diagnosis.db`(663KB, 13表) 和 `项目根/rare_disease_diagnosis.db`(94KB, 7表)
- 两个DB都有 patients 表，但错误仍发生，说明应用连接的可能是错误的或空的数据库
- `session.py` 使用 `Path(__file__).resolve().parent.parent` 计算绝对路径 — 正确
- alembic.ini 第89行使用相对路径 `sqlite:///./rare_disease_diagnosis.db`
- 无 .env 文件，无 DATABASE_URL 环境变量

### Self-Performed Gap Analysis (Metis unavailable)
**Identified Gaps** (addressed):
- 未验证 `init_db()` 执行结果 → 增加表存在性验证
- 废弃API的使用 → 迁移到 lifespan
- alembic.ini 路径不一致 → 修复为绝对路径
- 残留DB文件可能造成混淆 → 清理
- 无防御性检查 → 关键端点添加 DB 健康检查

---

## Work Objectives

### Core Objective
确保应用启动时数据库表100%可靠创建，VCF上传端点不再因缺少表而报500错误。

### Concrete Deliverables
- 修改后的 `backend/database/session.py`：`init_db()` 增加验证逻辑和日志
- 修改后的 `backend/main.py`：使用 lifespan 替代 `@app.on_event("startup")`
- 修改后的 `backend/alembic.ini`：绝对路径替代相对路径
- 清理 `/mnt/zzb/peixunban/hujie/hanjianbing/rare_disease_diagnosis.db`（根目录残留文件）
- 修改后的 `backend/api/variants.py`：防御性 DB 检查

### Definition of Done
- [ ] `curl -X POST http://localhost:8080/api/variants/upload` 上传VCF文件返回 200
- [ ] 应用启动日志明确显示 "Database initialized: N tables verified"
- [ ] 不存在项目根目录的残留 .db 文件
- [ ] `alembic upgrade head` 从任意目录运行都指向同一数据库

### Must Have
- `init_db()` 必须验证关键表（patients, variants, vcf_files 等）存在
- 启动时日志必须显示实际连接的数据库路径
- VCF上传不再因缺少表而500

### Must NOT Have (Guardrails)
- 不修改数据库模型/Schema
- 不迁移到 PostgreSQL
- 不添加新的业务功能
- 不删除 `backend/rare_disease_diagnosis.db`（正确的数据库）
- 不引入新的外部依赖
- 不过度抽象（不要创建DB健康检查微服务）

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (no pytest configured for this specific fix)
- **Automated tests**: None (bug fix, verified via Agent QA)
- **Framework**: N/A

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **API/Backend**: Use Bash (curl) - Send requests, assert status + response fields
- **Database**: Use Bash (sqlite3) - Verify table existence, schema correctness

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - independent fixes):
├── Task 1: 加固 init_db() 添加验证和日志 [quick]
├── Task 2: 修复 alembic.ini 使用绝对路径 [quick]
└── Task 3: 清理项目根目录残留 DB 文件 [quick]

Wave 2 (After Wave 1 - depends on Task 1):
├── Task 4: 迁移 main.py 到 lifespan context manager (depends: 1) [quick]
├── Task 5: 添加防御性 DB 检查到 variants.py (depends: 1) [quick]
└── Task 6: 端到端验证 - 重启服务并测试 VCF 上传 (depends: 1, 2, 3, 4, 5) [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 4 → Task 6 → F1-F4
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|---------|------|
| 1 | - | 4, 5, 6 | 1 |
| 2 | - | 6 | 1 |
| 3 | - | 6 | 1 |
| 4 | 1 | 6 | 2 |
| 5 | 1 | 6 | 2 |
| 6 | 1, 2, 3, 4, 5 | F1-F4 | 2 |
| F1-F4 | 6 | - | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **3** - T1 → `quick`, T2 → `quick`, T3 → `quick`
- **Wave 2**: **3** - T4 → `quick`, T5 → `quick`, T6 → `quick`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. 加固 init_db() — 添加验证逻辑和详细日志

  **What to do**:
  - 在 `backend/database/session.py` 的 `init_db()` 函数中：
    1. 添加数据库路径日志：`logger.info(f"Database URL: {DATABASE_URL}")`
    2. 在 `create_all()` 之后添加表存在性验证：使用 `inspect(engine).get_table_names()` 确认关键表存在
    3. 验证关键表：`patients`, `variants`, `vcf_files`, `acmg_evidence`, `acmg_classifications`, `clinical_reports`, `research_reports`, `case_documents`, `case_embeddings`, `chat_sessions`, `chat_messages`, `llm_settings`, `skill_configs`
    4. 如果缺少表，记录 ERROR 级别日志并列出缺失的表名
    5. 如果所有表存在，记录 INFO 级别日志：`"Database initialized: N tables verified"`
    6. 创建辅助函数 `verify_tables(engine) -> bool` 返回验证结果
    7. 在 `init_db()` 中如果验证失败，重新尝试 `create_all()` 一次（处理metadata可能为空的情况）
  - 添加 `import logging` 和 `logger = logging.getLogger(__name__)` 到 session.py

  **Must NOT do**:
  - 不修改数据库模型/Schema
  - 不添加新的外部依赖
  - 不删除现有表或数据

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单文件修改，逻辑简单，影响范围明确
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: 无UI交互需求

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4, 5, 6
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `backend/database/session.py:1-72` — 完整文件，init_db() 在第52-65行，需要修改此函数并添加验证逻辑
  - `backend/database/models.py:1-34` — Patient 模型定义，确认表名为 "patients"
  - `backend/database/case_models.py` — Case 模型定义，确认需要验证的表名列表

  **API/Type References** (contracts to implement against):
  - `backend/database/base.py:17` — SQLAlchemy Base，create_all() 使用的 metadata 来源
  - SQLAlchemy `inspect(engine).get_table_names()` — 获取已有表名列表的推荐方式

  **External References**:
  - SQLAlchemy inspect API: `from sqlalchemy import inspect; inspect(engine).get_table_names()`

  **WHY Each Reference Matters**:
  - `session.py`: 这是核心修改文件，init_db() 函数所在位置
  - `models.py` + `case_models.py`: 提供需要验证的完整表名列表
  - `base.py`: 理解 Base.metadata.create_all() 的 metadata 来源
  - `inspect API`: 比查询 sqlite_master 更通用的表名获取方式（兼容 PostgreSQL）

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: init_db() 正确验证所有表存在
    Tool: Bash
    Preconditions: 数据库文件 backend/rare_disease_diagnosis.db 存在且包含所有13张表
    Steps:
      1. cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
      2. python3 -c "from database.session import init_db, verify_tables, engine; init_db(); result = verify_tables(engine); print(f'Verify result: {result}')"
      3. Assert output contains "Verify result: True" or "Database initialized" in logs
    Expected Result: 验证函数返回 True，日志显示所有表已验证
    Failure Indicators: 输出包含 "missing tables" 或 "Verify result: False"
    Evidence: .sisyphus/evidence/task-1-init-db-verify.txt

  Scenario: init_db() 在空数据库上创建所有表
    Tool: Bash
    Preconditions: 使用临时空数据库文件
    Steps:
      1. cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
      2. python3 -c "
import os, tempfile
from database.base import Base
from database.session import init_db, verify_tables
temp_db = tempfile.mktemp(suffix='.db')
os.environ['DATABASE_URL'] = f'sqlite:///{temp_db}'
from sqlalchemy import create_engine
temp_engine = create_engine(f'sqlite:///{temp_db}', connect_args={'check_same_thread': False})
import database.models, database.case_models
Base.metadata.create_all(bind=temp_engine)
result = verify_tables(temp_engine)
print(f'Tables created and verified: {result}')
os.unlink(temp_db)
"
      3. Assert output contains "Tables created and verified: True"
    Expected Result: 空数据库上 create_all() 成功创建所有表，验证通过
    Failure Indicators: 输出包含 "False" 或抛出异常
    Evidence: .sisyphus/evidence/task-1-init-db-empty.txt

  Scenario: init_db() 日志输出数据库路径
    Tool: Bash
    Preconditions: 无
    Steps:
      1. cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
      2. python3 -c "import logging; logging.basicConfig(level=logging.INFO); from database.session import init_db; init_db()" 2>&1 | grep -i "database"
      3. Assert output contains "Database URL:" with actual path
    Expected Result: 日志中包含实际的 DATABASE_URL 路径
    Failure Indicators: 无 "Database URL" 日志输出
    Evidence: .sisyphus/evidence/task-1-init-db-logging.txt
  ```

  **Commit**: YES (groups with 2, 3, 4, 5)
  - Message: `fix(database): ensure reliable DB initialization and fix "no such table" error`
  - Files: `backend/database/session.py`
  - Pre-commit: `cd backend && python -c "from database.session import init_db; init_db(); print('OK')"`

- [x] 2. 修复 alembic.ini 使用绝对路径

  **What to do**:
  - 修改 `backend/alembic.ini` 第89行：
    - 将 `sqlalchemy.url = sqlite:///./rare_disease_diagnosis.db` 改为注释或占位符
  - 修改 `backend/alembic/env.py`：在 `run_migrations_online()` 中用 `database.session.DATABASE_URL` 动态设置 sqlalchemy.url，替换从 ini 文件读取的静态配置
  - 这样无论从哪个目录运行 alembic，都使用与 session.py 相同的绝对路径

  **Must NOT do**:
  - 不修改 alembic 迁移文件内容
  - 不改变数据库 schema
  - 不删除 alembic 版本记录

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 配置文件修改，逻辑简单
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `playwright`: 无UI需求

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 6
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `backend/alembic.ini:89` — 当前使用相对路径 `sqlite:///./rare_disease_diagnosis.db`，需要修改
  - `backend/alembic/env.py:1-35` — Alembic 环境，需要在此动态设置 DB URL
  - `backend/database/session.py:12-18` — DATABASE_URL 的计算逻辑，env.py 应直接引用此变量

  **API/Type References**:
  - `backend/database/session.py:DATABASE_URL` — 正确的数据库 URL，env.py 应直接引用此变量

  **WHY Each Reference Matters**:
  - `alembic.ini:89`: 这是导致残留DB文件的直接原因——相对路径从不同目录运行时创建不同的DB
  - `env.py`: 修改此文件以动态读取正确的 DATABASE_URL 是最佳实践
  - `session.py:DATABASE_URL`: 已经正确计算的数据库URL，应被 alembic env.py 直接引用

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: alembic 从 backend 目录运行指向正确数据库
    Tool: Bash
    Preconditions: backend/rare_disease_diagnosis.db 存在
    Steps:
      1. cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
      2. python3 -c "from alembic.config import Config; c = Config('alembic.ini'); print(c.get_main_option('sqlalchemy.url'))"
      3. Assert URL 包含 "backend" 目录路径组件
    Expected Result: URL 指向 backend 目录下的正确数据库文件
    Failure Indicators: URL 包含 "./" 相对路径或指向项目根目录
    Evidence: .sisyphus/evidence/task-2-alembic-url.txt

  Scenario: alembic upgrade head 不创建新的根目录DB文件
    Tool: Bash
    Preconditions: 根目录已清理（Task 3 完成）
    Steps:
      1. cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
      2. python3 -m alembic upgrade head 2>&1
      3. ls /mnt/zzb/peixunban/hujie/hanjianbing/rare_disease_diagnosis.db 2>/dev/null && echo "STRAY DB EXISTS" || echo "No stray DB"
      4. Assert "No stray DB" 在输出中
    Expected Result: alembic 操作不创建根目录下的新 DB 文件
    Failure Indicators: 输出 "STRAY DB EXISTS"
    Evidence: .sisyphus/evidence/task-2-alembic-no-stray-db.txt
  ```

  **Commit**: YES (groups with 1, 3, 4, 5)
  - Message: `fix(database): ensure reliable DB initialization and fix "no such table" error`
  - Files: `backend/alembic.ini`, `backend/alembic/env.py`

- [x] 3. 清理项目根目录残留数据库文件

  **What to do**:
  - 删除 `/mnt/zzb/peixunban/hujie/hanjianbing/rare_disease_diagnosis.db`（94KB的残留文件）
  - 此文件是由 alembic 从项目根目录运行时（使用相对路径）创建的
  - 它只包含7张旧表，缺少 case_models 相关的6张表和 alembic_version
  - 确认 `backend/rare_disease_diagnosis.db` 是唯一正确的数据库文件

  **Must NOT do**:
  - 不删除 `backend/rare_disease_diagnosis.db`（这是正确的数据库）
  - 不修改数据库内容

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单个文件删除操作
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - 所有skill均不适用

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 6
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - 无代码模式参考（文件删除操作）

  **API/Type References**:
  - `backend/database/session.py:14` — `_DEFAULT_DB_PATH = _BACKEND_DIR / "rare_disease_diagnosis.db"`，确认正确的DB位于 backend 目录下

  **WHY Each Reference Matters**:
  - `session.py:14`: 确认应用实际使用的数据库路径是 backend/ 下，而非根目录，因此根目录的DB文件可以安全删除

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 根目录残留DB文件已删除
    Tool: Bash
    Preconditions: 根目录存在 rare_disease_diagnosis.db
    Steps:
      1. ls /mnt/zzb/peixunban/hujie/hanjianbing/rare_disease_diagnosis.db 2>&1
      2. Assert 输出为 "No such file" 或返回非0退出码
    Expected Result: 文件不存在
    Failure Indicators: 文件仍然存在
    Evidence: .sisyphus/evidence/task-3-stale-db-removed.txt

  Scenario: 正确的DB文件仍然存在
    Tool: Bash
    Preconditions: backend 目录的 DB 文件不应被误删
    Steps:
      1. ls -la /mnt/zzb/peixunban/hujie/hanjianbing/backend/rare_disease_diagnosis.db
      2. Assert 文件存在且大小 > 0
      3. sqlite3 /mnt/zzb/peixunban/hujie/hanjianbing/backend/rare_disease_diagnosis.db "SELECT count(*) FROM sqlite_master WHERE type='table';"
      4. Assert count >= 13
    Expected Result: 正确的数据库文件完好，包含所有13+张表
    Failure Indicators: 文件不存在或表数量不足
    Evidence: .sisyphus/evidence/task-3-correct-db-intact.txt
  ```

  **Commit**: YES (groups with 1, 2, 4, 5)
  - Message: `fix(database): ensure reliable DB initialization and fix "no such table" error`
  - Files: 删除 `rare_disease_diagnosis.db`（根目录）

- [x] 4. 迁移 main.py 到 FastAPI lifespan context manager

  **What to do**:
  - 修改 `backend/main.py`：
    1. 删除 `@app.on_event("startup")` 和 `@app.on_event("shutdown")` 装饰器及其函数
    2. 添加 `from contextlib import asynccontextmanager`
    3. 创建 `lifespan` 异步上下文管理器函数：
       ```python
       @asynccontextmanager
       async def lifespan(app: FastAPI):
           # Startup
           logger.info("Starting Rare Disease Genetic Diagnosis System API")
           logger.info(f"CORS enabled for origins: {CORS_ORIGINS}")
           from database.session import init_db, close_db
           init_db()
           logger.info("Database tables initialized")
           yield
           # Shutdown
           logger.info("Shutting down API server")
           close_db()
       ```
    4. 将 `lifespan=lifespan` 参数传入 `FastAPI()` 构造函数
    5. 确保 startup 逻辑完整迁移（原有的日志和 init_db 调用）
    6. 确保 shutdown 逻辑完整迁移，并调用 `close_db()` 清理连接

  **Must NOT do**:
  - 不修改路由注册逻辑
  - 不修改 CORS 配置
  - 不修改 WebSocket 处理
  - 不添加认证/授权功能
  - 不改变 API 端点行为

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单文件修改，FastAPI 官方推荐的迁移模式
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - 所有skill均不适用

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 5)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1 (需要 init_db() 的验证逻辑先就位)

  **References**:

  **Pattern References**:
  - `backend/main.py:131-144` — 当前的 startup/shutdown 事件处理，需要迁移到 lifespan
  - `backend/main.py:38-42` — FastAPI app 构造，需要添加 lifespan 参数

  **API/Type References**:
  - `backend/database/session.py:68-72` — `close_db()` 函数，应在 shutdown 阶段调用
  - FastAPI Lifespan: `from contextlib import asynccontextmanager` + `FastAPI(lifespan=...)`

  **External References**:
  - FastAPI lifespan docs: https://fastapi.tiangolo.com/advanced/events/#lifespan

  **WHY Each Reference Matters**:
  - `main.py:131-144`: 这是需要迁移的核心代码——从废弃的 on_event 迁移到推荐的 lifespan
  - `main.py:38-42`: app 构造函数需要添加 lifespan 参数
  - `session.py:68-72`: close_db() 之前未被调用，应在 shutdown 中调用
  - FastAPI lifespan docs: 官方推荐模式，确保正确实现

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 服务启动使用 lifespan 正确初始化数据库
    Tool: Bash
    Preconditions: main.py 已修改
    Steps:
      1. cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
      2. 验证代码不包含 @app.on_event: grep -n "on_event" main.py
      3. Assert grep 返回空（无 on_event 使用）
      4. 验证包含 lifespan: grep -n "lifespan" main.py
      5. Assert grep 找到 lifespan 定义和 FastAPI(lifespan=...) 使用
    Expected Result: 废弃的 on_event 已替换为 lifespan
    Failure Indicators: 仍然包含 "on_event" 或缺少 "lifespan"
    Evidence: .sisyphus/evidence/task-4-lifespan-migration.txt

  Scenario: close_db() 在 shutdown 时被调用
    Tool: Bash
    Preconditions: main.py 已修改
    Steps:
      1. cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
      2. grep -n "close_db" main.py
      3. Assert close_db 在 lifespan 的 yield 之后被调用
    Expected Result: lifespan 的 shutdown 部分调用 close_db()
    Failure Indicators: close_db 未被调用
    Evidence: .sisyphus/evidence/task-4-close-db.txt
  ```

  **Commit**: YES (groups with 1, 2, 3, 5)
  - Message: `fix(database): ensure reliable DB initialization and fix "no such table" error`
  - Files: `backend/main.py`

- [x] 5. 添加防御性 DB 检查到 variants.py 上传端点

  **What to do**:
  - 修改 `backend/api/variants.py`：
    1. 在 `upload_vcf` 函数开头添加防御性检查：
       ```python
       from database.session import verify_tables, init_db
       if not verify_tables(engine):
           logger.warning("Database tables missing, re-initializing...")
           init_db()
       ```
    2. 或更简洁：在 `db.query(Patient)` 之前用 try/except 捕获 `OperationalError`，触发 `init_db()` 后重试
    3. 推荐方案：在 `get_db()` 依赖中添加隐式检查（更通用），但这需要修改 session.py
    4. 最小化方案：仅在 upload 端点添加 try/except + 自动修复逻辑

  **Must NOT do**:
  - 不修改 VCF 解析逻辑
  - 不修改 ACMG 分类逻辑
  - 不添加新的 API 端点
  - 不过度防御（不要在每个查询前都检查表存在）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 小范围防御性编程修改
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - 所有skill均不适用

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1 (需要 verify_tables 和健壮的 init_db 先就位)

  **References**:

  **Pattern References**:
  - `backend/api/variants.py:56-157` — upload_vcf 端点完整代码，错误发生在第89行
  - `backend/api/variants.py:89` — `db.query(Patient).filter(Patient.id == pid).first()` 触发错误的行

  **API/Type References**:
  - `backend/database/session.py:verify_tables()` — Task 1 创建的验证函数
  - `backend/database/session.py:init_db()` — 健壮的初始化函数（Task 1 修改后）
  - `sqlalchemy.exc.OperationalError` — 需要捕获的异常类型

  **WHY Each Reference Matters**:
  - `variants.py:89`: 错误的精确触发点，防御代码应在此查询之前或周围
  - `verify_tables()`: Task 1 创建的验证函数，用于检查表是否就绪
  - `init_db()`: 健壮的初始化函数，作为修复手段
  - `OperationalError`: 需要捕获的具体异常类型

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 上传端点在表缺失时自动修复而非报500
    Tool: Bash (curl)
    Preconditions: 服务正在运行
    Steps:
      1. curl -X POST http://localhost:8080/api/variants/upload \
           -F "file=@/mnt/zzb/peixunban/hujie/hanjianbing/tests/test_data/sample.vcf" \
           -F "patient_id=1" 2>&1
      2. Assert HTTP status 为 200 或 201（不是 500）
      3. Assert 响应包含 "vcf_file_id" 和 "patient_id" 字段
    Expected Result: VCF 上传成功，即使 DB 表之前不存在也能自动初始化
    Failure Indicators: HTTP 500 或 "no such table" 错误消息
    Evidence: .sisyphus/evidence/task-5-upload-defensive.txt

  Scenario: 上传端点在正常情况下仍然工作
    Tool: Bash (curl)
    Preconditions: 服务正在运行，数据库表已存在
    Steps:
      1. curl -s -X POST http://localhost:8080/api/variants/upload \
           -F "file=@/mnt/zzb/peixunban/hujie/hanjianbing/tests/test_data/sample.vcf" \
           -F "patient_id=999" \
           -F "patient_name=TestPatient" 2>&1
      2. Assert HTTP status 200
      3. Assert JSON 响应包含 total_variants >= 0
    Expected Result: 正常上传流程不受防御性检查影响
    Failure Indicators: HTTP 非200 或超时
    Evidence: .sisyphus/evidence/task-5-upload-normal.txt
  ```

  **Commit**: YES (groups with 1, 2, 3, 4)
  - Message: `fix(database): ensure reliable DB initialization and fix "no such table" error`
  - Files: `backend/api/variants.py`

- [x] 6. 端到端验证 — 重启服务并测试 VCF 上传

  **What to do**:
  - 停止当前运行的服务进程（如果还在运行）
  - 重新启动服务：`cd backend && python run.py`
  - 观察启动日志：确认包含 "Database URL:" 和 "Database initialized: N tables verified"
  - 执行 VCF 上传测试，确认不再出现 500 错误
  - 检查是否有新的残留 .db 文件被创建
  - 如果项目有测试 VCF 文件，使用它；否则创建一个最小的测试 VCF 文件

  **Must NOT do**:
  - 不修改代码逻辑（仅验证）
  - 不删除正确的数据库文件

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 验证任务，不涉及代码修改
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - 所有skill均不适用

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (after all previous tasks)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 1, 2, 3, 4, 5

  **References**:

  **Pattern References**:
  - `backend/run.py` — 开发服务器启动脚本
  - `backend/main.py` — FastAPI 应用入口

  **API/Type References**:
  - `http://localhost:8080/api/health` — 健康检查端点
  - `http://localhost:8080/api/variants/upload` — VCF 上传端点
  - `http://localhost:8080/docs` — API 文档

  **WHY Each Reference Matters**:
  - `run.py`: 了解如何启动服务以进行端到端验证
  - `/api/health`: 快速验证服务是否正常运行
  - `/api/variants/upload`: 这是报错的端点，必须验证它能正常工作

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 服务启动日志显示数据库初始化信息
    Tool: Bash
    Preconditions: 服务已重启
    Steps:
      1. 停止旧服务进程（如果运行中）
      2. cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python run.py > /tmp/server_start.log 2>&1 &
      3. sleep 3
      4. grep -i "database" /tmp/server_start.log
      5. Assert 输出包含 "Database URL:" 和 "Database initialized"
    Expected Result: 启动日志明确显示数据库路径和初始化结果
    Failure Indicators: 缺少数据库初始化日志
    Evidence: .sisyphus/evidence/task-6-startup-logs.txt

  Scenario: VCF 上传返回 200 而非 500
    Tool: Bash (curl)
    Preconditions: 服务正在运行
    Steps:
      1. 创建最小测试 VCF 文件（如果不存在）：
         echo '##fileformat=VCFv4.2
##contig=<ID=chr1,length=248956422>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
chr1	12345	.	A	T	30	PASS	.' > /tmp/test.vcf
      2. curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://localhost:8080/api/variants/upload \
           -F "file=@/tmp/test.vcf" -F "patient_id=1" 2>&1
      3. Assert HTTP_CODE 为 200
      4. Assert 响应 JSON 包含 "vcf_file_id" 和 "total_variants" 字段
    Expected Result: 上传成功，返回 200 和正确响应格式
    Failure Indicators: HTTP 500 或 "no such table" 错误
    Evidence: .sisyphus/evidence/task-6-e2e-upload.txt

  Scenario: 无新的残留 DB 文件
    Tool: Bash
    Preconditions: 服务已启动并处理了请求
    Steps:
      1. find /mnt/zzb/peixunban/hujie/hanjianbing -name "*.db" -not -path "*/backend/*" -not -path "*/.git/*" -not -path "*/node_modules/*"
      2. Assert 无输出（项目根目录及其他非 backend 位置无 .db 文件）
    Expected Result: 只在 backend/ 下存在 .db 文件
    Failure Indicators: 在根目录或其他位置发现 .db 文件
    Evidence: .sisyphus/evidence/task-6-no-stray-db.txt
  ```

  **Commit**: NO (验证任务，不产生代码变更)

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter (if applicable). Review all changed files for: `as any`/type ignores, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration. Test edge cases: empty DB, missing tables. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Single commit**: `fix(database): ensure reliable DB initialization and fix "no such table" error`
  - Files: `backend/database/session.py`, `backend/main.py`, `backend/alembic.ini`, `backend/api/variants.py`
  - Pre-commit: `cd backend && python -c "from database.session import init_db; init_db(); print('OK')"`

---

## Success Criteria

### Verification Commands
```bash
# 1. 数据库初始化验证
cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
python -c "from database.session import init_db; init_db(); print('OK')"
# Expected: OK

# 2. 表存在性验证
sqlite3 /mnt/zzb/peixunban/hujie/hanjianbing/backend/rare_disease_diagnosis.db "SELECT count(*) FROM sqlite_master WHERE type='table';"
# Expected: 13 or more

# 3. 无残留DB文件
ls /mnt/zzb/peixunban/hujie/hanjianbing/rare_disease_diagnosis.db 2>/dev/null
# Expected: file not found

# 4. 服务启动验证
curl -s http://localhost:8080/api/health | python -m json.tool
# Expected: {"status": "healthy"} or similar

# 5. VCF上传验证
curl -X POST http://localhost:8080/api/variants/upload \
  -F "file=@test_data/sample.vcf" \
  -F "patient_id=1" \
  -F "patient_name=Test"
# Expected: 200 OK with UploadResponse
```

### Final Checklist
- [x] All "Must Have" present
- [x] All "Must NOT Have" absent
- [x] VCF upload returns 200 (not 500)
- [x] Startup logs show DB path and table count
