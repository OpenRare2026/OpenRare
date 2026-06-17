#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export tissue-specific expression evidence from HPO terms.

The tool maps HPO IDs to coarse tissues, then exports a TPM table from GTEx
and HPA expression matrices. It is self-contained and does not import from the
VEP runner pipeline.
"""

import argparse
import gzip
import json
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNNER_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
BUNDLED_DATA_DIR = os.path.join(RUNNER_DIR, "vep_data", "hpo_tpm")
LEGACY_DATA_DIR = "/mnt/workspace/luqi/data"
DEFAULT_DATA_DIR = os.environ.get(
    "HPO_TPM_DATA_DIR",
    BUNDLED_DATA_DIR if os.path.isdir(BUNDLED_DATA_DIR) else LEGACY_DATA_DIR,
)
TPM_OUTPUT_COLUMNS = ["基因", "组织类型", "GTEx gene-level TPM", "HPA nTPM"]


def log(message: str):
    print(message, file=sys.stderr)


def clean_str(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def read_items_file(path: Optional[str]) -> List[str]:
    if not path:
        return []
    items = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            items.extend(x for x in re.split(r"[\s,;]+", line) if x)
    return items


def normalize_hpo_ids(hpo_ids: List[str]) -> List[str]:
    """Normalize HPO IDs and preserve duplicates for tissue voting."""
    normalized = []
    for raw in hpo_ids or []:
        text = clean_str(raw).upper().replace("_", ":")
        if not text:
            continue
        if re.fullmatch(r"\d{1,7}", text):
            text = f"HP:{int(text):07d}"
        match = re.search(r"HP:\d{7}", text)
        if match:
            normalized.append(match.group(0))
    return normalized


def coarse_tissue_name(name: str) -> Optional[str]:
    text = clean_str(name).lower().replace("_", " ")
    if not text:
        return None
    rules = [
        ("retina", ("retina", "retinal", "macula", "photoreceptor")),
        ("eye", ("eye", "ocular", "optic")),
        ("heart", ("heart", "cardiac", "myocard", "ventricle", "atrium")),
        ("muscle", ("muscle", "musculature", "myofiber", "myotube", "skeletal muscle")),
        ("nerve", ("nerve", "spinal cord", "peripheral nervous")),
        ("brain", ("brain", "cerebral", "cortex", "cerebell", "hippocamp", "neuron", "central nervous", "nervous system")),
        ("liver", ("liver", "hepatic", "hepatocyte")),
        ("lung", ("lung", "pulmonary", "bronch")),
        ("kidney", ("kidney", "renal", "nephron")),
        ("pancreas", ("pancreas", "pancreatic")),
        ("skin", ("skin", "epiderm", "dermis", "hair", "nail")),
        ("adipose", ("adipose", "fat")),
        ("adrenal gland", ("adrenal",)),
        ("blood vessel", ("blood vessel", "artery", "aorta", "vascular", "vein")),
        ("bone marrow", ("bone marrow", "hematopoietic", "haematopoietic")),
        ("blood", ("blood", "lymphocyte", "myeloid")),
        ("spleen", ("spleen", "splenic")),
        ("lymphoid", ("lymph", "thymus", "tonsil")),
        ("bone", ("bone", "phalanx", "metacarpal", "metatarsal", "femur", "tibia", "fibula", "humerus", "radius", "ulna", "rib", "vertebra", "sternum", "patella", "mandible", "clavicle", "skeleton", "skeletal joint")),
        ("colon", ("colon", "colorectal")),
        ("appendix", ("appendix",)),
        ("small intestine", ("small intestine", "duodenum", "ileum")),
        ("stomach", ("stomach", "gastric")),
        ("esophagus", ("esophagus", "oesophagus")),
        ("urinary bladder", ("urinary bladder", "bladder")),
        ("breast", ("breast", "mammary", "nipple")),
        ("cervix", ("cervix", "cervical")),
        ("ovary", ("ovary", "ovarian")),
        ("fallopian tube", ("fallopian",)),
        ("prostate", ("prostate",)),
        ("epididymis", ("epididymis",)),
        ("seminal vesicle", ("seminal vesicle",)),
        ("testis", ("testis", "testicular")),
        ("parathyroid gland", ("parathyroid",)),
        ("thyroid gland", ("thyroid",)),
        ("uterus", ("uterus", "uterine", "endometrium")),
        ("vagina", ("vagina", "vaginal", "vulva")),
        ("salivary gland", ("salivary",)),
        ("placenta", ("placenta", "placental")),
        ("choroid plexus", ("choroid plexus",)),
        ("pituitary", ("pituitary",)),
        ("tongue", ("tongue",)),
    ]
    for tissue, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return tissue
    return None


def open_text(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    return open(path, encoding="utf-8", errors="ignore")


class HPOMapper:
    def __init__(
        self,
        hpo_uberon_map: str,
        uberon_obo: str,
        hpo_obo: str,
        hp_full_owl: Optional[str] = None,
        top_n: int = 3,
    ):
        self.hpo_uberon_map = hpo_uberon_map
        self.uberon_obo = uberon_obo
        self.hpo_obo = hpo_obo
        self.hp_full_owl = hp_full_owl
        self.top_n = top_n
        self.hpo_to_uberon = defaultdict(list)
        self.hpo_parents = defaultdict(list)
        self.uberon_to_name = {}
        self.hpo_names = {}
        self._hpo_to_tissues_cache = {}
        self.last_tissue_counts = {}
        self.last_hpo_tissue_map = {}

    def load(self):
        self._load_uberon_names()
        self._load_hpo_obo()
        self._load_hpo_uberon_map()
        self._load_hpo_owl_mappings()

    def _add_hpo_uberon_mapping(self, hpo_id: str, uberon_id: str) -> bool:
        if uberon_id in self.hpo_to_uberon[hpo_id]:
            return False
        self.hpo_to_uberon[hpo_id].append(uberon_id)
        return True

    def _load_hpo_uberon_map(self):
        if not os.path.exists(self.hpo_uberon_map):
            log(f"[WARN] HPO-UBERON map not found: {self.hpo_uberon_map}")
            return
        count = 0
        with open_text(self.hpo_uberon_map) as handle:
            for line in handle:
                if line.startswith("#") or not line.strip():
                    continue
                normalized_line = line.replace("_", ":")
                hpo_match = re.search(r"HP:\d{7}", normalized_line)
                uberon_match = re.search(r"UBERON:\d{7}", normalized_line)
                if hpo_match and uberon_match:
                    if self._add_hpo_uberon_mapping(hpo_match.group(0), uberon_match.group(0)):
                        count += 1
        log(f"[HPO] phenotype_to_anatomy direct mappings: {count}")

    def _load_hpo_owl_mappings(self):
        """Extract HPO -> UBERON mappings from hp-full.owl logical definitions."""
        if not self.hp_full_owl or not os.path.exists(self.hp_full_owl):
            log(f"[HPO OWL] hp-full.owl not found, skip logical definitions: {self.hp_full_owl}")
            return
        log(f"[HPO OWL] Parsing logical definitions: {self.hp_full_owl}")
        count = 0
        with open_text(self.hp_full_owl) as handle:
            content = handle.read()
        pattern = re.compile(
            r'<owl:Class[^>]*rdf:about="http://purl\.obolibrary\.org/obo/HP_(\d+)"[^>]*>'
            r"(.*?)"
            r"</owl:Class>",
            re.DOTALL,
        )
        for match in pattern.finditer(content):
            hpo_id = f"HP:{int(match.group(1)):07d}"
            for uberon_match in re.finditer(r"UBERON[_:](\d+)", match.group(2)):
                uberon_id = f"UBERON:{int(uberon_match.group(1)):07d}"
                if self._add_hpo_uberon_mapping(hpo_id, uberon_id):
                    count += 1
        log(f"[HPO OWL] logical definition mappings: {count}")

    def _load_uberon_names(self):
        fallback = {
            "UBERON:0000966": "retina",
            "UBERON:0000948": "heart",
            "UBERON:0002048": "lung",
            "UBERON:0000007": "pituitary",
            "UBERON:0000955": "brain",
            "UBERON:0002371": "bone marrow",
            "UBERON:0002107": "liver",
            "UBERON:0002113": "kidney",
            "UBERON:0001264": "pancreas",
            "UBERON:0000970": "eye",
        }
        self.uberon_to_name.update(fallback)
        if not os.path.exists(self.uberon_obo):
            return
        current_id = None
        with open_text(self.uberon_obo) as handle:
            for line in handle:
                line = line.strip()
                if line == "[Term]":
                    current_id = None
                elif line.startswith("id: UBERON:"):
                    current_id = line.split("id:", 1)[1].strip()
                elif current_id and line.startswith("name: "):
                    self.uberon_to_name[current_id] = line.split("name:", 1)[1].strip().lower()

    def _load_hpo_obo(self):
        if not os.path.exists(self.hpo_obo):
            return
        current_id = None
        with open_text(self.hpo_obo) as handle:
            for line in handle:
                line = line.strip()
                if line == "[Term]":
                    current_id = None
                elif line.startswith("id: HP:"):
                    current_id = line.split("id:", 1)[1].strip()
                elif current_id and line.startswith("name: "):
                    self.hpo_names[current_id] = line.split("name:", 1)[1].strip()
                elif current_id and line.startswith("is_a: HP:"):
                    parent = line.split("is_a:", 1)[1].strip().split()[0].strip()
                    self.hpo_parents[current_id].append(parent)

    def _resolve_hpo_to_tissues(self, hpo_id: str) -> List[str]:
        """Climb is_a ancestors until the nearest usable UBERON tissue is found."""
        if hpo_id in self._hpo_to_tissues_cache:
            return self._hpo_to_tissues_cache[hpo_id]

        visited = set()
        queue = [hpo_id]
        tissues = []
        fallback_tissues = []
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for uberon in self.hpo_to_uberon.get(current, []):
                tissue = coarse_tissue_name(self.uberon_to_name.get(uberon, uberon))
                if tissue:
                    tissues.append(tissue)
            if tissues:
                break

            fallback = coarse_tissue_name(self.hpo_names.get(current, ""))
            if fallback and fallback not in fallback_tissues:
                fallback_tissues.append(fallback)

            queue.extend(self.hpo_parents.get(current, []))

        resolved = []
        seen = set()
        for tissue in tissues or fallback_tissues:
            if tissue not in seen:
                seen.add(tissue)
                resolved.append(tissue)
        self._hpo_to_tissues_cache[hpo_id] = resolved
        return resolved

    def map(self, hpo_ids: List[str]) -> List[str]:
        tissue_counts = Counter()
        first_seen_order = {}
        hpo_tissue_map = {}
        for hpo in hpo_ids:
            mapped_tissues = self._resolve_hpo_to_tissues(hpo)
            if mapped_tissues:
                hpo_tissue_map[hpo] = mapped_tissues
                for tissue in mapped_tissues:
                    if tissue not in first_seen_order:
                        first_seen_order[tissue] = len(first_seen_order)
                    tissue_counts[tissue] += 1
            else:
                log(f"[WARN] No tissue mapping for {hpo}")

        ranked = sorted(tissue_counts, key=lambda t: (-tissue_counts[t], first_seen_order[t], t))
        top_tissues = ranked[: max(int(self.top_n), 0)]
        self.last_tissue_counts = {tissue: int(tissue_counts[tissue]) for tissue in ranked}
        self.last_hpo_tissue_map = hpo_tissue_map
        if top_tissues:
            log("[HPO] Top tissues: " + ", ".join(f"{t}={self.last_tissue_counts[t]}" for t in top_tissues))
        return top_tissues


class GeneNormalizer:
    def __init__(self, hgnc_file: str, biomart_file: str):
        self.hgnc_file = hgnc_file
        self.biomart_file = biomart_file
        self.alias_to_official = {}
        self.ensembl_gene_to_symbol = {}

    def load(self):
        self._load_hgnc()
        self._load_biomart()

    @staticmethod
    def _split_multi_value(value: Any) -> List[str]:
        text = clean_str(value)
        if not text:
            return []
        return [x.strip() for x in re.split(r"[;,|]\s*", text) if x.strip()]

    @staticmethod
    def _strip_ensembl_version(value: str) -> str:
        return re.sub(r"\.\d+$", "", value)

    def _load_hgnc(self):
        if not os.path.exists(self.hgnc_file):
            log(f"[WARN] HGNC file not found: {self.hgnc_file}")
            return
        df = pd.read_csv(self.hgnc_file, sep="\t", low_memory=False)
        if "symbol" not in df.columns:
            return
        for _, row in df.iterrows():
            symbol = clean_str(row.get("symbol"))
            if not symbol:
                continue
            self.alias_to_official.setdefault(symbol, symbol)
            for col in ("alias_symbol", "prev_symbol"):
                for alias in self._split_multi_value(row.get(col)):
                    self.alias_to_official.setdefault(alias, symbol)
            ensembl_gene = clean_str(row.get("ensembl_gene_id"))
            if ensembl_gene:
                self.ensembl_gene_to_symbol.setdefault(self._strip_ensembl_version(ensembl_gene), symbol)

    def _load_biomart(self):
        if not os.path.exists(self.biomart_file):
            log(f"[WARN] BioMart file not found: {self.biomart_file}")
            return
        df = pd.read_csv(self.biomart_file, sep="\t", low_memory=False)
        gene_id_col = next((c for c in ("Gene stable ID", "Ensembl Gene ID", "ensembl_gene_id") if c in df.columns), None)
        symbol_col = next((c for c in ("HGNC symbol", "Gene name", "external_gene_name") if c in df.columns), None)
        if gene_id_col is None or symbol_col is None:
            return
        for _, row in df[[gene_id_col, symbol_col]].dropna().iterrows():
            gene_id = self._strip_ensembl_version(clean_str(row[gene_id_col]))
            symbol = clean_str(row[symbol_col])
            if gene_id and symbol:
                self.ensembl_gene_to_symbol.setdefault(gene_id, self.standardize(symbol))

    def standardize(self, gene: Any) -> str:
        gene = clean_str(gene)
        if not gene:
            return ""
        gene_no_version = self._strip_ensembl_version(gene)
        gene = self.ensembl_gene_to_symbol.get(gene_no_version, gene)
        return self.alias_to_official.get(gene, gene)


class ExpressionExporter:
    TISSUE_TO_GTEX = {
        "retina": [],
        "eye": [],
        "heart": ["Heart - Left Ventricle", "Heart - Atrial Appendage"],
        "muscle": ["Muscle - Skeletal"],
        "brain": [
            "Brain - Cortex", "Brain - Cerebellum", "Brain - Hippocampus",
            "Brain - Amygdala", "Brain - Anterior cingulate cortex (BA24)",
            "Brain - Caudate (basal ganglia)", "Brain - Cerebellar Hemisphere",
            "Brain - Frontal Cortex (BA9)", "Brain - Hypothalamus",
            "Brain - Nucleus accumbens (basal ganglia)",
            "Brain - Putamen (basal ganglia)", "Brain - Substantia nigra",
        ],
        "nerve": ["Nerve - Tibial", "Brain - Spinal cord (cervical c-1)"],
        "liver": ["Liver", "Liver - Hepatocyte", "Liver - Mixed Cell", "Liver - Portal Tract"],
        "lung": ["Lung"],
        "kidney": ["Kidney - Cortex", "Kidney - Medulla"],
        "pancreas": ["Pancreas", "Pancreas - Acini", "Pancreas - Islets", "Pancreas - Mixed Cell"],
        "skin": ["Skin - Not Sun Exposed (Suprapubic)", "Skin - Sun Exposed (Lower leg)"],
        "adipose": ["Adipose - Subcutaneous", "Adipose - Visceral (Omentum)"],
        "adrenal gland": ["Adrenal Gland"],
        "blood vessel": ["Artery - Aorta", "Artery - Coronary", "Artery - Pulmonary", "Artery - Tibial"],
        "bone marrow": ["Whole Blood"],
        "blood": ["Whole Blood", "Cells - EBV-transformed lymphocytes"],
        "lymphoid": ["Cells - EBV-transformed lymphocytes"],
        "spleen": ["Spleen"],
        "urinary bladder": ["Bladder"],
        "breast": ["Breast - Mammary Tissue"],
        "cervix": ["Cervix - Ectocervix", "Cervix - Endocervix"],
        "colon": [
            "Colon - Sigmoid", "Colon - Transverse", "Colon - Transverse - Mucosa",
            "Colon - Transverse - Muscularis", "Colon - Transverse - Mixed Cell",
        ],
        "small intestine": [
            "Small Intestine - Terminal Ileum",
            "Small Intestine - Terminal Ileum - Lymphoid Aggregate",
            "Small Intestine - Terminal Ileum - Mixed Cell",
        ],
        "stomach": [
            "Stomach", "Stomach - Mucosa", "Stomach - Muscularis",
            "Stomach - Mixed Cell",
        ],
        "esophagus": [
            "Esophagus - Mucosa", "Esophagus - Muscularis",
            "Esophagus - Gastroesophageal Junction",
        ],
        "ovary": ["Ovary"],
        "fallopian tube": ["Fallopian Tube"],
        "prostate": ["Prostate"],
        "testis": ["Testis"],
        "thyroid gland": ["Thyroid"],
        "uterus": ["Uterus"],
        "vagina": ["Vagina"],
        "salivary gland": ["Minor Salivary Gland"],
        "soft tissue": ["Cells - Cultured fibroblasts"],
        "pituitary": ["Pituitary"],
    }

    TISSUE_TO_HPA = {
        "retina": ["retina"],
        "eye": ["retina"],
        "heart": ["heart muscle"],
        "muscle": ["skeletal muscle", "smooth muscle"],
        "brain": ["cerebral cortex", "hippocampal formation", "cerebellum", "amygdala", "basal ganglia", "hypothalamus", "midbrain"],
        "nerve": ["spinal cord"],
        "liver": ["liver"],
        "lung": ["lung"],
        "kidney": ["kidney"],
        "pancreas": ["pancreas"],
        "skin": ["skin"],
        "adipose": ["adipose tissue"],
        "adrenal gland": ["adrenal gland"],
        "blood vessel": ["blood vessel"],
        "bone marrow": ["bone marrow"],
        "blood": ["bone marrow"],
        "lymphoid": ["lymph node", "thymus", "tonsil"],
        "spleen": ["spleen"],
        "urinary bladder": ["urinary bladder"],
        "breast": ["breast"],
        "cervix": ["cervix"],
        "colon": ["colon", "rectum"],
        "appendix": ["appendix"],
        "small intestine": ["small intestine", "duodenum"],
        "stomach": ["stomach"],
        "esophagus": ["esophagus"],
        "ovary": ["ovary"],
        "fallopian tube": ["fallopian tube"],
        "prostate": ["prostate"],
        "epididymis": ["epididymis"],
        "seminal vesicle": ["seminal vesicle"],
        "testis": ["testis"],
        "parathyroid gland": ["parathyroid gland"],
        "thyroid gland": ["thyroid gland"],
        "uterus": ["endometrium"],
        "vagina": ["vagina"],
        "salivary gland": ["salivary gland"],
        "gallbladder": ["gallbladder"],
        "placenta": ["placenta"],
        "choroid plexus": ["choroid plexus"],
        "tongue": ["tongue"],
        "pituitary": ["pituitary gland"],
    }

    def __init__(
        self,
        gtex_file: str,
        hpa_rna_file: str,
        gtex_tpm_cutoff: float,
        gtex_tau_cutoff: float,
        hpa_ntpm_cutoff: float,
        gene_normalizer: Optional[GeneNormalizer] = None,
    ):
        self.gtex_file = gtex_file
        self.hpa_rna_file = hpa_rna_file
        self.gtex_tpm_cutoff = float(gtex_tpm_cutoff)
        self.gtex_tau_cutoff = float(gtex_tau_cutoff)
        self.hpa_ntpm_cutoff = float(hpa_ntpm_cutoff)
        self.gene_normalizer = gene_normalizer or GeneNormalizer("", "")
        self.gtex = None
        self.hpa_matrix = None

    def load(self):
        self._load_gtex()
        self._load_hpa()

    @staticmethod
    def _column_key(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(name).lower())

    def _resolve_columns(self, available_columns, requested_columns: List[str]) -> List[str]:
        available = list(available_columns)
        by_key = {self._column_key(col): col for col in available}
        resolved = []
        for col in requested_columns:
            candidates = [
                col,
                str(col).replace(" - ", "_").replace(" ", "_").replace("-", "_"),
                str(col).replace("_", " - "),
                str(col).replace("_", " "),
            ]
            match = next((c for c in candidates if c in available), None)
            if match is None:
                match = by_key.get(self._column_key(col))
            if match is not None and match not in resolved:
                resolved.append(match)
        return resolved

    def _load_gtex(self):
        if not self.gtex_file or not os.path.exists(self.gtex_file):
            log(f"[WARN] GTEx file not found: {self.gtex_file}")
            return
        gtex = pd.read_csv(self.gtex_file, sep="\t", skiprows=2, index_col=0, low_memory=False)
        if "Description" in gtex.columns:
            gtex.index = gtex["Description"].map(self.gene_normalizer.standardize)
            gtex = gtex.drop(columns=["Description"])
        gtex = gtex.apply(pd.to_numeric, errors="coerce").fillna(0.0)
        self.gtex = gtex.groupby(gtex.index).max()
        log(f"[GTEx] Loaded: {self.gtex_file}")

    def _load_hpa(self):
        if not self.hpa_rna_file or not os.path.exists(self.hpa_rna_file):
            log(f"[WARN] HPA RNA file not found: {self.hpa_rna_file}")
            return
        hpa = pd.read_csv(self.hpa_rna_file, sep="\t", low_memory=False)
        if not {"Tissue", "nTPM"}.issubset(set(hpa.columns)):
            log(f"[WARN] HPA RNA file missing Tissue/nTPM columns: {self.hpa_rna_file}")
            return
        gene_col = next((c for c in ("Gene name", "Gene", "Ensembl") if c in hpa.columns), None)
        if gene_col is None:
            log(f"[WARN] HPA RNA file has no gene column: {self.hpa_rna_file}")
            return
        hpa = hpa[[gene_col, "Tissue", "nTPM"]].copy()
        hpa["gene"] = hpa[gene_col].map(self.gene_normalizer.standardize)
        hpa["nTPM"] = pd.to_numeric(hpa["nTPM"], errors="coerce").fillna(0.0)
        hpa = hpa[(hpa["gene"] != "") & hpa["Tissue"].notna()]
        if hpa.empty:
            return
        matrix = hpa.pivot_table(index="gene", columns="Tissue", values="nTPM", aggfunc="max", fill_value=0.0)
        self.hpa_matrix = matrix.groupby(matrix.index).max()
        log(f"[HPA] Loaded: {self.hpa_rna_file}")

    @staticmethod
    def _calculate_tau(expr_df: pd.DataFrame, target_cols: List[str]) -> pd.Series:
        x_max = expr_df.max(axis=1).replace(0, np.nan)
        tau = (1 - expr_df.div(x_max, axis=0)).sum(axis=1) / max(expr_df.shape[1] - 1, 1)
        return tau.fillna(0)

    def _set_record_value(self, records: Dict[Tuple[str, str], Dict[str, Any]], gene: Any, tissue: str, column: str, value: Any):
        gene = self.gene_normalizer.standardize(gene)
        numeric_value = pd.to_numeric(value, errors="coerce")
        if not gene or pd.isna(numeric_value):
            return
        record = records.setdefault(
            (gene, tissue),
            {"基因": gene, "组织类型": tissue, "GTEx gene-level TPM": np.nan, "HPA nTPM": np.nan},
        )
        record[column] = round(float(numeric_value), 6)

    def _gtex_expr_for_tissue(self, tissue: str) -> Optional[pd.Series]:
        if self.gtex is None:
            return None
        columns = self._resolve_columns(self.gtex.columns, self.TISSUE_TO_GTEX.get(tissue, []))
        if not columns:
            return None
        return self.gtex[columns].mean(axis=1)

    def _hpa_expr_for_tissue(self, tissue: str) -> Optional[pd.Series]:
        if self.hpa_matrix is None:
            return None
        requested = self.TISSUE_TO_HPA.get(tissue, [])
        by_lower = {str(col).lower(): col for col in self.hpa_matrix.columns}
        columns = []
        for col in requested:
            match = by_lower.get(str(col).lower())
            if match is not None and match not in columns:
                columns.append(match)
        if not columns:
            return None
        return self.hpa_matrix[columns].mean(axis=1)

    def _add_gtex_records(self, tissue: str, records: Dict[Tuple[str, str], Dict[str, Any]]):
        if self.gtex is None:
            return
        columns = self._resolve_columns(self.gtex.columns, self.TISSUE_TO_GTEX.get(tissue, []))
        if not columns:
            return
        expr = self.gtex[columns].mean(axis=1)
        tau = self._calculate_tau(self.gtex, columns)
        mask = (expr > self.gtex_tpm_cutoff) & (tau > self.gtex_tau_cutoff)
        for gene, value in expr[mask].items():
            self._set_record_value(records, gene, tissue, "GTEx gene-level TPM", value)

    def _add_hpa_records(self, tissue: str, records: Dict[Tuple[str, str], Dict[str, Any]]):
        expr = self._hpa_expr_for_tissue(tissue)
        if expr is None:
            return
        for gene, value in expr[expr > self.hpa_ntpm_cutoff].items():
            self._set_record_value(records, gene, tissue, "HPA nTPM", value)

    def _backfill(self, tissue: str, records: Dict[Tuple[str, str], Dict[str, Any]]):
        existing_genes = {gene for gene, record_tissue in records if record_tissue == tissue}
        if not existing_genes:
            return
        gtex_expr = self._gtex_expr_for_tissue(tissue)
        if gtex_expr is not None:
            for gene, value in gtex_expr.items():
                if gene in existing_genes:
                    self._set_record_value(records, gene, tissue, "GTEx gene-level TPM", value)
        hpa_expr = self._hpa_expr_for_tissue(tissue)
        if hpa_expr is not None:
            for gene, value in hpa_expr.items():
                if gene in existing_genes:
                    self._set_record_value(records, gene, tissue, "HPA nTPM", value)

    def build_table(self, tissues: List[str]) -> pd.DataFrame:
        records = {}
        for tissue in tissues:
            self._add_gtex_records(tissue, records)
            self._add_hpa_records(tissue, records)
            self._backfill(tissue, records)
        if not records:
            return pd.DataFrame(columns=TPM_OUTPUT_COLUMNS)
        df = pd.DataFrame(records.values(), columns=TPM_OUTPUT_COLUMNS)
        for column in ("GTEx gene-level TPM", "HPA nTPM"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df = df.sort_values(
            by=["组织类型", "GTEx gene-level TPM", "HPA nTPM", "基因"],
            ascending=[True, False, False, True],
            na_position="last",
        )
        return df[TPM_OUTPUT_COLUMNS].reset_index(drop=True)


def first_existing(paths: List[str]) -> str:
    for path in paths:
        if path and os.path.exists(path):
            return path
    return paths[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Map HPO IDs to tissues and export GTEx/HPA TPM evidence."
    )
    parser.add_argument(
        "--data-dir",
        default=DEFAULT_DATA_DIR,
        help=(
            "Directory containing HPO, UBERON, HGNC, BioMart, GTEx, and HPA files. "
            "Defaults to vep_data/hpo_tpm inside this bundle, or HPO_TPM_DATA_DIR."
        ),
    )
    parser.add_argument("--hpo-ids", nargs="*", default=[], help="HPO IDs. Repeated IDs are counted.")
    parser.add_argument("--hpo-file", help="File containing HPO IDs separated by whitespace/comma/semicolon.")
    parser.add_argument("--output-csv", default="TPM.csv")
    parser.add_argument("--audit-json")
    parser.add_argument("--top-n-tissues", type=int, default=3)
    parser.add_argument("--gtex-file")
    parser.add_argument("--hpa-rna-file")
    parser.add_argument("--hpo-uberon-map")
    parser.add_argument("--uberon-obo")
    parser.add_argument("--hpo-obo")
    parser.add_argument("--hp-full-owl")
    parser.add_argument("--hgnc-file")
    parser.add_argument("--biomart-file")
    parser.add_argument("--gtex-tpm-cutoff", type=float, default=5.0)
    parser.add_argument("--gtex-tau-cutoff", type=float, default=0.7)
    parser.add_argument("--hpa-ntpm-cutoff", type=float, default=5.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_dir = os.path.abspath(args.data_dir)
    gtex_file = args.gtex_file or first_existing([
        os.path.join(data_dir, "GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz"),
        os.path.join(data_dir, "GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct"),
        os.path.join(data_dir, "GTEx_Analysis_v9_RNAseq_RNASeQCv1.1.9_gene_median_tpm.gct.gz"),
        os.path.join(data_dir, "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz"),
    ])
    hpa_rna_file = args.hpa_rna_file or os.path.join(data_dir, "rna_tissue_consensus.tsv")
    hpo_uberon_map = args.hpo_uberon_map or os.path.join(data_dir, "phenotype_to_anatomy.txt")
    uberon_obo = args.uberon_obo or os.path.join(data_dir, "uberon.obo")
    hpo_obo = args.hpo_obo or os.path.join(data_dir, "hp.obo")
    hp_full_owl = args.hp_full_owl or os.path.join(data_dir, "hp-full.owl")
    hgnc_file = args.hgnc_file or os.path.join(data_dir, "hgnc_complete_set.txt")
    biomart_file = args.biomart_file or os.path.join(data_dir, "ensembl_biomart_export.txt")

    raw_hpos = list(args.hpo_ids) + read_items_file(args.hpo_file)
    hpo_ids = normalize_hpo_ids(raw_hpos)
    if not hpo_ids:
        raise SystemExit("hpo_ids cannot be empty; use --hpo-ids or --hpo-file.")

    mapper = HPOMapper(hpo_uberon_map, uberon_obo, hpo_obo, hp_full_owl=hp_full_owl, top_n=args.top_n_tissues)
    mapper.load()
    tissues = mapper.map(hpo_ids)

    gene_normalizer = GeneNormalizer(hgnc_file, biomart_file)
    gene_normalizer.load()

    exporter = ExpressionExporter(
        gtex_file=gtex_file,
        hpa_rna_file=hpa_rna_file,
        gtex_tpm_cutoff=args.gtex_tpm_cutoff,
        gtex_tau_cutoff=args.gtex_tau_cutoff,
        hpa_ntpm_cutoff=args.hpa_ntpm_cutoff,
        gene_normalizer=gene_normalizer,
    )
    exporter.load()
    tpm_df = exporter.build_table(tissues)

    output_csv = os.path.abspath(args.output_csv)
    output_dir = os.path.dirname(output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    tpm_df.to_csv(output_csv, index=False)

    audit = {
        "data_dir": data_dir,
        "gtex_file": gtex_file,
        "hpa_rna_file": hpa_rna_file,
        "hpo_uberon_map": hpo_uberon_map,
        "uberon_obo": uberon_obo,
        "hpo_obo": hpo_obo,
        "hp_full_owl": hp_full_owl,
        "hgnc_file": hgnc_file,
        "biomart_file": biomart_file,
        "hpo_count": len(hpo_ids),
        "hpo_ids": hpo_ids,
        "mapped_tissues": tissues,
        "mapped_tissue_counts": mapper.last_tissue_counts,
        "hpo_tissue_map": mapper.last_hpo_tissue_map,
        "tpm_row_count": int(len(tpm_df)),
        "output_csv": output_csv,
    }
    if args.audit_json:
        audit_json = os.path.abspath(args.audit_json)
        audit_dir = os.path.dirname(audit_json)
        if audit_dir:
            os.makedirs(audit_dir, exist_ok=True)
        with open(audit_json, "w", encoding="utf-8") as handle:
            json.dump(audit, handle, ensure_ascii=False, indent=2)

    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
