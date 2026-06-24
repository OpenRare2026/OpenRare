from __future__ import annotations

import json
import re
from typing import Any

from agent.open_targets_tools import (
    get_gene_disease_associations,
    get_gene_drug_details,
    lookup_gene,
)
from agent.report import china_trial_hits_from_payload, drugs_from_gene_drug_details
from report.models import (
    GeneCard,
    ReportContext,
    StrictDrugRecommendation,
    TrialTeamRow,
)
from report.open_targets_lookup import open_targets_enabled
from tools.china_trials import search_chictr_trials, search_chinadrug_trials

_STAGE_RANK = {
    "APPROVAL": 0,
    "PHASE_4": 1,
    "PHASE_3": 2,
    "PHASE_2_3": 3,
    "PHASE_2": 4,
    "PHASE_1_2": 5,
    "PHASE_1": 6,
}

_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "type",
        "disease",
        "syndrome",
        "disorder",
        "autosomal",
        "dominant",
        "recessive",
        "of",
        "in",
        "to",
        "a",
        "an",
    }
)

_HIGH_IMPACT_CONSEQUENCES = frozenset(
    {
        "frameshift_variant",
        "stop_gained",
        "stop_lost",
        "start_lost",
        "splice_acceptor_variant",
        "splice_donor_variant",
        "transcript_ablation",
    }
)


def _parse_tool_json(raw: str | object) -> Any:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9\u4e00-\u9fff]{3,}", (text or "").lower())
    return {token for token in tokens if token not in _STOPWORDS}


def _overlap_ratio(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
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


def _is_credible_variant(card: GeneCard) -> bool:
    clinvar = (card.top_clinvar or "").lower()
    if "pathogenic" in clinvar and "conflict" not in clinvar:
        return True
    if "likely pathogenic" in clinvar.replace("_", " "):
        return True
    return card.main_consequence in _HIGH_IMPACT_CONSEQUENCES


def _collect_patient_terms(context: ReportContext, card: GeneCard) -> set[str]:
    parts = [
        context.meta.clinical_info,
        " ".join(context.meta.hpo_terms),
        card.main_associated_phenotype,
        card.main_phenotype_hint,
    ]
    tokens: set[str] = set()
    for part in parts:
        tokens.update(_tokenize(part))
    return tokens


def _stage_rank(stage: str | None) -> int:
    return _STAGE_RANK.get(stage or "", 99)


def _targets_gene(mechanisms: list[dict[str, Any]], gene_symbol: str) -> bool:
    gene = gene_symbol.strip().upper()
    for mechanism in mechanisms:
        target_genes = mechanism.get("target_genes") or []
        if any(item.upper() == gene for item in target_genes if item):
            return True
    return False


def _best_indication_match(
    indication_name: str,
    gene_diseases: list[dict[str, Any]],
    patient_terms: set[str],
) -> tuple[float, float, str | None]:
    best_gene_score = 0.0
    best_gene_name = None
    for disease in gene_diseases:
        name = disease.get("name") or ""
        score = float(disease.get("score") or 0.0)
        overlap = _overlap_ratio(indication_name, name)
        weighted = overlap * (0.5 + min(score, 1.0))
        if weighted > best_gene_score:
            best_gene_score = weighted
            best_gene_name = name

    phenotype_score = 0.0
    if patient_terms:
        indication_tokens = _tokenize(indication_name)
        if indication_tokens & patient_terms:
            phenotype_score = len(indication_tokens & patient_terms) / len(indication_tokens)
        else:
            for term in patient_terms:
                phenotype_score = max(phenotype_score, _overlap_ratio(indication_name, term))

    return best_gene_score, phenotype_score, best_gene_name


def _evaluate_drug(
    drug: dict[str, Any],
    *,
    gene_symbol: str,
    gene_diseases: list[dict[str, Any]],
    patient_terms: set[str],
    credible_variant: bool,
) -> StrictDrugRecommendation | None:
    if not credible_variant:
        return None

    mechanisms = drug.get("mechanisms") or []
    gene_targeted = _targets_gene(mechanisms, gene_symbol)
    best: StrictDrugRecommendation | None = None
    best_rank = 99

    for indication in drug.get("indications") or []:
        indication_name = indication.get("disease_name") or ""
        if not indication_name:
            continue

        gene_score, phenotype_score, matched_gene_disease = _best_indication_match(
            indication_name,
            gene_diseases,
            patient_terms,
        )
        stage = indication.get("max_clinical_stage") or drug.get("maximum_clinical_stage") or ""
        stage_value = _stage_rank(stage)

        gene_match = gene_score >= 0.25
        phenotype_match = phenotype_score >= 0.2
        if not gene_match:
            continue
        top_gene_score = float(gene_diseases[0].get("score") or 0.0) if gene_diseases else 0.0
        if not phenotype_match and top_gene_score < 0.35:
            continue
        if stage_value > _STAGE_RANK["PHASE_2"]:
            continue
        if stage_value >= _STAGE_RANK["PHASE_2"] and not (phenotype_match and gene_match):
            continue
        if not gene_targeted and gene_score < 0.4:
            continue

        if stage in {"APPROVAL", "PHASE_4"} and phenotype_match:
            evidence_level = "strong"
        elif stage in {"APPROVAL", "PHASE_4", "PHASE_3", "PHASE_2_3"} and gene_match:
            evidence_level = "moderate"
        else:
            evidence_level = "exploratory"

        match_bits = [f"适应症与 {matched_gene_disease or indication_name} 关联"]
        if phenotype_match:
            match_bits.append("与样本临床/HPO 表型部分匹配")
        if gene_targeted:
            match_bits.append(f"作用机制涉及 {gene_symbol}")
        caution = (
            "仅基于 Open Targets 数据库关联，需结合 ClinVar/家系/临床表型与伦理规范确认；"
            "不得视为超适应症用药依据。"
        )
        if not phenotype_match:
            caution += " 当前样本表型与适应症匹配较弱，不建议直接用于本例治疗决策。"

        candidate = StrictDrugRecommendation(
            drug_name=drug.get("name") or "",
            chembl_id=drug.get("chembl_id") or "",
            indication=indication_name,
            clinical_stage=stage or drug.get("maximum_clinical_stage") or "-",
            evidence_level=evidence_level,
            match_basis="；".join(match_bits),
            caution=caution,
        )
        if stage_value < best_rank or (
            stage_value == best_rank
            and evidence_level == "strong"
            and (best is None or best.evidence_level != "strong")
        ):
            best = candidate
            best_rank = stage_value

    return best


def _strict_filter_drugs(
    drugs: list[dict[str, Any]],
    *,
    gene_symbol: str,
    gene_diseases: list[dict[str, Any]],
    patient_terms: set[str],
    credible_variant: bool,
    limit: int = 3,
) -> list[StrictDrugRecommendation]:
    recommendations: list[StrictDrugRecommendation] = []
    seen_names: set[str] = set()

    ranked_drugs = sorted(
        drugs,
        key=lambda item: _stage_rank(item.get("maximum_clinical_stage")),
    )

    for drug in ranked_drugs:
        rec = _evaluate_drug(
            drug,
            gene_symbol=gene_symbol,
            gene_diseases=gene_diseases,
            patient_terms=patient_terms,
            credible_variant=credible_variant,
        )
        if rec is None:
            continue
        name_key = rec.drug_name.strip().upper()
        if not name_key or name_key in seen_names:
            continue
        seen_names.add(name_key)
        recommendations.append(rec)

    order = {"strong": 0, "moderate": 1, "exploratory": 2}
    recommendations.sort(
        key=lambda item: (order.get(item.evidence_level, 9), _stage_rank(item.clinical_stage))
    )
    return recommendations[:limit]


def _team_rows_from_payload(payload: dict[str, Any], drug_name: str) -> list[TrialTeamRow]:
    rows: list[TrialTeamRow] = []
    for hit in china_trial_hits_from_payload(payload):
        team = hit.team or {}
        rows.append(
            TrialTeamRow(
                drug_name=drug_name,
                source=hit.source,
                registration_number=hit.registration_number,
                title=hit.title or "",
                sponsor=str(team.get("applicant") or team.get("company") or team.get("sponsor") or ""),
                principal_investigator=str(
                    team.get("main_leader") or team.get("principal_investigator") or ""
                ),
                institution=str(team.get("company") or team.get("institution") or ""),
            )
        )
    return rows


async def _fetch_gene_diseases(gene_symbol: str) -> list[dict[str, Any]]:
    lookup_raw = await lookup_gene.ainvoke({"gene_symbol": gene_symbol})
    lookup_payload = _parse_tool_json(lookup_raw)
    if not isinstance(lookup_payload, dict):
        return []

    ensembl_id = lookup_payload.get("ensembl_id") or ""
    if not ensembl_id:
        return []

    assoc_raw = await get_gene_disease_associations.ainvoke(
        {"ensembl_id": ensembl_id, "limit": 8}
    )
    assoc_payload = _parse_tool_json(assoc_raw)
    if not isinstance(assoc_payload, dict):
        return []

    rows = (assoc_payload.get("associatedDiseases") or {}).get("rows") or []
    diseases: list[dict[str, Any]] = []
    for row in rows:
        disease = row.get("disease") or {}
        name = disease.get("name") or ""
        if not name:
            continue
        diseases.append(
            {
                "id": disease.get("id") or "",
                "name": name,
                "score": float(row.get("score") or 0.0),
            }
        )
    return diseases


async def _fetch_gene_drugs(gene_symbol: str) -> list[dict[str, Any]]:
    raw = await get_gene_drug_details.ainvoke({"gene_symbol": gene_symbol, "limit": 8})
    payload = _parse_tool_json(raw)
    if payload is None:
        return []
    return [item.model_dump() for item in drugs_from_gene_drug_details(payload)]


async def _fetch_trial_teams(
    gene_symbol: str,
    recommendations: list[StrictDrugRecommendation],
) -> list[TrialTeamRow]:
    teams: list[TrialTeamRow] = []
    for rec in recommendations:
        if rec.evidence_level == "exploratory":
            continue
        drug_names = rec.drug_name
        chinadrug_raw = await search_chinadrug_trials.ainvoke(
            {"drug_names": drug_names, "gene_symbol": gene_symbol, "limit": 5}
        )
        chictr_raw = await search_chictr_trials.ainvoke(
            {"drug_names": drug_names, "gene_symbol": gene_symbol, "limit": 5}
        )
        chinadrug_payload = _parse_tool_json(chinadrug_raw)
        chictr_payload = _parse_tool_json(chictr_raw)
        if isinstance(chinadrug_payload, dict):
            teams.extend(_team_rows_from_payload(chinadrug_payload, rec.drug_name))
        if isinstance(chictr_payload, dict):
            teams.extend(_team_rows_from_payload(chictr_payload, rec.drug_name))
    return teams[:10]


def _summary_for_gene(
    recommendations: list[StrictDrugRecommendation],
    *,
    credible_variant: bool,
) -> str:
    if not credible_variant:
        return (
            "当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，"
            "本报告不提供用药建议。"
        )
    if not recommendations:
        return (
            "经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），"
            "暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。"
        )
    names = "、".join(rec.drug_name for rec in recommendations[:3])
    return f"严格匹配后保留 {len(recommendations)} 项候选：{names}（详见下表，需临床专家复核）。"


async def attach_drug_recommendations(context: ReportContext) -> ReportContext:
    if not open_targets_enabled():
        for card in context.gene_cards:
            card.drug_recommendation_summary = "Open Targets 查询已关闭，未生成用药建议。"
        return context

    for card in context.gene_cards:
        patient_terms = _collect_patient_terms(context, card)
        credible_variant = _is_credible_variant(card)

        try:
            gene_diseases = await _fetch_gene_diseases(card.gene_symbol)
            drugs = await _fetch_gene_drugs(card.gene_symbol)
        except Exception:
            card.drug_recommendation_summary = "药物数据库查询失败，未生成用药建议。"
            continue

        recommendations = _strict_filter_drugs(
            drugs,
            gene_symbol=card.gene_symbol,
            gene_diseases=gene_diseases,
            patient_terms=patient_terms,
            credible_variant=credible_variant,
        )
        card.drug_recommendations = recommendations
        card.drug_recommendation_summary = _summary_for_gene(
            recommendations,
            credible_variant=credible_variant,
        )

        if recommendations:
            try:
                card.trial_teams = await _fetch_trial_teams(card.gene_symbol, recommendations)
            except Exception:
                card.trial_teams = []

    return context
