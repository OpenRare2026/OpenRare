# OpenRare 外部路径与流程文件说明

本文档整理 **模块内相对路径**、**流程中间文件**（相对 `--out-dir`）以及 **外部数据路径**（通过环境变量配置，通常为绝对路径）。

模块根目录记为 `modules/pipeline/`（含 `pixi.toml`、`.env`）。在本目录复制 `.env.example` 为 `.env` 并填写本机数据路径即可，**无需软链或复制大文件进仓库**。

配置模板：[`.env.example`](.env.example)

---

## 1. 环境变量（`.env` 文件）

在 `modules/pipeline/.env` 中设置（`pixi run`、Shell、`path_utils.py` 会自动加载）：

| 环境变量 | `.env.example` 示例值 | 用途 |
|----------|----------------------|------|
| `OPENRARE_DATA_ROOT` | `/path/to/vep_runner` | VEP cache、插件数据、参考 FASTA、GTEx/HPO |
| `OPENRARE_PUBLIC_DATA_ROOT` | `/path/to/public_data` | 假基因 GENCODE / Pseudogene.org / HGNC |
| `FULL_PIPELINE_REF_DIR` | `/path/to/phasing/CHN_ref` | Beagle CHN reference panel |
| `FULL_PIPELINE_BEAGLE_JAR` | `/path/to/phasing/beagle.27Feb25.75f.jar` | Beagle JAR |
| `JAVA_BIN` | `java` | Beagle 用 Java |
| `VEP_RUNNER_TMPDIR` | 无 | VEP 临时目录（可选） |
| `HPO_TPM_DATA_DIR` | 无 | HPO→tissue（可选，默认 `$OPENRARE_DATA_ROOT/vep_data/hpo_tpm`） |
| `FULL_PIPELINE_API_JOBS_DIR` | `complete_pipeline/api_jobs` | API 任务目录（相对模块根） |
| `FULL_PIPELINE_API_HOST` | `127.0.0.1` | API 监听地址 |
| `FULL_PIPELINE_API_PORT` | `18901` | API 端口（pixi task） |
| `LIFTOVER_JAR` | 见 `.env.example` | GRCh37→GRCh38 liftover JAR |
| `LIFTOVER_CONFIG` | 见 `.env.example` | liftover TOML（chain、GRCh38 参考、picard 路径） |
| `OPENRARE_API_TEST_VCF` | 无 | API 集成测试输入 VCF（可选） |

解析逻辑：

- Shell：[`config/paths.sh`](config/paths.sh)（绝对路径原样使用；相对路径相对 `modules/pipeline` 展开）
- Python：[`config/path_utils.py`](config/path_utils.py)

**修改路径：**

```bash
cd modules/pipeline
cp .env.example .env
# 编辑 .env 中的绝对路径
```

也可在 shell 中 `export`（已存在于环境的变量不会被 `.env` 覆盖）。

---

## 2. 模块内资源（相对 `modules/pipeline/`）

| 相对路径 | 说明 |
|----------|------|
| `scripts/run_full_pipeline.sh` | 全流程 CLI 入口 |
| `scripts/start_full_pipeline_api.sh` | API 启动脚本 |
| `modules/vcf_preprocessing/liftover_grch37/scripts/run_liftover_vcf.py` | GRCh37→GRCh38 liftover |
| `complete_pipeline/full_pipeline_api.py` | FastAPI 服务 |
| `modules/vep_runner/config/vep_runner_config.json` | VEP 配置（`${OPENRARE_DATA_ROOT}` 占位符） |
| `modules/vcf_preprocessing/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz` | cCRE BED |
| `modules/vcf_preprocessing/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz` | ncRNA BED |
| `test/input/P001.genotyper10000.vcf` | 模块内测试 VCF |
| `test/prepare_sites_vcf_with_sample.sh` | sites-only VCF 补样本列 |

---

## 3. 全流程中间与输出文件（相对 `--out-dir`）

| 步骤 | 相对路径 | 说明 |
|------|----------|------|
| 输入 | `00_input/<basename>.vcf.gz` | 规范化后的输入 |
| 00b | `00_liftover/output/output.grch38.norm.vcf.gz` | GRCh37 输入经 liftover 后的 GRCh38 VCF（可选） |
| 01 | `01_phasing/*.original_sites.beagle_phase_merged.refsupport.vcf.gz` | Phasing 结果 |
| 02 | `02_vcf_preprocessing/preprocessed.regulatory.vcf.gz` | VAF + cCRE + ncRNA |
| 03 | `03_pseudogene_annotation/preprocessed.pseudogene_annotated.vcf.gz` | 假基因注释（进 VEP） |
| 03 | `03_pseudogene_annotation/pseudogene_annotation.log.json` | 假基因日志 |
| 04 | `04_vep/vep_output.base.csv` | VEP 基础 CSV |
| 04 | `04_vep/raw_vep.tsv` | 原始 VEP TSV |
| 04 | `04_vep/vep.log` | VEP 日志 |
| 05 | `05_vcf_info_to_csv/vep_output.with_info.csv` | 合并 VCF INFO/FORMAT |
| 06 | `06_genos_evee_annotation/vep_output.with_genos_evee.csv` | GENOS-VarRisk 宽表 |
| 07 | `07_hla_filter/vep_output.no_hla.csv` | **最终输出**（默认 `hla_filter=yes`） |
| 汇总 | `full_pipeline.outputs.tsv` | 各步路径索引 |
| 日志 | `logs/full_pipeline.log` | 全流程日志 |

---

## 4. API 任务目录（相对 `modules/pipeline/complete_pipeline/`）

| 相对路径 | 说明 |
|----------|------|
| `api_jobs/<job_id>/status.json` | 任务状态 |
| `api_jobs/<job_id>/api_run.log` | 任务日志 |
| `api_jobs/<job_id>/input/` | `/run-upload` 上传的 VCF |
| `api_jobs/<job_id>/output/` | 默认输出（结构同 `--out-dir`） |

---

## 5. `OPENRARE_DATA_ROOT` 下数据布局

环境变量 `OPENRARE_DATA_ROOT` 指向的目录（示例 `/path/to/vep_runner`）：

```text
${OPENRARE_DATA_ROOT}/
├── vep_cache/                    # vep_install offline cache
│   └── Plugins/                 # CADD.pm, SpliceAI.pm, LoFTEE, …
├── vep_data/
│   ├── reference/GRCh38.p14.genome.fa
│   ├── CADD/
│   ├── SpliceAI/
│   ├── AlphaMissense/
│   ├── dbNSFP/
│   ├── ClinVar/
│   ├── GTEx/v11/expression/gtex_v11_transcript_tpm.parquet   # 见 resource_mock/gtex_preprocess/README.md
│   └── hpo_tpm/
└── tmp/
```

安装说明：[`modules/vep_runner/README.md`](modules/vep_runner/README.md)

---

## 6. `OPENRARE_PUBLIC_DATA_ROOT` 下数据布局

| 相对路径（在 public data 根下） | 用途 |
|--------------------------------|------|
| `Pseudogene/GENCODE/release_49/gencode.v49.2wayconspseudos.gtf.gz` | 假基因坐标 |
| `Pseudogene/Pseudogene.org/Human90/Human90.txt` | Pseudogene.org |
| `phenotype_hpo_v1/hgnc_complete_set.txt` | HGNC |

---

## 7. Pixi 与测试

在 `modules/pipeline/` 下：

```bash
pixi install
pixi run pipeline-test    # CLI 回归
pixi run api-test         # API 集成测试
pixi run mock-smoke-test  # mock 库 + 全开关 dry-run
pixi run hla-filter-test  # HLA 过滤单测
```

迷你 mock 数据库（仅联调/smoke）：[`resource_mock/README.md`](resource_mock/README.md)

本地临时输出默认在 `modules/pipeline/tmp/`（已 gitignore）。
