# 路径清单

除特别说明外，以下路径都相对 `modules/pixi_ppi_score/`。

## 项目文件

| 用途 | 路径 |
| --- | --- |
| 服务代码 | `app/` |
| FastAPI 入口 | `app/api.py` |
| 路径配置 | `app/config.py` |
| PPI 评分逻辑 | `app/Network.py` |
| 数据下载脚本 | `app/download_data.sh` |
| GTEx v11 整理脚本 | `app/prepare_gtex_v11.py` |
| 数据检查脚本 | `scripts/check_data_files.py` |
| Pixi 配置 | `pixi.toml` |
| Pixi 锁文件 | `pixi.lock` |
| 依赖摘要 | `requirements.txt` |
| 启动脚本 | `scripts/run_api.sh` |
| curl 测试脚本 | `scripts/` |

## 外部数据目录

| 用途 | 默认路径 | 环境变量 |
| --- | --- | --- |
| 参考数据库目录 | `../../../data` | `RARE_PPI_DATA_DIR` |
| 缓存目录 | `../../../data/cache` | `RARE_PPI_CACHE_DIR` |
| 输出目录 | `output` | `RARE_PPI_OUTPUT_DIR` |
| 上传目录 | `uploads` | `RARE_PPI_UPLOAD_DIR` |
| GTEx v11 原始文件目录 | `../../../data/GTEx/v11` | `GTEX_V11_SOURCE_DIR` |

准备和检查数据：

```bash
pixi run download-data
pixi run check-data
pixi run check-data -- --json
```

`../../../data` 需要包含：

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

## 可能需要人工提供的数据

| 文件 | 说明 |
| --- | --- |
| `genemap2.txt` | OMIM 受限文件，需要合法 `OMIM_API_KEY` 才能自动下载。 |
| `GTEx/v11/expression/GTEx_Analysis_2025-08-22_v11_RSEMv1.3.3_transcripts_tpm.txt.gz` | GTEx v11 transcript TPM 原始文件，用于生成 gene median TPM。 |
| `GTEx/v11/metadata/GTEx_Analysis_v11_Annotations_SampleAttributesDS.txt` | GTEx v11 sample metadata，用于生成 gene median TPM。 |
| `CRISPRGeneEffect.csv`、`Model.csv` | DepMap 文件名和下载地址可能随版本更新；若自动下载失败，按 `check-data` 输出手动补齐。 |

## 输入文件

| 用途 | 说明 |
| --- | --- |
| phenotype-gene CSV | 通过 `curl -F phenotype_gene_csv=@...` 上传，或在 JSON 请求中填写服务端相对路径。 |
| VEP CSV | 通过 `curl -F vep_output_csv=@...` 上传，或在 JSON 请求中填写服务端相对路径。 |
| HPO 列表 | 通过 `curl -F hpo_file=@...` 上传，也可以用表单字段或 JSON 字段 `hpo_ids`。 |

## 运行输出

| 用途 | 默认路径 |
| --- | --- |
| 上传脚本输出 | `tests/outputs/upload_cases/<case_name>/` |
| 上传脚本响应 | `tests/outputs/upload_responses/<case_name>_response.json` |
| 路径型 clean-case 输出 | JSON 请求中的 `output_csv` 和 `ppi_output_csv` |
| 默认 API 输出 | `output/` |
| 上传模式保存 | `uploads/` |

`output/`、`uploads/`、`tests/outputs/` 下的运行产物默认被 Git 忽略。当前只保留 `output/.gitkeep` 作为默认输出目录占位文件。
