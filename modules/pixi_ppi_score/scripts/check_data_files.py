#!/usr/bin/env python3
"""Check external data files required by the PPI scoring service."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_DIR / "app"
sys.path.insert(0, str(APP_DIR))

from config import Config, DEFAULT_DATA_DIR  # noqa: E402


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_DIR.resolve()).as_posix()
    except ValueError:
        return os.path.relpath(path, PROJECT_DIR).replace(os.sep, "/")


def build_rows(data_dir: str) -> list[dict[str, object]]:
    cfg = Config(data_dir=data_dir)
    rows: list[dict[str, object]] = []

    for attr in cfg._PATH_ATTRS:
        path = Path(getattr(cfg, attr))
        exists = path.exists()
        rows.append(
            {
                "key": attr,
                "file": path.name,
                "path": display_path(path),
                "exists": exists,
                "size": path.stat().st_size if exists else 0,
            }
        )

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("RARE_PPI_DATA_DIR", DEFAULT_DATA_DIR),
        help="External data directory. Defaults to RARE_PPI_DATA_DIR or ../../../data.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    rows = build_rows(args.data_dir)
    missing = [row for row in rows if not row["exists"]]
    payload = {
        "data_dir": display_path(Path(args.data_dir)),
        "total_file_count": len(rows),
        "missing_file_count": len(missing),
        "missing_files": [row["path"] for row in missing],
        "files": rows,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"data_dir: {payload['data_dir']}")
        print(f"total_file_count: {payload['total_file_count']}")
        print(f"missing_file_count: {payload['missing_file_count']}")
        if missing:
            print("missing_files:")
            for row in missing:
                print(f"  - {row['path']}")
        else:
            print("all required files exist")

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
