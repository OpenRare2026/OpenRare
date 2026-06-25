# 本地数据目录

本目录存放报告流水线与基因检索 CLI 所需的**本地静态数据**。除下文标注可入库的文件外，大体积或受许可约束的数据需**自行下载**后放入对应子目录，并在 `.env` 中配置路径。

```
data/
├── ChinaDrug/chinadrugtrials.csv   # 可提交 git（公开登记数据）
├── Chictr/chictr.csv               # 可提交 git（公开登记数据）
├── omim/omim_20250411.sqlite3      # 需自行准备，不入库
├── MONDO/mondo-rare.json           # 需自行准备（仅 CLI 用）
└── pharmGKB/                       # 需自行准备，不入库
```

## 用途一览

| 路径 | 报告 API | 基因 CLI (`main.py`) | 说明 |
|------|:--------:|:--------------------:|------|
| `ChinaDrug/chinadrugtrials.csv` | ✅ | ✅ | 药物推荐 § 中国试验团队匹配 |
| `Chictr/chictr.csv` | ✅ | ✅ | 同上（ChiCTR） |
| `omim/*.sqlite3` | ✅ | ✅ | 遗传模式、基因功能回退 |
| `MONDO/mondo-rare.json` | — | ✅ | `--mondo-ids` 疾病匹配 |
| `pharmGKB/**` | 仅 `OPEN_TARGETS_ONLY=0` | 仅 `OPEN_TARGETS_ONLY=0` | 本地 ClinPGx |

---

## 1. 中国药物临床试验（可入库）

**文件**：`data/ChinaDrug/chinadrugtrials.csv`

**数据来源**：[药物临床试验登记与信息公示平台](http://www.chinadrugtrials.org.cn/)（国家药监局 NMPA 维护的公开登记信息）。

**获取方式**：平台无官方全量 CSV 下载，需自行从登记库导出或爬取后整理为 CSV。检索字段需覆盖代码中使用的列（如 `drug_name`、`indication`、`title`、`applicant`、`main_leader`、`company` 等，见 `tools/china_trials_local.py`）。

**入库**：登记信息为公开数据，**可将整理好的 CSV 提交到 git 仓库**，便于团队开箱即用。

```bash
mkdir -p data/ChinaDrug
# 将导出文件放到：
# data/ChinaDrug/chinadrugtrials.csv
```

---

## 2. 中国临床试验注册中心 ChiCTR（可入库）

**文件**：`data/Chictr/chictr.csv`

**数据来源**：[Chinese Clinical Trial Registry (ChiCTR)](https://www.chictr.org.cn/)（WHO ICTRP 注册平台，公开试验登记信息）。

**获取方式**：官网可按试验检索；全量数据需自行批量导出或爬取后整理为 CSV。检索字段需覆盖 `public_title`、`intervention`、`study_ailment`、`applicant`、`study_leader` 等（见 `tools/china_trials_local.py`）。

**入库**：公开登记数据，**可将 CSV 提交到 git**。

```bash
mkdir -p data/Chictr
# data/Chictr/chictr.csv
```

---

## 3. OMIM SQLite（需自行下载，不入库）

**文件**：`data/omim/omim_20250411.sqlite3`（文件名可自定，通过环境变量指定）

**数据来源**：[OMIM](https://www.omim.org/)（Online Mendelian Inheritance in Man）。需遵守 OMIM 数据使用条款；通常由团队内部从授权渠道构建 SQLite 快照。

**用途**：

- 报告 §3.x.1 **遗传模式**（`OMIM_ENABLED=1`，默认开启）
- NCBI Gene 无摘要时 **基因功能回退**（`GENE_FUNCTION_FALLBACK_OMIM=1`）

**配置**（`.env`）：

```bash
OMIM_ENABLED=1
OMIM_DB_PATH=./data/omim/omim_20250411.sqlite3
```

```bash
mkdir -p data/omim
# 放入 SQLite 文件（体积较大，已 gitignore）
```

---

## 4. MONDO 罕见病本体（需自行下载，CLI 专用）

**文件**：`data/MONDO/mondo-rare.json`

**数据来源**：[MONDO Disease Ontology](https://github.com/monarch-initiative/mondo)（Monarch Initiative）。可使用官方 release 中的 JSON，或按项目需要裁剪的 rare-disease 子集。

**用途**：仅 `python main.py --gene ... --mondo-ids MONDO_...` 结构化工作流中的疾病 ID 匹配；**报告 FastAPI 不读取此文件**。

```bash
mkdir -p data/MONDO
# data/MONDO/mondo-rare.json
```

---

## 5. ClinPGx / PharmGKB（需自行下载，不入库）

**目录**：`data/pharmGKB/`

**数据来源**：[ClinPGx Downloads](https://www.clinpgx.org/downloads)（PharmGKB 官方注释数据包，由 ClinPGx 分发）。

**目录结构**：

```
data/pharmGKB/
├── PrimaryData/
│   └── genes.zip
└── AnnotationData/
    ├── summaryAnnotations.zip
    ├── guidelineAnnotations.json.zip
    └── pathways-tsv.zip
```

**代码如何查询**：读取上述 zip，通过工具 `get_gene_pgx_profile`（`tools/clinpgx.py`）在本地检索基因的用药指南、证据等级、等位基因效应、代谢通路等。**不是**在线访问 pharmgkb.org。

**何时需要**：

| 场景 | 是否使用 |
|------|----------|
| 报告 FastAPI（`pixi run api`） | ❌ 不使用（药物信息走 Open Targets MCP） |
| 基因检索 CLI，`OPEN_TARGETS_ONLY=1`（**默认**） | ❌ 不加载 ClinPGx 工具 |
| 基因检索 CLI，`OPEN_TARGETS_ONLY=0` | ✅ Agent 会调用 `get_gene_pgx_profile` |

**配置**（`.env`）：

```bash
OPEN_TARGETS_ONLY=0          # 仅在需要 PharmGKB 时关闭独占模式
PHARMGKB_DATA_DIR=./data/pharmGKB
```

```bash
mkdir -p data/pharmGKB/PrimaryData data/pharmGKB/AnnotationData
# 将 ClinPGx 下载的 zip 放入对应子目录（见上）
```

zip 体积大，**不要提交 git**。

---

## Git 提交建议

| 路径 | 是否提交 |
|------|----------|
| `data/ChinaDrug/chinadrugtrials.csv` | ✅ 可以（公开） |
| `data/Chictr/chictr.csv` | ✅ 可以（公开） |
| `data/omim/*.sqlite3` | ❌ 太大 / 许可限制 |
| `data/MONDO/*.json` | ❌ 建议忽略（体积、可再生成） |
| `data/pharmGKB/**` | ❌ 太大 |

`.gitignore` 已忽略 `data/pharmGKB/` 与 `data/omim/`，**未忽略** `ChinaDrug/`、`Chictr/` 下的 CSV。

---

## 最小可跑报告 API

若仅验证流水线，至少需要：

1. **OMIM SQLite**（遗传模式有内容）
2. **ChinaDrug + ChiCTR CSV**（药物推荐里的中国试验匹配；缺失时该部分为空，不阻断报告）

**不需要** PharmGKB：报告 API 不读 `data/pharmGKB/`。

外部服务（非 `data/` 文件）：LLM API、Open Targets MCP、Neo4j Reactome 等见 `.env.example`。
