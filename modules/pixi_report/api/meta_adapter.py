from __future__ import annotations

import csv
import re
from pathlib import Path

from report.models import SampleMeta
from report.paths import normalize_stored_path, resolve_module_path

_HPO_PATTERN = re.compile(r"HP:\d+")


def _parse_hpo_file(path: Path) -> tuple[str, list[str]]:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    terms = sorted({match for line in raw_lines for match in _HPO_PATTERN.findall(line)})
    return "\n".join(raw_lines), terms


_ID_HEADERS = {"id", "样本id", "样本编号", "sample_id"}
_PHENOTYPE_HEADERS = {"phenotype", "clinical_info", "临床信息"}


def _is_header_row(cells: list[str]) -> bool:
    for cell in cells:
        token = cell.strip()
        if not token:
            continue
        lowered = token.lower()
        if lowered in _ID_HEADERS or lowered in _PHENOTYPE_HEADERS:
            return True
        if token in _PHENOTYPE_HEADERS:
            return True
    return False


def _find_id_index(headers: list[str]) -> int | None:
    for index, header in enumerate(headers):
        token = header.strip()
        if token.upper() == "ID" or token.lower() in _ID_HEADERS:
            return index
    return None


def _find_phenotype_index(headers: list[str]) -> int | None:
    for index, header in enumerate(headers):
        token = header.strip()
        if token.lower() in _PHENOTYPE_HEADERS or token in _PHENOTYPE_HEADERS:
            return index
    return None


def _split_phenotype_line(line: str) -> tuple[str, str] | None:
    text = line.strip()
    if not text:
        return None

    if "\t" in text:
        sample_id, clinical_info = text.split("\t", 1)
        return sample_id.strip(), clinical_info.strip()

    parts = text.split(None, 1)
    if len(parts) < 2:
        return None
    return parts[0].strip(), parts[1].strip()


def load_phenotype_csv(path: str | Path) -> tuple[str, str]:
    phenotype_path = Path(path)
    with phenotype_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No rows found in phenotype file: {phenotype_path}")

    has_header = _is_header_row(rows[0])
    headers = [header.strip() for header in rows[0]] if has_header else []
    id_idx = _find_id_index(headers) if has_header else None
    phenotype_idx = _find_phenotype_index(headers) if has_header else None
    data_rows = rows[1:] if has_header else rows

    for raw in data_rows:
        if not raw or not any(cell.strip() for cell in raw):
            continue

        if has_header:
            sample_id = (
                raw[id_idx].strip()
                if id_idx is not None and id_idx < len(raw)
                else ""
            )
            if phenotype_idx is not None and phenotype_idx < len(raw):
                clinical_info = raw[phenotype_idx].strip()
            elif len(raw) == 1:
                clinical_info = raw[0].strip()
            else:
                clinical_info = ""
                for index, cell in enumerate(raw):
                    if index == id_idx:
                        continue
                    if cell.strip():
                        clinical_info = cell.strip()
                        break
            if clinical_info:
                return sample_id, clinical_info
            continue

        if len(raw) == 1:
            text = raw[0].strip()
            parsed = _split_phenotype_line(text)
            if parsed:
                return parsed
            if text:
                return "", text
            continue

        joined = "\t".join(raw).strip()
        parsed = _split_phenotype_line(joined)
        if parsed:
            return parsed

    raise ValueError(f"No phenotype data row found in: {phenotype_path}")


def build_sample_meta(
    *,
    wide_path: str | Path,
    phenotype_path: str | Path,
    hpo_path: str | Path,
    ppi_path: str | Path = "",
) -> SampleMeta:
    wide_table = normalize_stored_path(str(wide_path))
    sample_id, clinical_info = load_phenotype_csv(resolve_module_path(str(phenotype_path)))
    hpo_raw, hpo_terms = _parse_hpo_file(resolve_module_path(str(hpo_path)))
    ppi = normalize_stored_path(str(ppi_path)) if str(ppi_path).strip() else ""

    return SampleMeta(
        sample_id=sample_id,
        clinical_info=clinical_info,
        hpo_raw=hpo_raw,
        hpo_terms=hpo_terms,
        wide_table_path=wide_table,
        ppi_path=ppi,
    )
