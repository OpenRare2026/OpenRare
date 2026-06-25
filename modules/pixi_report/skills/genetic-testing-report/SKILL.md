---
name: genetic-testing-report
description: >-
  Generate clinical single-gene genetic disease testing reports compliant with
  T/SZGIA 4-2018. Use when the user asks for monogenic genetic test reports,
  variant interpretation reports, 单基因遗传病检测报告, 基因检测报告规范,
  T/SZGIA 4-2018, or structured PGx/clinical genetics report output.
---

# Clinical Single-Gene Genetic Testing Report (T/SZGIA 4-2018)

## Overview

Generate reports for **clinical single-gene genetic disease testing** following
group standard **T/SZGIA 4-2018** (*临床单基因遗传病基因检测报告规范*).

| Standard | T/SZGIA 4-2018 |
| -------- | -------------- |
| Scope | Reports from third-party labs, hospital labs, university diagnostic labs |
| Structure | **Main body** (essential findings) + **Appendix** (supplementary detail) |

**Do not** issue a disease diagnosis in the report. State findings and
interpretation; recommend genetic counseling and confirmatory testing when
appropriate.

## When to apply

- User requests a monogenic / single-gene genetic test report
- User provides gene, variant(s), and clinical indication for report drafting
- User asks to format output per T/SZGIA 4-2018 or Chinese PGx report norms
- Agent tool `generate_genetic_testing_report` is invoked

## Mandatory report sections (13 items)

Every complete report **must** include all 13 sections below. Missing sections
are non-compliant.

| # | Section | Required in main body |
| - | ------- | --------------------- |
| 1 | Testing institution info & contact | Yes |
| 2 | Subject (patient) basic info | Yes |
| 3 | Referring institution & physician | Yes |
| 4 | Sample type | Yes |
| 5 | Sample receipt date & report date | Yes |
| 6 | Test item & method | Yes (summary); details in appendix |
| 7 | Test results (variants) | Yes (table) |
| 8 | Test conclusion | Yes |
| 9 | Result interpretation | Yes |
| 10 | Recommendations | Yes |
| 11 | References | Yes |
| 12 | Method description & limitations | Appendix preferred |
| 13 | Signatures & seal | Yes (placeholders if draft) |

## Main body vs appendix

**Main body** — concise, clinician-facing:

- Subject & test metadata (sections 1–6, abbreviated)
- **Primary results**: variants related to the clinical indication
- **Secondary / incidental findings** (only if consented and clinically actionable)
- Conclusion, interpretation, recommendations

**Appendix** — supplementary:

- Full gene panel / exome scope
- Disease background for detected genes
- Detailed method (library prep, sequencing platform, bioinformatics pipeline)
- QC metrics (coverage, depth, sensitivity/specificity)
- Benign / VUS variants not reported in main body (optional listing)
- ACMG evidence details per variant

## Section content requirements

### 1–6. Test metadata

**Subject info must include** (when available):

- Name, sex, date of birth
- Test date / sample accession date
- Test purpose & clinical indication: symptoms, age of onset, imaging/pathology,
  provisional diagnosis, family history, consanguinity

**Sample types**: peripheral blood, DNA, dried blood spot, saliva, tissue, etc.

**Test method summary**: e.g. targeted NGS panel, WES, Sanger confirmation.

### 7. Test results

For each reported variant, include:

| Field | Requirement |
| ----- | ----------- |
| Gene | HGNC symbol |
| Transcript | RefSeq/Ensembl ID with version; state canonical transcript rationale |
| Variant | HGVS c. / p. / g. nomenclature |
| Genotype | het / hom / hemizygous / mosaic (with fraction if known) |
| Zygosity context | de novo / inherited / unknown |
| Allele frequency | gnomAD, ExAC, 1000G, internal cohort |
| In silico prediction | SIFT, PolyPhen, CADD, splice predictors (if applicable) |
| ClinVar / HGMD | Known classification & ID |
| ACMG classification | Pathogenic / Likely pathogenic / VUS / Likely benign / Benign |
| Evidence codes | PM2, PP3, PS1, etc. (when classified) |

Present primary variants in a **table** in the main body.

### 8. Test conclusion

Reporting rules (ACMG-aligned):

| Variant class | Report in conclusion? |
| ------------- | --------------------- |
| Pathogenic / Likely pathogenic, related to indication | **Yes** |
| VUS, related to indication | Only when conclusion is **pending / unresolved** |
| Benign / Likely benign | **No** |
| Secondary / incidental findings | Only if consented; **clinically actionable** only |
| Unrelated VUS | **No** |

Use clear language: "detected", "consistent with", "cannot exclude" — avoid
definitive disease diagnosis.

### 9. Result interpretation

For each reported variant:

1. ACMG evidence summary (database hits, literature, segregation, de novo status)
2. Phenotype correlation with subject's clinical presentation
3. Inheritance pattern (AD / AR / XL / mitochondrial)
4. Recurrence risk for family members

### 10. Recommendations

Typical items:

- Genetic counseling referral
- Familial segregation / parental testing
- Expanded testing if negative or inconclusive
- Specialist referral aligned with phenotype
- Re-analysis when new evidence emerges

### 11. References

Vancouver or numbered style. Include PMIDs/DOIs for all citations used in
pathogenicity assessment.

### 12. Method & limitations

State:

- Specimen requirements & extraction method
- Sequencing platform & read length
- Target region / gene list / exome coverage
- Variant calling & annotation pipeline
- Validation method for reportable variants (Sanger, etc.)
- **Limitations**: regions not covered, genes not tested, types of variants
  not detectable (CNV, repeat expansions, methylation, low-level mosaicism)
- Analytical sensitivity & specificity for SNV/indels (and CNV if applicable)

### 13. Signatures & seal

- Report author (检验者)
- Result reviewer (核对者)
- Final approver (签发者)
- Third-party lab: "检测报告专用章" placeholder
- Report version / revision note if amended

## Tool: `generate_genetic_testing_report`

When exposed as an LLM tool, accept structured input and return JSON matching
[`report-schema.json`](report-schema.json).

### Input parameters

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `testing_institution` | object | Yes | Name, address, phone, lab license |
| `subject` | object | Yes | Patient demographics & clinical indication |
| `referring` | object | Yes | Referring hospital & physician |
| `sample` | object | Yes | Type, collection date, receipt date |
| `test` | object | Yes | Panel name, method, genes covered |
| `variants` | array | Yes | Detected variants (see schema) |
| `conclusion` | string | Yes | Primary conclusion text |
| `interpretation` | string | Yes | Detailed interpretation |
| `recommendations` | array[string] | Yes | Action items |
| `references` | array[object] | Yes | `{pmid, doi, citation}` |
| `method_limitations` | object | Yes | Method summary + limitation list |
| `signatures` | object | No | Author, reviewer, approver names |
| `include_appendix` | bool | No | Default `true` |

### Output

Return JSON conforming to `report-schema.json`. Also produce a human-readable
Markdown summary in `report_markdown` field.

## Variant classification quick reference

Follow **ACMG/AMP 2015** (PMID: 25741868) and ClinGen updates:

- Combine evidence using PS / PM / PP / BA / BS / BP codes
- Report only classifications with sufficient evidence
- Never upgrade VUS to pathogenic without strong evidence
- Document every evidence item used

## Quality checklist

Before finalizing, verify:

```
Report compliance:
- [ ] All 13 T/SZGIA sections present
- [ ] HGVS nomenclature used for all variants
- [ ] Transcript ID and version specified
- [ ] ACMG class stated for each reported variant
- [ ] No benign/LB variants in conclusion
- [ ] VUS reporting follows indication-only rule
- [ ] No definitive disease diagnosis language
- [ ] Limitations section covers method scope
- [ ] References match cited evidence
- [ ] Signatures / seal placeholders included
```

## Example conclusion phrasing

**Good:**

> In the *CFTR* gene, a likely pathogenic variant c.1521_1523del (p.Phe508del)
> was detected in the homozygous state, consistent with the clinical suspicion
> of cystic fibrosis. Genetic counseling and familial carrier testing are
> recommended.

**Avoid:**

> The patient has cystic fibrosis. (diagnosis — not allowed)

## Additional resources

- JSON schema for tool I/O: [report-schema.json](report-schema.json)
- Markdown report template: [report-template.md](report-template.md)
- Standard reference: T/SZGIA 4-2018, 深圳市生命科技产学研资联盟, 2018-12-26
