from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from report.models import ClinicalAdvice, GeneCard, ReportContext, SampleMeta, VariantRecord, build_genomic_context_items
from report.paths import format_report_path

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def _format_af(value: str) -> str:
    if not value or value == "-":
        return "0.0000"
    try:
        number = float(value)
        if number == 0:
            return "0.0000"
        return f"{number:.6g}"
    except ValueError:
        return value


def _format_vaf(value: str) -> str:
    if not value or value == "-":
        return "-"
    try:
        number = float(value)
        return f"{number * 100:.1f}%"
    except ValueError:
        return value


def _is_pathogenic_clinvar(clinvar: str) -> bool:
    if not clinvar or clinvar == "-":
        return False
    lowered = clinvar.lower()
    return "pathogenic" in lowered


def _parse_evidence_tree(evidence_summary: str) -> str:
    if not evidence_summary or evidence_summary == "-":
        return "暂无评分分解信息"

    parts = [part.strip() for part in evidence_summary.split(";") if part.strip()]
    total_match = re.search(r"total=([+-]?\d+)", evidence_summary)
    total = total_match.group(1) if total_match else "?"

    lines = [f"evidence_score: {total}"]
    for part in parts:
        if part.startswith("total="):
            continue
        lines.append(f"  ├── {part}")
    return "\n".join(lines)


def _tokenize_phenotype_text(text: str) -> set[str]:
    stopwords = frozenset(
        {"the", "and", "for", "with", "type", "disease", "syndrome", "disorder", "of", "in", "to", "a", "an"}
    )
    tokens = re.findall(r"[a-z0-9\u4e00-\u9fff]{3,}", (text or "").lower())
    return {token for token in tokens if token not in stopwords}


def _phenotype_overlap(left: str, right: str) -> float:
    left_tokens = _tokenize_phenotype_text(left)
    right_tokens = _tokenize_phenotype_text(right)
    if not left_tokens or not right_tokens:
        return 0.0
    shared = left_tokens & right_tokens
    if shared:
        return len(shared) / min(len(left_tokens), len(right_tokens))
    combined_left = " ".join(sorted(left_tokens))
    combined_right = " ".join(sorted(right_tokens))
    if combined_left in combined_right or combined_right in combined_left:
        return 0.6
    return 0.0


def _patient_phenotype_text(context: ReportContext) -> str:
    parts = [context.meta.clinical_info, " ".join(context.meta.hpo_terms)]
    return " ".join(part.strip() for part in parts if part and part.strip())


def _patient_phenotype_summary(context: ReportContext) -> str:
    if context.meta.clinical_info.strip():
        text = context.meta.clinical_info.strip()
        return text[:120] + "..." if len(text) > 123 else text

    labeled_hpo: list[str] = []
    for line in context.meta.hpo_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"(HP:\d+)\s+(.+)", line)
        if match:
            labeled_hpo.append(f"{match.group(1)} {match.group(2)}")
    if labeled_hpo:
        summary = "；".join(labeled_hpo[:4])
        if len(labeled_hpo) > 4:
            summary += " 等"
        return summary

    return "未提供临床表型信息"


def _gene_associated_phenotype(card: GeneCard) -> str:
    if card.narrative and card.narrative.phenotype_association.strip():
        return card.narrative.phenotype_association.strip()
    if card.main_associated_phenotype not in ("", "-"):
        return card.main_associated_phenotype.strip()
    return ""


def _best_phenotype_overlap(associated: str, patient_text: str) -> float:
    parts = [part.strip() for part in re.split(r"[;/|]", associated) if part.strip()]
    if not parts:
        return _phenotype_overlap(associated, patient_text)
    return max(_phenotype_overlap(part, patient_text) for part in parts)


def _phenotype_match_label(overlap: float) -> str:
    if overlap >= 0.35:
        return "与患者表型关联性较高"
    if overlap >= 0.15:
        return "与患者表型部分相关"
    return "与患者表型未见明确关联"


def _fallback_key_findings(context: ReportContext) -> list[str]:
    findings: list[str] = []
    patient_text = _patient_phenotype_text(context)

    for card in context.gene_cards:
        associated = _gene_associated_phenotype(card)
        if associated:
            overlap = _best_phenotype_overlap(associated, patient_text)
            match_label = _phenotype_match_label(overlap)
            findings.append(
                f"**{card.gene_symbol}**（致病性排名 #{card.best_pathogenic_rank}）："
                f"数据库关联表型为「{associated}」，{match_label}。"
            )
        else:
            findings.append(
                f"**{card.gene_symbol}**（致病性排名 #{card.best_pathogenic_rank}）："
                f"暂无明确关联表型记录，需结合临床与变异证据评估。"
            )

    if not context.gene_cards:
        findings.append(f"当前无 Top 基因；患者表型：{_patient_phenotype_summary(context)}。")

    return findings


def _clinical_advice_is_usable(advice: ClinicalAdvice | None) -> bool:
    """§7 临床建议：Agent 未运行、调用失败或 §7 相关字段均为空时使用脚本 fallback。"""
    if advice is None:
        return False
    return bool(
        advice.immediate_recommendations
        or advice.monitoring
        or advice.communication_points
    )


def _fallback_clinical_advice(context: ReportContext) -> dict:
    immediate: list[str] = []
    monitoring: list[str] = []
    communication: list[str] = []

    for card in context.gene_cards:
        clinvar = card.top_clinvar or "未提供"
        if _is_pathogenic_clinvar(card.top_clinvar):
            immediate.append(
                f"优先关注 {card.gene_symbol}（{card.variants[0].variant_label}，ClinVar={clinvar}）："
                f"建议遗传咨询并考虑 Sanger 验证。"
            )
            for drug in card.drug_recommendations[:2]:
                immediate.append(
                    f"{card.gene_symbol} 严格筛选候选用药 {drug.drug_name}（{drug.indication}，"
                    f"证据 {drug.evidence_level}）：需肿瘤/遗传专科评估后决策，不得视为处方。"
                )
        else:
            monitoring.append(
                f"{card.gene_symbol}（ClinVar={clinvar}）建议结合表型与家系信息进一步评估。"
            )

    communication.extend(
        [
            "本报告为计算注释与数据库证据的辅助解读，不构成最终临床诊断。",
            "所有候选变异建议经实验验证并由临床遗传学专家复核后用于临床决策。",
        ]
    )

    return {
        "immediate_recommendations": immediate or ["结合 Top 基因列表安排遗传咨询与验证实验。"],
        "monitoring": monitoring or ["动态随访临床表型与影像学变化。"],
        "communication_points": communication,
        "key_findings": _fallback_key_findings(context),
    }


def _gene_narrative_or_default(card: GeneCard) -> dict:
    if card.narrative:
        return card.narrative.model_dump()
    return {
        "gene_function": card.script_gene_function
        if card.script_gene_function not in ("", "-")
        else "-",
        "inheritance_mode": card.omim_inheritance_mode
        if card.omim_inheritance_mode not in ("", "-")
        else "待结合家系与变异类型进一步判断",
        "phenotype_association": card.main_associated_phenotype
        if card.main_associated_phenotype not in ("", "-")
        else "-",
        "pathway_summary": card.main_pathway
        if card.main_pathway not in ("", "-")
        else "-",
        "literature": [],
        "clinical_note": card.evidence_summary if card.evidence_summary != "-" else "",
        "therapeutic_implication": card.drug_recommendation_summary or "",
    }


def _safe_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _genomic_context_items(variant: VariantRecord, card: GeneCard, meta: SampleMeta) -> list[dict[str, str]]:
    return build_genomic_context_items(
        variant,
        gene_variant_count=len(card.variants),
        family_type=meta.family_type,
    )


def _has_genomic_context(variant: VariantRecord, card: GeneCard, meta: SampleMeta) -> bool:
    return bool(_genomic_context_items(variant, card, meta))


def _create_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["format_af"] = _format_af
    env.filters["format_vaf"] = _format_vaf
    env.filters["safe_float"] = _safe_float
    env.filters["report_path"] = format_report_path
    env.globals["genomic_context_items"] = _genomic_context_items
    env.globals["has_genomic_context"] = _has_genomic_context
    env.globals["parse_evidence_tree"] = _parse_evidence_tree
    env.globals["clinical_advice_is_usable"] = _clinical_advice_is_usable
    env.globals["fallback_clinical_advice"] = _fallback_clinical_advice
    env.globals["fallback_key_findings"] = _fallback_key_findings
    env.globals["gene_narrative_or_default"] = _gene_narrative_or_default
    env.globals["render_report_output_block"] = render_report_output_block
    return env


def render_report(context: ReportContext, output_path: str = "") -> str:
    env = _create_env()
    template = env.get_template("final_report.md.j2")
    return template.render(ctx=context, output_path=output_path)


def build_report_output_json(context: ReportContext, output_path: str) -> dict:
    display_output = format_report_path(output_path) or (Path(output_path).name if output_path else "")
    return {
        "report_version": context.report_version,
        "report_title": f"{context.meta.sample_id} 基因组变异分析报告",
        "gene_count": len(context.gene_cards),
        "variant_count": sum(card.variant_count for card in context.gene_cards),
        "top_genes": [card.gene_symbol for card in context.gene_cards],
        "output_path": display_output,
        "literature_strategy": "precomputed_plus_online_fallback",
        "disclaimer_included": True,
    }


def render_report_output_block(context: ReportContext, output_path: str) -> str:
    payload = build_report_output_json(context, output_path)
    return json.dumps(payload, ensure_ascii=False, indent=2)
