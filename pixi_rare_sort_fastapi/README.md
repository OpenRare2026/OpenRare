# rare_sort FastAPI

罕见病变异排序评分服务。对 VEP 宽表（CSV/Parquet）进行突变级评分，可选叠加基因表型加权（gene_score）和 PPI 网络加权（ppi_score），输出含 `evolve_score`、`pathogenic_score`、`pathogenic_rank` 的结果 CSV。

零外部私有依赖，所有评分逻辑收敛在 `_core.py`，环境由 Pixi + conda-forge 管理。

## 目录

- [环境要求](#环境要求)
- [安装与快速开始](#安装与快速开始)
- [获取输入文件](#获取输入文件)
- [API 文档](#api-文档)
- [评分公式](#评分公式)
- [项目结构](#项目结构)

---

## 环境要求

| 依赖 | 说明 |
|------|------|
| Pixi | 包管理与环境隔离。安装：`curl -fsSL https://pixi.prefix.dev/install.sh \| bash` |

Python、FastAPI、duckdb、pandas 等全部由 Pixi 自动安装，无需手动管理。

## 安装与快速开始

```bash
# 1. 获取代码
git clone git@github.com:OpenRare2026/OpenRare.git
cd OpenRare && git checkout dev-wyz
cd pixi_rare_sort_fastapi

# 2. 添加平台支持（按需）
pixi workspace platform add osx-arm64   # macOS Apple Silicon
pixi workspace platform add linux-64    # Linux x86_64

# 3. 安装依赖
pixi install

# 4. 启动服务（默认 5000 端口）
pixi run start

# 5. 验证
curl http://localhost:5000/jobs
# → {}
```

服务器上 Pixi 路径为 `/mnt/workspace/hujie/pixi`，用此路径替换上述 `pixi` 命令。

## 获取输入文件

服务需要三类文件，均来自 OpenRare 管线上游：

### VEP 宽表（必填）

`complete_pipeline` → `06_result_sorting/vep_output.sorted.csv`

必须含以下列：`chrom`, `pos`, `ref`, `alt`, `gene_symbol`, `tx_rank_within_variant`，以及评分所需的 ClinVar、consequence、spliceAI、REVEL/CADD、gnomAD、protein_domains 列。

### gene_phenotype_score.csv（可选）

HPO 表型匹配服务输出，含 `gene_symbol` 和 `gene_score` 列。

```
gene_symbol,gene_score,...
MTM1,0.673790,...
PDHA1,0.656325,...
```

### ppi_score.csv（可选）

PPI 网络分析服务输出，含 `gene` 和 `ppi_final` 列。

```
gene,ppi_final,...
CDC42,0.999599,...
RPL5,0.999153,...
```

---

## API 文档

### 端点一览

| 接口 | 方法 | 描述 |
|------|------|------|
| `/score` | POST | 服务器已有文件评分 |
| `/score/upload` | POST | 上传文件评分 |
| `/status/{job_id}` | GET | 查询任务状态 |
| `/jobs` | GET | 列出全部任务 |

### 任务状态

| status | 含义 |
|--------|------|
| `queued` | 已入队 |
| `running` | 执行中，含 `started_at` |
| `done` | 完成，含 `output` 路径和 `elapsed` 秒数 |
| `failed` | 失败，含 `error` |

### POST /score

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `input_path` | string | 是 | 服务器上 VEP 文件绝对路径 |
| `gene_score_path` | string | 否 | gene_phenotype_score.csv 路径 |
| `ppi_score_path` | string | 否 | ppi_score.csv 路径 |

```bash
# 仅突变级评分
curl -X POST "http://localhost:5000/score?input_path=/data/vep.csv"

# 完整三文件评分
curl -X POST "http://localhost:5000/score?input_path=/data/vep.csv&gene_score_path=/data/gene_phenotype_score.csv&ppi_score_path=/data/ppi_score.csv"
# → {"job_id":"a1b2c3d4","status":"queued"}
```

### POST /score/upload

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `file` | file | 是 | VEP CSV/Parquet |
| `gene_score_file` | file | 否 | gene_phenotype_score.csv |
| `ppi_score_file` | file | 否 | ppi_score.csv |

```bash
curl -X POST http://localhost:5000/score/upload \
  -F "file=@vep_output.sorted.csv" \
  -F "gene_score_file=@gene_phenotype_score.csv" \
  -F "ppi_score_file=@ppi_score.csv"
# → {"job_id":"abc12345","status":"queued","filename":"vep_output.sorted.csv"}
```

### GET /status/{job_id}

```bash
curl http://localhost:5000/status/abc12345
# → {"status":"done","output":"/tmp/.../ranked.csv","elapsed":2.07}
```

### GET /jobs

```bash
curl http://localhost:5000/jobs
# → {"abc12345":{"status":"done","input":"/data/vep.csv","filename":null}}
```

---

## 评分公式

### Pass 1 — 突变级评分（Python）

6 个 Contributor，每个有固定 calibrate 函数（`_core.py`），加权求和：

```
evolve_score = Σ (theta_i × calibrate_i(row))
```

theta 权重固定：

| Contributor | theta | 依赖列 |
|-------------|-------|--------|
| clinvar_score | 1.291 | clinvar_significance, clinvar_star_rating, clinvar_review_status |
| consequence_score | 1.101 | consequence, impact |
| splice_lof_score | 2.027 | spliceAI_ds_max, spliceAI_type, loftee_lof_flag, loftee_lof_filter |
| prediction_score | 0.497 | revel_score, cadd_phred |
| frequency_score | 0.210 | gnomAD_eas_AF, gnomAD_popmax_AF, gnomAD_nhomalt |
| domain_score | 3.661 | protein_domains |

结果按 variant 去重（tx_rank==1 优先），`evolve_rank` 降序编号。

### Pass 2 — 基因加权（duckdb SQL）

**仅 gene_score：**
```
pathogenic_score = evolve_score × √(gene_score)
```

**gene_score + ppi_score：**
```
pathogenic_score = evolve_score × √(gene_score) × √(ppi_final)
```

**不加权：** `pathogenic_score = evolve_score`

未匹配基因 score 为 0，`pathogenic_rank` 按降序重排，NULL 排末尾。

### 输出列

始终输出：原始 VEP 列 + `evolve_score` + `evolve_rank` + `pathogenic_score` + `pathogenic_rank`。提供 gene_score 时额外含 `gene_score`，提供 ppi_score 时额外含 `ppi_final`。

---

## 项目结构

```text
pixi_rare_sort_fastapi/
├── main.py          # FastAPI 入口，4 端点 + 异步任务队列
├── pipeline.py       # 评分流水线（Pass 1 特征提取 → Pass 2 duckdb JOIN）
├── _core.py          # 评分核心（6 个 Contributor calibrate + apply_theta + rank_units）
├── dataio.py         # 宽表 I/O（列裁剪 + 分块流式，自动选引擎）
├── pixi.toml         # 项目清单（全部依赖 conda-forge）
├── pixi.lock         # 依赖版本锁定
└── README.md
```

| 文件 | 作用 |
|------|------|
| `main.py` | FastAPI 服务，内存任务队列 |
| `pipeline.py` | 两阶段流水线，组装 Pass 1 + Pass 2 |
| `_core.py` | 评分核心：Contributor、calibrate、theta 加权、去重排名 |
| `dataio.py` | 大规模 I/O，引擎优先级 duckdb > polars > pyarrow > pandas |
| `pixi.toml` | 依赖声明，全部来自 conda-forge |
| `pixi.lock` | 锁定版本，跨机器复现 |
