# PubMed RAG Skill for Case Q&A

## TL;DR

> **Quick Summary**: 在罕见病遗传诊断系统的病例问答部分增加 PubMed 文献检索增强 skill，通过 LLM 分解用户查询、检索 PubMed 获取 abstract、LLM 生成带 PMID 引用的循证回答。
> 
> **Deliverables**:
> - `backend/services/skills/pubmed_search_skill.py` — PubMed RAG skill 主文件
> - `backend/services/pubmed_cache.py` — PubMed 结果缓存层
> - `backend/services/skills/prompts/pubmed_prompts.py` — 查询分解+回答合成 prompt 模板
> - NCBI 环境变量配置（.env.example + .env）
> - 单元测试 + 集成测试
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves + final verification
> **Critical Path**: Task 3 (prompts) → Task 4 (skill) → Task 5 (integration) → F1-F4

---

## Context

### Original Request
在 case Q&A 的部分，增加一个可以根据用户提问将关键信息分解，然后通过 PubMed 来检索，大模型根据检索出来的 abstract 相关的信息对用户问题进行回答的 skill。

### Interview Summary
**Key Discussions**:
- LLM 方案: 使用 Settings 中配置的模型（复用 LLMSettings 表，支持 OpenAI/Anthropic/Ollama/Custom）
- 查询分解: LLM 直接分解用户问题为 PubMed 搜索查询（含 MeSH 术语扩展）
- 回答形式: 引用式回答 — 每条声明附带 PMID 引用（UpToDate 风格）
- 中英处理: LLM 一体化处理（中文问题→英文查询+MeSH→中文回答）
- 检索策略: 纯关键词检索（ESearch + EFetch），简单高效
- 缓存: 需要，按 query hash 缓存到本地，减少 NCBI API 调用
- 结果数量: 100 篇 abstract 全量送 LLM（用户明确选择）
- 测试策略: Tests-after

**Research Findings**:
- `PubMedService` 已完整实现（ESearch/ESummary/EFetch + 速率限制 + 重试逻辑）
- Skill 系统完整（Skill ABC + 自动发现注册 + WebSocket 流式传输）
- 前端 `ChatInterface.tsx` 自动支持新 skill（`/` 触发下拉 + 引用显示）
- `LiteratureSkill` 存在但只搜本地 DB，不调 PubMed
- `LLMClient` 通过 `SkillContext.llm_client` 传入，已由 `RAGService._execute_skill_stream` 创建
- PubMed ~5M 记录无 MeSH 索引，需同时用关键词搜索
- 无 API key 时速率限制 3/sec，有 key 10/sec

### Metis Review (Self-Performed — Metis 不可用)
**Identified Gaps** (addressed):
- 100 篇 abstract token 消耗（~30-40K tokens）：大多数模型 128K+ context window 可支持，默认为用户选择
- NCBI API key 未配置时 fallback：Skill 应返回清晰错误提示，引导用户配置
- 缓存 TTL：默认 24 小时，可配置
- 无结果/少结果时：LLM 应明确说明未找到相关文献
- 中文 MeSH 不存在时：LLM 翻译为英文 MeSH 等价术语
- PubMed 返回不足 100 篇：返回实际可用数量
- 网络/NCBI 超时：PubMedService 已有重试逻辑

---

## Work Objectives

### Core Objective
创建一个 PubMed 文献检索增强 skill，集成到现有 case Q&A 系统中，使用户能够通过自然语言提问获取基于 PubMed 文献的循证回答。

### Concrete Deliverables
- `backend/services/skills/pubmed_search_skill.py` — PubMed RAG skill 主文件
- `backend/services/pubmed_cache.py` — PubMed 查询结果缓存
- `backend/services/skills/prompts/pubmed_prompts.py` — Prompt 模板
- `backend/.env.example` 更新 — 添加 NCBI_EMAIL, NCBI_API_KEY
- `tests/test_pubmed_search_skill.py` — 单元测试
- `tests/test_pubmed_integration.py` — 集成测试

### Definition of Done
- [ ] `/api/skills` 返回列表包含 `pubmed_search` skill
- [ ] WebSocket `/api/chat/ws/{patient_id}` 支持 `skill_name: "pubmed_search"` 调用
- [ ] 前端 `/` 下拉菜单出现 PubMed 检索选项
- [ ] 输入中文问题 → 返回带 PMID 引用的中文循证回答
- [ ] 100 篇 abstract 正确获取并送 LLM 处理
- [ ] 缓存命中时跳过 NCBI API 调用
- [ ] NCBI 凭证缺失时返回清晰错误提示
- [ ] 所有测试通过

### Must Have
- LLM 驱动的查询分解（中文→英文+MeSH）
- 复用现有 PubMedService 进行 ESearch + EFetch
- 100 篇 abstract 全量送 LLM
- 引用式回答（每条声明附 PMID）
- 本地文件缓存（query hash → 结果，TTL 24h）
- NCBI 凭证缺失时的优雅降级（清晰错误提示）
- Skill 自动注册到现有 skill 系统

### Must NOT Have (Guardrails)
- 不修改 `pubmed_service.py` 核心逻辑
- 不修改 `literature_skill.py`
- 不添加 BioPython 依赖
- 不做向量嵌入/语义检索/重排序
- 不做幻觉检测/NLI 验证
- 不修改 `skill_base.py` 接口
- 不修改前端代码（应自动工作）
- 不做 token 预算限制（用户明确选择 100 篇全量）
- 不在 skill 中硬编码 NCBI 凭证

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest + fixtures in tests/)
- **Automated tests**: Tests-after
- **Framework**: pytest
- **Test files**: `tests/test_pubmed_search_skill.py`, `tests/test_pubmed_integration.py`

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **API/Backend**: Use Bash (curl) — Send requests, assert status + response fields
- **Library/Module**: Use Bash (pytest) — Run tests, verify pass/fail
- **Integration**: Use Bash (curl + python) — End-to-end flow verification

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - foundation, 3 parallel tasks):
├── Task 1: NCBI environment configuration [quick]
├── Task 2: PubMed cache layer [quick]
└── Task 3: LLM prompt templates for PubMed [deep]

Wave 2 (After Wave 1 - core skill):
└── Task 4: PubMed Search Skill implementation [unspecified-high, depends: 1,2,3]

Wave 3 (After Wave 2 - verification + tests, 2 parallel):
├── Task 5: Skill integration verification [quick, depends: 4]
└── Task 6: Unit + integration tests [unspecified-low, depends: 4]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 3 → Task 4 → Task 5 → F1-F4 → user okay
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | - | 4 | 1 |
| 2 | - | 4 | 1 |
| 3 | - | 4 | 1 |
| 4 | 1, 2, 3 | 5, 6 | 2 |
| 5 | 4 | F1-F4 | 3 |
| 6 | 4 | F1-F4 | 3 |
| F1-F4 | 5, 6 | user okay | FINAL |

### Agent Dispatch Summary

- **Wave 1**: 3 — T1 `quick`, T2 `quick`, T3 `deep`
- **Wave 2**: 1 — T4 `unspecified-high`
- **Wave 3**: 2 — T5 `quick`, T6 `unspecified-low`
- **FINAL**: 4 — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [ ] 1. NCBI 环境变量配置

  **What to do**:
  - 在 `backend/.env.example` 末尾添加 `NCBI_EMAIL` 和 `NCBI_API_KEY` 配置项（带注释说明用途和获取方式）
  - 在 `backend/.env` 中添加实际值（如果存在）；如果不存在则添加占位符和注释
  - 验证 `PubMedService.__init__` 已正确读取 `os.getenv("NCBI_EMAIL")` 和 `os.getenv("NCBI_API_KEY")`（无需修改代码，仅确认）
  - 创建 `backend/services/skills/prompts/` 目录（为 Task 3 准备，确保目录存在）
  - 创建 `backend/services/skills/prompts/__init__.py` 空文件

  **Must NOT do**:
  - 不硬编码任何 NCBI 凭证到代码中
  - 不修改 `pubmed_service.py` 中的环境变量读取逻辑
  - 不在 `.env.example` 中放入真实 API key

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 仅修改配置文件和创建目录，代码变更量极小
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - 无相关 skill 需要加载

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Task 4
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `backend/.env.example:1-29` — 现有环境变量配置格式（key=value + 注释风格），新配置项应遵循此格式
  - `backend/services/pubmed_service.py:99-100` — PubMedService 读取环境变量方式：`os.getenv("NCBI_EMAIL", "")` 和 `os.getenv("NCBI_API_KEY", "")`

  **API/Type References**:
  - `backend/services/pubmed_service.py:RATE_LIMIT_NO_KEY=3` 和 `RATE_LIMIT_WITH_KEY=10` — 无 key 3次/秒，有 key 10次/秒，注释中应说明此差异

  **WHY Each Reference Matters**:
  - `.env.example` 格式：确保新配置项与现有格式一致（注释 + key=value）
  - PubMedService 环境变量读取：确认不需要修改代码，仅添加配置项即可

  **Acceptance Criteria**:

  - [ ] `backend/.env.example` 包含 `NCBI_EMAIL` 和 `NCBI_API_KEY` 配置项及中文注释
  - [ ] `backend/services/skills/prompts/` 目录及 `__init__.py` 存在
  - [ ] `python -c "import os; os.getenv('NCBI_EMAIL')"` 不报错

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 环境变量配置正确
    Tool: Bash
    Preconditions: backend/.env.example 文件存在
    Steps:
      1. grep "NCBI_EMAIL" backend/.env.example — 验证存在
      2. grep "NCBI_API_KEY" backend/.env.example — 验证存在
      3. grep -c "NCBI" backend/.env.example — 计数应为 2 或更多（含注释行）
    Expected Result: 两个环境变量均存在且有注释说明
    Failure Indicators: grep 返回空或计数少于 2
    Evidence: .sisyphus/evidence/task-1-env-config.txt

  Scenario: prompts 目录就绪
    Tool: Bash
    Preconditions: 无
    Steps:
      1. ls backend/services/skills/prompts/__init__.py
    Expected Result: 文件存在
    Failure Indicators: 文件不存在
    Evidence: .sisyphus/evidence/task-1-prompts-dir.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(pubmed): add NCBI environment configuration and prompts directory`
  - Files: `backend/.env.example`, `backend/services/skills/prompts/__init__.py`
  - Pre-commit: 无

- [ ] 2. PubMed 缓存层

  **What to do**:
  - 创建 `backend/services/pubmed_cache.py`，实现基于文件系统的 PubMed 查询结果缓存
  - 缓存 key: 对查询参数（query + max_results + sort）做 MD5 hash
  - 缓存 value: JSON 序列化的 PubMedSearchResult（articles 列表 + total_count + query_used）
  - 缓存存储位置: `backend/.pubmed_cache/` 目录
  - 缓存 TTL: 默认 24 小时（86400 秒），通过 `cache_ttl` 参数可配置
  - 主要方法:
    - `get(query, max_results, sort) -> Optional[PubMedSearchResult]` — 获取缓存
    - `set(query, max_results, sort, result: PubMedSearchResult)` — 写入缓存
    - `clear()` — 清除所有缓存
    - `_make_key(query, max_results, sort) -> str` — 生成缓存 key
    - `_is_expired(cache_file_path) -> bool` — 检查是否过期
  - 缓存命中时记录日志: `logger.info(f"PubMed cache hit: query='{query[:50]}'")`
  - 缓存目录不存在时自动创建

  **Must NOT do**:
  - 不使用数据库存储缓存（文件系统即可）
  - 不修改 `pubmed_service.py`
  - 不在缓存中存储 NCBI API key 或敏感信息

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 独立模块，逻辑简单（文件读写 + TTL 检查），约 80-120 行代码
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - 无相关 skill

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 4
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `backend/services/pubmed_service.py:56-78` — `PubMedArticle` 和 `PubMedSearchResult` dataclass 定义，缓存需要序列化/反序列化这两个类型

  **API/Type References**:
  - `backend/services/pubmed_service.py:PubMedArticle` — 缓存需存储的字段: pmid, title, authors, journal, year, abstract, url, doi
  - `backend/services/pubmed_service.py:PubMedSearchResult` — 缓存需存储的字段: articles, total_count, query_used

  **WHY Each Reference Matters**:
  - PubMedArticle/SearchResult 结构：缓存 JSON 的序列化/反序列化需与这些 dataclass 匹配，确保 skill 能直接使用反序列化后的对象

  **Acceptance Criteria**:

  - [ ] `backend/services/pubmed_cache.py` 文件存在
  - [ ] `PubMedCache` 类实现 `get()`, `set()`, `clear()` 方法
  - [ ] 缓存文件存储在 `backend/.pubmed_cache/` 目录
  - [ ] TTL 过期后 `get()` 返回 None
  - [ ] `python -c "from services.pubmed_cache import PubMedCache; print('OK')"` 输出 OK

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 缓存写入和读取正常
    Tool: Bash (python)
    Preconditions: backend/ 目录可写
    Steps:
      1. cd backend && python -c "
         from services.pubmed_cache import PubMedCache
         from services.pubmed_service import PubMedArticle, PubMedSearchResult
         cache = PubMedCache()
         result = PubMedSearchResult(
             articles=[PubMedArticle(pmid='12345', title='Test', abstract='Test abstract')],
             total_count=1, query_used='test query'
         )
         cache.set('test query', 100, 'relevance', result)
         cached = cache.get('test query', 100, 'relevance')
         assert cached is not None, 'Cache miss'
         assert cached.total_count == 1, 'Wrong count'
         assert cached.articles[0].pmid == '12345', 'Wrong PMID'
         cache.clear()
         print('PASS')
         "
    Expected Result: 输出 "PASS"
    Failure Indicators: AssertionError 或 ImportError
    Evidence: .sisyphus/evidence/task-2-cache-rw.txt

  Scenario: 缓存 TTL 过期返回 None
    Tool: Bash (python)
    Preconditions: backend/ 目录可写
    Steps:
      1. cd backend && python -c "
         from services.pubmed_cache import PubMedCache
         from services.pubmed_service import PubMedSearchResult
         cache = PubMedCache(cache_ttl=0)  # TTL=0 立即过期
         result = PubMedSearchResult(articles=[], total_count=0, query_used='test')
         cache.set('test', 100, 'relevance', result)
         cached = cache.get('test', 100, 'relevance')
         assert cached is None, f'Expected None, got {cached}'
         cache.clear()
         print('PASS')
         "
    Expected Result: 输出 "PASS"
    Failure Indicators: AssertionError
    Evidence: .sisyphus/evidence/task-2-cache-ttl.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(pubmed): add NCBI environment configuration and cache layer`
  - Files: `backend/services/pubmed_cache.py`, `backend/.env.example`, `backend/services/skills/prompts/__init__.py`
  - Pre-commit: 无

- [ ] 3. LLM Prompt 模板 — PubMed 查询分解与回答合成

  **What to do**:
  - 创建 `backend/services/skills/prompts/pubmed_prompts.py`，包含两个核心 prompt 模板：

  **1) `QUERY_DECOMPOSITION_PROMPT`** — 查询分解 prompt:
  - 输入: 用户原始问题（可能是中文）
  - 输出: JSON 格式的 PubMed 搜索查询，包含:
    - `mesh_terms`: MeSH 术语列表（英文）
    - `keywords`: 关键词列表（英文）
    - `pubmed_query`: 组合后的 PubMed 搜索字符串（使用 AND/OR/NOT 和字段标签 [mesh], [tiab], [majr]）
    - `search_strategy`: 搜索策略说明（简短）
  - Prompt 要求 LLM:
    - 将中文医学术语翻译为英文 MeSH 术语
    - 使用 MeSH 词汇表标准术语（如 "Neoplasms" 而非 "Cancer"）
    - 同时包含 MeSH 和关键词搜索（覆盖 ~5M 无 MeSH 索引的记录）
    - 合理使用布尔运算符：OR 用于同义词，AND 用于概念交叉
    - 返回严格的 JSON 格式（便于代码解析）

  **2) `ANSWER_SYNTHESIS_PROMPT`** — 回答合成 prompt:
  - 输入: 用户原始问题 + 100 篇 PubMed abstract（带 PMID 标注）
  - 输出: 引用式中文回答
  - Prompt 要求 LLM:
    - 每条事实声明必须附 [PMID: xxxxxxxx] 引用
    - 优先引用高质量证据（RCT、Meta-analysis、大样本研究）
    - 明确标注证据不足或存在争议的领域
    - 区分已达成共识和仍在研究中的发现
    - 回答使用中文，PMID 和术语保留英文
    - 如无直接相关文献，明确说明
    - 在回答末尾列出所有引用文献的完整信息（标题、作者、期刊、年份、PMID）

  **3) `PROMPT_RESPONSE_PARSING`** — 响应解析辅助:
  - `parse_decomposition_response(llm_response: str) -> dict` — 解析查询分解的 JSON 响应
  - 处理 JSON 解析失败的情况（尝试提取 JSON 块或返回默认查询）
  - `build_abstract_context(articles: List[PubMedArticle]) -> str` — 将 100 篇 abstract 格式化为 LLM 可读的上下文文本

  **Must NOT do**:
  - 不在 prompt 中硬编码任何 API key 或凭证
  - 不使用 LangChain 或其他框架的 prompt 模板系统（直接用 Python 字符串）
  - 不在 prompt 中指定具体模型名称

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Prompt 工程需要深度思考和迭代优化，直接影响最终回答质量
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - 无相关 skill

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 4
  - **Blocked By**: Task 1 (需要 prompts 目录存在)

  **References**:

  **Pattern References**:
  - `backend/services/rag_service.py:257-280` — `_generate_answer()` 中的 prompt 构建和 LLM 调用模式，新 prompt 应遵循类似的系统提示风格
  - `backend/services/skills/literature_skill.py:82-96` — `_format_results()` 结果格式化模式

  **API/Type References**:
  - `backend/services/pubmed_service.py:PubMedArticle` — abstract 格式化需包含: PMID, title, authors, journal, year, abstract
  - `backend/services/llm_client.py:LLMClient.chat()` — LLM 调用接口，messages 参数格式: `[{"role": "system", "content": ...}, {"role": "user", "content": ...}]`

  **External References**:
  - PubMed MeSH 浏览器: https://meshb.nlm.nih.gov/ — MeSH 术语标准
  - NCBI E-utilities 字段标签: [mesh], [tiab], [majr] — 搜索字段标签用法

  **WHY Each Reference Matters**:
  - RAGService prompt 模式：确保新 prompt 与现有系统风格一致（中文系统提示 + 用户消息）
  - PubMedArticle 结构：abstract 格式化需要包含哪些字段
  - LLMClient 接口：确保 prompt 输出格式与 LLM 调用方式兼容

  **Acceptance Criteria**:

  - [ ] `backend/services/skills/prompts/pubmed_prompts.py` 文件存在
  - [ ] `QUERY_DECOMPOSITION_PROMPT` 常量存在且包含 MeSH 和关键词搜索指令
  - [ ] `ANSWER_SYNTHESIS_PROMPT` 常量存在且包含 PMID 引用指令
  - [ ] `parse_decomposition_response()` 函数存在且能解析 JSON 响应
  - [ ] `build_abstract_context()` 函数存在且能格式化 PubMedArticle 列表
  - [ ] `python -c "from services.skills.prompts.pubmed_prompts import QUERY_DECOMPOSITION_PROMPT, ANSWER_SYNTHESIS_PROMPT; print('OK')"` 输出 OK

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Prompt 模板正确加载
    Tool: Bash (python)
    Preconditions: backend/ 目录
    Steps:
      1. cd backend && python -c "
         from services.skills.prompts.pubmed_prompts import (
             QUERY_DECOMPOSITION_PROMPT, ANSWER_SYNTHESIS_PROMPT,
             parse_decomposition_response, build_abstract_context
         )
         assert len(QUERY_DECOMPOSITION_PROMPT) > 100, 'Query prompt too short'
         assert len(ANSWER_SYNTHESIS_PROMPT) > 100, 'Answer prompt too short'
         assert 'MeSH' in QUERY_DECOMPOSITION_PROMPT or 'mesh' in QUERY_DECOMPOSITION_PROMPT, 'No MeSH in query prompt'
         assert 'PMID' in ANSWER_SYNTHESIS_PROMPT, 'No PMID in answer prompt'
         print('PASS')
         "
    Expected Result: 输出 "PASS"
    Failure Indicators: ImportError, AssertionError
    Evidence: .sisyphus/evidence/task-3-prompts-load.txt

  Scenario: 查询分解响应解析正确
    Tool: Bash (python)
    Preconditions: 无
    Steps:
      1. cd backend && python -c "
         from services.skills.prompts.pubmed_prompts import parse_decomposition_response
         # 正常 JSON
         result = parse_decomposition_response('{\"mesh_terms\": [\"Neoplasms\"], \"keywords\": [\"cancer\"], \"pubmed_query\": \"Neoplasms[mesh] OR cancer[tiab]\", \"search_strategy\": \"test\"}')
         assert 'pubmed_query' in result, 'Missing pubmed_query'
         assert result['pubmed_query'] == 'Neoplasms[mesh] OR cancer[tiab]', f'Wrong query: {result[\"pubmed_query\"]}'
         # 异常输入 - 返回默认查询
         fallback = parse_decomposition_response('this is not json at all')
         assert 'pubmed_query' in fallback, 'Fallback missing pubmed_query'
         print('PASS')
         "
    Expected Result: 输出 "PASS"
    Failure Indicators: AssertionError, JSONDecodeError
    Evidence: .sisyphus/evidence/task-3-parsing.txt

  Scenario: Abstract 上下文格式化正确
    Tool: Bash (python)
    Preconditions: 无
    Steps:
      1. cd backend && python -c "
         from services.skills.prompts.pubmed_prompts import build_abstract_context
         from services.pubmed_service import PubMedArticle
         articles = [
             PubMedArticle(pmid='12345', title='Test Article', authors=['Smith J'], journal='Nature', year='2024', abstract='This is a test abstract.', doi='10.1234/test'),
             PubMedArticle(pmid='67890', title='Another Article', authors=['Lee K'], journal='Science', year='2023', abstract='Another abstract.', doi='10.5678/another'),
         ]
         context = build_abstract_context(articles)
         assert '12345' in context, 'Missing PMID 12345'
         assert 'Test Article' in context, 'Missing title'
         assert 'Nature' in context, 'Missing journal'
         print('PASS')
         "
    Expected Result: 输出 "PASS"
    Failure Indicators: AssertionError
    Evidence: .sisyphus/evidence/task-3-format.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `feat(pubmed): add NCBI config, cache layer, and LLM prompt templates`
  - Files: `backend/services/skills/prompts/pubmed_prompts.py`, `backend/services/skills/prompts/__init__.py`, `backend/services/pubmed_cache.py`, `backend/.env.example`
  - Pre-commit: `cd backend && python -c "from services.skills.prompts.pubmed_prompts import QUERY_DECOMPOSITION_PROMPT; print('OK')"`

- [ ] 4. PubMed Search Skill 实现

  **What to do**:
  - 创建 `backend/services/skills/pubmed_search_skill.py`，实现 `PubMedSearchSkill` 类继承 `Skill` ABC

  **Skill 元数据**:
  - `name = "pubmed_search"`
  - `description = "PubMed 文献检索 - 搜索 MEDLINE 数据库获取罕见病遗传诊断相关文献摘要，生成循证回答"`
  - `skill_type = "tool_call"`
  - `icon = "search"`
  - `input_schema = {"query": "str - 搜索关键词或医学问题（支持中文）", "max_results": "int - 最大检索数量（默认100）"}`

  **`execute(context: SkillContext) -> SkillResult` 核心流程**:
  1. **NCBI 凭证检查**: 从环境变量读取 `NCBI_EMAIL`，缺失时返回 `SkillResult(content="⚠️ PubMed 检索需要配置 NCBI 邮箱...", confidence=0.0)`
  2. **缓存查询**: 使用 `PubMedCache.get()` 检查缓存
  3. **LLM 查询分解**:
     - 使用 `context.llm_client.chat()` 调用 LLM
     - Prompt: `QUERY_DECOMPOSITION_PROMPT`
     - 解析响应: `parse_decomposition_response()`
     - 如果 `context.llm_client` 为 None，回退到直接使用用户原始查询
  4. **PubMed 搜索**:
     - 使用 `PubMedService.search_and_fetch(query, max_results=100, include_abstracts=True)`
     - 将结果写入缓存 `PubMedCache.set()`
  5. **LLM 回答合成**:
     - 使用 `build_abstract_context()` 格式化 100 篇 abstract
     - 使用 `context.llm_client.chat()` 调用 LLM
     - Prompt: `ANSWER_SYNTHESIS_PROMPT`
     - 如果 `context.llm_client` 为 None，直接返回 abstract 列表
  6. **返回结果**:
     - `content`: LLM 生成的引用式回答
     - `references`: `ChatReference` 列表（reference_id=PMID, reference_type="pubmed", label=文章标题[:50], url=PubMed URL）
     - `confidence`: 基于检索结果数量的置信度（0.3-0.9）
     - `metadata`: {"skill": "pubmed_search", "query_used": PubMed查询, "total_results": 总数, "articles_fetched": 实际获取数, "from_cache": bool}

  **错误处理**:
  - `PubMedServiceError` / `PubMedSearchError`: 返回 SkillResult 含错误提示 + 引导用户重试
  - `PubMedRateLimitError`: 返回 SkillResult 含速率限制提示 + 建议配置 API key
  - LLM 调用失败: 回退到直接返回 PubMed abstract 列表（不合成回答）
  - PubMed 返回 0 结果: 返回 SkillResult 含"未找到相关文献"提示 + 建议修改查询词
  - 网络超时: PubMedService 已有重试逻辑，此处捕获最终异常

  **Must NOT do**:
  - 不修改 `pubmed_service.py` 核心逻辑
  - 不修改 `skill_base.py` 接口
  - 不修改 `rag_service.py` 中的 skill 执行逻辑
  - 不硬编码 NCBI 凭证
  - 不在 execute 中做 token 计算/截断（用户选择 100 篇全量）
  - 不使用 LangChain 或其他框架

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 核心功能实现，涉及多模块集成（PubMedService + PubMedCache + LLMClient + prompt 模板），逻辑复杂度高
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - 无相关 skill

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential, sole task)
  - **Blocks**: Tasks 5, 6
  - **Blocked By**: Tasks 1, 2, 3

  **References**:

  **Pattern References** (existing code to follow):
  - `backend/services/skills/literature_skill.py:1-106` — **完整 Skill 实现参考**：继承 Skill ABC、execute() 模式、SkillResult 构建、ChatReference 构建、错误处理模式。新 skill 应严格遵循此模式。
  - `backend/services/rag_service.py:510-553` — `_execute_skill_stream()` — tool_call 类型 skill 的执行流程：创建 SkillContext → 调用 skill.execute(context) → 返回 skill_result。理解 SkillContext 中 llm_client 如何传入。

  **API/Type References** (contracts to implement against):
  - `backend/services/skill_base.py:18-35` — SkillContext 字段: query, patient_id, db_session, llm_client, case_context
  - `backend/services/skill_base.py:37-52` — Skill ABC 接口: name, description, skill_type, icon, input_schema, execute()
  - `backend/services/skill_base.py:28-34` — SkillResult 字段: content, references, confidence, metadata
  - `backend/services/rag_service.py:31-36` — ChatReference 字段: reference_id, reference_type, label, url
  - `backend/services/pubmed_service.py:389-442` — `search_and_fetch()` 接口: query, max_results, sort, include_abstracts
  - `backend/services/llm_client.py:30-59` — LLMClient.chat() 接口: messages, temperature, max_tokens

  **WHY Each Reference Matters**:
  - `literature_skill.py`: 最直接的实现参考，新 skill 应遵循相同的类结构和返回模式
  - `_execute_skill_stream()`: 理解 skill 在 WebSocket 流中的调用方式，确保返回格式兼容
  - `SkillContext/SkillResult/ChatReference`: 这些是 skill 系统的接口契约，必须严格匹配
  - `search_and_fetch()`: PubMed 检索的入口方法，需正确传递参数
  - `LLMClient.chat()`: LLM 调用的接口，需正确构建 messages 列表

  **Acceptance Criteria**:

  - [ ] `backend/services/skills/pubmed_search_skill.py` 文件存在
  - [ ] `PubMedSearchSkill` 类继承 `Skill`，定义了 name, description, skill_type, icon, input_schema
  - [ ] `execute()` 方法实现了完整的查询分解→PubMed 检索→回答合成流程
  - [ ] 缓存命中时跳过 NCBI API 调用
  - [ ] NCBI 凭证缺失时返回清晰错误提示
  - [ ] LLM 不可用时回退到直接返回 abstract 列表
  - [ ] PubMed 返回 0 结果时返回适当提示
  - [ ] Skill 自动注册: `python -c "from services.skill_base import create_skill_registry; r = create_skill_registry(); assert 'pubmed_search' in [s.name for s in r.list()]"`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Skill 自动注册到 registry
    Tool: Bash (python)
    Preconditions: 所有依赖文件已创建
    Steps:
      1. cd backend && python -c "
         from services.skill_base import create_skill_registry
         r = create_skill_registry()
         names = [s.name for s in r.list()]
         assert 'pubmed_search' in names, f'pubmed_search not in {names}'
         skill = r.get('pubmed_search')
         assert skill.skill_type == 'tool_call', f'Wrong type: {skill.skill_type}'
         print('PASS')
         "
    Expected Result: 输出 "PASS"
    Failure Indicators: AssertionError
    Evidence: .sisyphus/evidence/task-4-skill-registry.txt

  Scenario: NCBI 凭证缺失时返回错误提示
    Tool: Bash (python)
    Preconditions: NCBI_EMAIL 环境变量未设置
    Steps:
      1. cd backend && python -c "
         import os
         os.environ.pop('NCBI_EMAIL', None)
         os.environ.pop('NCBI_API_KEY', None)
         from services.skill_base import SkillContext
         from services.skills.pubmed_search_skill import PubMedSearchSkill
         skill = PubMedSearchSkill()
         context = SkillContext(query='罕见病遗传诊断', patient_id=1, db_session=None, llm_client=None)
         result = skill.execute(context)
         assert result.confidence == 0.0, f'Expected 0.0, got {result.confidence}'
         assert 'NCBI' in result.content or '配置' in result.content or 'PubMed' in result.content, f'No config error hint: {result.content[:100]}'
         print('PASS')
         "
    Expected Result: 输出 "PASS"
    Failure Indicators: AssertionError 或实际发起了 API 调用
    Evidence: .sisyphus/evidence/task-4-no-ncbi-config.txt
  ```

  **Commit**: YES
  - Message: `feat(pubmed): implement PubMed RAG search skill`
  - Files: `backend/services/skills/pubmed_search_skill.py`
  - Pre-commit: `cd backend && python -c "from services.skill_base import create_skill_registry; r = create_skill_registry(); assert 'pubmed_search' in [s.name for s in r.list()]"`

- [ ] 5. Skill 集成验证与进度提示

  **What to do**:
  - 验证 `PubMedSearchSkill` 在完整 WebSocket 流程中正确工作
  - 验证 `GET /api/skills` 返回 `pubmed_search`
  - 在 `_execute_skill_stream` 的 `tool_call` 分支中，`skill.execute()` 前添加进度消息 yield
  - 进度消息格式: `{"type": "skill_progress", "content": "正在检索 PubMed 文献...", "skill_name": skill_name}`
  - 验证 PubMed skill 长时间执行不会导致 WebSocket 超时

  **Must NOT do**:
  - 不修改 `skill_base.py` 接口
  - 不修改前端代码
  - 不修改 `PubMedService`

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 仅验证集成和添加一行进度提示
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 6)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 4

  **References**:
  - `backend/services/rag_service.py:537-553` — `_execute_skill_stream()` tool_call 分支，进度消息插入点
  - `backend/api/skills.py:51-69` — `/api/skills` 端点

  **Acceptance Criteria**:
  - [ ] `GET /api/skills` 返回包含 `pubmed_search`
  - [ ] `_execute_skill_stream` yield 进度消息
  - [ ] 进度消息含 `skill_progress` type

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 进度消息存在
    Tool: Bash (python)
    Steps:
      1. cd backend && python -c "
         import inspect
         from services.rag_service import RAGService
         source = inspect.getsource(RAGService._execute_skill_stream)
         assert 'skill_progress' in source, 'No progress message'
         print('PASS')
         "
    Expected Result: PASS
    Evidence: .sisyphus/evidence/task-5-progress.txt
  ```

  **Commit**: YES
  - Message: `feat(pubmed): add skill execution progress message`
  - Files: `backend/services/rag_service.py`

- [ ] 6. 单元测试与集成测试

  **What to do**:
  - 创建 `tests/test_pubmed_search_skill.py`:
    - `test_skill_metadata` — name, description, skill_type, icon
    - `test_missing_ncbi_config` — 无凭证时错误提示
    - `test_missing_llm_client` — 无 LLM 时回退逻辑
    - `test_no_pubmed_results` — 0 结果处理
    - `test_cache_hit` — 缓存命中跳过 API
    - `test_execute_full_flow` — Mock 完整流程
    - `test_build_references` — ChatReference 构建
  - 创建 `tests/test_pubmed_integration.py`:
    - `TestPubMedCache.test_cache_roundtrip` — 缓存读写
    - `TestPubMedCache.test_cache_expiration` — TTL 过期
    - `TestPubMedCache.test_cache_clear` — 清除缓存
    - `TestPubMedPrompts.test_query_decomposition_prompt` — prompt 指令验证
    - `TestPubMedPrompts.test_answer_synthesis_prompt` — PMID 引用指令
    - `TestPubMedPrompts.test_parse_decomposition_response` — JSON 解析 + fallback
    - `TestPubMedPrompts.test_build_abstract_context` — abstract 格式化

  **Mock 策略**: `unittest.mock.patch` mock LLMClient.chat() 和 PubMedService.search_and_fetch()

  **Must NOT do**:
  - 不调用真实 NCBI API（使用 mock）
  - 不调用真实 LLM API（使用 mock）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: 测试逻辑明确，编写测试用例
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 5)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 4

  **References**:
  - `backend/services/skills/literature_skill.py:1-106` — 被测 skill 模式
  - `backend/services/pubmed_cache.py` — 被测缓存模块
  - `backend/services/skills/prompts/pubmed_prompts.py` — 被测 prompt 模块

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_pubmed_search_skill.py -v` → ALL PASS
  - [ ] `pytest tests/test_pubmed_integration.py -v` → ALL PASS

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 所有测试通过
    Tool: Bash (pytest)
    Steps:
      1. cd backend && pytest tests/test_pubmed_search_skill.py tests/test_pubmed_integration.py -v
    Expected Result: ALL PASS, 0 failures
    Evidence: .sisyphus/evidence/task-6-test-results.txt
  ```

  **Commit**: YES
  - Message: `test(pubmed): add unit and integration tests for PubMed RAG skill`
  - Files: `tests/test_pubmed_search_skill.py`, `tests/test_pubmed_integration.py`
  - Pre-commit: `pytest tests/test_pubmed_search_skill.py tests/test_pubmed_integration.py -v`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `pytest` + check Python linting. Review all changed files for: bare except, print() in prod, commented-out code, unused imports, hardcoded credentials. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Tests [N pass/N fail] | Lint [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration. Test edge cases: missing NCBI config, empty PubMed results, Chinese queries, MeSH terms. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(pubmed): add NCBI config and cache layer` — .env.example, pubmed_cache.py, pubmed_prompts.py
- **Wave 2**: `feat(pubmed): implement PubMed RAG search skill` — pubmed_search_skill.py
- **Wave 3**: `test(pubmed): add unit and integration tests` — test files
- Pre-commit: `pytest tests/ -x`

---

## Success Criteria

### Verification Commands
```bash
# Skill auto-registers
cd backend && python -c "from services.skill_base import create_skill_registry; r = create_skill_registry(); print([s.name for s in r.list()])"  # Expected: [..., 'pubmed_search', ...]

# Tests pass
pytest tests/test_pubmed_search_skill.py tests/test_pubmed_integration.py -v  # Expected: all PASS

# Cache layer works
python -c "from services.pubmed_cache import PubMedCache; c = PubMedCache(); print('Cache OK')"  # Expected: Cache OK

# Prompt templates load
python -c "from services.skills.prompts.pubmed_prompts import QUERY_DECOMPOSITION_PROMPT, ANSWER_SYNTHESIS_PROMPT; print('Prompts OK')"  # Expected: Prompts OK
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] Skill appears in `/api/skills` endpoint
- [ ] WebSocket streaming works with pubmed_search skill
- [ ] Chinese queries produce Chinese answers with English PMID references
- [ ] Cache reduces repeat API calls
- [ ] Missing NCBI config produces clear error message
