---
name: rare-disease-report
description: >
  Generate a candidate-gene diagnostic report for the rare-disease gene-analysis
  pipeline, delivered as streaming markdown plus a downloadable PDF. Built from the
  annotated variant wide table (main line) plus optional phenotype-HPO and PPI score
  tables, organized per candidate gene. Use whenever the user wants to produce,
  assemble, export, or download a report / summary / PDF of the gene-diagnosis
  results — phrases like "出报告", "生成报告", "导出 PDF", "把结果整理成报告". Do NOT
  use it to run the underlying VEP / phenotype / PPI analyses — only to turn their
  outputs into a report.
---

# Rare-disease candidate-gene report

Turns the pipeline's CSV outputs into one report, in two forms from a single source
of truth: **streaming markdown** for the UI and a **downloadable PDF**. The markdown
is canonical; the PDF is rendered from the finished markdown.

This bundle is a skill in packaging. In an environment where the agent can run code
it works directly (read this file, run the scripts). Because the target UI agent
**cannot run code**, the scripts are hosted behind a small FastAPI service
(`service/app.py`); the agent calls that service, and registers this skill as a thin
tool pointing at it. Skill = portable logic; service = execution host; tool = the
agent's entry point — same thing, three layers.

## The one rule that matters

Hard data — variant coordinates, HGVS, frequencies, scores, OMIM/MONDO/HP IDs — is
rendered **deterministically from the CSVs by `build_context.py`**. The model only
writes the narrative paragraphs in the `{{narrative:...}}` slots. A frequency or an
OMIM id must never be typed by the model: in a genetic report a transposed digit is
invisible and dangerous. `validate_narrative.py` enforces this — any number/ID in a
narrative that is not present in that slot's `ground_text` is rejected before the
text is shown.

## Inputs

- **Wide table CSV** (required, main line): per-variant VEP annotation with
  `gene_symbol`, `pathogenic_rank`, consequence/impact, HGVS, REVEL/CADD, `gnomAD_*`,
  ClinVar, `evidence_summary`. Drives gene selection and ordering.
- **Phenotype-HPO score CSV** (optional): per-gene `gene_score`, `conclusion_code`,
  best disease + IDs, HPO match. Joined on `gene_symbol`.
- **PPI score CSV** (optional): per-gene `ppi_final` and axes. Joined on `gene`.
- **Patient HPO list** + **symptom text** (optional, for the header).
- **Scope**: top-N genes (`--top-n`, default 10) **or** an explicit `--genes` list
  (overrides top-N). Both modes are supported. `--k` variants per gene (default 5).

Field meanings live in `assets/glossary.md`, distilled from each source's free-form
README. Feed the **glossary** (not raw READMEs) to the narrative step; nothing in the
pipeline parses a README, so their free format is fine.

## Design invariants (in build_context.py)

- **Backbone is the gene**, ordered strictly by best (minimum) `pathogenic_rank`.
  No validity filtering — that is a later concern.
- **Schema-driven rendering.** Only columns actually present and non-empty are shown;
  never assume a column exists because a README lists it — versions drift.
- **Graceful missing sources.** A gene with no phenotype/PPI row gets a "本模块无该
  基因数据" note, not an error. Most genes lack PPI rows — that is normal.
- **Normalization in the formatter:** `265000.0 → OMIM:265000`, mixed/`-` →
  scientific notation or `—`, JSON-in-CSV parsed, multi-term consequence compacted.

## Workflow (offline / code-exec environment)

```bash
# 1. deterministic skeleton: report.md (+ {{narrative:...}} slots) + narrative_context.json
python scripts/build_context.py \
  --wide WIDE.csv --phenotype PHENO.csv --ppi PPI.csv \
  --top-n 10 --k 5 --case-id CASE --hpo-file hpo.txt --symptom-text "..." \
  --outdir OUT
#    or pin specific genes (overrides --top-n):  --genes "CHRNG,HRAS,DNMT3B"

# 2. fill each {{narrative:slot}} from narrative_context.json using ONLY the numbers
#    already in that slot; validate with scripts/validate_narrative.py; assemble
#    OUT/report.filled.md

# 3. render the finished markdown to PDF
python scripts/render_pdf.py --md OUT/report.filled.md --pdf OUT/report.pdf
```

## Workflow (their runtime: hosted as a service)

`service/app.py` does all three steps behind one endpoint, with streaming:

```
POST /report/stream  -> Server-Sent Events:
   meta  (selected genes, coverage)
   md    (deterministic blocks flush immediately; each narrative slot is
          generated, validated, then emitted)
   done  (pdf_url)
GET  /report/{id}/pdf -> the rendered PDF
```

Plug your model into `_generate_once` (an Anthropic streaming path is stubbed; set
`ANTHROPIC_API_KEY`). Without a key it emits grounded, number-free placeholder prose
so the whole pipeline runs end-to-end.

## Files

- `scripts/build_context.py` — join + select + normalize; emits skeleton + per-slot
  grounding (`ground_text`). One small provider class per data source.
- `scripts/validate_narrative.py` — number/ID whitelist guard against hallucination.
- `scripts/render_pdf.py` — markdown → HTML → PDF via **xhtml2pdf** (pure pip).
- `assets/report.css` — A4 print styling, running footer + page numbers, CJK font.
- `assets/fonts/NotoSansSC-Regular.ttf` — bundled CJK font (see README there).
- `assets/glossary.md` — distilled field dictionary for the narrative step.
- `service/app.py`, `service/requirements.txt` — the FastAPI host.

## Dependencies

`pandas`, `markdown`, `xhtml2pdf` — all pip, **no system packages**. Chinese rendering
needs the bundled `.ttf` (travels with the skill); reportlab parses it directly, so
no apt-get / fontconfig. `fastapi`/`uvicorn` for the service; `anthropic` only if you
fill narratives server-side.
