# Pixi 版 PPI 评分服务

这是当前推荐使用的 OpenRare PPI 服务目录。业务代码在 `app/`，运行环境由
Pixi 管理，依赖版本写在 `pixi.toml` 和 `pixi.lock`。

## 快速启动

```bash
cd modules/pixi_ppi_score
pixi install
pixi run serve
```

默认端口为 `9000`，默认数据目录为 `../../../data`。

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

## 常用任务

| 命令 | 说明 |
| --- | --- |
| `pixi run serve` | 启动 FastAPI 服务。 |
| `pixi run health` | 调用 `/health`，确认数据文件齐全。 |
| `pixi run score -- <request.json>` | 使用 JSON 参数运行基础 `/score` 接口。 |
| `pixi run clean-case-upload -- <phenotype.csv> <vep.csv> <hpo.txt>` | multipart 上传文件版 clean-case。 |
| `pixi run clean-case -- <request.json>` | 使用 JSON 路径参数运行 clean-case。 |
| `pixi run check-imports` | 检查主要依赖和 API 模块可导入。 |

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `app/` | FastAPI 和 PPI 评分代码。 |
| `scripts/` | 启动和 curl 测试脚本。 |
| `tests/outputs/` | 本地运行输出目录，运行时自动创建，产物被 Git 忽略。 |
| `docs/` | 依赖、路径、输出字段和 PPI 评分说明。 |
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

当 VEP 大文件已经在服务器上时，仍建议使用 `/score/clean-case` 的 JSON
路径接口，避免重复上传。

## 输出

| 输出 | 说明 |
| --- | --- |
| `*_ppi_score.csv` | 纯 PPI 网络评分。 |
| `*_final_score.csv` | phenotype、VEP、PPI 融合后的最终排序。 |

字段解释见 `docs/FINAL_SCORE_README.md`。

## 文档

| 文档 | 内容 |
| --- | --- |
| `docs/DEPENDENCIES.md` | Pixi 依赖来源和版本约束。 |
| `docs/PATHS.md` | 外部数据、输入、输出、中间目录路径。 |
| `docs/FINAL_SCORE_README.md` | `*_final_score.csv` 字段和排名规则说明。 |
| `docs/PPI_SCORE.md` | PPI 评分逻辑的简要说明。 |
