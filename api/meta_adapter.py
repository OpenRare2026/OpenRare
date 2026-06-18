from __future__ import annotations

import csv
import re
from pathlib import Path

from report.models import SampleMeta

_HPO_PATTERN = re.compile(r"HP:\d+")


def _parse_hpo_file(path: Path) -> tuple[str, list[str]]:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    terms = sorted({match for line in raw_lines for match in _HPO_PATTERN.findall(line)})
    return "\n".join(raw_lines), terms


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

    for raw in rows[1:]:
        if not raw or not any(cell.strip() for cell in raw):
            continue

        if len(raw) == 1:
            parsed = _split_phenotype_line(raw[0])
            if parsed:
                return parsed
            continue

        headers = [header.strip() for header in rows[0]]
        id_idx = next((i for i, h in enumerate(headers) if h.upper() == "ID"), 0)
        phenotype_idx = next(
            (i for i, h in enumerate(headers) if h.lower() == "phenotype"),
            1 if len(headers) > 1 else 0,
        )
        sample_id = raw[id_idx].strip()
        clinical_info = raw[phenotype_idx].strip()
        if sample_id and clinical_info and sample_id != clinical_info:
            return sample_id, clinical_info

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
) -> SampleMeta:
    wide_table = str(Path(wide_path).resolve())
    sample_id, clinical_info = load_phenotype_csv(phenotype_path)
    hpo_raw, hpo_terms = _parse_hpo_file(Path(hpo_path))

    return SampleMeta(
        sample_id=sample_id,
        clinical_info=clinical_info,
        hpo_raw=hpo_raw,
        hpo_terms=hpo_terms,
        wide_table_path=wide_table,
    )
