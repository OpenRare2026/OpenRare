# 路径清单

除特别说明外，以下路径都相对 `pixi_ppi_score/`。

## 项目文件

| 用途 | 路径 |
| --- | --- |
| 服务代码 | `app/` |
| Pixi 配置 | `pixi.toml` |
| Pixi 锁文件 | `pixi.lock` |
| 依赖摘要 | `requirements.txt` |
| 启动脚本 | `scripts/run_api.sh` |
| curl 测试脚本 | `scripts/` |

## 外部数据

| 用途 | 默认路径 | 环境变量 |
| --- | --- | --- |
| 参考数据库目录 | `../../data` | `RARE_PPI_DATA_DIR` |
| 缓存目录 | `../../data/cache` | `RARE_PPI_CACHE_DIR` |
| 输出目录 | `output` | `RARE_PPI_OUTPUT_DIR` |
| 上传目录 | `uploads` | `RARE_PPI_UPLOAD_DIR` |

`../../data` 需要包含：

```text
9606.protein.info.v12.0.txt.gz
9606.protein.links.detailed.v12.0.txt.gz
CRISPRGeneEffect.csv
Ensembl2Reactome.txt
GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.gct.gz
Model.csv
ReactomePathwaysRelation.txt
en_product6.xml
ensembl_biomart_export.txt
genemap2.txt
genes_to_phenotype.txt
hgnc_complete_set.txt
hp-full.owl
hp.obo
idmapping_selected.tab.gz
mim2gene.txt
normal_ihc_data.tsv
panelapp_panels.json
phenotype.hpoa
phenotype_to_anatomy.txt
rna_tissue_consensus.tsv
uberon.obo
variant_summary.txt.gz
```

## 测试输入

| 用途 | 路径 |
| --- | --- |
| 小型 score 请求 | `tests/inputs/score_request.json` |
| Case5 clean-case 请求 | `tests/inputs/case5_clean_request.json` |
| Case5 HPO | `tests/inputs/case5_hpo.txt` |
| Case6 clean-case 请求 | `tests/inputs/case6_clean_request.json` |
| Case6 HPO | `tests/inputs/case6_hpo.txt` |

Case5/Case6 的大输入文件位于仓库外部，具体见
`docs/CLEAN_CASE_TESTS.md`。

## 运行输出

| 用途 | 默认路径 |
| --- | --- |
| 小型 score 输出 | `tests/outputs/score_result.csv` |
| Case5 final 输出 | `tests/outputs/clean_cases/case5/case5_final_score.csv` |
| Case5 PPI 输出 | `tests/outputs/clean_cases/case5/case5_ppi_score.csv` |
| Case6 final 输出 | `tests/outputs/clean_cases/case6/case6_final_score.csv` |
| Case6 PPI 输出 | `tests/outputs/clean_cases/case6/case6_ppi_score.csv` |
| 默认 API 输出 | `output/` |
| 上传模式保存 | `uploads/` |

`output/`、`uploads/`、`tests/outputs/` 下的运行产物默认被 Git 忽略，只保留
`.gitkeep` 占位文件。
