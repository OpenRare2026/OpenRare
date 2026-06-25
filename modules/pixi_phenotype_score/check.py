"""Health checks for the phenotype-HPO scoring module.

Checks: config/paths.toml, external data directories, key imports.
"""

import sys
from pathlib import Path

try:
    from doctor.core import CheckResult
except ImportError:
    from dataclasses import dataclass

    @dataclass
    class CheckResult:
        name: str
        status: str
        message: str


_MODULE_DIR = Path(__file__).resolve().parent
_EXPECTED_DATA_DIRS = ["hpo", "hgnc", "mondo", "omim", "orphanet"]


def run_check():
    results = []

    # ── A. Code / import check ──
    try:
        sys.path.insert(0, str(_MODULE_DIR / "src"))
        from phenotype_hpo_score import main  # noqa: F401
        results.append(CheckResult(name="code", status="ok", message="phenotype_hpo_score importable"))
    except ImportError as e:
        results.append(CheckResult(name="code", status="error", message=str(e)))
    finally:
        if str(_MODULE_DIR / "src") in sys.path:
            sys.path.remove(str(_MODULE_DIR / "src"))

    try:
        from path_config import load_config  # noqa: F401
        results.append(CheckResult(name="path_config", status="ok", message="path_config importable"))
    except ImportError:
        results.append(CheckResult(name="path_config", status="warn", message="path_config not importable"))

    # ── B. Config file check ──
    paths_toml = _MODULE_DIR / "config" / "paths.toml"
    if paths_toml.exists():
        results.append(CheckResult(name="paths_config", status="ok", message=str(paths_toml)))
    else:
        paths_example = _MODULE_DIR / "config" / "paths.example.toml"
        if paths_example.exists():
            results.append(CheckResult(
                name="paths_config",
                status="warn",
                message="paths.toml missing; copy from paths.example.toml"
            ))
        else:
            results.append(CheckResult(
                name="paths_config",
                status="error",
                message="paths.toml and paths.example.toml both missing"
            ))

    # ── C. External data directories ──
    # Check if an external_data dir exists (can be a symlink to real storage)
    external_data = _MODULE_DIR / "external_data"
    if external_data.exists():
        found = [d for d in _EXPECTED_DATA_DIRS if (external_data / d).exists()]
        missing = [d for d in _EXPECTED_DATA_DIRS if not (external_data / d).exists()]
        results.append(CheckResult(
            name="external_data",
            status="ok" if not missing else "error",
            message=f"found: {found}; missing: {missing}" if missing else f"all {len(found)} dirs present"
        ))
    else:
        results.append(CheckResult(
            name="external_data",
            status="error",
            message=f"external_data/ dir not found at {external_data}; see EXTERNAL_DATA.md"
        ))

    # ── D. Python ──
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    if (3, 12) <= sys.version_info < (3, 13):
        results.append(CheckResult(name="python", status="ok", message=f"Python {pyver}"))
    else:
        results.append(CheckResult(name="python", status="warn", message=f"Python {pyver} (3.12 expected)"))

    return results
