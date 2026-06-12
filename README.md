# search-agent

基因检索 Agent：整合 **Open Targets**（靶点 / 疾病 / 药物）、**ClinPGx 本地 PharmGKB**（药物基因组学）与 **PubMed 文献**，输出结构化研究报告。

## 功能概览

| 数据源 | 工具 | 内容 |
|--------|------|------|
| Open Targets | `lookup_gene` | 基因符号 → Ensembl ID |
| Open Targets | `get_gene_disease_associations` | 基因关联疾病及 score |
| Open Targets | `get_gene_drug_details` | 药物搜索 + 详情（临床阶段、适应症、MOA、不良反应、PGx、参考文献） |
| Open Targets | `get_drug_details` | 按 ChEMBL ID 查单药详情 |
| Open Targets | `search_gene_drugs` | 轻量药物名搜索（可选） |
| ClinPGx 本地 | `get_gene_pgx_profile` | 指南、证据等级、等位基因效应、代谢通路 |
| 文献 | `paper_search_search_pubmed` 等 | PubMed / arXiv 摘要 |

默认 `OPEN_TARGETS_ONLY=1` 时仅使用 Open Targets；设为 `0` 后启用 ClinPGx 与文献搜索。

ClinPGx 工具定义在 `tools/clinpgx.py`，由 `agent/factory.py` 注册到 Agent（`OPEN_TARGETS_ONLY=0` 时生效），不单独提供 CLI。

更细的调用链见 [docs/DATA_FLOW.md](docs/DATA_FLOW.md)（部分章节可能与最新代码略有差异，以 `agent/` 代码为准）。

## 前置依赖

### 1. Python 3.11+ 与 [uv](https://docs.astral.sh/uv/)

```bash
cd search_agent
uv sync
```

### 2. Open Targets Platform MCP（必需）

Agent 通过 HTTP MCP 访问 Open Targets，需先在本机启动 MCP 服务：

```bash
docker run -d \
  --name open-targets-mcp \
  -p 8010:8000 \
  -e OTP_MCP_HTTP_HOST=0.0.0.0 \
  -e OTP_MCP_JQ_ENABLED=true \
  ghcr.io/opentargets/open-targets-platform-mcp
```

- 容器内端口 `8000`，映射到主机 **`8010`**
- `.env` 中 `OPEN_TARGETS_MCP_URL=http://localhost:8010/mcp` 需与此一致

检查服务：

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8010/mcp
```

### 3. ClinPGx 本地数据（`OPEN_TARGETS_ONLY=0` 时需要）

将 PharmGKB 下载放到项目内：

```bash
# 目录结构见 data/README.md
data/pharmGKB/
├── PrimaryData/
└── AnnotationData/
```

`.env`：

```bash
PHARMGKB_DATA_DIR=./data/pharmGKB
```

相对路径会从**项目根目录**解析。

### 4. LLM API

复制环境变量并按你的服务商填写：

```bash
cp .env.example .env
```

必填：`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`（任意 OpenAI 兼容接口）。

## 配置说明

| 变量 | 说明 | 默认 |
|------|------|------|
| `LLM_BASE_URL` | LLM API 根地址 | — |
| `LLM_API_KEY` | API Key | — |
| `LLM_MODEL` | 模型名 | — |
| `OPEN_TARGETS_MCP_URL` | Open Targets MCP 地址 | `http://localhost:8010/mcp` |
| `OPEN_TARGETS_ONLY` | `1` 仅 OT；`0` 启用 ClinPGx + 文献 | `1` |
| `PHARMGKB_DATA_DIR` | 本地 PharmGKB 目录 | `data/pharmGKB` |
| `PAPER_SEARCH_MCP_*` | 文献 MCP 可选配置 | — |

## 启动 Agent

```bash
# 默认示例问题
uv run python main.py

# 指定问题
uv run python main.py "CYP2D6 影响哪些药物，有什么 PGx 证据"

# 只输出 JSON 报告
uv run python main.py "TPMT pharmacogenomics" --format json -o report.json

# 文本 + JSON
uv run python main.py "BRCA2" --format both
```

### 仅 Open Targets 模式（默认）

`.env`：

```bash
OPEN_TARGETS_ONLY=1
```

Agent 会依次调用：`lookup_gene` → `get_gene_disease_associations` → `get_gene_drug_details`。

### 完整三源模式

`.env`：

```bash
OPEN_TARGETS_ONLY=0
```

额外调用 `get_gene_pgx_profile` 与 PubMed/arXiv。

## 项目结构

```
search_agent/
├── agent/
│   ├── factory.py           # Agent 与 system prompt
│   ├── open_targets_tools.py  # Open Targets LangChain tools
│   ├── report.py              # 结构化 JSON report
│   └── config.py
├── tools/                     # Agent 可调用的 LangChain tools
│   ├── clinpgx.py             # get_gene_pgx_profile
│   └── clinpgx_local.py       # 本地 PharmGKB 加载
├── data/pharmGKB/             # 本地 ClinPGx 数据（gitignore）
├── docs/DATA_FLOW.md
├── skills/
└── main.py
```

## 许可证

See [LICENSE](LICENSE).
