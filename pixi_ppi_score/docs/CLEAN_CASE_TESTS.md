# Clean-case Test Inputs

Paths are relative to `pixi_ppi_score/`.

## Case5

Request:

```bash
RARE_PPI_PORT=9000 scripts/curl_clean_case.sh tests/inputs/case5_clean_request.json
```

Inputs:

| Purpose | Path |
| --- | --- |
| Phenotype-gene CSV | `../../input/Case5_gene_phenotype_score.csv` |
| VEP CSV | `../../../pangjiangshuan/vep_runner/tmux_runs/26D01487024_580d86_fork16_hpo_20260612_110118/26D01487024_580d86.vep.csv` |
| HPO file | `tests/inputs/case5_hpo.txt` |

Outputs:

| Purpose | Path |
| --- | --- |
| Final score CSV | `tests/outputs/clean_cases/case5/case5_final_score.csv` |
| PPI score CSV | `tests/outputs/clean_cases/case5/case5_ppi_score.csv` |

Latest validation:

```text
status=completion
count=47319
hpo_count=6
ranked_gene_count=5109
mapped_tissues=["brain","uterus"]
mapped_tissue_counts={"brain":5,"uterus":1}
```

## Case6

Request:

```bash
RARE_PPI_PORT=9000 scripts/curl_clean_case.sh tests/inputs/case6_clean_request.json
```

Inputs:

| Purpose | Path |
| --- | --- |
| Phenotype-gene CSV | `../../input/Case6_gene_phenotype_score.csv` |
| Supplied liftover VCF | `../../../changan/grch37_to_grch38_liftover/api_service/runs/25B06715455_89a308/output/output.grch38.vcf.gz` |
| VEP CSV used by clean-case API | `../../../pangjiangshuan/vep_runner/tmux_runs/25B06715455_89a308_fork16_hpo_20260613_142102/25B06715455_89a308.vep.csv` |
| HPO file | `tests/inputs/case6_hpo.txt` |

Outputs:

| Purpose | Path |
| --- | --- |
| Final score CSV | `tests/outputs/clean_cases/case6/case6_final_score.csv` |
| PPI score CSV | `tests/outputs/clean_cases/case6/case6_ppi_score.csv` |

Latest validation:

```text
status=completion
count=47078
hpo_count=2
ranked_gene_count=5106
mapped_tissues=["brain"]
mapped_tissue_counts={"brain":2}
```

Note: the clean-case API consumes VEP CSV fields such as `gene_symbol`,
`pathogenic_rank`, and `cadd_phred`. The supplied Case6 liftover VCF is recorded
above, while the matching VEP CSV was used for this endpoint.
