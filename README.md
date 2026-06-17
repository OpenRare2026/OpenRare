# search-agent

基因组变异分析报告生成：从 **manifest + V3 排序宽表** 产出临床解读 Markdown（`report.md`），并可选调用 LLM Agent 补充叙事与临床建议。

另含独立的 **基因检索 Agent**（`main.py`），用于 Open Targets / ClinPGx / PubMed 结构化调研。

---

## 快速开始：生成报告

仓库自带最小示例 `examples/demo_case/`（manifest + 宽表），在仓库根目录执行：

```bash
uv sync
cp .env.example .env   # 配置 LLM_API_KEY、OPEN_TARGETS_MCP_URL 等

# 完整报告：脚本预取 + Agent 叙事（默认）
uv run python scripts/generate_final_report.py \
  --manifest examples/demo_case/manifest.csv \
  --output-dir examples/demo_case/output_agent \
  --top-n 4
```

无需 LLM、仅验证脚本与模板时，加上 `--no-agent` 并输出到 `output/`：

```bash
uv run python scripts/generate_final_report.py \
  --manifest examples/demo_case/manifest.csv \
  --output-dir examples/demo_case/output \
  --top-n 4 \
  --no-agent
```

### 示例输入

| 文件 | 说明 |
|------|------|
| `examples/demo_case/manifest.csv` | 样本 26B03487389：临床信息 + HPO + 宽表路径 |
| `examples/demo_case/wide_table.csv` | 4 个 Top 基因（CNOT3、KANSL1、TNRC6B、SETD5） |

### 示例输出

| 目录 | 模式 | 主要文件 |
|------|------|----------|
| `examples/demo_case/output_agent/` | **默认（含 Agent）** | `report.md`、`context.json`、`context.pre_agent.json` |
| `examples/demo_case/output/` | `--no-agent` | `report.md`、`context.json` |

仓库内已预生成上述两份报告，可直接打开 `output_agent/report.md` 查看完整效果；重新运行对应命令会覆盖该目录。

### 常用参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `--manifest` | 测试用例清单 CSV（一行一样本） | `examples/demo_case/manifest.csv` |
| `--row-index` | manifest 数据行下标（0-based） | `0` |
| `--top-n` | 报告纳入的 Top 基因数 | `5` |
| `--output-dir` | 输出目录（写入 `report.md` 等固定文件名） | — |
| `--output` | 指定 `report.md` 路径（与 `--output-dir` 互斥） | `examples/demo_case/output_agent/report.md` |
| `--no-agent` | 跳过 LLM，仅脚本预取 + 模板 | 关闭 |

---

## 报告流水线概览

```
manifest.csv + 宽表 CSV
    → report/manifest.py + wide_table.py
    → 脚本预取（Reactome / Open Targets 表型 / NCBI Gene / OMIM / 用药筛选）
    → Agent 叙事（每基因 GeneNarrative + 样本级 ClinicalAdvice，可用 --no-agent 跳过）
    → Jinja2 模板 → report.md
```

入口代码：`scripts/generate_final_report.py` → `report/pipeline.py`

---

## 前置依赖

### 1. Python 3.11+ 与 [uv](https://docs.astral.sh/uv/)

```bash
cd search_agent
uv sync
```

### 2. LLM API（启用 Agent 时需要）

```bash
cp .env.example .env
```

必填：`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`（任意 OpenAI 兼容接口）。

### 3. Open Targets Platform MCP

脚本预取（Open Targets 表型、用药）与 Agent 工具均依赖 MCP：

```bash
docker run -d \
  --name open-targets-mcp \
  -p 8010:8000 \
  -e OTP_MCP_HTTP_HOST=0.0.0.0 \
  -e OTP_MCP_JQ_ENABLED=true \
  ghcr.io/opentargets/open-targets-platform-mcp
```

`.env`：`OPEN_TARGETS_MCP_URL=http://localhost:8010/mcp`

### 4. 可选本地数据

| 数据 | 用途 | 配置 |
|------|------|------|
| OMIM SQLite | 遗传模式 | `data/omim/` |
| Reactome Neo4j | 主要通路 | 见 `report/reactome.py` |
| PharmGKB | 基因检索 Agent 的 ClinPGx | `PHARMGKB_DATA_DIR`（`OPEN_TARGETS_ONLY=0`） |

---

## 配置说明

| 变量 | 说明 | 默认 |
|------|------|------|
| `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` | 报告 Agent 与基因检索 Agent | — |
| `OPEN_TARGETS_MCP_URL` | Open Targets MCP | `http://localhost:8010/mcp` |
| `OPEN_TARGETS_ONLY` | 基因检索 Agent：`1` 仅 OT；`0` 启用 ClinPGx + 文献 | `1` |
| `PHARMGKB_DATA_DIR` | 本地 PharmGKB | `data/pharmGKB` |

---

## 辅助工具：基因检索 Agent

用于交互式基因/药物/疾病调研，输出 JSON 研究报告（**不是** `report.md`）：

```bash
uv run python main.py "CYP2D6 影响哪些药物，有什么 PGx 证据"
uv run python main.py "TPMT pharmacogenomics" --format json -o report.json
```

调用链见 `agent/factory.py`、`main.py`。

---

## 项目结构

```
search_agent/
├── examples/
│   └── demo_case/                 # 内置 manifest + 宽表 + 样例输出
│       ├── output_agent/          # 默认：含 Agent 的预生成报告
│       └── output/                # --no-agent 预生成报告
├── scripts/
│   ├── generate_final_report.py   # 主入口：生成基因组报告
│   └── export_report.py           # report.md → HTML/PDF
├── report/                        # 报告流水线（manifest → render）
│   ├── pipeline.py
│   ├── wide_table.py
│   ├── enrich.py                  # Agent 叙事注入
│   └── templates/                 # Jinja2 报告模板
├── agent/                         # LangChain Agent 与 Open Targets 工具
├── tools/                         # ClinPGx、中国试验等本地工具
└── main.py                        # 基因检索 Agent CLI
```

---

## 许可证

See [LICENSE](LICENSE).
