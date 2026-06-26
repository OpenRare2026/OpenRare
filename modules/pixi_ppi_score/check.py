"""Health checks for the PPI scoring module.

Checks: PPI data directory, key env vars, module imports.
"""

import os
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


def run_check():
    results = []

    # ── A. Code / import check ──
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))
        from api import app  # noqa: F401
        results.append(CheckResult(name="code", status="ok", message="api module importable"))
    except ImportError as e:
        results.append(CheckResult(name="code", status="error", message=str(e)))
    finally:
        if str(Path(__file__).resolve().parent / "app") in sys.path:
            sys.path.remove(str(Path(__file__).resolve().parent / "app"))

    # ── B. Environment variables ──
    env_checks = [
        ("ppi_data_dir", "RARE_PPI_DATA_DIR"),
        ("ppi_host", "RARE_PPI_HOST"),
        ("ppi_port", "RARE_PPI_PORT"),
    ]
    for name, var in env_checks:
        val = os.environ.get(var, "")
        if val:
            results.append(CheckResult(name=name, status="ok", message=f"{var}={val}"))
        else:
            results.append(CheckResult(name=name, status="warn", message=f"missing {var} (will use default)"))

    # ── C. Data directory check ──
    data_dir = os.environ.get("RARE_PPI_DATA_DIR", "../../../data")
    p = Path(data_dir)
    if not p.exists():
        results.append(CheckResult(
            name="ppi_data_path",
            status="error",
            message=f"data dir not found: {data_dir} (set RARE_PPI_DATA_DIR)"
        ))
    else:
        results.append(CheckResult(name="ppi_data_path", status="ok", message=str(p.resolve())))
        # Critical data files (verified on 113: /mnt/workspace/luqi/data/)
        critical_files = [
            "hgnc_complete_set.txt",
            "hp.obo",
            "mim2gene.txt",
            "genemap2.txt",
        ]
        missing = [f for f in critical_files if not (p / f).exists()]
        if missing:
            results.append(CheckResult(
                name="ppi_data_files",
                status="error",
                message=f"missing {len(missing)}/{len(critical_files)}: {', '.join(missing)}"
            ))
        else:
            results.append(CheckResult(
                name="ppi_data_files",
                status="ok",
                message=f"all {len(critical_files)} core files present"
            ))

    # ── D. Port conflict check (production uses 9000) ──

    # ── D. Python ──
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    if (3, 10) <= sys.version_info < (3, 12):
        results.append(CheckResult(name="python", status="ok", message=f"Python {pyver}"))
    else:
        results.append(CheckResult(name="python", status="warn", message=f"Python {pyver} (3.10-3.11 expected)"))

    return results
