#!/usr/bin/env python3
"""Load project paths from a TOML file.

All configured paths are interpreted relative to the project root unless the
operator explicitly supplies an absolute deployment override.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "paths.toml"
EXAMPLE_CONFIG = PROJECT_ROOT / "config" / "paths.example.toml"


@dataclass(frozen=True)
class PathSettings:
    config_file: Path
    runtime_root: Path
    default_input_csv: Path
    default_hpo_file: Path
    hpo_ontology: Path
    hpo_annotations: Path
    gene_disease_associations: Path
    hgnc_symbols: Path
    mondo_ontology: Path
    omim_database: Path
    orphanet_packets: Path
    orphanet_index: Path


def _resolve(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        raise ValueError(f"Configured paths must be relative to the project root: {value}")
    return (PROJECT_ROOT / path).absolute()


def load_paths(config_file: Path | str | None = None) -> PathSettings:
    configured = config_file or os.environ.get("PHENOTYPE_PATHS_CONFIG")
    path = Path(configured).expanduser() if configured else DEFAULT_CONFIG
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    if not path.exists() and path == DEFAULT_CONFIG:
        path = EXAMPLE_CONFIG
    if not path.exists():
        raise FileNotFoundError(f"Path configuration not found: {path}")

    with path.open("rb") as handle:
        document = tomllib.load(handle)
    values = document.get("paths", {})
    required = {
        "runtime_root",
        "default_input_csv",
        "default_hpo_file",
        "hpo_ontology",
        "hpo_annotations",
        "gene_disease_associations",
        "hgnc_symbols",
        "mondo_ontology",
        "omim_database",
        "orphanet_packets",
        "orphanet_index",
    }
    missing = sorted(required - values.keys())
    if missing:
        raise ValueError("Missing path configuration keys: " + ", ".join(missing))

    return PathSettings(
        config_file=path.resolve(),
        **{name: _resolve(str(values[name])) for name in required},
    )


def resolve_project_path(path: Path) -> Path:
    """Resolve a CLI path consistently from the project root."""
    return path.absolute() if path.is_absolute() else (PROJECT_ROOT / path).absolute()


def display_path(path: Path) -> str:
    """Return a project-relative path for status, summaries, and logs."""
    absolute = path.absolute()
    return Path(os.path.relpath(absolute, PROJECT_ROOT)).as_posix()
