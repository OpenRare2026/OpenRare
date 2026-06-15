#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared configuration and request parameter models for the PPI scorer."""

import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, ConfigDict, Field as PydanticField, field_validator
except ImportError:
    BaseModel = None
    ConfigDict = None
    PydanticField = None
    field_validator = None


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_DATA_DIR = os.environ.get("RARE_PPI_DATA_DIR", os.path.join(PROJECT_DIR, "data"))
DEFAULT_CACHE_DIR = os.environ.get("RARE_PPI_CACHE_DIR", os.path.join(DEFAULT_DATA_DIR, "cache"))


class Config:
    """Runtime configuration for rare disease D/T anchor PPI scoring."""

    DATA_DIR = DEFAULT_DATA_DIR
    CACHE_DIR = DEFAULT_CACHE_DIR
    PATH_HGNC = os.path.join(DATA_DIR, "hgnc_complete_set.txt")
    PATH_ENSEMBL_BIOMART = os.path.join(DATA_DIR, "ensembl_biomart_export.txt")
    PATH_UNIPROT_MAPPING = os.path.join(DATA_DIR, "idmapping_selected.tab.gz")
    PATH_OMIM_MIM2GENE = os.path.join(DATA_DIR, "mim2gene.txt")
    PATH_OMIM_GENEMAP = os.path.join(DATA_DIR, "genemap2.txt")
    PATH_HPO_ANNOTATION = os.path.join(DATA_DIR, "phenotype.hpoa")
    PATH_HPO_GENES = os.path.join(DATA_DIR, "genes_to_phenotype.txt")
    PATH_HPO_OBO = os.path.join(DATA_DIR, "hp.obo")
    PATH_HP_FULL_OWL = os.path.join(DATA_DIR, "hp-full.owl")
    PATH_HPO_UBERON_MAP = os.path.join(DATA_DIR, "phenotype_to_anatomy.txt")
    PATH_UBERON_OBO = os.path.join(DATA_DIR, "uberon.obo")
    PATH_ORPHANET = os.path.join(DATA_DIR, "en_product6.xml")
    PATH_CLINVAR = os.path.join(DATA_DIR, "variant_summary.txt.gz")
    PATH_PANELAPP = os.path.join(DATA_DIR, "panelapp_panels.json")
    PATH_GTEX = os.path.join(DATA_DIR, "GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.gct.gz")
    PATH_HPA_RNA = os.path.join(DATA_DIR, "rna_tissue_consensus.tsv")
    PATH_HPA_PROTEIN = os.path.join(DATA_DIR, "normal_ihc_data.tsv")
    PATH_DEPMAP = os.path.join(DATA_DIR, "CRISPRGeneEffect.csv")
    PATH_DEPMAP_MODEL = os.path.join(DATA_DIR, "Model.csv")
    PATH_REACTOME_GENESET = os.path.join(DATA_DIR, "Ensembl2Reactome.txt")
    PATH_REACTOME_HIERARCHY = os.path.join(DATA_DIR, "ReactomePathwaysRelation.txt")
    PATH_STRING_LINKS = os.path.join(DATA_DIR, "9606.protein.links.detailed.v12.0.txt.gz")
    PATH_STRING_INFO = os.path.join(DATA_DIR, "9606.protein.info.v12.0.txt.gz")

    D_MIN_EVIDENCE = 2.0
    D_FALLBACK_EVIDENCE = 1.0
    D_BROADEN_HPO_LEVEL = 2
    SOURCE_WEIGHTS = {
        "omim": 1.0,
        "orpha": 0.8,
        "clinvar": 0.6,
        "hpo_genes": 0.3,
        "panelapp": 0.9,
    }

    T_GTEX_TPM_CUTOFF = 5.0
    T_TAU_CUTOFF = 0.7
    T_TOP_N_EXPR = 500
    T_PATHWAY_TOP_PCT = 70
    T_PATHWAY_TOP_N = 20

    STRING_SCORE_CUTOFF = 400

    W_DISEASE = 0.30
    W_TISSUE = 0.45
    W_TOPOLOGY = 0.25

    K_NEIGHBOR_CAP = 5
    TOP_N_NEIGHBORS = 25
    STRING_CHUNKSIZE = 500_000
    BETWEENNESS_SAMPLE_K = 200
    SSSP_CUTOFF = 4
    DEPMAP_EFFECT_CUTOFF = -0.5
    LOAD_CLINVAR = os.environ.get("RARE_PPI_LOAD_CLINVAR", "0") == "1"

    _PATH_ATTRS = (
        "PATH_HGNC", "PATH_ENSEMBL_BIOMART", "PATH_UNIPROT_MAPPING",
        "PATH_OMIM_MIM2GENE", "PATH_OMIM_GENEMAP", "PATH_HPO_ANNOTATION",
        "PATH_HPO_GENES", "PATH_HPO_OBO", "PATH_HP_FULL_OWL", "PATH_HPO_UBERON_MAP",
        "PATH_UBERON_OBO", "PATH_ORPHANET", "PATH_CLINVAR", "PATH_PANELAPP",
        "PATH_GTEX", "PATH_HPA_RNA", "PATH_HPA_PROTEIN", "PATH_DEPMAP",
        "PATH_DEPMAP_MODEL", "PATH_REACTOME_GENESET", "PATH_REACTOME_HIERARCHY",
        "PATH_STRING_LINKS", "PATH_STRING_INFO",
    )
    _OVERRIDABLE = (
        "D_MIN_EVIDENCE", "D_FALLBACK_EVIDENCE", "D_BROADEN_HPO_LEVEL", "SOURCE_WEIGHTS",
        "T_GTEX_TPM_CUTOFF", "T_TAU_CUTOFF", "T_TOP_N_EXPR",
        "T_PATHWAY_TOP_PCT", "T_PATHWAY_TOP_N", "STRING_SCORE_CUTOFF",
        "W_DISEASE", "W_TISSUE", "W_TOPOLOGY", "K_NEIGHBOR_CAP",
        "TOP_N_NEIGHBORS", "STRING_CHUNKSIZE", "BETWEENNESS_SAMPLE_K",
        "SSSP_CUTOFF", "DEPMAP_EFFECT_CUTOFF", "LOAD_CLINVAR",
    )

    def __init__(self, data_dir: Optional[str] = None, **overrides):
        self.DATA_DIR = data_dir or DEFAULT_DATA_DIR
        self._refresh_paths()
        for name in self._OVERRIDABLE:
            setattr(self, name, overrides.get(name, getattr(type(self), name)))

    def _refresh_paths(self):
        self.CACHE_DIR = os.environ.get("RARE_PPI_CACHE_DIR", os.path.join(self.DATA_DIR, "cache"))
        self.PATH_HGNC = os.path.join(self.DATA_DIR, "hgnc_complete_set.txt")
        self.PATH_ENSEMBL_BIOMART = os.path.join(self.DATA_DIR, "ensembl_biomart_export.txt")
        self.PATH_UNIPROT_MAPPING = os.path.join(self.DATA_DIR, "idmapping_selected.tab.gz")
        self.PATH_OMIM_MIM2GENE = os.path.join(self.DATA_DIR, "mim2gene.txt")
        self.PATH_OMIM_GENEMAP = os.path.join(self.DATA_DIR, "genemap2.txt")
        self.PATH_HPO_ANNOTATION = os.path.join(self.DATA_DIR, "phenotype.hpoa")
        self.PATH_HPO_GENES = os.path.join(self.DATA_DIR, "genes_to_phenotype.txt")
        self.PATH_HPO_OBO = os.path.join(self.DATA_DIR, "hp.obo")
        self.PATH_HP_FULL_OWL = os.path.join(self.DATA_DIR, "hp-full.owl")
        self.PATH_HPO_UBERON_MAP = os.path.join(self.DATA_DIR, "phenotype_to_anatomy.txt")
        self.PATH_UBERON_OBO = os.path.join(self.DATA_DIR, "uberon.obo")
        self.PATH_ORPHANET = os.path.join(self.DATA_DIR, "en_product6.xml")
        self.PATH_CLINVAR = os.path.join(self.DATA_DIR, "variant_summary.txt.gz")
        self.PATH_PANELAPP = os.path.join(self.DATA_DIR, "panelapp_panels.json")
        self.PATH_GTEX = os.path.join(self.DATA_DIR, "GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.gct.gz")
        self.PATH_HPA_RNA = os.path.join(self.DATA_DIR, "rna_tissue_consensus.tsv")
        self.PATH_HPA_PROTEIN = os.path.join(self.DATA_DIR, "normal_ihc_data.tsv")
        self.PATH_DEPMAP = os.path.join(self.DATA_DIR, "CRISPRGeneEffect.csv")
        self.PATH_DEPMAP_MODEL = os.path.join(self.DATA_DIR, "Model.csv")
        self.PATH_REACTOME_GENESET = os.path.join(self.DATA_DIR, "Ensembl2Reactome.txt")
        self.PATH_REACTOME_HIERARCHY = os.path.join(self.DATA_DIR, "ReactomePathwaysRelation.txt")
        self.PATH_STRING_LINKS = os.path.join(self.DATA_DIR, "9606.protein.links.detailed.v12.0.txt.gz")
        self.PATH_STRING_INFO = os.path.join(self.DATA_DIR, "9606.protein.info.v12.0.txt.gz")

    def to_dict(self, include_paths: bool = True) -> Dict[str, Any]:
        data = {"DATA_DIR": self.DATA_DIR, "CACHE_DIR": self.CACHE_DIR}
        if include_paths:
            data.update({name: getattr(self, name) for name in self._PATH_ATTRS})
        data.update({name: getattr(self, name) for name in self._OVERRIDABLE})
        return data

    def missing_files(self) -> List[str]:
        return [path for path in (getattr(self, name) for name in self._PATH_ATTRS) if not os.path.exists(path)]


if BaseModel is not None:
    class RunParameters(BaseModel):
        model_config = ConfigDict(extra="forbid")

        data_dir: str = PydanticField(default_factory=lambda: DEFAULT_DATA_DIR)
        candidate_genes: List[str] = PydanticField(default_factory=list)
        candidate_gene_file: Optional[str] = None
        hpo_ids: List[str] = PydanticField(default_factory=list)
        hpo_file: Optional[str] = None
        output_csv: Optional[str] = None
        audit_json: Optional[str] = None
        include_audit: bool = False
        assume_hgnc_standardized: bool = True

        d_min_evidence: float = Config.D_MIN_EVIDENCE
        d_fallback_evidence: float = Config.D_FALLBACK_EVIDENCE
        d_broaden_hpo_level: int = Config.D_BROADEN_HPO_LEVEL
        source_weights: Dict[str, float] = PydanticField(default_factory=lambda: dict(Config.SOURCE_WEIGHTS))
        t_gtex_tpm_cutoff: float = Config.T_GTEX_TPM_CUTOFF
        t_tau_cutoff: float = Config.T_TAU_CUTOFF
        t_top_n_expr: int = Config.T_TOP_N_EXPR
        t_pathway_top_pct: int = Config.T_PATHWAY_TOP_PCT
        t_pathway_top_n: int = Config.T_PATHWAY_TOP_N
        depmap_effect_cutoff: float = Config.DEPMAP_EFFECT_CUTOFF
        string_score_cutoff: int = Config.STRING_SCORE_CUTOFF
        k_neighbor_cap: int = Config.K_NEIGHBOR_CAP
        top_n_neighbors: int = Config.TOP_N_NEIGHBORS
        string_chunksize: int = Config.STRING_CHUNKSIZE
        betweenness_sample_k: int = Config.BETWEENNESS_SAMPLE_K
        sssp_cutoff: int = Config.SSSP_CUTOFF
        w_disease: float = Config.W_DISEASE
        w_tissue: float = Config.W_TISSUE
        w_topology: float = Config.W_TOPOLOGY
        load_clinvar: bool = Config.LOAD_CLINVAR

        @field_validator("candidate_genes", "hpo_ids", mode="before")
        @classmethod
        def _listify(cls, value):
            if value is None:
                return []
            if isinstance(value, str):
                return [x for x in re.split(r"[\s,;]+", value.strip()) if x]
            return value

        @field_validator("candidate_genes")
        @classmethod
        def _validate_candidate_genes(cls, value):
            return value

        @field_validator("hpo_ids")
        @classmethod
        def _validate_hpo_ids(cls, value):
            invalid = [x for x in value if not re.fullmatch(r"(HP:)?\d{1,7}", str(x).upper().replace("_", ":"))]
            if invalid:
                raise ValueError(f"hpo_ids 包含非法 HPO ID: {invalid[:5]}")
            return value

        @field_validator(
            "d_min_evidence", "d_fallback_evidence", "t_gtex_tpm_cutoff", "t_tau_cutoff",
            "depmap_effect_cutoff", "w_disease", "w_tissue", "w_topology", mode="after"
        )
        @classmethod
        def _validate_float_finite(cls, value):
            if not math.isfinite(float(value)):
                raise ValueError("参数必须是有限数值")
            return value

        @field_validator(
            "d_broaden_hpo_level", "t_top_n_expr", "t_pathway_top_pct", "string_score_cutoff",
            "t_pathway_top_n", "k_neighbor_cap", "top_n_neighbors", "string_chunksize",
            "betweenness_sample_k", "sssp_cutoff"
        )
        @classmethod
        def _validate_positive_int(cls, value):
            if int(value) < 0:
                raise ValueError("整数参数不能为负数")
            return value
else:
    @dataclass
    class RunParameters:
        data_dir: str = DEFAULT_DATA_DIR
        candidate_genes: List[str] = field(default_factory=list)
        candidate_gene_file: Optional[str] = None
        hpo_ids: List[str] = field(default_factory=list)
        hpo_file: Optional[str] = None
        output_csv: Optional[str] = None
        audit_json: Optional[str] = None
        include_audit: bool = False
        assume_hgnc_standardized: bool = True
        d_min_evidence: float = Config.D_MIN_EVIDENCE
        d_fallback_evidence: float = Config.D_FALLBACK_EVIDENCE
        d_broaden_hpo_level: int = Config.D_BROADEN_HPO_LEVEL
        source_weights: Dict[str, float] = field(default_factory=lambda: dict(Config.SOURCE_WEIGHTS))
        t_gtex_tpm_cutoff: float = Config.T_GTEX_TPM_CUTOFF
        t_tau_cutoff: float = Config.T_TAU_CUTOFF
        t_top_n_expr: int = Config.T_TOP_N_EXPR
        t_pathway_top_pct: int = Config.T_PATHWAY_TOP_PCT
        t_pathway_top_n: int = Config.T_PATHWAY_TOP_N
        depmap_effect_cutoff: float = Config.DEPMAP_EFFECT_CUTOFF
        string_score_cutoff: int = Config.STRING_SCORE_CUTOFF
        k_neighbor_cap: int = Config.K_NEIGHBOR_CAP
        top_n_neighbors: int = Config.TOP_N_NEIGHBORS
        string_chunksize: int = Config.STRING_CHUNKSIZE
        betweenness_sample_k: int = Config.BETWEENNESS_SAMPLE_K
        sssp_cutoff: int = Config.SSSP_CUTOFF
        w_disease: float = Config.W_DISEASE
        w_tissue: float = Config.W_TISSUE
        w_topology: float = Config.W_TOPOLOGY
        load_clinvar: bool = Config.LOAD_CLINVAR


def config_from_run_parameters(params: RunParameters) -> Config:
    """Convert API/CLI request parameters into the internal Config object."""
    return Config(
        data_dir=params.data_dir,
        D_MIN_EVIDENCE=params.d_min_evidence,
        D_FALLBACK_EVIDENCE=params.d_fallback_evidence,
        D_BROADEN_HPO_LEVEL=params.d_broaden_hpo_level,
        SOURCE_WEIGHTS=params.source_weights,
        T_GTEX_TPM_CUTOFF=params.t_gtex_tpm_cutoff,
        T_TAU_CUTOFF=params.t_tau_cutoff,
        T_TOP_N_EXPR=params.t_top_n_expr,
        T_PATHWAY_TOP_PCT=params.t_pathway_top_pct,
        T_PATHWAY_TOP_N=params.t_pathway_top_n,
        DEPMAP_EFFECT_CUTOFF=params.depmap_effect_cutoff,
        STRING_SCORE_CUTOFF=params.string_score_cutoff,
        K_NEIGHBOR_CAP=params.k_neighbor_cap,
        TOP_N_NEIGHBORS=params.top_n_neighbors,
        STRING_CHUNKSIZE=params.string_chunksize,
        BETWEENNESS_SAMPLE_K=params.betweenness_sample_k,
        SSSP_CUTOFF=params.sssp_cutoff,
        W_DISEASE=params.w_disease,
        W_TISSUE=params.w_tissue,
        W_TOPOLOGY=params.w_topology,
        LOAD_CLINVAR=params.load_clinvar,
    )


def validate_run_parameters(params: RunParameters):
    """Validate merged CLI/API parameters."""
    weights = [params.w_disease, params.w_tissue, params.w_topology]
    if any(float(w) < 0 for w in weights):
        raise ValueError("w_disease/w_tissue/w_topology 不能为负数")
    if sum(float(w) for w in weights) <= 0:
        raise ValueError("w_disease/w_tissue/w_topology 至少需要一个正权重")
    if not (0 <= float(params.t_tau_cutoff) <= 1):
        raise ValueError("t_tau_cutoff 必须在 0-1 之间")
    if not (0 <= int(params.t_pathway_top_pct) <= 100):
        raise ValueError("t_pathway_top_pct 必须在 0-100 之间")
    if not (0 <= int(params.string_score_cutoff) <= 1000):
        raise ValueError("string_score_cutoff 必须在 0-1000 之间")
    positive_ints = {
        "t_top_n_expr": params.t_top_n_expr,
        "t_pathway_top_n": params.t_pathway_top_n,
        "k_neighbor_cap": params.k_neighbor_cap,
        "string_chunksize": params.string_chunksize,
        "betweenness_sample_k": params.betweenness_sample_k,
    }
    for name, value in positive_ints.items():
        if int(value) <= 0:
            raise ValueError(f"{name} 必须为正整数")
    if int(params.sssp_cutoff) < 0:
        raise ValueError("sssp_cutoff 不能为负数；0 表示不截断")
    for name, value in getattr(params, "source_weights", {}).items():
        if float(value) < 0:
            raise ValueError(f"source_weights[{name}] 不能为负数")
