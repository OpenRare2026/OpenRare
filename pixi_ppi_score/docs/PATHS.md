# Path Inventory

All paths below are relative to `pixi_ppi_score/` unless noted.

## Project Paths

| Purpose | Path | Notes |
| --- | --- | --- |
| Service code | `app/` | FastAPI app and scoring modules. |
| Pixi manifest | `pixi.toml` | Dependency and task definition. |
| Pixi lock file | `pixi.lock` | Resolved environment versions after `pixi install`. |
| Dependency summary | `requirements.txt` | Plain dependency list. |
| API launcher | `scripts/run_api.sh` | Sets relative defaults and starts Uvicorn. |
| Health curl helper | `scripts/curl_health.sh` | Writes `tests/outputs/health_response.json`. |
| Score curl helper | `scripts/curl_score.sh` | Writes score response and checks CSV output. |

## Runtime Inputs

| Purpose | Default path | Environment variable |
| --- | --- | --- |
| Reference database directory | `../../data` | `RARE_PPI_DATA_DIR` |
| Cache directory | `../../data/cache` | `RARE_PPI_CACHE_DIR` |
| Test score JSON request | `tests/inputs/score_request.json` | n/a |
| Case5 clean-case JSON request | `tests/inputs/case5_clean_request.json` | n/a |
| Case6 clean-case JSON request | `tests/inputs/case6_clean_request.json` | n/a |
| Case5 HPO file | `tests/inputs/case5_hpo.txt` | n/a |
| Case6 HPO file | `tests/inputs/case6_hpo.txt` | n/a |
| Uploaded score candidate genes | `uploads/score_<id>/candidate_genes.txt` | `RARE_PPI_UPLOAD_DIR` |
| Uploaded score HPO file | `uploads/score_<id>/hpo_ids.txt` | `RARE_PPI_UPLOAD_DIR` |
| Uploaded clean-case inputs | `uploads/clean_case_<id>/inputs/` | `RARE_PPI_UPLOAD_DIR` |

## Runtime Outputs

| Purpose | Default path | Environment variable |
| --- | --- | --- |
| Score CSV output | `output/ppi_score_<id>.csv` | `RARE_PPI_OUTPUT_DIR` |
| Clean-case final CSV | `output/clean_case_<id>/final_score.csv` | `RARE_PPI_OUTPUT_DIR` |
| Clean-case PPI CSV | `output/clean_case_<id>/ppi_score.csv` | `RARE_PPI_OUTPUT_DIR` |
| Upload-mode score CSV | `uploads/score_<id>/ppi_score.csv` | `RARE_PPI_UPLOAD_DIR` |
| Upload-mode audit JSON | `uploads/score_<id>/audit.json` | `RARE_PPI_UPLOAD_DIR` |
| curl health response | `tests/outputs/health_response.json` | n/a |
| curl score response | `tests/outputs/score_response.json` | n/a |
| curl score CSV | `tests/outputs/score_result.csv` | n/a |
| Case5 clean-case final CSV | `tests/outputs/clean_cases/case5/case5_final_score.csv` | n/a |
| Case5 clean-case PPI CSV | `tests/outputs/clean_cases/case5/case5_ppi_score.csv` | n/a |
| Case6 clean-case final CSV | `tests/outputs/clean_cases/case6/case6_final_score.csv` | n/a |
| Case6 clean-case PPI CSV | `tests/outputs/clean_cases/case6/case6_ppi_score.csv` | n/a |

## External Data Files

The current remote service was observed using `RARE_PPI_DATA_DIR=../../data`
relative to this Pixi project. That directory must contain these files:

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

For the previous shared output layout, set these explicitly:

```bash
export RARE_PPI_OUTPUT_DIR=../../output
export RARE_PPI_UPLOAD_DIR=../../uploads
```

The Pixi refactor itself defaults to local `output/` and `uploads/` so generated
artifacts stay under this directory. Runtime artifacts under `output/`,
`uploads/`, and `tests/outputs/` are ignored by Git except for `.gitkeep`
placeholder files.
