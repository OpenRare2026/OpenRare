# 修复 VEPCSVParser 空结果 Bug + 大数据性能优化

## TL;DR

> **快速总结**: 修复 VEPCSVParser._map_row() 的参数传递和类型不匹配缺陷（导致所有字段返回空值/None），同时将字段查找从 O(n) 线性扫描优化为 O(1) 直接查找，解决大数据量时处理极慢的问题。
> 
> **交付物**:
> - VEPCSVParser 所有字段正确提取（9个失败测试全部通过）
> - 大数据解析性能从 O(columns × fields × rows) 提升到 O(fields × rows)
> - _map_row() 签名与 parse() 调用一致
> 
> **预估工作量**: Quick（2 个文件，聚焦 bug 修复）
> **并行执行**: YES - 2 waves
> **关键路径**: Task 1 → Task 2/3 → F1-F4

---

## Context

### Original Request
用户报告 VEPCSVParser 对 CSV 处理的结果好多都是空的，同时 vep_service.py 处理大结果时很慢。

### Interview Summary
**Key Discussions**:
- VEPCSVParser 输出大量空值：确认是 _map_row() 的参数和类型 bug
- 大数据性能问题：根因是 _map_row() 内部的 O(n) 线性查找
- 用户确认关键场景是结果量很大时的处理速度

**Research Findings**:
- 运行测试：9/10 VEPCSVParser 测试 FAIL，全部因 `TypeError: takes 3 to 4 positional arguments but 5 were given`
- 代码根因：`parse()` 重构了 `field_to_cols` 为 `Dict[str, List[str]]`，但 `_map_row()` 未同步更新
- 这是一次不完整的重构导致的回归 bug

### Metis Review (Self-performed)
**Identified Gaps** (addressed):
- 需确保 extra_field_to_keys 也在 _map_row 中正确使用（当前未传入）
- 需确保 _map_row 的 get_with_extra() 也从 O(n) 优化到 O(1)
- 测试覆盖：现有 10 个测试用例已覆盖主要场景，额外需确认大数据量性能

---

## Work Objectives

### Core Objective
修复 VEPCSVParser 的字段提取 bug（空结果）并将 _map_row 的字段查找从 O(n) 优化到 O(1)，使大数据量 VEP 结果处理不再阻塞。

### Concrete Deliverables
- `backend/services/vep_csv_parser.py` — 修复 _map_row() 签名 + 优化 get()/get_with_extra()
- `backend/tests/test_vep_csv_parser.py` — 所有现有测试通过

### Definition of Done
- [ ] `pytest tests/test_vep_csv_parser.py` 全部 PASS (当前 9/10 FAIL)
- [ ] 解析结果中所有字段（gene, consequence, impact, hgvs_c 等）均非空（当 CSV 中有数据时）

### Must Have
- _map_row() 签名与 parse() 的调用参数完全匹配
- get() 函数使用 field_to_cols (Dict[str, List[str]]) 进行 O(1) 查找
- get_with_extra() 使用 extra_field_to_keys 进行 O(1) 查找
- 所有现有测试通过
- vep_service.py 中 parse() 调用无需改动（parser 的公共接口 parse(csv_content) 不变）

### Must NOT Have (Guardrails)
- 不改动 parse() 方法的公共签名
- 不改动 VEPAnnotatedVariant dataclass 定义
- 不改动 COLUMN_ALIASES / EXTRA_KEY_ALIASES 映射表
- 不改动 vep_service.py 的 poll_job / get_result / process_vcf 逻辑
- 不引入新的外部依赖
- 不做流式解析重构（超出当前 bug 修复范围）

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: Tests-after (existing tests verify correctness)
- **Framework**: pytest

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Library/Module**: Use Bash (pytest + python REPL) - Run tests, import module, call functions, compare output

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — core bug fix, single task):
└── Task 1: Fix _map_row() signature, get(), and get_with_extra() [quick]

Wave 2 (After Wave 1 — verification + performance):
├── Task 2: Run existing tests and verify all PASS [quick]
└── Task 3: Add performance benchmark test for large CSV [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── F1: Plan compliance audit (oracle)
├── F2: Code quality review (unspecified-high)
├── F3: Real manual QA (unspecified-high)
└── F4: Scope fidelity check (deep)
→ Present results → Get explicit user okay
```

### Dependency Matrix
- **1**: None → blocks 2, 3
- **2**: 1 → blocks F1-F4
- **3**: 1 → blocks F1-F4
- **F1-F4**: 2, 3 → user okay

### Agent Dispatch Summary
- **Wave 1**: 1 task — T1 `quick`
- **Wave 2**: 2 tasks — T2 `quick`, T3 `quick`
- **FINAL**: 4 tasks — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [ ] 1. 修复 _map_row() 签名、get() 和 get_with_extra() 函数

  **What to do**:
  - 更新 `_map_row()` 方法签名，添加 `extra_field_to_keys: Dict[str, List[str]]` 参数：
    ```python
    def _map_row(
        self,
        norm_row: Dict[str, str],
        field_to_cols: Dict[str, List[str]],
        extra_field_to_keys: Dict[str, List[str]],
        extra_fields: Optional[Dict[str, str]] = None,
    ) -> VEPAnnotatedVariant:
    ```
  - 重写 `get()` 函数，利用 `field_to_cols` 进行 O(1) 直接查找（替代当前 O(n) 线性扫描）：
    ```python
    def get(field_name: str) -> Optional[str]:
        cols = field_to_cols.get(field_name, [])
        for col in cols:
            if col in norm_row:
                val = norm_row[col]
                if val:
                    return val
        return None
    ```
  - 重写 `get_with_extra()` 函数，利用 `extra_field_to_keys` 进行 O(1) 查找（替代对全局 `EXTRA_KEY_ALIASES` 的线性扫描）：
    ```python
    def get_with_extra(field_name: str) -> Optional[str]:
        val = get(field_name)
        if val:
            return val
        keys = extra_field_to_keys.get(field_name, [])
        for ek in keys:
            if ek in extra_fields:
                return extra_fields[ek]
        return None
    ```
  - 保持 `parse()` 第 260 行的调用不变（`self._map_row(norm_row, field_to_cols, extra_field_to_keys, extra_fields)` 已经传了 4 个参数，只需签名匹配）

  **Must NOT do**:
  - 不改动 parse() 方法内部的逻辑
  - 不改动 field_to_cols / extra_field_to_keys 的构建方式
  - 不删除 EXTRA_KEY_ALIASES 全局变量（parse() 仍用它构建 extra_field_to_keys）
  - 不改变 extra_fields 的解析逻辑
  - 不引入新依赖

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单函数签名修复 + 两个内部闭包重写，逻辑清晰且范围明确
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 1 是关键路径，单任务)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 2, 3
  - **Blocked By**: None

  **References**:

  **Pattern References** (existing code to follow):
  - `backend/services/vep_csv_parser.py:281-360` — 当前 _map_row() 完整实现，包含 get() 和 get_with_extra() 的所有逻辑
  - `backend/services/vep_csv_parser.py:220-260` — parse() 中 field_to_cols 和 extra_field_to_keys 的构建逻辑和调用方式

  **API/Type References** (contracts to implement against):
  - `backend/services/vep_csv_parser.py:17-71` — COLUMN_ALIASES 映射表，理解 field_to_cols 的值结构 `{target_field: [norm_col1, norm_col2, ...]}`
  - `backend/services/vep_csv_parser.py:74-102` — EXTRA_KEY_ALIASES 映射表，理解 extra_field_to_keys 的值结构
  - `backend/services/vep_csv_parser.py:106-138` — VEPAnnotatedVariant dataclass，所有需要映射的字段名

  **WHY Each Reference Matters**:
  - _map_row() 是唯一需要修改的函数，必须完整理解其当前 get() 和 get_with_extra() 的所有用法（约 20 个字段查找调用）
  - field_to_cols 的结构为 `{target_field: [norm_col1, norm_col2, ...]}`，get() 需按此结构查找
  - VEPAnnotatedVariant 的字段名（如 `gene`, `hgvs_c`, `clinvar_significance`）必须与 COLUMN_ALIASES 的值一致

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: _map_row() 正确提取直接列字段值（不再 TypeError）
    Tool: Bash (pytest)
    Preconditions: vep_csv_parser.py 已修改
    Steps:
      1. 运行 `cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python -m pytest tests/test_vep_csv_parser.py::TestVEPCSVParser::test_parse_default_format -v`
      2. 检查输出是否为 PASSED（不再报 TypeError）
      3. 验证 gene="GENE1", consequence="missense_variant", impact="MODERATE" 等字段不再为 None
    Expected Result: test_parse_default_format PASSED
    Failure Indicators: TypeError 或 AssertionError（字段值为 None）
    Evidence: .sisyphus/evidence/task-1-default-format-test.txt

  Scenario: _map_row() 基本解析不出错
    Tool: Bash (python -c)
    Preconditions: vep_csv_parser.py 已修改
    Steps:
      1. `cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python -c "from services.vep_csv_parser import VEPCSVParser; p = VEPCSVParser(); result = p.parse('Uploaded_variation,Location,Allele,Gene,Consequence,Impact\n1_12345_A_G,1:12345,G,BRCA1,missense_variant,MODERATE'); print(len(result), result[0].gene, result[0].consequence)"`
      2. 检查输出为 `1 BRCA1 missense_variant`（非空值）
    Expected Result: 输出 `1 BRCA1 missense_variant`
    Failure Indicators: TypeError 或 `None` 出现在输出中
    Evidence: .sisyphus/evidence/task-1-basic-parse.txt

  Scenario: Extra 列字段正确通过 get_with_extra() 提取
    Tool: Bash (pytest)
    Preconditions: vep_csv_parser.py 已修改
    Steps:
      1. 运行 `cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python -m pytest tests/test_vep_csv_parser.py::TestVEPCSVParser::test_parse_extra_column -v`
      2. 检查 PASSED，且 revel_score=0.85, cadd=25.3, spliceai_ds_max=0.02 等字段正确
    Expected Result: test_parse_extra_column PASSED
    Failure Indicators: AssertionError (字段值为 None)
    Evidence: .sisyphus/evidence/task-1-extra-column-test.txt

  Scenario: Empty extra 值被正确跳过
    Tool: Bash (pytest)
    Preconditions: vep_csv_parser.py 已修改
    Steps:
      1. 运行 `cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python -m pytest tests/test_vep_csv_parser.py::TestVEPCSVParser::test_parse_extra_column_empty_values_skipped -v`
      2. 检查 PASSED，空值的 extra 字段（revel_score=None, loftee_lof_flag=None, cadd=None）
    Expected Result: test_parse_extra_column_empty_values_skipped PASSED
    Failure Indicators: 非预期字段值
    Evidence: .sisyphus/evidence/task-1-empty-extra-test.txt
  ```

  **Commit**: YES
  - Message: `fix(vep): correct _map_row signature and optimize get()/get_with_extra() to O(1) lookup`
  - Files: `backend/services/vep_csv_parser.py`
  - Pre-commit: `cd backend && python -m pytest tests/test_vep_csv_parser.py -q`

- [ ] 2. 运行全部现有测试验证修复

  **What to do**:
  - 运行 `pytest tests/test_vep_csv_parser.py -v` 确认所有 26 个测试通过
  - 逐个验证之前失败的 9 个测试现在通过：
    - test_parse_default_format
    - test_parse_minimal_headers
    - test_parse_chr_prefix_location
    - test_parse_colon_format
    - test_parse_na_values_cleaned
    - test_parse_extra_column
    - test_parse_extra_column_empty_values_skipped
    - test_parse_clinvar_column_variants
  - 如果任何测试仍然失败，分析原因并修复
  - 运行完整测试套件确保无回归：`pytest tests/ -v --tb=short`

  **Must NOT do**:
  - 不修改测试代码来让测试通过
  - 不跳过任何失败的测试

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯验证任务，运行测试 + 检查结果
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 3)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `backend/tests/test_vep_csv_parser.py` — 完整测试文件，26 个测试用例

  **Why It Matters**: 这是验证 bug 修复是否正确的唯一标准

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 全部 parser 测试通过
    Tool: Bash (pytest)
    Preconditions: Task 1 已完成
    Steps:
      1. 运行 `cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python -m pytest tests/test_vep_csv_parser.py -v 2>&1`
      2. 检查所有 26 个测试项显示 PASSED
      3. 特别关注之前失败的 9 个测试
    Expected Result: 26 passed, 0 failed
    Failure Indicators: 任何 FAILED 项
    Evidence: .sisyphus/evidence/task-2-all-tests.txt

  Scenario: 无回归（完整测试套件）
    Tool: Bash (pytest)
    Preconditions: parser 测试已通过
    Steps:
      1. 运行 `cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python -m pytest tests/ -v --tb=short 2>&1`
      2. 检查无新失败
    Expected Result: 全部 PASSED
    Failure Indicators: 新的 FAILED 项
    Evidence: .sisyphus/evidence/task-2-regression.txt
  ```

  **Commit**: NO (verification only)

- [ ] 3. 添加大数据量性能基准测试

  **What to do**:
  - 在 `backend/tests/test_vep_csv_parser.py` 中添加性能基准测试类：
    - 生成 5000 行 VEP CSV 数据（模拟大数据量场景）
    - 测量 parse() 执行时间
    - 验证解析速度在合理范围内（5000 行 < 2 秒）
    - 验证所有行均被正确解析（非空 chromosome + position）
  - 使用 `time.time()` 或 `time.perf_counter()` 计时
  - 确保基准测试不影响其他测试

  **Must NOT do**:
  - 不添加外部性能测试依赖（如 pytest-benchmark）
  - 不修改生产代码来适应性能测试
  - 不设定过于严格的时间阈值（CI 环境性能波动）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 添加一个测试类，逻辑简单
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 2)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `backend/tests/test_vep_csv_parser.py:17-21` — VEP_DEFAULT_CSV 测试数据格式，生成大数据时参照此格式
  - `backend/tests/test_vep_csv_parser.py:115-170` — 现有 TestVEPCSVParser 类结构

  **WHY Each Reference Matters**:
  - 大数据测试需要与真实 VEP 输出格式一致
  - 保持与现有测试类相同的结构和风格

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: 大数据量解析性能达标
    Tool: Bash (pytest)
    Preconditions: Task 1 已完成
    Steps:
      1. 运行 `cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python -m pytest tests/test_vep_csv_parser.py -v -k performance 2>&1`
      2. 检查性能测试 PASSED
      3. 查看输出中的解析时间
    Expected Result: 5000 行 < 2s，所有行 chromosome 非空
    Failure Indicators: 性能测试 FAILED 或超时
    Evidence: .sisyphus/evidence/task-3-performance.txt

  Scenario: 大数据量解析结果完整性
    Tool: Bash (python -c)
    Preconditions: Task 1 已完成
    Steps:
      1. `cd /mnt/zzb/peixunban/hujie/hanjianbing/backend && python -c "
from services.vep_csv_parser import VEPCSVParser
header = 'Uploaded_variation,Location,Allele,Gene,Feature,Consequence,HGVSc,HGVSp,Impact,SIFT,PolyPhen,CADD_PHRED,gnomADe_AF,CLIN_SIG'
rows = [f'{i}_12345_A_G,{i}:12345,G,GENE{i},ENST{i},missense_variant,c.123A>G,p.Lys41Arg,MODERATE,deleterious(0.01),probably_damaging(0.95),25.3,0.00001,Uncertain_significance' for i in range(1, 5001)]
csv = header + '\n' + '\n'.join(rows)
p = VEPCSVParser()
result = p.parse(csv)
empty_chrom = sum(1 for v in result if not v.chromosome)
empty_gene = sum(1 for v in result if not v.gene)
print(f'Total: {len(result)}, Empty chromosome: {empty_chrom}, Empty gene: {empty_gene}')
"`
      2. 检查 Empty chromosome: 0, Empty gene: 0
    Expected Result: `Total: 5000, Empty chromosome: 0, Empty gene: 0`
    Failure Indicators: 任何空字段计数 > 0
    Evidence: .sisyphus/evidence/task-3-large-data.txt
  ```

  **Commit**: YES
  - Message: `test(vep): add performance benchmark for large CSV parsing`
  - Files: `backend/tests/test_vep_csv_parser.py`
  - Pre-commit: `cd backend && python -m pytest tests/test_vep_csv_parser.py -q`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run linter + `pytest`. Review changed files for: `as any`, empty catches, console.log, commented-out code, unused imports. Check AI slop indicators.
  Output: `Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Run ALL QA scenarios from ALL tasks. Test integration: parse a VEP CSV → verify all fields populated. Test edge cases: empty CSV, single row, large data. Save evidence.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec. Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Commit 1**: `fix(vep): correct _map_row signature and optimize get()/get_with_extra() to O(1) lookup` - `backend/services/vep_csv_parser.py` — after Task 1
  - Pre-commit: `cd backend && python -m pytest tests/test_vep_csv_parser.py -q`
- **Commit 2**: `test(vep): add performance benchmark for large CSV parsing` - `backend/tests/test_vep_csv_parser.py` — after Task 3
  - Pre-commit: `cd backend && python -m pytest tests/test_vep_csv_parser.py -q`

---

## Success Criteria

### Verification Commands
```bash
cd /mnt/zzb/peixunban/hujie/hanjianbing/backend
python -m pytest tests/test_vep_csv_parser.py -v  # Expected: 26+ passed, 0 failed
python -m pytest tests/ -v --tb=short               # Expected: all passed, no regression
```

### Final Checklist
- [ ] All "Must Have" present (4 items)
- [ ] All "Must NOT Have" absent (6 items)
- [ ] All tests pass
- [ ] 大数据量（5000行）解析 < 2 秒
- [ ] 解析结果中所有字段均非空（当 CSV 中有数据时）
