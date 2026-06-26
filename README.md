# OpenRare

<div align="center">
  <img src="./OpenRare.JPG" alt="OpenRare Logo" width="500">
</div>

[🇨🇳 中文版本](README_zh.md) | [🇬🇧 English Version](README.md)

---

## OpenRare Rare Disease Agent

**An Explainable AI System for Rare Disease Variant Prioritization**

OpenRare integrates patient clinical manifestations, gene sequencing data,
biomedical knowledge bases, and AI Agent technology into a complete analysis
pipeline: symptom understanding → variant annotation → pathogenicity
prioritization → report generation.

---

## Architecture

```
pixi_openrare_test/
├── pixi.toml                    # Root workspace + shared tasks
├── doctor/                      # Module health check CLI
├── gateway/                     # Single-entry orchestrator
├── pipeline/                    # End-to-end pipeline runner
└── modules/
    ├── pipeline/                # VCF → VEP annotation → pathogenic sorting
    ├── pixi_ppi_score/          # Protein-protein interaction network scoring
    ├── pixi_phenotype_score/    # HPO semantic similarity scoring
    ├── pixi_RAG-HPO/            # Clinical phenotype → HPO term extraction (LLM+RAG)
    ├── pixi_rare_sort_fastapi/  # Variant-level scoring and ranking
    ├── pixi_report/             # Genetic testing report generation (DeepAgents)
    └── RareSystem/              # Full-stack genetic diagnosis system (FastAPI+React)
```

Each module runs in its **own isolated Pixi environment** — independent Python
versions and dependency trees. The **gateway** launches modules as subprocesses
and serves as the single public entry point. A **pipeline runner** coordinates
data flow across all six analysis steps.

---

## Prerequisites

- **Pixi** ≥ 0.68 — [install guide](https://pixi.sh/latest/#installation)
- **Linux x86_64** (most modules require conda-forge/bioconda packages)
- **Disk space**: ~50 GB for VEP cache and reference data (pipeline module)

---

## Quick Start

### 1. Clone and install

```bash
git clone <repo-url> && cd pixi_openrare_test

# Install all module environments (~10 min, requires network)
for m in pipeline pixi_ppi_score pixi_phenotype_score pixi_RAG-HPO \
         pixi_rare_sort_fastapi pixi_report RareSystem; do
    pixi install -m modules/$m/pixi.toml
done
pixi install -e gateway
```

### 2. Configure data paths

Three modules require external data. Copy example configs and fill in paths:

**pipeline** — VEP cache, reference genome, annotation databases (~50 GB):

```bash
cp modules/pipeline/.env.example modules/pipeline/.env
# Edit modules/pipeline/.env and set:
#   OPENRARE_DATA_ROOT      — VEP cache + plugin directory
#   OPENRARE_PUBLIC_DATA_ROOT — public reference data (HGNC, pseudogene DB)
#   FULL_PIPELINE_REF_DIR   — Beagle phasing reference panel
#   FULL_PIPELINE_BEAGLE_JAR — Beagle JAR path
#   FULL_PIPELINE_GENOS_EVEE_DB — genos_evee database
```

OPENRARE_PUBLIC_DATA_ROOT must contain these subdirectories:

```
$OPENRARE_PUBLIC_DATA_ROOT/
├── phenotype_hpo_v1/
│   └── hgnc_complete_set.txt
└── Pseudogene/
    ├── GENCODE/release_49/gencode.v49.2wayconspseudos.gtf.gz
    └── Pseudogene.org/Human90/Human90.txt
```

VEP plugins and annotation databases are configured separately in
`modules/pipeline/modules/vep_runner/config/vep_runner_config.json`.

**ppi_score** — HGNC, HPO ontology, OMIM, StringDB (~5 GB):

```bash
cp modules/pixi_ppi_score/.env.example modules/pixi_ppi_score/.env
# Edit modules/pixi_ppi_score/.env and set:
#   RARE_PPI_DATA_DIR — directory containing hgnc_complete_set.txt,
#                       hp.obo, mim2gene.txt, genemap2.txt, etc.
```

Required files under RARE_PPI_DATA_DIR: `hgnc_complete_set.txt`, `hp.obo`,
`mim2gene.txt`, `genemap2.txt`, plus StringDB, GTEx, HPA, and DEPMAP data.
See [modules/pixi_ppi_score/docs/DEPENDENCIES.md](modules/pixi_ppi_score/docs/DEPENDENCIES.md).

**phenotype_score** — HPO ontology, HGNC, OMIM, Orphanet:

```bash
cd modules/pixi_phenotype_score
# Option A: symlink to existing data
ln -sf /path/to/external_data external_data

# Option B: set environment variable
export PHENOTYPE_DATA_DIR=/path/to/external_data
```

Required structure under external_data:
`hpo/{hp.obo,phenotype.hpoa,genes_to_disease.txt}`,
`hgnc/hgnc_complete_set.txt`, `mondo/mondo-rare.obo`,
`omim/omim_20250411.sqlite3`, `orphanet/Orphapackets`,
`indexes/orpha_gene_profiles.pkl`.

**RAG-HPO** — LLM API key, pre-built FAISS vector database:

```bash
cp modules/pixi_RAG-HPO/.env.example modules/pixi_RAG-HPO/.env
# Edit modules/pixi_RAG-HPO/.env and set:
#   RAG_HPO_API_KEY     — LLM API key
#   RAG_HPO_BASE_URL    — LLM endpoint
#   RAG_HPO_MODEL       — model name

# Build the FAISS vector database (requires internet for SapBERT model)
cd modules/pixi_RAG-HPO && pixi run build-db
```

### 3. Start all services

```bash
# Start all modules via the gateway (daemon):
setsid pixi run -e gateway up > /tmp/openrare_gateway.log 2>&1 & disown

# Check status:
curl http://127.0.0.1:8100/health
pixi run doctor
```

### 4. Run the analysis pipeline

```bash
# Full 6-step pipeline (HPO→VEP→Phenotype→PPI→Rank→Report):
pixi run -e gateway pipeline-full \
  -v /path/to/sample.vcf \
  -t "patient symptom description" \
  -o ./output_dir \
  --chromosomes 1-22

# Or run individual module tasks:
pixi run api                    # Start pipeline API standalone
pixi run pipeline-test          # Smoke-test the pipeline
```

### 5. Stop

```bash
# Ctrl-C if running in foreground, or:
pkill -f "gateway.main"
```

---

## Port Map

| Service | Port | Notes |
|---------|------|-------|
| gateway | 8100 | Public entry point |
| RAG-HPO | 5001 | HPO extraction API |
| pipeline | 5002 | VEP annotation API |
| phenotype_score | 5003 | Phenotype scoring API |
| ppi_score | 5004 | PPI scoring API |
| rare_sort | 5005 | Variant ranking API |
| report | 5006 | Report generation API |
| RareSystem | 18000 | Full-stack diagnosis (backend) |

---

## Module Overview

| Module | Description | Docs |
|--------|-------------|------|
| pipeline | VCF → phasing → VEP annotation → pathogenic sorting | [README](modules/pipeline/README.md) |
| pixi_ppi_score | PPI network scoring with StringDB | [README](modules/pixi_ppi_score/README.md) |
| pixi_phenotype_score | HPO semantic similarity scoring | [README](modules/pixi_phenotype_score/README.md) |
| pixi_RAG-HPO | LLM+RAG phenotype extraction | [README](modules/pixi_RAG-HPO/README.md) |
| pixi_rare_sort_fastapi | Variant-level scoring and ranking | [README](modules/pixi_rare_sort_fastapi/README.md) |
| pixi_report | Genetic testing report (DeepAgents+MCP) | [README](modules/pixi_report/README.md) |
| RareSystem | Full-stack diagnosis (FastAPI+React+Neo4j) | [README](modules/RareSystem/README.md) |

---

## Development Tools

### doctor — module health check

```bash
pixi run doctor
```

Reports readiness of all 7 modules: environment variables, data file existence,
code importability. No modules are modified — read-only diagnostics.

### Pipeline runner

```bash
# Local mode (services must be running via gateway):
pixi run -e gateway pipeline-full -v sample.vcf -t "symptoms"

# Remote mode (use existing services without starting locally):
pixi run -e gateway pipeline-full --remote -v sample.vcf -t "symptoms"

# Limit chromosomes (faster for test data):
pixi run -e gateway pipeline-full --chromosomes 1 -v sample.vcf -t "symptoms"
```

---

## Troubleshooting

| Symptom | Likely cause | Solution |
|---------|-------------|----------|
| `unsupported-platform` on install | Module pixi.toml missing your platform | Add platform via `pixi workspace platform add linux-64` |
| Pipeline job fails immediately | `.env` not configured | Create `.env` from `.env.example`, verify paths exist |
| `FileNotFoundError` in pipeline job | Missing data under OPENRARE_PUBLIC_DATA_ROOT | Ensure Pseudogene/ and phenotype_hpo_v1/ subdirectories exist |
| Gateway exits after SSH disconnect | `nohup` doesn't shield pixi subprocesses | Use `setsid ... & disown` |
| Module exits with code 1 on start | Missing data path or port conflict | Run `pixi run doctor`, check port availability |
| RAG-HPO server hangs at startup | Vector DB not built, model not cached | Run `pixi run build-db` in RAG-HPO module directory |
| HTTP 502 from pipeline runner | HTTP_PROXY intercepts local traffic | Unset HTTP_PROXY or use `trust_env=False` |
| Port already in use | Another process on that port | Change port in `gateway/src/gateway/main.py` → MODULES |

---

## Data Sources

Most external data files referenced above can be obtained from:

- **VEP cache & plugins**: [Ensembl VEP installation](https://useast.ensembl.org/info/docs/tools/vep/script/vep_cache.html)
- **HGNC complete set**: <https://www.genenames.org/download/>
- **HPO ontology (hp.obo)**: <https://github.com/obophenotype/human-phenotype-ontology>
- **OMIM**: <https://www.omim.org/downloads> (requires license)
- **Orphanet**: <https://www.orphadata.com/>
- **StringDB**: <https://string-db.org/>
- **ClinVar**: <https://ftp.ncbi.nlm.nih.gov/pub/clinvar/>
- **dbNSFP**: <https://sites.google.com/site/jpopgen/dbNSFP>
- **CADD**: <https://cadd.gs.washington.edu/download>
- **SpliceAI**: <https://github.com/Illumina/SpliceAI>
- **AlphaMissense**: <https://github.com/google-deepmind/alphamissense>
- **GTEx**: <https://gtexportal.org/home/datasets>
- **SapBERT model**: <https://huggingface.co/pritamdeka/SapBERT-mnli-snli-scinli-scitail-mednli-stsb>

For the full list of required files per module, see each module's README and
configuration files (`.env.example`, `paths.example.toml`, `config/paths.toml`).
