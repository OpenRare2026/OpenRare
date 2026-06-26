"""
Parquet Service — CSV→Parquet conversion and Parquet reading for VEP results.

Stores VEP output as both raw CSV (for downstream service inputs) and
Parquet (for fast paginated frontend reads with dynamic columns).
"""
import io
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data" / "vep_results"


def _detect_delimiter(header_line: str) -> str:
    tab_count = header_line.count("\t")
    comma_count = header_line.count(",")
    return "\t" if tab_count >= comma_count else ","


def _strip_vep_comments(csv_content: str) -> str:
    lines = csv_content.strip().splitlines()
    return "\n".join(line for line in lines if not line.startswith("##"))


@dataclass
class ParquetReadResult:
    columns: List[str]
    items: List[Dict[str, str]]
    total: int
    page: int
    page_size: int
    total_pages: int


class ParquetService:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else _DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def csv_to_parquet(self, csv_content: str, job_id: str) -> tuple:
        """
        Save CSV content to file and convert to Parquet.
        Returns (csv_path, parquet_path).
        """
        csv_path = self.data_dir / f"{job_id}.csv"
        parquet_path = self.data_dir / f"{job_id}.parquet"

        cleaned = _strip_vep_comments(csv_content)
        if not cleaned.strip():
            logger.warning(f"Empty CSV content for job {job_id}")
            csv_path.write_text("", encoding="utf-8")
            empty_df = pd.DataFrame()
            empty_df.to_parquet(str(parquet_path), engine="pyarrow")
            return str(csv_path), str(parquet_path)

        csv_path.write_text(csv_content, encoding="utf-8")

        first_line = cleaned.splitlines()[0]
        delimiter = _detect_delimiter(first_line)

        df = pd.read_csv(
            io.StringIO(cleaned),
            delimiter=delimiter,
            dtype=str,
            keep_default_na=False,
            na_values=[],
        )

        df.to_parquet(str(parquet_path), engine="pyarrow")
        logger.info(f"Saved CSV ({len(df)} rows) → Parquet: {parquet_path}")
        return str(csv_path), str(parquet_path)

    def get_schema(self, parquet_path: str) -> List[str]:
        """Return column names from Parquet file."""
        p = Path(parquet_path)
        if not p.exists():
            return []
        df = pd.read_parquet(str(p), engine="pyarrow")
        return [str(c) for c in df.columns]

    def read_parquet(
        self,
        parquet_path: str,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
    ) -> ParquetReadResult:
        """Read Parquet with pagination and optional text search across all columns."""
        p = Path(parquet_path)
        if not p.exists():
            return ParquetReadResult(
                columns=[], items=[], total=0,
                page=page, page_size=page_size, total_pages=0,
            )

        df = pd.read_parquet(str(p), engine="pyarrow")
        columns = [str(c) for c in df.columns]

        if search:
            mask = df.apply(
                lambda row: any(
                    search.lower() in str(val).lower() for val in row
                ),
                axis=1,
            )
            df = df[mask]

        total = len(df)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        start = (page - 1) * page_size
        end = start + page_size
        page_df = df.iloc[start:end]

        items: List[Dict[str, str]] = []
        for _, row in page_df.iterrows():
            items.append({col: str(row[col]) for col in columns})

        return ParquetReadResult(
            columns=columns,
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def read_row(self, parquet_path: str, row_index: int) -> Optional[Dict[str, str]]:
        """Read a single row by 0-based index."""
        p = Path(parquet_path)
        if not p.exists():
            return None

        df = pd.read_parquet(str(p), engine="pyarrow")
        if row_index < 0 or row_index >= len(df):
            return None

        row = df.iloc[row_index]
        return {str(col): str(row[col]) for col in df.columns}

    def row_count(self, parquet_path: str) -> int:
        p = Path(parquet_path)
        if not p.exists():
            return 0
        df = pd.read_parquet(str(p), engine="pyarrow")
        return len(df)
