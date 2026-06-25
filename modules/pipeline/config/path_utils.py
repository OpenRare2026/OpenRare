"""Resolve OpenRare pipeline module and external data paths."""

from __future__ import annotations

import os
from pathlib import Path

# modules/pipeline (pixi project root)
PIPELINE_ROOT = Path(__file__).resolve().parents[1]
# Backward-compatible alias used by older scripts
PIPELINE_V3_ROOT = PIPELINE_ROOT

# Fallback when .env and shell exports are unset (copy .env.example → .env).
DEFAULT_DATA_ROOT = "/path/to/vep_runner"
DEFAULT_PUBLIC_DATA_ROOT = "/path/to/public_data"
DEFAULT_REF_DIR = "/path/to/phasing/CHN_ref"
DEFAULT_BEAGLE_JAR = "/path/to/phasing/beagle.27Feb25.75f.jar"


def load_pipeline_dotenv() -> None:
    env_path = PIPELINE_ROOT / ".env"
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_pipeline_dotenv()


def resolve_pipeline_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (PIPELINE_ROOT / path).resolve()


def openrare_data_root() -> Path:
    raw = os.environ.get("OPENRARE_DATA_ROOT", DEFAULT_DATA_ROOT)
    return resolve_pipeline_path(raw)


def openrare_public_data_root() -> Path:
    raw = os.environ.get("OPENRARE_PUBLIC_DATA_ROOT", DEFAULT_PUBLIC_DATA_ROOT)
    return resolve_pipeline_path(raw)


def full_pipeline_ref_dir() -> Path:
    raw = os.environ.get("FULL_PIPELINE_REF_DIR", DEFAULT_REF_DIR)
    return resolve_pipeline_path(raw)


def full_pipeline_beagle_jar() -> Path:
    raw = os.environ.get("FULL_PIPELINE_BEAGLE_JAR", DEFAULT_BEAGLE_JAR)
    return resolve_pipeline_path(raw)


DEFAULT_LIFTOVER_JAR = "/path/to/grch37_to_grch38_liftover/liftover_runner/target/liftover-runner.jar"
DEFAULT_LIFTOVER_CONFIG = "/path/to/grch37_to_grch38_liftover/config/liftover_config.toml"


def liftover_jar_path() -> Path:
    raw = os.environ.get("LIFTOVER_JAR", DEFAULT_LIFTOVER_JAR)
    return resolve_pipeline_path(raw)


def liftover_config_path() -> Path:
    raw = os.environ.get("LIFTOVER_CONFIG", DEFAULT_LIFTOVER_CONFIG)
    return resolve_pipeline_path(raw)


def expand_openrare_tokens(value: str, data_root: str | Path | None = None) -> str:
    root = Path(data_root) if data_root else openrare_data_root()
    resolved = value.replace("${OPENRARE_DATA_ROOT}", str(root))
    if resolved.startswith("$OPENRARE_DATA_ROOT"):
        resolved = resolved.replace("$OPENRARE_DATA_ROOT", str(root), 1)
    return resolved
