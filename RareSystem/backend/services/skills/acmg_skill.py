from typing import List, Dict, Any
from services.skill_base import Skill, SkillContext, SkillResult
from services.rag_service import ChatReference


class ACMGClassificationSkill(Skill):
    name = "acmg_classification"
    description = "ACMG/AMP变异分类解读 - 应用PVS1-PS4, PM1-PM6, PP1-PP5, BP1-BP7标准进行系统化变异分类"
    skill_type = "prompt_injection"
    icon = "experiment"
    input_schema = {
        "variant_description": "str - 变异描述 (e.g. chr1:12345 A>G)",
        "focus_criteria": "list - 重点关注的标准 (e.g. ['PVS1', 'PS1'])"
    }

    def execute(self, context: SkillContext) -> SkillResult:
        acmg_prompt = self._build_acmg_prompt(context)
        if context.llm_client:
            try:
                response = context.llm_client.chat(
                    messages=[{"role": "user", "content": acmg_prompt}],
                    temperature=0.3,
                    max_tokens=2048
                )
                return SkillResult(
                    content=response.content,
                    references=self._build_references(context),
                    confidence=0.85,
                    metadata={"model": response.model, "skill": self.name}
                )
            except Exception as e:
                return SkillResult(
                    content=f"ACMG分类分析失败: {str(e)}。请检查LLM配置。",
                    references=[],
                    confidence=0.1,
                    metadata={"error": str(e)}
                )
        return SkillResult(
            content=self._mock_acmg_response(context.query),
            references=[],
            confidence=0.3,
            metadata={"mock": True}
        )

    def _build_acmg_prompt(self, context: SkillContext) -> str:
        parts = [
            "You are a clinical genetics expert performing ACMG/AMP variant classification.",
            "",
            "Apply the following criteria systematically:",
            "",
            "PATHOGENIC criteria:",
            "- PVS1: Null variant (nonsense, frameshift, canonical ±1/2 splice sites, initiation codon, single/multiexon deletion) in a gene where LOF is a known mechanism of disease",
            "- PS1: Same amino acid change as a previously established pathogenic variant regardless of nucleotide change",
            "- PS2: De novo (both maternity and paternity confirmed) in a patient with the disease and no family history",
            "- PS3: Well-established in vitro or in vivo functional studies supportive of a damaging effect",
            "- PS4: The prevalence of the variant in affected individuals is significantly increased compared with controls",
            "- PM1: Located in a mutational hot spot and/or critical and well-established functional domain without benign variation",
            "- PM2: Absent from controls in gnomAD population databases",
            "- PM3: For recessive disorders, detected in trans with a pathogenic variant",
            "- PM4: Protein length changes as a result of in-frame deletions/insertions in a non-repeat region or stop-loss",
            "- PM5: Novel missense change at an amino acid residue where a different pathogenic missense change has been seen before",
            "- PM6: Assumed de novo, but without confirmation of paternity and maternity",
            "- PP1: Co-segregation with disease in multiple affected family members",
            "- PP2: Missense variant in a gene with low rate of benign missense variation",
            "- PP3: Multiple lines of computational evidence support a deleterious effect",
            "- PP4: Patient's phenotype or family history is highly specific for a disease with a single genetic etiology",
            "",
            "BENIGN criteria:",
            "- BA1: Allele frequency >5% in gnomAD/ExAC",
            "- BS1: Allele frequency greater than expected for disorder",
            "- BS2: Observed in a healthy adult individual for a recessive disorder",
            "- BS3: Well-established in vitro or in vivo functional studies show no damaging effect",
            "- BS4: Lack of segregation in affected family members",
            "- BP1: Missense variant in a gene for which primarily truncating variants are known to cause disease",
            "- BP2: Observed in trans with a pathogenic variant for a fully penetrant dominant disorder",
            "- BP3: In-frame deletions/insertions in a repetitive region without a known function",
            "- BP4: Multiple lines of computational evidence suggest no impact",
            "- BP5: Variant found in a case with an alternate molecular basis for disease",
            "- BP6: Reputable source recently reports variant as benign",
            "- BP7: A synonymous variant for which splicing prediction algorithms predict no impact",
            "",
            "CLASSIFICATION RULES:",
            "- Pathogenic: 1 Very Strong (PVS1) AND ≥1 Strong (PS) OR ≥2 Moderate (PM) OR 1 Moderate + 1 Supporting (PP); OR ≥2 Strong (PS); OR 1 Strong + ≥3 Moderate; OR 1 Strong + 2 Moderate + ≥2 Supporting; OR 1 Strong + 1 Moderate + ≥4 Supporting",
            "- Likely Pathogenic: 1 Very Strong + 1 Moderate; OR 1 Strong + 1-2 Moderate; OR 1 Strong + ≥2 Supporting; OR ≥3 Moderate; OR 2 Moderate + ≥2 Supporting; OR 1 Moderate + ≥4 Supporting",
            "- VUS (Uncertain Significance): Does not meet criteria for other classifications",
            "- Likely Benign: 1 Strong (BS) + 1 Supporting (BP); OR ≥2 Supporting (BP)",
            "- Benign: 1 Stand-alone (BA1); OR ≥2 Strong (BS)",
            "",
        ]

        if context.case_context:
            parts.append(f"Patient/Case Context: {context.case_context}")
            parts.append("")

        parts.append(f"Question: {context.query}")
        parts.append("")
        parts.append("Provide a systematic ACMG classification with:")
        parts.append("1. Each applicable criterion with evidence (met/not met)")
        parts.append("2. Point tally for pathogenic and benign criteria")
        parts.append("3. Final classification (Pathogenic/Likely Pathogenic/VUS/Likely Benign/Benign)")
        parts.append("4. Confidence level and any caveats")

        return "\n".join(parts)

    def _build_references(self, context: SkillContext) -> List[ChatReference]:
        refs = [ChatReference(
            reference_id="acmg-amp-2015",
            reference_type="evidence",
            label="ACMG/AMP Guidelines 2015",
            url="https://www.acmg.net/docs/Standards_Guidelines_for_the_Interpretation_of_Sequence_Variants.pdf"
        )]
        if context.patient_id:
            refs.append(ChatReference(
                reference_id=f"patient-{context.patient_id}",
                reference_type="patient_summary",
                label=f"Patient {context.patient_id} Data"
            ))
        return refs

    def _mock_acmg_response(self, query: str) -> str:
        return (
            "ACMG/AMP Classification Analysis (Mock Response)\n\n"
            "Based on the variant description provided, here is a preliminary assessment:\n\n"
            "**Criteria Evaluated:**\n"
            "- PM2: Variant absent from population databases ✓\n"
            "- PP3: Computational evidence supports deleterious effect ✓\n"
            "- BP4: Some computational tools suggest neutral effect ✗\n\n"
            "**Classification: VUS (Variant of Uncertain Significance)**\n"
            "**Confidence: Low** - Additional functional studies and segregation data needed.\n\n"
            "Note: This is a mock response. Configure an LLM provider in Settings for AI-powered classification."
        )
