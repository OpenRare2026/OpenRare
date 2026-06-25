# OpenRare

<div align="center">
  <img src="./OpenRare.JPG" alt="OpenRare Logo" width="500">
</div>

[🇨🇳 中文版本](README_zh.md) | [🇬🇧 English Version](README.md)

---

## OpenRare Rare Disease Agent

**An Explainable AI System for Rare Disease Variant Prioritization**

Rare Disease Agent is an open-source genetic analysis system designed for rare disease diagnosis scenarios.

Our goal is not to replace clinical doctors in diagnosis, but to help physicians more efficiently identify candidate pathogenic variants that are most likely to explain patient phenotypes from massive genomic variation data, while providing a traceable, interpretable, and auditable evidence chain.

The system integrates patient clinical manifestations, gene sequencing data, biomedical knowledge bases, and AI Agent technology to construct a complete analysis pipeline from symptom understanding, variant annotation, pathogenicity prioritization, to report generation.

---

## Environment (Pixi)

Install once in the repository root directory to uniformly manage all modules:

```bash
cp modules/pipeline/.env.example modules/pipeline/.env   # Configure external data paths
pixi install
pixi run pipeline-test    # or pixi run api
```

Common tasks (root `pixi.toml`):

| Task | Description |
|------|-------------|
| `pipeline-test` | Full pipeline smoke test |
| `api` | Start Full Pipeline API |
| `api-test` | API integration test |
| `vep-dry-run` | VEP configuration dry-run |
| `vep-setup-plugins` / `vep-verify-plugins` | VEP plugin installation and verification |

You can also develop within the pipeline subdirectory: `cd modules/pipeline && pixi install && pixi run pipeline-test`.
The PPI module can run independently: `cd modules/pixi_ppi_score && pixi install && pixi run serve`.

## Pipeline Module

Main pipeline code is located at [`modules/pipeline/`](modules/pipeline/README.md). See [modules/pipeline/README.md](modules/pipeline/README.md) for details.

## PPI Scoring Module

The PPI scoring service is located at [`modules/pixi_ppi_score/`](modules/pixi_ppi_score/README.md), supporting phenotype-gene CSV, VEP CSV, and HPO input, outputting PPI scoring tables and fused final scores.

## Verified Deployment (Linux, pixi 0.68+)

Tested on 172.27.206.113 (Ubuntu 24.04, x86_64). All commands from repo root.

### Prerequisites

```bash
# Install pixi if not present
curl -fsSL https://pixi.sh/install.sh | bash
# Or use the shared binary: /mnt/workspace/hujie/pixi
```

### Quick Install

```bash
git clone <repo-url> && cd pixi_openrare_test

# Install all module environments (one-time, ~10 min)
for m in pipeline pixi_ppi_score pixi_phenotype_score pixi_RAG-HPO \
         pixi_rare_sort_fastapi pixi_report RareSystem; do
    pixi install -m modules/$m/pixi.toml
done
pixi install -e gateway
```

### Configure Data Paths

Three modules need external data. Point them to existing data or download:

```bash
# pipeline — VEP cache + reference + plugins (~50 GB)
cat > modules/pipeline/.env << EOF
OPENRARE_DATA_ROOT=/path/to/vep_runner_resource
OPENRARE_PUBLIC_DATA_ROOT=/path/to/public_data
FULL_PIPELINE_REF_DIR=/path/to/beagle/CHN_ref
FULL_PIPELINE_BEAGLE_JAR=/path/to/beagle.27Feb25.75f.jar
FULL_PIPELINE_GENOS_EVEE_DB=/path/to/genos_evee.cpra.tsv.gz
FULL_PIPELINE_API_PORT=15001
EOF

# ppi_score — HGNC, HPO, OMIM, StringDB (~5 GB)
cat > modules/pixi_ppi_score/.env << EOF
RARE_PPI_HOST=0.0.0.0
RARE_PPI_PORT=15002
RARE_PPI_DATA_DIR=/path/to/ppi_data
EOF

# phenotype_score — symlink or env var to external_data/
export PHENOTYPE_DATA_DIR=/path/to/external_data
```

### Start All Services

```bash
# Daemonize (survives SSH disconnect):
setsid pixi run -e gateway up > /tmp/gateway.log 2>&1 & disown

# Check status:
curl http://127.0.0.1:8100/health
pixi run doctor
```

### Port Map

| Module | Default Port | Notes |
|--------|-------------|-------|
| gateway | 8100 | Public entry |
| pipeline | 15001 | Avoids prod 18901 |
| ppi_score | 15002 | Avoids prod 9000 |
| phenotype_score | 7773 | |
| RAG-HPO | 8010 | Avoids prod 8000/9003 |
| rare_sort | 5010 | Avoids macOS AirPlay 5000 |
| report | 8800 | |
| RareSystem | 18000 | Needs full DB config |

### Verified: 5/7 modules start clean on Linux

```
✅ pipeline          — with .env → VEP data
✅ ppi_score         — with .env → luqi/data
✅ phenotype_score   — zero config
✅ rare_sort         — zero config (needs linux-64 in platforms)
✅ report            — zero config
❌ RAG-HPO           — needs pre-built FAISS vector DB (run pixi run build-db)
❌ RareSystem        — needs DATABASE_URL + downstream service URLs
```

### Smoke Test (local mode)

```bash
# Health check all modules via gateway dispatch
curl http://127.0.0.1:8100/health
curl http://127.0.0.1:8100/m/pipeline/health
curl http://127.0.0.1:8100/m/rare_sort/jobs
```

### Troubleshooting

- **Port conflicts**: production services on 18901/9000/8000 → use ports above
- **rare_sort "unsupported platform"**: add `linux-64` to its pixi.toml platforms
- **gateway dying after SSH exits**: use `setsid` not `nohup`
- **HTTP 502 from httpx**: check `HTTP_PROXY` env var, add `trust_env=False`
- **RAG-HPO stuck at startup**: pre-build vector DB with `pixi run -m modules/pixi_RAG-HPO/pixi.toml build-db`
