# OpenRare Pipeline — 罕见病变异注释与排序全流程

从患者 VCF 出发，串联 Beagle phasing、VCF 前置处理、假基因注释、VEP 多插件注释、INFO 回填与致病性排序，一键产出可解读的排序 CSV；支持命令行与 FastAPI 两种调用方式。

## 目录

- [安装与快速开始](#安装与快速开始)
- [使用示例](#使用示例)
- [API 文档](#api-文档)
- [命令行参数](#命令行参数)
- [流程说明](#流程说明)
- [输出文件](#输出文件)
- [项目结构](#项目结构)
- [环境变量与外部数据](#环境变量与外部数据)
- [更多文档](#更多文档)

---

## 安装与快速开始

### 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Linux x86_64 |
| [Pixi](https://pixi.sh/) | 用于安装运行环境（推荐） |
| Python | ≥ 3.11（pixi 自动提供） |
| Java | ≥ 17（pixi 提供 openjdk，供 Beagle 使用） |
| 磁盘 | VEP cache + 注释库较大，建议预留数十 GB（见 [vep_runner README](modules/vep_runner/README.md)） |

Pixi 环境包含：`ensembl-vep 115.x`、`bcftools`、`openjdk`、`fastapi`、`uvicorn` 等（见本目录 [`pixi.toml`](pixi.toml)）。

### 1. 克隆并安装依赖

```bash
cd /path/to/OpenRare/modules/pipeline
pixi install
```

### 2. 配置外部数据路径

大型数据库（VEP cache、CADD、phasing 参考等）不随仓库提交，通过本目录 `.env` 配置：

```bash
cp .env.example .env
# 编辑 .env，至少填写以下四项：
#   OPENRARE_DATA_ROOT
#   OPENRARE_PUBLIC_DATA_ROOT
#   FULL_PIPELINE_REF_DIR
#   FULL_PIPELINE_BEAGLE_JAR
```

`pixi run`、Shell 脚本与 Python 会自动加载 `.env`；shell 中已 `export` 的变量不会被覆盖。

### 3.（可选）安装 VEP 插件

若 `OPENRARE_DATA_ROOT` 下尚无插件 `.pm` / LoFTEE：

```bash
pixi run vep-setup-plugins          # 下载插件 Perl 模块 + LoFTEE
pixi run vep-verify-plugins         # 校验数据文件与 tabix 索引
```

安装目标目录取决于 `.env` 中的 `OPENRARE_DATA_ROOT`，详见 [modules/vep_runner/README.md](modules/vep_runner/README.md)。

### 4. 一键回归测试

```bash
pixi run pipeline-test    # P001 样本、chr1、约 2 分钟量级（视机器而定）
```

成功标志：生成 `tmp/openrare_pipeline_test/06_result_sorting/vep_output.sorted.csv`。

### 常用 Pixi Task

| Task | 说明 |
|------|------|
| `pixi run vep-dry-run` | 打印 VEP 命令（含插件），不实际运行 |
| `pixi run vep-setup-plugins` | 安装 VEP 插件 .pm + LoFTEE（可选 cache） |
| `pixi run vep-verify-plugins` | 校验插件数据与索引 |
| `pixi run pipeline-test` | P001 + chr1 全流程回归 |
| `pixi run api` | 启动 FastAPI（默认 `127.0.0.1:18901`） |
| `pixi run api-test` | 测试 `/health`、`/run`、`/run-upload` |

---

## 使用示例

### 命令行：最小调用

```bash
cd /path/to/OpenRare/modules/pipeline
pixi run bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/patient.vcf.gz \
  --out-dir /path/to/output \
  --fork 4
```

带患者 HPO（影响 HPO → 组织 → GTEx 加权的转录本选择）：

```bash
pixi run bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/patient.vcf.gz \
  --out-dir /path/to/output \
  --fork 4 \
  --hpo-id HP:0001250
```

### 命令行：预期输出片段

流程结束后终端会打印各步产物路径，并生成汇总文件：

```text
step                          path
original_input_vcf            /path/to/patient.vcf.gz
...
vep_csv                       /path/to/output/06_result_sorting/vep_output.sorted.csv
full_log                      /path/to/output/logs/full_pipeline.log
```

最终 CSV 表头示例（列较多，此处仅示意）：

```text
#CHROM,POS,REF,ALT,...,Gene,Consequence,CLIN_SIG,...,rank_score,rank_reason
chr1,1197557,G,A,...,TTLL10,missense_variant,...,selected,...,consequence=missense_variant(+15); ...
```

### 启动 API 服务

```bash
pixi run api
# 或指定端口：FULL_PIPELINE_API_PORT=18901 pixi run api
```

健康检查：

```bash
curl -s http://127.0.0.1:18901/health | python3 -m json.tool
```

### API：JSON 提交任务

```bash
curl -s -X POST http://127.0.0.1:18901/run \
  -H 'Content-Type: application/json' \
  -d '{
    "input_vcf": "/path/to/patient.vcf.gz",
    "output_dir": "/path/to/output",
    "fork": 4,
    "hpo_id": "HP:0001250"
  }'
```

### API：上传 VCF

```bash
curl -s -X POST http://127.0.0.1:18901/run-upload \
  -F 'input_vcf=@/path/to/patient.vcf.gz' \
  -F 'fork=4' \
  -F 'chromosomes=1'
```

查询任务状态与日志：

```bash
curl -s http://127.0.0.1:18901/jobs/<job_id>
curl -s http://127.0.0.1:18901/jobs/<job_id>/log
```

---

## API 文档

默认地址：`http://127.0.0.1:18901`（`FULL_PIPELINE_API_PORT`，默认 `18901`）。

### 端点一览

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 服务状态、默认资源路径、入口脚本是否存在 |
| `POST` | `/run` | JSON 提交任务；`input_vcf` 为服务器上的路径 |
| `POST` | `/run-upload` | multipart 上传 VCF 并提交任务 |
| `GET` | `/jobs/{job_id}` | 查询任务状态、命令、输出目录 |
| `GET` | `/jobs/{job_id}/log` | 查看任务运行日志 |

### `POST /run` 请求体（`RunRequest`）

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|:----:|--------|------|
| `input_vcf` | string | 是 | — | 输入 VCF/VCF.GZ 路径 |
| `output_dir` | string | 否 | `api_jobs/<job_id>/output` | 流水线输出目录 |
| `fork` | int | 否 | `1` | VEP `--fork` |
| `hpo_id` | string | 否 | `""` | HPO ID，逗号分隔多个 |
| `sample_id` | string | 否 | 自动 | 样本名 |
| `chromosomes` | string | 否 | `1-22` | 染色体范围，如 `1`、`1,3,5` |
| `ref_dir` | string | 否 | `.env` | Beagle CHN 参考 panel |
| `beagle_jar` | string | 否 | `.env` | Beagle JAR 路径 |
| `keep_raw_vep` | bool | 否 | 保留 | `true`/`false` |
| `dry_run` | bool | 否 | `false` | 仅打印命令不执行 |

完整高级字段与命令行参数一一对应，见 [命令行参数](#命令行参数) 与 [complete_pipeline/README.md](complete_pipeline/README.md)。

### `POST /run` 响应（`RunResponse`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 任务 ID |
| `status` | string | 初始为 `queued`，随后 `running` / `succeeded` / `failed` |
| `status_url` | string | 状态查询路径，如 `/jobs/<job_id>` |
| `output_dir` | string | 本次流水线 `--out-dir` |

示例：

```json
{
  "job_id": "a1b2c3d4e5f6...",
  "status": "queued",
  "status_url": "/jobs/a1b2c3d4e5f6...",
  "output_dir": "/path/to/OpenRare/modules/pipeline/complete_pipeline/api_jobs/a1b2c3d4.../output"
}
```

### `GET /jobs/{job_id}` 响应（成功完成后）

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | `succeeded` / `failed` / `running` |
| `output_dir` | string | 输出目录 |
| `summary` | object | 各步产物路径（来自 `full_pipeline.outputs.tsv`） |
| `error` | string | 失败时的错误信息 |

### API 默认目录

未传 `output_dir` 时：

```text
modules/pipeline/complete_pipeline/api_jobs/<job_id>/
├── status.json
├── api_run.log
├── input/          # /run-upload 上传的 VCF
└── output/         # 流水线输出（结构同 CLI --out-dir）
    └── 06_result_sorting/vep_output.sorted.csv
```

可通过 `.env` 设置 `FULL_PIPELINE_API_JOBS_DIR` 修改 jobs 根目录。

---

## 命令行参数

入口：`scripts/run_full_pipeline.sh`

| 参数 | 常用 | 默认值 | 说明 |
|------|:--:|--------|------|
| `--input-vcf FILE` | 是 | — | 患者 VCF（`.vcf` / `.vcf.gz`） |
| `--out-dir DIR` | 是 | — | 输出根目录 |
| `--fork N` | 是 | `1` | VEP fork 数 |
| `--hpo-id ID` | 是 | 空 | HPO ID，逗号分隔 |
| `--sample-id ID` | 否 | `auto` | 样本名 |
| `--chromosomes SPEC` | 否 | `1-22` | 如 `1`、`1,3,5` |
| `--ref-dir DIR` | 否 | `$FULL_PIPELINE_REF_DIR` | Beagle 参考 panel |
| `--beagle-jar FILE` | 否 | `$FULL_PIPELINE_BEAGLE_JAR` | Beagle JAR |
| `--java-bin PATH` | 否 | `$JAVA_BIN` | Java 可执行文件 |
| `--input-assembly SPEC` | 否 | `auto` | `auto` / `GRCh37` / `GRCh38`；GRCh37 时在 phasing 前 liftover |
| `--keep-raw-vep yes\|no` | 否 | `yes` | 保留 `04_vep/raw_vep.tsv` |
| `--dry-run` | 否 | 关闭 | 只打印命令 |

```bash
pixi run bash scripts/run_full_pipeline.sh --help
```

---

## 流程说明

| 步骤 | 目录 | 功能 | 主输出 |
|------|------|------|--------|
| 00 | `00_input/` | 输入 VCF 规范化（bgzip + 索引） | `*.vcf.gz` |
| 00b | `00_liftover/` | GRCh37→GRCh38 liftover（`--input-assembly` 触发） | `output.grch38.norm.vcf.gz` |
| 01 | `01_phasing/` | Beagle + CHN 参考 phasing/ref-support | `*.refsupport.vcf.gz` |
| 02 | `02_vcf_preprocessing/` | VAF、cCRE、ncRNA 注释 | `preprocessed.regulatory.vcf.gz` |
| 03 | `03_pseudogene_annotation/` | 假基因 INFO 注释 | `preprocessed.pseudogene_annotated.vcf.gz` |
| 04 | `04_vep/` | VEP + CADD/SpliceAI/dbNSFP/LoFTEE/ClinVar 等 | `vep_output.base.csv` |
| 05 | `05_vcf_info_to_csv/` | VCF INFO 回填到 CSV | `vep_output.with_info.csv` |
| 06 | `06_result_sorting/` | 致病性评分排序 | **`vep_output.sorted.csv`** |

---

## 输出文件

主结果：

```text
<out-dir>/06_result_sorting/vep_output.sorted.csv
```

| 路径 | 说明 |
|------|------|
| `<out-dir>/04_vep/vep_output.base.csv` | VEP 基础 CSV |
| `<out-dir>/04_vep/raw_vep.tsv` | VEP 原始 TSV（默认保留） |
| `<out-dir>/05_vcf_info_to_csv/vep_output.with_info.csv` | 含 VCF INFO 列 |
| `<out-dir>/full_pipeline.outputs.tsv` | 各步产物路径索引 |
| `<out-dir>/logs/full_pipeline.log` | 全流程日志 |

流水线**输出**由 `--out-dir` 指定，与 `OPENRARE_DATA_ROOT`（VEP 数据/插件）无关。

---

## 项目结构

```text
modules/pipeline/                    # 本模块（pixi 项目根）
├── pixi.toml
├── .env.example
├── README.md
├── EXTERNAL_PATHS.md
├── scripts/
│   ├── load-env.sh                  # pixi 激活时加载 .env
│   ├── run_full_pipeline.sh         # CLI 全流程入口
│   └── start_full_pipeline_api.sh
├── config/
│   ├── paths.sh
│   └── path_utils.py
├── complete_pipeline/
│   ├── full_pipeline_api.py         # FastAPI 服务
│   └── api_jobs/                    # API 任务目录（gitignore）
├── modules/                         # 各步骤实现
│   ├── phasing_beagle_refsupport/
│   ├── vcf_preprocessing/
│   ├── pseudogene_annotation/
│   ├── vep_runner/
│   ├── vcf_info_to_csv/
│   └── result_sorting/
└── test/
    ├── input/P001.genotyper10000.vcf
    ├── prepare_sites_vcf_with_sample.sh
    └── run_api_integration_test.sh
```

---

## 环境变量与外部数据

| 变量 | 用途 |
|------|------|
| `OPENRARE_DATA_ROOT` | VEP cache、插件、CADD/SpliceAI 等注释库 |
| `OPENRARE_PUBLIC_DATA_ROOT` | 假基因 GENCODE / Pseudogene.org / HGNC |
| `FULL_PIPELINE_REF_DIR` | Beagle CHN reference panel |
| `FULL_PIPELINE_BEAGLE_JAR` | Beagle JAR |
| `JAVA_BIN` | Beagle 用 Java（默认 `java`） |
| `FULL_PIPELINE_API_PORT` | API 端口（默认 `18901`） |
| `FULL_PIPELINE_API_JOBS_DIR` | API 任务根目录 |

完整说明与数据布局：[`EXTERNAL_PATHS.md`](EXTERNAL_PATHS.md)。

VEP 配置 [`modules/vep_runner/config/vep_runner_config.json`](modules/vep_runner/config/vep_runner_config.json) 使用 `${OPENRARE_DATA_ROOT}` 占位符，运行时由 `run_vep_to_csv.py` 展开；VEP 可执行文件从 PATH 解析（pixi 的 `ensembl-vep`）。

---

## 更多文档

| 文档 | 内容 |
|------|------|
| [complete_pipeline/README.md](complete_pipeline/README.md) | API 与 CLI 详细参数 |
| [modules/vep_runner/README.md](modules/vep_runner/README.md) | VEP 插件与注释库安装 |
| [EXTERNAL_PATHS.md](EXTERNAL_PATHS.md) | 外部路径与中间文件说明 |

### HPO 说明

仅支持标准 HPO ID（如 `HP:0001250`），不支持自由文本临床描述。传入后用于 HPO → 组织 → GTEx 表达加权，影响转录本选择；不传时仍会做转录本选择，但无 HPO 组织加权。

### 输入 VCF 说明

- 支持 `.vcf` 与 `.vcf.gz`；未压缩文件会自动 bgzip 到 `<out-dir>/00_input/` 并建索引。
- sites-only VCF（无样本列）可先经 `test/prepare_sites_vcf_with_sample.sh` 补样本列后再跑流程。
