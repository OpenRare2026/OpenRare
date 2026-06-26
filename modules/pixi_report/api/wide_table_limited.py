from __future__ import annotations

import csv
from pathlib import Path


def load_wide_table_rows_limited(
    path: str | Path,
    max_rows: int = 10000,
) -> list[dict[str, str]]:
    wide_path = Path(path)
    rows: list[dict[str, str]] = []
    with wide_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            if index >= max_rows:
                break
            rows.append(row)
    return rows
