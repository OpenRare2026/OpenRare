from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
HUMAN_TAXID = "9606"
GENE_SUMMARY_MAX_LEN = 2000
_REQUEST_INTERVAL_S = 0.34  # NCBI: max 3 req/s without API key


@dataclass(frozen=True)
class NcbiGeneRecord:
    gene_symbol: str
    ncbi_gene_id: str
    official_name: str
    summary: str
    aliases: str = ""
    chromosome: str = ""
    url: str = ""


def ncbi_gene_enabled() -> bool:
    return os.getenv("NCBI_GENE_ENABLED", "1").lower() in ("1", "true", "yes")


def _truncate_text(text: str, *, max_len: int = GENE_SUMMARY_MAX_LEN) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."


@lru_cache(maxsize=1)
def _request_identity() -> tuple[str, str]:
    tool = os.getenv("NCBI_TOOL_NAME", "search_agent").strip() or "search_agent"
    email = os.getenv("NCBI_CONTACT_EMAIL", "").strip()
    return tool, email


def _eutils_params(extra: dict[str, str]) -> dict[str, str]:
    params = dict(extra)
    api_key = os.getenv("NCBI_API_KEY", "").strip()
    if api_key:
        params["api_key"] = api_key
    tool, email = _request_identity()
    params.setdefault("tool", tool)
    if email:
        params.setdefault("email", email)
    return params


def _eutils_get(endpoint: str, params: dict[str, str]) -> dict:
    query = urllib.parse.urlencode(_eutils_params(params))
    url = f"{EUTILS_BASE}/{endpoint}?{query}"
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode())


def _search_gene_id(gene_symbol: str) -> str | None:
    symbol = gene_symbol.strip().upper()
    if not symbol:
        return None

    payload = _eutils_get(
        "esearch.fcgi",
        {
            "db": "gene",
            "term": f"{symbol}[sym] AND {HUMAN_TAXID}[taxid]",
            "retmode": "json",
            "retmax": "1",
        },
    )
    ids = payload.get("esearchresult", {}).get("idlist") or []
    return ids[0] if ids else None


def _fetch_gene_summaries(gene_ids: list[str]) -> dict[str, dict]:
    if not gene_ids:
        return {}

    payload = _eutils_get(
        "esummary.fcgi",
        {
            "db": "gene",
            "id": ",".join(gene_ids),
            "retmode": "json",
        },
    )
    result = payload.get("result", {})
    summaries: dict[str, dict] = {}
    for gene_id in gene_ids:
        item = result.get(gene_id)
        if isinstance(item, dict):
            summaries[gene_id] = item
    return summaries


def lookup_ncbi_gene(gene_symbol: str) -> NcbiGeneRecord | None:
    records = lookup_ncbi_genes([gene_symbol])
    symbol = gene_symbol.strip().upper()
    return records.get(symbol)


def lookup_ncbi_genes(gene_symbols: list[str]) -> dict[str, NcbiGeneRecord]:
    """Batch lookup human genes via NCBI Entrez Gene (E-utilities).

    Returns a map keyed by upper-case gene symbol.
    """
    if not ncbi_gene_enabled():
        return {}

    unique_symbols: list[str] = []
    seen: set[str] = set()
    for raw in gene_symbols:
        symbol = raw.strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            unique_symbols.append(symbol)

    if not unique_symbols:
        return {}

    symbol_to_id: dict[str, str] = {}
    for symbol in unique_symbols:
        try:
            gene_id = _search_gene_id(symbol)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
            gene_id = None
        if gene_id:
            symbol_to_id[symbol] = gene_id
        time.sleep(_REQUEST_INTERVAL_S)

    if not symbol_to_id:
        return {}

    id_to_symbol = {gene_id: symbol for symbol, gene_id in symbol_to_id.items()}
    try:
        summaries = _fetch_gene_summaries(list(symbol_to_id.values()))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return {}

    records: dict[str, NcbiGeneRecord] = {}
    for gene_id, item in summaries.items():
        symbol = id_to_symbol.get(gene_id, "")
        if not symbol:
            continue
        summary = _truncate_text(item.get("summary") or "")
        if not summary:
            continue
        official_name = (item.get("description") or item.get("name") or symbol).strip()
        aliases = (item.get("otheraliases") or item.get("alias") or "").strip()
        chromosome = (item.get("chromosome") or "").strip()
        records[symbol] = NcbiGeneRecord(
            gene_symbol=symbol,
            ncbi_gene_id=gene_id,
            official_name=official_name,
            summary=summary,
            aliases=aliases,
            chromosome=chromosome,
            url=f"https://www.ncbi.nlm.nih.gov/gene/{gene_id}",
        )
    return records
