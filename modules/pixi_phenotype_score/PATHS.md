# 项目路径清单

本文统一记录项目配置、输入、外部数据库、中间文件、运行状态和最终输出。表中的路径全部以项目根目录 `.` 为基准，不依赖服务器安装位置。

## 路径原则

- `config/paths.toml` 中的所有值必须是项目相对路径；配置为绝对路径时程序直接报错。
- 程序内部可将相对路径解析为运行时绝对路径访问文件，但源码、配置、状态 JSON、摘要和日志不保存服务器绝对路径。
- `external_data/`、`.pixi/` 和 `runtime/` 不上传 GitHub。
- API 上传目录、状态文件、日志和结果在首次运行时按需创建。
- 外部数据库通过 `external_data/` 提供；当前服务器使用相对软链接复用现有数据。

## 项目与配置

| 相对路径 | 类型 | 用途 | GitHub |
|---|---|---|---|
| `pixi.toml` | 输入配置 | Pixi 直接依赖和任务定义 | 提交 |
| `pixi.lock` | 生成配置 | 完整依赖锁定结果 | 提交 |
| `requirement.toml` | 审计输入 | 原 HPO Conda 环境依赖盘点 | 提交 |
| `config/paths.example.toml` | 示例配置 | 可复制的相对路径模板 | 提交 |
| `config/paths.toml` | 部署配置 | 当前部署实际路径配置 | 忽略 |
| `.pixi/` | 生成目录 | Pixi 项目环境，约 400 MB | 忽略 |

## 示例输入

| 相对路径 | 格式 | 用途 | 生命周期 |
|---|---|---|---|
| `examples/test.P002.csv` | CSV | 默认变异测试输入 | 固定示例 |
| `examples/hpo_test.txt` | 文本 | 默认患者 HPO 输入 | 固定示例 |

API 上传的真实输入不会覆盖示例文件，而是保存到任务独立目录。

## 外部数据库与索引

| 相对路径 | 数据源 | 用途 |
|---|---|---|
| `external_data/hpo/hp.obo` | HPO | HPO 本体和层级关系 |
| `external_data/hpo/phenotype.hpoa` | HPO | disease-HPO 注释和 IC 计算 |
| `external_data/hpo/genes_to_disease.txt` | HPO | gene-disease 关联 |
| `external_data/hgnc/hgnc_complete_set.txt` | HGNC | 基因符号及别名归一化 |
| `external_data/mondo/mondo-rare.obo` | MONDO | OMIM/Orphanet 疾病映射 |
| `external_data/omim/omim_20250411.sqlite3` | OMIM | OMIM 疾病本地查询 |
| `external_data/orphanet/Orphapackets/` | Orphanet | Orphapacket YAML 原始数据 |
| `external_data/indexes/orpha_gene_profiles.pkl` | 派生索引 | Orphanet gene-profile 加速索引 |

数据库版本、大小、许可、官方下载地址和当前服务器相对软链接映射见 [EXTERNAL_DATA.md](EXTERNAL_DATA.md)。

## 命令行运行路径

默认执行 `pixi run score` 时：

| 相对路径 | 类型 | 用途 |
|---|---|---|
| `runtime/results/gene_phenotype_score.csv` | 最终输出 | 基因级评分 |
| `runtime/results/variant_phenotype_score.csv` | 最终输出 | 变异级评分 |
| `runtime/results/run_summary.json` | 运行摘要 | 输入、输出、数量和参数摘要 |

指定 `--outdir` 时，三个文件写入指定的项目相对目录。

## API 运行路径

首次运行 `pixi run serve` 自动创建：

| 相对路径 | 类型 | 用途 | 清理建议 |
|---|---|---|---|
| `runtime/logs/api-7773.log` | 服务日志 | Uvicorn 启动和访问日志 | 定期轮转 |
| `runtime/api-7773.pid` | 服务状态 | 当前 API Python PID；服务停止时自动删除 | 不手动保留 |

每次 `POST /runs` 创建独立任务目录：

```text
runtime/api_runs/{uid}/
├── inputs/
│   ├── {uploaded_variant_file}
│   └── {uploaded_hpo_file_or_hpo_list.txt}
├── outputs/
│   ├── README.md
│   ├── gene_phenotype_score.csv
│   └── variant_phenotype_score.csv
├── run.log
└── status.json
```

| 相对路径 | 类型 | 用途 | 生命周期 |
|---|---|---|---|
| `runtime/api_runs/{uid}/inputs/` | 输入副本 | 隔离每个任务的上传文件 | 随任务清理 |
| `runtime/api_runs/{uid}/status.json` | 中间状态 | 队列位置、阶段、摘要和文件列表 | 随任务保留 |
| `runtime/api_runs/{uid}/status.json.tmp` | 原子写临时文件 | 防止状态文件写到一半 | 每次写入后立即替换，不应残留 |
| `runtime/api_runs/{uid}/run.log` | 任务日志 | 评分过程和错误诊断 | 随任务保留 |
| `runtime/api_runs/{uid}/outputs/README.md` | 最终输出 | 随结果提供的使用说明 | 随任务保留 |
| `runtime/api_runs/{uid}/outputs/gene_phenotype_score.csv` | 最终输出 | 基因级评分 | 随任务保留 |
| `runtime/api_runs/{uid}/outputs/variant_phenotype_score.csv` | 最终输出 | 变异级评分 | 随任务保留 |
| `runtime/api_runs/{uid}/outputs/run_summary.json` | 短暂中间文件 | 评分脚本与 API 之间传递摘要 | API 读取后立即删除 |

## 索引重建中间文件

显式使用 `--rebuild-orpha-index` 时：

| 相对路径 | 类型 | 用途 | 生命周期 |
|---|---|---|---|
| `external_data/indexes/orpha_gene_profiles.pkl.tmp` | 原子写临时文件 | 新索引完整写入后再替换正式索引 | 成功后立即替换，不应残留 |
| `external_data/indexes/orpha_gene_profiles.pkl` | 派生输出 | 正式 Orphanet 索引 | 按数据库版本更新 |

当前服务器默认复用已有索引，不执行重建，避免修改共享数据库资源。

## 清理边界

- 可安全删除：过期的 `runtime/api_runs/{uid}/`、不再需要的 `runtime/results/` 和 Python 缓存。
- 服务运行时保留：`runtime/logs/api-7773.log`、`runtime/api-7773.pid`。
- 不自动删除：`.pixi/`、`external_data/`、`pixi.lock`。
- 禁止当作临时文件清理：任何 `external_data/` 正式数据库或索引。
