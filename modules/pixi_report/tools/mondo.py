"""MONDO rare-disease ontology index for cross-ontology disease matching."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote

from agent.config import MONDO_DATA_PATH

_EXACT_MATCH = "http://www.w3.org/2004/02/skos/core#exactMatch"
_CLOSE_MATCH = "http://www.w3.org/2004/02/skos/core#closeMatch"
_MONDO_OBO_RE = re.compile(r"MONDO[_:](\d+)", re.IGNORECASE)
_EFO_RE = re.compile(r"EFO[_:/](\d+)", re.IGNORECASE)
_DOID_RE = re.compile(r"DOID[_:/](\d+)", re.IGNORECASE)
_HP_RE = re.compile(r"HP[_:/](\d+)", re.IGNORECASE)
_NCIT_RE = re.compile(r"NCIT[_:/]?([A-Z]?\d+)", re.IGNORECASE)


def normalize_disease_id(raw: str) -> str:
    """Normalize ontology IDs to a canonical PREFIX_NNN form."""
    if not raw:
        return ""
    value = unquote(raw.strip())
    if value.startswith("http://") or value.startswith("https://"):
        value = value.rsplit("/", 1)[-1]

    mondo = _MONDO_OBO_RE.search(value)
    if mondo:
        return f"MONDO_{mondo.group(1)}"

    efo = _EFO_RE.search(value)
    if efo:
        return f"EFO_{efo.group(1)}"

    doid = _DOID_RE.search(value)
    if doid:
        return f"DOID_{doid.group(1)}"

    hp = _HP_RE.search(value)
    if hp:
        return f"HP_{hp.group(1)}"

    ncit = _NCIT_RE.search(value)
    if ncit:
        return f"NCIT_{ncit.group(1)}"

    if ":" in value:
        prefix, suffix = value.split(":", 1)
        return f"{prefix.upper()}_{suffix}"

    return value.upper()


class MondoIndex:
    """Lazy-loaded index mapping MONDO IDs to equivalent ontology IDs."""

    def __init__(self, data_path: Path | None = None) -> None:
        self._data_path = data_path or MONDO_DATA_PATH
        self._expanded: dict[str, set[str]] | None = None

    def _ensure_loaded(self) -> None:
        if self._expanded is not None:
            return

        expanded: dict[str, set[str]] = {}
        if not self._data_path.exists():
            self._expanded = expanded
            return

        with self._data_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)

        for graph in payload.get("graphs", []):
            for node in graph.get("nodes", []):
                node_id = normalize_disease_id(node.get("id", ""))
                if not node_id.startswith("MONDO_"):
                    continue

                equivalents: set[str] = {node_id}
                meta = node.get("meta") or {}

                for xref in meta.get("xrefs") or []:
                    normalized = normalize_disease_id(xref.get("val", ""))
                    if normalized:
                        equivalents.add(normalized)

                for prop in meta.get("basicPropertyValues") or []:
                    pred = prop.get("pred", "")
                    if pred not in {_EXACT_MATCH, _CLOSE_MATCH}:
                        continue
                    normalized = normalize_disease_id(prop.get("val", ""))
                    if normalized:
                        equivalents.add(normalized)

                expanded[node_id] = equivalents

        self._expanded = expanded

    def expand_mondo_id(self, mondo_id: str) -> set[str]:
        """Return the MONDO ID plus equivalent/xref ontology IDs."""
        self._ensure_loaded()
        normalized = normalize_disease_id(mondo_id)
        if not normalized.startswith("MONDO_"):
            return {normalized} if normalized else set()

        assert self._expanded is not None
        return set(self._expanded.get(normalized, {normalized}))

    def match_drug_to_mondos(
        self,
        input_mondo_ids: list[str],
        indication_disease_ids: list[str],
    ) -> list[str]:
        """Return input MONDO IDs that match any indication disease ID."""
        if not input_mondo_ids or not indication_disease_ids:
            return []

        expanded_inputs: dict[str, set[str]] = {
            mondo_id: self.expand_mondo_id(mondo_id) for mondo_id in input_mondo_ids
        }
        normalized_indications = {
            normalize_disease_id(disease_id)
            for disease_id in indication_disease_ids
            if disease_id
        }

        matched: list[str] = []
        for mondo_id, equivalents in expanded_inputs.items():
            if equivalents & normalized_indications:
                matched.append(mondo_id)
        return matched


@lru_cache(maxsize=1)
def get_mondo_index() -> MondoIndex:
    return MondoIndex()
