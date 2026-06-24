"""Structured gene + MONDO disease research workflow."""

from __future__ import annotations

import json
import re
import time
from typing import Any

from agent.config import OPEN_TARGETS_ONLY
from agent.factory import build_china_trials_agent, build_literature_agent
from agent.open_targets_tools import (
    get_gene_disease_associations,
    get_gene_drug_details,
    lookup_gene,
)
from agent.report import (
    _parse_json_content,
    build_workflow_report,
    china_trial_hits_from_payload,
    diseases_from_associations,
    filtered_drug_from_payload,
    gene_info_from_lookup,
    papers_from_agent_result,
    summary_from_agent_result,
)
from agent.schemas import (
    DataSource,
    DrugTeamRecommendation,
    FilteredDrugHit,
    GeneDiseaseResearchInput,
    GeneDiseaseResearchReport,
    PaperHit,
)
from tools.china_trials import search_chictr_trials, search_chinadrug_trials
from tools.mondo import get_mondo_index

_STAGE_ORDER = {
    "APPROVAL": 0,
    "PHASE_4": 1,
    "PHASE_3": 2,
    "PHASE_2_3": 3,
    "PHASE_2": 4,
    "PHASE_1_2": 5,
    "PHASE_1": 6,
}

_LITERATURE_DRUGS_RE = re.compile(
    r"```(?:json)?\s*(\{.*?\})\s*```",
    re.DOTALL | re.IGNORECASE,
)


def _stage_rank(stage: str | None) -> int:
    return _STAGE_ORDER.get(stage or "", 99)


def _parse_tool_json(raw: str | object) -> object | None:
    if isinstance(raw, (dict, list)):
        return raw
    if not isinstance(raw, str):
        return None
    return _parse_json_content(raw)


async def _step_open_targets(
    gene_symbol: str,
    workflow_meta: dict[str, Any],
) -> tuple[object, object, list[FilteredDrugHit], list[DataSource]]:
    sources: list[DataSource] = []
    started = time.perf_counter()

    gene_raw = await lookup_gene.ainvoke({"gene_symbol": gene_symbol})
    gene_payload = _parse_tool_json(gene_raw)
    gene = gene_info_from_lookup(gene_payload) if isinstance(gene_payload, dict) else None
    if gene:
        sources.append(gene.source)

    diseases_payload: object = {}
    if gene and gene.ensembl_id:
        diseases_raw = await get_gene_disease_associations.ainvoke(
            {"ensembl_id": gene.ensembl_id, "limit": 5}
        )
        diseases_payload = _parse_tool_json(diseases_raw) or {}
        for disease in diseases_from_associations(diseases_payload):
            sources.append(disease.source)

    drugs_raw = await get_gene_drug_details.ainvoke({"gene_symbol": gene_symbol, "limit": 10})
    drugs_payload = _parse_tool_json(drugs_raw)
    ot_drugs: list[FilteredDrugHit] = []
    if isinstance(drugs_payload, list):
        for hit in drugs_payload:
            if not isinstance(hit, dict) or hit.get("error"):
                continue
            drug = filtered_drug_from_payload(hit, "get_gene_drug_details")
            if drug is not None:
                ot_drugs.append(drug)
                sources.append(drug.source)

    workflow_meta["step_1_1"] = {
        "duration_s": round(time.perf_counter() - started, 2),
        "ot_drug_count": len(ot_drugs),
    }
    return gene_payload, diseases_payload, ot_drugs, sources


def _parse_literature_drugs(agent_summary: str) -> list[FilteredDrugHit]:
    match = _LITERATURE_DRUGS_RE.search(agent_summary)
    if not match:
        return []

    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    drugs_data = payload.get("drugs") if isinstance(payload, dict) else None
    if not isinstance(drugs_data, list):
        return []

    literature_drugs: list[FilteredDrugHit] = []
    for item in drugs_data:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        source = DataSource(
            provider="paper_search",
            tool="paper_search_search_pubmed",
            url=None,
            entity_id=name,
        )
        literature_drugs.append(
            FilteredDrugHit(
                chembl_id="",
                name=name,
                description=item.get("evidence"),
                source=source,
            )
        )
    return literature_drugs


async def _step_literature_agent(
    gene_symbol: str,
    mondo_ids: list[str],
    existing_drug_names: set[str],
    workflow_meta: dict[str, Any],
) -> tuple[list[FilteredDrugHit], list[PaperHit], str]:
    if OPEN_TARGETS_ONLY:
        workflow_meta["step_1_2"] = {
            "skipped": True,
            "reason": "OPEN_TARGETS_ONLY=1",
        }
        return [], [], ""

    started = time.perf_counter()
    mondo_label = ", ".join(mondo_ids) if mondo_ids else "unknown disease"
    user_message = (
        f"Find drug candidates for gene {gene_symbol} related to diseases: {mondo_label}. "
        f"Existing drugs from Open Targets: {', '.join(sorted(existing_drug_names)) or 'none'}. "
        "Search PubMed and list additional drug candidates. "
        "End your response with a JSON block:\n"
        '```json\n{"drugs": [{"name": "DRUG", "evidence": "...", "pmids": ["123"]}]}\n```'
    )

    try:
        agent = await build_literature_agent()
        result = await agent.ainvoke({"messages": [{"role": "user", "content": user_message}]})
    except Exception as exc:
        workflow_meta["step_1_2"] = {
            "skipped": True,
            "reason": f"literature agent failed: {exc}",
            "duration_s": round(time.perf_counter() - started, 2),
        }
        return [], [], ""

    summary = summary_from_agent_result(result)
    papers = papers_from_agent_result(result)
    literature_drugs = _parse_literature_drugs(summary)

    deduped: list[FilteredDrugHit] = []
    seen = set(existing_drug_names)
    for drug in literature_drugs:
        key = drug.name.strip().upper()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(drug)

    workflow_meta["step_1_2"] = {
        "skipped": False,
        "duration_s": round(time.perf_counter() - started, 2),
        "literature_drug_count": len(deduped),
        "paper_count": len(papers),
    }
    return deduped, papers, summary


def _merge_drugs(
    ot_drugs: list[FilteredDrugHit],
    literature_drugs: list[FilteredDrugHit],
) -> list[FilteredDrugHit]:
    merged: list[FilteredDrugHit] = list(ot_drugs)
    seen = {drug.chembl_id for drug in ot_drugs if drug.chembl_id}
    seen_names = {drug.name.strip().upper() for drug in ot_drugs if drug.name}

    for drug in literature_drugs:
        name_key = drug.name.strip().upper()
        if drug.chembl_id and drug.chembl_id in seen:
            continue
        if name_key in seen_names:
            continue
        merged.append(drug)
        if drug.chembl_id:
            seen.add(drug.chembl_id)
        seen_names.add(name_key)
    return merged


def _annotate_and_sort_drugs(
    drugs: list[FilteredDrugHit],
    mondo_ids: list[str],
) -> list[FilteredDrugHit]:
    if not mondo_ids:
        return sorted(drugs, key=lambda drug: _stage_rank(drug.maximum_clinical_stage))

    index = get_mondo_index()
    annotated: list[FilteredDrugHit] = []
    for drug in drugs:
        indication_ids = [item.disease_id for item in drug.indications if item.disease_id]
        matched_mondo_ids = index.match_drug_to_mondos(mondo_ids, indication_ids)
        annotated.append(
            FilteredDrugHit(
                **drug.model_dump(
                    exclude={"matched_disease", "matched_mondo_ids"},
                ),
                matched_disease=bool(matched_mondo_ids),
                matched_mondo_ids=matched_mondo_ids,
            )
        )

    return sorted(
        annotated,
        key=lambda drug: (not drug.matched_disease, _stage_rank(drug.maximum_clinical_stage)),
    )


def _select_recommended_drugs(drugs: list[FilteredDrugHit], limit: int = 5) -> list[FilteredDrugHit]:
    matched = [drug for drug in drugs if drug.matched_disease]
    if matched:
        return matched
    return sorted(drugs, key=lambda drug: _stage_rank(drug.maximum_clinical_stage))[:limit]


async def _search_china_trials_for_drug(
    drug: FilteredDrugHit,
    gene_symbol: str,
) -> DrugTeamRecommendation:
    drug_names = drug.name
    chinadrug_raw = await search_chinadrug_trials.ainvoke(
        {"drug_names": drug_names, "gene_symbol": gene_symbol, "limit": 10}
    )
    chictr_raw = await search_chictr_trials.ainvoke(
        {"drug_names": drug_names, "gene_symbol": gene_symbol, "limit": 10}
    )

    chinadrug_payload = _parse_tool_json(chinadrug_raw)
    chictr_payload = _parse_tool_json(chictr_raw)

    chinadrug_trials = (
        china_trial_hits_from_payload(chinadrug_payload)
        if isinstance(chinadrug_payload, dict)
        else []
    )
    chictr_trials = (
        china_trial_hits_from_payload(chictr_payload)
        if isinstance(chictr_payload, dict)
        else []
    )

    return DrugTeamRecommendation(
        drug_name=drug.name,
        chembl_id=drug.chembl_id or None,
        matched_disease=drug.matched_disease,
        chinadrug_trials=chinadrug_trials,
        chictr_trials=chictr_trials,
    )


async def _step_china_trials(
    gene_symbol: str,
    recommended_drugs: list[FilteredDrugHit],
    workflow_meta: dict[str, Any],
) -> tuple[list[DrugTeamRecommendation], str]:
    started = time.perf_counter()
    recommendations: list[DrugTeamRecommendation] = []

    for drug in recommended_drugs:
        recommendations.append(await _search_china_trials_for_drug(drug, gene_symbol))

    agent_summary = ""
    if recommended_drugs:
        drug_list = ", ".join(drug.name for drug in recommended_drugs)
        user_message = (
            f"Search China clinical trials for gene {gene_symbol} and drugs: {drug_list}. "
            "Summarize the most relevant teams (sponsor, PI, institution) for each drug."
        )
        try:
            agent = await build_china_trials_agent()
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_message}]}
            )
            agent_summary = summary_from_agent_result(result)
        except Exception as exc:
            agent_summary = f"China trials agent summary unavailable: {exc}"

    if recommendations and agent_summary:
        recommendations[0] = recommendations[0].model_copy(
            update={"agent_summary": agent_summary}
        )

    workflow_meta["step_3"] = {
        "duration_s": round(time.perf_counter() - started, 2),
        "recommended_drug_count": len(recommended_drugs),
        "trial_search_count": len(recommendations),
    }
    return recommendations, agent_summary


def _build_summary(
    gene_symbol: str,
    mondo_ids: list[str],
    drugs: list[FilteredDrugHit],
    team_recommendations: list[DrugTeamRecommendation],
    literature_summary: str,
    china_summary: str,
) -> str:
    matched_count = sum(1 for drug in drugs if drug.matched_disease)
    lines = [
        f"## Gene: {gene_symbol}",
        f"## Target MONDO IDs: {', '.join(mondo_ids) if mondo_ids else 'none'}",
        f"## Drugs found: {len(drugs)} ({matched_count} matched target diseases)",
    ]

    for drug in drugs:
        flag = "matched" if drug.matched_disease else "unmatched"
        lines.append(
            f"- **{drug.name}** ({drug.chembl_id or 'no ChEMBL'}) "
            f"[{drug.maximum_clinical_stage or 'unknown'}] — {flag}"
        )

    if team_recommendations:
        lines.append("\n## China trial teams")
        for rec in team_recommendations:
            total = len(rec.chinadrug_trials) + len(rec.chictr_trials)
            lines.append(f"- **{rec.drug_name}**: {total} trial(s) found")

    if literature_summary:
        lines.append(f"\n## Literature supplement\n{literature_summary}")
    if china_summary:
        lines.append(f"\n## China trials agent summary\n{china_summary}")

    return "\n".join(lines)


async def run_workflow(workflow_input: GeneDiseaseResearchInput) -> GeneDiseaseResearchReport:
    """Run the structured gene + MONDO disease research workflow."""
    workflow_meta: dict[str, Any] = {}
    gene_symbol = workflow_input.gene_symbol.strip().upper()
    mondo_ids = [item.strip() for item in workflow_input.mondo_ids if item.strip()]

    gene_payload, diseases_payload, ot_drugs, sources = await _step_open_targets(
        gene_symbol,
        workflow_meta,
    )
    gene = gene_info_from_lookup(gene_payload) if isinstance(gene_payload, dict) else None
    diseases = (
        diseases_from_associations(diseases_payload)
        if isinstance(diseases_payload, dict)
        else []
    )

    literature_drugs: list[FilteredDrugHit] = []
    papers: list[PaperHit] = []
    literature_summary = ""
    if len(ot_drugs) < 5:
        existing_names = {drug.name.strip().upper() for drug in ot_drugs if drug.name}
        literature_drugs, papers, literature_summary = await _step_literature_agent(
            gene_symbol,
            mondo_ids,
            existing_names,
            workflow_meta,
        )
        for paper in papers:
            sources.append(paper.source)
        for drug in literature_drugs:
            sources.append(drug.source)
    else:
        workflow_meta["step_1_2"] = {"skipped": True, "reason": "ot_drug_count >= 5"}

    merged_drugs = _merge_drugs(ot_drugs, literature_drugs)

    step2_started = time.perf_counter()
    drugs = _annotate_and_sort_drugs(merged_drugs, mondo_ids)
    workflow_meta["step_2"] = {
        "duration_s": round(time.perf_counter() - step2_started, 2),
        "matched_count": sum(1 for drug in drugs if drug.matched_disease),
        "total_count": len(drugs),
    }

    recommended = _select_recommended_drugs(drugs)
    team_recommendations, china_summary = await _step_china_trials(
        gene_symbol,
        recommended,
        workflow_meta,
    )

    summary = _build_summary(
        gene_symbol,
        mondo_ids,
        drugs,
        team_recommendations,
        literature_summary,
        china_summary,
    )

    deduped_sources: dict[tuple[str, str, str | None], DataSource] = {}
    for source in sources:
        deduped_sources[(source.provider, source.tool, source.entity_id)] = source

    return build_workflow_report(
        workflow_input,
        gene=gene,
        diseases=diseases,
        drugs=drugs,
        literature_drugs=literature_drugs,
        team_recommendations=team_recommendations,
        papers=papers,
        summary=summary,
        workflow_meta=workflow_meta,
        sources=list(deduped_sources.values()),
    )
