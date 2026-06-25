"""Validated openFDA wrapper tools via @cyanheads/openfda-mcp-server."""

from __future__ import annotations

import json
import re

from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.config import get_mcp_config

_DRUG_HEADER_RE = re.compile(
    r"^###\s+(.+?)\s*\(([^)]+)\)\s*$", re.MULTILINE
)
_FIELD_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.+)$", re.MULTILINE)
_TOTAL_RESULTS_RE = re.compile(r"\*\*(\d+)\s+total label results\*\*", re.IGNORECASE)


async def _call_openfda(tool_name: str, args: dict) -> str:
    client = MultiServerMCPClient(get_mcp_config())
    async with client.session("openfda") as session:
        result = await session.call_tool(tool_name, args)
        if result.isError:
            texts = [getattr(item, "text", str(item)) for item in result.content]
            raise RuntimeError(
                texts[0] if texts else f"openFDA tool '{tool_name}' failed"
            )
        parts: list[str] = []
        for item in result.content:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
            else:
                parts.append(str(item))
        return "\n".join(parts)


def _normalize_disease_query(disease_name: str) -> str:
    disease_name = disease_name.strip()
    if not disease_name:
        raise ValueError("disease_name must not be empty")
    term = disease_name.replace('"', "").replace("+", " ")
    term = "+".join(term.split())
    return f"indications_and_usage:{term}"


def _parse_label_hits(raw: str, limit: int) -> tuple[int, list[dict]]:
    if "No labels found" in raw or "No labels matched" in raw:
        return 0, []

    total_match = _TOTAL_RESULTS_RE.search(raw)
    total = int(total_match.group(1)) if total_match else 0

    headers = list(_DRUG_HEADER_RE.finditer(raw))
    hits: list[dict] = []

    for index, match in enumerate(headers[:limit]):
        start = match.end()
        end = headers[index + 1].start() if index + 1 < len(headers) else len(raw)
        block = raw[start:end]

        brand_name = match.group(1).strip()
        generic_name = match.group(2).strip()
        fields = {
            key.strip().lower().replace(" ", "_"): value.strip()
            for key, value in _FIELD_RE.findall(block)
        }

        indication_snippet = ""
        indication_match = re.search(
            r"\*\*Indications and usage:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)",
            block,
            re.DOTALL | re.IGNORECASE,
        )
        if indication_match:
            indication_snippet = indication_match.group(1).strip()[:500]

        if brand_name.lower() == "unknown" and generic_name:
            brand_name = generic_name

        hits.append(
            {
                "brand_name": brand_name,
                "generic_name": generic_name,
                "manufacturer": fields.get("manufacturer"),
                "application_number": fields.get("application_number"),
                "product_type": fields.get("product_type"),
                "route": fields.get("route"),
                "set_id": fields.get("set_id"),
                "effective_date": fields.get("effective_date"),
                "indication_snippet": indication_snippet or None,
            }
        )

    if not total and hits:
        total = len(hits)
    return total, hits


def _dedupe_hits(hits: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped: list[dict] = []
    for hit in hits:
        key = (hit.get("generic_name") or hit.get("brand_name") or "").upper()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(hit)
    return deduped


@tool
async def search_fda_drugs_by_disease(disease_name: str, limit: int = 20) -> str:
    """Search FDA-approved drugs by disease or medical indication.

    Uses openFDA drug labeling (indications_and_usage) via the openFDA MCP server.
    Returns brand/generic names, manufacturer, application numbers, and indication
    snippets for drugs labeled for the given disease.

    Args:
        disease_name: Disease or condition name in English (e.g. "cystic fibrosis").
        limit: Maximum distinct drugs to return (1-50, default 20).
    """
    disease_name = disease_name.strip()
    if not disease_name:
        return "disease_name is required."

    limit = max(1, min(limit, 50))
    search = _normalize_disease_query(disease_name)

    try:
        raw = await _call_openfda(
            "openfda_get_drug_label",
            {"search": search, "limit": min(limit * 2, 100)},
        )
    except RuntimeError as exc:
        return str(exc)

    total, hits = _parse_label_hits(raw, limit * 2)
    hits = _dedupe_hits(hits)[:limit]

    payload = {
        "source": "openfda",
        "tool": "search_fda_drugs_by_disease",
        "query": {
            "disease_name": disease_name,
            "openfda_search": search,
        },
        "total_matches": total,
        "returned": len(hits),
        "drugs": hits,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


@tool
async def get_fda_drug_profile(drug_name: str) -> str:
    """Get consolidated FDA profile for a drug by brand or generic name.

    Returns label highlights, adverse event summary, recalls, approval status,
    and shortage information from the openFDA MCP server.

    Args:
        drug_name: Brand or generic drug name (e.g. "ivacaftor", "Kalydeco").
    """
    drug_name = drug_name.strip()
    if not drug_name:
        return "drug_name is required."

    try:
        raw = await _call_openfda("openfda_drug_profile", {"drug": drug_name})
    except RuntimeError as exc:
        return str(exc)

    payload = {
        "source": "openfda",
        "tool": "get_fda_drug_profile",
        "query": {"drug_name": drug_name},
        "profile": raw,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


@tool
async def search_fda_drug_approvals(drug_name: str, limit: int = 10) -> str:
    """Search FDA Drugs@FDA approvals (NDA/ANDA) for a drug name.

    Args:
        drug_name: Brand or generic drug name.
        limit: Maximum records to return (1-50, default 10).
    """
    drug_name = drug_name.strip()
    if not drug_name:
        return "drug_name is required."

    limit = max(1, min(limit, 50))
    term = drug_name.replace('"', "")
    search = (
        f'(openfda.brand_name:"{term}"+OR+openfda.generic_name:"{term}")'
    )

    try:
        raw = await _call_openfda(
            "openfda_search_drug_approvals",
            {"search": search, "limit": limit},
        )
    except RuntimeError as exc:
        return str(exc)

    payload = {
        "source": "openfda",
        "tool": "search_fda_drug_approvals",
        "query": {"drug_name": drug_name, "openfda_search": search},
        "approvals": raw,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def get_openfda_tools() -> list:
    return [
        search_fda_drugs_by_disease,
        get_fda_drug_profile,
        search_fda_drug_approvals,
    ]
