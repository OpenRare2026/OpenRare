#!/usr/bin/env python3
"""Phenotype-HPO scoring v2.

Inputs:
  - annotated variant CSV, using all_genes for candidate gene extraction
  - patient HPO list

Outputs:
  - gene_phenotype_score.csv
  - variant_phenotype_score.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pickle
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from path_config import display_path, load_paths, resolve_project_path

BROAD_ANCESTOR_BLACKLIST = {
    "HP:0000001",  # All
    "HP:0000118",  # Phenotypic abnormality
}


def log(message: str) -> None:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def elapsed_since(started_at: float) -> str:
    return f"{time.perf_counter() - started_at:.1f}s"


@dataclass
class HpoTerm:
    hpo_id: str
    name: str = ""
    is_obsolete: bool = False
    replaced_by: str = ""


@dataclass
class DiseaseProfile:
    gene_symbol: str
    omim_id: str = ""
    orpha_id: str = ""
    mondo_id: str = ""
    disease_name: str = ""
    source_dbs: set[str] = field(default_factory=set)
    disease_match_status: str = ""
    mapping_basis: str = ""
    hpos: dict[str, dict[str, Any]] = field(default_factory=dict)
    gene_disease_sources: set[str] = field(default_factory=set)
    disease_hpo_sources: set[str] = field(default_factory=set)


class HpoGraph:
    def __init__(self, hp_obo: Path):
        self.terms: dict[str, HpoTerm] = {}
        self.alt_id_to_id: dict[str, str] = {}
        self.parents: dict[str, set[str]] = defaultdict(set)
        self.children: dict[str, set[str]] = defaultdict(set)
        self._ancestor_cache: dict[str, set[str]] = {}
        self._parse_obo(hp_obo)

    def _parse_obo(self, hp_obo: Path) -> None:
        current: dict[str, Any] | None = None

        def flush(term: dict[str, Any] | None) -> None:
            if not term or "id" not in term:
                return
            hpo_id = term["id"]
            self.terms[hpo_id] = HpoTerm(
                hpo_id=hpo_id,
                name=term.get("name", ""),
                is_obsolete=term.get("is_obsolete", "false") == "true",
                replaced_by=term.get("replaced_by", ""),
            )
            for alt_id in term.get("alt_id", []):
                self.alt_id_to_id[alt_id] = hpo_id
            for parent_id in term.get("is_a", []):
                self.parents[hpo_id].add(parent_id)
                self.children[parent_id].add(hpo_id)

        with hp_obo.open() as f:
            for raw in f:
                line = raw.strip()
                if line == "[Term]":
                    flush(current)
                    current = {}
                    continue
                if line.startswith("[") and line != "[Term]":
                    flush(current)
                    current = None
                    continue
                if current is None or not line or line.startswith("!"):
                    continue
                if line.startswith("id: "):
                    current["id"] = line[4:].strip()
                elif line.startswith("name: "):
                    current["name"] = line[6:].strip()
                elif line.startswith("alt_id: "):
                    current.setdefault("alt_id", []).append(line[8:].strip())
                elif line.startswith("is_a: "):
                    current.setdefault("is_a", []).append(line[6:].split()[0])
                elif line.startswith("is_obsolete: "):
                    current["is_obsolete"] = line.split(":", 1)[1].strip()
                elif line.startswith("replaced_by: "):
                    current["replaced_by"] = line.split(":", 1)[1].strip()
            flush(current)

    def normalize_hpo(self, hpo_id: str) -> tuple[str, str]:
        hpo_id = hpo_id.strip()
        if hpo_id in self.alt_id_to_id:
            return self.alt_id_to_id[hpo_id], f"mapped_alt_id:{hpo_id}"
        term = self.terms.get(hpo_id)
        if term and term.is_obsolete and term.replaced_by:
            return term.replaced_by, f"mapped_obsolete:{hpo_id}"
        return hpo_id, ""

    def name(self, hpo_id: str) -> str:
        return self.terms.get(hpo_id, HpoTerm(hpo_id)).name

    def ancestors(self, hpo_id: str) -> set[str]:
        if hpo_id in self._ancestor_cache:
            return self._ancestor_cache[hpo_id]
        seen = {hpo_id}
        stack = list(self.parents.get(hpo_id, set()))
        while stack:
            parent = stack.pop()
            if parent in seen:
                continue
            seen.add(parent)
            stack.extend(self.parents.get(parent, set()))
        self._ancestor_cache[hpo_id] = seen
        return seen

    def is_valid(self, hpo_id: str) -> bool:
        return hpo_id in self.terms


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Phenotype-HPO score (Pixi edition)")
    p.add_argument("--config", type=Path, default=None, help="Path configuration TOML")
    p.add_argument("--input-csv", type=Path, default=None)
    p.add_argument("--hpo-file", type=Path, default=None)
    p.add_argument("--outdir", type=Path, default=None)
    p.add_argument("--min-similarity", type=float, default=0.20)
    p.add_argument("--max-orpha-files", type=int, default=0, help="debug only; 0 means all")
    p.add_argument("--input-format", choices=["auto", "csv", "parquet"], default="auto")
    p.add_argument("--chunksize", type=int, default=100000)
    p.add_argument("--orpha-index", type=Path, default=None)
    p.add_argument("--rebuild-orpha-index", action="store_true")
    return p.parse_args()


def split_gene_list(value: Any) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text or text in {"-", ".", "nan", "None"}:
        return []
    parts = re.split(r"[;,|/\\s]+", text)
    return [p.strip() for p in parts if p.strip() and p.strip() not in {"-", "."}]


def load_hgnc_aliases(hgnc_file: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    alias: dict[str, dict[str, str]] = {}
    approved: dict[str, dict[str, str]] = {}
    rows: list[dict[str, str]] = []
    with hgnc_file.open(newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    primary_keys: set[str] = set()
    row_infos: list[tuple[dict[str, str], dict[str, str]]] = []
    for row in rows:
        symbol = row.get("symbol", "").strip()
        if not symbol:
            continue
        info = {
            "gene_symbol": symbol,
            "hgnc_id": row.get("hgnc_id", "").strip(),
            "ensembl_gene_id": row.get("ensembl_gene_id", "").strip(),
            "ncbi_gene_id": row.get("entrez_id", "").strip(),
            "status": row.get("status", "").strip(),
        }
        approved[symbol.upper()] = info
        row_infos.append((row, info))
        for key in (symbol, row.get("hgnc_id", ""), row.get("ensembl_gene_id", ""), row.get("entrez_id", "")):
            key = str(key).strip().strip('"')
            if key:
                primary_keys.add(key.upper())
                alias[key.upper()] = info

    ambiguous_aliases: set[str] = set()
    for row, info in row_infos:
        for field_name in ("alias_symbol", "prev_symbol"):
            for key in str(row.get(field_name, "")).split("|"):
                key = str(key).strip().strip('"')
                if not key:
                    continue
                key_upper = key.upper()
                # A current HGNC-approved symbol must never be overridden by
                # another gene's historical alias, e.g. FHL1 is both an
                # approved gene and an old CFH alias.
                if key_upper in primary_keys or key_upper in ambiguous_aliases:
                    continue
                existing = alias.get(key_upper)
                if existing and existing.get("gene_symbol") != info.get("gene_symbol"):
                    ambiguous_aliases.add(key_upper)
                    alias.pop(key_upper, None)
                    continue
                alias[key_upper] = info
    return alias, approved


def normalize_gene(gene: str, alias_index: dict[str, dict[str, str]]) -> tuple[str, str, str]:
    gene = str(gene).strip()
    if not gene:
        return "", "", "empty"
    info = alias_index.get(gene.upper())
    if info:
        return info["gene_symbol"], info.get("hgnc_id", ""), "resolved"
    return gene, "", "unresolved"


def detect_input_format(path: Path, input_format: str) -> str:
    if input_format != "auto":
        return input_format
    suffix = path.suffix.lower()
    if suffix in {".parquet", ".pq"}:
        return "parquet"
    return "csv"


def iter_variant_chunks(path: Path, input_format: str, chunksize: int):
    fmt = detect_input_format(path, input_format)
    if fmt == "csv":
        yield from pd.read_csv(path, dtype=str, chunksize=max(chunksize, 1))
        return
    if fmt == "parquet":
        try:
            df = pd.read_parquet(path)
        except ImportError as exc:
            raise RuntimeError("Parquet input requires pyarrow or fastparquet in the runtime environment") from exc
        yield df
        return
    raise ValueError(f"Unsupported input format: {input_format}")


def prepare_variant_chunk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna("")
    if "all_genes" not in df.columns:
        raise ValueError("input file must contain all_genes column")
    if "gene_symbol" not in df.columns:
        raise ValueError("input file must contain gene_symbol column")
    variant_ids = []
    for _, row in df.iterrows():
        variant_ids.append(f"{row.get('chrom','')}-{row.get('pos','')}-{row.get('ref','')}-{row.get('alt','')}")
    df["_variant_id_v2"] = variant_ids
    return df


def scan_input_genes(
    input_path: Path,
    input_format: str,
    chunksize: int,
    alias_index: dict[str, dict[str, str]],
) -> tuple[set[str], dict[str, int], int]:
    candidate_genes: set[str] = set()
    counts: dict[str, int] = defaultdict(int)
    variant_rows = 0
    for chunk in iter_variant_chunks(input_path, input_format, chunksize):
        df = prepare_variant_chunk(chunk)
        variant_rows += len(df)
        for _, row in df.iterrows():
            raw_genes = split_gene_list(row.get("all_genes", ""))
            raw_genes.extend(split_gene_list(row.get("gene_symbol", "")))
            normalized_in_row: set[str] = set()
            for raw_gene in raw_genes:
                gene, _, _ = normalize_gene(raw_gene, alias_index)
                if gene:
                    candidate_genes.add(gene)
                    normalized_in_row.add(gene)
            for gene in normalized_in_row:
                counts[gene] += 1
    return candidate_genes, counts, variant_rows


def load_patient_hpos(hpo_file: Path, graph: HpoGraph) -> tuple[list[dict[str, Any]], list[str]]:
    qc_rows: list[dict[str, Any]] = []
    scoring: list[str] = []
    with hpo_file.open() as f:
        for raw in f:
            hpo_id = raw.strip()
            if not hpo_id or hpo_id.startswith("#"):
                continue
            scoring_hpo, warning = graph.normalize_hpo(hpo_id)
            valid = graph.is_valid(scoring_hpo)
            used = valid
            if used and scoring_hpo not in scoring:
                scoring.append(scoring_hpo)
            term = graph.terms.get(scoring_hpo)
            qc_rows.append(
                {
                    "input_hpo_id": hpo_id,
                    "scoring_hpo_id": scoring_hpo,
                    "hpo_name": graph.name(scoring_hpo),
                    "is_valid": valid,
                    "is_obsolete": bool(term.is_obsolete) if term else False,
                    "replaced_by": term.replaced_by if term else "",
                    "used_in_main_score": used,
                    "warning": warning if warning else ("" if valid else "invalid_hpo"),
                }
            )
    return qc_rows, scoring


def load_hpoa(hpoa_file: Path, graph: HpoGraph) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]]]:
    disease_hpos: dict[str, dict[str, Any]] = defaultdict(lambda: {"name": "", "hpos": {}})
    disease_positive_hpos: dict[str, set[str]] = defaultdict(set)
    with hpoa_file.open() as f:
        reader = None
        for line in f:
            if line.startswith("#"):
                continue
            if reader is None:
                header = line.rstrip("\n").split("\t")
                reader = csv.DictReader(f, delimiter="\t", fieldnames=header)
                break
        if reader is None:
            return disease_hpos, disease_positive_hpos
        for row in reader:
            disease_id = row.get("database_id", "").strip()
            hpo_id = row.get("hpo_id", "").strip()
            qualifier = row.get("qualifier", "").strip()
            if not disease_id or not hpo_id or qualifier == "NOT":
                continue
            hpo_id, _ = graph.normalize_hpo(hpo_id)
            if not graph.is_valid(hpo_id):
                continue
            disease_hpos[disease_id]["name"] = row.get("disease_name", "").strip()
            disease_hpos[disease_id]["hpos"][hpo_id] = {
                "hpo_name": graph.name(hpo_id) or row.get("hpo_id", ""),
                "frequency_raw": row.get("frequency", "").strip(),
                "evidence": row.get("evidence", "").strip(),
                "reference": row.get("reference", "").strip(),
                "source": "HPOA",
            }
            disease_positive_hpos[disease_id].add(hpo_id)
    return disease_hpos, disease_positive_hpos


def compute_ic(graph: HpoGraph, disease_positive_hpos: dict[str, set[str]]) -> dict[str, float]:
    total = max(len(disease_positive_hpos), 1)
    counts: dict[str, int] = defaultdict(int)
    for hpos in disease_positive_hpos.values():
        expanded: set[str] = set()
        for hpo_id in hpos:
            expanded.update(graph.ancestors(hpo_id))
        for hpo_id in expanded:
            counts[hpo_id] += 1
    ic: dict[str, float] = {}
    denom = total + 1
    for hpo_id in graph.terms:
        prob = (counts.get(hpo_id, 0) + 1) / denom
        ic[hpo_id] = -math.log(prob)
    return ic


def load_genes_to_disease(path: Path, alias_index: dict[str, dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            gene, hgnc_id, status = normalize_gene(row.get("gene_symbol", ""), alias_index)
            disease_id = row.get("disease_id", "").strip()
            if gene and disease_id.startswith("OMIM:"):
                out[gene].append(
                    {
                        "omim_id": disease_id.split(":", 1)[1],
                        "association_type": row.get("association_type", "").strip(),
                        "source": "genes_to_disease",
                    }
                )
    return out


def query_omim_sqlite(db_path: Path, genes: set[str], alias_index: dict[str, dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    if not genes:
        return out
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("create index if not exists idx_omim_hgnc_approved_gene_symbol on omim(hgnc_approved_gene_symbol)")
    cur.execute("create index if not exists idx_omim_hgnc_gene_symbol on omim(hgnc_gene_symbol)")
    con.commit()
    gene_list = sorted(genes)
    placeholders = ",".join("?" for _ in gene_list)
    rows = cur.execute(
        "select mim_number, mim_type, title, hgnc_approved_gene_symbol, hgnc_gene_symbol, inheritance "
        f"from omim where hgnc_approved_gene_symbol in ({placeholders}) or hgnc_gene_symbol in ({placeholders})",
        gene_list + gene_list,
    ).fetchall()
    for r in rows:
        mim_type = r["mim_type"] or ""
        if "phenotype" not in mim_type:
            continue
        matched_genes = {
            str(r["hgnc_approved_gene_symbol"] or "").strip(),
            str(r["hgnc_gene_symbol"] or "").strip(),
        }
        for gene in matched_genes & genes:
            if not gene:
                continue
            out[gene].append(
                {
                    "omim_id": str(r["mim_number"]),
                    "disease_name": r["title"] or "",
                    "inheritance": r["inheritance"] or "",
                    "source": "omim_sqlite",
                }
            )
    con.close()
    return out


def parse_external_refs(items: Any) -> dict[str, set[str]]:
    refs: dict[str, set[str]] = defaultdict(set)
    if not isinstance(items, list):
        return refs
    for item in items:
        ref = item.get("Reference") if isinstance(item, dict) else None
        src = item.get("Source") if isinstance(item, dict) else None
        if ref and src:
            refs[str(src).upper()].add(str(ref))
    return refs


def merge_hpo(target: dict[str, dict[str, Any]], hpo_id: str, hpo_name: str, freq: str, source: str) -> None:
    if not hpo_id:
        return
    row = target.setdefault(hpo_id, {"hpo_name": hpo_name, "frequency_raw": set(), "sources": set()})
    if hpo_name and not row.get("hpo_name"):
        row["hpo_name"] = hpo_name
    if freq:
        row["frequency_raw"].add(freq)
    row["sources"].add(source)


def load_orphapackets(
    yaml_dir: Path,
    genes: set[str],
    alias_index: dict[str, dict[str, str]],
    max_files: int = 0,
    log_progress: bool = False,
    index_path: Path | None = None,
    rebuild_index: bool = False,
) -> tuple[dict[str, list[DiseaseProfile]], dict[str, set[str]]]:
    if index_path and not max_files and index_path.exists() and not rebuild_index:
        step_started = time.perf_counter()
        with index_path.open("rb") as f:
            payload = pickle.load(f)
        all_profiles: dict[str, list[DiseaseProfile]] = payload.get("gene_profiles", {})
        all_refs: dict[str, set[str]] = payload.get("orpha_to_omim_gene_refs", {})
        filtered = {gene: all_profiles[gene] for gene in sorted(genes) if gene in all_profiles}
        if log_progress:
            log(
                "      Orphapacket index loaded: "
                f"indexed_genes={len(all_profiles)}, matched_genes={len(filtered)}, path={display_path(index_path)} ({elapsed_since(step_started)})"
            )
        return filtered, all_refs

    orpha_names: dict[str, str] = {}
    orpha_hpos: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    orpha_gene_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    orpha_to_omim_gene_refs: dict[str, set[str]] = defaultdict(set)

    def process_node(node: dict[str, Any]) -> None:
        orpha_id = str(node.get("ORPHAcode", "")).strip()
        label = str(node.get("Label", "")).strip()
        if not orpha_id:
            return
        if label:
            orpha_names.setdefault(orpha_id, label)
        hpos: dict[str, dict[str, Any]] = {}
        phenotypes = node.get("Phenotypes")
        if isinstance(phenotypes, list):
            for item in phenotypes:
                ph = item.get("Phenotype") if isinstance(item, dict) else None
                if not isinstance(ph, dict):
                    continue
                merge_hpo(hpos, str(ph.get("HPOId", "")).strip(), str(ph.get("HPOTerm", "")).strip(), str(ph.get("HPOFrequency", "")).strip(), "Orphapacket")
        for hid, hrow in hpos.items():
            orpha_hpos[orpha_id].setdefault(hid, {"hpo_name": hrow.get("hpo_name", ""), "frequency_raw": set(), "sources": set()})
            orpha_hpos[orpha_id][hid]["frequency_raw"].update(hrow.get("frequency_raw", set()))
            orpha_hpos[orpha_id][hid]["sources"].update(hrow.get("sources", set()))
        genes_obj = node.get("Genes")
        if isinstance(genes_obj, list):
            for item in genes_obj:
                g = item.get("Gene") if isinstance(item, dict) else None
                if not isinstance(g, dict):
                    continue
                gene_raw = str(g.get("Symbol", "")).strip()
                gene, hgnc_id, status = normalize_gene(gene_raw, alias_index)
                refs = parse_external_refs(g.get("ExternalReferences"))
                for omim_ref in refs.get("OMIM", set()):
                    orpha_to_omim_gene_refs[orpha_id].add(omim_ref)
                orpha_gene_records[orpha_id].append(
                    {
                        "gene": gene,
                        "raw_gene": gene_raw,
                        "hgnc_id": hgnc_id,
                        "association_type": str(g.get("DisorderGeneAssociationType", "")).strip(),
                    }
                )

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "ORPHAcode" in obj:
                process_node(obj)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    files = sorted(yaml_dir.glob("ORPHApacket_*.yaml"))
    if max_files:
        files = files[:max_files]
    if log_progress:
        log(f"      Orphapacket YAML files to parse: {len(files)}")
    for idx, path in enumerate(files, 1):
        try:
            data = yaml.safe_load(path.read_text())
        except Exception:
            continue
        walk(data)
        if log_progress and (idx % 1000 == 0 or idx == len(files)):
            log(f"      Orphapackets parsed: {idx}/{len(files)}")

    gene_profiles: dict[str, dict[str, DiseaseProfile]] = defaultdict(dict)
    build_full_index = bool(index_path and not max_files)
    for orpha_id, records in orpha_gene_records.items():
        if not orpha_hpos.get(orpha_id):
            continue
        for rec in records:
            gene = rec["gene"]
            if not gene:
                continue
            if not build_full_index and gene not in genes:
                continue
            profile = gene_profiles[gene].setdefault(
                orpha_id,
                DiseaseProfile(
                    gene_symbol=gene,
                    orpha_id=orpha_id,
                    disease_name=orpha_names.get(orpha_id, ""),
                    source_dbs={"ORPHA"},
                    disease_match_status="separate_orpha_record",
                    mapping_basis="none",
                ),
            )
            profile.gene_disease_sources.add("Orphapacket")
            for hid, hrow in orpha_hpos[orpha_id].items():
                profile.hpos.setdefault(hid, {"hpo_name": hrow.get("hpo_name", ""), "frequency_raw": set(), "sources": set()})
                profile.hpos[hid]["frequency_raw"].update(hrow.get("frequency_raw", set()))
                profile.hpos[hid]["sources"].update(hrow.get("sources", set()))
                profile.disease_hpo_sources.add("Orphapacket")
    out = {g: list(profs.values()) for g, profs in gene_profiles.items()}
    if build_full_index and index_path:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = index_path.with_suffix(index_path.suffix + ".tmp")
        with tmp.open("wb") as f:
            pickle.dump(
                {
                    "version": 1,
                    "source_dir": display_path(yaml_dir),
                    "gene_profiles": out,
                    "orpha_to_omim_gene_refs": dict(orpha_to_omim_gene_refs),
                },
                f,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        tmp.replace(index_path)
        filtered = {gene: out[gene] for gene in sorted(genes) if gene in out}
    else:
        filtered = out
    if log_progress:
        log(
            "      Orphapacket indexed profiles: "
            f"genes={len(filtered)}, indexed_genes={len(out)}, diseases_with_hpo={len(orpha_hpos)}, "
            f"gene_disease_records={sum(len(v) for v in orpha_gene_records.values())}"
        )
        if build_full_index and index_path:
            log(f"      Orphapacket index written: {index_path}")
    return filtered, orpha_to_omim_gene_refs


def load_mondo_xrefs(mondo_obo: Path) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    omim_to_mondo: dict[str, str] = {}
    orpha_to_mondo: dict[str, str] = {}
    mondo_names: dict[str, str] = {}
    current_id = ""
    current_name = ""

    def flush_xref(line: str) -> None:
        if not current_id:
            return
        if "MONDO:equivalentTo" not in line and "skos:exactMatch" not in line:
            return
        m = re.search(r"OMIM:(\d+)", line)
        if m:
            omim_to_mondo[m.group(1)] = current_id
        m = re.search(r"Orphanet:(\d+)", line)
        if m:
            orpha_to_mondo[m.group(1)] = current_id

    with mondo_obo.open() as f:
        for raw in f:
            line = raw.strip()
            if line == "[Term]":
                current_id = ""
                current_name = ""
            elif line.startswith("id: MONDO:"):
                current_id = line.split("id: ", 1)[1].strip()
            elif line.startswith("name: "):
                current_name = line.split("name: ", 1)[1].strip()
                if current_id:
                    mondo_names[current_id] = current_name
            elif line.startswith("xref: ") or line.startswith("property_value: skos:exactMatch"):
                flush_xref(line)
    return omim_to_mondo, orpha_to_mondo, mondo_names


def profile_from_omim(
    gene: str,
    omim_id: str,
    hpoa_disease_hpos: dict[str, dict[str, Any]],
    omim_name: str = "",
    source: str = "OMIM",
    association_type: str = "",
) -> DiseaseProfile | None:
    disease_key = f"OMIM:{omim_id}"
    hpoa = hpoa_disease_hpos.get(disease_key)
    if not hpoa or not hpoa.get("hpos"):
        return None
    profile = DiseaseProfile(
        gene_symbol=gene,
        omim_id=omim_id,
        disease_name=omim_name or hpoa.get("name", ""),
        source_dbs={"OMIM"},
        disease_match_status="separate_omim_record",
        mapping_basis="none",
    )
    profile.gene_disease_sources.add(source)
    for hid, hrow in hpoa["hpos"].items():
        profile.hpos[hid] = {
            "hpo_name": hrow.get("hpo_name", ""),
            "frequency_raw": {hrow.get("frequency_raw", "")} if hrow.get("frequency_raw") else set(),
            "sources": {"HPOA"},
        }
        profile.disease_hpo_sources.add("HPOA")
    return profile


def reconcile_profiles(
    omim_profiles: list[DiseaseProfile],
    orpha_profiles: list[DiseaseProfile],
    omim_to_mondo: dict[str, str],
    orpha_to_mondo: dict[str, str],
) -> list[DiseaseProfile]:
    used_orpha: set[int] = set()
    out: list[DiseaseProfile] = []
    for op in omim_profiles:
        op.mondo_id = omim_to_mondo.get(op.omim_id, "")
        matched = False
        for idx, rp in enumerate(orpha_profiles):
            if idx in used_orpha:
                continue
            rp.mondo_id = orpha_to_mondo.get(rp.orpha_id, "")
            if op.mondo_id and rp.mondo_id and op.mondo_id == rp.mondo_id:
                merged = DiseaseProfile(
                    gene_symbol=op.gene_symbol,
                    omim_id=op.omim_id,
                    orpha_id=rp.orpha_id,
                    mondo_id=op.mondo_id,
                    disease_name=op.disease_name or rp.disease_name,
                    source_dbs={"OMIM", "ORPHA"},
                    disease_match_status="matched_same_disease",
                    mapping_basis="MONDO_equivalentTo",
                )
                merged.gene_disease_sources.update(op.gene_disease_sources)
                merged.gene_disease_sources.update(rp.gene_disease_sources)
                merged.disease_hpo_sources.update(op.disease_hpo_sources)
                merged.disease_hpo_sources.update(rp.disease_hpo_sources)
                for p in (op, rp):
                    for hid, row in p.hpos.items():
                        merged.hpos.setdefault(hid, {"hpo_name": row.get("hpo_name", ""), "frequency_raw": set(), "sources": set()})
                        merged.hpos[hid]["frequency_raw"].update(row.get("frequency_raw", set()))
                        merged.hpos[hid]["sources"].update(row.get("sources", set()))
                out.append(merged)
                used_orpha.add(idx)
                matched = True
                break
        if not matched:
            out.append(op)
    for idx, rp in enumerate(orpha_profiles):
        if idx in used_orpha:
            continue
        rp.mondo_id = orpha_to_mondo.get(rp.orpha_id, "")
        out.append(rp)
    return out


def lin_similarity(
    p: str,
    d: str,
    graph: HpoGraph,
    ic: dict[str, float],
    min_similarity: float,
) -> tuple[float, str, str]:
    if p == d:
        return 1.0, p, "exact"
    p_anc = graph.ancestors(p)
    d_anc = graph.ancestors(d)
    common = p_anc & d_anc
    if not common:
        return 0.0, "", "no_match"
    mica = max(common, key=lambda x: ic.get(x, 0.0))
    if mica in BROAD_ANCESTOR_BLACKLIST:
        return 0.0, mica, "no_match"
    denom = ic.get(p, 0.0) + ic.get(d, 0.0)
    sim = 0.0 if denom <= 0 else (2.0 * ic.get(mica, 0.0) / denom)
    if sim < min_similarity:
        return 0.0, mica, "no_match"
    if d in p_anc:
        match_type = "patient_more_specific"
    elif p in d_anc:
        match_type = "disease_more_specific"
    else:
        match_type = "semantic_related"
    return sim, mica, match_type


def score_disease(
    patient_hpos: list[str],
    profile: DiseaseProfile,
    graph: HpoGraph,
    ic: dict[str, float],
    min_similarity: float,
) -> tuple[float, list[dict[str, Any]]]:
    if not patient_hpos:
        return 0.0, []
    denom = sum(ic.get(h, 0.0) for h in patient_hpos)
    if denom <= 0:
        denom = float(len(patient_hpos))
    evidence: list[dict[str, Any]] = []
    total = 0.0
    disease_hpos = list(profile.hpos)
    for p in patient_hpos:
        best = {
            "patient_hpo_id": p,
            "patient_hpo_name": graph.name(p),
            "patient_hpo_ic": ic.get(p, 0.0),
            "best_matched_disease_hpo_id": "",
            "best_matched_disease_hpo_name": "",
            "similarity": 0.0,
            "match_type": "none",
            "mica_hpo_id": "",
            "mica_hpo_name": "",
            "mica_ic": 0.0,
            "contribution": 0.0,
        }
        for d in disease_hpos:
            sim, mica, match_type = lin_similarity(p, d, graph, ic, min_similarity)
            if sim > best["similarity"]:
                best.update(
                    {
                        "best_matched_disease_hpo_id": d,
                        "best_matched_disease_hpo_name": graph.name(d) or profile.hpos[d].get("hpo_name", ""),
                        "similarity": sim,
                        "match_type": match_type,
                        "mica_hpo_id": mica,
                        "mica_hpo_name": graph.name(mica) if mica else "",
                        "mica_ic": ic.get(mica, 0.0) if mica else 0.0,
                    }
                )
        best["contribution"] = ic.get(p, 0.0) * best["similarity"]
        total += best["contribution"]
        evidence.append(best)
    return total / denom, evidence


def conclusion_code(score: float | None, no_model: bool, no_hpo: bool, no_gene: bool = False) -> str:
    if no_gene:
        return "NO_GENE_ANNOTATION"
    if no_hpo:
        return "NO_VALID_SCORING_HPO"
    if no_model:
        return "NO_GENE_DISEASE_MODEL"
    if score is None:
        return "PHENOTYPE_MATCH_NONE"
    if score >= 0.80:
        return "PHENOTYPE_MATCH_STRONG"
    if score >= 0.50:
        return "PHENOTYPE_MATCH_MODERATE"
    if score >= 0.20:
        return "PHENOTYPE_MATCH_WEAK"
    return "PHENOTYPE_MATCH_NONE"


def join_set(values: set[str] | list[str]) -> str:
    return ";".join(sorted(v for v in values if v))


def serialize_freq(row: dict[str, Any]) -> str:
    vals = row.get("frequency_raw", set())
    if isinstance(vals, set):
        return ";".join(sorted(v for v in vals if v))
    return str(vals or "")


def best_term_summary(evidence: list[dict[str, Any]], limit: int | None = None) -> str:
    parts = []
    rows = evidence if limit is None else evidence[:limit]
    for e in rows:
        parts.append(f"{e['patient_hpo_id']}->{e.get('best_matched_disease_hpo_id','')}:{e.get('similarity',0):.3f}")
    return ";".join(parts)


def main() -> None:
    run_started = time.perf_counter()
    args = parse_args()
    paths = load_paths(args.config)
    args.input_csv = resolve_project_path(args.input_csv) if args.input_csv else paths.default_input_csv
    args.hpo_file = resolve_project_path(args.hpo_file) if args.hpo_file else paths.default_hpo_file
    args.outdir = resolve_project_path(args.outdir) if args.outdir else paths.runtime_root / "results"
    hp_obo = paths.hpo_ontology
    hpoa = paths.hpo_annotations
    hgnc = paths.hgnc_symbols
    genes_to_disease = paths.gene_disease_associations
    omim_db = paths.omim_database
    orpha_yaml_dir = paths.orphanet_packets / "orphapacket" / "yaml"
    mondo_obo = paths.mondo_ontology
    orpha_index = resolve_project_path(args.orpha_index) if args.orpha_index else paths.orphanet_index
    args.outdir.mkdir(parents=True, exist_ok=True)

    step_started = time.perf_counter()
    log("[1/9] Loading HPO ontology")
    graph = HpoGraph(hp_obo)
    log(f"      HPO terms loaded: {len(graph.terms)} ({elapsed_since(step_started)})")

    step_started = time.perf_counter()
    log("[2/9] Loading patient HPO")
    hpo_qc, patient_hpos = load_patient_hpos(args.hpo_file, graph)
    log(f"      Patient HPO loaded: input={len(hpo_qc)}, scoring={len(patient_hpos)} ({elapsed_since(step_started)})")

    step_started = time.perf_counter()
    log("[3/9] Loading HPOA and computing IC")
    hpoa_disease_hpos, disease_positive_hpos = load_hpoa(hpoa, graph)
    ic = compute_ic(graph, disease_positive_hpos)
    log(
        "      HPOA loaded and IC computed: "
        f"diseases={len(hpoa_disease_hpos)}, positive_profiles={len(disease_positive_hpos)} ({elapsed_since(step_started)})"
    )

    step_started = time.perf_counter()
    log("[4/9] Loading HGNC aliases")
    alias_index, approved_index = load_hgnc_aliases(hgnc)
    log(f"      HGNC aliases loaded: aliases={len(alias_index)}, approved_symbols={len(approved_index)} ({elapsed_since(step_started)})")

    step_started = time.perf_counter()
    log("[5/9] Reading variant CSV and candidate genes")
    candidate_genes, candidate_variant_counts, variant_rows = scan_input_genes(
        args.input_csv,
        args.input_format,
        args.chunksize,
        alias_index,
    )
    log(f"      Variant rows={variant_rows}, candidate genes={len(candidate_genes)} ({elapsed_since(step_started)})")

    step_started = time.perf_counter()
    log("[6/9] Loading OMIM branch")
    g2d = load_genes_to_disease(genes_to_disease, alias_index)
    omim_sql = query_omim_sqlite(omim_db, candidate_genes, alias_index)
    log(
        "      OMIM branch loaded: "
        f"genes_to_disease_genes={len(g2d)}, sqlite_hit_genes={len(omim_sql)}, "
        f"sqlite_records={sum(len(v) for v in omim_sql.values())} ({elapsed_since(step_started)})"
    )

    step_started = time.perf_counter()
    log("[7/9] Loading ORPHA branch")
    orpha_by_gene, orpha_to_omim_gene_refs = load_orphapackets(
        orpha_yaml_dir,
        candidate_genes,
        alias_index,
        args.max_orpha_files,
        log_progress=True,
        index_path=orpha_index,
        rebuild_index=args.rebuild_orpha_index,
    )
    log(
        "      ORPHA branch loaded: "
        f"matched_genes={len(orpha_by_gene)}, orpha_omim_ref_diseases={len(orpha_to_omim_gene_refs)} ({elapsed_since(step_started)})"
    )

    step_started = time.perf_counter()
    log("[8/9] Loading MONDO xrefs")
    omim_to_mondo, orpha_to_mondo, mondo_names = load_mondo_xrefs(mondo_obo)
    log(
        "      MONDO xrefs loaded: "
        f"omim={len(omim_to_mondo)}, orpha={len(orpha_to_mondo)}, names={len(mondo_names)} ({elapsed_since(step_started)})"
    )

    step_started = time.perf_counter()
    log("[9/9] Scoring genes")
    gene_rows: list[dict[str, Any]] = []
    gene_result_by_gene: dict[str, dict[str, Any]] = {}
    candidate_gene_list = sorted(candidate_genes)
    for gene_idx, gene in enumerate(candidate_gene_list, 1):
        if gene_idx % 100 == 0 or gene_idx == len(candidate_gene_list):
            log(f"      Scoring gene progress: {gene_idx}/{len(candidate_gene_list)}")
        omim_profiles: list[DiseaseProfile] = []
        seen_omim: set[str] = set()
        for item in g2d.get(gene, []):
            omim_id = item["omim_id"]
            if omim_id in seen_omim:
                continue
            prof = profile_from_omim(gene, omim_id, hpoa_disease_hpos, source=item.get("source", "genes_to_disease"), association_type=item.get("association_type", ""))
            if prof:
                omim_profiles.append(prof)
                seen_omim.add(omim_id)
        for item in omim_sql.get(gene, []):
            omim_id = item["omim_id"]
            if omim_id in seen_omim:
                continue
            prof = profile_from_omim(gene, omim_id, hpoa_disease_hpos, omim_name=item.get("disease_name", ""), source=item.get("source", "omim_sqlite"))
            if prof:
                omim_profiles.append(prof)
                seen_omim.add(omim_id)

        orpha_profiles = orpha_by_gene.get(gene, [])
        profiles = reconcile_profiles(omim_profiles, orpha_profiles, omim_to_mondo, orpha_to_mondo)

        if not patient_hpos:
            row = {
                "gene_symbol": gene,
                "gene_score": "",
                "conclusion_code": conclusion_code(None, False, True),
                "warning": "no_valid_scoring_hpo",
            }
            gene_result_by_gene[gene] = row
            continue
        if not profiles:
            row = {
                "gene_symbol": gene,
                "hgnc_id": approved_index.get(gene.upper(), {}).get("hgnc_id", ""),
                "gene_score": "",
                "conclusion_code": conclusion_code(None, True, False),
                "best_disease_score": "",
                "best_disease_name": "",
                "best_omim_id": "",
                "best_orpha_id": "",
                "best_mondo_id": "",
                "best_disease_source_dbs": "",
                "best_disease_match_status": "",
                "mapping_basis": "",
                "second_best_disease_score": "",
                "score_gap_to_second_best": "",
                "disease_profile_count": 0,
                "input_hpo_count": len(hpo_qc),
                "scoring_hpo_count": len(patient_hpos),
                "matched_hpo_count": 0,
                "unmatched_hpo_count": len(patient_hpos),
                "mean_input_hpo_ic": sum(ic.get(h, 0.0) for h in patient_hpos) / max(len(patient_hpos), 1),
                "candidate_variant_count_in_gene": 0,
                "gene_sources": "annotated_gene",
                "best_term_evidence_summary": "",
                "db_versions": "HPO:2026-02-16;HPOA:2026-02-16;MONDO:2026-05-05;OMIM:2025-04-11",
                "warning": "no_gene_disease_model",
            }
            gene_result_by_gene[gene] = row
            gene_rows.append(row)
            continue

        scored: list[tuple[float, DiseaseProfile, list[dict[str, Any]]]] = []
        for prof in profiles:
            score, evidence = score_disease(patient_hpos, prof, graph, ic, args.min_similarity)
            scored.append((score, prof, evidence))
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_prof, best_evidence = scored[0]
        second = scored[1][0] if len(scored) > 1 else None
        matched_count = sum(1 for e in best_evidence if e.get("similarity", 0.0) >= args.min_similarity)
        row = {
            "gene_symbol": gene,
            "hgnc_id": approved_index.get(gene.upper(), {}).get("hgnc_id", ""),
            "gene_score": f"{best_score:.6f}",
            "conclusion_code": conclusion_code(best_score, False, False),
            "best_disease_score": f"{best_score:.6f}",
            "best_disease_name": best_prof.disease_name,
            "best_omim_id": best_prof.omim_id,
            "best_orpha_id": best_prof.orpha_id,
            "best_mondo_id": best_prof.mondo_id,
            "best_disease_source_dbs": join_set(best_prof.source_dbs),
            "best_disease_match_status": best_prof.disease_match_status,
            "mapping_basis": best_prof.mapping_basis,
            "second_best_disease_score": "" if second is None else f"{second:.6f}",
            "score_gap_to_second_best": "" if second is None else f"{best_score - second:.6f}",
            "disease_profile_count": len(profiles),
            "input_hpo_count": len(hpo_qc),
            "scoring_hpo_count": len(patient_hpos),
            "matched_hpo_count": matched_count,
            "unmatched_hpo_count": len(patient_hpos) - matched_count,
            "mean_input_hpo_ic": f"{sum(ic.get(h, 0.0) for h in patient_hpos) / max(len(patient_hpos), 1):.6f}",
            "candidate_variant_count_in_gene": 0,
            "gene_sources": "annotated_gene",
            "best_term_evidence_summary": best_term_summary(best_evidence),
            "db_versions": "HPO:2026-02-16;HPOA:2026-02-16;MONDO:2026-05-05;OMIM:2025-04-11",
            "warning": "",
        }
        gene_result_by_gene[gene] = row
        gene_rows.append(row)
    log(f"      Gene scoring completed: output_genes={len(gene_rows)} ({elapsed_since(step_started)})")

    step_started = time.perf_counter()
    log("[post] Building variant-level output")
    for row in gene_rows:
        row["candidate_variant_count_in_gene"] = candidate_variant_counts.get(row["gene_symbol"], 0)

    gene_rows.sort(key=lambda r: (float(r["gene_score"]) if r.get("gene_score") not in {"", None} else -1.0), reverse=True)
    for i, row in enumerate(gene_rows, 1):
        row["sample_id"] = args.hpo_file.stem
        row["gene_rank"] = i

    gene_out = args.outdir / "gene_phenotype_score.csv"
    pd.DataFrame(gene_rows).to_csv(gene_out, index=False)

    rank_by_gene = {r["gene_symbol"]: r["gene_rank"] for r in gene_rows}
    # Variant-level output: preserve input rows and align by gene_symbol.
    variant_out = args.outdir / "variant_phenotype_score.csv"
    wrote_variant_header = False
    written_variant_rows = 0
    for chunk in iter_variant_chunks(args.input_csv, args.input_format, args.chunksize):
        df = prepare_variant_chunk(chunk)
        append_rows: list[dict[str, Any]] = []
        for _, row in df.iterrows():
            raw_gene = str(row.get("gene_symbol", "")).strip()
            gene, hgnc_id, norm_status = normalize_gene(raw_gene, alias_index)
            result = gene_result_by_gene.get(gene)
            no_gene = not raw_gene or raw_gene in {"-", "."}
            if no_gene or not gene:
                result = None
                code = conclusion_code(None, False, False, no_gene=True)
            elif result is None:
                code = conclusion_code(None, True, False)
            else:
                code = result.get("conclusion_code", "")
            append_rows.append(
                {
                    "sample_id": args.hpo_file.stem,
                    "variant_id": row.get("_variant_id_v2", ""),
                    "gene_symbol_raw": raw_gene,
                    "gene_symbol_normalized": gene,
                    "hgnc_id_v2": hgnc_id,
                    "gene_source": "no_gene_annotation" if no_gene else "annotated_gene",
                    "gene_score": "" if result is None else result.get("gene_score", ""),
                    "gene_rank": "" if result is None else rank_by_gene.get(gene, ""),
                    "conclusion_code": code,
                    "best_disease_score": "" if result is None else result.get("best_disease_score", ""),
                    "best_disease_name": "" if result is None else result.get("best_disease_name", ""),
                    "best_omim_id": "" if result is None else result.get("best_omim_id", ""),
                    "best_orpha_id": "" if result is None else result.get("best_orpha_id", ""),
                    "best_mondo_id": "" if result is None else result.get("best_mondo_id", ""),
                    "best_disease_source_dbs": "" if result is None else result.get("best_disease_source_dbs", ""),
                    "matched_hpo_count": "" if result is None else result.get("matched_hpo_count", ""),
                    "unmatched_hpo_count": "" if result is None else result.get("unmatched_hpo_count", ""),
                    "phenotype_score_reused": True if result is not None else "",
                    "phenotype_score_source_gene": gene if result is not None else "",
                    "warning": "no_gene_annotation" if no_gene else ("" if result is not None else "no_gene_disease_model"),
                }
            )
        append_df = pd.DataFrame(append_rows)
        base_df = df.drop(columns=["_variant_id_v2"]).reset_index(drop=True)
        variant_df = pd.concat([base_df, append_df.reset_index(drop=True)], axis=1)
        variant_df.to_csv(variant_out, index=False, mode="a" if wrote_variant_header else "w", header=not wrote_variant_header)
        wrote_variant_header = True
        written_variant_rows += len(variant_df)
    log(f"      Output files written: gene_rows={len(gene_rows)}, variant_rows={written_variant_rows} ({elapsed_since(step_started)})")

    summary = {
        "input_csv": display_path(args.input_csv),
        "hpo_file": display_path(args.hpo_file),
        "candidate_genes": len(candidate_genes),
        "scored_genes": sum(1 for r in gene_rows if r.get("gene_score")),
        "variant_rows": variant_rows,
        "gene_output": display_path(gene_out),
        "variant_output": display_path(variant_out),
        "min_similarity": args.min_similarity,
    }
    (args.outdir / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    log(f"[done] Run completed ({elapsed_since(run_started)})")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
