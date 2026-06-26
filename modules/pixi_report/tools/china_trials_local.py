"""Local search over ChinaDrug and ChiCTR clinical trial registries."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from agent.config import PROJECT_ROOT

CHINADRUG_CSV = PROJECT_ROOT / "data/ChinaDrug/chinadrugtrials.csv"
CHICTR_CSV = PROJECT_ROOT / "data/Chictr/chictr.csv"

CHINADRUG_SEARCH_COLUMNS = ("drug_name", "indication", "title", "objective")
CHINADRUG_TEAM_FIELDS = (
    "applicant",
    "main_leader",
    "company",
    "committee",
)

CHICTR_SEARCH_COLUMNS = (
    "public_title",
    "scientific_title",
    "intervention",
    "study_ailment",
    "study_objective",
)
CHICTR_TEAM_FIELDS = (
    "applicant",
    "study_leader",
    "applicant_institution",
    "primary_sponsor",
)

_DRUG_NAME_SPLIT_RE = re.compile(r"[,;，；\n]+")
_NON_WORD_RE = re.compile(r"[\s\-_/]+")


def _is_ascii_identifier(term: str) -> bool:
    return bool(term) and term.isascii() and re.search(r"[A-Za-z]", term)


def _normalize_term(term: str) -> str:
    return _NON_WORD_RE.sub("", term.strip().lower())


def _ascii_term_pattern(term: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?<![A-Za-z0-9]){re.escape(term.strip())}(?![A-Za-z0-9])",
        re.IGNORECASE,
    )


def _parse_drug_names(drug_names: str | list[str] | None) -> list[str]:
    if drug_names is None:
        return []
    if isinstance(drug_names, list):
        raw_parts = drug_names
    else:
        raw_parts = _DRUG_NAME_SPLIT_RE.split(drug_names.strip())
    return [part.strip() for part in raw_parts if part and part.strip()]


def _collect_search_terms(
    drug_names: str | list[str] | None,
    gene_symbol: str | None,
) -> list[str]:
    terms: list[str] = []
    for drug in _parse_drug_names(drug_names):
        terms.append(drug)
    if gene_symbol and gene_symbol.strip():
        terms.append(gene_symbol.strip())
    seen: set[str] = set()
    unique: list[str] = []
    for term in terms:
        key = _normalize_term(term)
        if key and key not in seen:
            seen.add(key)
            unique.append(term)
    return unique


def _term_matches(term: str, text: str) -> bool:
    if not text or not term:
        return False
    stripped_term = term.strip()
    if not stripped_term:
        return False
    if stripped_term in text:
        return True
    if _is_ascii_identifier(stripped_term):
        if _ascii_term_pattern(stripped_term).search(text):
            return True
        normalized_term = _normalize_term(stripped_term)
        normalized_text = _normalize_term(text)
        if normalized_term and len(normalized_term) >= 3:
            return normalized_term in normalized_text
        return False
    return stripped_term in text


def _score_row(
    row: dict[str, str],
    terms: list[str],
    search_columns: tuple[str, ...],
    drug_column: str | None = None,
) -> tuple[int, list[str]]:
    score = 0
    matched_terms: list[str] = []
    for term in terms:
        term_hit = False
        if drug_column and _term_matches(term, row.get(drug_column, "")):
            score += 10
            term_hit = True
        for column in search_columns:
            if column == drug_column:
                continue
            if _term_matches(term, row.get(column, "")):
                score += 3
                term_hit = True
        if term_hit and term not in matched_terms:
            matched_terms.append(term)
    return score, matched_terms


def _extract_team(row: dict[str, str], team_fields: tuple[str, ...]) -> dict[str, str]:
    return {
        field_name: row.get(field_name, "").strip()
        for field_name in team_fields
        if row.get(field_name, "").strip()
    }


@dataclass
class TrialRegistryStore:
    chinadrug_rows: list[dict[str, str]] = field(default_factory=list)
    chictr_rows: list[dict[str, str]] = field(default_factory=list)

    @classmethod
    def load(cls) -> TrialRegistryStore:
        store = cls()
        store.chinadrug_rows = cls._read_csv(CHINADRUG_CSV)
        store.chictr_rows = cls._read_csv(CHICTR_CSV)
        return store

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def search_chinadrug(
        self,
        drug_names: str | list[str] | None = None,
        gene_symbol: str | None = None,
        limit: int = 20,
    ) -> dict:
        terms = _collect_search_terms(drug_names, gene_symbol)
        if not terms:
            return {
                "source": "ChinaDrug",
                "query": {"drug_names": _parse_drug_names(drug_names), "gene_symbol": gene_symbol},
                "total_matches": 0,
                "trials": [],
                "message": "Provide at least one drug name or gene symbol.",
            }

        scored: list[tuple[int, dict[str, str], list[str]]] = []
        for row in self.chinadrug_rows:
            score, matched_terms = _score_row(
                row,
                terms,
                CHINADRUG_SEARCH_COLUMNS,
                drug_column="drug_name",
            )
            if score > 0:
                scored.append((score, row, matched_terms))

        scored.sort(key=lambda item: (-item[0], item[1].get("registration_number", "")))
        trials = []
        for score, row, matched_terms in scored[:limit]:
            trials.append(
                {
                    "registration_number": row.get("registration_number", ""),
                    "drug_name": row.get("drug_name", ""),
                    "indication": row.get("indication", ""),
                    "title": row.get("title", ""),
                    "experimental_state": row.get("experimental_state", ""),
                    "stage": row.get("stage", ""),
                    "classification": row.get("classification", ""),
                    "team": _extract_team(row, CHINADRUG_TEAM_FIELDS),
                    "matched_terms": matched_terms,
                    "match_score": score,
                }
            )

        return {
            "source": "ChinaDrug",
            "query": {
                "drug_names": _parse_drug_names(drug_names),
                "gene_symbol": gene_symbol,
                "search_terms": terms,
            },
            "total_matches": len(scored),
            "returned": len(trials),
            "trials": trials,
        }

    def search_chictr(
        self,
        drug_names: str | list[str] | None = None,
        gene_symbol: str | None = None,
        limit: int = 20,
    ) -> dict:
        terms = _collect_search_terms(drug_names, gene_symbol)
        if not terms:
            return {
                "source": "ChiCTR",
                "query": {"drug_names": _parse_drug_names(drug_names), "gene_symbol": gene_symbol},
                "total_matches": 0,
                "trials": [],
                "message": "Provide at least one drug name or gene symbol.",
            }

        scored: list[tuple[int, dict[str, str], list[str]]] = []
        for row in self.chictr_rows:
            score, matched_terms = _score_row(
                row,
                terms,
                CHICTR_SEARCH_COLUMNS,
                drug_column="intervention",
            )
            if score > 0:
                scored.append((score, row, matched_terms))

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].get("registration_date", ""),
                item[1].get("registration_number", ""),
            )
        )
        trials = []
        for score, row, matched_terms in scored[:limit]:
            trials.append(
                {
                    "registration_number": row.get("registration_number", ""),
                    "url": row.get("url", ""),
                    "public_title": row.get("public_title", ""),
                    "scientific_title": row.get("scientific_title", ""),
                    "registration_status": row.get("registration_status", ""),
                    "registration_date": row.get("registration_date", ""),
                    "study_type": row.get("study_type", ""),
                    "intervention": row.get("intervention", ""),
                    "study_ailment": row.get("study_ailment", ""),
                    "team": _extract_team(row, CHICTR_TEAM_FIELDS),
                    "matched_terms": matched_terms,
                    "match_score": score,
                }
            )

        return {
            "source": "ChiCTR",
            "query": {
                "drug_names": _parse_drug_names(drug_names),
                "gene_symbol": gene_symbol,
                "search_terms": terms,
            },
            "total_matches": len(scored),
            "returned": len(trials),
            "trials": trials,
        }


_STORE: TrialRegistryStore | None = None


def get_trial_registry_store() -> TrialRegistryStore:
    global _STORE
    if _STORE is None:
        _STORE = TrialRegistryStore.load()
    return _STORE
