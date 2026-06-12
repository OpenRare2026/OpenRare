from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from report.models import SampleMeta

_HPO_PATTERN = re.compile(r"HP:\d+")


def _clean_path(value: str) -> str:
    text = (value or "").strip().strip('"').strip("'")
    if text.startswith("@"):
        text = text[1:]
    return text


def _parse_hpo_terms(raw: str) -> list[str]:
    return sorted(set(_HPO_PATTERN.findall(raw or "")))


def _parse_raghpo_returns(raw: str) -> dict | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _read_manifest_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.reader(handle))

    if len(raw_rows) < 2:
        return []

    headers = raw_rows[0]
    while headers and not headers[-1].strip():
        headers.pop()

    # Deduplicate blank header keys produced by leading/trailing commas.
    normalized_headers: list[str] = []
    blank_count = 0
    for header in headers:
        label = header.strip()
        if label:
            normalized_headers.append(label)
            continue
        blank_count += 1
        normalized_headers.append("家系类型" if blank_count == 1 else f"_extra_{blank_count}")

    rows: list[dict[str, str]] = []
    for raw in raw_rows[1:]:
        values = raw[: len(normalized_headers)]
        if len(values) < len(normalized_headers):
            values.extend([""] * (len(normalized_headers) - len(values)))
        rows.append(dict(zip(normalized_headers, values, strict=True)))
    return rows


def load_manifest(path: str | Path, row_index: int = 0) -> SampleMeta:
    manifest_path = Path(path)
    rows = _read_manifest_rows(manifest_path)

    if not rows:
        raise ValueError(f"No data rows found in manifest: {manifest_path}")

    if row_index < 0 or row_index >= len(rows):
        raise IndexError(
            f"row_index {row_index} out of range for manifest with {len(rows)} rows"
        )

    row = rows[row_index]
    family_type = (row.get("家系类型") or "").strip()

    hpo_raw = row.get("raghpo", "") or ""
    wide_table = _clean_path(row.get("宽表", "") or "")

    if wide_table and not Path(wide_table).is_absolute():
        wide_table = str((manifest_path.parent / wide_table).resolve())

    return SampleMeta(
        family_type=family_type,
        pedigree_role=(row.get("家系关系") or "").strip(),
        sample_id=(row.get("样本编号") or "").strip(),
        clinical_info=(row.get("临床信息") or "").strip(),
        hpo_raw=hpo_raw.strip(),
        hpo_terms=_parse_hpo_terms(hpo_raw),
        raghpo_returns=_parse_raghpo_returns(row.get("raghpo-returns", "") or ""),
        liftover_path=_clean_path(row.get("37 to 38", "") or ""),
        vcf_path=_clean_path(row.get("gz to vcf", "") or ""),
        wide_table_path=wide_table,
        gene_disease_path=_clean_path(row.get("基因与疾病", "") or ""),
        ppi_path=_clean_path(row.get("ppi", "") or ""),
        report_path=_clean_path(row.get("报告", "") or ""),
    )
