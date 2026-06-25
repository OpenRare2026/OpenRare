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
