# Pixi 版 PPI 评分服务

这是 OpenRare 的 PPI 评分服务模块。业务代码在 `app/`，运行环境由 Pixi 管理，依赖版本写在 `pixi.toml` 和 `pixi.lock`。

## 快速启动

```bash
cd modules/pixi_ppi_score
pixi install
pixi run check-data
pixi run serve
```

默认端口是 `9000`，默认外部数据库目录是 `../../../data`。

```bash
curl http://127.0.0.1:9000/health
```

如需覆盖路径：

```bash
RARE_PPI_DATA_DIR=/path/to/data \
RARE_PPI_OUTPUT_DIR=output \
RARE_PPI_UPLOAD_DIR=uploads \
pixi run serve
```

## 准备外部数据库

数据库文件不提交到 Git，默认下载或读取到 `modules/pixi_ppi_score/../../../data`。如果要放到其他位置，设置 `RARE_PPI_DATA_DIR`。

```bash
cd modules/pixi_ppi_score
pixi install
pixi run download-data
pixi run check-data
pixi run health
```

如果从仓库根目录运行，使用根 `pixi.toml` 中的任务：

```bash
pixi run ppi-download-data
pixi run ppi-check-data
pixi run ppi-health
```

`download-data` 会尽量自动准备 HGNC、Ensembl BioMart、UniProt、HPO、Orphadata、ClinVar、PanelApp、Uberon、HPA、DepMap、Reactome、STRING 等数据。OMIM 的 `genemap2.txt` 需要合法 `OMIM_API_KEY`；没有 key 时脚本会继续执行，但 `check-data` 会提示缺失。GTEx v11 的基因中位 TPM 文件优先由本地 GTEx v11 原始 transcript TPM 和 metadata 生成；缺少原始文件时，脚本会尝试下载公开旧版 fallback 文件。

如果要让其他 Agent 一键准备数据，可以直接把 `docs/DATA_SETUP_PROMPT.md` 里的 prompt 发给它。

## 常用任务

| 命令 | 说明 |
| --- | --- |
| `pixi run serve` | 启动 FastAPI 服务。 |
| `pixi run download-data` | 下载或整理外部数据库文件。 |
| `pixi run check-data` | 检查 PPI 服务需要的数据库文件是否齐全。 |
| `pixi run health` | 调用 `/health`，确认服务和数据文件状态。 |
| `pixi run score -- <request.json>` | 使用 JSON 参数运行基础 `/score` 接口。 |
| `pixi run clean-case-upload -- <phenotype.csv> <vep.csv> <hpo.txt>` | multipart 上传文件版 clean-case。 |
| `pixi run clean-case -- <request.json>` | 使用 JSON 路径参数运行 clean-case。 |
| `pixi run check-imports` | 检查主要依赖和 API 模块可导入。 |

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `app/` | FastAPI 和 PPI 评分代码。 |
| `app/download_data.sh` | 外部数据库下载与整理脚本。 |
| `app/prepare_gtex_v11.py` | 从 GTEx v11 原始文件生成服务需要的 gene median TPM。 |
| `scripts/` | 启动、curl 测试和数据检查脚本。 |
| `docs/` | 依赖、路径、输出字段、数据准备 prompt 和 PPI 评分说明。 |
| `output/` | 默认 API 输出目录，运行产物被 Git 忽略。 |
| `uploads/` | 默认上传保存目录，运行产物被 Git 忽略。 |

## 输入要求

clean-case 接口需要：

| 输入 | 必要字段 |
| --- | --- |
| phenotype-gene CSV | `gene_symbol`；推荐包含 `gene_score`、`gene_rank`。 |
| VEP CSV | `gene_symbol`；可选 `pathogenic_rank`、`cadd_phred`。 |
| HPO 文件或 `hpo_ids` | HPO ID 列表，重复项会保留。 |

## 上传文件运行

如果调用端持有输入文件，使用 `curl -F` 最直接：

```bash
curl -X POST http://127.0.0.1:9000/score/clean-case/upload \
  -F "phenotype_gene_csv=@gene_phenotype_score.csv" \
  -F "vep_output_csv=@case.vep.csv" \
  -F "hpo_file=@hpo_ids.txt" \
  -F "data_dir=../../../data" \
  -F "output_csv=output/case_final_score.csv" \
  -F "ppi_output_csv=output/case_ppi_score.csv" \
  -F "candidate_top_n=30000" \
  -F "vep_chunksize=250000"
```

也可以使用脚本：

```bash
pixi run clean-case-upload -- \
  gene_phenotype_score.csv \
  case.vep.csv \
  hpo_ids.txt \
  case_name
```

如果不想单独准备 HPO 文件，可以传环境变量：

```bash
HPO_IDS="HP:0002352,HP:0002500" \
pixi run clean-case-upload -- gene_phenotype_score.csv case.vep.csv
```

当 VEP 大文件已经在服务器上时，仍建议使用 `/score/clean-case` 的 JSON 路径接口，避免重复上传。

## 输出

| 输出 | 说明 |
| --- | --- |
| `*_ppi_score.csv` | 纯 PPI 网络评分。 |
| `*_final_score.csv` | phenotype、VEP、PPI 融合后的最终排序。 |

字段解释见 `docs/FINAL_SCORE_README.md`。

## 文档

| 文档 | 内容 |
| --- | --- |
| `docs/DATA_SETUP_PROMPT.md` | 给其他 Agent 使用的一键数据准备 prompt。 |
| `docs/DEPENDENCIES.md` | Pixi 依赖来源和版本约束。 |
| `docs/PATHS.md` | 外部数据、输入、输出、中间目录路径。 |
| `docs/FINAL_SCORE_README.md` | `*_final_score.csv` 字段和排名规则说明。 |
| `docs/PPI_SCORE.md` | PPI 评分逻辑的简要说明。 |
