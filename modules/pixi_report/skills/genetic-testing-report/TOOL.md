# Tool Spec: `generate_genetic_testing_report`

LangChain / Deep Agent tool definition for T/SZGIA 4-2018 compliant report generation.

## Tool metadata

| Field | Value |
| ----- | ----- |
| Name | `generate_genetic_testing_report` |
| Skill | `skills/genetic-testing-report/SKILL.md` |
| Output schema | `skills/genetic-testing-report/report-schema.json` |
| Template | `skills/genetic-testing-report/report-template.md` |

## Description (for `@tool` docstring)

```
Generate a clinical single-gene genetic disease testing report compliant with
T/SZGIA 4-2018 (临床单基因遗传病基因检测报告规范).

Input: structured patient, sample, test, and variant data.
Output: JSON report with all 13 mandatory sections plus optional appendix.

Rules:
- Use HGVS nomenclature for variants
- Classify variants per ACMG/AMP 2015
- Do NOT issue disease diagnosis; state findings and recommend counseling
- Report P/LP variants related to indication; omit B/LB from conclusion
- Report VUS only when conclusion is unresolved and variant relates to indication
- Include method limitations and signature placeholders
```

## Parameters

```python
@tool
def generate_genetic_testing_report(
    testing_institution: dict,
    subject: dict,
    referring: dict,
    sample: dict,
    test: dict,
    variants: list[dict],
    conclusion: str,
    interpretation: str,
    recommendations: list[str],
    references: list[dict],
    method_limitations: dict,
    signatures: dict | None = None,
    include_appendix: bool = True,
) -> str:
    """Generate T/SZGIA 4-2018 compliant monogenic genetic testing report JSON."""
```

### Parameter schemas (summary)

See `report-schema.json` for full JSON Schema. Key nested objects:

**`testing_institution`**
```json
{"name": "XX医学检验实验室", "address": "...", "phone": "...", "lab_license": "..."}
```

**`subject`**
```json
{
  "name": "张*",
  "sex": "男",
  "date_of_birth": "2020-01-15",
  "clinical_indication": "反复呼吸道感染，疑似囊性纤维化",
  "symptoms": ["咳嗽", "胰腺功能不全"],
  "family_history": "父母非近亲婚配",
  "provisional_diagnosis": "囊性 fibrosis 待排"
}
```

**`variants[]`**
```json
{
  "gene": "CFTR",
  "transcript": "NM_000492.4",
  "hgvs_c": "c.1521_1523del",
  "hgvs_p": "p.Phe508del",
  "genotype": "hom",
  "inheritance_origin": "unknown",
  "allele_frequency": {"gnomad": "0.0001"},
  "classification": "Pathogenic",
  "acmg_evidence": ["PS3", "PM2", "PP3"],
  "clinvar_id": "12345",
  "report_in_conclusion": true,
  "phenotype_correlation": "与受检者临床表型一致"
}
```

## Return value

JSON string with structure per `report-schema.json`, plus `report_markdown` field
containing rendered report from `report-template.md`.

## Agent integration

Register in `agent/factory.py` alongside existing tools, or load skill only:

```python
create_deep_agent(
    model=get_llm(),
    tools=[..., generate_genetic_testing_report],
    skills=[str(SKILLS_DIR / "genetic-testing-report")],
    system_prompt=SYSTEM_PROMPT_GENETIC_REPORT,
)
```

Trigger phrases for skill auto-selection:
- 单基因遗传病检测报告
- T/SZGIA 4-2018
- 基因检测报告规范
- variant interpretation report
- ACMG report

## Validation

Post-generation checklist (automate in validator if needed):

1. All 13 sections present and non-empty
2. Every `report_in_conclusion=true` variant appears in `conclusion`
3. No Benign/Likely benign in `results.primary_variants`
4. `limitations` array has ≥1 item
5. HGVS fields present for all primary variants
