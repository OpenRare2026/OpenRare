from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, ToolMessage

from agent.schemas import (
    ChinaTrialHit,
    DataSource,
    DiseaseAssociation,
    DrugAdverseEvent,
    DrugHit,
    DrugIndication,
    DrugMechanism,
    DrugPharmacogenomic,
    DrugReference,
    DrugTeamRecommendation,
    FilteredDrugHit,
    GeneDiseaseResearchInput,
    GeneDiseaseResearchReport,
    GeneInfo,
    GeneResearchReport,
    PaperHit,
    PgxAlleleEffect,
    PgxDrugProfile,
)

OPEN_TARGETS_BASE = "https://platform.opentargets.org"
CLINPGX_BASE = "https://www.clinpgx.org"
_LARGE_TOOL_PATH_RE = re.compile(r"/large_tool_results/\S+")


def _otp_disease_url(disease_id: str) -> str:
    return f"{OPEN_TARGETS_BASE}/disease/{disease_id}"


def _otp_target_url(ensembl_id: str) -> str:
    return f"{OPEN_TARGETS_BASE}/target/{ensembl_id}"


def _otp_drug_url(chembl_id: str) -> str:
    return f"{OPEN_TARGETS_BASE}/drug/{chembl_id}"


def _parse_json_content(content: str | list) -> object | None:
    if isinstance(content, list):
        items: list[object] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parsed = _parse_json_content(item.get("text", ""))
                if parsed is not None:
                    items.append(parsed)
            elif isinstance(item, str):
                parsed = _parse_json_content(item)
                if parsed is not None:
                    items.append(parsed)
        if not items:
            return None
        if len(items) == 1:
            return items[0]
        return items

    if not isinstance(content, str):
        return None
    content = content.strip()
    if not content:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def _resolve_tool_payload(
    content: str | list,
    files: dict | None = None,
) -> object | None:
    payload = _parse_json_content(content)
    if payload is not None:
        return payload

    if not isinstance(content, str) or not files or "large_tool_results" not in content:
        return None

    match = _LARGE_TOOL_PATH_RE.search(content)
    if not match:
        return None

    file_entry = files.get(match.group(0))
    if not isinstance(file_entry, dict):
        return None

    return _parse_json_content(file_entry.get("content", ""))


def _source_key(source: DataSource) -> tuple[str, str, str | None]:
    return (source.provider, source.tool, source.entity_id)


def _add_source(sources: dict[tuple[str, str, str | None], DataSource], source: DataSource) -> None:
    sources[_source_key(source)] = source


def _drug_hit_from_payload(hit: dict, tool_name: str) -> DrugHit | None:
    if not isinstance(hit, dict):
        return None
    chembl_id = hit.get("chembl_id") or hit.get("id", "")
    name = hit.get("name", "")
    if not chembl_id and not name:
        return None

    source = DataSource(
        provider="open_targets",
        tool=tool_name,
        url=_otp_drug_url(chembl_id) if chembl_id else None,
        entity_id=chembl_id or None,
    )
    return DrugHit(
        chembl_id=chembl_id,
        name=name,
        description=hit.get("description"),
        maximum_clinical_stage=hit.get("maximum_clinical_stage"),
        indications=[
            DrugIndication(
                disease_id=item.get("disease_id", ""),
                disease_name=item.get("disease_name", ""),
                max_clinical_stage=item.get("max_clinical_stage", ""),
            )
            for item in hit.get("indications", [])
            if isinstance(item, dict) and item.get("disease_name")
        ],
        mechanisms=[
            DrugMechanism(
                mechanism=item.get("mechanism", ""),
                target_name=item.get("target_name"),
                target_genes=item.get("target_genes", []),
            )
            for item in hit.get("mechanisms", [])
            if isinstance(item, dict) and item.get("mechanism")
        ],
        adverse_events=[
            DrugAdverseEvent(
                name=item.get("name", ""),
                count=item.get("count"),
                log_lr=item.get("log_lr"),
                meddra_code=item.get("meddra_code"),
            )
            for item in hit.get("adverse_events", [])
            if isinstance(item, dict) and item.get("name")
        ],
        pharmacogenomics=[
            DrugPharmacogenomic(
                gene_symbol=item.get("gene_symbol"),
                haplotype_id=item.get("haplotype_id"),
                variant_rs_id=item.get("variant_rs_id"),
                phenotype=item.get("phenotype"),
                category=item.get("category"),
                evidence_level=item.get("evidence_level"),
                annotation=item.get("annotation"),
                literature_pmids=item.get("literature_pmids", []),
            )
            for item in hit.get("pharmacogenomics", [])
            if isinstance(item, dict)
        ],
        references=[
            DrugReference(
                pmid=str(item.get("pmid", "")),
                title=item.get("title"),
                doi=item.get("doi"),
                url=item.get("url"),
            )
            for item in hit.get("references", [])
            if isinstance(item, dict) and item.get("pmid")
        ],
        source=source,
    )


def _merge_drug_hit(existing: DrugHit, incoming: DrugHit) -> DrugHit:
    if not existing.maximum_clinical_stage:
        existing.maximum_clinical_stage = incoming.maximum_clinical_stage
    if not existing.description:
        existing.description = incoming.description
    if incoming.indications:
        existing.indications = incoming.indications
    if incoming.mechanisms:
        existing.mechanisms = incoming.mechanisms
    if incoming.adverse_events:
        existing.adverse_events = incoming.adverse_events
    if incoming.pharmacogenomics:
        existing.pharmacogenomics = incoming.pharmacogenomics
    if incoming.references:
        existing.references = incoming.references
    if incoming.source.url:
        existing.source = incoming.source
    return existing


def _upsert_drug(drugs: list[DrugHit], drug: DrugHit) -> None:
    for index, existing in enumerate(drugs):
        if existing.chembl_id and existing.chembl_id == drug.chembl_id:
            drugs[index] = _merge_drug_hit(existing, drug)
            return
    drugs.append(drug)


def _paper_hit_from_payload(hit: dict, provider: str, tool_name: str) -> PaperHit | None:
    if not isinstance(hit, dict):
        return None
    if "text" in hit:
        try:
            hit = json.loads(hit["text"])
        except json.JSONDecodeError:
            return None
    if not isinstance(hit, dict):
        return None

    paper_id = str(hit.get("paper_id") or "")
    title = str(hit.get("title") or "")
    if not paper_id and not title:
        return None

    url = hit.get("url") or hit.get("pdf_url") or None
    pdf_url = hit.get("pdf_url") or None
    source = DataSource(
        provider=provider,
        tool=tool_name,
        url=url,
        entity_id=paper_id or None,
    )
    return PaperHit(
        paper_id=paper_id,
        title=title,
        authors=hit.get("authors") or None,
        abstract=hit.get("abstract") or None,
        published_date=hit.get("published_date") or None,
        url=url,
        doi=hit.get("doi") or None,
        pdf_url=pdf_url,
        source=source,
    )


def build_report(query: str, agent_result: dict) -> GeneResearchReport:
    messages = agent_result.get("messages", [])
    files = agent_result.get("files") or {}
    summary = ""
    gene: GeneInfo | None = None
    drugs: list[DrugHit] = []
    pgx_drugs: list[PgxDrugProfile] = []
    papers: list[PaperHit] = []
    sources: dict[tuple[str, str, str | None], DataSource] = {}

    for message in messages:
        if isinstance(message, AIMessage) and message.content and not message.tool_calls:
            summary = message.content if isinstance(message.content, str) else str(message.content)

        if not isinstance(message, ToolMessage):
            continue

        tool_name = message.name or ""
        payload = _resolve_tool_payload(message.content, files)
        if payload is None:
            continue

        if tool_name == "lookup_gene" and isinstance(payload, dict):
            ensembl_id = payload.get("ensembl_id", "")
            source = DataSource(
                provider="open_targets",
                tool=tool_name,
                url=_otp_target_url(ensembl_id) if ensembl_id else None,
                entity_id=ensembl_id or None,
            )
            _add_source(sources, source)
            gene = GeneInfo(
                symbol=payload.get("gene_symbol", ""),
                ensembl_id=ensembl_id,
                source=source,
            )

        elif tool_name == "get_gene_disease_associations" and isinstance(payload, dict):
            if gene is None:
                symbol = payload.get("approvedSymbol", "")
                if symbol:
                    gene = GeneInfo(
                        symbol=symbol,
                        ensembl_id="",
                        source=DataSource(
                            provider="open_targets",
                            tool=tool_name,
                            url=None,
                            entity_id=None,
                        ),
                    )

        elif tool_name == "search_gene_drugs" and isinstance(payload, list):
            for hit in payload:
                drug = _drug_hit_from_payload(hit, tool_name)
                if drug is None:
                    continue
                _add_source(sources, drug.source)
                _upsert_drug(drugs, drug)

        elif tool_name in {"get_drug_details", "get_gene_drug_details"}:
            hits = payload if isinstance(payload, list) else [payload]
            for hit in hits:
                if not isinstance(hit, dict) or hit.get("error"):
                    continue
                drug = _drug_hit_from_payload(hit, tool_name)
                if drug is None:
                    continue
                _add_source(sources, drug.source)
                _upsert_drug(drugs, drug)

        elif tool_name == "get_gene_pgx_profile" and isinstance(payload, dict):
            if payload.get("error"):
                continue
            gene_meta = payload.get("gene_meta") or {}
            accession_id = gene_meta.get("accession_id", "")
            symbol = payload.get("gene_symbol") or gene_meta.get("symbol", "")
            source = DataSource(
                provider="clinpgx_local",
                tool=tool_name,
                url=gene_meta.get("clinpgx_url")
                or (f"{CLINPGX_BASE}/gene/{accession_id}" if accession_id else None),
                entity_id=accession_id or symbol or None,
            )
            _add_source(sources, source)
            if gene is None and symbol:
                gene = GeneInfo(symbol=symbol, ensembl_id="", source=source)
            for hit in payload.get("drugs", []):
                if not isinstance(hit, dict):
                    continue
                drug_source = DataSource(
                    provider="clinpgx_local",
                    tool=tool_name,
                    url=(hit.get("clinpgx_urls") or [None])[0],
                    entity_id=hit.get("drug_name"),
                )
                _add_source(sources, drug_source)
                pgx_drugs.append(
                    PgxDrugProfile(
                        drug_name=hit.get("drug_name", ""),
                        priority=hit.get("priority", "P2"),
                        guideline_sources=hit.get("guideline_sources", []),
                        guideline_summary=hit.get("guideline_summary"),
                        evidence_levels=hit.get("evidence_levels", []),
                        effect_types=hit.get("effect_types", []),
                        allele_effects=[
                            PgxAlleleEffect(
                                allele=item.get("allele", ""),
                                effect=item.get("effect", ""),
                                allele_function=item.get("allele_function"),
                            )
                            for item in hit.get("allele_effects", [])
                            if isinstance(item, dict)
                        ],
                        pathways=hit.get("pathways", []),
                        source=drug_source,
                    )
                )

        elif tool_name.startswith("paper_search_search_"):
            provider = tool_name.removeprefix("paper_search_search_")
            hits = payload if isinstance(payload, list) else [payload]
            for hit in hits:
                paper = _paper_hit_from_payload(hit, provider, tool_name)
                if paper is None:
                    continue
                _add_source(sources, paper.source)
                papers.append(paper)

    return GeneResearchReport(
        query=query,
        generated_at=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        gene=gene,
        drugs=drugs,
        pgx_drugs=pgx_drugs,
        papers=papers,
        sources=list(sources.values()),
    )


def gene_info_from_lookup(payload: dict, tool_name: str = "lookup_gene") -> GeneInfo | None:
    if not isinstance(payload, dict):
        return None
    ensembl_id = payload.get("ensembl_id", "")
    symbol = payload.get("gene_symbol", "")
    if not symbol and not ensembl_id:
        return None
    source = DataSource(
        provider="open_targets",
        tool=tool_name,
        url=_otp_target_url(ensembl_id) if ensembl_id else None,
        entity_id=ensembl_id or None,
    )
    return GeneInfo(symbol=symbol, ensembl_id=ensembl_id, source=source)


def diseases_from_associations(
    payload: dict,
    tool_name: str = "get_gene_disease_associations",
) -> list[DiseaseAssociation]:
    if not isinstance(payload, dict):
        return []

    rows = (payload.get("associatedDiseases") or {}).get("rows") or []
    diseases: list[DiseaseAssociation] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        disease = row.get("disease") or {}
        disease_id = disease.get("id", "")
        disease_name = disease.get("name", "")
        if not disease_id and not disease_name:
            continue
        source = DataSource(
            provider="open_targets",
            tool=tool_name,
            url=_otp_disease_url(disease_id) if disease_id else None,
            entity_id=disease_id or None,
        )
        diseases.append(
            DiseaseAssociation(
                id=disease_id,
                name=disease_name,
                score=float(row.get("score") or 0.0),
                source=source,
            )
        )
    return diseases


def filtered_drug_from_payload(
    hit: dict,
    tool_name: str,
    *,
    matched_disease: bool = False,
    matched_mondo_ids: list[str] | None = None,
) -> FilteredDrugHit | None:
    drug = _drug_hit_from_payload(hit, tool_name)
    if drug is None:
        return None
    return FilteredDrugHit(
        **drug.model_dump(),
        matched_disease=matched_disease,
        matched_mondo_ids=matched_mondo_ids or [],
    )


def drugs_from_gene_drug_details(payload: object) -> list[FilteredDrugHit]:
    hits = payload if isinstance(payload, list) else [payload]
    drugs: list[FilteredDrugHit] = []
    for hit in hits:
        if not isinstance(hit, dict) or hit.get("error"):
            continue
        drug = filtered_drug_from_payload(hit, "get_gene_drug_details")
        if drug is not None:
            drugs.append(drug)
    return drugs


def china_trial_hits_from_payload(payload: dict) -> list[ChinaTrialHit]:
    if not isinstance(payload, dict):
        return []
    source = payload.get("source", "")
    trials: list[ChinaTrialHit] = []
    for row in payload.get("trials") or []:
        if not isinstance(row, dict):
            continue
        registration_number = row.get("registration_number", "")
        if not registration_number:
            continue
        title = row.get("title") or row.get("public_title") or row.get("scientific_title")
        trials.append(
            ChinaTrialHit(
                source=source,
                registration_number=registration_number,
                drug_name=row.get("drug_name") or row.get("intervention"),
                title=title,
                team=row.get("team") or {},
                match_score=row.get("match_score"),
            )
        )
    return trials


def papers_from_agent_result(agent_result: dict) -> list[PaperHit]:
    messages = agent_result.get("messages", [])
    files = agent_result.get("files") or {}
    papers: list[PaperHit] = []
    seen: set[str] = set()

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue
        tool_name = message.name or ""
        if not tool_name.startswith("paper_search_search_"):
            continue
        payload = _resolve_tool_payload(message.content, files)
        if payload is None:
            continue
        provider = tool_name.removeprefix("paper_search_search_")
        hits = payload if isinstance(payload, list) else [payload]
        for hit in hits:
            paper = _paper_hit_from_payload(hit, provider, tool_name)
            if paper is None or paper.paper_id in seen:
                continue
            seen.add(paper.paper_id)
            papers.append(paper)
    return papers


def summary_from_agent_result(agent_result: dict) -> str:
    messages = agent_result.get("messages", [])
    summary = ""
    for message in messages:
        if isinstance(message, AIMessage) and message.content and not message.tool_calls:
            summary = message.content if isinstance(message.content, str) else str(message.content)
    return summary


def build_workflow_report(
    workflow_input: GeneDiseaseResearchInput,
    *,
    gene: GeneInfo | None,
    diseases: list[DiseaseAssociation],
    drugs: list[FilteredDrugHit],
    literature_drugs: list[FilteredDrugHit],
    team_recommendations: list[DrugTeamRecommendation],
    papers: list[PaperHit],
    summary: str,
    workflow_meta: dict,
    sources: list[DataSource],
) -> GeneDiseaseResearchReport:
    mondo_label = ", ".join(workflow_input.mondo_ids) if workflow_input.mondo_ids else "none"
    query = (
        f"Gene {workflow_input.gene_symbol} research for MONDO diseases: {mondo_label}"
    )
    return GeneDiseaseResearchReport(
        input=workflow_input,
        query=query,
        generated_at=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        gene=gene,
        diseases=diseases,
        drugs=drugs,
        literature_drugs=literature_drugs,
        team_recommendations=team_recommendations,
        papers=papers,
        sources=sources,
        workflow_meta=workflow_meta,
    )
