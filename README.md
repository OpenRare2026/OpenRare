# search-agent

基因组变异分析报告生成：从 **manifest + V3 排序宽表** 产出临床解读 Markdown（`report.md`），并可选调用 LLM Agent 补充叙事与临床建议。

另含独立的 **基因检索 Agent**（`main.py`），用于 Open Targets / ClinPGx / PubMed 结构化调研。

---

## 环境（Pixi）

本项目使用 [Pixi](https://pixi.sh/) 管理 Python 与依赖（`pixi.toml` + `pixi.lock`）。

```bash
# 安装 pixi（任选其一）
# curl -fsSL https://pixi.sh/install.sh | bash
# conda install -c conda-forge pixi

pixi install          # 创建/更新 .pixi 环境
pixi shell            # 进入环境（可选）
pixi run <task>       # 在环境中运行任务，如 pixi run api
```

`pyproject.toml` 仍保留包元数据；Pixi 通过可编辑安装 `search-agent` 拉取其中依赖。

---

## 快速开始：生成报告

仓库自带最小示例 `examples/demo_case/`（manifest + 宽表），在仓库根目录执行：

```bash
pixi install
cp .env.example .env   # 配置 LLM_API_KEY、OPEN_TARGETS_MCP_URL 等

# 完整报告：脚本预取 + Agent 叙事（默认）
pixi run python scripts/generate_final_report.py \
  --manifest examples/demo_case/manifest.csv \
  --output-dir examples/demo_case/output_agent \
  --top-n 4
```

无需 LLM、仅验证脚本与模板时，加上 `--no-agent` 并输出到 `output/`：

```bash
pixi run python scripts/generate_final_report.py \
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

## FastAPI 报告服务

除 CLI 脚本外，可通过 HTTP API 流式生成报告（SSE），适合前端对接。

### 启动

```bash
pixi install
cp .env.example .env   # 与 CLI 相同：LLM_API_KEY、OPEN_TARGETS_MCP_URL 等

# 方式一（推荐）
pixi run api

# 方式二
pixi run python -m api.main
```

启动后访问 [http://127.0.0.1:8800/docs](http://127.0.0.1:8800/docs) 查看交互式 API 文档。

### 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查，返回 `{"status":"ok"}` |
| `POST` | `/report/stream` | SSE 流式分析并生成报告 |
| `GET` | `/report/{run_id}/md` | 按 `run_id` 下载 `report.md` |

### 请求参数（`POST /report/stream`）

| 字段 | 说明 | 默认 |
|------|------|------|
| `wide_path` | V3 排序宽表 CSV 路径（仅读取前 10000 行） | 见 `api/schemas.py` |
| `phenotype_path` | 样本表型 CSV（`ID` + `Phenotype` 两列） | 同上 |
| `hpo_path` | HPO 术语文件（每行一个 `HP:xxxxxxx`） | 同上 |
| `top_n` | Top 基因数 | `5` |

示例：

```bash
curl -N -X POST http://127.0.0.1:8800/report/stream \
  -H 'Content-Type: application/json' \
  -d '{
    "wide_path": "/path/to/vep_output.with_info.ranked_large.csv",
    "phenotype_path": "/path/to/phenotype.csv",
    "hpo_path": "/path/to/hpo_terms.txt",
    "top_n": 5
  }'
```

### SSE 事件格式

流式响应按顺序推送三类事件（`data: {json}\n\n`）：

1. **meta** — 任务元信息  
   `{"type":"meta","run_id":"64cec2d4c34c","genes":["SCN1A","KMT2D"]}`

2. **md** — 完整报告章节（按 `##` 一级标题切分，可有多条）  
   `{"type":"md","text":"# 基因组变异分析报告\n\n..."}`

3. **done** — 生成结束，附下载地址  
   `{"type":"done","md_url":"/report/64cec2d4c34c/md"}`

报告产物写入 `test_data/output/{run_id}/`（含 `report.md`、`context.json` 等）。

```bash
curl -OJ http://127.0.0.1:8800/report/64cec2d4c34c/md
```

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

字段解析见 `report/wide_table.py`；下表为当前流水线**实际读取**的宽表列名（CSV 表头须一致）。

### 宽表字段

宽表为 VEP 注释 + 排序后的 CSV。流水线先按 `(chrom, pos, ref, alt)` 去重，每个变异保留一条最佳转录本行，再按 `pathogenic_rank` 取 Top 基因。

**变异定位与排序（必需）**

| 列名 | 用途 |
|------|------|
| `chrom`, `pos`, `ref`, `alt` | 变异坐标，去重主键 |
| `gene_symbol` | 基因分组与报告展示 |
| `pathogenic_rank` | 致病性排序名次；基因级排名 = 组内最小值 |
| `vep_pick`, `tx_rank_within_variant`, `mane_select` | 同一变异多转录本时选最佳行（不写入报告正文） |

**转录本与变异后果**

| 列名 | 报告中的用途 |
|------|----------------|
| `transcript_id`, `refseq_id`, `mane_select` | 基因卡片：转录本、MANE |
| `consequence`, `impact` | 后果类型、VEP 影响等级 |
| `hgvsc`, `hgvsp`, `exon` | HGVS 命名、外显子 |
| `protein_domains` | 蛋白结构域 |

**预测与数据库证据**

| 列名 | 报告中的用途 |
|------|----------------|
| `revel_score`, `cadd_phred` | 有害性预测 |
| `spliceAI_ds_max`, `spliceAI_type` | 剪接影响 |
| `loftee_lof_flag` | LoF 预测 |
| `gnomAD_popmax_AF`, `gnomAD_eas_AF`, `gnomAD_nhomalt` | 人群频率 |
| `clinvar_significance`, `clinvar_review_status`, `clinvar_star_rating` | ClinVar 分类与星级 |
| `evidence_summary` | §2.3 排序得分白盒、证据分解 |

**测序质量与等位基因比例**

| 列名 | 报告中的用途 |
|------|----------------|
| `vcf_info_AF` | GATK 基因型 AF |
| `vcf_info_VAF`, `vcf_info_REF_DP`, `vcf_info_ALT_DP` | reads 层 VAF 与深度 |
| `vcf_info_DP`, `vcf_info_QD`, `vcf_info_FS`, `vcf_info_MQ` | 深度与质量指标 |
| `vcf_info_BEAGLE_PHASED`, `vcf_info_PHASING_CONFIDENCE` | 定相信息 |
| `vcf_info_CHN_REF_SUPPORT`, `vcf_info_CHN_ALT_CARRIER_COUNT`, `vcf_info_CHN_ALT_AC` | 家系/携带者相关 read 支持 |

**基因组注释上下文（可选，有则展示）**

| 列名 | 报告中的用途 |
|------|----------------|
| `vcf_info_REG_CCRE_ID`, `vcf_info_REG_CCRE_CLASS`, `vcf_info_REG_CCRE_COUNT` | 调控元件 |
| `vcf_info_NCRNA_GENE_NAME`, `vcf_info_NCRNA_GENE_TYPE` | 非编码 RNA 注释 |
| `vcf_info_is_pseudogene`, `vcf_info_pseudogene_name`, `vcf_info_pseudogene_source` | 假基因上下文 |

**表达组织**

| 列名 | 报告中的用途 |
|------|----------------|
| `clinical_best_tissue`, `clinical_transcript_tpm` | 临床相关表达组织与 TPM |
| `gtex_transcript_top5_tissues` | GTEx Top5 组织 |

宽表未列出的字段不会被读取。`主要关联表型`、`主要关联通路`、基因功能、遗传模式、用药候选等由脚本预取（Open Targets / NCBI / OMIM / Reactome）或 Agent 补充，不来自宽表列。

---

## 前置依赖

### 1. Python 3.11+ 与 [Pixi](https://pixi.sh/)

```bash
cd search_agent
pixi install
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
pixi run python main.py "CYP2D6 影响哪些药物，有什么 PGx 证据"
pixi run python main.py "TPMT pharmacogenomics" --format json -o report.json
```

调用链见 `agent/factory.py`、`main.py`。

---

## 项目结构

```
search_agent/
├── pixi.toml                      # Pixi 环境与任务（api、依赖）
├── pixi.lock                      # 锁定依赖版本（建议提交）
├── api/                           # FastAPI 报告服务（SSE + MD 下载）
│   └── main.py                    # 启动：pixi run api
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
