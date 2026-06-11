#!/usr/bin/env python3
"""
Build the *deterministic* part of a rare-disease candidate-gene report.

Design contract
---------------
The report backbone is the candidate GENE. Genes are ordered strictly by their
best (minimum) ``pathogenic_rank`` in the wide table. We keep the top-N genes
(default 10) OR a user-supplied gene list (``--genes`` overrides ``--top-n``),
and inside each gene we show its top-K variants by ``pathogenic_rank``.

Every hard number (coordinates, frequencies, IDs, scores) is rendered HERE, from
the CSVs. The language model only fills the ``{{narrative:...}}`` slots, so it
can never transcribe a frequency or an OMIM id wrong. That split is the whole
anti-hallucination mechanism.

The wide table is the main line. Phenotype and PPI tables are *supplementary*,
joined on the gene symbol; a gene with no row there gets a "no data" note. Each
data source is its own small provider class, so when a supplementary pipeline
later merges into the wide-table pipeline you can drop a provider without
touching the composer.

Outputs (written to --outdir):
  report.md              full document, with {{narrative:<slot>}} placeholders
  narrative_context.json per-slot grounding: instruction + structured context +
                         ``ground_text`` (the deterministic text the slot must
                         not contradict; validate_narrative.py checks against it)
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

DASH = "—"  # printed for a missing value
MAX_VARIANT_LEN = 50  # truncate long HGVS strings for PDF table display


# ----------------------------- formatting helpers -----------------------------
def _s(x) -> str:
    """Normalize any cell to a clean string; missing markers -> ''."""
    if x is None:
        return ""
    s = str(x).strip()
    if s.lower() in ("", "-", "nan", "none", "null"):
        return ""
    return s


def fmt_af(x) -> str:
    s = _s(x)
    if not s:
        return DASH
    try:
        v = float(s)
    except ValueError:
        return s
    if v == 0:
        return "0"
    if v < 1e-3:
        return f"{v:.2e}"
    return f"{v:.4g}"


def fmt_id(x, prefix: str = "") -> str:
    """265000.0 -> '265000'; '' for missing. Optional prefix like 'OMIM:'."""
    s = _s(x)
    if not s:
        return ""
    try:
        f = float(s)
        if f.is_integer():
            s = str(int(f))
    except ValueError:
        pass
    return f"{prefix}{s}" if prefix else s


def fmt_score(x, dp: int = 3) -> str:
    """Round a 0-1 style score for display; raw value stays in llm_context."""
    s = _s(x)
    if not s:
        return DASH
    try:
        v = float(s)
    except ValueError:
        return s
    return ("%.*f" % (dp, v)).rstrip("0").rstrip(".") or "0"


def short_consequence(x) -> str:
    """A variant row may carry a comma-joined consequence list; keep it compact."""
    s = _s(x)
    if not s:
        return DASH
    parts = [p for p in s.split(",") if p]
    return parts[0] if len(parts) <= 1 else f"{parts[0]} (+{len(parts) - 1})"


def md_table(headers, rows) -> str:
    """Render a markdown table, dropping columns empty for every row (schema-driven)."""
    keep = [i for i, _ in enumerate(headers)
            if any(_s(r[i]) for r in rows)] or list(range(len(headers)))
    h = [headers[i] for i in keep]
    body = [[(_s(r[i]) or DASH) for i in keep] for r in rows]
    out = ["| " + " | ".join(h) + " |",
           "| " + " | ".join("---" for _ in h) + " |"]
    out += ["| " + " | ".join(c for c in r) + " |" for r in body]
    return "\n".join(out)


def _json_load(x):
    s = _s(x)
    if not s:
        return None
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        return None


# --------------------------------- providers ----------------------------------
class WideTableProvider:
    """Main line. Per-variant rows; drives gene selection and ordering."""
    GENE = "gene_symbol"
    RANK = "pathogenic_rank"

    def __init__(self, path):
        self.df = pd.read_csv(path, dtype=str, low_memory=False)
        if self.RANK in self.df.columns:
            self.df[self.RANK] = pd.to_numeric(self.df[self.RANK], errors="coerce")
        else:
            self.df[self.RANK] = pd.NA
        self.df = self.df[self.df[self.GENE].map(lambda g: bool(_s(g)))]

    def select_genes(self, top_n, gene_list):
        best = (self.df.dropna(subset=[self.RANK])
                .groupby(self.GENE)[self.RANK].min().sort_values())
        if gene_list:                       # explicit list overrides top-n
            return sorted(gene_list, key=lambda g: best.get(g, 1e18))
        return list(best.head(top_n).index)

    def gene_best_rank(self, gene):
        sub = self.df[self.df[self.GENE] == gene][self.RANK]
        return int(sub.min()) if sub.notna().any() else None

    def variants(self, gene, k):
        return self.df[self.df[self.GENE] == gene].sort_values(self.RANK).head(k)

    def variant_block(self, gene, k):
        sub = self.variants(gene, k)
        if not len(sub):
            return "_宽表中未找到该基因的变异。_"
        headers = ["rank", "变异", "consequence", "impact",
                   "REVEL", "CADD", "gnomAD popmax", "ClinVar"]
        rows = []
        for _, r in sub.iterrows():
            variant = _s(r.get("hgvsp")) or _s(r.get("hgvsc")) or \
                f"{_s(r.get('chrom'))}:{_s(r.get('pos'))} {_s(r.get('ref'))}>{_s(r.get('alt'))}"
            if len(variant) > MAX_VARIANT_LEN:
                variant = variant[:MAX_VARIANT_LEN - 1] + "…"
            clinvar = _s(r.get("clinvar_significance"))
            star = _s(r.get("clinvar_star_rating"))
            if clinvar and star:
                clinvar = f"{clinvar} ({_s(star).replace('.0', '')}★)"
            rows.append([
                _s(r.get(self.RANK)).replace(".0", ""),
                variant,
                short_consequence(r.get("consequence")),
                _s(r.get("impact")),
                _s(r.get("revel_score")),
                _s(r.get("cadd_phred")),
                fmt_af(r.get("gnomAD_popmax_AF")),
                clinvar,
            ])
        return md_table(headers, rows)

    def llm_context(self, gene, k):
        sub = self.variants(gene, k)
        cols = ["pathogenic_rank", "consequence", "impact", "hgvsc", "hgvsp",
                "revel_score", "cadd_phred", "gnomAD_popmax_AF", "gnomAD_eas_AF",
                "spliceAI_ds_max", "spliceAI_type", "loftee_lof_flag",
                "clinvar_significance", "clinvar_star_rating", "evidence_summary"]
        cols = [c for c in cols if c in sub.columns]
        return sub[cols].to_dict("records")


class PhenotypeProvider:
    """Supplementary. Per-gene phenotype/HPO match score. Joined on gene_symbol."""
    GENE = "gene_symbol"

    def __init__(self, path):
        self.df = pd.read_csv(path, dtype=str, low_memory=False) if path else None

    def _row(self, gene):
        if self.df is None:
            return None
        m = self.df[self.df[self.GENE] == gene]
        return m.iloc[0] if len(m) else None

    def block(self, gene):
        r = self._row(gene)
        if r is None:
            return None
        disease = _s(r.get("best_disease_name")) or DASH
        ids = [fmt_id(r.get("best_omim_id"), "OMIM:"),
               fmt_id(r.get("best_orpha_id"), "ORPHA:"),
               _s(r.get("best_mondo_id"))]
        ids = " / ".join(i for i in ids if i)
        lines = [
            f"- **表型匹配分**：{fmt_score(r.get('gene_score'))}"
            f"（{_s(r.get('conclusion_code')) or DASH}）",
            f"- **最佳匹配疾病**：{disease}" + (f"（{ids}）" if ids else ""),
            f"- **HPO 命中 / 未命中**：{_s(r.get('matched_hpo_count')) or DASH}"
            f" / {_s(r.get('unmatched_hpo_count')) or DASH}",
        ]
        ev = _s(r.get("best_term_evidence_summary"))
        if ev:
            items = [seg.strip() for seg in ev.replace(";", "\n").split("\n") if seg.strip()][:8]
            if items:
                lines.append("- **逐项 HPO 匹配**（patient→disease:similarity）：")
                lines += [f"    - `{it}`" for it in items]
        return "\n".join(lines)

    def llm_context(self, gene):
        r = self._row(gene)
        if r is None:
            return {"present": False}
        keep = ["gene_score", "conclusion_code", "best_disease_name",
                "best_omim_id", "best_mondo_id", "matched_hpo_count",
                "unmatched_hpo_count", "disease_profile_count"]
        return {"present": True, **{k: _s(r.get(k)) for k in keep if k in r.index}}


class PPIProvider:
    """Supplementary. Per-gene PPI network priority. Joined on gene."""
    GENE = "gene"

    def __init__(self, path):
        self.df = pd.read_csv(path, dtype=str, low_memory=False) if path else None

    def _row(self, gene):
        if self.df is None:
            return None
        m = self.df[self.df[self.GENE] == gene]
        return m.iloc[0] if len(m) else None

    def block(self, gene):
        r = self._row(gene)
        if r is None:
            return None
        lines = [
            f"- **PPI 综合分**：{fmt_score(r.get('ppi_final'))}"
            f"（模式 {_s(r.get('score_mode')) or DASH}）",
            f"- **三轴**：疾病 {fmt_score(r.get('disease_score'))}"
            f" ｜ 组织 {fmt_score(r.get('tissue_score'))}"
            f" ｜ 拓扑 {fmt_score(r.get('topology_score'))}",
            f"- **进入锚点**：D={_s(r.get('gene_in_d')) or DASH}"
            f" ｜ T={_s(r.get('gene_in_t')) or DASH}",
        ]
        tissues = _json_load(r.get("mapped_tissues_json"))
        if tissues:
            lines.append(f"- **映射组织**：{', '.join(map(str, tissues[:6]))}")
        neighbors = _json_load(r.get("top_neighbors_json"))
        if isinstance(neighbors, list) and neighbors:
            names = []
            for n in neighbors[:6]:
                if isinstance(n, dict):
                    nm = n.get("gene") or n.get("name") or n.get("neighbor") or str(n)
                    tag = n.get("flag") or n.get("label") or ""
                    names.append(f"{nm}{f'({tag})' if tag and tag != 'none' else ''}")
                else:
                    names.append(str(n))
            lines.append(f"- **Top STRING 邻居**：{', '.join(names)}")
        return "\n".join(lines)

    def llm_context(self, gene):
        r = self._row(gene)
        if r is None:
            return {"present": False}
        keep = ["ppi_final", "score_mode", "disease_score", "tissue_score",
                "topology_score", "gene_in_d", "gene_in_t", "note"]
        return {"present": True, **{k: _s(r.get(k)) for k in keep if k in r.index}}


# --------------------------------- composer ------------------------------------
def compose(wide, pheno, ppi, genes, k, case_id, hpo_list, symptom_text):
    slots = {}
    parts = []

    parts.append("# 罕见病候选基因分析报告\n")
    parts.append("> 探索性报告，非临床诊断结论。\n")
    meta = [
        f"- **样本**：{case_id or DASH}",
        f"- **候选基因数（本报告）**：{len(genes)}（按宽表 pathogenic_rank 最佳变异排序）",
        f"- **每基因展示变异上限**：{k}",
    ]
    meta.append(f"- **输入 HPO（{len(hpo_list)}）**：{', '.join(hpo_list)}"
                if hpo_list else "- **输入 HPO**：（未提供）")
    parts.append("\n".join(meta) + "\n")

    parts.append("## 临床表型概述\n")
    if symptom_text:
        parts.append(f"> {symptom_text}\n")
    parts.append("{{narrative:phenotype_overview}}\n")
    slots["phenotype_overview"] = {
        "instruction": "用 2-4 句概述患者表型。可解读 HPO 含义，但 HPO ID 已在上方列出，"
                       "不要改写或新增任何 ID。",
        "ground_text": (", ".join(hpo_list) + "\n" + (symptom_text or "")),
        "context": {"hpo_list": hpo_list, "symptom_text": symptom_text or ""},
    }

    parts.append("## 候选基因排序总览\n")
    ov_headers = ["#", "基因", "最佳rank", "顶层变异", "表型分", "PPI分"]
    ov_rows = []
    for i, g in enumerate(genes, 1):
        tv = wide.variants(g, 1)
        cons = short_consequence(tv.iloc[0]["consequence"]) if len(tv) else DASH
        pr = pheno._row(g)
        ppr = ppi._row(g)
        ov_rows.append([
            str(i), g, str(wide.gene_best_rank(g) or DASH), cons,
            (f"{fmt_score(pr.get('gene_score'))}（{_s(pr.get('conclusion_code'))}）" if pr is not None else DASH),
            (f"{fmt_score(ppr.get('ppi_final'))}（{_s(ppr.get('score_mode'))}）" if ppr is not None else DASH),
        ])
    parts.append(md_table(ov_headers, ov_rows) + "\n")

    for i, g in enumerate(genes, 1):
        var_b = wide.variant_block(g, k)
        phe_b = pheno.block(g)
        ppi_b = ppi.block(g)

        parts.append(f"## 候选基因 {i}：{g}\n")
        parts.append(f"### 变异证据（宽表）\n{var_b}\n")
        parts.append("### 表型证据\n" + (phe_b if phe_b else "_本模块无该基因数据。_") + "\n")
        parts.append("### 网络证据（PPI）\n" + (ppi_b if ppi_b else "_本模块无该基因数据。_") + "\n")
        parts.append("### 综合解读\n" + "{{narrative:gene:%s}}\n" % g)

        slots[f"gene:{g}"] = {
            "instruction": ("整合上面三块证据，为该基因写一段解读（3-6 句）。"
                            "只能引用上方已出现的数值，不得新增或改写任何坐标、频率、ID、分数。"
                            "如实说明证据强弱与不确定性：例如顶层变异多为非编码/MODIFIER、"
                            "表型匹配弱、或 gnomAD 频率偏高提示可能为常见多态，都要点出。"),
            "ground_text": "\n".join(t for t in [var_b, phe_b, ppi_b] if t),
            "context": {
                "gene": g,
                "variants": wide.llm_context(g, k),
                "phenotype": pheno.llm_context(g),
                "ppi": ppi.llm_context(g),
            },
        }

    parts.append("## 方法与局限\n")
    parts.append(
        "- 候选基因按宽表 `pathogenic_rank` 的最佳变异严格排序，未做有效性过滤（早期版本）。\n"
        "- 表型分仅表示表型相似度，PPI 分仅表示网络优先级，均非致病性判定。\n"
        "- 本报告为探索性结果，不作为临床诊断依据。\n"
    )
    return "\n".join(parts), slots


def read_hpo(path):
    out = []
    if path and Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


def build(wide_csv, pheno_csv=None, ppi_csv=None, top_n=10, k=5, genes=None,
          case_id=None, hpo_file=None, symptom_text=None):
    """Library entry point used by the FastAPI service. Returns (md, slots, stats)."""
    wide = WideTableProvider(wide_csv)
    pheno = PhenotypeProvider(pheno_csv)
    ppi = PPIProvider(ppi_csv)
    gene_list = ([g.strip() for g in genes.split(",")]
                 if isinstance(genes, str) and genes else genes)
    selected = wide.select_genes(top_n, gene_list)
    hpo_list = read_hpo(hpo_file)
    md, slots = compose(wide, pheno, ppi, selected, k, case_id, hpo_list, symptom_text)
    stats = {
        "genes": selected,
        "pheno_coverage": sum(pheno._row(g) is not None for g in selected),
        "ppi_coverage": sum(ppi._row(g) is not None for g in selected),
    }
    return md, slots, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wide", required=True)
    ap.add_argument("--phenotype", default=None)
    ap.add_argument("--ppi", default=None)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--genes", default=None, help="comma-separated; overrides --top-n")
    ap.add_argument("--case-id", default=None)
    ap.add_argument("--hpo-file", default=None)
    ap.add_argument("--symptom-text", default=None)
    a = ap.parse_args()

    md, slots, stats = build(a.wide, a.phenotype, a.ppi, a.top_n, a.k,
                             a.genes, a.case_id, a.hpo_file, a.symptom_text)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text(md, encoding="utf-8")
    (out / "narrative_context.json").write_text(
        json.dumps(slots, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"genes selected ({len(stats['genes'])}): {stats['genes']}")
    print(f"phenotype coverage: {stats['pheno_coverage']}/{len(stats['genes'])}")
    print(f"ppi coverage:       {stats['ppi_coverage']}/{len(stats['genes'])}")
    print(f"wrote {out/'report.md'} and {out/'narrative_context.json'}")


if __name__ == "__main__":
    main()
