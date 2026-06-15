# Clean-case Final Score CSV

This document describes the `*_final_score.csv` file produced by the clean-case
workflow.

Clean-case runs write two CSV files for each sample:

```text
*_ppi_score.csv    Pure PPI output. Columns match the PPI output table in README.
*_final_score.csv  Final case table. It merges phenotype, VEP, and PPI evidence.
```

Use `*_ppi_score.csv` when you want to inspect only PPI network evidence. Use
`*_final_score.csv` when you want the final per-case candidate gene ranking.

## Inputs

The final table is built from three inputs:

| Input | Purpose |
| --- | --- |
| phenotype-gene CSV | Provides `gene_score`, `gene_rank`, and disease-match metadata |
| VEP CSV | Provides variant-level gene evidence summarized per gene |
| HPO list | Builds disease anchors `D`, maps tissues, builds tissue anchors `T`, and scores PPI |

For large VEP files, the clean-case workflow reads only these VEP columns:

```text
gene_symbol
pathogenic_rank
cadd_phred
```

The candidate list is the union of the top `candidate_top_n` VEP genes and the
top `candidate_top_n` phenotype-ranked genes. The default is `30000`; set
`candidate_top_n=0` to use all genes.

## Ranking Rule

The final table keeps all retained candidate genes, but only genes that can be
fully fused receive `final_rank`.

```text
rankable = gene_score is not empty AND in_network == true
combined_score = (gene_score + ppi_final) / 2
final_rank = rank among rankable genes by combined_score
```

This means `final_rank` is not a row number. If a gene has a high `ppi_final`
but the phenotype input has an empty `gene_score`, it remains in the final CSV
but `combined_score` and `final_rank` are empty. To inspect pure PPI ranking,
use `*_ppi_score.csv` or the `ppi_rank` column in `*_final_score.csv`.

## Columns

When `output_all_ppi_fields=true`, `*_final_score.csv` contains the columns
below. If `include_evidence_json=false`, evidence JSON columns may be omitted.
If `include_neighbors=false`, neighbor columns may be omitted.

| Column | Source | Description |
| --- | --- | --- |
| `final_rank` | Final fusion | Final comprehensive rank among rankable genes only |
| `gene` | Candidate list | HGNC gene symbol |
| `combined_score` | Final fusion | Average of `gene_score` and `ppi_final` for rankable genes |
| `gene_score` | phenotype CSV | Phenotype-gene score; empty if unavailable in input |
| `ppi_final` | PPI scorer | Final PPI network score |
| `in_network` | PPI scorer | Whether the gene is present in the STRING network |
| `disease_score` | PPI scorer | Disease-anchor `D` network proximity and interaction score |
| `tissue_score` | PPI scorer | Tissue-anchor `T` network proximity and interaction score |
| `topology_score` | PPI scorer | Global degree and betweenness topology score |
| `score_mode` | PPI scorer | PPI fusion mode, such as `FULL_ANCHOR`, `NO_D_REWEIGHTED`, or `TOPOLOGY_ONLY` |
| `score_weight_sum` | PPI scorer | Sum of PPI axis weights used in this row |
| `note` | PPI scorer | Boundary marker, such as `OK`, `EMPTY_D`, `EMPTY_T`, or `NOT_IN_STRING` |
| `gene_in_d` | PPI scorer | Whether this candidate entered disease anchor set `D` |
| `gene_d_evidence_score` | PPI scorer | Weighted disease-anchor evidence score for this gene |
| `gene_d_sources_json` | PPI scorer | JSON list of sources supporting this gene in `D` |
| `gene_in_t` | PPI scorer | Whether this candidate entered tissue anchor set `T` |
| `gene_t_weight` | PPI scorer | Number/weight of tissue layers supporting this gene |
| `gene_t_layers_json` | PPI scorer | JSON list of tissue support layers, such as expression, DepMap, or pathway |
| `gene_t_tissues_json` | PPI scorer | JSON list of tissues supporting this gene in `T` |
| `mapped_tissues_json` | PPI scorer | Top mapped tissues from HPO parsing as JSON |
| `d_gene_count` | PPI scorer | Number of genes in final disease anchor set `D` |
| `t_gene_count` | PPI scorer | Number of genes in final tissue anchor set `T` |
| `top_neighbors_json` | PPI scorer | Top STRING neighbors and D/T labels |
| `top_neighbors_count` | PPI scorer | Number of neighbors returned |
| `gene_rank` | phenotype CSV | Gene rank from phenotype-gene input |
| `ppi_rank` | PPI scorer | Rank by `ppi_final` only |
| `best_pathogenic_rank` | VEP CSV | Best, smallest `pathogenic_rank` across variants in this gene |
| `variant_row_count` | VEP CSV | Number of VEP rows mapped to this gene |
| `max_cadd_phred` | VEP CSV | Maximum `cadd_phred` across variants in this gene |
| `mapped_tissues` | PPI scorer | Comma-separated tissues for easier table viewing |
| `mapped_tissue_counts_json` | PPI scorer | JSON tissue mapping counts from HPO parsing |
| `conclusion_code` | phenotype CSV | Phenotype-gene conclusion label |
| `best_disease_score` | phenotype CSV | Best disease-match score in phenotype input |
| `best_disease_name` | phenotype CSV | Best matched disease name |
| `best_omim_id` | phenotype CSV | Best matched OMIM ID |
| `best_orpha_id` | phenotype CSV | Best matched Orphanet ID |
| `best_mondo_id` | phenotype CSV | Best matched MONDO ID |
| `best_disease_match_status` | phenotype CSV | Disease match status from phenotype input |
| `mapping_basis` | phenotype CSV | Basis used by phenotype disease mapping |

## Recommended Interpretation

For final candidate prioritization, start with rows where `final_rank` is not
empty. These genes have both phenotype evidence and PPI network evidence.

For genes without `final_rank`, check:

| Situation | Meaning |
| --- | --- |
| `gene_score` empty, `ppi_final` present | PPI evidence exists, but phenotype score was unavailable |
| `in_network=false` | Gene could not be scored in STRING; PPI score is not informative |
| `final_rank` empty but `ppi_rank` high | Gene is PPI-relevant but not eligible for phenotype+PPI fusion |

For network-only review, sort `*_ppi_score.csv` by `ppi_final` or sort
`*_final_score.csv` by `ppi_rank`.

## Output Paths

API and CLI users can explicitly set both paths:

```json
{
  "output_csv": "../output/case5/case5_final_score.csv",
  "ppi_output_csv": "../output/case5/case5_ppi_score.csv"
}
```

If `ppi_output_csv` is omitted, it is derived from `output_csv`; for example:

```text
case5_final_score.csv -> case5_ppi_score.csv
final_score.csv       -> ppi_score.csv
```
