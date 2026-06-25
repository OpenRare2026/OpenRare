from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from report.models import (
    GeneCard,
    ReportContext,
    ReportSummary,
    SampleMeta,
    TopGeneSummary,
    VariantRecord,
)

_VARIANT_KEY_FIELDS = ("chrom", "pos", "ref", "alt")


def _display(value: str | None) -> str:
    text = (value or "").strip()
    return text if text else "-"


def _parse_int(value: str | None) -> int | None:
    text = (value or "").strip()
    if not text or text == "-":
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _row_to_variant(row: dict[str, str]) -> VariantRecord:
    return VariantRecord(
        chrom=_display(row.get("chrom")),
        pos=_display(row.get("pos")),
        ref=_display(row.get("ref")),
        alt=_display(row.get("alt")),
        gene_symbol=_display(row.get("gene_symbol")),
        transcript_id=_display(row.get("transcript_id")),
        refseq_id=_display(row.get("refseq_id")),
        mane_select=_display(row.get("mane_select")),
        consequence=_display(row.get("consequence")),
        impact=_display(row.get("impact")),
        hgvsc=_display(row.get("hgvsc")),
        hgvsp=_display(row.get("hgvsp")),
        exon=_display(row.get("exon")),
        protein_domains=_display(row.get("protein_domains")),
        revel_score=_display(row.get("revel_score")),
        cadd_phred=_display(row.get("cadd_phred")),
        gnomad_popmax_af=_display(row.get("gnomAD_popmax_AF")),
        gnomad_eas_af=_display(row.get("gnomAD_eas_AF")),
        gnomad_nhomalt=_display(row.get("gnomAD_nhomalt")),
        spliceai_ds_max=_display(row.get("spliceAI_ds_max")),
        spliceai_type=_display(row.get("spliceAI_type")),
        loftee_lof_flag=_display(row.get("loftee_lof_flag")),
        clinvar_significance=_display(row.get("clinvar_significance")),
        clinvar_review_status=_display(row.get("clinvar_review_status")),
        clinvar_star_rating=_display(row.get("clinvar_star_rating")),
        vcf_info_af=_display(row.get("vcf_info_AF")),
        vcf_info_dp=_display(row.get("vcf_info_DP")),
        vcf_info_vaf=_display(row.get("vcf_info_VAF")),
        vcf_info_ref_dp=_display(row.get("vcf_info_REF_DP")),
        vcf_info_alt_dp=_display(row.get("vcf_info_ALT_DP")),
        vcf_info_qd=_display(row.get("vcf_info_QD")),
        vcf_info_fs=_display(row.get("vcf_info_FS")),
        vcf_info_mq=_display(row.get("vcf_info_MQ")),
        vcf_info_beagle_phased=_display(row.get("vcf_info_BEAGLE_PHASED")),
        vcf_info_chn_ref_support=_display(row.get("vcf_info_CHN_REF_SUPPORT")),
        vcf_info_chn_alt_carrier_count=_display(row.get("vcf_info_CHN_ALT_CARRIER_COUNT")),
        vcf_info_chn_alt_ac=_display(row.get("vcf_info_CHN_ALT_AC")),
        vcf_info_phasing_confidence=_display(row.get("vcf_info_PHASING_CONFIDENCE")),
        vcf_info_reg_ccre_id=_display(row.get("vcf_info_REG_CCRE_ID")),
        vcf_info_reg_ccre_class=_display(row.get("vcf_info_REG_CCRE_CLASS")),
        vcf_info_reg_ccre_count=_display(row.get("vcf_info_REG_CCRE_COUNT")),
        vcf_info_ncrna_gene_name=_display(row.get("vcf_info_NCRNA_GENE_NAME")),
        vcf_info_ncrna_gene_type=_display(row.get("vcf_info_NCRNA_GENE_TYPE")),
        vcf_info_is_pseudogene=_display(row.get("vcf_info_is_pseudogene")),
        vcf_info_pseudogene_name=_display(row.get("vcf_info_pseudogene_name")),
        vcf_info_pseudogene_source=_display(row.get("vcf_info_pseudogene_source")),
        clinical_best_tissue=_display(row.get("clinical_best_tissue")),
        clinical_transcript_tpm=_display(row.get("clinical_transcript_tpm")),
        gtex_transcript_top5_tissues=_display(row.get("gtex_transcript_top5_tissues")),
        pathogenic_rank=_parse_int(row.get("pathogenic_rank")),
        evidence_summary=_display(row.get("evidence_summary")),
        genos_evee=_display(row.get("GENOS-EVEE")),
    )


def _variant_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return tuple(_display(row.get(field)) for field in _VARIANT_KEY_FIELDS)  # type: ignore[return-value]


def _transcript_score(row: dict[str, str]) -> tuple[int, int, int, int, int]:
    vep_pick = 1 if (row.get("vep_pick") or "").strip() == "1" else 0
    tx_rank = _parse_int(row.get("tx_rank_within_variant")) or 999
    mane_select = 1 if (row.get("mane_select") or "").strip() not in ("", "-") else 0
    pathogenic_rank = _parse_int(row.get("pathogenic_rank")) or 999999
    tx_rank_score = -tx_rank
    return (vep_pick, tx_rank_score, mane_select, -pathogenic_rank, -tx_rank)


def _select_best_row(rows: list[dict[str, str]]) -> dict[str, str]:
    return max(rows, key=_transcript_score)


def load_wide_table_rows(path: str | Path) -> list[dict[str, str]]:
    wide_path = Path(path)
    with wide_path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def select_variants(rows: list[dict[str, str]]) -> list[VariantRecord]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[_variant_key(row)].append(row)

    selected: list[VariantRecord] = []
    for variant_rows in grouped.values():
        selected.append(_row_to_variant(_select_best_row(variant_rows)))

    selected.sort(
        key=lambda item: (
            item.pathogenic_rank if item.pathogenic_rank is not None else 999999,
            item.gene_symbol,
            item.chrom,
            int(item.pos) if item.pos.isdigit() else item.pos,
        )
    )
    return selected


def build_gene_cards(variants: list[VariantRecord], top_n: int) -> tuple[list[GeneCard], ReportSummary]:
    by_gene: dict[str, list[VariantRecord]] = defaultdict(list)
    for variant in variants:
        by_gene[variant.gene_symbol].append(variant)

    gene_stats: list[tuple[str, int, list[VariantRecord]]] = []
    for gene, gene_variants in by_gene.items():
        ranks = [v.pathogenic_rank for v in gene_variants if v.pathogenic_rank is not None]
        best_rank = min(ranks) if ranks else 999999
        gene_stats.append((gene, best_rank, gene_variants))

    gene_stats.sort(key=lambda item: (item[1], item[0]))
    top_stats = gene_stats[:top_n]

    gene_cards: list[GeneCard] = []
    top_gene_summaries: list[TopGeneSummary] = []

    for index, (gene, best_rank, gene_variants) in enumerate(top_stats, start=1):
        gene_variants = sorted(
            gene_variants,
            key=lambda item: item.pathogenic_rank if item.pathogenic_rank is not None else 999999,
        )
        primary = gene_variants[0]
        top_clinvar = primary.clinvar_significance if primary.clinvar_significance != "-" else ""
        card = GeneCard(
            rank=index,
            gene_symbol=gene,
            best_pathogenic_rank=best_rank,
            variant_count=len(gene_variants),
            top_clinvar=top_clinvar,
            main_consequence=primary.consequence,
            main_pathway="-",
            main_associated_phenotype="-",
            main_phenotype_hint=primary.clinical_best_tissue
            if primary.clinical_best_tissue != "-"
            else "",
            genos_evee=primary.genos_evee,
            evidence_summary=primary.evidence_summary,
            variants=gene_variants,
        )
        gene_cards.append(card)
        top_gene_summaries.append(
            TopGeneSummary(
                rank=index,
                gene=gene,
                variant_count=len(gene_variants),
                best_pathogenic_rank=best_rank,
                top_clinvar=top_clinvar,
                main_consequence=primary.consequence,
                main_pathway="-",
                main_associated_phenotype="-",
                evidence_summary=primary.evidence_summary,
            )
        )

    summary = ReportSummary(
        top_genes=top_gene_summaries,
        total_variants=len(variants),
        total_genes=len(by_gene),
        genes_outside_top_n=max(0, len(by_gene) - top_n),
    )
    return gene_cards, summary


def build_report_context(meta: SampleMeta, top_n: int = 5) -> ReportContext:
    if not meta.wide_table_path:
        raise ValueError("Sample manifest is missing wide table path (宽表)")

    rows = load_wide_table_rows(meta.wide_table_path)
    variants = select_variants(rows)
    gene_cards, summary = build_gene_cards(variants, top_n=top_n)

    return ReportContext(
        meta=meta,
        summary=summary,
        gene_cards=gene_cards,
        top_n=top_n,
    )
