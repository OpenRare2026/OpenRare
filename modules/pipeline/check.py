"""Health checks for the variant-annotation pipeline module.

Checks: env vars (data roots, Beagle JAR), VEP cache path, key imports.
"""

import os
import sys
from pathlib import Path

# Use doctor package if available, otherwise self-contained
try:
    from doctor.core import CheckResult  # noqa: F811
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
        from config import path_utils  # noqa: F401
        results.append(CheckResult(name="code", status="ok", message="path_utils importable"))
    except ImportError as e:
        results.append(CheckResult(name="code", status="error", message=str(e)))

    # ── B. Required environment variables ──
    required_vars = [
        ("data_root", "OPENRARE_DATA_ROOT"),
        ("public_data_root", "OPENRARE_PUBLIC_DATA_ROOT"),
        ("ref_dir", "FULL_PIPELINE_REF_DIR"),
        ("beagle_jar", "FULL_PIPELINE_BEAGLE_JAR"),
    ]
    for name, var in required_vars:
        val = os.environ.get(var, "")
        if val:
            results.append(CheckResult(name=name, status="ok", message=val))
        else:
            results.append(CheckResult(name=name, status="error", message=f"missing {var}"))

    # ── C. Path existence checks (when env vars are set) ──
    env_path_checks = [
        ("vep_data_dir", "OPENRARE_DATA_ROOT"),
        ("public_data_dir", "OPENRARE_PUBLIC_DATA_ROOT"),
        ("phasing_ref_dir", "FULL_PIPELINE_REF_DIR"),
        ("beagle_jar_file", "FULL_PIPELINE_BEAGLE_JAR"),
    ]
    for name, var in env_path_checks:
        val = os.environ.get(var, "")
        if val:
            p = Path(val)
            if p.exists():
                results.append(CheckResult(name=name, status="ok", message=str(p)))
            else:
                results.append(CheckResult(name=name, status="error", message=f"path not found: {val}"))

    # ── D. Python version ──
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 11):
        results.append(CheckResult(name="python", status="ok", message=f"Python {pyver}"))
    else:
        results.append(CheckResult(name="python", status="warn", message=f"Python {pyver} (>=3.11 recommended)"))

    return results
