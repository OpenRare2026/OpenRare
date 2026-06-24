# rare_sort FastAPI

基于 Pixi 的罕见病变异排序评分服务。对 VEP 宽表（CSV/Parquet）进行突变级评分，可选叠加基因表型加权（gene_score）和 PPI 网络加权（ppi_score），输出含 `evolve_score`、`pathogenic_score`、`pathogenic_rank` 的结果 CSV。

## 目录

- [环境要求](#环境要求)
- [安装与快速开始](#安装与快速开始)
- [获取输入文件](#获取输入文件)
- [API 文档](#api-文档)
- [评分公式](#评分公式)
- [使用示例](#使用示例)
- [项目结构](#项目结构)

---

## 环境要求

| 依赖 | 说明 |
|------|------|
| Pixi >= 0.68 | 包管理与环境隔离。服务器路径：`/mnt/workspace/hujie/pixi` |
| rare_sort | 罕见病评分核心库，需 clone 到本地 |

## 安装与快速开始

### 1. 安装 Pixi

```bash
# macOS / Linux 一键安装
curl -fsSL https://pixi.prefix.dev/install.sh | bash
# 重启 shell 或执行：
source ~/.bashrc
```

服务器上已有 Pixi，跳过此步，直接用 `/mnt/workspace/hujie/pixi` 替代 `pixi`。

### 2. 获取 rare_sort

```bash
git clone git@github.com:wyzBelinda/rare_sort.git /path/to/rare_sort
# 或服务器上已有：/home/wuyuzhuo/rare_sort
```

### 3. 获取本项目

```bash
git clone git@github.com:OpenRare2026/OpenRare.git
cd OpenRare
git checkout dev-wyz
cd pixi_rare_sort_fastapi
```

### 4. 配置 rare_sort 路径

编辑 `pixi.toml`，将 `[pypi-dependencies]` 中的 `path` 改为本机 rare_sort 路径：

```toml
[pypi-dependencies]
rare-sort = { path = "/home/wuyuzhuo/rare_sort" }   # 服务器路径
# rare-sort = { path = "/Users/xxx/rare_sort" }      # macOS 本地路径
```

### 5. 安装依赖

```bash
# 添加当前平台支持
pixi workspace platform add linux-64    # 服务器
pixi workspace platform add osx-arm64   # macOS

# 安装
pixi install
```

### 6. 启动服务

```bash
pixi run start        # → 0.0.0.0:5000
# 或指定端口：
pixi run uvicorn main:app --host 0.0.0.0 --port 5001
```

### 7. 快速测试

```bash
curl http://localhost:5000/jobs
# → {}
```

---

## 获取输入文件

本服务需要三类输入文件，均来自 OpenRare 管线上游阶段：

### VEP 宽表（必填）

来自 `complete_pipeline` 的 `06_result_sorting/vep_output.sorted.csv`。

该文件包含每条变异-转录本行的 VEP 注释，必须含以下列：

| 列 | 说明 |
|------|------|
| `chrom`, `pos`, `ref`, `alt` | 变异坐标 |
| `gene_symbol` | 基因名（用于 join gene_score 和 PPI） |
| `tx_rank_within_variant` | 转录本排名（Pass 1 过滤用） |
| 6 个 Contributor 所需列 | clinvar、consequence、spliceAI、预测分数、频率、domain |

### gene_phenotype_score.csv（可选）

来自 HPO 表型匹配服务，含 `gene_symbol` 和 `gene_score` 两列：

```
gene_symbol,hgnc_id,gene_score,...
MTM1,HGNC:7448,0.673790,...
PDHA1,HGNC:8806,0.656325,...
```

**获取方式：** 112 服务器 `/mnt/workspace/xlw/phenotype_score/v3/api_runs/{case_id}/outputs/gene_phenotype_score.csv`

### ppi_score.csv（可选）

来自 PPI 网络分析服务，含 `gene` 和 `ppi_final` 两列：

```
gene,in_network,disease_score,...,ppi_final,...
CDC42,True,1.0,...,0.9995992652674639,...
RPL5,True,1.0,...,0.9991529946596006,...
```

**获取方式：** 113 服务器 `/mnt/workspace/luqi/uploads/clean_case_{case_id}/output/ppi_score.csv`

---

## API 文档

| 接口 | 方法 | 描述 |
|------|------|------|
| `/score` | POST | 服务器已有文件评分 |
| `/score/upload` | POST | 上传文件评分 |
| `/status/{job_id}` | GET | 查询任务状态 |
| `/jobs` | GET | 列出全部任务 |

### POST /score

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `input_path` | string | 是 | 服务器上 VEP CSV/Parquet 绝对路径 |
| `gene_score_path` | string | 否 | gene_phenotype_score.csv 路径 |
| `ppi_score_path` | string | 否 | ppi_score.csv 路径 |

```bash
# 仅突变级评分
curl -X POST "http://172.27.206.113:5001/score?input_path=/data/vep.csv"

# 带基因表型 + PPI 加权
curl -X POST "http://172.27.206.113:5001/score?input_path=/data/vep.csv&gene_score_path=/data/gene_phenotype_score.csv&ppi_score_path=/data/ppi_score.csv"
# → {"job_id":"a1b2c3d4","status":"queued"}
```

### POST /score/upload

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `file` | file | 是 | VEP CSV/Parquet 文件 |
| `gene_score_file` | file | 否 | gene_phenotype_score.csv |
| `ppi_score_file` | file | 否 | ppi_score.csv |

```bash
# 上传本地文件 + 基因表型 + PPI
curl -X POST http://172.27.206.113:5001/score/upload \
  -F "file=@vep_output.sorted.csv" \
  -F "gene_score_file=@gene_phenotype_score.csv" \
  -F "ppi_score_file=@ppi_score.csv"
# → {"job_id":"e5f6g7h8","status":"queued","filename":"vep_output.sorted.csv"}
```

### GET /status/{job_id}

| status | 含义 |
|--------|------|
| `queued` | 已入队 |
| `running` | 正在评分，含 `started_at` |
| `done` | 完成，含 `output` 路径和 `elapsed` 秒数 |
| `failed` | 失败，含 `error` 消息 |

```bash
curl http://172.27.206.113:5001/status/a1b2c3d4
# {"status":"done","output":"/tmp/.../ranked.csv","elapsed":2.65}
```

### GET /jobs

```bash
curl http://172.27.206.113:5001/jobs
# → {"a1b2c3d4":{"status":"done","input":"/data/vep.csv","filename":null}}
```

---

## 评分公式

### Pass 1 — 突变级评分

```
evolve_score = Σ (theta_i × calibrate_i(row))    # 6 个 Contributor 加权求和
evolve_rank  = 按 evolve_score 降序，variant 级别去重排名
```

theta 权重（P12_V2）：

| Contributor | theta |
|-------------|-------|
| clinvar_score | 1.291 |
| consequence_score | 1.101 |
| splice_lof_score | 2.027 |
| prediction_score | 0.497 |
| frequency_score | 0.210 |
| domain_score | 3.661 |

### Pass 2 — 基因加权（可选）

**仅 gene_score：**
```
pathogenic_score = evolve_score × √(gene_score)
```

**gene_score + ppi_score：**
```
pathogenic_score = evolve_score × √(gene_score) × √(ppi_final)
```

**不加权（默认）：**
```
pathogenic_score = evolve_score
```

`pathogenic_rank` 始终按 `pathogenic_score` 降序重排。未匹配基因的 `gene_score` / `ppi_final` 为 0，排末尾。

---

## 使用示例

### 完整端到端流程

```bash
# 1. 上传评分（带 gene_score + PPI）
curl -X POST http://172.27.206.113:5001/score/upload \
  -F "file=@vep_output.sorted.csv" \
  -F "gene_score_file=@gene_phenotype_score.csv" \
  -F "ppi_score_file=@ppi_score.csv"
# → {"job_id":"abc12345","status":"queued","filename":"vep_output.sorted.csv"}

# 2. 轮询状态
curl http://172.27.206.113:5001/status/abc12345
# → {"status":"done","output":"/tmp/tmpv7v2n4tu/ranked.csv","elapsed":2.07}

# 3. 查看排名 top 10
head -11 /tmp/tmpv7v2n4tu/ranked.csv | cut -d',' -f1-5,evolve_score,pathogenic_score,pathogenic_rank
```

### 输出列

输出 CSV 始终含：原始 VEP 全部列 + `evolve_score` + `evolve_rank` + `pathogenic_score` + `pathogenic_rank`。

提供 gene_score 时额外含 `gene_score`。提供 ppi_score 时额外含 `ppi_final`。

### CLI 直接调用（无需启动服务）

```bash
pixi run python pipeline.py /data/vep.csv \
  --output /data/ranked.csv \
  --gene-score /data/gene_phenotype_score.csv \
  --ppi-score /data/ppi_score.csv
```

---

## 项目结构

```text
pixi_rare_sort_fastapi/
├── main.py          # FastAPI 入口（4 个端点 + 异步任务队列）
├── pipeline.py       # 评分流水线（Pass 1 特征提取 → Pass 2 duckdb JOIN 排序）
├── dataio.py         # 宽表 I/O 层（列裁剪 + 谓词下推 + 分块流式读取）
├── pixi.toml         # Pixi 项目清单（conda-forge 依赖 + rare_sort pypi 路径）
├── pixi.lock         # 锁定的依赖版本（可复现）
└── README.md
```

| 文件 | 作用 |
|------|------|
| `main.py` | FastAPI 服务，内存字典管理任务队列，支持同步（/score）和上传（/score/upload）两种评分入口 |
| `pipeline.py` | 核心流水线：Pass 1 Python 逐块特征提取 + 加权排名，Pass 2 duckdb SQL 全表 join + 排序导出 |
| `dataio.py` | 大规模宽表 I/O，自动选择引擎（duckdb > polars > pyarrow > pandas），列投影减少磁盘读取 |
| `pixi.toml` | 声明所有依赖（Python 3.11+、FastAPI、uvicorn、duckdb、pyarrow、pandas、numpy），全部来自 conda-forge；`rare_sort` 通过本地路径安装 |
| `pixi.lock` | 锁定所有依赖版本，保证跨机器可复现 |

### 依赖来源

| 包 | 来源 | 用途 |
|---|------|------|
| fastapi, uvicorn, python-multipart | conda-forge | Web 服务与文件上传 |
| duckdb | conda-forge | Pass 2 全表 JOIN + 排序导出（纯 SQL，不经过 Python） |
| pyarrow, pandas, numpy | conda-forge | Pass 1 数据帧与特征矩阵运算 |
| rare_sort | pypi（本地路径） | 评分核心：Contributor registry、theta 加权、rank_units |
