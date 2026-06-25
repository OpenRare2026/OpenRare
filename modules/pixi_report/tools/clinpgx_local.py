"""Local ClinPGx/PharmGKB data loader and gene-level PGx profile builder."""

from __future__ import annotations

import csv
import html
import io
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from zipfile import ZipFile

from agent.config import PHARMGKB_DATA_DIR

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_EVIDENCE_ORDER = {"1A": 0, "1B": 1, "2A": 2, "2B": 3, "3": 4, "4": 5}
_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
_HIGH_EVIDENCE = frozenset({"1A", "1B"})


def _strip_html(text: str) -> str:
    if not text:
        return ""
    cleaned = _HTML_TAG_RE.sub(" ", html.unescape(text))
    return _WS_RE.sub(" ", cleaned).strip()


def _split_drugs(raw: str) -> list[str]:
    if not raw or not raw.strip():
        return []
    return [part.strip() for part in raw.split(";") if part.strip()]


def _pathway_name_from_filename(filename: str) -> str:
    stem = filename.removesuffix(".tsv")
    if "-" in stem:
        stem = stem.split("-", 1)[1]
    return stem.replace("_", " ")


@dataclass
class AlleleEffect:
    allele: str
    text: str
    allele_function: str | None = None


@dataclass
class DrugProfile:
    drug_name: str
    priority: str = "P2"
    guideline_sources: list[str] = field(default_factory=list)
    guideline_summary: str | None = None
    evidence_levels: list[str] = field(default_factory=list)
    effect_types: list[str] = field(default_factory=list)
    allele_effects: list[AlleleEffect] = field(default_factory=list)
    pathways: list[str] = field(default_factory=list)
    clinpgx_urls: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "drug_name": self.drug_name,
            "priority": self.priority,
            "guideline_sources": self.guideline_sources,
            "guideline_summary": self.guideline_summary,
            "evidence_levels": sorted(
                set(self.evidence_levels),
                key=lambda level: _EVIDENCE_ORDER.get(level, 99),
            ),
            "effect_types": sorted(set(self.effect_types)),
            "allele_effects": [
                {
                    "allele": item.allele,
                    "effect": item.text,
                    "allele_function": item.allele_function,
                }
                for item in self.allele_effects
            ],
            "pathways": sorted(set(self.pathways)),
            "clinpgx_urls": sorted(set(self.clinpgx_urls)),
        }


@dataclass
class GeneMeta:
    symbol: str
    accession_id: str
    name: str
    is_vip: bool
    has_cpic_guideline: bool
    has_variant_annotation: bool

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "accession_id": self.accession_id,
            "name": self.name,
            "is_vip": self.is_vip,
            "has_cpic_guideline": self.has_cpic_guideline,
            "has_variant_annotation": self.has_variant_annotation,
            "clinpgx_url": f"https://www.clinpgx.org/gene/{self.accession_id}",
        }


class ClinPgxLocalStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self._loaded = False
        self.data_version: str | None = None
        self._genes: dict[str, GeneMeta] = {}
        self._summaries_by_gene: dict[str, list[dict[str, str]]] = {}
        self._alleles_by_ann_id: dict[str, list[dict[str, str]]] = {}
        self._guidelines_by_gene: dict[str, list[dict]] = {}
        self._pathways_by_gene: dict[str, set[str]] = {}

    def _annotation_dir(self) -> Path:
        return self.data_dir / "AnnotationData"

    def _primary_dir(self) -> Path:
        return self.data_dir / "PrimaryData"

    def _read_created_date(self, zip_path: Path) -> str | None:
        if not zip_path.exists():
            return None
        with ZipFile(zip_path) as archive:
            for name in archive.namelist():
                if name.startswith("CREATED_") and name.endswith(".txt"):
                    return archive.read(name).decode("utf-8").strip()
        return None

    def _read_tsv_from_zip(self, zip_path: Path, tsv_name: str) -> csv.DictReader:
        with ZipFile(zip_path) as archive:
            handle = io.TextIOWrapper(archive.open(tsv_name), encoding="utf-8")
            return csv.DictReader(handle, delimiter="\t")

    def load(self) -> None:
        if self._loaded:
            return

        genes_zip = self._primary_dir() / "genes.zip"
        summary_zip = self._annotation_dir() / "summaryAnnotations.zip"
        guideline_zip = self._annotation_dir() / "guidelineAnnotations.json.zip"
        pathway_zip = self._annotation_dir() / "pathways-tsv.zip"

        for path in (genes_zip, summary_zip, guideline_zip, pathway_zip):
            if not path.exists():
                raise FileNotFoundError(f"Missing ClinPGx data file: {path}")

        self.data_version = self._read_created_date(summary_zip)

        for row in self._read_tsv_from_zip(genes_zip, "genes.tsv"):
            symbol = row.get("Symbol", "").strip()
            if not symbol:
                continue
            self._genes[symbol.upper()] = GeneMeta(
                symbol=symbol,
                accession_id=row.get("PharmGKB Accession Id", "").strip(),
                name=row.get("Name", "").strip(),
                is_vip=row.get("Is VIP", "").strip().lower() == "yes",
                has_cpic_guideline=row.get("Has CPIC Dosing Guideline", "").strip().lower()
                == "yes",
                has_variant_annotation=row.get("Has Variant Annotation", "").strip().lower()
                == "yes",
            )

        for row in self._read_tsv_from_zip(summary_zip, "summary_ann_alleles.tsv"):
            ann_id = row.get("Summary Annotation ID", "").strip()
            if ann_id:
                self._alleles_by_ann_id.setdefault(ann_id, []).append(row)

        for row in self._read_tsv_from_zip(summary_zip, "summary_annotations.tsv"):
            gene = row.get("Gene", "").strip().upper()
            if gene:
                self._summaries_by_gene.setdefault(gene, []).append(row)

        with ZipFile(guideline_zip) as archive:
            for name in archive.namelist():
                if not name.endswith(".json"):
                    continue
                payload = json.loads(archive.read(name))
                guideline = payload.get("guideline", payload)
                gene_symbols = {
                    gene.get("symbol", "").strip().upper()
                    for gene in guideline.get("relatedGenes", [])
                    if gene.get("symbol")
                }
                for symbol in gene_symbols:
                    self._guidelines_by_gene.setdefault(symbol, []).append(guideline)

        with ZipFile(pathway_zip) as archive:
            for name in archive.namelist():
                if not name.endswith(".tsv") or name.startswith("CREATED_"):
                    continue
                pathway_name = _pathway_name_from_filename(name)
                reader = csv.DictReader(
                    io.TextIOWrapper(archive.open(name), encoding="utf-8"),
                    delimiter="\t",
                )
                genes_in_file: set[str] = set()
                for row in reader:
                    controller = row.get("Controller", "")
                    for token in re.split(r"[,/]", controller):
                        token = token.strip().upper()
                        if token and token in self._genes:
                            genes_in_file.add(token)
                for symbol in genes_in_file:
                    self._pathways_by_gene.setdefault(symbol, set()).add(pathway_name)

        self._loaded = True

    def _resolve_gene(self, gene_symbol: str) -> GeneMeta | None:
        self.load()
        return self._genes.get(gene_symbol.strip().upper())

    def _compute_priority(self, has_guideline: bool, evidence_levels: set[str]) -> str:
        if has_guideline:
            return "P0"
        if evidence_levels & _HIGH_EVIDENCE:
            return "P1"
        return "P2"

    def _best_evidence(self, levels: set[str]) -> str:
        if not levels:
            return "4"
        return min(levels, key=lambda level: _EVIDENCE_ORDER.get(level, 99))

    def build_gene_pgx_profile(
        self,
        gene_symbol: str,
        *,
        include_low_evidence: bool = False,
        include_pathways: bool = True,
    ) -> dict:
        gene = self._resolve_gene(gene_symbol)
        if gene is None:
            return {
                "error": f"Gene '{gene_symbol}' not found in local ClinPGx genes.tsv.",
                "gene_symbol": gene_symbol.strip().upper(),
            }

        symbol = gene.symbol.upper()
        drugs: dict[str, DrugProfile] = {}

        def get_drug(name: str) -> DrugProfile:
            key = name.strip()
            if key not in drugs:
                drugs[key] = DrugProfile(drug_name=key)
            return drugs[key]

        for guideline in self._guidelines_by_gene.get(symbol, []):
            source = (guideline.get("source") or "").strip()
            summary_html = (guideline.get("summaryMarkdown") or {}).get("html", "")
            summary_text = _strip_html(summary_html)
            for chemical in guideline.get("relatedChemicals", []):
                drug_name = (chemical.get("name") or "").strip()
                if not drug_name:
                    continue
                profile = get_drug(drug_name)
                if source and source not in profile.guideline_sources:
                    profile.guideline_sources.append(source)
                if summary_text and not profile.guideline_summary:
                    profile.guideline_summary = summary_text

        for summary in self._summaries_by_gene.get(symbol, []):
            level = (summary.get("Level of Evidence") or "").strip()
            effect_type = (summary.get("Phenotype Category") or "").strip()
            url = (summary.get("URL") or "").strip()
            ann_id = (summary.get("Summary Annotation ID") or "").strip()
            for drug_name in _split_drugs(summary.get("Drug(s)", "")):
                profile = get_drug(drug_name)
                if level:
                    profile.evidence_levels.append(level)
                if effect_type:
                    profile.effect_types.append(effect_type)
                if url:
                    profile.clinpgx_urls.append(url)
                seen_effects: set[tuple[str, str]] = {
                    (item.allele, item.text) for item in profile.allele_effects
                }
                for allele_row in self._alleles_by_ann_id.get(ann_id, []):
                    allele = (allele_row.get("Genotype/Allele") or "").strip()
                    text = (allele_row.get("Annotation Text") or "").strip()
                    if not allele or not text:
                        continue
                    key = (allele, text)
                    if key in seen_effects:
                        continue
                    seen_effects.add(key)
                    profile.allele_effects.append(
                        AlleleEffect(
                            allele=allele,
                            text=text,
                            allele_function=(allele_row.get("Allele Function") or "").strip()
                            or None,
                        )
                    )

        if include_pathways:
            for pathway_name in sorted(self._pathways_by_gene.get(symbol, set())):
                for drug_name in drugs:
                    if drug_name.lower() in pathway_name.lower():
                        drugs[drug_name].pathways.append(pathway_name)
                if not drugs:
                    profile = get_drug(symbol)
                    profile.pathways.append(pathway_name)

        results: list[DrugProfile] = []
        for profile in drugs.values():
            profile.guideline_sources = sorted(set(profile.guideline_sources))
            evidence_set = set(profile.evidence_levels)
            profile.priority = self._compute_priority(
                bool(profile.guideline_sources),
                evidence_set,
            )
            profile.allele_effects = profile.allele_effects[:10]
            if not include_low_evidence and profile.priority == "P2":
                continue
            results.append(profile)

        results.sort(
            key=lambda item: (
                _PRIORITY_ORDER.get(item.priority, 99),
                _EVIDENCE_ORDER.get(self._best_evidence(set(item.evidence_levels)), 99),
                item.drug_name.lower(),
            )
        )

        return {
            "gene_symbol": gene.symbol,
            "gene_meta": gene.to_dict(),
            "data_version": self.data_version,
            "include_low_evidence": include_low_evidence,
            "drug_count": len(results),
            "drugs": [item.to_dict() for item in results],
        }


_STORE: ClinPgxLocalStore | None = None


def get_clinpgx_store(data_dir: Path | None = None) -> ClinPgxLocalStore:
    global _STORE
    if _STORE is None or (data_dir is not None and _STORE.data_dir != data_dir):
        _STORE = ClinPgxLocalStore(data_dir or PHARMGKB_DATA_DIR)
    return _STORE
