# rare_sort FastAPI

基于 Pixi 的罕见病变异排序评分服务，对 VEP 宽表（CSV/Parquet）进行打分、排序，输出含 `evolve_score` 和 `evolve_rank` 的结果 CSV。

## 目录

- [环境要求](#环境要求)
- [安装与快速开始](#安装与快速开始)
- [API 文档](#api-文档)
- [使用示例](#使用示例)
- [项目结构](#项目结构)

---

## 环境要求

| 依赖 | 说明 |
|------|------|
| Pixi >= 0.39 | 包管理与环境隔离（[安装指南](https://pixi.prefix.dev/latest/#installation)） |
| Python >= 3.11 | 由 Pixi 自动安装 |

## 安装与快速开始

```bash
# 1. 进入项目目录
cd pixi_rare_sort_fastapi

# 2. 安装所有依赖（含 rare_sort 本地包）
pixi install

# 3. 启动服务（默认端口 5000）
pixi run start
```

启动成功后会看到：

```
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

## 快速测试

```bash
# 健康检查
curl http://localhost:5000/jobs
# → {}

# 用服务器已有文件评分
curl -X POST "http://localhost:5000/score?input_path=/data/vep.csv"
# → {"job_id":"a1b2c3d4","status":"queued"}
```

---

## API 文档

| 接口 | 方法 | 描述 |
|------|------|------|
| `/score` | POST | 对服务器上已有文件发起评分任务 |
| `/score/upload` | POST | 上传本地文件并发起评分任务 |
| `/status/{job_id}` | GET | 查询任务状态与结果 |
| `/jobs` | GET | 列出全部任务 |

### POST /score

对服务器上已有的 CSV 或 Parquet 文件进行评分。

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `input_path` | string | 是 | 服务器上的文件绝对路径（query 参数） |

```bash
curl -X POST "http://localhost:5000/score?input_path=/data/vep.csv"
# → {"job_id":"a1b2c3d4","status":"queued"}
```

### POST /score/upload

上传本地文件并评分。文件以 8MB 块写入临时目录。

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `file` | file | 是 | 上传的 CSV 或 Parquet 文件（multipart/form-data） |

```bash
curl -F "file=@vep_output.csv" http://localhost:5000/score/upload
# → {"job_id":"e5f6g7h8","status":"queued","filename":"vep_output.csv"}
```

### GET /status/{job_id}

查询评分任务的执行状态。

**状态说明：**

| status | 含义 |
|--------|------|
| `queued` | 已入队，等待执行 |
| `running` | 正在评分，含 `started_at` |
| `done` | 评分完成，含 `output` 路径和 `elapsed` 秒数 |
| `failed` | 评分失败，含 `error` 消息 |

```bash
curl http://localhost:5000/status/a1b2c3d4
# running → {"status":"running","input":"/data/vep.csv","started_at":1718700000.0}
# done    → {"status":"done","output":"/tmp/.../ranked.csv","elapsed":136.0}
# failed  → {"status":"failed","error":"file not found"}
```

### GET /jobs

列出所有任务及其状态摘要。

```bash
curl http://localhost:5000/jobs
# → {"a1b2c3d4":{"status":"done","input":"/data/vep.csv","filename":null}}
```

---

## 使用示例

### 完整流程

```bash
# 1. 上传本地 VEP CSV 并发起评分
curl -F "file=@vep_output.csv" http://localhost:5000/score/upload
# → {"job_id":"abc12345","status":"queued","filename":"vep_output.csv"}

# 2. 轮询任务状态
curl http://localhost:5000/status/abc12345
# → {"status":"running","input":"/tmp/.../vep_output.csv","started_at":1720000000.0}

# 3. 任务完成后获取结果路径
curl http://localhost:5000/status/abc12345
# → {"status":"done","output":"/tmp/.../ranked.csv","elapsed":142.3}

# 4. 查看排名
head /tmp/.../ranked.csv
```

### 输出格式

结果 CSV 包含原始 VEP 全部列 + `evolve_score`（评分）+ `evolve_rank`（排名），按 `evolve_score` 降序排列。

---

## 项目结构

```text
pixi_rare_sort_fastapi/
├── main.py          # FastAPI 服务（4 个端点 + 异步任务队列）
├── pipeline.py       # 评分流水线：两阶段（特征提取 → duckdb JOIN 排序）
├── dataio.py         # 宽表 I/O：列裁剪 + 谓词下推 + 分块流式读取
├── pixi.toml         # Pixi 项目清单（依赖、通道、任务）
├── pixi.lock         # 锁定的依赖版本（保证可复现）
└── README.md
```

| 文件 | 作用 |
|------|------|
| `main.py` | FastAPI 入口，定义 `/score`、`/score/upload`、`/status/{job_id}`、`/jobs` 四个端点，内存字典管理任务队列 |
| `pipeline.py` | 核心评分流水线，调用 `rare_sort` 的 registry + theta 权重进行特征提取和排序 |
| `dataio.py` | 大规模宽表 I/O 层，支持 duckdb / polars / pyarrow / pandas 四种引擎，按需列投影 |
| `pixi.toml` | 声明 Python 3.11+、FastAPI、uvicorn、duckdb、pyarrow、pandas、numpy 等依赖，全部来自 conda-forge |

### 依赖来源

| 包 | 来源 | 用途 |
|---|------|------|
| fastapi, uvicorn, python-multipart | conda-forge | Web 框架与文件上传 |
| duckdb | conda-forge | 列存 SQL 引擎（PASS 2 排序导出） |
| pyarrow, pandas, numpy | conda-forge | 数据帧处理与特征矩阵运算 |
| rare_sort | pypi (本地路径) | 罕见病评分核心库（registry、theta 权重、rank_units） |
