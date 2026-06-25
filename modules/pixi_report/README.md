# pixi_report

自包含的基因组变异分析报告子模块，可嵌入其他项目的 `modules/pixi_report` 目录。

## 目录结构

```
modules/pixi_report/
├── pixi.toml          # 唯一依赖清单 + 任务
├── pyproject.toml     # Python 包定义
├── agent/             # LLM Agent、MCP 配置
├── api/               # FastAPI（SSE 流式 + MD 下载）
├── report/            # 报告流水线与模板
├── tools/             # ClinPGx、中国试验等本地工具
├── scripts/           # CLI 与测试脚本
├── skills/            # deepagents skills
├── data/              # 本地静态数据（部署见「数据部署与下载」）
├── examples/          # CLI 演示用例
├── fixtures/          # API 测试输入（相对路径）
└── test_data/output/  # API 报告输出目录
```

## 报告输入格式

FastAPI（`POST /report/stream`）需要三个输入文件。路径可为绝对路径，或相对本模块根目录（如 `fixtures/wide_table.csv`）。

### 1. 宽表 CSV（`wide_path`）

由上游 **VCF 注释与排序服务** 产出（典型流程：VCF → VEP/功能注释 → 打分排序 → 导出 CSV）。本模块不负责生成宽表，只消费其结果。

- 编码：UTF-8（支持 BOM）
- 格式：首行为表头，每行一条 **变异 × 转录本** 记录；同一变异（`chrom,pos,ref,alt`）可有多行，流水线会按 `vep_pick`、`tx_rank_within_variant`、`mane_select`、`pathogenic_rank` 等规则选代表转录本
- **Top 基因**按各基因变异的最小 `pathogenic_rank` 升序选取（`top_n` 参数）

**必选列**（表头名需一致）：

| 列名 | 说明 |
|------|------|
| `chrom` | 染色体 |
| `pos` | 位置 |
| `ref` / `alt` | 参考 / 变异等位基因 |
| `gene_symbol` | 基因符号 |
| `pathogenic_rank` | 致病性排序分（整数，越小越优先） |

**报告展示常用列**（缺失时报告中显示为 `-`）：

| 列名 | 说明 |
|------|------|
| `transcript_id` / `refseq_id` / `mane_select` | 转录本 |
| `consequence` / `impact` / `hgvsc` / `hgvsp` / `exon` | 功能后果 |
| `protein_domains` | 蛋白结构域 |
| `cadd_phred` / `revel_score` | 预测分数 |
| `gnomAD_popmax_AF` / `gnomAD_eas_AF` | 人群频率 |
| `spliceAI_ds_max` / `spliceAI_type` | 剪接预测 |
| `clinvar_significance` / `clinvar_review_status` / `clinvar_star_rating` | ClinVar |
| `vcf_info_VAF` / `vcf_info_DP` 等 `vcf_info_*` | 样本 VCF INFO |
| `clinical_best_tissue` / `gtex_transcript_top5_tissues` | 表达组织 |
| `evidence_summary` | 证据摘要 |
| `GENOS-EVEE` | GENOS-EVEE 评分（可选） |

完整列表示例见 `examples/demo_case/wide_table.csv` 或 `fixtures/wide_table.csv`。

> API 读取大宽表时默认只加载前 **10000** 行，避免超大文件 OOM。

### 2. 表型 CSV（`phenotype_path`）

样本编号与临床描述，一行一样本（取第一个有效数据行）。

**推荐格式**（带表头）：

```csv
ID,Phenotype
26B03487389,遗传咨询#主诉：…#现病史：…
```

| 列 | 说明 |
|----|------|
| `ID` | 样本编号（表头大小写不敏感） |
| `Phenotype` | 临床信息自由文本 |

也支持无表头的 `样本ID<TAB或空格>临床信息` 单行格式。示例：`fixtures/phenotype.csv`。

### 3. HPO 术语文件（`hpo_path`）

纯文本，每行一个或多个 HPO 术语；解析时提取所有 `HP:\d+` 编号。

```text
HP:0001249
HP:0001250 癫痫/Epilepsy
```

示例：`fixtures/hpo_terms.txt`。

### 4. PPI 文件（`ppi_path`，可选）

保留字段，当前报告流水线 **不做处理**，可传空字符串。

### API 请求示例

```bash
curl -N -X POST http://127.0.0.1:8800/report/stream \
  -H 'Content-Type: application/json' \
  -d '{
    "wide_path": "fixtures/wide_table.csv",
    "phenotype_path": "fixtures/phenotype.csv",
    "hpo_path": "fixtures/hpo_terms.txt",
    "top_n": 5
  }'
```

## 快速开始

```bash
cd modules/pixi_report
pixi install
cp .env.example .env    # 配置 LLM、MCP 等（见下文「数据部署」）

pixi run api            # http://0.0.0.0:8800
pixi run health
pixi run test-api       # curl 全流程测试
```

> **Pixi 注意**：请使用 [prefix.dev Pixi](https://pixi.sh)（`pixi run` / `pixi install`），勿与 PyPI 上的 Pixiv 下载工具 `pixi` 混淆。若目录曾重命名（如 `module/` → `modules/`），需 `rm -rf .pixi && pixi install` 重建环境。

配置文件路径：**`modules/pixi_report/.env`**（非仓库根目录 `.env`）。

## 数据部署与下载

报告流水线依赖 `data/` 下的本地静态数据，以及 `.env` 中的外部服务。克隆仓库后请按下列说明补齐缺失项。

### 目录布局

```
data/
├── ChinaDrug/chinadrugtrials.csv   # 公开，可提交 git
├── Chictr/chictr.csv               # 公开，可提交 git
├── omim/omim_20250411.sqlite3      # 需自行准备，不入库
├── MONDO/mondo-rare.json           # 需自行准备（仅 CLI）
└── pharmGKB/                       # 需自行准备，不入库
    ├── PrimaryData/genes.zip
    └── AnnotationData/*.zip
```

### 用途一览

| 路径 | 报告 API | 基因 CLI (`main.py`) | 说明 |
|------|:--------:|:--------------------:|------|
| `ChinaDrug/chinadrugtrials.csv` | ✅ | ✅ | 药物推荐 § 中国试验（NMPA） |
| `Chictr/chictr.csv` | ✅ | ✅ | 药物推荐 § 中国试验（ChiCTR） |
| `omim/*.sqlite3` | ✅ | ✅ | 遗传模式、基因功能回退 |
| `MONDO/mondo-rare.json` | — | ✅ | `--mondo-ids` 疾病匹配 |
| `pharmGKB/**` | — | 仅 `OPEN_TARGETS_ONLY=0` | 本地 ClinPGx 用药注释 |

### 1. 中国药物临床试验（NMPA）

| 项 | 内容 |
|----|------|
| 文件 | `data/ChinaDrug/chinadrugtrials.csv` |
| 来源 | [药物临床试验登记与信息公示平台](http://www.chinadrugtrials.org.cn/) |
| 获取 | 平台无官方全量 CSV，需从登记库导出或爬取后整理 |
| 字段 | `drug_name`、`indication`、`title`、`applicant`、`main_leader`、`company` 等（见 `tools/china_trials_local.py`） |
| Git | ✅ 公开登记数据，可提交 |

```bash
mkdir -p data/ChinaDrug
# 将 CSV 放到 data/ChinaDrug/chinadrugtrials.csv
```

### 2. ChiCTR 临床试验

| 项 | 内容 |
|----|------|
| 文件 | `data/Chictr/chictr.csv` |
| 来源 | [Chinese Clinical Trial Registry](https://www.chictr.org.cn/) |
| 获取 | 官网检索或批量导出后整理为 CSV |
| 字段 | `public_title`、`intervention`、`study_ailment`、`applicant`、`study_leader` 等 |
| Git | ✅ 可提交 |

```bash
mkdir -p data/Chictr
# 将 CSV 放到 data/Chictr/chictr.csv
```

### 3. OMIM SQLite（推荐）

| 项 | 内容 |
|----|------|
| 文件 | `data/omim/omim_20250411.sqlite3`（文件名可自定） |
| 来源 | [OMIM](https://www.omim.org/)，需遵守使用条款；通常由团队从授权渠道构建 SQLite 快照 |
| 用途 | 报告 §3.x.1 **遗传模式**；NCBI 无摘要时 **基因功能回退** |
| Git | ❌ 体积大 / 许可限制，已 gitignore |

`.env` 配置：

```bash
OMIM_ENABLED=1
OMIM_DB_PATH=./data/omim/omim_20250411.sqlite3
GENE_FUNCTION_FALLBACK_OMIM=1
```

```bash
mkdir -p data/omim
# 放入 SQLite 文件
```

### 4. MONDO 罕见病本体（CLI 专用）

| 项 | 内容 |
|----|------|
| 文件 | `data/MONDO/mondo-rare.json` |
| 来源 | [MONDO Disease Ontology](https://github.com/monarch-initiative/mondo) release JSON 或 rare 子集 |
| 用途 | 仅 `python main.py --gene ... --mondo-ids MONDO_...`；**报告 API 不读取** |
| Git | ❌ 建议忽略 |

```bash
mkdir -p data/MONDO
# 放入 mondo-rare.json
```

### 5. ClinPGx / PharmGKB（CLI 可选）

| 项 | 内容 |
|----|------|
| 目录 | `data/pharmGKB/` |
| 来源 | [ClinPGx Downloads](https://www.clinpgx.org/downloads) |
| 用途 | 本地 `get_gene_pgx_profile`（用药指南、证据等级等）；**报告 API 不使用** |
| 何时需要 | 基因检索 CLI 且 `OPEN_TARGETS_ONLY=0` |
| Git | ❌ zip 体积大，已 gitignore |

目录结构：

```
data/pharmGKB/
├── PrimaryData/genes.zip
└── AnnotationData/
    ├── summaryAnnotations.zip
    ├── guidelineAnnotations.json.zip
    └── pathways-tsv.zip
```

`.env` 配置（仅 CLI 需要 PharmGKB 时）：

```bash
OPEN_TARGETS_ONLY=0
PHARMGKB_DATA_DIR=./data/pharmGKB
```

### 外部服务（`.env` 配置，非 `data/` 文件）

| 服务 | 环境变量 | 用途 | API 默认 |
|------|----------|------|:--------:|
| LLM | `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL` | Agent 叙事、临床建议 | ✅ 必需 |
| Open Targets MCP | `OPEN_TARGETS_MCP_URL` | 表型/靶点 enrichment | ✅ 建议 |
| Open Targets 脚本查询 | `OPEN_TARGETS_ENABLED=1` | §2.1 主要关联表型 | ✅ |
| Reactome Neo4j | `REACTOME_*` | 通路查询 | 可选 |
| NCBI Entrez Gene | `NCBI_*` | §3.x.1 基因功能摘要 | 可选 |
| openFDA MCP | `OPENFDA_MCP_URL` | 药物安全信息 | 可选（有公共托管） |
| paper-search MCP | `PAPER_SEARCH_MCP_*` | PubMed 文献 | Agent 阶段 |

Open Targets MCP 本地启动示例：

```bash
docker run -d -p 8010:8000 \
  -e OTP_MCP_HTTP_HOST=0.0.0.0 \
  -e OTP_MCP_JQ_ENABLED=true \
  ghcr.io/opentargets/open-targets-platform-mcp
```

`.env` 中设置：`OPEN_TARGETS_MCP_URL=http://localhost:8010/mcp`

### 最小可跑报告 API

| 类别 | 必需项 | 缺失时影响 |
|------|--------|------------|
| 配置 | `modules/pixi_report/.env` 中 LLM 三项 | 无法启动 Agent |
| 本地数据 | OMIM SQLite | 遗传模式为空，不阻断 |
| 本地数据 | ChinaDrug + ChiCTR CSV | 中国试验匹配为空，不阻断 |
| 外部服务 | Open Targets MCP | enrichment 降级，可能部分章节简略 |
| 不需要 | PharmGKB、MONDO | 报告 API 不读取 |

用 `fixtures/` 做冒烟测试时，至少准备 **LLM**；OMIM 与试验 CSV 建议补齐以得到完整报告。

### Git 提交建议

| 路径 | 提交 |
|------|------|
| `data/ChinaDrug/chinadrugtrials.csv` | ✅ |
| `data/Chictr/chictr.csv` | ✅ |
| `data/omim/*.sqlite3` | ❌ |
| `data/MONDO/*` | ❌ |
| `data/pharmGKB/**` | ❌ |

更细的字段说明与许可备注见 **[data/README.md](data/README.md)**。

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/report/stream` | SSE 流式生成报告 |
| `GET` | `/report/{run_id}/md` | 下载 report.md |

请求体路径可使用相对路径（相对本模块根目录），例如 `fixtures/wide_table.csv`。

## CLI 生成报告

```bash
pixi run python scripts/generate_final_report.py \
  --manifest examples/demo_case/manifest.csv \
  --output-dir examples/demo_case/output_agent \
  --top-n 4
```

## 嵌入父项目

将整个 `modules/pixi_report` 目录复制或 git submodule 到父仓库，在父项目中：

```bash
cd modules/pixi_report && pixi install && pixi run api
```

依赖与环境仅由本目录下的 `pixi.toml` 管理。数据部署见 **[数据部署与下载](#数据部署与下载)**。
