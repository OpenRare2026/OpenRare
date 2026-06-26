from services.skill_base import Skill, SkillContext, SkillResult
from services.rag_service import ChatReference


class PedigreeAnalysisSkill(Skill):
    name = "pedigree_analysis"
    description = "家系分析与遗传模式推断 - 分析家族遗传史推断遗传模式和再发风险"
    skill_type = "prompt_injection"
    icon = "apartment"
    input_schema = {
        "family_history": "str - 家族遗传史描述",
        "affected_members": "list - 受累家庭成员列表"
    }

    def execute(self, context: SkillContext) -> SkillResult:
        prompt = self._build_pedigree_prompt(context)
        if context.llm_client:
            try:
                response = context.llm_client.chat(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
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
                    content=f"家系分析失败: {str(e)}",
                    references=[],
                    confidence=0.1,
                    metadata={"error": str(e)}
                )
        return SkillResult(
            content=self._mock_pedigree_response(context.query),
            references=[],
            confidence=0.3,
            metadata={"mock": True}
        )

    def _build_pedigree_prompt(self, context: SkillContext) -> str:
        parts = [
            "You are a clinical genetics expert specializing in pedigree analysis and inheritance pattern determination.",
            "",
            "Analyze the family history and determine the most likely inheritance pattern.",
            "",
            "For each inheritance pattern, evaluate:",
            "",
            "**Autosomal Dominant (AD):**",
            "- Vertical transmission (affected individuals in multiple generations)",
            "- Both sexes equally affected",
            "- Affected individuals typically have one affected parent (except de novo)",
            "- 50% risk to offspring of affected individual",
            "",
            "**Autosomal Recessive (AR):**",
            "- Horizontal pattern (multiple affected siblings, parents unaffected)",
            "- Both sexes equally affected",
            "- Consanguinity increases risk",
            "- 25% risk to siblings of affected individual",
            "",
            "**X-linked Recessive:**",
            "- Mainly males affected",
            "- Carrier females usually unaffected",
            "- No male-to-male transmission",
            "",
            "**X-linked Dominant:**",
            "- Both sexes affected, but females more commonly and often less severely",
            "- No male-to-male transmission",
            "",
            "**Mitochondrial:**",
            "- Maternal inheritance only",
            "- Both sexes affected, but only females transmit",
            "- Variable expressivity",
            "",
            "Provide:",
            "1. Most likely inheritance pattern with reasoning",
            "2. Alternative patterns considered and why they are less likely",
            "3. Recurrence risk estimates",
            "4. Recommended genetic counseling points",
            "5. Suggested genetic tests based on the inheritance pattern",
            "",
        ]

        if context.case_context:
            parts.append(f"Patient/Family Context: {context.case_context}")
            parts.append("")

        parts.append(f"Question: {context.query}")

        return "\n".join(parts)

    def _build_references(self):
        return [
            ChatReference(reference_id="omim-inheritance", reference_type="evidence", label="OMIM Inheritance Patterns"),
            ChatReference(reference_id="genereviews", reference_type="evidence", label="GeneReviews", url="https://www.ncbi.nlm.nih.gov/books/NBK1116/"),
        ]

    def _mock_pedigree_response(self, query: str) -> str:
        return (
            "**Pedigree Analysis Report (Mock Response)**\n\n"
            "Based on the family history provided:\n\n"
            "**Most Likely Inheritance Pattern: Autosomal Recessive (AR)**\n"
            "- Reasoning: Multiple affected siblings with unaffected parents suggests AR inheritance\n"
            "- Consanguinity: Not reported\n\n"
            "**Recurrence Risk:**\n"
            "- Siblings of affected individual: 25%\n"
            "- Offspring of affected individual: Low (<1% unless partner is a carrier)\n\n"
            "**Genetic Counseling Recommendations:**\n"
            "- Offer carrier testing to parents and at-risk relatives\n"
            "- Discuss options for prenatal diagnosis in future pregnancies\n"
            "- Consider testing for known pathogenic variants in the family\n\n"
            "Note: This is a mock response. Configure an LLM provider for AI-powered analysis."
        )
