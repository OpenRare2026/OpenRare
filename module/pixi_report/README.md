# pixi_report

自包含的基因组变异分析报告子模块，可嵌入其他项目的 `module/pixi_report` 目录。

## 目录结构

```
module/pixi_report/
├── pixi.toml          # 唯一依赖清单 + 任务
├── pyproject.toml     # Python 包定义
├── agent/             # LLM Agent、MCP 配置
├── api/               # FastAPI（SSE 流式 + MD 下载）
├── report/            # 报告流水线与模板
├── tools/             # ClinPGx、中国试验等本地工具
├── scripts/           # CLI 与测试脚本
├── skills/            # deepagents skills
├── data/              # OMIM、MONDO、试验数据等（大文件见 data/README.md）
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
cd module/pixi_report
pixi install
cp .env.example .env    # 配置 LLM、MCP 等

pixi run api            # http://0.0.0.0:8800
pixi run health
pixi run test-api       # curl 全流程测试
```

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

将整个 `module/pixi_report` 目录复制或 git submodule 到父仓库，在父项目中：

```bash
cd module/pixi_report && pixi install && pixi run api
```

依赖与环境仅由本目录下的 `pixi.toml` 管理。

## 本地数据（`data/`）

报告与 CLI 依赖的本地文件需用户自行下载，详见 **[data/README.md](data/README.md)**。

| 数据 | 报告 API | 说明 |
|------|:--------:|------|
| `omim/*.sqlite3` | ✅ | 遗传模式；需自行准备 |
| `ChinaDrug/chinadrugtrials.csv` | ✅ | 公开 |
| `Chictr/chictr.csv` | ✅ | 公开 |
| `pharmGKB/**` | — | 本地 ClinPGx/PharmGKB zip，仅 `main.py` 且 `OPEN_TARGETS_ONLY=0` 时通过 `get_gene_pgx_profile` 查询 |
| `MONDO/mondo-rare.json` | — | 仅基因检索 CLI（`--mondo-ids`） |

PharmGKB 从 [ClinPGx Downloads](https://www.clinpgx.org/downloads) 下载后放入 `data/pharmGKB/`，配置 `PHARMGKB_DATA_DIR=./data/pharmGKB`（默认）。zip 体积大，不入库。
