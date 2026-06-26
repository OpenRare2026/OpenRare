# OpenRare
![last commit](https://img.shields.io/badge/last_commit-2026.06.26-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)
![Badge](https://hitscounter.dev/api/hit?url=https%3A%2F%2Fgithub.com%2FOpenRare2026%2FOpenRare&label=Visitors&icon=github&color=%23198754&message=&style=flat&tz=UTC)

<div align="center">
  <img src="./OpenRare.png" alt="OpenRare Logo" width="500">
</div>

[🇨🇳 中文版本](README_zh.md) | [🇬🇧 English Version](README.md)

---

## OpenRare Rare Disease Agent

**An Explainable AI System for Rare Disease Variant Prioritization**

Rare Disease Agent is an open-source genetic analysis system for rare disease diagnosis scenarios.

Our goal is not to replace clinical doctors in diagnosis, but to help doctors more efficiently identify candidate pathogenic variants that are most likely to explain patient phenotypes from massive genetic variations, and provide a traceable, explainable, and auditable evidence chain.

The system integrates patient clinical manifestations, gene sequencing data, biomedical knowledge bases, and AI Agent technology to build a complete analysis pipeline from symptom understanding, variant annotation, pathogenicity prioritization to report generation.

---

## Environment Setup (Pixi)

Install once in the repository root directory to uniformly manage all modules:

```bash
cp modules/pipeline/.env.example modules/pipeline/.env   # Configure external data paths
pixi install
pixi run pipeline-test    # or pixi run api
```

Common tasks (root directory `pixi.toml`):

| Task | Description |
|------|-------------|
| `pipeline-test` | Full pipeline smoke test |
| `api` | Start Full Pipeline API |
| `api-test` | API integration test |
| `vep-dry-run` | VEP configuration dry-run |
| `vep-setup-plugins` / `vep-verify-plugins` | VEP plugin installation and verification |

You can also develop only in the pipeline subdirectory: `cd modules/pipeline && pixi install && pixi run pipeline-test`.
PPI module can run independently: `cd modules/pixi_ppi_score && pixi install && pixi run serve`.

## Pipeline Module

Main pipeline code is located at [`modules/pipeline/`](modules/pipeline/README.md). See [modules/pipeline/README.md](modules/pipeline/README.md) for details.

## Phenotype Association Module

Phenotype association scoring module code is located at [`modules/pixi_phenotype_score`](modules/pixi_phenotype_score/README.md). See [modules/pixi_phenotype_score/README.md](modules/pixi_phenotype_score/README.md) for details.

## PPI Scoring Module

PPI scoring service is located at [`modules/pixi_ppi_score/`](modules/pixi_ppi_score/README.md), supports phenotype-gene CSV, VEP CSV and HPO input, outputs PPI scoring table and fused final score.

PPI external database can be prepared with one click from the repository root: `pixi run ppi-download-data && pixi run ppi-check-data`. When needing to delegate to other Agents, you can directly use [`modules/pixi_ppi_score/docs/DATA_SETUP_PROMPT.md`](modules/pixi_ppi_score/docs/DATA_SETUP_PROMPT.md).

## RAG-HPO Module

LLM + RAG driven clinical phenotype automatic extraction system, extracting Human Phenotype Ontology (HPO) terms from medical records in any language. Code is located at [`modules/pixi_RAG-HPO/`](modules/pixi_RAG-HPO/README.md).

## Rare Sort Module

Rare disease variant ranking scoring service, performing variant-level scoring on VEP wide tables, with optional gene phenotype weighting and PPI network weighting. Code is located at [`modules/pixi_rare_sort_fastapi/`](modules/pixi_rare_sort_fastapi/README.md).

## RareSystem Module

Full-stack genetic diagnosis system, supporting multi-type variant detection (SNV/INDEL/STR/CNV), ACMG automatic classification, dual-track reporting and RAG-based intelligent Q&A. Backend FastAPI + frontend React 18. Code is located at [`modules/RareSystem/`](modules/RareSystem/README.md).

## Report Generation Module

Genomic variant analysis report service is located at [`modules/pixi_report/`](modules/pixi_report/README.md), based on ranked wide tables, clinical phenotypes and HPO terms, generating traceable analysis reports via FastAPI streaming or command line.

---

## Unified Entry Point (Gateway)

All modules are started and managed through Gateway, exposing a single port (8000) to the outside.

```bash
# Install gateway environment
pixi install -e gateway

# One-click start all modules (daemon):
setsid pixi run -e gateway up > /tmp/openrare_gateway.log 2>&1 & disown

# Check status:
curl http://127.0.0.1:8000/health
```

Gateway starts independent pixi subprocesses for each module, and each module can use different Python versions and dependencies without conflict.

### Port Mapping

| Service | Port | Description |
|---------|------|-------------|
| gateway | 8000 | Unified entry point |
| RAG-HPO | 8001 | HPO extraction API |
| pipeline | 8002 | VEP annotation API |
| phenotype_score | 8003 | Phenotype scoring API |
| ppi_score | 8004 | PPI scoring API |
| rare_sort | 8005 | Variant ranking API |
| report | 8006 | Report generation API |
| RareSystem | 8007 | Full-stack diagnosis system |

---

## Module Health Check (Doctor)

```bash
pixi run doctor
```

Check the operational readiness of all modules: environment variables, data files, code importability. Read-only diagnostics, does not modify any module code.

## Full Pipeline Orchestration (Pipeline Runner)

Connect all 6 analysis steps:

```
HPO RAG → VEP Annotation → Phenotype Scoring → PPI Scoring → Variant Ranking → Report Generation
```

```bash
# After starting all services, run the full pipeline:
pixi run -e gateway pipeline-full \
  -v /path/to/sample.vcf \
  -t "patient symptom description" \
  -o ./output \
  --chromosomes 1-22
```

---

## Complete Deployment Steps

### 1. Install All Modules

```bash
git clone <repo-url> && cd pixi_openrare_test

for m in pipeline pixi_ppi_score pixi_phenotype_score pixi_RAG-HPO \
         pixi_rare_sort_fastapi pixi_report RareSystem; do
    pixi install -m modules/$m/pixi.toml
done
pixi install -e gateway
```

### 2. Configure Data Paths

**pipeline** — VEP cache, reference genome, annotation databases (~50 GB):

```bash
cp modules/pipeline/.env.example modules/pipeline/.env
# Edit modules/pipeline/.env, set:
#   OPENRARE_DATA_ROOT        — VEP cache and plugin directory
#   OPENRARE_PUBLIC_DATA_ROOT — public reference data (HGNC, pseudogene database)
#   FULL_PIPELINE_REF_DIR     — Beagle phasing reference panel
#   FULL_PIPELINE_BEAGLE_JAR  — Beagle JAR path
```

OPENRARE_PUBLIC_DATA_ROOT needs to contain the following subdirectories:
```
$OPENRARE_PUBLIC_DATA_ROOT/
├── phenotype_hpo_v1/hgnc_complete_set.txt
└── Pseudogene/
    ├── GENCODE/release_49/gencode.v49.2wayconspseudos.gtf.gz
    └── Pseudogene.org/Human90/Human90.txt
```

**ppi_score** — HGNC, HPO ontology, OMIM, StringDB (~5 GB):

```bash
cp modules/pixi_ppi_score/.env.example modules/pixi_ppi_score/.env
# Set RARE_PPI_DATA_DIR to point to the directory containing hgnc_complete_set.txt, hp.obo, etc.
# Or automatically download via pixi run ppi-download-data
```

**phenotype_score** — Link or download external data:

```bash
cd modules/pixi_phenotype_score
ln -sf /path/to/external_data external_data
```

**RAG-HPO** — Configure LLM API key and build vector database:

```bash
cp modules/pixi_RAG-HPO/.env.example modules/pixi_RAG-HPO/.env
# Edit .env, set RAG_HPO_API_KEY, RAG_HPO_BASE_URL, RAG_HPO_MODEL

# Build FAISS vector database (requires internet to download SapBERT model, ~2.5 GB):
cd modules/pixi_RAG-HPO && pixi run build-db
```

### 3. Start Services

```bash
setsid pixi run -e gateway up > /tmp/openrare_gateway.log 2>&1 & disown
curl http://127.0.0.1:8000/health
pixi run doctor
```

### 4. Stop

```bash
pkill -f "gateway.main"
```

---

## Data Download Reference

| Data | Source |
|------|--------|
| VEP cache and plugins | [Ensembl VEP](https://useast.ensembl.org/info/docs/tools/vep/script/vep_cache.html) |
| HGNC complete dataset | <https://www.genenames.org/download/> |
| HPO ontology (hp.obo) | <https://github.com/obophenotype/human-phenotype-ontology> |
| OMIM | <https://www.omim.org/downloads> (license required) |
| Orphanet | <https://www.orphadata.com/> |
| StringDB | <https://string-db.org/> |
| ClinVar | <https://ftp.ncbi.nlm.nih.gov/pub/clinvar/> |
| CADD | <https://cadd.gs.washington.edu/download> |
| SpliceAI | <https://github.com/Illumina/SpliceAI> |
| GTEx | <https://gtexportal.org/home/datasets> |
| SapBERT model | <https://huggingface.co/pritamdeka/SapBERT-mnli-snli-scinli-scitail-mednli-stsb> |

---

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| `unsupported-platform` during installation | pixi.toml missing current platform | `pixi workspace platform add linux-64` |
| Pipeline job fails immediately | `.env` not configured | Create `.env` from `.env.example`, verify paths exist |
| `FileNotFoundError` with Pseudogene | Missing subdirectories under OPENRARE_PUBLIC_DATA_ROOT | Ensure Pseudogene/ and phenotype_hpo_v1/ subdirectories exist |
| Gateway exits after SSH disconnect | `nohup` doesn't protect pixi subprocesses | Use `setsid ... & disown` |
| Module startup fails (exit code 1) | Missing data or port conflict | Run `pixi run doctor` to check |
| RAG-HPO hangs at startup | Vector DB not built or model not cached | Run `pixi run build-db` |
| Port already in use | Another process on that port | Change port in `gateway/src/gateway/main.py` → MODULES |

---

## Contact

- **Email**: openrare@163.com
- **Issues**: [GitHub Issues](https://github.com/OpenRare2026/OpenRare/issues)
