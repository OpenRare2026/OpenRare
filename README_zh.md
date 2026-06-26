# OpenRare 
![last commit](https://img.shields.io/badge/last_commit-2026.06.26-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)
![Badge](https://hitscounter.dev/api/hit?url=https%3A%2F%2Fgithub.com%2FOpenRare2026%2FOpenRare&label=Visitors&icon=github&color=%23198754&message=&style=flat&tz=UTC)


<div align="center">
  <img src="./OpenRare.JPG" alt="OpenRare 标志" width="500">
</div>

[🇨🇳 中文版本](README_zh.md) | [🇬🇧 English Version](README.md)

---

## OpenRare 罕见病 Agent

**面向罕见病变异优先级排序的可解释 AI 系统**

Rare Disease Agent 是一个面向罕见病诊断场景的开源基因分析系统。

我们的目标不是替代临床医生进行诊断，而是帮助医生在海量基因变异中更高效地发现最有可能解释患者表型的候选致病变异，并提供可追溯、可解释、可审计的证据链。

系统融合患者临床表现、基因测序数据、生物医学知识库以及 AI Agent 技术，构建从症状理解、变异注释、致病性排序到报告生成的完整分析流程。

---

## 环境配置（Pixi）

在仓库根目录安装一次，统一管理各模块：

```bash
cp modules/pipeline/.env.example modules/pipeline/.env   # 配置外部数据路径
pixi install
pixi run pipeline-test    # 或 pixi run api
```

常用任务（根目录 `pixi.toml`）：

| 任务 | 说明 |
|------|------|
| `pipeline-test` | 完整流程冒烟测试 |
| `api` | 启动 Full Pipeline API |
| `api-test` | API 集成测试 |
| `vep-dry-run` | VEP 配置 dry-run |
| `vep-setup-plugins` / `vep-verify-plugins` | VEP 插件安装与校验 |

也可仅在 pipeline 子目录内开发：`cd modules/pipeline && pixi install && pixi run pipeline-test`。
PPI 模块可独立运行：`cd modules/pixi_ppi_score && pixi install && pixi run serve`。

## Pipeline 模块

主流程代码位于 [`modules/pipeline/`](modules/pipeline/README.md)。详见 [modules/pipeline/README.md](modules/pipeline/README.md)。  

## 表型关联模块
表型关联评分模块代码位于[`modules/pixi_phenotype_score`](modules/pixi_phenotype_score/README.md)。详见 [modules/pixi_phenotype_score/README.md](modules/pixi_phenotype_score/README.md)。

## PPI 评分模块

PPI 评分服务位于 [`modules/pixi_ppi_score/`](modules/pixi_ppi_score/README.md)，支持 phenotype-gene CSV、VEP CSV 和 HPO 输入，输出 PPI 评分表与融合后的 final score。

PPI 外部数据库可从仓库根目录一键准备：`pixi run ppi-download-data && pixi run ppi-check-data`。需要交给其他 Agent 执行时，可直接使用 [`modules/pixi_ppi_score/docs/DATA_SETUP_PROMPT.md`](modules/pixi_ppi_score/docs/DATA_SETUP_PROMPT.md)。

## RAG-HPO 模块

LLM + RAG 驱动的临床表型自动提取系统，从任意语言病历中提取 Human Phenotype Ontology (HPO) 术语。代码位于 [`modules/pixi_RAG-HPO/`](modules/pixi_RAG-HPO/README.md)。

## Rare Sort 模块

罕见病变异排序评分服务，对 VEP 宽表进行突变级评分，可选叠加基因表型加权和 PPI 网络加权。代码位于 [`modules/pixi_rare_sort_fastapi/`](modules/pixi_rare_sort_fastapi/README.md)。

## RareSystem 模块

全栈遗传诊断系统，支持多类型变异检测（SNV/INDEL/STR/CNV）、ACMG 自动分级、双轨报告及基于 RAG 的智能问答。后端 FastAPI + 前端 React 18。代码位于 [`modules/RareSystem/`](modules/RareSystem/README.md)。

## 报告生成模块

基因组变异分析报告服务位于 [`modules/pixi_report/`](modules/pixi_report/README.md)，基于排序宽表、临床表型与 HPO 术语，通过 FastAPI 流式或命令行生成可追溯的分析报告。

---

## 统一入口（Gateway）

所有模块通过 Gateway 统一启动和管理，对外暴露单一端口（8100）。

```bash
# 安装 gateway 环境
pixi install -e gateway

# 一键启动所有模块（守护进程）：
setsid pixi run -e gateway up > /tmp/openrare_gateway.log 2>&1 & disown

# 检查状态：
curl http://127.0.0.1:8100/health
```

Gateway 会为每个模块启动独立的 pixi 子进程，各模块可使用不同的 Python 版本和依赖，互不冲突。

### 端口映射

| 服务 | 端口 | 说明 |
|------|------|------|
| gateway | 8100 | 统一入口 |
| RAG-HPO | 5001 | HPO 提取 API |
| pipeline | 5002 | VEP 注释 API |
| phenotype_score | 5003 | 表型评分 API |
| ppi_score | 5004 | PPI 评分 API |
| rare_sort | 5005 | 变异排序 API |
| report | 5006 | 报告生成 API |
| RareSystem | 18000 | 全栈诊断系统 |

---

## 模块健康检查（Doctor）

```bash
pixi run doctor
```

检查所有模块的运行就绪状态：环境变量、数据文件、代码可导入性。只读诊断，不修改任何模块代码。

## 全流程编排（Pipeline Runner）

串联全部 6 个分析步骤：

```
HPO RAG → VEP 注释 → 表型评分 → PPI 评分 → 变异排序 → 报告生成
```

```bash
# 启动所有服务后，运行完整流程：
pixi run -e gateway pipeline-full \
  -v /path/to/sample.vcf \
  -t "患者症状描述" \
  -o ./output \
  --chromosomes 1-22
```

---

## 完整部署步骤

### 1. 安装所有模块

```bash
git clone <repo-url> && cd pixi_openrare_test

for m in pipeline pixi_ppi_score pixi_phenotype_score pixi_RAG-HPO \
         pixi_rare_sort_fastapi pixi_report RareSystem; do
    pixi install -m modules/$m/pixi.toml
done
pixi install -e gateway
```

### 2. 配置数据路径

**pipeline** — VEP 缓存、参考基因组、注释数据库（~50 GB）：

```bash
cp modules/pipeline/.env.example modules/pipeline/.env
# 编辑 modules/pipeline/.env，设置：
#   OPENRARE_DATA_ROOT        — VEP 缓存和插件目录
#   OPENRARE_PUBLIC_DATA_ROOT — 公共参考数据（HGNC、假基因数据库）
#   FULL_PIPELINE_REF_DIR     — Beagle phasing 参考面板
#   FULL_PIPELINE_BEAGLE_JAR  — Beagle JAR 路径
```

OPENRARE_PUBLIC_DATA_ROOT 需包含以下子目录：
```
$OPENRARE_PUBLIC_DATA_ROOT/
├── phenotype_hpo_v1/hgnc_complete_set.txt
└── Pseudogene/
    ├── GENCODE/release_49/gencode.v49.2wayconspseudos.gtf.gz
    └── Pseudogene.org/Human90/Human90.txt
```

**ppi_score** — HGNC、HPO 本体、OMIM、StringDB（~5 GB）：

```bash
cp modules/pixi_ppi_score/.env.example modules/pixi_ppi_score/.env
# 设置 RARE_PPI_DATA_DIR 指向包含 hgnc_complete_set.txt、hp.obo 等文件的目录
# 也可通过 pixi run ppi-download-data 自动下载
```

**phenotype_score** — 链接或下载外部数据：

```bash
cd modules/pixi_phenotype_score
ln -sf /path/to/external_data external_data
```

**RAG-HPO** — 配置 LLM API key 并构建向量数据库：

```bash
cp modules/pixi_RAG-HPO/.env.example modules/pixi_RAG-HPO/.env
# 编辑 .env，设置 RAG_HPO_API_KEY、RAG_HPO_BASE_URL、RAG_HPO_MODEL

# 构建 FAISS 向量数据库（需联网下载 SapBERT 模型，约 2.5 GB）：
cd modules/pixi_RAG-HPO && pixi run build-db
```

### 3. 启动服务

```bash
setsid pixi run -e gateway up > /tmp/openrare_gateway.log 2>&1 & disown
curl http://127.0.0.1:8100/health
pixi run doctor
```

### 4. 停止

```bash
pkill -f "gateway.main"
```

---

## 数据下载参考

| 数据 | 来源 |
|------|------|
| VEP 缓存与插件 | [Ensembl VEP](https://useast.ensembl.org/info/docs/tools/vep/script/vep_cache.html) |
| HGNC 完整数据集 | <https://www.genenames.org/download/> |
| HPO 本体 (hp.obo) | <https://github.com/obophenotype/human-phenotype-ontology> |
| OMIM | <https://www.omim.org/downloads>（需许可） |
| Orphanet | <https://www.orphadata.com/> |
| StringDB | <https://string-db.org/> |
| ClinVar | <https://ftp.ncbi.nlm.nih.gov/pub/clinvar/> |
| CADD | <https://cadd.gs.washington.edu/download> |
| SpliceAI | <https://github.com/Illumina/SpliceAI> |
| GTEx | <https://gtexportal.org/home/datasets> |
| SapBERT 模型 | <https://huggingface.co/pritamdeka/SapBERT-mnli-snli-scinli-scitail-mednli-stsb> |

---

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| 安装报 `unsupported-platform` | pixi.toml 缺少当前平台 | `pixi workspace platform add linux-64` |
| Pipeline 作业立即失败 | `.env` 未配置 | 从 `.env.example` 创建 `.env`，确认路径存在 |
| `FileNotFoundError` 含 Pseudogene | OPENRARE_PUBLIC_DATA_ROOT 下缺少子目录 | 确保 Pseudogene/ 和 phenotype_hpo_v1/ 子目录存在 |
| SSH 断开后 gateway 退出 | `nohup` 不保护 pixi 子进程 | 使用 `setsid ... & disown` |
| 模块启动失败 (exit code 1) | 缺少数据或端口冲突 | 运行 `pixi run doctor` 检查 |
| RAG-HPO 启动卡住 | 向量 DB 未构建或模型未缓存 | 运行 `pixi run build-db` |
| 端口已被占用 | 其他进程占用 | 修改 `gateway/src/gateway/main.py` → MODULES 中的端口
