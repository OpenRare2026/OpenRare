# VEP CSV Parser 返回类型修复

## TL;DR

> **Quick Summary**: 修复 `VEPCSVParser.parse()` 返回类型不匹配问题，将 dataclass 返回值改为简单 tuple `(rows, columns)`
>
> **Deliverables**:
> - 修改后的 `vep_csv_parser.py`
> - 更新后的 `vep_service.py` 调用代码
> - 更新后的 `test_vep_csv_parser.py` 测试文件
>
> **Estimated Effort**: Quick
> **Parallel Execution**: NO - sequential (单文件修改链)
> **Critical Path**: parser → service → tests

---

## Context

### Original Request
用户报告 VEPCSVParser 对 CSV 处理结果有问题，字段解析错误。

### Interview Summary
**Key Discussions**:
- 问题根因：`parse()` 返回 `VEPParseResult` dataclass，但调用方期望 `List[Dict]`
- 解决方案：简化返回值为 `Tuple[List[Dict[str, str]], List[str]]`
- columns 信息需要保留

**Research Findings**:
- 当前代码已使用 pandas 解析（无需改动解析逻辑）
- 数据库 `Variant` 模型有固定字段名
- VEP CSV 列名可能不固定，但当前代码已处理

---

## Work Objectives

### Core Objective
修复 `VEPCSVParser.parse()` 的返回类型，使其与调用方期望一致。

### Concrete Deliverables
- `backend/services/vep_csv_parser.py` - 返回类型改为 tuple
- `backend/services/vep_service.py` - 更新调用代码
- `backend/tests/test_vep_csv_parser.py` - 更新所有测试断言

### Definition of Done
- [ ] `pytest backend/tests/test_vep_csv_parser.py` 全部通过
- [ ] `pytest backend/tests/test_vep_integration.py` 全部通过（如有）

### Must Have
- 返回 `Tuple[List[Dict[str, str]], List[str]]`
- 保留 columns 信息
- 所有测试通过

### Must NOT Have (Guardrails)
- 不修改 pandas 解析逻辑
- 不修改 delimiter 检测逻辑
- 不修改 comment 剥离逻辑
- 不修改数据库模型字段

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: Tests-after（先修改代码，后验证测试）
- **Framework**: pytest
- **If TDD**: N/A

### QA Policy
每个任务包含 Agent-Executed QA Scenarios。

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - sequential chain):
├── Task 1: 修改 vep_csv_parser.py [quick]
└── (Blocks: Task 2)

Wave 2 (After Task 1):
├── Task 2: 更新 vep_service.py [quick]
└── (Blocks: Task 3)

Wave 3 (After Task 2):
├── Task 3: 更新测试文件 [quick]
└── (Blocks: Final Verification)

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 2 → Task 3 → Final Wave
```

---

## TODOs

- [ ] 1. 修改 vep_csv_parser.py 返回类型

  **What to do**:
  - 将 `VEPParseResult` dataclass 改为直接返回 tuple
  - 修改 `parse()` 方法的返回类型签名
  - 返回 `(rows, columns)` 而非 `VEPParseResult(rows=rows, columns=columns)`
  - 可以保留 `VEPParseResult` 作为内部类型或完全移除

  **Must NOT do**:
  - 不修改 pandas 解析逻辑
  - 不修改 delimiter 检测
  - 不修改 comment 剥离

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单文件修改，逻辑简单，只改返回类型
  - **Skills**: `[]`
    - 无特殊技能需求

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References** (CRITICAL):
  - `backend/services/vep_csv_parser.py:45-91` - parse() 方法完整实现
  - `backend/services/vep_csv_parser.py:17-22` - VEPParseResult dataclass 定义

  **Acceptance Criteria**:
  - [ ] 返回类型为 `Tuple[List[Dict[str, str]], List[str]]`
  - [ ] 代码语法正确，可导入

  **QA Scenarios**:
  ```
  Scenario: Verify parser return type
    Tool: Bash (python -c)
    Preconditions: 虚拟环境已激活
    Steps:
      1. python -c "from services.vep_csv_parser import VEPCSVParser; p = VEPCSVParser(); r = p.parse(''); print(type(r))"
    Expected Result: `<class 'tuple'>`
    Evidence: .sisyphus/evidence/task-1-return-type.txt
  ```

  **Commit**: NO

---

- [ ] 2. 更新 vep_service.py 调用代码

  **What to do**:
  - 将 `variants = self.parser.parse(csv_content)` 改为 `rows, columns = self.parser.parse(csv_content)`
  - 更新日志输出，包含 columns 信息
  - 保持返回值为 `rows`（或调整返回类型）

  **Must NOT do**:
  - 不修改 HTTP 请求逻辑
  - 不修改错误处理逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 单行调用修改
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:
  - `backend/services/vep_service.py:172-174` - parser.parse() 调用位置

  **Acceptance Criteria**:
  - [ ] 调用代码正确解包 tuple
  - [ ] 日志输出包含 columns 信息

  **QA Scenarios**:
  ```
  Scenario: Verify service handles tuple return
    Tool: Bash (pytest)
    Preconditions: Task 1 已完成
    Steps:
      1. pytest backend/tests/test_vep_integration.py -v
    Expected Result: All tests pass or skip gracefully
    Evidence: .sisyphus/evidence/task-2-service-test.txt
  ```

  **Commit**: NO

---

- [ ] 3. 更新测试文件 test_vep_csv_parser.py

  **What to do**:
  - 将所有 `variants = parser.parse(...)` 改为 `rows, columns = parser.parse(...)`
  - 更新断言：`len(variants)` → `len(rows)`
  - 更新断言：`variants[0]` → `rows[0]`
  - 添加 columns 验证断言

  **Must NOT do**:
  - 不删除测试用例
  - 不改变测试覆盖范围

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 机械性更新断言
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Final Wave
  - **Blocked By**: Task 2

  **References**:
  - `backend/tests/test_vep_csv_parser.py:35-152` - 所有测试用例

  **Acceptance Criteria**:
  - [ ] `pytest backend/tests/test_vep_csv_parser.py` 全部通过

  **QA Scenarios**:
  ```
  Scenario: All parser tests pass
    Tool: Bash (pytest)
    Preconditions: Task 1, 2 已完成
    Steps:
      1. cd backend && pytest tests/test_vep_csv_parser.py -v
    Expected Result: All tests pass (X passed, 0 failed)
    Evidence: .sisyphus/evidence/task-3-tests-pass.txt
  ```

  **Commit**: YES
  - Message: `fix(vep): simplify VEPCSVParser return type to tuple (rows, columns)`
  - Files: `backend/services/vep_csv_parser.py`, `backend/services/vep_service.py`, `backend/tests/test_vep_csv_parser.py`
  - Pre-commit: `pytest backend/tests/test_vep_csv_parser.py`

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Verify Must Have/Must NOT Have compliance and evidence files.

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` (if TypeScript) or `mypy` + `ruff` + `pytest`.

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Run all QA scenarios and capture evidence.

- [ ] F4. **Scope Fidelity Check** — `deep`
  Verify changes match spec exactly.

---

## Commit Strategy

- **1**: `fix(vep): simplify VEPCSVParser return type to tuple (rows, columns)` - all modified files, after tests pass

---

## Success Criteria

### Verification Commands
```bash
cd backend && pytest tests/test_vep_csv_parser.py -v  # Expected: All tests pass
cd backend && pytest tests/test_vep_integration.py -v  # Expected: All tests pass or skip
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
