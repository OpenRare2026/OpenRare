# OpenRare

This branch includes the rare disease dual-anchor PPI scoring workflow in
`script1/`.

## PPI Workflow Quick Start

```bash
cd script1
./setup_env.sh
./download_data.sh
```

Run a command-line scoring job:

```bash
../ppi_env/bin/python Network.py \
  --data-dir ../data \
  --candidate-file candidates.txt \
  --hpo-ids HP:0000488 HP:0000505 \
  --output-csv ../output/result.csv \
  --audit-json ../output/audit.json
```

Start the API:

```bash
cd script1
./run_api.sh
```

See `script1/README.md` for the full method description, data dependencies,
API routes, and case-level entry points.
