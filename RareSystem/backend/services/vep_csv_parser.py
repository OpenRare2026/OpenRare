"""
VEP CSV Parser — raw pandas read with no preset field assumptions.

Reads CSV content as-is via pandas, returns whatever columns the CSV has.
No field mapping, no aliasing, no filtering — CSV is king.
"""
import io
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class VEPParseResult:
    """Result of parsing VEP CSV — carries both raw rows and column metadata."""
    rows: List[Dict[str, str]]
    columns: List[str]


def _detect_delimiter(header_line: str) -> str:
    """Auto-detect delimiter by checking which character appears more frequently in header."""
    tab_count = header_line.count("\t")
    comma_count = header_line.count(",")
    return "\t" if tab_count >= comma_count else ","


def _strip_vep_comments(csv_content: str) -> str:
    """Remove VEP metadata lines (##) only — keep header and data intact."""
    lines = csv_content.strip().splitlines()
    kept: list[str] = []
    for line in lines:
        if line.startswith("##"):
            continue
        kept.append(line)
    return "\n".join(kept)


class VEPCSVParser:
    """Parse VEP CSV output using pandas — no field mapping, raw display."""

    def parse(self, csv_content: str) -> VEPParseResult:
        """Parse CSV content with pandas and return raw rows + column names.

        Whatever the CSV header says, that's what you get — no filtering,
        no aliasing, no type coercion beyond what pandas does.
        """
        if not csv_content or not csv_content.strip():
            return VEPParseResult(rows=[], columns=[])

        cleaned = _strip_vep_comments(csv_content)
        if not cleaned.strip():
            return VEPParseResult(rows=[], columns=[])

        # Detect delimiter from the first line
        first_line = cleaned.splitlines()[0]
        delimiter = _detect_delimiter(first_line)

        try:
            df = pd.read_csv(
                io.StringIO(cleaned),
                delimiter=delimiter,
                dtype=str,        # keep everything as string — no type guessing
                keep_default_na=False,
                na_values=[],
            )
        except pd.errors.EmptyDataError:
            return VEPParseResult(rows=[], columns=[])
        except Exception as e:
            logger.error(f"pandas failed to parse VEP CSV: {e}")
            return VEPParseResult(rows=[], columns=[])

        if df.empty:
            return VEPParseResult(rows=[], columns=list(df.columns))

        columns = [str(c) for c in df.columns]

        # Convert each row to a plain dict with original column names
        rows: List[Dict[str, str]] = []
        for _, row in df.iterrows():
            clean_row: Dict[str, str] = {}
            for col in columns:
                val = row[col]
                clean_row[col] = "" if pd.isna(val) else str(val)
            rows.append(clean_row)

        logger.info(f"Parsed {len(rows)} rows from VEP CSV ({len(columns)} columns: {columns})")
        return VEPParseResult(rows=rows, columns=columns)
