"""Scalable table I/O -- the ONLY module that touches the full wide table.

At 9 GB the bottleneck is reading, so we never read the whole table:
  * column projection -- read only needed_columns(registry), not all columns.
    Parquet is columnar, so unread columns cost nothing; CSV still byte-scans
    but at least we avoid materializing unused columns.
  * predicate pushdown -- optionally read only the selected transcript per
    variant (one row per variant instead of one per variant x transcript).
  * chunked streaming -- yield bounded row-batches so memory is O(chunk),
    not O(table). Feature extraction accumulates a tiny (n_rows x 6) matrix.

Engines, in preference order: duckdb (projection+predicate+streaming on both
parquet and csv), polars (if installed), pyarrow (parquet), pandas (fallback).
All values are returned as strings with missing == "-", matching the parsing
convention the contributors expect.
"""
from __future__ import annotations

import os
from typing import Iterable, Iterator, Optional

import pandas as pd

# selected-transcript predicate (null-safe: keep variants lacking a ranked tx)
SELECTED_TX_SQL = ("(CAST(tx_rank_within_variant AS VARCHAR) = '1' "
                   "OR tx_rank_within_variant IS NULL)")


def available_engines() -> list[str]:
    out = []
    for m in ("duckdb", "polars", "pyarrow"):
        try:
            __import__(m)
            out.append(m)
        except Exception:
            pass
    out.append("pandas")
    return out


def _detect_fmt(path: str, fmt: str) -> str:
    if fmt != "auto":
        return fmt
    low = path.lower()
    if low.endswith((".parquet", ".pq")):
        return "parquet"
    if low.endswith((".csv", ".csv.gz", ".tsv", ".txt", ".gz")):
        return "csv"
    return "parquet"


def _pick_engine(engine: str) -> str:
    if engine != "auto":
        return engine
    eng = available_engines()
    return eng[0]


def _normalize(df: pd.DataFrame, want: list[str]) -> pd.DataFrame:
    """Project to exactly `want` (adding any missing column as '-'), in order,
    with all values as strings and missing == '-'."""
    for c in want:
        if c not in df.columns:
            df[c] = "-"
    df = df.loc[:, list(want)]
    df = df.where(pd.notna(df), "-")
    df = df.astype(str)
    return df.replace({"None": "-", "nan": "-", "NaN": "-", "<NA>": "-", "": "-"})


# --------------------------------------------------------------------------
# duckdb (primary): projection + optional predicate + streaming, parquet & csv
# --------------------------------------------------------------------------
def _duckdb_source(path: str, fmt: str) -> str:
    p = path.replace("'", "''")
    if fmt == "csv":
        return f"read_csv_auto('{p}', all_varchar=true)"
    return f"read_parquet('{p}')"


def _duckdb_iter(path, want, fmt, row_filter, chunk_rows) -> Iterator[pd.DataFrame]:
    import duckdb
    con = duckdb.connect()
    try:
        src = _duckdb_source(path, fmt)
        schema = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()]
        sel = [c for c in want if c in schema]
        proj = ", ".join(f'CAST("{c}" AS VARCHAR) AS "{c}"' for c in sel) or "NULL"
        q = f"SELECT {proj} FROM {src}"
        if row_filter and "tx_rank_within_variant" in schema:
            q += f" WHERE {row_filter}"
        reader = con.execute(q).fetch_record_batch(chunk_rows)
        for batch in reader:
            yield _normalize(batch.to_pandas(), want)
    finally:
        con.close()


# --------------------------------------------------------------------------
# polars (optional): lazy scan + projection
# --------------------------------------------------------------------------
def _polars_iter(path, want, fmt, row_filter, chunk_rows) -> Iterator[pd.DataFrame]:
    import polars as pl
    lf = pl.scan_parquet(path) if fmt == "parquet" else pl.scan_csv(path, infer_schema_length=0)
    have = lf.collect_schema().names()
    sel = [c for c in want if c in have]
    lf = lf.select(sel)
    if row_filter == "selected_tx" and "tx_rank_within_variant" in have:
        lf = lf.filter((pl.col("tx_rank_within_variant").cast(pl.Utf8) == "1")
                       | pl.col("tx_rank_within_variant").is_null())
    df = lf.collect().to_pandas()
    for i in range(0, len(df), chunk_rows):
        yield _normalize(df.iloc[i:i + chunk_rows].copy(), want)


# --------------------------------------------------------------------------
# pyarrow (parquet) / pandas (csv) fallback
# --------------------------------------------------------------------------
def _pyarrow_iter(path, want, row_filter, chunk_rows) -> Iterator[pd.DataFrame]:
    import pyarrow.dataset as ds
    d = ds.dataset(path, format="parquet")
    sel = [c for c in want if c in d.schema.names]
    for batch in d.scanner(columns=sel, batch_size=chunk_rows).to_batches():
        df = _normalize(batch.to_pandas(), want)
        if row_filter == "selected_tx" and "tx_rank_within_variant" in df.columns:
            df = df[(df["tx_rank_within_variant"] == "1")
                    | (df["tx_rank_within_variant"] == "-")]
        if len(df):
            yield df


def _pandas_csv_iter(path, want, row_filter, chunk_rows) -> Iterator[pd.DataFrame]:
    head = pd.read_csv(path, nrows=0)
    sel = [c for c in want if c in head.columns]
    for chunk in pd.read_csv(path, dtype=str, keep_default_na=False,
                             usecols=sel or None, chunksize=chunk_rows):
        df = _normalize(chunk, want)
        if row_filter == "selected_tx" and "tx_rank_within_variant" in df.columns:
            df = df[(df["tx_rank_within_variant"] == "1")
                    | (df["tx_rank_within_variant"] == "-")]
        if len(df):
            yield df


# --------------------------------------------------------------------------
# public API
# --------------------------------------------------------------------------
def iter_chunks(path: str, columns: Iterable[str], *, engine: str = "auto",
                fmt: str = "auto", row_filter: Optional[str] = None,
                chunk_rows: int = 250_000, selected_tx_only: bool = False
                ) -> Iterator[pd.DataFrame]:
    """Yield projected, string-normalized row-batches for one case file.

    row_filter: raw SQL (duckdb only) OR the sentinel 'selected_tx'. The
    convenience flag selected_tx_only=True sets the null-safe selected-transcript
    predicate for every engine."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    want = list(dict.fromkeys(columns))
    fmt = _detect_fmt(path, fmt)
    eng = _pick_engine(engine)
    if selected_tx_only and not row_filter:
        row_filter = SELECTED_TX_SQL if eng == "duckdb" else "selected_tx"

    if eng == "duckdb":
        yield from _duckdb_iter(path, want, fmt, row_filter, chunk_rows)
    elif eng == "polars":
        yield from _polars_iter(path, want, fmt,
                                "selected_tx" if selected_tx_only else None, chunk_rows)
    elif eng == "pyarrow" and fmt == "parquet":
        yield from _pyarrow_iter(path, want,
                                 "selected_tx" if selected_tx_only else None, chunk_rows)
    else:
        yield from _pandas_csv_iter(path, want,
                                    "selected_tx" if selected_tx_only else None, chunk_rows)


def read_columns(path: str, columns: Iterable[str], *, engine: str = "auto",
                 fmt: str = "auto", row_filter: Optional[str] = None,
                 selected_tx_only: bool = False) -> pd.DataFrame:
    """Read one case file fully into memory, projected to `columns` only."""
    parts = list(iter_chunks(path, columns, engine=engine, fmt=fmt,
                             row_filter=row_filter, chunk_rows=250_000,
                             selected_tx_only=selected_tx_only))
    if not parts:
        return _normalize(pd.DataFrame(), list(dict.fromkeys(columns)))
    return pd.concat(parts, ignore_index=True)
