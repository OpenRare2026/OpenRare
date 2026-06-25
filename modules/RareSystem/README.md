# 罕见病遗传诊断分析系统 / Rare Disease Genetic Diagnosis Analysis System

端到端的罕见病遗传诊断分析系统，支持多类型变异检测（SNV/INDEL、STR、CNV）、ACMG 临床分级、双轨报告（临床/科研）以及基于 RAG 的智能问答。

## 核心功能

- **多类型变异检测** — SNV/INDEL、STR、CNV 分析，集成 VEP 注释
- **ACMG 自动分级** — 基于 ACMG/AMP 准则的变异致病性分类，完整证据链（PVS1-PP5 / BP1-BP7）
- **双轨报告** — 临床级报告（循证、可追溯）+ 科研探索报告（不确定性量化、假说生成）
- **智能问答** — 基于 RAG 的病例问答，支持 PubMed 文献检索、表型-HPO 映射、通路分析等技能
- **隐私优先** — 仅限本地部署，不持久化患者数据，外部服务通过加密 API 调用
- **中英双语** — 自动检测浏览器语言

## 技术栈

| 层级 | 技术 |
|---|---|
| 后端 | FastAPI + SQLAlchemy + Alembic + Uvicorn |
| 前端 | React 18 + TypeScript + Ant Design 5 + Zustand + Vite |
| 变异处理 | pysam + scikit-allel + VEP API |
| 数据处理 | NumPy + Pandas + Dask + PyArrow |
| 图数据库 | Neo4j（通路与基因关联） |
| 智能问答 | RAG + LLM（可配置 OpenAI / 兼容 API） |
| 包管理 | [Pixi](https://pixi.sh)（conda + PyPI 统一管理） |

## 项目结构

```
.
├── pixi.toml                    # Pixi 工作区配置（依赖、任务、环境）
├── pixi.lock                    # 锁定文件（确保可复现）
├── backend/                     # FastAPI 后端
│   ├── main.py                  # 应用入口，路由注册，WebSocket
│   ├── config.py                # 配置加载
│   ├── api/                     # API 端点
│   │   ├── health.py            # 健康检查
│   │   ├── variants.py          # VCF 上传与变异查询
│   │   ├── acmg.py              # ACMG 分类与分析
│   │   ├── chat.py              # 对话式问答
│   │   ├── cases.py             # 病例管理
│   │   ├── genes.py             # 基因信息查询
│   │   ├── hpo.py               # HPO 表型查找
│   │   ├── phenotype_hpo.py     # 表型-HPO 自动提取
│   │   ├── pathways.py          # 通路分析
│   │   ├── ppi_score.py         # PPI 打分
│   │   ├── pubmed.py            # PubMed 文献检索
│   │   ├── report.py            # 报告生成
│   │   ├── settings.py          # LLM / 分析参数配置
│   │   ├── skills.py            # 技能执行
│   │   ├── vep.py               # VEP 注释任务
│   │   ├── middleware.py        # 日志 / 异常中间件
│   │   └── ws_manager.py        # WebSocket 连接管理
│   ├── services/                # 业务逻辑
│   │   ├── vcf_parser.py        # VCF 解析
│   │   ├── variant_service.py   # 变异查询与注释
│   │   ├── acmg_classifier.py   # ACMG 分级引擎
│   │   ├── rag_service.py       # RAG 问答服务
│   │   ├── llm_client.py        # LLM 客户端
│   │   ├── embedding_service.py # 向量嵌入
│   │   ├── hpo_service.py       # HPO 本体服务
│   │   ├── pathway_service.py   # 通路分析服务
│   │   ├── ppi_score_service.py # PPI 打分服务
│   │   ├── pubmed_service.py    # PubMed 检索服务
│   │   ├── report_service.py    # 报告生成服务
│   │   ├── vep_service.py       # VEP 注释服务
│   │   └── skills/              # 可扩展技能模块
│   │       ├── acmg_skill.py
│   │       ├── variant_skill.py
│   │       ├── phenotype_skill.py
│   │       ├── literature_skill.py
│   │       └── pubmed_search_skill.py
│   ├── database/                # 数据模型与会话
│   │   ├── models.py            # SQLAlchemy 模型
│   │   ├── case_models.py       # 病例相关模型
│   │   ├── session.py           # 数据库连接
│   │   └── base.py              # Base 类
│   ├── alembic/                 # 数据库迁移
│   ├── prompts/                 # LLM 提示词模板
│   ├── reference/               # 参考数据
│   └── tests/                   # 后端测试
├── frontend/                    # React 前端
│   ├── src/
│   │   ├── pages/               # 页面路由
│   │   │   ├── UploadPage.tsx   # VCF 上传
│   │   │   ├── BrowseCases.tsx  # 病例浏览
│   │   │   └── AnalysisPage.tsx # 分析交互
│   │   ├── components/          # UI 组件
│   │   │   ├── VCFUpload.tsx
│   │   │   ├── VariantList.tsx
│   │   │   ├── VariantDetailPage.tsx
│   │   │   ├── ACMGDisplay.tsx
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DualTrackReport.tsx
│   │   │   ├── PathwayView.tsx
│   │   │   ├── GeneView/
│   │   │   ├── Settings.tsx
│   │   │   └── SkillDropdown.tsx
│   │   ├── store/               # Zustand 状态管理
│   │   ├── services/            # API 调用封装
│   │   ├── i18n/                # 国际化
│   │   └── types/               # TypeScript 类型定义
│   └── vite.config.ts           # Vite 配置（含 API 代理）
├── config/                      # 运行时配置
├── docker/                      # Docker 相关
├── Dockerfile                   # 生产环境 Dockerfile
└── docker-compose.yml           # Docker Compose 编排
```

## 安装

### 前置条件

只需要安装 [Pixi](https://pixi.sh)，其余依赖（Python、Node.js、所有包）由 Pixi 自动管理：

```bash
# 官方安装脚本
curl -fsSL https://pixi.sh/install.sh | bash

# 或者直接拷贝 pixi 二进制到新机器
scp pixi /usr/local/bin/pixi && chmod +x /usr/local/bin/pixi
```

### 获取项目代码

```bash
# 方式一：Git
git clone <repo-url> && cd HANJIANBING

# 方式二：从已有服务器同步（排除生成目录）
rsync -avz --exclude='.pixi/' --exclude='node_modules/' \
  --exclude='__pycache__/' --exclude='.git/' \
  source-server:/path/to/HANJIANBING/ ./HANJIANBING/
```

> **重要**：`pixi.lock` 必须随项目一起传输，它锁定了所有包的精确版本，确保环境可复现。

### 安装依赖

```bash
# 安装所有环境（default + dev + frontend + test）
pixi install

# 安装前端 npm 依赖
pixi run -e frontend frontend-install
```

## 快速开始

### 一键启动（前端 + 后端）

```bash
pixi run dev-full
```

启动后访问：

| 服务 | 地址 |
|---|---|
| 前端界面 | http://localhost:8888 |
| 后端 API | http://localhost:18000/api/health |
| API 文档 (Swagger) | http://localhost:18000/docs |

### 单独启动

```bash
# 仅后端
pixi run dev

# 仅前端
pixi run frontend

# 生产模式（无热重载）
pixi run start
```

### 配置环境变量

```bash
# 后端配置 — 项目已包含 backend/.env（服务器部署配置）
# 如需自定义，可基于 .env.example 修改：
cp backend/.env.example backend/.env

# 前端配置
cp frontend/.env.example frontend/.env
```

> **注意**： 已纳入版本控制，包含当前服务器（172.27.206.113/112）的外部服务地址。部署到新环境时需修改其中的 IP 地址。

关键配置项：

| 变量 | 说明 | 默认值 |
|---|---|---|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./rare_disease_diagnosis.db` |
| `API_PORT` | 后端端口 | `18000` |
| `CORS_ORIGINS` | 允许的前端来源 | `http://localhost:8888,...` |
| `LLM_PROVIDER` | LLM 提供商 | `openai` |
| `LLM_API_KEY` | LLM API 密钥 | — |
| `LLM_MODEL` | LLM 模型名 | `gpt-4` |
| `LLM_BASE_URL` | LLM API 地址 | `https://api.openai.com/v1` |
| `VEP_ENABLED` | 是否启用 VEP 注释 | `true` |
| `VEP_API_BASE_URL` | VEP 服务地址 | `http://127.0.0.1:18000` |
| `HPO_API_BASE_URL` | HPO 服务地址 | `http://127.0.0.1:9004` |
| `PHENOTYPE_HPO_API_BASE_URL` | 表型-HPO 服务地址 | `http://127.0.0.1:7002` |
| `PPI_SCORE_API_BASE_URL` | PPI 打分服务地址 | `http://127.0.0.1:9000` |
| `REPORT_API_BASE_URL` | 报告服务地址 | `http://127.0.0.1:7000` |
| `GFF3_ANNOTATION_PATH` | GFF3 注释文件路径 | `` (使用相对路径) |
| `NCBI_EMAIL` | NCBI 邮箱（PubMed 检索需要） | — |
| `NCBI_API_KEY` | NCBI API 密钥 | — |

## 使用示例

### 典型工作流

```
1. 上传 VCF → 2. 变异检测与注释 → 3. ACMG 分级 → 4. 智能问答 → 5. 生成报告
```

### API 调用示例

```bash
# 健康检查
curl http://localhost:18000/api/health

# 上传 VCF 文件
curl -X POST http://localhost:18000/api/variants/upload \
  -F "file=@sample.vcf" \
  -F "patient_id=1"

# 查询变异列表
curl http://localhost:18000/api/variants/{vcf_file_id}

# ACMG 分析
curl -X POST http://localhost:18000/api/acmg/{variant_id}/analyze

# HPO 表型提取
curl -X POST http://localhost:18000/api/hpo/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "患者表现为肌张力低下、发育迟缓"}'

# PubMed 文献检索
curl "http://localhost:18000/api/pubmed/search?query=BRCA1+rare+disease&max_results=10"

# 提交报告生成
curl -X POST http://localhost:18000/api/report/submit \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1, "report_type": "clinical"}'
```

### WebSocket 对话

```javascript
const ws = new WebSocket('ws://localhost:18000/api/chat/ws/1');
ws.send(JSON.stringify({
  type: 'chat',
  content: '该患者的致病变异有哪些？',
  session_token: 'optional-session-token'
}));
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## 环境说明

项目通过 Pixi 管理四个环境，每个环境包含不同的依赖集合：

| 环境 | 包含 Feature | 用途 |
|---|---|---|
| `default` | — | 生产运行（Python 后端依赖） |
| `dev` | dev + frontend | 开发调试（ruff、ipython、Node.js、前后端同启） |
| `frontend` | frontend | 前端开发（Node.js + npm） |
| `test` | test | 测试（pytest、pytest-asyncio、pytest-cov） |

### Pixi 任务一览

| 命令 | 环境 | 说明 |
|---|---|---|
| `pixi run dev-full` | dev | 同时启动前端 + 后端（开发推荐） |
| `pixi run dev` | dev | 仅启动后端（热重载） |
| `pixi run frontend` | dev | 仅启动前端 |
| `pixi run start` | default | 后端生产模式 |
| `pixi run migrate` | default | 执行数据库迁移 |
| `pixi run makemigration` | default | 生成迁移脚本 |
| `pixi run test` | test | 运行后端测试 |
| `pixi run test-cov` | test | 运行测试 + 覆盖率 |
| `pixi run lint` | dev | Ruff 代码检查 |
| `pixi run format` | dev | Ruff 代码格式化 |
| `pixi run frontend-install` | frontend | 安装 npm 依赖 |
| `pixi run frontend-build` | frontend | 构建前端生产包 |

### 依赖来源

Pixi 采用 **conda-first** 策略：优先从 conda-forge / bioconda 安装预编译二进制包，仅对 conda 中不可用的包使用 PyPI。

| 来源 | 频道 | 典型包 |
|---|---|---|
| conda-forge | conda-forge | fastapi, numpy, pandas, scikit-allel, pydantic, ... |
| bioconda | bioconda | pysam |
| PyPI | pypi.org | neo4j |

### 部署到新机器

```bash
# 1. 安装 pixi
curl -fsSL https://pixi.sh/install.sh | bash

# 2. 拷贝项目（确保 pixi.lock 随行）
rsync -avz --exclude='.pixi/' --exclude='node_modules/' \
  --exclude='__pycache__/' \
  ./HANJIANBING/ user@newhost:/path/to/HANJIANBING/

# 3. 安装依赖
cd /path/to/HANJIANBING
pixi install
pixi run -e frontend frontend-install

# 4. 配置环境变量
# 项目自带 backend/.env（含服务器配置），新环境需修改服务地址：
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入实际服务地址和 LLM_API_KEY

# 5. 启动
pixi run dev-full
```

### Docker 部署（可选）

```bash
docker-compose up -d

# 常用命令
make help        # 查看所有命令
make logs        # 查看日志
make stop        # 停止
make restart     # 重启
```

## 数据流

```
VCF 上传 + 患者元数据 → 解析 → 校验
    ↓
变异检测管线 (SNV/INDEL, STR, CNV) → QC → 入库
    ↓
ACMG 分级 → 证据评分 → 证据链生成
    ↓
双轨报告生成
    ├── 临床级：ACMG 分级变异，完全验证，可直接用于临床决策
    └── 科研级：探索性发现，标注不确定性，假说生成
    ↓
交互式可视化 + RAG 智能问答
```

## 安全说明

- **不持久化患者数据** — 所有患者数据仅在处理时驻留内存
- **仅脱敏数据** — 患者特征必须脱敏后才能输入系统
- **加密外部调用** — 外部数据服务通过加密 API 访问
- **本地部署优先** — 不使用云存储，敏感数据不离开本地
