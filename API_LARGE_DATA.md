# Large Data API

Use the clean-case async API for large VEP CSV files.

This path is optimized for files like a 9.8 GB VEP CSV:

- VEP CSV is streamed in chunks.
- Only `gene_symbol`, `pathogenic_rank`, and `cadd_phred` are read.
- PPI scoring uses anchor-side batch shortest-path maps instead of one graph
  traversal per candidate gene.
- Neighbor JSON is skipped by default; set `include_neighbors=true` only for
  small debug runs.

## Start API

```bash
cd script1
RARE_PPI_PORT=9000 ./run_api.sh
```

## Submit Large Local Files

```bash
curl -X POST http://127.0.0.1:9000/score/clean-case/async \
  -H 'Content-Type: application/json' \
  -d '{
    "phenotype_gene_csv": "../input/gene_phenotype_score.csv",
    "vep_output_csv": "../input/tes1.vep.csv",
    "hpo_file": "../input/hpo_ids.txt",
    "output_csv": "../output/case_final_score.csv",
    "clean_output_dir": true,
    "include_neighbors": false,
    "include_evidence_json": false,
    "include_audit": false,
    "vep_chunksize": 250000
  }'
```

Response:

```json
{
  "job_id": "...",
  "status": "queuing",
  "mode": "clean_case"
}
```

## Check And Download

```bash
curl http://127.0.0.1:9000/score/<job_id>
curl -L -o final_score.csv http://127.0.0.1:9000/score/<job_id>/csv
```

## Upload API

Multipart clients can use:

```text
POST /score/clean-case/upload/async
```

Important form fields:

```text
phenotype_gene_csv=@gene_phenotype_score.csv
vep_output_csv=@tes1.vep.csv
hpo_file=@hpo_ids.txt
output_csv=../output/case_final_score.csv
include_neighbors=false
include_evidence_json=false
include_audit=false
vep_chunksize=250000
```
