# RAG-HPO

LLM + RAG 驱动的临床表型自动提取系统——从任意语言病历中提取 Human Phenotype Ontology (HPO) 术语。

解决的核心问题：医生不愿意手动从 20,000+ HPO 词条中查找匹配，而这个系统用**中文 LLM + 医学 embedding + RAG 检索**自动完成 90% 的工作。

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![pixi](https://img.shields.io/badge/pixi-0.68+-gold)](https://pixi.prefix.dev/)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 目录

- [5 分钟快速开始](#5-分钟快速开始)
- [使用示例](#使用示例)
- [API 文档](#api-文档)
- [配置参数](#配置参数)
- [项目结构](#项目结构)
- [常用命令](#常用命令)
- [部署](#部署)
- [FAQ](#faq)

---

## 5 分钟快速开始

### 环境要求

- [pixi](https://pixi.prefix.dev/latest/#installation) ≥ 0.68（macOS / Linux）
- 8 GB+ 内存（模型加载需要 ~2.5 GB）
- DeepSeek / Groq / 任意 OpenAI 兼容 API key

### 安装

```bash
git clone https://github.com/wyzBelinda/RAG-HPO.git
cd RAG-HPO

# 安装所有依赖（Python + 14 个包，conda-forge，自动锁定版本）
pixi install
```

### 配置

```bash
cp .env.example .env
# 编辑 .env，填入你的 API key：
#   RAG_HPO_API_KEY=sk-xxx
#   RAG_HPO_BASE_URL=https://api.deepseek.com
#   RAG_HPO_MODEL=deepseek-v4-pro
```

### 启动服务

```bash
pixi run serve
# → Uvicorn running on http://127.0.0.1:8000
```

### 验证

```bash
curl http://localhost:8000/api/v1/health
# → {"status":"ok","model_loaded":true,"queue_size":0}
```

---

## 使用示例

### 中文病历 → HPO 术语

```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H 'Content-Type: application/json' \
  -d '{
    "notes": [
      {
        "patient_id": "P001",
        "clinical_note": "患儿出生时发现左手多指畸形，伴有先天性心脏病房间隔缺损，生长发育迟缓"
      }
    ]
  }'
```

返回 `job_id`，等待完成后查询：

```bash
curl http://localhost:8000/runs/{job_id}
```

### 输出

```json
{
  "status": "completed",
  "elapsed_seconds": 13.4,
  "results": [
    {"patient_id": "P001", "phrase": "Atrial septal defect",  "hpo_id": "HP:0001631"},
    {"patient_id": "P001", "phrase": "Left hand polydactyly",  "hpo_id": "HP:0001161"},
    {"patient_id": "P001", "phrase": "Growth delay",           "hpo_id": "HP:0001510"}
  ]
}
```

### 下载导出文件

```bash
# HPO ID 列表（每行一个）
curl -O http://localhost:8000/runs/{job_id}/download/hpo_ids.txt
# HP:0001631
# HP:0001161
# HP:0001510

# 患者 ID + 原始病历（TSV，含表头）
curl -O http://localhost:8000/runs/{job_id}/download/phenotypes.tsv
# ID	Phenotype
# P001	患儿出生时发现左手多指畸形...
```

---

## API 文档

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/v1/extract` · `/runs` | 提交临床笔记，返回 `job_id` |
| `GET` | `/api/v1/jobs/{id}` · `/runs/{id}` | 查询任务状态 + 结果 |
| `GET` | `/runs/{id}/result` | 仅返回结果列表 |
| `GET` | `/runs/{id}/log` | 执行日志（耗时、错误） |
| `GET` | `/runs/{id}/download/hpo_ids.txt` | 下载 HPO ID 纯文本 |
| `GET` | `/runs/{id}/download/phenotypes.tsv` | 下载 患者ID + 原始病历 TSV |
| `GET` | `/api/v1/health` | 健康检查 |

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `notes[].patient_id` | string | 是 | 患者唯一标识 |
| `notes[].clinical_note` | string | 是 | 临床病历文本（中文/英文均可） |
| `input_filename` | string | 否 | 输入文件引用名 |

---

## 配置参数

所有参数通过 `RAG_HPO_` 环境变量覆盖。详见 `src/config.py`。

| 参数 | 默认值 | 说明 |
|---|---|---|
| `RAG_HPO_API_KEY` | — | **必填**，LLM API key |
| `RAG_HPO_BASE_URL` | `https://api.groq.com/...` | API 端点 |
| `RAG_HPO_MODEL` | `deepseek-v4-pro` | 模型名 |
| `RAG_HPO_TEMPERATURE` | 0.7 | LLM 温度 |
| `RAG_HPO_PIPELINE_MAX_WORKERS` | 20 | 并行线程数 |
| `RAG_HPO_EMBEDDING_MODEL` | `pritamdeka/SapBERT-...` | 嵌入模型 |
| `RAG_HPO_JOBS_DIR` | `jobs` | 任务持久化目录 |

---

## 项目结构

```text
pixi_RAG-HPO/
├── src/                       # 源码
│   ├── server.py              # FastAPI 应用 + /runs API
│   ├── pipeline.py            # 管线核心（翻译 → 提取 → 映射 → 去重）
│   ├── rag_hpo.py             # LLM 客户端、FAISS、嵌入模型
│   ├── config.py              # 集中配置（pydantic-settings）
│   ├── schemas.py             # API 请求/响应模型
│   ├── http_utils.py          # HTTP 重试 + 连接池
│   ├── build_vector_db.py     # 构建 HPO 向量数据库
│   └── postprocess.py         # 后处理（废弃词替换、SNOMED/UMLS 合并）
├── tests/                     # 测试
├── hp.obo                     # HPO 本体（~10 MB）
├── hpo_meta.json              # HPO 元数据（~31 MB）
├── hpo_embedded.npz           # HPO 向量（~61 MB，float16）
├── hpo_terms_full.csv         # HPO 全量表（~158 MB）
├── system_prompts.json        # LLM 提示词
├── .env.example               # 凭证模板
├── pixi.toml                  # 项目配置 + 依赖 + tasks
├── pixi.lock                  # 精确依赖锁文件
└── README.md
```

---

## 常用命令

```bash
pixi install                 # 安装 default 环境
pixi run serve               # 启动 FastAPI（开发模式）
pixi run -e prod serve-prod  # 生产模式（gunicorn, 4 workers）
pixi run test                # 运行测试
pixi run lint                # 代码检查
pixi run fmt                 # 代码格式化
pixi run build-db            # 重建 HPO 向量数据库
pixi shell                   # 进入环境 shell
pixi list                    # 查看已安装的包
```

---

## 部署

### Docker

```bash
docker build -t rag-hpo .
docker run -d -p 8000:8000 --env-file .env rag-hpo
```

### 裸金属（生产）

```bash
pixi install -e prod
pixi run -e prod serve-prod
# → gunicorn + 4 uvicorn workers on :8000
```

### 多环境

| 环境 | 包含 | 用途 |
|---|---|---|
| `default` | 14 个核心依赖 | 运行时 |
| `test` | + pytest, httpx | CI 测试 |
| `dev` | + ruff | 本地开发 |
| `prod` | + gunicorn | 生产部署 |

---

## FAQ

**Q: 为什么用 pixi 而不是 pip？**

pip 不解决 C 扩展（faiss-cpu 需要 Intel MKL）的跨平台二进制问题。pixi 通过 conda-forge 提供预编译包，macOS arm64 和 Linux x86_64 都能一键装好。

**Q: 模型缓存在哪里？**

默认在 `~/.cache/huggingface/hub/`。离线环境设置 `HF_HUB_OFFLINE=1`。

**Q: 启动报 "DB files not found"？**

确保 `hp.obo`、`hpo_meta.json`、`hpo_embedded.npz` 在 `src/` 目录下（或创建符号链接）。

**Q: 怎么换 LLM？**

改 `.env` 中的 `RAG_HPO_BASE_URL` 和 `RAG_HPO_MODEL`。任何 OpenAI 兼容 API 都支持。
