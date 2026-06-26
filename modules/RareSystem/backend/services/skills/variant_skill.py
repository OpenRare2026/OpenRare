from typing import List, Optional
from services.skill_base import Skill, SkillContext, SkillResult
from services.rag_service import ChatReference


class VariantAnnotationSkill(Skill):
    name = "variant_annotation"
    description = "变异注释检索 - 查询本地数据库获取变异的注释信息、ACMG分类和群体频率"
    skill_type = "tool_call"
    icon = "search"
    input_schema = {
        "variant_description": "str - 变异描述 (e.g. chr1:12345 A>G)",
        "databases": "list - 要查询的数据库 (gnomad, clinvar, dbsnp)"
    }

    def execute(self, context: SkillContext) -> SkillResult:
        if not context.db_session:
            return SkillResult(
                content="Variant annotation requires database access. No database session available.",
                references=[],
                confidence=0.0,
                metadata={"error": "no_db_session"}
            )

        annotations = self._query_variant_annotations(context)
        return SkillResult(
            content=self._format_annotations(annotations, context.query),
            references=annotations.get("references", []),
            confidence=annotations.get("confidence", 0.5),
            metadata={"skill": self.name, "variant_found": annotations.get("found", False)}
        )

    def _query_variant_annotations(self, context: SkillContext) -> dict:
        from database.models import Variant, VCFFile, ACMGClassification, ACMGEvidence

        result = {"found": False, "variant_data": None, "classification": None, "evidence": [], "references": []}
        db = context.db_session

        try:
            vcf_files = db.query(VCFFile.id).filter(
                VCFFile.patient_id == context.patient_id
            ).all()

            if not vcf_files:
                return result

            vcf_ids = [v.id for v in vcf_files]
            variant = db.query(Variant).filter(
                Variant.vcf_file_id.in_(vcf_ids)
            ).first()

            if not variant:
                return result

            result["found"] = True
            result["variant_data"] = {
                "chromosome": variant.chromosome,
                "position": variant.position,
                "ref": variant.ref,
                "alt": variant.alt,
                "variant_type": variant.variant_type,
                "quality": variant.quality,
                "gene": variant.gene,
                "hgvs_p": variant.hgvs_p,
                "consequence": variant.consequence,
                "gnomad_af": variant.gnomad_af,
            }

            classification = db.query(ACMGClassification).filter(
                ACMGClassification.variant_id == variant.id
            ).first()

            if classification:
                result["classification"] = {
                    "classification": classification.classification,
                    "confidence_score": classification.confidence_score,
                }
                result["references"].append(ChatReference(
                    reference_id=f"acmg-{variant.id}",
                    reference_type="evidence",
                    label=f"ACMG: {classification.classification}"
                ))

            evidence_list = db.query(ACMGEvidence).filter(
                ACMGEvidence.variant_id == variant.id
            ).limit(5).all()

            result["evidence"] = [
                {"criterion": e.criterion, "description": e.description, "is_applied": e.is_applied}
                for e in evidence_list
            ]

            result["confidence"] = 0.9 if result["classification"] else 0.6

        except Exception:
            pass

        return result

    def _format_annotations(self, annotations: dict, query: str) -> str:
        if not annotations.get("found"):
            return f"No variant annotations found for query: '{query}'. The variant may not exist in the local database for this patient."

        parts = ["**Variant Annotation Report**\n"]

        vd = annotations.get("variant_data", {})
        if vd:
            parts.append(f"**Variant:** {vd.get('chromosome')}:{vd.get('position')} {vd.get('ref')}>{vd.get('alt')}")
            parts.append(f"**Type:** {vd.get('variant_type')}")
            parts.append(f"**Gene:** {vd.get('gene', 'N/A')}")
            parts.append(f"**HGVS.p:** {vd.get('hgvs_p', 'N/A')}")
            parts.append(f"**Consequence:** {vd.get('consequence', 'N/A')}")
            parts.append(f"**Quality:** {vd.get('quality', 'N/A')}")
            if vd.get('gnomad_af') is not None:
                parts.append(f"**gnomAD AF:** {vd.get('gnomad_af'):.6f}")

        cls = annotations.get("classification")
        if cls:
            parts.append(f"\n**ACMG Classification:** {cls.get('classification')}")
            if cls.get('confidence_score'):
                parts.append(f"**Confidence:** {cls.get('confidence_score'):.2f}")

        evidence = annotations.get("evidence", [])
        if evidence:
            parts.append("\n**Applied Evidence:**")
            for e in evidence:
                status = "✓" if e.get("is_applied") else "✗"
                parts.append(f"  {status} {e.get('criterion')}: {e.get('description')}")

        return "\n".join(parts)
