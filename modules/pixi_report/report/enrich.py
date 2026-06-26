from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import AIMessage

from agent.factory import build_report_clinical_agent, build_report_gene_agent
from report.models import (
    ClinicalAdvice,
    GeneCard,
    GeneNarrative,
    LiteratureHit,
    ReportContext,
    ReportNarrative,
    SampleMeta,
    build_genomic_context_items,
)

_report_gene_agent = None
_report_clinical_agent = None


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        parts: list[str] = []
        for key in ("primary", "summary", "text", "description", "detail", "note"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                parts.append(item.strip())
        if parts:
            return " ".join(parts)
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "; ".join(part for part in (_coerce_text(item) for item in value) if part)
    return str(value).strip()


def _coerce_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [part for part in (_coerce_text(item) for item in value) if part]
    text = _coerce_text(value)
    return [text] if text else []


    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def _final_agent_text(result: dict) -> str:
    text = ""
    for message in result.get("messages", []):
        if isinstance(message, AIMessage) and message.content and not message.tool_calls:
            text = message.content if isinstance(message.content, str) else str(message.content)
    return text


async def _get_report_gene_agent():
    global _report_gene_agent
    if _report_gene_agent is None:
        _report_gene_agent = await build_report_gene_agent()
    return _report_gene_agent


async def _get_report_clinical_agent():
    global _report_clinical_agent
    if _report_clinical_agent is None:
        _report_clinical_agent = await build_report_clinical_agent()
    return _report_clinical_agent


async def _run_agent_json(agent, user_message: str) -> dict[str, Any]:
    result = await agent.ainvoke({"messages": [{"role": "user", "content": user_message}]})
    return _extract_json(_final_agent_text(result))


def _variant_payload(meta: SampleMeta, card: GeneCard) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for variant in card.variants:
        payloads.append(
            {
                "coordinate": variant.coordinate,
                "hgvsc": variant.hgvsc,
                "hgvsp": variant.hgvsp,
                "consequence": variant.consequence,
                "clinvar": variant.clinvar_significance,
                "cadd": variant.cadd_phred,
                "vaf": variant.primary_vaf,
                "gatk_af": variant.vcf_info_af,
                "read_vaf": variant.vcf_info_vaf,
                "read_support": variant.read_support_summary,
                "sequencing_quality_note": variant.sequencing_quality_note,
                "genomic_context": build_genomic_context_items(
                    variant,
                    gene_variant_count=len(card.variants),
                    family_type=meta.family_type,
                ),
                "evidence_summary": variant.evidence_summary,
            }
        )
    return payloads


def _drug_payload(card: GeneCard) -> dict[str, Any]:
    return {
        "summary": card.drug_recommendation_summary,
        "candidates": [
            rec.model_dump()
            for rec in card.drug_recommendations
        ],
        "trial_teams": [team.model_dump() for team in card.trial_teams],
    }


def _gene_card_payload(meta: SampleMeta, card: GeneCard) -> dict[str, Any]:
    return {
        "sample_id": meta.sample_id,
        "clinical_info": meta.clinical_info,
        "hpo_terms": meta.hpo_terms,
        "gene_symbol": card.gene_symbol,
        "pathogenic_rank": card.best_pathogenic_rank,
        "reactome_main_pathway": card.main_pathway,
        "open_targets_main_phenotype": card.main_associated_phenotype,
        "script_gene_function": card.script_gene_function,
        "script_gene_function_source": card.script_gene_function_source,
        "ncbi_gene_id": card.ncbi_gene_id,
        "ncbi_gene_url": card.ncbi_gene_url,
        "omim_inheritance_mode": card.omim_inheritance_mode,
        "clinvar": card.top_clinvar,
        "main_consequence": card.main_consequence,
        "variants": _variant_payload(meta, card),
        "strict_drug_candidates": _drug_payload(card),
    }


async def enrich_gene_narrative(meta: SampleMeta, card: GeneCard) -> GeneNarrative:
    agent = await _get_report_gene_agent()
    payload = _gene_card_payload(meta, card)

    user_message = (
        "请为以下基因生成报告叙事 JSON。"
        "用户消息中已包含脚本预取的 script_gene_function（来源见 script_gene_function_source，"
        "通常为 NCBI Gene / Entrez）与 omim_inheritance_mode，"
        "请原样写入 gene_function / inheritance_mode，不要改写或编造。"
        "用户消息中的 strict_drug_candidates 为脚本严格筛选后的用药候选；"
        "**不得新增或替换候选药物**，therapeutic_implication 只能基于候选列表解释机制/治疗意义；"
        "若无候选则明确写暂无严格匹配用药。"
        "请再调用 get_gene_disease_associations 补充表型关联，"
        "调用 paper_search_search_pubmed 检索基因+疾病+用药相关文献（max_results=3），再输出 JSON。\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )

    try:
        data = await _run_agent_json(agent, user_message)
    except Exception:
        return GeneNarrative(
            gene_function=card.script_gene_function
            if card.script_gene_function not in ("", "-")
            else "Agent 生成失败",
            inheritance_mode=card.omim_inheritance_mode
            if card.omim_inheritance_mode not in ("", "-")
            else "",
            pathway_summary=card.main_pathway if card.main_pathway != "-" else "",
        )

    literature = [
        LiteratureHit(**item) if isinstance(item, dict) else LiteratureHit()
        for item in data.get("literature", [])
    ]

    pathway_summary = _coerce_text(data.get("pathway_summary"))
    if not pathway_summary and card.main_pathway not in ("", "-"):
        pathway_summary = card.main_pathway

    try:
        return GeneNarrative(
            gene_function=card.script_gene_function
            if card.script_gene_function not in ("", "-")
            else _coerce_text(data.get("gene_function")),
            inheritance_mode=card.omim_inheritance_mode
            if card.omim_inheritance_mode not in ("", "-")
            else _coerce_text(data.get("inheritance_mode")),
            phenotype_association=_coerce_text(data.get("phenotype_association")),
            pathway_summary=pathway_summary,
            literature=literature,
            clinical_note=_coerce_text(data.get("clinical_note")),
            therapeutic_implication=_coerce_text(data.get("therapeutic_implication")),
        )
    except Exception:
        return GeneNarrative(
            gene_function=card.script_gene_function
            if card.script_gene_function not in ("", "-")
            else "Agent 生成失败",
            inheritance_mode=card.omim_inheritance_mode
            if card.omim_inheritance_mode not in ("", "-")
            else "",
            pathway_summary=card.main_pathway if card.main_pathway != "-" else "",
        )


async def enrich_clinical_advice(context: ReportContext) -> ClinicalAdvice | None:
    agent = await _get_report_clinical_agent()
    payload = {
        "sample_id": context.meta.sample_id,
        "clinical_info": context.meta.clinical_info,
        "hpo_terms": context.meta.hpo_terms,
        "top_genes": [
            {
                "gene": card.gene_symbol,
                "rank": card.rank,
                "clinvar": card.top_clinvar,
                "consequence": card.main_consequence,
                "reactome_main_pathway": card.main_pathway,
                "open_targets_main_phenotype": card.main_associated_phenotype,
                "variants": _variant_payload(context.meta, card),
                "strict_drug_candidates": _drug_payload(card),
            }
            for card in context.gene_cards
        ],
    }

    user_message = (
        "请生成本样本的临床建议 JSON。"
        "请先对关键基因调用 lookup_gene 和 get_gene_disease_associations 了解疾病背景，"
        "再结合临床信息、HPO 与 strict_drug_candidates 输出 JSON。"
        "**immediate_recommendations 中的用药建议只能引用 strict_drug_candidates.candidates 中已列出的药物**，"
        "并说明需专家复核；无候选时不得编造具体药名。"
        "**key_findings 须逐基因写表型匹配**：对照 open_targets_main_phenotype 与 clinical_info/hpo_terms，"
        "说明疾病关键表型是否与患者一致，避免只列变异注释。\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )

    try:
        data = await _run_agent_json(agent, user_message)
    except Exception:
        return None

    advice = ClinicalAdvice(
        immediate_recommendations=_coerce_text_list(data.get("immediate_recommendations")),
        monitoring=_coerce_text_list(data.get("monitoring")),
        communication_points=_coerce_text_list(data.get("communication_points")),
        key_findings=_coerce_text_list(data.get("key_findings")),
    )
    if not (
        advice.immediate_recommendations
        or advice.monitoring
        or advice.communication_points
        or advice.key_findings
    ):
        return None
    return advice


async def enrich_report_context(context: ReportContext) -> ReportContext:
    narrative = ReportNarrative()

    for card in context.gene_cards:
        gene_narrative = await enrich_gene_narrative(context.meta, card)
        narrative.gene_narratives[card.gene_symbol] = gene_narrative
        card.narrative = gene_narrative

    narrative.clinical_advice = await enrich_clinical_advice(context)
    context.narrative = narrative
    return context
