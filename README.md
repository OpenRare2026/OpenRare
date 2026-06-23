# OpenRare PPI 评分服务

本仓库提供罕见病候选基因的 PPI 网络评分服务。当前推荐使用
`pixi_ppi_score/`，它已经用 Pixi 固定运行环境，并通过 Case5、Case6
clean-case 测试。

## 目录说明

| 路径 | 说明 |
| --- | --- |
| `pixi_ppi_score/` | 推荐入口。Pixi 环境、FastAPI 服务、测试请求和文档都在这里。 |
| `docs/FINAL_SCORE_README.md` | `*_final_score.csv` 字段和排名规则说明。 |
| `docs/PPI_SCORE.md` | PPI 评分逻辑的简要说明。 |

大型数据库、VEP 文件、上传文件和结果 CSV 不提交到 GitHub。

## 快速启动

```bash
git clone -b dev_lq https://github.com/OpenRare2026/OpenRare.git
cd OpenRare/pixi_ppi_score
pixi install
pixi run serve
```

默认服务地址：

```text
http://127.0.0.1:9000
```

默认外部数据目录：

```text
../../data
```

如果数据不在默认位置，可以显式指定：

```bash
RARE_PPI_DATA_DIR=/path/to/data pixi run serve
```

健康检查：

```bash
pixi run health
curl http://127.0.0.1:9000/health
```

## 输入和输出

clean-case 流程输入三类文件：

| 输入 | 说明 |
| --- | --- |
| phenotype-gene CSV | 至少包含 `gene_symbol`，通常也包含 `gene_score`、`gene_rank` 等字段。 |
| VEP CSV | 至少包含 `gene_symbol`；如有 `pathogenic_rank`、`cadd_phred` 会参与汇总。 |
| HPO 列表 | 每行一个 HPO ID；重复 HPO 会保留并参与组织投票。 |

每个病例输出两张表：

| 输出 | 说明 |
| --- | --- |
| `*_ppi_score.csv` | 纯 PPI 网络评分表。 |
| `*_final_score.csv` | phenotype、VEP 和 PPI 融合后的最终候选基因排序表。 |

最终表字段见 `docs/FINAL_SCORE_README.md`。

## 运行 clean-case

推荐使用路径型接口，避免上传 9GB 以上的大 VEP 文件：

```bash
curl -X POST http://127.0.0.1:9000/score/clean-case \
  -H 'Content-Type: application/json' \
  -d '{
    "data_dir": "../../data",
    "phenotype_gene_csv": "../../input/gene_phenotype_score.csv",
    "vep_output_csv": "../../input/case.vep.csv",
    "hpo_file": "../../input/hpo_ids.txt",
    "output_csv": "output/case_final_score.csv",
    "ppi_output_csv": "output/case_ppi_score.csv",
    "candidate_top_n": 30000,
    "vep_chunksize": 250000
  }'
```

也可以使用已保存的测试请求：

```bash
cd pixi_ppi_score
pixi run case5-clean
pixi run case6-clean
```

测试数据说明见 `pixi_ppi_score/docs/CLEAN_CASE_TESTS.md`。

## 常用 Pixi 命令

```bash
cd pixi_ppi_score
pixi install
pixi run serve
pixi run health
pixi run test-score
pixi run case5-clean
pixi run case6-clean
```

更多路径说明见 `pixi_ppi_score/docs/PATHS.md`。

## 环境说明

Pixi 环境锁定在 `pixi_ppi_score/pixi.lock`。其中 `pandas` 固定为
`>=2.3,<3`，避免 Pandas 3.x 在大 VEP CSV 分块读取时触发解析问题。

## 当前验证

已在服务器上完成：

| 用例 | 状态 | 输出行数 | 说明 |
| --- | --- | ---: | --- |
| Case5 | `completion` | 47319 | HPO 数 6，映射组织 `brain=5, uterus=1` |
| Case6 | `completion` | 47078 | HPO 数 2，映射组织 `brain=2` |
