from services.skill_base import Skill, SkillContext, SkillResult
from services.rag_service import ChatReference


class PhenotypeMatchingSkill(Skill):
    name = "phenotype_matching"
    description = "临床表型与基因关联匹配 - 分析患者表型特征与已知致病基因的关联性"
    skill_type = "prompt_injection"
    icon = "medicine-box"
    input_schema = {
        "phenotype_terms": "list - HPO术语或临床表型描述",
        "inheritance_mode": "str - 推断的遗传模式 (AD/AR/XL/mitochondrial)"
    }

    def execute(self, context: SkillContext) -> SkillResult:
        prompt = self._build_phenotype_prompt(context)
        if context.llm_client:
            try:
                response = context.llm_client.chat(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=2048
                )
                return SkillResult(
                    content=response.content,
                    references=self._build_references(),
                    confidence=0.8,
                    metadata={"model": response.model, "skill": self.name}
                )
            except Exception as e:
                return SkillResult(
                    content=f"表型匹配分析失败: {str(e)}",
                    references=[],
                    confidence=0.1,
                    metadata={"error": str(e)}
                )
        return SkillResult(
            content=self._mock_phenotype_response(context.query),
            references=[],
            confidence=0.3,
            metadata={"mock": True}
        )

    def _build_phenotype_prompt(self, context: SkillContext) -> str:
        parts = [
            "You are a clinical genetics expert specializing in phenotype-genotype correlations for rare diseases.",
            "",
            "Analyze the patient's clinical phenotype and identify potential gene-disease associations.",
            "",
            "For each candidate gene, provide:",
            "1. Gene symbol and full name",
            "2. Associated disease(s) (OMIM references if possible)",
            "3. Inheritance pattern (AD/AR/XL/mitochondrial)",
            "4. How well the patient's phenotype matches the gene's known clinical spectrum",
            "5. Key diagnostic criteria that are met/unmet",
            "6. Recommended next steps (e.g., specific genetic testing, functional studies)",
            "",
            "Consider the following inheritance patterns:",
            "- Autosomal Dominant (AD): One copy of the altered gene is sufficient",
            "- Autosomal Recessive (AR): Both copies must be altered",
            "- X-linked (XL): Gene is on the X chromosome",
            "- Mitochondrial: Maternal inheritance from mitochondrial DNA",
            "",
        ]

        if context.case_context:
            parts.append(f"Patient Clinical Context: {context.case_context}")
            parts.append("")

        parts.append(f"Question: {context.query}")
        parts.append("")
        parts.append("Provide a ranked list of candidate genes with evidence strength and clinical reasoning.")

        return "\n".join(parts)

    def _build_references(self):
        return [
            ChatReference(reference_id="omim", reference_type="evidence", label="OMIM Database", url="https://omim.org/"),
            ChatReference(reference_id="hpo", reference_type="evidence", label="HPO Ontology", url="https://hpo.jax.org/"),
        ]

    def _mock_phenotype_response(self, query: str) -> str:
        return (
            "**Phenotype-Gene Association Analysis (Mock Response)**\n\n"
            "Based on the clinical features described, here are potential gene associations:\n\n"
            "1. **Gene A** - Associated with [Disease X] (OMIM: XXXXXX)\n"
            "   - Inheritance: Autosomal Recessive\n"
            "   - Phenotype match: Moderate\n"
            "   - Key features: [feature list]\n\n"
            "2. **Gene B** - Associated with [Disease Y] (OMIM: XXXXXX)\n"
            "   - Inheritance: Autosomal Dominant\n"
            "   - Phenotype match: Low\n"
            "   - Key features: [feature list]\n\n"
            "Note: This is a mock response. Configure an LLM provider for AI-powered analysis."
        )
