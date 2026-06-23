# Pixi 版 PPI 评分服务

这是当前推荐使用的 OpenRare PPI 服务目录。业务代码在 `app/`，运行环境由
Pixi 管理，依赖版本写在 `pixi.toml` 和 `pixi.lock`。

## 快速启动

```bash
cd pixi_ppi_score
pixi install
pixi run serve
```

默认端口为 `9000`，默认数据目录为 `../../data`。

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
| `pixi run test-score` | 运行一个小型 `/score` 测试。 |
| `pixi run case5-clean` | 使用 Case5 示例输入运行 clean-case。 |
| `pixi run case6-clean` | 使用 Case6 示例输入运行 clean-case。 |
| `pixi run check-imports` | 检查主要依赖和 API 模块可导入。 |

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `app/` | FastAPI 和 PPI 评分代码。 |
| `scripts/` | 启动和 curl 测试脚本。 |
| `tests/inputs/` | 小型测试请求、Case5/Case6 HPO 和请求 JSON。 |
| `tests/outputs/` | 本地测试输出目录，运行产物被 Git 忽略。 |
| `docs/` | 依赖、路径和 clean-case 测试说明。 |
| `output/` | 默认 API 输出目录，运行产物被 Git 忽略。 |
| `uploads/` | 默认上传保存目录，运行产物被 Git 忽略。 |

## 输入要求

clean-case 接口需要：

| 输入 | 必要字段 |
| --- | --- |
| phenotype-gene CSV | `gene_symbol`；推荐包含 `gene_score`、`gene_rank`。 |
| VEP CSV | `gene_symbol`；可选 `pathogenic_rank`、`cadd_phred`。 |
| HPO 文件或 `hpo_ids` | HPO ID 列表，重复项会保留。 |

## 输出

| 输出 | 说明 |
| --- | --- |
| `*_ppi_score.csv` | 纯 PPI 网络评分。 |
| `*_final_score.csv` | phenotype、VEP、PPI 融合后的最终排序。 |

字段解释见仓库根目录 `docs/FINAL_SCORE_README.md`。

## 文档

| 文档 | 内容 |
| --- | --- |
| `docs/DEPENDENCIES.md` | Pixi 依赖来源和版本约束。 |
| `docs/PATHS.md` | 外部数据、输入、输出、中间目录路径。 |
| `docs/CLEAN_CASE_TESTS.md` | Case5/Case6 测试输入和验证结果。 |
