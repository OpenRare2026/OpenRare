# Large Data API

Use the clean-case async API for large VEP CSV files.

This path is optimized for files like a 9.8 GB VEP CSV:

- VEP CSV is streamed in chunks.
- Only `gene_symbol`, `pathogenic_rank`, and `cadd_phred` are read.
- PPI scoring uses anchor-side batch shortest-path maps instead of one graph
  traversal per candidate gene.
- Neighbor JSON is skipped by default; set `include_neighbors=true` only for
  small debug runs.
- By default, candidates are the union of the top 30000 VEP genes and the top
  30000 phenotype-ranked genes. Set `candidate_top_n=0` to use all genes.

## Start API

```bash
cd script1
RARE_PPI_PORT=9000 ./run_api.sh
```

Confirm that the running service is the large-data version:

```bash
curl http://127.0.0.1:9000/version | python -m json.tool
```

The response should list `candidate_top_n`, `output_all_ppi_fields`, and
`vep_chunksize` under `supports_parameters`. If a request gets 422 saying these
fields do not exist, the API process is still running old code; pull the latest
repository and restart `run_api.sh`.

## Submit Large Files With curl -F

Use the upload async endpoint when the client and API run on the same machine or
when you need to upload files through HTTP:

```bash
curl -X POST http://127.0.0.1:9000/score/clean-case/upload/async \
  -F "phenotype_gene_csv=@/home/xiesiwei/vep_runner/26B01490717_3a1e48_fork16_hpo_/gene_phenotype_score.csv" \
  -F "vep_output_csv=@/home/xiesiwei/vep_runner/26B01490717_3a1e48_fork16_hpo_/tes1.vep.csv" \
  -F "hpo_file=@/path/to/hpo_ids.txt" \
  -F "output_csv=/home/xiesiwei/vep_runner/26B01490717_3a1e48_fork16_hpo_/output/case_final_score.csv" \
  -F "clean_output_dir=true" \
  -F "candidate_top_n=30000" \
  -F "output_all_ppi_fields=true" \
  -F "include_audit=false" \
  -F "vep_chunksize=250000"
```

The response contains a `job_id`. Poll it to see progress:

```bash
curl http://127.0.0.1:9000/score/<job_id> | python -m json.tool
```

The job status includes `stage`, `message`, and `progress`.

## Submit Existing Server Paths

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
    "output_all_ppi_fields": false,
    "candidate_top_n": 30000,
    "timeout": 0,
    "vep_chunksize": 250000
  }'
```

To output all PPI fields, including evidence JSON and `top_neighbors_json`, use:

```json
{
  "output_all_ppi_fields": true,
  "candidate_top_n": 30000
}
```

This is heavier because every retained gene gets evidence JSON and top STRING
neighbors in the final CSV.

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

Important upload form fields:

```text
phenotype_gene_csv=@gene_phenotype_score.csv
vep_output_csv=@tes1.vep.csv
hpo_file=@hpo_ids.txt
output_csv=../output/case_final_score.csv
include_neighbors=false
include_evidence_json=false
include_audit=false
output_all_ppi_fields=false
candidate_top_n=30000
vep_chunksize=250000
```
