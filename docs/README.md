# 基因组变异分析报告生成说明（v3_P001 样例）

本目录为 OpenRare **V3 排序宽表**样例：`26B01490717`。使用仓库根目录下的 `scripts/generate_final_report.py` 从 manifest + 宽表生成 Markdown 报告及中间 JSON。

## 快速开始

在**仓库根目录**执行：

```bash
cd /mnt/workspace/lixinhang/code/search_agent/
uv run python scripts/generate_final_report.py \
  --manifest test_data/test_case/v3_P001_case/06_result_sorting/test_v3_P001.csv \
  --output-dir test_data/test_case/v3_P001_case/06_result_sorting \
  --top-n 5
```

成功后会写入（或覆盖）本目录下：

| 文件 | 说明 |
|------|------|
| `report.md` | 最终 Markdown 报告 |
| `meta.json` | manifest 解析后的样本元信息 |
| `context.json` | 完整 `ReportContext`（宽表 + 工具预取 + Agent 叙事） |
| `context.pre_agent.json` | Agent 运行前的快照（便于对比脚本 vs Agent） |

字段级来源对照见 [report_字段来源注释.md](./report_字段来源注释.md)；宽表列含义见 [../../宽表字段说明.md](../../宽表字段说明.md)。

---

## 命令行参数

脚本：`scripts/generate_final_report.py`（相对路径均相对于**仓库根目录**解析）。

### `--manifest`（必填，有默认值）

- **含义**：测试用例清单 CSV，一行对应一个样本。
- **本样例**：`test_data/test_case/v3_P001_case/06_result_sorting/test_v3_P001.csv`
- **格式**：与 `test_data/test_case/test1.csv` 相同表头；UTF-8（支持 BOM）。
- **说明**：脚本默认读第 0 行数据（见 `--row-index`）。manifest 与宽表可在同一目录，宽表路径可写相对路径（相对 manifest 所在目录解析）。

### `--output-dir`（推荐）

- **含义**：所有产物输出到**同一目录**。
- **本样例**：`test_data/test_case/v3_P001_case/06_result_sorting`
- **固定文件名**：`report.md`、`meta.json`、`context.json`、`context.pre_agent.json`
- **与 `--output` 关系**：二者互斥；未指定任一时，默认写到 `test_data/output/<样本编号>_final_report.md`。

### `--top-n`（可选，默认 `5`）

- **含义**：报告 §2 / §3 纳入的 **Top 基因数量**。
- **排序规则**（`report/wide_table.py`）：
  1. 宽表按 `(chrom, pos, ref, alt)` 去重，每变异保留一条最佳转录本行；
  2. 按 `gene_symbol` 分组，基因排序 = 组内最小 `pathogenic_rank`；
  3. 取前 `top-n` 个基因生成基因卡片。
- **示例**：`--top-n 10` 可展开更多基因；`--top-n 3` 仅保留前 3 个基因。

### `--row-index`（可选，默认 `0`）

- **含义**：manifest CSV 中**数据行**的下标（0-based，不含表头）。
- **用途**：同一 manifest 多行多样本时，指定生成第几行，例如 `--row-index 1`。

### `--output`（可选，与 `--output-dir` 互斥）

- **含义**：仅指定最终 `report.md` 路径。
- **副作用**：`meta.json` / `context.json` 会写到同目录，文件名带样本 ID（如 `26B01490717.meta.json`），**不会**使用 `report.md` 这一套固定命名。

### `--json-snapshot`（可选）

- **含义**：单独指定 `context.json` 路径；仅在与 `--output` 联用时生效。
- **默认**：与 `--output` 同目录、扩展名改为 `.context.json`。

---

## 输入文件要求

### 1. Manifest：`test_v3_P001.csv`

**必需列**（列名需与下表一致）：

| 列名 | 是否必需 | 写入报告 / 用途 |
|------|----------|-----------------|
| `样本编号` | **是** | §1 样本 ID；输出文件命名 |
| `宽表` | **是** | 排序宽表 CSV 路径；§1、§4 引用 |
| `临床信息` | 建议 | §1 临床指征；Agent 表型匹配 |
| `家系类型` | 可选 | §1 家系类型 |
| `家系关系` | 可选 | §1 家系关系 |
| `raghpo` | 可选 | 自由文本或 HPO 列表；解析 `HP:xxxxxxx` |
| `raghpo-returns` | 可选 | JSON；可补充 `hpo_id`（本样例 HPO 主要在此） |
| `gz to vcf` | 可选 | §1 / §4 VCF 路径 |
| `37 to 38` | 可选 | §1 / §4 liftover 路径；支持前导 `@` |
| `基因与疾病` | 可选 | 当前流水线未使用（预留） |
| `ppi` | 可选 | 当前未使用 |
| `报告` | 可选 | 当前未使用 |

**本样例关键路径**（manifest 第 1 行）：

| 字段 | 值 |
|------|-----|
| 样本编号 | `26B01490717` |
| 宽表 | `vep_output.sorted.csv`（与本 manifest 同目录） |
| 临床信息 | 听力障碍、语言发育差、韦氏评分 50 分等 |
| raghpo-returns | 含 `HP:0000365`、`HP:0000750` 等 |

**路径规则**：

- `宽表` 为**相对路径**时：相对于 manifest 文件所在目录，例如 `vep_output.sorted.csv`。
- `宽表` 为绝对路径时：直接使用。
- `37 to 38`、`gz to vcf` 可带 `@` 前缀，脚本会自动去掉。

### 2. 排序宽表：`vep_output.sorted.csv`

**必需**：

- 文件存在且可读（UTF-8，建议带表头）。
- 每行 = 一个「变异 × 转录本」组合（VEP 展开行）。

**核心列**（缺失时报告中对应项显示 `-`）：

| 类别 | 列名示例 |
|------|----------|
| 坐标 | `chrom`, `pos`, `ref`, `alt` |
| 基因 / 转录本 | `gene_symbol`, `transcript_id`, `refseq_id`, `mane_select` |
| VEP | `consequence`, `impact`, `hgvsc`, `hgvsp`, `exon` |
| 预测 | `cadd_phred`, `revel_score`, `spliceAI_ds_max`, `spliceAI_type`, `loftee_lof_flag` |
| 人群 / 数据库 | `gnomAD_eas_AF`, `gnomAD_popmax_AF`, `gnomAD_nhomalt`, `clinvar_significance`, `clinvar_review_status`, `clinvar_star_rating` |
| 测序 | `vcf_info_AF` 或 `vcf_info_VAF`, `vcf_info_DP`（V3 另有 `vcf_info_REF_DP` / `vcf_info_ALT_DP` 等） |
| 表达 | `clinical_best_tissue`, `clinical_transcript_tpm`, `gtex_transcript_top5_tissues` |
| 排序 | `pathogenic_rank`, `evidence_summary` |
| 转录本选择 | `vep_pick`, `tx_rank_within_variant`, `mane_select`（用于去重选行） |

**版本**：本目录为 **OpenRare V3（101 列）**；旧版 `testcase.csv`（83 列）同样兼容。列说明见 `vep_output.sorted.header_fields.zh.md`。

**不要求**：VCF、liftover 文件必须在本地存在（仅写入报告路径说明）；但路径错误不影响宽表解析。

---

## 运行环境与依赖

在项目根目录配置 `.env`（可参考 `.env.example`）。报告生成**默认启用 Agent**（`with_agent=True`），并调用外部数据源：

| 能力 | 环境变量 | 说明 |
|------|----------|------|
| LLM（Agent 叙事） | `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` | **必需**，否则 Agent 步骤失败 |
| Open Targets 表型 | `OPEN_TARGETS_ENABLED=1`, `OPEN_TARGETS_MCP_URL` | §2.1 / §3 主要关联表型 |
| Reactome 通路 | `REACTOME_ENABLED=1`, Neo4j 连接项 | §2.1 / §3 主要关联通路 |
| NCBI 基因功能 | `NCBI_GENE_ENABLED=1`, `NCBI_CONTACT_EMAIL` | §3.1 基因功能（可回退 OMIM） |
| OMIM 遗传模式 | `OMIM_ENABLED=1`, `OMIM_DB_PATH` | §3.1 遗传模式 |
| PubMed 文献 | `paper-search-mcp`（报告 Agent 默认加载） | §3.3.6 文献证据 |
| 严格用药筛选 | Open Targets MCP | §3.5；无命中时输出「暂无符合标准」 |

Open Targets / Reactome / OMIM 不可用时，脚本仍会生成报告，对应字段为 `-` 或占位文案；**LLM 不可用会导致 §2.2 / §3 叙事与 §7 临床建议质量下降或为空**。

安装依赖：

```bash
cd /path/to/search_agent
uv sync
```

---

## 生成流程（简图）

```text
test_v3_P001.csv
    → manifest.py（样本元信息）
vep_output.sorted.csv
    → wide_table.py（去重、Top-N 基因）
    → Reactome / Open Targets / NCBI / OMIM / 用药筛选（脚本）
    → enrich.py（基因叙事 Agent + 临床建议 Agent）
    → render.py + Jinja2 模板
    → report.md + context.json
```

---

## 常用变体命令

```bash
# 只生成前 3 个基因
uv run python scripts/generate_final_report.py \
  --manifest test_data/test_case/v3_P001_case/06_result_sorting/test_v3_P001.csv \
  --output-dir test_data/output/26B01490717_v3_top3 \
  --top-n 3

# 使用默认 test1.csv（25B06715455 旧宽表样例）
uv run python scripts/generate_final_report.py \
  --manifest test_data/test_case/test1.csv \
  --output-dir test_data/output/25B06715455

# 指定单行 manifest + 自定义 report 路径（不用 output-dir）
uv run python scripts/generate_final_report.py \
  --manifest test_data/test_case/v3_P001_case/06_result_sorting/test_v3_P001.csv \
  --row-index 0 \
  --top-n 5 \
  --output test_data/output/26B01490717_final_report.md
```

---

## 本目录文件一览

| 文件 | 角色 |
|------|------|
| `test_v3_P001.csv` | **输入**：样本 manifest |
| `vep_output.sorted.csv` | **输入**：V3 排序宽表 |
| `vep_output.sorted.header_fields.zh.md` | 宽表表头中文说明 |
| `report.md` | **输出**：最终报告 |
| `meta.json` / `context.json` / `context.pre_agent.json` | **输出**：中间数据 |
| `report_字段来源注释.md` | 报告各字段数据来源说明 |
| `result_sorting.log.json` | 上游排序日志（非报告脚本输入） |

---

## 故障排查

| 现象 | 可能原因 |
|------|----------|
| `No data rows found in manifest` | manifest 只有表头、路径错误或编码问题 |
| `row_index out of range` | `--row-index` 超出 manifest 数据行数 |
| `Sample manifest is missing wide table path` | `宽表` 列为空 |
| `FileNotFoundError`（宽表） | `宽表` 相对路径与 manifest 目录不一致 |
| §7 / §2.2 为空或很简略 | LLM 未配置或 Agent 调用失败；可查 `context.pre_agent.json` 与 `context.json` 差异 |
| 主要关联表型 / 通路为 `-` | Open Targets / Reactome 未启用或 MCP/Neo4j 不可达 |
| HPO 在 §1 显示异常 | 本样例 `raghpo` 列为 job UUID；真实 HPO 在 `raghpo-returns` JSON 中，Agent 会合并使用 |

更完整的流水线说明见仓库根目录 [docs/FINAL_REPORT_GENERATION.md](../../../../docs/FINAL_REPORT_GENERATION.md)。
