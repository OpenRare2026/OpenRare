#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
罕见病双轴 PPI 评分框架
========================
疾病轴 (Disease Anchor, D) + 组织核心轴 (Tissue Core Anchor, T)

输入：HGNC 标准化后的候选基因列表 + 患者 HPO ID 列表
输出：每个候选基因的 PPI 综合评分 + 互作最强的 Top 25 邻居基因列表

"""

import os
import json
import pickle
import hashlib
import re
import argparse
import sys
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import networkx as nx
from collections import Counter, defaultdict
from typing import Any, List, Dict, Set, Tuple, Optional
from config import Config, RunParameters, config_from_run_parameters, validate_run_parameters


# OWL 解析入口：把 OWL（网络本体语言） 文件从磁盘上的文本变成内存中的对象/图结构
try:
    from owlready2 import get_ontology
    HAS_OWLREADY = True
except ImportError:
    HAS_OWLREADY = False


CACHE_VERSION = "rare_ppi_cache_v2"


def log(message: str = ""):
    print(message, file=sys.stderr)


def _ensure_cache_dir(cfg: Config) -> str:
    cache_dir = getattr(cfg, "CACHE_DIR", os.path.join(cfg.DATA_DIR, "cache"))
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _file_signature(paths: List[str]) -> Dict[str, Dict[str, Any]]:
    signature = {}
    for path in paths:
        if not path:
            continue
        if os.path.exists(path):
            stat = os.stat(path)
            signature[path] = {"mtime": stat.st_mtime, "size": stat.st_size}
        else:
            signature[path] = None
    return signature


def _cache_signature(paths: List[str], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "version": CACHE_VERSION,
        "files": _file_signature(paths),
        "params": params or {},
    }


def _safe_cache_name(prefix: str, data: Any) -> str:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True, default=str)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _load_pickle_cache(path: str, signature: Dict[str, Any]) -> Optional[Any]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as handle:
            payload = pickle.load(handle)
        if payload.get("signature") == signature:
            return payload.get("data")
    except Exception as exc:
        log(f"[缓存警告] 读取失败，忽略 {path}: {exc}")
    return None


def _save_pickle_cache(path: str, signature: Dict[str, Any], data: Any):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "wb") as handle:
            pickle.dump({"signature": signature, "data": data}, handle, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, path)
    except Exception as exc:
        log(f"[缓存警告] 写入失败，忽略 {path}: {exc}")


def _load_json_cache(path: str, signature: Dict[str, Any]) -> Optional[Any]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
        if payload.get("signature") == signature:
            return payload.get("data")
    except Exception as exc:
        log(f"[缓存警告] 读取失败，忽略 {path}: {exc}")
    return None


def _save_json_cache(path: str, signature: Dict[str, Any], data: Any):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump({"signature": signature, "data": data}, handle, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception as exc:
        log(f"[缓存警告] 写入失败，忽略 {path}: {exc}")


def _clean_str(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _unique_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _split_multi_value(value: Any) -> List[str]:
    text = _clean_str(value)
    if not text:
        return []
    return [x.strip() for x in re.split(r"[;,|]\s*", text) if x.strip()]


def normalize_hpo_ids(hpo_ids: List[str], deduplicate: bool = True) -> List[str]:
    normalized = []
    for raw in hpo_ids or []:
        text = _clean_str(raw).upper().replace("_", ":")
        if not text:
            continue
        if re.fullmatch(r"\d{1,7}", text):
            text = f"HP:{int(text):07d}"
        match = re.search(r"HP:\d{7}", text)
        if match:
            normalized.append(match.group(0))
    return _unique_preserve_order(normalized) if deduplicate else normalized


def coarse_tissue_name(name: str) -> Optional[str]:
    """Map free text to a supported coarse tissue; unknown phenotype words return None."""
    text = _clean_str(name).lower().replace("_", " ")
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

# ========================= 1. ID 标准化模块 =========================

class IDStandardizer:
    """
    负责将 VEP 输出的基因 SYMBOL 统一标准化，并建立 Symbol → Ensembl Protein → STRING ID 的映射。
    这是后续所有数据库对接的基石，别名不匹配是罕见病分析中最常见的沉默错误。
    """
    
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.symbol_to_ensp = {}   # HGNC Symbol -> Ensembl Protein ID
        self.ensembl_gene_to_symbol = {}  # Ensembl Gene ID -> HGNC Symbol
        self.ensp_to_string = {}   # Ensembl Protein ID -> STRING Protein ID (e.g., 9606.ENSP000003...)
        self.ensp_to_symbol = {}   # Ensembl Protein ID -> HGNC Symbol
        self.string_id_to_symbol = {}  # STRING Protein ID -> HGNC Symbol
        self.symbol_to_string_ids = defaultdict(list)  # HGNC Symbol -> [STRING Protein ID]
        self.alias_to_official = {}  # 别名 -> 官方 Symbol
        
    def load(self):
        """顺序加载 HGNC、BioMart、UniProt、STRING info，建立完整映射链。"""
        cache_paths = [
            self.cfg.PATH_HGNC,
            self.cfg.PATH_ENSEMBL_BIOMART,
            self.cfg.PATH_UNIPROT_MAPPING,
            self.cfg.PATH_STRING_INFO,
        ]
        signature = _cache_signature(cache_paths, {"id_strategy": "official_symbol_precedence_v2"})
        cache_path = os.path.join(_ensure_cache_dir(self.cfg), "id_standardizer.pkl")
        cached = _load_pickle_cache(cache_path, signature)
        if cached:
            for name, value in cached.items():
                setattr(self, name, value)
            self.symbol_to_string_ids = defaultdict(list, self.symbol_to_string_ids)
            log(f"[ID] 使用缓存: {cache_path}")
            return

        self._load_hgnc()
        self._load_biomart()
        self._load_uniprot()
        self._load_string_info()
        _save_pickle_cache(cache_path, signature, {
            "symbol_to_ensp": self.symbol_to_ensp,
            "ensembl_gene_to_symbol": self.ensembl_gene_to_symbol,
            "ensp_to_string": self.ensp_to_string,
            "ensp_to_symbol": self.ensp_to_symbol,
            "string_id_to_symbol": self.string_id_to_symbol,
            "symbol_to_string_ids": dict(self.symbol_to_string_ids),
            "alias_to_official": self.alias_to_official,
        })
        log(f"[ID] 映射链建立完成: {len(self.symbol_to_ensp)} symbols -> ENSP -> STRING")
        
    def _load_hgnc(self):
        """HGNC 官方文件：提取 approved symbol 与 alias 的对应关系。"""
        if not os.path.exists(self.cfg.PATH_HGNC):
            log(f"[警告] 未找到 HGNC 文件: {self.cfg.PATH_HGNC}")
            return
        df = pd.read_csv(self.cfg.PATH_HGNC, sep="\t", low_memory=False)
        approved_symbols = set()
        for _, row in df.iterrows():
            official = _clean_str(row.get("symbol"))
            if not official:
                continue
            approved_symbols.add(official)
            self.alias_to_official[official] = official
            ensg = _clean_str(row.get("ensembl_gene_id"))
            if ensg:
                self.ensembl_gene_to_symbol[ensg] = official

        for _, row in df.iterrows():
            official = _clean_str(row.get("symbol"))
            if not official:
                continue
            # 处理别名字段（可能以逗号或竖线分隔）。approved symbol 永远优先，避免
            # RAI1/SMO/TCF4 等合法基因名被其它基因的 alias 覆盖。
            aliases = str(row.get("alias_symbol", "")).replace("|", ",")
            prev_symbols = str(row.get("prev_symbol", "")).replace("|", ",")
            for a in aliases.split(","):
                a = a.strip()
                if a and a not in approved_symbols:
                    self.alias_to_official[a] = official
            for p in prev_symbols.split(","):
                p = p.strip()
                if p and p not in approved_symbols:
                    self.alias_to_official[p] = official
                    
    def _load_biomart(self):
        """Ensembl BioMart 导出：Symbol -> Ensembl Gene ID -> Ensembl Protein ID。"""
        if not os.path.exists(self.cfg.PATH_ENSEMBL_BIOMART):
            return
        df = pd.read_csv(self.cfg.PATH_ENSEMBL_BIOMART, sep="\t", low_memory=False)
        # 兼容 BioMart 的 external_gene_name/HGNC symbol 两套列名。
        for _, row in df.iterrows():
            sym = _clean_str(row.get("Gene name", row.get("HGNC symbol", row.get("HGNC Symbol", ""))))
            ensg = _clean_str(row.get("Gene stable ID", row.get("Ensembl Gene ID", row.get("Ensembl gene ID", ""))))
            ensp = _clean_str(row.get("Protein stable ID"))
            if sym and ensp and sym in self.alias_to_official:
                official = self.alias_to_official[sym]
                if ensg:
                    self.ensembl_gene_to_symbol[ensg] = official
                self.symbol_to_ensp[official] = ensp
                
    def _load_uniprot(self):
        """UniProt ID mapping：用 Ensembl gene/protein 列补充缺失的 ENSP->Symbol 映射。"""
        if not os.path.exists(self.cfg.PATH_UNIPROT_MAPPING):
            return
        try:
            reader = pd.read_csv(
                self.cfg.PATH_UNIPROT_MAPPING,
                sep="\t",
                header=None,
                usecols=[18, 20],  # selected.tab: Ensembl, Ensembl_PRO
                chunksize=200_000,
                low_memory=False,
            )
            for chunk in reader:
                for _, row in chunk.iterrows():
                    ensg_values = _split_multi_value(row.get(18))
                    ensp_values = _split_multi_value(row.get(20))
                    symbol = next((self.ensembl_gene_to_symbol.get(ensg) for ensg in ensg_values if ensg in self.ensembl_gene_to_symbol), None)
                    if not symbol:
                        continue
                    for ensp in ensp_values:
                        if ensp.startswith("ENSP"):
                            self.symbol_to_ensp.setdefault(symbol, ensp)
                            self.ensp_to_symbol.setdefault(ensp, symbol)
        except ValueError as exc:
            log(f"[ID 警告] UniProt mapping 列格式不符合 idmapping_selected.tab，跳过: {exc}")
                    
    def _load_string_info(self):
        """STRING protein.info：建立 STRING protein ID -> HGNC Symbol 映射。"""
        if not os.path.exists(self.cfg.PATH_STRING_INFO):
            return
        df = pd.read_csv(self.cfg.PATH_STRING_INFO, sep="\t", low_memory=False)
        for _, row in df.iterrows():
            string_id = str(row.get("#string_protein_id", row.get("protein_external_id", ""))).strip()
            preferred = str(row.get("preferred_name", "")).strip()
            if not string_id.startswith("9606.") or not preferred:
                continue
            symbol = self.alias_to_official.get(preferred, preferred)
            self.string_id_to_symbol[string_id] = symbol
            self.symbol_to_string_ids[symbol].append(string_id)
            ensp = string_id.split(".", 1)[1]
            if ensp.startswith("ENSP"):
                self.ensp_to_string[ensp] = string_id
                self.ensp_to_symbol[ensp] = symbol
                self.symbol_to_ensp.setdefault(symbol, ensp)
                
    def standardize(self, raw_symbols: List[str]) -> List[str]:
        """将输入的原始 Symbol 列表（可能含别名）转换为 HGNC 官方 Symbol。"""
        official = []
        for s in raw_symbols:
            if s is None or (isinstance(s, float) and pd.isna(s)):
                continue
            s_clean = str(s).strip()
            if not s_clean or s_clean.lower() == "nan":
                continue
            if s_clean in self.alias_to_official:
                official.append(self.alias_to_official[s_clean])
            else:
                official.append(s_clean)  # 未匹配到的保留原样，后续标记
        return _unique_preserve_order(official)
    
    def symbol_to_string_id(self, symbol: str) -> Optional[str]:
        """Symbol -> STRING Protein ID。若任一步断裂，返回 None。"""
        ids = self.symbol_to_string_ids.get(symbol)
        if ids:
            return ids[0]
        ensp = self.symbol_to_ensp.get(symbol)
        if not ensp:
            return None
        return self.ensp_to_string.get(ensp)


# ========================= 2. HPO -> 组织映射模块 =========================

class HPOMapper:
    """
    将患者 HPO ID 收敛到标准解剖组织名。
    先合并 phenotype_to_anatomy.txt direct 映射和 hp-full.owl logical definitions
    中的 UBERON 引用，再按 GPET 策略沿 is_a 祖先链向上寻找最近可用组织。
    """
    TOP_TISSUE_N = 3
    
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.hpo_to_uberon = defaultdict(list)   # HPO ID -> [UBERON ID]
        self.uberon_to_name = {}                 # UBERON ID -> 可读名称
        self.hpo_parents = defaultdict(list)      # HPO ID -> parent HPO IDs
        self.hpo_names = {}
        self._hpo_to_tissues_cache = {}
        self.last_tissue_counts = {}
        self.last_hpo_tissue_map = {}
        
    def load(self):
        hp_full_owl = self._hp_full_owl_path()
        signature = _cache_signature([
            self.cfg.PATH_HPO_UBERON_MAP,
            self.cfg.PATH_UBERON_OBO,
            self.cfg.PATH_HPO_OBO,
            hp_full_owl,
        ], {"hpo_mapper_strategy": "gpet_ancestor_owl_v2"})
        cache_path = os.path.join(_ensure_cache_dir(self.cfg), "hpo_mapper.pkl")
        cached = _load_pickle_cache(cache_path, signature)
        if cached:
            self.hpo_to_uberon = defaultdict(list, cached.get("hpo_to_uberon", {}))
            self.uberon_to_name = cached.get("uberon_to_name", {})
            self.hpo_parents = defaultdict(list, cached.get("hpo_parents", {}))
            self.hpo_names = cached.get("hpo_names", {})
            self._hpo_to_tissues_cache = {}
            log(f"[HPO] 使用缓存: {cache_path}")
            return

        self._load_uberon_names()
        self._load_hpo_parents()
        self._load_hpo_uberon_map()
        self._load_hpo_owl_mappings(hp_full_owl)
        _save_pickle_cache(cache_path, signature, {
            "hpo_to_uberon": dict(self.hpo_to_uberon),
            "uberon_to_name": self.uberon_to_name,
            "hpo_parents": dict(self.hpo_parents),
            "hpo_names": self.hpo_names,
        })
        log(f"[HPO] 映射表加载完成: {len(self.hpo_to_uberon)} HPO terms -> UBERON")

    def _hp_full_owl_path(self) -> str:
        """Optional hp-full.owl path; config.py may not define it in older deployments."""
        return getattr(self.cfg, "PATH_HP_FULL_OWL", os.path.join(self.cfg.DATA_DIR, "hp-full.owl"))

    def _add_hpo_uberon_mapping(self, hpo_id: str, uberon_id: str) -> bool:
        if uberon_id in self.hpo_to_uberon[hpo_id]:
            return False
        self.hpo_to_uberon[hpo_id].append(uberon_id)
        return True
        
    def _load_hpo_uberon_map(self):
        """HPO 官网 phenotype_to_anatomy.txt：提取每行中的 HP:* 与 UBERON:*。"""
        if not os.path.exists(self.cfg.PATH_HPO_UBERON_MAP):
            log(f"[警告] 未找到 HPO-UBERON 映射文件: {self.cfg.PATH_HPO_UBERON_MAP}")
            return
        count = 0
        with open(self.cfg.PATH_HPO_UBERON_MAP, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                normalized_line = line.replace("_", ":")
                hpo_match = re.search(r"HP:\d{7}", normalized_line)
                uberon_match = re.search(r"UBERON:\d{7}", normalized_line)
                hpo_id = hpo_match.group(0) if hpo_match else None
                uberon_id = uberon_match.group(0) if uberon_match else None
                if hpo_id and uberon_id:
                    if self._add_hpo_uberon_mapping(hpo_id, uberon_id):
                        count += 1
        log(f"[HPO] phenotype_to_anatomy direct 映射: {count}")

    def _load_hpo_owl_mappings(self, hp_full_owl: str):
        """从 hp-full.owl logical definitions 补充 HPO -> UBERON 映射。"""
        if not hp_full_owl or not os.path.exists(hp_full_owl):
            log(f"[HPO OWL] 未找到 hp-full.owl，跳过 logical definitions: {hp_full_owl}")
            return
        if HAS_OWLREADY:
            self._parse_owl_with_owlready2(hp_full_owl)
        else:
            log("[HPO OWL] owlready2 未安装，使用正则解析 hp-full.owl logical definitions")
            self._parse_owl_with_regex(hp_full_owl)

    def _parse_owl_with_owlready2(self, hp_full_owl: str):
        log(f"[HPO OWL] 使用 owlready2 解析: {hp_full_owl}")
        onto = get_ontology(f"file://{os.path.abspath(hp_full_owl)}").load()
        count = 0
        for cls in onto.classes():
            iri = str(getattr(cls, "iri", ""))
            if not iri.startswith("http://purl.obolibrary.org/obo/HP_"):
                continue
            hpo_id = "HP:" + iri.rsplit("_", 1)[-1]
            for uberon_id in self._extract_uberon_from_class(cls):
                if self._add_hpo_uberon_mapping(hpo_id, uberon_id):
                    count += 1
        log(f"[HPO OWL] logical definitions 补充映射: {count}")

    def _extract_uberon_from_class(self, cls) -> List[str]:
        uberons = []
        for expr in list(getattr(cls, "equivalent_to", [])) + list(getattr(cls, "is_a", [])):
            uberons.extend(self._extract_uberon_from_expression(expr))
        return _unique_preserve_order(uberons)

    def _extract_uberon_from_expression(self, expr) -> List[str]:
        """递归解析 owlready2 class / restriction / boolean expression 中的 UBERON IRI。"""
        uberons = []
        uberons.extend(self._iri_to_uberon(str(getattr(expr, "iri", ""))))
        for attr in ("Classes", "entities", "operands"):
            for sub in list(getattr(expr, attr, []) or []):
                uberons.extend(self._extract_uberon_from_expression(sub))
        for attr in ("Class", "value", "property"):
            sub = getattr(expr, attr, None)
            if sub is not None:
                uberons.extend(self._extract_uberon_from_expression(sub))
        return _unique_preserve_order(uberons)

    def _iri_to_uberon(self, iri: str) -> List[str]:
        match = re.search(r"UBERON[_:](\d+)", iri)
        if not match:
            return []
        return [f"UBERON:{int(match.group(1)):07d}"]

    def _parse_owl_with_regex(self, hp_full_owl: str):
        log(f"[HPO OWL] 使用正则解析: {hp_full_owl}")
        with open(hp_full_owl, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        pattern = re.compile(
            r'<owl:Class[^>]*rdf:about="http://purl\.obolibrary\.org/obo/HP_(\d+)"[^>]*>'
            r"(.*?)"
            r"</owl:Class>",
            re.DOTALL,
        )
        count = 0
        for match in pattern.finditer(content):
            hpo_id = f"HP:{int(match.group(1)):07d}"
            for uberon_match in re.finditer(r"UBERON[_:](\d+)", match.group(2)):
                uberon_id = f"UBERON:{int(uberon_match.group(1)):07d}"
                if self._add_hpo_uberon_mapping(hpo_id, uberon_id):
                    count += 1
        log(f"[HPO OWL] logical definitions 补充映射: {count}")
                    
    def _load_uberon_names(self):
        """从 uberon.obo 提取 UBERON ID -> 可读名称（如 'retina'）。"""
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
            "UBERON:0000970": "eye",  # 泛眼
        }
        self.uberon_to_name.update(fallback)
        if not os.path.exists(self.cfg.PATH_UBERON_OBO):
            return

        current_id = None
        with open(self.cfg.PATH_UBERON_OBO, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line == "[Term]":
                    current_id = None
                elif line.startswith("id: UBERON:"):
                    current_id = line.split("id:", 1)[1].strip()
                elif current_id and line.startswith("name: "):
                    self.uberon_to_name[current_id] = line.split("name:", 1)[1].strip().lower()
    
    def _load_hpo_parents(self):
        """从 hp.obo 解析 HPO 名称和 is_a 父节点，作为祖先遍历基础。"""
        if not os.path.exists(self.cfg.PATH_HPO_OBO):
            return
        current_id = None
        with open(self.cfg.PATH_HPO_OBO, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line == "[Term]":
                    current_id = None
                elif line.startswith("id: HP:"):
                    current_id = line.split("id:", 1)[1].strip()
                elif current_id and line.startswith("name: "):
                    self.hpo_names[current_id] = line.split("name:", 1)[1].strip()
                elif current_id and line.startswith("is_a: HP:"):
                    parent = line.split("is_a:", 1)[1].split()[0].strip()
                    self.hpo_parents[current_id].append(parent)
        
    def map(self, hpo_ids: List[str]) -> List[str]:
        """
        输入：患者 HPO ID 列表（如 ["HP:0000488", "HP:0000505"]）
        输出：按 HPO 映射次数排序后的 Top 3 目标组织名称列表。
        """
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
                log(f"[HPO 映射提示] {hpo} 无可用组织映射；仍保留用于 D 轴表型/疾病匹配")

        ranked_tissues = sorted(
            tissue_counts,
            key=lambda tissue: (-tissue_counts[tissue], first_seen_order[tissue], tissue),
        )
        top_n = max(int(getattr(self.cfg, "TOP_TISSUE_N", self.TOP_TISSUE_N)), 0)
        top_tissues = ranked_tissues[:top_n]
        self.last_tissue_counts = {tissue: int(tissue_counts[tissue]) for tissue in ranked_tissues}
        self.last_hpo_tissue_map = hpo_tissue_map
        if self.last_tissue_counts:
            log(
                "[HPO] 组织映射计数 Top3: "
                + ", ".join(f"{tissue}={self.last_tissue_counts[tissue]}" for tissue in top_tissues)
            )
        return top_tissues

    def _resolve_hpo_to_tissues(self, hpo_id: str) -> List[str]:
        """沿 is_a 祖先链向上查找首个可映射到 UBERON/组织的 HPO。"""
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

            for uberon_id in self.hpo_to_uberon.get(current, []):
                tissue = coarse_tissue_name(self.uberon_to_name.get(uberon_id, uberon_id))
                if tissue:
                    tissues.append(tissue)
            if tissues:
                break

            fallback_tissue = self._infer_tissue_from_hpo_name(current)
            if fallback_tissue and fallback_tissue not in fallback_tissues:
                fallback_tissues.append(fallback_tissue)

            queue.extend(self.hpo_parents.get(current, []))

        resolved = _unique_preserve_order(tissues or fallback_tissues)
        self._hpo_to_tissues_cache[hpo_id] = resolved
        return resolved
    
    def _infer_tissue_from_hpo_name(self, hpo: str) -> Optional[str]:
        """Fallback only when the HPO name contains a supported coarse tissue keyword."""
        name = self.hpo_names.get(hpo, "").lower()
        return coarse_tissue_name(name)
    
    def get_broader_hpos(self, hpo_ids: List[str], levels: int = 2) -> List[str]:
        """
        当 HPO 无法映射到组织，或 D 集为空时，上溯 HPO 父节点以扩大检索范围。
        需要 hp.obo 文件解析 is_a 关系。
        """
        broader = set()
        frontier = set(hpo_ids)
        for _ in range(levels):
            next_frontier = set()
            for hpo in frontier:
                for parent in self.hpo_parents.get(hpo, []):
                    if parent not in broader:
                        broader.add(parent)
                        next_frontier.add(parent)
            frontier = next_frontier
            if not frontier:
                break
        return list(broader)


# ========================= 3. D 集构建模块（疾病轴） =========================

class DiseaseModuleBuilder:
    """
    整合 OMIM / Orphanet / ClinVar / PanelApp 构建疾病基因集 D。
    采用按来源独立性加权的证据分过滤噪音，并包含罕见病场景下的三级降级策略。
    """
    
    def __init__(self, cfg: Config, id_std: IDStandardizer):
        self.cfg = cfg
        self.id_std = id_std
        self.omim_cache = {}      # HPO -> genes
        self.orpha_cache = {}     # HPO -> genes
        self.clinvar_cache = {}   # HPO -> genes
        self.panelapp_cache = {}  # HPO -> genes
        self.hpo_names = {}
        self.hpo_gene_cache = defaultdict(list)  # HPO -> genes_to_phenotype genes
        
    def load(self):
        signature = _cache_signature([
            self.cfg.PATH_HPO_GENES,
            self.cfg.PATH_HPO_ANNOTATION,
            self.cfg.PATH_OMIM_GENEMAP,
            self.cfg.PATH_OMIM_MIM2GENE,
            self.cfg.PATH_ORPHANET,
            self.cfg.PATH_CLINVAR,
            self.cfg.PATH_PANELAPP,
            self.cfg.PATH_HPO_OBO,
        ], {"load_clinvar": bool(self.cfg.LOAD_CLINVAR)})
        cache_path = os.path.join(_ensure_cache_dir(self.cfg), "disease_sources.pkl")
        cached = _load_pickle_cache(cache_path, signature)
        if cached:
            self.omim_cache = cached.get("omim_cache", {})
            self.orpha_cache = cached.get("orpha_cache", {})
            self.clinvar_cache = cached.get("clinvar_cache", {})
            self.panelapp_cache = cached.get("panelapp_cache", {})
            self.hpo_gene_cache = defaultdict(list, cached.get("hpo_gene_cache", {}))
            log(f"[Disease] 使用缓存: {cache_path}")
            return

        self._load_omim()
        self._load_orphanet()
        self._load_clinvar()
        self._load_panelapp()
        _save_pickle_cache(cache_path, signature, {
            "omim_cache": self.omim_cache,
            "orpha_cache": self.orpha_cache,
            "clinvar_cache": self.clinvar_cache,
            "panelapp_cache": self.panelapp_cache,
            "hpo_gene_cache": dict(self.hpo_gene_cache),
        })
        log("[Disease] 疾病数据库加载完成")
        
    def _load_omim(self):
        """加载 HPO genes_to_phenotype，并用 phenotype.hpoa + genemap2 补充 OMIM 表型 MIM->gene。"""
        if os.path.exists(self.cfg.PATH_HPO_GENES):
            df = pd.read_csv(self.cfg.PATH_HPO_GENES, sep="\t", comment="#", low_memory=False)
            lower_cols = {c.lower(): c for c in df.columns}
            hpo_col = next((c for k, c in lower_cols.items() if "hpo" in k and "id" in k), None)
            gene_col = next((c for k, c in lower_cols.items() if "symbol" in k or ("gene" in k and "id" not in k)), None)
            if hpo_col is None:
                hpo_col = df.columns[2] if len(df.columns) > 2 else None
            if gene_col is None:
                gene_col = df.columns[1] if len(df.columns) > 1 else None
            if hpo_col is None or gene_col is None:
                log(f"[Disease 警告] 无法识别 HPO genes 文件列: {list(df.columns)}")
            else:
                for _, row in df[[hpo_col, gene_col]].dropna().iterrows():
                    hpo = _clean_str(row[hpo_col])
                    gene = _clean_str(row[gene_col])
                    if hpo.startswith("HP:") and gene:
                        self.hpo_gene_cache[hpo].append(gene)

        if not os.path.exists(self.cfg.PATH_HPO_ANNOTATION):
            return

        phenotype_mim_to_genes = self._load_genemap2_phenotype_genes()
        mim_to_genes_fallback = self._load_mim2gene_fallback()
        if not phenotype_mim_to_genes and mim_to_genes_fallback:
            log("[Disease 警告] genemap2 未提供 OMIM 表型映射，临时回退到 mim2gene；可能混淆表型 MIM 与基因 MIM")

        hpoa_cols = ["database_id", "disease_name", "qualifier", "hpo_id", "reference", "evidence", "onset", "frequency", "sex", "modifier", "aspect", "biocuration"]
        hpoa = pd.read_csv(self.cfg.PATH_HPO_ANNOTATION, sep="\t", comment="#", header=None, names=hpoa_cols, low_memory=False)
        for _, row in hpoa[["database_id", "hpo_id"]].dropna().iterrows():
            database_id = _clean_str(row["database_id"])
            hpo = _clean_str(row["hpo_id"])
            if not (database_id.startswith("OMIM:") and hpo.startswith("HP:")):
                continue
            mim = database_id.split(":", 1)[1]
            genes = phenotype_mim_to_genes.get(mim)
            if not genes:
                genes = mim_to_genes_fallback.get(mim, set())
            self.omim_cache.setdefault(hpo, []).extend(sorted(genes))

    def _load_genemap2_phenotype_genes(self) -> Dict[str, Set[str]]:
        """从 genemap2 的 Phenotypes 列解析 phenotype MIM -> approved gene symbol。"""
        phenotype_mim_to_genes = defaultdict(set)
        if not os.path.exists(self.cfg.PATH_OMIM_GENEMAP):
            return phenotype_mim_to_genes

        genemap_cols = [
            "Chromosome", "Genomic Position Start", "Genomic Position End",
            "Cyto Location", "Computed Cyto Location", "Mim Number",
            "Gene Symbols", "Gene Name", "Approved Symbol", "Entrez Gene ID",
            "Ensembl Gene ID", "Comments", "Phenotypes", "Mouse Gene Symbol/ID",
        ]
        try:
            genemap = pd.read_csv(
                self.cfg.PATH_OMIM_GENEMAP,
                sep="\t",
                comment="#",
                header=None,
                names=genemap_cols,
                dtype=str,
                low_memory=False,
            )
        except Exception as exc:
            log(f"[Disease 警告] genemap2 解析失败，跳过 OMIM 表型映射: {exc}")
            return phenotype_mim_to_genes

        for _, row in genemap.iterrows():
            symbol = self._genemap_gene_symbol(row)
            if not symbol:
                continue
            for mim in self._extract_phenotype_mims(row.get("Phenotypes")):
                phenotype_mim_to_genes[mim].add(symbol)
        return phenotype_mim_to_genes

    @staticmethod
    def _genemap_gene_symbol(row: pd.Series) -> str:
        """优先使用 Approved Symbol；缺失时用 Gene Symbols 的第一个符号兜底。"""
        approved = _clean_str(row.get("Approved Symbol"))
        if approved and approved.lower() != "approved symbol":
            return approved
        gene_symbols = _clean_str(row.get("Gene Symbols"))
        if not gene_symbols or gene_symbols.lower() == "gene symbols":
            return ""
        return next((x.strip() for x in re.split(r"[,;|]", gene_symbols) if x.strip()), "")

    @staticmethod
    def _extract_phenotype_mims(phenotypes: Any) -> Set[str]:
        """提取 genemap2 Phenotypes 字段中的 6 位 phenotype MIM。"""
        text = _clean_str(phenotypes)
        if not text or text.lower() == "phenotypes":
            return set()
        return set(re.findall(r"\b\d{6}\b", text))

    def _load_mim2gene_fallback(self) -> Dict[str, Set[str]]:
        """mim2gene 只作为 genemap2 不可用时的兜底，不作为 OMIM 表型主映射。"""
        mim_to_genes = defaultdict(set)
        if not os.path.exists(self.cfg.PATH_OMIM_MIM2GENE):
            return mim_to_genes
        try:
            mim_df = pd.read_csv(
                self.cfg.PATH_OMIM_MIM2GENE,
                sep="\t",
                comment="#",
                header=None,
                names=["mim", "entry_type", "entrez", "symbol", "ensembl"],
                dtype=str,
                low_memory=False,
            )
        except Exception as exc:
            log(f"[Disease 警告] mim2gene 解析失败，跳过兜底映射: {exc}")
            return mim_to_genes
        for _, row in mim_df.iterrows():
            mim = _clean_str(row.get("mim"))
            symbol = _clean_str(row.get("symbol"))
            if mim and symbol:
                mim_to_genes[mim].add(symbol)
        return mim_to_genes
    
    def _load_orphanet(self):
        """Orphanet en_product6.xml：提取罕见病基因。"""
        if not (os.path.exists(self.cfg.PATH_ORPHANET) and os.path.exists(self.cfg.PATH_HPO_ANNOTATION)):
            return

        orpha_to_genes = defaultdict(set)
        current_orpha = None
        in_gene = False
        try:
            for event, elem in ET.iterparse(self.cfg.PATH_ORPHANET, events=("start", "end")):
                tag = elem.tag.split("}", 1)[-1]
                if event == "start" and tag == "Disorder":
                    current_orpha = None
                elif event == "start" and tag == "Gene":
                    in_gene = True
                elif event == "end" and tag == "OrphaCode" and current_orpha is None:
                    current_orpha = _clean_str(elem.text)
                elif event == "end" and tag == "Symbol" and in_gene and current_orpha:
                    symbol = _clean_str(elem.text)
                    if symbol:
                        orpha_to_genes[current_orpha].add(symbol)
                elif event == "end" and tag == "Gene":
                    in_gene = False
                elif event == "end" and tag == "Disorder":
                    elem.clear()
        except ET.ParseError as exc:
            log(f"[Disease 警告] Orphanet XML 解析失败，跳过: {exc}")
            return

        hpoa_cols = ["database_id", "disease_name", "qualifier", "hpo_id", "reference", "evidence", "onset", "frequency", "sex", "modifier", "aspect", "biocuration"]
        hpoa = pd.read_csv(self.cfg.PATH_HPO_ANNOTATION, sep="\t", comment="#", header=None, names=hpoa_cols, low_memory=False)
        for _, row in hpoa[["database_id", "hpo_id"]].dropna().iterrows():
            database_id = _clean_str(row["database_id"])
            hpo = _clean_str(row["hpo_id"])
            if not (database_id.startswith("ORPHA:") and hpo.startswith("HP:")):
                continue
            orpha_id = database_id.split(":", 1)[1]
            self.orpha_cache.setdefault(hpo, []).extend(sorted(orpha_to_genes.get(orpha_id, [])))
    
    def _load_clinvar(self):
        """ClinVar variant_summary.txt.gz：按 HPO 或疾病名筛选 Pathogenic/LP 变异对应的基因。"""
        if not self.cfg.LOAD_CLINVAR or not os.path.exists(self.cfg.PATH_CLINVAR):
            return
        usecols = ["GeneSymbol", "ClinicalSignificance", "PhenotypeIDS"]
        try:
            reader = pd.read_csv(self.cfg.PATH_CLINVAR, sep="\t", usecols=usecols, chunksize=200_000, low_memory=False)
        except ValueError as exc:
            log(f"[Disease 警告] ClinVar 列格式不符合预期，跳过: {exc}")
            return
        for chunk in reader:
            sig = chunk["ClinicalSignificance"].astype(str)
            chunk = chunk[sig.str.contains("Pathogenic|Likely pathogenic", case=False, na=False)]
            for _, row in chunk.iterrows():
                gene = _clean_str(row.get("GeneSymbol"))
                if not gene:
                    continue
                for hpo in re.findall(r"HP:\d{7}", _clean_str(row.get("PhenotypeIDS"))):
                    self.clinvar_cache[hpo].append(gene)
    
    def _load_panelapp(self):
        """PanelApp panels JSON：从相关 HPO/疾病文本中提取专家 curated 基因。"""
        if not os.path.exists(self.cfg.PATH_PANELAPP):
            return
        try:
            with open(self.cfg.PATH_PANELAPP, encoding="utf-8-sig", errors="ignore") as handle:
                payload = json.load(handle)
        except Exception as exc:
            log(f"[Disease 警告] PanelApp JSON 解析失败，跳过: {exc}")
            return

        panels = payload.get("results", payload) if isinstance(payload, dict) else payload
        if not isinstance(panels, list):
            log("[Disease 警告] PanelApp JSON 格式不符合预期，跳过")
            return

        known_hpos = set(self.hpo_gene_cache) | set(self.omim_cache) | set(self.orpha_cache) | set(self.clinvar_cache)
        loaded_links = 0
        for panel in panels:
            if not isinstance(panel, dict):
                continue

            gene_hpo_links = self._extract_panelapp_gene_hpo_links(panel)
            if gene_hpo_links:
                for hpo, genes in gene_hpo_links.items():
                    self.panelapp_cache.setdefault(hpo, []).extend(genes)
                    loaded_links += len(genes)
                continue

            panel_meta = {
                key: panel.get(key)
                for key in (
                    "id", "name", "disease_group", "disease_sub_group",
                    "status", "relevant_disorders", "types"
                )
            }
            text = json.dumps(panel_meta, ensure_ascii=False)
            hpo_hits = set()
            if not hpo_hits:
                lower_text = text.lower()
                hpo_hits = {hpo for hpo in known_hpos if self._panel_matches_hpo(lower_text, hpo)}
            if not hpo_hits:
                continue
            genes = self._extract_panelapp_genes(panel)
            for hpo in hpo_hits:
                self.panelapp_cache.setdefault(hpo, []).extend(genes)
                loaded_links += len(genes)
        if loaded_links:
            log(f"[Disease] PanelApp 映射加载: {loaded_links} HPO-gene links")

    @staticmethod
    def _extract_panelapp_gene_hpo_links(panel: Dict[str, Any]) -> Dict[str, List[str]]:
        """Use row-level HPO annotations when the local PanelApp TSV cache provides them."""
        links = defaultdict(list)
        genes = panel.get("genes")
        if not isinstance(genes, list):
            return links
        for item in genes:
            if not isinstance(item, dict):
                continue
            gene = _clean_str(item.get("gene_symbol") or item.get("entity_name") or item.get("gene"))
            if not gene:
                continue
            text = " ".join(_clean_str(item.get(key)) for key in ("hpo", "phenotypes", "description"))
            for hpo in re.findall(r"HP:\d{7}", text):
                links[hpo].append(gene)
        return {hpo: _unique_preserve_order(genes) for hpo, genes in links.items()}

    def _panel_matches_hpo(self, panel_text: str, hpo: str) -> bool:
        """PanelApp 面板缺少 HPO ID 时，用 HPO 名称做保守文本匹配。"""
        hpo_name = _clean_str(getattr(self, "hpo_names", {}).get(hpo, ""))
        if not hpo_name:
            return False
        tokens = [x for x in re.split(r"\W+", hpo_name.lower()) if len(x) >= 4]
        return bool(tokens) and all(token in panel_text for token in tokens[:4])

    @staticmethod
    def _extract_panelapp_genes(panel: Dict[str, Any]) -> List[str]:
        """兼容 PanelApp 常见嵌套结构，提取 gene_symbol/entity_name。"""
        genes = []

        def visit(obj: Any):
            if isinstance(obj, dict):
                for key in ("gene_symbol", "hgnc_symbol", "symbol", "entity_name", "gene"):
                    value = obj.get(key)
                    if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9.-]+", value.strip()):
                        genes.append(value.strip())
                for value in obj.values():
                    visit(value)
            elif isinstance(obj, list):
                for item in obj:
                    visit(item)

        visit(panel)
        return _unique_preserve_order(genes)
    
    def build(self, hpo_ids: List[str], hpo_mapper: HPOMapper) -> Tuple[List[str], Dict]:
        """
        三级策略构建 D 集：
        1. 严格模式：加权证据分 >= D_MIN_EVIDENCE
        2. 保底模式：加权证据分 >= D_FALLBACK_EVIDENCE
        3. 父节点扩展：HPO 上溯两层，重新检索
        """
        D, evidence = self._query_multi_source(hpo_ids, min_evidence=self.cfg.D_MIN_EVIDENCE)
        
        if not D:
            log(f"[Disease 降级] 严格加权阈值({self.cfg.D_MIN_EVIDENCE})下 D 集为空，降至保底阈值...")
            D, evidence = self._query_multi_source(hpo_ids, min_evidence=self.cfg.D_FALLBACK_EVIDENCE)
            
        if not D:
            log(f"[Disease 降级] 单库仍为空，扩展 HPO 父节点...")
            broad_hpos = hpo_mapper.get_broader_hpos(hpo_ids, levels=self.cfg.D_BROADEN_HPO_LEVEL)
            if broad_hpos:
                D, evidence = self._query_multi_source(broad_hpos, min_evidence=self.cfg.D_FALLBACK_EVIDENCE)
                
        if not D:
            log("[Disease 警告] D 集完全为空，D 轴将不参与最终融合")
            
        # 基因名已在 _query_multi_source 内标准化；这里保留一次去重兜底。
        D_std = self.id_std.standardize(D)
        return D_std, evidence
    
    def _query_multi_source(self, hpo_ids: List[str], min_evidence: float) -> Tuple[List[str], Dict]:
        """多库查询并按来源独立性累加加权证据分。"""
        gene_scores = Counter()
        gene_sources = defaultdict(set)
        source_weights = getattr(self.cfg, "SOURCE_WEIGHTS", Config.SOURCE_WEIGHTS)
        sources = {
            'hpo_genes': self._query_hpo_genes(hpo_ids),
            'omim': self._query_omim(hpo_ids),
            'orpha': self._query_orphanet(hpo_ids),
            'clinvar': self._query_clinvar(hpo_ids),
            'panelapp': self._query_panelapp(hpo_ids),
        }
        for src_name, genes in sources.items():
            weight = float(source_weights.get(src_name, 1.0))
            for g in self.id_std.standardize(list(set(genes))):
                gene_scores[g] += weight
                gene_sources[g].add(src_name)
                
        threshold = float(min_evidence)
        D = [g for g, score in gene_scores.items() if score >= threshold]
        evidence = {
            g: {
                "evidence_score": round(float(score), 4),
                "sources": sorted(gene_sources[g]),
            }
            for g, score in gene_scores.items()
        }
        return D, evidence
    
    def _query_omim(self, hpo_ids: List[str]) -> List[str]:
        genes = []
        for hpo in hpo_ids:
            genes.extend(self.omim_cache.get(hpo, []))
        return genes
    def _query_hpo_genes(self, hpo_ids: List[str]) -> List[str]:
        genes = []
        for hpo in hpo_ids:
            genes.extend(self.hpo_gene_cache.get(hpo, []))
        return genes
    def _query_orphanet(self, hpo_ids: List[str]) -> List[str]:
        genes = []
        for hpo in hpo_ids:
            genes.extend(self.orpha_cache.get(hpo, []))
        return genes
    def _query_clinvar(self, hpo_ids: List[str]) -> List[str]:
        genes = []
        for hpo in hpo_ids:
            genes.extend(self.clinvar_cache.get(hpo, []))
        return genes
    def _query_panelapp(self, hpo_ids: List[str]) -> List[str]:
        genes = []
        for hpo in hpo_ids:
            genes.extend(self.panelapp_cache.get(hpo, []))
        return genes


# ========================= 4. T 集构建模块（组织核心轴） =========================

class TissueModuleBuilder:
    """
    三层策略构建组织核心基因集 T：
    1. 表达层：GTEx + HPA（组织高表达且高特异）
    2. 必需层：DepMap（目标组织或相近细胞系中功能丧失致死或严重受损）
    3. 通路层：Reactome（组织富集通路的核心骨架基因）
    
    关键修复：GTEx 组织名与 UBERON/HPO 输出名不一致，必须通过映射表转换。
    """
    TPM_OUTPUT_COLUMNS = ["基因", "组织类型", "GTEx gene-level TPM", "HPA nTPM"]
    
    def __init__(self, cfg: Config, id_std: IDStandardizer):
        self.cfg = cfg
        self.id_std = id_std
        
        # UBERON/组织名 -> GTEx 组织列名的映射（必须人工校对）
        self.TISSUE_TO_GTEX = {
            "retina": [],  # GTEx v9 无 retina！需回退到 EyeIntegration 或留空
            "eye": [],     # GTEx 无 eye
            "heart": ["Heart_Left_Ventricle", "Heart_Atrial_Appendage", "Heart - Left Ventricle", "Heart - Atrial Appendage"],
            "muscle": ["Muscle_Skeletal"],
            "brain": [
                "Brain_Cortex", "Brain_Cerebellum", "Brain_Hippocampus", "Brain_Amygdala",
                "Brain_Anterior_cingulate_cortex_BA24", "Brain_Caudate_basal_ganglia",
                "Brain_Cerebellar_Hemisphere", "Brain_Frontal_Cortex_BA9",
                "Brain_Hypothalamus", "Brain_Nucleus_accumbens_basal_ganglia",
                "Brain_Putamen_basal_ganglia", "Brain_Substantia_nigra",
                "Brain - Cortex", "Brain - Cerebellum", "Brain - Hippocampus",
            ],
            "nerve": ["Nerve_Tibial", "Brain_Spinal_cord_cervical_c-1"],
            "liver": ["Liver", "Liver_Hepatocyte", "Liver_Mixed_Cell", "Liver_Portal_Tract"],
            "lung": ["Lung"],
            "kidney": ["Kidney_Cortex", "Kidney_Medulla", "Kidney - Cortex", "Kidney - Medulla"],
            "pancreas": ["Pancreas", "Pancreas_Acini", "Pancreas_Islets", "Pancreas_Mixed_Cell"],
            "skin": ["Skin_Not_Sun_Exposed_Suprapubic", "Skin_Sun_Exposed_Lower_leg"],
            "adipose": ["Adipose_Subcutaneous", "Adipose_Visceral_Omentum"],
            "adrenal gland": ["Adrenal_Gland"],
            "blood vessel": ["Artery_Aorta", "Artery_Coronary", "Artery_Tibial"],
            "bone marrow": ["Whole Blood"],  # 近似
            "blood": ["Whole_Blood", "Cells_EBV-transformed_lymphocytes", "Whole Blood"],
            "lymphoid": ["Cells_EBV-transformed_lymphocytes"],
            "spleen": ["Spleen"],
            "urinary bladder": ["Bladder"],
            "breast": ["Breast_Mammary_Tissue"],
            "cervix": ["Cervix_Ectocervix", "Cervix_Endocervix"],
            "colon": ["Colon_Sigmoid", "Colon_Transverse", "Colon_Transverse_Mucosa", "Colon_Transverse_Muscularis", "Colon_Transverse_Mixed_Cell"],
            "small intestine": ["Small_Intestine_Terminal_Ileum", "Small_Intestine_Terminal_Ileum_Lymphode_Aggregate", "Small_Intestine_Terminal_Ileum_Mixed_Cell"],
            "stomach": ["Stomach", "Stomach_Mucosa", "Stomach_Muscularis", "Stomach_Mixed_Cell"],
            "esophagus": ["Esophagus_Mucosa", "Esophagus_Muscularis", "Esophagus_Gastroesophageal_Junction"],
            "ovary": ["Ovary"],
            "fallopian tube": ["Fallopian_Tube"],
            "prostate": ["Prostate"],
            "testis": ["Testis"],
            "thyroid gland": ["Thyroid"],
            "uterus": ["Uterus"],
            "vagina": ["Vagina"],
            "salivary gland": ["Minor_Salivary_Gland"],
            "soft tissue": ["Cells_Cultured_fibroblasts"],
            "pituitary": ["Pituitary"],
        }
        
        # UBERON/组织名 -> HPA 组织列名
        self.TISSUE_TO_HPA = {
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
        
        # UBERON/组织名 -> DepMap 模型元数据关键词（近似映射）
        self.TISSUE_TO_DEPMAP = {
            "retina": ["retina", "eye", "uveal"],
            "eye": ["eye", "ocular", "retinoblastoma", "uveal"],
            "heart": ["heart", "cardiac"],
            "muscle": ["muscle", "rhabdomyosarcoma", "leiomyosarcoma"],
            "brain": ["brain", "cns", "central nervous", "glioma", "neuroblastoma"],
            "nerve": ["peripheral nervous", "nerve sheath", "neuroblastoma"],
            "liver": ["liver", "hepat"],
            "lung": ["lung"],
            "kidney": ["kidney", "renal"],
            "pancreas": ["pancreas", "pancreatic"],
            "skin": ["skin", "melanoma", "cutaneous"],
            "adrenal gland": ["adrenal"],
            "urinary bladder": ["bladder", "urinary tract", "urethral"],
            "breast": ["breast"],
            "cervix": ["cervix", "cervical"],
            "colon": ["bowel", "colon", "colorectal"],
            "appendix": ["bowel", "appendix"],
            "small intestine": ["small bowel", "bowel"],
            "stomach": ["stomach", "gastric", "esophagogastric"],
            "esophagus": ["esophagus", "esophageal", "esophagogastric"],
            "ovary": ["ovary", "ovarian"],
            "fallopian tube": ["fallopian"],
            "prostate": ["prostate"],
            "epididymis": ["testis", "germ cell"],
            "testis": ["testis", "germ cell"],
            "seminal vesicle": ["prostate"],
            "thyroid gland": ["thyroid"],
            "parathyroid gland": ["parathyroid"],
            "uterus": ["uterus", "uterine", "endometrial"],
            "vagina": ["vagina", "vulva"],
            "salivary gland": ["salivary"],
            "gallbladder": ["biliary", "gallbladder"],
            "placenta": ["gestational trophoblastic", "placenta"],
            "choroid plexus": ["brain", "cns", "central nervous"],
            "bone": ["bone", "osteosarcoma", "chondrosarcoma", "chordoma"],
            "soft tissue": ["soft tissue", "sarcoma", "fibrosarcoma", "liposarcoma"],
            "bone marrow": ["haematopoietic", "hematopoietic", "blood"],
            "blood": ["blood", "myeloid", "leukemia"],
            "lymphoid": ["lymphoid", "lymphoma", "b-cell", "t-cell"],
            "spleen": ["lymphoid"],
            "pituitary": ["pituitary"],
        }
        
    def load(self):
        self._load_gtex()
        self._load_hpa()
        self._load_depmap()
        self._load_reactome()
        log("[Tissue] 组织数据库加载完成")
        
    def _load_gtex(self):
        """GTEx median TPM。GCT 行含 Ensembl ID 和 Description(Symbol)。"""
        self.gtex_path = None
        gtex_path = self.cfg.PATH_GTEX
        if not os.path.exists(gtex_path):
            candidates = [
                os.path.join(self.cfg.DATA_DIR, "GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.gct.gz"),
                os.path.join(self.cfg.DATA_DIR, "GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.gct"),
                os.path.join(self.cfg.DATA_DIR, "GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz"),
                os.path.join(self.cfg.DATA_DIR, "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz"),
                os.path.join(self.cfg.DATA_DIR, "GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct"),
                os.path.join(self.cfg.DATA_DIR, "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct"),
            ]
            gtex_path = next((p for p in candidates if os.path.exists(p)), gtex_path)
        if not os.path.exists(gtex_path):
            log(f"[警告] GTEx 文件未找到: {self.cfg.PATH_GTEX}")
            self.gtex = None
            return
        if gtex_path != self.cfg.PATH_GTEX:
            log(f"[GTEx] 使用可用版本: {gtex_path}")
        self.gtex_path = gtex_path
        gtex = pd.read_csv(gtex_path, sep="\t", skiprows=2, index_col=0, low_memory=False)
        if "Description" in gtex.columns:
            gtex.index = gtex["Description"].astype(str)
            gtex = gtex.drop(columns=["Description"])
        gtex = gtex.apply(pd.to_numeric, errors="coerce").fillna(0.0)
        gtex = gtex.groupby(gtex.index).max()
        self.gtex = gtex
        
    def _load_hpa(self):
        self.hpa_rna = None
        self.hpa_protein = None
        if os.path.exists(self.cfg.PATH_HPA_RNA):
            self.hpa_rna = pd.read_csv(self.cfg.PATH_HPA_RNA, sep="\t", low_memory=False)
        hpa_protein_path = self.cfg.PATH_HPA_PROTEIN
        if not os.path.exists(hpa_protein_path):
            legacy = os.path.join(self.cfg.DATA_DIR, "normal_tissue.tsv")
            hpa_protein_path = legacy if os.path.exists(legacy) else hpa_protein_path
        if os.path.exists(hpa_protein_path):
            self.hpa_protein = pd.read_csv(hpa_protein_path, sep="\t", low_memory=False)
            
    def _load_depmap(self):
        self.depmap = None
        self.depmap_model = None
        if os.path.exists(self.cfg.PATH_DEPMAP):
            depmap = pd.read_csv(self.cfg.PATH_DEPMAP, index_col=0, low_memory=False)
            depmap.columns = [re.sub(r"\s+\(\d+\)$", "", str(c)).strip() for c in depmap.columns]
            self.depmap = depmap
        if os.path.exists(self.cfg.PATH_DEPMAP_MODEL):
            self.depmap_model = pd.read_csv(self.cfg.PATH_DEPMAP_MODEL, low_memory=False)
            
    def _load_reactome(self):
        """Reactome 通路基因集与层级关系。"""
        self.reactome_genes = defaultdict(list)  # pathway ID -> [genes]
        if os.path.exists(self.cfg.PATH_REACTOME_GENESET):
            with open(self.cfg.PATH_REACTOME_GENESET, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 3 and self.cfg.PATH_REACTOME_GENESET.endswith(".gmt"):
                        pathway = parts[0]
                        self.reactome_genes[pathway].extend(parts[2:])
                    elif len(parts) >= 2:
                        if len(parts) >= 6 and parts[5] != "Homo sapiens":
                            continue
                        gene = self.id_std.ensembl_gene_to_symbol.get(parts[0], parts[0])
                        pathway = parts[1]
                        self.reactome_genes[pathway].append(gene)
        # 层级关系可选，用于合并子通路
        self.reactome_hierarchy = {}
        
    def build(self, tissue_names: List[str]) -> Tuple[List[str], Dict[str, int]]:
        """
        对输入的每个组织分别建 T 集，最后取并集，权重累加。
        返回: (T_genes, T_weights) 其中 weight = 1~3（支持层数）
        """
        all_T = []
        all_weights = Counter()
        all_evidence = defaultdict(lambda: {"layers": set(), "tissues": set()})
        
        for tissue in _unique_preserve_order([coarse_tissue_name(t) for t in tissue_names if coarse_tissue_name(t)]):
            cached_layers = self._load_tissue_layers_cache(tissue)
            if cached_layers is not None:
                T_expr = cached_layers.get("expression", [])
                T_ess = cached_layers.get("essential_depmap", [])
                T_pw = cached_layers.get("pathway", [])
                log(f"[Tissue] 使用缓存: {tissue}")
            else:
                T_expr = self._build_expression_layer(tissue)
                T_ess = self._build_essential_layer(tissue)
                T_pw = self._build_pathway_layer(tissue, T_expr + T_ess)
                self._save_tissue_layers_cache(tissue, {
                    "expression": T_expr,
                    "essential_depmap": T_ess,
                    "pathway": T_pw,
                })
            
            # 合并该组织的 T 集，并保留每个基因来自哪一层/哪个组织以便输出审计。
            for layer_name, layer_genes in (
                ("expression", T_expr),
                ("essential_depmap", T_ess),
                ("pathway", T_pw),
            ):
                for g in layer_genes:
                    all_evidence[g]["layers"].add(layer_name)
                    all_evidence[g]["tissues"].add(tissue)
                all_T.extend(layer_genes)
            
        # 去重，保留最大权重
        T = _unique_preserve_order(all_T)
        all_weights = {g: len(all_evidence[g]["layers"]) for g in T}
        self.last_t_evidence = {
            g: {
                "weight": int(all_weights.get(g, 0)),
                "layers": sorted(all_evidence[g]["layers"]),
                "tissues": sorted(all_evidence[g]["tissues"]),
            }
            for g in T
        }
        return T, dict(all_weights)

    def _tissue_cache_signature(self, tissue: str) -> Dict[str, Any]:
        return _cache_signature([
            getattr(self, "gtex_path", None) or self.cfg.PATH_GTEX,
            self.cfg.PATH_HPA_RNA,
            self.cfg.PATH_DEPMAP,
            self.cfg.PATH_DEPMAP_MODEL,
            self.cfg.PATH_REACTOME_GENESET,
            self.cfg.PATH_STRING_LINKS,
        ], {
            "tissue": tissue,
            "t_gtex_tpm_cutoff": float(self.cfg.T_GTEX_TPM_CUTOFF),
            "t_tau_cutoff": float(self.cfg.T_TAU_CUTOFF),
            "t_top_n_expr": int(self.cfg.T_TOP_N_EXPR),
            "t_pathway_top_pct": int(self.cfg.T_PATHWAY_TOP_PCT),
            "t_pathway_top_n": int(self.cfg.T_PATHWAY_TOP_N),
            "depmap_effect_cutoff": float(self.cfg.DEPMAP_EFFECT_CUTOFF),
            "string_score_cutoff": int(self.cfg.STRING_SCORE_CUTOFF),
        })

    def _tissue_cache_path(self, tissue: str, signature: Dict[str, Any]) -> str:
        safe_tissue = re.sub(r"[^A-Za-z0-9]+", "_", tissue).strip("_").lower() or "unknown"
        return os.path.join(_ensure_cache_dir(self.cfg), _safe_cache_name(f"tissue_{safe_tissue}", signature) + ".json")

    def _load_tissue_layers_cache(self, tissue: str) -> Optional[Dict[str, List[str]]]:
        signature = self._tissue_cache_signature(tissue)
        return _load_json_cache(self._tissue_cache_path(tissue, signature), signature)

    def _save_tissue_layers_cache(self, tissue: str, layers: Dict[str, List[str]]):
        signature = self._tissue_cache_signature(tissue)
        _save_json_cache(self._tissue_cache_path(tissue, signature), signature, layers)

    @staticmethod
    def _column_key(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(name).lower())

    def _resolve_columns(self, available_columns, requested_columns: List[str]) -> List[str]:
        """Resolve tissue columns across GTEx versions that differ by spaces, hyphens, and underscores."""
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
    
    def _build_expression_layer(self, tissue: str) -> List[str]:
        """
        第一层：组织高表达 + 高特异基因。
        修复：GTEx 组织名必须通过 TISSUE_TO_GTEX 映射，否则 KeyError。
        """
        T_expr = []
        
        # --- GTEx 分支 ---
        if self.gtex is not None:
            gtex_cols = self.TISSUE_TO_GTEX.get(tissue, [])
            if gtex_cols:
                # 取映射到的所有 GTEx 列的平均表达
                available_cols = self._resolve_columns(self.gtex.columns, gtex_cols)
                if available_cols:
                    expr = self.gtex[available_cols].mean(axis=1)
                    tau = self._calculate_tau(self.gtex, available_cols)
                    
                    mask = (expr > self.cfg.T_GTEX_TPM_CUTOFF) & (tau > self.cfg.T_TAU_CUTOFF)
                    T_expr = expr[mask].sort_values(ascending=False).head(self.cfg.T_TOP_N_EXPR).index.tolist()
                else:
                    log(f"[GTEx] 组织 '{tissue}' 的映射列在 GTEx 中不存在")
            else:
                log(f"[GTEx] 组织 '{tissue}' 无映射配置（如 retina 不在 GTEx 中）")
                
        # --- HPA 分支（补充或替代）---
        if self.hpa_rna is not None:
            hpa_cols = self.TISSUE_TO_HPA.get(tissue, [])
            if hpa_cols and {"Tissue", "nTPM"}.issubset(set(self.hpa_rna.columns)):
                gene_col = next((c for c in ("Gene name", "Gene", "Ensembl") if c in self.hpa_rna.columns), None)
                if gene_col:
                    hpa_sub = self.hpa_rna[self.hpa_rna["Tissue"].astype(str).str.lower().isin([x.lower() for x in hpa_cols])]
                    hpa_sub = hpa_sub[pd.to_numeric(hpa_sub["nTPM"], errors="coerce") > self.cfg.T_GTEX_TPM_CUTOFF]
                    hpa_genes = []
                    for gene in hpa_sub[gene_col].dropna().astype(str):
                        hpa_genes.append(self.id_std.ensembl_gene_to_symbol.get(gene, gene))
                    T_expr = _unique_preserve_order(T_expr + hpa_genes)
            
        return self.id_std.standardize(T_expr)

    def build_tpm_expression_table(self, tissue_names: List[str]) -> pd.DataFrame:
        """输出 GTEx/HPA 中目标组织高表达且相对特异基因的表达审计表。"""
        records: Dict[Tuple[str, str], Dict[str, Any]] = {}
        tissues = _unique_preserve_order(
            [coarse_tissue_name(t) for t in tissue_names if coarse_tissue_name(t)]
        )
        for tissue in tissues:
            self._add_gtex_tpm_records(tissue, records)
            self._add_hpa_tpm_records(tissue, records)
            self._backfill_tpm_values(tissue, records)
        if not records:
            return pd.DataFrame(columns=self.TPM_OUTPUT_COLUMNS)

        df = pd.DataFrame(records.values(), columns=self.TPM_OUTPUT_COLUMNS)
        for column in ("GTEx gene-level TPM", "HPA nTPM"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df = df.sort_values(
            by=["组织类型", "GTEx gene-level TPM", "HPA nTPM", "基因"],
            ascending=[True, False, False, True],
            na_position="last",
        )
        return df[self.TPM_OUTPUT_COLUMNS].reset_index(drop=True)

    def _standard_gene_for_expression_output(self, gene: Any) -> str:
        gene = _clean_str(gene)
        if not gene:
            return ""
        gene = self.id_std.ensembl_gene_to_symbol.get(gene, gene)
        return self.id_std.alias_to_official.get(gene, gene)

    def _set_tpm_record_value(
        self,
        records: Dict[Tuple[str, str], Dict[str, Any]],
        gene: Any,
        tissue: str,
        column: str,
        value: Any,
    ):
        gene = self._standard_gene_for_expression_output(gene)
        if not gene:
            return
        numeric_value = pd.to_numeric(value, errors="coerce")
        if pd.isna(numeric_value):
            return
        key = (gene, tissue)
        record = records.setdefault(
            key,
            {
                "基因": gene,
                "组织类型": tissue,
                "GTEx gene-level TPM": np.nan,
                "HPA nTPM": np.nan,
            },
        )
        record[column] = round(float(numeric_value), 6)

    def _add_gtex_tpm_records(self, tissue: str, records: Dict[Tuple[str, str], Dict[str, Any]]):
        expr = self._gtex_target_expression(tissue)
        if expr is None:
            return
        available_cols = self._resolve_columns(self.gtex.columns, self.TISSUE_TO_GTEX.get(tissue, []))
        tau = self._calculate_tau(self.gtex, available_cols)
        mask = (expr > self.cfg.T_GTEX_TPM_CUTOFF) & (tau > self.cfg.T_TAU_CUTOFF)
        for gene, value in expr[mask].items():
            self._set_tpm_record_value(records, gene, tissue, "GTEx gene-level TPM", value)

    def _gtex_target_expression(self, tissue: str) -> Optional[pd.Series]:
        if self.gtex is None:
            return None
        gtex_cols = self.TISSUE_TO_GTEX.get(tissue, [])
        if not gtex_cols:
            return None
        available_cols = self._resolve_columns(self.gtex.columns, gtex_cols)
        if not available_cols:
            return None
        return self.gtex[available_cols].mean(axis=1)

    def _fill_gtex_values_for_existing_records(
        self,
        tissue: str,
        records: Dict[Tuple[str, str], Dict[str, Any]],
        expr: pd.Series,
    ):
        existing_genes = {gene for gene, record_tissue in records if record_tissue == tissue}
        if not existing_genes:
            return
        for gene, value in expr.items():
            std_gene = self._standard_gene_for_expression_output(gene)
            if std_gene in existing_genes:
                self._set_tpm_record_value(records, std_gene, tissue, "GTEx gene-level TPM", value)

    def _hpa_expression_matrix(self) -> Optional[pd.DataFrame]:
        if hasattr(self, "_cached_hpa_expression_matrix"):
            return self._cached_hpa_expression_matrix
        self._cached_hpa_expression_matrix = None
        if self.hpa_rna is None or not {"Tissue", "nTPM"}.issubset(set(self.hpa_rna.columns)):
            return None
        gene_col = next((c for c in ("Gene name", "Gene", "Ensembl") if c in self.hpa_rna.columns), None)
        if gene_col is None:
            return None
        hpa = self.hpa_rna[[gene_col, "Tissue", "nTPM"]].copy()
        hpa["gene"] = hpa[gene_col].map(self._standard_gene_for_expression_output)
        hpa["nTPM"] = pd.to_numeric(hpa["nTPM"], errors="coerce").fillna(0.0)
        hpa = hpa[(hpa["gene"] != "") & hpa["Tissue"].notna()]
        if hpa.empty:
            return None
        matrix = hpa.pivot_table(index="gene", columns="Tissue", values="nTPM", aggfunc="max", fill_value=0.0)
        matrix = matrix.groupby(matrix.index).max()
        self._cached_hpa_expression_matrix = matrix
        return matrix

    def _resolve_hpa_columns(self, requested_columns: List[str]) -> List[str]:
        matrix = self._hpa_expression_matrix()
        if matrix is None:
            return []
        by_lower = {str(col).lower(): col for col in matrix.columns}
        resolved = []
        for col in requested_columns:
            match = by_lower.get(str(col).lower())
            if match is not None and match not in resolved:
                resolved.append(match)
        return resolved

    def _add_hpa_tpm_records(self, tissue: str, records: Dict[Tuple[str, str], Dict[str, Any]]):
        expr = self._hpa_target_expression(tissue)
        if expr is None:
            return
        matrix = self._hpa_expression_matrix()
        available_cols = self._resolve_hpa_columns(self.TISSUE_TO_HPA.get(tissue, []))
        if not available_cols:
            return
        mask = expr > self.cfg.T_GTEX_TPM_CUTOFF
        for gene, value in expr[mask].items():
            self._set_tpm_record_value(records, gene, tissue, "HPA nTPM", value)

    def _hpa_target_expression(self, tissue: str) -> Optional[pd.Series]:
        matrix = self._hpa_expression_matrix()
        if matrix is None:
            return None
        hpa_cols = self.TISSUE_TO_HPA.get(tissue, [])
        if not hpa_cols:
            return None
        available_cols = self._resolve_hpa_columns(hpa_cols)
        if not available_cols:
            return None
        return matrix[available_cols].mean(axis=1)

    def _backfill_tpm_values(self, tissue: str, records: Dict[Tuple[str, str], Dict[str, Any]]):
        gtex_expr = self._gtex_target_expression(tissue)
        if gtex_expr is not None:
            self._fill_gtex_values_for_existing_records(tissue, records, gtex_expr)
        hpa_expr = self._hpa_target_expression(tissue)
        if hpa_expr is not None:
            self._fill_hpa_values_for_existing_records(tissue, records, hpa_expr)

    def _fill_hpa_values_for_existing_records(
        self,
        tissue: str,
        records: Dict[Tuple[str, str], Dict[str, Any]],
        expr: pd.Series,
    ):
        existing_genes = {gene for gene, record_tissue in records if record_tissue == tissue}
        if not existing_genes:
            return
        for gene, value in expr.items():
            if gene in existing_genes:
                self._set_tpm_record_value(records, gene, tissue, "HPA nTPM", value)
    
    def _calculate_tau(self, gtex_df: pd.DataFrame, target_cols: List[str]) -> pd.Series:
        """
        Tau 组织特异性指数：0 = 广谱表达，1 = 绝对特异。
        公式：tau = sum(1 - x_i/x_max) / (N-1)
        """
        x_max = gtex_df.max(axis=1).replace(0, np.nan)
        tau = (1 - gtex_df.div(x_max, axis=0)).sum(axis=1) / max(gtex_df.shape[1] - 1, 1)
        return tau.fillna(0)
    
    def _build_essential_layer(self, tissue: str) -> List[str]:
        """第二层：DepMap 目标组织或相近细胞系必需基因。"""
        T_ess = []
        if self.depmap is not None:
            matched_lines = self._match_depmap_lines(tissue)
            if matched_lines:
                median_effect = self.depmap.loc[matched_lines].apply(pd.to_numeric, errors="coerce").median(axis=0)
                depmap_genes = median_effect[median_effect < self.cfg.DEPMAP_EFFECT_CUTOFF].index.tolist()
                T_ess.extend(depmap_genes)
            
        return self.id_std.standardize(T_ess)
    
    def _match_depmap_lines(self, tissue: str) -> List[str]:
        """按组织名近似匹配 DepMap 模型；没有 Model.csv 时回退到行名模糊匹配。"""
        keywords = [x.lower() for x in self.TISSUE_TO_DEPMAP.get(tissue, [])]
        if not keywords or self.depmap is None:
            return []
        if self.depmap_model is not None:
            id_col = next((c for c in ("ModelID", "DepMap_ID", "depmap_id") if c in self.depmap_model.columns), None)
            text_cols = [c for c in ("OncotreeLineage", "OncotreePrimaryDisease", "Tissue", "CCLEName", "ModelCondition") if c in self.depmap_model.columns]
            if id_col and text_cols:
                matched = []
                for _, row in self.depmap_model.iterrows():
                    text = " ".join(str(row.get(c, "")) for c in text_cols).lower()
                    model_id = str(row[id_col])
                    if model_id in self.depmap.index and any(k in text for k in keywords):
                        matched.append(model_id)
                return matched
        return [idx for idx in self.depmap.index if any(k in str(idx).lower() for k in keywords)]
    
    def _build_pathway_layer(self, tissue: str, seed_genes: List[str]) -> List[str]:
        """
        第三层：用种子基因（表达+必需）做 Reactome 通路富集，提取各通路核心骨架基因。
        注意：Reactome 本身无组织标签，必须通过组织高表达基因反推富集通路。
        """
        T_pw = []
        if not self.reactome_genes or not seed_genes:
            return T_pw
            
        # 简化版：统计种子基因落在哪些 Reactome 通路中（超几何富集）
        # 生产环境建议用 gseapy 或 goatools 做正式富集
        pathway_hits = Counter()
        seed_set = set(self.id_std.standardize(seed_genes))
        for pw, genes in self.reactome_genes.items():
            pathway_genes = self.id_std.standardize(genes)
            overlap = set(pathway_genes) & seed_set
            if len(overlap) > 2:  # 至少 3 个基因命中
                pathway_hits[pw] = len(overlap)
                
        # 取命中数 top 的通路，提取核心基因
        top_pathways = [pw for pw, _ in pathway_hits.most_common(self.cfg.T_PATHWAY_TOP_N)]
        for pw in top_pathways:
            genes = self.id_std.standardize(self.reactome_genes[pw])
            core = self._pathway_core_genes(genes)
            T_pw.extend(core)
            
        return _unique_preserve_order(self.id_std.standardize(T_pw))

    def _pathway_core_genes(self, genes: List[str]) -> List[str]:
        """按 STRING 子图 degree 选择通路核心基因，阈值由 T_PATHWAY_TOP_PCT 控制。"""
        genes = _unique_preserve_order([g for g in genes if g])
        if not genes:
            return []
        ppi = getattr(getattr(self, "ppi_engine", None), "G", None)
        if ppi is None or ppi.number_of_nodes() == 0:
            return []
        present = [g for g in genes if g in ppi]
        if not present:
            return genes
        subgraph = ppi.subgraph(present)
        degrees = dict(subgraph.degree())
        if not degrees:
            return []
        cutoff_pct = min(max(float(self.cfg.T_PATHWAY_TOP_PCT), 0.0), 100.0)
        cutoff = float(np.percentile(list(degrees.values()), cutoff_pct))
        core = [g for g in present if degrees.get(g, 0) >= cutoff]
        return core or present


# ========================= 5. STRING 网络构建与评分模块 =========================

class PPIEngine:
    """
    负责构建 STRING 网络、预计算拓扑统计量、执行双轴评分、提取 Top N 邻居。
    """
    
    def __init__(self, cfg: Config, id_std: IDStandardizer):
        self.cfg = cfg
        self.id_std = id_std
        self.G = nx.Graph()           # STRING 网络（无向）
        self.node_to_symbol = {}      # STRING ID -> HGNC Symbol
        self.symbol_to_node = {}      # HGNC Symbol -> STRING ID
        self._network_stats_ready = False
        self.avg_degree = 0.0
        self.std_degree = 0.0
        self.betweenness = {}
        self.betweenness_rank_pct = {}
        
    def load(self):
        """加载 STRING 并构建 networkx 图。"""
        if not os.path.exists(self.cfg.PATH_STRING_LINKS):
            raise FileNotFoundError(f"STRING 文件未找到: {self.cfg.PATH_STRING_LINKS}")
        signature = _cache_signature([
            self.cfg.PATH_STRING_LINKS,
            self.cfg.PATH_STRING_INFO,
            self.cfg.PATH_HGNC,
            self.cfg.PATH_ENSEMBL_BIOMART,
            self.cfg.PATH_UNIPROT_MAPPING,
        ], {
            "string_score_cutoff": int(self.cfg.STRING_SCORE_CUTOFF),
            "betweenness_sample_k": int(self.cfg.BETWEENNESS_SAMPLE_K),
            "id_strategy": "official_symbol_precedence_v2",
        })
        cache_name = _safe_cache_name("string_graph", signature) + ".pkl"
        cache_path = os.path.join(_ensure_cache_dir(self.cfg), cache_name)
        cached = _load_pickle_cache(cache_path, signature)
        if cached:
            self.G = cached["G"]
            self.symbol_to_node = cached.get("symbol_to_node", {})
            self.node_to_symbol = cached.get("node_to_symbol", {})
            self.avg_degree = cached.get("avg_degree", 0.0)
            self.std_degree = cached.get("std_degree", 1e-9)
            self.betweenness = cached.get("betweenness", {})
            self.betweenness_rank_pct = cached.get("betweenness_rank_pct", {})
            if not self.betweenness_rank_pct:
                self._prepare_betweenness_rank()
            self._network_stats_ready = True
            log(f"[STRING] 使用缓存: {cache_path}")
            log(f"[STRING] 网络: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
            return

        usecols = ["protein1", "protein2", "combined_score"]
        for chunk in pd.read_csv(
            self.cfg.PATH_STRING_LINKS,
            sep=r"\s+",
            usecols=usecols,
            chunksize=self.cfg.STRING_CHUNKSIZE,
            low_memory=False
        ):
            chunk = chunk[chunk["combined_score"] >= self.cfg.STRING_SCORE_CUTOFF]
            for row in chunk.itertuples(index=False):
                sym1 = self._string_id_to_symbol(row.protein1)
                sym2 = self._string_id_to_symbol(row.protein2)
                if sym1 and sym2 and sym1 != sym2:
                    self.G.add_edge(sym1, sym2, combined_score=int(row.combined_score))
                    self.symbol_to_node.setdefault(sym1, row.protein1)
                    self.symbol_to_node.setdefault(sym2, row.protein2)
                
        log(f"[STRING] 网络构建完成: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
        self._precompute_stats()
        _save_pickle_cache(cache_path, signature, {
            "G": self.G,
            "symbol_to_node": self.symbol_to_node,
            "node_to_symbol": self.node_to_symbol,
            "avg_degree": self.avg_degree,
            "std_degree": self.std_degree,
            "betweenness": self.betweenness,
            "betweenness_rank_pct": self.betweenness_rank_pct,
        })
        
    def _string_id_to_symbol(self, string_id: str) -> Optional[str]:
        """STRING ID -> Symbol。利用 IDStandardizer 的反向映射。"""
        symbol = self.id_std.string_id_to_symbol.get(string_id)
        if symbol:
            return symbol
        if not string_id.startswith("9606."):
            return None
        ensp = string_id[5:]  # 去掉 "9606."
        return self.id_std.ensp_to_symbol.get(ensp)
    
    def _precompute_stats(self):
        """预计算网络拓扑统计量，避免每次评分重复计算。"""
        if self.G.number_of_nodes() == 0:
            return
            
        degrees = dict(self.G.degree())
        deg_values = np.array(list(degrees.values()), dtype=float)
        self.avg_degree = float(np.mean(deg_values))
        self.std_degree = float(np.std(deg_values)) + 1e-9  # 防除零
        
        # betweenness 用 k 采样近似（大图加速）
        k = min(self.cfg.BETWEENNESS_SAMPLE_K, self.G.number_of_nodes())
        self.betweenness = nx.betweenness_centrality(self.G, k=k, seed=42)
        self._prepare_betweenness_rank()
        self._network_stats_ready = True

    def _prepare_betweenness_rank(self):
        """Precompute betweenness rank percentiles once for fast per-gene scoring."""
        if not self.betweenness:
            self.betweenness_rank_pct = {}
            return
        ranks = pd.Series(self.betweenness, dtype=float).rank(method="average", pct=True)
        self.betweenness_rank_pct = {gene: float(rank) for gene, rank in ranks.items()}
        
    def score_gene(self, g: str, D: List[str], T: List[str], T_weights: Dict[str, int]) -> Dict:
        """
        双轴 PPI 评分核心算法。
        疾病轴和组织轴基于候选基因在完整 STRING 网络中的单源最短路径结果计算。
        D/T 空轴不参与最终融合，按可用轴权重重归一化。
        """
        result = {
            "gene": g,
            "in_network": g in self.G,
            "disease_score": 0.0,
            "tissue_score": 0.0,
            "topology_score": 0.0,
            "ppi_final": 0.0,
            "score_mode": "",
            "score_weight_sum": 0.0,
            "note": ""
        }
        
        # --- 边界 1：基因不在 STRING 网络中 ---
        if g not in self.G:
            result["note"] = "NOT_IN_STRING"
            result["score_mode"] = "NOT_IN_STRING"
            result["ppi_final"] = 0.0
            return result
            
        D_set = set(D)
        T_set = set(T)
        D_in_graph = {d for d in D_set if d in self.G}
        T_in_graph = {t for t in T_set if t in self.G}
        cutoff = self.cfg.SSSP_CUTOFF if self.cfg.SSSP_CUTOFF > 0 else None
        dist_from_g = nx.single_source_shortest_path_length(self.G, g, cutoff=cutoff)
        weighted_scores = []
        
        # --- 边界 2：D 集为空 ---
        if not D_set:
            result["note"] += "EMPTY_D;"
        elif not D_in_graph:
            result["note"] += "NO_D_IN_STRING;"
        else:
            result["disease_score"] = self._calc_disease_score(g, D_in_graph, dist_from_g)
            weighted_scores.append((self.cfg.W_DISEASE, result["disease_score"]))
            
        # --- 边界 3：T 集为空 ---
        if not T_set:
            result["note"] += "EMPTY_T;"
        elif not T_in_graph:
            result["note"] += "NO_T_IN_STRING;"
        else:
            result["tissue_score"] = self._calc_tissue_score(g, T_in_graph, T_weights, dist_from_g)
            weighted_scores.append((self.cfg.W_TISSUE, result["tissue_score"]))
            
        # --- 拓扑评分 ---
        result["topology_score"] = self._calc_topology_score(g)
        weighted_scores.append((self.cfg.W_TOPOLOGY, result["topology_score"]))
        
        # --- 加权融合：只使用可用轴，并按参与权重重归一化 ---
        weight_sum = sum(w for w, _ in weighted_scores)
        result["score_weight_sum"] = round(float(weight_sum), 4)
        if weight_sum > 0:
            result["ppi_final"] = sum(w * score for w, score in weighted_scores) / weight_sum
            
        disease_available = bool(D_set and D_in_graph)
        tissue_available = bool(T_set and T_in_graph)
        if disease_available and tissue_available:
            result["score_mode"] = "FULL_ANCHOR"
        elif disease_available:
            result["score_mode"] = "NO_T_REWEIGHTED"
        elif tissue_available:
            result["score_mode"] = "NO_D_REWEIGHTED"
        else:
            result["score_mode"] = "TOPOLOGY_ONLY"
        
        # --- 边界 4：孤立基因 ---
        if self.G.degree(g) == 0:
            result["note"] += "ISOLATED;"
        if not result["note"]:
            result["note"] = "OK"
            
        return result

    def score_genes_batch(self, genes: List[str], D: List[str], T: List[str], T_weights: Dict[str, int]) -> List[Dict]:
        """Score many genes using anchor-side BFS maps instead of one BFS per gene."""
        D_set = set(D)
        T_set = set(T)
        D_in_graph = {d for d in D_set if d in self.G}
        T_in_graph = {t for t in T_set if t in self.G}
        cutoff = self.cfg.SSSP_CUTOFF if self.cfg.SSSP_CUTOFF > 0 else None
        disease_available = bool(D_set and D_in_graph)
        tissue_available = bool(T_set and T_in_graph)

        d_dist = {}
        t_dist = {}
        if disease_available:
            d_dist = dict(nx.multi_source_dijkstra_path_length(self.G, D_in_graph, cutoff=cutoff, weight=None))
        if tissue_available:
            t_dist = dict(nx.multi_source_dijkstra_path_length(self.G, T_in_graph, cutoff=cutoff, weight=None))

        records = []
        for g in genes:
            result = {
                "gene": g,
                "in_network": g in self.G,
                "disease_score": 0.0,
                "tissue_score": 0.0,
                "topology_score": 0.0,
                "ppi_final": 0.0,
                "score_mode": "",
                "score_weight_sum": 0.0,
                "note": "",
            }
            if g not in self.G:
                result["note"] = "NOT_IN_STRING"
                result["score_mode"] = "NOT_IN_STRING"
                records.append(result)
                continue

            weighted_scores = []
            if not D_set:
                result["note"] += "EMPTY_D;"
            elif not D_in_graph:
                result["note"] += "NO_D_IN_STRING;"
            else:
                result["disease_score"] = self._calc_disease_score_fast(g, D_in_graph, d_dist)
                weighted_scores.append((self.cfg.W_DISEASE, result["disease_score"]))

            if not T_set:
                result["note"] += "EMPTY_T;"
            elif not T_in_graph:
                result["note"] += "NO_T_IN_STRING;"
            else:
                result["tissue_score"] = self._calc_tissue_score_fast(g, T_in_graph, T_weights, t_dist)
                weighted_scores.append((self.cfg.W_TISSUE, result["tissue_score"]))

            result["topology_score"] = self._calc_topology_score(g)
            weighted_scores.append((self.cfg.W_TOPOLOGY, result["topology_score"]))

            weight_sum = sum(w for w, _ in weighted_scores)
            result["score_weight_sum"] = round(float(weight_sum), 4)
            if weight_sum > 0:
                result["ppi_final"] = sum(w * score for w, score in weighted_scores) / weight_sum
            result["disease_score"] = float(result["disease_score"])
            result["tissue_score"] = float(result["tissue_score"])
            result["topology_score"] = float(result["topology_score"])
            result["ppi_final"] = float(result["ppi_final"])

            if disease_available and tissue_available:
                result["score_mode"] = "FULL_ANCHOR"
            elif disease_available:
                result["score_mode"] = "NO_T_REWEIGHTED"
            elif tissue_available:
                result["score_mode"] = "NO_D_REWEIGHTED"
            else:
                result["score_mode"] = "TOPOLOGY_ONLY"
            if self.G.degree(g) == 0:
                result["note"] += "ISOLATED;"
            if not result["note"]:
                result["note"] = "OK"
            records.append(result)
        return records
    
    def _calc_disease_score(self, g: str, D_set: Set[str], dist_from_g: Dict[str, int]) -> float:
        """疾病锚点评分：直接互作 + 基于单源最短路径结果的网络距离倒数。"""
        if g in D_set:
            return 1.0
            
        neighbors = set(self.G.neighbors(g))
        direct_d = len(neighbors & D_set)
        
        # 直接互作归一化（饱和阈值 K_NEIGHBOR_CAP）
        direct_score = min(direct_d / self.cfg.K_NEIGHBOR_CAP, 1.0)
        
        # 网络距离：到 D 中每个基因的最短路径
        distances = []
        for d in D_set:
            dist = dist_from_g.get(d, float("inf"))
            if dist == float("inf"):
                distances.append(0.0)
            else:
                distances.append(1.0 / (1.0 + dist))
        proximity_d = np.mean(distances) if distances else 0.0
        
        return 0.6 * direct_score + 0.4 * proximity_d

    def _calc_disease_score_fast(self, g: str, D_set: Set[str], min_dist_to_d: Dict[str, int]) -> float:
        if g in D_set:
            return 1.0
        neighbors = set(self.G.neighbors(g))
        direct_d = len(neighbors & D_set)
        direct_score = min(direct_d / self.cfg.K_NEIGHBOR_CAP, 1.0)
        dist = min_dist_to_d.get(g)
        proximity_d = 0.0 if dist is None else 1.0 / (1.0 + dist)
        return 0.6 * direct_score + 0.4 * proximity_d
    
    def _calc_tissue_score(
        self,
        g: str,
        T_set: Set[str],
        T_weights: Dict[str, int],
        dist_from_g: Dict[str, int]
    ) -> float:
        """组织锚点评分：直接互作（加权） + 基于单源最短路径结果的加权网络距离。"""
        if g in T_set:
            # 基础分 0.5 + 层支持加成（最多 3 层 -> 0.5 + 0.5*1 = 1.0）
            w = T_weights.get(g, 1)
            return 0.5 + 0.5 * (min(w, 3) / 3.0)
            
        neighbors = set(self.G.neighbors(g))
        direct_t = neighbors & T_set
        
        # 直接互作得分：邻居的 T_weight 越高，得分越高
        direct_t_score = sum([min(T_weights.get(t, 1), 3) / 3.0 for t in direct_t])
        direct_t_score = min(direct_t_score / self.cfg.K_NEIGHBOR_CAP, 1.0)
        
        # 加权网络距离
        distances_t = []
        for t in T_set:
            dist = dist_from_g.get(t, float("inf"))
            if dist == float("inf"):
                distances_t.append(0.0)
            else:
                # 距离价值 = 距离倒数 × T 基因权重
                weighted_dist = (1.0 / (1.0 + dist)) * (min(T_weights.get(t, 1), 3) / 3.0)
                distances_t.append(weighted_dist)
        proximity_t = np.mean(distances_t) if distances_t else 0.0
        
        return 0.6 * direct_t_score + 0.4 * proximity_t

    def _calc_tissue_score_fast(
        self,
        g: str,
        T_set: Set[str],
        T_weights: Dict[str, int],
        min_dist_to_t: Dict[str, int],
    ) -> float:
        if g in T_set:
            w = T_weights.get(g, 1)
            return 0.5 + 0.5 * (min(w, 3) / 3.0)
        neighbors = set(self.G.neighbors(g))
        direct_t = neighbors & T_set
        direct_t_score = sum(min(T_weights.get(t, 1), 3) / 3.0 for t in direct_t)
        direct_t_score = min(direct_t_score / self.cfg.K_NEIGHBOR_CAP, 1.0)
        dist = min_dist_to_t.get(g)
        proximity_t = 0.0 if dist is None else 1.0 / (1.0 + dist)
        return 0.6 * direct_t_score + 0.4 * proximity_t
    
    def _calc_topology_score(self, g: str) -> float:
        """全局拓扑评分：degree Z-score + betweenness rank（避免量纲被吞）。"""
        degree = self.G.degree(g)
        degree_z = (degree - self.avg_degree) / self.std_degree
        
        # betweenness rank is precomputed once; building the full array here is expensive at scale.
        bt_rank_pct = self.betweenness_rank_pct.get(g, 0.0)
        
        # sigmoid 压缩 degree_z（避免极端 hub 基因垄断）
        sigmoid_dz = 1.0 / (1.0 + np.exp(-degree_z))
        
        return 0.5 * sigmoid_dz + 0.5 * bt_rank_pct
    
    def get_top_neighbors(self, g: str, D: List[str], T: List[str], T_weights: Dict[str, int]) -> List[Dict]:
        """
        提取基因 g 的 Top N 互作邻居，按 STRING combined_score 排序。
        每个邻居标注：是否属于 D / T / both / none，以及 T_weight。
        """
        if g not in self.G:
            return []
            
        D_set = set(D)
        T_set = set(T)
        neighbors = []
        
        for neighbor in self.G.neighbors(g):
            edge_data = self.G[g][neighbor]
            score = edge_data.get("combined_score", 0)
            
            flags = []
            if neighbor in D_set:
                flags.append("D")
            if neighbor in T_set:
                flags.append("T")
                
            neighbors.append({
                "gene": neighbor,
                "string_score": int(score),
                "flag": "|".join(flags) if flags else "none",
                "t_weight": T_weights.get(neighbor, 0)
            })
            
        # 排序：先按 STRING score 降序，再按 T_weight 降序（组织核心优先展示）
        neighbors.sort(key=lambda x: (x["string_score"], x["t_weight"]), reverse=True)
        return neighbors[:self.cfg.TOP_N_NEIGHBORS]


# ========================= 6. 主流程控制器 =========================

class RareDiseasePPIScorer:
    """
    主控制器：串联 ID 标准化 -> HPO 映射 -> D 集 -> T 集 -> PPI 评分 -> 输出。
    """
    
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.id_std = IDStandardizer(cfg)
        self.hpo_mapper = HPOMapper(cfg)
        self.disease_builder = DiseaseModuleBuilder(cfg, self.id_std)
        self.tissue_builder = TissueModuleBuilder(cfg, self.id_std)
        self.ppi_engine = PPIEngine(cfg, self.id_std)
        self.tissue_builder.ppi_engine = self.ppi_engine
        self.last_audit = {}
        
    def initialize(self):
        """顺序加载所有数据库。耗时操作集中在此。"""
        log("=" * 60)
        log("罕见病双轴 PPI 评分框架 - 初始化")
        log("=" * 60)
        self.id_std.load()
        self.hpo_mapper.load()
        self.disease_builder.hpo_names = self.hpo_mapper.hpo_names
        self.disease_builder.load()
        self.ppi_engine.load()
        self.tissue_builder.load()
        log("[系统] 所有模块初始化完成\n")
        
    def run(
        self,
        candidate_genes: List[str],
        hpo_ids: List[str],
        assume_hgnc_standardized: bool = True,
    ) -> pd.DataFrame:
        """
        主入口。
        
        参数:
            candidate_genes: HGNC 标准化后的候选基因 SYMBOL 列表
            hpo_ids: 患者 HPO ID 列表（如 ["HP:0000488", "HP:0000505"]）
            
        返回:
            DataFrame: 包含 ppi_final, disease_score, tissue_score, topology_score, 
                      D/T 集审计信息, top_neighbors (JSON), note 等列
        """
        # Step 1: 输入基因清洗；默认假定为 HGNC 标准名，也可通过参数启用别名标准化。
        raw_genes = [_clean_str(g) for g in candidate_genes or []]
        raw_genes = [g for g in raw_genes if g]
        G = _unique_preserve_order(raw_genes if assume_hgnc_standardized else self.id_std.standardize(raw_genes))
        log(f"[输入] 候选基因数: {len(G)}")
        if not G:
            return pd.DataFrame(columns=[
                "gene", "in_network", "disease_score", "tissue_score", "topology_score",
                "ppi_final", "score_mode", "score_weight_sum", "note",
                "gene_in_d", "gene_d_evidence_score", "gene_d_sources_json",
                "gene_in_t", "gene_t_weight", "gene_t_layers_json", "gene_t_tissues_json",
                "mapped_tissues_json", "d_gene_count", "t_gene_count",
                "top_neighbors_json", "top_neighbors_count",
            ])

        hpo_ids = normalize_hpo_ids(hpo_ids, deduplicate=False)
        log(f"[输入] HPO 数: {len(hpo_ids)}")
        
        # Step 2: 构建 D 集（疾病轴）。D 轴始终使用完整 HPO 输入，不受组织映射过滤影响。
        D, D_evidence = self.disease_builder.build(hpo_ids, self.hpo_mapper)
        log(f"[D集] 疾病模块基因数: {len(D)}")

        # Step 3: HPO -> 组织，仅用于 T 轴组织投票。
        tissues = self.hpo_mapper.map(hpo_ids)
        tissues = _unique_preserve_order(tissues)
        tissue_counts = getattr(self.hpo_mapper, "last_tissue_counts", {})
        hpo_tissue_map = getattr(self.hpo_mapper, "last_hpo_tissue_map", {})
        log(f"[HPO] 映射到组织 Top3: {tissues}")
        
        # Step 4: 构建 T 集（组织核心轴）
        T, T_weights = self.tissue_builder.build(tissues)
        log(f"[T集] 组织核心基因数: {len(T)}")

        D_set = set(D)
        T_set = set(T)
        T_evidence = getattr(self.tissue_builder, "last_t_evidence", {})
        D_anchor_evidence = {g: D_evidence.get(g, {}) for g in D}
        mapped_tissues_json = json.dumps(tissues, ensure_ascii=False)
        self.last_audit = {
            "input": {
                "candidate_gene": len(G),
                "candidate_gene_count": len(G),
                "candidate_genes": G,
                "hpo_count": len(hpo_ids),
                "hpo_ids": hpo_ids,
            },
            "mapped_tissues": tissues,
            "mapped_tissue_counts": tissue_counts,
            "hpo_tissue_map": hpo_tissue_map,
            "disease": {
                "gene_count": len(D),
                "genes": D,
                "evidence": D_anchor_evidence,
            },
            "tissue": {
                "gene_count": len(T),
                "genes": T,
                "weights": T_weights,
                "evidence": T_evidence,
            },
        }
        
        # Step 5: 双轴评分
        records = self.ppi_engine.score_genes_batch(G, D, T, T_weights)
        include_neighbors = self.cfg.TOP_N_NEIGHBORS > 0
        for score_dict in records:
            g = score_dict["gene"]
            top_n = self.ppi_engine.get_top_neighbors(g, D, T, T_weights) if include_neighbors else []
            d_gene_evidence = D_evidence.get(g, {}) if g in D_set else {}
            t_gene_evidence = T_evidence.get(g, {})
            
            # 将 Top 25 邻居序列化为 JSON 字符串存入 DataFrame
            score_dict["gene_in_d"] = g in D_set
            score_dict["gene_d_evidence_score"] = float(d_gene_evidence.get("evidence_score", 0.0))
            score_dict["gene_d_sources_json"] = json.dumps(d_gene_evidence.get("sources", []), ensure_ascii=False)
            score_dict["gene_in_t"] = g in T_set
            score_dict["gene_t_weight"] = int(T_weights.get(g, 0))
            score_dict["gene_t_layers_json"] = json.dumps(t_gene_evidence.get("layers", []), ensure_ascii=False)
            score_dict["gene_t_tissues_json"] = json.dumps(t_gene_evidence.get("tissues", []), ensure_ascii=False)
            score_dict["mapped_tissues_json"] = mapped_tissues_json
            score_dict["d_gene_count"] = len(D)
            score_dict["t_gene_count"] = len(T)
            score_dict["top_neighbors_json"] = json.dumps(top_n, ensure_ascii=False)
            score_dict["top_neighbors_count"] = len(top_n)
            
        df = pd.DataFrame(records)
        
        return df


def _read_items_file(path: Optional[str]) -> List[str]:
    if not path:
        return []
    items = []
    with open(path, encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            items.extend(x for x in re.split(r"[\s,;]+", line) if x)
    return items


def _params_from_payload(payload: Dict[str, Any]) -> RunParameters:
    return RunParameters(**payload)


def load_run_parameters_from_cli(argv: Optional[List[str]] = None) -> RunParameters:
    parser = argparse.ArgumentParser(description="Rare disease D/T anchor PPI scorer")
    parser.add_argument("--params-json", help="JSON file containing RunParameters fields")
    parser.add_argument("--data-dir")
    parser.add_argument("--candidate-genes", nargs="*")
    parser.add_argument("--candidate-file")
    parser.add_argument("--hpo-ids", nargs="*")
    parser.add_argument("--hpo-file")
    parser.add_argument("--output-csv")
    parser.add_argument("--audit-json")
    parser.add_argument("--no-assume-hgnc-standardized", action="store_true")
    parser.add_argument("--d-min-evidence", type=float)
    parser.add_argument("--d-fallback-evidence", type=float)
    parser.add_argument("--d-broaden-hpo-level", type=int)
    parser.add_argument("--t-gtex-tpm-cutoff", type=float)
    parser.add_argument("--t-tau-cutoff", type=float)
    parser.add_argument("--t-top-n-expr", type=int)
    parser.add_argument("--t-pathway-top-pct", type=int)
    parser.add_argument("--t-pathway-top-n", type=int)
    parser.add_argument("--depmap-effect-cutoff", type=float)
    parser.add_argument("--string-score-cutoff", type=int)
    parser.add_argument("--k-neighbor-cap", type=int)
    parser.add_argument("--top-n-neighbors", type=int)
    parser.add_argument("--string-chunksize", type=int)
    parser.add_argument("--betweenness-sample-k", type=int)
    parser.add_argument("--sssp-cutoff", type=int)
    parser.add_argument("--w-disease", type=float)
    parser.add_argument("--w-tissue", type=float)
    parser.add_argument("--w-topology", type=float)
    parser.add_argument("--load-clinvar", action="store_true")
    args = parser.parse_args(argv)

    payload: Dict[str, Any] = {}
    if args.params_json:
        with open(args.params_json, encoding="utf-8") as handle:
            payload.update(json.load(handle))

    cli_fields = {
        "data_dir": args.data_dir,
        "candidate_genes": args.candidate_genes,
        "candidate_gene_file": args.candidate_file,
        "hpo_ids": args.hpo_ids,
        "hpo_file": args.hpo_file,
        "output_csv": args.output_csv,
        "audit_json": args.audit_json,
        "d_min_evidence": args.d_min_evidence,
        "d_fallback_evidence": args.d_fallback_evidence,
        "d_broaden_hpo_level": args.d_broaden_hpo_level,
        "t_gtex_tpm_cutoff": args.t_gtex_tpm_cutoff,
        "t_tau_cutoff": args.t_tau_cutoff,
        "t_top_n_expr": args.t_top_n_expr,
        "t_pathway_top_pct": args.t_pathway_top_pct,
        "t_pathway_top_n": args.t_pathway_top_n,
        "depmap_effect_cutoff": args.depmap_effect_cutoff,
        "string_score_cutoff": args.string_score_cutoff,
        "k_neighbor_cap": args.k_neighbor_cap,
        "top_n_neighbors": args.top_n_neighbors,
        "string_chunksize": args.string_chunksize,
        "betweenness_sample_k": args.betweenness_sample_k,
        "sssp_cutoff": args.sssp_cutoff,
        "w_disease": args.w_disease,
        "w_tissue": args.w_tissue,
        "w_topology": args.w_topology,
    }
    payload.update({k: v for k, v in cli_fields.items() if v not in (None, [])})
    if args.no_assume_hgnc_standardized:
        payload["assume_hgnc_standardized"] = False
    if args.load_clinvar:
        payload["load_clinvar"] = True

    params = _params_from_payload(payload)
    params.candidate_genes = _unique_preserve_order(list(params.candidate_genes) + _read_items_file(params.candidate_gene_file))
    params.hpo_ids = normalize_hpo_ids(list(params.hpo_ids) + _read_items_file(params.hpo_file), deduplicate=False)
    validate_run_parameters(params)
    return params


def main(argv: Optional[List[str]] = None) -> int:
    params = load_run_parameters_from_cli(argv)
    if not params.candidate_genes:
        raise SystemExit("candidate_genes 不能为空；使用 --candidate-genes 或 --candidate-file。")
    if not params.hpo_ids:
        log("[输入警告] HPO 为空，D/T 轴可能为空，最终可能退化为 TOPOLOGY_ONLY。")

    cfg = config_from_run_parameters(params)
    scorer = RareDiseasePPIScorer(cfg)
    scorer.initialize()
    df = scorer.run(
        candidate_genes=params.candidate_genes,
        hpo_ids=params.hpo_ids,
        assume_hgnc_standardized=params.assume_hgnc_standardized,
    )

    if params.output_csv:
        output_dir = os.path.dirname(os.path.abspath(params.output_csv))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        df.to_csv(params.output_csv, index=False)
        log(f"[输出] {params.output_csv}")
    if params.audit_json:
        audit_dir = os.path.dirname(os.path.abspath(params.audit_json))
        if audit_dir:
            os.makedirs(audit_dir, exist_ok=True)
        with open(params.audit_json, "w", encoding="utf-8") as handle:
            json.dump(scorer.last_audit, handle, ensure_ascii=False, indent=2)
        log(f"[审计输出] {params.audit_json}")
    if params.output_csv:
        return 0
    else:
        print(df.to_json(orient="records", force_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
