from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from report.models import GeneCard, ReportContext, VariantRecord

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


def _fallback_key_findings(context: ReportContext) -> list[str]:
    findings: list[str] = []
    for card in context.gene_cards:
        findings.append(
            f"**{card.gene_symbol}**：{card.main_consequence}，ClinVar={card.top_clinvar or '未提供'}，"
            f"致病性排名 #{card.best_pathogenic_rank}"
            f"{'；Open Targets 主要关联表型：' + card.main_associated_phenotype if card.main_associated_phenotype not in ('', '-') else ''}。"
        )
        if not card.drug_recommendations and card.drug_recommendation_summary:
            findings.append(f"**{card.gene_symbol} 用药**：{card.drug_recommendation_summary}")
    if context.meta.hpo_terms:
        findings.append(
            f"临床 HPO 表型 {', '.join(context.meta.hpo_terms)} 需在解读中与候选基因逐一比对。"
        )
    return findings


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
        "gene_function": card.omim_gene_function
        if card.omim_gene_function not in ("", "-")
        else "待 OMIM / Agent 补充",
        "inheritance_mode": card.omim_inheritance_mode
        if card.omim_inheritance_mode not in ("", "-")
        else "待结合家系与变异类型进一步判断",
        "phenotype_association": card.main_associated_phenotype
        if card.main_associated_phenotype not in ("", "-")
        else "待 Agent 结合 HPO 与疾病数据库补充",
        "pathway_summary": card.main_pathway
        if card.main_pathway not in ("", "-")
        else "待 Agent 补充",
        "literature": [],
        "clinical_note": card.evidence_summary if card.evidence_summary != "-" else "",
        "therapeutic_implication": card.drug_recommendation_summary or "",
    }


def _safe_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


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
    env.globals["parse_evidence_tree"] = _parse_evidence_tree
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
    return {
        "report_version": context.report_version,
        "report_title": f"{context.meta.sample_id} 基因组变异分析报告",
        "gene_count": len(context.gene_cards),
        "variant_count": sum(card.variant_count for card in context.gene_cards),
        "top_genes": [card.gene_symbol for card in context.gene_cards],
        "output_path": output_path,
        "literature_strategy": "precomputed_plus_online_fallback",
        "disclaimer_included": True,
    }


def render_report_output_block(context: ReportContext, output_path: str) -> str:
    payload = build_report_output_json(context, output_path)
    return json.dumps(payload, ensure_ascii=False, indent=2)
