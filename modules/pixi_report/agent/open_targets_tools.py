"""Validated Open Targets wrapper tools.

The raw `query_open_targets_graphql` MCP tool fails when the LLM constructs
invalid queries (variables, unknown fields, jq filters). These wrappers use
pre-tested GraphQL templates instead.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.config import get_mcp_config

_ENSEMBL_RE = re.compile(r"^ENSG\d+$")
_CHEMBL_RE = re.compile(r"^CHEMBL\d+$")
_PUBMED_BASE = "https://pubmed.ncbi.nlm.nih.gov"
_EVIDENCE_LEVEL_ORDER = {"1A": 0, "1B": 1, "2A": 2, "2B": 3, "3": 4, "4": 5}
_STAGE_ORDER = {
    "APPROVAL": 0,
    "PHASE_4": 1,
    "PHASE_3": 2,
    "PHASE_2_3": 3,
    "PHASE_2": 4,
    "PHASE_1_2": 5,
    "PHASE_1": 6,
}


async def _call_open_targets(tool_name: str, args: dict) -> str:
    client = MultiServerMCPClient(get_mcp_config())
    async with client.session("open_targets") as session:
        result = await session.call_tool(tool_name, args)
        if result.isError:
            texts = [getattr(item, "text", str(item)) for item in result.content]
            raise RuntimeError(
                texts[0] if texts else f"Open Targets tool '{tool_name}' failed"
            )
        return "\n".join(getattr(item, "text", str(item)) for item in result.content)


def _parse_otp_payload(raw: str) -> dict:
    outer = json.loads(raw)
    if isinstance(outer, dict) and "text" in outer:
        outer = json.loads(outer["text"])
    if isinstance(outer, dict) and "result" in outer:
        return outer["result"]
    return outer


async def _query_open_targets_graphql(query: str) -> dict:
    raw = await _call_open_targets(
        "query_open_targets_graphql", {"query_string": query.strip()}
    )
    return _parse_otp_payload(raw)


def _fetch_pubmed_references(pmids: list[str]) -> list[dict]:
    unique_pmids = [pmid for pmid in dict.fromkeys(pmids) if pmid and pmid.isdigit()]
    if not unique_pmids:
        return []

    params = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "id": ",".join(unique_pmids),
            "retmode": "json",
        }
    )
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=15) as response:
        payload = json.loads(response.read().decode())

    result = payload.get("result", {})
    references: list[dict] = []
    for pmid in unique_pmids:
        item = result.get(pmid, {})
        if not isinstance(item, dict):
            continue
        doi = next(
            (
                article_id.get("value")
                for article_id in item.get("articleids", [])
                if article_id.get("idtype") == "doi" and article_id.get("value")
            ),
            None,
        )
        references.append(
            {
                "pmid": pmid,
                "title": item.get("title") or None,
                "doi": doi,
                "url": f"{_PUBMED_BASE}/{pmid}/",
            }
        )
    return references


def _stage_rank(stage: str) -> int:
    return _STAGE_ORDER.get(stage or "", 99)


def _evidence_rank(level: str | None) -> int:
    if not level:
        return 99
    return _EVIDENCE_LEVEL_ORDER.get(level, 98)


def _truncate(text: str | None, max_len: int = 400) -> str | None:
    if not text:
        return None
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _normalize_drug_details(
    drug: dict,
    *,
    gene_symbol: str = "",
    indication_limit: int = 15,
    adverse_event_limit: int = 10,
    pharmacogenomics_limit: int = 20,
    reference_limit: int = 5,
    pubmed_references: list[dict] | None = None,
) -> dict:
    gene_filter = gene_symbol.strip().upper()
    indication_rows = [
        {
            "disease_id": row.get("disease", {}).get("id", ""),
            "disease_name": row.get("disease", {}).get("name", ""),
            "max_clinical_stage": row.get("maxClinicalStage", ""),
        }
        for row in (drug.get("indications") or {}).get("rows", [])
        if row.get("disease", {}).get("name")
    ]
    indication_rows.sort(key=lambda item: _stage_rank(item["max_clinical_stage"]))
    indications = indication_rows[:indication_limit]

    mechanisms = []
    for row in (drug.get("mechanismsOfAction") or {}).get("rows", []):
        targets = row.get("targets") or []
        mechanisms.append(
            {
                "mechanism": row.get("mechanismOfAction", ""),
                "target_name": row.get("targetName"),
                "target_genes": [
                    target.get("approvedSymbol", "")
                    for target in targets
                    if target.get("approvedSymbol")
                ],
            }
        )

    adverse_events = [
        {
            "name": row.get("name", ""),
            "count": row.get("count"),
            "log_lr": row.get("logLR"),
            "meddra_code": row.get("meddraCode") or None,
        }
        for row in (drug.get("adverseEvents") or {}).get("rows", [])[:adverse_event_limit]
        if row.get("name")
    ]

    pharmacogenomics = []
    for row in drug.get("pharmacogenomics") or []:
        target = row.get("target") or {}
        entry_gene = target.get("approvedSymbol") or ""
        if gene_filter and entry_gene.upper() != gene_filter:
            continue
        pharmacogenomics.append(
            {
                "gene_symbol": entry_gene or None,
                "haplotype_id": row.get("haplotypeId"),
                "variant_rs_id": row.get("variantRsId"),
                "phenotype": row.get("phenotypeText"),
                "category": row.get("pgxCategory"),
                "evidence_level": row.get("evidenceLevel"),
                "annotation": _truncate(row.get("genotypeAnnotationText")),
                "literature_pmids": (row.get("literature") or [])[:3],
            }
        )
    pharmacogenomics.sort(
        key=lambda item: (
            _evidence_rank(item.get("evidence_level")),
            item.get("haplotype_id") or "",
            item.get("variant_rs_id") or "",
        )
    )
    pharmacogenomics = pharmacogenomics[:pharmacogenomics_limit]

    literature_pmids = [
        row.get("pmid", "")
        for row in (drug.get("literatureOcurrences") or {}).get("rows", [])
        if row.get("pmid")
    ]
    pgx_pmids = [
        pmid
        for entry in pharmacogenomics
        for pmid in entry.get("literature_pmids", [])
        if pmid
    ]
    ordered_pmids = list(dict.fromkeys([*pgx_pmids, *literature_pmids]))[:reference_limit]

    if pubmed_references is None:
        pubmed_references = _fetch_pubmed_references(ordered_pmids)
    else:
        by_pmid = {item["pmid"]: item for item in pubmed_references}
        pubmed_references = [
            by_pmid[pmid]
            for pmid in ordered_pmids
            if pmid in by_pmid
        ]

    return {
        "chembl_id": drug.get("id", ""),
        "name": drug.get("name", ""),
        "description": drug.get("description"),
        "maximum_clinical_stage": drug.get("maximumClinicalStage"),
        "indications": indications,
        "indications_total": len(indication_rows),
        "mechanisms": mechanisms,
        "adverse_events": adverse_events,
        "adverse_events_total": (drug.get("adverseEvents") or {}).get("count"),
        "pharmacogenomics": pharmacogenomics,
        "pharmacogenomics_total": len(pharmacogenomics) if not gene_filter else sum(
            1
            for row in drug.get("pharmacogenomics") or []
            if ((row.get("target") or {}).get("approvedSymbol") or "").upper() == gene_filter
        ),
        "references": pubmed_references,
    }


async def _fetch_drug_details(
    chembl_id: str,
    *,
    gene_symbol: str = "",
    indication_limit: int = 15,
    adverse_event_limit: int = 10,
    pharmacogenomics_limit: int = 20,
    reference_limit: int = 5,
) -> dict:
    query = f"""
    query {{
      drug(chemblId: "{chembl_id}") {{
        id
        name
        description
        maximumClinicalStage
        indications {{
          count
          rows {{
            maxClinicalStage
            disease {{ id name }}
          }}
        }}
        mechanismsOfAction {{
          rows {{
            mechanismOfAction
            targetName
            targets {{ approvedSymbol }}
          }}
        }}
        adverseEvents {{
          count
          rows {{ name count logLR meddraCode }}
        }}
        pharmacogenomics {{
          haplotypeId
          variantRsId
          phenotypeText
          pgxCategory
          evidenceLevel
          genotypeAnnotationText
          literature
          target {{ approvedSymbol }}
        }}
        literatureOcurrences {{
          count
          rows {{ pmid pmcid publicationDate }}
        }}
      }}
    }}
    """
    data = await _query_open_targets_graphql(query)
    drug = data.get("drug")
    if not drug:
        raise RuntimeError(f"No drug data returned for {chembl_id}.")
    return _normalize_drug_details(
        drug,
        gene_symbol=gene_symbol,
        indication_limit=indication_limit,
        adverse_event_limit=adverse_event_limit,
        pharmacogenomics_limit=pharmacogenomics_limit,
        reference_limit=reference_limit,
    )


@tool
async def lookup_gene(gene_symbol: str) -> str:
    """Resolve a gene symbol (e.g. BRCA2, TP53) to its Ensembl target ID."""
    raw = await _call_open_targets(
        "search_entities", {"query_strings": [gene_symbol.strip()]}
    )
    payload = json.loads(raw)
    inner = json.loads(payload["text"]) if "text" in payload else payload
    hits = inner["results"][0]["result"]["result"][0]
    targets = [h for h in hits if h.get("entity") == "target"]
    if not targets:
        return f"No target found for gene symbol '{gene_symbol}'."
    primary = targets[0]
    return json.dumps(
        {
            "gene_symbol": gene_symbol,
            "ensembl_id": primary["id"],
            "related_diseases": [h for h in hits if h.get("entity") == "disease"],
        },
        ensure_ascii=False,
        indent=2,
    )


@tool
async def get_gene_disease_associations(ensembl_id: str, limit: int = 5) -> str:
    """Get top disease associations for an Ensembl gene ID (ENSG...)."""
    ensembl_id = ensembl_id.strip()
    if not _ENSEMBL_RE.match(ensembl_id):
        return f"Invalid Ensembl ID '{ensembl_id}'. Expected format ENSG00000000000."

    limit = max(1, min(limit, 10))
    query = f"""
    query {{
      target(ensemblId: "{ensembl_id}") {{
        approvedSymbol
        associatedDiseases(page: {{index: 0, size: {limit}}}) {{
          count
          rows {{ disease {{ id name }} score }}
        }}
      }}
    }}
    """
    raw = await _call_open_targets(
        "query_open_targets_graphql", {"query_string": query.strip()}
    )
    data = _parse_otp_payload(raw)
    target = data.get("target")
    if not target:
        return f"No target data returned for {ensembl_id}."
    return json.dumps(target, ensure_ascii=False, indent=2)


@tool
async def search_gene_drugs(gene_symbol: str, drug_hint: str = "") -> str:
    """Search drugs related to a gene symbol via Open Targets drug search."""
    gene_symbol = gene_symbol.strip()
    hint = drug_hint.strip()
    query_string = f"{gene_symbol} {hint}".strip() if hint else gene_symbol
    query = f"""
    query {{
      search(queryString: "{query_string}", entityNames: ["drug"]) {{
        hits {{ id name description }}
      }}
    }}
    """
    raw = await _call_open_targets(
        "query_open_targets_graphql", {"query_string": query.strip()}
    )
    data = _parse_otp_payload(raw)
    hits = data.get("search", {}).get("hits", [])
    return json.dumps(hits[:10], ensure_ascii=False, indent=2)


@tool
async def get_drug_details(
    chembl_id: str,
    gene_symbol: str = "",
    indication_limit: int = 15,
    adverse_event_limit: int = 10,
    pharmacogenomics_limit: int = 20,
    reference_limit: int = 5,
) -> str:
    """Get detailed drug profile from Open Targets by ChEMBL ID.

    Returns maximum clinical stage, indications, mechanisms of action,
    adverse events, pharmacogenomics (optionally filtered by gene_symbol),
    and PubMed references enriched with title and DOI.
    """
    chembl_id = chembl_id.strip()
    if not _CHEMBL_RE.match(chembl_id):
        return f"Invalid ChEMBL ID '{chembl_id}'. Expected format CHEMBL123456."

    adverse_event_limit = max(1, min(adverse_event_limit, 25))
    pharmacogenomics_limit = max(1, min(pharmacogenomics_limit, 50))
    reference_limit = max(1, min(reference_limit, 10))

    try:
        details = await _fetch_drug_details(
            chembl_id,
            gene_symbol=gene_symbol.strip(),
            indication_limit=indication_limit,
            adverse_event_limit=adverse_event_limit,
            pharmacogenomics_limit=pharmacogenomics_limit,
            reference_limit=reference_limit,
        )
    except RuntimeError as exc:
        return str(exc)

    return json.dumps(details, ensure_ascii=False, indent=2)


@tool
async def get_gene_drug_details(
    gene_symbol: str,
    limit: int = 5,
    drug_hint: str = "",
    indication_limit: int = 15,
    adverse_event_limit: int = 10,
    pharmacogenomics_limit: int = 20,
    reference_limit: int = 5,
) -> str:
    """Search drugs for a gene and return full Open Targets drug profiles.

    Combines drug search with detailed fields: clinical stage, indications,
    mechanisms, adverse events, gene-filtered pharmacogenomics, and references.
    """
    gene_symbol = gene_symbol.strip()
    hint = drug_hint.strip()
    query_string = f"{gene_symbol} {hint}".strip() if hint else gene_symbol
    limit = max(1, min(limit, 10))
    adverse_event_limit = max(1, min(adverse_event_limit, 25))
    pharmacogenomics_limit = max(1, min(pharmacogenomics_limit, 50))
    reference_limit = max(1, min(reference_limit, 10))

    query = f"""
    query {{
      search(queryString: "{query_string}", entityNames: ["drug"]) {{
        hits {{ id name description }}
      }}
    }}
    """
    data = await _query_open_targets_graphql(query)
    hits = data.get("search", {}).get("hits", [])[:limit]
    if not hits:
        return json.dumps([], ensure_ascii=False, indent=2)

    results: list[dict] = []
    for hit in hits:
        chembl_id = hit.get("id", "")
        if not chembl_id:
            continue
        try:
            details = await _fetch_drug_details(
                chembl_id,
                gene_symbol=gene_symbol,
                indication_limit=indication_limit,
                adverse_event_limit=adverse_event_limit,
                pharmacogenomics_limit=pharmacogenomics_limit,
                reference_limit=reference_limit,
            )
        except Exception as exc:
            details = {
                "chembl_id": chembl_id,
                "name": hit.get("name", ""),
                "description": hit.get("description"),
                "error": f"No detailed drug data returned for {chembl_id}: {exc}",
            }
        results.append(details)

    return json.dumps(results, ensure_ascii=False, indent=2)


def get_open_targets_tools() -> list:
    return [
        lookup_gene,
        get_gene_disease_associations,
        search_gene_drugs,
        get_drug_details,
        get_gene_drug_details,
    ]
