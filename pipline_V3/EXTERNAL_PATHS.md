# OpenRare 外部路径与流程文件说明

本文档整理 **仓库内相对路径**、**流程中间文件**（相对 `--out-dir`）以及 **外部数据路径**（通过环境变量配置，通常为绝对路径）。

仓库根目录记为 `OpenRare/`（含 `pixi.toml`）。在仓库根复制 `.env.example` 为 `.env` 并填写本机数据路径即可，**无需软链或复制大文件进仓库**。

配置模板：仓库根 [`.env.example`](../../.env.example)

---

## 1. 环境变量（`.env` 文件）

在 `OpenRare/.env` 中设置（`pixi run`、Shell、`path_utils.py` 会自动加载）：

| 环境变量 | `.env.example` 示例值 | 用途 |
|----------|----------------------|------|
| `OPENRARE_DATA_ROOT` | `/path/to/vep_runner` | VEP cache、插件数据、参考 FASTA、GTEx/HPO |
| `OPENRARE_PUBLIC_DATA_ROOT` | `/path/to/public_data` | 假基因 GENCODE / Pseudogene.org / HGNC |
| `FULL_PIPELINE_REF_DIR` | `/path/to/phasing/CHN_ref` | Beagle CHN reference panel |
| `FULL_PIPELINE_BEAGLE_JAR` | `/path/to/phasing/beagle.27Feb25.75f.jar` | Beagle JAR |
| `JAVA_BIN` | `java` | Beagle 用 Java |
| `VEP_RUNNER_TMPDIR` | 无 | VEP 临时目录（可选） |
| `HPO_TPM_DATA_DIR` | 无 | HPO→tissue（可选，默认 `$OPENRARE_DATA_ROOT/vep_data/hpo_tpm`） |
| `FULL_PIPELINE_API_JOBS_DIR` | `pipline_V3/complete_pipeline/api_jobs` | API 任务目录 |
| `FULL_PIPELINE_API_HOST` | `127.0.0.1` | API 监听地址 |
| `FULL_PIPELINE_API_PORT` | `18901` | API 端口（pixi task） |
| `OPENRARE_API_TEST_VCF` | 无 | API 集成测试输入 VCF（可选） |

解析逻辑：

- Shell：[`config/paths.sh`](config/paths.sh)（绝对路径原样使用；相对路径相对仓库根展开）
- Python：[`config/path_utils.py`](config/path_utils.py)

**修改路径：**

```bash
cp .env.example .env
# 编辑 .env 中的绝对路径
```

也可在 shell 中 `export`（优先级高于 `.env` 中未设置的项；已存在于环境的变量不会被 `.env` 覆盖）。

---

## 2. 仓库内资源（相对 `pipline_V3/`）

| 相对路径 | 说明 |
|----------|------|
| `complete_pipeline/run_full_pipeline.sh` | 全流程 CLI 入口 |
| `complete_pipeline/start_full_pipeline_api.sh` | API 启动脚本 |
| `complete_pipeline/full_pipeline_api.py` | FastAPI 服务 |
| `modules/vep_runner/config/vep_runner_config.json` | VEP 配置（`${OPENRARE_DATA_ROOT}` 占位符） |
| `modules/vcf_preprocessing/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz` | cCRE BED |
| `modules/vcf_preprocessing/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz` | ncRNA BED |
| `test/input/P001.genotyper10000.vcf` | 仓库内测试 VCF |
| `test/prepare_sites_vcf_with_sample.sh` | sites-only VCF 补样本列 |

---

## 3. 全流程中间与输出文件（相对 `--out-dir`）

| 步骤 | 相对路径 | 说明 |
|------|----------|------|
| 输入 | `00_input/<basename>.vcf.gz` | 规范化后的输入 |
| 01 | `01_phasing/*.original_sites.beagle_phase_merged.refsupport.vcf.gz` | Phasing 结果 |
| 02 | `02_vcf_preprocessing/preprocessed.regulatory.vcf.gz` | VAF + cCRE + ncRNA |
| 03 | `03_pseudogene_annotation/preprocessed.pseudogene_annotated.vcf.gz` | 假基因注释（进 VEP） |
| 03 | `03_pseudogene_annotation/pseudogene_annotation.log.json` | 假基因日志 |
| 04 | `04_vep/vep_output.base.csv` | VEP 基础 CSV |
| 04 | `04_vep/raw_vep.tsv` | 原始 VEP TSV |
| 04 | `04_vep/vep.log` | VEP 日志 |
| 05 | `05_vcf_info_to_csv/vep_output.with_info.csv` | 合并 VCF INFO |
| 06 | `06_result_sorting/vep_output.sorted.csv` | **最终输出** |
| 汇总 | `full_pipeline.outputs.tsv` | 各步路径索引 |
| 日志 | `logs/full_pipeline.log` | 全流程日志 |

---

## 4. API 任务目录（相对 `pipline_V3/complete_pipeline/`）

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
│   ├── GTEx/v11/expression/gtex_v11_transcript_tpm.parquet
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

## 7. Phasing 外部依赖

| 环境变量 | 指向 |
|----------|------|
| `FULL_PIPELINE_REF_DIR` | CHN reference panel **目录** |
| `FULL_PIPELINE_BEAGLE_JAR` | Beagle **JAR 文件** |

---

## 8. 配置文件占位符

`vep_runner_config.json` 使用 `${OPENRARE_DATA_ROOT}`，由 `run_vep_to_csv.py` 按当前环境变量展开为绝对路径。

VEP 模块内 `__VEP_RUNNER__` 表示 `modules/vep_runner/`（模块内小型默认路径）。
