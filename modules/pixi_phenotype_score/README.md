# Phenotype-HPO Score —— 基于 HPO 语义相似度的候选基因表型评分服务

本项目根据患者 HPO 表型与候选基因关联疾病的表型谱计算相似度，输出基因级和变异级评分；Pixi 负责依赖求解、锁定和可复现运行。

> `gene_score` 表示表型解释程度，不等同于变异致病性结论。临床解释仍需结合变异频率、ClinVar、ACMG、遗传模式、家系和临床证据。

## 目录

- [安装与快速开始](#安装与快速开始)
- [外部数据库](#外部数据库)
- [路径管理](#路径管理)
- [命令行使用](#命令行使用)
- [FastAPI 服务](#fastapi-服务)
- [输入与输出](#输入与输出)
- [项目结构](#项目结构)
- [依赖与官方链接](#依赖与官方链接)

## 安装与快速开始

### 环境要求

- Linux x86-64
- [Pixi](https://pixi.prefix.dev/latest/)
- 可用的外部数据库，详见 [EXTERNAL_DATA.md](EXTERNAL_DATA.md)

Pixi 官方安装方式：

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

若服务器到 GitHub Release 的连接受限，也可以通过 Conda Forge 官方包安装独立启动环境，不会修改 HPO 环境：

```bash
conda create -n pixi-cli --override-channels -c conda-forge pixi=0.70.2
conda run -n pixi-cli pixi --version
```

重新进入终端后，在项目根目录执行：

```bash
cp config/paths.example.toml config/paths.toml
pixi install
pixi run check-paths
pixi run test
```

`pixi install` 会生成或使用 `pixi.lock`，环境保存在 `.pixi/`，不需要激活 Conda 环境。

## 外部数据库

模块依赖数据库与派生索引统一放在 `external_data/`：

```text
external_data/
├── hpo/
├── hgnc/
├── mondo/
├── omim/
├── orphanet/
└── indexes/
```

HPO 与 HGNC 是独立数据源，分别配置。完整文件清单、版本、下载地址、许可和服务器复用方式见 [EXTERNAL_DATA.md](EXTERNAL_DATA.md)。

## 路径管理

所有配置、输入、中间文件、运行状态和输出路径见 [PATHS.md](PATHS.md)。提交配置只允许使用项目相对路径，绝对路径会被拒绝。

## 命令行使用

使用默认示例：

```bash
pixi run score
```

指定输入和输出：

```bash
pixi run python src/phenotype_hpo_score.py \
  --config config/paths.toml \
  --input-csv examples/test.P002.csv \
  --hpo-file examples/hpo_test.txt \
  --outdir runtime/results
```

所有相对路径均以项目根目录解析，因此命令不依赖服务器安装位置。

## FastAPI 服务

### 启动

新服务固定使用 7773：

```bash
pixi run serve
```

后台启动示例：

```bash
nohup pixi run serve >/dev/null 2>&1 &
```

启动脚本会按需创建 `runtime/logs/api-7773.log`。

### 健康检查

```bash
curl -s http://127.0.0.1:7773/health
```

### 提交任务

```bash
curl -s -X POST http://127.0.0.1:7773/runs \
  -F file=@examples/test.P002.csv \
  -F hpo_file=@examples/hpo_test.txt
```

返回内容包含 `uid`、状态地址和文件列表地址。任务状态为 `completion` 后可下载结果。

### API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/health` | 服务健康检查 |
| `GET` | `/queue` | 当前运行任务和等待队列 |
| `POST` | `/runs` | 上传变异文件和 HPO，创建评分任务 |
| `GET` | `/runs/{uid}` | 查询任务状态 |
| `GET` | `/runs/{uid}/files` | 获取完成任务的结果文件列表 |
| `GET` | `/runs/{uid}/files/{filename}` | 下载指定结果文件 |

`POST /runs` 主要参数：

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---:|---:|---|
| `file` | CSV/Parquet 文件 | 是 | — | 必须包含 `all_genes` 和 `gene_symbol` |
| `hpo_file` | 文本文件 | 否 | 示例 HPO | 每行一个 HPO ID |
| `hpo_list` | 文本 | 否 | — | 逗号、分号或换行分隔 |
| `min_similarity` | 浮点数 | 否 | `0.20` | 最低语义相似度 |
| `input_format` | 文本 | 否 | `auto` | `auto`、`csv` 或 `parquet` |
| `chunksize` | 整数 | 否 | `100000` | 分块读取行数 |

## 输入与输出

HPO 文件每行一个 `HP:xxxxxxx`。变异文件至少包含：

| 字段 | 用途 |
|---|---|
| `all_genes` | 提取候选基因集合 |
| `gene_symbol` | 将基因评分回填到变异记录 |

每次 API 任务在首次提交时自动创建：

```text
runtime/api_runs/{uid}/
├── inputs/
├── outputs/
│   ├── README.md
│   ├── gene_phenotype_score.csv
│   └── variant_phenotype_score.csv
├── run.log
└── status.json
```

命令行默认输出到 `runtime/results/`。`runtime/` 不进入 GitHub。

## 项目结构

```text
.
├── config/
│   └── paths.example.toml
├── examples/
├── scripts/
├── src/
├── tests/
├── .gitignore
├── EXTERNAL_DATA.md
├── PATHS.md
├── README.md
├── pixi.toml
└── requirement.toml
```

`api_runs/`、`logs/` 和结果目录不预先创建；运行时按需产生。

## 依赖与官方链接

`requirement.toml` 保存原 HPO Conda 环境的依赖审计，`pixi.toml` 保存项目直接依赖，`pixi.lock` 保存完整锁定结果。

| 工具或包 | 用途 | 官方链接 |
|---|---|---|
| Pixi | 环境、任务和锁文件管理 | [Pixi 文档](https://pixi.prefix.dev/latest/) · [安装说明](https://pixi.prefix.dev/latest/installation/) · [Conda Forge 包](https://anaconda.org/conda-forge/pixi) |
| Python 3.12 | 运行时 | [Python](https://www.python.org/downloads/) |
| pandas | CSV/Parquet 分块处理 | [pandas](https://pandas.pydata.org/) |
| PyYAML | Orphapacket YAML 解析 | [PyYAML](https://pyyaml.org/) |
| FastAPI | HTTP API | [FastAPI](https://fastapi.tiangolo.com/) |
| Uvicorn | ASGI 服务 | [Uvicorn](https://www.uvicorn.org/) |
| python-multipart | API 文件上传 | [python-multipart](https://github.com/Kludex/python-multipart) |

项目运行不需要旧 Conda 环境。数据库下载不由安装任务自动触发，避免无审批下载大文件。
